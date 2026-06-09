"""
Analyzer — uses Claude to convert a transcript into:
  - Structured notes (sections + bullets)
  - Key timestamps with labels
  - Action items with priorities
"""
import json
import re
from typing import List, Dict, Any

import anthropic
from app.core.config import settings
from app.models.schemas import AnalysisResult, NoteSection, Timestamp, ActionItem

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are an expert note-taker and knowledge organizer. You receive video transcripts (with inline timestamps) and produce clean, structured output.

Always respond with a single JSON object. No markdown fences, no extra text — pure JSON only."""

ANALYSIS_PROMPT = """Analyze this transcript and produce a JSON object with exactly this structure:

{{
  "title": "Concise video title (infer from content)",
  "overview": "2-3 sentence executive summary of the entire video",
  "sections": [
    {{
      "heading": "Section heading",
      "bullets": ["Key point 1", "Key point 2", "Key point 3"]
    }}
  ],
  "timestamps": [
    {{
      "time": "MM:SS",
      "seconds": 0,
      "label": "Short topic label",
      "summary": "One-sentence description of what happens here"
    }}
  ],
  "action_items": [
    {{
      "task": "Clear, actionable task description",
      "priority": "high|medium|low",
      "owner": "Person mentioned or null",
      "context": "Why this task matters (one sentence)"
    }}
  ]
}}

Rules:
- sections: 3-8 sections covering main topics; 3-6 bullets each
- timestamps: 5-15 key moments where topics shift or important info appears; use actual timestamps from the transcript (format [MM:SS] or [HH:MM:SS])
- action_items: only real tasks/decisions/follow-ups; empty array if none exist
- Be specific and concrete — no vague generalities

TRANSCRIPT:
{transcript}"""


def analyze(transcript_text: str, segments: List[Dict[str, Any]]) -> AnalysisResult:
    """Run full analysis pipeline on transcript."""
    prompt = ANALYSIS_PROMPT.format(transcript=transcript_text[:50000])  # ~12k tokens

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Strip any accidental fences
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    data = json.loads(raw)

    # Enrich timestamps with actual seconds from segments
    timestamps = []
    for ts in data.get("timestamps", []):
        enriched = _find_segment_seconds(ts["time"], segments)
        timestamps.append(
            Timestamp(
                time=ts["time"],
                seconds=enriched if enriched is not None else _parse_time_str(ts["time"]),
                label=ts["label"],
                summary=ts["summary"],
            )
        )

    action_items = [
        ActionItem(
            task=a["task"],
            priority=a.get("priority", "medium"),
            owner=a.get("owner"),
            context=a.get("context"),
        )
        for a in data.get("action_items", [])
    ]

    sections = [
        NoteSection(heading=s["heading"], bullets=s["bullets"])
        for s in data.get("sections", [])
    ]

    return AnalysisResult(
        title=data.get("title", "Untitled"),
        overview=data.get("overview", ""),
        sections=sections,
        timestamps=timestamps,
        action_items=action_items,
    )


def _parse_time_str(time_str: str) -> float:
    """Convert MM:SS or HH:MM:SS string to seconds."""
    parts = time_str.strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0.0


def _find_segment_seconds(time_str: str, segments: List[Dict[str, Any]]) -> float | None:
    """Find the actual segment start closest to the given timestamp string."""
    target = _parse_time_str(time_str)
    if not segments:
        return None
    closest = min(segments, key=lambda s: abs(s["start"] - target))
    return closest["start"]
