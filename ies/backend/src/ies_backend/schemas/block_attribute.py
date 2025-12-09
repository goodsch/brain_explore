"""Block Attribute System schemas for SiYuan integration.

This module defines schemas for querying and managing SiYuan block attributes
(custom-* prefixed metadata) that link SiYuan documents to backend entities.

Block attributes enable:
- Cross-app entity linking via be_id
- AI-powered content processing via type/status
- ADHD-friendly navigation via resonance/energy
- Journey tracking across documents
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class BlockType(str, Enum):
    """IES block types stored in custom-be_type attribute."""

    SPARK = "spark"
    INSIGHT = "insight"
    THREAD = "thread"
    SESSION = "session"
    CONCEPT = "concept"
    QUESTION = "question"
    CONTEXT = "context"
    HIGHLIGHT = "highlight"
    BOOK = "book"


class BlockStatus(str, Enum):
    """Block lifecycle status stored in custom-status attribute."""

    CAPTURED = "captured"
    EXPLORING = "exploring"
    ANCHORED = "anchored"
    ARCHIVED = "archived"


class ResonanceSignal(str, Enum):
    """Emotional resonance signals for ADHD-friendly retrieval (custom-resonance)."""

    CURIOUS = "curious"
    EXCITED = "excited"
    SURPRISED = "surprised"
    MOVED = "moved"
    DISTURBED = "disturbed"
    UNCLEAR = "unclear"
    CONNECTED = "connected"
    VALIDATED = "validated"


class EnergyLevel(str, Enum):
    """Energy level for mood-appropriate access (custom-energy)."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# -----------------------------------------------------------------------------
# Core Block Attribute Model
# -----------------------------------------------------------------------------


class BlockAttribute(BaseModel):
    """SiYuan block attributes (custom-* prefixed metadata).

    Maps SiYuan document blocks to backend entities for cross-app integration.
    """

    # SiYuan identifiers
    block_id: str  # SiYuan block ID (primary key in SiYuan)
    notebook_id: str | None = None

    # Backend linking (required for cross-app sync)
    be_type: BlockType | None = None  # custom-be_type
    be_id: str | None = None  # custom-be_id (backend entity UUID)

    # Lifecycle
    status: BlockStatus | None = None  # custom-status

    # ADHD-friendly metadata
    resonance: ResonanceSignal | None = None  # custom-resonance
    energy: EnergyLevel | None = None  # custom-energy

    # Additional attributes (for specific block types)
    context_id: str | None = None  # custom-context (active Context)
    source_id: str | None = None  # custom-source (source reference)
    source_cfi: str | None = None  # custom-source-cfi (epub location)

    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "block_id": "20251209143000-abc123",
                "notebook_id": "20251201113102-ctr4bco",
                "be_type": "spark",
                "be_id": "spark_20251209_x7y8z9",
                "status": "captured",
                "resonance": "surprised",
                "energy": "medium",
                "context_id": "ctx_feynman_m2n3o4",
            }
        }
    }


# -----------------------------------------------------------------------------
# Query Schemas
# -----------------------------------------------------------------------------


class BlockAttributeQuery(BaseModel):
    """Query parameters for searching blocks by attributes."""

    be_type: BlockType | None = None
    be_id: str | None = None
    status: BlockStatus | None = None
    resonance: ResonanceSignal | None = None
    energy: EnergyLevel | None = None
    context_id: str | None = None
    notebook_id: str | None = None

    # Pagination
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class BlockAttributeListResponse(BaseModel):
    """Response containing list of block attributes."""

    blocks: list[BlockAttribute]
    total: int


# -----------------------------------------------------------------------------
# Update Schemas
# -----------------------------------------------------------------------------


class BlockAttributeUpdate(BaseModel):
    """Update block attributes (all fields optional)."""

    be_type: BlockType | None = None
    be_id: str | None = None
    status: BlockStatus | None = None
    resonance: ResonanceSignal | None = None
    energy: EnergyLevel | None = None
    context_id: str | None = None
    source_id: str | None = None
    source_cfi: str | None = None


class BlockAttributeUpdateResponse(BaseModel):
    """Response after updating block attributes."""

    block_id: str
    updated_fields: list[str]
    success: bool


# -----------------------------------------------------------------------------
# Statistics Schemas
# -----------------------------------------------------------------------------


class BlockAttributeStats(BaseModel):
    """Statistics about block attributes in the system."""

    total_blocks: int
    blocks_by_type: dict[str, int] = Field(default_factory=dict)
    blocks_by_status: dict[str, int] = Field(default_factory=dict)
    blocks_by_resonance: dict[str, int] = Field(default_factory=dict)
    blocks_by_energy: dict[str, int] = Field(default_factory=dict)
    blocks_with_backend_link: int  # Has be_id
    blocks_without_backend_link: int  # Missing be_id
