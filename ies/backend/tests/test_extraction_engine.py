"""Tests for Extraction Engine service."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ies_backend.schemas.context import (
    Context,
    ContextStatus,
    ContextType,
    Question,
)
from ies_backend.schemas.extraction import (
    ExtractionProfile,
    ExtractionResult,
    ExtractionRunRequest,
    ExtractionRunResponse,
)
from ies_backend.schemas.question import QuestionSource, QuestionStatus
from ies_backend.services.extraction_engine import ExtractionEngine


@pytest.fixture
def sample_context():
    """Sample context for testing."""
    return Context(
        id="ctx_test123",
        type=ContextType.FEYNMAN_PROBLEM,
        title="Understanding Executive Function",
        status=ContextStatus.ACTIVE,
        core_concepts=["executive function", "working memory", "ADHD"],
        linked_sources=["42", "87"],
        key_questions=[],
        artifacts={},
    )


@pytest.fixture
def sample_question():
    """Sample question for testing."""
    return Question(
        id="q_test456",
        context_id="ctx_test123",
        text="How does executive function relate to working memory?",
        question_type="HOW",
        status=QuestionStatus.OPEN,
        source=QuestionSource.READER,
        prerequisite_questions=[],
        related_concepts=["executive function", "working memory"],
        linked_sources=[],
        created_at="2025-12-09T00:00:00Z",
        updated_at="2025-12-09T00:00:00Z",
    )


@pytest.fixture
def sample_profile():
    """Sample extraction profile."""
    return ExtractionProfile(
        context_id="ctx_test123",
        core_concepts=["executive function", "working memory"],
        synonyms={
            "executive function": ["EF", "cognitive control"],
            "working memory": ["WM", "short-term memory"],
        },
        relation_types=["supports", "contradicts", "enables"],
        domain_filters=["neuroscience", "psychology"],
    )


@pytest.fixture
def sample_segments():
    """Sample search segments."""
    return [
        {
            "source_id": "42",
            "source_title": "ADHD 2.0",
            "text": "Executive function involves working memory and impulse control...",
            "chunk_id": "chunk_1",
            "score": 0.95,
        },
        {
            "source_id": "42",
            "source_title": "ADHD 2.0",
            "text": "Working memory is a key component of executive function...",
            "chunk_id": "chunk_2",
            "score": 0.87,
        },
        {
            "source_id": "87",
            "source_title": "Driven to Distraction",
            "text": "ADHD affects executive function through dopamine regulation...",
            "chunk_id": "chunk_3",
            "score": 0.72,
        },
    ]


class TestExtractionEngineProfile:
    """Tests for profile management."""

    def test_save_profile(self, sample_profile):
        """Test saving an extraction profile."""
        saved = ExtractionEngine.save_profile(sample_profile)

        assert saved.context_id == "ctx_test123"
        assert saved == sample_profile

    def test_get_profile(self, sample_profile):
        """Test retrieving a saved profile."""
        ExtractionEngine.save_profile(sample_profile)
        retrieved = ExtractionEngine.get_profile("ctx_test123")

        assert retrieved is not None
        assert retrieved.context_id == "ctx_test123"
        assert retrieved.core_concepts == sample_profile.core_concepts

    def test_get_nonexistent_profile(self):
        """Test getting a profile that doesn't exist."""
        result = ExtractionEngine.get_profile("nonexistent_ctx")
        assert result is None

    def test_create_default_profile(self, sample_context):
        """Test creating default profile from context."""
        profile = ExtractionEngine._create_default_profile(sample_context)

        assert profile.context_id == sample_context.id
        assert profile.core_concepts == sample_context.core_concepts
        assert profile.synonyms == {}
        assert "supports" in profile.relation_types


