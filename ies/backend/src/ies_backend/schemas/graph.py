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


# === Entity Details Endpoint (Phase 2A) ===


class SourceBook(BaseModel):
    """A book that mentions this entity with evidence snippet."""

    title: str
    author: str | None = None
    snippet: str | None = Field(
        default=None, description="Text snippet where entity is mentioned"
    )


class RelatedEntity(BaseModel):
    """A related entity with relationship info."""

    name: str
    type: str = Field(description="Node type (Concept, Researcher, Theory, etc.)")
    relationship: str = Field(description="Relationship type (COMPONENT_OF, SUPPORTS, etc.)")


class EntityDetailsResponse(BaseModel):
    """Rich entity details for Flow Mode EntityFocus view.

    Provides entity information, related concepts, and source evidence
    without requiring user_id (works with knowledge graph concepts).
    """

    name: str
    type: str = Field(description="Primary node type")
    description: str | None = Field(
        default=None, description="Entity description if available"
    )
    related: list[RelatedEntity] = Field(
        default_factory=list, description="1-hop related entities"
    )
    source_books: list[SourceBook] = Field(
        default_factory=list, description="Books mentioning this entity"
    )


# === Facet Schemas (Phase 2B) ===


class FacetEntity(BaseModel):
    """An entity within a facet."""

    name: str
    type: str = Field(description="Node type (Concept, Researcher, Theory, etc.)")
    relationship: str = Field(
        description="How this entity relates to the facet",
        default="BELONGS_TO"
    )


class Facet(BaseModel):
    """A thematic facet grouping related concepts under an entity.

    Facets provide categorical organization for drilling into entities.
    Example: ADHD might have facets like "Diagnosis", "Neurobiology", "Treatment".
    """

    name: str = Field(description="Facet name (e.g., 'Diagnosis & Assessment')")
    description: str | None = Field(
        default=None,
        description="Brief description of what this facet covers"
    )
    entity_count: int = Field(
        default=0,
        description="Number of entities in this facet"
    )
    entities: list[FacetEntity] = Field(
        default_factory=list,
        description="Entities belonging to this facet"
    )


class EntityFacetsResponse(BaseModel):
    """Response containing facets for an entity.

    Enables entity → facet → sub-entity drilling in Flow Mode.
    """

    entity_name: str
    entity_type: str
    facets: list[Facet] = Field(
        default_factory=list,
        description="Thematic facets for this entity"
    )
    generated: bool = Field(
        default=False,
        description="True if facets were AI-generated on this request"
    )


# === Create Entity from Facet ===

class CreateEntityRequest(BaseModel):
    """Request to create a new entity from a facet exploration."""

    name: str = Field(description="Name of the entity to create")
    entity_type: str = Field(
        default="Concept",
        description="Type of entity (Concept, Theory, Person, Method, etc.)"
    )
    parent_entity: str | None = Field(
        default=None,
        description="Parent entity this was expanded from"
    )
    facet_name: str | None = Field(
        default=None,
        description="Facet name if created from facet exploration"
    )
    description: str | None = Field(
        default=None,
        description="Initial description of the entity"
    )


class CreateEntityResponse(BaseModel):
    """Response after creating an entity."""

    name: str
    entity_type: str
    created: bool = Field(description="True if newly created, False if already existed")
    parent_entity: str | None = None
    facet_name: str | None = None


# === Evidence Endpoint (Sprint 2) ===


class EvidencePassage(BaseModel):
    """A text passage providing evidence for an entity.

    Evidence comes from two sources:
    - Chunks: Extracted text passages with explicit MENTIONS relationships
    - Books: Inferred mentions based on Book→Entity MENTIONS relationships
    """

    id: str = Field(description="Unique passage identifier (chunk_id or generated)")
    text: str = Field(description="The evidence text passage")
    source_title: str = Field(description="Book or document title")
    source_author: str | None = Field(default=None, description="Author name")
    location: dict | None = Field(
        default=None,
        description="Location info: chapter, page, CFI for jump-back"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Relevance confidence (1.0 = direct mention, <1.0 = inferred)"
    )
    source_type: str = Field(
        default="chunk",
        description="Evidence source: 'chunk' (extracted) or 'book' (inferred)"
    )


class EntityEvidenceResponse(BaseModel):
    """Response containing evidence passages for an entity.

    Enables evidence panel in Flow Mode showing source text
    with jump-back capability to IES Reader.
    """

    entity_name: str
    evidence: list[EvidencePassage] = Field(
        default_factory=list,
        description="Evidence passages ordered by confidence"
    )
    total_count: int = Field(
        default=0,
        description="Total evidence count (may exceed returned items)"
    )
    sources_searched: int = Field(
        default=0,
        description="Number of books/sources searched"
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


# === Question Extraction from Facets (Sprint 4) ===


class ExtractedQuestion(BaseModel):
    """A question extracted from facet decomposition."""

    text: str = Field(description="The question text")
    question_type: str = Field(
        default="general",
        description="Type: why, how, what, when, who, where, which, general"
    )
    related_concepts: list[str] = Field(
        default_factory=list,
        description="Concepts this question relates to"
    )


class EntityQuestionsResponse(BaseModel):
    """Response containing questions extracted for an entity."""

    entity_name: str
    entity_type: str
    questions: list[ExtractedQuestion] = Field(
        default_factory=list,
        description="Questions that emerge from exploring this entity"
    )
    generated: bool = Field(
        default=False,
        description="True if questions were AI-generated on this request"
    )


class ClarificationRequest(BaseModel):
    """Request for guided clarification before facet decomposition."""

    entity_name: str = Field(description="Entity to explore")
    user_goal: str | None = Field(
        default=None,
        description="What the user wants to understand (optional)"
    )


class ClarificationResponse(BaseModel):
    """Response with clarification dialogue to guide exploration."""

    entity_name: str
    clarifying_question: str = Field(
        description="Question to clarify user's exploration intent"
    )
    suggested_facets: list[str] = Field(
        default_factory=list,
        description="Suggested facets based on user's goal"
    )
    prerequisites: list[str] = Field(
        default_factory=list,
        description="Prerequisite concepts to understand first"
    )
    why_it_matters: str | None = Field(
        default=None,
        description="Brief explanation of why this entity matters"
    )
