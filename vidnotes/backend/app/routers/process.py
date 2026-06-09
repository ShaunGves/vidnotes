"""
Process router — SSE stream for live progress + result endpoint.
"""
import json
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from app.core.jobs import job_store
from app.models.schemas import JobStatusResponse

router = APIRouter()


@router.get("/{job_id}/stream")
async def stream_progress(job_id: str):
    """Server-Sent Events stream — pushes status updates until job completes."""
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    async def event_generator():
        while True:
            job = job_store.get(job_id)
            if not job:
                break

            payload = {
                "id": job["id"],
                "status": job["status"],
                "progress": job["progress"],
                "stage_message": job["stage_message"],
            }

            # Include result if done
            if job["status"] == "done" and job["result"]:
                payload["result"] = job["result"].model_dump()
            elif job["status"] == "error":
                payload["error"] = job["error"]

            yield f"data: {json.dumps(payload)}\n\n"

            if job["status"] in ("done", "error"):
                break

            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{job_id}/result")
async def get_result(job_id: str):
    """Fetch final result once job is done."""
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job["status"] != "done":
        raise HTTPException(400, f"Job not complete. Current status: {job['status']}")
    return job["result"]


@router.get("/{job_id}/export")
async def export_markdown(job_id: str):
    """Export notes as Markdown file."""
    job = job_store.get(job_id)
    if not job or job["status"] != "done":
        raise HTTPException(404, "Job not found or not complete")

    result = job["result"]
    md = _to_markdown(result)

    return StreamingResponse(
        iter([md]),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="vidnotes_{job_id[:8]}.md"'},
    )


def _to_markdown(result) -> str:
    lines = [f"# {result.title}", "", f"> {result.overview}", "", "---", ""]

    lines.append("## 📋 Notes\n")
    for section in result.sections:
        lines.append(f"### {section.heading}")
        for bullet in section.bullets:
            lines.append(f"- {bullet}")
        lines.append("")

    lines.append("## ⏱️ Key Timestamps\n")
    for ts in result.timestamps:
        lines.append(f"**[{ts.time}]** — **{ts.label}**")
        lines.append(f"_{ts.summary}_")
        lines.append("")

    if result.action_items:
        lines.append("## ✅ Action Items\n")
        for item in result.action_items:
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(item.priority, "⚪")
            owner = f" _(owner: {item.owner})_" if item.owner else ""
            lines.append(f"- {priority_emoji} **{item.task}**{owner}")
            if item.context:
                lines.append(f"  _{item.context}_")
        lines.append("")

    return "\n".join(lines)
