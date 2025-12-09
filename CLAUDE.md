<!-- MANUAL -->
# brain_explore — Intelligent Exploration System

*Domain-agnostic tool for structured thinking and knowledge exploration*

## What This Is

Four-layer system for AI-partnered knowledge exploration:

| Layer | Component | Purpose |
|-------|-----------|---------|
| 1 | Knowledge Graph | Ingests materials → entities/relationships (179 books, ~300 entities) |
| 2 | Backend APIs | Graph, dialogue, journeys, profiles (185 tests passing) |
| 3 | SiYuan Plugin | Dashboard, 5 thinking modes, flow exploration |
| 4 | IES Reader | Standalone e-book reader with entity overlay and flow panel |

**Note:** IES Reader replaced Readest (Dec 2025). Readest worktree is archived, no longer in active development.

**The Virtuous Cycle:** Dialogue reveals thinking patterns → personalized exploration → concept discovery → enriches graph → deeper exploration.

## Current Status

**Phase 2c: ~75% complete** (Dec 7, 2025)

Completed:
- 5-wave backend remediation (all components production-ready)
- IES Reader Waves 1-3 (library, PWA, interactive, mobile UX)
- IES MCP Server (voice-driven ForgeMode via Claude Desktop)
- SiYuan remediation complete
- Conversation service (parse Claude exports → Neo4j)

In Progress:
- Pass 2/3 enrichment pipeline
- Cross-app sync

See `docs/CHANGELOG.md` for detailed history.

## Quick Start

```bash
# Start infrastructure
docker compose up -d

# Backend (port 8081)
cd ies/backend && uv run uvicorn ies_backend.main:app --reload --port 8081

# SiYuan plugin development
cd .worktrees/siyuan/ies/plugin && pnpm dev

# IES Reader development
cd .worktrees/ies-reader/ies/reader && pnpm dev
```

## Project Layout

```
brain_explore/
├── ies/backend/           # FastAPI backend (Layer 2)
├── calibre/library/       # Book catalog (179 books)
├── library/graph/         # Neo4j client, entity extraction
├── .worktrees/
│   ├── siyuan/           # SiYuan plugin (Layer 3)
│   ├── ies-reader/       # IES Reader (Layer 4) - active
│   └── readest/          # Archived - replaced by IES Reader
└── docs/                  # Documentation
```

**Worktrees:** Feature work happens in worktrees, not master branch.
- `.worktrees/siyuan/` → SiYuan plugin on `feature/siyuan-evolution`
- `.worktrees/ies-reader/` → IES Reader on `feature/ies-reader-enhancement` (ACTIVE)
- `.worktrees/readest/` → Archived (replaced by IES Reader)
- Master branch → Backend only

## Key Commands

```bash
# Tests
cd ies/backend && uv run pytest

# Docker
docker compose up -d      # Start
docker compose ps         # Status
docker compose down       # Stop

# Git
git log --oneline -10     # Recent commits
git status                # Current state
```

## Critical Constraints

**DO NOT:**
- Work on features in master branch (use worktrees)
- Skip tests before committing
- Add therapy-specific hardcoding (system is domain-agnostic)

**ALWAYS:**
- Check git status before starting work
- Run tests after changes: `uv run pytest`
- Use Serena symbolic tools for code exploration
- Check `docs/SYSTEM-DESIGN.md` for architecture questions

## Key Resources

| Resource | Purpose |
|----------|---------|
| `docs/SYSTEM-DESIGN.md` | Architecture and data flows |
| `docs/CHANGELOG.md` | Development history |
| `docs/plans/` | Feature design documents |
| Serena memory: `true_vision` | Core project vision |

## Working Style

Claude acts as project manager. Identify optimal next action and proceed — don't ask what to work on. User will redirect if needed.

## Context Efficiency

This CLAUDE.md is intentionally brief. For details:
- **History:** `docs/CHANGELOG.md`
- **Architecture:** Use `mcp__serena__read_memory` with `ies_architecture`
- **Implementation:** Read code with Serena symbolic tools
- **Plans:** Check `docs/plans/` directory
<!-- END MANUAL -->
