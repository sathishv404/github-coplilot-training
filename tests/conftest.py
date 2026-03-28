import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for making requests to the app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to a clean state for each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 3,
            "participants": ["alice@mergington.edu", "bob@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 2,
            "participants": ["charlie@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting and drawing",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 1,
            "participants": []
        }
    }
    
    # Store original state
    original_state = {k: v.copy() for k, v in activities.items()}
    
    # Clear and repopulate with test data
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Restore original state
    activities.clear()
    activities.update(original_state)
