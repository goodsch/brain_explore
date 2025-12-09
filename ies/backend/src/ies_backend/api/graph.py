"""Graph API router for Layer 3 exploration.

Provides 12 endpoints for visual knowledge graph exploration:
- GET /explore/{concept} - Related concepts and relationships
- GET /search - Concept search
- GET /sources/{concept} - Supporting text chunks
- GET /stats - Graph statistics
- GET /suggestions - Dashboard topic suggestions
- GET /entity/{name} - Rich entity details for Flow Mode EntityFocus
- GET /entity/{name}/facets - Facets for entity drilling (AI-generated if empty)
- GET /entity/{name}/evidence - Evidence passages from source materials
- GET /entity/{name}/questions - AI-generated questions for entity exploration (Sprint 4)
- POST /entity - Create entity from facet exploration
- POST /thinking-partner - Generate reflection question
- POST /clarify - Guided clarification before facet decomposition (Sprint 4)
"""

from fastapi import APIRouter, HTTPException, Query

from ies_backend.config import settings
from ies_backend.services.graph_service import GraphService
from ies_backend.schemas.graph import (
    ClarificationRequest,
    ClarificationResponse,
    CreateEntityRequest,
    CreateEntityResponse,
    EntityDetailsResponse,
    EntityEvidenceResponse,
    EntityFacetsResponse,
    EntityQuestionsResponse,
    EvidencePassage,
    ExploreResponse,
    ExtractedQuestion,
    Facet,
    FacetEntity,
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


@router.get("/entity/{name}/facets", response_model=EntityFacetsResponse)
async def get_entity_facets(
    name: str,
    generate: bool = Query(
        default=True,
        description="Generate facets via AI if none exist"
    ),
    refresh: bool = Query(
        default=False,
        description="Force regenerate facets (deletes existing)"
    ),
) -> EntityFacetsResponse:
    """Get facets for an entity to enable categorical drilling in Flow Mode.

    Facets are thematic groupings of related concepts (e.g., ADHD might have
    facets like "Diagnosis", "Neurobiology", "Treatment"). This enables
    entity → facet → sub-entity exploration.

    If no facets exist and `generate=True`, AI will generate them automatically.
    Use `refresh=True` to force regeneration of facets.

    Args:
        name: Entity name to get facets for
        generate: If True, generate facets via AI when none exist
        refresh: If True, delete existing facets and regenerate

    Returns:
        EntityFacetsResponse with list of facets and their entities

    Raises:
        HTTPException 404 if entity not found
    """
    result = await GraphService.get_entity_facets(
        entity_name=name,
        generate_if_empty=generate,
        force_regenerate=refresh,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Entity '{name}' not found in knowledge graph"
        )

    return EntityFacetsResponse(
        entity_name=result["entity_name"],
        entity_type=result["entity_type"],
        facets=[
            Facet(
                name=f["name"],
                description=f.get("description"),
                entity_count=f["entity_count"],
                entities=[
                    FacetEntity(
                        name=e["name"],
                        type=e["type"],
                        relationship=e.get("relationship", "BELONGS_TO"),
                    )
                    for e in f.get("entities", [])
                ],
            )
            for f in result.get("facets", [])
        ],
        generated=result.get("generated", False),
    )


@router.get("/entity/{name}/evidence", response_model=EntityEvidenceResponse)
async def get_entity_evidence(
    name: str,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum evidence passages to return"
    ),
    include_book_mentions: bool = Query(
        default=True,
        description="Include book-level mentions when chunks are sparse"
    ),
) -> EntityEvidenceResponse:
    """Get evidence passages for an entity from source materials.

    Returns text passages from books that mention or discuss this entity.
    Evidence comes from two sources:
    1. Chunks: Extracted text with explicit entity mentions (high confidence)
    2. Books: Book-level mentions when chunk data is sparse (lower confidence)

    Evidence includes location info (chapter, CFI) for jump-back to IES Reader.

    Args:
        name: Entity name to find evidence for
        limit: Maximum passages to return (1-100)
        include_book_mentions: Include book mentions when chunks sparse

    Returns:
        EntityEvidenceResponse with evidence passages and metadata
    """
    result = await GraphService.get_entity_evidence(
        entity_name=name,
        limit=limit,
        include_book_mentions=include_book_mentions,
    )

    return EntityEvidenceResponse(
        entity_name=result["entity_name"],
        evidence=[
            EvidencePassage(
                id=e["id"],
                text=e["text"],
                source_title=e["source_title"],
                source_author=e.get("source_author"),
                location=e.get("location"),
                confidence=e.get("confidence", 1.0),
                source_type=e.get("source_type", "chunk"),
            )
            for e in result.get("evidence", [])
        ],
        total_count=result.get("total_count", 0),
        sources_searched=result.get("sources_searched", 0),
    )


