"""Tests for ReframeGenerator (Pass 3: Generative Reframe Creation).

Validates proactive reframe generation that connects abstract concepts
to concrete stories/patterns when explicit reframes don't exist.
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from library.graph.reframe_generator import (
    ReframeGenerator,
    GeneratedReframe,
    DENSE_CONCEPT_THRESHOLD,
)


class TestGeneratedReframe:
    """Test the GeneratedReframe dataclass."""

    def test_generated_reframe_creation(self):
        """GeneratedReframe should store all fields correctly."""
        reframe = GeneratedReframe(
            concept_name="Working Memory",
            source_entity="Backwards Bicycle",
            source_type="story_insight",
            reframe_type="Metaphor",
            domain="Neuroscience",
            text="Your working memory is like the backwards bicycle: it keeps snapping back to old patterns.",
            structural_connection="Both involve unlearning deeply ingrained pathways"
        )
        assert reframe.concept_name == "Working Memory"
        assert reframe.source_entity == "Backwards Bicycle"
        assert reframe.reframe_type == "Metaphor"
        assert "backwards bicycle" in reframe.text.lower()

    def test_generated_reframe_valid_types(self):
        """GeneratedReframe should accept all valid reframe types."""
        for reframe_type in ["Metaphor", "Analogy", "Story", "Pattern", "Contrast"]:
            reframe = GeneratedReframe(
                concept_name="Test",
                source_entity="Source",
                source_type="pattern",
                reframe_type=reframe_type,
                domain="Test",
                text="Test reframe",
                structural_connection="Test connection"
            )
            assert reframe.reframe_type == reframe_type


class TestReframeGeneratorQueries:
    """Test ReframeGenerator graph query methods."""

    @pytest.fixture
    def mock_kg(self):
        """Create a mock KnowledgeGraph."""
        kg = MagicMock()
        kg.driver = MagicMock()
        return kg

    def test_get_concepts_needing_reframes(self, mock_kg):
        """Should return high-connectivity concepts with few reframes."""
        mock_session = MagicMock()
        mock_kg.driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.return_value = [
            {"name": "Executive Function", "description": "Self-management", "in_degree": 15, "reframe_count": 0},
            {"name": "Working Memory", "description": "Cognitive capacity", "in_degree": 12, "reframe_count": 1},
        ]

        with patch("library.graph.reframe_generator.OpenAI"):
            generator = ReframeGenerator(mock_kg)
            concepts = generator.get_concepts_needing_reframes(limit=10)

        assert len(concepts) == 2
        assert concepts[0]["in_degree"] == 15  # Highest connectivity first
        assert concepts[0]["reframe_count"] == 0  # Needs reframes most

        # Verify threshold is passed to query
        call_args = mock_session.run.call_args
        assert call_args[1]["threshold"] == DENSE_CONCEPT_THRESHOLD

    def test_get_story_insights_and_patterns(self, mock_kg):
        """Should return available story/pattern sources."""
        mock_session = MagicMock()
        mock_kg.driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.return_value = [
            {"name": "Backwards Bicycle", "type": "story_insight", "description": "Unlearning", "source_domain": "Neuroscience"},
            {"name": "Feedback Loop", "type": "pattern", "description": "Self-regulation", "source_domain": "Systems"},
        ]

        with patch("library.graph.reframe_generator.OpenAI"):
            generator = ReframeGenerator(mock_kg)
            sources = generator.get_story_insights_and_patterns(limit=20)

        assert len(sources) == 2
        assert sources[0]["type"] == "story_insight"
        assert sources[1]["type"] == "pattern"

    def test_find_best_source_excludes_already_used(self, mock_kg):
        """Should exclude sources already used for this concept's reframes."""
        mock_session = MagicMock()
        mock_kg.driver.session.return_value.__enter__.return_value = mock_session

        # First call returns already used sources
        mock_record = MagicMock()
        mock_record.__getitem__ = lambda self, key: ["Backwards Bicycle"]  # Already used
        mock_session.run.return_value.single.return_value = mock_record

        with patch("library.graph.reframe_generator.OpenAI"):
            generator = ReframeGenerator(mock_kg)

            concept = {"name": "Working Memory", "description": "Test"}
            sources = [
                {"name": "Backwards Bicycle", "type": "story_insight"},  # Already used
                {"name": "Feedback Loop", "type": "pattern"},  # Available
            ]

            best = generator.find_best_source_for_concept(concept, sources)

        assert best["name"] == "Feedback Loop"  # Should pick unused source

    def test_find_best_source_returns_none_when_all_used(self, mock_kg):
        """Should return None when all sources are already used."""
        mock_session = MagicMock()
        mock_kg.driver.session.return_value.__enter__.return_value = mock_session

        mock_record = MagicMock()
        mock_record.__getitem__ = lambda self, key: ["Source A", "Source B"]
        mock_session.run.return_value.single.return_value = mock_record

        with patch("library.graph.reframe_generator.OpenAI"):
            generator = ReframeGenerator(mock_kg)

            concept = {"name": "Test Concept", "description": "Test"}
            sources = [
                {"name": "Source A", "type": "pattern"},
                {"name": "Source B", "type": "story_insight"},
            ]

            best = generator.find_best_source_for_concept(concept, sources)

        assert best is None


