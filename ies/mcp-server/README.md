# IES MCP Server

ForgeMode thinking sessions via Claude Desktop and mobile voice interface.

## Overview

A lightweight MCP server that wraps the IES backend APIs, enabling voice-driven structured thinking sessions. Uses Redis session persistence via the backend.

## Available Tools

| Tool | Purpose |
|------|---------|
| `start_session` | Begin ForgeMode session with mode + topic |
| `submit_response` | Answer current question, get next |
| `end_session` | Complete session, trigger extraction |
| `get_question` | Get current question (context recovery) |
| `list_templates` | Available thinking modes |
| `get_status` | Session state, progress, history |

## Thinking Modes

- **learning** — Understand how something works (Mechanism Map template)
- **articulating** — Clarify vague intuitions (Clarify Intuition template)
- **planning** — (coming soon)
- **ideating** — (coming soon)
- **reflecting** — (coming soon)

## Installation

```bash
cd ies/mcp-server
pip install -r requirements.txt
```

## Claude Desktop Configuration

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

## Prerequisites

1. **Infrastructure running:**
   ```bash
   docker compose up -d  # Neo4j, Redis, Qdrant
   ```

2. **Backend running:**
   ```bash
   cd ies/backend
   uv run uvicorn ies_backend.main:app --port 8081
   ```

## Testing

1. Start infrastructure and backend (see above)
2. Debug MCP server directly:
   ```bash
   python ies/mcp-server/server.py
   ```
3. Restart Claude Desktop to load the MCP
4. Test via voice: "Start a learning session about executive function"

## Example Conversation

> **You:** "Start a learning session about executive function"
>
> **Claude:** *calls start_session(mode="learning", topic="executive function")*
>
> "I've started a learning session about executive function. First question: What concept or system are you trying to understand?"
>
> **You:** "I want to understand how executive function relates to ADHD and self-regulation"
>
> **Claude:** *calls submit_response(session_id, response)*
>
> "Great. Next question: List the key components or actors involved."
>
> **You:** "The prefrontal cortex, working memory, inhibition, and emotional regulation"
>
> *...continues through template sections...*
>
> **You:** "That's enough for now"
>
> **Claude:** *calls end_session(session_id)*
>
> "Session complete! I extracted 3 concepts and saved the session to your SiYuan notebook."

## Session Recovery

If your conversation is interrupted (app restart, voice timeout), use:

- `get_question` — Retrieves current question to continue
- `get_status` — Shows full session progress and history

Sessions persist in Redis for 24 hours with automatic TTL extension on activity.
