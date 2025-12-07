# IES MCP Server Design

**Date:** 2025-12-06
**Status:** Design Complete
**Purpose:** Expose ForgeMode thinking sessions to Claude Desktop/mobile for voice-based structured thinking

## Overview

A lightweight MCP server that wraps existing IES backend APIs, enabling voice-driven ForgeMode sessions through Claude Desktop or mobile. Uses existing Redis session persistence — no backend changes required.

## Scope

**In scope:**
- ForgeMode thinking sessions (5 modes: Learning, Articulating, Planning, Ideating, Reflecting)
- 6 MCP tools for complete session lifecycle
- Stateless design with Redis session persistence

**Out of scope (future):**
- Flow Mode graph exploration
- Spark/insight capture
- Free dialogue sessions

## MCP Tools

| Tool | Backend Endpoint | Purpose |
|------|------------------|---------|
| `start_session` | `POST /session/start` | Begin ForgeMode session with mode + topic |
| `submit_response` | `POST /session/respond` | Answer current question, get next |
| `end_session` | `POST /session/end` | Complete session, trigger extraction |
| `get_question` | `GET /session/{id}/current` | Get current question + hints |
| `list_templates` | `GET /templates` | Available thinking modes |
| `get_status` | `GET /session/{id}` | Session state, progress, history |

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Claude Voice   │────▶│  IES MCP Server │────▶│  IES Backend    │
│  (Desktop/iOS)  │     │  (Python wrap)  │     │  (FastAPI)      │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │     Redis       │
                                                │  (Session Store)│
                                                └─────────────────┘
```

**Design decisions:**
- **Stateless wrapper:** No session state in MCP server, all state in Redis via backend
- **Lightweight:** Single Python file (~150 lines), minimal dependencies
- **No auth:** Local use only initially

## File Structure

```
ies/mcp-server/
├── server.py          # MCP server implementation
├── requirements.txt   # mcp, httpx
└── README.md          # Setup instructions
```

## Tool Signatures

```python
@server.tool()
async def start_session(mode: str, topic: str, user_id: str = "default") -> dict:
    """Start a ForgeMode thinking session.

    Args:
        mode: One of: learning, articulating, planning, ideating, reflecting
        topic: What you want to think about
        user_id: User identifier (default: "default")

    Returns:
        session_id, current_question, hints, template_info
    """

@server.tool()
async def submit_response(session_id: str, response: str) -> dict:
    """Submit response to current question.

    Args:
        session_id: Active session identifier
        response: User's response to the current question

    Returns:
        next_question, hints, progress, is_complete
    """

@server.tool()
async def end_session(session_id: str) -> dict:
    """End session and trigger extraction.

    Args:
        session_id: Active session identifier

    Returns:
        summary, entities_extracted, insights, siyuan_doc_id
    """

@server.tool()
async def get_question(session_id: str) -> dict:
    """Get current question (for context recovery).

    Args:
        session_id: Active session identifier

    Returns:
        current_question, hints, question_class, progress
    """

@server.tool()
async def list_templates() -> dict:
    """List available thinking modes.

    Returns:
        List of templates with id, name, description, section_count
    """

@server.tool()
async def get_status(session_id: str) -> dict:
    """Get session status and history.

    Args:
        session_id: Active session identifier

    Returns:
        status, mode, topic, progress, question_response_history
    """
