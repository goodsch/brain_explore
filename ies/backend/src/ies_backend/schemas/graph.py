"""Graph API schemas for Layer 3 exploration."""

from pydantic import BaseModel, Field


# === Explore Endpoint ===

class GraphNode(BaseModel):
    """A node in the knowledge graph."""

    name: str
    type: str = Field(description="Node type (Concept, Researcher, Theory, etc.)")
    labels: list[str] = Field(default_factory=list, description="All node labels")


class GraphRelationship(BaseModel):
    """A relationship between nodes."""

    start: str = Field(description="Source node name")
    type: str = Field(description="Relationship type (COMPONENT_OF, SUPPORTS, etc.)")
    end: str = Field(description="Target node name")


class ExploreResponse(BaseModel):
    """Response from exploring a concept."""

    concept: str
    nodes: list[GraphNode] = Field(default_factory=list)
    relationships: list[GraphRelationship] = Field(default_factory=list)


# === Search Endpoint ===

class SearchResult(BaseModel):
    """A search result."""

    name: str
    type: str
    score: float = Field(description="Relevance score (0-1)")


class SearchResponse(BaseModel):
    """Response from searching concepts."""

    query: str
    results: list[SearchResult] = Field(default_factory=list)


# === Sources Endpoint ===

class SourceChunk(BaseModel):
    """A source text chunk supporting a concept."""

    text: str
    book: str
    author: str | None = None
    chapter: str | None = None


class SourcesResponse(BaseModel):
    """Response from getting sources for a concept."""

    concept: str
    sources: list[SourceChunk] = Field(default_factory=list)


# === Stats Endpoint ===

class GraphStats(BaseModel):
    """Knowledge graph statistics."""

    entities: int = Field(description="Total entity count")
    relationships: int = Field(description="Total relationship count")
    books: int = Field(description="Number of books indexed")
    node_counts: dict[str, int] = Field(
        default_factory=dict, description="Count by node type"
    )
    relationship_counts: dict[str, int] = Field(
        default_factory=dict, description="Count by relationship type"
    )


# === Suggestions Endpoint ===

class SuggestedTopic(BaseModel):
    """A suggested topic for exploration."""

    name: str
    type: str = Field(description="Why suggested: recent, connected, or new")
    score: float | None = Field(
        default=None, description="Relevance or connection score"
    )


class SuggestionsResponse(BaseModel):
    """Response with suggested exploration topics."""

    recent: list[SuggestedTopic] = Field(
        default_factory=list, description="Recently explored topics"
    )
    connected: list[SuggestedTopic] = Field(
        default_factory=list, description="Most connected topics"
    )
    new: list[SuggestedTopic] = Field(
        default_factory=list, description="New or less explored topics"
    )


# === Thinking Partner Endpoint ===

class ThinkingPartnerRequest(BaseModel):
    """Request for a thinking partner question."""

    concept: str = Field(description="Current concept being explored")
    path: list[str] = Field(
        default_factory=list, description="Exploration path so far"
    )
    related: list[str] = Field(
        default_factory=list, description="Related concepts visible"
    )


class ThinkingPartnerResponse(BaseModel):
    """Response with a thinking partner question."""

    question: str = Field(description="Clarifying question to deepen exploration")
