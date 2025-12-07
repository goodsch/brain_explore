"""Tests for ChatService - Wave 5 test coverage."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from ies_backend.services.chat_service import ChatService


@pytest.fixture
def chat_service():
    """Create ChatService instance with mocked Anthropic client."""
    with patch("ies_backend.services.chat_service.anthropic.Anthropic"):
        service = ChatService()
        yield service


@pytest.fixture
def mock_session_context():
    """Mock session context response."""
    context = MagicMock()
    context.profile_summary = "User prefers visual learning, high energy mornings"
    context.recent_sessions = [
        MagicMock(
            topic="Exploring acceptance",
            entities=["Acceptance", "Change"],
            hanging_question="How does acceptance enable change?",
        )
    ]
    context.capacity = 7
    return context


@pytest.fixture
def mock_session_data():
    """Mock session data from session store."""
    return {
        "session_id": "session_001",
        "user_id": "test_user",
        "started_at": "2025-12-06T10:00:00+00:00",
        "last_activity": "2025-12-06T10:30:00+00:00",
        "messages": [
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "Hi there"},
        ],
        "context_data": {
            "profile_summary": "Test profile",
            "recent_sessions": [],
        },
    }


class TestChatServiceStartSession:
    """Tests for session start functionality."""

    @pytest.mark.asyncio
    async def test_start_session_returns_session_id(self, chat_service, mock_session_context):
        """Test that start_session returns a valid session ID."""
        with patch(
            "ies_backend.services.chat_service.session_context_service.get_context",
            new_callable=AsyncMock,
            return_value=mock_session_context,
        ), patch(
            "ies_backend.services.chat_service.session_store.create",
            new_callable=AsyncMock,
        ) as mock_create:
            result = await chat_service.start_session("test_user")

            assert "session_id" in result
            assert result["session_id"] is not None
            assert len(result["session_id"]) == 36  # UUID format
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_session_includes_profile_summary(self, chat_service, mock_session_context):
        """Test that start_session includes profile summary."""
        with patch(
            "ies_backend.services.chat_service.session_context_service.get_context",
            new_callable=AsyncMock,
            return_value=mock_session_context,
        ), patch(
            "ies_backend.services.chat_service.session_store.create",
            new_callable=AsyncMock,
        ):
            result = await chat_service.start_session("test_user")

            assert "profile_summary" in result
            assert "visual learning" in result["profile_summary"]

    @pytest.mark.asyncio
    async def test_start_session_includes_greeting(self, chat_service, mock_session_context):
        """Test that start_session includes a greeting."""
        with patch(
            "ies_backend.services.chat_service.session_context_service.get_context",
            new_callable=AsyncMock,
            return_value=mock_session_context,
        ), patch(
            "ies_backend.services.chat_service.session_store.create",
            new_callable=AsyncMock,
        ):
            result = await chat_service.start_session("test_user")

            assert "greeting" in result
            assert result["greeting"] is not None

    @pytest.mark.asyncio
    async def test_start_session_includes_recent_context(self, chat_service, mock_session_context):
        """Test that start_session includes recent context when available."""
        with patch(
            "ies_backend.services.chat_service.session_context_service.get_context",
            new_callable=AsyncMock,
            return_value=mock_session_context,
        ), patch(
            "ies_backend.services.chat_service.session_store.create",
            new_callable=AsyncMock,
        ):
            result = await chat_service.start_session("test_user")

            assert "recent_context" in result
            assert "acceptance" in result["recent_context"].lower()

    @pytest.mark.asyncio
    async def test_start_session_stores_in_redis(self, chat_service, mock_session_context):
        """Test that start_session stores session in Redis."""
        with patch(
            "ies_backend.services.chat_service.session_context_service.get_context",
            new_callable=AsyncMock,
            return_value=mock_session_context,
        ), patch(
            "ies_backend.services.chat_service.session_store.create",
            new_callable=AsyncMock,
        ) as mock_create:
            result = await chat_service.start_session("test_user")

            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["user_id"] == "test_user"
            assert call_kwargs["session_id"] == result["session_id"]


class TestChatServiceGetSession:
    """Tests for session retrieval."""

    @pytest.mark.asyncio
    async def test_get_session_returns_session_data(self, chat_service, mock_session_data):
        """Test that get_session returns session data."""
        with patch(
            "ies_backend.services.chat_service.session_store.get",
            new_callable=AsyncMock,
            return_value=mock_session_data,
        ):
            result = await chat_service.get_session("session_001")

            assert result is not None
            assert result["session_id"] == "session_001"
            assert result["user_id"] == "test_user"

    @pytest.mark.asyncio
    async def test_get_session_returns_none_for_nonexistent(self, chat_service):
        """Test that get_session returns None for non-existent session."""
        with patch(
            "ies_backend.services.chat_service.session_store.get",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await chat_service.get_session("nonexistent")

            assert result is None


class TestChatServiceEndSession:
    """Tests for session end functionality."""

    @pytest.mark.asyncio
    async def test_end_session_deletes_from_store(self, chat_service):
        """Test that end_session removes session from store."""
        with patch(
            "ies_backend.services.chat_service.session_store.delete",
            new_callable=AsyncMock,
        ) as mock_delete:
            await chat_service.end_session("session_001")

            mock_delete.assert_called_once_with("session_001")


class TestChatServiceListSessions:
    """Tests for session listing."""

    @pytest.mark.asyncio
    async def test_list_sessions_returns_user_sessions(self, chat_service):
        """Test that list_sessions returns sessions for user."""
        mock_sessions = [
            {"session_id": "s1", "user_id": "test_user", "started_at": "2025-12-06T10:00:00"},
            {"session_id": "s2", "user_id": "test_user", "started_at": "2025-12-06T11:00:00"},
        ]

        with patch(
            "ies_backend.services.chat_service.session_store.list_user_sessions",
            new_callable=AsyncMock,
            return_value=mock_sessions,
        ):
            result = await chat_service.list_sessions("test_user")

            assert len(result) == 2
            assert result[0]["session_id"] == "s1"
            assert result[1]["session_id"] == "s2"

    @pytest.mark.asyncio
    async def test_list_sessions_returns_empty_for_no_sessions(self, chat_service):
        """Test that list_sessions returns empty list for user with no sessions."""
        with patch(
            "ies_backend.services.chat_service.session_store.list_user_sessions",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await chat_service.list_sessions("new_user")

            assert result == []


class TestChatServiceResumeSession:
    """Tests for session resumption."""

    @pytest.mark.asyncio
    async def test_resume_session_returns_session_with_messages(self, chat_service, mock_session_data):
        """Test that resume_session returns session with message history."""
        with patch(
            "ies_backend.services.chat_service.session_store.get",
            new_callable=AsyncMock,
            return_value=mock_session_data,
        ):
            result = await chat_service.resume_session("session_001")

            assert result is not None
            assert result["session_id"] == "session_001"
            assert result["message_count"] == 2
            assert len(result["messages"]) == 2

    @pytest.mark.asyncio
    async def test_resume_session_returns_none_for_nonexistent(self, chat_service):
        """Test that resume_session returns None for non-existent session."""
        with patch(
            "ies_backend.services.chat_service.session_store.get",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await chat_service.resume_session("nonexistent")

            assert result is None

    @pytest.mark.asyncio
    async def test_resume_session_includes_timestamps(self, chat_service, mock_session_data):
        """Test that resume_session includes timing information."""
        with patch(
            "ies_backend.services.chat_service.session_store.get",
            new_callable=AsyncMock,
            return_value=mock_session_data,
        ):
            result = await chat_service.resume_session("session_001")

            assert "started_at" in result
            assert "last_activity" in result
