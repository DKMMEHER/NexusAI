import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, Mock
from fastapi import UploadFile
from io import BytesIO
import os
import sys

# Ensure we can import modules from the project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from ImageGeneration.backend import app
from auth import verify_token

client = TestClient(app)

# Mock the verify_token dependency correctly
def mock_verify_token():
    return "test_user_id"

# Override the dependency at the app level
app.dependency_overrides[verify_token] = mock_verify_token

@pytest.fixture
def mock_external_services():
    """Mocks the external API calls and database/storage operations."""
    with patch("ImageGeneration.backend.call_nano_banana") as mock_call, \
         patch("ImageGeneration.backend.db") as mock_db, \
         patch("ImageGeneration.backend.storage") as mock_storage:
        
        # Setup successful response for call_nano_banana
        # Returns: img_b64, mime, error, status, tokens
        mock_call.return_value = ("fake_base64_image_data", "image/png", None, 200, 100)
        
        # Setup storage mock
        mock_storage.save_image.return_value = "generated_images/test_job_id.png"
        
        yield mock_call, mock_db, mock_storage


# ========== HEALTH CHECK TESTS ==========

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ImageGeneration"}


# ========== IMAGE GENERATION TESTS ==========

def test_generate_image_success(mock_external_services):
    """Test successful image generation."""
    mock_call, mock_db, mock_storage = mock_external_services
    
    response = client.post(
        "/image/generate",
        data={
            "prompt": "A futuristic city",
            "model": "gemini-2.5-flash-image",
            "user_id": "test_user_id",
            "api_key": "fake_api_key"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "image" in data
    assert data["image"] == "fake_base64_image_data"
    assert data["mime"] == "image/png"
    
    # Verify mocks were called
    mock_call.assert_called_once()
    mock_db.save_job.assert_called_once()
    mock_storage.save_image.assert_called_once()


def test_generate_image_no_auth():
    """Test behavior when API key is missing."""
    with patch.dict(os.environ, {}, clear=True):
        response = client.post(
            "/image/generate",
            data={
                "prompt": "Test prompt",
            }
        )
        # Expect 401 because api_key is required
        assert response.status_code == 401


def test_generate_image_api_failure(mock_external_services):
    """Test handling of external API failure."""
    mock_call, mock_db, mock_storage = mock_external_services
    
    # Simulate API error
    mock_call.return_value = (None, None, "API Error", 500, 0)
    
    response = client.post(
        "/image/generate",
        data={
            "prompt": "Crash test",
            "user_id": "test_user_id",
            "api_key": "fake_key"
        }
    )
    
    assert response.status_code == 500
    assert response.json()["detail"] == "API Error"
    
    # Database and storage should NOT be called on failure
    mock_db.save_job.assert_not_called()
    mock_storage.save_image.assert_not_called()


def test_generate_image_with_aspect_ratio_16_9(mock_external_services):
    """Test image generation with custom aspect ratio 16:9."""
    mock_call, mock_db, mock_storage = mock_external_services
    
    response = client.post(
        "/image/generate",
        data={
            "prompt": "A landscape photo",
            "model": "gemini-2.5-flash-image",
            "user_id": "test_user_id",
            "api_key": "fake_api_key",
            "aspect_ratio": "16:9"
        }
    )
    
    assert response.status_code == 200
    # Verify that aspect_ratio was passed to call_nano_banana
    mock_call.assert_called_once()
    call_args = mock_call.call_args
    assert call_args.kwargs.get("aspect_ratio") == "16:9"


def test_generate_image_square_aspect_ratio_1_1(mock_external_services):
    """Test image generation with 1:1 aspect ratio."""
    mock_call, mock_db, mock_storage = mock_external_services
    
    response = client.post(
        "/image/generate",
        data={
            "prompt": "A square portrait",
            "model": "gemini-2.5-flash-image",
            "user_id": "test_user_id",
            "api_key": "fake_api_key",
            "aspect_ratio": "1:1"
        }
    )
    
    assert response.status_code == 200
    mock_call.assert_called_once()
    call_args = mock_call.call_args
    assert call_args.kwargs.get("aspect_ratio") == "1:1"



def test_generate_image_safety_blocked(mock_external_services):
    """Test handling when image generation is blocked by safety filters."""
    mock_call, mock_db, mock_storage = mock_external_services
    
    # Simulate safety block
    mock_call.return_value = (None, None, "The image generation was blocked by safety settings. Please try a different prompt.", 400, 0)
    
    response = client.post(
        "/image/generate",
        data={
            "prompt": "Inappropriate content",
            "user_id": "test_user_id",
            "api_key": "fake_key"
        }
    )
    
    assert response.status_code == 400
    assert "safety" in response.json()["detail"].lower()


# ========== IMAGE EDITING TESTS ==========

def test_edit_image_success(mock_external_services):
    """Test successful image editing."""
    mock_call, mock_db, mock_storage = mock_external_services
    
    # Create a fake image file
    fake_image = BytesIO(b"fake image data")
    
    response = client.post(
        "/image/edit",
        data={
            "prompt": "Make it blue",
            "api_key": "fake_api_key",
            "model": "gemini-2.5-flash-image"
        },
        files={"file": ("test.png", fake_image, "image/png")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "image" in data
    assert data["image"] == "fake_base64_image_data"


# ========== VIRTUAL TRY-ON TESTS ==========

def test_virtual_try_on_success(mock_external_services):
    """Test successful virtual try-on."""
    mock_call, mock_db, mock_storage = mock_external_services
    
    product_image = BytesIO(b"fake product image")
    person_image = BytesIO(b"fake person image")
    
    response = client.post(
        "/image/virtual_try_on",
        data={
            "prompt": "Try on this shirt",
            "api_key": "fake_api_key",
            "user_id": "test_user_id"
        },
        files={
            "product": ("product.png", product_image, "image/png"),
            "person": ("person.png", person_image, "image/png")
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "image" in data


# ========== AD CREATION TESTS ==========

def test_create_ads_multiple_variations(mock_external_services):
    """Test creating multiple ad variations."""
    mock_call, mock_db, mock_storage = mock_external_services
    
    model_image = BytesIO(b"fake model image")
    product_image = BytesIO(b"fake product image")
    
    response = client.post(
        "/image/create_ads",
        data={
            "prompt": "Fashion ad",
            "variations": "3",
            "api_key": "fake_api_key",
            "user_id": "test_user_id"
        },
        files={
            "model_image": ("model.png", model_image, "image/png"),
            "product": ("product.png", product_image, "image/png")
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 3


# ========== MERGE IMAGES TESTS ==========

def test_merge_images_success(mock_external_services):
    """Test successful image merging."""
    mock_call, mock_db, mock_storage = mock_external_services
    
    image1 = BytesIO(b"fake image 1")
    image2 = BytesIO(b"fake image 2")
    
    response = client.post(
        "/image/merge_images",
        data={
            "prompt": "Merge these",
            "api_key": "fake_api_key",
            "user_id": "test_user_id"
        },
        files=[
            ("files", ("img1.png", image1, "image/png")),
            ("files", ("img2.png", image2, "image/png"))
        ]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "image" in data
    assert data["image"] == "fake_base64_image_data"


# ========== SCENE GENERATION TESTS ==========

def test_generate_scenes_success(mock_external_services):
    """Test successful scene generation from an input image."""
    mock_call, mock_db, mock_storage = mock_external_services
    
    scene_image = BytesIO(b"fake scene image")
    
    response = client.post(
        "/image/generate_scenes",
        data={
            "prompt": "Cyberpunk style",
            "api_key": "fake_api_key",
            "user_id": "test_user_id"
        },
        files={
            "scene": ("scene.png", scene_image, "image/png")
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Expect 3 variations by default
    assert "results" in data
    assert len(data["results"]) == 3
    assert data["results"][0]["image"] == "fake_base64_image_data"


# ========== IMAGE RESTORATION TESTS ==========

def test_restore_old_image_success(mock_external_services):
    """Test successful image restoration."""
    mock_call, mock_db, mock_storage = mock_external_services
    
    old_image = BytesIO(b"fake old image")
    
    response = client.post(
        "/image/restore_old_image",
        data={
            "api_key": "fake_api_key",
            "user_id": "test_user_id"
        },
        files={"file": ("old.png", old_image, "image/png")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "image" in data