class TestReframeGeneratorLLMIntegration:
    """Test LLM-based reframe generation."""

    @pytest.fixture
    def generator_with_mocks(self):
        """Create generator with mocked dependencies."""
        mock_kg = MagicMock()
        mock_kg.driver = MagicMock()

        with patch("library.graph.reframe_generator.OpenAI") as mock_openai:
            generator = ReframeGenerator(mock_kg)
            generator.mock_openai = mock_openai
            yield generator

    def test_generate_reframe_success(self, generator_with_mocks):
        """Should generate a reframe from concept + source pairing."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "reframe_type": "Metaphor",
            "domain": "Neuroscience",
            "text": "Your working memory is like the backwards bicycle: old patterns keep snapping back.",
            "structural_connection": "Both involve unlearning ingrained pathways"
        })
        generator_with_mocks.client.chat.completions.create.return_value = mock_response

        concept = {"name": "Working Memory", "description": "Cognitive holding capacity"}
        source = {"name": "Backwards Bicycle", "type": "story_insight", "description": "Unlearning experiment"}

        reframe = generator_with_mocks.generate_reframe(concept, source)

        assert reframe is not None
        assert reframe.concept_name == "Working Memory"
        assert reframe.source_entity == "Backwards Bicycle"
        assert reframe.reframe_type == "Metaphor"
        assert "backwards bicycle" in reframe.text.lower()

    def test_generate_reframe_handles_llm_error(self, generator_with_mocks):
        """Should return None on LLM error, not crash."""
        generator_with_mocks.client.chat.completions.create.side_effect = Exception("API error")

        concept = {"name": "Test", "description": "Test"}
        source = {"name": "Source", "type": "pattern", "description": "Test"}

        reframe = generator_with_mocks.generate_reframe(concept, source)

        assert reframe is None

    def test_generate_reframe_uses_source_domain_fallback(self, generator_with_mocks):
        """Should use source's domain when LLM doesn't provide one."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "reframe_type": "Analogy",
            "text": "Test reframe text",
            "structural_connection": "Test connection"
            # No domain field
        })
        generator_with_mocks.client.chat.completions.create.return_value = mock_response

        concept = {"name": "Concept", "description": "Test"}
        source = {"name": "Source", "type": "pattern", "description": "Test", "source_domain": "Physics"}

        reframe = generator_with_mocks.generate_reframe(concept, source)

        assert reframe.domain == "Physics"  # Falls back to source domain


class TestReframeGeneratorStorage:
    """Test storing generated reframes in Neo4j."""

    @pytest.fixture
    def generator_with_session(self):
        """Create generator with mocked session for storage testing."""
        mock_kg = MagicMock()
        mock_session = MagicMock()
        mock_kg.driver.session.return_value.__enter__.return_value = mock_session

        with patch("library.graph.reframe_generator.OpenAI"):
            generator = ReframeGenerator(mock_kg)
            generator.mock_session = mock_session
            yield generator

    def test_store_generated_reframe_success(self, generator_with_session):
        """Should store reframe in graph with correct properties."""
        reframe = GeneratedReframe(
            concept_name="Executive Function",
            source_entity="Feedback Loop",
            source_type="pattern",
            reframe_type="Analogy",
            domain="Systems",
            text="Executive function is like a feedback loop: constant adjustment based on results.",
            structural_connection="Both involve iterative self-correction"
        )

        result = generator_with_session.store_generated_reframe(reframe)

        assert result is True
        generator_with_session.mock_session.run.assert_called_once()

        # Verify key properties are passed
        call_args = generator_with_session.mock_session.run.call_args
        assert call_args[1]["concept_name"] == "Executive Function"
        assert call_args[1]["source_entity"] == "Feedback Loop"
        assert "source: 'generated_pass3'" in call_args[0][0]

    def test_store_generated_reframe_handles_db_error(self, generator_with_session):
        """Should return False on DB error, not crash."""
        generator_with_session.mock_session.run.side_effect = Exception("DB error")

        reframe = GeneratedReframe(
            concept_name="Test",
            source_entity="Source",
            source_type="pattern",
            reframe_type="Metaphor",
            domain="Test",
            text="Test reframe",
            structural_connection="Test"
        )

        result = generator_with_session.store_generated_reframe(reframe)

        assert result is False


