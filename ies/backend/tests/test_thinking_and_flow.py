"""Tests for ThinkingService and FlowSessionService."""

import pytest

from ies_backend.schemas.capture import CaptureCreateRequest, CaptureSource, CaptureStatus
from ies_backend.schemas.flow_session import FlowOpenRequest, FlowStepRequest
from ies_backend.schemas.thinking import ThinkingCompleteRequest, ThinkingStartRequest, ThinkingStepRequest
from ies_backend.services.capture_service import CaptureService
from ies_backend.services.flow_session_service import FlowSessionService
from ies_backend.services.neo4j_client import Neo4jClient
from ies_backend.services.thinking_service import ThinkingService


@pytest.fixture
def graph_store(monkeypatch):
    """Mock Neo4j storage for capture, thinking, and flow sessions."""
    captures: dict[str, dict] = {}
    capture_relations: dict[str, set[str]] = {}
    thinking: dict[str, dict] = {}
    flows: dict[str, dict] = {}

    async def mock_write(query: str, params: dict | None = None):
        p = params or {}

        if "MERGE (c:CaptureItem" in query:
            node = {
                "id": p["id"],
                "raw_text": p.get("raw_text"),
                "source": p.get("source"),
                "captured_at": p.get("captured_at"),
                "status": p.get("status"),
                "context_snippet": p.get("context_snippet"),
                "entities": p.get("entities", []),
                "topics": p.get("topics", []),
                "spark": p.get("spark"),
            }
            captures[node["id"]] = node
            return [{"c": node}]

        if "SET c.status = COALESCE" in query and "CaptureItem" in query:
            node = captures.get(p["id"])
            if node:
                if p.get("status") is not None:
                    node["status"] = p["status"]
                if p.get("entities") is not None:
                    node["entities"] = p["entities"]
                if p.get("topics") is not None:
                    node["topics"] = p["topics"]
            return [{"c": node}] if node else []

        if "MERGE (c)-[:MENTIONS]->(e)" in query:
            rels = capture_relations.setdefault(p["id"], set())
            for name in p.get("entities", []):
                rels.add(name)
            return []

        if "DELETE r" in query and "MENTIONS" in query:
            capture_relations.pop(p.get("id"), None)
            return []

        if "DETACH DELETE c" in query and "CaptureItem" in query:
            deleted = 1 if captures.pop(p.get("id"), None) else 0
            capture_relations.pop(p.get("id"), None)
            return [{"deleted": deleted}]

        if "MERGE (t:ThinkingSession" in query:
            thinking[p["id"]] = {
                "id": p["id"],
                "capture_id": p.get("capture_id"),
                "created_at": p.get("created_at"),
                "status": p.get("status"),
                "siyuan_note_id": p.get("siyuan_note_id"),
                "angles_json": p.get("angles_json"),
                "entities": p.get("entities", []),
                "breadcrumbs_json": p.get("breadcrumbs_json"),
            }
            return [{"t": thinking[p["id"]]}]

        if "SET t.breadcrumbs_json" in query:
            node = thinking.get(p["id"])
            if node:
                node["breadcrumbs_json"] = p.get("breadcrumbs_json", node.get("breadcrumbs_json"))
                node["updated_at"] = p.get("updated_at")
            return []

        if "SET t.status" in query and "ThinkingSession" in query:
            node = thinking.get(p["id"])
            if node:
                node["status"] = p.get("status", node.get("status"))
                node["completed_at"] = p.get("completed_at")
                node["summary"] = p.get("summary")
                node["insights"] = p.get("insights", [])
            return []

        if "MERGE (f:FlowSession" in query:
            flows[p["id"]] = {
                "id": p["id"],
                "origin": p.get("origin"),
                "visited_nodes": p.get("visited_nodes", []),
                "visited_edges": p.get("visited_edges", []),
                "breadcrumbs_json": p.get("breadcrumbs_json", "[]"),
                "insights": p.get("insights", []),
            }
            return [{"f": flows[p["id"]]}]

        if "SET f.breadcrumbs_json" in query:
            node = flows.get(p["id"])
            if node:
                node["breadcrumbs_json"] = p.get("breadcrumbs_json", node.get("breadcrumbs_json"))
                node["visited_nodes"] = p.get("visited_nodes", node.get("visited_nodes"))
                node["visited_edges"] = p.get("visited_edges", node.get("visited_edges"))
            return []

        return []

    async def mock_query(query: str, params: dict | None = None):
        p = params or {}
        if "MATCH (c:CaptureItem {id: $id})" in query:
            cid = p["id"]
            node = captures.get(cid)
            if not node:
                return []
            return [{"capture": node, "entities": list(capture_relations.get(cid, []))}]
        if "MATCH (c:CaptureItem)" in query:
            status = p.get("status")
            results = []
            for cid, node in captures.items():
                if status is None or node.get("status") == status:
                    results.append({"capture": node, "entities": list(capture_relations.get(cid, []))})
            return results
        if "MATCH (t:ThinkingSession {id: $id})" in query:
            node = thinking.get(p["id"])
            return [{"t": node}] if node else []
        if "MATCH (f:FlowSession {id: $id})" in query:
            node = flows.get(p["id"])
            return [{"f": node}] if node else []
        return []

    monkeypatch.setattr(Neo4jClient, "execute_write", staticmethod(mock_write))
    monkeypatch.setattr(Neo4jClient, "execute_query", staticmethod(mock_query))

    captures.clear()
    capture_relations.clear()
    thinking.clear()
    flows.clear()
    return {
        "captures": captures,
        "capture_relations": capture_relations,
        "thinking": thinking,
        "flows": flows,
    }


