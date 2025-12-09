"""Passage ranking schemas for question-driven reading."""

from pydantic import BaseModel, Field


class RankedPassage(BaseModel):
    """A text passage ranked by relevance to a question.

    Represents a chunk of text from a book with metadata about its
    relevance and source attribution.
    """

    chunk_id: str = Field(..., description="Unique identifier for this chunk")
    text: str = Field(..., description="The passage text")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")

    # Source attribution
    source_id: str | None = Field(None, description="Calibre ID or source identifier")
    source_title: str | None = Field(None, description="Book or source title")
    source_author: str | None = Field(None, description="Book author")

    # Optional location info
    chapter: str | None = Field(None, description="Chapter or section")
    page: int | None = Field(None, description="Page number if available")

    # Matching details
    keywords_matched: list[str] = Field(default_factory=list, description="Keywords found in this passage")
    concepts_mentioned: list[str] = Field(default_factory=list, description="Concepts mentioned in this passage")


class PassageRankingRequest(BaseModel):
    """Request for passage ranking."""

    max_passages: int = Field(10, ge=1, le=100, description="Maximum passages to return")
    min_score: float = Field(0.1, ge=0.0, le=1.0, description="Minimum relevance score")
    source_ids: list[str] | None = Field(None, description="Optional: limit to specific sources")


class PassageRankingResponse(BaseModel):
    """Response with ranked passages for a question."""

    question_id: str
    question_text: str
    passages: list[RankedPassage]
    total_candidates: int = Field(..., description="Total passages considered")
    keywords_used: list[str] = Field(default_factory=list, description="Keywords used for ranking")
