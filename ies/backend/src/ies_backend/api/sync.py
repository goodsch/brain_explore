"""API endpoints for cross-app exploration session synchronization.

Enables continuity between Reader and SiYuan apps by managing shared exploration sessions.
"""

from fastapi import APIRouter, HTTPException, Query

from ..schemas.sync import (
    AppSource,
    ResumeData,
    SessionCreateRequest,
    SessionListResponse,
    SessionResponse,
    SessionStatusUpdateRequest,
    SessionUpdateRequest,
)
from ..services.sync_service import sync_service

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/sessions", response_model=SessionResponse)
async def create_or_update_session(
    request: SessionCreateRequest,
    session_id: str | None = Query(None, description="Optional session ID for updates"),
) -> SessionResponse:
    """Create a new exploration session or update an existing one.

    Use this endpoint to:
    - Create a new session when starting exploration in Reader or SiYuan
    - Update an existing session when navigating to new entities
    - Update reading position as user progresses through book
    - Add journey steps as exploration continues

    If session_id is provided and exists, updates that session.
    Otherwise, creates a new session.
    """
    session = await sync_service.create_or_update_session(request, session_id)
    return SessionResponse(session=session)


@router.get("/sessions/active", response_model=SessionListResponse)
async def get_active_sessions(
    user_id: str = Query(..., description="User ID to get sessions for"),
    include_paused: bool = Query(True, description="Include paused sessions"),
) -> SessionListResponse:
    """Get active and optionally paused sessions for a user.

    Returns sessions sorted by most recently updated first.
    Useful for displaying resumable sessions in UI.
    """
    sessions = await sync_service.get_active_sessions(user_id, include_paused)
    return SessionListResponse(sessions=sessions, total=len(sessions))


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    """Get a specific session by ID.

    Returns complete session data including journey path, trail stack,
    and reading position.
    """
    session = await sync_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(session=session)


@router.get("/sessions/{session_id}/resume", response_model=ResumeData)
async def get_resume_data(
    session_id: str,
    target_app: AppSource = Query(..., description="Target app to resume in"),
) -> ResumeData:
    """Get data needed to resume a session in the target app.

    Returns:
    - Session data
    - Deep link to open target app at correct location
    - User-friendly instructions for resuming

    Use this when user wants to switch from Reader to SiYuan or vice versa.
    """
    resume_data = await sync_service.get_resume_data(session_id, target_app)
    if not resume_data:
        raise HTTPException(status_code=404, detail="Session not found")
    return ResumeData(**resume_data)


@router.put("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str, request: SessionUpdateRequest
) -> SessionResponse:
    """Update an existing session.

    Use this to:
    - Update current entity being explored
    - Update reading position
    - Add journey steps
    - Update trail stack
    - Change session status
    """
    session = await sync_service.update_session(session_id, request)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(session=session)


@router.put("/sessions/{session_id}/status", response_model=SessionResponse)
async def update_session_status(
    session_id: str, request: SessionStatusUpdateRequest
) -> SessionResponse:
    """Update session status only.

    Convenient endpoint for pausing/resuming/completing sessions without
    sending full update payload.
    """
    session = await sync_service.update_session_status(session_id, request.status)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(session=session)


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> dict:
    """Delete a session.

    Removes the session and all associated data. Use when user explicitly
    discards a session or for cleanup of old sessions.
    """
    success = await sync_service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}
