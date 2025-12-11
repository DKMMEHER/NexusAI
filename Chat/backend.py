import os
import uvicorn
from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import google.generativeai as genai
from dotenv import load_dotenv
import logging
from pydantic import BaseModel
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="Chat & Q&A Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501",
                   "http://localhost:5173", "http://127.0.0.1:5173",
                   "http://localhost:5174", "http://127.0.0.1:5174",
                   "http://localhost:8080", "http://127.0.0.1:8080",
                   "https://nexusai-962267416185.asia-south1.run.app",
                   "*"],
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

# In-memory chat history storage (simple version)
# In a production app, this should be in a database or Redis
# Key: session_id, Value: ChatSession object
chat_sessions = {}

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = [] # Optional: Client can send full history if they want stateless backend
    model: str = "gemini-2.5-flash"

import uuid
from datetime import datetime

# In-memory storage for analytics
# List of dicts: { "job_id": str, "type": str, "model": str, "rpm": str, "tpm": str, "rpd": str, "status": str, "time": str }
job_history = []

@app.post("/chat")
async def chat_endpoint(
    message: str = Form(...), 
    history: str = Form(None), 
    model: str = Form("gemini-2.0-flash-exp"),
    tools: str = Form(None) # JSON string of list of tools: ["google_search", "code_execution"]
):
    job_id = str(uuid.uuid4())[:8]
    start_time = datetime.now()
    status = "Failed"
    token_usage = "0"
    
    try:
        logger.info(f"Received chat message: {message} | Model: {model} | Tools: {tools}")
        
        # Validate Model
        valid_models = [
            "gemini-2.0-flash-exp", 
            "gemini-2.0-flash-thinking-exp-1219", 
            "gemini-3-pro-preview"
        ]
        
        # Fallback if model not in list (or allow it if it's a valid Gemini string)
        if model not in valid_models:
            logger.warning(f"Requested model {model} not in explicit list, passing through anyway.")

        # Configure Tools
        enabled_tools = []
        tool_type = "Chat"
        if tools:
            import json
            try:
                tool_names = json.loads(tools)
                for name in tool_names:
                    if name == "google_search":
                        enabled_tools.append({"google_search": {}})
                        tool_type = "Search"
                    elif name == "code_execution":
                        enabled_tools.append({"code_execution": {}})
                        tool_type = "Code"
            except Exception as e:
                logger.warning(f"Failed to parse tools: {e}")

        # Configure the model with system instructions
        system_instruction = "You are a helpful AI assistant. When providing code, use standard Markdown code blocks (```language ... ```). NEVER wrap the entire response or code blocks in triple quotes (\"\"\") or single quotes ('''). Output raw text and markdown only. Do NOT use triple quotes (\"\"\" or ''') for comments or docstrings in Python code; use hash (#) comments instead."
        
        # Initialize model with tools
        gen_model = genai.GenerativeModel(
            model_name=model, 
            tools=enabled_tools if enabled_tools else None,
            system_instruction=system_instruction
        )
        
        # Parse History
        chat_history = []
        if history:
            import json
            try:
                raw_history = json.loads(history)
                for msg in raw_history:
                    # Gemini expects 'user' or 'model' roles
                    role = "user" if msg['role'] == 'user' else "model"
                    # Filter out empty content or system messages if any
                    if msg.get('content'):
                        chat_history.append({'role': role, 'parts': [msg['content']]})
            except Exception as e:
                logger.warning(f"Failed to parse history: {e}")

        # Start Chat
        chat = gen_model.start_chat(history=chat_history)
        
        # Send Message
        response = chat.send_message(message)
        
        # Extract Text and Grounding Metadata
        response_text = response.text
        
        # Post-processing: Strip outer triple quotes if present (double or single)
        response_text = response_text.strip()
        if response_text.startswith('"""') and response_text.endswith('"""'):
            response_text = response_text[3:-3].strip()
        elif response_text.startswith("'''") and response_text.endswith("'''"):
            response_text = response_text[3:-3].strip()
        
        # Check for grounding metadata (citations)
        grounding_info = None
        if response.candidates and response.candidates[0].grounding_metadata:
             # Just a flag or raw data for now, frontend can parse if needed
             grounding_info = "Grounding metadata available" 
        
        # Capture Usage
        if response.usage_metadata:
            token_usage = str(response.usage_metadata.total_token_count)
        
        status = "Success"

        return JSONResponse({
            "response": response_text,
            "history": history, # Echo back
            "grounding": grounding_info
        })

    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        status = "Failed"
        return JSONResponse({"detail": str(e)}, status_code=500)
    
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
        tpm = 0
        current_tokens = 0
        try:
             # Try to convert token_usage to int safely
             current_tokens = int(token_usage)
        except:
             current_tokens = 0

        # Sum tokens from recent jobs
        for job in recent_jobs:
            tpm += int(job.get('tokens', 0))
        tpm += current_tokens

        # Record Job
        job_history.insert(0, {
            "job_id": job_id,
            "type": tool_type,
            "model": model,
            "rpm": rpm,
            "tpm": tpm,
            "rpd": rpd,
            "tokens": current_tokens, # Store for future TPM calc
            "status": status,
            "time": start_time.strftime("%Y-%m-%d %H:%M:%S")
        })
        save_history(job_history)

@app.get("/analytics")
def get_analytics():
    return job_history

@app.get("/")
def health_check():
    return {"status": "Chat Service Running"}

@app.get("/health")
def health_check_explicit():
    return {"status": "healthy"}

@app.get("/chat")
def health_check_chat():
    return {"status": "Chat Service Running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
