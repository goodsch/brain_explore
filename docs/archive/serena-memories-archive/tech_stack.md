# Tech Stack

## Python (3.10+)
- Package manager: `uv` (via .tool-versions)
- Build system: hatchling

## Core Dependencies
- `qdrant-client` - Vector store client
- `neo4j` - Graph database driver
- `openai` - Embeddings (text-embedding-3-small) + LLM extraction (gpt-4o-mini)
- `ebooklib` - EPUB parsing
- `pymupdf` - PDF extraction
- `beautifulsoup4` - HTML parsing
- `tiktoken` - Token counting
- `pydantic` - Data models
- `rich` - CLI output

## Infrastructure (Docker Compose)
- **Qdrant**: localhost:6333 (HTTP), localhost:6334 (gRPC)
- **Neo4j**: localhost:7474 (browser), localhost:7687 (Bolt)
  - Auth: neo4j/brainexplore
  - Plugin: APOC

## MCP Servers
- annas (Anna's Archive search/download)
- arxiv (paper search/download)
- ebook-mcp (EPUB/PDF reading)
- siyuan-mcp (SiYuan knowledge base)

## IES Backend (FastAPI)
- **Port**: 8081 (8000 is occupied by Portainer)
- **Start command**: `cd ies-backend && IES_NEO4J_PASSWORD=brainexplore uv run uvicorn ies_backend.main:app --host 0.0.0.0 --port 8081`
- **Requires**: Neo4j running (docker compose up -d)
- **Environment prefix**: IES_ (e.g., IES_NEO4J_PASSWORD, IES_SIYUAN_TOKEN)

### Available Endpoints (16 total)
- `/health` - Health check
- `/profile/*` - User profile management (6 routes)
- `/session/*` - Session processing and context (4 routes)
- `/question-engine/*` - Socratic questioning (6 routes)

## Future (IES Plugin)
- SiYuan plugin (TypeScript)
- Claude API integration for extraction
