"""Tests for facet functionality (Phase 2B Flow Mode).

Tests cover:
- get_entity_facets: Retrieve facets for an entity
- create_facet: Create a facet for an entity
- add_entity_to_facet: Add concepts to facets
"""

from unittest.mock import AsyncMock, patch
import pytest

from ies_backend.services.graph_service import GraphService


class TestGetEntityFacets:
    """Tests for get_entity_facets method."""

    @pytest.mark.asyncio
    async def test_get_entity_facets_returns_facets_with_entities(self):
        """Test that get_entity_facets returns facets and their entities."""
        # Mock entity lookup
        mock_entity = [
            {
                "e": {"name": "ADHD"},
                "labels": ["Concept"],
            }
        ]

        # Mock facets with entities
        mock_facets = [
            {
                "facet_name": "Diagnosis & Assessment",
                "facet_description": "Diagnostic criteria and assessment tools",
                "facet_order": 0,
                "entities": [
                    {"name": "DSM-5 Criteria", "type": "Concept", "relationship": "BELONGS_TO"},
                    {"name": "ADHD Rating Scale", "type": "Tool", "relationship": "BELONGS_TO"},
                ],
            },
            {
                "facet_name": "Neurobiology",
                "facet_description": "Brain mechanisms underlying ADHD",
                "facet_order": 1,
                "entities": [
                    {"name": "Dopamine", "type": "Neurotransmitter", "relationship": "BELONGS_TO"},
                    {"name": "Prefrontal Cortex", "type": "Brain Region", "relationship": "BELONGS_TO"},
                ],
            },
        ]

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=[mock_entity, mock_facets],
        ):
            result = await GraphService.get_entity_facets("ADHD")

            assert result is not None
            assert result["entity_name"] == "ADHD"
            assert result["entity_type"] == "Concept"
            assert len(result["facets"]) == 2

            # Check first facet
            facet1 = result["facets"][0]
            assert facet1["name"] == "Diagnosis & Assessment"
            assert facet1["description"] == "Diagnostic criteria and assessment tools"
            assert facet1["entity_count"] == 2
            assert len(facet1["entities"]) == 2
            assert facet1["entities"][0]["name"] == "DSM-5 Criteria"
            assert facet1["entities"][0]["type"] == "Concept"
            assert facet1["entities"][0]["relationship"] == "BELONGS_TO"

            # Check second facet
            facet2 = result["facets"][1]
            assert facet2["name"] == "Neurobiology"
            assert len(facet2["entities"]) == 2

    @pytest.mark.asyncio
    async def test_get_entity_facets_returns_empty_facets_when_none_exist(self):
        """Test that get_entity_facets returns empty list when no facets exist."""
        mock_entity = [
            {
                "e": {"name": "Some Entity"},
                "labels": ["Concept"],
            }
        ]
        # Empty facets result
        mock_facets = []

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=[mock_entity, mock_facets],
        ):
            result = await GraphService.get_entity_facets("Some Entity")

            assert result is not None
            assert result["entity_name"] == "Some Entity"
            assert result["facets"] == []

    @pytest.mark.asyncio
    async def test_get_entity_facets_handles_facets_without_entities(self):
        """Test that get_entity_facets handles facets that have no entities yet."""
        mock_entity = [
            {
                "e": {"name": "Executive Function"},
                "labels": ["Concept"],
            }
        ]

        # Facet with empty entities (OPTIONAL MATCH returns null)
        mock_facets = [
            {
                "facet_name": "Components",
                "facet_description": "Core EF components",
                "facet_order": 0,
                "entities": [{"name": None, "type": None, "relationship": None}],  # Null from OPTIONAL MATCH
            },
        ]

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=[mock_entity, mock_facets],
        ):
            result = await GraphService.get_entity_facets("Executive Function")

            assert result is not None
            assert len(result["facets"]) == 1
            assert result["facets"][0]["entity_count"] == 0  # No valid entities
            assert result["facets"][0]["entities"] == []  # Filtered out nulls

    @pytest.mark.asyncio
    async def test_get_entity_facets_returns_none_for_missing_entity(self):
        """Test that get_entity_facets returns None when entity not found."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[],  # Entity not found
        ):
            result = await GraphService.get_entity_facets("NonExistent")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_entity_facets_returns_none_on_exception(self):
        """Test that get_entity_facets returns None on database error."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=Exception("Database error"),
        ):
            result = await GraphService.get_entity_facets("Test")

            assert result is None


