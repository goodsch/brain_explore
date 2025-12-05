"""Schemas for reframe generation and feedback endpoints."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class ReframeType(str, Enum):
    """Available reframe types that can be generated."""

    METAPHOR = "metaphor"
    ANALOGY = "analogy"
    STORY = "story"
    PATTERN = "pattern"
    CONTRAST = "contrast"


class ReframeResponse(BaseModel):
    """Response model representing a single reframe option."""

    id: str = Field(..., description="Unique identifier for the reframe suggestion")
    concept_id: str = Field(..., description="Identifier of the related concept")
    type: ReframeType = Field(..., description="Type of reframing strategy used")
    domain: str = Field(..., description="Domain/context the reframe targets")
    text: str = Field(..., description="Generated reframe text")
    strength: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Optional normalized usefulness score",
    )
    helpful_votes: int = Field(0, ge=0, description="Number of helpful votes received")
    confusing_votes: int = Field(0, ge=0, description="Number of confusing votes received")
    created_at: datetime = Field(..., description="Creation timestamp for the reframe")


class ReframeListResponse(BaseModel):
    """List response containing multiple reframes."""

    reframes: list[ReframeResponse] = Field(default_factory=list)


class GenerateReframesRequest(BaseModel):
    """Request payload for generating new reframes."""

    count: int = Field(5, ge=1, le=10, description="Desired number of reframes to generate")


class FeedbackRequest(BaseModel):
    """Feedback vote payload for a reframe."""

    vote: Literal["helpful", "confusing"]

