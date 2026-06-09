"""
RAG-based Q&A: retrieve relevant transcript chunks, answer with Claude.
"""
import chromadb
from chromadb.utils import embedding_functions
import anthropic
from app.core.config import get_settings
from app.models.schemas import QueryResponse

settings = get_settings()

_embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

RAG_SYSTEM = """You are a helpful assistant answering questions about a video transcript.
Use ONLY the provided transcript excerpts to answer. 
Be specific and cite approximate timestamps when relevant.
If the answer is not in the excerpts, say "I couldn't find that in the transcript."
"""


def _get_collection(job_id: str):
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return client.get_collection(
        name=f"job_{job_id}",
        embedding_function=_embed_fn,
    )


def query(job_id: str, question: str, k: int = 5) -> QueryResponse:
    """
    1. Embed the question
    2. Retrieve top-k transcript chunks from ChromaDB
    3. Pass chunks + question to Claude for grounded answering
    """
    collection = _get_collection(job_id)

    results = collection.query(
        query_texts=[question],
        n_results=min(k, collection.count()),
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    # Build context string for Claude
    context = "\n\n---\n\n".join(
        f"[~{meta['start']:.0f}s - {meta['end']:.0f}s]\n{doc}"
        for doc, meta in zip(docs, metas)
    )

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=1024,
        system=RAG_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"Transcript excerpts:\n\n{context}\n\nQuestion: {question}"
            }
        ],
    )

    answer = response.content[0].text.strip()
    sources = [
        {
            "text": doc[:200] + "..." if len(doc) > 200 else doc,
            "start": meta["start"],
            "end": meta["end"],
            "score": 1 - dist,
        }
        for doc, meta, dist in zip(docs, metas, distances)
    ]

    return QueryResponse(answer=answer, sources=sources)