class TestKeywordBuilding:
    """Tests for keyword extraction."""

    def test_build_keywords_from_profile(self, sample_profile):
        """Test building keywords from profile only."""
        keywords = ExtractionEngine._build_keywords(sample_profile, None)

        assert "executive function" in keywords
        assert "working memory" in keywords
        assert "EF" in keywords  # synonym
        assert "cognitive control" in keywords  # synonym
        assert len(keywords) == len(set(keywords))  # no duplicates

    def test_build_keywords_with_question(self, sample_profile, sample_question):
        """Test building keywords including question terms."""
        keywords = ExtractionEngine._build_keywords(sample_profile, sample_question)

        assert "executive function" in keywords
        assert "relate" in keywords  # from question
        # stopwords should be filtered
        assert "does" not in keywords
        assert "to" not in keywords

    def test_stopword_filtering(self, sample_profile):
        """Test that stopwords are filtered from questions."""
        question = Question(
            id="q_test",
            context_id="ctx_test123",
            text="What is the relationship between concepts?",
            question_type="WHAT",
            status=QuestionStatus.OPEN,
            source=QuestionSource.READER,
            prerequisite_questions=[],
            related_concepts=[],
            linked_sources=[],
            created_at="2025-12-09T00:00:00Z",
            updated_at="2025-12-09T00:00:00Z",
        )

        keywords = ExtractionEngine._build_keywords(sample_profile, question)

        # stopwords should not appear
        assert "what" not in keywords
        assert "is" not in keywords
        assert "the" not in keywords
        # content words should appear (with punctuation removed)
        assert "relationship" in keywords
        assert "concepts" in keywords
        assert "between" in keywords


class TestSourceFiltering:
    """Tests for domain-based source filtering."""

    @pytest.mark.asyncio
    async def test_filter_sources_no_domains(self):
        """Test that sources pass through when no domain filters."""
        source_ids = ["42", "87", "123"]
        filtered = await ExtractionEngine._filter_sources_by_domain(
            source_ids=source_ids,
            domain_filters=[],
        )
        assert filtered == source_ids

    @pytest.mark.asyncio
    async def test_filter_sources_no_sources(self):
        """Test filtering with empty source list."""
        filtered = await ExtractionEngine._filter_sources_by_domain(
            source_ids=[],
            domain_filters=["neuroscience"],
        )
        assert filtered == []

    @pytest.mark.asyncio
    async def test_filter_sources_by_domain(self):
        """Test filtering sources by domain tags."""
        with patch.object(
            ExtractionEngine, "_filter_sources_by_domain",
            return_value=["42", "87"]
        ) as mock_filter:
            filtered = await ExtractionEngine._filter_sources_by_domain(
                source_ids=["42", "87", "123"],
                domain_filters=["neuroscience", "psychology"],
            )
            assert len(filtered) == 2
            assert "42" in filtered
            assert "87" in filtered


class TestInvertedIndexSearch:
    """Tests for full-text index search."""

    @pytest.mark.asyncio
    async def test_search_inverted_index_no_keywords(self):
        """Test search with empty keywords."""
        segments = await ExtractionEngine._search_inverted_index(
            keywords=[],
            source_ids=["42"],
            max_segments=50,
        )
        assert segments == []

    @pytest.mark.asyncio
    async def test_search_inverted_index_success(self, sample_segments):
        """Test successful full-text search."""
        mock_neo4j_results = [
            {
                "source_id": 42,
                "source_title": "ADHD 2.0",
                "text": "Executive function involves...",
                "chunk_id": "chunk_1",
                "score": 0.95,
            }
        ]

        with patch(
            "ies_backend.services.extraction_engine.Neo4jClient.execute_query",
            return_value=mock_neo4j_results,
        ):
            segments = await ExtractionEngine._search_inverted_index(
                keywords=["executive function", "working memory"],
                source_ids=["42"],
                max_segments=50,
            )

            assert len(segments) == 1
            assert segments[0]["source_id"] == "42"
            assert segments[0]["score"] == 0.95

    @pytest.mark.asyncio
    async def test_search_fallback_on_index_error(self, sample_segments):
        """Test fallback to CONTAINS when full-text index fails."""
        with patch(
            "ies_backend.services.extraction_engine.Neo4jClient.execute_query",
            side_effect=Exception("Index not found"),
        ):
            with patch.object(
                ExtractionEngine,
                "_search_segments_fallback",
                return_value=sample_segments,
            ) as mock_fallback:
                segments = await ExtractionEngine._search_inverted_index(
                    keywords=["executive function"],
                    source_ids=["42"],
                    max_segments=50,
                )

                mock_fallback.assert_called_once()
                assert len(segments) == 3


