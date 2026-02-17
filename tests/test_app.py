"""
Tests for the Mergington High School Activities API
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
        "Soccer Team": {
            "description": "Team practices and competitive soccer matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Swim training and local meet preparation",
            "schedule": "Wednesdays and Fridays, 3:00 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["ella@mergington.edu", "lucas@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting workshops and school theater productions",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["grace@mergington.edu", "henry@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Advanced problem solving and competition preparation",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["zoe@mergington.edu", "ethan@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments and science fair projects",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "jack@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }

    # Import here to get the actual module
    from app import activities
    
    # Clear and restore
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Restore after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Soccer Team" in data
        assert "Programming Class" in data
        assert len(data) == 9

    def test_get_activities_includes_activity_details(self, client, reset_activities):
        """Test that activities include expected fields"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Soccer Team"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_shows_current_participants(self, client, reset_activities):
        """Test that participants list is accurate"""
        response = client.get("/activities")
        data = response.json()
        
        soccer_participants = data["Soccer Team"]["participants"]
        assert "liam@mergington.edu" in soccer_participants
        assert "ava@mergington.edu" in soccer_participants


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_success(self, client, reset_activities):
        """Test successful signup of a new participant"""
        response = client.post(
            "/activities/Soccer Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Soccer Team" in data["message"]

    def test_signup_adds_participant_to_list(self, client, reset_activities):
        """Test that signup adds participant to the activity"""
        client.post("/activities/Swimming Club/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        participants = response.json()["Swimming Club"]["participants"]
        assert "newstudent@mergington.edu" in participants

    def test_signup_duplicate_fails(self, client, reset_activities):
        """Test that signing up twice fails"""
        response = client.post(
            "/activities/Soccer Team/signup?email=liam@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signup for nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_multiple_participants(self, client, reset_activities):
        """Test that multiple different participants can sign up"""
        client.post("/activities/Art Studio/signup?email=student1@mergington.edu")
        client.post("/activities/Art Studio/signup?email=student2@mergington.edu")
        
        response = client.get("/activities")
        participants = response.json()["Art Studio"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants
        assert len(participants) == 4  # 2 original + 2 new


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant_success(self, client, reset_activities):
        """Test successful unregistration of a participant"""
        response = client.post(
            "/activities/Soccer Team/unregister?email=liam@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "liam@mergington.edu" in data["message"]

    def test_unregister_removes_participant_from_list(self, client, reset_activities):
        """Test that unregister removes participant from the activity"""
        client.post("/activities/Swimming Club/unregister?email=noah@mergington.edu")
        
        response = client.get("/activities")
        participants = response.json()["Swimming Club"]["participants"]
        assert "noah@mergington.edu" not in participants

    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering a nonexistent participant fails"""
        response = client.post(
            "/activities/Soccer Team/unregister?email=notasignedupstudent@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregister from nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_and_signup_same_participant(self, client, reset_activities):
        """Test that a participant can unregister and then sign up again"""
        # Unregister
        client.post("/activities/Drama Club/unregister?email=grace@mergington.edu")
        
        # Verify unregistered
        response = client.get("/activities")
        assert "grace@mergington.edu" not in response.json()["Drama Club"]["participants"]
        
        # Sign up again
        client.post("/activities/Drama Club/signup?email=grace@mergington.edu")
        
        # Verify signed up again
        response = client.get("/activities")
        assert "grace@mergington.edu" in response.json()["Drama Club"]["participants"]


class TestIntegration:
    """Integration tests for the API"""

    def test_full_signup_flow(self, client, reset_activities):
        """Test complete signup flow"""
        # Get initial activities
        response = client.get("/activities")
        initial_count = len(response.json()["Math Olympiad"]["participants"])
        
        # Sign up for the activity
        response = client.post(
            "/activities/Math Olympiad/signup?email=integration@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant was added
        response = client.get("/activities")
        new_count = len(response.json()["Math Olympiad"]["participants"])
        assert new_count == initial_count + 1
        assert "integration@mergington.edu" in response.json()["Math Olympiad"]["participants"]

    def test_full_unregister_flow(self, client, reset_activities):
        """Test complete unregister flow"""
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Programming Class"]["participants"])
        
        # Unregister a participant
        response = client.post(
            "/activities/Programming Class/unregister?email=emma@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        response = client.get("/activities")
        new_count = len(response.json()["Programming Class"]["participants"])
        assert new_count == initial_count - 1
        assert "emma@mergington.edu" not in response.json()["Programming Class"]["participants"]

    def test_multiple_activities_independence(self, client, reset_activities):
        """Test that changes to one activity don't affect others"""
        new_student = "multiactivity@mergington.edu"
        
        # Sign up for multiple activities
        client.post(f"/activities/Soccer Team/signup?email={new_student}")
        client.post(f"/activities/Chess Club/signup?email={new_student}")
        
        # Verify participant is in both
        response = client.get("/activities")
        assert new_student in response.json()["Soccer Team"]["participants"]
        assert new_student in response.json()["Chess Club"]["participants"]
        
        # Unregister from one activity
        client.post(f"/activities/Soccer Team/unregister?email={new_student}")
        
        # Verify only removed from Soccer Team, still in Chess Club
        response = client.get("/activities")
        assert new_student not in response.json()["Soccer Team"]["participants"]
        assert new_student in response.json()["Chess Club"]["participants"]
