"""Service for managing cross-app session state.

Tracks active session state (context, question, reading position) across
IES Reader and SiYuan plugin to enable seamless transitions.

Uses in-memory storage (MVP). Will migrate to Redis later for
multi-instance support and persistence.
"""

from datetime import datetime, timedelta
from typing import Optional

from ..schemas.session_state import (
    SessionState,
    SessionStateUpdate,
    SessionStateHistory,
    SessionStateHistoryResponse,
    ReadingPosition,
    HeartbeatRequest,
    HeartbeatResponse,
)


class SessionStateService:
    """Service for cross-app session state management.

    Maintains active session state and history for each user.
    In-memory storage (MVP) - will migrate to Redis for production.
    """

    # Session timeout: 30 minutes of inactivity = session considered inactive
    SESSION_TIMEOUT = timedelta(minutes=30)

    # History retention: Keep last N state changes per user
    MAX_HISTORY_PER_USER = 100

    def __init__(self):
        # In-memory store: user_id -> SessionState
        self._states: dict[str, SessionState] = {}

        # In-memory history: user_id -> list[SessionStateHistory] (newest first)
        self._history: dict[str, list[SessionStateHistory]] = {}

    async def get_state(self, user_id: str) -> Optional[SessionState]:
        """Get current session state for a user.

        Args:
            user_id: User identifier

        Returns:
            Current session state or None if user has no active session
        """
        return self._states.get(user_id)

    async def update_state(
        self,
        user_id: str,
        update: SessionStateUpdate,
    ) -> SessionState:
        """Update session state with partial updates.

        Creates new session state if user doesn't have one yet.
        Records state changes to history for "Resume" features.

        Args:
            user_id: User identifier
            update: Partial state update (only provided fields are updated)

        Returns:
            Updated session state
        """
        now = datetime.utcnow()

        # Get or create session state
        state = self._states.get(user_id)
        if state is None:
            # Create new session state
            state = SessionState(
                user_id=user_id,
                last_activity_at=now,
                created_at=now,
                updated_at=now,
            )
            self._states[user_id] = state

        # Track what changed for history
        change_type: Optional[str] = None

        # Apply updates
        if update.active_context_id is not None:
            if state.active_context_id != update.active_context_id:
                change_type = "context_opened"
                state.active_context_id = update.active_context_id

        if update.active_question_id is not None:
            if state.active_question_id != update.active_question_id:
                change_type = "question_selected"
                state.active_question_id = update.active_question_id

        if update.current_book is not None:
            # Check if this is a new book or progress update
            if state.current_book is None:
                change_type = "book_opened"
            elif state.current_book.calibre_id != update.current_book.calibre_id:
                change_type = "book_opened"
            elif state.current_book.cfi != update.current_book.cfi:
                change_type = "reading_progress"

            state.current_book = update.current_book

        # Update timestamps
        state.last_activity_at = now
        state.updated_at = now

        # Record to history if something changed
        if change_type:
            await self._record_history(
                user_id=user_id,
                context_id=state.active_context_id,
                question_id=state.active_question_id,
                book_position=state.current_book,
                change_type=change_type,
                timestamp=now,
            )

        return state

    async def heartbeat(self, request: HeartbeatRequest) -> HeartbeatResponse:
        """Update last activity timestamp (heartbeat).

        Frontends can call this periodically to keep session active
        without changing any state.

        Args:
            request: Heartbeat request with user_id

        Returns:
            Response with updated timestamp and session active status
        """
        now = datetime.utcnow()

        # Get or create session state
        state = self._states.get(request.user_id)
        if state is None:
            state = SessionState(
                user_id=request.user_id,
                last_activity_at=now,
                created_at=now,
                updated_at=now,
            )
            self._states[request.user_id] = state
        else:
            state.last_activity_at = now
            state.updated_at = now

        # Check if session is still active (within timeout window)
        session_active = (now - state.last_activity_at) < self.SESSION_TIMEOUT

        return HeartbeatResponse(
            user_id=request.user_id,
            last_activity_at=state.last_activity_at,
            session_active=session_active,
        )

    async def get_history(
        self,
        user_id: str,
        limit: int = 20,
    ) -> SessionStateHistoryResponse:
        """Get recent session state history for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of history entries to return

        Returns:
            List of recent session state changes (newest first)
        """
        history_entries = self._history.get(user_id, [])

        return SessionStateHistoryResponse(
            user_id=user_id,
            history=history_entries[:limit],
            total=len(history_entries),
        )

    async def clear_state(self, user_id: str) -> bool:
        """Clear session state for a user.

        Records a "session_ended" history entry before clearing.

        Args:
            user_id: User identifier

        Returns:
            True if state existed and was cleared, False otherwise
        """
        state = self._states.get(user_id)
        if state is None:
            return False

        # Record session end to history
        await self._record_history(
            user_id=user_id,
            context_id=state.active_context_id,
            question_id=state.active_question_id,
            book_position=state.current_book,
            change_type="session_ended",
            timestamp=datetime.utcnow(),
        )

        # Clear state
        del self._states[user_id]
        return True

    async def is_session_active(self, user_id: str) -> bool:
        """Check if user has an active session (within timeout window).

        Args:
            user_id: User identifier

        Returns:
            True if session is active, False otherwise
        """
        state = self._states.get(user_id)
        if state is None:
            return False

        now = datetime.utcnow()
        return (now - state.last_activity_at) < self.SESSION_TIMEOUT

    async def _record_history(
        self,
        user_id: str,
        context_id: Optional[str],
        question_id: Optional[str],
        book_position: Optional[ReadingPosition],
        change_type: str,
        timestamp: datetime,
    ) -> None:
        """Record a session state change to history.

        Args:
            user_id: User identifier
            context_id: Active context at this time (if any)
            question_id: Active question at this time (if any)
            book_position: Reading position at this time (if any)
            change_type: What changed (context_opened, question_selected, etc.)
            timestamp: When the change occurred
        """
        history_entry = SessionStateHistory(
            user_id=user_id,
            context_id=context_id,
            question_id=question_id,
            book_position=book_position,
            timestamp=timestamp,
            change_type=change_type,
        )

        # Get or create history list
        if user_id not in self._history:
            self._history[user_id] = []

        # Add to front (newest first)
        self._history[user_id].insert(0, history_entry)

        # Trim to max history length
        if len(self._history[user_id]) > self.MAX_HISTORY_PER_USER:
            self._history[user_id] = self._history[user_id][:self.MAX_HISTORY_PER_USER]

    async def clear_all_states(self) -> int:
        """Clear all session states (for testing).

        Returns:
            Number of states cleared
        """
        count = len(self._states)
        self._states.clear()
        return count

    async def clear_all_history(self) -> int:
        """Clear all history (for testing).

        Returns:
            Number of users whose history was cleared
        """
        count = len(self._history)
        self._history.clear()
        return count
