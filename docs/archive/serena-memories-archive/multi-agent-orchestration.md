# Multi-Agent Orchestration System

## Context

Stop hooks for documentation validation were brittle:
- Fired too late (context compressed, user rushing)
- Could only validate, not do the work
- Required meta-overrides to bypass

## Decision

Implemented proactive multi-agent system with:
- **context-loader** (Haiku): Loads project context at session start
- **scribe** (Haiku): Updates documentation after significant work
- **reviewer** (Sonnet): Code review before completion

## Key Architectural Choices

1. **Two-tier maximum**: Main orchestrator → specialists (no nesting per Claude Code constraint)
2. **Haiku for cheap agents**: Context-loader and scribe can run frequently
3. **Sonnet for reasoning**: Reviewer needs deeper analysis
4. **File handoffs**: Structured prompts, not shared memory
5. **Hybrid triggers**: SessionStart hook + CLAUDE.md instructions + explicit /sync

## SiYuan Integration

Each project maps to a notebook:
- ies → 20251201113102-ctr4bco
- framework → 20251130004638-unaugyc
- therapy → 20251130004638-cm5m9g8

Scribe agent updates both progress.md and SiYuan notes.

## Files

- `.claude/agents/` - Agent definitions
- `.claude/commands/sync.md` - Manual trigger
- `docs/plans/2025-12-01-multi-agent-orchestration-design.md` - Full design

## Usage

- `/sync` to manually trigger documentation
- Scribe auto-spawns after commits, features, or before /clear
