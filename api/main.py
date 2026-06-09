"""FastAPI backend — search, RAG, and notes management."""
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import chromadb
from config import CHROMA_DIR, COLLECTION_NAME, API_HOST, API_PORT
from rag import rag_query, similarity_search

app = FastAPI(title="Notes RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


def _get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(COLLECTION_NAME)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats():
    col = _get_collection()
    data = col.get(include=["metadatas"])
    files = sorted({m["relative"] for m in data["metadatas"]}) if data["metadatas"] else []
    return {"files": len(files), "chunks": col.count()}


@app.get("/notes")
def list_notes():
    col = _get_collection()
    data = col.get(include=["metadatas"])
    files = sorted({m["relative"] for m in data["metadatas"]}) if data["metadatas"] else []
    return {"notes": files, "total": len(files)}


@app.post("/search")
def search(req: SearchRequest):
    hits = similarity_search(req.query, top_k=req.top_k)
    return {"query": req.query, "results": hits}


@app.post("/query")
def query(req: QueryRequest):
    try:
        return rag_query(req.question, top_k=req.top_k)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
