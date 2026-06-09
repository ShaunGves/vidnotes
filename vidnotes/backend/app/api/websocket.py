"""
WebSocket endpoint for real-time job progress streaming.
"""
import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect


async def job_progress_ws(websocket: WebSocket, job_id: str):
    """Stream job progress updates over WebSocket until job is done or failed."""
    import os
    JOB_STORE_DIR = "./job_store"

    await websocket.accept()
    try:
        while True:
            path = f"{JOB_STORE_DIR}/{job_id}.json"
            if os.path.exists(path):
                with open(path) as f:
                    job = json.load(f)
                await websocket.send_json({
                    "job_id": job_id,
                    "status": job.get("status"),
                    "progress": job.get("progress", 0),
                    "stage": job.get("stage", ""),
                    "error": job.get("error"),
                })
                if job.get("status") in ("done", "failed"):
                    break
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()
