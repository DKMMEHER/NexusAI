import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from YoutubeTranscript.backend import app, extract_transcript_details

client = TestClient(app)

@pytest.fixture
def mock_genai():
    with patch("YoutubeTranscript.backend.genai") as mock:
        yield mock

@pytest.fixture
def mock_yt_api():
    with patch("YoutubeTranscript.backend.YouTubeTranscriptApi") as mock:
        yield mock

@pytest.fixture
def mock_db():
    with patch("YoutubeTranscript.backend.db") as mock:
        yield mock

def test_extract_transcript_summary_success(mock_genai, mock_yt_api, mock_db):
    # Mock YT API
    mock_yt_api.get_transcript.return_value = [
        {"text": "Hello world", "start": 0, "duration": 1},
        {"text": "This is a test", "start": 1, "duration": 1}
    ]
    
    # Mock Gemini
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Video Summary"
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    response = client.post(
        "/transcript",
        data={"url": "https://www.youtube.com/watch?v=12345", "user_id": "u1"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Video Summary"
    assert "Hello world This is a test" in data["transcript"] # Check concatenation
    assert data["video_id"] == "12345"
    
    # Verify DB
    mock_db.save_job.assert_called_once()
    assert mock_db.save_job.call_args[0][0]["type"] == "Transcript"

def test_invalid_url_format():
    response = client.post(
        "/transcript",
        data={"url": "not_a_youtube_url"}
    )
    assert response.status_code == 400  # User error, not server error
    assert "Invalid YouTube URL" in response.json()["detail"]

def test_transcript_api_failure(mock_yt_api):
    mock_yt_api.get_transcript.side_effect = Exception("Transcripts Disabled")
    
    response = client.post(
        "/transcript",
        data={"url": "https://www.youtube.com/watch?v=restricted"}
    )
    
    assert response.status_code == 400  # User error (video has no captions)
    assert "transcript" in response.json()["detail"].lower()

def test_health_check_explicit():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
