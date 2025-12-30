"""
Integration Tests for Chat Service
Tests the full workflow of chat including:
- Chat session management
- History handling
- Tool integration (Google Search, Code Execution)
- Multi-turn conversations
- Database integration
"""
import pytest
import os
import sys
import json
import time
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi.testclient import TestClient
from Chat.backend import app

client = TestClient(app)


@pytest.fixture
def mock_genai():
    """Mock the Gemini API for chat."""
    with patch("Chat.backend.genai") as mock:
        mock_model = MagicMock()
        mock_chat = MagicMock()
        mock_response = MagicMock()
        
        mock_response.text = "This is a test response from the AI."
        mock_response.usage_metadata.total_token_count = 50
        mock_response.candidates = []
        
        mock_chat.send_message.return_value = mock_response
        mock_model.start_chat.return_value = mock_chat
        mock.GenerativeModel.return_value = mock_model
        
        yield mock


class TestChatIntegration:
    """Integration tests for Chat service."""
    
    def test_health_endpoint(self):
        """Test that the health endpoint is accessible."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_simple_chat_workflow(self, mock_genai):
        """Test a simple chat interaction."""
        response = client.post(
            "/chat",
            data={
                "message": "Hello, how are you?",
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert len(data["response"]) > 0
        
        print(f"✅ Chat response: {data['response']}")
    
    def test_chat_with_conversation_history(self, mock_genai):
        """Test chat with conversation history."""
        # Simulate a multi-turn conversation
        history = [
            {"role": "user", "content": "My name is Alice"},
            {"role": "model", "content": "Nice to meet you, Alice!"},
            {"role": "user", "content": "I like programming"},
            {"role": "model", "content": "That's great! What languages do you enjoy?"}
        ]
        
        response = client.post(
            "/chat",
            data={
                "message": "What's my name?",
                "history": json.dumps(history),
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        
        # Verify that history was passed to the model
        mock_genai.GenerativeModel.return_value.start_chat.assert_called_once()
        call_kwargs = mock_genai.GenerativeModel.return_value.start_chat.call_args[1]
        assert "history" in call_kwargs
        assert len(call_kwargs["history"]) == 4
        
        print("✅ Chat with history works correctly")
    
    def test_chat_with_google_search_tool(self, mock_genai):
        """Test chat with Google Search tool enabled."""
        tools = ["google_search"]
        
        response = client.post(
            "/chat",
            data={
                "message": "What's the weather in Paris today?",
                "tools": json.dumps(tools),
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        
        # Verify tools were passed to the model
        call_kwargs = mock_genai.GenerativeModel.call_args[1]
        assert "tools" in call_kwargs
        assert call_kwargs["tools"] is not None
        
        print("✅ Google Search tool integration works")
    
    def test_chat_with_code_execution_tool(self, mock_genai):
        """Test chat with Code Execution tool enabled."""
        tools = ["code_execution"]
        
        response = client.post(
            "/chat",
            data={
                "message": "Calculate the factorial of 10",
                "tools": json.dumps(tools),
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        
        # Verify code execution tool was enabled
        call_kwargs = mock_genai.GenerativeModel.call_args[1]
        assert "tools" in call_kwargs
        
        print("✅ Code Execution tool integration works")
    
    def test_chat_with_multiple_tools(self, mock_genai):
        """Test chat with multiple tools enabled."""
        tools = ["google_search", "code_execution"]
        
        response = client.post(
            "/chat",
            data={
                "message": "Search for Python tutorials and calculate 2^10",
                "tools": json.dumps(tools),
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        
        print("✅ Multiple tools integration works")
    
    def test_chat_with_different_models(self, mock_genai):
        """Test chat with different Gemini models."""
        models = [
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash-thinking-exp-1219",
            "gemini-3-pro-preview"
        ]
        
        for model in models:
            response = client.post(
                "/chat",
                data={
                    "message": f"Test message for {model}",
                    "model": model,
                    "user_id": "test_user_123"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            
            print(f"✅ Model {model} works correctly")
    
    def test_response_cleaning(self, mock_genai):
        """Test that triple quotes are properly cleaned from responses."""
        # Mock response with triple quotes
        mock_genai.GenerativeModel.return_value.start_chat.return_value.send_message.return_value.text = '"""Clean this text"""'
        
        response = client.post(
            "/chat",
            data={
                "message": "Test cleaning",
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be cleaned
        assert data["response"] == "Clean this text"
        
        print("✅ Response cleaning works correctly")
    
    def test_database_integration(self, mock_genai):
        """Test that chat jobs are saved to database."""
        with patch("Chat.backend.db") as mock_db:
            response = client.post(
                "/chat",
                data={
                    "message": "Database test",
                    "user_id": "test_user_123"
                }
            )
            
            assert response.status_code == 200
            
            # Verify database save was called
            mock_db.save_job.assert_called_once()
            
            # Verify the saved data structure
            call_args = mock_db.save_job.call_args[0][0]
            assert "job_id" in call_args
            assert "user_id" in call_args
            assert "type" in call_args
            
            print("✅ Database integration works correctly")
    
    def test_error_handling_empty_message(self):
        """Test error handling for empty message."""
        response = client.post(
            "/chat",
            data={
                "message": "",
                "user_id": "test_user_123"
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 422, 500]
    
    def test_error_handling_invalid_history(self, mock_genai):
        """Test error handling for invalid history format."""
        response = client.post(
            "/chat",
            data={
                "message": "Test",
                "history": "invalid json",
                "user_id": "test_user_123"
            }
        )
        
        # Should still work, just ignore invalid history
        assert response.status_code == 200
    
    def test_concurrent_chat_sessions(self, mock_genai):
        """Test handling of multiple concurrent chat sessions."""
        import concurrent.futures
        
        def make_chat_request(i):
            return client.post(
                "/chat",
                data={
                    "message": f"Concurrent message {i}",
                    "user_id": f"user_{i}"
                }
            )
        
        # Submit 5 concurrent chat requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_chat_request, i) for i in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        for result in results:
            assert result.status_code == 200
        
        print("✅ Concurrent chat sessions handled successfully")
    
    def test_long_conversation_history(self, mock_genai):
        """Test chat with very long conversation history."""
        # Create a long history (20 turns)
        history = []
        for i in range(20):
            history.append({"role": "user", "content": f"Message {i}"})
            history.append({"role": "model", "content": f"Response {i}"})
        
        response = client.post(
            "/chat",
            data={
                "message": "Final message",
                "history": json.dumps(history),
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 200
        
        print("✅ Long conversation history handled successfully")
    
    def test_response_time_performance(self, mock_genai):
        """Test that chat responds within acceptable time."""
        start_time = time.time()
        
        response = client.post(
            "/chat",
            data={
                "message": "Performance test",
                "user_id": "test_user_123"
            }
        )
        
        duration = time.time() - start_time
        
        assert response.status_code == 200
        # Should respond within 3 seconds (with mocked API)
        assert duration < 3.0, f"Response took too long: {duration}s"
        
        print(f"✅ Response time: {duration:.2f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
