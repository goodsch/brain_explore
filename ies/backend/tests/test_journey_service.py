"""Tests for JourneyService - Wave 5 test coverage."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from ies_backend.schemas.journey import (
    BreadcrumbJourney,
    EntryPoint,
    EntryPointType,
    JourneyCreateRequest,
    JourneyMark,
    JourneyStep,
    JourneyUpdateRequest,
    MarkType,
    ThinkingPartnerExchange,
)
from ies_backend.services.journey_service import JourneyService


# Test data fixtures
@pytest.fixture
def sample_entry_point():
    """Sample entry point for tests."""
    return EntryPoint(
        type=EntryPointType.BOOK,
        reference="book_123",
        context="Chapter 1: Introduction",
    )


@pytest.fixture
def sample_journey_step():
    """Sample journey step for tests."""
    return JourneyStep(
        entity_id="entity_001",
        entity_name="Acceptance",
        timestamp=datetime(2025, 12, 6, 10, 0, 0, tzinfo=timezone.utc),
        source_passage="Acceptance is the key to change",
        source_book_id="book_123",
        dwell_time_seconds=45.5,
    )


@pytest.fixture
def sample_mark():
    """Sample journey mark for tests."""
    return JourneyMark(
        type=MarkType.HIGHLIGHT,
        entity_id="entity_001",
        content="Important insight about acceptance",
        timestamp=datetime(2025, 12, 6, 10, 5, 0, tzinfo=timezone.utc),
        source_location="book:chapter1:page5",
    )


@pytest.fixture
def sample_exchange():
    """Sample thinking partner exchange for tests."""
    return ThinkingPartnerExchange(
        question="How does acceptance relate to change?",
        response="Acceptance creates the foundation for change by...",
        timestamp=datetime(2025, 12, 6, 10, 10, 0, tzinfo=timezone.utc),
        entity_context="entity_001",
    )


@pytest.fixture
def sample_create_request(sample_entry_point, sample_journey_step, sample_mark, sample_exchange):
    """Sample journey create request."""
    return JourneyCreateRequest(
        user_id="test_user",
        entry_point=sample_entry_point,
        path=[sample_journey_step],
        marks=[sample_mark],
        thinking_partner_exchanges=[sample_exchange],
        title="Exploring Acceptance",
        tags=["psychology", "self-help"],
        notes="Great exploration session",
    )


@pytest.fixture
def mock_journey_node():
    """Mock journey node returned from Neo4j."""
    return {
        "id": "journey_001",
        "user_id": "test_user",
        "started_at": "2025-12-06T10:00:00+00:00",
        "ended_at": None,
        "entry_point_type": "book",
        "entry_point_reference": "book_123",
        "entry_point_context": "Chapter 1",
        "title": "Test Journey",
        "tags": ["test"],
        "notes": "Test notes",
        "processed": False,
        "siyuan_note_id": None,
    }


class TestJourneyServiceCreate:
    """Tests for journey creation."""

    @pytest.mark.asyncio
    async def test_create_journey_returns_journey_with_id(self, sample_create_request, mock_journey_node):
        """Test that create_journey returns a journey with assigned ID."""
        with patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_write",
            new_callable=AsyncMock,
        ) as mock_write, patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query:
            # Mock the create query
            mock_write.return_value = [{"j": mock_journey_node}]
            # Mock get_journey queries (journey, steps, marks, exchanges)
            mock_query.side_effect = [
                [{"j": mock_journey_node}],  # Journey node
                [{"s": {"entity_id": "entity_001", "entity_name": "Acceptance", "step_order": 0}}],  # Steps
                [{"m": {"type": "highlight", "entity_id": "entity_001", "content": "Test"}}],  # Marks
                [{"e": {"question": "Test?", "response": "Yes"}}],  # Exchanges
            ]

            result = await JourneyService.create_journey(sample_create_request)

            assert result is not None
            assert result.id == "journey_001"
            assert result.user_id == "test_user"
            assert mock_write.call_count >= 1  # At least one write for journey creation

    @pytest.mark.asyncio
    async def test_create_journey_stores_entry_point(self, sample_create_request, mock_journey_node):
        """Test that create_journey correctly stores entry point data."""
        with patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_write",
            new_callable=AsyncMock,
        ) as mock_write, patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query:
            mock_write.return_value = [{"j": mock_journey_node}]
            mock_query.side_effect = [
                [{"j": mock_journey_node}],
                [],  # No steps
                [],  # No marks
                [],  # No exchanges
            ]

            await JourneyService.create_journey(sample_create_request)

            # Verify the create query included entry point data
            create_call = mock_write.call_args_list[0]
            params = create_call[0][1]
            assert params["entry_point_type"] == "book"
            assert params["entry_point_reference"] == "book_123"


class TestJourneyServiceGet:
    """Tests for journey retrieval."""

    @pytest.mark.asyncio
    async def test_get_journey_returns_complete_journey(self, mock_journey_node):
        """Test that get_journey returns a complete journey with all components."""
        with patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query:
            mock_query.side_effect = [
                [{"j": mock_journey_node}],
                [{"s": {"entity_id": "e1", "entity_name": "Concept1", "step_order": 0, "dwell_time_seconds": 30}}],
                [{"m": {"type": "highlight", "entity_id": "e1", "content": "Important", "timestamp": "2025-12-06T10:00:00"}}],
                [{"e": {"question": "Why?", "response": "Because...", "timestamp": "2025-12-06T10:05:00"}}],
            ]

            result = await JourneyService.get_journey("journey_001")

            assert result is not None
            assert result.id == "journey_001"
            assert len(result.path) == 1
            assert len(result.marks) == 1
            assert len(result.thinking_partner_exchanges) == 1
            assert result.entry_point.type == EntryPointType.BOOK

    @pytest.mark.asyncio
    async def test_get_journey_returns_none_for_nonexistent(self):
        """Test that get_journey returns None for non-existent journey."""
        with patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query:
            mock_query.return_value = []

            result = await JourneyService.get_journey("nonexistent")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_journey_handles_empty_components(self, mock_journey_node):
        """Test that get_journey handles journeys with no steps/marks/exchanges."""
        with patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query:
            mock_query.side_effect = [
                [{"j": mock_journey_node}],
                [],  # No steps
                [],  # No marks
                [],  # No exchanges
            ]

            result = await JourneyService.get_journey("journey_001")

            assert result is not None
            assert len(result.path) == 0
            assert len(result.marks) == 0
            assert len(result.thinking_partner_exchanges) == 0


class TestJourneyServiceList:
    """Tests for journey listing."""

    @pytest.mark.asyncio
    async def test_list_journeys_returns_user_journeys(self):
        """Test that list_journeys returns journeys for a user."""
        mock_journey_1 = {
            "id": "j1", "user_id": "test_user", "started_at": "2025-12-06T10:00:00",
            "entry_point_type": "book", "entry_point_reference": "b1",
            "title": "Journey 1", "tags": [], "processed": False,
        }
        mock_journey_2 = {
            "id": "j2", "user_id": "test_user", "started_at": "2025-12-06T11:00:00",
            "entry_point_type": "search", "entry_point_reference": "acceptance",
            "title": "Journey 2", "tags": [], "processed": False,
        }

        with patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query:
            # list_journeys makes: count query, list query, then get_journey for each
            mock_query.side_effect = [
                [{"total": 2}],  # Count query
                [{"id": "j1"}, {"id": "j2"}],  # List query (returns IDs)
                # get_journey for j1: journey, steps, marks, exchanges
                [{"j": mock_journey_1}], [], [], [],
                # get_journey for j2: journey, steps, marks, exchanges
                [{"j": mock_journey_2}], [], [], [],
            ]

            journeys, total = await JourneyService.list_journeys("test_user")

            assert total == 2
            assert len(journeys) == 2
            assert journeys[0].id == "j1"
            assert journeys[1].id == "j2"

    @pytest.mark.asyncio
    async def test_list_journeys_respects_pagination(self):
        """Test that list_journeys respects page and page_size."""
        with patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query:
            # Count query, then list query (empty)
            mock_query.side_effect = [
                [{"total": 0}],
                [],
            ]

            journeys, total = await JourneyService.list_journeys("test_user", page=2, page_size=10)

            # Verify SKIP and LIMIT in the list query (second call)
            list_call = mock_query.call_args_list[1]
            params = list_call[0][1]
            assert params["skip"] == 10  # page 2 with size 10 = skip 10
            assert params["limit"] == 10

    @pytest.mark.asyncio
    async def test_list_journeys_returns_empty_for_no_journeys(self):
        """Test that list_journeys returns empty list for user with no journeys."""
        with patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query:
            mock_query.side_effect = [
                [{"total": 0}],  # Count query
                [],  # List query (empty)
            ]

            journeys, total = await JourneyService.list_journeys("new_user")

            assert total == 0
            assert len(journeys) == 0


class TestJourneyServiceUpdate:
    """Tests for journey updates."""

    @pytest.mark.asyncio
    async def test_update_journey_adds_steps(self, mock_journey_node, sample_journey_step):
        """Test that update_journey can add new steps."""
        update_request = JourneyUpdateRequest(
            path=[sample_journey_step],
        )

        with patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_write",
            new_callable=AsyncMock,
        ) as mock_write, patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query:
            # update_journey flow:
            # 1. get_journey (check exists): journey, steps, marks, exchanges
            # 2. count existing steps
            # 3. get_journey (return result): journey, steps, marks, exchanges
            mock_query.side_effect = [
                # First get_journey call (check exists)
                [{"j": mock_journey_node}], [], [], [],
                # Count existing steps
                [{"count": 2}],
                # Final get_journey call (return result)
                [{"j": mock_journey_node}],
                [{"s": {"entity_id": "e1", "entity_name": "C1", "step_order": 0}}],
                [], [],
            ]
            mock_write.return_value = []

            result = await JourneyService.update_journey("journey_001", update_request)

            # Verify _add_step was called (at least one write for the step)
            assert mock_write.call_count >= 1
            assert result is not None

    @pytest.mark.asyncio
    async def test_update_journey_updates_metadata(self, mock_journey_node):
        """Test that update_journey can update title, tags, notes."""
        update_request = JourneyUpdateRequest(
            title="Updated Title",
            tags=["new", "tags"],
            notes="Updated notes",
        )

        with patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_write",
            new_callable=AsyncMock,
        ) as mock_write, patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query:
            # update_journey flow for metadata update:
            # 1. get_journey (check exists): journey, steps, marks, exchanges
            # 2. get_journey (return result): journey, steps, marks, exchanges
            mock_query.side_effect = [
                # First get_journey call (check exists)
                [{"j": mock_journey_node}], [], [], [],
                # Final get_journey call (return result)
                [{"j": mock_journey_node}], [], [], [],
            ]
            mock_write.return_value = []

            await JourneyService.update_journey("journey_001", update_request)

            # Verify metadata update was called
            assert mock_write.call_count >= 1
            # Find the metadata update call
            for call in mock_write.call_args_list:
                query = call[0][0]
                if "SET" in query:
                    params = call[0][1]
                    assert params.get("title") == "Updated Title"
                    assert params.get("tags") == ["new", "tags"]
                    assert params.get("notes") == "Updated notes"
                    break

    @pytest.mark.asyncio
    async def test_update_journey_returns_none_for_nonexistent(self):
        """Test that update_journey returns None for non-existent journey."""
        update_request = JourneyUpdateRequest(title="New Title")

        with patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query:
            mock_query.return_value = []  # Journey not found

            result = await JourneyService.update_journey("nonexistent", update_request)

            assert result is None


class TestJourneyServiceDelete:
    """Tests for journey deletion."""

    @pytest.mark.asyncio
    async def test_delete_journey_removes_journey_and_components(self):
        """Test that delete_journey removes the journey and all related nodes."""
        with patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_write",
            new_callable=AsyncMock,
        ) as mock_write:
            mock_write.return_value = []

            await JourneyService.delete_journey("journey_001")

            # Verify delete query was called
            assert mock_write.call_count == 1
            query = mock_write.call_args[0][0]
            assert "DELETE" in query or "DETACH DELETE" in query


class TestJourneyServiceSynthesis:
    """Tests for journey synthesis generation."""

    @pytest.mark.asyncio
    async def test_generate_synthesis_returns_ai_summary(self, mock_journey_node):
        """Test that generate_synthesis returns AI-generated summary."""
        with patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query, patch(
            "ies_backend.services.journey_service.JourneyService._get_anthropic_client",
        ) as mock_client_factory:
            # Mock journey retrieval
            mock_query.side_effect = [
                [{"j": mock_journey_node}],
                [{"s": {"entity_id": "e1", "entity_name": "Acceptance", "step_order": 0}}],
                [{"m": {"type": "highlight", "entity_id": "e1", "content": "Key insight"}}],
                [{"e": {"question": "Why?", "response": "Because..."}}],
            ]

            # Mock Anthropic client
            mock_client = MagicMock()
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text="This journey explored acceptance and its implications...")]
            mock_client.messages.create.return_value = mock_message
            mock_client_factory.return_value = mock_client

            result = await JourneyService.generate_synthesis("journey_001")

            assert result is not None
            assert result.synthesis is not None
            assert "acceptance" in result.synthesis.lower() or len(result.synthesis) > 0

    @pytest.mark.asyncio
    async def test_generate_synthesis_handles_no_journey(self):
        """Test that generate_synthesis returns None for non-existent journey."""
        with patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query:
            mock_query.return_value = []

            result = await JourneyService.generate_synthesis("nonexistent")

            assert result is None

    @pytest.mark.asyncio
    async def test_generate_synthesis_fallback_on_api_error(self, mock_journey_node):
        """Test that generate_synthesis provides fallback summary on API error."""
        with patch(
            "ies_backend.services.journey_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query, patch(
            "ies_backend.services.journey_service.JourneyService._get_anthropic_client",
        ) as mock_client_factory:
            mock_query.side_effect = [
                [{"j": mock_journey_node}],
                [{"s": {"entity_id": "e1", "entity_name": "Concept1", "step_order": 0}}],
                [],
                [],
            ]

            # Simulate API error
            mock_client = MagicMock()
            mock_client.messages.create.side_effect = Exception("API Error")
            mock_client_factory.return_value = mock_client

            result = await JourneyService.generate_synthesis("journey_001")

            # Should return fallback synthesis, not None
            assert result is not None
            assert result.synthesis is not None
