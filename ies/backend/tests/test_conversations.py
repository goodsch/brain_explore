"""Tests for conversation import pipeline."""

import json
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from ies_backend.schemas.conversation import ConversationImport, ConversationSource
from ies_backend.schemas.entity import ExtractionResult, ExtractedEntity
from ies_backend.schemas.personal import CreateSparkRequest
from ies_backend.schemas.profile import ProfileObservation
from ies_backend.services.conversation_service import ConversationService
from ies_backend.services.neo4j_client import Neo4jClient


@pytest.fixture
def conversation_store(monkeypatch):
    """In-memory stand-ins for Neo4j writes/reads."""
    store: dict[str, dict] = {}
    relations: dict[str, set[str]] = {}
    open_questions: list[dict] = []
    spark_links: list[tuple[str | None, str | None]] = []

    async def mock_write(query: str, parameters: dict | None = None):
        params = parameters or {}
        if "MERGE (c:ConversationSession" in query:
            node = {
                "id": params["id"],
                "source": params["source"],
                "topic": params.get("topic"),
                "user_id": params.get("user_id"),
                "imported_at": params.get("imported_at"),
                "turn_count": params.get("turn_count", 0),
                "entity_count": params.get("entity_count", 0),
                "transcript": params.get("transcript"),
            }
            store[node["id"]] = node
            return [{"c": node}]

        if "OpenQuestion" in query:
            open_questions.extend(params.get("questions", []))
            return []

        if "MERGE (e:Entity" in query:
            rels = relations.setdefault(params["id"], set())
            rels.update(params.get("entities", []))
            return []

        if "DERIVED_FROM" in query:
            spark_links.append((params.get("session_id"), params.get("spark_id")))
            return []

        if "DETACH DELETE c" in query:
            deleted = 1 if store.pop(params.get("id"), None) else 0
            relations.pop(params.get("id"), None)
            return [{"deleted": deleted}]

        return []

    async def mock_query(query: str, parameters: dict | None = None):
        params = parameters or {}
        if "MATCH (c:ConversationSession {id:" in query:
            cid = params.get("id")
            node = store.get(cid)
            if not node:
                return []
            rels = relations.get(cid, set())
            return [{"c": node, "entities": list(rels)}]

        if "MATCH (c:ConversationSession)" in query:
            results = []
            for cid, node in store.items():
                if params.get("user_id") is None or node.get("user_id") == params.get("user_id"):
                    results.append({"c": node})
            # mimic ordering by imported_at descending
            results.sort(key=lambda r: r["c"]["imported_at"], reverse=True)
            return results

        return []

    monkeypatch.setattr(Neo4jClient, "execute_write", staticmethod(mock_write))
    monkeypatch.setattr(Neo4jClient, "execute_query", staticmethod(mock_query))

    store.clear()
    relations.clear()
    open_questions.clear()
    spark_links.clear()
    return {
        "sessions": store,
        "relations": relations,
        "open_questions": open_questions,
        "spark_links": spark_links,
    }


@pytest.mark.asyncio
async def test_import_conversation_claude_json(monkeypatch, conversation_store):
    """Claude JSON export should parse turns, extract entities, and persist node."""
    sample = {
        "chat_messages": [
            {"role": "user", "content": "How do I stay focused?"},
            {"role": "assistant", "content": "Try timeboxing and shorter sprints."},
        ]
    }
    extraction = ExtractionResult(
        entities=[
            ExtractedEntity(
                name="Timeboxing",
                kind="idea",
                domain="meta",
                status="seed",
                description="Work in short time blocks",
                quotes=[],
                connections=[],
            )
        ]
    )
    extraction.session_summary.key_insights = ["Timeboxing helps regulate nervous system"]
    extraction.session_summary.open_questions = ["How do I make timeboxing feel flexible?"]
    extraction.session_summary.threads_explored = ["Attention patterns"]

    class DummyProfileService:
        def __init__(self) -> None:
            self.calls: list[tuple[str, ProfileObservation]] = []

        async def apply_observation(self, user_id: str, observation: ProfileObservation):
            self.calls.append((user_id, observation))
            return None

    class DummySparkService:
        def __init__(self) -> None:
            self.requests: list[CreateSparkRequest] = []

        async def create_spark(self, request: CreateSparkRequest):
            self.requests.append(request)
            return SimpleNamespace(id=f"spark_{len(self.requests)}")

    async def fake_extract(transcript: str):
        return extraction

    monkeypatch.setattr(ConversationService, "_extract_entities", staticmethod(fake_extract))
    profile_stub = DummyProfileService()
    spark_stub = DummySparkService()
    monkeypatch.setattr(ConversationService, "profile_service", profile_stub)
    monkeypatch.setattr(ConversationService, "personal_graph_service", spark_stub)

    request = ConversationImport(
        source=ConversationSource.CLAUDE,
        content=json.dumps(sample),
        topic=None,
        user_id="tester",
        create_sparks=True,
    )
    resp = await ConversationService.import_conversation(request)

    assert resp.session.turn_count == 2
    assert resp.session.entity_count == 1
    assert resp.extraction.entities[0].name == "Timeboxing"
    assert profile_stub.calls, "Profile observation should be recorded"
    topics = profile_stub.calls[0][1].topics_explored
    assert "Attention patterns" in topics
    assert spark_stub.requests, "Spark capture should run for key insights"
    assert conversation_store["open_questions"], "Open questions should be stored"
    assert conversation_store["spark_links"], "Spark should be linked to session"


@pytest.mark.asyncio
async def test_list_and_delete_conversations(monkeypatch, conversation_store):
    """List returns stored conversations and delete removes them."""
    # Seed one conversation
    now = datetime.now(timezone.utc).isoformat()
    await Neo4jClient.execute_write(
        "MERGE (c:ConversationSession {id: $id}) SET c.source=$source, c.imported_at=$imported_at",
        {"id": "conv_seed", "source": "text", "imported_at": now, "turn_count": 1, "entity_count": 0},
    )

    listed = await ConversationService.list_conversations()
    assert listed.conversations
    assert listed.conversations[0].id == "conv_seed"

    deleted = await ConversationService.delete_conversation("conv_seed")
    assert deleted
    listed_after = await ConversationService.list_conversations()
    assert not listed_after.conversations
