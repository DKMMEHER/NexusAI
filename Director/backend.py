import os
import time
import uuid
import logging
import asyncio
import subprocess
import httpx
import json
import re
from datetime import datetime
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import google.generativeai as genai
from dotenv import load_dotenv

# Import extracted components
from .models import (
    MovieRequest, VisualDetails, CameraDirection, MotionAndActions, 
    Music, Voiceover, AudioDesign, LanguagePreferences, Style, 
    TechnicalPreferences, ScenePrompt, Scene, MovieJob, ApprovalRequest
)
from .storage import LocalStorage
from .database import JsonDatabase, FirestoreDatabase

# Load environment variables
load_dotenv()

# LangSmith Integration
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langsmith_config import trace_async_llm_call, token_tracker
from langsmith import traceable

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Director")

app = FastAPI(title="Director Video Service")

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    logger.warning("No GEMINI_API_KEY or GOOGLE_API_KEY found in environment variables.")
else:
    genai.configure(api_key=api_key)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Providers
# Initialize Providers
# storage = LocalStorage() # Moved to conditional block below
# Init Providers
from .storage import LocalStorage, GoogleCloudStorage

# Auth
from fastapi import Header, Depends, HTTPException, Form
from fastapi.security import HTTPAuthorizationCredentials
from auth import verify_token

# Database Selection Logic
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
is_cloud_run = os.getenv("K_SERVICE") is not None

if is_cloud_run and project_id:
    logger.info(f"Detected Cloud Run environment. Using Firestore (Project: {project_id}).")
    try:
        db = FirestoreDatabase(project_id)
    except Exception as e:
        logger.error(f"Failed to initialize Firestore: {e}. Falling back to JsonDatabase (Ephemeral!).")
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

# Serve Generated Videos (LocalStorage specific)
# We still need this for LocalStorage to work with the frontend
os.makedirs("Generated_Videos", exist_ok=True)
app.mount("/videos", StaticFiles(directory="Generated_Videos"), name="videos")


# --- Core Logic ---

