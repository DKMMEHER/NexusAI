from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
import json
import os
import logging
from google.cloud import firestore
from google.api_core.exceptions import NotFound

# Import extracted components
from .models import VideoJob

logger = logging.getLogger("Database")

class DatabaseProvider(ABC):
    @abstractmethod
    def save_job(self, job: VideoJob):
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> Optional[VideoJob]:
        pass
        
    @abstractmethod
    def get_user_jobs(self, user_id: str) -> List[Dict[str, Any]]:
        pass

class JsonDatabase(DatabaseProvider):
    def __init__(self, db_file: str = "jobs.json"):
        self.db_file = db_file
        self.jobs = self._load_db()

    def _load_db(self):
        if not os.path.exists(self.db_file):
            return []
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def _save_db(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.jobs, f, indent=4)

    def save_job(self, job: VideoJob):
        # Determine if update or insert
        job_dict = job.model_dump()
        existing_idx = next((i for i, j in enumerate(self.jobs) if j["job_id"] == job.job_id), -1)
        
        if existing_idx >= 0:
            self.jobs[existing_idx] = job_dict
        else:
            self.jobs.insert(0, job_dict) # Newest first
            
        self._save_db()

    def get_job(self, job_id: str) -> Optional[VideoJob]:
        self.jobs = self._load_db() # Reload to get latest state
        job_data = next((j for j in self.jobs if j["job_id"] == job_id), None)
        if job_data:
            return VideoJob(**job_data)
        return None

    def get_user_jobs(self, user_id: str) -> List[Dict[str, Any]]:
        self.jobs = self._load_db()
        if not user_id:
            return self.jobs
        return [job for job in self.jobs if job.get('user_id') == user_id]

class FirestoreDatabase(DatabaseProvider):
    def __init__(self, project_id: str, collection: str = "video_jobs"):
        self.client = firestore.Client(project=project_id)
        self.collection_ref = self.client.collection(collection)
        logger.info(f"Initialized FirestoreDatabase with collection: {collection}")

    def save_job(self, job: VideoJob):
        job_dict = job.model_dump()
        doc_ref = self.collection_ref.document(job.job_id)
        doc_ref.set(job_dict)
        logger.info(f"Saved job {job.job_id} to Firestore")

    def get_job(self, job_id: str) -> Optional[VideoJob]:
        doc_ref = self.collection_ref.document(job_id)
        doc = doc_ref.get()
        if doc.exists:
            return VideoJob(**doc.to_dict())
        return None

    def get_user_jobs(self, user_id: str) -> List[Dict[str, Any]]:
        query = self.collection_ref.where("user_id", "==", user_id).order_by("created_at", direction=firestore.Query.DESCENDING)
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
