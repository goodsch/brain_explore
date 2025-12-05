"""API endpoints for Flow Sessions."""

from fastapi import APIRouter, HTTPException

from ies_backend.schemas.flow_session import (
    FlowOpenRequest,
    FlowOpenResponse,
    FlowSession,
    FlowStepRequest,
    FlowSynthesisResponse,
)
from ies_backend.services.flow_session_service import FlowSessionService

router = APIRouter(prefix="/flow", tags=["flow"])


@router.post("/openFromSession", response_model=FlowOpenResponse)
async def open_flow_from_session(request: FlowOpenRequest) -> FlowOpenResponse:
    """Open a Flow session from a thinking session."""
    try:
        return await FlowSessionService.open_from_thinking_session(request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{session_id}", response_model=FlowSession)
async def get_flow_session(session_id: str) -> FlowSession:
    """Get the current state of a flow session."""
    session = await FlowSessionService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Flow session not found")
    return session


@router.post("/{session_id}/step", response_model=FlowSession)
async def record_flow_step(session_id: str, request: FlowStepRequest) -> FlowSession:
    """Record a step (breadcrumb) during flow exploration."""
    session = await FlowSessionService.record_step(session_id, request)
    if not session:
        raise HTTPException(status_code=404, detail="Flow session not found")
    return session


@router.post("/{session_id}/synthesize", response_model=FlowSynthesisResponse)
async def synthesize_flow(session_id: str) -> FlowSynthesisResponse:
    """Generate synthesis from flow journey."""
    response = await FlowSessionService.generate_synthesis(session_id)
    if not response:
        raise HTTPException(status_code=404, detail="Flow session not found")
    return response


@router.get("/{session_id}/journey", response_model=FlowSession)
async def get_flow_journey(session_id: str) -> FlowSession:
    """Get complete journey with all breadcrumbs."""
    # Journey is same as session - session includes all breadcrumbs
    session = await FlowSessionService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Flow session not found")
    return session
