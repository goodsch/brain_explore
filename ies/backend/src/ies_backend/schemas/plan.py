"""Schemas for Quick Add plan/checklist/spark generation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .entity import ExtractionResult


class PlanStep(BaseModel):
    """A timeboxed plan step."""

    description: str
    timebox_minutes: int = Field(default=10, description="Estimated timebox in minutes")
    done_criteria: Optional[str] = None
    friction_reducer: Optional[str] = None


class Plan(BaseModel):
    """ADHD-friendly plan with micro-start and friction reducers."""

    id: str
    title: str
    micro_start: str
    steps: list[PlanStep] = Field(default_factory=list)
    total_minutes: Optional[int] = None
    due: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChecklistItem(BaseModel):
    """Checklist item."""

    description: str
    done_criteria: Optional[str] = None


class Checklist(BaseModel):
    """Checklist generated from prompt."""

    id: str
    title: str
    items: list[ChecklistItem] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Spark(BaseModel):
    """Concise insight/spark."""

    id: str
    content: str
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BuildPlanRequest(BaseModel):
    """Request to build plan/checklist/spark from a prompt."""

    intent: list[str] = Field(description="plan|checklist|spark|summary")
    content: str
    duration: Optional[int] = Field(default=None, description="Target total minutes")
    due: Optional[str] = None
    source_id: Optional[str] = None
    user_id: str = "system"


class BuildPlanResponse(BaseModel):
    """Response with generated artifacts and extraction."""

    plan: Optional[Plan] = None
    checklist: Optional[Checklist] = None
    spark: Optional[Spark] = None
    extraction: Optional[ExtractionResult] = None
