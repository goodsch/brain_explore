"""Service for managing cross-app session state.

Tracks active session state (context, question, reading position) across
IES Reader and SiYuan plugin to enable seamless transitions.

Uses Redis for persistent storage and multi-instance support.
"""

import json
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
    JourneyTrailItem,
    ContinueExplorationResponse,
    AppSource,
)
from .redis_client import redis_client

# Max trail items to keep
MAX_TRAIL_ITEMS = 50


class SessionStateService:
    """Service for cross-app session state management.

    Maintains active session state and history for each user.
    Uses Redis for persistence across restarts and multi-instance deployments.
    """

    # Session timeout: 30 minutes of inactivity = session considered inactive
    SESSION_TIMEOUT = timedelta(minutes=30)

    # Session TTL in Redis: 24 hours (auto-cleanup of abandoned sessions)
    SESSION_TTL_SECONDS = 24 * 60 * 60

    # History retention: Keep last N state changes per user
    MAX_HISTORY_PER_USER = 100

    # Redis key prefixes
    STATE_KEY_PREFIX = "ies:session:state:"
    HISTORY_KEY_PREFIX = "ies:session:history:"

    def __init__(self):
        """Initialize service (connection happens lazily)."""
        pass

    def _state_key(self, user_id: str) -> str:
        """Get Redis key for user's session state."""
        return f"{self.STATE_KEY_PREFIX}{user_id}"

    def _history_key(self, user_id: str) -> str:
        """Get Redis key for user's history list."""
        return f"{self.HISTORY_KEY_PREFIX}{user_id}"

    def _serialize_state(self, state: SessionState) -> str:
        """Serialize session state to JSON."""
        return state.model_dump_json()

    def _deserialize_state(self, data: str) -> SessionState:
        """Deserialize session state from JSON."""
        return SessionState.model_validate_json(data)

    def _serialize_history_entry(self, entry: SessionStateHistory) -> str:
        """Serialize history entry to JSON."""
        return entry.model_dump_json()

    def _deserialize_history_entry(self, data: str) -> SessionStateHistory:
        """Deserialize history entry from JSON."""
        return SessionStateHistory.model_validate_json(data)

    async def get_state(self, user_id: str) -> Optional[SessionState]:
        """Get current session state for a user.

        Args:
            user_id: User identifier

        Returns:
            Current session state or None if user has no active session
        """
        client = await redis_client.get_client()
        data = await client.get(self._state_key(user_id))
        if data is None:
            return None
        return self._deserialize_state(data)

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
        client = await redis_client.get_client()

        # Get or create session state
        state = await self.get_state(user_id)
        if state is None:
            # Create new session state
            state = SessionState(
                user_id=user_id,
                last_activity_at=now,
                created_at=now,
                updated_at=now,
            )

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

        # Handle journey continuity fields
        if update.current_entity_id is not None:
            state.current_entity_id = update.current_entity_id

        if update.current_entity_name is not None:
            state.current_entity_name = update.current_entity_name

        if update.app_source is not None:
            state.last_app_source = update.app_source

        if update.add_trail_item is not None:
            # Add new trail item to the front (most recent first)
            state.journey_trail.insert(0, update.add_trail_item)
            # Keep only the most recent items
            state.journey_trail = state.journey_trail[:MAX_TRAIL_ITEMS]
            # Set the entity tracking automatically
            state.current_entity_id = update.add_trail_item.entity_id
            state.current_entity_name = update.add_trail_item.entity_name
            state.last_app_source = update.add_trail_item.source_app
            change_type = "entity_visited"

        # Update timestamps
        state.last_activity_at = now
        state.updated_at = now

        # Save to Redis with TTL
        await client.setex(
            self._state_key(user_id),
            self.SESSION_TTL_SECONDS,
            self._serialize_state(state),
        )

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
        client = await redis_client.get_client()

        # Get or create session state
        state = await self.get_state(request.user_id)
        if state is None:
            state = SessionState(
                user_id=request.user_id,
                last_activity_at=now,
                created_at=now,
                updated_at=now,
            )
        else:
            state.last_activity_at = now
            state.updated_at = now

        # Save to Redis with TTL refresh
        await client.setex(
            self._state_key(request.user_id),
            self.SESSION_TTL_SECONDS,
            self._serialize_state(state),
        )

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
        client = await redis_client.get_client()
        history_key = self._history_key(user_id)

        # Get total count
        total = await client.llen(history_key)

        # Get entries (stored newest first)
        raw_entries = await client.lrange(history_key, 0, limit - 1)

        history_entries = [
            self._deserialize_history_entry(entry)
            for entry in raw_entries
        ]

        return SessionStateHistoryResponse(
            user_id=user_id,
            history=history_entries,
            total=total,
        )

    async def clear_state(self, user_id: str) -> bool:
        """Clear session state for a user.

        Records a "session_ended" history entry before clearing.

        Args:
            user_id: User identifier

        Returns:
            True if state existed and was cleared, False otherwise
        """
        state = await self.get_state(user_id)
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

        # Clear state from Redis
        client = await redis_client.get_client()
        await client.delete(self._state_key(user_id))
        return True

    async def is_session_active(self, user_id: str) -> bool:
        """Check if user has an active session (within timeout window).

        Args:
            user_id: User identifier

        Returns:
            True if session is active, False otherwise
        """
        state = await self.get_state(user_id)
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

        client = await redis_client.get_client()
        history_key = self._history_key(user_id)

        # Add to front of list (LPUSH for newest first)
        await client.lpush(history_key, self._serialize_history_entry(history_entry))

        # Trim to max history length
        await client.ltrim(history_key, 0, self.MAX_HISTORY_PER_USER - 1)

        # Set TTL on history (same as session)
        await client.expire(history_key, self.SESSION_TTL_SECONDS)

    async def clear_all_states(self) -> int:
        """Clear all session states (for testing).

        Returns:
            Number of states cleared
        """
        client = await redis_client.get_client()
        keys = []
        async for key in client.scan_iter(f"{self.STATE_KEY_PREFIX}*"):
            keys.append(key)
        if keys:
            await client.delete(*keys)
        return len(keys)

    async def clear_all_history(self) -> int:
        """Clear all history (for testing).

        Returns:
            Number of users whose history was cleared
        """
        client = await redis_client.get_client()
        keys = []
        async for key in client.scan_iter(f"{self.HISTORY_KEY_PREFIX}*"):
            keys.append(key)
        if keys:
            await client.delete(*keys)
        return len(keys)

    async def get_continue_exploration(
        self,
        user_id: str,
        trail_limit: int = 10,
    ) -> ContinueExplorationResponse:
        """Get data needed to continue exploration from either app.

        Returns current state with deep links for resuming in Reader or SiYuan.

        Args:
            user_id: User identifier
            trail_limit: Max trail items to return (default 10)

        Returns:
            ContinueExplorationResponse with state and deep links
        """
        state = await self.get_state(user_id)

        if state is None:
            return ContinueExplorationResponse(
                user_id=user_id,
                has_active_exploration=False,
            )

        # Check if there's actually something to continue
        has_active = bool(
            state.current_entity_id
            or state.active_context_id
            or state.journey_trail
        )

        # Build deep links
        reader_deep_link = None
        siyuan_deep_link = None
        resume_hint = None

        if state.current_entity_id:
            # Deep link to entity in both apps
            entity_name = state.current_entity_name or state.current_entity_id

            # Reader: open with entity focus
            if state.current_book:
                reader_deep_link = (
                    f"http://localhost:5173/reader"
                    f"?calibreId={state.current_book.calibre_id}"
                    f"&entity={state.current_entity_id}"
                )
                if state.current_book.cfi:
                    reader_deep_link += f"&cfi={state.current_book.cfi}"
            else:
                reader_deep_link = (
                    f"http://localhost:5173/reader"
                    f"?entity={state.current_entity_id}"
                )

            # SiYuan: open Flow Mode with entity
            siyuan_deep_link = (
                f"siyuan://plugins/ies"
                f"?entity={state.current_entity_id}"
            )
            if state.active_context_id:
                siyuan_deep_link += f"&context={state.active_context_id}"

            resume_hint = f"Continue exploring {entity_name}"

        elif state.active_context_id:
            # Deep link to context
            siyuan_deep_link = (
                f"siyuan://plugins/ies"
                f"?context={state.active_context_id}"
            )
            if state.active_question_id:
                siyuan_deep_link += f"&question={state.active_question_id}"
                resume_hint = "Continue with your question"
            else:
                resume_hint = "Continue your exploration"

        return ContinueExplorationResponse(
            user_id=user_id,
            has_active_exploration=has_active,
            current_entity_id=state.current_entity_id,
            current_entity_name=state.current_entity_name,
            active_context_id=state.active_context_id,
            active_question_id=state.active_question_id,
            journey_trail=state.journey_trail[:trail_limit],
            last_app_source=state.last_app_source,
            reader_deep_link=reader_deep_link,
            siyuan_deep_link=siyuan_deep_link,
            resume_hint=resume_hint,
            last_activity_at=state.last_activity_at,
        )
