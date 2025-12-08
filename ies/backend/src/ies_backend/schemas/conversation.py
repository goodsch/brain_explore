"""Schemas for importing and querying AI chat conversations."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from .entity import ExtractionResult


class ConversationSource(str, Enum):
    """Supported conversation sources."""

    CLAUDE = "claude"
    CHATGPT = "chatgpt"
    TEXT = "text"
    URL = "url"


class ConversationTurn(BaseModel):
    """Single conversation turn."""

    role: str = Field(description="Role of the speaker (user|assistant|system)")
    text: str = Field(description="Content of the turn")
    timestamp: Optional[datetime] = Field(default=None, description="Optional timestamp if available")


class ConversationImport(BaseModel):
    """Import request for a conversation transcript."""

    source: ConversationSource
    content: str = Field(description="Raw content, JSON export, or URL depending on source")
    topic: Optional[str] = None
    extract_entities: bool = True
    create_sparks: bool = False
    user_id: str = Field(default="system", description="Owner of the conversation and entities")


class ConversationSession(BaseModel):
    """Stored conversation session metadata."""

    id: str
    source: ConversationSource
    topic: Optional[str] = None
    imported_at: datetime
    turn_count: int
    entity_count: int = 0
    transcript: Optional[str] = None
    turns: list[ConversationTurn] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)


class ConversationImportResponse(BaseModel):
    """Response after importing a conversation."""

    session: ConversationSession
    extraction: ExtractionResult | None = None


class ConversationListResponse(BaseModel):
    """List wrapper for conversations."""

    conversations: list[ConversationSession] = Field(default_factory=list)