class TestCreateFacet:
    """Tests for create_facet method."""

    @pytest.mark.asyncio
    async def test_create_facet_succeeds(self):
        """Test that create_facet creates a facet successfully."""
        mock_result = [{"f": {"name": "Diagnosis", "entity": "ADHD"}}]

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=mock_result,
        ) as mock_query:
            result = await GraphService.create_facet(
                entity_name="ADHD",
                facet_name="Diagnosis",
                description="Diagnostic criteria",
                order=0,
            )

            assert result is True
            # Verify query params
            call_params = mock_query.call_args[0][1]
            assert call_params["entity_name"] == "ADHD"
            assert call_params["facet_name"] == "Diagnosis"
            assert call_params["description"] == "Diagnostic criteria"
            assert call_params["order"] == 0

    @pytest.mark.asyncio
    async def test_create_facet_with_minimal_params(self):
        """Test that create_facet works with just entity and facet name."""
        mock_result = [{"f": {"name": "Treatment"}}]

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            result = await GraphService.create_facet(
                entity_name="ADHD",
                facet_name="Treatment",
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_create_facet_returns_false_on_error(self):
        """Test that create_facet returns False on database error."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=Exception("Database error"),
        ):
            result = await GraphService.create_facet(
                entity_name="ADHD",
                facet_name="Treatment",
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_create_facet_returns_false_when_entity_not_found(self):
        """Test that create_facet returns False when entity doesn't exist."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[],  # No results = entity not found
        ):
            result = await GraphService.create_facet(
                entity_name="NonExistent",
                facet_name="Test Facet",
            )

            assert result is False


