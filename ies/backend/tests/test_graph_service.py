"""Tests for GraphService - Wave 5 test coverage."""

from unittest.mock import AsyncMock, patch
import pytest

from ies_backend.services.graph_service import GraphService


class TestGraphServiceFindRelatedConcepts:
    """Tests for finding related concepts."""

    @pytest.mark.asyncio
    async def test_find_related_concepts_returns_nodes_and_relationships(self):
        """Test that find_related_concepts returns nodes and relationships."""
        mock_results = [{
            "nodes": [
                {"name": "Concept1", "labels": ["Concept"]},
                {"name": "Concept2", "labels": ["Concept"]},
            ],
            "relationships": [
                {"type": "RELATED_TO", "start": "Concept1", "end": "Concept2"},
            ],
        }]

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=mock_results,
        ):
            result = await GraphService.find_related_concepts("TestConcept")

            assert "nodes" in result
            assert "relationships" in result
            assert len(result["nodes"]) == 2

    @pytest.mark.asyncio
    async def test_find_related_concepts_respects_depth(self):
        """Test that find_related_concepts passes depth parameter."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_query:
            await GraphService.find_related_concepts("TestConcept", depth=3)

            # First call should have depth parameter
            call_params = mock_query.call_args_list[0][0][1]
            assert call_params["depth"] == 3

    @pytest.mark.asyncio
    async def test_find_related_concepts_falls_back_on_apoc_error(self):
        """Test that find_related_concepts falls back to simpler query on APOC error."""
        fallback_results = [
            {"name": "Related1", "labels": ["Concept"], "rel_type": "RELATED_TO", "from_name": "Test"},
        ]

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query:
            # First call (APOC) raises, second call (fallback) returns results
            mock_query.side_effect = [Exception("APOC not available"), fallback_results]

            result = await GraphService.find_related_concepts("Test")

            assert len(result["nodes"]) == 1
            assert result["nodes"][0]["name"] == "Related1"

    @pytest.mark.asyncio
    async def test_find_related_concepts_returns_empty_on_complete_failure(self):
        """Test that find_related_concepts returns empty on complete failure."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=Exception("Database error"),
        ):
            result = await GraphService.find_related_concepts("Test")

            assert result["nodes"] == []
            assert result["relationships"] == []
            assert "error" in result


class TestGraphServiceFindSupportingChunks:
    """Tests for finding supporting text chunks."""

    @pytest.mark.asyncio
    async def test_find_supporting_chunks_returns_chunks(self):
        """Test that find_supporting_chunks returns matching chunks."""
        mock_chunks = [
            {"chunk_id": "c1", "content": "Text about concept", "book_title": "Book 1", "book_author": "Author 1"},
            {"chunk_id": "c2", "content": "More text", "book_title": "Book 2", "book_author": "Author 2"},
        ]

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=mock_chunks,
        ):
            result = await GraphService.find_supporting_chunks("Concept")

            assert len(result) == 2
            assert result[0]["book_title"] == "Book 1"

    @pytest.mark.asyncio
    async def test_find_supporting_chunks_respects_limit(self):
        """Test that find_supporting_chunks passes limit parameter."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_query:
            await GraphService.find_supporting_chunks("Concept", limit=5)

            call_params = mock_query.call_args[0][1]
            assert call_params["limit"] == 5

    @pytest.mark.asyncio
    async def test_find_supporting_chunks_returns_empty_on_error(self):
        """Test that find_supporting_chunks returns empty on error."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=Exception("Database error"),
        ):
            result = await GraphService.find_supporting_chunks("Concept")

            assert result == []


