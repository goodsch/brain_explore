"""Service for cross-app exploration session synchronization.

Manages exploration sessions that enable continuity between Reader and SiYuan apps.
Uses Redis for persistent session storage with TTL management.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any

import redis.asyncio as redis

from ies_backend.config import settings
from ies_backend.schemas.sync import (
    AppSource,
    ExplorationSession,
    JourneyStep,
    ReadingPosition,
    SessionCreateRequest,
    SessionStatus,
    SessionUpdateRequest,
    TrailItem,
)


class SyncService:
    """Service for managing exploration session synchronization."""

    DEFAULT_TTL_SECONDS = 86400 * 7  # 7 days (longer than dialogue sessions)

    def __init__(self, redis_url: str | None = None):
        """Initialize sync service with Redis connection.

        Args:
            redis_url: Redis URL (defaults to settings.redis_url)
        """
        self._redis_url = redis_url or getattr(
            settings, "redis_url", "redis://localhost:6379"
        )
        self._redis: redis.Redis | None = None

    async def _get_redis(self) -> redis.Redis:
        """Get or create Redis connection (lazy initialization)."""
        if self._redis is None:
            self._redis = redis.from_url(self._redis_url, decode_responses=True)
        return self._redis

    def _session_key(self, session_id: str) -> str:
        """Generate Redis key for session."""
        return f"ies:sync_session:{session_id}"

    def _user_sessions_key(self, user_id: str, status: SessionStatus | None = None) -> str:
        """Generate Redis key for user's session list."""
        if status:
            return f"ies:user_sync_sessions:{user_id}:{status.value}"
        return f"ies:user_sync_sessions:{user_id}"

    def _serialize_session(self, session: ExplorationSession) -> str:
        """Serialize session to JSON string for Redis storage."""
        # Convert Pydantic model to dict, then to JSON
        data = session.model_dump(mode="json")
        return json.dumps(data)

    def _deserialize_session(self, data: str) -> ExplorationSession:
        """Deserialize session from JSON string."""
        session_dict = json.loads(data)
        return ExplorationSession(**session_dict)

    async def create_or_update_session(
        self, request: SessionCreateRequest, session_id: str | None = None
    ) -> ExplorationSession:
        """Create a new session or update existing one (upsert).

        Args:
            request: Session data
            session_id: Optional existing session ID (for updates)

        Returns:
            The created or updated session
        """
        r = await self._get_redis()
        now = datetime.now(timezone.utc)

        # Generate or use provided session ID
        sid = session_id or f"session_{uuid.uuid4().hex[:12]}"

        # Check if session exists
        existing_data = await r.get(self._session_key(sid))
        if existing_data:
            # Update existing session
            session = self._deserialize_session(existing_data)
            session.updated_at = now
            session.app_source = request.app_source
            session.status = request.status

            if request.current_entity_id is not None:
                session.current_entity_id = request.current_entity_id
            if request.current_entity_name is not None:
                session.current_entity_name = request.current_entity_name
            if request.reading_position is not None:
                session.reading_position = request.reading_position
            if request.journey_path:
                session.journey_path = request.journey_path
            if request.trail_stack:
                session.trail_stack = request.trail_stack
            if request.resume_hint is not None:
                session.resume_hint = request.resume_hint
        else:
            # Create new session
            session = ExplorationSession(
                id=sid,
                user_id=request.user_id,
                app_source=request.app_source,
                created_at=now,
                updated_at=now,
                status=request.status,
                current_entity_id=request.current_entity_id,
                current_entity_name=request.current_entity_name,
                reading_position=request.reading_position,
                journey_path=request.journey_path,
                trail_stack=request.trail_stack,
                resume_hint=request.resume_hint,
            )

        # Store session with TTL
        await r.setex(
            self._session_key(sid),
            self.DEFAULT_TTL_SECONDS,
            self._serialize_session(session),
        )

        # Add to user's session lists (by status)
        await r.sadd(self._user_sessions_key(request.user_id), sid)
        await r.sadd(
            self._user_sessions_key(request.user_id, session.status), sid
        )

        return session

    async def get_session(self, session_id: str) -> ExplorationSession | None:
        """Get session by ID.

        Also extends TTL on access (session stays alive while active).

        Args:
            session_id: Session to retrieve

        Returns:
            Session data or None if not found/expired
        """
        r = await self._get_redis()
        key = self._session_key(session_id)

        data = await r.get(key)
        if not data:
            return None

        # Extend TTL on access
        await r.expire(key, self.DEFAULT_TTL_SECONDS)

        return self._deserialize_session(data)

    async def update_session(
        self, session_id: str, updates: SessionUpdateRequest
    ) -> ExplorationSession | None:
        """Update an existing session.

        Args:
            session_id: Session to update
            updates: Fields to update

        Returns:
            Updated session or None if not found
        """
        session = await self.get_session(session_id)
        if not session:
            return None

        r = await self._get_redis()
        old_status = session.status
        session.updated_at = datetime.now(timezone.utc)

        # Update fields if provided
        if updates.status is not None:
            session.status = updates.status
        if updates.current_entity_id is not None:
            session.current_entity_id = updates.current_entity_id
        if updates.current_entity_name is not None:
            session.current_entity_name = updates.current_entity_name
        if updates.reading_position is not None:
            session.reading_position = updates.reading_position
        if updates.journey_path is not None:
            session.journey_path = updates.journey_path
        if updates.trail_stack is not None:
            session.trail_stack = updates.trail_stack
        if updates.resume_hint is not None:
            session.resume_hint = updates.resume_hint

        # Store updated session
        await r.setex(
            self._session_key(session_id),
            self.DEFAULT_TTL_SECONDS,
            self._serialize_session(session),
        )

        # Update status-based sets if status changed
        if updates.status and updates.status != old_status:
            await r.srem(
                self._user_sessions_key(session.user_id, old_status),
                session_id,
            )
            await r.sadd(
                self._user_sessions_key(session.user_id, session.status),
                session_id,
            )

        return session

    async def update_session_status(
        self, session_id: str, status: SessionStatus
    ) -> ExplorationSession | None:
        """Update session status only.

        Args:
            session_id: Session to update
            status: New status

        Returns:
            Updated session or None if not found
        """
        return await self.update_session(
            session_id, SessionUpdateRequest(status=status)
        )

    async def get_active_sessions(
        self, user_id: str, include_paused: bool = True
    ) -> list[ExplorationSession]:
        """Get active (and optionally paused) sessions for a user.

        Args:
            user_id: User whose sessions to retrieve
            include_paused: Whether to include paused sessions

        Returns:
            List of sessions, sorted by updated_at (newest first)
        """
        r = await self._get_redis()
        sessions = []
        expired_ids = []

        # Get active sessions
        active_ids = await r.smembers(
            self._user_sessions_key(user_id, SessionStatus.ACTIVE)
        )
        for session_id in active_ids:
            session = await self.get_session(session_id)
            if session:
                sessions.append(session)
            else:
                expired_ids.append(session_id)

        # Get paused sessions if requested
        if include_paused:
            paused_ids = await r.smembers(
                self._user_sessions_key(user_id, SessionStatus.PAUSED)
            )
            for session_id in paused_ids:
                session = await self.get_session(session_id)
                if session:
                    sessions.append(session)
                else:
                    expired_ids.append(session_id)

        # Clean up expired session references
        if expired_ids:
            await r.srem(self._user_sessions_key(user_id), *expired_ids)
            for status in SessionStatus:
                await r.srem(
                    self._user_sessions_key(user_id, status), *expired_ids
                )

        # Sort by updated_at (newest first)
        sessions.sort(key=lambda s: s.updated_at, reverse=True)

        return sessions

    async def get_resume_data(
        self, session_id: str, target_app: AppSource
    ) -> dict[str, Any] | None:
        """Get data needed to resume a session in the target app.

        Args:
            session_id: Session to resume
            target_app: Target app (reader or siyuan)

        Returns:
            Resume data including deep link and instructions, or None if not found
        """
        session = await self.get_session(session_id)
        if not session:
            return None

        # Generate deep link based on target app
        deep_link = None
        instructions = None

        if target_app == AppSource.SIYUAN:
            # Generate SiYuan deep link
            if session.current_entity_id:
                deep_link = (
                    f"siyuan://blocks/ies?ies-session={session_id}"
                    f"&entity={session.current_entity_id}"
                )
                instructions = f"Resume exploring {session.current_entity_name or 'entity'} in SiYuan"

        elif target_app == AppSource.READER:
            # Generate Reader deep link
            if session.reading_position and session.reading_position.book_hash:
                base_link = f"readest://open?bookHash={session.reading_position.book_hash}"
                if session.reading_position.cfi:
                    base_link += f"&cfi={session.reading_position.cfi}"
                if session.current_entity_id:
                    base_link += f"&entity={session.current_entity_id}"
                base_link += f"&ies-session={session_id}"
                deep_link = base_link

                book_info = (
                    f"book {session.reading_position.calibre_id}"
                    if session.reading_position.calibre_id
                    else "your book"
                )
                instructions = f"Resume reading {book_info} and exploring {session.current_entity_name or 'entity'}"

        return {
            "session": session,
            "deep_link": deep_link,
            "instructions": instructions,
        }

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session to delete

        Returns:
            True if deleted, False if not found
        """
        r = await self._get_redis()
        session = await self.get_session(session_id)

        if not session:
            return False

        # Remove from Redis
        await r.delete(self._session_key(session_id))

        # Remove from user's session lists
        await r.srem(self._user_sessions_key(session.user_id), session_id)
        for status in SessionStatus:
            await r.srem(
                self._user_sessions_key(session.user_id, status), session_id
            )

        return True

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None


# Singleton instance
sync_service = SyncService()
