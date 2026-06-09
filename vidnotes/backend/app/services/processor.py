"""
Transcript chunking + ChromaDB embedding pipeline.
Splits transcript segments into overlapping chunks for RAG.
"""
import chromadb
from chromadb.utils import embedding_functions
from typing import Any
from app.core.config import get_settings

settings = get_settings()

# sentence-transformer embeddings (runs locally, no API key needed)
_embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def _get_collection(job_id: str):
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return client.get_or_create_collection(
        name=f"job_{job_id}",
        embedding_function=_embed_fn,
        metadata={"hnsw:space": "cosine"},
    )


def chunk_segments(segments: list[dict], chunk_tokens: int = 500, overlap: int = 50) -> list[dict]:
    """
    Group Whisper segments into ~chunk_tokens-word chunks with overlap.
    Returns: [{"text", "start", "end", "chunk_id"}, ...]
    """
    chunks = []
    current_words: list[str] = []
    current_start: float = 0.0
    current_end: float = 0.0
    chunk_idx = 0

    for seg in segments:
        words = seg["text"].split()
        if not current_words:
            current_start = seg["start"]

        current_words.extend(words)
        current_end = seg["end"]

        if len(current_words) >= chunk_tokens:
            chunks.append({
                "chunk_id": f"chunk_{chunk_idx}",
                "text": " ".join(current_words),
                "start": current_start,
                "end": current_end,
            })
            # overlap: keep last N words as context for next chunk
            current_words = current_words[-overlap:]
            current_start = current_end
            chunk_idx += 1

    # flush remainder
    if current_words:
        chunks.append({
            "chunk_id": f"chunk_{chunk_idx}",
            "text": " ".join(current_words),
            "start": current_start,
            "end": current_end,
        })

    return chunks


def embed_and_store(job_id: str, chunks: list[dict]) -> None:
    """Embed all chunks and upsert into ChromaDB collection."""
    collection = _get_collection(job_id)
    collection.upsert(
        ids=[c["chunk_id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[{"start": c["start"], "end": c["end"]} for c in chunks],
    )


def delete_collection(job_id: str) -> None:
    """Remove ChromaDB collection when job is deleted."""
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    try:
        client.delete_collection(f"job_{job_id}")
    except Exception:
        pass
