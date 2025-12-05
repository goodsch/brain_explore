"""Service for generating, caching, and rating reframes."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from anthropic import AsyncAnthropic

from ies_backend.config import settings
from ies_backend.schemas.reframe import ReframeResponse, ReframeType
from ies_backend.services.neo4j_client import Neo4jClient


CONCEPT_MATCH_CLAUSE = """
MATCH (c:Concept)
WHERE c.id = $concept_lookup
   OR c.concept_id = $concept_lookup
   OR c.slug = $concept_lookup
   OR toLower(c.name) = toLower($concept_lookup)
"""


REFRAME_PROMPT = """You are a wise therapeutic guide who specializes in reframing complex ideas.

Concept: {name}
Definition or summary: {definition}
Related concepts: {related}

Generate {count} distinct reframes that help someone understand or feel into this concept.
- Each reframe should pick a different strategy (metaphor, analogy, pattern, story, contrast).
- Keep them short (1-2 sentences) and concrete.
- Try to cover therapy, personal-life, and meta/system perspectives where helpful.

Respond ONLY with valid JSON matching:
{{
  "reframes": [
    {{
      "type": "metaphor | analogy | pattern | story | contrast",
      "domain": "therapy | personal | meta | system | practice",
      "text": "string",
      "strength": 0-1 number estimating clarity/impact
    }}
  ]
}}
"""


class ReframeService:
    """Generate and manage reframes stored in Neo4j."""

    def __init__(self, anthropic_client: AsyncAnthropic | None = None) -> None:
        self._anthropic_client = anthropic_client

    @property
    def anthropic_client(self) -> AsyncAnthropic:
        """Return or create the Anthropic client lazily."""
        if self._anthropic_client is None:
            if not settings.anthropic_api_key:
                raise RuntimeError("Anthropic API key is not configured")
            self._anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        return self._anthropic_client

    async def get_reframes(self, concept_id: str) -> list[ReframeResponse]:
        """Return cached reframes for the requested concept."""
        query = f"""
        {CONCEPT_MATCH_CLAUSE}
        WITH c
        OPTIONAL MATCH (c)-[:HAS_REFRAME]->(r:Reframe)
        WITH r WHERE r IS NOT NULL
        RETURN r
        ORDER BY r.created_at DESC
        """

        results = await Neo4jClient.execute_query(
            query,
            {"concept_lookup": concept_id},
        )

        reframes = []
        for record in results:
            node = record.get("r")
            if node:
                reframes.append(self._node_to_reframe(node))

        return reframes

    async def generate_reframes(self, concept_id: str, count: int = 5) -> list[ReframeResponse]:
        """Generate new reframes via Claude and cache them in Neo4j."""
        concept = await self._get_concept_context(concept_id)
        if concept is None:
            raise ValueError(f"Concept '{concept_id}' was not found in the graph")

        safe_count = max(1, min(count, 10))
        prompt = self._build_prompt(concept, safe_count)

        message = await self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = message.content[0].text if message.content else ""
        reframe_payloads = self._parse_reframe_payload(raw_text)

        created: list[ReframeResponse] = []
        for payload in reframe_payloads[:safe_count]:
            stored = await self._store_reframe(concept, concept_id, payload)
            if stored:
                created.append(stored)

        return created

    async def record_feedback(self, reframe_id: str, vote: str) -> None:
        """Update votes and normalized strength for a reframe."""
        vote_value = vote.lower()
        if vote_value not in {"helpful", "confusing"}:
            raise ValueError("Vote must be either 'helpful' or 'confusing'")

        query = """
        MATCH (r:Reframe {id: $reframe_id})
        WITH r,
             coalesce(r.helpful_votes, 0) AS helpful,
             coalesce(r.confusing_votes, 0) AS confusing
        WITH r,
             helpful + CASE WHEN $vote = 'helpful' THEN 1 ELSE 0 END AS new_helpful,
             confusing + CASE WHEN $vote = 'confusing' THEN 1 ELSE 0 END AS new_confusing
        SET r.helpful_votes = new_helpful,
            r.confusing_votes = new_confusing,
            r.strength = CASE
                WHEN new_helpful + new_confusing = 0 THEN 0.5
                ELSE toFloat(new_helpful) / (new_helpful + new_confusing)
            END
        RETURN r
        """

        results = await Neo4jClient.execute_write(
            query,
            {"reframe_id": reframe_id, "vote": vote_value},
        )

        if not results:
            raise ValueError(f"Reframe '{reframe_id}' was not found")

    async def _get_concept_context(self, concept_id: str) -> dict[str, Any] | None:
        """Load core metadata + related names for prompt construction."""
        query = f"""
        {CONCEPT_MATCH_CLAUSE}
        OPTIONAL MATCH (c)-[r]-(related)
        RETURN c AS concept, collect(DISTINCT related.name) AS related_names
        LIMIT 1
        """

        results = await Neo4jClient.execute_query(
            query,
            {"concept_lookup": concept_id},
        )

        if not results:
            return None

        record = results[0]
        concept_node = record.get("concept") or record.get("c")
        if not concept_node:
            return None

        related_names = [name for name in record.get("related_names", []) if name]

        return {
            "node": concept_node,
            "name": concept_node.get("name") or concept_id,
            "description": concept_node.get("definition")
            or concept_node.get("description")
            or concept_node.get("summary")
            or "No definition available.",
            "related": related_names[:3],
        }

    def _build_prompt(self, concept: dict[str, Any], count: int) -> str:
        related = concept.get("related") or []
        related_text = ", ".join(related) if related else "(no related concepts recorded)"
        return REFRAME_PROMPT.format(
            name=concept.get("name", "Unnamed Concept"),
            definition=concept.get("description", "No definition available."),
            related=related_text,
            count=count,
        )

    def _parse_reframe_payload(self, text: str) -> list[dict[str, Any]]:
        """Parse Claude output into a list of reframe dicts."""
        cleaned = text.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json", 1)[1].split("```", 1)[0]
        elif cleaned.startswith("```"):
            cleaned = cleaned.strip("`")

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            return []

        if isinstance(data, dict):
            payloads = data.get("reframes") or data.get("ideas") or []
        elif isinstance(data, list):
            payloads = data
        else:
            payloads = []

        valid_payloads = []
        for item in payloads:
            if isinstance(item, dict) and item.get("text"):
                valid_payloads.append(item)

        return valid_payloads

    async def _store_reframe(
        self,
        concept_context: dict[str, Any],
        requested_id: str,
        payload: dict[str, Any],
    ) -> ReframeResponse | None:
        """Persist a reframe node and return its response representation."""
        reframe_id = str(uuid4())
        created_at = datetime.now(timezone.utc)
        type_value = self._resolve_type(payload.get("type"))
        domain = str(payload.get("domain") or "general").strip() or "general"
        strength = self._resolve_strength(payload.get("strength"))

        text_value = payload.get("text", "").strip()
        if not text_value:
            return None

        query = f"""
        {CONCEPT_MATCH_CLAUSE}
        WITH c
        CREATE (r:Reframe {{
            id: $reframe_id,
            concept_id: $stored_concept_id,
            type: $type,
            domain: $domain,
            text: $text,
            strength: $strength,
            helpful_votes: 0,
            confusing_votes: 0,
            created_at: $created_at
        }})
        MERGE (c)-[:HAS_REFRAME]->(r)
        RETURN r
        """

        stored_concept_id = (
            concept_context["node"].get("id")
            or concept_context["node"].get("concept_id")
            or concept_context["node"].get("slug")
            or concept_context["node"].get("name")
            or requested_id
        )

        params = {
            "concept_lookup": requested_id,
            "reframe_id": reframe_id,
            "stored_concept_id": stored_concept_id,
            "type": type_value.value,
            "domain": domain,
            "text": text_value,
            "strength": strength,
            "created_at": created_at.isoformat(),
        }

        results = await Neo4jClient.execute_write(query, params)
        if not results:
            raise ValueError(
                f"Failed to store reframe because concept '{requested_id}' was not found"
            )

        node = results[0].get("r")
        if not node:
            return None

        return self._node_to_reframe(node)

    def _node_to_reframe(self, node: dict[str, Any]) -> ReframeResponse:
        """Convert a Neo4j node dict into a Pydantic response."""
        created_at = self._parse_datetime(node.get("created_at"))
        type_value = self._resolve_type(node.get("type"))
        strength_value = node.get("strength")
        strength = float(strength_value) if strength_value is not None else None

        return ReframeResponse(
            id=node.get("id", ""),
            concept_id=node.get("concept_id", ""),
            type=type_value,
            domain=node.get("domain", "general"),
            text=node.get("text", ""),
            strength=strength,
            helpful_votes=int(node.get("helpful_votes", 0)),
            confusing_votes=int(node.get("confusing_votes", 0)),
            created_at=created_at,
        )

    @staticmethod
    def _parse_datetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            iso_value = value
            if iso_value.endswith("Z"):
                iso_value = iso_value[:-1] + "+00:00"
            try:
                return datetime.fromisoformat(iso_value)
            except ValueError:
                pass
        return datetime.now(timezone.utc)

    @staticmethod
    def _resolve_type(value: Any) -> ReframeType:
        text = str(value or "metaphor").lower()
        try:
            return ReframeType(text)
        except ValueError:
            return ReframeType.METAPHOR

    @staticmethod
    def _resolve_strength(value: Any) -> float:
        try:
            val = float(value)
        except (TypeError, ValueError):
            return 0.5
        return max(0.0, min(1.0, val))


# Singleton-style access for routers/services
reframe_service = ReframeService()
