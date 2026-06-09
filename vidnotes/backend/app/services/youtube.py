"""
YouTube audio extractor using yt-dlp.
Returns path to extracted .mp3 file.
"""
import os
import yt_dlp
from app.core.config import settings


def extract_audio(url: str, job_id: str) -> str:
    """Download audio from YouTube URL. Returns local file path."""
    out_path = os.path.join(settings.UPLOAD_DIR, f"{job_id}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "Untitled Video")

    audio_path = os.path.join(settings.UPLOAD_DIR, f"{job_id}.mp3")
    return audio_path, title
