import base64
import os
import time
import requests
import json
import uuid
import logging
import sys
import random
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from auth import verify_token

from dotenv import load_dotenv
load_dotenv() # Load from .env in CWD

# Use relative import for prompts to work when imported from parent directory
try:
    from .prompts import PROMPTS
except ImportError:
    from prompts import PROMPTS

# === Configuration ===
IMAGES_DIR = "Generated_Images"
DB_FILE = "images.json"
API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# Ensure images directory exists
os.makedirs(IMAGES_DIR, exist_ok=True)

# === Logging Setup ===
logger = logging.getLogger("backend.image")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)

print("DEBUG: ImageGeneration backend module loaded", flush=True)

# === Database & Models ===

# === Database & Models ===
# Imports from local modules
from .database import ImageJob, JsonDatabase, FirestoreDatabase
from .storage import LocalStorage, GoogleCloudStorage

# Database Selection Logic
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
is_cloud_run = os.getenv("K_SERVICE") is not None

if is_cloud_run and project_id:
    logger.info(f"Detected Cloud Run environment. Using Firestore (Project: {project_id}).")
    try:
        db = FirestoreDatabase(project_id)
    except Exception as e:
        logger.error(f"Failed to initialize Firestore: {e}. Falling back to JsonDatabase.")
        db = JsonDatabase()

    # Cloud Storage Initialization
    bucket_name = os.getenv("GCS_BUCKET_NAME", "nexus-ai-media")
    try:
        storage = GoogleCloudStorage(bucket_name)
    except Exception as e:
        logger.error(f"Failed to initialize GCS: {e}. Falling back to LocalStorage.")
        storage = LocalStorage()
else:
    logger.info("Running locally. Using JsonDatabase and LocalStorage.")
    db = JsonDatabase()
    storage = LocalStorage()

# === Helper Functions ===

def get_api_key(api_key_input: str = None):
    key = api_key_input or os.getenv("GEMINI_API_KEY")
    if not key:
        raise HTTPException(status_code=401, detail="GEMINI_API_KEY not found in environment variables or request.")
    return key

def b64encode_file(file: UploadFile):
    data = file.file.read()
    mime = file.content_type or "image/png"
    return base64.b64encode(data).decode('utf-8'), mime

def call_nano_banana(api_key: str, prompt: str, images: List[dict] = None, model: str = "gemini-2.5-flash-image", grounding: bool = False, aspect_ratio: str = None, retries: int = 3, backoff: float = 1.5):
    # Construct URL based on model
    url = API_BASE_URL.format(model=model)
    
    parts = [{'text': prompt}]
    if images:
        for img in images:
            parts.append({'inlineData': {'data': img['data'], 'mimeType': img['mime']}})

    # Append Aspect Ratio to prompt if provided
    if aspect_ratio:
        parts[0]['text'] += f"\n\nAspect Ratio: {aspect_ratio}"

    payload = {'contents': [{'parts': parts}]}
    
    # Add Tools (Grounding) if requested and supported
    if grounding and "gemini-3-pro" in model:
        payload['tools'] = [{'google_search': {}}]
    
    generation_config = {}
    if generation_config:
        payload['generationConfig'] = generation_config

    attempt = 0
    while attempt <= retries:
        print(f"DEBUG: Sending request to: {url}", flush=True)
        res = requests.post(f"{url}?key={api_key}", json=payload, headers={"Content-Type": "application/json"})
        
        if res.status_code == 429:
            if attempt == retries:
                return None, None, "Quota exceeded. Please try again later.", res.status_code
            sleep_for = backoff ** attempt
            time.sleep(sleep_for)
            attempt += 1
            continue
        
        if res.status_code != 200:
            try:
                error_data = res.json()
                if "error" in error_data:
                    error_msg = error_data["error"].get("message", res.text)
                    status = error_data["error"].get("status", "UNKNOWN")
                    
                    if status == "INTERNAL" or "internal error" in error_msg.lower():
                        return None, None, "The AI service is temporarily unavailable. Please try again in a moment.", 500
                    if "safety" in error_msg.lower():
                        return None, None, "The request was blocked by safety filters. Please modify your prompt.", 400
                    return None, None, f"AI Error: {error_msg}", res.status_code
            except Exception:
                pass
            return None, None, f"Error {res.status_code}: {res.text}", res.status_code

        data = res.json()
        parts_out = data.get('candidates', [{}])[0].get('content', {}).get('parts', [])
        for p in parts_out:
            if 'inlineData' in p:
                return p['inlineData']['data'], p['inlineData'].get('mimeType', 'image/png'), None, 200
        
        logger.error(f"No image returned. Full response: {data}")
        candidate = data.get('candidates', [{}])[0]
        finish_reason = candidate.get('finishReason')
        if finish_reason == "SAFETY":
             return None, None, "The image generation was blocked by safety settings. Please try a different prompt.", 400
             
        return None, None, "No image returned. The model might have refused the request.", 500
    return None, None, "Exhausted retries", 500

