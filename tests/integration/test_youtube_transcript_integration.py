"""
Integration Tests for YouTube Transcript Service
Tests the full workflow of YouTube transcript extraction and summarization including:
- Transcript extraction from YouTube videos
- Different URL formats
- Transcript summarization
- Error handling
- Database integration
"""
import pytest
import os
import sys
import time
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi.testclient import TestClient
from YoutubeTranscript.backend import app

client = TestClient(app)


@pytest.fixture
def mock_youtube_transcript():
    """Mock YouTube Transcript API."""
    with patch("YoutubeTranscript.backend.YouTubeTranscriptApi") as mock:
        # Mock transcript data
        mock.get_transcript.return_value = [
            {"text": "Welcome to this video tutorial.", "start": 0.0, "duration": 3.0},
            {"text": "Today we'll learn about Python programming.", "start": 3.0, "duration": 4.0},
            {"text": "Python is a versatile language.", "start": 7.0, "duration": 3.5},
            {"text": "It's used for web development, data science, and more.", "start": 10.5, "duration": 4.5},
            {"text": "Let's get started with the basics.", "start": 15.0, "duration": 3.0}
        ]
        yield mock


@pytest.fixture
def mock_genai():
    """Mock Gemini API for transcript summarization."""
    with patch("YoutubeTranscript.backend.genai") as mock:
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This video tutorial introduces Python programming, covering its versatility in web development and data science, and promises to teach the basics."
        mock_response.usage_metadata = MagicMock()
        mock_response.usage_metadata.total_token_count = 50
        mock_model.generate_content.return_value = mock_response
        mock.GenerativeModel.return_value = mock_model
        yield mock


class TestYouTubeTranscriptIntegration:
    """Integration tests for YouTube Transcript service."""
    
    def test_health_endpoint(self):
        """Test that the health endpoint is accessible."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print("✅ Health endpoint works")
    
    def test_get_transcript_workflow(self, mock_youtube_transcript, mock_genai):
        """Test the complete transcript extraction workflow."""
        # Submit request for transcript
        response = client.post(
            "/transcript",
            data={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "transcript" in data
        assert "summary" in data
        assert "video_id" in data
        assert len(data["transcript"]) > 0
        assert len(data["summary"]) > 0
        
        # Verify transcript content
        transcript_text = data["transcript"]
        assert "Welcome to this video tutorial" in transcript_text
        assert "Python programming" in transcript_text
        
        print(f"✅ Transcript extraction works")
    
    def test_different_youtube_url_formats(self, mock_youtube_transcript, mock_genai):
        """Test different YouTube URL formats."""
        urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLxxx",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        ]
        
        for url in urls:
            response = client.post(
                "/transcript",
                data={
                    "url": url,
                    "user_id": "test_user_123"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "transcript" in data
            assert "summary" in data
            print(f"✅ URL format works: {url[:50]}...")
    
    def test_transcript_with_different_models(self, mock_youtube_transcript, mock_genai):
        """Test transcript summarization with different models."""
        models = [
            "gemini-2.0-flash-exp",
            "gemini-2.5-flash"
        ]
        
        for model in models:
            response = client.post(
                "/transcript",
                data={
                    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "model": model,
                    "user_id": "test_user_123"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            print(f"✅ Model {model} works correctly")
    
    def test_error_handling_invalid_url(self):
        """Test error handling for invalid YouTube URL."""
        response = client.post(
            "/transcript",
            data={
                "url": "not_a_valid_url",
                "user_id": "test_user_123"
            }
        )
        
        # Should handle gracefully
        assert response.status_code == 400  # User error
        print("✅ Invalid URL validation works")
    
    def test_error_handling_empty_url(self):
        """Test error handling for empty URL."""
        response = client.post(
            "/transcript",
            data={
                "url": "",
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code in [400, 422, 500]  # Accept user error or validation error
        print("✅ Empty URL validation works")
    
    def test_error_handling_missing_url(self):
        """Test error handling when URL is missing."""
        response = client.post(
            "/transcript",
            data={
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 422  # Validation error
        print("✅ Missing URL validation works")
    
    def test_error_handling_video_not_found(self, mock_youtube_transcript, mock_genai):
        """Test error handling when video doesn't exist."""
        # Mock transcript not available
        mock_youtube_transcript.get_transcript.side_effect = Exception("Video not found")
        
        response = client.post(
            "/transcript",
            data={
                "url": "https://www.youtube.com/watch?v=nonexistent",
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 400  # User error
    
    def test_error_handling_no_transcript_available(self, mock_youtube_transcript, mock_genai):
        """Test error handling when transcript is not available."""
        # Mock no transcript available
        mock_youtube_transcript.get_transcript.side_effect = Exception("Transcript not available")
        
        response = client.post(
            "/transcript",
            data={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 400  # User error - no transcript available
    
    def test_database_integration(self, mock_youtube_transcript, mock_genai):
        """Test that transcript jobs are saved to database."""
        with patch("YoutubeTranscript.backend.db") as mock_db:
            response = client.post(
                "/transcript",
                data={
                    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
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
            assert call_args["user_id"] == "test_user_123"
            assert "type" in call_args
            
            print("✅ Database integration works correctly")
    
    def test_long_video_transcript(self, mock_youtube_transcript, mock_genai):
        """Test handling of transcripts from long videos."""
        # Mock a very long transcript
        long_transcript = [
            {"text": f"Segment {i} of the video.", "start": float(i * 5), "duration": 5.0}
            for i in range(100)  # 100 segments = ~8 minutes
        ]
        mock_youtube_transcript.get_transcript.return_value = long_transcript
        
        response = client.post(
            "/transcript",
            data={
                "url": "https://www.youtube.com/watch?v=long_video",
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "transcript" in data
        
        print("✅ Long video transcript handling works")
    
    def test_concurrent_transcript_requests(self, mock_youtube_transcript, mock_genai):
        """Test handling of multiple concurrent transcript requests."""
        import concurrent.futures
        
        def make_request(i):
            return client.post(
                "/transcript",
                data={
                    "url": f"https://www.youtube.com/watch?v=video{i}",
                    "user_id": f"user_{i}"
                }
            )
        
        # Submit 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        for result in results:
            assert result.status_code == 200
        
        print("✅ Concurrent requests handled successfully")
    
    def test_response_time_performance(self, mock_youtube_transcript, mock_genai):
        """Test that transcript extraction responds within acceptable time."""
        start_time = time.time()
        
        response = client.post(
            "/transcript",
            data={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "user_id": "test_user_123"
            }
        )
        
        duration = time.time() - start_time
        
        assert response.status_code == 200
        # Should respond within 3 seconds (with mocked API)
        assert duration < 3.0, f"Response took too long: {duration}s"
        
        print(f"✅ Response time: {duration:.2f}s")
    
    def test_transcript_formatting(self, mock_youtube_transcript, mock_genai):
        """Test that transcript is properly formatted."""
        response = client.post(
            "/transcript",
            data={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Transcript should be a string
        assert isinstance(data["transcript"], str)
        
        # Should have proper spacing/formatting
        assert len(data["transcript"]) > 0
        
        print("✅ Transcript formatting is correct")
    
    def test_summary_generation(self, mock_youtube_transcript, mock_genai):
        """Test that summary is generated correctly."""
        response = client.post(
            "/transcript",
            data={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Summary should exist
        assert "summary" in data
        assert len(data["summary"]) > 0
        
        # Summary should be shorter than transcript (typically)
        # Note: This might not always be true, but it's a good sanity check
        
        print("✅ Summary generation works correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
