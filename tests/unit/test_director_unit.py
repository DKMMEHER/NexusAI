import pytest
from unittest.mock import MagicMock, patch, AsyncMock, ANY
from fastapi.testclient import TestClient
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from Director.backend import app, generate_script

client = TestClient(app)

from auth import verify_token
def override_verify_token():
    return "u1"

app.dependency_overrides[verify_token] = override_verify_token

@pytest.fixture
def mock_genai():
    with patch("Director.backend.genai") as mock:
        yield mock

@pytest.fixture
def mock_db():
    with patch("Director.backend.db") as mock:
        yield mock

@pytest.fixture
def mock_background_tasks():
    with patch("fastapi.BackgroundTasks.add_task") as mock:
        yield mock

def test_create_movie_new_job_success(mock_db, mock_background_tasks):
    mock_db.save_job = MagicMock()
    
    payload = {
        "topic": "Space Adventure",
        "duration_seconds": 60,
        "user_id": "u1",
        "resolution": "1080p",
        "model": "veo-3.1"
    }
    
    response = client.post(
        "/create_movie",
        json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    
    # Verify DB save
    mock_db.save_job.assert_called()
    
    # Verify background task added (generate_script_task)
    mock_background_tasks.assert_called()
    # Arg 0 is the function, Arg 1 is job_id
    # We can check the name of the function passed to add_task
    task_func = mock_background_tasks.call_args[0][0]
    assert task_func.__name__ == "generate_script_task"

def test_create_movie_with_existing_scenes_success(mock_db, mock_background_tasks):
    # Simulate "Retake" or "Edit" flow
    payload = {
        "topic": "Space Adventure",
        "duration_seconds": 8,
        "user_id": "u1",
        "scenes": [
            {
                "id": 1,
                "scene_heading": "EXT. SPACE - DAY",
                "visual_prompt": "Scene 1 prompt",
                "duration": 4,
                "status": "pending",
                "prompt": { # Request model expects 'prompt' to be populated for regeneration/structure
                    "scene_description": "Desc",
                    "visual_details": {
                        "environment": "Env", 
                        "character": "Char",
                        "props": "None"
                    },
                    "camera_direction": {
                        "movement": "Static", 
                        "framing": "Wide", 
                        "focus": "Soft", 
                        "lens": "50mm"
                    },
                    "motion_and_actions": {
                        "character_action": "Walk", 
                        "environment_motion": "None"
                    },
                    "audio_design": {
                        "music": {"enabled": True, "style": "Epic", "intensity": "High"},
                        "ambient_sfx": {"wind": "None", "environment": "Space", "footsteps": "None"},
                        "voiceover": {"enabled": True, "script": "Hi", "tone": "Dramatic", "lip_sync": "DISABLED"}
                    },
                    "language_preferences": {
                        "narration_language": "English",
                        "subtitle_language": "English",
                        "tone": "Dramatic"
                    },
                    "style": {
                        "cinematic_style": "Cinematic", 
                        "color_grade": "Dark",
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
    }
    
    response = client.post(
        "/create_movie",
        json=payload
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "production_started"
    
    # Verify background task uses production_loop
    task_func = mock_background_tasks.call_args[0][0]
    assert task_func.__name__ == "production_loop"

def test_generate_script_logic(mock_genai, mock_db):
    # Test the core logic of generate_script parsing
    import asyncio
    
    job_id = "test_job"
    
    # Mock LLM response
    mock_model = MagicMock()
    mock_response = MagicMock()
    
    # Valid JSON response from LLM with all required fields
    fake_json = [
        {
            "id": 1, 
            "scene_heading": "INT. LAB", 
            "prompt": {
                "scene_description": "A scientist working in a lab",
                "visual_details": {
                    "environment": "Modern laboratory",
                    "character": "A scientist in a white coat",
                    "props": "Test tubes and equipment"
                }, 
                "camera_direction": {
                    "movement": "Static",
                    "framing": "Medium shot",
                    "focus": "Sharp",
                    "lens": "50mm"
                }, 
                "motion_and_actions": {
                    "character_action": "Working at desk",
                    "environment_motion": "None"
                }, 
                "audio_design": {
                    "music": {"enabled": True, "style": "Ambient", "intensity": "Low"},
                    "ambient_sfx": {"wind": "None", "environment": "Lab sounds", "footsteps": "None"},
                    "voiceover": {"enabled": True, "script": "Science in action", "tone": "Professional", "lip_sync": "DISABLED"}
                }, 
                "language_preferences": {
                    "narration_language": "English",
                    "subtitle_language": "English",
                    "tone": "Professional"
                }, 
                "style": {
                    "cinematic_style": "Documentary",
                    "color_grade": "Neutral",
                    "quality": "High"
                }, 
                "technical_preferences": {
                    "frame_rate": "24fps",
                    "resolution": "1080p",
                    "stabilization": "High"
                }
            },
            "visual_prompt": "A lab", 
            "duration": 4
        }
    ]
    mock_response.text = f"```json\n{json.dumps(fake_json)}\n```"
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)
    mock_genai.GenerativeModel.return_value = mock_model
    
    # Mock DB get_job to return object we can update
    # Note: update the db mock to actually be useful
    mock_job_obj = MagicMock()
    mock_job_obj.scenes = [] # Initially empty
    mock_db.get_job.return_value = mock_job_obj
    
    # Execute synchronously via asyncio.run
    asyncio.run(generate_script(job_id, "Science", 4, "1080p"))
    
    # Assert
    assert len(mock_job_obj.scenes) == 1
    mock_db.save_job.assert_called_with(mock_job_obj)
    assert mock_job_obj.scenes[0].id == 1

def test_approve_script(mock_db, mock_background_tasks):
    mock_job = MagicMock()
    mock_db.get_job.return_value = mock_job
    
    response = client.post(
        "/approve_script/job_123",
        json={"scenes": []} # approving as is
    )
    
    assert response.status_code == 200
    assert mock_job.status == "filming"
    mock_db.save_job.assert_called()
    
    # Starts production
    task_func = mock_background_tasks.call_args[0][0]
    assert task_func.__name__ == "production_loop"

def test_approve_script_not_found(mock_db):
    mock_db.get_job.return_value = None
    response = client.post("/approve_script/missing", json={})
    assert response.status_code == 404

def test_health_check_director():
    response = client.get("/health")
    assert response.status_code == 200
