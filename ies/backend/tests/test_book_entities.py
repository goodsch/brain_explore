"""Tests for book entities API."""

import pytest
from unittest.mock import patch, AsyncMock


class TestGetBookEntities:
    """Tests for GET /graph/entities/by-book/{book_hash}."""

    @pytest.mark.asyncio
    async def test_returns_entities_for_valid_book(self):
        """Should return entities mentioned in the book."""
        from ies_backend.services.graph_service import GraphService

        mock_entities = [
            {"name": "Executive Function", "type": "Concept", "mention_count": 15},
            {"name": "Russell Barkley", "type": "Person", "mention_count": 8},
        ]

        with patch.object(
            GraphService,
            "get_entities_by_book",
            new_callable=AsyncMock,
            return_value=mock_entities
        ):
            result = await GraphService.get_entities_by_book("abc123hash")
            assert len(result) == 2
            assert result[0]["name"] == "Executive Function"
            assert result[0]["type"] == "Concept"

    @pytest.mark.asyncio
    async def test_returns_empty_for_unknown_book(self):
        """Should return empty list for book not in graph."""
        from ies_backend.services.graph_service import GraphService

        with patch.object(
            GraphService,
            "get_entities_by_book",
            new_callable=AsyncMock,
            return_value=[]
        ):
            result = await GraphService.get_entities_by_book("nonexistent")
            assert result == []

    @pytest.mark.asyncio
    async def test_filters_by_entity_type(self):
        """Should filter results by entity type when specified."""
        from ies_backend.services.graph_service import GraphService

        mock_entities = [
            {"name": "Executive Function", "type": "Concept", "mention_count": 15},
        ]

        with patch.object(
            GraphService,
            "get_entities_by_book",
            new_callable=AsyncMock,
            return_value=mock_entities
        ):
            result = await GraphService.get_entities_by_book("abc123", types=["Concept"])
            assert len(result) == 1
            assert result[0]["type"] == "Concept"