class TestReframeGeneratorBatchProcessing:
    """Test the batch generation orchestration."""

    @pytest.fixture
    def fully_mocked_generator(self):
        """Create generator with all methods mocked for orchestration testing."""
        mock_kg = MagicMock()
        mock_kg.driver = MagicMock()

        with patch("library.graph.reframe_generator.OpenAI"):
            generator = ReframeGenerator(mock_kg)
            generator.get_concepts_needing_reframes = MagicMock()
            generator.get_story_insights_and_patterns = MagicMock()
            generator.find_best_source_for_concept = MagicMock()
            generator.generate_reframe = MagicMock()
            generator.store_generated_reframe = MagicMock()
            yield generator

    def test_run_batch_generation_full_pipeline(self, fully_mocked_generator):
        """Should orchestrate full Pass 3 batch pipeline."""
        fully_mocked_generator.get_concepts_needing_reframes.return_value = [
            {"name": "Concept A", "description": "Test"},
            {"name": "Concept B", "description": "Test"}
        ]
        fully_mocked_generator.get_story_insights_and_patterns.return_value = [
            {"name": "Source 1", "type": "pattern"},
            {"name": "Source 2", "type": "story_insight"}
        ]
        fully_mocked_generator.find_best_source_for_concept.return_value = {"name": "Source 1", "type": "pattern"}

        mock_reframe = GeneratedReframe("Concept", "Source", "pattern", "Metaphor", "Test", "text", "connection")
        fully_mocked_generator.generate_reframe.return_value = mock_reframe
        fully_mocked_generator.store_generated_reframe.return_value = True

        result = fully_mocked_generator.run_batch_generation(max_concepts=10)

        assert result["concepts"] == 2
        assert result["sources_available"] == 2
        assert result["generated"] == 2
        assert result["stored"] == 2

    def test_run_batch_generation_no_concepts(self, fully_mocked_generator):
        """Should return early when no concepts need reframes."""
        fully_mocked_generator.get_concepts_needing_reframes.return_value = []

        result = fully_mocked_generator.run_batch_generation(max_concepts=10)

        assert result["concepts"] == 0
        assert result["generated"] == 0
        fully_mocked_generator.get_story_insights_and_patterns.assert_not_called()

    def test_run_batch_generation_no_sources(self, fully_mocked_generator):
        """Should return early when no story/pattern sources available."""
        fully_mocked_generator.get_concepts_needing_reframes.return_value = [
            {"name": "Concept", "description": "Test"}
        ]
        fully_mocked_generator.get_story_insights_and_patterns.return_value = []

        result = fully_mocked_generator.run_batch_generation(max_concepts=10)

        assert result["concepts"] == 1
        assert result["generated"] == 0
        fully_mocked_generator.find_best_source_for_concept.assert_not_called()

    def test_run_batch_generation_skips_concepts_without_sources(self, fully_mocked_generator):
        """Should skip concepts when no unused source is available."""
        fully_mocked_generator.get_concepts_needing_reframes.return_value = [
            {"name": "Concept A", "description": "Test"},
            {"name": "Concept B", "description": "Test"}
        ]
        fully_mocked_generator.get_story_insights_and_patterns.return_value = [
            {"name": "Source", "type": "pattern"}
        ]
        # First concept gets source, second doesn't
        fully_mocked_generator.find_best_source_for_concept.side_effect = [
            {"name": "Source", "type": "pattern"},
            None  # No source for second concept
        ]

        mock_reframe = GeneratedReframe("Concept", "Source", "pattern", "Metaphor", "Test", "text", "connection")
        fully_mocked_generator.generate_reframe.return_value = mock_reframe
        fully_mocked_generator.store_generated_reframe.return_value = True

        result = fully_mocked_generator.run_batch_generation(max_concepts=10)

        assert result["generated"] == 1  # Only one generated


class TestConstants:
    """Test module constants are correctly defined."""

    def test_dense_concept_threshold_reasonable(self):
        """Threshold should be positive and reasonable."""
        assert DENSE_CONCEPT_THRESHOLD >= 1
        assert DENSE_CONCEPT_THRESHOLD <= 10  # Shouldn't be too restrictive
