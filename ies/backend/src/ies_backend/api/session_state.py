"""Session state API for cross-app continuity.

Provides endpoints to:
- Get current session state (active context, question, reading position)
- Update session state from either frontend (IES Reader or SiYuan)
- Send heartbeats to keep session alive
- Get session history for "Resume where you left off" features
"""

from fastapi import APIRouter, HTTPException, Query

from ..schemas.session_state import (
    SessionState,
    SessionStateUpdate,
    SessionStateHistoryResponse,
    HeartbeatRequest,
    HeartbeatResponse,
)
from ..services.session_state_service import SessionStateService

router = APIRouter(tags=["session_state"])

# Service instance
session_state_service = SessionStateService()


@router.get("/{user_id}", response_model=SessionState)
async def get_session_state(user_id: str = "default_user"):
    """Get current session state for a user.

    Returns active context, question, and reading position.
    Used by both frontends to sync state on startup.

    **Example:**
    - Get state: `GET /session-state/default_user`

    **Returns:**
    - 200: Current session state
    - 404: No active session for this user
    """
    state = await session_state_service.get_state(user_id)
    if state is None:
        raise HTTPException(
            status_code=404,
            detail=f"No active session for user '{user_id}'"
        )
    return state


@router.patch("/{user_id}", response_model=SessionState)
async def update_session_state(
    user_id: str,
    update: SessionStateUpdate,
):
    """Update session state with partial updates.

    Only provided fields are updated. Use null to clear a field.
    Creates new session state if user doesn't have one yet.

    **Example requests:**

    Set active context:
    ```json
    {
      "active_context_id": "ctx_abc123"
    }
    ```

    Update reading position:
    ```json
    {
      "current_book": {
        "calibre_id": 42,
        "cfi": "epubcfi(/6/4[chapter1]!/4/2/1:0)",
        "chapter_title": "Chapter 1",
        "progress_percent": 23.5,
        "last_read_at": "2025-12-09T10:30:00Z"
      }
    }
    ```

    Clear active question:
    ```json
    {
      "active_question_id": null
    }
    ```

    **Use cases:**
    - IES Reader: Update reading position when user navigates
    - SiYuan: Set active context when user opens Context Mode
    - Both: Switch active question when user selects from dropdown
    """
    return await session_state_service.update_state(user_id, update)


@router.post("/{user_id}/heartbeat", response_model=HeartbeatResponse)
async def heartbeat(user_id: str = "default_user"):
    """Send heartbeat to update last activity timestamp.

    Frontends should call this periodically (e.g., every 5 minutes)
    to keep session alive without changing any state.

    **Example:**
    - Send heartbeat: `POST /session-state/default_user/heartbeat`

    **Returns:**
    - Updated last_activity_at timestamp
    - session_active: True if session is still active (within 30min timeout)

    **Use case:**
    - Keep session alive while user is reading or exploring
    - Detect if other frontend has taken over the session
    """
    request = HeartbeatRequest(user_id=user_id)
    return await session_state_service.heartbeat(request)


@router.get("/{user_id}/history", response_model=SessionStateHistoryResponse)
async def get_session_history(
    user_id: str = "default_user",
    limit: int = Query(20, ge=1, le=100, description="Maximum history entries"),
):
    """Get recent session state history for a user.

    Returns chronological list of state changes (context opens, question
    selections, reading progress, etc.) for "Resume" features.

    **Example:**
    - Get history: `GET /session-state/default_user/history?limit=20`

    **Use cases:**
    - Show "Recent activity" timeline
    - "Resume where you left off" suggestions
    - Understand user's exploration journey
    """
    return await session_state_service.get_history(user_id, limit)


@router.delete("/{user_id}")
async def clear_session_state(user_id: str = "default_user"):
    """Clear session state for a user.

    Records a "session_ended" history entry before clearing.

    **Example:**
    - Clear state: `DELETE /session-state/default_user`

    **Use cases:**
    - Explicit "End session" action
    - Reset state for testing

    **Returns:**
    - cleared: True if state was cleared, False if no state existed
    """
    cleared = await session_state_service.clear_state(user_id)
    return {
        "user_id": user_id,
        "cleared": cleared,
    }


@router.get("/{user_id}/is-active")
async def is_session_active(user_id: str = "default_user"):
    """Check if user has an active session (within timeout window).

    A session is considered active if there was activity within the
    last 30 minutes.

    **Example:**
    - Check active: `GET /session-state/default_user/is-active`

    **Returns:**
    - user_id: User identifier
    - active: True if session is active, False otherwise

    **Use case:**
    - Check if user is currently active before sending notifications
    - Determine if session has timed out
    """
    active = await session_state_service.is_session_active(user_id)
    return {
        "user_id": user_id,
        "active": active,
    }
