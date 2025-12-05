"""Tests for Flow Mode capture queue service."""

import pytest

from ies_backend.schemas.capture import (
    AutoExtracted,
    CaptureCreateRequest,
    CaptureSource,
    CaptureStatus,
    CaptureUpdateRequest,
)
from ies_backend.services.capture_service import CaptureService
from ies_backend.services.neo4j_client import Neo4jClient


@pytest.fixture
def capture_store(monkeypatch):
    """In-memory Neo4j stand-in for capture service tests."""
    store: dict[str, dict] = {}
    relations: dict[str, set[str]] = {}

    async def mock_write(query: str, parameters: dict | None = None):
        params = parameters or {}
        if "MERGE (c:CaptureItem" in query or "CREATE (c:CaptureItem" in query:
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
        if "MATCH (c:CaptureItem {id: $id})" in query:
            cid = params["id"]
            node = store.get(cid)
            if not node:
                return []
            return [{"capture": node, "entities": list(relations.get(cid, []))}]

        if "MATCH (c:CaptureItem)" in query:
            status = params.get("status")
            results = []
            for cid, node in store.items():
                if status is None or node.get("status") == status:
                    results.append({"capture": node, "entities": list(relations.get(cid, []))})
            return results
        return []

    monkeypatch.setattr(Neo4jClient, "execute_write", staticmethod(mock_write))
    monkeypatch.setattr(Neo4jClient, "execute_query", staticmethod(mock_query))

    store.clear()
    relations.clear()
    return store, relations


@pytest.mark.asyncio
async def test_create_capture_generates_id_and_auto_extracts(capture_store):
    """Capture creation should persist a queued item with auto metadata."""
    request = CaptureCreateRequest(
        rawText="Entry-point dependence and choice paralysis keep showing up.",
        source=CaptureSource.ASSISTANT_INTERRUPTION,
    )

    created = await CaptureService.create_capture(request)

    assert created.id.startswith("capture_")
    assert created.status == CaptureStatus.QUEUED
    assert created.auto_extracted is not None
    assert created.auto_extracted.entities


@pytest.mark.asyncio
async def test_list_captures_filters_by_status(capture_store):
    """Listing captures respects status filter."""
    req = CaptureCreateRequest(
        rawText="First capture",
        source=CaptureSource.SIYUAN,
    )
    first = await CaptureService.create_capture(req)
    await CaptureService.update_capture(
        first.id, CaptureUpdateRequest(status=CaptureStatus.IN_THINKING)
    )
    await CaptureService.create_capture(
        CaptureCreateRequest(rawText="Second capture", source=CaptureSource.PHONE)
    )

    queued = await CaptureService.list_captures(CaptureStatus.QUEUED)
    assert all(item.status == CaptureStatus.QUEUED for item in queued.items)
    assert queued.total == 1

    all_items = await CaptureService.list_captures(None)
    assert all_items.total == 2


@pytest.mark.asyncio
async def test_update_capture_status_and_entities(capture_store):
    """Updating capture should replace status and entity relationships."""
    created = await CaptureService.create_capture(
        CaptureCreateRequest(rawText="Original text", source=CaptureSource.PHONE)
    )

    updated = await CaptureService.update_capture(
        created.id,
        CaptureUpdateRequest(
            status=CaptureStatus.INTEGRATED,
            auto_extracted=AutoExtracted(entities=["entry-point dependence"], topics=["adhd"]),
        ),
    )

    assert updated is not None
    assert updated.status == CaptureStatus.INTEGRATED
    assert updated.auto_extracted.entities == ["entry-point dependence"]


@pytest.mark.asyncio
async def test_delete_capture(capture_store):
    """Captures can be deleted cleanly."""
    created = await CaptureService.create_capture(
        CaptureCreateRequest(rawText="To delete", source=CaptureSource.READEST)
    )

    success = await CaptureService.delete_capture(created.id)
    assert success is True

    missing = await CaptureService.get_capture(created.id)
    assert missing is None
