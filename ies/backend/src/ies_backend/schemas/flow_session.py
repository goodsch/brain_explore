"""Schemas for Flow Mode session integration."""

from enum import Enum
from pydantic import BaseModel, Field

from ies_backend.schemas.thinking import Breadcrumb


class FlowOriginType(str, Enum):
    """Entry point for a flow session."""

    THINKING_SESSION_NOTE = "thinking-session-note"
    SPARK = "spark"
    CONCEPT = "concept"


class FlowOrigin(BaseModel):
    """Origin metadata for flow session."""

    type: FlowOriginType
    siyuan_note_id: str | None = Field(default=None, alias="siyuanNoteId")
    capture_id: str | None = Field(default=None, alias="captureId")
    concept_id: str | None = Field(default=None, alias="conceptId")

    model_config = {"populate_by_name": True}


class GraphNode(BaseModel):
    """Lightweight graph node representation."""

    id: str
    label: str | None = None


class GraphEdge(BaseModel):
    """Lightweight graph edge representation."""

    id: str
    source: str
    target: str
    type: str | None = None


class RecommendedPath(BaseModel):
    """Suggested traversal path for the flow canvas."""

    id: str
    name: str
    nodes: list[str]


class FlowInitialView(BaseModel):
    """Initial canvas view for Flow."""

    center_node: str | None = Field(default=None, alias="centerNode")
    neighbor_nodes: list[GraphNode] = Field(default_factory=list, alias="neighborNodes")
    edges: list[GraphEdge] = Field(default_factory=list)
    recommended_paths: list[RecommendedPath] = Field(default_factory=list, alias="recommendedPaths")

    model_config = {"populate_by_name": True}


class FlowSession(BaseModel):
    """Flow session state."""

    id: str
    origin: FlowOrigin
    visited_nodes: list[str] = Field(default_factory=list, alias="visitedNodes")
    visited_edges: list[str] = Field(default_factory=list, alias="visitedEdges")
    breadcrumbs: list[Breadcrumb] = Field(default_factory=list)
    insights: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class FlowOpenRequest(BaseModel):
    """Request to open Flow from a thinking session."""

    thinking_session_id: str = Field(alias="thinkingSessionId")

    model_config = {"populate_by_name": True}


class FlowOpenResponse(BaseModel):
    """Response when opening Flow."""

    flow_session: FlowSession = Field(alias="flowSession")
    initial_view: FlowInitialView = Field(alias="initialView")

    model_config = {"populate_by_name": True}


class FlowStepRequest(BaseModel):
    """Record a flow step (breadcrumb)."""

    node_id: str | None = Field(default=None, alias="nodeId")
    edge_id: str | None = Field(default=None, alias="edgeId")
    from_spark: str | None = Field(default=None, alias="fromSpark")
    user_note: str | None = Field(default=None, alias="userNote")
    summary: str | None = None

    model_config = {"populate_by_name": True}


class FlowSynthesisResponse(BaseModel):
    """Response after synthesizing a flow session."""

    synthesis: str
    flow_session: FlowSession = Field(alias="flowSession")

    model_config = {"populate_by_name": True}


# ============ Orientation Phase Schemas ============


class Strand(BaseModel):
    """A potential exploration path suggested during orientation."""

    id: str
    name: str  # e.g., "The Shame Loop", "Executive Pathway"
    description: str
    starting_entities: list[str] = Field(default_factory=list, alias="startingEntities")

    model_config = {"populate_by_name": True}


class EntitySummary(BaseModel):
    """Lightweight entity info for orientation display."""

    id: str
    name: str
    type: str | None = None
    summary: str | None = None
    connection_count: int = Field(default=0, alias="connectionCount")

    model_config = {"populate_by_name": True}


class OrientationRequest(BaseModel):
    """Request to generate strand proposals from spark context."""

    spark_type: str = Field(alias="sparkType")  # note, selection, highlight, thought
    user_id: str = Field(alias="userId")

    # Context fields (at least one required)
    note_id: str | None = Field(default=None, alias="noteId")
    note_title: str | None = Field(default=None, alias="noteTitle")
    text: str | None = None  # Selected text or thought content
    block_ids: list[str] | None = Field(default=None, alias="blockIds")
    book_id: str | None = Field(default=None, alias="bookId")
    location: str | None = None  # e.g., page, chapter

    model_config = {"populate_by_name": True}


class OrientationResponse(BaseModel):
    """Response with extracted entities and suggested exploration strands."""

    extracted_entities: list[EntitySummary] = Field(
        default_factory=list, alias="extractedEntities"
    )
    suggested_strands: list[Strand] = Field(
        default_factory=list, alias="suggestedStrands"
    )

    model_config = {"populate_by_name": True}
