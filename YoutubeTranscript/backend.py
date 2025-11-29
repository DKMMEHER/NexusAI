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

        # Use instance method fetch() as per installed version
        transcript_text_list = YouTubeTranscriptApi().fetch(video_id)

        transcript = ""
        for i in transcript_text_list:
            # Handle both dictionary and object access
            if isinstance(i, dict):
                transcript += " " + i.get('text', '')
            else:
                transcript += " " + getattr(i, 'text', '')

        return transcript, video_id

    except Exception as e:
        logger.error(f"Error extracting transcript: {str(e)}")
        raise e

import uuid
from datetime import datetime

# In-memory storage for analytics
job_history = []

@app.post("/transcript")
async def get_transcript_summary(url: str = Form(...), model: str = Form("gemini-2.5-flash")):
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
        # Calculate Metrics
        now = datetime.now()
        one_minute_ago = now.timestamp() - 60
        one_day_ago = now.timestamp() - 86400
        
        # RPM (Requests Per Minute)
        recent_jobs = [j for j in job_history if datetime.strptime(j['time'], "%Y-%m-%d %H:%M:%S").timestamp() > one_minute_ago]
        rpm = len(recent_jobs) + 1 # Include current job
        
        # RPD (Requests Per Day)
        daily_jobs = [j for j in job_history if datetime.strptime(j['time'], "%Y-%m-%d %H:%M:%S").timestamp() > one_day_ago]
        rpd = len(daily_jobs) + 1 # Include current job

        # TPM (Tokens Per Minute)
        # Note: This requires usage_metadata from response, which we'll try to extract
        tpm = 0
        current_tokens = 0
        if response and hasattr(response, 'usage_metadata'):
            current_tokens = response.usage_metadata.total_token_count
        
        # Sum tokens from recent jobs (assuming we store token count in history, which we will start doing)
        for job in recent_jobs:
            tpm += job.get('tokens', 0)
        tpm += current_tokens

        # Record Job
        job_history.insert(0, {
            "job_id": job_id,
            "type": "Transcript",
            "model": model,
            "rpm": rpm,
            "tpm": tpm,
            "rpd": rpd,
            "tokens": current_tokens, # Store for future TPM calc
            "status": status,
            "time": start_time.strftime("%Y-%m-%d %H:%M:%S")
        })

@app.get("/analytics")
def get_analytics():
    return job_history

@app.get("/")
def health_check():
    return {"status": "YouTube Transcript Service Running"}

@app.get("/transcript")
def health_check_transcript():
    return {"status": "YouTube Transcript Service Running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