```

## Voice Interaction Flow

**Example session:**

> **User:** "Start a learning session about executive function"
>
> **Claude:** *calls `start_session(mode="learning", topic="executive function")`*
>
> "I've started a learning session. First question: What do you already know about executive function? Take your time."
>
> **User:** "It's about self-regulation, planning, and impulse control. I think it's related to the prefrontal cortex."
>
> **Claude:** *calls `submit_response(session_id, response)`*
>
> "Good foundation. Next: What specific aspect of executive function are you most curious about understanding better?"
>
> *...continues through template sections...*
>
> **User:** "I think that's enough for now"
>
> **Claude:** *calls `end_session(session_id)`*
>
> "Session complete. I extracted 3 concepts and 2 insights. The session is saved to your SiYuan notebook."

**Behaviors:**
- Claude uses `get_question` if conversation context is lost (e.g., after app restart)
- Hints available via tool response, Claude decides when to offer them
- Session persists in Redis — can resume later via `get_status`

## Setup

### Installation

```bash
cd ies/mcp-server
pip install -r requirements.txt
```

### Claude Desktop Configuration

Add to `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ies": {
      "command": "python",
      "args": ["/home/chris/dev/projects/codex/brain_explore/ies/mcp-server/server.py"],
      "env": {
        "IES_BACKEND_URL": "http://localhost:8081"
      }
    }
  }
}
```

### Testing

1. Start infrastructure: `docker compose up -d`
2. Start backend: `cd ies/backend && uv run uvicorn ies_backend.main:app --port 8081`
3. Debug MCP server: `python ies/mcp-server/server.py`
4. Restart Claude Desktop to load the MCP
5. Test: "Start an articulating session about my current project"

## Success Criteria

- [ ] Can start ForgeMode session via voice command
- [ ] Questions flow naturally with voice responses
- [ ] Session ends cleanly with extraction summary
- [ ] Session document appears in SiYuan after completion
- [ ] Can resume interrupted session via `get_status`

## Source Access Tools

The IES MCP server also provides access to external sources (Anna's Archive, Arxiv) with optional auto-ingestion into the knowledge graph.

### Additional Tools

| Tool | Purpose |
|------|---------|
| `search_books` | Search Anna's Archive for books by title/author/topic |
| `search_papers` | Search Arxiv for research papers by query/author |
| `download_source` | Download book/paper, optionally auto-ingest to Calibre |
| `get_source_status` | Check ingestion status of a downloaded source |

### Tool Signatures

```python
@server.tool()
async def search_books(query: str, limit: int = 5) -> dict:
    """Search Anna's Archive for books.

    Args:
        query: Search term (title, author, topic)
        limit: Max results to return (default: 5)

    Returns:
        List of books with title, author, format, md5_hash, file_size
    """

@server.tool()
async def search_papers(query: str, limit: int = 5) -> dict:
    """Search Arxiv for research papers.

    Args:
        query: Search term (title, author, topic)
        limit: Max results to return (default: 5)

    Returns:
        List of papers with title, authors, abstract, arxiv_id, pdf_url
    """

@server.tool()
async def download_source(
    source_type: str,
    identifier: str,
    title: str,
    auto_ingest: bool = False
) -> dict:
    """Download source and optionally ingest.

    Args:
        source_type: "book" or "paper"
        identifier: MD5 hash (Anna's) or arxiv ID
        title: Source title (for filename)
        auto_ingest: If True, add to Calibre and queue for entity extraction

    Returns:
        file_path, ingestion_status, calibre_id (if ingested)
    """

@server.tool()
async def get_source_status(identifier: str) -> dict:
    """Check source ingestion status.

    Args:
        identifier: MD5 hash or arxiv ID

    Returns:
        downloaded, ingested, calibre_id, entity_count, extraction_status
    """
```

### Ingestion Flow

When `auto_ingest=True`:
1. Download file to `calibre/ingest/` folder
2. Calibre auto-import daemon picks it up
3. `auto_ingest_daemon.py` extracts entities
4. Source becomes searchable in knowledge graph

### Dependencies

- Anna's Archive: Uses existing `mcp__annas__search` and `mcp__annas__download` internally
- Arxiv: Uses `arxiv` Python package for search and PDF download
- Calibre: Files placed in ingest folder for auto-import

## Future Extensions

Once validated, consider adding:
- Flow Mode exploration tools
- Spark/insight quick capture
- Journey retrieval and synthesis
- Cross-session pattern analysis
