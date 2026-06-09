from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.core.jobs import job_store
from app.services import rag

router = APIRouter()


@router.post("/{job_id}", response_model=ChatResponse)
async def chat(job_id: str, body: ChatRequest):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job["status"] != "done":
        raise HTTPException(400, "Video not yet processed")

    answer, sources = rag.answer(job_id, body.question, body.history)
    return ChatResponse(answer=answer, sources=sources)
