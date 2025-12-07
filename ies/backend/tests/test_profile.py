"""Tests for profile API and service."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from ies_backend.main import app
from ies_backend.schemas.profile import UserProfile

client = TestClient(app)


class TestProfileAPI:
    """Test profile API endpoints."""

    def test_login_creates_new_profile(self) -> None:
        """Test login endpoint creates profile if not exists."""
        response = client.post("/profile/login?user_id=login_new_user&display_name=NewUser")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "login_new_user"
        assert data["display_name"] == "NewUser"

    def test_login_returns_existing_profile(self) -> None:
        """Test login endpoint returns existing profile."""
        # Create first
        client.post("/profile/login_existing?display_name=Existing")
        # Login again
        response = client.post("/profile/login?user_id=login_existing")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "login_existing"
        assert data["display_name"] == "Existing"

    def test_create_profile(self) -> None:
        """Test creating a new profile."""
        response = client.post("/profile/test_user?display_name=Test")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user"
        assert data["display_name"] == "Test"
        assert data["onboarding_complete"] is False

    def test_get_profile(self) -> None:
        """Test getting an existing profile."""
        # Create first
        client.post("/profile/get_test?display_name=GetTest")
        # Then get
        response = client.get("/profile/get_test")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "get_test"

    def test_get_nonexistent_profile(self) -> None:
        """Test getting a profile that doesn't exist."""
        response = client.get("/profile/nonexistent")
        assert response.status_code == 404

    def test_update_profile(self) -> None:
        """Test updating profile dimensions."""
        # Create first
        client.post("/profile/update_test")
        # Update
        response = client.patch(
            "/profile/update_test",
            json={
                "processing": {
                    "style": "pattern_first",
                    "decision_style": "intuitive",
                    "habituation_speed": 8,
                    "abstraction_preference": 7,
                }
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["processing"]["style"] == "pattern_first"
        assert data["processing"]["habituation_speed"] == 8

    def test_capacity_checkin(self) -> None:
        """Test capacity check-in."""
        # Create first
        client.post("/profile/capacity_test")
        # Check in
        response = client.post(
            "/profile/capacity_test/capacity",
            json={"current_capacity": 7, "notes": "Feeling good today"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["attention"]["current_capacity"] == 7

    def test_profile_summary(self) -> None:
        """Test getting profile summary."""
        # Create first
        client.post("/profile/summary_test?display_name=Summary")
        # Get summary
        response = client.get("/profile/summary_test/summary")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "current_capacity" in data
        assert "processing_style" in data


class TestProfileLearning:
    """Test profile learning from session observations."""

    def test_apply_observation_increments_session_count(self) -> None:
        """Test that apply_observation increments sessions_completed."""
        # Create profile
        client.post("/profile/learning_test_1?display_name=Learning1")

        # Apply observation
        response = client.post(
            "/profile/learning_test_1/observe",
            json={
                "session_id": "session_001",
                "session_length_minutes": 30,
                "topics_explored": ["dopamine", "adhd"],
                "energy_signals": ["engaged", "focused"],
                "approach_effectiveness": {"socratic": 8, "exploratory": 6},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sessions_completed"] == 1

    def test_apply_observation_adds_high_engagement_topics_to_hyperfocus_triggers(self) -> None:
        """Test that deeply engaged topics get added to hyperfocus triggers."""
        # Create profile
        client.post("/profile/learning_test_2?display_name=Learning2")

        # Apply observation with high engagement
        response = client.post(
            "/profile/learning_test_2/observe",
            json={
                "session_id": "session_002",
                "session_length_minutes": 45,
                "topics_explored": ["pattern_recognition"],
                "energy_signals": ["hyperfocused", "deep_engagement"],
                "time_per_entity": {"pattern_recognition": 300},  # 5 minutes = high engagement
                "thinking_partner_exchanges": 5,
                "insights_count": 2,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "pattern_recognition" in data["attention"]["hyperfocus_triggers"]

    def test_apply_observation_does_not_add_low_engagement_topics(self) -> None:
        """Test that briefly touched topics don't get added to triggers."""
        # Create profile
        client.post("/profile/learning_test_3?display_name=Learning3")

        # Apply observation with low engagement
        response = client.post(
            "/profile/learning_test_3/observe",
            json={
                "session_id": "session_003",
                "session_length_minutes": 10,
                "topics_explored": ["fleeting_topic"],
                "energy_signals": [],
                "time_per_entity": {"fleeting_topic": 30},  # Only 30 seconds
                "thinking_partner_exchanges": 0,
                "insights_count": 0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "fleeting_topic" not in data["attention"]["hyperfocus_triggers"]

    def test_apply_observation_stores_approach_effectiveness(self) -> None:
        """Test that approach effectiveness is tracked for question selection."""
        # Create profile with unique name to avoid conflicts
        user_id = f"learning_test_4_{datetime.now().timestamp()}"
        client.post(f"/profile/{user_id}?display_name=Learning4")

        # Apply observation with approach ratings
        response = client.post(
            f"/profile/{user_id}/observe",
            json={
                "session_id": "session_004",
                "session_length_minutes": 25,
                "topics_explored": ["executive_function"],
                "approach_effectiveness": {"socratic": 9, "exploratory": 5, "reflective": 7},
            },
        )
        assert response.status_code == 200
        # The observe endpoint returns the updated profile
        observe_data = response.json()
        assert "approach_effectiveness" in observe_data
        # Verify observe response has the data
        assert "socratic" in observe_data["approach_effectiveness"], (
            f"Observe returned: {observe_data['approach_effectiveness']}"
        )
        assert observe_data["approach_effectiveness"]["socratic"]["average_score"] >= 9

    def test_apply_observation_caps_hyperfocus_triggers_at_20(self) -> None:
        """Test that hyperfocus triggers list is capped at 20 items."""
        # Create profile
        client.post("/profile/learning_test_5?display_name=Learning5")

        # Apply 25 high-engagement sessions with different topics
        for i in range(25):
            client.post(
                "/profile/learning_test_5/observe",
                json={
                    "session_id": f"session_{i:03d}",
                    "session_length_minutes": 30,
                    "topics_explored": [f"topic_{i:02d}"],
                    "energy_signals": ["hyperfocused"],
                    "time_per_entity": {f"topic_{i:02d}": 600},  # 10 minutes each
                    "thinking_partner_exchanges": 5,
                    "insights_count": 1,
                },
            )

        # Verify cap
        response = client.get("/profile/learning_test_5")
        data = response.json()
        assert len(data["attention"]["hyperfocus_triggers"]) <= 20
