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

## Quick Commands

**Post a message:**
```bash
echo '{"from":"claude","to":"codex","type":"task","subject":"...","body":"..."}' > .agents/queue/$(date +%Y%m%d_%H%M%S)_claude_codex_task.json
```

**Check inbox:**
```bash
cat .agents/queue/*_$(whoami)_*.json 2>/dev/null
```

**Update status:**
```bash
# Use the Python helper or edit .agents/status.json directly
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
