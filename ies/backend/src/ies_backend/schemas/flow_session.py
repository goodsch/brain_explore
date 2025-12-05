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
