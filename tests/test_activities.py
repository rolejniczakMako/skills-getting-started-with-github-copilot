"""Tests for the activities signup and unregister endpoints."""

import pytest


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup"""

    def test_signup_success(self, client):
        """Test successful signup to an activity."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert "newstudent@mergington.edu" in response.json()["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant to the activity."""
        email = "newstudent@mergington.edu"
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant was added by fetching activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]

    def test_signup_duplicate_email_fails(self, client):
        """Test that trying to signup with an already registered email fails."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signup to a non-existent activity returns 404."""
        response = client.post(
            "/activities/Fake%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_multiple_students_same_activity(self, client):
        """Test that multiple different students can sign up for the same activity."""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email1}"
        )
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email2}"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both are in the activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email1 in activities["Chess Club"]["participants"]
        assert email2 in activities["Chess Club"]["participants"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/signup"""

    def test_unregister_success(self, client):
        """Test successful unregister from an activity."""
        response = client.delete(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant from the activity."""
        email = "michael@mergington.edu"
        
        # Verify student is initially enrolled
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities["Chess Club"]["participants"]

    def test_unregister_non_enrolled_student_fails(self, client):
        """Test that trying to unregister a non-enrolled student fails."""
        response = client.delete(
            "/activities/Chess%20Club/signup?email=notstudent@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregister from a non-existent activity returns 404."""
        response = client.delete(
            "/activities/Fake%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_twice_fails(self, client):
        """Test that unregistering twice from the same activity fails on the second attempt."""
        email = "michael@mergington.edu"
        
        # First unregister succeeds
        response1 = client.delete(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second unregister fails
        response2 = client.delete(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "not signed up" in response2.json()["detail"]


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister workflows."""

    def test_signup_then_unregister(self, client):
        """Test the flow of signing up and then unregistering."""
        email = "newstudent@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify enrolled
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Programming Class"]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify not enrolled
        activities_response = client.get("/activities")
        assert email not in activities_response.json()["Programming Class"]["participants"]

    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple activities."""
        email = "student@mergington.edu"
        
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        response2 = client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify in both activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]
