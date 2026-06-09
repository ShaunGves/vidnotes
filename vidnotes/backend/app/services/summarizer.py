"""
Claude-powered summarization + structured notes generation.
"""
import anthropic
import json
from app.core.config import get_settings
from app.models.schemas import NoteSection

settings = get_settings()


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


NOTES_SYSTEM = """You are an expert note-taker for technical content (lectures, meetings, YouTube videos).
Given a full transcript, produce structured notes as JSON.

Output ONLY valid JSON matching this schema (no markdown, no preamble):
{
  "summary": "2-3 sentence executive summary of the entire content",
  "sections": [
    {
      "heading": "Section title",
      "content": "Dense markdown notes for this section. Use bullet points, bold key terms, and code blocks if relevant.",
      "start_time": 0.0,
      "end_time": 120.0
    }
  ]
}

Guidelines:
- Identify 4-8 natural topic sections
- Be specific and technical — preserve numbers, names, and key concepts
- start_time and end_time are approximate seconds from the segment context
- Content should be 3-8 bullet points per section, each 1-2 sentences
"""


def generate_notes(transcript_text: str, segments: list[dict]) -> dict:
    """
    Use Claude to generate structured notes from the full transcript.
    Returns parsed JSON with summary and sections.
    """
    # Build a timestamped transcript for Claude context
    timestamped = "\n".join(
        f"[{seg['start']:.0f}s] {seg['text']}" for seg in segments
    )

    client = _client()
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=4096,
        system=NOTES_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"Transcript:\n\n{timestamped[:80000]}"  # ~80k char limit
            }
        ],
    )

    raw = response.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    return json.loads(raw)


SUMMARY_SYSTEM = """You are a concise summarizer. Given a chunk of transcript, 
produce a 1-2 sentence summary capturing the key point. No preamble."""


def summarize_chunk(text: str) -> str:
    """Summarize a single chunk (used for timestamp labels)."""
    client = _client()
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=150,
        messages=[{"role": "user", "content": f"Summarize this in 1-2 sentences:\n{text}"}],
    )
    return response.content[0].text.strip()
