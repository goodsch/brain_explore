"""Service layer for importing AI chat conversations."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx

from ies_backend.schemas.conversation import (
    ConversationImport,
    ConversationImportResponse,
    ConversationListResponse,
    ConversationSession,
    ConversationSource,
    ConversationTurn,
)
from ies_backend.schemas.entity import ExtractionResult, ExtractedEntity
from ies_backend.schemas.personal import CreateSparkRequest, EnergyLevel, ResonanceSignal
from ies_backend.schemas.profile import ProfileObservation
from ies_backend.services.extraction_service import ExtractionService
from ies_backend.services.personal_graph_service import PersonalGraphService
from ies_backend.services.profile_service import ProfileService
from ies_backend.services.neo4j_client import Neo4jClient
from ies_backend.services.conversation_parser import ConversationParser, ParsedTurn

# Simple extraction fallback mirrors inbox approach
import re


logger = logging.getLogger(__name__)


class ConversationService:
    """Import, store, and retrieve conversations with extracted entities."""

    profile_service = ProfileService()
    personal_graph_service = PersonalGraphService

    @staticmethod
    async def import_conversation(request: ConversationImport) -> ConversationImportResponse:
        """Import a conversation, extract entities, and persist to Neo4j."""
        content = request.content
        if request.source == ConversationSource.URL:
            content = await ConversationService._fetch_url(request.content)
            source_for_parse = ConversationService._infer_source_from_url(request.content)
        else:
            source_for_parse = request.source.value

        turns = ConversationService._normalize_turns(content, source_for_parse)
        topic = request.topic or ConversationService._infer_topic(turns)
        transcript = ConversationService._build_transcript(turns)

        extraction: ExtractionResult | None = None
        if request.extract_entities:
            extraction = await ConversationService._extract_entities(transcript)

        session = await ConversationService._persist_session(
            user_id=request.user_id,
            source=request.source,
            topic=topic,
            turns=turns,
            extraction=extraction,
            transcript=transcript,
        )

        if extraction:
            try:
                await ConversationService._post_process_learning(
                    request=request,
                    session=session,
                    extraction=extraction,
                    turns=turns,
                    transcript=transcript,
                )
            except Exception:
                logger.exception("Conversation enrichment failed for %s", session.id)

        return ConversationImportResponse(session=session, extraction=extraction)

    @staticmethod
    async def list_conversations(user_id: str | None = None) -> ConversationListResponse:
        """List stored conversations (optionally filtered by user)."""
        query = """
        MATCH (c:ConversationSession)
        WHERE $user_id IS NULL OR c.user_id = $user_id
        RETURN c
        ORDER BY c.imported_at DESC
        """
        rows = await Neo4jClient.execute_query(query, {"user_id": user_id})
        conversations: list[ConversationSession] = []
        for row in rows:
            node = row.get("c", {})
            conversations.append(
                ConversationSession(
                    id=node.get("id"),
                    source=ConversationSource(node.get("source", "text")),
                    topic=node.get("topic"),
                    imported_at=datetime.fromisoformat(node.get("imported_at")),
                    turn_count=node.get("turn_count", 0),
                    entity_count=node.get("entity_count", 0),
                    transcript=node.get("transcript"),
                    entities=row.get("entities", []),
                    turns=[],
                )
            )
        return ConversationListResponse(conversations=conversations)

    @staticmethod
    async def get_conversation(conversation_id: str) -> ConversationSession | None:
        """Fetch a single conversation with basic metadata."""
        query = """
        MATCH (c:ConversationSession {id: $id})
        OPTIONAL MATCH (c)-[:MENTIONS]->(e:Entity)
        RETURN c, collect(e.name) AS entities
        """
        rows = await Neo4jClient.execute_query(query, {"id": conversation_id})
        if not rows:
            return None
        row = rows[0]
        node = row.get("c", {})
        transcript = node.get("transcript")
        turns = []
        if transcript:
            turns = ConversationService._normalize_turns(transcript, source_for_parse=node.get("source", "text"))
        return ConversationSession(
            id=node.get("id"),
            source=ConversationSource(node.get("source", "text")),
            topic=node.get("topic"),
            imported_at=datetime.fromisoformat(node.get("imported_at")),
            turn_count=node.get("turn_count", 0),
            entity_count=node.get("entity_count", 0),
            transcript=transcript,
            entities=row.get("entities", []),
            turns=turns,
        )

    @staticmethod
    async def delete_conversation(conversation_id: str) -> bool:
        """Delete a conversation and its relationships."""
        query = """
        MATCH (c:ConversationSession {id: $id})
        DETACH DELETE c
        RETURN COUNT(c) AS deleted
        """
        rows = await Neo4jClient.execute_write(query, {"id": conversation_id})
        if not rows:
            return False
        return bool(rows[0].get("deleted", 0))

    @staticmethod
    async def get_extraction_result(conversation_id: str) -> ExtractionResult | None:
        """Fetch extraction result for a conversation."""
        query = """
        MATCH (c:ConversationSession {id: $id})-[:MENTIONS]->(e:Entity)
        RETURN e
        """
        rows = await Neo4jClient.execute_query(query, {"id": conversation_id})
        if not rows:
            return None

        entities: list[ExtractedEntity] = []
        for row in rows:
            node = row.get("e", {})
            # Assuming ExtractedEntity fields are directly on the Node.
            # 'quotes' and 'connections' might need more complex retrieval if not stored directly.
            # For now, initialize as empty lists if not present.
            entities.append(
                ExtractedEntity(
                    name=node.get("name"),
                    kind=node.get("kind", "idea"),  # Default to 'idea' if not present
                    domain=node.get("domain", "meta"),  # Default to 'meta'
                    status=node.get("status", "seed"),  # Default to 'seed'
                    description=node.get("description", ""),
                    quotes=node.get("quotes", []),
                    connections=node.get("connections", []),
                )
            )
        return ExtractionResult(entities=entities)

    # ----- Internal helpers ----- #

    @staticmethod
    async def _fetch_url(url: str) -> str:
        """Fetch remote content for URL imports."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=15)
            response.raise_for_status()
            return response.text

    @staticmethod
    def _infer_source_from_url(url: str) -> str:
        """Heuristic to guess exporter type from URL."""
        if "claude.ai" in url:
            return "claude"
        if "chat.openai.com" in url or "chatgpt" in url:
            return "chatgpt"
        return "text"

    @staticmethod
    def _normalize_turns(content: str, source_for_parse: str) -> list[ConversationTurn]:
        """Parse raw content into ConversationTurn models."""
        parsed: list[ParsedTurn] = ConversationParser.parse(content, source_for_parse)
        return [
            ConversationTurn(role=turn.role, text=turn.text, timestamp=turn.timestamp)
            for turn in parsed
        ]

    @staticmethod
    def _infer_topic(turns: list[ConversationTurn]) -> str | None:
        """Infer a lightweight topic from early turns."""
        if not turns:
            return None
        first = turns[0].text.strip().splitlines()[0]
        return first[:120]

    @staticmethod
    def _build_transcript(turns: list[ConversationTurn]) -> str:
        """Flatten turns into transcript string."""
        return "\n".join([f"{t.role.upper()}: {t.text}" for t in turns])

    @staticmethod
    async def _extract_entities(transcript: str) -> ExtractionResult:
        """Run AI extraction with simple fallback if unavailable."""
        try:
            extractor = ExtractionService()
            return await extractor.extract_entities(transcript)
        except Exception:
            # Fallback: naive capitalized phrase extraction
            return ExtractionResult(entities=ConversationService._simple_extract(transcript))

    @staticmethod
    def _simple_extract(transcript: str) -> list[ExtractedEntity]:
        """Heuristic entity extraction for offline/testing."""
        entities: list[ExtractedEntity] = []
        pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b"
        seen: set[str] = set()
        for match in re.findall(pattern, transcript):
            if match.lower() in {"assistant", "user"}:
                continue
            if match not in seen:
                seen.add(match)
                entities.append(
                    ExtractedEntity(
                        name=match,
                        kind="idea",
                        domain="meta",
                        status="seed",
                        description="",
                        quotes=[],
                        connections=[],
                    )
                )
        return entities[:10]

    @classmethod
    async def _post_process_learning(
        cls,
        request: ConversationImport,
        session: ConversationSession,
        extraction: ExtractionResult,
        turns: list[ConversationTurn],
        transcript: str,
    ) -> None:
        """Run downstream learning hooks once extraction succeeds."""

        await cls._apply_profile_learning(request.user_id, session, extraction, turns, transcript)
        await cls._create_sparks_from_insights(session, extraction)
        await cls._store_open_questions(request.user_id, session, extraction)

    @classmethod
    async def _apply_profile_learning(
        cls,
        user_id: str,
        session: ConversationSession,
        extraction: ExtractionResult,
        turns: list[ConversationTurn],
        transcript: str,
    ) -> None:
        """Send conversation-derived observations to the profile service."""

        if not cls.profile_service:
            return

        observation = cls._build_profile_observation(session, extraction, turns, transcript)
        if not observation:
            return

        try:
            await cls.profile_service.apply_observation(user_id, observation)
        except Exception:
            # Profile learning shouldn't block imports.
            logger.exception("Profile observation failed for %s", session.id)

    @staticmethod
    def _build_profile_observation(
        session: ConversationSession,
        extraction: ExtractionResult,
        turns: list[ConversationTurn],
        transcript: str,
    ) -> ProfileObservation | None:
        """Derive a profile observation payload from conversation signals."""

        summary = extraction.session_summary
        topics: list[str] = []
        if session.topic:
            topics.append(session.topic)
        topics.extend(summary.threads_explored)
        concept_names = [entity.name for entity in extraction.entities if entity.name]
        topics.extend(concept_names)
        topics = ConversationService._dedupe_preserve_order([t.strip() for t in topics if t])

        session_length_minutes = ConversationService._estimate_session_minutes(transcript, turns)
        thinking_partner_exchanges = ConversationService._count_thinking_partner_exchanges(turns)
        energy_signals = ConversationService._derive_energy_signals(
            len(turns), len(summary.key_insights)
        )
        time_per_entity = ConversationService._estimate_time_per_entity(extraction.entities)
        for topic in summary.threads_explored:
            if topic not in time_per_entity:
                time_per_entity[topic] = 300

        suggested_updates = {}
        for idx, insight in enumerate(summary.key_insights, start=1):
            cleaned = insight.strip()
            if not cleaned:
                continue
            suggested_updates[f"insight_{idx}"] = cleaned

        return ProfileObservation(
            session_id=session.id,
            session_length_minutes=session_length_minutes,
            topics_explored=topics,
            energy_signals=energy_signals,
            time_per_entity=time_per_entity,
            thinking_partner_exchanges=thinking_partner_exchanges,
            insights_count=len(summary.key_insights),
            suggested_updates=suggested_updates,
        )

    @staticmethod
    def _estimate_session_minutes(transcript: str, turns: list[ConversationTurn]) -> int:
        """Estimate conversation duration from transcript density and turns."""

        word_count = len(transcript.split()) if transcript else 0
        word_minutes = max(1, round(word_count / 180)) if word_count else 1
        turn_minutes = max(1, len(turns) // 3) if turns else 1
        return max(word_minutes, turn_minutes)

    @staticmethod
    def _count_thinking_partner_exchanges(turns: list[ConversationTurn]) -> int:
        """Approximate exchanges as paired non-system turns."""

        conversational_turns = [t for t in turns if t.role != "system"]
        if not conversational_turns:
            return 0
        return max(1, len(conversational_turns) // 2)

    @staticmethod
    def _derive_energy_signals(turn_count: int, insights_count: int) -> list[str]:
        """Map rough engagement levels to qualitative energy signals."""

        signals: list[str] = []
        if turn_count >= 22 or insights_count >= 3:
            signals.append("hyperfocused")
            signals.append("flow")
        elif turn_count >= 14 or insights_count >= 2:
            signals.append("deep_engagement")
        elif turn_count >= 6:
            signals.append("energized")
        else:
            signals.append("steady")
        return signals

    @staticmethod
    def _estimate_time_per_entity(entities: list[ExtractedEntity]) -> dict[str, int]:
        """Convert description/quote volume into coarse engagement seconds."""

        time_map: dict[str, int] = {}
        for entity in entities:
            description_words = len(entity.description.split()) if entity.description else 0
            quote_words = sum(len(q.split()) for q in entity.quotes)
            total_words = description_words + quote_words
            estimated_seconds = max(60, int(total_words * 2)) if total_words else 60
            time_map[entity.name] = estimated_seconds
        return time_map

    @staticmethod
    def _infer_energy_level(turn_count: int) -> EnergyLevel:
        """Map conversation length to spark energy level."""

        if turn_count >= 18:
            return EnergyLevel.HIGH
        if turn_count >= 8:
            return EnergyLevel.MEDIUM
        return EnergyLevel.LOW

    @staticmethod
    def _infer_resonance_signal(insight: str) -> ResonanceSignal:
        """Lightweight heuristic for spark resonance categorization."""

        text = insight.lower()
        if "surpris" in text:
            return ResonanceSignal.SURPRISED
        if "excited" in text or "energ" in text:
            return ResonanceSignal.EXCITED
        if "moved" in text or "grateful" in text:
            return ResonanceSignal.MOVED
        return ResonanceSignal.CURIOUS

    @classmethod
    async def _create_sparks_from_insights(
        cls,
        session: ConversationSession,
        extraction: ExtractionResult,
    ) -> None:
        """Convert key insights into spark captures linked to the session."""

        if not cls.personal_graph_service:
            return

        insights = [ins.strip() for ins in extraction.session_summary.key_insights if ins.strip()]
        if not insights:
            return

        concept_names = ConversationService._dedupe_preserve_order(
            [entity.name for entity in extraction.entities if entity.name]
        )
        energy_level = ConversationService._infer_energy_level(session.turn_count)

        for insight in insights:
            title = insight[:120] or "Conversation insight"
            content = (
                f"{insight}\n\nSource: conversation {session.id} "
                f"({session.topic or session.source.value})"
            )
            spark_request = CreateSparkRequest(
                title=title,
                content=content,
                energy_level=energy_level,
                resonance_signal=ConversationService._infer_resonance_signal(insight),
                source_id=session.id,
                concept_ids=concept_names[:5],
            )
            try:
                spark = await cls.personal_graph_service.create_spark(spark_request)
            except Exception:
                logger.exception("Failed to create spark for %s", session.id)
                continue

            try:
                await ConversationService._link_spark_to_session(session.id, spark.id)
            except Exception:
                logger.exception("Failed to link spark %s to session %s", spark.id, session.id)

    @staticmethod
    async def _link_spark_to_session(session_id: str, spark_id: str) -> None:
        """Connect a spark node back to its originating conversation."""

        query = """
        MATCH (c:ConversationSession {id: $session_id})
        MATCH (s:Spark {id: $spark_id})
        MERGE (s)-[:DERIVED_FROM]->(c)
        """
        await Neo4jClient.execute_write(query, {"session_id": session_id, "spark_id": spark_id})

    @classmethod
    async def _store_open_questions(
        cls,
        user_id: str,
        session: ConversationSession,
        extraction: ExtractionResult,
    ) -> None:
        """Persist open questions for future generation/link them to entities."""

        questions = [q.strip() for q in extraction.session_summary.open_questions if q.strip()]
        if not questions:
            return

        entity_names = ConversationService._dedupe_preserve_order(
            [entity.name for entity in extraction.entities if entity.name]
        )
        created_at = datetime.now(timezone.utc).isoformat()
        payload = [
            {
                "id": f"oq_{uuid.uuid4().hex[:10]}",
                "text": question,
                "entity_names": entity_names,
                "created_at": created_at,
                "topic": session.topic,
                "source": session.source.value,
            }
            for question in questions
        ]

        query = """
        UNWIND $questions AS row
        MERGE (q:OpenQuestion:ADHDEntity {id: row.id})
        SET q.text = row.text,
            q.user_id = $user_id,
            q.session_id = $session_id,
            q.topic = row.topic,
            q.source = row.source,
            q.created_at = row.created_at
        WITH q, row
        MATCH (c:ConversationSession {id: $session_id})
        MERGE (c)-[:HAS_OPEN_QUESTION]->(q)
        WITH q, row
        FOREACH (entity_name IN row.entity_names |
            MERGE (e:Entity {user_id: $user_id, name: entity_name})
            MERGE (q)-[:RELATES_TO]->(e)
        )
        """

        await Neo4jClient.execute_write(
            query,
            {
                "questions": payload,
                "user_id": user_id,
                "session_id": session.id,
            },
        )

    @staticmethod
    def _dedupe_preserve_order(values: list[str]) -> list[str]:
        """Remove duplicates while preserving the first occurrence order."""

        seen: set[str] = set()
        ordered: list[str] = []
        for value in values:
            if not value or value in seen:
                continue
            seen.add(value)
            ordered.append(value)
        return ordered

    @staticmethod
    async def _persist_session(
        user_id: str,
        source: ConversationSource,
        topic: str | None,
        turns: list[ConversationTurn],
        extraction: ExtractionResult | None,
        transcript: str,
    ) -> ConversationSession:
        """Persist session and relationships to Neo4j."""
        session_id = f"conv_{uuid.uuid4().hex[:10]}"
        imported_at = datetime.now(timezone.utc).isoformat()
        entity_names = [e.name for e in extraction.entities] if extraction else []

        query = """
        MERGE (c:ConversationSession {id: $id})
        SET c.source = $source,
            c.topic = $topic,
            c.user_id = $user_id,
            c.imported_at = $imported_at,
            c.turn_count = $turn_count,
            c.entity_count = $entity_count,
            c.transcript = $transcript
        """
        await Neo4jClient.execute_write(
            query,
            {
                "id": session_id,
                "source": source.value,
                "topic": topic,
                "user_id": user_id,
                "imported_at": imported_at,
                "turn_count": len(turns),
                "entity_count": len(entity_names),
                "transcript": transcript,
            },
        )

        if entity_names:
            rel_query = """
            UNWIND $entities AS name
            MERGE (e:Entity {user_id: $user_id, name: name})
            ON CREATE SET e.created_at = $now, e.status = 'seed'
            SET e.updated_at = $now
            WITH e
            MATCH (c:ConversationSession {id: $id})
            MERGE (c)-[:MENTIONS]->(e)
            """
            await Neo4jClient.execute_write(
                rel_query,
                {
                    "entities": entity_names,
                    "user_id": user_id,
                    "id": session_id,
                    "now": imported_at,
                },
            )

        return ConversationSession(
            id=session_id,
            source=source,
            topic=topic,
            imported_at=datetime.fromisoformat(imported_at),
            turn_count=len(turns),
            entity_count=len(entity_names),
            transcript=transcript,
            turns=turns,
        )
