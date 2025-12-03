"""Schemas for Quick Capture processing."""

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
