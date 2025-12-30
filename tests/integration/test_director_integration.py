"""
Integration Tests for Director Service
Tests the full video creation workflow including:
- Script generation
- Scene approval
- Video production orchestration
- Stitching
- Database and storage integration
"""
import pytest
import os
import sys
import json
import time
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi.testclient import TestClient
from Director.backend import app
from Director.models import MovieJob, Scene, ScenePrompt
from auth import verify_token

# Override auth for integration tests
def override_verify_token():
    return "test_user_123"

app.dependency_overrides[verify_token] = override_verify_token

client = TestClient(app)


@pytest.fixture
def mock_genai():
    """Mock Gemini API for script generation."""
    with patch("Director.backend.genai") as mock:
        mock_model = MagicMock()
        mock_response = MagicMock()
        
        # Mock script generation response
        fake_script = [
            {
                "id": 1,
                "scene_heading": "EXT. SPACE - DAY",
                "prompt": {
                    "scene_description": "A spaceship flying through stars",
                    "visual_details": {
                        "environment": "Deep space with stars",
                        "character": "Sleek silver spaceship",
                        "props": "Asteroids in background"
                    },
                    "camera_direction": {
                        "movement": "Dolly forward",
                        "framing": "Wide shot",
                        "focus": "Sharp on ship",
                        "lens": "35mm"
                    },
                    "motion_and_actions": {
                        "character_action": "Flying forward",
                        "environment_motion": "Stars moving past"
                    },
                    "audio_design": {
                        "music": {"enabled": True, "style": "Epic", "intensity": "High"},
                        "ambient_sfx": {"wind": "None", "environment": "Space ambience", "footsteps": "None"},
                        "voiceover": {"enabled": True, "script": "Journey to the stars", "tone": "Epic", "lip_sync": "DISABLED"}
                    },
                    "language_preferences": {
                        "narration_language": "English",
                        "subtitle_language": "English",
                        "tone": "Epic"
                    },
                    "style": {
                        "cinematic_style": "Sci-Fi",
                        "color_grade": "Cool tones",
                        "quality": "High"
                    },
                    "technical_preferences": {
                        "frame_rate": "24fps",
                        "resolution": "1080p",
                        "stabilization": "High"
                    }
                },
                "visual_prompt": "A sleek silver spaceship flying through deep space",
                "duration": 8
            }
        ]
        
        mock_response.text = f"```json\n{json.dumps(fake_script)}\n```"
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock.GenerativeModel.return_value = mock_model
        
        yield mock


