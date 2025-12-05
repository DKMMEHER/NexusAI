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
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Director")

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("GEMINI_API_KEY not found in environment variables")
else:
    genai.configure(api_key=api_key)

app = FastAPI(title="NexusAI Director Service")

# CORS
from fastapi.staticfiles import StaticFiles

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Generated Videos
os.makedirs("Generated_Video", exist_ok=True)
app.mount("/videos", StaticFiles(directory="Generated_Video"), name="videos")

# --- Data Models ---

class MovieRequest(BaseModel):
    topic: str
    style: Optional[str] = "Cinematic"
    duration_seconds: Optional[int] = 60
    model: Optional[str] = "veo-3.1-fast-generate-preview"
    resolution: Optional[str] = "1080p"
    aspect_ratio: Optional[str] = "16:9"

class VisualDetails(BaseModel):
    environment: str
    character: str
    props: str

class CameraDirection(BaseModel):
    movement: str
    framing: str
    focus: str
    lens: str

class MotionAndActions(BaseModel):
    character_action: str
    environment_motion: str

class Music(BaseModel):
    enabled: bool
    style: str
    intensity: str

class Voiceover(BaseModel):
    enabled: bool
    language: Optional[str] = ""
    script: Optional[str] = ""
    tone: Optional[str] = ""

class AudioDesign(BaseModel):
    music: Music
    ambient_sfx: Dict[str, str]
    voiceover: Voiceover

class LanguagePreferences(BaseModel):
    narration_language: str
    subtitle_language: str
    tone: str

class Style(BaseModel):
    cinematic_style: str
    color_grade: str
    quality: str

class TechnicalPreferences(BaseModel):
    frame_rate: str
    resolution: str
    stabilization: str


class ScenePrompt(BaseModel):
    scene_description: str
    visual_details: VisualDetails
    camera_direction: CameraDirection
    motion_and_actions: MotionAndActions
    audio_design: AudioDesign
    language_preferences: LanguagePreferences
    style: Style
    technical_preferences: TechnicalPreferences
    continuity_rules: Optional[List[str]] = []

class Scene(BaseModel):
    id: int
    scene_heading: str
    prompt: ScenePrompt
    
    # Computed/System fields
    visual_prompt: str # Synthesized for Veo
    duration: int # seconds
    status: str = "pending" # pending, generating, done, failed
    video_path: Optional[str] = None
    is_extension: bool = False

class MovieJob(BaseModel):
    job_id: str
    topic: str
    status: str # starting, scripting, filming, stitching, completed, failed
    progress: int # 0-100
    scenes: List[Scene] = []
    final_video_path: Optional[str] = None
    error: Optional[str] = None
    created_at: str
    # Settings
    model: str
    resolution: str
    aspect_ratio: str

class ApprovalRequest(BaseModel):
    scenes: Optional[List[Scene]] = None

# --- In-Memory Storage ---
jobs = {}
JOBS_FILE = "jobs.json"

def save_jobs():
    try:
        data = {jid: job.dict() for jid, job in jobs.items()}
        with open(JOBS_FILE, "w") as f:
            json.dump(data, f, default=str, indent=2)
    except Exception as e:
        logger.error(f"Failed to save jobs: {e}")

def load_jobs():
    global jobs
    if os.path.exists(JOBS_FILE):
        try:
            with open(JOBS_FILE, "r") as f:
                data = json.load(f)
                jobs = {jid: MovieJob(**j_data) for jid, j_data in data.items()}
            logger.info(f"Loaded {len(jobs)} jobs from {JOBS_FILE}")
        except Exception as e:
            logger.error(f"Failed to load jobs: {e}")

load_jobs()

# --- Core Logic ---

