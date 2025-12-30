"""
Integration Tests for Video Generation Service
Tests the full workflow of video generation including:
- Text-to-video generation
- Image-to-video generation
- Video extension
- Status polling
- Different models and parameters
"""
import pytest
import os
import sys
import time
from unittest.mock import patch, MagicMock, AsyncMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi.testclient import TestClient
from VideoGeneration.backend import app

client = TestClient(app)


@pytest.fixture
def mock_veo():
    """Mock the Veo helper functions for video generation."""
    with patch("VideoGeneration.backend.generate_text_to_video") as mock_text_to_video, \
         patch("VideoGeneration.backend.generate_image_to_video") as mock_image_to_video, \
         patch("VideoGeneration.backend.extend_veo_video") as mock_extend, \
         patch("VideoGeneration.backend.get_operation_status") as mock_status, \
         patch("VideoGeneration.backend.download_video_bytes") as mock_download, \
         patch("VideoGeneration.backend.get_video_object_from_operation") as mock_get_video:
        
        # Mock text-to-video response
        mock_text_to_video.return_value = {
            "operation_name": "projects/test/locations/us-central1/operations/12345"
        }
        
        # Mock image-to-video response
        mock_image_to_video.return_value = {
            "operation_name": "projects/test/locations/us-central1/operations/67890"
        }
        
        # Mock extend video response
        mock_extend.return_value = {
            "operation_name": "projects/test/locations/us-central1/operations/extend123"
        }
        
        # Mock status check response
        mock_status.return_value = {
            "state": "SUCCEEDED",
            "done": True
        }
        
        # Mock download response
        mock_download.return_value = (b"fake_video_data", "test_video.mp4")
        
        # Mock get video object
        mock_get_video.return_value = MagicMock()
        
        yield {
            "text_to_video": mock_text_to_video,
            "image_to_video": mock_image_to_video,
            "extend": mock_extend,
            "status": mock_status,
            "download": mock_download,
            "get_video": mock_get_video
        }


@pytest.fixture
def mock_storage():
    """Mock storage operations."""
    with patch("VideoGeneration.backend.storage") as mock:
        mock.save_video.return_value = "test_video_path.mp4"
        yield mock


