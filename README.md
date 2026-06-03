# notes-mcp-server

Local notes & documents RAG with an MCP server for AI coding assistants.

## Stack
- **Embeddings**: `sentence-transformers` (fully local, no API key)
- **Vector store**: ChromaDB (persistent local DB)
- **Transport**: MCP SSE over HTTP

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # edit NOTES_DIR to point at your notes
```

## 1 — Index your notes

Put your `.txt`, `.md`, or `.pdf` files in the `notes/` folder (or set `NOTES_DIR`), then:

```bash
python indexer.py
# or point at a custom directory:
python indexer.py /path/to/my/notes
```

Re-run whenever you add or update notes. Existing chunks are upserted (not duplicated).

## 2 — Start the MCP server

```bash
python server.py
# SSE endpoint: http://localhost:8765/sse
```

## 3 — Connect to Claude Code

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

## Tools exposed

| Tool | Description |
|------|-------------|
| `search_notes` | Semantic search — returns top-N relevant passages with source filenames |
| `list_notes` | Lists all indexed note files |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NOTES_DIR` | `./notes` | Directory to index |
| `CHROMA_DIR` | `./chroma_db` | ChromaDB storage path |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Any sentence-transformers model |
| `SERVER_HOST` | `0.0.0.0` | Bind host |
| `SERVER_PORT` | `8765` | Bind port |
