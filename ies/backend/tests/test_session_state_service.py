"""Tests for session state service with Redis backend."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from ies_backend.services.session_state_service import SessionStateService
from ies_backend.schemas.session_state import (
    SessionState,
    SessionStateUpdate,
    SessionStateHistory,
    ReadingPosition,
    HeartbeatRequest,
    JourneyTrailItem,
    AppSource,
)


class TestSessionStateService:
    """Test session state service functionality with mocked Redis."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create mock Redis client."""
        mock = AsyncMock()
        mock.get = AsyncMock(return_value=None)
        mock.setex = AsyncMock()
        mock.delete = AsyncMock()
        mock.lpush = AsyncMock()
        mock.ltrim = AsyncMock()
        mock.lrange = AsyncMock(return_value=[])
        mock.llen = AsyncMock(return_value=0)
        mock.expire = AsyncMock()
        mock.scan_iter = MagicMock(return_value=iter([]))
        return mock

    @pytest.fixture
    def service(self, mock_redis_client):
        """Create service with mocked Redis."""
        service = SessionStateService()
        return service

    @pytest.fixture
    def sample_state(self):
        """Create sample session state."""
        now = datetime.utcnow()
        return SessionState(
            user_id="test-user",
            active_context_id="ctx-123",
            active_question_id="q-456",
            current_book=ReadingPosition(
                calibre_id=789,
                cfi="/6/4[chapter1]!/4/2/1:0",
                chapter_title="Introduction",
                progress_percent=25.5,
            ),
            last_activity_at=now,
            created_at=now,
            updated_at=now,
        )

    @pytest.mark.asyncio
    async def test_get_state_not_found(self, service, mock_redis_client):
        """Test getting state for user with no session."""
        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            result = await service.get_state("nonexistent-user")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_state_found(self, service, mock_redis_client, sample_state):
        """Test getting existing session state."""
        mock_redis_client.get = AsyncMock(
            return_value=sample_state.model_dump_json()
        )

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            result = await service.get_state("test-user")

            assert result is not None
            assert result.user_id == "test-user"
            assert result.active_context_id == "ctx-123"
            assert result.active_question_id == "q-456"
            assert result.current_book is not None
            assert result.current_book.calibre_id == 789

    @pytest.mark.asyncio
    async def test_update_state_creates_new(self, service, mock_redis_client):
        """Test updating state creates new session if none exists."""
        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            update = SessionStateUpdate(active_context_id="ctx-new")
            result = await service.update_state("new-user", update)

            assert result.user_id == "new-user"
            assert result.active_context_id == "ctx-new"
            mock_redis_client.setex.assert_called()

    @pytest.mark.asyncio
    async def test_update_state_updates_existing(
        self, service, mock_redis_client, sample_state
    ):
        """Test updating existing session state."""
        mock_redis_client.get = AsyncMock(
            return_value=sample_state.model_dump_json()
        )

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            update = SessionStateUpdate(active_question_id="q-new")
            result = await service.update_state("test-user", update)

            assert result.active_question_id == "q-new"
            assert result.active_context_id == "ctx-123"  # Unchanged
            mock_redis_client.setex.assert_called()

    @pytest.mark.asyncio
    async def test_update_state_records_history_on_context_change(
        self, service, mock_redis_client, sample_state
    ):
        """Test that context change is recorded to history."""
        mock_redis_client.get = AsyncMock(
            return_value=sample_state.model_dump_json()
        )

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            update = SessionStateUpdate(active_context_id="ctx-different")
            await service.update_state("test-user", update)

            # Should have called lpush for history
            mock_redis_client.lpush.assert_called()

    @pytest.mark.asyncio
    async def test_update_state_records_history_on_book_open(
        self, service, mock_redis_client
    ):
        """Test that opening a book is recorded to history."""
        # Start with no book
        now = datetime.utcnow()
        state_no_book = SessionState(
            user_id="test-user",
            last_activity_at=now,
            created_at=now,
            updated_at=now,
        )
        mock_redis_client.get = AsyncMock(
            return_value=state_no_book.model_dump_json()
        )

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            update = SessionStateUpdate(
                current_book=ReadingPosition(
                    calibre_id=123,
                    cfi="/6/4",
                )
            )
            await service.update_state("test-user", update)

            mock_redis_client.lpush.assert_called()

    @pytest.mark.asyncio
    async def test_heartbeat_creates_session(self, service, mock_redis_client):
        """Test heartbeat creates session for new user."""
        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            request = HeartbeatRequest(user_id="new-user")
            result = await service.heartbeat(request)

            assert result.user_id == "new-user"
            assert result.session_active is True
            mock_redis_client.setex.assert_called()

    @pytest.mark.asyncio
    async def test_heartbeat_updates_existing(
        self, service, mock_redis_client, sample_state
    ):
        """Test heartbeat updates existing session."""
        mock_redis_client.get = AsyncMock(
            return_value=sample_state.model_dump_json()
        )

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            request = HeartbeatRequest(user_id="test-user")
            result = await service.heartbeat(request)

            assert result.user_id == "test-user"
            assert result.session_active is True
            mock_redis_client.setex.assert_called()

    @pytest.mark.asyncio
    async def test_get_history_empty(self, service, mock_redis_client):
        """Test getting history for user with no history."""
        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            result = await service.get_history("test-user")

            assert result.user_id == "test-user"
            assert result.history == []
            assert result.total == 0

    @pytest.mark.asyncio
    async def test_get_history_with_entries(self, service, mock_redis_client):
        """Test getting history with existing entries."""
        now = datetime.utcnow()
        history_entry = SessionStateHistory(
            user_id="test-user",
            context_id="ctx-123",
            timestamp=now,
            change_type="context_opened",
        )
        mock_redis_client.lrange = AsyncMock(
            return_value=[history_entry.model_dump_json()]
        )
        mock_redis_client.llen = AsyncMock(return_value=1)

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            result = await service.get_history("test-user")

            assert result.total == 1
            assert len(result.history) == 1
            assert result.history[0].change_type == "context_opened"

    @pytest.mark.asyncio
    async def test_clear_state_not_found(self, service, mock_redis_client):
        """Test clearing state for user with no session."""
        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            result = await service.clear_state("nonexistent-user")
            assert result is False

    @pytest.mark.asyncio
    async def test_clear_state_success(
        self, service, mock_redis_client, sample_state
    ):
        """Test clearing existing session state."""
        mock_redis_client.get = AsyncMock(
            return_value=sample_state.model_dump_json()
        )

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            result = await service.clear_state("test-user")

            assert result is True
            mock_redis_client.delete.assert_called()
            # Should record session_ended to history
            mock_redis_client.lpush.assert_called()

    @pytest.mark.asyncio
    async def test_is_session_active_no_session(self, service, mock_redis_client):
        """Test checking activity for user with no session."""
        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            result = await service.is_session_active("nonexistent-user")
            assert result is False

    @pytest.mark.asyncio
    async def test_is_session_active_recent(
        self, service, mock_redis_client, sample_state
    ):
        """Test checking activity for recently active session."""
        mock_redis_client.get = AsyncMock(
            return_value=sample_state.model_dump_json()
        )

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            result = await service.is_session_active("test-user")
            assert result is True

    @pytest.mark.asyncio
    async def test_is_session_active_timed_out(self, service, mock_redis_client):
        """Test checking activity for timed out session."""
        # Create state with old last_activity
        old_time = datetime.utcnow() - timedelta(hours=2)
        state = SessionState(
            user_id="test-user",
            last_activity_at=old_time,
            created_at=old_time,
            updated_at=old_time,
        )
        mock_redis_client.get = AsyncMock(return_value=state.model_dump_json())

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            result = await service.is_session_active("test-user")
            assert result is False

    @pytest.mark.asyncio
    async def test_clear_all_states(self, service, mock_redis_client):
        """Test clearing all session states."""
        # Mock scan_iter to return some keys
        async def async_iter():
            for key in ["ies:session:state:user1", "ies:session:state:user2"]:
                yield key

        mock_redis_client.scan_iter = MagicMock(return_value=async_iter())
        mock_redis_client.delete = AsyncMock()

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            result = await service.clear_all_states()

            assert result == 2
            mock_redis_client.delete.assert_called()

    @pytest.mark.asyncio
    async def test_clear_all_history(self, service, mock_redis_client):
        """Test clearing all history."""
        async def async_iter():
            for key in ["ies:session:history:user1"]:
                yield key

        mock_redis_client.scan_iter = MagicMock(return_value=async_iter())
        mock_redis_client.delete = AsyncMock()

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            result = await service.clear_all_history()

            assert result == 1
            mock_redis_client.delete.assert_called()


