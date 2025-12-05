"""Tests for the TemplateService graph mapping engine."""

from unittest.mock import AsyncMock

import pytest

from ies_backend.services.template_service import TemplateService, TemplateServiceError


class TestTemplateService:
    """Validate template loading and execution."""

    def test_load_template_returns_model(self):
        service = TemplateService()

        template = service.load_template("learning-mechanism-map")

        assert template.id == "learning-mechanism-map"
        assert template.sections
        assert template.graph_mapping is not None

    def test_validate_template_rejects_invalid_payload(self):
        service = TemplateService()

        invalid_template: dict = {"mode": "learning"}

        with pytest.raises(TemplateServiceError):
            service.validate_template(invalid_template)

    @pytest.mark.asyncio
    async def test_execute_graph_mapping_creates_entities(self, monkeypatch):
        service = TemplateService()
        template = service.load_template("learning-mechanism-map")

        write_mock = AsyncMock(
            side_effect=[
                [{"entity_id": "spark_test"}],
                [],
                [],
            ]
        )
        monkeypatch.setattr(
            "ies_backend.services.template_service.Neo4jClient.execute_write",
            write_mock,
        )

        session_data = {
            "user_id": "test_user",
            "session_id": "session-123",
            "session_title": "Mechanism Map",
            "section_responses": {
                "synthesis": "Working memory loops info through rehearsal",
                "focus": {"concept_id": "Working Memory"},
            },
            "journey_id": "journey-456",
            "transcript": "Focused exploration",
        }

        created_entities = await service.execute_graph_mapping(template, session_data)

        assert created_entities == ["spark_test"]
        assert write_mock.await_count == 3  # create, link, journey update
