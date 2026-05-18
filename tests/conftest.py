"""Pytest configuration and shared fixtures for tests."""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client with a fresh copy of the app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to a clean state before each test."""
    # Store original activities
    original_activities = activities.copy()
    original_participants = {
        name: details["participants"].copy()
        for name, details in activities.items()
    }
    
    yield
    
    # Restore original state
    for name, details in activities.items():
        details["participants"] = original_participants[name]


@pytest.fixture
def clean_activities():
    """Provide a minimal set of activities for isolated testing."""
    # Clear existing participants
    for activity in activities.values():
        activity["participants"] = []
    
    yield activities
    
    # Reset to original state
    for name in activities:
        activities[name]["participants"] = []
