"""Tests for ReframeMapper (Pass 2: Cross-Domain Mapping).

Validates the "ADHD Leap" - finding non-obvious structural connections
between newly extracted patterns/stories and existing concepts.
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from dataclasses import asdict

from library.graph.reframe_mapper import (
    ReframeMapper,
    ResonanceMatch,
    REFRAME_SOURCE_TYPES,
    CONFIDENCE_THRESHOLD,
)


class TestResonanceMatch:
    """Test the ResonanceMatch dataclass."""

    def test_resonance_match_creation(self):
        """ResonanceMatch should store all fields correctly."""
        match = ResonanceMatch(
            source_entity="Feedback Loop Pattern",
            target_concept="Emotional Regulation",
            relationship_type="RESONATES_WITH",
            confidence=0.85,
            rationale="Both involve cyclical self-adjustment mechanisms"
        )
        assert match.source_entity == "Feedback Loop Pattern"
        assert match.target_concept == "Emotional Regulation"
        assert match.relationship_type == "RESONATES_WITH"
        assert match.confidence == 0.85

    def test_resonance_match_valid_relationship_types(self):
        """ResonanceMatch should accept all valid relationship types."""
        for rel_type in ["RESONATES_WITH", "METAPHOR_FOR", "ANALOGOUS_TO"]:
            match = ResonanceMatch(
                source_entity="Test",
                target_concept="Target",
                relationship_type=rel_type,
                confidence=0.8,
                rationale="Test"
            )
            assert match.relationship_type == rel_type


class TestReframeMapperQueries:
    """Test ReframeMapper graph query methods."""

    @pytest.fixture
    def mock_kg(self):
        """Create a mock KnowledgeGraph."""
        kg = MagicMock()
        kg.driver = MagicMock()
        return kg

    def test_get_reframe_sources_for_book(self, mock_kg):
        """Should query for pattern/story entities from a specific book."""
        mock_session = MagicMock()
        mock_kg.driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.return_value = [
            {"name": "Backwards Bicycle", "type": "story_insight", "description": "Unlearning experiment"},
            {"name": "Feedback Loop", "type": "pattern", "description": "Self-regulating cycle"},
        ]

        with patch("library.graph.reframe_mapper.OpenAI"):
            mapper = ReframeMapper(mock_kg)
            sources = mapper.get_reframe_sources_for_book(calibre_id=42)

        assert len(sources) == 2
        assert sources[0]["name"] == "Backwards Bicycle"
        assert sources[1]["type"] == "pattern"

        # Verify query includes REFRAME_SOURCE_TYPES
        call_args = mock_session.run.call_args
        assert call_args[1]["source_types"] == REFRAME_SOURCE_TYPES
        assert call_args[1]["calibre_id"] == 42

    def test_get_concepts_without_reframes(self, mock_kg):
        """Should return concepts ordered by fewest reframe connections."""
        mock_session = MagicMock()
        mock_kg.driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.return_value = [
            {"name": "Working Memory", "description": "Cognitive capacity", "reframe_count": 0},
            {"name": "Executive Function", "description": "Self-management", "reframe_count": 1},
        ]

        with patch("library.graph.reframe_mapper.OpenAI"):
            mapper = ReframeMapper(mock_kg)
            concepts = mapper.get_concepts_without_reframes(limit=10)

        assert len(concepts) == 2
        assert concepts[0]["reframe_count"] == 0  # Prioritized

        # Verify limit is passed
        call_args = mock_session.run.call_args
        assert call_args[1]["limit"] == 10


class TestReframeMapperLLMIntegration:
    """Test LLM-based resonance finding."""

    @pytest.fixture
    def mapper_with_mocks(self):
        """Create mapper with mocked dependencies."""
        mock_kg = MagicMock()
        mock_kg.driver = MagicMock()

        with patch("library.graph.reframe_mapper.OpenAI") as mock_openai:
            mapper = ReframeMapper(mock_kg)
            mapper.mock_openai = mock_openai
            yield mapper

    def test_find_resonances_returns_matches_above_threshold(self, mapper_with_mocks):
        """Should return only matches with confidence >= CONFIDENCE_THRESHOLD."""
        # Mock LLM response with mixed confidence scores
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "matches": [
                {
                    "target_concept": "Emotional Regulation",
                    "relationship_type": "RESONATES_WITH",
                    "confidence": 0.85,  # Above threshold
                    "rationale": "Both involve feedback mechanisms"
                },
                {
                    "target_concept": "Time Blindness",
                    "relationship_type": "METAPHOR_FOR",
                    "confidence": 0.5,  # Below threshold (0.7)
                    "rationale": "Weak connection"
                }
            ]
        })
        mapper_with_mocks.client.chat.completions.create.return_value = mock_response

        source = {"name": "Feedback Loop", "type": "pattern", "description": "Self-regulating cycle"}
        concepts = [
            {"name": "Emotional Regulation", "description": "Managing emotions"},
            {"name": "Time Blindness", "description": "ADHD time perception"}
        ]

        matches = mapper_with_mocks.find_resonances(source, concepts)

        assert len(matches) == 1  # Only high-confidence match
        assert matches[0].target_concept == "Emotional Regulation"
        assert matches[0].confidence == 0.85

    def test_find_resonances_empty_concepts_returns_empty(self, mapper_with_mocks):
        """Should return empty list when no concepts provided."""
        source = {"name": "Test Pattern", "type": "pattern", "description": "Test"}

        matches = mapper_with_mocks.find_resonances(source, [])

        assert matches == []
        # Should not call LLM
        mapper_with_mocks.client.chat.completions.create.assert_not_called()

    def test_find_resonances_handles_llm_error(self, mapper_with_mocks):
        """Should return empty list on LLM error, not crash."""
        mapper_with_mocks.client.chat.completions.create.side_effect = Exception("API error")

        source = {"name": "Test", "type": "pattern", "description": "Test"}
        concepts = [{"name": "Concept", "description": "Test concept"}]

        matches = mapper_with_mocks.find_resonances(source, concepts)

        assert matches == []


class TestReframeMapperRelationshipCreation:
    """Test graph relationship creation from matches."""

    @pytest.fixture
    def mapper_with_session(self):
        """Create mapper with mocked session for relationship creation."""
        mock_kg = MagicMock()
        mock_session = MagicMock()
        mock_kg.driver.session.return_value.__enter__.return_value = mock_session

        with patch("library.graph.reframe_mapper.OpenAI"):
            mapper = ReframeMapper(mock_kg)
            mapper.mock_session = mock_session
            yield mapper

    def test_create_resonance_relationships_success(self, mapper_with_session):
        """Should create graph relationships for valid matches."""
        matches = [
            ResonanceMatch(
                source_entity="Backwards Bicycle",
                target_concept="Neuroplasticity",
                relationship_type="METAPHOR_FOR",
                confidence=0.9,
                rationale="Both demonstrate unlearning/relearning"
            ),
            ResonanceMatch(
                source_entity="Feedback Loop",
                target_concept="Emotional Regulation",
                relationship_type="RESONATES_WITH",
                confidence=0.85,
                rationale="Cyclical self-adjustment"
            )
        ]

        created = mapper_with_session.create_resonance_relationships(matches)

        assert created == 2
        assert mapper_with_session.mock_session.run.call_count == 2

    def test_create_resonance_relationships_handles_db_error(self, mapper_with_session):
        """Should continue processing after individual failures."""
        mapper_with_session.mock_session.run.side_effect = [
            Exception("DB error"),  # First fails
            None  # Second succeeds
        ]

        matches = [
            ResonanceMatch("A", "B", "RESONATES_WITH", 0.8, "test"),
            ResonanceMatch("C", "D", "METAPHOR_FOR", 0.9, "test")
        ]

        created = mapper_with_session.create_resonance_relationships(matches)

        assert created == 1  # One succeeded despite first failure


class TestReframeMapperProcessBook:
    """Test the main process_book orchestration method."""

    @pytest.fixture
    def fully_mocked_mapper(self):
        """Create mapper with all methods mocked for orchestration testing."""
        mock_kg = MagicMock()
        mock_kg.driver = MagicMock()

        with patch("library.graph.reframe_mapper.OpenAI"):
            mapper = ReframeMapper(mock_kg)
            # Mock individual methods
            mapper.get_reframe_sources_for_book = MagicMock()
            mapper.get_concepts_without_reframes = MagicMock()
            mapper.find_resonances = MagicMock()
            mapper.create_resonance_relationships = MagicMock()
            yield mapper

    def test_process_book_full_pipeline(self, fully_mocked_mapper):
        """Should orchestrate full Pass 2 pipeline."""
        fully_mocked_mapper.get_reframe_sources_for_book.return_value = [
            {"name": "Pattern A", "type": "pattern", "description": "Test"}
        ]
        fully_mocked_mapper.get_concepts_without_reframes.return_value = [
            {"name": "Concept X", "description": "Test"}
        ]
        fully_mocked_mapper.find_resonances.return_value = [
            ResonanceMatch("Pattern A", "Concept X", "RESONATES_WITH", 0.8, "test")
        ]
        fully_mocked_mapper.create_resonance_relationships.return_value = 1

        result = fully_mocked_mapper.process_book(calibre_id=42)

        assert result["sources"] == 1
        assert result["matches"] == 1
        assert result["relationships"] == 1
        fully_mocked_mapper.kg.update_book_status.assert_called_with(42, "relationships_mapped")

    def test_process_book_no_sources(self, fully_mocked_mapper):
        """Should return early when no reframe sources found."""
        fully_mocked_mapper.get_reframe_sources_for_book.return_value = []

        result = fully_mocked_mapper.process_book(calibre_id=42)

        assert result["sources"] == 0
        assert result["matches"] == 0
        fully_mocked_mapper.find_resonances.assert_not_called()

    def test_process_book_no_concepts(self, fully_mocked_mapper):
        """Should return early when no concepts in graph."""
        fully_mocked_mapper.get_reframe_sources_for_book.return_value = [
            {"name": "Pattern", "type": "pattern", "description": "Test"}
        ]
        fully_mocked_mapper.get_concepts_without_reframes.return_value = []

        result = fully_mocked_mapper.process_book(calibre_id=42)

        assert result["sources"] == 1
        assert result["matches"] == 0
        fully_mocked_mapper.find_resonances.assert_not_called()


class TestConstants:
    """Test module constants are correctly defined."""

    def test_reframe_source_types_complete(self):
        """Should include all entity types that can serve as reframe sources."""
        expected = ["pattern", "dynamic_pattern", "story_insight", "schema_break"]
        assert REFRAME_SOURCE_TYPES == expected

    def test_confidence_threshold_reasonable(self):
        """Threshold should be between 0.5 and 1.0."""
        assert 0.5 <= CONFIDENCE_THRESHOLD <= 1.0
