import pytest
from fastapi.testclient import TestClient


def test_get_activities(client, reset_activities):
    """Test fetching all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_for_activity(client, reset_activities):
    """Test signing up for an activity"""
    response = client.post(
        "/activities/Chess Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    
    # Verify the student was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_student(client, reset_activities):
    """Test that a student cannot sign up twice"""
    # First signup
    response1 = client.post(
        "/activities/Chess Club/signup?email=duplicate@mergington.edu"
    )
    assert response1.status_code == 200
    
    # Second signup with same email
    response2 = client.post(
        "/activities/Chess Club/signup?email=duplicate@mergington.edu"
    )
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_nonexistent_activity(client, reset_activities):
    """Test signing up for an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Club/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_delete_participant(client, reset_activities):
    """Test removing a participant from an activity"""
    # Delete an existing participant
    response = client.delete(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]
    
    # Verify the participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_delete_nonexistent_participant(client, reset_activities):
    """Test removing a participant that doesn't exist in the activity"""
    response = client.delete(
        "/activities/Chess Club/signup?email=nonexistent@mergington.edu"
    )
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


def test_delete_from_nonexistent_activity(client, reset_activities):
    """Test removing a participant from an activity that doesn't exist"""
    response = client.delete(
        "/activities/Nonexistent Club/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_root_redirect(client):
    """Test that root path redirects to index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"
