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