@pytest.fixture
def mock_video_service():
    """Mock the Video Generation service."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        # Mock video generation response
        mock_gen_response = MagicMock()
        mock_gen_response.json.return_value = {"operation_name": "test_operation_123"}
        mock_gen_response.raise_for_status = MagicMock()
        mock_instance.post = AsyncMock(return_value=mock_gen_response)
        
        # Mock status polling response
        mock_status_response = MagicMock()
        mock_status_response.json.return_value = {"state": "succeeded", "status": "COMPLETE"}
        mock_instance.get = AsyncMock(return_value=mock_status_response)
        
        yield mock_instance


@pytest.fixture
def mock_storage():
    """Mock storage operations."""
    with patch("Director.backend.storage") as mock:
        mock.save_video.return_value = "test_video_path.mp4"
        yield mock


class TestDirectorIntegration:
    """Integration tests for Director service."""
    
    def test_health_endpoint(self):
        """Test that the health endpoint is accessible."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_create_movie_new_job(self):
        """Test creating a new movie job (script generation flow)."""
        response = client.post(
            "/create_movie",
            json={
                "topic": "Space Adventure",
                "duration_seconds": 8,
                "user_id": "test_user_123",
                "model": "veo-3.1",
                "resolution": "1080p"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "job_id" in data
        assert data["status"] == "queued"
        
        print(f"✅ Movie job created: {data['job_id']}")
    
    def test_create_movie_with_existing_scenes(self):
        """Test creating a movie with pre-defined scenes (retake/edit flow)."""
        scenes = [
            {
                "id": 1,
                "scene_heading": "EXT. BEACH - DAY",
                "visual_prompt": "A beautiful beach scene",
                "duration": 8,
                "status": "pending",
                "prompt": {
                    "scene_description": "Beach scene",
                    "visual_details": {
                        "environment": "Sandy beach",
                        "character": "Person walking",
                        "props": "Palm trees"
                    },
                    "camera_direction": {
                        "movement": "Static",
                        "framing": "Wide",
                        "focus": "Sharp",
                        "lens": "50mm"
                    },
                    "motion_and_actions": {
                        "character_action": "Walking",
                        "environment_motion": "Waves"
                    },
                    "audio_design": {
                        "music": {"enabled": True, "style": "Relaxing", "intensity": "Low"},
                        "ambient_sfx": {"wind": "Gentle", "environment": "Ocean waves", "footsteps": "Sand"},
                        "voiceover": {"enabled": True, "script": "Peace and tranquility", "tone": "Calm", "lip_sync": "DISABLED"}
                    },
                    "language_preferences": {
                        "narration_language": "English",
                        "subtitle_language": "English",
                        "tone": "Calm"
                    },
                    "style": {
                        "cinematic_style": "Documentary",
                        "color_grade": "Warm",
                        "quality": "High"
                    },
                    "technical_preferences": {
                        "frame_rate": "24fps",
                        "resolution": "1080p",
                        "stabilization": "High"
                    }
                }
            }
        ]
        
        response = client.post(
            "/create_movie",
            json={
                "topic": "Beach Relaxation",
                "duration_seconds": 8,
                "user_id": "test_user_123",
                "scenes": scenes
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "job_id" in data
        assert data["status"] == "production_started"
        
        print(f"✅ Movie with existing scenes created: {data['job_id']}")
    
    def test_script_generation_workflow(self, mock_genai):
        """Test the script generation workflow."""
        with patch("Director.backend.db") as mock_db:
            # Mock job object
            mock_job = MagicMock()
            mock_job.scenes = []
            mock_db.get_job.return_value = mock_job
            
            # Import and run the async function
            from Director.backend import generate_script
            
            asyncio.run(generate_script(
                job_id="test_job_123",
                topic="Space Exploration",
                duration_seconds=8,
                resolution="1080p"
            ))
            
            # Verify script was generated
            assert len(mock_job.scenes) > 0
            assert mock_job.scenes[0].id == 1
            
            # Verify database save was called
            mock_db.save_job.assert_called_with(mock_job)
            
            print("✅ Script generation workflow works correctly")
    
    def test_approve_script_endpoint(self):
        """Test the script approval endpoint."""
        with patch("Director.backend.db") as mock_db:
            mock_job = MagicMock()
            mock_job.status = "waiting_for_approval"
            mock_db.get_job.return_value = mock_job
            
            response = client.post(
                "/approve_script/test_job_123",
                json={"scenes": []}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "production_started"
            
            # Verify job status was updated to filming
            # Note: In the actual flow, production_loop may complete immediately
            assert mock_job.status in ["filming", "completed"]
            
            print("✅ Script approval works correctly")
    
    def test_approve_script_not_found(self):
        """Test script approval for non-existent job."""
        with patch("Director.backend.db") as mock_db:
            mock_db.get_job.return_value = None
            
            response = client.post(
                "/approve_script/nonexistent_job",
                json={}
            )
            
            assert response.status_code == 404
    
    def test_get_movie_status(self):
        """Test getting movie status."""
        with patch("Director.backend.db") as mock_db:
            mock_job = MagicMock()
            mock_job.job_id = "test_job_123"
            mock_job.status = "filming"
            mock_job.progress = 50
            mock_job.scenes = []
            mock_db.get_job.return_value = mock_job
            
            response = client.get("/movie_status/test_job_123")
            
            assert response.status_code == 200
            # Response should be the job object
    
    def test_get_user_jobs(self):
        """Test getting all jobs for a user."""
        with patch("Director.backend.db") as mock_db:
            mock_jobs = [
                {"job_id": "job1", "topic": "Test 1"},
                {"job_id": "job2", "topic": "Test 2"}
            ]
            mock_db.get_user_jobs.return_value = mock_jobs
            
            response = client.get("/my_jobs/test_user_123")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            
            print("✅ User jobs retrieval works correctly")
    
    def test_save_external_job(self):
        """Test saving an external job (from TextToVideo service)."""
        with patch("Director.backend.db") as mock_db:
            external_job = {
                "job_id": "external_123",
                "type": "text_to_video",
                "topic": "External video",
                "status": "completed",
                "progress": 100,
                "scenes": [],
                "created_at": "2025-01-01T00:00:00",
                "model": "veo-3.1",
                "resolution": "1080p",
                "aspect_ratio": "16:9"
            }
            
            response = client.post(
                "/save_external_job",
                json=external_job
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "saved"
            
            # Verify database save was called
            mock_db.save_job.assert_called_once()
            
            print("✅ External job saving works correctly")
    
    def test_database_integration(self):
        """Test database operations throughout the workflow."""
        # Don't mock the database for this test - let it use the real JsonDatabase
        response = client.post(
            "/create_movie",
            json={
                "topic": "Database Test",
                "duration_seconds": 8,
                "user_id": "test_user_123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify the response structure
        assert "job_id" in data
        assert "status" in data
        assert data["status"] == "queued"
        
        print("✅ Database integration works correctly")
    def test_error_handling_unauthorized_access(self):
        """Test that users can't access other users' jobs."""
        with patch("Director.backend.db") as mock_db:
            response = client.get("/my_jobs/different_user")
            
            # Should get 403 Forbidden
            assert response.status_code == 403
    
    def test_concurrent_movie_creation(self):
        """Test handling of multiple concurrent movie creation requests."""
        import concurrent.futures
        
        def create_movie(i):
            return client.post(
                "/create_movie",
                json={
                    "topic": f"Concurrent Movie {i}",
                    "duration_seconds": 8,
                    "user_id": "test_user_123"
                }
            )
        
        # Submit 3 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(create_movie, i) for i in range(3)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        for result in results:
            assert result.status_code == 200
        
        print("✅ Concurrent movie creation handled successfully")
    
    def test_response_time_performance(self):
        """Test that movie creation responds quickly."""
        start_time = time.time()
        
        response = client.post(
            "/create_movie",
            json={
                "topic": "Performance Test",
                "duration_seconds": 8,
                "user_id": "test_user_123"
            }
        )
        
        duration = time.time() - start_time
        
        assert response.status_code == 200
        # Should respond within 2 seconds (just creating the job)
        assert duration < 2.0, f"Response took too long: {duration}s"
        
        print(f"✅ Response time: {duration:.2f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
