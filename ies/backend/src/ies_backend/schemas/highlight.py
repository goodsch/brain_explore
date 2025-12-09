"""Schemas for reader highlights."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class HighlightColor(str, Enum):
    """Standard highlight colors."""

    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    PINK = "pink"
    PURPLE = "purple"


class SyncStatus(str, Enum):
    """Sync status for highlights."""

    PENDING = "pending"
    SYNCED = "synced"
    ERROR = "error"
    MODIFIED = "modified"


class NoteType(str, Enum):
    """Note type classification."""

    THOUGHT = "thought"
    QUESTION = "question"
    INSIGHT = "insight"
    CLARIFICATION = "clarification"


class HighlightCreate(BaseModel):
    """Request to create a highlight."""

    book_id: str  # Calibre ID as string
    text: str
    cfi: str  # EPUB CFI location
    note: str | None = None
    color: HighlightColor = HighlightColor.YELLOW
    context_id: str | None = None  # Related context/question
    chapter: str | None = None  # Chapter title if available
    note_type: NoteType | None = None  # Optional note classification
    question_id: str | None = None  # Link to question if relevant


class Highlight(BaseModel):
    """A reader highlight with full metadata."""

    id: str
    book_id: str
    book_title: str | None = None
    book_author: str | None = None
    text: str
    cfi: str
    note: str | None = None
    color: HighlightColor = HighlightColor.YELLOW
    context_id: str | None = None
    chapter: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = False  # Has entity extraction been run?
    entity_refs: list[str] = Field(default_factory=list)  # Extracted entity names
    siyuan_block_id: str | None = None  # If synced to SiYuan

    # New sync-related fields
    sync_status: SyncStatus = SyncStatus.PENDING
    sync_error: str | None = None
    synced_at: datetime | None = None
    note_type: NoteType | None = None
    question_id: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "hl_001",
                "book_id": "8",
                "book_title": "Atomic Habits",
                "text": "Habits are the compound interest of self-improvement.",
                "cfi": "/6/4[chap01]!/4/2/1:0",
                "note": "Great metaphor for habit formation",
                "color": "yellow",
                "chapter": "The Fundamentals",
                "sync_status": "synced",
                "note_type": "insight",
            }
        }
    }


class HighlightUpdate(BaseModel):
    """Request to update a highlight."""

    note: str | None = None
    color: HighlightColor | None = None
    context_id: str | None = None
    note_type: NoteType | None = None
    question_id: str | None = None


class HighlightResponse(BaseModel):
    """Response after creating/updating a highlight."""

    highlight: Highlight
    message: str = "Highlight saved"
    siyuan_synced: bool = False


class HighlightListResponse(BaseModel):
    """Response for listing highlights."""

    highlights: list[Highlight]
    total: int
    book_id: str | None = None


class HighlightBatchCreate(BaseModel):
    """Request to sync multiple highlights at once."""

    book_id: str
    highlights: list[HighlightCreate]


class HighlightBatchResponse(BaseModel):
    """Response after batch highlight sync."""

    created: int
    updated: int
    errors: list[str] = Field(default_factory=list)
    message: str = "Highlights synced"


class SyncResult(BaseModel):
    """Result of syncing a single highlight."""

    highlight_id: str
    success: bool
    siyuan_block_id: str | None = None
    error: str | None = None


class BatchSyncResult(BaseModel):
    """Result of batch syncing highlights."""

    book_id: str
    total: int
    synced: int
    failed: int
    results: list[SyncResult]


class SyncStatusResponse(BaseModel):
    """Summary of sync status."""

    total_highlights: int
    synced: int
    pending: int
    error: int
    modified: int
    book_id: str | None = None
