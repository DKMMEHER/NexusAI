import base64
import os
import time
import requests
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import random
import logging
import json
import sys

# Use relative import for prompts to work when imported from parent directory
try:
    from .prompts import PROMPTS
except ImportError:
    from prompts import PROMPTS

# === FastAPI Router for Nano Banana ===
# === FastAPI Router for Nano Banana ===
router = APIRouter()

@router.get("/")
def health_check():
    return {"status": "Image Generation Service Running"}

# Base URL pattern - will be formatted with model name
API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# Configure logger explicitly to ensure output to stdout
logger = logging.getLogger("backend.image")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)

print("DEBUG: ImageGeneration backend module loaded", flush=True)

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

    # Append Aspect Ratio to prompt if provided (since it's not supported in generationConfig for this model)
    if aspect_ratio:
        parts[0]['text'] += f"\n\nAspect Ratio: {aspect_ratio}"

    payload = {'contents': [{'parts': parts}]}
    
    # Add Tools (Grounding) if requested and supported (Gemini 3 Pro only usually, but we can send if requested)
    if grounding and "gemini-3-pro" in model:
        payload['tools'] = [{'google_search': {}}]
    
    # Add Generation Config (Sample Count)
    generation_config = {}
    # if aspect_ratio:
    #     generation_config['aspectRatio'] = aspect_ratio
        
    if generation_config:
        payload['generationConfig'] = generation_config

    attempt = 0
    while attempt <= retries:
        # Log the request for debugging
        print(f"DEBUG: Sending request to: {url}", flush=True)
        # print(f"DEBUG: Payload: {payload}", flush=True)
        
        res = requests.post(f"{url}?key={api_key}", json=payload, headers={"Content-Type": "application/json"})
        if res.status_code == 429:
            # Quota / rate limit – exponential backoff
            if attempt == retries:
                return None, None, "Quota exceeded. Please try again later.", res.status_code
            sleep_for = backoff ** attempt
            time.sleep(sleep_for)
            attempt += 1
            continue
        
        if res.status_code != 200:
            # Try to parse the error message from JSON
            try:
                error_data = res.json()
                print(f"DEBUG: Error Response JSON: {error_data}", flush=True)
                
                # Check for standard Google API error structure
                if "error" in error_data:
                    error_msg = error_data["error"].get("message", res.text)
                    status = error_data["error"].get("status", "UNKNOWN")
                    
                    print(f"DEBUG: Parsed Error - Status: {status}, Msg: {error_msg}", flush=True)

                    # Map specific errors to user-friendly messages
                    if status == "INTERNAL" or "internal error" in error_msg.lower():
                        print(f"DEBUG: Caught INTERNAL error. Returning friendly message.", flush=True)
                        return None, None, "The AI service is temporarily unavailable. Please try again in a moment.", 500
                    if "safety" in error_msg.lower():
                        return None, None, "The request was blocked by safety filters. Please modify your prompt.", 400
                        
                    return None, None, f"AI Error: {error_msg}", res.status_code
            except Exception as e:
                print(f"DEBUG: Error parsing JSON error: {e}", flush=True)
                pass
                
            return None, None, f"Error {res.status_code}: {res.text}", res.status_code

        data = res.json()
        parts_out = data.get('candidates', [{}])[0].get('content', {}).get('parts', [])
        for p in parts_out:
            if 'inlineData' in p:
                return p['inlineData']['data'], p['inlineData'].get('mimeType', 'image/png'), None, 200
        
        # Log the full response for debugging
        logger.error(f"No image returned. Full response: {data}")
        
        # Check for finishReason
        candidate = data.get('candidates', [{}])[0]
        finish_reason = candidate.get('finishReason')
        if finish_reason == "SAFETY":
             return None, None, "The image generation was blocked by safety settings. Please try a different prompt.", 400
             
        return None, None, "No image returned. The model might have refused the request.", 500
    return None, None, "Exhausted retries", 500

@router.post("/generate")
def generate_image(api_key: str = Form(None), prompt: str = Form(...), model: str = Form("gemini-2.5-flash-image"), grounding: bool = Form(False), aspect_ratio: str = Form(None)):
    final_key = get_api_key(api_key)
    system_prompt = random.choice(PROMPTS["generate_image"])
    full_prompt = f"{system_prompt} {prompt}"
    img_b64, mime, error, status = call_nano_banana(final_key, full_prompt, model=model, grounding=grounding, aspect_ratio=aspect_ratio)
    if img_b64:
        return JSONResponse({"image": img_b64, "mime": mime})
    return JSONResponse({"detail": error}, status_code=status)

@router.post("/edit")
def edit_image(api_key: str = Form(None), prompt: str = Form(...), file: UploadFile = File(...), model: str = Form("gemini-2.5-flash-image"), grounding: bool = Form(False)):
    final_key = get_api_key(api_key)
    img_data, mime = b64encode_file(file)
    system_prompt = random.choice(PROMPTS["edit_image"])
    full_prompt = f"{system_prompt} {prompt}"
    img_b64, out_mime, error, status = call_nano_banana(final_key, full_prompt, images=[{'data': img_data, 'mime': mime}], model=model, grounding=grounding)
    if img_b64:
        return JSONResponse({"image": img_b64, "mime": out_mime})
    return JSONResponse({"detail": error}, status_code=status)

