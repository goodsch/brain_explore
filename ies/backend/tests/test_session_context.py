"""Tests for session context endpoint (Phase 4)."""

import json

import pytest
from fastapi.testclient import TestClient

from ies_backend.main import app

client = TestClient(app)


class TestSessionContext:
    """Tests for GET /session/context/{user_id}."""

    def test_get_context_returns_all_fields(self):
        """Context endpoint returns all required fields."""
        response = client.get("/session/context/test_user")

        assert response.status_code == 200
        data = response.json()

        # Check all fields present
        assert "profile_summary" in data
        assert "capacity" in data
        assert "recent_sessions" in data
        assert "active_entities" in data

    def test_context_returns_empty_for_new_user(self):
        """Context endpoint returns empty data for user with no history."""
        response = client.get("/session/context/new_user")

        assert response.status_code == 200
        data = response.json()

        assert data["recent_sessions"] == []
        assert data["active_entities"] == []
        assert data["capacity"] is None

    def test_context_includes_recent_sessions(self, sample_session_data):
        """Context includes recent session data when available."""
        response = client.get("/session/context/test_user")

        assert response.status_code == 200
        data = response.json()

        assert len(data["recent_sessions"]) == 1
        session = data["recent_sessions"][0]
        assert session["topic"] == "Meaning-making as solution"
        assert session["hanging_question"] == "How distinguish addressable vs unavoidable pain?"
        assert "Narrow Window" in session["entities"]

    def test_context_includes_active_entities(self, sample_entity_data):
        """Context includes active (developing/seed) entities."""
        response = client.get("/session/context/test_user")

        assert response.status_code == 200
        data = response.json()

        assert len(data["active_entities"]) == 2
        entity_names = [e["name"] for e in data["active_entities"]]
        assert "Narrow Window" in entity_names
        assert "Meaning-making" in entity_names

    def test_context_includes_capacity_from_profile(self, sample_profile_with_capacity):
        """Context includes capacity when profile has it set."""
        response = client.get("/session/context/test_user")

        assert response.status_code == 200
        data = response.json()

        assert data["capacity"] == 7


@pytest.fixture
def sample_profile_with_capacity(mock_neo4j):
    """Create a profile with capacity set."""
    from tests.conftest import _test_profiles

    _test_profiles["test_user"] = {
        "user_id": "test_user",
        "display_name": "Test User",
        "processing": json.dumps({
            "style": "pattern_first",
            "decision_style": "deliberative",
            "habituation_speed": 5,
            "abstraction_preference": 6,
        }),
        "attention": json.dumps({
            "current_capacity": 7,
            "hyperfocus_triggers": [],
            "distraction_vulnerabilities": [],
            "recovery_patterns": [],
            "optimal_session_length": 30,
        }),
        "communication": json.dumps({
            "verbal_fluency": 5,
            "scripts_preference": 3,
            "directness_preference": 5,
            "pace": "adaptive",
            "wait_time_needed": 3,
        }),
        "executive": json.dumps({
            "task_initiation": 5,
            "transition_cost": 5,
            "time_perception": 5,
            "structure_need": "moderate",
            "working_memory": 5,
        }),
        "sensory": json.dumps({
            "environment_preference": 5,
            "overwhelm_signals": [],
            "regulation_tools": [],
        }),
        "masking": None,
        "onboarding_complete": True,
        "sessions_completed": 5,
        "last_updated": "2025-12-01T10:00:00Z",
    }
    yield
    _test_profiles.clear()
