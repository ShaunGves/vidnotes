# VidNotes 🎬→📝

**Turn any long-form video into structured notes, timestamped highlights, and actionable tasks — powered by Whisper, Claude, and RAG.**

> Built as a production-ready AI engineering portfolio project.

---

## Architecture

```
Video/URL → Whisper (STT) → Transcript Chunking → ChromaDB (RAG)
                                    ↓
                           Claude API (Summarization + Extraction)
                                    ↓
              Notes | Timestamps | Action Items | Q&A Chat
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Python 3.11 |
| Speech-to-Text | OpenAI Whisper (local) |
| LLM | Anthropic Claude (claude-sonnet-4) |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers |
| Frontend | React 18 + TypeScript + Vite + Tailwind |
| Job Queue | Celery + Redis |

---

## Features

- 📥 **Multiple inputs**: YouTube URL, direct upload (mp4/mp3/wav), or local file path
- 🎙️ **Whisper transcription**: word-level timestamps, speaker diarization-ready
- 📋 **Structured notes**: hierarchical, topic-segmented markdown notes
- ⏱️ **Smart timestamps**: auto-detected topic changes and key moments
- ✅ **Action items**: extracted tasks, decisions, and follow-ups
- 💬 **RAG Q&A**: ask questions about any part of the video
- 📤 **Export**: Markdown, PDF, Notion-ready JSON

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (`brew install redis` / `apt install redis-server`)
- ffmpeg (`brew install ffmpeg` / `apt install ffmpeg`)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # fill in your API keys

redis-server &            # start Redis
uvicorn app.main:app --reload --port 8000
# separate terminal:
celery -A app.worker worker --loglevel=info
```

### Frontend
```bash
cd frontend
npm install
npm run dev               # http://localhost:5173
```

---

## Environment Variables

```env
ANTHROPIC_API_KEY=your_key_here
REDIS_URL=redis://localhost:6379
CHROMA_PERSIST_DIR=./chroma_db
WHISPER_MODEL=base        # tiny | base | small | medium | large
MAX_FILE_SIZE_MB=500
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/jobs` | Submit video for processing |
| GET | `/api/v1/jobs/{id}` | Poll job status + results |
| GET | `/api/v1/jobs/{id}/notes` | Get structured notes |
| GET | `/api/v1/jobs/{id}/timestamps` | Get timestamp list |
| GET | `/api/v1/jobs/{id}/actions` | Get action items |
| POST | `/api/v1/jobs/{id}/query` | RAG Q&A on transcript |
| GET | `/api/v1/jobs/{id}/export?format=md` | Export (md/json) |
| WS | `/ws/jobs/{id}` | Real-time progress stream |

---

## License
MIT
