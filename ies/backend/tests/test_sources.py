"""Tests for source document import and rendering."""

import pytest

from ies_backend.schemas.source_document import SourceImport, SourceType
from ies_backend.schemas.entity import ExtractionResult, ExtractedEntity
from ies_backend.services.source_service import SourceService
from ies_backend.services.neo4j_client import Neo4jClient


@pytest.fixture
def source_store(monkeypatch):
    """In-memory store for SourceDocument tests."""
    store: dict[str, dict] = {}
    relations: dict[str, set[str]] = {}

    async def mock_write(query: str, parameters: dict | None = None):
        params = parameters or {}
        if "MERGE (s:SourceDocument" in query:
            node = {
                "id": params["id"],
                "source_type": params["source_type"],
                "title": params.get("title"),
                "topic": params.get("topic"),
                "uri": params.get("uri"),
                "user_id": params.get("user_id"),
                "imported_at": params.get("imported_at"),
                "entity_count": params.get("entity_count", 0),
                "content": params.get("content", ""),
            }
            store[node["id"]] = node
            return [{"s": node}]
        if "MERGE (e:Entity" in query:
            rels = relations.setdefault(params["id"], set())
            rels.update(params.get("entities", []))
            return []
        if "DETACH DELETE s" in query:
            deleted = 1 if store.pop(params.get("id"), None) else 0
            relations.pop(params.get("id"), None)
            return [{"deleted": deleted}]
        return []

    async def mock_query(query: str, parameters: dict | None = None):
        params = parameters or {}
        if "MATCH (s:SourceDocument {id:" in query:
            sid = params.get("id")
            node = store.get(sid)
            if not node:
                return []
            return [{"s": node}]
        if "MATCH (s:SourceDocument)" in query:
            results = []
            for sid, node in store.items():
                if params.get("user_id") is None or node.get("user_id") == params.get("user_id"):
                    results.append({"s": node})
            results.sort(key=lambda r: r["s"]["imported_at"], reverse=True)
            return results
        return []

    monkeypatch.setattr(Neo4jClient, "execute_write", staticmethod(mock_write))
    monkeypatch.setattr(Neo4jClient, "execute_query", staticmethod(mock_query))

    store.clear()
    relations.clear()
    return store, relations


@pytest.mark.asyncio
async def test_import_source(monkeypatch, source_store):
    """Importing a text source should store node and entities."""
    extraction = ExtractionResult(
        entities=[
            ExtractedEntity(
                name="Focus",
                kind="idea",
                domain="meta",
                status="seed",
                description="",
                quotes=[],
                connections=[],
            )
        ]
    )

    async def fake_extract(content: str):
        return extraction

    monkeypatch.setattr(SourceService, "_extract_entities", staticmethod(fake_extract))

    request = SourceImport(
        source_type=SourceType.TEXT,
        content="Improving focus with breaks and timeboxing.",
        title="Focus Notes",
        user_id="tester",
    )
    resp = await SourceService.import_source(request)

    assert resp.document.title == "Focus Notes"
    assert resp.document.entity_count == 1
    assert resp.extraction.entities[0].name == "Focus"


@pytest.mark.asyncio
async def test_list_and_delete_source(source_store):
    """List returns stored sources and delete removes them."""
    now = "2025-01-01T00:00:00Z"
    await Neo4jClient.execute_write(
        "MERGE (s:SourceDocument {id: $id}) SET s.source_type=$source_type, s.imported_at=$imported_at",
        {"id": "src_seed", "source_type": "text", "imported_at": now, "entity_count": 0, "content": ""},
    )

    listed = await SourceService.list_sources()
    assert listed.sources
    assert listed.sources[0].id == "src_seed"

    deleted = await SourceService.delete_source("src_seed")
    assert deleted
    listed_after = await SourceService.list_sources()
    assert not listed_after.sources