class TestVideoGenerationIntegration:
    """Integration tests for Video Generation service."""
    
    def test_health_endpoint(self):
        """Test that the health endpoint is accessible."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print("✅ Health endpoint works")
    
    def test_text_to_video_workflow(self, mock_veo):
        """Test the complete text-to-video generation workflow."""
        # Step 1: Submit video generation request
        response = client.post(
            "/text_to_video",
            data={
                "prompt": "A cat playing with a ball of yarn",
                "model": "veo-3.1",
                "duration_seconds": 8,
                "resolution": "1080p"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Step 2: Verify response structure
        assert "operation_name" in data
        assert len(data["operation_name"]) > 0
        
        operation_name = data["operation_name"]
        print(f"✅ Text-to-video initiated: {operation_name}")
        
        # Step 3: Verify the helper function was called
        mock_veo["text_to_video"].assert_called_once()
    
    def test_text_to_video_with_different_models(self, mock_veo):
        """Test video generation with different Veo models."""
        models = [
            "veo-3.1",
            "veo-3.1-fast-generate-preview"
        ]
        
        for model in models:
            response = client.post(
                "/text_to_video",
                data={
                    "prompt": f"Test video for {model}",
                    "model": model,
                    "duration_seconds": 8
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "operation_name" in data
            print(f"✅ Model {model} works correctly")
    
    def test_text_to_video_with_different_durations(self, mock_veo):
        """Test video generation with different durations."""
        durations = [4, 8]
        
        for duration in durations:
            response = client.post(
                "/text_to_video",
                data={
                    "prompt": f"Test video {duration} seconds",
                    "duration_seconds": duration
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "operation_name" in data
            print(f"✅ Duration {duration}s works correctly")
    
    def test_text_to_video_with_different_resolutions(self, mock_veo):
        """Test video generation with different resolutions."""
        resolutions = ["720p", "1080p"]
        
        for resolution in resolutions:
            response = client.post(
                "/text_to_video",
                data={
                    "prompt": f"Test video at {resolution}",
                    "resolution": resolution
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "operation_name" in data
            print(f"✅ Resolution {resolution} works correctly")
    
    def test_text_to_video_with_different_aspect_ratios(self, mock_veo):
        """Test video generation with different aspect ratios."""
        aspect_ratios = ["16:9", "9:16", "1:1"]
        
        for ratio in aspect_ratios:
            response = client.post(
                "/text_to_video",
                data={
                    "prompt": f"Test video {ratio}",
                    "aspect_ratio": ratio
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "operation_name" in data
            print(f"✅ Aspect ratio {ratio} works correctly")
    
    def test_image_to_video_workflow(self, mock_veo):
        """Test image-to-video generation workflow."""
        import io
        
        # Create a fake image file
        fake_image = io.BytesIO(b"fake_image_data")
        
        response = client.post(
            "/image_to_video",
            files={"image": ("test.jpg", fake_image, "image/jpeg")},
            data={
                "prompt": "Make this image come to life",
                "duration_seconds": 8
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "operation_name" in data
        print("✅ Image-to-video workflow works")
    
    def test_video_extension_workflow(self, mock_veo):
        """Test video extension from previous operation."""
        response = client.post(
            "/extend_veo_video",
            data={
                "prompt": "Continue the scene",
                "previous_operation_name": "projects/test/locations/us-central1/operations/12345",
                "duration_seconds": 8
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "operation_name" in data
        print("✅ Video extension workflow works")
    
    def test_status_check_workflow(self, mock_veo):
        """Test checking video generation status."""
        operation_name = "projects/test/locations/us-central1/operations/12345"
        
        response = client.get(f"/status/{operation_name}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have state or status field
        assert "state" in data or "status" in data or "done" in data
        print("✅ Status check works correctly")
    
    def test_save_local_workflow(self, mock_veo, mock_storage):
        """Test saving video locally from GCS."""
        operation_name = "projects/test/locations/us-central1/operations/12345"
        
        with patch("VideoGeneration.backend.os.makedirs"):
            with patch("builtins.open", create=True) as mock_open:
                response = client.get(f"/save_local/{operation_name}")
                
                assert response.status_code == 200
                data = response.json()
                assert "file_path" in data
                print("✅ Save local workflow works")
    
    def test_error_handling_missing_prompt(self):
        """Test error handling when prompt is missing."""
        response = client.post(
            "/text_to_video",
            data={
                "duration_seconds": 8
                # Missing prompt
            }
        )
        
        assert response.status_code == 422  # Validation error
        print("✅ Missing prompt validation works")
    
    def test_error_handling_empty_prompt(self):
        """Test error handling when prompt is empty."""
        response = client.post(
            "/text_to_video",
            data={
                "prompt": "",
                "duration_seconds": 8
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 422, 500]
        print("✅ Empty prompt validation works")
    
    def test_error_handling_invalid_duration(self):
        """Test error handling for invalid duration."""
        response = client.post(
            "/text_to_video",
            data={
                "prompt": "Test video",
                "duration_seconds": 100  # Invalid duration
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 422, 500]
    
    def test_error_handling_invalid_operation_name(self, mock_veo):
        """Test error handling for invalid operation name."""
        # Mock an error response
        mock_veo["status"].side_effect = Exception("Operation not found")
        
        response = client.get("/status/invalid_operation")
        
        assert response.status_code == 500
    
    def test_concurrent_video_requests(self, mock_veo):
        """Test handling of multiple concurrent video generation requests."""
        import concurrent.futures
        
        def make_request(i):
            return client.post(
                "/text_to_video",
                data={
                    "prompt": f"Concurrent video {i}",
                    "duration_seconds": 8
                }
            )
        
        # Submit 3 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request, i) for i in range(3)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        for result in results:
            assert result.status_code == 200
        
        print("✅ Concurrent requests handled successfully")
    
    def test_response_time_performance(self, mock_veo):
        """Test that video generation request responds quickly."""
        start_time = time.time()
        
        response = client.post(
            "/text_to_video",
            data={
                "prompt": "Performance test video",
                "duration_seconds": 8
            }
        )
        
        duration = time.time() - start_time
        
        assert response.status_code == 200
        # Should respond within 3 seconds (just submitting the request)
        assert duration < 3.0, f"Response took too long: {duration}s"
        
        print(f"✅ Response time: {duration:.2f}s")
    
    def test_status_polling_performance(self, mock_veo):
        """Test that status polling responds quickly."""
        start_time = time.time()
        
        response = client.get("/status/projects/test/locations/us-central1/operations/12345")
        
        duration = time.time() - start_time
        
        assert response.status_code == 200
        # Should respond within 2 seconds
        assert duration < 2.0, f"Status check took too long: {duration}s"
        
        print(f"✅ Status check time: {duration:.2f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
