# # test_app.py

# import os
# from unittest import mock

# import pytest
# from flask import url_for
# from werkzeug.datastructures import FileStorage

# from app import create_app


# @pytest.fixture
# def app():
#     """Create and configure a new app instance for each test."""
#     app = create_app()
#     app.config.update({
#         "TESTING": True,
#         "SECRET_KEY": "testsecretkey",
#         "MONGO_URI": "mongodb://localhost:27017/testdb",
#         "MONGO_DBNAME": "testdb",
#     })
#     return app


# @pytest.fixture
# def client(app):
#     """A test client for the app."""
#     return app.test_client()


# @pytest.fixture
# def runner(app):
#     """A test runner for the app's Click commands."""
#     return app.test_cli_runner()


# # Mock MongoDB Client
# @pytest.fixture
# def mock_pymongo_client():
#     with mock.patch("app.pymongo.MongoClient") as mock_client:
#         yield mock_client


# # Mock Requests.post
# @pytest.fixture
# def mock_requests_post():
#     with mock.patch("app.requests.post") as mock_post:
#         yield mock_post


# def test_home_page(client, mock_pymongo_client):
#     """Test the home page without user parameter."""
#     response = client.get("/")
#     assert response.status_code == 200
#     assert b"home.html" in response.data or b"Home" in response.data  # Adjust based on actual content


# def test_home_page_with_user(client, mock_pymongo_client):
#     """Test the home page with user parameter."""
#     mock_db = mock_pymongo_client.return_value.__getitem__.return_value
#     mock_db.plants.find.return_value.sort.return_value = [
#         {"_id": 1, "name": "Plant1"},
#         {"_id": 2, "name": "Plant2"},
#         {"_id": 3, "name": "Plant3"},
#         {"_id": 4, "name": "Plant4"},
#     ]

#     response = client.get("/?user=testuser")
#     assert response.status_code == 200
#     assert b"Plant1" in response.data
#     assert b"Plant2" in response.data
#     assert b"Plant3" in response.data
#     assert b"Plant4" not in response.data  # Only latest three


# def test_login_get(client):
#     """Test GET request to login page."""
#     response = client.get("/login")
#     assert response.status_code == 200
#     assert b"login.html" in response.data or b"Login" in response.data  # Adjust based on actual content


# def test_login_post_success(client, mock_pymongo_client):
#     """Test POST request to login with valid credentials."""
#     mock_db = mock_pymongo_client.return_value.__getitem__.return_value
#     mock_db.users.find_one.return_value = {"username": "testuser", "password": "hashedpassword"}

#     with client.session_transaction() as session:
#         pass  # Initialize session

#     response = client.post("/login", data={"username": "testuser", "password": "password"}, follow_redirects=False)
#     assert response.status_code == 302
#     assert response.headers["Location"] == url_for("home", user="testuser", _external=True)


# def test_login_post_failure(client, mock_pymongo_client):
#     """Test POST request to login with invalid credentials."""
#     mock_db = mock_pymongo_client.return_value.__getitem__.return_value
#     mock_db.users.find_one.return_value = None  # User not found

#     response = client.post("/login", data={"username": "invaliduser", "password": "password"})
#     assert response.status_code == 200
#     assert b"Invalid credentials" in response.data


# def test_signup_get(client):
#     """Test GET request to signup page."""
#     response = client.get("/signup")
#     assert response.status_code == 200
#     assert b"signup.html" in response.data or b"Sign Up" in response.data  # Adjust based on actual content


# def test_signup_post_success(client, mock_pymongo_client):
#     """Test POST request to signup with new user."""
#     mock_db = mock_pymongo_client.return_value.__getitem__.return_value
#     mock_db.users.find_one.return_value = None  # Username does not exist

#     response = client.post("/signup", data={"username": "newuser", "password": "newpassword"}, follow_redirects=False)
#     assert response.status_code == 302
#     assert response.headers["Location"] == url_for("home", user="newuser", _external=True)
#     mock_db.users.insert_one.assert_called_once()


# def test_signup_post_existing_user(client, mock_pymongo_client):
#     """Test POST request to signup with existing username."""
#     mock_db = mock_pymongo_client.return_value.__getitem__.return_value
#     mock_db.users.find_one.return_value = {"username": "existinguser", "password": "password"}

