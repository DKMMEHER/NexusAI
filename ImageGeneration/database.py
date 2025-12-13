from abc import ABC, abstractmethod
import json
import os
import logging
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger("Database")

class ImageJob(BaseModel):
    job_id: str
    user_id: str
    type: str  # generate, edit, try_on, etc.
    prompt: str
    image_path: str
    timestamp: str
    model: str
    status: str = "completed"

class DatabaseProvider(ABC):
    @abstractmethod
    def save_job(self, job: ImageJob):
        pass

    @abstractmethod
    def get_user_jobs(self, user_id: str) -> List[dict]:
        pass

class JsonDatabase(DatabaseProvider):
    def __init__(self, db_file="images.json"):
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
            json.dump(self.jobs, f, indent=2)

    def save_job(self, job: ImageJob):
        self.jobs.append(job.dict())
        self._save_db()

    def get_user_jobs(self, user_id: str) -> List[dict]:
        return [job for job in self.jobs if job.get('user_id') == user_id]

class FirestoreDatabase(DatabaseProvider):
    def __init__(self, project_id: str, collection_name: str = "image_jobs"):
        from google.cloud import firestore
        self.db = firestore.Client(project=project_id)
        self.collection = collection_name
        logger.info(f"Initialized FirestoreDatabase (Project: {project_id}, Collection: {collection_name})")

    def save_job(self, job: ImageJob):
        try:
            doc_ref = self.db.collection(self.collection).document(job.job_id)
            doc_ref.set(job.dict())
            logger.info(f"Saved job {job.job_id} to Firestore")
        except Exception as e:
            logger.error(f"Failed to save job to Firestore: {e}")
            raise e

    def get_user_jobs(self, user_id: str) -> List[dict]:
        try:
            # Order by timestamp descending
            docs = (
                self.db.collection(self.collection)
                .where("user_id", "==", user_id)
                .stream()
            )
            
            jobs = [doc.to_dict() for doc in docs]
            # Sort manually if needed, or composite index
            jobs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return jobs
        except Exception as e:
            logger.error(f"Failed to fetch jobs from Firestore: {e}")
            return []
