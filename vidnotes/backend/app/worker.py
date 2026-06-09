"""
Celery worker: orchestrates the full video → notes pipeline.
Each job goes through: download → transcribe → chunk/embed → summarize → extract
"""
import os
import json
from celery import Celery
from datetime import datetime
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery("vidnotes", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
)

# In-memory job store (replace with Redis/DB in production)
# For this demo, we persist job state to disk as JSON
JOB_STORE_DIR = "./job_store"
os.makedirs(JOB_STORE_DIR, exist_ok=True)


def _save_job(job_id: str, data: dict):
    with open(f"{JOB_STORE_DIR}/{job_id}.json", "w") as f:
        json.dump(data, f, default=str)


def _load_job(job_id: str) -> dict | None:
    path = f"{JOB_STORE_DIR}/{job_id}.json"
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def _update_job(job_id: str, **kwargs):
    job = _load_job(job_id) or {}
    job.update(kwargs)
    _save_job(job_id, job)


@celery_app.task(bind=True, name="process_video")
def process_video(self, job_id: str, source_type: str, source_value: str, language: str = "en"):
    """
    Main pipeline task.
    source_type: "url" | "file"
    source_value: URL string or local file path
    """
    import asyncio
    from app.services.downloader import download_video
    from app.services.transcriber import transcribe_sync
    from app.services.processor import chunk_segments, embed_and_store
    from app.services.summarizer import generate_notes
    from app.services.extractor import extract_timestamps, extract_action_items

    def update(stage: str, progress: int, status: str = "processing"):
        _update_job(job_id, status=status, progress=progress, stage=stage)
        self.update_state(
            state="PROGRESS",
            meta={"stage": stage, "progress": progress},
        )

    try:
        update("Downloading video", 5, "downloading")

        # 1. Get audio file
        if source_type == "url":
            audio_path = asyncio.run(download_video(source_value, job_id))
        else:
            audio_path = source_value  # already saved by API

        update("Transcribing with Whisper", 20, "transcribing")

        # 2. Transcribe
        transcript_data = transcribe_sync(audio_path)
        segments = transcript_data["segments"]
        full_text = transcript_data["text"]

        update("Chunking & embedding transcript", 45, "processing")

        # 3. Chunk + embed into ChromaDB
        chunks = chunk_segments(segments)
        embed_and_store(job_id, chunks)

        update("Generating structured notes with Claude", 60, "processing")

        # 4. Summarize + notes (single Claude call)
        notes_data = generate_notes(full_text, segments)

        update("Extracting timestamps", 75, "processing")

        # 5. Extract timestamps
        timestamps = extract_timestamps(segments)

        update("Extracting action items", 88, "processing")

        # 6. Extract action items
        actions = extract_action_items(full_text)

        update("Finalizing", 95, "processing")

        # 7. Persist final result
        result = {
            "summary": notes_data.get("summary", ""),
            "sections": notes_data.get("sections", []),
            "timestamps": [t.model_dump() for t in timestamps],
            "action_items": [a.model_dump() for a in actions],
            "transcript": full_text,
        }
        _update_job(job_id, status="done", progress=100, stage="Done", result=result)

        return {"status": "done", "job_id": job_id}

    except Exception as e:
        _update_job(job_id, status="failed", stage="Error", error=str(e))
        raise