class TestLLMExtraction:
    """Tests for LLM-based entity extraction."""

    @pytest.mark.asyncio
    async def test_extract_from_segments_empty(self, sample_context, sample_profile):
        """Test extraction with no segments."""
        result = await ExtractionEngine._extract_from_segments(
            segments=[],
            context=sample_context,
            profile=sample_profile,
            question=None,
        )

        assert result.context_id == "ctx_test123"
        assert result.sources_processed == 0
        assert result.segments_analyzed == 0
        assert result.concepts_found == []

    @pytest.mark.asyncio
    async def test_extract_from_segments_success(
        self, sample_context, sample_profile, sample_segments
    ):
        """Test successful LLM extraction."""
        mock_llm_response = {
            "concepts": ["executive function", "working memory", "impulse control"],
            "relationships": [
                {
                    "source": "executive function",
                    "target": "working memory",
                    "type": "component_of",
                    "evidence": "Working memory is a key component",
                }
            ],
            "questions": ["How does dopamine affect executive function?"],
        }

        # Create mock response with JSON string
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(mock_llm_response))]

        with patch("ies_backend.services.extraction_engine.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            result = await ExtractionEngine._extract_from_segments(
                segments=sample_segments,
                context=sample_context,
                profile=sample_profile,
                question=None,
            )

            assert result.sources_processed == 2  # 2 unique source_ids
            assert result.segments_analyzed == 3
            assert len(result.concepts_found) == 3
            assert len(result.relations_found) == 1
            assert len(result.subquestions_generated) == 1


class TestKnowledgeGraphPersistence:
    """Tests for persisting to Neo4j knowledge graph."""

    @pytest.mark.asyncio
    async def test_persist_empty_result(self):
        """Test persistence with empty results."""
        result = ExtractionResult(context_id="ctx_test123")

        # Should not raise error and should return without DB calls
        await ExtractionEngine._persist_to_knowledge_graph(
            result=result,
            context_id="ctx_test123",
        )

    @pytest.mark.asyncio
    async def test_persist_concepts(self):
        """Test persisting concepts to knowledge graph."""
        result = ExtractionResult(
            context_id="ctx_test123",
            concepts_found=["executive function", "working memory"],
        )

        with patch(
            "ies_backend.services.extraction_engine.Neo4jClient.execute_write",
            return_value=[{"name": "executive function"}],
        ) as mock_write:
            await ExtractionEngine._persist_to_knowledge_graph(
                result=result,
                context_id="ctx_test123",
            )

            # Should be called once per concept
            assert mock_write.call_count >= 2

    @pytest.mark.asyncio
    async def test_persist_relationships(self):
        """Test persisting relationships to knowledge graph."""
        result = ExtractionResult(
            context_id="ctx_test123",
            concepts_found=["executive function", "working memory"],
            relations_found=[
                {
                    "source": "executive function",
                    "target": "working memory",
                    "type": "component_of",
                    "evidence": "quote from text",
                }
            ],
        )

        with patch(
            "ies_backend.services.extraction_engine.Neo4jClient.execute_write",
            return_value=[{"rel_type": "COMPONENT_OF"}],
        ) as mock_write:
            await ExtractionEngine._persist_to_knowledge_graph(
                result=result,
                context_id="ctx_test123",
            )

            # Should be called for concepts + relationships
            assert mock_write.call_count >= 3


