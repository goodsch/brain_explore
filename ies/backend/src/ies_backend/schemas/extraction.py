"""Extraction Profile schemas for context-aware entity extraction.

This module defines types for configuring targeted entity extraction
based on context and question focus.
"""

from pydantic import BaseModel, Field


class QuestionExtractionProfile(BaseModel):
    """Extraction settings specific to a question.

    Allows fine-grained control over what to extract when exploring
    a specific question within a context.
    """

    focus_concepts: list[str] = Field(
        default_factory=list,
        description="Specific concepts to prioritize for this question",
    )
    relation_types: list[str] = Field(
        default_factory=list,
        description="Relationship types to extract (e.g., 'causes', 'enables')",
    )
    depth: int = Field(
        default=1,
        ge=1,
        le=3,
        description="How many hops to follow in the knowledge graph (1-3)",
    )


class ExtractionProfile(BaseModel):
    """Profile for context-aware entity extraction.

    Defines what to extract from sources when exploring a specific context.
    Used by the extraction engine to filter and prioritize entity extraction.
    """

    context_id: str = Field(description="Context this profile applies to")
    core_concepts: list[str] = Field(
        default_factory=list,
        description="Primary concepts to extract from sources",
    )
    synonyms: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Concept -> synonyms mapping for flexible matching",
    )
    relation_types: list[str] = Field(
        default_factory=list,
        description="Relationship types to extract (e.g., 'supports', 'contradicts')",
    )
    domain_filters: list[str] = Field(
        default_factory=list,
        description="Domain tags to filter sources (e.g., 'neuroscience', 'psychology')",
    )
    question_overrides: dict[str, QuestionExtractionProfile] | None = Field(
        default=None,
        description="Question ID -> override profile for question-specific extraction",
    )


class ExtractionResult(BaseModel):
    """Result of an extraction run.

    Captures what was found during a context-aware extraction session.
    """

    context_id: str = Field(description="Context this extraction ran within")
    concepts_found: list[str] = Field(
        default_factory=list,
        description="Concepts discovered during extraction",
    )
    relations_found: list[dict] = Field(
        default_factory=list,
        description="Relationships discovered (source, target, type)",
    )
    subquestions_generated: list[str] = Field(
        default_factory=list,
        description="New questions generated from extraction insights",
    )
    sources_processed: int = Field(
        default=0,
        ge=0,
        description="Number of sources analyzed",
    )
    segments_analyzed: int = Field(
        default=0,
        ge=0,
        description="Number of text segments processed",
    )


# API Request/Response schemas for extraction endpoints

class ExtractionProfileCreate(BaseModel):
    """Request to create an extraction profile."""

    context_id: str
    core_concepts: list[str] = Field(default_factory=list)
    synonyms: dict[str, list[str]] = Field(default_factory=dict)
    relation_types: list[str] = Field(default_factory=list)
    domain_filters: list[str] = Field(default_factory=list)


class ExtractionRunRequest(BaseModel):
    """Request to run extraction for a context."""

    context_id: str
    question_id: str | None = Field(
        default=None,
        description="Optional question to focus extraction on",
    )
    source_ids: list[str] | None = Field(
        default=None,
        description="Specific sources to extract from (if None, uses context sources)",
    )
    max_segments: int | None = Field(
        default=None,
        ge=1,
        description="Maximum segments to process (for rate limiting)",
    )


class ExtractionRunResponse(BaseModel):
    """Response from running an extraction."""

    result: ExtractionResult
    journey_entry_id: str | None = Field(
        default=None,
        description="ID of journey entry recording this extraction",
    )