#     response = client.post("/signup", data={"username": "existinguser", "password": "password"})
#     assert response.status_code == 200
#     assert b"Username already exists" in response.data


# def test_upload_get(client):
#     """Test GET request to upload page."""
#     response = client.get("/upload")
#     assert response.status_code == 200
#     assert b"upload.html" in response.data or b"Upload" in response.data  # Adjust based on actual content


# def test_upload_post_no_photo(client):
#     """Test POST request to upload without photo data."""
#     response = client.post("/upload", data={})
#     assert response.status_code == 400
#     assert b"No photo data received" in response.data


# def test_upload_post_invalid_photo(client):
#     """Test POST request to upload with invalid photo data."""
#     response = client.post("/upload", data={"photo": "invaliddata"})
#     assert response.status_code == 400
#     assert b"Invalid photo data" in response.data


# def test_upload_post_save_error(client, mock_pymongo_client):
#     """Test POST request to upload with file save error."""
#     with mock.patch("app.save_photo", side_effect=IOError("File save failed")):
#         response = client.post("/upload", data={"photo": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA"})
#         assert response.status_code == 500
#         assert b"File save failed" in response.data


# def test_upload_post_processing_error(client, mock_pymongo_client, mock_requests_post):
#     """Test POST request to upload with processing error."""
#     mock_requests_post.side_effect = requests.RequestException("ML client error")

#     response = client.post("/upload", data={"photo": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA"}, follow_redirects=False)
#     assert response.status_code == 500
#     assert b"Error processing the photo" in response.data


# @mock.patch("app.decode_photo")
# @mock.patch("app.save_photo")
# @mock.patch("app.process_photo")
# def test_upload_post_success(mock_process_photo, mock_save_photo, mock_decode_photo, client, mock_pymongo_client):
#     """Test successful POST request to upload."""
#     mock_decode_photo.return_value = b"binarydata"
#     mock_save_photo.return_value = ("path/to/file.png", "file.png")
#     mock_process_photo.return_value = None

#     response = client.post("/upload", data={"photo": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA"}, follow_redirects=False)
#     assert response.status_code == 302
#     assert response.headers["Location"] == url_for("results", filename="file.png", _external=True)


# def test_new_entry_get_missing_id(client):
#     """Test GET request to new_entry without entry_id."""
#     response = client.get("/new_entry")
#     assert response.status_code == 400
#     assert b"No entry ID provided" in response.data


# def test_new_entry_get_invalid_id(client):
#     """Test GET request to new_entry with invalid entry_id."""
#     response = client.get("/new_entry", query_string={"new_entry_id": "invalidid"})
#     assert response.status_code == 400
#     assert b"Invalid entry ID" in response.data


# def test_new_entry_get_not_found(client, mock_pymongo_client):
#     """Test GET request to new_entry with non-existing entry."""
#     mock_db = mock_pymongo_client.return_value.__getitem__.return_value
#     mock_db.plants.find_one.return_value = None

#     response = client.get("/new_entry", query_string={"new_entry_id": "507f1f77bcf86cd799439011"})
#     assert response.status_code == 404
#     assert b"Entry not found" in response.data


# def test_new_entry_get_success(client, mock_pymongo_client):
#     """Test GET request to new_entry with existing entry."""
#     mock_db = mock_pymongo_client.return_value.__getitem__.return_value
#     mock_db.plants.find_one.return_value = {"photo": "file.png", "name": "Plant1"}

#     response = client.get("/new_entry", query_string={"new_entry_id": "507f1f77bcf86cd799439011"})
#     assert response.status_code == 200
#     assert b"new-entry.html" in response.data or b"New Entry" in response.data  # Adjust based on actual content


# def test_new_entry_post_success(client, mock_pymongo_client):
#     """Test POST request to new_entry with valid data."""
#     mock_db = mock_pymongo_client.return_value.__getitem__.return_value
#     mock_db.plants.find_one.return_value = {"photo": "file.png", "name": "Plant1"}

#     with client.session_transaction() as session:
#         session["username"] = "testuser"

