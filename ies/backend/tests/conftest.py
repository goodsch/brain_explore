"""Test configuration and fixtures."""

import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from ies_backend.schemas.profile import UserProfile


# In-memory storage for tests
_test_profiles: dict[str, dict[str, Any]] = {}
_test_sessions: list[dict[str, Any]] = []
_test_entities: list[dict[str, Any]] = []


def _profile_to_node(profile: UserProfile) -> dict[str, Any]:
    """Convert UserProfile to Neo4j node format."""
    return {
        "user_id": profile.user_id,
        "display_name": profile.display_name,
        "processing": json.dumps(profile.processing.model_dump()),
        "attention": json.dumps(profile.attention.model_dump()),
        "communication": json.dumps(profile.communication.model_dump()),
        "executive": json.dumps(profile.executive.model_dump()),
        "sensory": json.dumps(profile.sensory.model_dump()),
        "masking": json.dumps(profile.masking.model_dump()) if profile.masking else None,
        "onboarding_complete": profile.onboarding_complete,
        "sessions_completed": profile.sessions_completed,
        "last_updated": profile.last_updated,
    }


async def mock_execute_query(query: str, parameters: dict | None = None) -> list[dict]:
    """Mock Neo4j query execution."""
    params = parameters or {}

    if "MATCH (p:UserProfile" in query and "user_id" in params:
        user_id = params["user_id"]
        if user_id in _test_profiles:
            return [{"p": _test_profiles[user_id]}]
        return []

    # Session queries (Phase 4)
    if "MATCH (s:Session" in query:
        user_id = params.get("user_id")
        sessions = [s for s in _test_sessions if s.get("user_id") == user_id]
        return [{"s": s} for s in sessions]

    # Entity queries (Phase 4)
    if "MATCH (e:Entity" in query:
        user_id = params.get("user_id")
        entities = [e for e in _test_entities if e.get("user_id") == user_id]
        # Filter by status if needed
        if "status IN" in query:
            entities = [e for e in entities if e.get("status") in ["seed", "developing"]]
        return [{"e": e} for e in entities]

    return []


async def mock_execute_write(query: str, parameters: dict | None = None) -> list[dict]:
    """Mock Neo4j write execution."""
    params = parameters or {}

    if "CREATE (p:UserProfile" in query:
        # Store the profile
        user_id = params["user_id"]
        _test_profiles[user_id] = {
            "user_id": user_id,
            "display_name": params.get("display_name"),
            "processing": params.get("processing", "{}"),
            "attention": params.get("attention", "{}"),
            "communication": params.get("communication", "{}"),
            "executive": params.get("executive", "{}"),
            "sensory": params.get("sensory", "{}"),
            "masking": params.get("masking"),
            "onboarding_complete": params.get("onboarding_complete", False),
            "sessions_completed": params.get("sessions_completed", 0),
            "last_updated": params.get("last_updated"),
        }
        return [{"p": _test_profiles[user_id]}]

    elif "MATCH (p:UserProfile" in query and "SET" in query:
        # Update the profile
        user_id = params["user_id"]
        if user_id in _test_profiles:
            for key, value in params.items():
                if key != "user_id" and key in _test_profiles[user_id]:
                    _test_profiles[user_id][key] = value
            return [{"p": _test_profiles[user_id]}]

    return []


@pytest.fixture(autouse=True)
def mock_neo4j():
    """Mock Neo4j client for all tests."""
    _test_profiles.clear()  # Clear between tests
    _test_sessions.clear()
    _test_entities.clear()

    with patch(
        "ies_backend.services.profile_service.Neo4jClient.execute_query",
        side_effect=mock_execute_query,
    ), patch(
        "ies_backend.services.profile_service.Neo4jClient.execute_write",
        side_effect=mock_execute_write,
    ), patch(
        "ies_backend.services.entity_storage_service.Neo4jClient.execute_query",
        side_effect=mock_execute_query,
    ), patch(
        "ies_backend.services.entity_storage_service.Neo4jClient.execute_write",
        side_effect=mock_execute_write,
    ):
        yield


@pytest.fixture
def sample_session_data():
    """Add sample session data for context tests."""
    _test_sessions.append({
        "user_id": "test_user",
        "date": "2025-12-01",
        "topic": "Meaning-making as solution",
        "entity_names": ["Narrow Window", "Unnecessary Pain"],
        "hanging_question": "How distinguish addressable vs unavoidable pain?",
    })
    yield
    _test_sessions.clear()


@pytest.fixture
def sample_entity_data():
    """Add sample entity data for context tests."""
    _test_entities.extend([
        {
            "user_id": "test_user",
            "name": "Narrow Window",
            "status": "developing",
            "kind": "idea",
            "updated_at": "2025-12-01T10:00:00Z",
        },
        {
            "user_id": "test_user",
            "name": "Meaning-making",
            "status": "seed",
            "kind": "idea",
            "updated_at": "2025-12-01T09:00:00Z",
        },
    ])
    yield
    _test_entities.clear()
