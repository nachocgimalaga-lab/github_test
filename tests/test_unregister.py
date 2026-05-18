"""Tests for the POST /activities/{activity_name}/unregister endpoint."""

import pytest


class TestUnregister:
    """Test suite for unregister functionality."""

    def test_unregister_successful(self, client, clean_activities):
        """Test successful unregister from an activity."""
        email = "student@mergington.edu"
        activity_name = "Chess Club"
        
        # First sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Then unregister
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == (
            f"Unregistered {email} from {activity_name}"
        )
        
        # Verify student was removed from participants
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]

    def test_unregister_not_registered_student(self, client, clean_activities):
        """Test unregister fails for student not registered."""
        email = "never_registered@mergington.edu"
        activity_name = "Programming Class"
        
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()

    def test_unregister_invalid_activity(self, client, clean_activities):
        """Test unregister fails for non-existent activity."""
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_missing_email(self, client, clean_activities):
        """Test unregister fails when email parameter is missing."""
        activity_name = "Gym Class"
        
        response = client.post(f"/activities/{activity_name}/unregister")
        
        # Should fail due to missing required query parameter
        assert response.status_code == 422

    def test_unregister_updates_participant_count(self, client, clean_activities):
        """Test that unregister correctly reduces participant count."""
        email = "counter@mergington.edu"
        activity_name = "Soccer Team"
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Get participant count after signup
        after_signup = client.get("/activities")
        count_after_signup = len(
            after_signup.json()[activity_name]["participants"]
        )
        
        # Unregister
        client.post(f"/activities/{activity_name}/unregister?email={email}")
        
        # Get participant count after unregister
        after_unregister = client.get("/activities")
        count_after_unregister = len(
            after_unregister.json()[activity_name]["participants"]
        )
        
        assert count_after_unregister == count_after_signup - 1

    def test_unregister_other_participants_unaffected(self, client, clean_activities):
        """Test that unregistering one student doesn't affect others."""
        emails = [
            "alice@mergington.edu",
            "bob@mergington.edu",
            "charlie@mergington.edu"
        ]
        activity_name = "Art Club"
        
        # Sign up multiple students
        for email in emails:
            client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Unregister one student
        client.post(
            f"/activities/{activity_name}/unregister?email={emails[1]}"
        )
        
        # Verify other students still registered
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        
        assert emails[0] in participants
        assert emails[1] not in participants
        assert emails[2] in participants
        assert len(participants) == 2

    def test_unregister_twice_fails_second_time(self, client, clean_activities):
        """Test that unregistering twice fails the second time."""
        email = "double@mergington.edu"
        activity_name = "Drama Society"
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # First unregister
        response1 = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert response1.status_code == 200
        
        # Second unregister
        response2 = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert response2.status_code == 400
        assert "not registered" in response2.json()["detail"].lower()

    def test_unregister_signup_re_register_cycle(self, client, clean_activities):
        """Test signup->unregister->signup cycle works correctly."""
        email = "cycler@mergington.edu"
        activity_name = "Science Olympiad"
        
        # Sign up
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response3.status_code == 200
        
        # Verify student is registered
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert email in participants

    def test_unregister_with_special_characters_in_email(self, client, clean_activities):
        """Test unregister with email containing special characters."""
        email = "john.doe-ext@mergington.edu"
        activity_name = "Debate Team"
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Unregister
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        assert response.status_code == 200
        
        # Verify removed
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert email not in participants
