from typing import List, Optional, Dict
from pydantic import BaseModel

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