class TestSubquestionGeneration:
    """Tests for creating AI-generated subquestions."""

    @pytest.mark.asyncio
    async def test_create_subquestions_empty(self):
        """Test with no questions to create."""
        await ExtractionEngine._create_subquestions(
            questions=[],
            context_id="ctx_test123",
            parent_question_id=None,
        )
        # Should not raise error

    @pytest.mark.asyncio
    async def test_create_subquestions_success(self):
        """Test successful question creation."""
        questions = [
            "How does dopamine affect executive function?",
            "What is the role of prefrontal cortex?",
        ]

        with patch(
            "ies_backend.services.extraction_engine.QuestionService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service.create = AsyncMock()
            mock_service_class.return_value = mock_service

            await ExtractionEngine._create_subquestions(
                questions=questions,
                context_id="ctx_test123",
                parent_question_id="q_parent",
            )

            # Should be called once per question
            assert mock_service.create.call_count == 2

            # Verify correct source is set
            call_args = mock_service.create.call_args_list[0][0][0]
            assert call_args.source == QuestionSource.AI_SUGGESTED
            assert call_args.parent_question_id == "q_parent"


class TestFullExtractionPipeline:
    """Integration tests for complete extraction pipeline."""

    @pytest.mark.asyncio
    async def test_run_extraction_context_not_found(self):
        """Test extraction with non-existent context."""
        request = ExtractionRunRequest(context_id="nonexistent")

        with patch(
            "ies_backend.services.extraction_engine.ContextService.get_context",
            return_value=None,
        ):
            response = await ExtractionEngine.run_extraction(request)

            assert response.result.context_id == "nonexistent"
            assert response.journey_entry_id is None

    @pytest.mark.asyncio
    async def test_run_extraction_full_pipeline(
        self, sample_context, sample_profile, sample_segments
    ):
        """Test complete extraction pipeline."""
        request = ExtractionRunRequest(
            context_id="ctx_test123",
            question_id=None,
            source_ids=["42", "87"],
            max_segments=50,
        )

        mock_extraction_result = ExtractionResult(
            context_id="ctx_test123",
            concepts_found=["executive function", "working memory"],
            relations_found=[{"source": "A", "target": "B", "type": "enables"}],
            subquestions_generated=["How does X affect Y?"],
            sources_processed=2,
            segments_analyzed=3,
        )

        with patch(
            "ies_backend.services.extraction_engine.ContextService.get_context",
            return_value=sample_context,
        ):
            with patch.object(
                ExtractionEngine, "get_profile", return_value=sample_profile
            ):
                with patch.object(
                    ExtractionEngine,
                    "_filter_sources_by_domain",
                    return_value=["42", "87"],
                ):
                    with patch.object(
                        ExtractionEngine,
                        "_search_inverted_index",
                        return_value=sample_segments,
                    ):
                        with patch.object(
                            ExtractionEngine,
                            "_extract_from_segments",
                            return_value=mock_extraction_result,
                        ):
                            with patch.object(
                                ExtractionEngine,
                                "_persist_to_knowledge_graph",
                            ):
                                with patch.object(
                                    ExtractionEngine,
                                    "_create_subquestions",
                                ):
                                    with patch.object(
                                        ExtractionEngine,
                                        "_log_extraction_journey",
                                        return_value="je_test123",
                                    ):
                                        response = await ExtractionEngine.run_extraction(
                                            request
                                        )

        assert response.result.context_id == "ctx_test123"
        assert len(response.result.concepts_found) == 2
        assert response.journey_entry_id == "je_test123"

    @pytest.mark.asyncio
    async def test_run_extraction_creates_default_profile(self, sample_context):
        """Test that default profile is created if none exists."""
        request = ExtractionRunRequest(context_id="ctx_test123")

        with patch(
            "ies_backend.services.extraction_engine.ContextService.get_context",
            return_value=sample_context,
        ):
            with patch.object(ExtractionEngine, "get_profile", return_value=None):
                with patch.object(
                    ExtractionEngine, "save_profile"
                ) as mock_save:
                    with patch.object(
                        ExtractionEngine,
                        "_filter_sources_by_domain",
                        return_value=[],
                    ):
                        with patch.object(
                            ExtractionEngine,
                            "_search_inverted_index",
                            return_value=[],
                        ):
                            with patch.object(
                                ExtractionEngine,
                                "_log_extraction_journey",
                                return_value="je_test",
                            ):
                                await ExtractionEngine.run_extraction(request)

                                # Should create and save default profile
                                mock_save.assert_called_once()