@router.post("/virtual_try_on")
def virtual_try_on(api_key: str = Form(None), product: UploadFile = File(...), person: UploadFile = File(...), prompt: str = Form(""), model: str = Form("gemini-2.5-flash-image"), grounding: bool = Form(False)):
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
        return JSONResponse({"image": img_b64, "mime": out_mime})
    return JSONResponse({"detail": error}, status_code=status)

MAX_AD_VARIATIONS = int(os.getenv("MAX_AD_VARIATIONS", "3"))
MAX_SCENE_VARIATIONS = int(os.getenv("MAX_SCENE_VARIATIONS", "3"))

@router.post("/create_ads")
def create_ads(api_key: str = Form(None), model_file: UploadFile = File(..., alias="model_image"), product: UploadFile = File(...), prompt: str = Form(""), variations: int = Form(None), model: str = Form("gemini-2.5-flash-image"), grounding: bool = Form(False)):
    final_key = get_api_key(api_key)
    images = []
    for f in [model_file, product]:
        data, mime = b64encode_file(f)
        images.append({'data': data, 'mime': mime})
    # Determine how many variations to attempt
    target = variations or MAX_AD_VARIATIONS
    # Clamp to maximum of 3 variations
    target = max(1, min(target, 3))
    system_prompt = PROMPTS["create_ads"][0]
    base_hints = [
        "lifestyle angle",
        "dramatic lighting",
        "portrait social feed style",
        "product-forward macro",
        "cinematic depth",
        "high contrast poster feel",
        "minimal negative space layout",
        "moody editorial",
        "bright commercial",
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
            results.append({'image': img_b64, 'mime': out_mime})
        else:
            # If one fails, we might want to stop or continue. For now, let's just log/skip or return error if all fail.
            logger.error(f"Ad variation {i+1} failed: {error}")
            
    if not results:
         return JSONResponse({"detail": "Failed to generate any variations"}, status_code=500)
         
    return JSONResponse({"results": results})

@router.post("/merge_images")
def merge_images(api_key: str = Form(None), files: List[UploadFile] = File(...), prompt: str = Form(""), model: str = Form("gemini-2.5-flash-image"), grounding: bool = Form(False)):
    final_key = get_api_key(api_key)
    images = []
    
    # Determine max images based on model
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
        return JSONResponse({"image": img_b64, "mime": out_mime})
    return JSONResponse({"detail": error}, status_code=status)

@router.post("/generate_scenes")
def generate_scenes(api_key: str = Form(None), scene: UploadFile = File(...), prompt: str = Form(""), variations: int = Form(None), model: str = Form("gemini-2.5-flash-image"), grounding: bool = Form(False)):
    final_key = get_api_key(api_key)
    data, mime = b64encode_file(scene)
    # Force exactly up to 3 images regardless of requested variations
    target = 3
    system_prompt = PROMPTS["generate_scenes"][0]
    base_hints = [
        "wide cinematic extension",
        "dawn atmosphere",
        "midday clarity",
        "night / blue hour mood",
        "stylized painterly reinterpretation",
        "foggy ambient variant",
        "high contrast sunset",
        "rainy ambience",
        "snowy transformation",
        "minimal desaturated look"
    ]
    results = []
    for i in range(min(target, 3)):
        hint = base_hints[i % len(base_hints)]
        full_prompt = f"{system_prompt} Variation {i+1}: {hint}.".strip()
        if prompt:
            full_prompt += f" User: {prompt.strip()}"
        img_b64, out_mime, error, status = call_nano_banana(final_key, full_prompt, images=[{'data': data, 'mime': mime}], model=model, grounding=grounding)
        if img_b64:
            results.append({'image': img_b64, 'mime': out_mime})
    # Hard truncate just in case
    if len(results) > 3:
        results = results[:3]
    return JSONResponse({"results": results})

@router.post("/restore_old_image")
def restore_old_image(api_key: str = Form(None), file: UploadFile = File(...), prompt: str = Form(""), model: str = Form("gemini-2.5-flash-image"), grounding: bool = Form(False)):
    final_key = get_api_key(api_key)
    img_data, mime = b64encode_file(file)
    system_prompt = random.choice(PROMPTS["restore_old_image"])
    full_prompt = system_prompt
    if prompt:
        full_prompt += " " + prompt
    img_b64, out_mime, error, status = call_nano_banana(final_key, full_prompt, images=[{'data': img_data, 'mime': mime}], model=model, grounding=grounding)
    if img_b64:
        return JSONResponse({"image": img_b64, "mime": out_mime})
    return JSONResponse({"detail": error}, status_code=status)

# === FastAPI App Setup ===
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Image Generation Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router with prefix /image to match frontend proxy
app.include_router(router, prefix="/image")

@app.get("/")
def health_check():
    return {"status": "Image Generation Service Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
