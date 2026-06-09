"""
Simple in-memory job store.
For production: replace with Redis or a DB-backed queue (Celery, ARQ).
"""
from typing import Dict, Any, Optional
import time
import uuid


class JobStore:
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}

    def create(self, source_type: str, source: str) -> str:
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "id": job_id,
            "source_type": source_type,   # "url" | "file"
            "source": source,
            "status": "queued",           # queued | transcribing | analyzing | done | error
            "progress": 0,
            "stage_message": "Queued",
            "transcript": None,
            "result": None,
            "error": None,
            "created_at": time.time(),
        }
        return job_id

    def get(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.jobs.get(job_id)

    def update(self, job_id: str, **kwargs):
        if job_id in self.jobs:
            self.jobs[job_id].update(kwargs)


job_store = JobStore()
