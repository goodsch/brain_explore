"""Passage Ranking Service.

Ranks text passages from books by relevance to a specific question.
Uses keyword extraction, TF-IDF-like scoring, and concept matching.
"""

import logging
import re
from collections import Counter
from typing import Optional

from ies_backend.schemas.passage import (
    PassageRankingRequest,
    PassageRankingResponse,
    RankedPassage,
)
from ies_backend.services.neo4j_client import Neo4jClient
from ies_backend.services.question_service import QuestionService

logger = logging.getLogger(__name__)


class PassageRankingService:
    """Service for ranking passages by relevance to questions."""

    # Common stop words to exclude from keyword extraction
    STOP_WORDS = {
        "what", "how", "why", "when", "where", "who", "which", "whom",
        "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "having",
        "do", "does", "did", "doing",
        "would", "could", "should", "may", "might", "must", "can",
        "will", "shall",
        "the", "a", "an", "and", "or", "but", "if", "then",
        "to", "of", "in", "for", "on", "at", "by", "with", "from",
        "as", "into", "through", "during", "before", "after",
        "above", "below", "between", "under", "over",
        "this", "that", "these", "those",
        "i", "you", "he", "she", "it", "we", "they",
        "my", "your", "his", "her", "its", "our", "their",
        "me", "him", "us", "them",
        "about", "against", "among", "around", "because",
        "some", "such", "than", "too", "very",
        "not", "no", "yes",
    }

    @classmethod
    def _extract_keywords(cls, text: str, min_length: int = 3) -> list[str]:
        """Extract keywords from text by removing stop words and short words.

        Args:
            text: Input text to extract keywords from
            min_length: Minimum word length to consider

        Returns:
            List of keywords (lowercase, deduplicated)
        """
        # Convert to lowercase and split on non-word characters
        words = re.findall(r'\b\w+\b', text.lower())

        # Filter stop words and short words
        keywords = [
            w for w in words
            if w not in cls.STOP_WORDS and len(w) >= min_length
        ]

        # Return unique keywords, preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        return unique_keywords

    @classmethod
    def _calculate_relevance_score(
        cls,
        passage_text: str,
        keywords: list[str],
        concepts: list[str],
    ) -> tuple[float, list[str]]:
        """Calculate relevance score for a passage.

        Scoring algorithm:
        - Keyword match: +0.1 per keyword (normalized by passage length)
        - Concept match: +0.3 per concept
        - Multiple occurrences: diminishing returns (log scale)

        Args:
            passage_text: The passage to score
            keywords: Keywords to search for
            concepts: Related concepts to search for

        Returns:
            Tuple of (relevance_score, matched_keywords)
        """
        passage_lower = passage_text.lower()
        passage_words = set(re.findall(r'\b\w+\b', passage_lower))

        # Count keyword matches
        keyword_matches = []
        keyword_score = 0.0
        for kw in keywords:
            if kw.lower() in passage_lower:
                keyword_matches.append(kw)
                # Count occurrences (with diminishing returns)
                count = passage_lower.count(kw.lower())
                keyword_score += 0.1 * (1 + 0.5 * (count - 1))

        # Count concept matches (concepts are more valuable)
        concept_score = 0.0
        for concept in concepts:
            concept_lower = concept.lower()
            if concept_lower in passage_lower:
                keyword_matches.append(concept)
                count = passage_lower.count(concept_lower)
                concept_score += 0.3 * (1 + 0.5 * (count - 1))

        # Normalize by passage length (longer passages have natural advantage)
        word_count = len(passage_words)
        length_penalty = min(1.0, 100.0 / max(word_count, 1))

        # Combine scores
        raw_score = (keyword_score + concept_score) * length_penalty

        # Cap at 1.0
        final_score = min(1.0, raw_score)

        return final_score, keyword_matches

    @classmethod
    async def rank_passages_for_question(
        cls,
        question_id: str,
        request: Optional[PassageRankingRequest] = None,
    ) -> PassageRankingResponse:
        """Rank passages by relevance to a question.

        Args:
            question_id: Question to find passages for
            request: Optional ranking parameters

        Returns:
            PassageRankingResponse with ranked passages

        Raises:
            ValueError: If question not found
        """
        # Default request if not provided
        if request is None:
            request = PassageRankingRequest()

        # Get question
        question = await QuestionService().get(question_id)
        if not question:
            raise ValueError(f"Question not found: {question_id}")

        # Extract keywords from question text
        keywords = cls._extract_keywords(question.text)

        # Add related concepts as additional keywords
        concepts = question.related_concepts or []

        # Build search query for Neo4j
        # Search both question keywords and related concepts
        all_search_terms = keywords + concepts

        if not all_search_terms:
            # No keywords to search with
            return PassageRankingResponse(
                question_id=question_id,
                question_text=question.text,
                passages=[],
                total_candidates=0,
                keywords_used=[],
            )

        # Limit search terms to avoid overly complex queries
        search_terms = all_search_terms[:20]

        # Build Cypher query to find relevant chunks
        # Use CONTAINS for case-insensitive substring matching
        term_conditions = " OR ".join([
            f"toLower(c.text) CONTAINS toLower('{term}')"
            for term in search_terms
        ])

        query = f"""
        MATCH (b:Book)-[:HAS_CHUNK]->(c:Chunk)
        WHERE ({term_conditions})
        RETURN c.id as chunk_id,
               c.text as text,
               b.calibre_id as source_id,
               b.title as source_title,
               b.author as source_author,
               c.chapter as chapter,
               c.page as page
        LIMIT $max_candidates
        """

        try:
            # Query Neo4j for candidate passages
            # Get more candidates than needed for ranking
            max_candidates = request.max_passages * 5
            results = await Neo4jClient.execute_query(
                query,
                {"max_candidates": max_candidates}
            )

            if not results:
                return PassageRankingResponse(
                    question_id=question_id,
                    question_text=question.text,
                    passages=[],
                    total_candidates=0,
                    keywords_used=search_terms,
                )

            # Score and rank passages
            ranked = []
            for result in results:
                score, matched = cls._calculate_relevance_score(
                    passage_text=result["text"],
                    keywords=keywords,
                    concepts=concepts,
                )

                # Filter by minimum score
                if score >= request.min_score:
                    # Get concepts mentioned in this passage
                    # (Simple approach: check which concepts appear)
                    concepts_mentioned = [
                        c for c in concepts
                        if c.lower() in result["text"].lower()
                    ]

                    ranked.append(RankedPassage(
                        chunk_id=result["chunk_id"],
                        text=result["text"],
                        relevance_score=score,
                        source_id=str(result["source_id"]) if result.get("source_id") else None,
                        source_title=result.get("source_title"),
                        source_author=result.get("source_author"),
                        chapter=result.get("chapter"),
                        page=result.get("page"),
                        keywords_matched=matched,
                        concepts_mentioned=concepts_mentioned,
                    ))

            # Sort by relevance score (descending)
            ranked.sort(key=lambda p: p.relevance_score, reverse=True)

            # Limit to requested max
            final_passages = ranked[:request.max_passages]

            return PassageRankingResponse(
                question_id=question_id,
                question_text=question.text,
                passages=final_passages,
                total_candidates=len(results),
                keywords_used=search_terms,
            )

        except Exception as e:
            logger.error(f"Failed to rank passages for question {question_id}: {e}")
            raise
