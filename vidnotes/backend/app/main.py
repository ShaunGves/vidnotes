"""
VidNotes FastAPI application entry point.
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.routes import router
from app.api.websocket import job_progress_ws

settings = get_settings()

app = FastAPI(
    title="VidNotes API",
    description="Convert long-form videos into structured notes, timestamps, and action items.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.websocket("/ws/jobs/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    await job_progress_ws(websocket, job_id)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
