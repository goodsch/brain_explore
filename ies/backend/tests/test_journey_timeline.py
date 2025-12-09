"""Tests for journey timeline functionality."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest

from ies_backend.schemas.context import ContextJourneyEntry, JourneyClassification
from ies_backend.schemas.journey import (
    BreadcrumbJourney,
    EntryPoint,
    EntryPointType,
    JourneyMark,
    JourneyStep,
    MarkType,
)
from ies_backend.schemas.journey_timeline import (
    JourneyTimelineEntry,
    JourneyTimelineRequest,
    TimelineEntryType,
    TimelineGrouping,
)
from ies_backend.services.journey_timeline_service import JourneyTimelineService


@pytest.fixture
def mock_timeline_entries():
    """Mock JourneyTimelineEntry records (already converted)."""
    now = datetime.now(timezone.utc)
    return [
        JourneyTimelineEntry(
            id="tle_001",
            timestamp=now - timedelta(hours=2),
            entry_type=TimelineEntryType.ENTITY_VISIT,
            title="Searched for executive function",
            context_id="ctx_test",
            focus_id="q_001",
            target_id="entity_001",
            entity_links=["entity_001"],
        ),
        JourneyTimelineEntry(
            id="tle_002",
            timestamp=now - timedelta(hours=1),
            entry_type=TimelineEntryType.HIGHLIGHT_CREATED,
            title="Created highlight",
            context_id="ctx_test",
            target_id="entity_002",
            entity_links=["entity_002"],
        ),
        JourneyTimelineEntry(
            id="tle_003",
            timestamp=now,
            entry_type=TimelineEntryType.QUESTION_ASKED,
            title="Asked: How does working memory affect attention?",
            context_id="ctx_test",
            focus_id="q_001",
        ),
    ]


@pytest.fixture
def mock_breadcrumb_journey():
    """Mock BreadcrumbJourney with steps."""
    now = datetime.now(timezone.utc)
    return BreadcrumbJourney(
        id="journey_001",
        user_id="test_user",
        started_at=now - timedelta(hours=3),
        ended_at=now,
        entry_point=EntryPoint(type=EntryPointType.BOOK, reference="book_123"),
        path=[
            JourneyStep(
                entity_id="entity_001",
                entity_name="Executive Function",
                timestamp=now - timedelta(hours=3),
                dwell_time_seconds=120.0,
                source_book_id="book_123",
                source_passage="Executive function refers to cognitive processes...",
            ),
            JourneyStep(
                entity_id="entity_002",
                entity_name="Working Memory",
                timestamp=now - timedelta(hours=2, minutes=30),
                dwell_time_seconds=90.0,
                source_book_id="book_123",
            ),
        ],
        marks=[
            JourneyMark(
                type=MarkType.HIGHLIGHT,
                entity_id="entity_001",
                content="Key insight about prefrontal cortex",
                timestamp=now - timedelta(hours=2, minutes=45),
            )
        ],
    )


@pytest.mark.asyncio
class TestJourneyTimelineService:
    """Tests for JourneyTimelineService."""

    async def test_build_timeline_with_context_entries(self, mock_timeline_entries):
        """Test building timeline from context entries."""
        with patch.object(
            JourneyTimelineService,
            "_get_context_entries",
            return_value=mock_timeline_entries,
        ):
            with patch.object(JourneyTimelineService, "_get_breadcrumb_entries", return_value=[]):
                request = JourneyTimelineRequest(
                    context_id="ctx_test", grouping=TimelineGrouping.FLAT, limit=100
                )
                response = await JourneyTimelineService.build_timeline(request)

                assert response.total_entries == 3
                assert len(response.groups) == 1
                assert response.groups[0].entry_count == 3

    async def test_build_timeline_with_breadcrumb_journey(self, mock_breadcrumb_journey):
        """Test building timeline from breadcrumb journey."""
        with patch(
            "ies_backend.services.journey_timeline_service.JourneyService.list_journeys",
            return_value=([mock_breadcrumb_journey], 1),
        ):
            breadcrumb_entries = await JourneyTimelineService._get_breadcrumb_entries(
                "test_user", None, None, None
            )

            # Should have 2 steps + 1 mark = 3 entries
            assert len(breadcrumb_entries) == 3

            # Check entity visit entries
            entity_visits = [e for e in breadcrumb_entries if e.entry_type == TimelineEntryType.ENTITY_VISIT]
            assert len(entity_visits) == 2

            # Check highlight entry
            highlights = [e for e in breadcrumb_entries if e.entry_type == TimelineEntryType.HIGHLIGHT_CREATED]
            assert len(highlights) == 1

    async def test_grouping_by_day(self):
        """Test timeline grouping by day."""
        now = datetime.now(timezone.utc)
        entries_day1 = [
            JourneyTimelineEntry(
                id=f"tle_{i}",
                timestamp=now - timedelta(days=1, hours=i),
                entry_type=TimelineEntryType.NOTE_TAKEN,
                title=f"Entry {i}",
                context_id="ctx_test",
            )
            for i in range(3)
        ]
        entries_day2 = [
            JourneyTimelineEntry(
                id=f"tle_{i+3}",
                timestamp=now - timedelta(hours=i),
                entry_type=TimelineEntryType.NOTE_TAKEN,
                title=f"Entry {i+3}",
                context_id="ctx_test",
            )
            for i in range(2)
        ]

        with patch.object(
            JourneyTimelineService,
            "_get_context_entries",
            return_value=entries_day1 + entries_day2,
        ):
            with patch.object(JourneyTimelineService, "_get_breadcrumb_entries", return_value=[]):
                request = JourneyTimelineRequest(
                    context_id="ctx_test", grouping=TimelineGrouping.BY_DAY, limit=100
                )
                response = await JourneyTimelineService.build_timeline(request)

                assert response.total_entries == 5
                assert response.total_groups == 2
                # Each day should have its entries
                assert any(g.entry_count == 3 for g in response.groups)
                assert any(g.entry_count == 2 for g in response.groups)

    async def test_grouping_by_session(self):
        """Test timeline grouping by session (30-minute gaps)."""
        now = datetime.now(timezone.utc)
        # Session 1: 3 entries within 15 minutes
        session1 = [
            JourneyTimelineEntry(
                id=f"tle_{i}",
                timestamp=now - timedelta(hours=2, minutes=i * 5),
                entry_type=TimelineEntryType.NOTE_TAKEN,
                title=f"Session 1 entry {i}",
                context_id="ctx_test",
            )
            for i in range(3)
        ]
        # Session 2: 2 entries within 10 minutes (45 minutes after session 1)
        session2 = [
            JourneyTimelineEntry(
                id=f"tle_{i+3}",
                timestamp=now - timedelta(hours=1, minutes=i * 5),
                entry_type=TimelineEntryType.NOTE_TAKEN,
                title=f"Session 2 entry {i}",
                context_id="ctx_test",
            )
            for i in range(2)
        ]

        with patch.object(
            JourneyTimelineService,
            "_get_context_entries",
            return_value=session1 + session2,
        ):
            with patch.object(JourneyTimelineService, "_get_breadcrumb_entries", return_value=[]):
                request = JourneyTimelineRequest(
                    context_id="ctx_test", grouping=TimelineGrouping.BY_SESSION, limit=100
                )
                response = await JourneyTimelineService.build_timeline(request)

                assert response.total_entries == 5
                # Should create 2 sessions due to 45-minute gap
                assert response.total_groups == 2

    async def test_grouping_by_context(self, mock_timeline_entries):
        """Test timeline grouping by context."""
        # Add entries from different contexts
        context2_entries = [
            JourneyTimelineEntry(
                id="tle_ctx2_001",
                timestamp=datetime.now(timezone.utc),
                entry_type=TimelineEntryType.NOTE_TAKEN,
                title="Other context entry",
                context_id="ctx_other",
            )
        ]

        with patch.object(
            JourneyTimelineService,
            "_get_context_entries",
            return_value=mock_timeline_entries + context2_entries,
        ):
            with patch.object(JourneyTimelineService, "_get_breadcrumb_entries", return_value=[]):
                request = JourneyTimelineRequest(context_id="ctx_test", grouping=TimelineGrouping.BY_CONTEXT, limit=100)
                response = await JourneyTimelineService.build_timeline(request)

                assert response.total_entries == 4
                assert response.total_groups == 2

    async def test_entry_type_filtering(self, mock_timeline_entries):
        """Test filtering entries by type."""
        with patch.object(
            JourneyTimelineService,
            "_get_context_entries",
            return_value=mock_timeline_entries,
        ):
            with patch.object(JourneyTimelineService, "_get_breadcrumb_entries", return_value=[]):
                request = JourneyTimelineRequest(
                    context_id="ctx_test",
                    entry_types=[TimelineEntryType.HIGHLIGHT_CREATED],
                    grouping=TimelineGrouping.FLAT,
                    limit=100,
                )
                response = await JourneyTimelineService.build_timeline(request)

                # Should only return highlight entry
                assert response.total_entries == 1
                assert response.groups[0].entries[0].entry_type == TimelineEntryType.HIGHLIGHT_CREATED

    async def test_pagination(self, mock_timeline_entries):
        """Test timeline pagination."""
        with patch.object(
            JourneyTimelineService,
            "_get_context_entries",
            return_value=mock_timeline_entries,
        ):
            with patch.object(JourneyTimelineService, "_get_breadcrumb_entries", return_value=[]):
                # Get first page
                request = JourneyTimelineRequest(
                    context_id="ctx_test", grouping=TimelineGrouping.FLAT, limit=2, offset=0
                )
                response = await JourneyTimelineService.build_timeline(request)

                assert response.total_entries == 3  # Total in DB
                assert len(response.groups[0].entries) == 2  # Paginated

                # Get second page
                request.offset = 2
                response = await JourneyTimelineService.build_timeline(request)
                assert len(response.groups[0].entries) == 1

    async def test_timeline_stats(self):
        """Test timeline statistics calculation."""
        now = datetime.now(timezone.utc)
        entries = [
            JourneyTimelineEntry(
                id=f"tle_{i}",
                timestamp=now - timedelta(hours=i),
                entry_type=TimelineEntryType.HIGHLIGHT_CREATED if i % 2 == 0 else TimelineEntryType.QUESTION_ASKED,
                title=f"Entry {i}",
                context_id="ctx_test",
                entity_links=[f"entity_{i}"],
            )
            for i in range(5)
        ]

        with patch.object(
            JourneyTimelineService,
            "_get_context_entries",
            return_value=entries,
        ):
            with patch.object(JourneyTimelineService, "_get_breadcrumb_entries", return_value=[]):
                stats = await JourneyTimelineService.get_timeline_stats(context_id="ctx_test")

                assert stats.total_entries == 5
                assert stats.contexts_count == 1
                assert stats.days_active > 0
                assert stats.last_activity is not None

    async def test_entry_linking(self):
        """Test that entries are linked with previous_entry_id."""
        now = datetime.now(timezone.utc)
        entries = [
            JourneyTimelineEntry(
                id=f"tle_{i}",
                timestamp=now - timedelta(hours=3 - i),
                entry_type=TimelineEntryType.NOTE_TAKEN,
                title=f"Entry {i}",
                context_id="ctx_test",
            )
            for i in range(3)
        ]

        with patch.object(
            JourneyTimelineService,
            "_get_context_entries",
            return_value=entries,
        ):
            with patch.object(JourneyTimelineService, "_get_breadcrumb_entries", return_value=[]):
                request = JourneyTimelineRequest(
                    context_id="ctx_test", grouping=TimelineGrouping.FLAT, limit=100
                )
                response = await JourneyTimelineService.build_timeline(request)

                timeline_entries = response.groups[0].entries
                # First entry has no previous
                assert timeline_entries[0].previous_entry_id is None
                # Subsequent entries link to previous
                assert timeline_entries[1].previous_entry_id == timeline_entries[0].id
                assert timeline_entries[2].previous_entry_id == timeline_entries[1].id

    async def test_classification_to_type_mapping(self):
        """Test that classifications are correctly mapped to entry types."""
        service = JourneyTimelineService

        assert (
            service._map_classification_to_type([JourneyClassification.HIGHLIGHT])
            == TimelineEntryType.HIGHLIGHT_CREATED
        )
        assert (
            service._map_classification_to_type([JourneyClassification.NEW_QUESTION])
            == TimelineEntryType.QUESTION_ASKED
        )
        assert (
            service._map_classification_to_type([JourneyClassification.ANSWER_FRAGMENT])
            == TimelineEntryType.QUESTION_ANSWERED
        )
        assert (
            service._map_classification_to_type([JourneyClassification.EXTRACTION_RUN])
            == TimelineEntryType.EXTRACTION_RUN
        )
        assert (
            service._map_classification_to_type([JourneyClassification.QUESTION_CLICK])
            == TimelineEntryType.ENTITY_VISIT
        )

    async def test_dwell_time_aggregation(self):
        """Test that dwell times are correctly aggregated."""
        now = datetime.now(timezone.utc)
        entries = [
            JourneyTimelineEntry(
                id=f"tle_{i}",
                timestamp=now - timedelta(hours=i),
                entry_type=TimelineEntryType.NOTE_TAKEN,
                title=f"Entry {i}",
                context_id="ctx_test",
            )
            for i in range(3)
        ]

        # Mock breadcrumb with dwell times
        journey = BreadcrumbJourney(
            id="journey_001",
            user_id="test_user",
            started_at=now - timedelta(hours=2),
            ended_at=now,
            entry_point=EntryPoint(type=EntryPointType.BOOK, reference="book_123"),
            path=[
                JourneyStep(
                    entity_id=f"entity_{i}",
                    entity_name=f"Entity {i}",
                    timestamp=now - timedelta(hours=2 - i),
                    dwell_time_seconds=60.0 * (i + 1),  # 60, 120, 180 seconds
                )
                for i in range(3)
            ],
        )

        with patch.object(JourneyTimelineService, "_get_context_entries", return_value=entries):
            with patch(
                "ies_backend.services.journey_timeline_service.JourneyService.list_journeys",
                return_value=([journey], 1),
            ):
                request = JourneyTimelineRequest(
                    user_id="test_user", grouping=TimelineGrouping.FLAT, limit=100
                )
                response = await JourneyTimelineService.build_timeline(request)

                # Total dwell time should be 60 + 120 + 180 = 360 seconds
                assert response.total_dwell_time == 360.0

    async def test_empty_timeline(self):
        """Test handling of empty timeline."""
        with patch.object(JourneyTimelineService, "_get_context_entries", return_value=[]):
            with patch.object(JourneyTimelineService, "_get_breadcrumb_entries", return_value=[]):
                request = JourneyTimelineRequest(
                    context_id="ctx_nonexistent", grouping=TimelineGrouping.FLAT, limit=100
                )
                response = await JourneyTimelineService.build_timeline(request)

                assert response.total_entries == 0
                assert response.total_groups == 0
                assert len(response.groups) == 0

    async def test_date_range_filtering(self):
        """Test filtering entries by date range."""
        now = datetime.now(timezone.utc)
        entries = [
            JourneyTimelineEntry(
                id=f"tle_{i}",
                timestamp=now - timedelta(days=i),
                entry_type=TimelineEntryType.NOTE_TAKEN,
                title=f"Entry {i}",
                context_id="ctx_test",
            )
            for i in range(7)
        ]

        with patch.object(
            JourneyTimelineService,
            "_get_context_entries",
            return_value=entries[0:3],  # Service will filter
        ):
            with patch.object(JourneyTimelineService, "_get_breadcrumb_entries", return_value=[]):
                # Request last 3 days
                request = JourneyTimelineRequest(
                    context_id="ctx_test",
                    start_date=now - timedelta(days=3),
                    end_date=now,
                    grouping=TimelineGrouping.FLAT,
                    limit=100,
                )
                response = await JourneyTimelineService.build_timeline(request)

                assert response.total_entries == 3
