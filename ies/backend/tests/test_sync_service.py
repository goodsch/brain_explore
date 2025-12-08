"""Tests for cross-app exploration session synchronization."""

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from ies_backend.schemas.sync import (
    AppSource,
    JourneyStep,
    ReadingPosition,
    SessionCreateRequest,
    SessionStatus,
    SessionUpdateRequest,
    TrailItem,
)
from ies_backend.services.sync_service import SyncService


class TestSyncService:
    """Test sync service functionality with mocked Redis."""

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
    def service(self, mock_redis):
        """Create sync service with mocked Redis."""
        service = SyncService()
        service._redis = mock_redis
        return service

    @pytest.mark.asyncio
    async def test_create_session(self, service, mock_redis):
        """Test creating a new exploration session."""
        mock_redis.get.return_value = None  # Session doesn't exist yet

        request = SessionCreateRequest(
            user_id="user-123",
            app_source=AppSource.READER,
            current_entity_id="entity-456",
            current_entity_name="Mindfulness",
            reading_position=ReadingPosition(
                book_hash="abc123",
                calibre_id=42,
                cfi="epubcfi(/6/4!/4)",
                progress_percent=25.5,
            ),
        )

        result = await service.create_or_update_session(request)

        assert result.user_id == "user-123"
        assert result.app_source == AppSource.READER
        assert result.status == SessionStatus.ACTIVE
        assert result.current_entity_id == "entity-456"
        assert result.current_entity_name == "Mindfulness"
        assert result.reading_position is not None
        assert result.reading_position.book_hash == "abc123"
        assert result.id is not None

        # Verify Redis calls
        mock_redis.setex.assert_called_once()
        assert mock_redis.sadd.call_count == 2  # User sessions + status-based set

    @pytest.mark.asyncio
    async def test_update_existing_session(self, service, mock_redis):
        """Test updating an existing session."""
        # Setup existing session in Redis
        existing_session = {
            "id": "session-123",
            "user_id": "user-456",
            "app_source": "reader",
            "created_at": "2025-12-07T10:00:00Z",
            "updated_at": "2025-12-07T10:00:00Z",
            "status": "active",
            "current_entity_id": "entity-old",
            "current_entity_name": "Old Entity",
            "reading_position": None,
            "journey_path": [],
            "trail_stack": [],
            "resume_hint": None,
        }
        mock_redis.get.return_value = json.dumps(existing_session)

        request = SessionCreateRequest(
            user_id="user-456",
            app_source=AppSource.READER,
            current_entity_id="entity-new",
            current_entity_name="New Entity",
            journey_path=[
                JourneyStep(
                    entity_id="entity-new",
                    entity_name="New Entity",
                    dwell_time=45.0,
                )
            ],
        )

        result = await service.create_or_update_session(request, "session-123")

        assert result.id == "session-123"
        assert result.current_entity_id == "entity-new"
        assert result.current_entity_name == "New Entity"
        assert len(result.journey_path) == 1
        assert result.journey_path[0].entity_id == "entity-new"

    @pytest.mark.asyncio
    async def test_get_session(self, service, mock_redis):
        """Test retrieving a session by ID."""
        session_data = {
            "id": "session-abc",
            "user_id": "user-123",
            "app_source": "siyuan",
            "created_at": "2025-12-07T10:00:00Z",
            "updated_at": "2025-12-07T10:30:00Z",
            "status": "paused",
            "current_entity_id": "entity-789",
            "current_entity_name": "Acceptance",
            "reading_position": None,
            "journey_path": [],
            "trail_stack": [],
            "resume_hint": "Resume exploring Acceptance",
        }
        mock_redis.get.return_value = json.dumps(session_data)

        result = await service.get_session("session-abc")

        assert result is not None
        assert result.id == "session-abc"
        assert result.user_id == "user-123"
        assert result.app_source == AppSource.SIYUAN
        assert result.status == SessionStatus.PAUSED
        assert result.current_entity_name == "Acceptance"

        # Verify TTL was extended
        mock_redis.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, service, mock_redis):
        """Test getting non-existent session."""
        mock_redis.get.return_value = None

        result = await service.get_session("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_update_session(self, service, mock_redis):
        """Test updating session fields."""
        existing_session = {
            "id": "session-xyz",
            "user_id": "user-999",
            "app_source": "reader",
            "created_at": "2025-12-07T09:00:00Z",
            "updated_at": "2025-12-07T09:00:00Z",
            "status": "active",
            "current_entity_id": "entity-old",
            "current_entity_name": "Old",
            "reading_position": {"book_hash": "old123", "calibre_id": None, "cfi": None, "chapter": None, "progress_percent": None},
            "journey_path": [],
            "trail_stack": [],
            "resume_hint": None,
        }
        mock_redis.get.return_value = json.dumps(existing_session)

        updates = SessionUpdateRequest(
            current_entity_id="entity-new",
            current_entity_name="New",
            reading_position=ReadingPosition(
                book_hash="new456",
                cfi="epubcfi(/6/8!/2)",
                progress_percent=50.0,
            ),
        )

        result = await service.update_session("session-xyz", updates)

        assert result is not None
        assert result.current_entity_id == "entity-new"
        assert result.current_entity_name == "New"
        assert result.reading_position.book_hash == "new456"
        assert result.reading_position.progress_percent == 50.0

    @pytest.mark.asyncio
    async def test_update_session_status(self, service, mock_redis):
        """Test updating session status."""
        existing_session = {
            "id": "session-status",
            "user_id": "user-111",
            "app_source": "reader",
            "created_at": "2025-12-07T08:00:00Z",
            "updated_at": "2025-12-07T08:00:00Z",
            "status": "active",
            "current_entity_id": None,
            "current_entity_name": None,
            "reading_position": None,
            "journey_path": [],
            "trail_stack": [],
            "resume_hint": None,
        }
        mock_redis.get.return_value = json.dumps(existing_session)

        result = await service.update_session_status("session-status", SessionStatus.PAUSED)

        assert result is not None
        assert result.status == SessionStatus.PAUSED

        # Verify status-based set updates
        assert mock_redis.srem.call_count >= 1  # Remove from old status set
        assert mock_redis.sadd.call_count >= 1  # Add to new status set

    @pytest.mark.asyncio
    async def test_get_active_sessions(self, service, mock_redis):
        """Test retrieving active and paused sessions for a user."""
        active_session = {
            "id": "session-active",
            "user_id": "user-222",
            "app_source": "reader",
            "created_at": "2025-12-07T10:00:00Z",
            "updated_at": "2025-12-07T11:00:00Z",
            "status": "active",
            "current_entity_id": "entity-a",
            "current_entity_name": "Entity A",
            "reading_position": None,
            "journey_path": [],
            "trail_stack": [],
            "resume_hint": None,
        }
        paused_session = {
            "id": "session-paused",
            "user_id": "user-222",
            "app_source": "siyuan",
            "created_at": "2025-12-07T09:00:00Z",
            "updated_at": "2025-12-07T10:00:00Z",
            "status": "paused",
            "current_entity_id": "entity-b",
            "current_entity_name": "Entity B",
            "reading_position": None,
            "journey_path": [],
            "trail_stack": [],
            "resume_hint": None,
        }

        # Mock smembers to return session IDs for each status
        async def mock_smembers(key):
            if "active" in key:
                return {"session-active"}
            elif "paused" in key:
                return {"session-paused"}
            return set()

        mock_redis.smembers.side_effect = mock_smembers

        # Mock get to return different sessions
        async def mock_get(key):
            if "session-active" in key:
                return json.dumps(active_session)
            elif "session-paused" in key:
                return json.dumps(paused_session)
            return None

        mock_redis.get.side_effect = mock_get

        result = await service.get_active_sessions("user-222", include_paused=True)

        assert len(result) == 2
        session_ids = {s.id for s in result}
        assert "session-active" in session_ids
        assert "session-paused" in session_ids

        # Should be sorted by updated_at (newest first)
        assert result[0].id == "session-active"  # Updated more recently

    @pytest.mark.asyncio
    async def test_get_active_sessions_only(self, service, mock_redis):
        """Test retrieving only active sessions (excluding paused)."""
        async def mock_smembers(key):
            if "active" in key:
                return {"session-active"}
            return set()

        mock_redis.smembers.side_effect = mock_smembers

        active_session = {
            "id": "session-active",
            "user_id": "user-333",
            "app_source": "reader",
            "created_at": "2025-12-07T10:00:00Z",
            "updated_at": "2025-12-07T10:00:00Z",
            "status": "active",
            "current_entity_id": None,
            "current_entity_name": None,
            "reading_position": None,
            "journey_path": [],
            "trail_stack": [],
            "resume_hint": None,
        }
        mock_redis.get.return_value = json.dumps(active_session)

        result = await service.get_active_sessions("user-333", include_paused=False)

        assert len(result) == 1
        assert result[0].id == "session-active"
        assert result[0].status == SessionStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_get_resume_data_for_siyuan(self, service, mock_redis):
        """Test generating resume data for SiYuan target."""
        session_data = {
            "id": "session-resume-sy",
            "user_id": "user-444",
            "app_source": "reader",
            "created_at": "2025-12-07T10:00:00Z",
            "updated_at": "2025-12-07T10:00:00Z",
            "status": "paused",
            "current_entity_id": "entity-xyz",
            "current_entity_name": "Mindfulness",
            "reading_position": {
                "book_hash": "book123",
                "calibre_id": 42,
                "cfi": "epubcfi(/6/4!/4)",
                "chapter": None,
                "progress_percent": 30.0,
            },
            "journey_path": [],
            "trail_stack": [],
            "resume_hint": None,
        }
        mock_redis.get.return_value = json.dumps(session_data)

        result = await service.get_resume_data("session-resume-sy", AppSource.SIYUAN)

        assert result is not None
        assert "session" in result
        assert result["session"].id == "session-resume-sy"
        assert result["deep_link"] is not None
        assert "siyuan://" in result["deep_link"]
        assert "entity-xyz" in result["deep_link"]
        assert "instructions" in result
        assert "Mindfulness" in result["instructions"]

    @pytest.mark.asyncio
    async def test_get_resume_data_for_reader(self, service, mock_redis):
        """Test generating resume data for Reader target."""
        session_data = {
            "id": "session-resume-rd",
            "user_id": "user-555",
            "app_source": "siyuan",
            "created_at": "2025-12-07T10:00:00Z",
            "updated_at": "2025-12-07T10:00:00Z",
            "status": "paused",
            "current_entity_id": "entity-abc",
            "current_entity_name": "Acceptance",
            "reading_position": {
                "book_hash": "bookhash456",
                "calibre_id": 99,
                "cfi": "epubcfi(/6/8!/2)",
                "chapter": "Chapter 3",
                "progress_percent": 45.0,
            },
            "journey_path": [],
            "trail_stack": [],
            "resume_hint": None,
        }
        mock_redis.get.return_value = json.dumps(session_data)

        result = await service.get_resume_data("session-resume-rd", AppSource.READER)

        assert result is not None
        assert result["deep_link"] is not None
        assert "readest://" in result["deep_link"]
        assert "bookhash456" in result["deep_link"]
        assert "entity-abc" in result["deep_link"]
        assert "epubcfi(/6/8!/2)" in result["deep_link"]
        assert "instructions" in result
        assert "book 99" in result["instructions"]

    @pytest.mark.asyncio
    async def test_get_resume_data_not_found(self, service, mock_redis):
        """Test getting resume data for non-existent session."""
        mock_redis.get.return_value = None

        result = await service.get_resume_data("nonexistent", AppSource.READER)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_session(self, service, mock_redis):
        """Test deleting a session."""
        session_data = {
            "id": "session-del",
            "user_id": "user-666",
            "app_source": "reader",
            "created_at": "2025-12-07T10:00:00Z",
            "updated_at": "2025-12-07T10:00:00Z",
            "status": "completed",
            "current_entity_id": None,
            "current_entity_name": None,
            "reading_position": None,
            "journey_path": [],
            "trail_stack": [],
            "resume_hint": None,
        }
        mock_redis.get.return_value = json.dumps(session_data)

        result = await service.delete_session("session-del")

        assert result is True
        mock_redis.delete.assert_called_once()
        # Should remove from user sessions and all status sets
        assert mock_redis.srem.call_count >= 2

    @pytest.mark.asyncio
    async def test_delete_session_not_found(self, service, mock_redis):
        """Test deleting non-existent session."""
        mock_redis.get.return_value = None

        result = await service.delete_session("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_session_with_journey_path(self, service, mock_redis):
        """Test creating session with journey path."""
        mock_redis.get.return_value = None

        request = SessionCreateRequest(
            user_id="user-777",
            app_source=AppSource.READER,
            journey_path=[
                JourneyStep(
                    entity_id="entity-1",
                    entity_name="Step 1",
                    dwell_time=30.0,
                ),
                JourneyStep(
                    entity_id="entity-2",
                    entity_name="Step 2",
                    dwell_time=45.5,
                ),
            ],
        )

        result = await service.create_or_update_session(request)

        assert len(result.journey_path) == 2
        assert result.journey_path[0].entity_id == "entity-1"
        assert result.journey_path[1].entity_id == "entity-2"
        assert result.journey_path[1].dwell_time == 45.5

    @pytest.mark.asyncio
    async def test_session_with_trail_stack(self, service, mock_redis):
        """Test creating session with trail stack."""
        mock_redis.get.return_value = None

        request = SessionCreateRequest(
            user_id="user-888",
            app_source=AppSource.SIYUAN,
            trail_stack=[
                TrailItem(
                    entity_id="trail-1",
                    entity_name="Trail Item 1",
                    context={"source": "search"},
                ),
                TrailItem(
                    entity_id="trail-2",
                    entity_name="Trail Item 2",
                ),
            ],
        )

        result = await service.create_or_update_session(request)

        assert len(result.trail_stack) == 2
        assert result.trail_stack[0].entity_id == "trail-1"
        assert result.trail_stack[0].context == {"source": "search"}
        assert result.trail_stack[1].entity_id == "trail-2"

    @pytest.mark.asyncio
    async def test_session_key_format(self, service):
        """Test session key generation."""
        key = service._session_key("test-session-123")
        assert key == "ies:sync_session:test-session-123"

    @pytest.mark.asyncio
    async def test_user_sessions_key_format(self, service):
        """Test user sessions key generation."""
        # Without status
        key1 = service._user_sessions_key("user-123")
        assert key1 == "ies:user_sync_sessions:user-123"

        # With status
        key2 = service._user_sessions_key("user-123", SessionStatus.ACTIVE)
        assert key2 == "ies:user_sync_sessions:user-123:active"

    @pytest.mark.asyncio
    async def test_ttl_configuration(self, service):
        """Test that TTL is properly configured (7 days)."""
        assert service.DEFAULT_TTL_SECONDS == 86400 * 7

    @pytest.mark.asyncio
    async def test_close_connection(self, service, mock_redis):
        """Test closing Redis connection."""
        await service.close()
        mock_redis.close.assert_called_once()
        assert service._redis is None
