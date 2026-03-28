import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Test GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Art Studio"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 3
        for activity_name in expected_activities:
            assert activity_name in activities
            assert "description" in activities[activity_name]
            assert "schedule" in activities[activity_name]
            assert "max_participants" in activities[activity_name]
            assert "participants" in activities[activity_name]


class TestSignup:
    """Test POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "david@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities").json()
        assert email in activities_response[activity_name]["participants"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        # Arrange
        activity_name = "NonExistent Club"
        email = "david@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_registered(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "alice@mergington.edu"  # Already registered
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_activity_at_capacity(self, client, reset_activities):
        # Arrange
        activity_name = "Art Studio"  # max 1, currently 0
        email1 = "eve@mergington.edu"
        email2 = "frank@mergington.edu"
        
        # Act - First signup should succeed
        response1 = client.post(f"/activities/{activity_name}/signup?email={email1}")
        assert response1.status_code == 200
        
        # Act - Second signup should fail (at capacity)
        response2 = client.post(f"/activities/{activity_name}/signup?email={email2}")
        
        # Assert
        assert response2.status_code == 400
        assert "maximum capacity" in response2.json()["detail"]


class TestUnregister:
    """Test DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "alice@mergington.edu"  # Currently registered
        
        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities").json()
        assert email not in activities_response[activity_name]["participants"]
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        # Arrange
        activity_name = "NonExistent Club"
        email = "alice@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_enrolled(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "not_enrolled@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]


class TestIntegration:
    """Test multi-step workflows"""
    
    def test_signup_unregister_signup_again(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "george@mergington.edu"
        
        # Act & Assert - Sign up
        response1 = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response1.status_code == 200
        activities1 = client.get("/activities").json()
        assert email in activities1[activity_name]["participants"]
        
        # Act & Assert - Unregister
        response2 = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response2.status_code == 200
        activities2 = client.get("/activities").json()
        assert email not in activities2[activity_name]["participants"]
        
        # Act & Assert - Sign up again
        response3 = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response3.status_code == 200
        activities3 = client.get("/activities").json()
        assert email in activities3[activity_name]["participants"]
    
    def test_multiple_students_signup_and_unregister(self, client, reset_activities):
        # Arrange
        activity_name = "Art Studio"
        students = ["henry@mergington.edu", "iris@mergington.edu"]
        
        # Act & Assert - Multiple signups
        response1 = client.post(f"/activities/{activity_name}/signup?email={students[0]}")
        assert response1.status_code == 200
        
        response2 = client.post(f"/activities/{activity_name}/signup?email={students[1]}")
        assert response2.status_code == 400  # At capacity
        
        # Verify first student is in, second is out
        activities = client.get("/activities").json()
        assert students[0] in activities[activity_name]["participants"]
        assert students[1] not in activities[activity_name]["participants"]
        
        # Act & Assert - Unregister first student
        response_unreg = client.delete(f"/activities/{activity_name}/unregister?email={students[0]}")
        assert response_unreg.status_code == 200
        
        # Act & Assert - Second student can now signup
        response_signup = client.post(f"/activities/{activity_name}/signup?email={students[1]}")
        assert response_signup.status_code == 200
        
        # Verify second student is in, first is out
        activities_final = client.get("/activities").json()
        assert students[0] not in activities_final[activity_name]["participants"]
        assert students[1] in activities_final[activity_name]["participants"]
