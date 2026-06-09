"""
Ingest endpoints — accept YouTube URL or file upload.
Returns a job_id that the client polls/streams for progress.
"""
import os
import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks

from app.core.config import settings
from app.core.jobs import job_store
from app.models.schemas import IngestURLRequest, IngestResponse
from app.pipeline import run_pipeline

router = APIRouter()


@router.post("/url", response_model=IngestResponse)
async def ingest_url(body: IngestURLRequest, background_tasks: BackgroundTasks):
    job_id = job_store.create(source_type="url", source=body.url)
    background_tasks.add_task(run_pipeline, job_id)
    return IngestResponse(job_id=job_id, message="Job queued. Stream progress at /api/process/{job_id}/stream")


@router.post("/file", response_model=IngestResponse)
async def ingest_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    allowed = {".mp4", ".mp3", ".wav", ".m4a", ".webm", ".mkv", ".mov"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported file type: {ext}. Allowed: {allowed}")

    # Check size
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(413, f"File too large ({size_mb:.1f} MB). Max: {settings.MAX_UPLOAD_SIZE_MB} MB")

    job_id = job_store.create(source_type="file", source=file.filename)
    save_path = os.path.join(settings.UPLOAD_DIR, f"{job_id}{ext}")

    with open(save_path, "wb") as f:
        f.write(contents)

    job_store.update(job_id, file_path=save_path)
    background_tasks.add_task(run_pipeline, job_id)

    return IngestResponse(job_id=job_id, message="Job queued.")
