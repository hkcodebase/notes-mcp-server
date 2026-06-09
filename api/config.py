import os
from pathlib import Path

NOTES_DIR = Path(os.getenv("NOTES_DIR", "./notes"))
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", "./chroma_db"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
COLLECTION_NAME = "notes"

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://model-runner.docker.internal/engines/llama.cpp/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "ai/gemma4")

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
