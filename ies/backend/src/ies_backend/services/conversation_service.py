"""Service layer for importing AI chat conversations."""

from __future__ import annotations

import json
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
from ies_backend.services.extraction_service import ExtractionService
from ies_backend.services.neo4j_client import Neo4jClient
from ies_backend.services.conversation_parser import ConversationParser, ParsedTurn

# Simple extraction fallback mirrors inbox approach
import re


class ConversationService:
    """Import, store, and retrieve conversations with extracted entities."""

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
