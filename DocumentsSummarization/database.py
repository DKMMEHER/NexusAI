from abc import ABC, abstractmethod
import json
import os
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger("Database")

class DatabaseProvider(ABC):
    @abstractmethod
    def save_job(self, job: Dict[str, Any]):
        pass

    @abstractmethod
    def get_user_jobs(self, user_id: str) -> List[Dict[str, Any]]:
        pass

class JsonDatabase(DatabaseProvider):
    def __init__(self, db_file="analytics.json"):
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

    def save_job(self, job: Dict[str, Any]):
        # Insert at beginning to keep latest first
        self.jobs = self._load_db() # Reload to get latest data
        self.jobs.insert(0, job)
        self._save_db()

    def get_user_jobs(self, user_id: str) -> List[Dict[str, Any]]:
        self.jobs = self._load_db() # Reload to ensure freshness
        if not user_id:
            return self.jobs
        return [job for job in self.jobs if job.get('user_id') == user_id]

class FirestoreDatabase(DatabaseProvider):
    def __init__(self, project_id: str, collection_name: str = "doc_sum_analytics"):
        from google.cloud import firestore
        self.db = firestore.Client(project=project_id)
        self.collection = collection_name
        logger.info(f"Initialized FirestoreDatabase (Project: {project_id}, Collection: {collection_name})")

    def save_job(self, job: Dict[str, Any]):
        try:
            job_id = job.get("job_id")
            if not job_id:
                logger.error("Job missing job_id, cannot save to Firestore")
                return
                
            doc_ref = self.db.collection(self.collection).document(str(job_id))
            doc_ref.set(job)
            logger.info(f"Saved job {job_id} to Firestore")
        except Exception as e:
            logger.error(f"Failed to save job to Firestore: {e}")
            raise e

    def get_user_jobs(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            query = self.db.collection(self.collection)
            if user_id:
                query = query.where("user_id", "==", user_id)
            
            docs = query.stream()
            jobs = [doc.to_dict() for doc in docs]
            
            # Sort by time descending (assuming 'time' field exists and is ISO string)
            jobs.sort(key=lambda x: x.get('time', ''), reverse=True)
            return jobs
        except Exception as e:
            logger.error(f"Failed to fetch jobs from Firestore: {e}")
            return []
