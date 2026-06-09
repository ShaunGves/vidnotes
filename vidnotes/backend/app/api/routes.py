"""
FastAPI route handlers for VidNotes API.
"""
import uuid
import json
import os
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import PlainTextResponse

from app.models.schemas import (
    SubmitJobRequest, JobResponse, JobStatus, JobResult,
    NoteSection, Timestamp, ActionItem, QueryRequest, QueryResponse
)
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/v1")

JOB_STORE_DIR = "./job_store"
os.makedirs(JOB_STORE_DIR, exist_ok=True)


def _load_job(job_id: str) -> dict:
    path = f"{JOB_STORE_DIR}/{job_id}.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Job not found")
    with open(path) as f:
        return json.load(f)


def _save_job(job_id: str, data: dict):
    with open(f"{JOB_STORE_DIR}/{job_id}.json", "w") as f:
        json.dump(data, f, default=str)


def _job_to_response(job: dict) -> JobResponse:
    result = None
    if job.get("result"):
        r = job["result"]
        result = JobResult(
            notes=[NoteSection(**s) for s in r.get("sections", [])],
            timestamps=[Timestamp(**t) for t in r.get("timestamps", [])],
            action_items=[ActionItem(**a) for a in r.get("action_items", [])],
            summary=r.get("summary", ""),
            transcript=r.get("transcript", ""),
        )
    return JobResponse(
        id=job["id"],
        status=JobStatus(job.get("status", "pending")),
        progress=job.get("progress", 0),
        stage=job.get("stage", ""),
        title=job.get("title"),
        duration=job.get("duration"),
        created_at=datetime.fromisoformat(job["created_at"]),
        result=result,
        error=job.get("error"),
    )


@router.post("/jobs", response_model=JobResponse)
async def create_job(request: SubmitJobRequest):
    """Submit a YouTube/video URL for processing."""
    if not request.url:
        raise HTTPException(status_code=400, detail="url is required")

    job_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    job = {
        "id": job_id,
        "status": "pending",
        "progress": 0,
        "stage": "Queued",
        "title": request.title or "Processing...",
        "created_at": now,
        "source_type": "url",
        "source_value": request.url,
        "language": request.language,
    }
    _save_job(job_id, job)

    # Fire off Celery task
    from app.worker import process_video
    process_video.delay(job_id, "url", request.url, request.language)

    return _job_to_response(job)


@router.post("/jobs/upload", response_model=JobResponse)
async def create_job_from_upload(
    file: UploadFile = File(...),
    title: str = Form(default=""),
    language: str = Form(default="en"),
):
    """Upload a video/audio file for processing."""
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_file_size_mb}MB limit")

    job_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    # Save upload
    from app.services.downloader import save_upload
    import asyncio
    file_path = asyncio.run(save_upload(content, file.filename or "upload.wav", job_id))

    job = {
        "id": job_id,
        "status": "pending",
        "progress": 0,
        "stage": "Queued",
        "title": title or file.filename or "Uploaded File",
        "created_at": now,
        "source_type": "file",
        "source_value": file_path,
        "language": language,
    }
    _save_job(job_id, job)

    from app.worker import process_video
    process_video.delay(job_id, "file", file_path, language)

    return _job_to_response(job)


@router.get("/jobs", response_model=list[JobResponse])
async def list_jobs():
    """List all jobs, newest first."""
    jobs = []
    for f in sorted(Path(JOB_STORE_DIR).glob("*.json"), key=os.path.getmtime, reverse=True):
        with open(f) as fp:
            jobs.append(_job_to_response(json.load(fp)))
    return jobs[:50]  # cap at 50


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    job = _load_job(job_id)
    return _job_to_response(job)


@router.get("/jobs/{job_id}/notes", response_model=list[NoteSection])
async def get_notes(job_id: str):
    job = _load_job(job_id)
    if job.get("status") != "done":
        raise HTTPException(status_code=202, detail="Job not complete")
    return [NoteSection(**s) for s in job["result"].get("sections", [])]


@router.get("/jobs/{job_id}/timestamps", response_model=list[Timestamp])
async def get_timestamps(job_id: str):
    job = _load_job(job_id)
    if job.get("status") != "done":
        raise HTTPException(status_code=202, detail="Job not complete")
    return [Timestamp(**t) for t in job["result"].get("timestamps", [])]


@router.get("/jobs/{job_id}/actions", response_model=list[ActionItem])
async def get_actions(job_id: str):
    job = _load_job(job_id)
    if job.get("status") != "done":
        raise HTTPException(status_code=202, detail="Job not complete")
    return [ActionItem(**a) for a in job["result"].get("action_items", [])]


@router.post("/jobs/{job_id}/query", response_model=QueryResponse)
async def query_transcript(job_id: str, request: QueryRequest):
    """RAG Q&A on the transcript."""
    job = _load_job(job_id)
    if job.get("status") != "done":
        raise HTTPException(status_code=202, detail="Job not complete")
    from app.services.rag import query
    return query(job_id, request.question, request.k)


@router.get("/jobs/{job_id}/export")
async def export_job(job_id: str, format: str = "md"):
    """Export notes as markdown or JSON."""
    job = _load_job(job_id)
    if job.get("status") != "done":
        raise HTTPException(status_code=202, detail="Job not complete")

    r = job["result"]

    if format == "json":
        return r

    # Build markdown export
    lines = [f"# {job.get('title', 'Video Notes')}\n"]
    lines.append(f"**Summary:** {r.get('summary', '')}\n")
    lines.append("\n---\n\n## Notes\n")
    for sec in r.get("sections", []):
        lines.append(f"\n### {sec['heading']}\n")
        lines.append(sec["content"])

    lines.append("\n\n---\n\n## Key Timestamps\n")
    for ts in r.get("timestamps", []):
        mins = int(ts["time"] // 60)
        secs = int(ts["time"] % 60)
        lines.append(f"- **{mins:02d}:{secs:02d}** — {ts['label']}: {ts['summary']}")

    lines.append("\n\n---\n\n## Action Items\n")
    for ai in r.get("action_items", []):
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(ai["priority"], "⚪")
        lines.append(f"- {priority_emoji} [{ai['category'].upper()}] {ai['text']}")

    md = "\n".join(lines)
    return PlainTextResponse(content=md, media_type="text/markdown")


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    path = f"{JOB_STORE_DIR}/{job_id}.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Job not found")
    os.remove(path)
    from app.services.processor import delete_collection
    delete_collection(job_id)
    return {"deleted": True}
