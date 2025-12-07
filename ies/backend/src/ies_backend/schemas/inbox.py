"""Schemas for Quick Inbox processing and inbox queue management."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class InboxType(str, Enum):
    """Type of inbox content."""

    TEXT = "text"
    VOICE = "voice"  # Transcribed audio
    IMAGE = "image"  # OCR'd text from image
    LINK = "link"    # Fetched and summarized URL


class PlacementType(str, Enum):
    """Where to place the inbox content."""

    NOTE = "note"           # Append to existing note
    CONCEPT = "concept"     # Link to concept/entity
    JOURNEY = "journey"     # Associate with journey
    NEW_NOTE = "new_note"   # Create new note


class DialogueRole(str, Enum):
    """Role in a dialogue message."""

    ASSISTANT = "assistant"
    USER = "user"


class DialogueSuggestion(BaseModel):
    """A suggestion offered by the assistant in dialogue."""

    label: str
    action: str  # e.g., "link_to_concept", "create_note", "explore_in_flow"
    target_id: str | None = Field(default=None, alias="targetId")
    target_name: str | None = Field(default=None, alias="targetName")
    confidence: float = 0.5

    model_config = {"populate_by_name": True}


class DialogueMessage(BaseModel):
    """A message in the collaborative processing dialogue."""

    role: DialogueRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    suggestions: list[DialogueSuggestion] | None = None  # For assistant messages

    model_config = {"populate_by_name": True}


class ExtractedEntity(BaseModel):
    """An entity extracted from inbox content."""

    name: str
    type: str  # concept, person, theory, etc.
    confidence: float = Field(ge=0.0, le=1.0)
    graph_match: bool = False  # Whether entity exists in knowledge graph


class SuggestedPlacement(BaseModel):
    """A suggested placement for the inbox content."""

    target_type: PlacementType
    target_id: str | None = None  # Note ID, concept ID, or journey ID
    target_name: str | None = None  # Human-readable name
    confidence: float = Field(ge=0.0, le=1.0)
    preview: str  # How the content would appear if placed here
    rationale: str  # Why this placement is suggested


class InboxProcessRequest(BaseModel):
    """Request to process inbox content."""

    content: str
    type: InboxType = Field(default=InboxType.TEXT, alias="inbox_type")
    context: dict | None = None  # Optional context (current note, journey, etc.)

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "content": "Just realized acceptance isn't about giving up - it's about engaging with what is. This connects to the metabolization idea.",
                "inbox_type": "text",
                "context": {
                    "current_note_id": "note_123",
                    "current_journey_id": "journey_456",
                },
            }
        }
    }


class InboxProcessResponse(BaseModel):
    """Response from processing inbox content."""

    extracted_entities: list[ExtractedEntity] = Field(serialization_alias="entities")
    suggested_placements: list[SuggestedPlacement] = Field(serialization_alias="placements")
    summary: str | None = None  # AI-generated summary of the content
    tags: list[str] = Field(default_factory=list, serialization_alias="suggested_tags")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "entities": [
                    {"name": "Acceptance", "type": "concept", "confidence": 0.95},
                    {"name": "Metabolization", "type": "concept", "confidence": 0.8},
                ],
                "placements": [
                    {
                        "target_type": "note",
                        "target_id": "note_123",
                        "target_name": "Acceptance vs Resignation",
                        "confidence": 0.85,
                        "preview": "...existing content...\n\n## New Insight\nJust realized acceptance isn't about giving up...",
                        "rationale": "Content relates directly to the acceptance concept in this note",
                    }
                ],
                "summary": "Insight about acceptance as active engagement rather than resignation",
                "suggested_tags": ["acceptance", "metabolization", "insight"],
            }
        }
    }


class InboxRouteRequest(BaseModel):
    """Request to route inbox content to a specific location."""

    inbox_id: str  # From previous process response
    placement: SuggestedPlacement  # Selected placement


class InboxRouteResponse(BaseModel):
    """Response after routing inbox content."""

    success: bool
    target_id: str
    message: str


# ============================================================================
# Flow Mode Inbox Queue Schemas
# ============================================================================


class InboxStatus(str, Enum):
    """Status of an inbox item."""

    QUEUED = "queued"
    IN_THINKING = "in_thinking"
    INTEGRATED = "integrated"


class InboxSource(str, Enum):
    """Source of an inbox item (where the capture originated)."""

    # Primary external sources
    IOS_SHORTCUT = "ios_shortcut"
    BROWSER = "browser"
    VOICE = "voice"
    EMAIL = "email"

    # App sources
    SIYUAN = "siyuan"
    IES_READER = "ies_reader"

    # Legacy (backward compatibility)
    PHONE = "phone"  # Maps to ios_shortcut
    READEST = "readest"  # Maps to ies_reader
    ASSISTANT_INTERRUPTION = "assistant_interruption"


class SparkType(str, Enum):
    """Type of the spark that triggered inbox."""

    NOTE = "note"
    SELECTION = "selection"
    HIGHLIGHT = "highlight"
    THOUGHT = "thought"


class SparkSource(BaseModel):
    """Origin metadata for a spark."""

    type: str
    note_id: str | None = Field(default=None, alias="noteId")
    block_ids: list[str] | None = Field(default=None, alias="blockIds")
    book_id: str | None = Field(default=None, alias="bookId")
    location: str | None = None

    model_config = {"populate_by_name": True}


class Spark(BaseModel):
    """A spark is the live piece of context Flow latches onto."""

    id: str
    type: SparkType
    text: str
    source: SparkSource
    captured_at: datetime = Field(alias="capturedAt")

    model_config = {"populate_by_name": True}


class AutoExtracted(BaseModel):
    """Automatically extracted metadata for an inbox item."""

    entities: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)


class InboxItem(BaseModel):
    """Inbox queue item stored in Neo4j."""

    id: str
    raw_text: str = Field(alias="rawText")
    source: InboxSource
    captured_at: datetime = Field(alias="capturedAt")
    status: InboxStatus = InboxStatus.QUEUED
    context_snippet: str | None = Field(default=None, alias="contextSnippet")
    auto_extracted: AutoExtracted | None = Field(default=None, alias="autoExtracted")
    spark: Spark | None = None
    dialogue: list[DialogueMessage] = Field(default_factory=list)

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "id": "inbox_123",
                "rawText": "Flow doesn't start from zero...",
                "source": "assistant_interruption",
                "capturedAt": "2025-12-05T10:30:00Z",
                "status": "queued",
                "contextSnippet": "During discussion about architecture",
                "autoExtracted": {
                    "entities": ["entry-point dependence"],
                    "topics": ["ADHD", "tool-design"],
                },
                "dialogue": [],
            }
        },
    }


class InboxCreateRequest(BaseModel):
    """Request to create an inbox item."""

    raw_text: str = Field(alias="rawText")
    source: InboxSource
    context_snippet: str | None = Field(default=None, alias="contextSnippet")
    auto_extracted: AutoExtracted | None = Field(default=None, alias="autoExtracted")
    spark: Spark | None = None

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "rawText": "Flow doesn't start from zero...",
                "source": "assistant-interruption",
                "contextSnippet": "During discussion about architecture",
                "autoExtracted": {
                    "entities": ["entry-point dependence", "choice paralysis"],
                    "topics": ["ADHD", "tool-design"],
                },
            }
        },
    }


class InboxUpdateRequest(BaseModel):
    """Request to update an inbox item."""

    status: InboxStatus | None = None
    auto_extracted: AutoExtracted | None = Field(default=None, alias="autoExtracted")

    model_config = {"populate_by_name": True}


class InboxListResponse(BaseModel):
    """Response wrapper for a list of inbox items."""

    items: list[InboxItem]
    total: int


class DialogueMessageRequest(BaseModel):
    """Request to add a user message to inbox dialogue."""

    content: str = Field(min_length=1, max_length=2000)


class DialogueResponse(BaseModel):
    """Response from adding a message (includes AI response)."""

    user_message: DialogueMessage = Field(alias="userMessage")
    assistant_message: DialogueMessage = Field(alias="assistantMessage")
    inbox_item: InboxItem = Field(alias="inboxItem")

    model_config = {"populate_by_name": True}


class ResolutionAction(str, Enum):
    """Action to take when resolving an inbox item."""

    LINK_TO_CONCEPT = "link_to_concept"
    CREATE_NOTE = "create_note"
    ADD_TO_NOTE = "add_to_existing_note"
    EXPLORE_IN_FLOW = "explore_in_flow"
    LINK_TO_JOURNEY = "link_to_journey"


class ResolveRequest(BaseModel):
    """Request to resolve an inbox item to a destination."""

    action: ResolutionAction
    target_id: str | None = Field(default=None, alias="targetId")
    target_name: str | None = Field(default=None, alias="targetName")

    model_config = {"populate_by_name": True}


class ResolveResponse(BaseModel):
    """Response after resolving an inbox item."""

    success: bool
    action: ResolutionAction
    message: str
    target_id: str | None = Field(default=None, alias="targetId")
    target_name: str | None = Field(default=None, alias="targetName")
    note_id: str | None = Field(default=None, alias="noteId")  # If note created/modified

    model_config = {"populate_by_name": True}
