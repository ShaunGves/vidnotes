"""
Claude-powered timestamp and action item extraction.
"""
import anthropic
import json
from app.core.config import get_settings
from app.models.schemas import Timestamp, ActionItem

settings = get_settings()


def _client():
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


TIMESTAMP_SYSTEM = """You are an AI that identifies key moments in video transcripts.
Given a timestamped transcript, return a JSON array of important timestamps.

Output ONLY valid JSON (no markdown, no preamble):
[
  {
    "time": 45.0,
    "label": "Short label (5 words max)",
    "summary": "One sentence describing what happens at this moment"
  }
]

Rules:
- Identify 6-15 key moments: topic changes, key insights, definitions, examples, conclusions
- time is the float seconds value from the segment markers
- Focus on moments that would help someone navigate the video
"""

ACTION_SYSTEM = """You are an expert meeting/lecture analyst.
Extract all action items, decisions, and follow-ups from a transcript.

Output ONLY valid JSON (no markdown, no preamble):
[
  {
    "text": "Clear description of the action or task",
    "category": "task|decision|followup|resource",
    "priority": "high|medium|low",
    "assignee": "person name or null"
  }
]

Categories:
- task: something that needs to be done
- decision: a conclusion or choice made
- followup: something to research or revisit
- resource: a tool, link, or resource mentioned

If nothing found, return [].
"""


def extract_timestamps(segments: list[dict]) -> list[Timestamp]:
    timestamped = "\n".join(
        f"[{seg['start']:.1f}s] {seg['text']}" for seg in segments
    )

    client = _client()
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=2048,
        system=TIMESTAMP_SYSTEM,
        messages=[{"role": "user", "content": f"Transcript:\n\n{timestamped[:60000]}"}],
    )

    raw = _strip_fences(response.content[0].text)
    data = json.loads(raw)
    return [Timestamp(**item) for item in data]


def extract_action_items(transcript_text: str) -> list[ActionItem]:
    client = _client()
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=2048,
        system=ACTION_SYSTEM,
        messages=[{"role": "user", "content": f"Transcript:\n\n{transcript_text[:60000]}"}],
    )

    raw = _strip_fences(response.content[0].text)
    data = json.loads(raw)
    return [ActionItem(**item) for item in data]


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()
