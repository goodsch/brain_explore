"""Schemas for non-chat source imports (web, arxiv, youtube, text)."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from .entity import ExtractionResult


class SourceType(str, Enum):
    """Supported source types."""

    WEB = "web"
    ARXIV = "arxiv"
    YOUTUBE = "youtube"
    TEXT = "text"
    FILE = "file"


class SourceImport(BaseModel):
    """Import request for a source document."""

    source_type: SourceType
    content: str = Field(description="Raw text or URL depending on type")
    title: Optional[str] = None
    topic: Optional[str] = None
    user_id: str = Field(default="system", description="Owner of the source and entities")
    extract_entities: bool = True


class SourceDocument(BaseModel):
    """Stored source document metadata."""

    id: str
    source_type: SourceType
    title: Optional[str] = None
    topic: Optional[str] = None
    uri: Optional[str] = None
    imported_at: datetime
    entity_count: int = 0
    content: str
    entities: list[str] = Field(default_factory=list)


class SourceImportResponse(BaseModel):
    """Response after importing a source."""

    document: SourceDocument
    extraction: ExtractionResult | None = None


class SourceListResponse(BaseModel):
    """List wrapper for sources."""

    sources: list[SourceDocument] = Field(default_factory=list)
