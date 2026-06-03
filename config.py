import os
from pathlib import Path

NOTES_DIR = Path(os.getenv("NOTES_DIR", "./notes"))
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", "./chroma_db"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
COLLECTION_NAME = "notes"
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8765"))
