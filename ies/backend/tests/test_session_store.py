"""Tests for Redis-backed session store."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from datetime import datetime, timezone

from ies_backend.services.session_store import SessionStore


class TestSessionStore:
    """Test session store functionality with mocked Redis."""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        mock = AsyncMock()
        mock.setex = AsyncMock()
        mock.get = AsyncMock()
        mock.delete = AsyncMock()
        mock.sadd = AsyncMock()
        mock.srem = AsyncMock()
        mock.smembers = AsyncMock(return_value=set())
        mock.expire = AsyncMock()
        mock.close = AsyncMock()
        return mock

    @pytest.fixture
    def store(self, mock_redis):
        """Create session store with mocked Redis."""
        store = SessionStore()
        store._redis = mock_redis
        return store

    @pytest.mark.asyncio
    async def test_create_session(self, store, mock_redis):
        """Test creating a new session."""
        session_id = "test-session-123"
        user_id = "user-456"
        context_data = {"profile_summary": "Test user"}

        result = await store.create(
            session_id=session_id,
            user_id=user_id,
            context_data=context_data,
        )

        # Verify session data structure
        assert result["session_id"] == session_id
        assert result["user_id"] == user_id
        assert result["context"] == context_data
        assert result["messages"] == []
        assert "started_at" in result
        assert "last_activity" in result

        # Verify Redis calls
        mock_redis.setex.assert_called_once()
        mock_redis.sadd.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, store, mock_redis):
        """Test getting a non-existent session."""
        mock_redis.get.return_value = None

        result = await store.get("nonexistent-session")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_session_found(self, store, mock_redis):
        """Test getting an existing session."""
        session_data = {
            "session_id": "test-123",
            "user_id": "user-456",
            "context": {"profile_summary": "Test"},
            "messages": [],
            "started_at": "2025-12-06T00:00:00Z",
            "last_activity": "2025-12-06T00:00:00Z",
        }
        mock_redis.get.return_value = json.dumps(session_data)

        result = await store.get("test-123")

        assert result is not None
        assert result["session_id"] == "test-123"
        assert result["user_id"] == "user-456"

        # Verify TTL was extended
        mock_redis.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_message(self, store, mock_redis):
        """Test adding a message to session."""
        session_data = {
            "session_id": "test-123",
            "user_id": "user-456",
            "context": {},
            "messages": [],
            "started_at": "2025-12-06T00:00:00Z",
            "last_activity": "2025-12-06T00:00:00Z",
        }
        mock_redis.get.return_value = json.dumps(session_data)

        result = await store.add_message("test-123", "user", "Hello world")

        assert result is True
        # Verify setex was called to save updated session
        assert mock_redis.setex.call_count >= 1

    @pytest.mark.asyncio
    async def test_add_message_session_not_found(self, store, mock_redis):
        """Test adding message to non-existent session."""
        mock_redis.get.return_value = None

        result = await store.add_message("nonexistent", "user", "Hello")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_session(self, store, mock_redis):
        """Test deleting a session."""
        session_data = {
            "session_id": "test-123",
            "user_id": "user-456",
            "context": {},
            "messages": [],
            "started_at": "2025-12-06T00:00:00Z",
            "last_activity": "2025-12-06T00:00:00Z",
        }
        mock_redis.get.return_value = json.dumps(session_data)

        result = await store.delete("test-123")

        assert result is True
        mock_redis.delete.assert_called_once()
        mock_redis.srem.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_session_not_found(self, store, mock_redis):
        """Test deleting non-existent session."""
        mock_redis.get.return_value = None

        result = await store.delete("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_list_user_sessions(self, store, mock_redis):
        """Test listing user sessions."""
        session1 = {
            "session_id": "session-1",
            "user_id": "user-456",
            "context": {},
            "messages": [{"role": "user", "content": "Hi"}],
            "started_at": "2025-12-06T00:00:00Z",
            "last_activity": "2025-12-06T01:00:00Z",
        }
        session2 = {
            "session_id": "session-2",
            "user_id": "user-456",
            "context": {},
            "messages": [],
            "started_at": "2025-12-06T00:00:00Z",
            "last_activity": "2025-12-06T02:00:00Z",
        }

        mock_redis.smembers.return_value = {"session-1", "session-2"}

        # Configure get to return different sessions
        async def mock_get(key):
            if "session-1" in key:
                return json.dumps(session1)
            elif "session-2" in key:
                return json.dumps(session2)
            return None

        mock_redis.get.side_effect = mock_get

        result = await store.list_user_sessions("user-456")

        assert len(result) == 2
        # Both sessions should be returned with correct message counts
        session_ids = {s["session_id"] for s in result}
        assert "session-1" in session_ids
        assert "session-2" in session_ids
        # Find session-1 and verify message count
        s1 = next(s for s in result if s["session_id"] == "session-1")
        assert s1["message_count"] == 1

    @pytest.mark.asyncio
    async def test_list_user_sessions_cleans_expired(self, store, mock_redis):
        """Test that listing sessions cleans up expired references."""
        mock_redis.smembers.return_value = {"active-session", "expired-session"}

        session_data = {
            "session_id": "active-session",
            "user_id": "user-456",
            "context": {},
            "messages": [],
            "started_at": "2025-12-06T00:00:00Z",
            "last_activity": "2025-12-06T00:00:00Z",
        }

        # First session exists, second doesn't
        async def mock_get(key):
            if "active-session" in key:
                return json.dumps(session_data)
            return None

        mock_redis.get.side_effect = mock_get

        result = await store.list_user_sessions("user-456")

        assert len(result) == 1
        assert result[0]["session_id"] == "active-session"

        # Should have cleaned up expired reference
        mock_redis.srem.assert_called()

    @pytest.mark.asyncio
    async def test_update_session(self, store, mock_redis):
        """Test updating session data."""
        session_data = {
            "session_id": "test-123",
            "user_id": "user-456",
            "context": {"old": "data"},
            "messages": [],
            "started_at": "2025-12-06T00:00:00Z",
            "last_activity": "2025-12-06T00:00:00Z",
        }
        mock_redis.get.return_value = json.dumps(session_data)

        result = await store.update("test-123", {"context": {"new": "data"}})

        assert result is not None
        assert result["context"] == {"new": "data"}

    @pytest.mark.asyncio
    async def test_session_key_format(self, store):
        """Test session key generation."""
        key = store._session_key("test-123")
        assert key == "ies:session:test-123"

    @pytest.mark.asyncio
    async def test_user_sessions_key_format(self, store):
        """Test user sessions key generation."""
        key = store._user_sessions_key("user-456")
        assert key == "ies:user_sessions:user-456"
