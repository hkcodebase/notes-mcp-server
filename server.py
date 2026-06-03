"""MCP SSE server exposing search_notes and list_notes tools."""
import logging
from typing import Any

import chromadb
import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import TextContent, Tool
from sentence_transformers import SentenceTransformer
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route

from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL, SERVER_HOST, SERVER_PORT

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("notes-mcp")

_collection = None
_model = None


def _get_resources():
    global _collection, _model
    if _collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_or_create_collection(COLLECTION_NAME)
        _model = SentenceTransformer(EMBEDDING_MODEL)
        log.info("Loaded ChromaDB (%d docs) and embedding model.", _collection.count())
    return _collection, _model


mcp = Server("notes-mcp")


@mcp.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_notes",
            description=(
                "Semantic search over your personal notes and documents. "
                "Returns the most relevant passages along with the source file name."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for"},
                    "n_results": {
                        "type": "integer",
                        "description": "Max number of results (default 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="list_notes",
            description="List all note files that have been indexed.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@mcp.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    collection, model = _get_resources()

    if name == "search_notes":
        query = arguments.get("query", "")
        n = int(arguments.get("n_results", 5))
        embedding = model.encode([query]).tolist()
        results = collection.query(query_embeddings=embedding, n_results=max(1, n))

        parts: list[str] = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            parts.append(f"[{meta['filename']}]\n{doc}")

        text = "\n\n---\n\n".join(parts) if parts else "No results found."
        return [TextContent(type="text", text=text)]

    if name == "list_notes":
        data = collection.get(include=["metadatas"])
        files = sorted({m["relative"] for m in data["metadatas"]}) if data["metadatas"] else []
        text = "\n".join(files) if files else "No notes indexed yet. Run: python indexer.py"
        return [TextContent(type="text", text=text)]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


sse_transport = SseServerTransport("/messages/")


async def handle_sse(request: Request):
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp.run(streams[0], streams[1], mcp.create_initialization_options())


starlette_app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages", app=sse_transport.handle_post_message),
    ]
)

if __name__ == "__main__":
    log.info("Starting notes-mcp SSE server on %s:%d", SERVER_HOST, SERVER_PORT)
    log.info("SSE endpoint: http://%s:%d/sse", SERVER_HOST, SERVER_PORT)
    uvicorn.run(starlette_app, host=SERVER_HOST, port=SERVER_PORT)
