import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import app - explicit import to handle potential import errors in test env
try:
    from VideoGeneration.backend import app
except ImportError:
    # If running from root without package, we might need adjustments
    # But usually sys.path fix above helps.
    from VideoGeneration.backend import app

client = TestClient(app)

# Mock the helper module entirely
@pytest.fixture
def mock_helpers():
    with patch("VideoGeneration.backend.generate_text_to_video") as mock_t2v, \
         patch("VideoGeneration.backend.generate_image_to_video") as mock_i2v, \
         patch("VideoGeneration.backend.get_operation_status") as mock_status, \
         patch("VideoGeneration.backend.download_video_bytes") as mock_download, \
         patch("VideoGeneration.backend.db") as mock_db, \
         patch("VideoGeneration.backend.storage") as mock_storage:
        
        yield {
            "t2v": mock_t2v,
            "i2v": mock_i2v,
            "status": mock_status,
            "download": mock_download,
            "db": mock_db,
            "storage": mock_storage
        }

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Veo 3.1 Backend is running"}

def test_text_to_video_success(mock_helpers):
    # Setup mock
    mock_helpers["t2v"].return_value = {
        "operation_name": "projects/123/locations/us-central1/operations/456",
        "message": "started"
    }

    response = client.post(
        "/text_to_video",
        data={
            "prompt": "A flying cat",
            "model": "veo-3.1",
            "duration_seconds": 4,
            "user_id": "test_user" 
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "operation_name" in data
    
    # Verify DB save was called
    mock_helpers["db"].save_job.assert_called_once()

def test_text_to_video_failure(mock_helpers):
    mock_helpers["t2v"].side_effect = Exception("API Error")

    response = client.post(
        "/text_to_video",
        data={"prompt": "fail"}
    )

    assert response.status_code == 500
    assert "API Error" in response.json()["detail"]

def test_image_to_video_success(mock_helpers):
    mock_helpers["i2v"].return_value = {
        "operation_name": "op_image",
        "message": "started"
    }
    
    # Create fake image bytes
    files = {'image': ('test.jpg', b'fake_image_bytes', 'image/jpeg')}
    
    response = client.post(
        "/image_to_video",
        data={"prompt": "animate this", "user_id": "u1"},
        files=files
    )

    assert response.status_code == 200
    assert response.json()["ok"] is True
    mock_helpers["db"].save_job.assert_called_once()

def test_status_pending(mock_helpers):
    mock_helpers["status"].return_value = {
        "done": False,
        "state": "pending"
    }
    
    response = client.get("/status/op_123")
    assert response.status_code == 200
    assert response.json()["done"] is False
    # Should NOT try to download or save yet
    mock_helpers["download"].assert_not_called()

def test_status_completed_and_persistence(mock_helpers):
    # Mock status done
    mock_helpers["status"].return_value = {
        "done": True,
        "state": "succeeded"
    }
    
    # Mock download success
    mock_helpers["download"].return_value = (b"video_bytes", "video.mp4")
    
    # Mock storage save
    mock_helpers["storage"].save_video.return_value = "gs://bucket/video.mp4"
    
    # Mock DB retrieval to update job
    mock_job = MagicMock()
    mock_job.status = "pending"
    mock_helpers["db"].get_job_by_operation.return_value = mock_job
    
    response = client.get("/status/op_success")
    
    assert response.status_code == 200
    
    # Verify flow
    mock_helpers["download"].assert_called_with("op_success")
    mock_helpers["storage"].save_video.assert_called()
    mock_helpers["db"].save_job.assert_called() # Should save updated status
    assert mock_job.status == "completed"
    assert mock_job.video_path == "gs://bucket/video.mp4"

def test_download_endpoint(mock_helpers):
    mock_helpers["download"].return_value = (b"some_bytes", "vid.mp4")
    
    response = client.get("/download/op_dl")
    
    assert response.status_code == 200
    assert response.content == b"some_bytes"
    # It should also try to auto-save to storage as a backup
    mock_helpers["storage"].save_video.assert_called()
