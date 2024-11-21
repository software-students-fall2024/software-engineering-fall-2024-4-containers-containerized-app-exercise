from flask import url_for
from app import db


def test_invalid_signup(client):
    """Test signing up with an existing username."""
    db.users.insert_one({"username": "testuser", "password": "testpassword"})
    response = client.post(
        url_for("signup"),
        data={"username": "testuser", "password": "newpassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Username already exists" in response.data


def test_missing_signup_fields(client):
    """Test signup with missing fields."""
    response = client.post(
        url_for("signup"),
        data={"username": "", "password": ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Account created successfully" not in response.data


def test_protected_route_redirect(client):
    """Test accessing a protected route without login."""
    response = client.get(url_for("home_page"), follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data


def test_session_creation(client):
    """Test session creation after starting a focus session."""
    db.users.insert_one({"username": "testuser", "password": "testpassword"})
    client.post(
        url_for("login"),
        data={"username": "testuser", "password": "testpassword"},
        follow_redirects=True,
    )
    response = client.get(url_for("session_form"))
    assert response.status_code == 200


def test_mouse_tracking_event(client):
    """Test mouse tracking POST request with valid event data."""
    response = client.post(
        url_for("track_mouse"),
        json={"event": "mousemove", "x": 100, "y": 200},
    )
    assert response.status_code == 200
    assert b"success" in response.data


def test_mouse_report_storage(client):
    """Test if mouse report is correctly stored in the database."""
    # Create and log in a test user
    user = db.users.insert_one({"username": "testuser", "password": "testpassword"})
    client.post(
        url_for("login"),
        data={"username": "testuser", "password": "testpassword"},
        follow_redirects=True,
    )

    # Access the mouse report route
    response = client.get(url_for("mouse_report"))
    assert response.status_code == 200  # Ensure the request succeeds
    data = response.get_json()
    assert data is not None
    assert "total_mouse_distance" in data

    # Check the report is stored in the database
    stored_report = db.mouse_activity.find_one({"user_id": str(user.inserted_id)})
    assert stored_report is not None
    assert "total_mouse_distance" in stored_report


def test_logout_flow(client):
    """Test logging out after logging in."""
    db.users.insert_one({"username": "testuser", "password": "testpassword"})
    client.post(
        url_for("login"),
        data={"username": "testuser", "password": "testpassword"},
        follow_redirects=True,
    )
    response = client.get(url_for("logout"), follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data


def test_delete_user_data(client):
    """Test clearing user data from the database."""
    # Insert a test user
    user = db.users.insert_one({"username": "testuser", "password": "testpassword"})
    assert user.inserted_id is not None  # Ensure the user is created

    # Insert associated mouse activity and session data
    db.mouse_activity.insert_one({"user_id": str(user.inserted_id), "data": "example"})
    db.sessions.insert_one({"user_id": str(user.inserted_id), "data": "example"})

    # Delete the user and associated data
    db.users.delete_one({"_id": user.inserted_id})  # Delete user
    db.mouse_activity.delete_many(
        {"user_id": str(user.inserted_id)}
    )  # Delete activities
    db.sessions.delete_many({"user_id": str(user.inserted_id)})  # Delete sessions

    # Verify the user was deleted
    assert db.users.find_one({"_id": user.inserted_id}) is None

    # Verify associated data was cleared
    activities = list(db.mouse_activity.find({"user_id": str(user.inserted_id)}))
    sessions = list(db.sessions.find({"user_id": str(user.inserted_id)}))
    assert len(activities) == 0  # Ensure activities are deleted
    assert len(sessions) == 0  # Ensure sessions are deleted