class TestGraphServiceGetStats:
    """Tests for graph statistics."""

    @pytest.mark.asyncio
    async def test_get_stats_returns_node_and_relationship_counts(self):
        """Test that get_stats returns node and relationship counts."""
        node_results = [
            {"label": "Concept", "count": 100},
            {"label": "Book", "count": 50},
        ]
        rel_results = [
            {"type": "RELATED_TO", "count": 200},
            {"type": "MENTIONS", "count": 150},
        ]

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query:
            mock_query.side_effect = [node_results, rel_results]

            result = await GraphService.get_stats()

            assert result["nodes"]["Concept"] == 100
            assert result["nodes"]["Book"] == 50
            assert result["relationships"]["RELATED_TO"] == 200
            assert result["relationships"]["MENTIONS"] == 150

    @pytest.mark.asyncio
    async def test_get_stats_returns_empty_on_error(self):
        """Test that get_stats returns empty dicts on error."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=Exception("Database error"),
        ):
            result = await GraphService.get_stats()

            assert result["nodes"] == {}
            assert result["relationships"] == {}
            assert "error" in result


class TestGraphServiceSearchConcepts:
    """Tests for concept search."""

    @pytest.mark.asyncio
    async def test_search_concepts_returns_matching_concepts(self):
        """Test that search_concepts returns matching concepts."""
        mock_results = [
            {"name": "Acceptance", "labels": ["Concept"]},
            {"name": "Active Acceptance", "labels": ["Concept"]},
        ]

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=mock_results,
        ):
            result = await GraphService.search_concepts("accept")

            assert len(result) == 2
            assert result[0]["name"] == "Acceptance"
            assert result[0]["type"] == "Concept"

    @pytest.mark.asyncio
    async def test_search_concepts_respects_limit(self):
        """Test that search_concepts passes limit parameter."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_query:
            await GraphService.search_concepts("test", limit=5)

            call_params = mock_query.call_args[0][1]
            assert call_params["limit"] == 5

    @pytest.mark.asyncio
    async def test_search_concepts_returns_empty_on_error(self):
        """Test that search_concepts returns empty on error."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=Exception("Database error"),
        ):
            result = await GraphService.search_concepts("test")

            assert result == []


class TestGraphServiceGetMostConnected:
    """Tests for most connected concepts."""

    @pytest.mark.asyncio
    async def test_get_most_connected_returns_concepts_with_connection_count(self):
        """Test that get_most_connected returns concepts with connection counts."""
        mock_results = [
            {"name": "Hub Concept", "labels": ["Concept"], "connections": 50},
            {"name": "Secondary", "labels": ["Concept"], "connections": 30},
        ]

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=mock_results,
        ):
            result = await GraphService.get_most_connected()

            assert len(result) == 2
            assert result[0]["name"] == "Hub Concept"
            assert result[0]["connections"] == 50

    @pytest.mark.asyncio
    async def test_get_most_connected_returns_empty_on_error(self):
        """Test that get_most_connected returns empty on error."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=Exception("Database error"),
        ):
            result = await GraphService.get_most_connected()

            assert result == []


class TestGraphServiceGetEntitiesByBook:
    """Tests for getting entities by book."""

    @pytest.mark.asyncio
    async def test_get_entities_by_book_returns_entities(self):
        """Test that get_entities_by_book returns entities for a book."""
        mock_results = [
            {"name": "Entity1", "type": "Concept", "mention_count": 10},
            {"name": "Entity2", "type": "Person", "mention_count": 5},
        ]

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=mock_results,
        ):
            result = await GraphService.get_entities_by_book("abc123hash")

            assert len(result) == 2
            assert result[0]["name"] == "Entity1"
            assert result[0]["mention_count"] == 10

    @pytest.mark.asyncio
    async def test_get_entities_by_book_with_title_fallback(self):
        """Test that get_entities_by_book uses title for fallback matching."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_query:
            await GraphService.get_entities_by_book("abc123", title="Test Book")

            call_params = mock_query.call_args[0][1]
            assert call_params["title"] == "Test Book"

    @pytest.mark.asyncio
    async def test_get_entities_by_book_returns_empty_on_error(self):
        """Test that get_entities_by_book returns empty on error."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=Exception("Database error"),
        ):
            result = await GraphService.get_entities_by_book("abc123")

            assert result == []


class TestGraphServiceGetEntitiesByCalibreId:
    """Tests for getting entities by Calibre ID."""

    @pytest.mark.asyncio
    async def test_get_entities_by_calibre_id_returns_entities(self):
        """Test that get_entities_by_calibre_id returns entities."""
        mock_results = [
            {"name": "Entity1", "type": "Concept", "mention_count": 15},
        ]

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=mock_results,
        ):
            result = await GraphService.get_entities_by_calibre_id(123)

            assert len(result) == 1
            assert result[0]["name"] == "Entity1"

    @pytest.mark.asyncio
    async def test_get_entities_by_calibre_id_respects_limit(self):
        """Test that get_entities_by_calibre_id passes limit parameter."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_query:
            await GraphService.get_entities_by_calibre_id(123, limit=100)

            call_params = mock_query.call_args[0][1]
            assert call_params["limit"] == 100

    @pytest.mark.asyncio
    async def test_get_entities_by_calibre_id_returns_empty_on_error(self):
        """Test that get_entities_by_calibre_id returns empty on error."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=Exception("Database error"),
        ):
            result = await GraphService.get_entities_by_calibre_id(123)

            assert result == []
