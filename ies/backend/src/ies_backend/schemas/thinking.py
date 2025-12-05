"""Schemas for Thinking Session service."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class Angle(BaseModel):
    """Exploration angle suggested for a thinking session."""

    id: str
    title: str
    description: str


class Breadcrumb(BaseModel):
    """A breadcrumb recorded during thinking or flow."""

    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    node_id: str | None = Field(default=None, alias="nodeId")
    edge_id: str | None = Field(default=None, alias="edgeId")
    from_spark: str | None = Field(default=None, alias="fromSpark")
    user_note: str | None = Field(default=None, alias="userNote")
    summary: str | None = None
    angle_id: str | None = Field(default=None, alias="angleId")

    model_config = {"populate_by_name": True}


class ThinkingStatus(str, Enum):
    """Lifecycle status for a thinking session."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class ThinkingSession(BaseModel):
    """State of a thinking session derived from a capture item."""

    id: str
    capture_id: str = Field(alias="captureId")
    created_at: datetime = Field(alias="createdAt")
    status: ThinkingStatus = ThinkingStatus.ACTIVE
    siyuan_note_id: str | None = Field(default=None, alias="siyuanNoteId")
    angles: list[Angle] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    breadcrumbs: list[Breadcrumb] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class ThinkingStartRequest(BaseModel):
    """Request payload to start a thinking session."""

    capture_id: str = Field(alias="captureId")

    model_config = {"populate_by_name": True}


class ThinkingStepRequest(BaseModel):
    """Record a breadcrumb during thinking."""

    node_id: str | None = Field(default=None, alias="nodeId")
    edge_id: str | None = Field(default=None, alias="edgeId")
    from_spark: str | None = Field(default=None, alias="fromSpark")
    user_note: str | None = Field(default=None, alias="userNote")
    summary: str | None = None
    angle_id: str | None = Field(default=None, alias="angleId")
    timestamp: datetime | None = None

    model_config = {"populate_by_name": True}


class ThinkingCompleteRequest(BaseModel):
    """Mark a thinking session complete."""

    summary: str | None = None
    insights: list[str] | None = None


class NoteTemplateSuggestion(BaseModel):
    """Suggested SiYuan note template."""

    title: str
    headings: list[str]


class ThinkingStartResponse(BaseModel):
    """Response when starting a thinking session."""

    session: ThinkingSession
    siyuan_template_suggestion: NoteTemplateSuggestion = Field(alias="siyuanTemplateSuggestion")

    model_config = {"populate_by_name": True}
