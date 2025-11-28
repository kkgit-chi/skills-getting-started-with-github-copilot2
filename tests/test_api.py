"""Test cases for the Mergington High School API."""

import pytest


class TestActivities:
    """Tests for the /activities endpoint."""

    def test_get_activities(self, client):
        """Test retrieving the list of all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Verify we get a dictionary of activities
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify structure of an activity
        first_activity = list(data.values())[0]
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        assert isinstance(first_activity["participants"], list)

    def test_activities_contain_expected_activities(self, client):
        """Test that expected activities are present."""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in data


class TestSignup:
    """Tests for the signup endpoint."""

    def test_signup_for_activity(self, client):
        """Test signing up a student for an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_duplicate_student(self, client):
        """Test that duplicate signups are rejected."""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity(self, client):
        """Test that signing up for a non-existent activity fails."""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_participant_added_to_activity(self, client):
        """Test that a participant is actually added to the activity."""
        email = "newstudent@mergington.edu"
        activity_name = "Programming Class"
        
        # Get initial participants count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity_name]["participants"])
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Verify participant was added
        response2 = client.get("/activities")
        new_count = len(response2.json()[activity_name]["participants"])
        assert new_count == initial_count + 1
        assert email in response2.json()[activity_name]["participants"]


class TestUnregister:
    """Tests for the unregister endpoint."""

    def test_unregister_participant(self, client):
        """Test unregistering a student from an activity."""
        email = "unregister@mergington.edu"
        activity_name = "Tennis Club"
        
        # First, sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Then unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        data = unregister_response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_not_signed_up(self, client):
        """Test that unregistering a non-participant fails."""
        email = "notregistered@mergington.edu"
        activity_name = "Drama Club"
        
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()

    def test_unregister_nonexistent_activity(self, client):
        """Test that unregistering from a non-existent activity fails."""
        response = client.post(
            "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_participant_removed_from_activity(self, client):
        """Test that a participant is actually removed from the activity."""
        email = "removeme@mergington.edu"
        activity_name = "Art Studio"
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Get participant count before unregister
        response1 = client.get("/activities")
        count_after_signup = len(response1.json()[activity_name]["participants"])
        
        # Unregister
        client.post(f"/activities/{activity_name}/unregister?email={email}")
        
        # Verify participant was removed
        response2 = client.get("/activities")
        count_after_unregister = len(response2.json()[activity_name]["participants"])
        assert count_after_unregister == count_after_signup - 1
        assert email not in response2.json()[activity_name]["participants"]

    def test_unregister_restores_availability(self, client):
        """Test that unregistering increases available spots."""
        email = "testspots@mergington.edu"
        activity_name = "Debate Team"
        
        # Get initial availability
        response1 = client.get("/activities")
        initial_max = response1.json()[activity_name]["max_participants"]
        initial_participants = len(response1.json()[activity_name]["participants"])
        initial_availability = initial_max - initial_participants
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Verify availability decreased
        response2 = client.get("/activities")
        after_signup_participants = len(response2.json()[activity_name]["participants"])
        assert after_signup_participants == initial_participants + 1
        
        # Unregister
        client.post(f"/activities/{activity_name}/unregister?email={email}")
        
        # Verify availability restored
        response3 = client.get("/activities")
        final_participants = len(response3.json()[activity_name]["participants"])
        assert final_participants == initial_participants


class TestRoot:
    """Tests for the root endpoint."""

    def test_redirect_to_static(self, client):
        """Test that the root endpoint redirects to the static HTML."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
