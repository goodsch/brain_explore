"""Redis-backed session store for persistent session management.

Replaces in-memory dict storage with Redis for:
- Session state survives server restarts
- 24-hour TTL with extension on activity
- Session listing and resumption support
"""

import json
from datetime import datetime, timezone
from typing import Any

import redis.asyncio as redis

from ies_backend.config import settings


class SessionStore:
    """Redis-backed session store with TTL management."""

    DEFAULT_TTL_SECONDS = 86400  # 24 hours

    def __init__(self, redis_url: str | None = None):
        """Initialize session store with Redis connection.

        Args:
            redis_url: Redis URL (defaults to settings.redis_url or localhost)
        """
        self._redis_url = redis_url or getattr(settings, "redis_url", "redis://localhost:6379")
        self._redis: redis.Redis | None = None

    async def _get_redis(self) -> redis.Redis:
        """Get or create Redis connection (lazy initialization)."""
        if self._redis is None:
            self._redis = redis.from_url(self._redis_url, decode_responses=True)
        return self._redis

    def _session_key(self, session_id: str) -> str:
        """Generate Redis key for session."""
        return f"ies:session:{session_id}"

    def _user_sessions_key(self, user_id: str) -> str:
        """Generate Redis key for user's session list."""
        return f"ies:user_sessions:{user_id}"

    async def create(
        self,
        session_id: str,
        user_id: str,
        context_data: dict[str, Any],
        ttl_seconds: int | None = None,
    ) -> dict[str, Any]:
        """Create a new session in Redis.

        Args:
            session_id: Unique session identifier
            user_id: User who owns this session
            context_data: Session context (profile summary, recent sessions, etc.)
            ttl_seconds: Optional TTL override (default: 24 hours)

        Returns:
            The created session data
        """
        r = await self._get_redis()
        ttl = ttl_seconds or self.DEFAULT_TTL_SECONDS

        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "context": context_data,
            "messages": [],
            "started_at": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
        }

        # Store session with TTL
        await r.setex(
            self._session_key(session_id),
            ttl,
            json.dumps(session_data),
        )

        # Add to user's session list (for listing)
        await r.sadd(self._user_sessions_key(user_id), session_id)

        return session_data

    async def get(self, session_id: str) -> dict[str, Any] | None:
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

        # Extend TTL on access (session activity extends life)
        await r.expire(key, self.DEFAULT_TTL_SECONDS)

        session = json.loads(data)

        # Update last activity
        session["last_activity"] = datetime.now(timezone.utc).isoformat()
        await r.setex(key, self.DEFAULT_TTL_SECONDS, json.dumps(session))

        return session

    async def update(
        self,
        session_id: str,
        updates: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Update session data.

        Args:
            session_id: Session to update
            updates: Fields to update (merged with existing)

        Returns:
            Updated session or None if not found
        """
        session = await self.get(session_id)
        if not session:
            return None

        # Merge updates
        session.update(updates)
        session["last_activity"] = datetime.now(timezone.utc).isoformat()

        r = await self._get_redis()
        await r.setex(
            self._session_key(session_id),
            self.DEFAULT_TTL_SECONDS,
            json.dumps(session),
        )

        return session

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> bool:
        """Add a message to session history.

        Args:
            session_id: Session to update
            role: Message role (user/assistant)
            content: Message content

        Returns:
            True if successful, False if session not found
        """
        session = await self.get(session_id)
        if not session:
            return False

        session["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        r = await self._get_redis()
        await r.setex(
            self._session_key(session_id),
            self.DEFAULT_TTL_SECONDS,
            json.dumps(session),
        )

        return True

    async def delete(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session to delete

        Returns:
            True if deleted, False if not found
        """
        r = await self._get_redis()
        session = await self.get(session_id)

        if not session:
            return False

        # Remove from Redis
        await r.delete(self._session_key(session_id))

        # Remove from user's session list
        user_id = session.get("user_id")
        if user_id:
            await r.srem(self._user_sessions_key(user_id), session_id)

        return True

    async def list_user_sessions(self, user_id: str) -> list[dict[str, Any]]:
        """List all active sessions for a user.

        Args:
            user_id: User whose sessions to list

        Returns:
            List of session summaries (id, started_at, last_activity)
        """
        r = await self._get_redis()
        session_ids = await r.smembers(self._user_sessions_key(user_id))

        sessions = []
        expired_ids = []

        for session_id in session_ids:
            session = await self.get(session_id)
            if session:
                sessions.append({
                    "session_id": session["session_id"],
                    "started_at": session.get("started_at"),
                    "last_activity": session.get("last_activity"),
                    "message_count": len(session.get("messages", [])),
                })
            else:
                # Session expired, clean up reference
                expired_ids.append(session_id)

        # Clean up expired session references
        if expired_ids:
            await r.srem(self._user_sessions_key(user_id), *expired_ids)

        # Sort by last activity (most recent first)
        sessions.sort(
            key=lambda s: s.get("last_activity", ""),
            reverse=True,
        )

        return sessions

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None


# Singleton instance
session_store = SessionStore()
