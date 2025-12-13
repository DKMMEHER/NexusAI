from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class VideoJob(BaseModel):
    job_id: str
    user_id: Optional[str] = None
    type: str # text_to_video, image_to_video, etc.
    prompt: str
    status: str # pending, flimimg, completed, failed
    model: str
    created_at: str
    
    # Optional parameters
    duration: Optional[int] = None
    resolution: Optional[str] = None
    aspect_ratio: Optional[str] = None
    
    # Result
    video_path: Optional[str] = None
    operation_name: Optional[str] = None
    error: Optional[str] = None
    
    # Extension specific
    base_video_path: Optional[str] = None
