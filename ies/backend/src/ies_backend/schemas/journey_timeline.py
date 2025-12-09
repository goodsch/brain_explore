"""Journey Timeline schemas for visualization and exploration history.

This module provides timeline-friendly data structures for rendering
journey history showing exploration paths through entities, questions,
and concepts.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TimelineEntryType(str, Enum):
    """Types of entries that can appear in a timeline."""

    ENTITY_VISIT = "entity_visit"
    QUESTION_ASKED = "question_asked"
    QUESTION_ANSWERED = "question_answered"
    HIGHLIGHT_CREATED = "highlight_created"
    NOTE_TAKEN = "note_taken"
    CONCEPT_FORMALIZED = "concept_formalized"
    EXTRACTION_RUN = "extraction_run"
    SEARCH_PERFORMED = "search_performed"
    FACET_EXPLORED = "facet_explored"
    CONTEXT_CREATED = "context_created"
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
    TEMPLATE_SESSION = "template_session"


class TimelineGrouping(str, Enum):
    """Grouping strategies for timeline entries."""

    BY_DAY = "by_day"
    BY_SESSION = "by_session"
    BY_WEEK = "by_week"
    BY_CONTEXT = "by_context"
    FLAT = "flat"


class JourneyTimelineEntry(BaseModel):
    """A single entry in the timeline view.

    Combines data from ContextJourneyEntry, BreadcrumbJourney steps,
    highlights, and other sources into a unified timeline format.
    """

    id: str
    timestamp: datetime

    # Entry classification
    entry_type: TimelineEntryType
    title: str  # Human-readable title
    description: str | None = None

    # Context
    context_id: str | None = None
    context_title: str | None = None
    focus_id: str | None = None  # Question or Area ID
    focus_title: str | None = None

    # Target (what was interacted with)
    target_type: str | None = None  # "entity", "question", "highlight", "concept"
    target_id: str | None = None
    target_name: str | None = None
    target_preview: str | None = None  # Short preview text

    # Source (where this happened)
    source_type: str | None = None  # "book", "siyuan", "reader", "flow_mode"
    source_id: str | None = None
    source_title: str | None = None
    source_location: str | None = None  # chapter, page, block_id

    # Duration tracking
    dwell_time_seconds: float | None = None

    # Connections (what led to this)
    previous_entry_id: str | None = None
    related_entry_ids: list[str] = Field(default_factory=list)

    # Metadata
    entity_links: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "tle_abc123",
                "timestamp": "2025-12-09T14:30:00Z",
                "entry_type": "entity_visit",
                "title": "Explored: Executive Function",
                "description": "Examined mechanisms and neural correlates",
                "context_id": "ctx_xyz789",
                "context_title": "Understanding ADHD",
                "target_type": "entity",
                "target_id": "concept_123",
                "target_name": "Executive Function",
                "source_type": "book",
                "source_id": "book_456",
                "source_title": "Taking Charge of Adult ADHD",
                "dwell_time_seconds": 120.5,
                "entity_links": ["concept_123"],
            }
        }
    }


class TimelineGroup(BaseModel):
    """A group of timeline entries (by day, session, etc.)."""

    group_key: str  # e.g., "2025-12-09", "session_001"
    group_label: str  # Human-readable label
    start_time: datetime
    end_time: datetime | None = None
    entry_count: int
    entries: list[JourneyTimelineEntry] = Field(default_factory=list)

    # Group statistics
    entity_count: int = 0
    question_count: int = 0
    highlight_count: int = 0
    total_dwell_time: float = 0.0


class JourneyTimelineRequest(BaseModel):
    """Request parameters for timeline generation."""

    context_id: str | None = None
    focus_id: str | None = None  # Filter to specific question/area
    user_id: str | None = None

    # Time range
    start_date: datetime | None = None
    end_date: datetime | None = None

    # Grouping and filtering
    grouping: TimelineGrouping = TimelineGrouping.BY_DAY
    entry_types: list[TimelineEntryType] | None = None  # Filter by type

    # Pagination
    limit: int = 100
    offset: int = 0


class JourneyTimelineResponse(BaseModel):
    """Response containing timeline data."""

    groups: list[TimelineGroup] = Field(default_factory=list)
    total_entries: int
    total_groups: int

    # Summary statistics
    date_range: dict[str, str] = Field(default_factory=dict)  # start, end
    entry_type_counts: dict[str, int] = Field(default_factory=dict)
    contexts_involved: list[str] = Field(default_factory=list)
    total_dwell_time: float = 0.0

    model_config = {
        "json_schema_extra": {
            "example": {
                "groups": [
                    {
                        "group_key": "2025-12-09",
                        "group_label": "December 9, 2025",
                        "start_time": "2025-12-09T00:00:00Z",
                        "end_time": "2025-12-09T23:59:59Z",
                        "entry_count": 15,
                        "entity_count": 8,
                        "question_count": 3,
                        "highlight_count": 4,
                    }
                ],
                "total_entries": 15,
                "total_groups": 1,
                "entry_type_counts": {
                    "entity_visit": 8,
                    "highlight_created": 4,
                    "question_asked": 3,
                },
            }
        }
    }


class TimelineStatsResponse(BaseModel):
    """Summary statistics for a journey timeline."""

    total_entries: int
    contexts_count: int
    entities_visited: int
    questions_explored: int
    highlights_created: int
    notes_taken: int
    concepts_formalized: int
    total_dwell_time_hours: float

    # Activity over time
    entries_by_day: dict[str, int] = Field(default_factory=dict)
    most_active_context: str | None = None
    most_visited_entity: str | None = None

    # Recent activity
    last_activity: datetime | None = None
    days_active: int = 0
