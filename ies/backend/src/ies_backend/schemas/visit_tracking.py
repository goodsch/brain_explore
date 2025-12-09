"""Visit tracking schemas for "New since last run" functionality.

Tracks when users last visited contexts, books, and entities
to surface new content since their last session.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class VisitScope(str, Enum):
    """Scope of what was visited."""

    CONTEXT = "context"  # A specific context
    BOOK = "book"  # A specific book
    ENTITY = "entity"  # A specific entity
    GLOBAL = "global"  # Global "last active" timestamp


class VisitRecord(BaseModel):
    """Record of when a user last visited a scope.

    Used to track "new since last visit" for contexts, books, entities.
    """

    user_id: str = Field(description="User identifier (default: 'default_user')")
    scope: VisitScope = Field(description="What was visited")
    scope_id: str = Field(description="ID of the visited item (context_id, book_id, entity_name, or 'global')")
    last_visited_at: datetime = Field(description="When the visit occurred")


class RecordVisitRequest(BaseModel):
    """Request to record a visit."""

    user_id: str = Field(default="default_user", description="User identifier")
    scope: VisitScope = Field(description="What was visited")
    scope_id: str = Field(description="ID of the visited item")


class RecordVisitResponse(BaseModel):
    """Response after recording a visit."""

    visit_record: VisitRecord
    previous_visit: datetime | None = Field(
        default=None,
        description="Previous visit timestamp if it existed"
    )


class NewItemsSummary(BaseModel):
    """Summary of new items since last visit."""

    scope: VisitScope
    scope_id: str
    last_visited_at: datetime | None = Field(
        default=None,
        description="When user last visited this scope (None = never visited)"
    )
    new_entities: int = Field(default=0, description="New entities created")
    new_highlights: int = Field(default=0, description="New highlights added")
    new_questions: int = Field(default=0, description="New questions created")
    new_relationships: int = Field(default=0, description="New relationships formed")
    new_journey_entries: int = Field(default=0, description="New journey entries logged")


class NewItemsDetailRequest(BaseModel):
    """Request for detailed list of new items."""

    user_id: str = Field(default="default_user", description="User identifier")
    scope: VisitScope = Field(description="What scope to check")
    scope_id: str = Field(description="ID of the scope")
    limit: int = Field(default=50, ge=1, le=500, description="Max items to return")


class NewEntity(BaseModel):
    """A new entity created since last visit."""

    name: str
    type: str
    created_at: datetime
    source: str | None = Field(default=None, description="Where it came from")


class NewHighlight(BaseModel):
    """A new highlight created since last visit."""

    id: str
    book_id: str
    text: str
    created_at: datetime
    context_id: str | None = None


class NewQuestion(BaseModel):
    """A new question created since last visit."""

    id: str
    text: str
    context_id: str
    created_at: datetime
    status: str


class NewRelationship(BaseModel):
    """A new relationship created since last visit."""

    source: str
    relationship_type: str
    target: str
    created_at: datetime


class NewItemsDetailResponse(BaseModel):
    """Detailed list of new items since last visit."""

    scope: VisitScope
    scope_id: str
    last_visited_at: datetime | None
    entities: list[NewEntity] = Field(default_factory=list)
    highlights: list[NewHighlight] = Field(default_factory=list)
    questions: list[NewQuestion] = Field(default_factory=list)
    relationships: list[NewRelationship] = Field(default_factory=list)
    total_new_items: int = Field(description="Total count of all new items")


class GlobalActivitySummary(BaseModel):
    """Summary of all new activity across the system."""

    last_active_at: datetime | None = Field(
        default=None,
        description="When user was last active globally (None = first time)"
    )
    new_entities_total: int = Field(default=0)
    new_highlights_total: int = Field(default=0)
    new_questions_total: int = Field(default=0)
    new_contexts_total: int = Field(default=0)
    active_contexts: list[str] = Field(
        default_factory=list,
        description="Context IDs with new activity"
    )
