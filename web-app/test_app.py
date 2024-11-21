"""
Unit testing for the web application
"""

import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_home(client):
    """Test GET /"""

    response = client.get("/")
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "Record your voice:" in html
    assert "Upload the audio file:" in html

def test_create_spoken(client):
    """Test POST /spoken"""
    response = client.get('/spoken')
    html = response.data.decode("utf-8")

    assert response.status_code == 201
    assert "Here's a transcript of what you spoke!:" in html

def test_create_upload(client):
    """Test POST /upload"""
    response = client.get('/upload')
    html = response.data.decode("utf-8")
    
    assert response.status_code == 201
    assert "Here's a transcript of what you uploaded!:" in html