# === FastAPI App Setup ===
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated images statically
# Only needed for LocalStorage
app.mount("/image/images", StaticFiles(directory=IMAGES_DIR), name="images")

router = APIRouter()

# === Endpoints ===

@router.get("/")
def health_check():
    return {"status": "Image Generation Service Running"}

@router.get("/health")
def health_check_explicit():
    return {"status": "healthy"}

@router.get("/my_images/{user_id}")
def get_my_images(user_id: str, token_uid: str = Depends(verify_token)):
    if token_uid != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to another user's images.")
    return db.get_user_jobs(user_id)

@router.post("/generate")
def generate_image(
    api_key: str = Form(None), 
    prompt: str = Form(...), 
    model: str = Form("gemini-2.5-flash-image"), 
    grounding: bool = Form(False), 
    aspect_ratio: str = Form(None),
    user_id: str = Form(None),
    token_uid: str = Depends(verify_token) # Injected by Dependency
):
    if user_id and user_id != "undefined" and token_uid != user_id:
         raise HTTPException(status_code=403, detail="User ID mismatch.")
    try:
        print(f"DEBUG: generate_image called with prompt='{prompt}' model='{model}' user_id='{user_id}'", flush=True)
        final_key = get_api_key(api_key)
            
        system_prompt = random.choice(PROMPTS["generate_image"])
        full_prompt = f"{system_prompt} {prompt}"
        img_b64, mime, error, status = call_nano_banana(final_key, full_prompt, model=model, grounding=grounding, aspect_ratio=aspect_ratio)
        
        if img_b64:
            # Persistence Logic
            try:
                if user_id and user_id != "undefined":
                    job_id = str(uuid.uuid4())
                    
                    # Use Storage Provider (Local or GCS)
                    web_path = storage.save_image(img_b64, job_id)
                    
                    if web_path:
                        job = ImageJob(
                            job_id=job_id,
                            user_id=user_id,
                            type="generate",
                            prompt=prompt,
                            image_path=web_path,
                            timestamp=datetime.now().isoformat(),
                            model=model
                        )
                        db.save_job(job)
            except Exception as e:
                print(f"ERROR: Failed to save image job: {e}", flush=True)
                import traceback
                traceback.print_exc()
                # Do not fail the request if persistence fails, just log it.

            return JSONResponse({"image": img_b64, "mime": mime})
        return JSONResponse({"detail": error}, status_code=status)
    except HTTPException:
        # Re-raise HTTP exceptions (like 401) so they propagate as specific status codes
        raise
    except Exception as e:
        print(f"CRITICAL ERROR in generate_image: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return JSONResponse({"detail": f"Server Error: {str(e)}"}, status_code=500)

@router.post("/edit")
def edit_image(
    api_key: str = Form(None), 
    prompt: str = Form(...), 
    file: UploadFile = File(...), 
    model: str = Form("gemini-2.5-flash-image"), 
    grounding: bool = Form(False),
    user_id: str = Form(None)
):
    final_key = get_api_key(api_key)
    img_data, mime = b64encode_file(file)
    system_prompt = random.choice(PROMPTS["edit_image"])
    full_prompt = f"{system_prompt} {prompt}"
    img_b64, out_mime, error, status = call_nano_banana(final_key, full_prompt, images=[{'data': img_data, 'mime': mime}], model=model, grounding=grounding)
    
    if img_b64:
        if user_id and user_id != "undefined":
            job_id = str(uuid.uuid4())
            web_path = storage.save_image(img_b64, job_id)
            if web_path:
                job = ImageJob(
                    job_id=job_id,
                    user_id=user_id,
                    type="edit",
                    prompt=prompt,
                    image_path=web_path,
                    timestamp=datetime.now().isoformat(),
                    model=model
                )
                db.save_job(job)
        return JSONResponse({"image": img_b64, "mime": out_mime})
    return JSONResponse({"detail": error}, status_code=status)

@router.post("/virtual_try_on")
def virtual_try_on(
    api_key: str = Form(None), 
    product: UploadFile = File(...), 
    person: UploadFile = File(...), 
    prompt: str = Form(""), 
    model: str = Form("gemini-2.5-flash-image"), 
    grounding: bool = Form(False),
    user_id: str = Form(None),
    token_uid: str = Depends(verify_token)
):
    if user_id and user_id != "undefined" and token_uid != user_id:
         raise HTTPException(status_code=403, detail="User ID mismatch.")

    final_key = get_api_key(api_key)
    images = []
    for f in [product, person]:
        data, mime = b64encode_file(f)
        images.append({'data': data, 'mime': mime})
    system_prompt = random.choice(PROMPTS["virtual_try_on"])
    full_prompt = system_prompt
    if prompt:
        full_prompt += " " + prompt
    img_b64, out_mime, error, status = call_nano_banana(final_key, full_prompt, images=images, model=model, grounding=grounding)
    
    if img_b64:
        # Persistence Logic
        try:
            if user_id and user_id != "undefined":
                job_id = str(uuid.uuid4())
                web_path = storage.save_image(img_b64, job_id)
                
                if web_path:
                    job = ImageJob(
                        job_id=job_id,
                        user_id=user_id,
                        type="virtual_try_on",
                        prompt=prompt or "Virtual Try-On",
                        image_path=web_path,
                        timestamp=datetime.now().isoformat(),
                        model=model
                    )
                    db.save_job(job)
        except Exception as e:
            logger.error(f"Failed to save try-on job: {e}")
            # Non-blocking failure

        return JSONResponse({"image": img_b64, "mime": out_mime})
    return JSONResponse({"detail": error}, status_code=status)

MAX_AD_VARIATIONS = int(os.getenv("MAX_AD_VARIATIONS", "3"))

@router.post("/create_ads")
def create_ads(
    api_key: str = Form(None), 
    model_file: UploadFile = File(..., alias="model_image"), 
    product: UploadFile = File(...), 
    prompt: str = Form(""), 
    variations: int = Form(None), 
    model: str = Form("gemini-2.5-flash-image"), 
    grounding: bool = Form(False),
    user_id: str = Form(None),
    token_uid: str = Depends(verify_token)
):
    if user_id and user_id != "undefined" and token_uid != user_id:
         raise HTTPException(status_code=403, detail="User ID mismatch.")

    final_key = get_api_key(api_key)
    images = []
    for f in [model_file, product]:
        data, mime = b64encode_file(f)
        images.append({'data': data, 'mime': mime})
    target = variations or MAX_AD_VARIATIONS
    target = max(1, min(target, 3))
    system_prompt = PROMPTS["create_ads"][0]
    base_hints = [
        "lifestyle angle", "dramatic lighting", "portrait social feed style",
        "product-forward macro", "cinematic depth", "high contrast poster feel",
        "minimal negative space layout", "moody editorial", "bright commercial",
        "subtle neutral studio"
    ]
    results = []
    for i in range(target):
        hint = base_hints[i % len(base_hints)]
        full_prompt = f"{system_prompt} Variation {i+1}: {hint}.".strip()
        if prompt:
            full_prompt += f" User: {prompt.strip()}"
        img_b64, out_mime, error, status = call_nano_banana(final_key, full_prompt, images=images, model=model, grounding=grounding)
        if img_b64:
            # Persistence Logic
            try:
                if user_id and user_id != "undefined":
                    job_id = str(uuid.uuid4())
                    web_path = storage.save_image(img_b64, job_id)
                    
                    if web_path:
                        job = ImageJob(
                            job_id=job_id,
                            user_id=user_id,
                            type="create_ads",
                            prompt=full_prompt,
                            image_path=web_path,
                            timestamp=datetime.now().isoformat(),
                            model=model
                        )
                        db.save_job(job)
            except Exception as e:
                logger.error(f"Failed to save ad variation {i+1}: {e}")

            results.append({'image': img_b64, 'mime': out_mime})
        else:
            logger.error(f"Ad variation {i+1} failed: {error}")
            
    if not results:
         return JSONResponse({"detail": "Failed to generate any variations"}, status_code=500)
         
    return JSONResponse({"results": results})

@router.post("/merge_images")
def merge_images(
    api_key: str = Form(None), 
    files: List[UploadFile] = File(...), 
    prompt: str = Form(""), 
    model: str = Form("gemini-2.5-flash-image"), 
    grounding: bool = Form(False),
    user_id: str = Form(None),
    token_uid: str = Depends(verify_token)
):
    if user_id and user_id != "undefined" and token_uid != user_id:
         raise HTTPException(status_code=403, detail="User ID mismatch.")

    final_key = get_api_key(api_key)
    images = []
    max_images = 14 if "gemini-3-pro" in model else 5
    for f in files[:max_images]:
        data, mime = b64encode_file(f)
        images.append({'data': data, 'mime': mime})
    system_prompt = random.choice(PROMPTS["merge_images"])
    full_prompt = system_prompt
    if prompt:
        full_prompt += " " + prompt
    img_b64, out_mime, error, status = call_nano_banana(final_key, full_prompt, images=images, model=model, grounding=grounding)
    if img_b64:
        # Persistence Logic
        try:
            if user_id and user_id != "undefined":
                job_id = str(uuid.uuid4())
                web_path = storage.save_image(img_b64, job_id)
                
                if web_path:
                    job = ImageJob(
                        job_id=job_id,
                        user_id=user_id,
                        type="merge",
                        prompt=prompt or "Merge Images",
                        image_path=web_path,
                        timestamp=datetime.now().isoformat(),
                        model=model
                    )
                    db.save_job(job)
        except Exception as e:
            logger.error(f"Failed to save merge job: {e}")

        return JSONResponse({"image": img_b64, "mime": out_mime})
    return JSONResponse({"detail": error}, status_code=status)

@router.post("/generate_scenes")
def generate_scenes(
    api_key: str = Form(None), 
    scene: UploadFile = File(...), 
    prompt: str = Form(""), 
    variations: int = Form(None), 
    model: str = Form("gemini-2.5-flash-image"), 
    grounding: bool = Form(False),
    user_id: str = Form(None),
    token_uid: str = Depends(verify_token)
):
    if user_id and user_id != "undefined" and token_uid != user_id:
         raise HTTPException(status_code=403, detail="User ID mismatch.")

    final_key = get_api_key(api_key)
    data, mime = b64encode_file(scene)
    target = 3
    system_prompt = PROMPTS["generate_scenes"][0]
    base_hints = [
        "wide cinematic extension", "dawn atmosphere", "midday clarity",
        "night / blue hour mood", "stylized painterly reinterpretation",
        "foggy ambient variant", "high contrast sunset", "rainy ambience",
        "snowy transformation", "minimal desaturated look"
    ]
    results = []
    for i in range(min(target, 3)):
        hint = base_hints[i % len(base_hints)]
        full_prompt = f"{system_prompt} Variation {i+1}: {hint}.".strip()
        if prompt:
            full_prompt += f" User: {prompt.strip()}"
        img_b64, out_mime, error, status = call_nano_banana(final_key, full_prompt, images=[{'data': data, 'mime': mime}], model=model, grounding=grounding)
        if img_b64:
            # Persistence Logic
            try:
                if user_id and user_id != "undefined":
                    job_id = str(uuid.uuid4())
                    web_path = storage.save_image(img_b64, job_id)
                    
                    if web_path:
                        job = ImageJob(
                            job_id=job_id,
                            user_id=user_id,
                            type="scenes",
                            prompt=full_prompt,
                            image_path=web_path,
                            timestamp=datetime.now().isoformat(),
                            model=model
                        )
                        db.save_job(job)
            except Exception as e:
                logger.error(f"Failed to save scene variation {i+1}: {e}")

            results.append({'image': img_b64, 'mime': out_mime})
    if len(results) > 3:
        results = results[:3]
    return JSONResponse({"results": results})

@router.post("/restore_old_image")
def restore_old_image(
    api_key: str = Form(None), 
    file: UploadFile = File(...), 
    prompt: str = Form(""), 
    model: str = Form("gemini-2.5-flash-image"), 
    grounding: bool = Form(False),
    user_id: str = Form(None),
    token_uid: str = Depends(verify_token)
):
    if user_id and user_id != "undefined" and token_uid != user_id:
         raise HTTPException(status_code=403, detail="User ID mismatch.")

    final_key = get_api_key(api_key)
    img_data, mime = b64encode_file(file)
    system_prompt = random.choice(PROMPTS["restore_old_image"])
    full_prompt = system_prompt
    if prompt:
        full_prompt += " " + prompt
    img_b64, out_mime, error, status = call_nano_banana(final_key, full_prompt, images=[{'data': img_data, 'mime': mime}], model=model, grounding=grounding)
    if img_b64:
        # Persistence Logic
        try:
            if user_id and user_id != "undefined":
                job_id = str(uuid.uuid4())
                web_path = storage.save_image(img_b64, job_id)
                
                if web_path:
                    job = ImageJob(
                        job_id=job_id,
                        user_id=user_id,
                        type="restore",
                        prompt=prompt or "Restore Image",
                        image_path=web_path,
                        timestamp=datetime.now().isoformat(),
                        model=model
                    )
                    db.save_job(job)
        except Exception as e:
            logger.error(f"Failed to save restore job: {e}")

        return JSONResponse({"image": img_b64, "mime": out_mime})
    return JSONResponse({"detail": error}, status_code=status)

# Include the router with prefix /image to match frontend proxy
app.include_router(router, prefix="/image")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
