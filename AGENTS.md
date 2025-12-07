# AGENTS — Codex Operating Guide

This repo is stewarded by Claude; Codex should follow these rules to stay in sync with current development.

## Purpose
- Mirror CLAUDE.md priorities while giving Codex concrete steps to ship work safely.
- Keep work scoped to the correct worktree and run the right checks before handoff.

## Current Phase (Dec 7, 2025)

**Phase 2c: ~75% complete**

| Component | Status |
|-----------|--------|
| Backend APIs | 185 tests passing |
| IES Reader Wave 1 | ✅ Complete (library, PWA, design system) |
| IES Reader Wave 2 | ✅ Complete (interactive features) |
| IES Reader Wave 3 | 🔄 Section 2 done, Sections 1/3/4 pending |
| Reframe Layer Pass 1 | ✅ Entity extraction (9 types) |
| Reframe Layer Pass 2 | ✅ Cross-domain mapping |
| Reframe Layer Pass 3 | ✅ Generative reframes |
| Cross-app sync | ⏳ Pending |

## Worktrees & Branching

**Use worktrees, not master, for feature work:**

| Worktree | Branch | Purpose |
|----------|--------|---------|
| `.worktrees/siyuan/` | `feature/siyuan-evolution` | SiYuan plugin (Layer 3) |
| `.worktrees/readest/` | `feature/readest-integration` | Readest fork (Layer 4) |
| `.worktrees/ies-reader/` | `feature/ies-reader` | Standalone IES Reader |
| `.worktrees/ux-dev/` | `feature/ux-development` | Design system work |
| `.worktrees/flowmode/` | varies | Flow mode features |

**Master branch is for backend only; do not land feature work there.**

Always check `git status` before edits; never revert unrelated changes.

## Stack Quickstart

```bash
# Infrastructure
docker compose up -d

# Backend dev (port 8081)
cd ies/backend && uv run uvicorn ies_backend.main:app --reload --port 8081

# Backend tests
cd ies/backend && uv run pytest

# IES Reader dev
cd .worktrees/ies-reader/ies/reader && pnpm dev

# SiYuan plugin dev
cd .worktrees/siyuan/ies/plugin && pnpm dev

# Readest dev
cd .worktrees/readest/readest/apps/readest-app && pnpm dev
```

## Serena Memories

**Always check relevant memories before starting work:**

| Memory | Purpose |
|--------|---------|
| `ies_architecture` | Current 4-layer architecture, API routes, entity types, Docker services |
| `true_vision` | Core project vision (meta-cognitive exploration system) |
| `configuration_impact` | Configuration decisions and their effects |
| `books-to-download` | Book acquisition queue |

**Usage:**
```
mcp__serena__read_memory(memory_file_name="ies_architecture")
```

## Reframe Layer Pipeline

The enrichment pipeline for ADHD-friendly knowledge graph:

| Pass | File | Purpose |
|------|------|---------|
| Pass 1 | `library/graph/entities.py` | Extract 9 entity types from text |
| Pass 2 | `library/graph/reframe_mapper.py` | Cross-domain resonance check |
| Pass 3 | `library/graph/reframe_generator.py` | Generate reframes for dense concepts |

**Entity types:** concept, researcher, theory, assessment, pattern, dynamic_pattern, story_insight, schema_break, reframe

**Integration:** `scripts/auto_ingest_daemon.py` runs Pass 1 + Pass 2 automatically.

## Key Documentation

| Resource | Purpose |
|----------|---------|
| `CLAUDE.md` | Full project instructions (read at session start) |
| `docs/SYSTEM-DESIGN.md` | Architecture and data flows |
| `docs/CHANGELOG.md` | Development history |
| `docs/plans/` | Feature design documents |
| `docs/plans/2025-12-07-reframe-layer-methodology.md` | Reframe Layer design |
| `docs/plans/2025-12-07-ies-reader-wave3-design.md` | IES Reader Wave 3 spec |

## Guardrails

- **DO NOT** hardcode therapy-specific logic; system stays domain-agnostic.
- **DO NOT** commit secrets, book files, or session data.
- **DO** run relevant tests before handoff (backend: `uv run pytest`).
- **DO** prefer small, focused commits with imperative prefixes (`fix:`, `feat:`, `docs:`).

## Coding Conventions

**Python (backend/library):**
- PEP 8, 4-space indents, snake_case
- Typed dataclasses/Pydantic models
- Small public API surface, documented

**TypeScript/Svelte (plugin/reader):**
- ES modules, camelCase vars, PascalCase components
- State in stores/modules
- Co-located component styles

**Tests:**
- Mirror module paths (`tests/services/test_foo.py`)
- Deterministic fixtures over live API calls

## How Codex Should Operate

1. **Start session:** Read `CLAUDE.md`, check Serena memories (`ies_architecture`, `true_vision`)
2. **Before edits:** `git status` to understand current state
3. **Navigate code:** Use Serena symbolic tools (`find_symbol`, `get_symbols_overview`, `search_for_pattern`)
4. **Make changes:** Scoped to correct worktree, run targeted checks
5. **Finish:** Summarize changes and next steps

**If unexpected repo changes appear, pause and ask the user rather than cleaning them.**

## Current Focus Areas

1. **IES Reader Wave 3** — Mobile optimization (hide nav arrows, FAB for notes, touch targets)
2. **Cross-app sync** — SiYuan ↔ Readest state sharing
3. **Pass 4** — Pattern type classification (deferred/optional)

## Backend API Routes

| Route | Purpose |
|-------|---------|
| `/graph` | Entity search, exploration, relationships |
| `/session` | Thinking sessions, ForgeMode |
| `/journeys` | Breadcrumb tracking, synthesis |
| `/profile` | User profiles, login |
| `/books` | Calibre catalog, covers, files, ingestion queue |
| `/templates` | Thinking mode templates |
| `/reframes` | Concept metaphors/analogies |
| `/personal` | Sparks, insights, ADHD-friendly capture |
| `/flow` | Flow session lifecycle |
| `/capture` | Quick capture queue |
| `/thinking` | Thinking session lifecycle |

## Docker Services

```
brain_explore_neo4j     # 7474, 7687
brain_explore_qdrant    # 6333, 6334
brain_explore_redis     # 6379
brain_explore_calibre   # 8083
brain_explore_siyuan    # 6806
```
