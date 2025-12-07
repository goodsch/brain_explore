"""Tests for Flow Mode inbox queue service."""

import pytest

from ies_backend.schemas.inbox import (
    AutoExtracted,
    InboxCreateRequest,
    InboxSource,
    InboxStatus,
    InboxUpdateRequest,
)
from ies_backend.services.inbox_service import InboxService
from ies_backend.services.neo4j_client import Neo4jClient


@pytest.fixture
def inbox_store(monkeypatch):
    """In-memory Neo4j stand-in for inbox service tests."""
    store: dict[str, dict] = {}
    relations: dict[str, set[str]] = {}

    async def mock_write(query: str, parameters: dict | None = None):
        params = parameters or {}
        if "MERGE (c:InboxItem" in query or "CREATE (c:InboxItem" in query:
            node = {
                "id": params["id"],
                "raw_text": params.get("raw_text"),
                "source": params.get("source"),
                "captured_at": params.get("captured_at"),
                "status": params.get("status"),
                "context_snippet": params.get("context_snippet"),
                "entities": params.get("entities", []),
                "topics": params.get("topics", []),
                "spark": params.get("spark"),
            }
            store[node["id"]] = node
            return [{"c": node}]

        if "SET c.status = COALESCE" in query:
            node = store.get(params["id"])
            if node:
                if params.get("status") is not None:
                    node["status"] = params["status"]
                if params.get("entities") is not None:
                    node["entities"] = params["entities"]
                if params.get("topics") is not None:
                    node["topics"] = params["topics"]
                node["updated_at"] = params.get("updated_at")
            return [{"c": node}] if node else []

        if "MERGE (c)-[:MENTIONS]->(e)" in query:
            rels = relations.setdefault(params["id"], set())
            for name in params.get("entities", []):
                rels.add(name)
            return []

        if "DELETE r" in query and "MENTIONS" in query:
            relations.pop(params.get("id"), None)
            return []

        if "DETACH DELETE c" in query:
            deleted = 1 if store.pop(params.get("id"), None) else 0
            relations.pop(params.get("id"), None)
            return [{"deleted": deleted}]

        return []

    async def mock_query(query: str, parameters: dict | None = None):
        params = parameters or {}
        if "MATCH (c:InboxItem {id: $id})" in query:
            cid = params["id"]
            node = store.get(cid)
            if not node:
                return []
            return [{"inbox": node, "entities": list(relations.get(cid, []))}]

        if "MATCH (c:InboxItem)" in query:
            status = params.get("status")
            results = []
            for cid, node in store.items():
                if status is None or node.get("status") == status:
                    results.append({"inbox": node, "entities": list(relations.get(cid, []))})
            return results
        return []

    monkeypatch.setattr(Neo4jClient, "execute_write", staticmethod(mock_write))
    monkeypatch.setattr(Neo4jClient, "execute_query", staticmethod(mock_query))

    store.clear()
    relations.clear()
    return store, relations


@pytest.mark.asyncio
async def test_create_inbox_generates_id_and_auto_extracts(inbox_store):
    """Inbox creation should persist a queued item with auto metadata."""
    request = InboxCreateRequest(
        rawText="Entry-point dependence and choice paralysis keep showing up.",
        source=InboxSource.ASSISTANT_INTERRUPTION,
    )

    created = await InboxService.create_inbox(request)

    assert created.id.startswith("inbox_")
    assert created.status == InboxStatus.QUEUED
    assert created.auto_extracted is not None
    assert created.auto_extracted.entities


@pytest.mark.asyncio
async def test_list_inbox_filters_by_status(inbox_store):
    """Listing inbox items respects status filter."""
    req = InboxCreateRequest(
        rawText="First inbox item",
        source=InboxSource.SIYUAN,
    )
    first = await InboxService.create_inbox(req)
    await InboxService.update_inbox(
        first.id, InboxUpdateRequest(status=InboxStatus.IN_THINKING)
    )
    await InboxService.create_inbox(
        InboxCreateRequest(rawText="Second inbox item", source=InboxSource.PHONE)
    )

    queued = await InboxService.list_inbox(InboxStatus.QUEUED)
    assert all(item.status == InboxStatus.QUEUED for item in queued.items)
    assert queued.total == 1

    all_items = await InboxService.list_inbox(None)
    assert all_items.total == 2


@pytest.mark.asyncio
async def test_update_inbox_status_and_entities(inbox_store):
    """Updating inbox should replace status and entity relationships."""
    created = await InboxService.create_inbox(
        InboxCreateRequest(rawText="Original text", source=InboxSource.PHONE)
    )

    updated = await InboxService.update_inbox(
        created.id,
        InboxUpdateRequest(
            status=InboxStatus.INTEGRATED,
            auto_extracted=AutoExtracted(entities=["entry-point dependence"], topics=["adhd"]),
        ),
    )

    assert updated is not None
    assert updated.status == InboxStatus.INTEGRATED
    assert updated.auto_extracted.entities == ["entry-point dependence"]


@pytest.mark.asyncio
async def test_delete_inbox(inbox_store):
    """Inbox items can be deleted cleanly."""
    created = await InboxService.create_inbox(
        InboxCreateRequest(rawText="To delete", source=InboxSource.READEST)
    )

    success = await InboxService.delete_inbox(created.id)
    assert success is True

    missing = await InboxService.get_inbox(created.id)
    assert missing is None