@trace_async_llm_call(name="generate_video_script", service="Director")
async def generate_script(job_id: str, topic: str, duration_seconds: int, resolution: str = "1080p"):
    """Generates a scene-by-scene script using Gemini."""
    logger.info(f"[{job_id}] Generating script for: {topic} ({duration_seconds}s, {resolution})")
    
    try:
        model = genai.GenerativeModel("gemini-3-pro-preview")
        
        # Initialize duration variables with defaults
        duration_instruction = "Each scene MUST be exactly 8 seconds long."
        scene_duration_placeholder = "8"
        
        # Duration logic
        if resolution == "720p":
            duration_instruction = "For each scene, you MUST decide the duration. Choose either 4 or 8 seconds based on the pacing."
            scene_duration_placeholder = "4 or 8"
        else:
            # 1080p and other resolutions require fixed 8s for now
            duration_instruction = "Each scene MUST be exactly 8 seconds long."
            scene_duration_placeholder = "8"

        # Inject explicit language instruction if detected in topic
        voiceover_language_placeholder = "English"
        if "hindi" in topic.lower():
            voiceover_language_placeholder = "Hindi"
        elif "spanish" in topic.lower():
            voiceover_language_placeholder = "Spanish"

        prompt = f"""
        You are a world-class Film Director and Cinematographer.
        Your task is to create a highly detailed, cinematic, and ultra-realistic script for a video about: "{topic}".
        The total video length should be approximately {duration_seconds} seconds.
        {duration_instruction}

        ### INSTRUCTIONS FOR QUALITY:
        1.  **VISUALS**: Do NOT use generic terms like "a man walking". Use specific details: "A weathered man in his 40s, wearing a tattered flannel shirt, trudges heavily..."
        2.  **CAMERA**: Use professional terminology (Dolly zoom, Rack focus, Low angle, Anamorphic lens flare).
        3.  **LIGHTING**: Describe the light quality (Golden hour, Blue hour, Harsh noon, Soft diffused window light).
        4.  **AUDIO**: Design a complete soundscape.
        5.  **VOICEOVER**: ALWAYS generate a compelling voiceover script relevant to the scene. Do not leave it blank.
        6.  **REASONING**: Before generating the JSON, think about the visual flow, color palette, and emotional arc.
        7.  **SAFETY & COMPLIANCE**: DO NOT use real names of famous people or historical figures in 'visual_prompt', 'scene_description', or 'visual_details'.
            The video generation model will BLOCK requests with real names.
            INSTEAD, describe the person visually.
            BAD: "Veer Surendra Sai walking..."
            GOOD: "A tall, bearded Indian freedom fighter from the 19th century, wearing a turban and white dhoti, walking..."
            (You MAY use the real name in the 'voiceover' script, just not in the visual directives).

        8. **CONSISTENCY IS KING**: **CRITICAL**: The component 'visual_details.character' MUST BE IDENTICAL in every single scene. Do not change the age, clothes, or face of the main character between scenes.
            *   *Strategy*: Write the character description ONCE mentally, and copy-paste it into every scene's JSON.
        9. **LANGUAGE**: If the user asked for a specific language (e.g., Hindi), the 'audio_design.voiceover.script' MUST be in that language.
            *   Example: If Hindi is requested -> `"script": "जीवन एक यात्रा है..."` (Use Devanagari or appropriate script).

        ### REQUIRED JSON STRUCTURE:
        For EACH scene, you must provide a JSON object with the following EXACT structure. 
        
        [
            {{
                "id": 1,
                "scene_heading": "EXT. LOCATION - TIME",
                "prompt": {{
                    "scene_description": "Precise description of what happens.",
                    "visual_details": {{
                        "environment": "Detailed setting...",
                        "character": "STRICTLY CONSISTENT: [Age, Gender, Clothing, defining features]. Must match Scene 1 exactly.",
                        "props": "..."
                    }},
                    "camera_direction": {{
                        "movement": "e.g. Dolly forward",
                        "framing": "e.g. Medium Shot",
                        "focus": "e.g. Rack focus to subject",
                        "lens": "e.g. 35mm Anamorphic"
                    }},
                    "motion_and_actions": {{
                        "character_action": "Specific movement...",
                        "environment_motion": "Wind, background chaos..."
                    }},
                    "audio_design": {{
                        "music": {{ "enabled": true, "style": "...", "intensity": "..." }},
                        "ambient_sfx": {{ "wind": "...", "environment": "...", "footsteps": "..." }},
                        "voiceover": {{
                            "enabled": true,
                            "language": "{voiceover_language_placeholder}", 
                            "script": "The actual spoken words in the target language.",
                            "tone": "...",
                            "lip_sync": "DISABLED - Character must NOT move lips."
                        }}
                    }},
                    "language_preferences": {{
                        "narration_language": "{voiceover_language_placeholder}",
                        "subtitle_language": "English",
                        "tone": "..."
                    }},
                    "style": {{
                        "cinematic_style": "...",
                        "color_grade": "...",
                        "quality": "..."
                    }},
                    "technical_preferences": {{
                        "frame_rate": "24fps",
                        "resolution": "{resolution}",
                        "stabilization": "High"
                    }},
                    "continuity_rules": [
                        "Character appearance MUST match Scene 1.",
                        "Lighting direction must remain consistent."
                    ]
                }},
                "visual_prompt": "A text-to-video prompt string. Combine [visual_details.environment] + [visual_details.character] + [camera_direction] + [style]. IMPORTANT: Append audio instruction: 'Audio: [voiceover.script]'. Append lip-sync instruction: '[voiceover.lip_sync]'. NO REAL NAMES.", 
                "duration": {scene_duration_placeholder}
            }},
            ...
        ]
        """
        
        # Inject explicit language instruction if detected in topic
        # (Moved above prompt definition)
        # Add more languages as needed

        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]

        response = await model.generate_content_async(prompt, request_options={"timeout": 600}, safety_settings=safety_settings)
        
        try:
            logger.info(f"[{job_id}] Response Candidates: {response.candidates}")
            text = response.text.strip()
            logger.info(f"[{job_id}] Raw Response: {text[:500]}...")
            if not text:
                raise ValueError("Empty response text from AI model.")
        except Exception as e:
            logger.error(f"[{job_id}] Generation failed/blocked. Feedback: {response.prompt_feedback}")
            raise ValueError(f"AI generation blocked or empty: {e}")
        
        # Robust JSON cleanup
        # 1. Try to find JSON within markdown code blocks
        json_match = re.search(r"```json(.*?)```", text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        else:
            # 2. Try generic code block
            code_match = re.search(r"```(.*?)```", text, re.DOTALL)
            if code_match:
                text = code_match.group(1)
        
        text = text.strip()
        
        # 3. If still not valid JSON (or no code blocks found), try to find the array boundaries
        if not (text.startswith("[") and text.endswith("]")):
             start = text.find("[")
             end = text.rfind("]")
             if start != -1 and end != -1:
                 text = text[start:end+1]
            
        scenes_data = json.loads(text)
        
        # Convert to Scene objects
        scenes = []
        for s in scenes_data:
            prompt_data = s.get('prompt', {})
            s_duration = s.get('duration', 8)
            
            scenes.append(Scene(
                id=s['id'],
                scene_heading=s.get('scene_heading'),
                prompt=ScenePrompt(
                    scene_description=prompt_data.get('scene_description', ''),
                    visual_details=VisualDetails(**prompt_data.get('visual_details', {})),
                    camera_direction=CameraDirection(**prompt_data.get('camera_direction', {})),
                    motion_and_actions=MotionAndActions(**prompt_data.get('motion_and_actions', {})),
                    audio_design=AudioDesign(**prompt_data.get('audio_design', {})),
                    language_preferences=LanguagePreferences(**prompt_data.get('language_preferences', {})),
                    style=Style(**prompt_data.get('style', {})),
                    technical_preferences=TechnicalPreferences(**prompt_data.get('technical_preferences', {})),
                    continuity_rules=prompt_data.get('continuity_rules', [])
                ),
                visual_prompt=s.get('visual_prompt', ''),
                duration=s_duration,
                status="pending"
            ))
            
        job = db.get_job(job_id)
        if job:
            job.scenes = scenes
            db.save_job(job)
            logger.info(f"[{job_id}] Generated {len(scenes)} scenes.")

    except Exception as e:
        logger.error(f"[{job_id}] Script generation failed: {e}")
        raise e

async def production_loop(job_id: str):
    """Orchestrates the video generation for each scene."""
    logger.info(f"[{job_id}] Starting production loop")
    
    job = db.get_job(job_id)
    if not job:
        logger.error(f"[{job_id}] Job not found in production loop")
        return

    total_scenes = len(job.scenes)
    
    async with httpx.AsyncClient(timeout=300) as client:
        previous_operation_name = None
        
        for i, scene in enumerate(job.scenes):
            if scene.status == "done":
                # Assuming linear flow continuation
                continue
                
            logger.info(f"[{job_id}] Generating Scene {scene.id}/{total_scenes}: {scene.visual_prompt[:50]}...")
            scene.status = "generating"
            db.save_job(job)
            
            max_retries = 0
            retry_delay = 0
            
            for attempt in range(max_retries + 1):
                try:
                    # 1. Request Video Generation
                    payload = {
                        "prompt": scene.visual_prompt,
                        "model": job.model, 
                        "duration_seconds": scene.duration,
                        "resolution": job.resolution,
                        "aspect_ratio": job.aspect_ratio
                    }
                    
                    if i > 0 and attempt == 0:
                        logger.info(f"[{job_id}] Waiting 40s before next scene to respect rate limits...")
                        await asyncio.sleep(40)

                    if previous_operation_name:
                        logger.info(f"[{job_id}] Extending from previous operation: {previous_operation_name}")
                        payload["previous_operation_name"] = previous_operation_name
                        endpoint = "http://127.0.0.1:8002/extend_veo_video"
                        scene.is_extension = True
                    else:
                        logger.info(f"[{job_id}] Starting new sequence with Text-to-Video")
                        endpoint = "http://127.0.0.1:8002/text_to_video"
                        scene.is_extension = False

                    response = await client.post(endpoint, data=payload)
                    response.raise_for_status()
                    result = response.json()
                    operation_name = result.get("operation_name")
                    
                    if not operation_name:
                        raise Exception("No operation_name returned from Video Service")
                    
                    # 2. Poll for Status
                    poll_start_time = time.time()
                    while True:
                        await asyncio.sleep(5)
                        
                        if time.time() - poll_start_time > 900:
                            raise Exception("Video generation timed out after 15 minutes.")

                        status_res = await client.get(f"http://127.0.0.1:8002/status/{operation_name}")
                        status_data = status_res.json()
                        state = status_data.get("state")
                        
                        if int(time.time() - poll_start_time) % 60 == 0:
                             logger.info(f"[{job_id}] Polling status for {operation_name}: {state}")

                        if state == "succeeded" or status_data.get("status") == "COMPLETE":
                            break
                        elif state == "failed" or status_data.get("status") == "ERROR":
                            raise Exception(f"Video generation failed: {status_data.get('error') or status_data.get('message')}")
                    
                    # 3. Save Local & Finalize via Provider
                    save_res = await client.get(f"http://127.0.0.1:8002/save_local/{operation_name}")
                    if save_res.status_code != 200:
                         raise Exception(f"Save local failed: {save_res.text}")
                         
                    save_data = save_res.json()
                    source_video_path = save_data.get("file_path")
                    
                    safe_op_name = operation_name.replace("/", "_")
                    filename = f"scene_{job_id}_{scene.id}_{safe_op_name}.mp4"
                    final_path = storage.save_video(source_video_path, filename)
                    
                    scene.video_path = final_path
                    scene.status = "done"
                    scene.operation_name = operation_name
                    
                    previous_operation_name = operation_name
                    logger.info(f"[{job_id}] Scene {scene.id} completed. Path: {final_path}")
                    
                    job.progress = int(10 + ((i + 1) / total_scenes) * 80)
                    db.save_job(job)
                    break 
                    
                except Exception as e:
                    logger.error(f"[{job_id}] Scene {scene.id} failed (Attempt {attempt+1}/{max_retries+1}): {e}")
                    if attempt < max_retries:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.info(f"[{job_id}] Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        scene.status = "failed"
                        db.save_job(job)
                        continue

        # All scenes processed
        await stitch_movie(job_id)
        
        job.status = "completed"
        job.progress = 100
        db.save_job(job)
        logger.info(f"[{job_id}] Job completed successfully.")

async def stitch_movie(job_id: str):
    """Combines all clips into the final movie."""
    logger.info(f"[{job_id}] Stitching movie")
    
    job = db.get_job(job_id)
    if not job:
        return

    valid_scenes = [s for s in job.scenes if s.status == "done" and s.video_path]
    
    if not valid_scenes:
        logger.error(f"[{job_id}] No valid scenes to stitch.")
        return

    final_scenes_to_stitch = []
    for s in valid_scenes:
        if s.is_extension and final_scenes_to_stitch:
            final_scenes_to_stitch.pop()
        final_scenes_to_stitch.append(s)
        
    list_path = f"temp_list_{job_id}.txt"
    with open(list_path, "w") as f:
        for scene in final_scenes_to_stitch:
            safe_path = scene.video_path.replace("\\", "/")
            f.write(f"file '{safe_path}'\n")
    
    output_filename = f"Movie_{job.topic.replace(' ', '_')[:30]}_{job_id}.mp4"
    temp_output_path = os.path.join(os.getcwd(), f"temp_{output_filename}")
    
    try:
        cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0", "-i", list_path,
            "-c", "copy", "-y", temp_output_path
        ]
        
        logger.info(f"[{job_id}] Running FFmpeg: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        final_key = storage.save_video(temp_output_path, output_filename)
        
        if os.path.exists(temp_output_path):
            os.remove(temp_output_path)

        job.final_video_path = output_filename 
        db.save_job(job)
        
        logger.info(f"[{job_id}] Stitching complete: {final_key}")

        # Cleanup intermediate scene files
        logger.info(f"[{job_id}] Cleaning up {len(valid_scenes)} intermediate scene files...")
        for scene in valid_scenes:
            if scene.video_path and os.path.exists(scene.video_path):
                try:
                    os.remove(scene.video_path)
                    logger.info(f"[{job_id}] Deleted intermediate file: {scene.video_path}")
                except Exception as ex:
                    logger.warning(f"[{job_id}] Failed to delete {scene.video_path}: {ex}")
            
            # Also cleanup the "auto-saved" redundant file from VideoGeneration service
            if scene.operation_name:
                safe_op = scene.operation_name.replace("/", "_") + ".mp4"
                auto_saved_path = os.path.join(os.getcwd(), "Generated_Videos", safe_op)
                if os.path.exists(auto_saved_path):
                    try:
                        os.remove(auto_saved_path)
                        logger.info(f"[{job_id}] Deleted redundant auto-save: {auto_saved_path}")
                    except Exception as ex:
                        logger.warning(f"[{job_id}] Failed to delete redundant {auto_saved_path}: {ex}")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"[{job_id}] FFmpeg failed: {e.stderr.decode()}")
        raise Exception(f"Stitching failed: {e.stderr.decode()}")
        
    finally:
        if os.path.exists(list_path):
            os.remove(list_path)

async def generate_script_task(job_id: str, request: MovieRequest):
    job = db.get_job(job_id)
    if not job: 
        return
        
    try:
        # 1. Scripting
        job.status = "scripting"
        job.progress = 5
        db.save_job(job)
        await generate_script(job_id, request.topic, request.duration_seconds, request.resolution)
        
        # Pause for approval
        job.status = "waiting_for_approval"
        job.progress = 10
        db.save_job(job)
        logger.info(f"[{job_id}] Script generated. Waiting for approval.")
        
    except Exception as e:
        logger.error(f"[{job_id}] Script generation failed: {e}")
        job.status = "failed"
        job.error = str(e)
        db.save_job(job)

@app.post("/create_movie")
async def create_movie(
    request: MovieRequest, 
    background_tasks: BackgroundTasks,
    token_uid: str = Depends(verify_token)
):
    if token_uid != request.user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

    job_id = str(uuid.uuid4())[:8]
    
    new_job = MovieJob(
        job_id=job_id,
        topic=request.topic,
        duration=request.duration_seconds,
        status="queued",
        model=request.model,
        resolution=request.resolution,
        aspect_ratio=request.aspect_ratio,
        user_id=request.user_id,
        created_at=datetime.now().isoformat(),
        progress=0
    )
    
    # Logic for pre-defined scenes (e.g. from UI edit or retake)
    if request.scenes:
        updated_scenes = []
        for scene_data in request.scenes:
            # Convert dict to Scene object if needed
            if isinstance(scene_data, dict):
                s = Scene(**scene_data)
            else:
                s = scene_data
            
            # Ensure prompt is a ScenePrompt object
            if isinstance(s.prompt, dict):
                s.prompt = ScenePrompt(**s.prompt)
                
            p = s.prompt
            # Reconstruct visual prompt if needed
            veo_prompt = (
                f"{p.style.cinematic_style} style, {p.style.color_grade}. "
                f"{p.scene_description} "
                f"{p.visual_details.environment}, {p.visual_details.character}. "
                f"{p.camera_direction.movement}, {p.camera_direction.framing}, {p.camera_direction.focus}, {p.camera_direction.lens}. "
                f"{p.motion_and_actions.character_action} {p.motion_and_actions.environment_motion}. "
                f"Audio: {p.audio_design.voiceover.script}. "
                f"Lip-sync: {p.audio_design.voiceover.lip_sync or 'DISABLED'}"
            )
            s.visual_prompt = veo_prompt
            updated_scenes.append(s)
            
        new_job.scenes = updated_scenes
        db.save_job(new_job)
        logger.info(f"[{job_id}] Created job with existing scenes. Starting production loop.")
        background_tasks.add_task(production_loop, job_id)
        return {"job_id": job_id, "status": "production_started"}
    
    else:
        db.save_job(new_job)
        logger.info(f"[{job_id}] New job created. Starting script generation.")
        background_tasks.add_task(generate_script_task, job_id, request)
        return {"job_id": job_id, "status": "queued"}

@app.post("/approve_script/{job_id}")
async def approve_script(job_id: str, request: ApprovalRequest, background_tasks: BackgroundTasks):
    """Approves the script and starts production."""
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    logger.info(f"[{job_id}] Script approved. Starting production.")
    
    # Update scenes if user modified them
    if request.scenes:
        logger.info(f"[{job_id}] Updating scenes from approval request.")
        # Ensure we map dict back to Scene objects if needed, but Pydantic should handle it
        # However, checking if request.scenes is list of dicts or objects
        job.scenes = request.scenes
    
    job.status = "filming"
    job.progress = 15
    db.save_job(job)
    
    background_tasks.add_task(production_loop, job_id)
    return {"status": "production_started"}

@app.get("/movie_status/{job_id}")
async def get_movie_status(job_id: str):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status == "waiting_for_approval":
        logger.info(f"[{job_id}] Returning status: {job.status}, Scenes: {len(job.scenes)}")
        
    return job

@app.get("/my_jobs/{user_id}")
async def get_my_jobs(user_id: str, token_uid: str = Depends(verify_token)):
    """Fetches all jobs belonging to a specific user."""
    if token_uid != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to another user's jobs.")
        
    logger.info(f"Fetching jobs for user: {user_id}")
    return db.get_user_jobs(user_id)

@app.post("/save_external_job")
async def save_external_job(job: MovieJob):
    """Saves a job created by another service (e.g. TextToVideo)."""
    logger.info(f"Saving external job: {job.job_id} (Type: {job.type})")
    db.save_job(job)
    return {"status": "saved"}

@app.get("/")
def health_check_root():
    return {"status": "Director Service Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
