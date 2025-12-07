"""Session API endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ies_backend.schemas.entity import (
    ChatMessage,
    EntityConnection,
    EntityPageData,
    LiteratureLink,
    SessionChatRequest,
    SessionContext,
    SessionEndRequest,
    SessionEndResponse,
    SessionProcessRequest,
    SessionProcessResponse,
    SessionStartRequest,
    SessionStartResponse,
)
from ies_backend.schemas.entity import EntityKind, EntityDomain, EntityStatus
from ies_backend.services.chat_service import chat_service
from ies_backend.services.entity_storage_service import EntityStorageService
from ies_backend.services.session_context_service import session_context_service
from ies_backend.services.session_service import SessionService

router = APIRouter()

storage_service = EntityStorageService()
session_service = SessionService()


# Plugin API Endpoints

@router.post("/start", response_model=SessionStartResponse)
async def start_session(request: SessionStartRequest) -> SessionStartResponse:
    """Start a new IES session.

    Loads user profile, recent context, and generates a personalized greeting.

    Args:
        request: Session start request with user_id

    Returns:
        SessionStartResponse with session_id, profile_summary, recent_context, greeting
    """
    try:
        result = await chat_service.start_session(request.user_id)
        return SessionStartResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start session: {str(e)}",
        )


@router.post("/chat")
async def chat(request: SessionChatRequest):
    """Chat with the IES guide.

    Streams the assistant's response using Server-Sent Events.

    Args:
        request: Chat request with session_id, message, and conversation history

    Returns:
        StreamingResponse with SSE events
    """
    try:
        async def generate():
            async for chunk in chat_service.chat_stream(
                session_id=request.session_id,
                message=request.message,
                messages=request.messages,
            ):
                # SSE format: data: <content>\n\n
                yield f"data: {chunk}\n\n"
            # Signal end of stream
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}",
        )


@router.post("/chat-sync")
async def chat_sync(request: SessionChatRequest) -> dict:
    """Chat with the IES guide (non-streaming).

    Returns the complete response in a single JSON response.
    Used by plugin when streaming is not available.

    Args:
        request: Chat request with session_id, message, and conversation history

    Returns:
        dict with 'response' field containing the full message
    """
    try:
        # Collect all chunks into a single response
        full_response = ""
        async for chunk in chat_service.chat_stream(
            session_id=request.session_id,
            message=request.message,
            messages=request.messages,
        ):
            full_response += chunk

        return {"response": full_response}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}",
        )


@router.post("/end", response_model=SessionEndResponse)
async def end_session(request: SessionEndRequest) -> SessionEndResponse:
    """End an IES session and process the transcript.

    Extracts entities, creates session document in SiYuan, stores in Neo4j.

    Args:
        request: Session end request with transcript

    Returns:
        SessionEndResponse with doc_id, entities_extracted, summary
    """
    try:
        # Convert ChatMessage transcript to string
        transcript_text = "\n".join([
            f"{msg.role.upper()}: {msg.content}"
            for msg in request.transcript
        ])

        # Use existing process_session logic
        process_request = SessionProcessRequest(
            user_id=request.user_id,
            transcript=transcript_text,
            session_title=request.session_title,
            session_id=request.session_id,
            template_id=request.template_id,
            section_responses=request.section_responses,
            journey_id=request.journey_id,
        )

        # Process via existing flow
        response = await process_session(process_request)

        # Cleanup session from Redis
        await chat_service.end_session(request.session_id)

        return SessionEndResponse(
            doc_id=response.session_doc_id,
            entities_extracted=len(response.entities_created) + len(response.entities_updated),
            summary=response.summary.key_insights[0] if response.summary.key_insights else None,
            # Enhanced fields for concept extraction flow
            entities_created=response.entities_created,
            entities_updated=response.entities_updated,
            key_insights=response.summary.key_insights,
            open_questions=response.summary.open_questions,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to end session: {str(e)}",
        )


@router.post("/process", response_model=SessionProcessResponse)
async def process_session(request: SessionProcessRequest) -> SessionProcessResponse:
    """Process a session transcript.

    1. Extract entities via Claude API
    2. Generate session document in SiYuan
    3. Store entities in Neo4j
    4. Return summary

    Args:
        request: Session processing request with transcript and metadata
    """
    try:
        return await session_service.process_session(request)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Session processing failed: {str(e)}",
        )


@router.get("/entities/{user_id}")
async def get_user_entities(user_id: str, limit: int = 50) -> list[dict]:
    """Get all entities for a user.

    Args:
        user_id: User ID
        limit: Maximum entities to return
    """
    try:
        entities = await storage_service.get_user_entities(user_id, limit)
        return entities
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve entities: {str(e)}",
        )


@router.get("/entities/{user_id}/{entity_name}/graph")
async def get_entity_graph(
    user_id: str, entity_name: str, depth: int = 2
) -> dict:
    """Get an entity and its connected entities.

    Args:
        user_id: User ID
        entity_name: Name of central entity
        depth: How many hops to traverse (default 2)
    """
    try:
        graph = await storage_service.get_entity_graph(user_id, entity_name, depth)
        return graph
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve entity graph: {str(e)}",
        )


# Phase 4: Session Context endpoint

@router.get("/context/{user_id}", response_model=SessionContext)
async def get_session_context(user_id: str) -> SessionContext:
    """Get session context for session start.

    Returns profile summary, capacity, recent sessions, and active entities.
    Used by /explore-session command to load context at session start.

    Args:
        user_id: User ID
    """
    try:
        context = await session_context_service.get_context(user_id)
        return context
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load session context: {str(e)}",
        )


@router.get("/entities/{user_id}/{entity_name}/page-data", response_model=EntityPageData)
async def get_entity_page_data(user_id: str, entity_name: str) -> EntityPageData:
    """Get full entity data for rendering a SiYuan page.

    Returns entity details, connected entities, and literature links.
    Used by plugin or Claude Code to create entity pages on-demand.

    Args:
        user_id: User ID
        entity_name: Name of the entity
    """
    from ies_backend.services.neo4j_client import Neo4jClient

    try:
        # Get entity details
        entity_query = """
        MATCH (e:Entity {user_id: $user_id, name: $name})
        RETURN e
        """
        entity_results = await Neo4jClient.execute_query(
            entity_query, {"user_id": user_id, "name": entity_name}
        )

        if not entity_results:
            raise HTTPException(status_code=404, detail=f"Entity '{entity_name}' not found")

        entity = entity_results[0]["e"]

        # Get connected entities
        connections_query = """
        MATCH (e:Entity {user_id: $user_id, name: $name})-[r:RELATES_TO]-(other:Entity)
        RETURN other.name as name, r.type as relationship,
               other.kind as kind, other.status as status, other.description as description
        """
        connections_results = await Neo4jClient.execute_query(
            connections_query, {"user_id": user_id, "name": entity_name}
        )

        connections = [
            EntityConnection(
                name=c["name"],
                relationship=c["relationship"] or "relates_to",
                kind=EntityKind(c["kind"]),
                status=EntityStatus(c["status"]),
                description=c["description"] or "",
            )
            for c in connections_results
        ]

        # Get literature links
        literature_query = """
        MATCH (e:Entity {user_id: $user_id, name: $name})-[r:GROUNDED_IN]->(c:Chunk)
        RETURN c.chunk_id as chunk_id, c.content as content,
               c.source_file as source_file, c.chapter as chapter, r.score as score
        ORDER BY r.score DESC
        """
        literature_results = await Neo4jClient.execute_query(
            literature_query, {"user_id": user_id, "name": entity_name}
        )

        literature = [
            LiteratureLink(
                chunk_id=lit["chunk_id"],
                content=lit["content"] or "",
                source_file=lit["source_file"] or "unknown",
                chapter=lit["chapter"],
                score=lit["score"] or 0.0,
            )
            for lit in literature_results
        ]

        return EntityPageData(
            name=entity["name"],
            kind=EntityKind(entity["kind"]),
            domain=EntityDomain(entity["domain"]),
            status=EntityStatus(entity["status"]),
            description=entity["description"] or "",
            quotes=entity.get("quotes", []),
            created_at=entity.get("created_at"),
            updated_at=entity.get("updated_at"),
            session_ids=entity.get("session_ids", []),
            connections=connections,
            literature=literature,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get entity page data: {str(e)}",
        )


# Session persistence endpoints (Redis-backed)

@router.get("/list/{user_id}")
async def list_user_sessions(user_id: str) -> list[dict]:
    """List all active sessions for a user.

    Returns session summaries with id, started_at, last_activity, and message_count.
    Sessions are stored in Redis with 24-hour TTL and expire automatically.

    Args:
        user_id: User whose sessions to list

    Returns:
        List of session summaries, sorted by last activity (most recent first)
    """
    try:
        sessions = await chat_service.list_sessions(user_id)
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list sessions: {str(e)}",
        )


@router.get("/resume/{session_id}")
async def resume_session(session_id: str) -> dict:
    """Resume an existing session.

    Returns full session context including messages for continuation.
    Extends the session TTL on access.

    Args:
        session_id: Session to resume

    Returns:
        Session data with messages for resumption
    """
    try:
        session = await chat_service.resume_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session not found or expired: {session_id}",
            )
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resume session: {str(e)}",
        )


# ForgeMode State Management (for MCP Server)


@router.get("/state/{session_id}")
async def get_session_state(session_id: str) -> dict:
    """Get full session state including ForgeMode data.

    Used by MCP server to retrieve session state for context recovery.

    Args:
        session_id: Session to retrieve

    Returns:
        Full session data including forge_mode state
    """
    try:
        session = await chat_service.get_full_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session not found or expired: {session_id}",
            )
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session state: {str(e)}",
        )


@router.post("/state/{session_id}")
async def update_session_state(session_id: str, updates: dict) -> dict:
    """Update session state with arbitrary data.

    Used by MCP server to store ForgeMode progress.

    Args:
        session_id: Session to update
        updates: Fields to merge into session

    Returns:
        Updated session data
    """
    try:
        session = await chat_service.update_session_state(session_id, updates)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session not found or expired: {session_id}",
            )
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update session state: {str(e)}",
        )
