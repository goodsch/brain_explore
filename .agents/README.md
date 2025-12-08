# Cross-Agent Communication System

Three AI agents collaborate on this project. This directory provides structured communication.

## Agents

| Agent | Config File | Strengths |
|-------|-------------|-----------|
| **Claude** | `CLAUDE.md` | Project manager, architecture, complex reasoning, tests |
| **Codex** | `AGENTS.md` | Deep reasoning, design decisions, focused implementation |
| **Gemini** | `GEMINI.md` | Web research, codebase analysis, parallel exploration |

## Communication Protocol

### Message Queue: `.agents/queue/`

Agents post messages as JSON files. Filename format: `{timestamp}_{from}_{to}_{type}.json`

**Types:**
- `task` — Work assignment
- `question` — Needs input from another agent
- `update` — Status/progress update
- `handoff` — Completing work, passing to another agent
- `blocker` — Stuck, needs help

**Example:** `20251207_143022_claude_codex_task.json`

### Reading Messages

Each agent should check for messages on session start:
```bash
ls -la .agents/queue/*_${AGENT_NAME}_*.json 2>/dev/null
```

After processing, move to `.agents/archive/`.

### Status Board: `.agents/status.json`

Real-time status of each agent's current work. Updated when starting/completing tasks.

### Shared Context: `.agents/context/`

Longer-form shared documents:
- `decisions.md` — Architecture decisions made
- `blockers.md` — Current blockers across all agents
- `learnings.md` — Lessons learned, patterns discovered

## Quick Commands (No Script Required)

All agents can communicate by directly reading/writing JSON files.

**Post a message:**
```
1. Create file: .agents/queue/{YYYYMMDD}_{HHMMSS}_{from}_{to}_{type}.json
2. Write JSON with schema below
```

**Check inbox (look for messages addressed to you):**
```
Read files matching: .agents/queue/*_{your_agent_name}_*.json
Also check: .agents/queue/*_all_*.json (broadcast messages)
```

**After processing a message:**
```
Move file from .agents/queue/ to .agents/archive/
```

**Update your status:**
```
Edit .agents/status.json directly - update your agent's entry
```

## Message Schema

```json
{
  "from": "claude|codex|gemini",
  "to": "claude|codex|gemini|all",
  "type": "task|question|update|handoff|blocker",
  "priority": "low|normal|high|urgent",
  "subject": "Brief description",
  "body": "Detailed message",
  "context": {
    "files": ["paths/affected"],
    "branch": "current-branch",
    "related_task": "optional-reference"
  },
  "created_at": "ISO8601 timestamp"
}
```
