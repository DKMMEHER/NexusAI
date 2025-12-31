import os
import uvicorn
from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

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

def extract_transcript_details(youtube_video_url):
    try:
        if "v=" in youtube_video_url:
            video_id = youtube_video_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_video_url:
            video_id = youtube_video_url.split("youtu.be/")[1].split("?")[0]
        else:
            raise ValueError("Invalid YouTube URL format")

        # Configure Proxy if available
        proxies = None
        proxy_url = os.getenv("YOUTUBE_PROXY")
        if proxy_url:
            proxies = {"http": proxy_url, "https": proxy_url}
            logger.info(f"Using YouTube Proxy: {proxy_url}")

        # Fetch transcript using the correct API
        try:
            logger.info(f"Fetching transcript for video ID: {video_id}")
            # Use get_transcript - this is the correct method for youtube-transcript-api 0.6.1
            transcript_text_list = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies)
            logger.info(f"Successfully fetched transcript with {len(transcript_text_list)} entries")
        except Exception as api_error:
            logger.error(f"API Error: {str(api_error)}")
            # Try without proxies as fallback
            try:
                logger.info("Retrying without proxy...")
                transcript_text_list = YouTubeTranscriptApi.get_transcript(video_id)
                logger.info(f"Successfully fetched transcript without proxy")
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {str(fallback_error)}")
                raise fallback_error

        transcript = ""
        for i in transcript_text_list:
            # Handle both dictionary and object access
            if isinstance(i, dict):
                transcript += " " + i.get('text', '')
            else:
                transcript += " " + getattr(i, 'text', '')

        logger.info(f"Transcript length: {len(transcript)} characters")
        return transcript, video_id

    except Exception as e:
        logger.error(f"Error extracting transcript: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        raise e

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
    model: str = Form("gemini-2.5-flash"),
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
        
        status = "Success"
        
        return JSONResponse({
            "transcript": transcript_text,
            "summary": response.text,
            "video_id": video_id
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error processing request: {str(e)}")
        status = "Failed"
        return JSONResponse({"detail": f"Backend Error: {str(e)}"}, status_code=500)
        
    finally:
        # Calculate Metrics - placeholders or simplistic
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
