"""Entity schemas for knowledge graph extraction."""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class EntityKind(str, Enum):
    """Type of entity."""

    IDEA = "idea"
    PERSON = "person"
    PROCESS = "process"
    QUESTION = "question"
    TENSION = "tension"


class EntityDomain(str, Enum):
    """Domain context for entity."""

    THERAPY = "therapy"
    PERSONAL = "personal"
    META = "meta"


class EntityStatus(str, Enum):
    """Development status of entity."""

    SEED = "seed"
    DEVELOPING = "developing"
    SOLID = "solid"


class ConnectionType(str, Enum):
    """Type of connection between entities."""

    SUPPORTS = "supports"
    TENSIONS = "tensions"
    DEVELOPS = "develops"


class EntityConnection(BaseModel):
    """Connection to another entity."""

    to: str = Field(description="Name of target entity")
    relationship: ConnectionType


class ExtractedEntity(BaseModel):
    """Entity extracted from session transcript."""

    name: str
    kind: EntityKind
    domain: EntityDomain
    status: EntityStatus
    description: str
    quotes: list[str] = Field(default_factory=list, description="Exact quotes from transcript")
    connections: list[EntityConnection] = Field(default_factory=list)


class SessionSummary(BaseModel):
    """Summary of session content."""

    key_insights: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    threads_explored: list[str] = Field(default_factory=list)


class ExtractionResult(BaseModel):
    """Result of entity extraction from transcript."""

    entities: list[ExtractedEntity] = Field(default_factory=list)
    session_summary: SessionSummary = Field(default_factory=SessionSummary)


class SessionProcessRequest(BaseModel):
    """Request to process a session transcript."""

    user_id: str
    transcript: str
    session_title: str | None = None
    session_date: str | None = None


class SessionProcessResponse(BaseModel):
    """Response from session processing."""

    session_doc_id: str | None = None
    entities_created: list[str] = Field(default_factory=list)
    entities_updated: list[str] = Field(default_factory=list)
    literature_links: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Map of entity names to chunk IDs linked from literature",
    )
    summary: SessionSummary


# Session Context schemas for Phase 4

class RecentSession(BaseModel):
    """Summary of a recent session for context loading."""

    date: str
    topic: str
    entities: list[str] = Field(default_factory=list)
    hanging_question: str | None = None


class ActiveEntity(BaseModel):
    """Entity being actively developed."""

    name: str
    status: EntityStatus
    kind: EntityKind
    last_updated: str | None = None


class SessionContext(BaseModel):
    """Context loaded at session start."""

    profile_summary: str
    capacity: int | None = None
    recent_sessions: list[RecentSession] = Field(default_factory=list)
    active_entities: list[ActiveEntity] = Field(default_factory=list)


# Entity Page Data schemas

class LiteratureLink(BaseModel):
    """A link to source literature."""

    chunk_id: str
    content: str
    source_file: str
    chapter: str | None = None
    score: float


class EntityConnection(BaseModel):
    """A connection to another entity."""

    name: str
    relationship: str
    kind: EntityKind
    status: EntityStatus
    description: str


class EntityPageData(BaseModel):
    """Full entity data for rendering a SiYuan page."""

    # Core entity info
    name: str
    kind: EntityKind
    domain: EntityDomain
    status: EntityStatus
    description: str
    quotes: list[str] = Field(default_factory=list)

    # Metadata
    created_at: str | None = None
    updated_at: str | None = None
    session_ids: list[str] = Field(default_factory=list)

    # Connected entities
    connections: list[EntityConnection] = Field(default_factory=list)

    # Literature grounding
    literature: list[LiteratureLink] = Field(default_factory=list)


# Session Start/Chat schemas for Plugin API

class SessionStartRequest(BaseModel):
    """Request to start a new session."""

    user_id: str


class SessionStartResponse(BaseModel):
    """Response from starting a session."""

    session_id: str
    profile_summary: str
    recent_context: str | None = None
    greeting: str


class ChatMessage(BaseModel):
    """A single chat message."""

    role: str = Field(description="'user' or 'assistant'")
    content: str


class SessionChatRequest(BaseModel):
    """Request for a chat turn."""

    session_id: str
    message: str
    messages: list[ChatMessage] = Field(default_factory=list, description="Full conversation history")


class SessionEndRequest(BaseModel):
    """Request to end a session."""

    session_id: str
    user_id: str
    transcript: list[ChatMessage]
    session_title: str | None = None


class SessionEndResponse(BaseModel):
    """Response from ending a session."""

    doc_id: str | None = None
    entities_extracted: int = 0
    summary: str | None = None