@pytest.fixture(autouse=True)
def disable_llm(monkeypatch):
    """Force services to use fallback logic."""
    monkeypatch.setattr(ThinkingService, "_get_anthropic_client", classmethod(lambda cls: None))
    monkeypatch.setattr(FlowSessionService, "_get_anthropic_client", classmethod(lambda cls: None))


@pytest.mark.asyncio
async def test_start_thinking_session_builds_angles_and_template(graph_store):
    capture = await CaptureService.create_capture(
        CaptureCreateRequest(rawText="Flow spark about decision paralysis", source=CaptureSource.SIYUAN)
    )

    response = await ThinkingService.start_session(
        ThinkingStartRequest(captureId=capture.id)
    )

    assert response.session.status.value == "active"
    assert len(response.session.angles) >= 3
    assert "Thinking" in response.siyuan_template_suggestion.title


@pytest.mark.asyncio
async def test_record_thinking_step_updates_breadcrumbs(graph_store):
    capture = await CaptureService.create_capture(
        CaptureCreateRequest(rawText="Spark text", source=CaptureSource.PHONE)
    )
    start = await ThinkingService.start_session(ThinkingStartRequest(captureId=capture.id))

    session = await ThinkingService.record_breadcrumb(
        start.session.id,
        ThinkingStepRequest(userNote="First breadcrumb", summary="Summarized"),
    )

    assert session is not None
    assert len(session.breadcrumbs) == 1
    assert session.breadcrumbs[0].user_note == "First breadcrumb"


@pytest.mark.asyncio
async def test_complete_session_marks_capture_integrated(graph_store):
    capture = await CaptureService.create_capture(
        CaptureCreateRequest(rawText="Complete me", source=CaptureSource.READEST)
    )
    start = await ThinkingService.start_session(ThinkingStartRequest(captureId=capture.id))

    completed = await ThinkingService.complete_session(
        start.session.id, ThinkingCompleteRequest(summary="done")
    )

    assert completed is not None
    assert completed.status.value == "completed"
    updated_capture = await CaptureService.get_capture(capture.id)
    assert updated_capture is not None
    assert updated_capture.status == CaptureStatus.INTEGRATED


@pytest.mark.asyncio
async def test_open_flow_from_thinking(graph_store, monkeypatch):
    capture = await CaptureService.create_capture(
        CaptureCreateRequest(rawText="Flow entry point", source=CaptureSource.SIYUAN)
    )
    thinking = await ThinkingService.start_session(ThinkingStartRequest(captureId=capture.id))

    async def mock_fetch_graph_view(cls, center):
        return {"nodes": [{"name": "neighbor"}], "relationships": []}

    monkeypatch.setattr(
        FlowSessionService,
        "_fetch_graph_view",
        classmethod(mock_fetch_graph_view),
    )

    opened = await FlowSessionService.open_from_thinking_session(
        FlowOpenRequest(thinkingSessionId=thinking.session.id)
    )

    assert opened.flow_session.id.startswith("flow_")
    assert opened.initial_view.center_node is not None
    assert len(opened.initial_view.neighbor_nodes) == 1


@pytest.mark.asyncio
async def test_flow_step_and_synthesis(graph_store, monkeypatch):
    capture = await CaptureService.create_capture(
        CaptureCreateRequest(rawText="Flow synthesis", source=CaptureSource.PHONE)
    )
    thinking = await ThinkingService.start_session(ThinkingStartRequest(captureId=capture.id))

    async def mock_fetch_graph_view(cls, center):
        return {"nodes": [], "relationships": []}

    monkeypatch.setattr(
        FlowSessionService,
        "_fetch_graph_view",
        classmethod(mock_fetch_graph_view),
    )

    opened = await FlowSessionService.open_from_thinking_session(
        FlowOpenRequest(thinkingSessionId=thinking.session.id)
    )

    session = await FlowSessionService.record_step(
        opened.flow_session.id,
        FlowStepRequest(nodeId="entry-point", userNote="explore", summary="summary"),
    )
    assert session is not None
    assert "entry-point" in session.visited_nodes

    synthesis = await FlowSessionService.generate_synthesis(opened.flow_session.id)
    assert synthesis is not None
    assert "flow" in synthesis.synthesis.lower()
