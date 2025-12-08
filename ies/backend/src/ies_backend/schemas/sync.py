"""Schemas for cross-app exploration session synchronization."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class AppSource(str, Enum):
    """Source application for exploration session."""

    READER = "reader"
    SIYUAN = "siyuan"


class SessionStatus(str, Enum):
    """Status of an exploration session."""

    ACTIVE = "active"  # Currently being explored
    PAUSED = "paused"  # User left, can resume
    COMPLETED = "completed"  # User explicitly ended


class ReadingPosition(BaseModel):
    """Reading position in a book (for Reader app)."""

    book_hash: str
    calibre_id: int | None = None
    cfi: str | None = None
    chapter: str | None = None
    progress_percent: float | None = None


class JourneyStep(BaseModel):
    """A single step in an exploration journey."""

    entity_id: str
    entity_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_passage: str | None = None
    dwell_time: float = 0.0  # seconds


class TrailItem(BaseModel):
    """Trail stack item (for SiYuan navigation)."""

    entity_id: str
    entity_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    context: dict | None = None


class ExplorationSession(BaseModel):
    """Cross-app exploration session for continuity between Reader and SiYuan."""

    id: str
    user_id: str
    app_source: AppSource
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: SessionStatus = SessionStatus.ACTIVE

    # Current state
    current_entity_id: str | None = None
    current_entity_name: str | None = None
    reading_position: ReadingPosition | None = None

    # Journey tracking
    journey_path: list[JourneyStep] = Field(default_factory=list)
    trail_stack: list[TrailItem] = Field(default_factory=list)

    # Resume hint for UI
    resume_hint: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "session_123abc",
                "user_id": "chris",
                "app_source": "reader",
                "status": "paused",
                "current_entity_id": "entity_456",
                "current_entity_name": "Acceptance",
                "reading_position": {
                    "book_hash": "abc123",
                    "calibre_id": 42,
                    "cfi": "epubcfi(/6/4[chapter01]!/4/2)",
                    "progress_percent": 35.2,
                },
                "journey_path": [
                    {
                        "entity_id": "entity_123",
                        "entity_name": "Mindfulness",
                        "dwell_time": 45.2,
                    },
                    {
                        "entity_id": "entity_456",
                        "entity_name": "Acceptance",
                        "dwell_time": 30.0,
                    },
                ],
                "resume_hint": "Resume exploring Acceptance in The Power of Now",
            }
        }
    }


class SessionCreateRequest(BaseModel):
    """Request to create or update an exploration session."""

    user_id: str
    app_source: AppSource
    status: SessionStatus = SessionStatus.ACTIVE
    current_entity_id: str | None = None
    current_entity_name: str | None = None
    reading_position: ReadingPosition | None = None
    journey_path: list[JourneyStep] = Field(default_factory=list)
    trail_stack: list[TrailItem] = Field(default_factory=list)
    resume_hint: str | None = None


class SessionUpdateRequest(BaseModel):
    """Request to update an exploration session."""

    status: SessionStatus | None = None
    current_entity_id: str | None = None
    current_entity_name: str | None = None
    reading_position: ReadingPosition | None = None
    journey_path: list[JourneyStep] | None = None
    trail_stack: list[TrailItem] | None = None
    resume_hint: str | None = None


class SessionStatusUpdateRequest(BaseModel):
    """Request to update session status only."""

    status: SessionStatus


class SessionResponse(BaseModel):
    """Response containing session data."""

    session: ExplorationSession


class SessionListResponse(BaseModel):
    """Response for listing sessions."""

    sessions: list[ExplorationSession]
    total: int


class ResumeData(BaseModel):
    """Data needed to resume a session in the target app."""

    session: ExplorationSession
    deep_link: str | None = None
    instructions: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "session": {
                    "id": "session_123",
                    "user_id": "chris",
                    "app_source": "reader",
                    "current_entity_id": "entity_456",
                    "current_entity_name": "Acceptance",
                },
                "deep_link": "siyuan://blocks/note_123?ies-session=session_123&entity=entity_456",
                "instructions": "Resume exploring Acceptance in SiYuan",
            }
        }
    }
