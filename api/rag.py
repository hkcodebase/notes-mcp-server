"""Semantic search and RAG query using ChromaDB + Docker Model Runner."""
import chromadb
from openai import OpenAI
from sentence_transformers import SentenceTransformer

from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL, LLM_BASE_URL, LLM_MODEL

_collection = None
_model = None

_SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the question based ONLY on the provided context. "
    "If the context does not contain enough information, say so — do not make things up."
)


def _get_resources():
    global _collection, _model
    if _collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_or_create_collection(COLLECTION_NAME)
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _collection, _model


def similarity_search(query: str, top_k: int = 5) -> list[dict]:
    collection, model = _get_resources()
    embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=embedding, n_results=max(1, top_k))

    hits = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        hits.append({
            "text": doc,
            "source": meta.get("relative", meta.get("filename", "")),
            "filename": meta.get("filename", ""),
        })
    return hits


def rag_query(question: str, top_k: int = 5) -> dict:
    hits = similarity_search(question, top_k)
    context = "\n\n---\n\n".join(h["text"] for h in hits)

    client = OpenAI(base_url=LLM_BASE_URL, api_key="not-required")
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    answer = resp.choices[0].message.content
    return {"answer": answer, "sources": hits}
