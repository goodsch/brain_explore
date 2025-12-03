"""Schemas for breadcrumb journey tracking."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class EntryPointType(str, Enum):
    """How a journey was started."""

    BOOK = "book"
    SEARCH = "search"
    DASHBOARD = "dashboard"
    ENTITY = "entity"
    EXTERNAL = "external"


class MarkType(str, Enum):
    """Types of marks made during exploration."""

    HIGHLIGHT = "highlight"
    ANNOTATION = "annotation"
    QUESTION = "question"
    BOOKMARK = "bookmark"


class JourneyStep(BaseModel):
    """A single step in an exploration journey."""

    entity_id: str
    entity_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_passage: str | None = None
    source_book_id: str | None = None
    dwell_time_seconds: float = 0.0


class JourneyMark(BaseModel):
    """A mark (highlight, annotation, etc.) made during exploration."""

    type: MarkType
    entity_id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_location: str | None = None  # book:chapter:page or similar


class ThinkingPartnerExchange(BaseModel):
    """A question/response exchange with the thinking partner."""

    question: str
    response: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    entity_context: str | None = None  # Which entity prompted this


class EntryPoint(BaseModel):
    """How a journey was initiated."""

    type: EntryPointType
    reference: str  # book_id, search_query, entity_id, etc.
    context: str | None = None  # Additional context


class BreadcrumbJourney(BaseModel):
    """Complete record of an exploration journey."""

    id: str | None = None  # Assigned on save
    user_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None

    entry_point: EntryPoint
    path: list[JourneyStep] = Field(default_factory=list)
    marks: list[JourneyMark] = Field(default_factory=list)
    thinking_partner_exchanges: list[ThinkingPartnerExchange] = Field(default_factory=list)

    # Metadata
    title: str | None = None  # User-assigned or auto-generated
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None  # User reflection

    # Processing state
    processed: bool = False  # Has this journey been analyzed?
    siyuan_note_id: str | None = None  # If saved to SiYuan

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "chris",
                "entry_point": {
                    "type": "search",
                    "reference": "acceptance",
                },
                "path": [
                    {
                        "entity_id": "concept_123",
                        "entity_name": "Acceptance",
                        "dwell_time_seconds": 45.2,
                    },
                    {
                        "entity_id": "concept_456",
                        "entity_name": "Resignation",
                        "dwell_time_seconds": 30.0,
                    },
                ],
                "marks": [
                    {
                        "type": "highlight",
                        "entity_id": "concept_123",
                        "content": "Acceptance requires active engagement with reality",
                    }
                ],
            }
        }
    }


class JourneyCreateRequest(BaseModel):
    """Request to create/save a journey."""

    user_id: str
    entry_point: EntryPoint
    path: list[JourneyStep] = Field(default_factory=list)
    marks: list[JourneyMark] = Field(default_factory=list)
    thinking_partner_exchanges: list[ThinkingPartnerExchange] = Field(default_factory=list)
    title: str | None = None
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None


class JourneyCreateResponse(BaseModel):
    """Response after creating a journey."""

    id: str
    siyuan_note_id: str | None = None
    message: str = "Journey saved successfully"


class JourneyListResponse(BaseModel):
    """Response for listing journeys."""

    journeys: list[BreadcrumbJourney]
    total: int
    page: int = 1
    page_size: int = 20


class JourneyUpdateRequest(BaseModel):
    """Request to update a journey (add steps, marks, etc.)."""

    path: list[JourneyStep] | None = None  # Append to existing
    marks: list[JourneyMark] | None = None  # Append to existing
    thinking_partner_exchanges: list[ThinkingPartnerExchange] | None = None
    ended_at: datetime | None = None
    title: str | None = None
    tags: list[str] | None = None
    notes: str | None = None
