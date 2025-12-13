from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import json
import os
import logging
from .models import MovieJob

logger = logging.getLogger("Database")

class DatabaseProvider(ABC):
    @abstractmethod
    def save_job(self, job: MovieJob):
        pass
    
    @abstractmethod
    def get_job(self, job_id: str) -> Optional[MovieJob]:
        pass

    @abstractmethod
    def get_all_jobs(self) -> Dict[str, MovieJob]:
        pass

    @abstractmethod
    def get_user_jobs(self, user_id: str) -> List[MovieJob]:
        pass

class JsonDatabase(DatabaseProvider):
    def __init__(self, file_path: str = "jobs.json"):
        self.file_path = file_path
        self.jobs: Dict[str, MovieJob] = {}
        self.load_jobs()

    def load_jobs(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    self.jobs = {jid: MovieJob(**j_data) for jid, j_data in data.items()}
                logger.info(f"Loaded {len(self.jobs)} jobs from {self.file_path}")
            except Exception as e:
                logger.error(f"Failed to load jobs: {e}")

    def save_disk(self):
        try:
            data = {jid: job.dict() for jid, job in self.jobs.items()}
            with open(self.file_path, "w") as f:
                json.dump(data, f, default=str, indent=2)
        except Exception as e:
            logger.error(f"Failed to save jobs to disk: {e}")

    def save_job(self, job: MovieJob):
        self.jobs[job.job_id] = job
        self.save_disk()
    
    def get_job(self, job_id: str) -> Optional[MovieJob]:
        return self.jobs.get(job_id)

    def get_all_jobs(self) -> Dict[str, MovieJob]:
        return self.jobs

    def get_user_jobs(self, user_id: str) -> List[MovieJob]:
        return [job for job in self.jobs.values() if job.user_id == user_id]

class FirestoreDatabase(DatabaseProvider):
    def __init__(self, project_id: str, collection: str = "nexus_director_jobs"):
        try:
            from google.cloud import firestore
            self.db = firestore.Client(project=project_id)
            self.collection = self.db.collection(collection)
            logger.info(f"Connected to Firestore Project: {project_id}, Collection: {collection}")
        except Exception as e:
            logger.error(f"Failed to connect to Firestore: {e}")
            raise e

    def save_job(self, job: MovieJob):
        try:
            # Convert Pydantic model to dict (using jsonable_encoder style or .dict())
            doc_ref = self.collection.document(job.job_id)
            doc_ref.set(json.loads(job.json())) # Utilizing .json() then loads ensures generic serialization
            logger.info(f"Saved job {job.job_id} to Firestore")
        except Exception as e:
            logger.error(f"Failed to save job to Firestore: {e}")

    def get_job(self, job_id: str) -> Optional[MovieJob]:
        try:
            doc_ref = self.collection.document(job_id)
            doc = doc_ref.get()
            if doc.exists:
                return MovieJob(**doc.to_dict())
            return None
        except Exception as e:
            logger.error(f"Failed to get job from Firestore: {e}")
            return None

    def get_all_jobs(self) -> Dict[str, MovieJob]:
        try:
            jobs = {}
            docs = self.collection.stream()
            for doc in docs:
                try:
                    job = MovieJob(**doc.to_dict())
                    jobs[job.job_id] = job
                except Exception as parse_err:
                     logger.warning(f"Skipping invalid job doc {doc.id}: {parse_err}")
            return jobs
        except Exception as e:
            logger.error(f"Failed to get all jobs from Firestore: {e}")
            return {}

    def get_user_jobs(self, user_id: str) -> List[MovieJob]:
        try:
            jobs = []
            # Query Firestore for jobs where user_id matches
            docs = self.collection.where("user_id", "==", user_id).stream()
            for doc in docs:
                try:
                    job = MovieJob(**doc.to_dict())
                    jobs.append(job)
                except Exception as parse_err:
                     logger.warning(f"Skipping invalid job doc {doc.id}: {parse_err}")
            return jobs
        except Exception as e:
            logger.error(f"Failed to get user jobs from Firestore: {e}")
            return []
