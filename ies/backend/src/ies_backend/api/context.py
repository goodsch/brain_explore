"""API endpoints for Context + Question Layer."""

from fastapi import APIRouter, HTTPException

from ies_backend.schemas.context import (
    Context,
    ContextCreateRequest,
    ContextCreateResponse,
    ContextListResponse,
    ContextNoteParseRequest,
    ContextNoteParseResponse,
    ContextSearchRequest,
    ContextSearchResponse,
    ContextStatus,
    JourneyEntryCreateRequest,
    JourneyListResponse,
    Question,
    QuestionCreateRequest,
    QuestionListResponse,
)
from ies_backend.services.context_service import ContextService

router = APIRouter(prefix="/context", tags=["context"])


# -----------------------------------------------------------------------------
# Context Endpoints
# -----------------------------------------------------------------------------


@router.post("/parse", response_model=ContextNoteParseResponse)
async def parse_context_note(request: ContextNoteParseRequest) -> ContextNoteParseResponse:
    """Parse a SiYuan Context Note into structured data.

    Takes markdown content and extracts:
    - Context metadata (title, type, summary)
    - Key Questions
    - Areas of Exploration
    - Core Concepts
    """
    return ContextService.parse_context_note(request)


@router.post("/save-parsed", response_model=Context)
async def save_parsed_context(request: ContextNoteParseRequest) -> Context:
    """Parse and save a Context Note to Neo4j.

    Convenience endpoint that parses + saves in one call.
    """
    parsed = ContextService.parse_context_note(request)
    return await ContextService.save_parsed_context(parsed)


@router.post("", response_model=ContextCreateResponse)
async def create_context(request: ContextCreateRequest) -> ContextCreateResponse:
    """Create a new context."""
    return await ContextService.create_context(request)


@router.get("", response_model=ContextListResponse)
async def list_contexts(status: ContextStatus | None = None) -> ContextListResponse:
    """List all contexts, optionally filtered by status."""
    return await ContextService.list_contexts(status)


@router.get("/{context_id}", response_model=Context)
async def get_context(context_id: str) -> Context:
    """Get a context by ID."""
    context = await ContextService.get_context(context_id)
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    return context


# -----------------------------------------------------------------------------
# Question Endpoints
# -----------------------------------------------------------------------------


@router.post("/{context_id}/questions", response_model=Question)
async def create_question(context_id: str, request: QuestionCreateRequest) -> Question:
    """Create a new question in a context."""
    if request.context_id != context_id:
        request.context_id = context_id
    return await ContextService.create_question(request)


@router.get("/{context_id}/questions", response_model=QuestionListResponse)
async def list_questions(context_id: str) -> QuestionListResponse:
    """List all questions for a context."""
    return await ContextService.get_questions(context_id)


@router.get("/questions/{question_id}", response_model=Question)
async def get_question(question_id: str) -> Question:
    """Get a question by ID."""
    question = await ContextService.get_question(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


# -----------------------------------------------------------------------------
# Search Endpoints
# -----------------------------------------------------------------------------


@router.post("/{context_id}/search", response_model=ContextSearchResponse)
async def search_in_context(context_id: str, request: ContextSearchRequest) -> ContextSearchResponse:
    """Search for relevant snippets within a context.

    Uses keywords from the context and optional focus (question/area)
    to find relevant passages across the library.
    """
    if request.context_id != context_id:
        request.context_id = context_id
    return await ContextService.search_for_context(request)


# -----------------------------------------------------------------------------
# Journey Endpoints
# -----------------------------------------------------------------------------


@router.post("/{context_id}/journey", response_model=JourneyListResponse)
async def log_journey_entry(context_id: str, request: JourneyEntryCreateRequest) -> JourneyListResponse:
    """Log a journey entry and return recent entries."""
    if request.context_id != context_id:
        request.context_id = context_id
    await ContextService.log_journey_entry(request)
    return await ContextService.get_journey_entries(context_id, request.focus_id)


@router.get("/{context_id}/journey", response_model=JourneyListResponse)
async def get_journey_entries(
    context_id: str, focus_id: str | None = None, limit: int = 50
) -> JourneyListResponse:
    """Get journey entries for a context."""
    return await ContextService.get_journey_entries(context_id, focus_id, limit)
