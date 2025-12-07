"""Tests for UnifiedGraphClient - single Neo4j client combining all three existing clients.

This test suite validates:
1. Entity type preservation (no 14→4 collapse)
2. Cypher injection protection
3. Single connection pool (singleton pattern)
4. Personal-domain bridge methods (SPARKED_BY relationships)
5. All methods from KnowledgeGraph, ADHDKnowledgeGraph, and GraphService
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from library.graph.unified_client import (
    UnifiedGraphClient,
    ALLOWED_TYPES,
    get_driver,
)
from library.graph.adhd_ontology import (
    ResonanceSignal,
    EnergyLevel,
    EntityStatus,
    RelationshipType,
)


class TestEntityTypePreservation:
    """Test that entity types are preserved, not collapsed to generic Concept."""

    def test_add_entity_preserves_framework_type(self):
        """Framework entities should keep Framework label, not collapse to Concept."""
        with patch("library.graph.unified_client.get_driver") as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

            client = UnifiedGraphClient()
            client.add_entity_with_type("Test Framework", "Framework", "A test framework")

            # Verify MERGE query uses Framework label
            call_args = mock_session.run.call_args
            query = call_args[0][0]
            assert ":Framework" in query
            assert "MERGE (e:Framework" in query

    def test_add_entity_preserves_person_type(self):
        """Person entities should keep Person label."""
        with patch("library.graph.unified_client.get_driver") as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

            client = UnifiedGraphClient()
            client.add_entity_with_type("Russell Barkley", "Person", "ADHD researcher")

            call_args = mock_session.run.call_args
            query = call_args[0][0]
            assert ":Person" in query

    def test_add_entity_preserves_theory_type(self):
        """Theory entities should keep Theory label."""
        with patch("library.graph.unified_client.get_driver") as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

            client = UnifiedGraphClient()
            client.add_entity_with_type("Cognitive Load Theory", "Theory", "Theory of learning")

            call_args = mock_session.run.call_args
            query = call_args[0][0]
            assert ":Theory" in query

    def test_add_entity_preserves_spark_type(self):
        """Spark entities (personal) should keep Spark label."""
        with patch("library.graph.unified_client.get_driver") as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

            client = UnifiedGraphClient()
            client.add_entity_with_type("Interesting idea", "Spark", "A moment of insight")

            call_args = mock_session.run.call_args
            query = call_args[0][0]
            assert ":Spark" in query


class TestCypherInjectionProtection:
    """Test that invalid entity types are blocked (Cypher injection protection)."""

    def test_invalid_entity_type_raises_error(self):
        """Invalid entity types should raise ValueError."""
        client = UnifiedGraphClient()

        with pytest.raises(ValueError, match="Invalid entity type"):
            client.add_entity_with_type("Test", "InvalidType'; DROP TABLE users; --", "Injection attempt")

    def test_allowed_types_include_all_14_types(self):
        """ALLOWED_TYPES should include all 14 entity types."""
        expected_types = {
            # Domain types
            "Concept", "Person", "Theory", "Framework", "Assessment",
            # Personal types
            "Spark", "Insight", "Thread", "FavoriteProblem",
            # Enrichment types
            "Reframe", "Pattern", "Mechanism", "Method",
            # Content types
            "Book", "Chunk",
        }
        assert expected_types.issubset(ALLOWED_TYPES)

    def test_sql_injection_string_blocked(self):
        """SQL injection patterns should be blocked."""
        client = UnifiedGraphClient()

        with pytest.raises(ValueError):
            client.add_entity_with_type("Test", "Concept'; DELETE FROM nodes; --", "SQL injection")


class TestSingletonConnectionPool:
    """Test that driver is a singleton with single connection pool."""

    def test_get_driver_returns_same_instance(self):
        """Multiple calls to get_driver() should return same driver instance."""
        # Reset global driver
        import library.graph.unified_client as module
        module._driver = None

        with patch("library.graph.unified_client.GraphDatabase") as mock_gdb:
            mock_driver = MagicMock()
            mock_gdb.driver.return_value = mock_driver

            driver1 = get_driver()
            driver2 = get_driver()

            # Should only create driver once
            assert mock_gdb.driver.call_count == 1
            assert driver1 is driver2

    def test_driver_uses_connection_pool_settings(self):
        """Driver should be created with connection pool configuration."""
        import library.graph.unified_client as module
        module._driver = None

        with patch("library.graph.unified_client.GraphDatabase") as mock_gdb:
            get_driver()

            call_kwargs = mock_gdb.driver.call_args[1]
            assert call_kwargs.get("max_connection_lifetime") == 3600
            assert call_kwargs.get("max_connection_pool_size") == 50


class TestPersonalDomainBridge:
    """Test methods that bridge personal graph (sparks) with domain graph (entities)."""

    def test_link_spark_to_entity_creates_sparked_by_relationship(self):
        """link_spark_to_entity should create SPARKED_BY relationship."""
        with patch("library.graph.unified_client.get_driver") as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

            client = UnifiedGraphClient()
            client.link_spark_to_entity("spark_123", "Executive Function")

            # Verify relationship creation
            call_args = mock_session.run.call_args
            query = call_args[0][0]
            assert "SPARKED_BY" in query
            assert "spark_123" in str(call_args[1])
            assert "Executive Function" in str(call_args[1])

    def test_find_sparks_for_entity_returns_user_sparks(self):
        """find_sparks_for_entity should find sparks linked to a domain entity."""
        with patch("library.graph.unified_client.get_driver") as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

            # Mock query results
            mock_result = MagicMock()
            mock_result.__iter__ = lambda self: iter([
                {"spark_id": "spark_1", "title": "First spark"},
                {"spark_id": "spark_2", "title": "Second spark"},
            ])
            mock_session.run.return_value = mock_result

            client = UnifiedGraphClient()
            sparks = client.find_sparks_for_entity("Executive Function")

            # Verify query structure
            call_args = mock_session.run.call_args
            query = call_args[0][0]
            assert "SPARKED_BY" in query
            assert len(sparks) == 2

    def test_find_entities_for_spark_returns_domain_concepts(self):
        """find_entities_for_spark should find domain entities linked to a spark."""
        with patch("library.graph.unified_client.get_driver") as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

            mock_result = MagicMock()
            mock_result.__iter__ = lambda self: iter([
                {"name": "Executive Function", "type": "Concept"},
            ])
            mock_session.run.return_value = mock_result

            client = UnifiedGraphClient()
            entities = client.find_entities_for_spark("spark_123")

            assert len(entities) == 1
            assert entities[0]["name"] == "Executive Function"

    def test_enrich_entity_from_sparks_updates_entity_properties(self):
        """enrich_entity_from_sparks should update entity with insights from sparks."""
        with patch("library.graph.unified_client.get_driver") as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

            client = UnifiedGraphClient()
            client.enrich_entity_from_sparks("Executive Function", user_insights="Personal experience notes")

            # Verify entity update
            call_args = mock_session.run.call_args
            query = call_args[0][0]
            assert "SET" in query
            assert "user_insights" in str(call_args[1])


class TestKnowledgeGraphMethods:
    """Test methods from original KnowledgeGraph class (16 methods)."""

    def test_add_book_creates_book_node(self):
        """add_book should create Book node with calibre_id."""
        with patch("library.graph.unified_client.get_driver") as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

            client = UnifiedGraphClient()
            client.add_book("Test Book", "Author", "/path", calibre_id=42)

            call_args = mock_session.run.call_args
            query = call_args[0][0]
            assert "Book" in query
            assert "calibre_id" in str(call_args[1])

    def test_book_exists_checks_by_calibre_id(self):
        """book_exists should check for book by calibre_id."""
        with patch("library.graph.unified_client.get_driver") as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

            mock_result = MagicMock()
            mock_result.single.return_value = {"exists": True}
            mock_session.run.return_value = mock_result

            client = UnifiedGraphClient()
            exists = client.book_exists(42)

            assert exists is True


class TestADHDGraphMethods:
    """Test methods from ADHDKnowledgeGraph class (24 methods)."""

    def test_capture_spark_creates_spark_node(self):
        """capture_spark should create Spark node with resonance signal."""
        with patch("library.graph.unified_client.get_driver") as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

            client = UnifiedGraphClient()
            spark_id = client.capture_spark(
                title="Test Spark",
                content="Content",
                resonance_signal=ResonanceSignal.CURIOUS,
                energy_level=EnergyLevel.MEDIUM
            )

            assert spark_id.startswith("spark_")
            call_args = mock_session.run.call_args
            query = call_args[0][0]
            assert "Spark" in query
            # Parameter name in query is 'resonance', not 'resonance_signal'
            assert "resonance" in str(call_args[1])

    def test_find_by_energy_level_filters_correctly(self):
        """find_by_energy_level should filter entities by energy level."""
        with patch("library.graph.unified_client.get_driver") as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

            mock_result = MagicMock()
            mock_result.__iter__ = lambda self: iter([])
            mock_session.run.return_value = mock_result

            client = UnifiedGraphClient()
            results = client.find_by_energy_level(EnergyLevel.LOW, limit=10)

            call_args = mock_session.run.call_args
            query = call_args[0][0]
            assert "energy_level" in query


class TestGraphServiceMethods:
    """Test query methods from GraphService class (7 methods)."""

    def test_search_concepts_by_name(self):
        """search_concepts should find concepts by name substring."""
        with patch("library.graph.unified_client.get_driver") as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

            mock_result = MagicMock()
            mock_result.__iter__ = lambda self: iter([
                {"name": "Executive Function", "labels": ["Concept"]},
            ])
            mock_session.run.return_value = mock_result

            client = UnifiedGraphClient()
            results = client.search_concepts("Executive", limit=10)

            assert len(results) == 1
            call_args = mock_session.run.call_args
            query = call_args[0][0]
            assert "CONTAINS" in query or "contains" in query.lower()

    def test_get_most_connected_returns_top_nodes(self):
        """get_most_connected should return nodes with most relationships."""
        with patch("library.graph.unified_client.get_driver") as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

            mock_result = MagicMock()
            mock_result.__iter__ = lambda self: iter([
                {"name": "Executive Function", "labels": ["Concept"], "connections": 15},
            ])
            mock_session.run.return_value = mock_result

            client = UnifiedGraphClient()
            results = client.get_most_connected(limit=10)

            assert len(results) == 1
            assert results[0]["connections"] == 15
