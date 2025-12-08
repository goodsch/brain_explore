"""Graph API router for Layer 3 exploration.

Provides 7 endpoints for visual knowledge graph exploration:
- GET /explore/{concept} - Related concepts and relationships
- GET /search - Concept search
- GET /sources/{concept} - Supporting text chunks
- GET /stats - Graph statistics
- GET /suggestions - Dashboard topic suggestions
- GET /entity/{name} - Rich entity details for Flow Mode EntityFocus
- POST /thinking-partner - Generate reflection question
"""

from fastapi import APIRouter, HTTPException, Query

from ies_backend.config import settings
from ies_backend.services.graph_service import GraphService
from ies_backend.schemas.graph import (
    EntityDetailsResponse,
    ExploreResponse,
    GraphNode,
    GraphRelationship,
    GraphStats,
    RelatedEntity,
    SearchResponse,
    SearchResult,
    SourceBook,
    SourceChunk,
    SourcesResponse,
    SuggestedTopic,
    SuggestionsResponse,
    ThinkingPartnerRequest,
    ThinkingPartnerResponse,
)

# Optional Anthropic for thinking partner
try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

router = APIRouter()


@router.get("/explore/{concept}", response_model=ExploreResponse)
async def explore_concept(
    concept: str,
    depth: int = Query(default=1, ge=1, le=3, description="Exploration depth (1-3)"),
) -> ExploreResponse:
    """Explore a concept and its relationships in the knowledge graph.

    Returns the concept's related nodes and the relationships between them.
    """
    try:
        related = await GraphService.find_related_concepts(concept, depth=depth)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph query failed: {e}")

    # Convert to response schema
    nodes = []
    relationships = []

    for node in related.get("nodes", []):
        name = node.get("name", "")
        if name and name.lower() != concept.lower():  # Exclude self
            labels = node.get("labels", [])
            node_type = labels[0] if labels else "Concept"
            nodes.append(GraphNode(name=name, type=node_type, labels=labels))

    for rel in related.get("relationships", []):
        relationships.append(
            GraphRelationship(
                start=rel.get("start", ""),
                type=rel.get("type", "RELATED_TO"),
                end=rel.get("end", ""),
            )
        )

    return ExploreResponse(
        concept=concept,
        nodes=nodes,
        relationships=relationships,
    )


