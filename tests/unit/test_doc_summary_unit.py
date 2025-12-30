import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from DocumentsSummarization.backend import app

client = TestClient(app)

@pytest.fixture
def mock_genai():
    with patch("DocumentsSummarization.backend.genai") as mock:
        yield mock

@pytest.fixture
def mock_db():
    with patch("DocumentsSummarization.backend.db") as mock:
        yield mock

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_summarize_txt_success(mock_genai, mock_db):
    # Mock generation response
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "This is a summary."
    mock_response.usage_metadata.total_token_count = 100
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    files = {
        'files': ('test.txt', b'This is some content to summarize.', 'text/plain')
    }
    
    response = client.post(
        "/summarize",
        files=files,
        data={"prompt": "Short summary", "user_id": "u1"}
    )
    
    assert response.status_code == 200
    assert response.json()["summary"] == "This is a summary."
    
    # Verify DB save
    mock_db.save_job.assert_called_once()
    saved_job = mock_db.save_job.call_args[0][0]
    assert saved_job["type"] == "Summarization"
    assert saved_job["tokens"] == 100

def test_summarize_unsupported_file(mock_genai):
    files = {
        'files': ('test.exe', b'binary', 'application/octet-stream')
    }
    
    response = client.post(
        "/summarize",
        files=files
    )
    
    # Depending on implementation, it might ignore and error if no valid files, 
    # or return 400 if list is empty of valid files.
    # The code says: if not combined_content: return 400
    assert response.status_code == 400
    assert "No valid content" in response.json()["detail"]

def test_summarize_pdf_flow(mock_genai):
    # PDF handling logic in backend.py appends a dict with mime_type
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "PDF Summary"
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    files = {
        'files': ('doc.pdf', b'%PDF-1.4...', 'application/pdf')
    }
    
    response = client.post(
        "/summarize",
        files=files
    )
    
    assert response.status_code == 200
    assert response.json()["summary"] == "PDF Summary"
    
    # Check that generate_content was called with the special dict structure
    call_args = mock_model.generate_content.call_args[0][0]
    # It should be a list containing prompt + content parts
    assert any(isinstance(part, dict) and part.get("mime_type") == "application/pdf" for part in call_args)

def test_analytics_auth_failure(mock_db):
    # Mock verify_token dependency? 
    # Since verify_token is imported from auth, we might need to override the dependency 
    # or mock the auth.verify_token function if it's used directly.
    # However, FastAPI depends usually require overriding app.dependency_overrides.
    
    # Let's try mocking the DB call first, assuming no token provided = 403 or 422
    # But wait, the endpoint definition is: get_analytics(user_id, token_uid=Depends(verify_token))
    # If we don't provider header/token, verify_token raises HTTPException.
    
    # Verify rejection without token
    response = client.get("/analytics?user_id=u1")
    assert response.status_code in [401, 403] 

