"""Service for working with structured thinking templates."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError as PydanticValidationError

try:  # pragma: no cover - optional dependency fallback
    from jsonschema import Draft7Validator
except Exception:  # pragma: no cover
    Draft7Validator = None  # type: ignore[assignment]

from ies_backend.schemas.template import GraphMappingAction, ThinkingTemplate
from ies_backend.services.neo4j_client import Neo4jClient


class TemplateServiceError(Exception):
    """Raised when template operations fail."""


class TemplateService:
    """Loads templates and executes their graph mappings."""

    def __init__(
        self,
        templates_dir: Path | None = None,
        schema_path: Path | None = None,
    ) -> None:
        backend_dir = Path(__file__).resolve().parents[3]
        repo_root = backend_dir.parent.parent
        self.templates_dir = templates_dir or (repo_root / "schemas" / "templates")
        self.schema_path = schema_path or (repo_root / "schemas" / "thinking-template.schema.json")
        self._template_cache: dict[str, ThinkingTemplate] = {}
        self._validator: Draft7Validator | None = None

    def load_template(self, template_id: str) -> ThinkingTemplate:
        """Load a template definition from disk."""

        if template_id in self._template_cache:
            return self._template_cache[template_id]

        template_file = self.templates_dir / f"{template_id}.json"
        if not template_file.exists():
            raise TemplateServiceError(f"Template '{template_id}' not found")

        data = json.loads(template_file.read_text(encoding="utf-8"))
        self.validate_template(data)

        template = ThinkingTemplate.model_validate(data)
        self._template_cache[template_id] = template
        return template

    def validate_template(self, template_data: dict[str, Any]) -> bool:
        """Validate template JSON against the schema."""

        validator = self._get_validator()
        if validator:
            errors = sorted(validator.iter_errors(template_data), key=lambda err: list(err.path))
            if errors:
                details = ", ".join(
                    f"{'/'.join(str(p) for p in err.path) or '<root>'}: {err.message}"
                    for err in errors
                )
                raise TemplateServiceError(f"Template validation failed: {details}")
            return True

        # Fallback to Pydantic validation when jsonschema is unavailable
        try:
            ThinkingTemplate.model_validate(template_data)
        except PydanticValidationError as exc:  # pragma: no cover - rare fallback
            raise TemplateServiceError(str(exc)) from exc
        return True

    async def execute_graph_mapping(
        self,
        template: ThinkingTemplate,
        session_data: dict[str, Any],
    ) -> list[str]:
        """Execute on_complete actions for the template."""

        if not template.graph_mapping or not template.graph_mapping.on_complete:
            return []

        created_entities: list[str] = []
        for action in template.graph_mapping.on_complete:
            normalized = (action.action or "").lower()
            if normalized == "create_or_link":
                entity_id = await self._handle_create_entity(action, template, session_data)
                if entity_id:
                    created_entities.append(entity_id)
            elif normalized == "update_journey":
                await self._handle_update_journey(action, template, session_data)

        return created_entities

    def _get_validator(self) -> Draft7Validator | None:
        """Initialize JSON schema validator lazily."""

        if Draft7Validator is None:
            return None
        if self._validator is None:
            schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
            self._validator = Draft7Validator(schema)
        return self._validator

    async def _handle_create_entity(
        self,
        action: GraphMappingAction,
        template: ThinkingTemplate,
        session_data: dict[str, Any],
    ) -> str | None:
        user_id = session_data.get("user_id")
        if not user_id:
            raise TemplateServiceError("session_data must include 'user_id'")

        if not action.source_section:
            return None

        raw_value = self._get_section_value(session_data, action.source_section)
        content = self._stringify_value(raw_value)
        if not content:
            return None

        title = self._derive_title(raw_value, content)
        entity_type = (action.entity_type or "spark").lower()
        label = self._node_label(entity_type)
        entity_id = f"{entity_type}_{uuid.uuid4().hex}"
        metadata = self._prepare_metadata(action.metadata or {}, session_data)
        metadata.setdefault("template_id", template.id)
        metadata.setdefault("template_name", template.name)
        metadata.setdefault("mode", template.mode.value)
        metadata.setdefault("source_section", action.source_section)

        params = {
            "id": entity_id,
            "user_id": user_id,
            "title": title,
            "content": content,
            "template_id": template.id,
            "template_name": template.name,
            "mode": template.mode.value,
            "session_id": session_data.get("session_id"),
            "session_doc_id": session_data.get("session_doc_id"),
            "source_section": action.source_section,
            "metadata": metadata,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        query = f"""
        CREATE (e:{label} {{
            id: $id,
            user_id: $user_id,
            title: $title,
            content: $content,
            template_id: $template_id,
            template_name: $template_name,
            mode: $mode,
            session_id: $session_id,
            session_doc_id: $session_doc_id,
            source_section: $source_section,
            metadata: $metadata,
            created_at: $created_at
        }})
        RETURN e.id as entity_id
        """

        result = await Neo4jClient.execute_write(query, params)
        created_id = result[0]["entity_id"] if result else entity_id

        if action.link_to:
            await self._link_to_target(created_id, entity_type, action, session_data)

        return created_id

    async def _link_to_target(
        self,
        entity_id: str,
        entity_type: str,
        action: GraphMappingAction,
        session_data: dict[str, Any],
    ) -> None:
        target_reference = self._resolve_reference(session_data, action.link_to)
        if not target_reference:
            return

        relationship = (action.relationship or "sparked_by").upper()
        label = self._node_label(entity_type)
        await Neo4jClient.execute_write(
            f"""
            MATCH (e:{label} {{id: $entity_id}})
            MATCH (target)
            WHERE (target.id = $target_ref OR target.name = $target_ref)
              AND ($user_id IS NULL OR target.user_id IS NULL OR target.user_id = $user_id)
            WITH e, target LIMIT 1
            MERGE (e)-[r:{relationship}]->(target)
            RETURN id(r) as rel_id
            """,
            {
                "entity_id": entity_id,
                "target_ref": target_reference,
                "user_id": session_data.get("user_id"),
            },
        )

    async def _handle_update_journey(
        self,
        action: GraphMappingAction,
        template: ThinkingTemplate,
        session_data: dict[str, Any],
    ) -> None:
        if not action.add_exchange:
            return

        journey_id = session_data.get("journey_id")
        if not journey_id:
            return

        response_text = self._build_journey_entry(template, session_data)
        if not response_text:
            return

        await Neo4jClient.execute_write(
            """
            MATCH (j:Journey {id: $journey_id})
            CREATE (e:ThinkingPartnerExchange {
                id: $exchange_id,
                question: $question,
                response: $response,
                timestamp: $timestamp,
                entity_context: $entity_context
            })
            CREATE (j)-[:HAS_EXCHANGE]->(e)
            RETURN e.id as exchange_id
            """,
            {
                "journey_id": journey_id,
                "exchange_id": f"exchange_{uuid.uuid4().hex}",
                "question": f"Session via template: {template.name}",
                "response": response_text,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "entity_context": session_data.get("session_title") or template.mode.value,
            },
        )

    def _build_journey_entry(
        self,
        template: ThinkingTemplate,
        session_data: dict[str, Any],
    ) -> str:
        responses = []
        for section in template.sections:
            value = self._get_section_value(session_data, section.id)
            text = self._stringify_value(value)
            if text:
                responses.append(f"{section.prompt}: {text}")

        if responses:
            return "\n\n".join(responses)
        return self._stringify_value(session_data.get("transcript"))

    def _get_section_value(self, session_data: dict[str, Any], section_id: str) -> Any:
        sections = session_data.get("section_responses") or {}
        return sections.get(section_id)

    def _stringify_value(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict):
            for key in ("text", "content", "value", "summary"):
                if key in value and value[key]:
                    return str(value[key]).strip()
            # Fall back to joining remaining values
            return "\n".join(
                str(v).strip()
                for v in value.values()
                if isinstance(v, (str, int, float)) and str(v).strip()
            )
        if isinstance(value, list):
            return "\n".join(str(v).strip() for v in value if v)
        return str(value).strip()

    def _derive_title(self, raw_value: Any, fallback: str) -> str:
        if isinstance(raw_value, dict):
            for key in ("title", "heading", "summary"):
                if raw_value.get(key):
                    return str(raw_value[key]).strip()
        return fallback.splitlines()[0][:140]

    def _prepare_metadata(self, metadata: dict[str, Any], session_data: dict[str, Any]) -> dict[str, Any]:
        prepared: dict[str, Any] = {}
        for key, value in metadata.items():
            prepared[key] = self._resolve_metadata_value(value, session_data)
        return prepared

    def _resolve_metadata_value(self, value: Any, session_data: dict[str, Any]) -> Any:
        if isinstance(value, str):
            resolved = self._resolve_reference(session_data, value)
            return resolved if resolved is not None else value
        if isinstance(value, dict):
            return {k: self._resolve_metadata_value(v, session_data) for k, v in value.items()}
        if isinstance(value, list):
            return [self._resolve_metadata_value(v, session_data) for v in value]
        return value

    def _resolve_reference(self, session_data: dict[str, Any], reference: str | None) -> Any:
        if not reference:
            return None

        parts = reference.split(".")
        source = parts[0]
        remaining = parts[1:]
        sections = session_data.get("section_responses") or {}
        current: Any

        if source in sections:
            current = sections[source]
        else:
            current = session_data.get(source)

        for part in remaining:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None

        if isinstance(current, dict):
            return self._stringify_value(current)
        return current

    def _node_label(self, entity_type: str) -> str:
        mapping = {
            "spark": "Spark",
            "insight": "Insight",
            "thread": "Thread",
        }
        return mapping.get(entity_type.lower(), "PersonalEntity")

