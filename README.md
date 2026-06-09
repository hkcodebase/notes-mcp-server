# notes-mcp-server

Local notes & documents RAG with an MCP server for AI coding assistants, plus a web UI powered by a local Docker model.

## Stack

- **Embeddings**: `sentence-transformers` (fully local, no API key)
- **Vector store**: ChromaDB (persistent local DB)
- **LLM**: Gemma 4 via Docker Model Runner (OpenAI-compatible, fully local)
- **MCP transport**: SSE over HTTP
- **UI**: React + Vite
- **API**: FastAPI

## Quick start (Docker)

Requires Docker Desktop 4.40+ with Model Runner enabled.

```bash
cp .env.example .env   # edit NOTES_DIR if needed
python indexer.py      # index your notes first
docker compose up --build
```

| Service | URL |
|---------|-----|
| Web UI  | http://localhost:3000 |
| API     | http://localhost:8000 |
| MCP SSE | http://localhost:8765/sse |

## Manual setup (dev mode)

```bash
pip install -r requirements.txt
cp .env.example .env
```

### 1 — Index your notes

Put `.txt`, `.md`, or `.pdf` files in the `notes/` folder (or set `NOTES_DIR`), then:

```bash
python indexer.py
# or point at a custom directory:
python indexer.py /path/to/my/notes
```

Re-run whenever you add or update notes. Existing chunks are upserted (not duplicated).

### 2 — Start the API + UI

```bash
# Terminal 1 — FastAPI backend
cd api
pip install -r requirements.txt
python main.py          # http://localhost:8000

# Terminal 2 — React frontend
cd ui
npm install
npm run dev             # http://localhost:5173
```

### 3 — Start the MCP server (for Claude Code / Cursor)

```bash
python server.py
# SSE endpoint: http://localhost:8765/sse
```

### 4 — Connect to Claude Code

Add to your project's `.claude/settings.json` (or `~/.claude/settings.json` for global):

```json
{
  "mcpServers": {
    "notes": {
      "type": "sse",
      "url": "http://localhost:8765/sse"
    }
  }
}
```

Then restart Claude Code. You'll see `search_notes` and `list_notes` available as tools.

## Web UI features

| Tab | Description |
|-----|-------------|
| **Ask** | Ask a question — Gemma 4 answers using your notes as context (RAG) |
| **Search** | Semantic similarity search — returns relevant passages without LLM |
| **Notes** | Lists all indexed note files |

## MCP tools

| Tool | Description |
|------|-------------|
| `search_notes` | Semantic search — returns top-N relevant passages with source filenames |
| `list_notes` | Lists all indexed note files |

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/stats` | File and chunk counts |
| GET | `/notes` | List all indexed files |
| POST | `/search` | Semantic search `{ query, top_k }` |
| POST | `/query` | RAG query `{ question, top_k }` → LLM answer + sources |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NOTES_DIR` | `./notes` | Directory to index |
| `CHROMA_DIR` | `./chroma_db` | ChromaDB storage path |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Any sentence-transformers model |
| `LLM_BASE_URL` | `http://model-runner.docker.internal/engines/llama.cpp/v1` | Docker Model Runner endpoint |
| `LLM_MODEL` | `ai/gemma4` | Model name (Docker Model Runner catalog) |
| `SERVER_HOST` | `0.0.0.0` | MCP server bind host |
| `SERVER_PORT` | `8765` | MCP server bind port |
| `API_HOST` | `0.0.0.0` | FastAPI bind host |
| `API_PORT` | `8000` | FastAPI bind port |