@router.get("/search", response_model=SearchResponse)
async def search_concepts(
    q: str = Query(description="Search query"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum results"),
) -> SearchResponse:
    """Search for concepts matching a text query.

    Uses substring matching on concept names.
    """
    try:
        results = await GraphService.search_concepts(q, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

    search_results = [
        SearchResult(
            name=r["name"],
            type=r.get("type", "Concept"),
            score=1.0,  # Exact match gets full score
        )
        for r in results
    ]

    return SearchResponse(query=q, results=search_results)


@router.get("/sources/{concept}", response_model=SourcesResponse)
async def get_sources(
    concept: str,
    limit: int = Query(default=5, ge=1, le=20, description="Maximum sources"),
) -> SourcesResponse:
    """Get supporting text chunks for a concept.

    Returns passages from books that mention or discuss the concept.
    """
    try:
        chunks = await GraphService.find_supporting_chunks(concept, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Source lookup failed: {e}")

    sources = []
    for chunk in chunks:
        sources.append(
            SourceChunk(
                text=chunk.get("content", "")[:500],  # Truncate long texts
                book=chunk.get("book_title", "Unknown"),
                author=chunk.get("book_author"),
                chapter=None,
            )
        )

    return SourcesResponse(concept=concept, sources=sources)


@router.get("/stats", response_model=GraphStats)
async def get_stats() -> GraphStats:
    """Get knowledge graph statistics for the dashboard."""
    try:
        stats = await GraphService.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats query failed: {e}")

    node_counts = stats.get("nodes", {})
    rel_counts = stats.get("relationships", {})

    # Calculate totals
    total_entities = sum(node_counts.values())
    total_relationships = sum(rel_counts.values())
    book_count = node_counts.get("Book", 0)

    return GraphStats(
        entities=total_entities,
        relationships=total_relationships,
        books=book_count,
        node_counts=node_counts,
        relationship_counts=rel_counts,
    )


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions() -> SuggestionsResponse:
    """Get suggested topics for the dashboard.

    Returns:
    - recent: Recently explored topics (placeholder - needs session tracking)
    - connected: Most connected topics in the graph
    - new: Less explored or new topics
    """
    # Get most connected concepts from graph
    try:
        most_connected = await GraphService.get_most_connected(limit=5)
        connected = [
            SuggestedTopic(
                name=c["name"],
                type="connected",
                score=c.get("connections", 0) / 100,  # Normalize
            )
            for c in most_connected
        ]
    except Exception:
        connected = []

    # Static suggestions for Phase 1 concepts (new/novel)
    new = [
        SuggestedTopic(name="metabolization", type="new", score=None),
        SuggestedTopic(name="narrow window", type="new", score=None),
        SuggestedTopic(name="authentic presence", type="new", score=None),
    ]

    # Recent would come from session tracking - placeholder for now
    recent: list[SuggestedTopic] = []

    return SuggestionsResponse(
        recent=recent,
        connected=connected,
        new=new,
    )



@router.get("/entity/{name}", response_model=EntityDetailsResponse)
async def get_entity_details(name: str) -> EntityDetailsResponse:
    """Get detailed entity information for Flow Mode EntityFocus view.

    Returns rich entity details including description, related concepts,
    and source book evidence. Works with any knowledge graph node type.

    Args:
        name: Entity/concept name to look up

    Returns:
        EntityDetailsResponse with entity info, related entities, and sources

    Raises:
        HTTPException 404 if entity not found
    """
    result = await GraphService.get_entity_details(name)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Entity '{name}' not found in knowledge graph"
        )

    return EntityDetailsResponse(
        name=result["name"],
        type=result["type"],
        description=result.get("description"),
        related=[
            RelatedEntity(
                name=r["name"],
                type=r["type"],
                relationship=r["relationship"],
            )
            for r in result.get("related", [])
        ],
        source_books=[
            SourceBook(
                title=s["title"],
                author=s.get("author"),
                snippet=s.get("snippet"),
            )
            for s in result.get("source_books", [])
        ],
    )


THINKING_PARTNER_SYSTEM = """You are a thinking partner helping someone explore therapeutic concepts.
Your role is to ask one thoughtful, clarifying question that deepens their exploration.

Guidelines:
- Ask only ONE question
- Make it specific to what they just explored
- Help them connect to their own experience or thinking
- Be curious, not directive
- Keep it brief (1-2 sentences)

Do NOT:
- Explain concepts to them
- Give advice
- Ask multiple questions
- Be lengthy"""


@router.post("/thinking-partner", response_model=ThinkingPartnerResponse)
async def thinking_partner(request: ThinkingPartnerRequest) -> ThinkingPartnerResponse:
    """Generate a thinking partner question based on exploration context.

    The question helps the user reflect on their exploration path and
    connect concepts to their own experience.
    """
    if not ANTHROPIC_AVAILABLE or not settings.anthropic_api_key:
        return ThinkingPartnerResponse(
            question="What aspects of this concept resonate with your own experience?"
        )

    path_str = " → ".join(request.path[-5:]) if request.path else "just started"
    related_str = ", ".join(request.related[:5]) if request.related else "none found"

    prompt = f"""The person is exploring the concept "{request.concept}".
Their exploration path: {path_str}
Related concepts found: {related_str}

Ask ONE thoughtful question to deepen their exploration."""

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=150,
            system=THINKING_PARTNER_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        question = response.content[0].text.strip()
    except Exception:
        # Fallback to generic question
        question = f"What draws you to explore {request.concept}?"

    return ThinkingPartnerResponse(question=question)
