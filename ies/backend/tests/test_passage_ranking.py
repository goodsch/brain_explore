"""Tests for passage ranking service."""

import pytest
from unittest.mock import AsyncMock, patch

from ies_backend.schemas.question import Question, QuestionStatus, QuestionSource
from ies_backend.schemas.passage import (
    PassageRankingRequest,
    PassageRankingResponse,
    RankedPassage,
)
from ies_backend.services.passage_ranking_service import PassageRankingService


class TestPassageRankingService:
    """Test suite for PassageRankingService."""

    def test_extract_keywords(self):
        """Test keyword extraction from text."""
        text = "How does ADHD affect executive function in adults?"
        keywords = PassageRankingService._extract_keywords(text)

        # Should extract meaningful words, excluding stop words
        assert "adhd" in keywords
        assert "affect" in keywords
        assert "executive" in keywords
        assert "function" in keywords
        assert "adults" in keywords

        # Stop words should be excluded
        assert "how" not in keywords
        assert "does" not in keywords
        assert "in" not in keywords

    def test_extract_keywords_min_length(self):
        """Test that short words are filtered out."""
        text = "Why is it so hard to focus?"
        keywords = PassageRankingService._extract_keywords(text, min_length=3)

        # Words shorter than 3 chars should be excluded
        assert "so" not in keywords
        assert "to" not in keywords
        assert "is" not in keywords

        # Longer words should be included
        assert "hard" in keywords
        assert "focus" in keywords

    def test_calculate_relevance_score_keyword_match(self):
        """Test relevance scoring with keyword matches."""
        passage = "Executive function is a key cognitive ability that helps with planning and organization."
        keywords = ["executive", "function", "cognitive"]
        concepts = []

        score, matched = PassageRankingService._calculate_relevance_score(
            passage, keywords, concepts
        )

        # Should have positive score
        assert score > 0.0
        assert score <= 1.0

        # Should identify matched keywords
        assert "executive" in matched
        assert "function" in matched
        assert "cognitive" in matched

    def test_calculate_relevance_score_concept_bonus(self):
        """Test that concept matches score higher than keywords."""
        passage = "Working memory is a core component of executive function."
        keywords = ["memory"]
        concepts = ["working memory", "executive function"]

        score_with_concepts, _ = PassageRankingService._calculate_relevance_score(
            passage, keywords, concepts
        )

        # Score with concepts should be higher
        score_without_concepts, _ = PassageRankingService._calculate_relevance_score(
            passage, keywords, []
        )

        assert score_with_concepts > score_without_concepts

    def test_calculate_relevance_score_no_match(self):
        """Test that passages with no matches have zero score."""
        passage = "The quick brown fox jumps over the lazy dog."
        keywords = ["adhd", "executive", "function"]
        concepts = []

        score, matched = PassageRankingService._calculate_relevance_score(
            passage, keywords, concepts
        )

        assert score == 0.0
        assert len(matched) == 0

    def test_calculate_relevance_score_multiple_occurrences(self):
        """Test diminishing returns for multiple keyword occurrences."""
        passage_one = "Executive function is important. Executive function helps with planning."
        passage_two = "Executive function is important for planning."
        keywords = ["executive", "function"]
        concepts = []

        score_one, _ = PassageRankingService._calculate_relevance_score(
            passage_one, keywords, concepts
        )
        score_two, _ = PassageRankingService._calculate_relevance_score(
            passage_two, keywords, concepts
        )

        # First passage has more matches but should not score 2x higher
        # due to diminishing returns
        assert score_one > score_two
        assert score_one < score_two * 2.0

    @pytest.mark.asyncio
    async def test_rank_passages_question_not_found(self):
        """Test that ranking fails gracefully when question doesn't exist."""
        with patch(
            'ies_backend.services.passage_ranking_service.QuestionService'
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get.return_value = None
            mock_service_class.return_value = mock_service

            with pytest.raises(ValueError, match="Question not found"):
                await PassageRankingService.rank_passages_for_question(
                    question_id="nonexistent"
                )

    @pytest.mark.asyncio
    async def test_rank_passages_no_keywords(self):
        """Test ranking with a question that has no keywords."""
        # Mock question with no meaningful keywords
        mock_question = Question(
            id="q1",
            context_id="ctx1",
            text="Is it?",
            status=QuestionStatus.OPEN,
            source=QuestionSource.READER,
            prerequisite_questions=[],
            related_concepts=[],
            linked_sources=[],
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )

        with patch(
            'ies_backend.services.passage_ranking_service.QuestionService'
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get.return_value = mock_question
            mock_service_class.return_value = mock_service

            response = await PassageRankingService.rank_passages_for_question(
                question_id="q1"
            )

            assert response.question_id == "q1"
            assert len(response.passages) == 0
            assert response.total_candidates == 0
            assert len(response.keywords_used) == 0

    @pytest.mark.asyncio
    async def test_rank_passages_with_results(self):
        """Test full passage ranking with mock Neo4j results."""
        # Mock question
        mock_question = Question(
            id="q1",
            context_id="ctx1",
            text="How does executive function affect time perception?",
            status=QuestionStatus.OPEN,
            source=QuestionSource.READER,
            prerequisite_questions=[],
            related_concepts=["working memory", "time blindness"],
            linked_sources=[],
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )

        # Mock Neo4j results
        mock_chunks = [
            {
                "chunk_id": "chunk1",
                "text": "Executive function plays a crucial role in time perception and working memory.",
                "source_id": 123,
                "source_title": "ADHD and Time",
                "source_author": "Dr. Smith",
                "chapter": "Chapter 3",
                "page": 42,
            },
            {
                "chunk_id": "chunk2",
                "text": "Time blindness is a common symptom related to executive function deficits.",
                "source_id": 123,
                "source_title": "ADHD and Time",
                "source_author": "Dr. Smith",
                "chapter": "Chapter 5",
                "page": 67,
            },
            {
                "chunk_id": "chunk3",
                "text": "The quick brown fox jumps over the lazy dog.",  # Irrelevant
                "source_id": 456,
                "source_title": "Other Book",
                "source_author": "Other Author",
                "chapter": None,
                "page": None,
            },
        ]

        with patch(
            'ies_backend.services.passage_ranking_service.QuestionService'
        ) as mock_service_class, patch(
            'ies_backend.services.passage_ranking_service.Neo4jClient'
        ) as mock_neo4j:
            # Setup mocks
            mock_service = AsyncMock()
            mock_service.get.return_value = mock_question
            mock_service_class.return_value = mock_service

            mock_neo4j.execute_query = AsyncMock(return_value=mock_chunks)

            # Execute ranking
            response = await PassageRankingService.rank_passages_for_question(
                question_id="q1"
            )

            # Verify response structure
            assert response.question_id == "q1"
            assert response.question_text == mock_question.text
            assert response.total_candidates == 3
            assert len(response.keywords_used) > 0

            # Should have passages (irrelevant one might be filtered by min_score)
            assert len(response.passages) > 0

            # Verify passages are sorted by score (descending)
            scores = [p.relevance_score for p in response.passages]
            assert scores == sorted(scores, reverse=True)

            # Verify passage structure
            for passage in response.passages:
                assert passage.chunk_id in ["chunk1", "chunk2", "chunk3"]
                assert passage.relevance_score >= 0.0
                assert passage.relevance_score <= 1.0
                assert passage.text
                assert passage.source_id

    @pytest.mark.asyncio
    async def test_rank_passages_with_filters(self):
        """Test passage ranking with request filters."""
        mock_question = Question(
            id="q1",
            context_id="ctx1",
            text="How does ADHD affect focus?",
            status=QuestionStatus.OPEN,
            source=QuestionSource.READER,
            prerequisite_questions=[],
            related_concepts=[],
            linked_sources=[],
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )

        mock_chunks = [
            {
                "chunk_id": f"chunk{i}",
                "text": "ADHD and focus " * i,  # Varying relevance
                "source_id": 123,
                "source_title": "Book",
                "source_author": "Author",
                "chapter": None,
                "page": None,
            }
            for i in range(1, 21)
        ]

        with patch(
            'ies_backend.services.passage_ranking_service.QuestionService'
        ) as mock_service_class, patch(
            'ies_backend.services.passage_ranking_service.Neo4jClient'
        ) as mock_neo4j:
            mock_service = AsyncMock()
            mock_service.get.return_value = mock_question
            mock_service_class.return_value = mock_service
            mock_neo4j.execute_query = AsyncMock(return_value=mock_chunks)

            # Test with max_passages limit
            request = PassageRankingRequest(
                max_passages=5,
                min_score=0.0,
            )
            response = await PassageRankingService.rank_passages_for_question(
                question_id="q1",
                request=request,
            )

            # Should respect max_passages
            assert len(response.passages) <= 5

    @pytest.mark.asyncio
    async def test_rank_passages_with_min_score_filter(self):
        """Test that passages below min_score are filtered out."""
        mock_question = Question(
            id="q1",
            context_id="ctx1",
            text="executive function",
            status=QuestionStatus.OPEN,
            source=QuestionSource.READER,
            prerequisite_questions=[],
            related_concepts=[],
            linked_sources=[],
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )

        # One highly relevant, one barely relevant
        mock_chunks = [
            {
                "chunk_id": "chunk1",
                "text": "Executive function is crucial for cognitive control and working memory.",
                "source_id": 123,
                "source_title": "Book",
                "source_author": "Author",
                "chapter": None,
                "page": None,
            },
            {
                "chunk_id": "chunk2",
                "text": "The weather is nice today, and function halls are popular.",
                "source_id": 123,
                "source_title": "Book",
                "source_author": "Author",
                "chapter": None,
                "page": None,
            },
        ]

        with patch(
            'ies_backend.services.passage_ranking_service.QuestionService'
        ) as mock_service_class, patch(
            'ies_backend.services.passage_ranking_service.Neo4jClient'
        ) as mock_neo4j:
            mock_service = AsyncMock()
            mock_service.get.return_value = mock_question
            mock_service_class.return_value = mock_service
            mock_neo4j.execute_query = AsyncMock(return_value=mock_chunks)

            # Use high min_score to filter out weak matches
            request = PassageRankingRequest(
                max_passages=10,
                min_score=0.5,
            )
            response = await PassageRankingService.rank_passages_for_question(
                question_id="q1",
                request=request,
            )

            # Should filter out low-scoring passages
            for passage in response.passages:
                assert passage.relevance_score >= 0.5