class TestAddEntityToFacet:
    """Tests for add_entity_to_facet method."""

    @pytest.mark.asyncio
    async def test_add_entity_to_facet_succeeds(self):
        """Test that add_entity_to_facet adds a concept to a facet."""
        mock_result = [
            {
                "f": {"name": "Diagnosis", "entity": "ADHD"},
                "c": {"name": "DSM-5 Criteria"},
            }
        ]

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=mock_result,
        ) as mock_query:
            result = await GraphService.add_entity_to_facet(
                facet_name="Diagnosis",
                entity_name="ADHD",
                concept_name="DSM-5 Criteria",
            )

            assert result is True
            # Verify query params
            call_params = mock_query.call_args[0][1]
            assert call_params["facet_name"] == "Diagnosis"
            assert call_params["entity_name"] == "ADHD"
            assert call_params["concept_name"] == "DSM-5 Criteria"

    @pytest.mark.asyncio
    async def test_add_entity_to_facet_returns_false_on_error(self):
        """Test that add_entity_to_facet returns False on database error."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=Exception("Database error"),
        ):
            result = await GraphService.add_entity_to_facet(
                facet_name="Diagnosis",
                entity_name="ADHD",
                concept_name="Test",
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_add_entity_to_facet_returns_false_when_facet_not_found(self):
        """Test that add_entity_to_facet returns False when facet doesn't exist."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[],  # No results = facet or concept not found
        ):
            result = await GraphService.add_entity_to_facet(
                facet_name="NonExistent",
                entity_name="ADHD",
                concept_name="Test",
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_add_entity_to_facet_returns_false_when_concept_not_found(self):
        """Test that add_entity_to_facet returns False when concept doesn't exist."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[],  # Concept not found
        ):
            result = await GraphService.add_entity_to_facet(
                facet_name="Diagnosis",
                entity_name="ADHD",
                concept_name="NonExistentConcept",
            )

            assert result is False


class TestFacetIntegration:
    """Integration-style tests for facet workflows."""

    @pytest.mark.asyncio
    async def test_facet_workflow_create_and_populate(self):
        """Test complete workflow: create facet, add entities, retrieve."""
        # Simulate creating a facet
        create_result = [{"f": {"name": "Treatment", "entity": "ADHD"}}]

        # Simulate adding entities
        add_result1 = [{"f": {}, "c": {"name": "Medication"}}]
        add_result2 = [{"f": {}, "c": {"name": "Therapy"}}]

        # Simulate retrieving facets
        entity_result = [{"e": {"name": "ADHD"}, "labels": ["Concept"]}]
        facets_result = [
            {
                "facet_name": "Treatment",
                "facet_description": None,
                "facet_order": 0,
                "entities": [
                    {"name": "Medication", "type": "Concept", "relationship": "BELONGS_TO"},
                    {"name": "Therapy", "type": "Concept", "relationship": "BELONGS_TO"},
                ],
            }
        ]

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query:
            # Create facet
            mock_query.return_value = create_result
            created = await GraphService.create_facet("ADHD", "Treatment")
            assert created is True

            # Add entities
            mock_query.return_value = add_result1
            added1 = await GraphService.add_entity_to_facet("Treatment", "ADHD", "Medication")
            assert added1 is True

            mock_query.return_value = add_result2
            added2 = await GraphService.add_entity_to_facet("Treatment", "ADHD", "Therapy")
            assert added2 is True

            # Retrieve facets
            mock_query.side_effect = [entity_result, facets_result]
            result = await GraphService.get_entity_facets("ADHD")

            assert result is not None
            assert len(result["facets"]) == 1
            assert result["facets"][0]["name"] == "Treatment"
            assert result["facets"][0]["entity_count"] == 2


class TestGetEntityEvidence:
    """Tests for get_entity_evidence method (Sprint 2)."""

    @pytest.mark.asyncio
    async def test_get_entity_evidence_returns_chunk_evidence(self):
        """Test that get_entity_evidence returns evidence from chunks."""
        mock_chunk_results = [
            {
                "id": "chunk_001",
                "text": "ADHD affects dopamine regulation in the prefrontal cortex...",
                "chapter": "Chapter 3",
                "source_file": "books/adhd-2.0.epub",
                "book_title": "ADHD 2.0",
                "book_author": "Edward Hallowell",
            },
            {
                "id": "chunk_002",
                "text": "The dopamine hypothesis suggests that ADHD symptoms...",
                "chapter": "Chapter 5",
                "source_file": None,
                "book_title": "Driven to Distraction",
                "book_author": "Edward Hallowell",
            },
        ]

        # Mock: chunks first, then empty books (no additional needed)
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=[
                mock_chunk_results,  # Chunk query
                [],  # Book query (no additional)
                [{"chunk_count": 2}],  # Count query
                [{"book_count": 0}],  # Book count query
            ],
        ):
            result = await GraphService.get_entity_evidence("ADHD")

            assert result["entity_name"] == "ADHD"
            assert len(result["evidence"]) == 2
            assert result["evidence"][0]["source_type"] == "chunk"
            assert result["evidence"][0]["confidence"] == 1.0
            assert result["evidence"][0]["text"].startswith("ADHD affects")
            assert result["evidence"][0]["source_title"] == "ADHD 2.0"
            assert result["evidence"][0]["location"]["chapter"] == "Chapter 3"

    @pytest.mark.asyncio
    async def test_get_entity_evidence_includes_book_mentions_when_sparse(self):
        """Test that book-level mentions are included when chunks are sparse."""
        mock_chunk_results = [
            {
                "id": "chunk_001",
                "text": "One chunk about dopamine...",
                "chapter": None,
                "source_file": "book1.epub",
                "book_title": "Book 1",
                "book_author": "Author 1",
            },
        ]
        mock_book_results = [
            {
                "title": "Book 2",
                "author": "Author 2",
                "description": "A comprehensive guide to ADHD.",
            },
        ]

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=[
                mock_chunk_results,  # Chunk query
                mock_book_results,  # Book query
                [{"chunk_count": 1}],  # Count query
                [{"book_count": 1}],  # Book count query
            ],
        ):
            result = await GraphService.get_entity_evidence("ADHD", limit=20)

            assert len(result["evidence"]) == 2

            # Chunk evidence comes first (higher confidence)
            chunk_evidence = [e for e in result["evidence"] if e["source_type"] == "chunk"]
            book_evidence = [e for e in result["evidence"] if e["source_type"] == "book"]

            assert len(chunk_evidence) == 1
            assert len(book_evidence) == 1
            assert book_evidence[0]["confidence"] == 0.7  # Lower confidence
            assert book_evidence[0]["source_title"] == "Book 2"

    @pytest.mark.asyncio
    async def test_get_entity_evidence_returns_empty_when_no_evidence(self):
        """Test that get_entity_evidence returns empty list when no evidence."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=[
                [],  # No chunks
                [],  # No books
                [{"chunk_count": 0}],
                [{"book_count": 0}],
            ],
        ):
            result = await GraphService.get_entity_evidence("Unknown Entity")

            assert result["entity_name"] == "Unknown Entity"
            assert result["evidence"] == []
            assert result["total_count"] == 0

    @pytest.mark.asyncio
    async def test_get_entity_evidence_respects_limit(self):
        """Test that get_entity_evidence respects the limit parameter."""
        mock_chunks = [
            {"id": f"chunk_{i}", "text": f"Evidence {i}", "chapter": None,
             "source_file": f"book{i}.epub", "book_title": f"Book {i}", "book_author": None}
            for i in range(3)  # Returns exactly 3 chunks
        ]

        # When limit is met (3 chunks returned, limit=3), book query is skipped
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=[
                mock_chunks,  # Chunk query returns 3
                # Book query skipped (len(evidence) >= limit)
                [{"chunk_count": 5}],  # Total chunks in graph
                [{"book_count": 2}],  # Total book mentions
            ],
        ):
            result = await GraphService.get_entity_evidence("Test", limit=3)

            assert len(result["evidence"]) == 3
            assert result["total_count"] == 7  # 5 chunks + 2 books = total available

    @pytest.mark.asyncio
    async def test_get_entity_evidence_handles_query_errors(self):
        """Test that get_entity_evidence handles database errors gracefully."""
        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=Exception("Database error"),
        ):
            result = await GraphService.get_entity_evidence("Test")

            # Should return empty result, not raise
            assert result["entity_name"] == "Test"
            assert result["evidence"] == []

    @pytest.mark.asyncio
    async def test_get_entity_evidence_excludes_book_mentions_when_disabled(self):
        """Test that include_book_mentions=False excludes book-level evidence."""
        mock_chunks = [
            {"id": "chunk_001", "text": "Only chunk", "chapter": None,
             "source_file": "book.epub", "book_title": "Book", "book_author": None}
        ]

        with patch(
            "ies_backend.services.graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            side_effect=[
                mock_chunks,
                # Book query should not be called
                [{"chunk_count": 1}],
                [{"book_count": 5}],  # Even though 5 books exist
            ],
        ):
            result = await GraphService.get_entity_evidence(
                "Test", include_book_mentions=False
            )

            # Only chunk evidence, no book mentions
            assert len(result["evidence"]) == 1
            assert all(e["source_type"] == "chunk" for e in result["evidence"])