class TestSessionStateServiceKeys:
    """Test Redis key generation."""

    def test_state_key_format(self):
        """Test state key generation."""
        service = SessionStateService()
        key = service._state_key("user-123")
        assert key == "ies:session:state:user-123"

    def test_history_key_format(self):
        """Test history key generation."""
        service = SessionStateService()
        key = service._history_key("user-123")
        assert key == "ies:session:history:user-123"


class TestSessionStateServiceSerialization:
    """Test serialization/deserialization."""

    def test_serialize_state(self):
        """Test state serialization."""
        service = SessionStateService()
        now = datetime.utcnow()
        state = SessionState(
            user_id="test-user",
            last_activity_at=now,
            created_at=now,
            updated_at=now,
        )

        json_str = service._serialize_state(state)
        assert '"user_id":"test-user"' in json_str

    def test_deserialize_state(self):
        """Test state deserialization."""
        service = SessionStateService()
        now = datetime.utcnow()
        state = SessionState(
            user_id="test-user",
            active_context_id="ctx-123",
            last_activity_at=now,
            created_at=now,
            updated_at=now,
        )
        json_str = state.model_dump_json()

        result = service._deserialize_state(json_str)
        assert result.user_id == "test-user"
        assert result.active_context_id == "ctx-123"

    def test_serialize_history_entry(self):
        """Test history entry serialization."""
        service = SessionStateService()
        entry = SessionStateHistory(
            user_id="test-user",
            context_id="ctx-123",
            timestamp=datetime.utcnow(),
            change_type="context_opened",
        )

        json_str = service._serialize_history_entry(entry)
        assert '"change_type":"context_opened"' in json_str

    def test_deserialize_history_entry(self):
        """Test history entry deserialization."""
        service = SessionStateService()
        entry = SessionStateHistory(
            user_id="test-user",
            context_id="ctx-123",
            timestamp=datetime.utcnow(),
            change_type="question_selected",
        )
        json_str = entry.model_dump_json()

        result = service._deserialize_history_entry(json_str)
        assert result.change_type == "question_selected"
        assert result.context_id == "ctx-123"


