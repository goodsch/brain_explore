"""Tests for EnrichmentService (Pass 3 LLM enrichment)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ies_backend.services.enrichment_service import (
    EnrichmentService,
    calculate_enrichment_priority,
    should_extract_mechanism,
)


class TestEnrichmentPriorityCalculation:
    """Test entity prioritization algorithm."""

    def test_high_priority_entity(self):
        """Test high-priority entity scoring."""
        entity = {
            "type": "Concept",
            "mention_count": 50,
            "description": "Short desc",
            "has_reframes": False,
        }

        priority = calculate_enrichment_priority(entity)

        # Should score high: priority type + high mentions + needs description + no reframes
        assert priority >= 0.8
        assert priority <= 1.0

    def test_low_priority_entity(self):
        """Test low-priority entity scoring."""
        entity = {
            "type": "Person",
            "mention_count": 2,
            "description": "This is a long description that exceeds 50 characters easily",
            "has_reframes": True,
        }

        priority = calculate_enrichment_priority(entity)

        # Should score low: non-priority type, low mentions, has description, has reframes
        assert priority < 0.5

    def test_priority_capped_at_one(self):
        """Test priority score is capped at 1.0."""
        entity = {
            "type": "Concept",
            "mention_count": 1000,  # Very high mentions
            "description": "",
            "has_reframes": False,
        }

        priority = calculate_enrichment_priority(entity)
        assert priority == 1.0


class TestMechanismEligibility:
    """Test mechanism extraction eligibility checks."""

    def test_eligible_concept_with_description(self):
        """Test concept with description is eligible."""
        entity = {
            "type": "Concept",
            "description": "This is a description longer than 30 characters",
            "has_mechanism": False,
        }

        assert should_extract_mechanism(entity) is True

    def test_ineligible_person_type(self):
        """Test Person type is not eligible."""
        entity = {
            "type": "Person",
            "description": "This is a description longer than 30 characters",
            "has_mechanism": False,
        }

        assert should_extract_mechanism(entity) is False

    def test_ineligible_already_has_mechanism(self):
        """Test entity with existing mechanism is not eligible."""
        entity = {
            "type": "Concept",
            "description": "This is a description longer than 30 characters",
            "has_mechanism": True,
        }

        assert should_extract_mechanism(entity) is False

    def test_ineligible_short_description(self):
        """Test entity with short description is not eligible."""
        entity = {
            "type": "Concept",
            "description": "Short",
            "has_mechanism": False,
        }

        assert should_extract_mechanism(entity) is False


@pytest.mark.asyncio
class TestEnrichmentService:
    """Test EnrichmentService methods."""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Mock Anthropic client."""
        client = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_anthropic_client):
        """Create service with mocked client."""
        return EnrichmentService(anthropic_client=mock_anthropic_client)

    async def test_generate_reframes_for_entity(self, service):
        """Test reframe generation delegates to ReframeService."""
        entity = {
            "id": "concept_123",
            "name": "Executive Function",
            "type": "Concept",
        }

        book_context = {
            "calibre_id": 42,
            "title": "ADHD 2.0",
            "author": "Barkley",
        }

        with patch(
            "ies_backend.services.enrichment_service.reframe_service.generate_reframes",
            return_value=[{"id": "r1"}, {"id": "r2"}, {"id": "r3"}],
        ):
            count = await service._generate_reframes_for_entity(entity, book_context)

        assert count == 3

    async def test_parse_json_response_with_markdown(self, service):
        """Test JSON parsing handles markdown code blocks."""
        response_text = """Here's the result:

```json
{
  "has_mechanism": true,
  "mechanism": {
    "name": "Test Mechanism",
    "confidence": 0.9
  }
}
```
"""
        result = service._parse_json_response(response_text)

        assert result is not None
        assert result["has_mechanism"] is True
        assert result["mechanism"]["name"] == "Test Mechanism"

    async def test_parse_json_response_plain_json(self, service):
        """Test JSON parsing handles plain JSON."""
        response_text = """
        {
          "is_pattern": false,
          "pattern": null
        }
        """
        result = service._parse_json_response(response_text)

        assert result is not None
        assert result["is_pattern"] is False
        assert result["pattern"] is None

    async def test_get_book_context_not_found(self, service):
        """Test book context returns None for missing book."""
        with patch(
            "ies_backend.services.enrichment_service.Neo4jClient.execute_query",
            return_value=[],
        ):
            context = await service._get_book_context(999)

        assert context is None

    async def test_get_book_context_success(self, service):
        """Test book context retrieval."""
        mock_result = [
            {
                "title": "Test Book",
                "author": "Test Author",
                "genres": ["psychology"],
                "description": "A test book",
            }
        ]

        with patch(
            "ies_backend.services.enrichment_service.Neo4jClient.execute_query",
            return_value=mock_result,
        ):
            context = await service._get_book_context(42)

        assert context is not None
        assert context["calibre_id"] == 42
        assert context["title"] == "Test Book"
        assert context["author"] == "Test Author"

    async def test_get_prioritized_entities(self, service):
        """Test entity prioritization."""
        mock_results = [
            {
                "id": "e1",
                "name": "Concept A",
                "type": "Concept",
                "description": "Short",
                "mention_count": 50,
                "has_reframes": False,
                "has_mechanism": False,
            },
            {
                "id": "e2",
                "name": "Person B",
                "type": "Person",
                "description": "Longer description here",
                "mention_count": 10,
                "has_reframes": True,
                "has_mechanism": False,
            },
        ]

        with patch(
            "ies_backend.services.enrichment_service.Neo4jClient.execute_query",
            return_value=mock_results,
        ):
            entities = await service._get_prioritized_entities(42, limit=20)

        assert len(entities) == 2
        # First entity should have higher priority
        assert entities[0]["name"] == "Concept A"
        assert entities[0]["priority"] > entities[1]["priority"]

    async def test_enrich_book_entities_no_book(self, service):
        """Test enrichment handles missing book gracefully."""
        with patch.object(service, "_get_book_context", return_value=None):
            stats = await service.enrich_book_entities(999)

        assert stats["calibre_id"] == 999
        assert stats["entities_processed"] == 0
        assert stats["reframes_generated"] == 0

    async def test_enrich_book_entities_success(self, service):
        """Test successful enrichment flow."""
        mock_book_context = {
            "calibre_id": 42,
            "title": "Test Book",
            "author": "Author",
        }

        mock_entities = [
            {
                "id": "e1",
                "name": "Test Concept",
                "type": "Concept",
                "description": "Short",
                "mention_count": 30,
                "has_reframes": False,
                "has_mechanism": False,
                "priority": 0.8,
            }
        ]

        with patch.object(service, "_get_book_context", return_value=mock_book_context):
            with patch.object(
                service, "_get_prioritized_entities", return_value=mock_entities
            ):
                with patch.object(
                    service, "_generate_reframes_for_entity", return_value=3
                ):
                    with patch.object(
                        service, "_update_book_status", return_value=None
                    ):
                        stats = await service.enrich_book_entities(
                            42,
                            enable_mechanisms=False,
                            enable_patterns=False,
                            enable_descriptions=False,
                        )

        assert stats["calibre_id"] == 42
        assert stats["entities_processed"] == 1
        assert stats["reframes_generated"] == 3
        assert stats["errors"] == 0
