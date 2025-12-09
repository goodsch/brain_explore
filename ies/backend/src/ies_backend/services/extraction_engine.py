"""Extraction Engine Service.

Context-aware entity extraction that uses ExtractionProfile to find
relevant concepts and relationships from sources.

Pipeline:
1. Load context and profile
2. Filter sources by domain_filters
3. Search sources for core_concepts + synonyms (using full-text index)
4. Extract entities and relationships via LLM
5. Write to knowledge graph
6. Generate subquestions
7. Log journey entry
"""

import logging
import re
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
from ..schemas.question import QuestionCreate, QuestionSource
from .context_service import ContextService
from .neo4j_client import Neo4jClient
from .question_service import QuestionService

logger = logging.getLogger(__name__)


class ExtractionEngine:
    """Context-aware extraction engine."""

    # In-memory profile storage (MVP)
    _profiles: dict[str, ExtractionProfile] = {}

    @classmethod
    async def initialize_schema(cls) -> None:
        """Initialize Neo4j schema including full-text index for chunks."""
        try:
            # Create full-text index on Chunk nodes for efficient search
            query = """
            CREATE FULLTEXT INDEX chunk_content IF NOT EXISTS
            FOR (c:Chunk)
            ON EACH [c.content, c.text]
            """
            await Neo4jClient.execute_write(query)
            logger.info("Neo4j full-text index initialized for chunk content")
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")

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

        # Filter sources by domain if specified
        filtered_sources = await cls._filter_sources_by_domain(
            source_ids=request.source_ids or context.linked_sources,
            domain_filters=profile.domain_filters,
        )

        # Search for relevant segments using full-text index
        segments = await cls._search_inverted_index(
            keywords=keywords,
            source_ids=filtered_sources,
            max_segments=request.max_segments or 50,
        )

        # Extract entities and relationships
        extraction_result = await cls._extract_from_segments(
            segments=segments,
            context=context,
            profile=profile,
            question=question,
        )

        # Persist to knowledge graph
        await cls._persist_to_knowledge_graph(
            result=extraction_result,
            context_id=context_id,
        )

        # Create subquestions
        await cls._create_subquestions(
            questions=extraction_result.subquestions_generated,
            context_id=context_id,
            parent_question_id=question_id,
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
            # Simple tokenization of question text with punctuation removal
            text = question.text.lower()
            # Remove punctuation
            text = re.sub(r'[^\w\s]', ' ', text)
            words = text.split()
            # Filter common words
            stopwords = {
                "what", "how", "why", "when", "where", "is", "are", "the",
                "a", "an", "to", "of", "in", "for", "and", "or", "with",
                "does", "do", "can", "could", "would", "should", "this", "that",
            }
            keywords.extend([w for w in words if w not in stopwords and len(w) > 2])

        return list(set(keywords))

    @classmethod
    async def _filter_sources_by_domain(
        cls,
        source_ids: list[str],
        domain_filters: list[str],
    ) -> list[str]:
        """Filter source IDs by domain tags.

        Args:
            source_ids: List of calibre_ids or book identifiers
            domain_filters: List of domain tags to filter by

        Returns:
            Filtered list of source IDs
        """
        if not domain_filters or not source_ids:
            return source_ids

        try:
            # Query books with matching domain tags
            # Books may have 'domain' or 'tags' properties
            query = """
            MATCH (b:Book)
            WHERE b.calibre_id IN $source_ids
              AND (
                ANY(tag IN $domain_filters WHERE tag IN b.tags)
                OR ANY(domain IN $domain_filters WHERE domain = b.domain)
              )
            RETURN DISTINCT b.calibre_id as calibre_id
            """
            results = await Neo4jClient.execute_query(
                query,
                {
                    "source_ids": [int(sid) if sid.isdigit() else sid for sid in source_ids],
                    "domain_filters": domain_filters,
                }
            )
            filtered = [str(r["calibre_id"]) for r in (results or [])]

            if filtered:
                logger.info(f"Filtered {len(source_ids)} sources to {len(filtered)} by domains: {domain_filters}")
                return filtered
            else:
                # Graceful fallback: if no domains set, return all sources
                logger.warning(f"No sources matched domain filters {domain_filters}, using all sources")
                return source_ids

        except Exception as e:
            logger.error(f"Domain filtering failed: {e}, using all sources")
            return source_ids

    @classmethod
    async def _search_inverted_index(
        cls,
        keywords: list[str],
        source_ids: list[str],
        max_segments: int,
    ) -> list[dict]:
        """Search for relevant text segments using Neo4j full-text index.

        Returns list of {source_id, text, score, chunk_id} dicts.
        """
        if not keywords:
            return []

        try:
            # Build Lucene query for full-text search
            # Core concepts get exact match, synonyms get OR
            # Lucene query syntax: "exact phrase" OR term1 OR term2
            core_terms = keywords[:5]  # Limit to top concepts
            lucene_parts = [f'"{term}"' for term in core_terms]
            lucene_query = " OR ".join(lucene_parts)

            # Use full-text index if available, fallback to CONTAINS
            query = """
            CALL db.index.fulltext.queryNodes('chunk_content', $lucene_query)
            YIELD node as c, score
            MATCH (b:Book)-[:HAS_CHUNK]->(c)
            WHERE b.calibre_id IN $source_ids
            RETURN b.calibre_id as source_id,
                   b.title as source_title,
                   c.text as text,
                   c.id as chunk_id,
                   score
            ORDER BY score DESC
            LIMIT $max_segments
            """

            results = await Neo4jClient.execute_query(
                query,
                {
                    "lucene_query": lucene_query,
                    "source_ids": [int(sid) if sid.isdigit() else sid for sid in source_ids],
                    "max_segments": max_segments,
                }
            )

            segments = [
                {
                    "source_id": str(r["source_id"]),
                    "source_title": r["source_title"],
                    "text": r["text"],
                    "chunk_id": r["chunk_id"],
                    "score": r.get("score", 0.0),
                }
                for r in (results or [])
            ]

            logger.info(f"Full-text search found {len(segments)} segments for {len(keywords)} keywords")
            return segments

        except Exception as e:
            # Fallback to simple CONTAINS search if full-text index doesn't exist
            logger.warning(f"Full-text search failed: {e}, falling back to CONTAINS")
            return await cls._search_segments_fallback(keywords, source_ids, max_segments)

    @classmethod
    async def _search_segments_fallback(
        cls,
        keywords: list[str],
        source_ids: list[str],
        max_segments: int,
    ) -> list[dict]:
        """Fallback search using CONTAINS (for when full-text index unavailable)."""
        keyword_conditions = " OR ".join(
            [f"toLower(c.text) CONTAINS toLower('{kw}')" for kw in keywords[:10]]
        )

        query = f"""
        MATCH (b:Book)-[:HAS_CHUNK]->(c:Chunk)
        WHERE ({keyword_conditions})
          AND b.calibre_id IN $source_ids
        RETURN b.calibre_id as source_id, b.title as source_title,
               c.text as text, c.id as chunk_id
        LIMIT $max_segments
        """

        try:
            results = await Neo4jClient.execute_query(
                query,
                {
                    "source_ids": [int(sid) if sid.isdigit() else sid for sid in source_ids],
                    "max_segments": max_segments,
                }
            )
            return [
                {
                    "source_id": str(r["source_id"]),
                    "source_title": r["source_title"],
                    "text": r["text"],
                    "chunk_id": r["chunk_id"],
                    "score": 0.0,
                }
                for r in (results or [])
            ]
        except Exception as e:
            logger.error(f"Fallback segment search failed: {e}")
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
  "relationships": [{"source": "A", "target": "B", "type": "enables", "evidence": "quote"}],
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
    async def _persist_to_knowledge_graph(
        cls,
        result: ExtractionResult,
        context_id: str,
    ) -> None:
        """Persist extracted entities and relationships to Neo4j knowledge graph.

        Args:
            result: Extraction result with concepts and relationships
            context_id: Context this extraction ran within
        """
        if not result.concepts_found and not result.relations_found:
            return

        try:
            # Create/update concept nodes
            for concept_name in result.concepts_found:
                query = """
                MERGE (c:Concept {name: $name})
                ON CREATE SET
                    c.created_at = datetime(),
                    c.description = '',
                    c.linked_contexts = [$context_id]
                ON MATCH SET
                    c.linked_contexts = CASE
                        WHEN NOT $context_id IN c.linked_contexts
                        THEN c.linked_contexts + $context_id
                        ELSE c.linked_contexts
                    END
                RETURN c.name as name
                """
                await Neo4jClient.execute_write(
                    query,
                    {"name": concept_name, "context_id": context_id}
                )

            logger.info(f"Persisted {len(result.concepts_found)} concepts to knowledge graph")

            # Create relationships between concepts
            for rel in result.relations_found:
                source = rel.get("source")
                target = rel.get("target")
                rel_type = rel.get("type", "RELATED_TO").upper().replace(" ", "_")
                evidence = rel.get("evidence", "")

                if not source or not target:
                    continue

                query = f"""
                MATCH (a:Concept {{name: $source}})
                MATCH (b:Concept {{name: $target}})
                MERGE (a)-[r:{rel_type}]->(b)
                ON CREATE SET
                    r.created_at = datetime(),
                    r.evidence = $evidence,
                    r.context_id = $context_id
                RETURN type(r) as rel_type
                """
                try:
                    await Neo4jClient.execute_write(
                        query,
                        {
                            "source": source,
                            "target": target,
                            "evidence": evidence,
                            "context_id": context_id,
                        }
                    )
                except Exception as e:
                    logger.error(f"Failed to create relationship {source}->{target}: {e}")

            logger.info(f"Persisted {len(result.relations_found)} relationships to knowledge graph")

        except Exception as e:
            logger.error(f"Failed to persist to knowledge graph: {e}")

    @classmethod
    async def _create_subquestions(
        cls,
        questions: list[str],
        context_id: str,
        parent_question_id: str | None,
    ) -> None:
        """Create AI-generated subquestions and save to QuestionService.

        Args:
            questions: List of question texts to create
            context_id: Context these questions belong to
            parent_question_id: Optional parent question ID
        """
        if not questions:
            return

        try:
            question_service = QuestionService()
            created_count = 0

            for question_text in questions:
                question_create = QuestionCreate(
                    context_id=context_id,
                    text=question_text,
                    source=QuestionSource.AI_SUGGESTED,
                    parent_question_id=parent_question_id,
                )
                await question_service.create(question_create)
                created_count += 1

            logger.info(f"Created {created_count} AI-generated subquestions")

        except Exception as e:
            logger.error(f"Failed to create subquestions: {e}")

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
