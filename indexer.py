"""Index notes from a directory into ChromaDB using sentence-transformers."""
import sys
from pathlib import Path
from typing import Optional

import chromadb
from sentence_transformers import SentenceTransformer

from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL, NOTES_DIR


def _load_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _load_pdf(path: Path) -> str:
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def load_file(path: Path) -> Optional[str]:
    ext = path.suffix.lower()
    if ext in (".txt", ".md"):
        return _load_txt(path)
    if ext == ".pdf":
        return _load_pdf(path)
    return None


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 40) -> list[str]:
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i : i + chunk_size]))
        i += chunk_size - overlap
    return [c for c in chunks if c.strip()]


def index_notes(notes_dir: Path = NOTES_DIR) -> int:
    if not notes_dir.exists():
        print(f"Notes directory not found: {notes_dir.resolve()}", file=sys.stderr)
        return 0

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(COLLECTION_NAME)
    model = SentenceTransformer(EMBEDDING_MODEL)

    patterns = ["*.txt", "*.md", "*.pdf"]
    files: list[Path] = []
    for pat in patterns:
        files.extend(notes_dir.rglob(pat))

    total_chunks = 0
    for file_path in sorted(set(files)):
        text = load_file(file_path)
        if not text or not text.strip():
            continue

        chunks = chunk_text(text)
        if not chunks:
            continue

        embeddings = model.encode(chunks).tolist()
        rel = str(file_path.relative_to(notes_dir))
        ids = [f"{rel}::{i}" for i in range(len(chunks))]
        metadatas = [
            {"source": str(file_path), "filename": file_path.name, "relative": rel, "chunk": i}
            for i in range(len(chunks))
        ]

        collection.upsert(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
        print(f"  {file_path.name}: {len(chunks)} chunks")
        total_chunks += len(chunks)

    print(f"\nDone. {len(files)} files → {total_chunks} chunks. Total in DB: {collection.count()}")
    return total_chunks


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else NOTES_DIR
    index_notes(target)
