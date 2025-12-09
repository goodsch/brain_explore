"""Session state schemas for cross-app continuity.

Tracks active session state across IES Reader and SiYuan plugin
to enable seamless transitions between frontends.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ReadingPosition(BaseModel):
    """Current reading position in a book.

    Uses CFI (Canonical Fragment Identifier) for precise location tracking
    within EPUB files.
    """

    calibre_id: int = Field(description="Calibre book ID")
    cfi: str = Field(description="EPUB CFI (Canonical Fragment Identifier) for precise location")
    chapter_title: Optional[str] = Field(default=None, description="Current chapter title")
    page_number: Optional[int] = Field(default=None, description="Current page number (if available)")
    progress_percent: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Reading progress as percentage (0-100)"
    )
    last_read_at: datetime = Field(default_factory=datetime.utcnow, description="When this position was last recorded")


class SessionState(BaseModel):
    """Active session state for a user across IES frontends.

    Tracks what the user is currently working on to enable
    seamless transitions between IES Reader and SiYuan plugin.
    """

    user_id: str = Field(description="User identifier")
    active_context_id: Optional[str] = Field(
        default=None,
        description="Currently active exploration context ID"
    )
    active_question_id: Optional[str] = Field(
        default=None,
        description="Currently active question ID"
    )
    current_book: Optional[ReadingPosition] = Field(
        default=None,
        description="Current reading position in a book"
    )
    last_activity_at: datetime = Field(description="When user was last active in any frontend")
    created_at: datetime = Field(description="When session state was first created")
    updated_at: datetime = Field(description="When session state was last updated")


class SessionStateUpdate(BaseModel):
    """Partial update to session state.

    All fields are optional - only provided fields will be updated.
    """

    active_context_id: Optional[str] = Field(
        default=None,
        description="Update active context (null to clear)"
    )
    active_question_id: Optional[str] = Field(
        default=None,
        description="Update active question (null to clear)"
    )
    current_book: Optional[ReadingPosition] = Field(
        default=None,
        description="Update reading position (null to clear)"
    )


class SessionStateHistory(BaseModel):
    """Historical session state for "Resume" features.

    Captures snapshots of session state over time to support
    "Resume where you left off" and "Recent activity" features.
    """

    user_id: str = Field(description="User identifier")
    context_id: Optional[str] = Field(default=None, description="Context active at this time")
    question_id: Optional[str] = Field(default=None, description="Question active at this time")
    book_position: Optional[ReadingPosition] = Field(
        default=None,
        description="Reading position at this time"
    )
    timestamp: datetime = Field(description="When this state was recorded")
    change_type: str = Field(
        description="What changed: 'context_opened', 'question_selected', 'book_opened', 'reading_progress', 'session_ended'"
    )


class HeartbeatRequest(BaseModel):
    """Heartbeat to update last activity timestamp."""

    user_id: str = Field(default="default_user", description="User identifier")


class HeartbeatResponse(BaseModel):
    """Response to heartbeat request."""

    user_id: str
    last_activity_at: datetime
    session_active: bool = Field(
        description="True if session is still considered active (within timeout window)"
    )


class SessionStateHistoryResponse(BaseModel):
    """Response with list of historical session states."""

    user_id: str
    history: list[SessionStateHistory] = Field(
        description="Recent session state changes, newest first"
    )
    total: int = Field(description="Total history entries for user")
