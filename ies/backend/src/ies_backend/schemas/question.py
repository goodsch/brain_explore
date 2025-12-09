"""Question schemas for the Context + Question layer."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class QuestionStatus(str, Enum):
    """Question resolution status."""
    OPEN = "open"
    PARTIAL = "partial"
    ANSWERED = "answered"
    MODELED = "modeled"


class QuestionSource(str, Enum):
    """Where the question originated."""
    SIYUAN = "siyuan"
    READER = "reader"
    AI_SUGGESTED = "ai-suggested"
    DIALOGUE = "dialogue"


class QuestionBase(BaseModel):
    """Base question fields."""
    context_id: str
    text: str = Field(..., min_length=1, max_length=2000)
    parent_question_id: str | None = None
    status: QuestionStatus = QuestionStatus.OPEN
    source: QuestionSource = QuestionSource.READER
    siyuan_block_id: str | None = None


class QuestionCreate(QuestionBase):
    """Schema for creating a question."""
    pass


class QuestionUpdate(BaseModel):
    """Schema for updating a question."""
    text: str | None = Field(None, min_length=1, max_length=2000)
    status: QuestionStatus | None = None
    parent_question_id: str | None = None
    prerequisite_questions: list[str] | None = None
    related_concepts: list[str] | None = None
    linked_sources: list[str] | None = None
    siyuan_block_id: str | None = None


class Question(QuestionBase):
    """Full question with all fields."""
    id: str
    prerequisite_questions: list[str] = []
    related_concepts: list[str] = []
    linked_sources: list[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnswerBlockBase(BaseModel):
    """Base answer block fields."""
    question_id: str
    content: str = Field(..., min_length=1)
    quality: str = "draft"  # draft, good_enough, polished


class AnswerBlockCreate(AnswerBlockBase):
    """Schema for creating an answer block."""
    pass


class AnswerBlock(AnswerBlockBase):
    """Full answer block."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
