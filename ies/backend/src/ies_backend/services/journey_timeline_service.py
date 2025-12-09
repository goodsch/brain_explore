"""Journey Timeline Service for building timeline views from journey data.

This service aggregates journey entries from multiple sources:
- ContextJourneyEntry (Flow Mode interactions)
- BreadcrumbJourney steps (Reader exploration paths)
- Highlights, notes, and other captured artifacts

It transforms them into timeline-friendly structures for visualization.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from ies_backend.schemas.context import ContextJourneyEntry, JourneyClassification
from ies_backend.schemas.journey import BreadcrumbJourney, MarkType
from ies_backend.schemas.journey_timeline import (
    JourneyTimelineEntry,
    JourneyTimelineRequest,
    JourneyTimelineResponse,
    TimelineEntryType,
    TimelineGroup,
    TimelineGrouping,
    TimelineStatsResponse,
)
from ies_backend.services.context_service import ContextService
from ies_backend.services.journey_service import JourneyService
from ies_backend.services.neo4j_client import Neo4jClient


class JourneyTimelineService:
    """Service for building and querying journey timelines."""

    @classmethod
    async def build_timeline(cls, request: JourneyTimelineRequest) -> JourneyTimelineResponse:
        """Build a timeline from journey entries.

        Args:
            request: Timeline request with filters and grouping

        Returns:
            Timeline response with grouped entries and statistics
        """
        # Collect entries from all sources
        all_entries: list[JourneyTimelineEntry] = []

        # 1. Get ContextJourneyEntry records
        if request.context_id:
            context_entries = await cls._get_context_entries(
                request.context_id, request.focus_id, request.start_date, request.end_date
            )
            all_entries.extend(context_entries)

        # 2. Get BreadcrumbJourney steps
        if request.user_id:
            breadcrumb_entries = await cls._get_breadcrumb_entries(
                request.user_id, request.context_id, request.start_date, request.end_date
            )
            all_entries.extend(breadcrumb_entries)

        # 3. Filter by entry type if specified
        if request.entry_types:
            all_entries = [e for e in all_entries if e.entry_type in request.entry_types]

        # 4. Sort by timestamp
        all_entries.sort(key=lambda e: e.timestamp)

        # 5. Link entries (set previous_entry_id) - returns new list with linked entries
        all_entries = cls._link_entries(all_entries)

        # 6. Apply pagination
        paginated_entries = all_entries[request.offset : request.offset + request.limit]

        # 7. Group entries
        groups = cls._group_entries(paginated_entries, request.grouping)

        # 8. Calculate statistics
        stats = cls._calculate_stats(all_entries)

        return JourneyTimelineResponse(
            groups=groups,
            total_entries=len(all_entries),
            total_groups=len(groups),
            date_range=stats["date_range"],
            entry_type_counts=stats["entry_type_counts"],
            contexts_involved=stats["contexts_involved"],
            total_dwell_time=stats["total_dwell_time"],
        )

    @classmethod
    async def get_timeline_stats(
        cls, context_id: str | None = None, user_id: str | None = None
    ) -> TimelineStatsResponse:
        """Get summary statistics for a timeline.

        Args:
            context_id: Optional context filter
            user_id: Optional user filter

        Returns:
            Timeline statistics
        """
        # Build timeline with no pagination
        request = JourneyTimelineRequest(
            context_id=context_id, user_id=user_id, limit=10000, grouping=TimelineGrouping.FLAT
        )
        timeline = await cls.build_timeline(request)

        # Flatten all entries
        all_entries = [entry for group in timeline.groups for entry in group.entries]

        # Count by type
        entity_visits = sum(1 for e in all_entries if e.entry_type == TimelineEntryType.ENTITY_VISIT)
        questions = sum(
            1
            for e in all_entries
            if e.entry_type in [TimelineEntryType.QUESTION_ASKED, TimelineEntryType.QUESTION_ANSWERED]
        )
        highlights = sum(1 for e in all_entries if e.entry_type == TimelineEntryType.HIGHLIGHT_CREATED)
        notes = sum(1 for e in all_entries if e.entry_type == TimelineEntryType.NOTE_TAKEN)
        concepts = sum(1 for e in all_entries if e.entry_type == TimelineEntryType.CONCEPT_FORMALIZED)

        # Activity by day
        entries_by_day: dict[str, int] = defaultdict(int)
        for entry in all_entries:
            day_key = entry.timestamp.strftime("%Y-%m-%d")
            entries_by_day[day_key] += 1

        # Find most active context and entity
        context_counts: dict[str, int] = defaultdict(int)
        entity_counts: dict[str, int] = defaultdict(int)

        for entry in all_entries:
            if entry.context_id:
                context_counts[entry.context_id] += 1
            for entity_id in entry.entity_links:
                entity_counts[entity_id] += 1

        most_active_context = max(context_counts, key=context_counts.get) if context_counts else None
        most_visited_entity = max(entity_counts, key=entity_counts.get) if entity_counts else None

        # Calculate time metrics
        total_dwell_time = sum(e.dwell_time_seconds or 0 for e in all_entries)
        last_activity = max((e.timestamp for e in all_entries), default=None)
        days_active = len(entries_by_day)

        return TimelineStatsResponse(
            total_entries=len(all_entries),
            contexts_count=len(context_counts),
            entities_visited=entity_visits,
            questions_explored=questions,
            highlights_created=highlights,
            notes_taken=notes,
            concepts_formalized=concepts,
            total_dwell_time_hours=total_dwell_time / 3600,
            entries_by_day=dict(entries_by_day),
            most_active_context=most_active_context,
            most_visited_entity=most_visited_entity,
            last_activity=last_activity,
            days_active=days_active,
        )

    # -----------------------------------------------------------------------------
    # Private: Entry Collection
    # -----------------------------------------------------------------------------

    @classmethod
    async def _get_context_entries(
        cls, context_id: str, focus_id: str | None, start_date: datetime | None, end_date: datetime | None
    ) -> list[JourneyTimelineEntry]:
        """Convert ContextJourneyEntry records to timeline entries."""
        # Get entries from context service
        response = await ContextService.get_journey_entries(context_id, focus_id, limit=1000)
        entries: list[JourneyTimelineEntry] = []

        for ce in response.entries:
            # Filter by date range
            if start_date and ce.timestamp < start_date:
                continue
            if end_date and ce.timestamp > end_date:
                continue

            # Map classification to entry type
            entry_type = cls._map_classification_to_type(ce.classifications)

            # Build title and description
            title, description = cls._build_title_description(ce)

            timeline_entry = JourneyTimelineEntry(
                id=ce.id or f"tle_{ce.timestamp.timestamp()}",
                timestamp=ce.timestamp,
                entry_type=entry_type,
                title=title,
                description=description,
                context_id=ce.context_id,
                focus_id=ce.focus_id,
                target_type="question" if ce.focus_id else None,
                target_id=ce.focus_id,
                source_action=ce.source_action,
                entity_links=ce.entity_links,
                tags=list(c.value for c in ce.classifications),
            )
            entries.append(timeline_entry)

        return entries

    @classmethod
    async def _get_breadcrumb_entries(
        cls, user_id: str, context_id: str | None, start_date: datetime | None, end_date: datetime | None
    ) -> list[JourneyTimelineEntry]:
        """Convert BreadcrumbJourney steps to timeline entries."""
        # Get journeys for user
        journeys, _ = await JourneyService.list_journeys(user_id, page=1, page_size=100)
        entries: list[JourneyTimelineEntry] = []

        for journey in journeys:
            # Filter by date range
            if start_date and journey.started_at < start_date:
                continue
            if end_date and journey.started_at > end_date:
                continue

            # Convert steps to timeline entries
            for step in journey.path:
                # Filter by date
                if start_date and step.timestamp < start_date:
                    continue
                if end_date and step.timestamp > end_date:
                    continue

                timeline_entry = JourneyTimelineEntry(
                    id=f"tle_step_{journey.id}_{step.entity_id}",
                    timestamp=step.timestamp,
                    entry_type=TimelineEntryType.ENTITY_VISIT,
                    title=f"Explored: {step.entity_name}",
                    description=step.source_passage[:200] if step.source_passage else None,
                    context_id=context_id,  # Not directly available in breadcrumb
                    target_type="entity",
                    target_id=step.entity_id,
                    target_name=step.entity_name,
                    target_preview=step.source_passage[:100] if step.source_passage else None,
                    source_type="book",
                    source_id=step.source_book_id,
                    dwell_time_seconds=step.dwell_time_seconds,
                    entity_links=[step.entity_id],
                    tags=["breadcrumb_journey"],
                )
                entries.append(timeline_entry)

            # Convert marks to timeline entries
            for mark in journey.marks:
                entry_type_map = {
                    MarkType.HIGHLIGHT: TimelineEntryType.HIGHLIGHT_CREATED,
                    MarkType.ANNOTATION: TimelineEntryType.NOTE_TAKEN,
                    MarkType.QUESTION: TimelineEntryType.QUESTION_ASKED,
                    MarkType.BOOKMARK: TimelineEntryType.NOTE_TAKEN,
                }

                timeline_entry = JourneyTimelineEntry(
                    id=f"tle_mark_{journey.id}_{mark.entity_id}",
                    timestamp=mark.timestamp,
                    entry_type=entry_type_map.get(mark.type, TimelineEntryType.NOTE_TAKEN),
                    title=f"{mark.type.value.capitalize()}: {mark.content[:50]}...",
                    description=mark.content,
                    context_id=context_id,
                    target_type="entity",
                    target_id=mark.entity_id,
                    source_location=mark.source_location,
                    entity_links=[mark.entity_id],
                    tags=["mark", mark.type.value],
                )
                entries.append(timeline_entry)

        return entries

    # -----------------------------------------------------------------------------
    # Private: Entry Processing
    # -----------------------------------------------------------------------------

    @classmethod
    def _map_classification_to_type(
        cls, classifications: list[JourneyClassification]
    ) -> TimelineEntryType:
        """Map journey classification to timeline entry type."""
        if not classifications:
            return TimelineEntryType.NOTE_TAKEN

        # Priority mapping
        type_map = {
            JourneyClassification.ANSWER_FRAGMENT: TimelineEntryType.QUESTION_ANSWERED,
            JourneyClassification.NEW_QUESTION: TimelineEntryType.QUESTION_ASKED,
            JourneyClassification.HIGHLIGHT: TimelineEntryType.HIGHLIGHT_CREATED,
            JourneyClassification.READING_NOTE: TimelineEntryType.NOTE_TAKEN,
            JourneyClassification.EXTRACTION_RUN: TimelineEntryType.EXTRACTION_RUN,
            JourneyClassification.QUESTION_CLICK: TimelineEntryType.ENTITY_VISIT,
        }

        for classification in classifications:
            if classification in type_map:
                return type_map[classification]

        return TimelineEntryType.NOTE_TAKEN

    @classmethod
    def _build_title_description(cls, entry: ContextJourneyEntry) -> tuple[str, str | None]:
        """Build human-readable title and description from entry."""
        if entry.text:
            title = entry.text[:80]
            description = entry.text if len(entry.text) > 80 else None
        elif entry.user_message:
            title = f"Asked: {entry.user_message[:80]}"
            description = entry.user_message
        elif entry.ai_message:
            title = f"Response: {entry.ai_message[:80]}"
            description = entry.ai_message
        else:
            action_titles = {
                "context_search": "Searched for concepts",
                "flow_button_click": "Explored entity",
                "extraction_run": "Ran extraction",
            }
            title = action_titles.get(entry.source_action or "", "Activity")
            description = None

        return title, description

    @classmethod
    def _link_entries(cls, entries: list[JourneyTimelineEntry]) -> list[JourneyTimelineEntry]:
        """Link entries by setting previous_entry_id.

        Returns new list with updated entries (Pydantic models are immutable).
        """
        if not entries:
            return entries

        linked_entries = [entries[0]]  # First entry has no previous

        for i in range(1, len(entries)):
            # Create new entry with previous_entry_id set
            linked_entry = entries[i].model_copy(update={"previous_entry_id": entries[i - 1].id})
            linked_entries.append(linked_entry)

        return linked_entries

    # -----------------------------------------------------------------------------
    # Private: Grouping
    # -----------------------------------------------------------------------------

    @classmethod
    def _group_entries(
        cls, entries: list[JourneyTimelineEntry], grouping: TimelineGrouping
    ) -> list[TimelineGroup]:
        """Group entries by specified strategy."""
        if grouping == TimelineGrouping.FLAT:
            return cls._group_flat(entries)
        elif grouping == TimelineGrouping.BY_DAY:
            return cls._group_by_day(entries)
        elif grouping == TimelineGrouping.BY_WEEK:
            return cls._group_by_week(entries)
        elif grouping == TimelineGrouping.BY_CONTEXT:
            return cls._group_by_context(entries)
        elif grouping == TimelineGrouping.BY_SESSION:
            return cls._group_by_session(entries)
        else:
            return cls._group_flat(entries)

    @classmethod
    def _group_flat(cls, entries: list[JourneyTimelineEntry]) -> list[TimelineGroup]:
        """No grouping - single group with all entries."""
        if not entries:
            return []

        return [
            TimelineGroup(
                group_key="all",
                group_label="All Activity",
                start_time=entries[0].timestamp,
                end_time=entries[-1].timestamp if len(entries) > 1 else None,
                entry_count=len(entries),
                entries=entries,
                entity_count=len({e.target_id for e in entries if e.entry_type == TimelineEntryType.ENTITY_VISIT}),
                question_count=sum(1 for e in entries if "question" in e.entry_type.value),
                highlight_count=sum(1 for e in entries if e.entry_type == TimelineEntryType.HIGHLIGHT_CREATED),
                total_dwell_time=sum(e.dwell_time_seconds or 0 for e in entries),
            )
        ]

    @classmethod
    def _group_by_day(cls, entries: list[JourneyTimelineEntry]) -> list[TimelineGroup]:
        """Group entries by day."""
        if not entries:
            return []

        groups_dict: dict[str, list[JourneyTimelineEntry]] = defaultdict(list)
        for entry in entries:
            day_key = entry.timestamp.strftime("%Y-%m-%d")
            groups_dict[day_key].append(entry)

        groups = []
        for day_key, day_entries in sorted(groups_dict.items()):
            date = datetime.strptime(day_key, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            groups.append(
                TimelineGroup(
                    group_key=day_key,
                    group_label=date.strftime("%B %d, %Y"),
                    start_time=date,
                    end_time=date + timedelta(days=1),
                    entry_count=len(day_entries),
                    entries=day_entries,
                    entity_count=len(
                        {e.target_id for e in day_entries if e.entry_type == TimelineEntryType.ENTITY_VISIT}
                    ),
                    question_count=sum(1 for e in day_entries if "question" in e.entry_type.value),
                    highlight_count=sum(1 for e in day_entries if e.entry_type == TimelineEntryType.HIGHLIGHT_CREATED),
                    total_dwell_time=sum(e.dwell_time_seconds or 0 for e in day_entries),
                )
            )

        return groups

    @classmethod
    def _group_by_week(cls, entries: list[JourneyTimelineEntry]) -> list[TimelineGroup]:
        """Group entries by week."""
        if not entries:
            return []

        groups_dict: dict[str, list[JourneyTimelineEntry]] = defaultdict(list)
        for entry in entries:
            # Get Monday of the week
            week_start = entry.timestamp - timedelta(days=entry.timestamp.weekday())
            week_key = week_start.strftime("%Y-W%U")
            groups_dict[week_key].append(entry)

        groups = []
        for week_key, week_entries in sorted(groups_dict.items()):
            # Get first entry timestamp for start time
            start_time = min(e.timestamp for e in week_entries)
            end_time = max(e.timestamp for e in week_entries)

            groups.append(
                TimelineGroup(
                    group_key=week_key,
                    group_label=f"Week of {start_time.strftime('%B %d, %Y')}",
                    start_time=start_time,
                    end_time=end_time,
                    entry_count=len(week_entries),
                    entries=week_entries,
                    entity_count=len(
                        {e.target_id for e in week_entries if e.entry_type == TimelineEntryType.ENTITY_VISIT}
                    ),
                    question_count=sum(1 for e in week_entries if "question" in e.entry_type.value),
                    highlight_count=sum(1 for e in week_entries if e.entry_type == TimelineEntryType.HIGHLIGHT_CREATED),
                    total_dwell_time=sum(e.dwell_time_seconds or 0 for e in week_entries),
                )
            )

        return groups

    @classmethod
    def _group_by_context(cls, entries: list[JourneyTimelineEntry]) -> list[TimelineGroup]:
        """Group entries by context."""
        if not entries:
            return []

        groups_dict: dict[str, list[JourneyTimelineEntry]] = defaultdict(list)
        for entry in entries:
            context_key = entry.context_id or "no_context"
            groups_dict[context_key].append(entry)

        groups = []
        for context_key, context_entries in groups_dict.items():
            start_time = min(e.timestamp for e in context_entries)
            end_time = max(e.timestamp for e in context_entries)

            groups.append(
                TimelineGroup(
                    group_key=context_key,
                    group_label=context_entries[0].context_title or context_key,
                    start_time=start_time,
                    end_time=end_time,
                    entry_count=len(context_entries),
                    entries=context_entries,
                    entity_count=len(
                        {e.target_id for e in context_entries if e.entry_type == TimelineEntryType.ENTITY_VISIT}
                    ),
                    question_count=sum(1 for e in context_entries if "question" in e.entry_type.value),
                    highlight_count=sum(1 for e in context_entries if e.entry_type == TimelineEntryType.HIGHLIGHT_CREATED),
                    total_dwell_time=sum(e.dwell_time_seconds or 0 for e in context_entries),
                )
            )

        return groups

    @classmethod
    def _group_by_session(cls, entries: list[JourneyTimelineEntry]) -> list[TimelineGroup]:
        """Group entries by session (entries within 30 minutes).

        A session is a continuous exploration period. We define boundaries
        as gaps of more than 30 minutes between entries.
        """
        if not entries:
            return []

        SESSION_GAP_MINUTES = 30
        groups = []
        current_session: list[JourneyTimelineEntry] = []

        for entry in entries:
            if not current_session:
                current_session.append(entry)
            else:
                # Check time gap
                last_entry = current_session[-1]
                gap = (entry.timestamp - last_entry.timestamp).total_seconds() / 60

                if gap > SESSION_GAP_MINUTES:
                    # End current session, start new one
                    groups.append(cls._create_session_group(len(groups) + 1, current_session))
                    current_session = [entry]
                else:
                    current_session.append(entry)

        # Add final session
        if current_session:
            groups.append(cls._create_session_group(len(groups) + 1, current_session))

        return groups

    @classmethod
    def _create_session_group(cls, session_num: int, entries: list[JourneyTimelineEntry]) -> TimelineGroup:
        """Create a TimelineGroup from session entries."""
        start_time = entries[0].timestamp
        end_time = entries[-1].timestamp
        duration_minutes = (end_time - start_time).total_seconds() / 60

        return TimelineGroup(
            group_key=f"session_{session_num}",
            group_label=f"Session {session_num} ({int(duration_minutes)} min)",
            start_time=start_time,
            end_time=end_time,
            entry_count=len(entries),
            entries=entries,
            entity_count=len({e.target_id for e in entries if e.entry_type == TimelineEntryType.ENTITY_VISIT}),
            question_count=sum(1 for e in entries if "question" in e.entry_type.value),
            highlight_count=sum(1 for e in entries if e.entry_type == TimelineEntryType.HIGHLIGHT_CREATED),
            total_dwell_time=sum(e.dwell_time_seconds or 0 for e in entries),
        )

    # -----------------------------------------------------------------------------
    # Private: Statistics
    # -----------------------------------------------------------------------------

    @classmethod
    def _calculate_stats(cls, entries: list[JourneyTimelineEntry]) -> dict:
        """Calculate summary statistics for entries."""
        if not entries:
            return {
                "date_range": {},
                "entry_type_counts": {},
                "contexts_involved": [],
                "total_dwell_time": 0.0,
            }

        # Date range
        start = min(e.timestamp for e in entries)
        end = max(e.timestamp for e in entries)

        # Entry type counts
        type_counts: dict[str, int] = defaultdict(int)
        for entry in entries:
            type_counts[entry.entry_type.value] += 1

        # Contexts
        contexts = list({e.context_id for e in entries if e.context_id})

        # Total dwell time
        total_dwell = sum(e.dwell_time_seconds or 0 for e in entries)

        return {
            "date_range": {"start": start.isoformat(), "end": end.isoformat()},
            "entry_type_counts": dict(type_counts),
            "contexts_involved": contexts,
            "total_dwell_time": total_dwell,
        }
