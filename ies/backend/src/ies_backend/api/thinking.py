"""API endpoints for Thinking Sessions."""

from fastapi import APIRouter, HTTPException

from ies_backend.schemas.thinking import (
    ThinkingCompleteRequest,
    ThinkingSession,
    ThinkingStartRequest,
    ThinkingStartResponse,
    ThinkingStepRequest,
)
from ies_backend.services.thinking_service import ThinkingService

router = APIRouter(prefix="/thinking", tags=["thinking"])


@router.post("/start", response_model=ThinkingStartResponse)
async def start_thinking_session(
    request: ThinkingStartRequest,
) -> ThinkingStartResponse:
    """Start a thinking session from a capture item."""
    try:
        return await ThinkingService.start_session(request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{session_id}", response_model=ThinkingSession)
async def get_thinking_session(session_id: str) -> ThinkingSession:
    """Get the current state of a thinking session."""
    session = await ThinkingService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Thinking session not found")
    return session


@router.post("/{session_id}/step", response_model=ThinkingSession)
async def record_thinking_step(
    session_id: str, request: ThinkingStepRequest
) -> ThinkingSession:
    """Record a breadcrumb during thinking."""
    session = await ThinkingService.record_breadcrumb(session_id, request)
    if not session:
        raise HTTPException(status_code=404, detail="Thinking session not found")
    return session


@router.post("/{session_id}/complete", response_model=ThinkingSession)
async def complete_thinking_session(
    session_id: str, request: ThinkingCompleteRequest
) -> ThinkingSession:
    """Mark a thinking session complete."""
    session = await ThinkingService.complete_session(session_id, request)
    if not session:
        raise HTTPException(status_code=404, detail="Thinking session not found")
    return session
