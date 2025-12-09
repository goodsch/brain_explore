"""API endpoints for Context + Question Layer."""

from fastapi import APIRouter, HTTPException

from ies_backend.schemas.context import (
    Context,
    ContextCreateRequest,
    ContextCreateResponse,
    ContextListResponse,
    ContextNoteParseRequest,
    ContextNoteParseResponse,
    ContextNoteParseResult,
    ContextNoteValidateRequest,
    ContextNoteValidateResponse,
    ContextSearchRequest,
    ContextSearchResponse,
    ContextStatus,
    JourneyEntryCreateRequest,
    JourneyListResponse,
    Question,
    QuestionCreateRequest,
    QuestionListResponse,
)
from ies_backend.services.context_note_parser import ContextNoteParser
from ies_backend.services.context_service import ContextService

router = APIRouter(prefix="/context", tags=["context"])


# -----------------------------------------------------------------------------
# Context Note Parsing (Enhanced)
# -----------------------------------------------------------------------------


@router.post("/parse", response_model=ContextNoteParseResponse)
async def parse_context_note(request: ContextNoteParseRequest) -> ContextNoteParseResponse:
    """Parse a SiYuan Context Note into structured data.

    Takes markdown content and extracts:
    - Context metadata (title, type, summary, status from frontmatter)
    - Key Questions (with checkbox status and existing IDs)
    - Areas of Exploration
    - Core Concepts

    Example markdown format:
    ```
    ---
    context_id: ctx_abc123
    context_type: feynman_problem
    status: active
    ---

    # Feynman: Understanding Executive Function

    ## Summary / Intent
    Exploring how executive function works...

    ## Key Questions
    - [ ] What are the core components? <!-- q_abc123 -->
    - [x] How does working memory affect EF?

    ## Areas of Exploration
    - Neural mechanisms <!-- area_xyz789 -->

    ## Core Concepts
    - Executive Function
    - Working Memory
    ```
    """
    # Use legacy parser (backward compatible)
    return ContextService.parse_context_note(request)


@router.post("/parse-enhanced", response_model=ContextNoteParseResult)
async def parse_context_note_enhanced(request: ContextNoteParseRequest) -> ContextNoteParseResult:
    """Parse a Context Note with enhanced parser.

    Returns ParsedQuestion, ParsedArea, ParsedConcept objects with metadata:
    - existing_id fields for tracking
    - is_completed status for questions
    - prefix labels (Q1:, Q2:, etc.)

    Use this endpoint when you need the enhanced metadata.
    Use /parse for backward compatibility with existing clients.
    """
    result = ContextNoteParser.parse(
        markdown_content=request.markdown_content,
        siyuan_block_id=request.siyuan_block_id,
    )
    return result


@router.post("/validate", response_model=ContextNoteValidateResponse)
async def validate_context_note(request: ContextNoteValidateRequest) -> ContextNoteValidateResponse:
    """Validate a Context Note without saving.

    Parses the markdown and returns:
    - parse_result: The full parsed structure
    - is_valid: Whether parsing succeeded
    - warnings: Non-critical issues (missing sections, etc.)
    - errors: Critical parsing failures

    Use this for real-time validation in editors.
    """
    try:
        result = ContextNoteParser.parse(
            markdown_content=request.markdown_content,
            siyuan_block_id=None,
        )

        warnings = []
        errors = []

        # Check for common issues
        if not result.questions:
            warnings.append("No questions found in 'Key Questions' section")

        if not result.context.summary:
            warnings.append("No summary found in 'Summary / Intent' section")

        if not result.concepts:
            warnings.append("No concepts found in 'Core Concepts' section")

        return ContextNoteValidateResponse(
            parse_result=result,
            is_valid=True,
            warnings=warnings,
            errors=errors,
        )
    except Exception as e:
        # Parsing failed
        return ContextNoteValidateResponse(
            parse_result=ContextNoteParseResult(
                context=Context(title="Parse Failed", type="feynman_problem"),
                questions=[],
                areas=[],
                concepts=[],
            ),
            is_valid=False,
            errors=[f"Parsing failed: {str(e)}"],
        )


@router.post("/save-parsed", response_model=Context)
async def save_parsed_context(request: ContextNoteParseRequest) -> Context:
    """Parse and save a Context Note to Neo4j.

    Convenience endpoint that parses + saves in one call.
    Uses legacy parser for backward compatibility.
    """
    parsed = ContextService.parse_context_note(request)
    return await ContextService.save_parsed_context(parsed)


# -----------------------------------------------------------------------------
# Context CRUD
# -----------------------------------------------------------------------------


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