class TestJourneyTrailSync:
    """Tests for journey trail synchronization functionality."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create mock Redis client."""
        mock = AsyncMock()
        mock.get = AsyncMock(return_value=None)
        mock.setex = AsyncMock()
        mock.delete = AsyncMock()
        mock.lpush = AsyncMock()
        mock.ltrim = AsyncMock()
        mock.lrange = AsyncMock(return_value=[])
        mock.llen = AsyncMock(return_value=0)
        mock.expire = AsyncMock()
        return mock

    @pytest.fixture
    def service(self):
        """Create service with mocked Redis."""
        return SessionStateService()

    @pytest.fixture
    def sample_trail_item(self):
        """Create sample journey trail item."""
        return JourneyTrailItem(
            entity_id="ent-123",
            entity_name="Cognitive Load",
            entity_type="concept",
            source_app=AppSource.READER,
            source_context="Thinking Fast and Slow, Ch. 2",
        )

    @pytest.mark.asyncio
    async def test_add_trail_item_to_empty_state(
        self, service, mock_redis_client, sample_trail_item
    ):
        """Test adding trail item creates session state with entity tracking."""
        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            update = SessionStateUpdate(add_trail_item=sample_trail_item)
            result = await service.update_state("test-user", update)

            # Trail item should be added
            assert len(result.journey_trail) == 1
            assert result.journey_trail[0].entity_id == "ent-123"
            assert result.journey_trail[0].entity_name == "Cognitive Load"
            assert result.journey_trail[0].source_app == AppSource.READER

            # Entity tracking should be updated automatically
            assert result.current_entity_id == "ent-123"
            assert result.current_entity_name == "Cognitive Load"
            assert result.last_app_source == AppSource.READER

            # Should record history
            mock_redis_client.lpush.assert_called()

    @pytest.mark.asyncio
    async def test_add_trail_item_to_existing_state(
        self, service, mock_redis_client, sample_trail_item
    ):
        """Test adding trail item to existing state preserves other fields."""
        now = datetime.utcnow()
        existing_state = SessionState(
            user_id="test-user",
            active_context_id="ctx-123",
            active_question_id="q-456",
            last_activity_at=now,
            created_at=now,
            updated_at=now,
        )
        mock_redis_client.get = AsyncMock(
            return_value=existing_state.model_dump_json()
        )

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            update = SessionStateUpdate(add_trail_item=sample_trail_item)
            result = await service.update_state("test-user", update)

            # Trail item should be added
            assert len(result.journey_trail) == 1
            # Other fields preserved
            assert result.active_context_id == "ctx-123"
            assert result.active_question_id == "q-456"

    @pytest.mark.asyncio
    async def test_trail_items_ordered_newest_first(
        self, service, mock_redis_client
    ):
        """Test that trail items are stored newest first."""
        now = datetime.utcnow()
        existing_state = SessionState(
            user_id="test-user",
            journey_trail=[
                JourneyTrailItem(
                    entity_id="ent-old",
                    entity_name="Old Entity",
                    source_app=AppSource.SIYUAN,
                )
            ],
            last_activity_at=now,
            created_at=now,
            updated_at=now,
        )
        mock_redis_client.get = AsyncMock(
            return_value=existing_state.model_dump_json()
        )

        new_item = JourneyTrailItem(
            entity_id="ent-new",
            entity_name="New Entity",
            source_app=AppSource.READER,
        )

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            update = SessionStateUpdate(add_trail_item=new_item)
            result = await service.update_state("test-user", update)

            # New item should be first (most recent)
            assert len(result.journey_trail) == 2
            assert result.journey_trail[0].entity_id == "ent-new"
            assert result.journey_trail[1].entity_id == "ent-old"

    @pytest.mark.asyncio
    async def test_trail_limited_to_max_items(
        self, service, mock_redis_client
    ):
        """Test that trail is limited to MAX_TRAIL_ITEMS."""
        from ies_backend.services.session_state_service import MAX_TRAIL_ITEMS

        now = datetime.utcnow()
        # Create state with max items already
        existing_trail = [
            JourneyTrailItem(
                entity_id=f"ent-{i}",
                entity_name=f"Entity {i}",
                source_app=AppSource.SIYUAN,
            )
            for i in range(MAX_TRAIL_ITEMS)
        ]
        existing_state = SessionState(
            user_id="test-user",
            journey_trail=existing_trail,
            last_activity_at=now,
            created_at=now,
            updated_at=now,
        )
        mock_redis_client.get = AsyncMock(
            return_value=existing_state.model_dump_json()
        )

        new_item = JourneyTrailItem(
            entity_id="ent-newest",
            entity_name="Newest Entity",
            source_app=AppSource.READER,
        )

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            update = SessionStateUpdate(add_trail_item=new_item)
            result = await service.update_state("test-user", update)

            # Should still be limited to MAX_TRAIL_ITEMS
            assert len(result.journey_trail) == MAX_TRAIL_ITEMS
            # New item should be first
            assert result.journey_trail[0].entity_id == "ent-newest"
            # Oldest item should be dropped
            assert result.journey_trail[-1].entity_id == f"ent-{MAX_TRAIL_ITEMS - 2}"

    @pytest.mark.asyncio
    async def test_update_entity_tracking_without_trail(
        self, service, mock_redis_client
    ):
        """Test updating entity tracking directly without adding trail item."""
        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            update = SessionStateUpdate(
                current_entity_id="ent-direct",
                current_entity_name="Direct Entity",
                app_source=AppSource.SIYUAN,
            )
            result = await service.update_state("test-user", update)

            assert result.current_entity_id == "ent-direct"
            assert result.current_entity_name == "Direct Entity"
            assert result.last_app_source == AppSource.SIYUAN
            # No trail items added
            assert len(result.journey_trail) == 0


