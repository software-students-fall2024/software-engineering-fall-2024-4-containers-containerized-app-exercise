from io import BytesIO
import pytest
from app import app, audio_collection, metadata_collection
from unittest.mock import patch, MagicMock


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200


def test_record_route(client):
    response = client.get("/record")
    assert response.status_code == 200


@patch("app.audio_collection.insert_one")
@patch("app.requests.get")
@patch("app.metadata_collection.insert_one")
def test_upload_audio_success(mock_req, mock_md, mock_audio, client):

    mock_audio.return_value.inserted_id = "mock_file"
    mock_md.return_value.acknowledged = True
    mock_req.return_value.ok = True
    mock_req.return_value.text = "Success"

    data = {
        "name": "test_audio",
    }
    file_info = (BytesIO(b"fake_audio_data"), "test_audio.wav")
    response = client.post("/upload-audio", data={"audio": file_info, **data})

    assert response.status_code == 302  # Expecting a redirect to index
    assert mock_audio.called
    assert mock_md.called
    assert mock_req.called


if __name__ == '__main__':
    unittest.main()
