"""Tests for ThinkingService and FlowSessionService."""

import pytest

from ies_backend.schemas.inbox import InboxCreateRequest, InboxSource, InboxStatus
from ies_backend.schemas.flow_session import FlowOpenRequest, FlowStepRequest
from ies_backend.schemas.thinking import ThinkingCompleteRequest, ThinkingStartRequest, ThinkingStepRequest
from ies_backend.services.inbox_service import InboxService
from ies_backend.services.flow_session_service import FlowSessionService
from ies_backend.services.neo4j_client import Neo4jClient
from ies_backend.services.thinking_service import ThinkingService


@pytest.fixture
def graph_store(monkeypatch):
    """Mock Neo4j storage for inbox, thinking, and flow sessions."""
    inbox_items: dict[str, dict] = {}
    inbox_relations: dict[str, set[str]] = {}
    thinking: dict[str, dict] = {}
    flows: dict[str, dict] = {}

    async def mock_write(query: str, params: dict | None = None):
        p = params or {}

        if "MERGE (c:InboxItem" in query:
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
            inbox_items[node["id"]] = node
            return [{"c": node}]

        if "SET c.status = COALESCE" in query and "InboxItem" in query:
            node = inbox_items.get(p["id"])
            if node:
                if p.get("status") is not None:
                    node["status"] = p["status"]
                if p.get("entities") is not None:
                    node["entities"] = p["entities"]
                if p.get("topics") is not None:
                    node["topics"] = p["topics"]
            return [{"c": node}] if node else []

        if "MERGE (c)-[:MENTIONS]->(e)" in query:
            rels = inbox_relations.setdefault(p["id"], set())
            for name in p.get("entities", []):
                rels.add(name)
            return []

        if "DELETE r" in query and "MENTIONS" in query:
            inbox_relations.pop(p.get("id"), None)
            return []

        if "DETACH DELETE c" in query and "InboxItem" in query:
            deleted = 1 if inbox_items.pop(p.get("id"), None) else 0
            inbox_relations.pop(p.get("id"), None)
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
        if "MATCH (c:InboxItem {id: $id})" in query:
            cid = p["id"]
            node = inbox_items.get(cid)
            if not node:
                return []
            return [{"inbox": node, "entities": list(inbox_relations.get(cid, []))}]
        if "MATCH (c:InboxItem)" in query:
            status = p.get("status")
            results = []
            for cid, node in inbox_items.items():
                if status is None or node.get("status") == status:
                    results.append({"inbox": node, "entities": list(inbox_relations.get(cid, []))})
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

    inbox_items.clear()
    inbox_relations.clear()
    thinking.clear()
    flows.clear()
    return {
        "inbox": inbox_items,
        "inbox_relations": inbox_relations,
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
    inbox = await InboxService.create_inbox(
        InboxCreateRequest(rawText="Flow spark about decision paralysis", source=InboxSource.SIYUAN)
    )

    response = await ThinkingService.start_session(
        ThinkingStartRequest(captureId=inbox.id)
    )

    assert response.session.status.value == "active"
    assert len(response.session.angles) >= 3
    assert "Thinking" in response.siyuan_template_suggestion.title


@pytest.mark.asyncio
async def test_record_thinking_step_updates_breadcrumbs(graph_store):
    inbox = await InboxService.create_inbox(
        InboxCreateRequest(rawText="Spark text", source=InboxSource.PHONE)
    )
    start = await ThinkingService.start_session(ThinkingStartRequest(captureId=inbox.id))

    session = await ThinkingService.record_breadcrumb(
        start.session.id,
        ThinkingStepRequest(userNote="First breadcrumb", summary="Summarized"),
    )

    assert session is not None
    assert len(session.breadcrumbs) == 1
    assert session.breadcrumbs[0].user_note == "First breadcrumb"


@pytest.mark.asyncio
async def test_complete_session_marks_inbox_integrated(graph_store):
    inbox = await InboxService.create_inbox(
        InboxCreateRequest(rawText="Complete me", source=InboxSource.READEST)
    )
    start = await ThinkingService.start_session(ThinkingStartRequest(captureId=inbox.id))

    completed = await ThinkingService.complete_session(
        start.session.id, ThinkingCompleteRequest(summary="done")
    )

    assert completed is not None
    assert completed.status.value == "completed"
    updated_inbox = await InboxService.get_inbox(inbox.id)
    assert updated_inbox is not None
    assert updated_inbox.status == InboxStatus.INTEGRATED


@pytest.mark.asyncio
async def test_open_flow_from_thinking(graph_store, monkeypatch):
    inbox = await InboxService.create_inbox(
        InboxCreateRequest(rawText="Flow entry point", source=InboxSource.SIYUAN)
    )
    thinking = await ThinkingService.start_session(ThinkingStartRequest(captureId=inbox.id))

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
    inbox = await InboxService.create_inbox(
        InboxCreateRequest(rawText="Flow synthesis", source=InboxSource.PHONE)
    )
    thinking = await ThinkingService.start_session(ThinkingStartRequest(captureId=inbox.id))

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
