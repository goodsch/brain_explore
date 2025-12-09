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


class HighlightCreate(BaseModel):
    """Request to create a highlight."""

    book_id: str  # Calibre ID as string
    text: str
    cfi: str  # EPUB CFI location
    note: str | None = None
    color: HighlightColor = HighlightColor.YELLOW
    context_id: str | None = None  # Related context/question
    chapter: str | None = None  # Chapter title if available


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
            }
        }
    }


class HighlightUpdate(BaseModel):
    """Request to update a highlight."""

    note: str | None = None
    color: HighlightColor | None = None
    context_id: str | None = None


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
