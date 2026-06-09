# VidNotes Architecture

## Pipeline

```
YouTube URL / File Upload
         │
    [yt-dlp / save]
         │ audio (wav)
    [Whisper STT]
         │ segments [{text, start, end}]
    ┌────┴──────────────────┐
    │                       │
[chunk + embed]      [Claude x3 calls]
[→ ChromaDB]         [notes / timestamps / actions]
    │
[RAG Q&A on demand]
```

## Model Defaults
- Whisper: `base` (fast, accurate enough for most content)
- Embeddings: `all-MiniLM-L6-v2` (local, no API cost)
- LLM: `claude-sonnet-4-20250514`

## Scaling Path
1. Replace file-based job store → PostgreSQL
2. Replace local uploads → S3/R2
3. Add JWT auth for multi-user
4. Docker Compose for one-command deploy
5. Whisper → faster-whisper for 2-4x speed boost
