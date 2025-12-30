import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from Chat.backend import app

client = TestClient(app)

@pytest.fixture
def mock_genai():
    with patch("Chat.backend.genai") as mock:
        yield mock

@pytest.fixture
def mock_db():
    with patch("Chat.backend.db") as mock:
        yield mock

@pytest.fixture(autouse=True)
def override_db(mock_db):
    """Ensure app uses the mock DB"""
    # Since 'db' is a module-level variable in backend.py, patching "Chat.backend.db" BEFORE 
    # the test function runs (via fixture) usually works IF the endpoint uses the variable `db`.
    # However, to be extra safe if there are other import paths:
    import Chat.backend
    Chat.backend.db = mock_db
    yield

def test_chat_simple_success(mock_genai, mock_db):
    # Mock Chat Session
    mock_model = MagicMock()
    mock_chat = MagicMock()
    mock_response = MagicMock()
    
    mock_response.text = "Hello there!"
    mock_response.usage_metadata.total_token_count = 10
    
    mock_chat.send_message.return_value = mock_response
    mock_model.start_chat.return_value = mock_chat
    mock_genai.GenerativeModel.return_value = mock_model
    
    response = client.post(
        "/chat",
        data={"message": "Hi", "user_id": "u1", "model": "gemini-2.0-flash-exp"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Hello there!"
    
    # Verify DB
    mock_db.save_job.assert_called_once()  

def test_chat_with_history(mock_genai):
    mock_model = MagicMock()
    mock_chat = MagicMock()
    mock_response = MagicMock()
    
    # Mock response
    mock_response.text = "I'm doing well, thanks!"
    mock_response.usage_metadata.total_token_count = 15
    mock_response.candidates = []
    
    mock_chat.send_message.return_value = mock_response
    mock_model.start_chat.return_value = mock_chat
    mock_genai.GenerativeModel.return_value = mock_model
    
    history = json.dumps([
        {"role": "user", "content": "Hello"},
        {"role": "model", "content": "Hi"}
    ])
    
    response = client.post(
        "/chat",
        data={"message": "How are you?", "history": history}
    )
    
    assert response.status_code == 200
    
    # Check start_chat call with history
    mock_model.start_chat.assert_called_once()
    call_kwargs = mock_model.start_chat.call_args[1]
    hist_arg = call_kwargs.get('history')
    
    # The app converts history to [{'role': '...', 'parts': [...]}]
    assert len(hist_arg) == 2
    assert hist_arg[0]['role'] == 'user'
    assert hist_arg[1]['role'] == 'model'

def test_chat_with_tools(mock_genai):
    mock_model = MagicMock()
    mock_chat = MagicMock()
    mock_response = MagicMock()
    
    # Mock response
    mock_response.text = "Search results here"
    mock_response.usage_metadata.total_token_count = 20
    mock_response.candidates = []
    
    mock_chat.send_message.return_value = mock_response
    mock_model.start_chat.return_value = mock_chat
    mock_genai.GenerativeModel.return_value = mock_model
    
    tools = json.dumps(["google_search"])
    
    response = client.post(
        "/chat",
        data={"message": "Search this", "tools": tools}
    )
    
    assert response.status_code == 200
    
    # Verify tools were passed to GenerativeModel constructor
    call_kwargs = mock_genai.GenerativeModel.call_args[1] 
    passed_tools = call_kwargs.get('tools') or []
    
    # Check structure [{'google_search': {}}]
    assert isinstance(passed_tools, list)
    assert "google_search" in passed_tools[0]

def test_response_cleaning(mock_genai):
    # Test stripping of triple quotes
    mock_model = MagicMock()
    mock_chat = MagicMock()
    mock_response = MagicMock()
    
    # Simulate response with quotes
    mock_response.text = '"""Clean me"""' 
    mock_chat.send_message.return_value = mock_response
    mock_model.start_chat.return_value = mock_chat
    mock_genai.GenerativeModel.return_value = mock_model
    
    response = client.post(
        "/chat",
        data={"message": "test"}
    )
    
    assert response.status_code == 200
    assert response.json()["response"] == "Clean me"
