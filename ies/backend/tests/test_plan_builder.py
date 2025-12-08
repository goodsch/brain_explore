"""Tests for PlanBuilderService and quick add prompt."""

import pytest

from ies_backend.schemas.entity import ExtractionResult, ExtractedEntity
from ies_backend.schemas.plan import BuildPlanRequest
from ies_backend.services.plan_builder_service import PlanBuilderService
from ies_backend.services.neo4j_client import Neo4jClient


@pytest.fixture
def neo4j_stub(monkeypatch):
    """In-memory stub for Neo4j writes/queries."""
    nodes = {}
    rels = {}

    async def mock_write(query: str, parameters: dict | None = None):
        params = parameters or {}
        if "MERGE (n:QuickAddItem" in query:
            nodes[params["id"]] = {
                "user_id": params["user_id"],
                "type": params["item_type"],
            }
        if "MERGE (e:Entity" in query:
            rels.setdefault(params["id"], set()).update(params.get("entities", []))
        return []

    async def mock_query(query: str, parameters: dict | None = None):
        return []

    monkeypatch.setattr(Neo4jClient, "execute_write", staticmethod(mock_write))
    monkeypatch.setattr(Neo4jClient, "execute_query", staticmethod(mock_query))
    nodes.clear()
    rels.clear()
    return nodes, rels


@pytest.mark.asyncio
async def test_plan_builder_with_extraction(monkeypatch, neo4j_stub):
    """build() returns plan/checklist/spark and links entities."""
    extraction = ExtractionResult(
        entities=[
            ExtractedEntity(
                name="Timeboxing",
                kind="idea",
                domain="meta",
                status="seed",
                description="",
                quotes=[],
                connections=[],
            )
        ]
    )

    async def fake_extract(prompt: str):
        return extraction

    monkeypatch.setattr(PlanBuilderService, "_extract_entities", staticmethod(fake_extract))
    monkeypatch.setattr(PlanBuilderService, "_llm_build_plan", staticmethod(lambda p, d, due: None))
    monkeypatch.setattr(PlanBuilderService, "_llm_build_checklist", staticmethod(lambda p: None))
    monkeypatch.setattr(PlanBuilderService, "_llm_build_spark", staticmethod(lambda p: None))

    req = BuildPlanRequest(
        intent=["plan", "checklist", "spark"],
        content="Write a short post about focus.",
        duration=30,
        user_id="tester",
    )

    resp = await PlanBuilderService.build(
        prompt=req.content,
        intents=req.intent,
        duration=req.duration,
        due=req.due,
        user_id=req.user_id,
        source_id=None,
    )

    assert resp.plan is not None
    assert resp.checklist is not None
    assert resp.spark is not None
    assert resp.extraction.entities[0].name == "Timeboxing"


@pytest.mark.asyncio
async def test_quick_add_endpoint_smoke(monkeypatch, neo4j_stub):
    """Smoke test the quick add flow using fallback builders."""
    extraction = ExtractionResult(entities=[])

    async def fake_extract(prompt: str):
        return extraction

    monkeypatch.setattr(PlanBuilderService, "_extract_entities", staticmethod(fake_extract))
    resp = await PlanBuilderService.build(
        prompt="Summarize today's tasks",
        intents=["plan"],
        duration=None,
        due=None,
        user_id="tester",
    )
    assert resp.plan is not None
    assert resp.plan.micro_start
    assert resp.plan.steps