#     response = client.post(
#         "/new_entry",
#         query_string={"new_entry_id": "507f1f77bcf86cd799439011"},
#         data={"instructions": "New instructions"},
#         follow_redirects=False,
#     )
#     assert response.status_code == 302
#     assert response.headers["Location"] == url_for("home", user="testuser", _external=True)
#     mock_db.plants.update_one.assert_called_once()


# def test_results_get_not_found(client, mock_pymongo_client):
#     """Test GET request to results with non-existing prediction."""
#     mock_db = mock_pymongo_client.return_value.__getitem__.return_value
#     mock_db.predictions.find_one.return_value = None

#     response = client.get("/results/nonexistent.png")
#     assert response.status_code == 404
#     assert b"Result not found" in response.data


# def test_results_get_success(client, mock_pymongo_client):
#     """Test GET request to results with existing prediction."""
#     mock_db = mock_pymongo_client.return_value.__getitem__.return_value
#     mock_db.predictions.find_one.return_value = {
#         "photo": "file.png",
#         "plant_name": "Plant1",
#     }

#     response = client.get("/results/file.png")
#     assert response.status_code == 200
#     assert b"Plant1" in response.data
#     assert b"file.png" in response.data


# def test_history_get(client, mock_pymongo_client):
#     """Test GET request to history page."""
#     mock_db = mock_pymongo_client.return_value.__getitem__.return_value
#     mock_db.predictions.find.return_value = [
#         {"photo": "file1.png", "plant_name": "Plant1"},
#         {"photo": "file2.png", "plant_name": "Plant2"},
#     ]

#     response = client.get("/history")
#     assert response.status_code == 200
#     assert b"Plant1" in response.data
#     assert b"Plant2" in response.data


# def test_uploaded_file(client):
#     """Test serving an uploaded file."""
#     with mock.patch("os.path.join", return_value="/path/to/static/uploads/file.png"):
#         with mock.patch("flask.send_from_directory") as mock_send:
#             mock_send.return_value = "file content"
#             response = client.get("/uploads/file.png")
#             assert response.status_code == 200
#             mock_send.assert_called_once()


# def test_decode_photo_valid():
#     """Test decode_photo with valid data."""
#     from app import decode_photo
#     valid_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA"
#     decoded = decode_photo(valid_data)
#     assert isinstance(decoded, bytes)


# def test_decode_photo_invalid():
#     """Test decode_photo with invalid data."""
#     from app import decode_photo
#     invalid_data = "invaliddata"
#     with pytest.raises(ValueError) as excinfo:
#         decode_photo(invalid_data)
#     assert "Invalid photo data" in str(excinfo.value)


# def test_handle_error(client):
#     """Test handle_error function."""
#     from app import handle_error
#     response = handle_error("Test error message", 400)
#     assert response.status_code == 400
#     assert b"Test error message" in response.data


# @mock.patch("app.get_db")
# def test_process_photo_success(mock_get_db, mock_requests_post):
#     """Test process_photo function with successful ML client response."""
#     from app import process_photo

#     mock_response = mock.Mock()
#     mock_response.json.return_value = {"plant_name": "TestPlant"}
#     mock_response.raise_for_status.return_value = None
#     mock_requests_post.return_value = mock_response

#     mock_db = mock.Mock()
#     mock_get_db.return_value = mock_db

#     process_photo("path/to/file.png", "file.png")
#     mock_requests_post.assert_called_once()
#     mock_db.predictions.insert_one.assert_called_once_with({
#         "photo": "file.png",
#         "filepath": "path/to/file.png",
#         "plant_name": "TestPlant",
#     })


# @mock.patch("app.get_db")
# def test_process_photo_ml_error(mock_get_db, mock_requests_post):
#     """Test process_photo function with ML client error."""
#     from app import process_photo
#     mock_requests_post.side_effect = requests.RequestException("ML client failed")

#     with pytest.raises(requests.RequestException):
#         process_photo("path/to/file.png", "file.png")


# def test_get_db(app):
#     """Test get_db function."""
#     from app import get_db
#     with app.app_context():
#         db = get_db()
#         assert db.name == os.getenv("MONGO_DBNAME", "testdb")
