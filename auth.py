import os
import logging
from fastapi import HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth

# Initialize Logging
logger = logging.getLogger("Auth")

# Global variables
security = HTTPBearer()

def initialize_firebase():
    """Initializes Firebase Admin SDK if not already initialized."""
    try:
        if not firebase_admin._apps:
            # Check for serviceAccountKey.json in the current working directory or specific path
            cred_path = os.getenv("FIREBASE_CREDENTIALS", "serviceAccountKey.json")
            
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized successfully.")
            else:
                logger.warning(f"firebase-admin credentials not found at {cred_path}. Auth verification will fail or be mocked.")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")

# Initialize immediately on import attempt (optional, or call in startup)
initialize_firebase()

async def verify_token(request: Request, token: HTTPAuthorizationCredentials = Security(security)):
    """
    Verifies the Firebase ID token.
    Returns the decoded token (dict) if valid, raises HTTPException otherwise.
    """
    if not firebase_admin._apps:
        # Fail open or closed? For Strict Verification, we fail closed.
        # But for development without keys, maybe we log warning?
        # Let's enforce it: server needs keys.
        logger.error("Firebase Admin not initialized. Cannot verify token.")
        raise HTTPException(status_code=500, detail="Authentication configuration error.")

    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(token.credentials)
        
        # Check if the user_id in request matches the token (Strict Isolation)
        # This requires reading form data or query params, which consumes the stream.
        # Ideally, we return the user context and the endpoint checks match.
        # But to be helpful, let's just return the uid.
        uid = decoded_token['uid']
        
        # Determine user_id from request (optional strict check)
        # If the endpoint takes 'user_id' as form/query, we could compare.
        # For now, we trust the token's UID is the Source of Truth.
        request.state.user_id = uid 
        return uid
        
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid Authentication Token")

def get_current_user_id(request: Request):
    # Dependency to get user_id from request state (set by middleware/dependency)
    # This implies verify_token was called.
    return getattr(request.state, "user_id", None)
