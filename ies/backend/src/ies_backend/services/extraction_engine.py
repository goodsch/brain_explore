"""Extraction Engine Service.

Context-aware entity extraction that uses ExtractionProfile to find
relevant concepts and relationships from sources.

Pipeline:
1. Load context and profile
2. Filter sources by domain_filters
3. Search sources for core_concepts + synonyms
4. Extract entities and relationships via LLM
5. Write to knowledge graph
6. Generate subquestions
7. Log journey entry
"""

import logging
import uuid
from datetime import datetime, timezone

from anthropic import Anthropic

from ..schemas.context import (
    Context,
    ContextJourneyEntry,
    JourneyClassification,
    Question,
)
from ..schemas.extraction import (
    ExtractionProfile,
    ExtractionResult,
    ExtractionRunRequest,
    ExtractionRunResponse,
)
from .context_service import ContextService
from .neo4j_client import Neo4jClient

logger = logging.getLogger(__name__)


class ExtractionEngine:
    """Context-aware extraction engine."""

    # In-memory profile storage (MVP)
    _profiles: dict[str, ExtractionProfile] = {}

    @classmethod
    def save_profile(cls, profile: ExtractionProfile) -> ExtractionProfile:
        """Save an extraction profile for a context."""
        cls._profiles[profile.context_id] = profile
        return profile

    @classmethod
    def get_profile(cls, context_id: str) -> ExtractionProfile | None:
        """Get extraction profile for a context."""
        return cls._profiles.get(context_id)

    @classmethod
    async def run_extraction(
        cls, request: ExtractionRunRequest
    ) -> ExtractionRunResponse:
        """Run context-aware extraction.

        Args:
            request: Extraction run configuration

        Returns:
            ExtractionRunResponse with results and journey entry ID
        """
        context_id = request.context_id
        question_id = request.question_id

        # Load context
        context = await ContextService.get_context(context_id)
        if not context:
            logger.warning(f"Context not found: {context_id}")
            return ExtractionRunResponse(
                result=ExtractionResult(context_id=context_id),
                journey_entry_id=None,
            )

        # Load or create profile
        profile = cls.get_profile(context_id)
        if not profile:
            # Create default profile from context
            profile = cls._create_default_profile(context)
            cls.save_profile(profile)

        # Get question focus if specified
        question: Question | None = None
        if question_id:
            question = await ContextService.get_question(question_id)

        # Build search keywords
        keywords = cls._build_keywords(profile, question)

        # Search for relevant segments
        segments = await cls._search_segments(
            keywords=keywords,
            source_ids=request.source_ids or context.linked_sources,
            domain_filters=profile.domain_filters,
            max_segments=request.max_segments or 50,
        )

        # Extract entities and relationships
        extraction_result = await cls._extract_from_segments(
            segments=segments,
            context=context,
            profile=profile,
            question=question,
        )

        # Log journey entry
        journey_entry_id = await cls._log_extraction_journey(
            context_id=context_id,
            question_id=question_id,
            result=extraction_result,
        )

        return ExtractionRunResponse(
            result=extraction_result,
            journey_entry_id=journey_entry_id,
        )

    @classmethod
    def _create_default_profile(cls, context: Context) -> ExtractionProfile:
        """Create default extraction profile from context."""
        return ExtractionProfile(
            context_id=context.id or "",
            core_concepts=context.core_concepts,
            synonyms={},
            relation_types=["supports", "contradicts", "component_of", "enables"],
            domain_filters=[],
        )

    @classmethod
    def _build_keywords(
        cls, profile: ExtractionProfile, question: Question | None
    ) -> list[str]:
        """Build search keywords from profile and question."""
        keywords = list(profile.core_concepts)

        # Add synonyms
        for concept, syns in profile.synonyms.items():
            keywords.extend(syns)

        # Add question terms if provided
        if question:
            # Simple tokenization of question text
            words = question.text.lower().split()
            # Filter common words
            stopwords = {
                "what", "how", "why", "when", "where", "is", "are", "the",
                "a", "an", "to", "of", "in", "for", "and", "or", "with",
                "does", "do", "can", "could", "would", "should", "this", "that",
            }
            keywords.extend([w for w in words if w not in stopwords and len(w) > 2])

        return list(set(keywords))

    @classmethod
    async def _search_segments(
        cls,
        keywords: list[str],
        source_ids: list[str],
        domain_filters: list[str],
        max_segments: int,
    ) -> list[dict]:
        """Search for relevant text segments in sources.

        Returns list of {source_id, text, score} dicts.
        """
        if not keywords:
            return []

        # Build Cypher query to find chunks containing keywords
        # Using Neo4j full-text search or CONTAINS
        keyword_conditions = " OR ".join(
            [f"toLower(c.text) CONTAINS toLower('{kw}')" for kw in keywords[:10]]
        )

        query = f"""
        MATCH (b:Book)-[:HAS_CHUNK]->(c:Chunk)
        WHERE ({keyword_conditions})
        RETURN b.calibre_id as source_id, b.title as source_title,
               c.text as text, c.id as chunk_id
        LIMIT $max_segments
        """

        try:
            results = await Neo4jClient.execute_query(
                query, {"max_segments": max_segments}
            )
            return [
                {
                    "source_id": str(r["source_id"]),
                    "source_title": r["source_title"],
                    "text": r["text"],
                    "chunk_id": r["chunk_id"],
                }
                for r in (results or [])
            ]
        except Exception as e:
            logger.error(f"Segment search failed: {e}")
            return []

    @classmethod
    async def _extract_from_segments(
        cls,
        segments: list[dict],
        context: Context,
        profile: ExtractionProfile,
        question: Question | None,
    ) -> ExtractionResult:
        """Extract entities and relationships from segments using LLM."""
        if not segments:
            return ExtractionResult(
                context_id=context.id or "",
                sources_processed=0,
                segments_analyzed=0,
            )

        # Build prompt for extraction
        focus = question.text if question else context.title
        concepts_hint = ", ".join(profile.core_concepts[:10]) if profile.core_concepts else "relevant concepts"

        prompt = f"""You are extracting knowledge from text segments for a research context.

Context: {context.title}
Focus: {focus}
Target concepts: {concepts_hint}

For each segment below, extract:
1. Concepts mentioned (that relate to the focus)
2. Relationships between concepts (type: supports, contradicts, enables, component_of)
3. Any new questions this raises

Segments:
"""
        for i, seg in enumerate(segments[:10], 1):
            prompt += f"\n[{i}] Source: {seg.get('source_title', 'Unknown')}\n{seg['text'][:500]}...\n"

        prompt += """
Return as JSON:
{
  "concepts": ["concept1", "concept2"],
  "relationships": [{"source": "A", "target": "B", "type": "enables"}],
  "questions": ["New question 1?"]
}
"""

        try:
            client = Anthropic()
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            response_text = response.content[0].text
            import json
            # Find JSON in response
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(response_text[start:end])
                return ExtractionResult(
                    context_id=context.id or "",
                    concepts_found=data.get("concepts", []),
                    relations_found=data.get("relationships", []),
                    subquestions_generated=data.get("questions", []),
                    sources_processed=len(set(s["source_id"] for s in segments)),
                    segments_analyzed=len(segments),
                )
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")

        return ExtractionResult(
            context_id=context.id or "",
            sources_processed=len(set(s.get("source_id", "") for s in segments)),
            segments_analyzed=len(segments),
        )

    @classmethod
    async def _log_extraction_journey(
        cls,
        context_id: str,
        question_id: str | None,
        result: ExtractionResult,
    ) -> str | None:
        """Log extraction run as journey entry."""
        try:
            entry_id = f"je_{uuid.uuid4().hex[:12]}"
            entry = ContextJourneyEntry(
                id=entry_id,
                timestamp=datetime.now(timezone.utc),
                context_id=context_id,
                focus_id=question_id,
                text=f"Extraction run: {result.segments_analyzed} segments, {len(result.concepts_found)} concepts found",
                classifications=[JourneyClassification.EXTRACTION_RUN],
                entity_links=result.concepts_found[:10],
                source_action="extraction_engine",
            )

            # Save to Neo4j
            query = """
            CREATE (j:ContextJourneyEntry {
                id: $id,
                timestamp: datetime($timestamp),
                context_id: $context_id,
                focus_id: $focus_id,
                text: $text,
                classifications: $classifications,
                entity_links: $entity_links,
                source_action: $source_action
            })
            RETURN j.id as id
            """
            await Neo4jClient.execute_query(
                query,
                {
                    "id": entry.id,
                    "timestamp": entry.timestamp.isoformat(),
                    "context_id": entry.context_id,
                    "focus_id": entry.focus_id,
                    "text": entry.text,
                    "classifications": [c.value for c in entry.classifications],
                    "entity_links": entry.entity_links,
                    "source_action": entry.source_action,
                },
            )
            return entry_id
        except Exception as e:
            logger.error(f"Failed to log journey entry: {e}")
            return None
