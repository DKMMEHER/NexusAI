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

# LangSmith Integration (optional)
try:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from langsmith_config import token_tracker
except Exception as e:
    token_tracker = None
    import logging
    logging.warning(f"LangSmith integration not available: {e}")

app = FastAPI(title="Chat & Q&A Backend")

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

@app.post("/chat")
async def chat_endpoint(
    message: str = Form(...), 
    history: str = Form(None), 
    model: str = Form("gemini-2.0-flash-exp"),
    tools: str = Form(None), # JSON string of list of tools: ["google_search", "code_execution"]
    user_id: str = Form(None)
):
    job_id = str(uuid.uuid4())[:8]
    start_time = datetime.now()
    status = "Failed"
    token_usage = "0"
    
    try:
        logger.info(f"Received chat message: {message} | Model: {model} | Tools: {tools}")
        
        # ... [validation and tool parsing logic same as before, simplified for diff] ...
        # (This replacement is massive because we are stripping lines 70-209. 
        # Ideally I'd use multi_replace but since I want to replace the whole block efficiently I'll include the necessary logic)
        
        # Initialize enabled_tools, tool_type etc.
        # ... skipping some unchanged lines for brevity in instruction, assuming complete block replacement ...
        # Actually I must include all logic if I replace the whole block.
        
        valid_models = [
            "gemini-2.0-flash-exp", 
            "gemini-2.0-flash-thinking-exp-1219", 
            "gemini-3-pro-preview"
        ]
        
        if model not in valid_models:
            logger.warning(f"Requested model {model} not in explicit list, passing through anyway.")

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

        system_instruction = "You are a helpful AI assistant. When providing code, use standard Markdown code blocks (```language ... ```). NEVER wrap the entire response or code blocks in triple quotes (\"\"\") or single quotes ('''). Output raw text and markdown only. Do NOT use triple quotes (\"\"\" or ''') for comments or docstrings in Python code; use hash (#) comments instead."
        
        gen_model = genai.GenerativeModel(
            model_name=model, 
            tools=enabled_tools if enabled_tools else None,
            system_instruction=system_instruction
        )
        
        chat_history = []
        if history:
            import json
            try:
                raw_history = json.loads(history)
                for msg in raw_history:
                    role = "user" if msg['role'] == 'user' else "model"
                    if msg.get('content'):
                        chat_history.append({'role': role, 'parts': [msg['content']]})
            except Exception as e:
                logger.warning(f"Failed to parse history: {e}")

        chat = gen_model.start_chat(history=chat_history)
        response = chat.send_message(message)
        response_text = response.text
        
        response_text = response_text.strip()
        if response_text.startswith('"""') and response_text.endswith('"""'):
            response_text = response_text[3:-3].strip()
        elif response_text.startswith("'''") and response_text.endswith("'''"):
            response_text = response_text[3:-3].strip()
        
        grounding_info = None
        if response.candidates and response.candidates[0].grounding_metadata:
             grounding_info = "Grounding metadata available" 
        
        if response.usage_metadata:
            token_usage = str(response.usage_metadata.total_token_count)
            
            # Track token usage with LangSmith
            if user_id:
                try:
                    token_tracker.log_usage(
                        service="Chat",
                        operation="chat_message",
                        model=model,
                        input_tokens=response.usage_metadata.prompt_token_count,
                        output_tokens=response.usage_metadata.candidates_token_count,
                        user_id=user_id,
                        job_id=job_id
                    )
                except Exception as e:
                    logger.warning(f"Failed to log token usage: {e}")
        
        status = "Success"

        return JSONResponse({
            "response": response_text,
            "history": history, 
            "grounding": grounding_info
        })

    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        status = "Failed"
        return JSONResponse({"detail": str(e)}, status_code=500)
    
    finally:
        # Calculate Metrics
        current_tokens = 0
        try:
             current_tokens = int(token_usage)
        except:
             current_tokens = 0

        # Record Job
        job_data = {
            "job_id": job_id,
            "user_id": user_id, 
            "type": tool_type,
            "model": model,
            "rpm": 1,
            "tpm": current_tokens,
            "rpd": 1,
            "tokens": current_tokens,
        }
        db.save_job(job_data)

@app.get("/analytics")
def get_analytics(user_id: str, token_uid: str = Depends(verify_token)):
    if token_uid != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch.")
    return db.get_user_jobs(user_id)

@app.get("/chat")
def health_check_chat():
    return {"status": "Chat Service Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
