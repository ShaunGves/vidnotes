"""
Full processing pipeline: ingest → transcribe → analyze → index
Runs in a background task. Updates job_store at each stage.
"""
import os
import traceback

from app.core.jobs import job_store
from app.core.config import settings
from app.services import transcriber, analyzer, rag
from app.services.youtube import extract_audio


async def run_pipeline(job_id: str):
    job = job_store.get(job_id)
    if not job:
        return

    try:
        # ── Stage 1: Acquire audio ────────────────────────────────────────
        job_store.update(job_id, status="transcribing", progress=5, stage_message="Acquiring audio…")
        title_override = None

        if job["source_type"] == "url":
            audio_path, yt_title = extract_audio(job["source"], job_id)
            title_override = yt_title
        else:
            audio_path = job.get("file_path")
            if not audio_path or not os.path.exists(audio_path):
                raise FileNotFoundError("Uploaded file not found on disk")

        # ── Stage 2: Transcribe ───────────────────────────────────────────
        job_store.update(job_id, progress=15, stage_message="Transcribing with Whisper…")
        segments = transcriber.transcribe(audio_path)
        full_text = transcriber.segments_to_full_text(segments)

        job_store.update(
            job_id,
            transcript=full_text,
            progress=55,
            stage_message="Transcription complete. Analyzing with Claude…",
        )

        # ── Stage 3: Analyze with Claude ─────────────────────────────────
        job_store.update(job_id, progress=60, stage_message="Claude is generating notes and timestamps…")
        result = analyzer.analyze(full_text, segments)

        # Override title with YouTube title if available
        if title_override and result.title in ("Untitled", ""):
            result.title = title_override

        # Attach raw transcript for export
        result.raw_transcript = full_text

        job_store.update(job_id, progress=85, stage_message="Indexing transcript for Q&A…")

        # ── Stage 4: RAG indexing ─────────────────────────────────────────
        rag.index_transcript(job_id, segments)

        # ── Done ──────────────────────────────────────────────────────────
        job_store.update(
            job_id,
            status="done",
            progress=100,
            stage_message="Done!",
            result=result,
        )

        # Cleanup audio file
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception:
            pass

    except Exception as e:
        job_store.update(
            job_id,
            status="error",
            stage_message="Pipeline failed",
            error=str(e),
            progress=0,
        )
        print(f"[Pipeline ERROR] job={job_id}\n{traceback.format_exc()}")
