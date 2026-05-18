"""Tests for the GET /activities endpoint."""

import pytest


class TestGetActivities:
    """Test suite for retrieving all activities."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all activities are present
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Soccer Team" in data
        assert "Basketball Club" in data
        assert "Art Club" in data
        assert "Drama Society" in data
        assert "Debate Team" in data
        assert "Science Olympiad" in data

    def test_activities_have_required_fields(self, client):
        """Test that each activity has all required fields."""
        response = client.get("/activities")
        data = response.json()
        
        required_fields = {
            "description",
            "schedule",
            "max_participants",
            "participants"
        }
        
        for activity_name, activity_data in data.items():
            assert required_fields.issubset(
                activity_data.keys()
            ), f"Activity '{activity_name}' missing required fields"

    def test_activity_fields_have_correct_types(self, client):
        """Test that activity fields have correct data types."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(
                activity_data["description"], str
            ), f"'{activity_name}' description should be string"
            assert isinstance(
                activity_data["schedule"], str
            ), f"'{activity_name}' schedule should be string"
            assert isinstance(
                activity_data["max_participants"], int
            ), f"'{activity_name}' max_participants should be int"
            assert isinstance(
                activity_data["participants"], list
            ), f"'{activity_name}' participants should be list"

    def test_participants_are_email_strings(self, client):
        """Test that participants are stored as email strings."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            for participant in activity_data["participants"]:
                assert isinstance(
                    participant, str
                ), f"Participant in '{activity_name}' should be string"
                assert "@" in participant, (
                    f"Participant '{participant}' in '{activity_name}' "
                    "should be an email"
                )

    def test_max_participants_is_positive(self, client):
        """Test that max_participants is a positive integer."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert activity_data["max_participants"] > 0, (
                f"'{activity_name}' max_participants should be positive"
            )

    def test_participants_count_within_limit(self, client):
        """Test that participant count doesn't exceed max_participants."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert len(activity_data["participants"]) <= activity_data[
                "max_participants"
            ], (
                f"'{activity_name}' has more participants than max allowed"
            )
