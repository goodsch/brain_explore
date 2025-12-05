"""Service for Quick Capture processing and Flow capture queue."""

import json
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from ..schemas.capture import (
    AutoExtracted,
    CaptureCreateRequest,
    CaptureItem,
    CaptureListResponse,
    CaptureProcessRequest,
    CaptureProcessResponse,
    CaptureSource,
    CaptureStatus,
    CaptureType,
    CaptureUpdateRequest,
    ExtractedEntity,
    PlacementType,
    Spark,
    SuggestedPlacement,
)
from .graph_service import GraphService
from .neo4j_client import Neo4jClient

# Check for Anthropic availability
ANTHROPIC_AVAILABLE = False
try:
    import anthropic

    ANTHROPIC_AVAILABLE = bool(os.getenv("ANTHROPIC_API_KEY"))
except ImportError:
    pass


class CaptureService:
    """Service for processing and routing captured content."""

    @staticmethod
    async def process_capture(
        request: CaptureProcessRequest,
    ) -> CaptureProcessResponse:
        """Process captured content to extract entities and suggest placements.

        Args:
            request: Capture processing request

        Returns:
            Processed response with entities and placement suggestions
        """
        content = request.content

        # Extract entities (AI-powered if available, otherwise simple extraction)
        if ANTHROPIC_AVAILABLE:
            entities, summary, tags = await CaptureService._ai_extract(content)
        else:
            entities = CaptureService._simple_extract(content)
            summary = content[:200] + "..." if len(content) > 200 else content
            tags = CaptureService._extract_tags(content)

        # Find related concepts in graph
        related_concepts = []
        for entity in entities:
            graph_matches = await GraphService.search_concepts(entity.name, limit=3)
            related_concepts.extend(graph_matches)

        # Generate placement suggestions
        placements = await CaptureService._suggest_placements(
            content, entities, related_concepts, request.context
        )

        return CaptureProcessResponse(
            extracted_entities=entities,
            suggested_placements=placements,
            summary=summary,
            tags=tags,
        )

    @staticmethod
    async def _ai_extract(
        content: str,
    ) -> tuple[list[ExtractedEntity], str, list[str]]:
        """Use AI to extract entities, summary, and tags."""
        client = anthropic.Anthropic()

        prompt = f"""Analyze this captured thought/note and extract:
1. Key concepts/entities mentioned (with type: concept, person, theory, framework, practice)
2. A one-sentence summary
3. Relevant tags (3-5 short words)

Content:
{content}

Respond in this exact format:
ENTITIES:
- [name]: [type] ([confidence 0-1])
- [name]: [type] ([confidence 0-1])
...

SUMMARY: [one sentence]

TAGS: [tag1, tag2, tag3, ...]"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )

            text = response.content[0].text

            # Parse entities
            entities = []
            entity_section = re.search(r"ENTITIES:\n(.*?)(?=\nSUMMARY:)", text, re.DOTALL)
            if entity_section:
                for line in entity_section.group(1).strip().split("\n"):
                    match = re.match(r"- (.+?): (.+?) \(([0-9.]+)\)", line)
                    if match:
                        entities.append(
                            ExtractedEntity(
                                name=match.group(1).strip(),
                                type=match.group(2).strip().lower(),
                                confidence=float(match.group(3)),
                            )
                        )

            # Parse summary
            summary_match = re.search(r"SUMMARY: (.+?)(?=\nTAGS:|$)", text, re.DOTALL)
            summary = summary_match.group(1).strip() if summary_match else content[:200]

            # Parse tags
            tags_match = re.search(r"TAGS: (.+?)$", text)
            tags = []
            if tags_match:
                tags = [t.strip().lower() for t in tags_match.group(1).split(",")]

            return entities, summary, tags

        except Exception:
            # Fallback to simple extraction
            return (
                CaptureService._simple_extract(content),
                content[:200],
                CaptureService._extract_tags(content),
            )

    @staticmethod
    def _simple_extract(content: str) -> list[ExtractedEntity]:
        """Simple entity extraction without AI."""
        entities = []

        # Look for capitalized phrases (potential concepts)
        # Match 1-4 consecutive capitalized words
        pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b"
        matches = re.findall(pattern, content)

        seen = set()
        for match in matches:
            # Skip common words
            if match.lower() in {"the", "this", "that", "just", "about", "with"}:
                continue
            if match not in seen:
                seen.add(match)
                entities.append(
                    ExtractedEntity(
                        name=match,
                        type="concept",
                        confidence=0.5,
                    )
                )

        return entities[:10]  # Limit to 10

    @staticmethod
    def _extract_tags(content: str) -> list[str]:
        """Extract potential tags from content."""
        # Common therapy/psychology concepts to look for
        keywords = [
            "acceptance",
            "grief",
            "shame",
            "trauma",
            "healing",
            "insight",
            "awareness",
            "presence",
            "metabolization",
            "regulation",
            "nervous system",
            "capacity",
            "window",
        ]

        content_lower = content.lower()
        return [kw for kw in keywords if kw in content_lower][:5]

    @staticmethod
    async def _suggest_placements(
        content: str,
        entities: list[ExtractedEntity],
        related_concepts: list[dict],
        context: dict | None,
    ) -> list[SuggestedPlacement]:
        """Generate placement suggestions based on content and context."""
        placements = []

        # If we have context with a current note, suggest appending there
        if context and context.get("current_note_id"):
            placements.append(
                SuggestedPlacement(
                    target_type=PlacementType.NOTE,
                    target_id=context["current_note_id"],
                    target_name="Current Note",
                    confidence=0.7,
                    preview=f"[Append to current note]\n\n{content[:100]}...",
                    rationale="You were viewing this note when capturing",
                )
            )

        # If we have context with a current journey, suggest linking
        if context and context.get("current_journey_id"):
            placements.append(
                SuggestedPlacement(
                    target_type=PlacementType.JOURNEY,
                    target_id=context["current_journey_id"],
                    target_name="Current Journey",
                    confidence=0.6,
                    preview=f"[Link to journey as mark]\n\n{content[:100]}...",
                    rationale="You were on this exploration journey when capturing",
                )
            )

        # Suggest linking to related concepts
        for concept in related_concepts[:3]:
            confidence = 0.5 + (0.2 if concept.get("type") == "concept" else 0.0)
            placements.append(
                SuggestedPlacement(
                    target_type=PlacementType.CONCEPT,
                    target_id=concept.get("name"),
                    target_name=concept.get("name"),
                    confidence=confidence,
                    preview=f"[Link to concept: {concept.get('name')}]\n\n{content[:100]}...",
                    rationale=f"Content mentions or relates to {concept.get('name')}",
                )
            )

        # Always offer creating a new note
        placements.append(
            SuggestedPlacement(
                target_type=PlacementType.NEW_NOTE,
                target_id=None,
                target_name="New Note",
                confidence=0.3,
                preview=f"[Create new note]\n\n{content}",
                rationale="Create a standalone note for this thought",
            )
        )

        # Sort by confidence
        placements.sort(key=lambda p: p.confidence, reverse=True)

        return placements[:5]  # Return top 5

    # =========================================================================
    # Flow Mode Capture Queue
    # =========================================================================

    @staticmethod
    async def create_capture(request: CaptureCreateRequest) -> CaptureItem:
        """Create a capture queue item and persist to Neo4j."""
        await CaptureService._ensure_capture_schema()

        capture_id = f"capture_{uuid.uuid4().hex[:12]}"
        captured_at = datetime.now(timezone.utc)
        auto_extracted = request.auto_extracted or CaptureService._auto_extract(request.raw_text)
        spark_payload = request.spark.model_dump(by_alias=True) if request.spark else None

        params = {
            "id": capture_id,
            "raw_text": request.raw_text,
            "source": request.source.value,
            "captured_at": captured_at.isoformat(),
            "status": CaptureStatus.QUEUED.value,
            "context_snippet": request.context_snippet,
            "entities": auto_extracted.entities if auto_extracted else [],
            "topics": auto_extracted.topics if auto_extracted else [],
            "spark": json.dumps(spark_payload) if spark_payload else None,
        }

        create_query = """
        MERGE (c:CaptureItem {id: $id})
        SET c.raw_text = $raw_text,
            c.source = $source,
            c.captured_at = $captured_at,
            c.status = $status,
            c.context_snippet = $context_snippet,
            c.entities = $entities,
            c.topics = $topics,
            c.spark = $spark
        """
        await Neo4jClient.execute_write(create_query, params)

        if auto_extracted and auto_extracted.entities:
            rel_query = """
            MATCH (c:CaptureItem {id: $id})
            UNWIND $entities AS entity_name
            MERGE (e:Concept {name: entity_name})
            MERGE (c)-[:MENTIONS]->(e)
            """
            await Neo4jClient.execute_write(rel_query, {"id": capture_id, "entities": auto_extracted.entities})

        return await CaptureService.get_capture(capture_id)

    @staticmethod
    async def list_captures(status: CaptureStatus | None = None) -> CaptureListResponse:
        """List capture queue items, optionally filtered by status."""
        await CaptureService._ensure_capture_schema()

        list_query = """
        MATCH (c:CaptureItem)
        WHERE $status IS NULL OR c.status = $status
        OPTIONAL MATCH (c)-[:MENTIONS]->(e:Concept)
        RETURN c AS capture, collect(DISTINCT e.name) AS entities
        ORDER BY c.captured_at DESC
        """
        params = {"status": status.value if status else None}
        results = await Neo4jClient.execute_query(list_query, params)
        items: list[CaptureItem] = []
        for record in results:
            capture = CaptureService._record_to_capture(record)
            if capture:
                items.append(capture)

        return CaptureListResponse(items=items, total=len(items))

    @staticmethod
    async def get_capture(capture_id: str) -> CaptureItem | None:
        """Get a single capture item."""
        await CaptureService._ensure_capture_schema()

        query = """
        MATCH (c:CaptureItem {id: $id})
        OPTIONAL MATCH (c)-[:MENTIONS]->(e:Concept)
        RETURN c AS capture, collect(DISTINCT e.name) AS entities
        """
        results = await Neo4jClient.execute_query(query, {"id": capture_id})
        if not results:
            return None
        return CaptureService._record_to_capture(results[0])

    @staticmethod
    async def update_capture(capture_id: str, request: CaptureUpdateRequest) -> CaptureItem | None:
        """Update capture status or auto-extracted metadata."""
        await CaptureService._ensure_capture_schema()

        auto = request.auto_extracted
        params = {
            "id": capture_id,
            "status": request.status.value if request.status else None,
            "entities": auto.entities if auto and auto.entities is not None else None,
            "topics": auto.topics if auto and auto.topics is not None else None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        update_query = """
        MATCH (c:CaptureItem {id: $id})
        SET c.status = COALESCE($status, c.status),
            c.entities = CASE WHEN $entities IS NULL THEN c.entities ELSE $entities END,
            c.topics = CASE WHEN $topics IS NULL THEN c.topics ELSE $topics END,
            c.updated_at = $updated_at
        """
        await Neo4jClient.execute_write(update_query, params)

        # Refresh mention relationships if entities provided
        if auto and auto.entities is not None:
            await Neo4jClient.execute_write(
                """
                MATCH (c:CaptureItem {id: $id})-[r:MENTIONS]->(e)
                DELETE r
                """,
                {"id": capture_id},
            )
            if auto.entities:
                await Neo4jClient.execute_write(
                    """
                    MATCH (c:CaptureItem {id: $id})
                    UNWIND $entities AS entity_name
                    MERGE (e:Concept {name: entity_name})
                    MERGE (c)-[:MENTIONS]->(e)
                    """,
                    {"id": capture_id, "entities": auto.entities},
                )

        return await CaptureService.get_capture(capture_id)

    @staticmethod
    async def delete_capture(capture_id: str) -> bool:
        """Delete a capture item."""
        await CaptureService._ensure_capture_schema()

        query = """
        MATCH (c:CaptureItem {id: $id})
        DETACH DELETE c
        RETURN count(c) as deleted
        """
        results = await Neo4jClient.execute_write(query, {"id": capture_id})
        if not results:
            return False
        deleted = results[0].get("deleted")
        if isinstance(deleted, list):
            # Neo4j driver can return lists for aggregates in mocks
            deleted = deleted[0] if deleted else 0
        return bool(deleted)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    async def _ensure_capture_schema() -> None:
        """Ensure constraints/indexes for capture nodes."""
        constraints = [
            "CREATE CONSTRAINT capture_id IF NOT EXISTS FOR (c:CaptureItem) REQUIRE c.id IS UNIQUE",
            "CREATE INDEX capture_status IF NOT EXISTS FOR (c:CaptureItem) ON (c.status)",
            "CREATE INDEX capture_captured_at IF NOT EXISTS FOR (c:CaptureItem) ON (c.captured_at)",
        ]
        for query in constraints:
            try:
                await Neo4jClient.execute_write(query)
            except Exception:
                continue

    @staticmethod
    def _auto_extract(raw_text: str) -> AutoExtracted:
        """Lightweight auto extraction when LLM not explicitly provided."""
        entities = [entity.name for entity in CaptureService._simple_extract(raw_text)]
        topics = CaptureService._extract_tags(raw_text)
        return AutoExtracted(entities=entities, topics=topics)

    @staticmethod
    def _record_to_capture(record: dict) -> CaptureItem | None:
        """Convert Neo4j record to CaptureItem."""
        node = record.get("capture") or record.get("c")
        if node is None:
            return None

        data = dict(node)
        status_value = data.get("status", CaptureStatus.QUEUED.value)
        try:
            status = CaptureStatus(status_value)
        except ValueError:
            status = CaptureStatus.QUEUED

        captured_at_raw = data.get("captured_at") or data.get("capturedAt")
        captured_at = CaptureService._parse_datetime(captured_at_raw)

        entities = record.get("entities") or data.get("entities") or []
        topics = record.get("topics") or data.get("topics") or []

        spark = None
        spark_raw = data.get("spark")
        if spark_raw:
            try:
                spark_payload = spark_raw if isinstance(spark_raw, dict) else json.loads(str(spark_raw))
                spark = Spark.model_validate(spark_payload)
            except Exception:
                spark = None

        auto = None
        if entities or topics:
            auto = AutoExtracted(entities=list(entities), topics=list(topics))

        return CaptureItem(
            id=data.get("id", ""),
            raw_text=data.get("raw_text") or data.get("rawText", ""),
            source=data.get("source", CaptureSource.ASSISTANT_INTERRUPTION.value),
            captured_at=captured_at,
            status=status,
            context_snippet=data.get("context_snippet"),
            auto_extracted=auto,
            spark=spark,
        )

    @staticmethod
    def _parse_datetime(value: Any) -> datetime:
        """Parse ISO datetime strings safely."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
        return datetime.now(timezone.utc)
