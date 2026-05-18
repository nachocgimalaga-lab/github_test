"""Tests for the POST /activities/{activity_name}/signup endpoint."""

import pytest


class TestSignup:
    """Test suite for signup functionality."""

    def test_signup_successful(self, client, clean_activities):
        """Test successful signup for an activity."""
        email = "new_student@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == (
            f"Signed up {email} for {activity_name}"
        )
        
        # Verify student was added to participants
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]

    def test_signup_duplicate_registration_prevented(self, client, clean_activities):
        """Test that duplicate registrations are prevented."""
        email = "student@mergington.edu"
        activity_name = "Programming Class"
        
        # First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup (duplicate attempt)
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_invalid_activity(self, client, clean_activities):
        """Test signup fails for non-existent activity."""
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_missing_email(self, client, clean_activities):
        """Test signup fails when email parameter is missing."""
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup")
        
        # Should fail due to missing required query parameter
        assert response.status_code == 422

    def test_signup_multiple_students_same_activity(self, client, clean_activities):
        """Test multiple different students can sign up for same activity."""
        activity_name = "Gym Class"
        emails = [
            "alice@mergington.edu",
            "bob@mergington.edu",
            "charlie@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all students are registered
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        
        for email in emails:
            assert email in participants
        assert len(participants) == 3

    def test_signup_multiple_activities_same_student(self, client, clean_activities):
        """Test a student can sign up for multiple different activities."""
        email = "versatile_student@mergington.edu"
        activities_to_join = ["Chess Club", "Art Club", "Science Olympiad"]
        
        for activity_name in activities_to_join:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify student is in all activities
        activities_response = client.get("/activities")
        data = activities_response.json()
        
        for activity_name in activities_to_join:
            assert email in data[activity_name]["participants"]

    def test_signup_updates_participant_count(self, client, clean_activities):
        """Test that signup correctly updates the in-memory data."""
        email = "counter@mergington.edu"
        activity_name = "Soccer Team"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(
            initial_response.json()[activity_name]["participants"]
        )
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Get new participant count
        new_response = client.get("/activities")
        new_count = len(new_response.json()[activity_name]["participants"])
        
        assert new_count == initial_count + 1

    def test_signup_with_special_characters_in_email(self, client, clean_activities):
        """Test signup with email containing special characters."""
        email = "john.doe-ext@mergington.edu"
        activity_name = "Drama Society"
        
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        assert response.status_code == 200
        
        # Verify special characters in email are preserved
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert email in participants

    def test_signup_empty_email_string(self, client, clean_activities):
        """Test signup with empty email string."""
        email = ""
        activity_name = "Basketball Club"
        
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Empty email should still be added (validation not currently implemented)
        # This test documents current behavior
        assert response.status_code == 200
