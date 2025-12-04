"""Schemas for personal knowledge graph entities (ADHD-friendly ontology)."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ResonanceSignal(str, Enum):
    """Emotional resonance signals for ADHD-friendly retrieval."""

    CURIOUS = "curious"
    EXCITED = "excited"
    SURPRISED = "surprised"
    MOVED = "moved"
    DISTURBED = "disturbed"
    UNCLEAR = "unclear"
    CONNECTED = "connected"
    VALIDATED = "validated"


class EnergyLevel(str, Enum):
    """Energy level for mood-appropriate navigation."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EntityStatus(str, Enum):
    """Non-judgmental lifecycle status."""

    CAPTURED = "captured"
    EXPLORING = "exploring"
    ANCHORED = "anchored"


class CreateSparkRequest(BaseModel):
    """Request to create a spark (raw resonance capture)."""

    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    resonance_signal: ResonanceSignal | None = None
    energy_level: EnergyLevel = EnergyLevel.MEDIUM
    source_id: str | None = None  # Optional link to domain concept
    concept_ids: list[str] = Field(default_factory=list)  # Related concepts
    siyuan_block_id: str | None = None  # SiYuan block reference

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Connection between EF and shame",
                "content": "Reading Barkley - realized shame blocks executive function access",
                "resonance_signal": "surprised",
                "energy_level": "medium",
                "source_id": "concept_executive_function",
            }
        }
    }


class SparkResponse(BaseModel):
    """Response containing a spark entity."""

    id: str
    title: str
    content: str
    resonance_signal: ResonanceSignal | None = None
    energy_level: EnergyLevel
    status: EntityStatus
    source_id: str | None = None
    concept_ids: list[str] = Field(default_factory=list)
    siyuan_block_id: str | None = None
    visit_count: int = 0
    created_at: datetime
    updated_at: datetime | None = None


class PromoteSparkRequest(BaseModel):
    """Request to promote a spark to an insight."""

    insight_title: str | None = None  # Override title if provided
    additional_context: str | None = None  # Extra context for the insight
    thread_id: str | None = None  # Link to exploration thread


class InsightResponse(BaseModel):
    """Response containing an insight entity."""

    id: str
    title: str
    content: str
    original_spark_id: str
    resonance_signal: ResonanceSignal | None = None
    energy_level: EnergyLevel
    status: EntityStatus
    concept_ids: list[str] = Field(default_factory=list)
    thread_id: str | None = None
    siyuan_block_id: str | None = None
    created_at: datetime


class SparkListResponse(BaseModel):
    """List of sparks."""

    sparks: list[SparkResponse]
    total: int


class PersonalStatsResponse(BaseModel):
    """Statistics for personal knowledge graph."""

    total_sparks: int
    total_insights: int
    total_threads: int
    total_favorite_problems: int
    sparks_by_status: dict[str, int]
    sparks_by_resonance: dict[str, int]
    recent_activity_count: int  # Last 7 days