class TestContinueExploration:
    """Tests for continue exploration functionality."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create mock Redis client."""
        mock = AsyncMock()
        mock.get = AsyncMock(return_value=None)
        return mock

    @pytest.fixture
    def service(self):
        """Create service with mocked Redis."""
        return SessionStateService()

    @pytest.mark.asyncio
    async def test_continue_no_session(self, service, mock_redis_client):
        """Test continue exploration with no session."""
        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            result = await service.get_continue_exploration("test-user")

            assert result.user_id == "test-user"
            assert result.has_active_exploration is False
            assert result.reader_deep_link is None
            assert result.siyuan_deep_link is None

    @pytest.mark.asyncio
    async def test_continue_with_entity(self, service, mock_redis_client):
        """Test continue exploration with current entity."""
        now = datetime.utcnow()
        state = SessionState(
            user_id="test-user",
            current_entity_id="ent-123",
            current_entity_name="Test Entity",
            current_book=ReadingPosition(
                calibre_id=42,
                cfi="/6/4",
            ),
            last_activity_at=now,
            created_at=now,
            updated_at=now,
        )
        mock_redis_client.get = AsyncMock(return_value=state.model_dump_json())

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            result = await service.get_continue_exploration("test-user")

            assert result.has_active_exploration is True
            assert result.current_entity_id == "ent-123"
            assert result.current_entity_name == "Test Entity"
            assert result.reader_deep_link is not None
            assert "calibreId=42" in result.reader_deep_link
            assert "entity=ent-123" in result.reader_deep_link
            assert result.siyuan_deep_link is not None
            assert "entity=ent-123" in result.siyuan_deep_link
            assert result.resume_hint == "Continue exploring Test Entity"

    @pytest.mark.asyncio
    async def test_continue_with_context_only(self, service, mock_redis_client):
        """Test continue exploration with context but no entity."""
        now = datetime.utcnow()
        state = SessionState(
            user_id="test-user",
            active_context_id="ctx-123",
            active_question_id="q-456",
            last_activity_at=now,
            created_at=now,
            updated_at=now,
        )
        mock_redis_client.get = AsyncMock(return_value=state.model_dump_json())

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            result = await service.get_continue_exploration("test-user")

            assert result.has_active_exploration is True
            assert result.active_context_id == "ctx-123"
            assert result.siyuan_deep_link is not None
            assert "context=ctx-123" in result.siyuan_deep_link
            assert "question=q-456" in result.siyuan_deep_link

    @pytest.mark.asyncio
    async def test_continue_trail_limit(self, service, mock_redis_client):
        """Test that trail is limited in continue response."""
        now = datetime.utcnow()
        trail = [
            JourneyTrailItem(
                entity_id=f"ent-{i}",
                entity_name=f"Entity {i}",
                source_app=AppSource.READER,
            )
            for i in range(20)
        ]
        state = SessionState(
            user_id="test-user",
            journey_trail=trail,
            current_entity_id="ent-0",
            last_activity_at=now,
            created_at=now,
            updated_at=now,
        )
        mock_redis_client.get = AsyncMock(return_value=state.model_dump_json())

        with patch(
            "ies_backend.services.session_state_service.redis_client.get_client",
            return_value=mock_redis_client,
        ):
            # Request only 5 items
            result = await service.get_continue_exploration("test-user", trail_limit=5)

            assert len(result.journey_trail) == 5
            # Should be newest first
            assert result.journey_trail[0].entity_id == "ent-0"
