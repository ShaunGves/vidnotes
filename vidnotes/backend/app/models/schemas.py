from pydantic import BaseModel, HttpUrl
from enum import Enum
from typing import Optional
import uuid
from datetime import datetime


class JobStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class VideoSource(str, Enum):
    URL = "url"
    UPLOAD = "upload"


class SubmitJobRequest(BaseModel):
    url: Optional[str] = None  # YouTube or direct video URL
    title: Optional[str] = None
    language: str = "en"


class Timestamp(BaseModel):
    time: float        # seconds
    label: str
    summary: str


class ActionItem(BaseModel):
    text: str
    category: str      # task | decision | followup | resource
    priority: str      # high | medium | low
    assignee: Optional[str] = None


class NoteSection(BaseModel):
    heading: str
    content: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class JobResult(BaseModel):
    notes: list[NoteSection] = []
    timestamps: list[Timestamp] = []
    action_items: list[ActionItem] = []
    summary: str = ""
    transcript: str = ""


class JobResponse(BaseModel):
    id: str
    status: JobStatus
    progress: int = 0          # 0-100
    stage: str = ""
    title: Optional[str] = None
    duration: Optional[float] = None
    created_at: datetime
    result: Optional[JobResult] = None
    error: Optional[str] = None


class QueryRequest(BaseModel):
    question: str
    k: int = 5     # top-k chunks to retrieve


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]   # [{text, timestamp, score}]


class ProgressUpdate(BaseModel):
    job_id: str
    status: JobStatus
    progress: int
    stage: str
    message: str = ""