@router.post("/entity", response_model=CreateEntityResponse)
async def create_entity(request: CreateEntityRequest) -> CreateEntityResponse:
    """Create a new entity from facet/graph exploration.

    When exploring facets, clicking on a facet that doesn't exist as an entity
    triggers creation. The new entity is linked to its parent and facet.

    This enables the graph to grow organically from exploration.

    Args:
        request: Entity creation details including name, type, parent, facet

    Returns:
        CreateEntityResponse with entity info and whether newly created

    Raises:
        HTTPException 500 if creation fails
    """
    try:
        result = await GraphService.create_entity_from_exploration(
            name=request.name,
            entity_type=request.entity_type,
            parent_entity=request.parent_entity,
            facet_name=request.facet_name,
            description=request.description,
        )

        return CreateEntityResponse(
            name=result["name"],
            entity_type=result["entity_type"],
            created=result["created"],
            parent_entity=result.get("parent_entity"),
            facet_name=result.get("facet_name"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create entity: {e}"
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


@router.get("/entity/{name}/questions", response_model=EntityQuestionsResponse)
async def get_entity_questions(
    name: str,
    generate: bool = Query(
        default=True,
        description="Generate questions via AI if none exist"
    ),
) -> EntityQuestionsResponse:
    """Get questions for exploring an entity (Sprint 4: Questions + Clarification).

    Returns a list of questions that would help understand this entity deeply.
    Questions are classified by type (why, how, what, when, who, where, which).
    If `generate=True` and no cached questions exist, AI will generate them.

    This endpoint enables the question extraction from facet decomposition
    workflow, providing AI-generated questions to guide exploration.

    Args:
        name: Entity name to get questions for
        generate: If True, generate questions via AI when none exist

    Returns:
        EntityQuestionsResponse with list of extracted questions

    Raises:
        HTTPException 404 if entity not found
    """
    # First verify entity exists
    entity_result = await GraphService.get_entity_details(name)
    if entity_result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Entity '{name}' not found in knowledge graph"
        )

    entity_type = entity_result.get("type", "Concept")

    if not generate:
        # Return empty if not generating
        return EntityQuestionsResponse(
            entity_name=name,
            entity_type=entity_type,
            questions=[],
            generated=False,
        )

    # Get entity facets for context (if available)
    facets_result = await GraphService.get_entity_facets(
        entity_name=name,
        generate_if_empty=False,  # Don't auto-generate facets
        force_regenerate=False,
    )

    facets = facets_result.get("facets", []) if facets_result else []

    # Generate questions using AI
    result = await GraphService.generate_questions_for_entity(
        entity_name=name,
        entity_type=entity_type,
        facets=facets,
        persist=False,  # Don't persist for now (in-memory cache later)
    )

    return EntityQuestionsResponse(
        entity_name=result["entity_name"],
        entity_type=result["entity_type"],
        questions=[
            ExtractedQuestion(
                text=q["text"],
                question_type=q["question_type"],
                related_concepts=q.get("related_concepts", []),
            )
            for q in result.get("questions", [])
        ],
        generated=result.get("generated", False),
    )


@router.post("/clarify", response_model=ClarificationResponse)
async def get_clarification(request: ClarificationRequest) -> ClarificationResponse:
    """Get guided clarification before facet decomposition (Sprint 4).

    This endpoint provides a dialogue to help users articulate what they
    want to understand about an entity before diving into exploration.
    Returns a clarifying question, suggested facets, prerequisites, and context.

    Use this to implement the "clarification dialogue before facet generation"
    flow in the UI.

    Args:
        request: ClarificationRequest with entity_name and optional user_goal

    Returns:
        ClarificationResponse with clarifying question and guidance

    Raises:
        HTTPException 404 if entity not found
    """
    # Verify entity exists (optional - could allow clarification for new topics)
    entity_result = await GraphService.get_entity_details(request.entity_name)
    if entity_result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Entity '{request.entity_name}' not found in knowledge graph"
        )

    # Generate clarification dialogue
    result = await GraphService.generate_clarification(
        entity_name=request.entity_name,
        user_goal=request.user_goal,
    )

    return ClarificationResponse(
        entity_name=result["entity_name"],
        clarifying_question=result["clarifying_question"],
        suggested_facets=result.get("suggested_facets", []),
        prerequisites=result.get("prerequisites", []),
        why_it_matters=result.get("why_it_matters"),
    )
