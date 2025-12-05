"""Service for Thinking Sessions derived from capture items."""

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from anthropic import AsyncAnthropic

from ies_backend.config import settings
from ies_backend.schemas.capture import CaptureStatus
from ies_backend.schemas.thinking import (
    Angle,
    Breadcrumb,
    NoteTemplateSuggestion,
    ThinkingCompleteRequest,
    ThinkingSession,
    ThinkingStartRequest,
    ThinkingStartResponse,
    ThinkingStatus,
    ThinkingStepRequest,
)
from ies_backend.services.capture_service import CaptureService
from ies_backend.schemas.capture import CaptureUpdateRequest
from ies_backend.services.neo4j_client import Neo4jClient


class ThinkingService:
    """Thinking session orchestration with LLM support."""

    _anthropic_client: AsyncAnthropic | None = None

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------
    @classmethod
    async def start_session(cls, request: ThinkingStartRequest) -> ThinkingStartResponse:
        """Start a thinking session from a capture."""
        capture = await CaptureService.get_capture(request.capture_id)
        if not capture:
            raise ValueError(f"Capture not found: {request.capture_id}")

        await CaptureService.update_capture(
            request.capture_id, CaptureUpdateRequest(status=CaptureStatus.IN_THINKING)
        )

        session_id = f"thinking_{uuid.uuid4().hex[:12]}"
        created_at = datetime.now(timezone.utc)
        entities = capture.auto_extracted.entities if capture.auto_extracted else []

        angles = await cls._generate_angles(capture.raw_text, entities)
        siyuan_note_id = cls._build_note_id(capture, entities, session_id)
        breadcrumbs: list[Breadcrumb] = []

        await cls._ensure_schema()
        await Neo4jClient.execute_write(
            """
            MERGE (t:ThinkingSession {id: $id})
            SET t.capture_id = $capture_id,
                t.created_at = $created_at,
                t.status = $status,
                t.siyuan_note_id = $siyuan_note_id,
                t.angles_json = $angles_json,
                t.entities = $entities,
                t.breadcrumbs_json = $breadcrumbs_json
            WITH t
            MATCH (c:CaptureItem {id: $capture_id})
            MERGE (t)-[:FROM_CAPTURE]->(c)
            """,
            {
                "id": session_id,
                "capture_id": request.capture_id,
                "created_at": created_at.isoformat(),
                "status": ThinkingStatus.ACTIVE.value,
                "siyuan_note_id": siyuan_note_id,
                "angles_json": json.dumps([a.model_dump() for a in angles]),
                "entities": entities,
                "breadcrumbs_json": json.dumps([]),
            },
        )

        session = ThinkingSession(
            id=session_id,
            capture_id=request.capture_id,
            created_at=created_at,
            status=ThinkingStatus.ACTIVE,
            siyuan_note_id=siyuan_note_id,
            angles=angles,
            entities=entities,
            breadcrumbs=breadcrumbs,
        )

        template = cls._suggest_template(capture.raw_text, entities, angles)

        return ThinkingStartResponse(session=session, siyuanTemplateSuggestion=template)

    @classmethod
    async def get_session(cls, session_id: str) -> ThinkingSession | None:
        """Fetch a thinking session by ID."""
        await cls._ensure_schema()
        results = await Neo4jClient.execute_query(
            """
            MATCH (t:ThinkingSession {id: $id})
            RETURN t
            """,
            {"id": session_id},
        )
        if not results:
            return None

        record = results[0]
        node = record.get("t") if isinstance(record, dict) else record
        return cls._record_to_session(node)

    @classmethod
    async def record_breadcrumb(
        cls, session_id: str, request: ThinkingStepRequest
    ) -> ThinkingSession | None:
        """Append a breadcrumb to a thinking session."""
        session = await cls.get_session(session_id)
        if not session:
            return None

        breadcrumb_id = f"breadcrumb_{uuid.uuid4().hex[:10]}"
        timestamp = request.timestamp or datetime.now(timezone.utc)
        breadcrumb = Breadcrumb(
            id=breadcrumb_id,
            timestamp=timestamp,
            node_id=request.node_id,
            edge_id=request.edge_id,
            from_spark=request.from_spark,
            user_note=request.user_note,
            summary=request.summary,
            angle_id=request.angle_id,
        )

        breadcrumbs = list(session.breadcrumbs) + [breadcrumb]

        await Neo4jClient.execute_write(
            """
            MATCH (t:ThinkingSession {id: $id})
            SET t.breadcrumbs_json = $breadcrumbs_json,
                t.updated_at = $updated_at
            """,
            {
                "id": session_id,
                "breadcrumbs_json": json.dumps([b.model_dump(mode="json") for b in breadcrumbs]),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        session.breadcrumbs = breadcrumbs
        return session

    @classmethod
    async def complete_session(
        cls, session_id: str, request: ThinkingCompleteRequest
    ) -> ThinkingSession | None:
        """Mark a session as completed and integrate capture."""
        session = await cls.get_session(session_id)
        if not session:
            return None

        await Neo4jClient.execute_write(
            """
            MATCH (t:ThinkingSession {id: $id})
            SET t.status = $status,
                t.completed_at = $completed_at,
                t.summary = $summary,
                t.insights = $insights
            """,
            {
                "id": session_id,
                "status": ThinkingStatus.COMPLETED.value,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "summary": request.summary,
                "insights": request.insights or [],
            },
        )

        # Promote capture to integrated when thinking session completes
        await CaptureService.update_capture(
            session.capture_id, CaptureUpdateRequest(status=CaptureStatus.INTEGRATED)
        )

        session.status = ThinkingStatus.COMPLETED
        return session

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @classmethod
    async def _ensure_schema(cls) -> None:
        constraints = [
            "CREATE CONSTRAINT thinking_id IF NOT EXISTS FOR (t:ThinkingSession) REQUIRE t.id IS UNIQUE",
            "CREATE INDEX thinking_status IF NOT EXISTS FOR (t:ThinkingSession) ON (t.status)",
        ]
        for query in constraints:
            try:
                await Neo4jClient.execute_write(query)
            except Exception:
                continue

    @classmethod
    def _get_anthropic_client(cls) -> AsyncAnthropic | None:
        if cls._anthropic_client is None and settings.anthropic_api_key:
            cls._anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        return cls._anthropic_client

    @classmethod
    async def _generate_angles(cls, raw_text: str, entities: list[str]) -> list[Angle]:
        """Generate 3-5 exploration angles using LLM with graceful fallback."""
        client = cls._get_anthropic_client()
        if not client:
            return cls._fallback_angles(raw_text, entities)

        prompt = f"""You are guiding a user to explore a spark.
Spark text: {raw_text}
Entities: {', '.join(entities) if entities else 'none'}

Generate 3-5 concise exploration angles as JSON:
[{{"title": "...", "description": "..."}}]
"""
        try:
            message = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            text = message.content[0].text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            angles_data = json.loads(text)
        except Exception:
            angles_data = []

        angles: list[Angle] = []
        for item in angles_data:
            if not isinstance(item, dict):
                continue
            angles.append(
                Angle(
                    id=f"angle_{uuid.uuid4().hex[:8]}",
                    title=item.get("title", "Exploration angle"),
                    description=item.get("description", "Explore this thread."),
                )
            )

        if not angles:
            angles = cls._fallback_angles(raw_text, entities)
        return angles

    @staticmethod
    def _fallback_angles(raw_text: str, entities: list[str]) -> list[Angle]:
        """Deterministic angles when LLM is unavailable."""
        base_topics = entities or [word.strip() for word in raw_text.split()[:3] if word.strip()]
        suggestions = [
            ("Clarify terms", "Define the core idea in your own words."),
            ("Why now", "Why did this spark show up now? What triggered it?"),
            ("Connections", "List related concepts or past notes to link."),
            ("Counterexample", "Where might this not hold or break down?"),
        ]
        angles = []
        for idx, (title, desc) in enumerate(suggestions):
            topic = base_topics[min(idx, len(base_topics) - 1)] if base_topics else "spark"
            angles.append(
                Angle(
                    id=f"angle_{uuid.uuid4().hex[:8]}",
                    title=f"{title} – {topic}",
                    description=desc,
                )
            )
        return angles

    @staticmethod
    def _suggest_template(
        raw_text: str, entities: list[str], angles: list[Angle]
    ) -> NoteTemplateSuggestion:
        """Suggest a SiYuan note outline."""
        title_entity = entities[0] if entities else "Spark"
        today = datetime.now(timezone.utc).date().isoformat()
        headings = [
            "Spark text",
            "Decomposed ideas",
            "Angles to explore",
            "Connections to existing concepts",
            "Insights / reframes",
        ]
        angle_lines = [f"{i+1}. {angle.title} - {angle.description}" for i, angle in enumerate(angles[:3])]
        if angle_lines:
            headings.append("Angle prompts")
        return NoteTemplateSuggestion(
            title=f"Thinking – {title_entity} ({today})",
            headings=headings,
        )

    @staticmethod
    def _build_note_id(capture: Any, entities: list[str], session_id: str) -> str:
        """Build a human-friendly note ID for SiYuan integration."""
        if entities:
            slug = entities[0].lower().replace(" ", "-")
            return f"note-think-{slug}"
        text = getattr(capture, "raw_text", "thinking").split()
        slug = "-".join(text[:3]).lower() if text else session_id
        return f"note-think-{slug}"

    @staticmethod
    def _record_to_session(node: Any) -> ThinkingSession:
        """Convert stored Neo4j node to ThinkingSession."""
        data = dict(node)
        angles_json = data.get("angles_json") or data.get("angles") or "[]"
        if not isinstance(angles_json, str):
            angles_json = json.dumps(angles_json or [])
        breadcrumbs_json = data.get("breadcrumbs_json") or "[]"
        if not isinstance(breadcrumbs_json, str):
            breadcrumbs_json = json.dumps(breadcrumbs_json or [])
        try:
            angles = [Angle.model_validate(a) for a in json.loads(angles_json)]
        except Exception:
            angles = []
        try:
            breadcrumbs = [Breadcrumb.model_validate(b) for b in json.loads(breadcrumbs_json)]
        except Exception:
            breadcrumbs = []

        created_at = data.get("created_at") or data.get("createdAt")
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except ValueError:
                created_at = datetime.now(timezone.utc)

        status_value = data.get("status", ThinkingStatus.ACTIVE.value)
        try:
            status = ThinkingStatus(status_value)
        except ValueError:
            status = ThinkingStatus.ACTIVE

        return ThinkingSession(
            id=data.get("id", ""),
            capture_id=data.get("capture_id") or data.get("captureId", ""),
            created_at=created_at if isinstance(created_at, datetime) else datetime.now(timezone.utc),
            status=status,
            siyuan_note_id=data.get("siyuan_note_id"),
            angles=angles,
            entities=data.get("entities", []),
            breadcrumbs=breadcrumbs,
        )