async def generate_script(job_id: str, topic: str, duration_seconds: int, resolution: str = "1080p"):
    """Generates a scene-by-scene script using Gemini."""
    logger.info(f"[{job_id}] Generating script for: {topic} ({duration_seconds}s, {resolution})")
    
    try:
        model = genai.GenerativeModel("gemini-3-pro-preview")
        
        # Duration logic
        if resolution == "720p":
            duration_instruction = "For each scene, you MUST decide the duration. Choose either 4 or 8 seconds based on the pacing."
            scene_duration_placeholder = "4 or 8"
        else:
            # 1080p usually requires fixed 8s for now (or whatever the constraint is)
            duration_instruction = "Each scene MUST be exactly 8 seconds long."
            scene_duration_placeholder = "8"

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

        ### REQUIRED JSON STRUCTURE:
        For EACH scene, you must provide a JSON object with the following EXACT structure. 
        Use this example as a template for the level of detail required:

        [
            {{
                "id": 1,
                "scene_heading": "EXT. MOUNTAIN CLIFF - SUNSET",
                "prompt": {{
                    "scene_description": "A cinematic, ultra-realistic sequence of a single adult male walking slowly toward a cliff edge at sunset; mood is inspirational and contemplative.",
                    "visual_details": {{
                        "environment": "Golden-hour sunset over layered mountains and deep valleys; soft atmospheric haze; natural rocky terrain.",
                        "character": "Adult male (30-40), casual outdoor clothing (non-branded), neutral skin tone, natural gait; no facial closeups.",
                        "props": "Rocks, grass, small wind-swept plants"
                    }},
                    "camera_direction": {{
                        "movement": "Slow forward dolly-in, steady and cinematic",
                        "framing": "Medium-wide shot from behind showing subject and cliff",
                        "focus": "Shallow depth of field; subject sharply in focus, background soft",
                        "lens": "35mm cinematic lens look"
                    }},
                    "motion_and_actions": {{
                        "character_action": "Walks slowly toward edge -> pauses -> turns head slightly and breathes in",
                        "environment_motion": "Soft wind affecting grass and distant clouds moving subtly"
                    }},
                    "audio_design": {{
                        "music": {{
                            "enabled": true,
                            "style": "Emotional cinematic score with soft strings and ambient pads",
                            "intensity": "low"
                        }},
                        "ambient_sfx": {{
                            "wind": "Gentle mountain breeze",
                            "environment": "Distant valley echo and natural ambience",
                            "footsteps": "Light, realistic on rocky ground"
                        }},
                        "voiceover": {{
                            "enabled": true,
                            "language": "Hindi",
                            "script": "Sometimes, silence speaks louder than words. In this vastness, I find myself.",
                            "tone": "Deep, reflective, male voice with a poetic touch"
                        }}
                    }},
                    "language_preferences": {{
                        "narration_language": "English",
                        "subtitle_language": "English",
                        "tone": "Calm, inspirational"
                    }},
                    "style": {{
                        "cinematic_style": "Epic, atmospheric, realistic",
                        "color_grade": "Warm golden-hour tones",
                        "quality": "High detail, realistic lighting and skin tones"
                    }},
                    "technical_preferences": {{
                        "frame_rate": "24fps",
                        "resolution": "{resolution}",
                        "stabilization": "Very stable, no jitter"
                    }},
                    "continuity_rules": [
                        "Do not change the man's clothing or appearance during the shot.",
                        "Maintain consistent golden-hour lighting throughout the clip."
                    ]
                }},
                "visual_prompt": "JSON_STRING_HERE", 
                "duration": {scene_duration_placeholder}
            }},
            ...
        ]
        """
        
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

        response = model.generate_content(prompt, request_options={"timeout": 600}, safety_settings=safety_settings)
        
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
        # This handles cases where there is conversational text but no code blocks, 
        # or if the code block extraction left some whitespace/newlines.
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
            # Use generated duration, defaulting to 8 if missing/invalid
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
            
        jobs[job_id].scenes = scenes
        save_jobs()
        logger.info(f"[{job_id}] Generated {len(scenes)} scenes.")

    except Exception as e:
        logger.error(f"[{job_id}] Script generation failed: {e}")
        raise e

async def production_loop(job_id: str):
    """Orchestrates the video generation for each scene."""
    logger.info(f"[{job_id}] Starting production loop")
    
    job = jobs[job_id]
    total_scenes = len(job.scenes)
    
    async with httpx.AsyncClient(timeout=300) as client:
        previous_operation_name = None
        
        for i, scene in enumerate(job.scenes):
            if scene.status == "done":
                continue
                
            logger.info(f"[{job_id}] Generating Scene {scene.id}/{total_scenes}: {scene.visual_prompt[:50]}...")
            scene.status = "generating"
            save_jobs()
            
            # Retry logic disabled to prevent quota exhaustion
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
                    
                    # Add delay between scenes to avoid rate limits
                    if i > 0 and attempt == 0:
                        logger.info(f"[{job_id}] Waiting 40s before next scene to respect rate limits...")
                        await asyncio.sleep(40)

                    # Determine endpoint: Extend if we have a previous operation, else Text-to-Video
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
                        await asyncio.sleep(5) # Poll every 5 seconds
                        
                        # Timeout check (15 minutes)
                        if time.time() - poll_start_time > 900:
                            raise Exception("Video generation timed out after 15 minutes.")

                        status_res = await client.get(f"http://127.0.0.1:8002/status/{operation_name}")
                        status_data = status_res.json()
                        
                        state = status_data.get("state")
                        
                        # Log status every 60 seconds
                        if int(time.time() - poll_start_time) % 60 == 0:
                             logger.info(f"[{job_id}] Polling status for {operation_name}: {state}")

                        # Check for both 'succeeded' (Veo) and 'COMPLETE' (Helper)
                        if state == "succeeded" or status_data.get("status") == "COMPLETE":
                            break
                        elif state == "failed" or status_data.get("status") == "ERROR":
                            raise Exception(f"Video generation failed: {status_data.get('error') or status_data.get('message')}")
                    
                    # 3. Save Local
                    save_res = await client.get(f"http://127.0.0.1:8002/save_local/{operation_name}")
                    if save_res.status_code != 200:
                         raise Exception(f"Save local failed: {save_res.text}")
                         
                    save_data = save_res.json()
                    video_path = save_data.get("file_path")
                    
                    scene.video_path = video_path
                    scene.status = "done"
                    
                    # Update previous_operation_name for the next scene in the chain
                    previous_operation_name = operation_name
                    logger.info(f"[{job_id}] Scene {scene.id} completed. Operation: {operation_name}. Path: {video_path}")
                    
                    # Update Job Progress
                    job.progress = int(10 + ((i + 1) / total_scenes) * 80) # Scripting is 0-10, Filming 10-90
                    save_jobs()
                    break # Success, exit retry loop
                    
                except Exception as e:
                    logger.error(f"[{job_id}] Scene {scene.id} failed (Attempt {attempt+1}/{max_retries+1}): {e}")
                    if attempt < max_retries:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.info(f"[{job_id}] Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        scene.status = "failed"
                        save_jobs()
                        # Continue to next scene even if this one fails permanently
                        continue

        # All scenes processed
        await stitch_movie(job_id)
        
        job.status = "completed"
        job.progress = 100
        save_jobs()
        logger.info(f"[{job_id}] Job completed successfully.")

async def stitch_movie(job_id: str):
    """Combines all clips into the final movie."""
    logger.info(f"[{job_id}] Stitching movie")
    
    job = jobs[job_id]
    valid_scenes = [s for s in job.scenes if s.status == "done" and s.video_path]
    
    if not valid_scenes:
        logger.error(f"[{job_id}] No valid scenes to stitch.")
        return

    # Create file list for FFmpeg
    # Logic: If a scene is an extension, it contains the content of the previous scene(s).
    # So we should NOT include the previous scene in the stitch list if the current one extends it.
    
    final_scenes_to_stitch = []
    for s in valid_scenes:
        if s.is_extension and final_scenes_to_stitch:
            # Remove the previous scene because 's' already contains it
            final_scenes_to_stitch.pop()
        final_scenes_to_stitch.append(s)
        
    list_path = f"temp_list_{job_id}.txt"
    with open(list_path, "w") as f:
        for scene in final_scenes_to_stitch:
            # Escape paths for FFmpeg
            safe_path = scene.video_path.replace("\\", "/")
            f.write(f"file '{safe_path}'\n")
    
    output_filename = f"Movie_{job.topic.replace(' ', '_')[:30]}_{job_id}.mp4"
    output_path = os.path.join(os.getcwd(), "Generated_Video", output_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        # Run FFmpeg
        cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0", "-i", list_path,
            "-c", "copy", "-y", output_path
        ]
        
        logger.info(f"[{job_id}] Running FFmpeg: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        job.final_video_path = output_path
        save_jobs()
        logger.info(f"[{job_id}] Stitching complete: {output_path}")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"[{job_id}] FFmpeg failed: {e.stderr.decode()}")
        raise Exception(f"Stitching failed: {e.stderr.decode()}")
        
    finally:
        if os.path.exists(list_path):
            os.remove(list_path)

async def generate_script_task(job_id: str, request: MovieRequest):
    job = jobs[job_id]
    try:
        # 1. Scripting
        job.status = "scripting"
        job.progress = 5
        save_jobs()
        await generate_script(job_id, request.topic, request.duration_seconds, request.resolution)
        
        # Pause for approval
        job.status = "waiting_for_approval"
        job.progress = 10
        save_jobs()
        logger.info(f"[{job_id}] Script generated. Waiting for approval.")
        
    except Exception as e:
        logger.error(f"[{job_id}] Script generation failed: {e}")
        job.status = "failed"
        job.error = str(e)
        save_jobs()

# --- Endpoints ---

@app.post("/create_movie")
async def create_movie(request: MovieRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    new_job = MovieJob(
        job_id=job_id,
        topic=request.topic,
        status="starting",
        progress=0,
        created_at=datetime.now().isoformat(),
        model=request.model,
        resolution=request.resolution,
        aspect_ratio=request.aspect_ratio
    )
    jobs[job_id] = new_job
    save_jobs()
    
    # Start script generation only
    background_tasks.add_task(generate_script_task, job_id, request)
    
    return {"job_id": job_id, "status": "started"}

@app.post("/approve_script/{job_id}")
async def approve_script(job_id: str, request: ApprovalRequest, background_tasks: BackgroundTasks):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job.status != "waiting_for_approval":
        raise HTTPException(status_code=400, detail=f"Job is in {job.status} state, cannot approve.")
    
    # Update scenes if provided
    if request.scenes:
        # Update scenes with user edits
        updated_scenes = []
        for s in request.scenes:
            # Re-synthesize Veo prompt from potentially edited fields
            p = s.prompt
            veo_prompt = (
                f"{p.style.cinematic_style} style, {p.style.color_grade}. "
                f"{p.scene_description} "
                f"{p.visual_details.environment}, {p.visual_details.character}. "
                f"{p.camera_direction.movement}, {p.camera_direction.framing}, {p.camera_direction.focus}, {p.camera_direction.lens}. "
                f"{p.motion_and_actions.character_action} {p.motion_and_actions.environment_motion}"
            )
            s.visual_prompt = veo_prompt
            updated_scenes.append(s)
            
        job.scenes = updated_scenes
        save_jobs()
        logger.info(f"[{job_id}] Updated {len(job.scenes)} scenes with user edits.")

    # Start production
    background_tasks.add_task(production_loop, job_id)
    
    return {"status": "production_started"}

@app.get("/movie_status/{job_id}")
async def get_movie_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    # Debug log to verify scenes are present
    if job.status == "waiting_for_approval":
        logger.info(f"[{job_id}] Returning status: {job.status}, Scenes: {len(job.scenes)}")
        
    return job

@app.get("/")
def health_check():
    return {"status": "Director Service Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
