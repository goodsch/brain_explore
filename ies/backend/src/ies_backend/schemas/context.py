"""Context + Question Layer schemas.

This module defines the core types for the Context-aware exploration system:
- Context: A structured place where attention lives (Feynman problems, projects, theories)
- Question: Structured unknowns within a context
- ContextJourneyEntry: Chronological trace of context-aware interactions
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ContextType(str, Enum):
    """Types of contexts that can anchor exploration."""

    FEYNMAN_PROBLEM = "feynman_problem"
    PROJECT = "project"
    THEORY = "theory"
    CONCEPT_CLUSTER = "concept_cluster"
    LIFE_AREA = "life_area"


class ContextStatus(str, Enum):
    """Lifecycle status of a context."""

    IDEA = "idea"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class QuestionStatus(str, Enum):
    """Progress status of a question."""

    OPEN = "open"
    PARTIAL = "partial"
    ANSWERED = "answered"
    MODELED = "modeled"


class JourneyClassification(str, Enum):
    """Classification tags for journey entries."""

    ANSWER_FRAGMENT = "answer_fragment"
    NEW_QUESTION = "new_question"
    CLARIFICATION = "clarification"
    TODO = "todo"
    META_STRUCTURE = "meta_structure"
    READING_NOTE = "reading_note"
    HIGHLIGHT = "highlight"
    EXTRACTION_RUN = "extraction_run"
    QUESTION_CLICK = "question_click"


# -----------------------------------------------------------------------------
# Core Types
# -----------------------------------------------------------------------------


class Context(BaseModel):
    """A structured place where attention lives.

    Examples: Feynman problem, project, theory, concept cluster, life area.
    """

    id: str | None = None  # Assigned on save
    type: ContextType = ContextType.FEYNMAN_PROBLEM
    title: str
    summary: str | None = None  # 1-2 sentence intent
    status: ContextStatus = ContextStatus.ACTIVE
    parent_context_id: str | None = None

    # Linked elements (IDs)
    key_questions: list[str] = Field(default_factory=list)
    core_concepts: list[str] = Field(default_factory=list)
    linked_sources: list[str] = Field(default_factory=list)
    areas_of_exploration: list[str] = Field(default_factory=list)

    # SiYuan integration
    siyuan_block_id: str | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Question(BaseModel):
    """A structured unknown within a context."""

    id: str | None = None  # Assigned on save
    context_id: str
    parent_question_id: str | None = None

    text: str
    status: QuestionStatus = QuestionStatus.OPEN

    # Links
    prerequisite_questions: list[str] = Field(default_factory=list)
    related_concepts: list[str] = Field(default_factory=list)
    linked_sources: list[str] = Field(default_factory=list)

    # SiYuan integration
    siyuan_block_id: str | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AreaOfExploration(BaseModel):
    """A thematic area within a context (not a question, but a direction)."""

    id: str | None = None
    context_id: str
    title: str
    description: str | None = None

    siyuan_block_id: str | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)


class ContextJourneyEntry(BaseModel):
    """A single entry in the context-aware journey trace.

    Records interactions within a context: button clicks, extractions,
    notes, highlights, AI responses, etc.
    """

    id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    context_id: str | None = None
    focus_id: str | None = None  # Question or Area ID

    # Content
    text: str | None = None
    user_message: str | None = None
    ai_message: str | None = None

    # Classification
    classifications: list[JourneyClassification] = Field(default_factory=list)

    # Links
    entity_links: list[str] = Field(default_factory=list)  # Concept IDs
    source_links: list[str] = Field(default_factory=list)  # Source IDs

    # Metadata
    source_action: str | None = None  # e.g., "flow_button_click", "reader_highlight"


# -----------------------------------------------------------------------------
# API Request/Response Schemas
# -----------------------------------------------------------------------------


class ContextCreateRequest(BaseModel):
    """Request to create a new context."""

    type: ContextType = ContextType.FEYNMAN_PROBLEM
    title: str
    summary: str | None = None
    siyuan_block_id: str | None = None


class ContextCreateResponse(BaseModel):
    """Response after creating a context."""

    context: Context
    questions_created: int = 0


class ContextListResponse(BaseModel):
    """Response listing contexts."""

    contexts: list[Context]
    total: int


class QuestionCreateRequest(BaseModel):
    """Request to create a new question."""

    context_id: str
    text: str
    parent_question_id: str | None = None


class QuestionListResponse(BaseModel):
    """Response listing questions for a context."""

    questions: list[Question]
    total: int


class ContextNoteParseRequest(BaseModel):
    """Request to parse a SiYuan Context Note."""

    siyuan_block_id: str
    markdown_content: str


class ContextNoteParseResponse(BaseModel):
    """Response from parsing a Context Note."""

    context: Context
    questions: list[Question]
    areas: list[AreaOfExploration]
    raw_sections: dict[str, list[str]] = Field(default_factory=dict)


class ContextSearchRequest(BaseModel):
    """Request to search within a context/question."""

    context_id: str
    focus_id: str | None = None  # Question or Area ID
    keywords: list[str] | None = None  # If None, derived from context/question


class ContextSearchResult(BaseModel):
    """A single search result."""

    source_id: str
    source_title: str
    snippet: str
    relevance_score: float = 0.0
    concepts_found: list[str] = Field(default_factory=list)


class ContextSearchResponse(BaseModel):
    """Response from context-aware search."""

    results: list[ContextSearchResult]
    concepts_found: list[str] = Field(default_factory=list)
    suggested_subquestions: list[str] = Field(default_factory=list)
    journey_entry_id: str | None = None


class JourneyEntryCreateRequest(BaseModel):
    """Request to log a journey entry."""

    context_id: str | None = None
    focus_id: str | None = None
    text: str | None = None
    classifications: list[JourneyClassification] = Field(default_factory=list)
    source_action: str | None = None


class JourneyListResponse(BaseModel):
    """Response listing journey entries for a context."""

    entries: list[ContextJourneyEntry]
    total: int
