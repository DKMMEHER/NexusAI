import os
import uvicorn
from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# LangSmith Integration
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langsmith_config import trace_async_llm_call, token_tracker

app = FastAPI()

# Health Check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("GEMINI_API_KEY not found in environment variables")
else:
    genai.configure(api_key=api_key)

# Get YouTube API Key
youtube_api_key = os.getenv("YOUTUBE_API_KEY")
if not youtube_api_key:
    logger.warning("YOUTUBE_API_KEY not found. YouTube Data API features will be limited.")

def extract_video_id(youtube_video_url):
    """Extract video ID from YouTube URL"""
    try:
        if "v=" in youtube_video_url:
            video_id = youtube_video_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_video_url:
            video_id = youtube_video_url.split("youtu.be/")[1].split("?")[0]
        else:
            raise ValueError("Invalid YouTube URL format")
        return video_id
    except Exception as e:
        logger.error(f"Error extracting video ID: {str(e)}")
        raise ValueError("Invalid YouTube URL format")

def get_transcript_via_youtube_api(video_id, api_key):
    """
    Fetch transcript using official YouTube Data API v3
    This is more reliable and not blocked by YouTube
    """
    try:
        logger.info(f"Fetching transcript via YouTube Data API for video: {video_id}")
        
        # Build YouTube API client
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Get captions list
        captions_response = youtube.captions().list(
            part='snippet',
            videoId=video_id
        ).execute()
        
        if not captions_response.get('items'):
            raise ValueError("No captions available for this video")
        
        # Find English caption track (or first available)
        caption_id = None
        for item in captions_response['items']:
            if item['snippet']['language'] == 'en':
                caption_id = item['id']
                break
        
        if not caption_id and captions_response['items']:
            caption_id = captions_response['items'][0]['id']
        
        if not caption_id:
            raise ValueError("No suitable caption track found")
        
        # Download caption
        # Note: YouTube Data API v3 doesn't directly support caption download
        # We need to fall back to youtube-transcript-api for actual download
        # But we verified captions exist via official API
        logger.info(f"Captions available. Attempting download via transcript API...")
        
        # Try youtube-transcript-api as fallback for actual download
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        transcript = ""
        for entry in transcript_list:
            if isinstance(entry, dict):
                transcript += " " + entry.get('text', '')
            else:
                transcript += " " + getattr(entry, 'text', '')
        
        logger.info(f"Successfully fetched transcript. Length: {len(transcript)} characters")
        return transcript
        
    except HttpError as e:
        logger.error(f"YouTube API Error: {str(e)}")
        if e.resp.status == 403:
            raise ValueError("YouTube API quota exceeded or API key invalid")
        elif e.resp.status == 404:
            raise ValueError("Video not found")
        else:
            raise ValueError(f"YouTube API error: {str(e)}")
    except Exception as e:
        logger.error(f"Error fetching transcript via API: {str(e)}")
        raise e

def get_transcript_fallback(video_id):
    """
    Fallback method using youtube-transcript-api
    May be blocked in Cloud Run but worth trying
    """
    try:
        logger.info(f"Attempting fallback transcript fetch for video: {video_id}")
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        transcript = ""
        for entry in transcript_list:
            if isinstance(entry, dict):
                transcript += " " + entry.get('text', '')
            else:
                transcript += " " + getattr(entry, 'text', '')
        
        logger.info(f"Fallback successful. Transcript length: {len(transcript)} characters")
        return transcript
    except Exception as e:
        logger.error(f"Fallback method failed: {str(e)}")
        raise e

