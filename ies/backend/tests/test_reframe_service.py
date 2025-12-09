"""Tests for the ReframeService."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ies_backend.schemas.reframe import ReframeType
from ies_backend.services.reframe_service import ReframeService


@pytest.mark.asyncio
async def test_get_reframes_returns_responses(monkeypatch):
    """get_reframes should convert Neo4j rows into schema objects."""

    sample_node = {
        "id": "ref-1",
        "concept_id": "concept-1",
        "type": "metaphor",
        "domain": "therapy",
        "text": "Therapy as tuning a radio dial toward relief.",
        "strength": 0.8,
        "helpful_votes": 2,
        "confusing_votes": 1,
        "created_at": "2025-01-01T00:00:00+00:00",
    }

    execute_query = AsyncMock(return_value=[{"r": sample_node}])
    monkeypatch.setattr(
        "ies_backend.services.reframe_service.Neo4jClient.execute_query",
        execute_query,
    )

    # Mock Redis to return cache miss
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.setex = AsyncMock()

    service = ReframeService(anthropic_client=AsyncMock())
    service._redis = mock_redis

    reframes = await service.get_reframes("concept-1")

    assert len(reframes) == 1
    assert reframes[0].id == "ref-1"
    assert reframes[0].type == ReframeType.METAPHOR

    # Verify cache was written
    mock_redis.setex.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_reframes_uses_cache(monkeypatch):
    """get_reframes should return cached data without hitting Neo4j."""

    cached_data = [
        {
            "id": "ref-1",
            "concept_id": "concept-1",
            "type": "metaphor",
            "domain": "therapy",
            "text": "Cached reframe text",
            "strength": 0.9,
            "helpful_votes": 5,
            "confusing_votes": 1,
            "created_at": "2025-01-01T00:00:00+00:00",
        }
    ]

    # Mock Redis to return cached data
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=json.dumps(cached_data))

    # Mock Neo4j - should NOT be called when cache hits
    execute_query = AsyncMock()
    monkeypatch.setattr(
        "ies_backend.services.reframe_service.Neo4jClient.execute_query",
        execute_query,
    )

    service = ReframeService(anthropic_client=AsyncMock())
    service._redis = mock_redis

    reframes = await service.get_reframes("concept-1")

    # Verify cache was used
    assert len(reframes) == 1
    assert reframes[0].id == "ref-1"
    assert reframes[0].text == "Cached reframe text"

    # Verify Neo4j was NOT queried
    execute_query.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_reframes_handles_invalid_cache(monkeypatch):
    """get_reframes should fall back to Neo4j if cache data is invalid."""

    sample_node = {
        "id": "ref-1",
        "concept_id": "concept-1",
        "type": "metaphor",
        "domain": "therapy",
        "text": "Fresh from Neo4j",
        "strength": 0.8,
        "helpful_votes": 2,
        "confusing_votes": 1,
        "created_at": "2025-01-01T00:00:00+00:00",
    }

    execute_query = AsyncMock(return_value=[{"r": sample_node}])
    monkeypatch.setattr(
        "ies_backend.services.reframe_service.Neo4jClient.execute_query",
        execute_query,
    )

    # Mock Redis with invalid JSON
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value="invalid json{")
    mock_redis.setex = AsyncMock()

    service = ReframeService(anthropic_client=AsyncMock())
    service._redis = mock_redis

    reframes = await service.get_reframes("concept-1")

    # Should fall back to Neo4j
    assert len(reframes) == 1
    assert reframes[0].text == "Fresh from Neo4j"
    execute_query.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_reframes_persists_results(monkeypatch):
    """Generated reframes should be stored via Neo4j writes."""

    concept_result = [{
        "concept": {
            "id": "concept-1",
            "name": "Narrow Window",
            "description": "Humans sit in a small band of awareness.",
        },
        "related_names": ["Meaning", "Unnecessary Pain"],
    }]

    execute_query = AsyncMock(return_value=concept_result)
    monkeypatch.setattr(
        "ies_backend.services.reframe_service.Neo4jClient.execute_query",
        execute_query,
    )

    stored_params: list[dict] = []

    async def fake_execute_write(query: str, params: dict):
        stored_params.append(params)
        return [{
            "r": {
                "id": params["reframe_id"],
                "concept_id": params["stored_concept_id"],
                "type": params["type"],
                "domain": params["domain"],
                "text": params["text"],
                "strength": params["strength"],
                "helpful_votes": 0,
                "confusing_votes": 0,
                "created_at": params["created_at"],
            }
        }]

    monkeypatch.setattr(
        "ies_backend.services.reframe_service.Neo4jClient.execute_write",
        fake_execute_write,
    )

    llm_payload = {
        "reframes": [
            {
                "type": "metaphor",
                "domain": "therapy",
                "text": "Therapy widens the window like opening shutters.",
                "strength": 0.8,
            },
            {
                "type": "analogy",
                "domain": "personal",
                "text": "It's like tuning a radio away from static toward a signal.",
                "strength": 0.7,
            },
        ]
    }

    response = SimpleNamespace(
        content=[SimpleNamespace(text=json.dumps(llm_payload))]
    )
    messages = SimpleNamespace(create=AsyncMock(return_value=response))
    anthropic_client = SimpleNamespace(messages=messages)

    # Mock Redis cache invalidation
    mock_redis = AsyncMock()
    mock_redis.delete = AsyncMock()

    service = ReframeService(anthropic_client=anthropic_client)
    service._redis = mock_redis

    reframes = await service.generate_reframes("concept-1", count=2)

    assert len(reframes) == 2
    assert len(stored_params) == 2
    assert messages.create.await_count == 1

    # Verify cache was invalidated
    mock_redis.delete.assert_awaited_once()
    call_args = mock_redis.delete.call_args
    assert "ies:reframes:concept-1" in str(call_args)


@pytest.mark.asyncio
async def test_generate_reframes_invalidates_cache(monkeypatch):
    """generate_reframes should invalidate cache to force fresh reads."""

    concept_result = [{
        "concept": {
            "id": "concept-1",
            "name": "Test Concept",
            "description": "Test description",
        },
        "related_names": [],
    }]

    execute_query = AsyncMock(return_value=concept_result)
    monkeypatch.setattr(
        "ies_backend.services.reframe_service.Neo4jClient.execute_query",
        execute_query,
    )

    async def fake_execute_write(query: str, params: dict):
        return [{
            "r": {
                "id": params["reframe_id"],
                "concept_id": params["stored_concept_id"],
                "type": params["type"],
                "domain": params["domain"],
                "text": params["text"],
                "strength": params["strength"],
                "helpful_votes": 0,
                "confusing_votes": 0,
                "created_at": params["created_at"],
            }
        }]

    monkeypatch.setattr(
        "ies_backend.services.reframe_service.Neo4jClient.execute_write",
        fake_execute_write,
    )

    llm_payload = {
        "reframes": [
            {
                "type": "metaphor",
                "domain": "therapy",
                "text": "New reframe",
                "strength": 0.8,
            }
        ]
    }

    response = SimpleNamespace(
        content=[SimpleNamespace(text=json.dumps(llm_payload))]
    )
    messages = SimpleNamespace(create=AsyncMock(return_value=response))
    anthropic_client = SimpleNamespace(messages=messages)

    # Mock Redis
    mock_redis = AsyncMock()
    mock_redis.delete = AsyncMock()

    service = ReframeService(anthropic_client=anthropic_client)
    service._redis = mock_redis

    await service.generate_reframes("concept-1", count=1)

    # Verify cache invalidation was called
    mock_redis.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_record_feedback_updates_votes(monkeypatch):
    """record_feedback should increment votes via write query."""

    execute_write = AsyncMock(return_value=[{"r": {"id": "ref-1"}}])
    monkeypatch.setattr(
        "ies_backend.services.reframe_service.Neo4jClient.execute_write",
        execute_write,
    )

    service = ReframeService(anthropic_client=AsyncMock())
    await service.record_feedback("ref-1", "helpful")

    execute_write.assert_awaited_once()
    called_params = execute_write.await_args.args[1]
    assert called_params["vote"] == "helpful"


@pytest.mark.asyncio
async def test_record_feedback_does_not_invalidate_cache(monkeypatch):
    """record_feedback should NOT invalidate cache (votes don't affect reframe list)."""

    execute_write = AsyncMock(return_value=[{"r": {"id": "ref-1"}}])
    monkeypatch.setattr(
        "ies_backend.services.reframe_service.Neo4jClient.execute_write",
        execute_write,
    )

    # Mock Redis
    mock_redis = AsyncMock()
    mock_redis.delete = AsyncMock()

    service = ReframeService(anthropic_client=AsyncMock())
    service._redis = mock_redis

    await service.record_feedback("ref-1", "helpful")

    # Cache should NOT be invalidated (feedback only updates vote counts, not list)
    mock_redis.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_user_reframe_preferences(monkeypatch):
    """get_user_reframe_preferences should return preferred types and domains."""
    # Mock Neo4j results showing user preference pattern
    execute_query = AsyncMock(return_value=[
        {"type": "metaphor", "domain": "therapy", "helpful": 8, "total": 10},
        {"type": "analogy", "domain": "personal", "helpful": 6, "total": 8},
        {"type": "story", "domain": "meta", "helpful": 1, "total": 5},
    ])
    monkeypatch.setattr(
        "ies_backend.services.reframe_service.Neo4jClient.execute_query",
        execute_query,
    )

    service = ReframeService(anthropic_client=AsyncMock())
    prefs = await service.get_user_reframe_preferences("user-123")

    # User prefers metaphor (80% helpful) and analogy (75% helpful)
    assert "metaphor" in prefs["preferred_types"]
    assert "analogy" in prefs["preferred_types"]
    # Story has low helpful rate (20%), should be in avoid list
    assert "story" in prefs.get("avoid_types", [])
    # Domains should also be tracked
    assert "therapy" in prefs["preferred_domains"]


@pytest.mark.asyncio
async def test_get_user_reframe_preferences_empty_history(monkeypatch):
    """get_user_reframe_preferences should return empty prefs for new users."""
    execute_query = AsyncMock(return_value=[])
    monkeypatch.setattr(
        "ies_backend.services.reframe_service.Neo4jClient.execute_query",
        execute_query,
    )

    service = ReframeService(anthropic_client=AsyncMock())
    prefs = await service.get_user_reframe_preferences("new-user")

    assert prefs["preferred_types"] == []
    assert prefs["preferred_domains"] == []
    assert prefs.get("avoid_types", []) == []


@pytest.mark.asyncio
async def test_cache_key_generation():
    """_cache_key should generate correct Redis key format."""
    service = ReframeService()
    key = service._cache_key("my-concept")
    assert key == "ies:reframes:my-concept"


@pytest.mark.asyncio
async def test_redis_connection_lazy_initialization(monkeypatch):
    """Redis connection should be created lazily on first use."""
    service = ReframeService()
    assert service._redis is None

    # Mock Redis connection
    mock_redis_conn = AsyncMock()

    # Mock the from_url function properly
    mock_from_url = MagicMock(return_value=mock_redis_conn)
    monkeypatch.setattr(
        "redis.asyncio.from_url",
        mock_from_url,
    )

    conn = await service._get_redis()
    assert conn == mock_redis_conn
    assert service._redis == mock_redis_conn

    # Second call should reuse connection
    conn2 = await service._get_redis()
    assert conn2 == mock_redis_conn

    # from_url should only be called once (lazy init)
    assert mock_from_url.call_count == 1


@pytest.mark.asyncio
async def test_close_closes_redis_connection():
    """close() should close Redis connection and reset to None."""
    service = ReframeService()

    # Mock Redis connection
    mock_redis = AsyncMock()
    mock_redis.close = AsyncMock()
    service._redis = mock_redis

    await service.close()

    mock_redis.close.assert_awaited_once()
    assert service._redis is None
