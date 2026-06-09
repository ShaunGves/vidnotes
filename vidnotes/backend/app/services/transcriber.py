"""
Whisper-based speech-to-text transcription.
Returns word-level segments with timestamps.
"""
import whisper
import asyncio
from pathlib import Path
from typing import Any
from app.core.config import get_settings

settings = get_settings()

# Lazy-load model (cached after first use)
_model = None


def _get_model():
    global _model
    if _model is None:
        _model = whisper.load_model(settings.whisper_model)
    return _model


def transcribe_sync(audio_path: str) -> dict[str, Any]:
    """
    Run Whisper transcription synchronously.
    Returns:
        {
          "text": full transcript string,
          "segments": [{"id", "start", "end", "text"}, ...]
        }
    """
    model = _get_model()
    result = model.transcribe(
        audio_path,
        word_timestamps=True,
        verbose=False,
    )
    return {
        "text": result["text"].strip(),
        "segments": [
            {
                "id": seg["id"],
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
            }
            for seg in result["segments"]
        ],
    }


async def transcribe(audio_path: str) -> dict[str, Any]:
    """Async wrapper — runs Whisper in a thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, transcribe_sync, audio_path)


def format_timestamp(seconds: float) -> str:
    """Convert float seconds to HH:MM:SS string."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"