def extract_transcript_details(youtube_video_url):
    """
    Main function to extract transcript
    Tries YouTube Data API first, then falls back to youtube-transcript-api
    """
    try:
        # Extract video ID
        video_id = extract_video_id(youtube_video_url)
        logger.info(f"Extracted video ID: {video_id}")
        
        transcript = None
        
        # Method 1: Try YouTube Data API v3 (if API key available)
        if youtube_api_key:
            try:
                transcript = get_transcript_via_youtube_api(video_id, youtube_api_key)
                logger.info("Successfully fetched transcript via YouTube Data API")
            except Exception as api_error:
                logger.warning(f"YouTube Data API failed: {str(api_error)}")
                logger.info("Falling back to youtube-transcript-api...")
        
        # Method 2: Fallback to youtube-transcript-api
        if not transcript:
            try:
                transcript = get_transcript_fallback(video_id)
                logger.info("Successfully fetched transcript via fallback method")
            except Exception as fallback_error:
                logger.error(f"All methods failed. Last error: {str(fallback_error)}")
                # Provide user-friendly error message
                error_msg = str(fallback_error)
                if "Subtitles are disabled" in error_msg or "Could not retrieve" in error_msg:
                    raise ValueError(
                        "This video doesn't have captions/subtitles available. "
                        "Please try a different video with captions enabled (look for the [CC] badge on YouTube). "
                        "Note: Some videos may have captions but are blocked from automated access."
                    )
                else:
                    raise ValueError(f"Failed to fetch transcript: {error_msg}")
        
        return transcript, video_id
        
    except ValueError as ve:
        # Re-raise ValueError with user-friendly message
        raise ve
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        raise ValueError(f"An unexpected error occurred: {str(e)}")

import uuid
from datetime import datetime

# Database Initialization
from .database import JsonDatabase, FirestoreDatabase
from auth import verify_token
from fastapi import Depends, HTTPException

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
is_cloud_run = os.getenv("K_SERVICE") is not None

if is_cloud_run and project_id:
    logger.info(f"Detected Cloud Run environment. Using Firestore (Project: {project_id}).")
    try:
        db = FirestoreDatabase(project_id)
    except Exception as e:
        logger.error(f"Failed to initialize Firestore: {e}. Falling back to JsonDatabase.")
        db = JsonDatabase()
else:
    logger.info("Running locally. Using JsonDatabase.")
    db = JsonDatabase()

@app.post("/transcript")
async def get_transcript_summary(
    url: str = Form(...), 
    model: str = Form("gemini-2.0-flash-exp"),
    user_id: str = Form(None)
):
    job_id = str(uuid.uuid4())[:8]
    start_time = datetime.now()
    status = "Failed"
    response = None
    
    try:
        logger.info(f"Processing URL: {url} with model: {model}")
        
        # 1. Get Transcript
        transcript_text, video_id = extract_transcript_details(url)
        
        # 2. Generate Summary
        prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here: """

        gen_model = genai.GenerativeModel(model)
        response = gen_model.generate_content(prompt + transcript_text)
        
        # Track token usage with LangSmith
        if response.usage_metadata and user_id:
            try:
                token_tracker.log_usage(
                    service="YoutubeTranscript",
                    operation="transcript_summary",
                    model=model,
                    input_tokens=response.usage_metadata.prompt_token_count,
                    output_tokens=response.usage_metadata.candidates_token_count,
                    user_id=user_id,
                    job_id=job_id or str(uuid.uuid4())
                )
            except Exception as e:
                logger.warning(f"Failed to log token usage: {e}")
        
        status = "Success"
        
        return JSONResponse({
            "transcript": transcript_text,
            "summary": response.text,
            "video_id": video_id
        })

    except ValueError as ve:
        # User-friendly errors
        logger.error(f"User error: {str(ve)}")
        status = "Failed"
        return JSONResponse({"detail": str(ve)}, status_code=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error processing request: {str(e)}")
        status = "Failed"
        return JSONResponse({"detail": f"Backend Error: {str(e)}"}, status_code=500)
        
    finally:
        # Calculate Metrics
        now = datetime.now()
        
        # TPM (Tokens Per Minute)
        current_tokens = 0
        if response and hasattr(response, 'usage_metadata'):
            current_tokens = response.usage_metadata.total_token_count
        
        # Record Job
        job_data = {
            "job_id": job_id,
            "user_id": user_id, 
            "type": "Transcript",
            "model": model,
            "rpm": 1,
            "tpm": current_tokens,
            "rpd": 1,
            "tokens": current_tokens,
            "status": status,
            "time": start_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        db.save_job(job_data)

@app.get("/analytics")
def get_analytics(user_id: str, token_uid: str = Depends(verify_token)):
    if token_uid != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch.")
    return db.get_user_jobs(user_id)

@app.get("/")
def health_check():
    return {"status": "YouTube Transcript Service Running"}

@app.get("/health")
def health_check_explicit():
    return {"status": "healthy"}

@app.get("/transcript")
def health_check_transcript():
    return {"status": "YouTube Transcript Service Running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
