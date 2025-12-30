"""
Integration Tests for Image Generation Service
Tests the full workflow of image generation including:
- API endpoint connectivity
- Request/response handling
- Database integration
- File storage
- Error handling
"""
import pytest
import os
import sys
import time
import base64
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi.testclient import TestClient
from ImageGeneration.backend import app
from auth import verify_token

# Override auth for integration tests
def override_verify_token():
    return "test_user_123"

app.dependency_overrides[verify_token] = override_verify_token

client = TestClient(app)


@pytest.fixture
def mock_imagen():
    """Mock the HTTP requests to Gemini API to avoid real API calls during integration tests."""
    with patch("ImageGeneration.backend.requests.post") as mock:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "inlineData": {
                            "data": base64.b64encode(b"fake_image_data_12345").decode('utf-8'),
                            "mimeType": "image/png"
                        }
                    }]
                }
            }],
            "usageMetadata": {
                "totalTokenCount": 100
            }
        }
        mock.return_value = mock_response
        yield mock


@pytest.fixture
def cleanup_test_images():
    """Clean up test images after tests."""
    yield
    # Cleanup logic if needed
    test_image_dir = "Generated_Images"
    if os.path.exists(test_image_dir):
        for file in os.listdir(test_image_dir):
            if file.startswith("test_"):
                try:
                    os.remove(os.path.join(test_image_dir, file))
                except:
                    pass


class TestImageGenerationIntegration:
    """Integration tests for Image Generation service."""
    
    def test_health_endpoint(self):
        """Test that the health endpoint is accessible."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_generate_image_full_workflow(self, mock_imagen, cleanup_test_images):
        """Test the complete image generation workflow."""
        # Step 1: Submit image generation request
        response = client.post(
            "/image/generate",
            data={
                "prompt": "A beautiful sunset over mountains",
                "model": "imagen-3.0-generate-001",
                "aspect_ratio": "1:1",
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Step 2: Verify response structure
        assert "image" in data
        assert "mime" in data
        
        # Step 3: Verify image data is base64 encoded
        try:
            decoded = base64.b64decode(data["image"])
            assert len(decoded) > 0
        except Exception as e:
            pytest.fail(f"Image data is not valid base64: {e}")
        
        print(f"✅ Image generated successfully")
    
    def test_generate_image_with_different_models(self, mock_imagen):
        """Test image generation with different model options."""
        models = [
            "imagen-3.0-generate-001",
            "imagen-3.0-fast-generate-001"
        ]
        
        for model in models:
            response = client.post(
                "/image/generate",
                data={
                    "prompt": f"Test image for {model}",
                    "model": model,
                    "user_id": "test_user_123"
                }
            )
            
            assert response.status_code == 200, f"Failed for model: {model}"
            data = response.json()
            assert "image" in data
            print(f"✅ Model {model} works correctly")
    
    def test_generate_image_with_different_aspect_ratios(self, mock_imagen):
        """Test image generation with different aspect ratios."""
        aspect_ratios = ["1:1", "16:9", "9:16", "4:3", "3:4"]
        
        for ratio in aspect_ratios:
            response = client.post(
                "/image/generate",
                data={
                    "prompt": f"Test image with {ratio} aspect ratio",
                    "aspect_ratio": ratio,
                    "user_id": "test_user_123"
                }
            )
            
            assert response.status_code == 200, f"Failed for aspect ratio: {ratio}"
            print(f"✅ Aspect ratio {ratio} works correctly")
    
    def test_generate_image_with_safety_settings(self, mock_imagen):
        """Test image generation with different safety filter levels."""
        safety_levels = ["block_some", "block_few", "block_fewest"]
        
        for level in safety_levels:
            response = client.post(
                "/image/generate",
                data={
                    "prompt": "A peaceful landscape",
                    "safety_filter_level": level,
                    "user_id": "test_user_123"
                }
            )
            
            assert response.status_code == 200, f"Failed for safety level: {level}"
            print(f"✅ Safety level {level} works correctly")
    
    def test_error_handling_missing_prompt(self):
        """Test error handling when prompt is missing."""
        response = client.post(
            "/image/generate",
            data={
                "model": "imagen-3.0-generate-001",
                "user_id": "test_user_123"
                # Missing prompt
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_error_handling_empty_prompt(self):
        """Test error handling when prompt is empty."""
        response = client.post(
            "/image/generate",
            data={
                "prompt": "",
                "user_id": "test_user_123"
            }
        )
        
        # Should either reject or handle gracefully
        assert response.status_code in [400, 422, 500]
    
    def test_concurrent_requests(self, mock_imagen):
        """Test handling of multiple concurrent requests."""
        import concurrent.futures
        
        def make_request(i):
            return client.post(
                "/image/generate",
                data={
                    "prompt": f"Concurrent test image {i}",
                    "user_id": "test_user_123"
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
    
    def test_database_integration(self, mock_imagen):
        """Test that image generation jobs are saved to database."""
        with patch("ImageGeneration.backend.db") as mock_db:
            response = client.post(
                "/image/generate",
                data={
                    "prompt": "Database integration test",
                    "user_id": "test_user_123"
                }
            )
            
            assert response.status_code == 200
            
            # Verify database save was called
            mock_db.save_job.assert_called_once()
            
            # Verify the saved data structure (it's an ImageJob object)
            saved_job = mock_db.save_job.call_args[0][0]
            assert hasattr(saved_job, 'job_id')
            assert hasattr(saved_job, 'user_id')
            assert saved_job.user_id == "test_user_123"
            
            print("✅ Database integration works correctly")
    
    def test_response_time_performance(self, mock_imagen):
        """Test that image generation responds within acceptable time."""
        start_time = time.time()
        
        response = client.post(
            "/image/generate",
            data={
                "prompt": "Performance test image",
                "user_id": "test_user_123"
            }
        )
        
        duration = time.time() - start_time
        
        assert response.status_code == 200
        # Should respond within 5 seconds (with mocked API)
        assert duration < 5.0, f"Response took too long: {duration}s"
        
        print(f"✅ Response time: {duration:.2f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
