"""Tests for profile API and service."""

import pytest
from fastapi.testclient import TestClient

from ies_backend.main import app
from ies_backend.schemas.profile import UserProfile

client = TestClient(app)


class TestProfileAPI:
    """Test profile API endpoints."""

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
