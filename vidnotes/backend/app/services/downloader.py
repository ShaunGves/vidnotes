"""
yt-dlp-based video downloader.
Supports YouTube, Vimeo, direct URLs, and most yt-dlp-compatible sources.
"""
import os
import uuid
import asyncio
from pathlib import Path
from app.core.config import get_settings

settings = get_settings()


async def download_video(url: str, job_id: str) -> str:
    """
    Download video/audio to uploads dir. Returns path to audio file.
    Uses yt-dlp to extract audio as wav for Whisper.
    """
    out_dir = Path(settings.upload_dir) / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = str(out_dir / "audio.%(ext)s")

    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "wav",
        "--audio-quality", "0",
        "--output", out_path,
        "--no-playlist",
        url,
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {stderr.decode()}")

    # Find the output file
    files = list(out_dir.glob("audio.*"))
    if not files:
        raise FileNotFoundError("yt-dlp produced no output file")
    return str(files[0])


async def save_upload(file_bytes: bytes, filename: str, job_id: str) -> str:
    """Save an uploaded file to disk. Returns path."""
    out_dir = Path(settings.upload_dir) / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    out_path.write_bytes(file_bytes)
    return str(out_path)


async def get_video_title(url: str) -> str:
    """Fetch the video title from URL without downloading."""
    cmd = ["yt-dlp", "--get-title", "--no-playlist", url]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    title = stdout.decode().strip()
    return title or "Untitled Video"


async def get_video_duration(url: str) -> float:
    """Fetch video duration in seconds."""
    cmd = ["yt-dlp", "--get-duration", "--no-playlist", url]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    raw = stdout.decode().strip()
    # Duration format: HH:MM:SS or MM:SS
    parts = raw.split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        return float(raw)
    except Exception:
        return 0.0
