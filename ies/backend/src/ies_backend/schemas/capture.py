"""Schemas for Quick Capture processing and capture queue management."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class CaptureType(str, Enum):
    """Type of captured content."""

    TEXT = "text"
    VOICE = "voice"  # Transcribed audio
    IMAGE = "image"  # OCR'd text from image
    LINK = "link"    # Fetched and summarized URL


class PlacementType(str, Enum):
    """Where to place the captured content."""

    NOTE = "note"           # Append to existing note
    CONCEPT = "concept"     # Link to concept/entity
    JOURNEY = "journey"     # Associate with journey
    NEW_NOTE = "new_note"   # Create new note


class ExtractedEntity(BaseModel):
    """An entity extracted from captured content."""

    name: str
    type: str  # concept, person, theory, etc.
    confidence: float = Field(ge=0.0, le=1.0)


class SuggestedPlacement(BaseModel):
    """A suggested placement for the captured content."""

    target_type: PlacementType
    target_id: str | None = None  # Note ID, concept ID, or journey ID
    target_name: str | None = None  # Human-readable name
    confidence: float = Field(ge=0.0, le=1.0)
    preview: str  # How the content would appear if placed here
    rationale: str  # Why this placement is suggested


class CaptureProcessRequest(BaseModel):
    """Request to process captured content."""

    content: str
    type: CaptureType = CaptureType.TEXT
    context: dict | None = None  # Optional context (current note, journey, etc.)

    model_config = {
        "json_schema_extra": {
            "example": {
                "content": "Just realized acceptance isn't about giving up - it's about engaging with what is. This connects to the metabolization idea.",
                "type": "text",
                "context": {
                    "current_note_id": "note_123",
                    "current_journey_id": "journey_456",
                },
            }
        }
    }


class CaptureProcessResponse(BaseModel):
    """Response from processing captured content."""

    extracted_entities: list[ExtractedEntity]
    suggested_placements: list[SuggestedPlacement]
    summary: str | None = None  # AI-generated summary of the content
    tags: list[str] = Field(default_factory=list)  # Suggested tags

    model_config = {
        "json_schema_extra": {
            "example": {
                "extracted_entities": [
                    {"name": "Acceptance", "type": "concept", "confidence": 0.95},
                    {"name": "Metabolization", "type": "concept", "confidence": 0.8},
                ],
                "suggested_placements": [
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
                "tags": ["acceptance", "metabolization", "insight"],
            }
        }
    }


class CaptureRouteRequest(BaseModel):
    """Request to route captured content to a specific location."""

    capture_id: str  # From previous process response
    placement: SuggestedPlacement  # Selected placement


class CaptureRouteResponse(BaseModel):
    """Response after routing captured content."""

    success: bool
    target_id: str
    message: str


# ============================================================================
# Flow Mode Capture Queue Schemas
# ============================================================================


class CaptureStatus(str, Enum):
    """Status of a captured item."""

    QUEUED = "queued"
    IN_THINKING = "in_thinking"
    INTEGRATED = "integrated"


class CaptureSource(str, Enum):
    """Source of a captured spark."""

    PHONE = "phone"
    SIYUAN = "siyuan"
    READEST = "readest"
    ASSISTANT_INTERRUPTION = "assistant-interruption"


class SparkType(str, Enum):
    """Type of the spark that triggered capture."""

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
    """Automatically extracted metadata for a capture."""

    entities: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)


class CaptureItem(BaseModel):
    """Capture queue item stored in Neo4j."""

    id: str
    raw_text: str = Field(alias="rawText")
    source: CaptureSource
    captured_at: datetime = Field(alias="capturedAt")
    status: CaptureStatus = CaptureStatus.QUEUED
    context_snippet: str | None = Field(default=None, alias="contextSnippet")
    auto_extracted: AutoExtracted | None = Field(default=None, alias="autoExtracted")
    spark: Spark | None = None

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "id": "capture_123",
                "rawText": "Flow doesn't start from zero...",
                "source": "assistant-interruption",
                "capturedAt": "2025-12-05T10:30:00Z",
                "status": "queued",
                "contextSnippet": "During discussion about architecture",
                "autoExtracted": {
                    "entities": ["entry-point dependence"],
                    "topics": ["ADHD", "tool-design"],
                },
            }
        },
    }


class CaptureCreateRequest(BaseModel):
    """Request to create a capture item."""

    raw_text: str = Field(alias="rawText")
    source: CaptureSource
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


class CaptureUpdateRequest(BaseModel):
    """Request to update a capture item."""

    status: CaptureStatus | None = None
    auto_extracted: AutoExtracted | None = Field(default=None, alias="autoExtracted")

    model_config = {"populate_by_name": True}


class CaptureListResponse(BaseModel):
    """Response wrapper for a list of captures."""

    items: list[CaptureItem]
    total: int
