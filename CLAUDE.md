<!-- MANUAL -->
# brain_explore — Intelligent Exploration System

*Domain-agnostic tool for structured thinking and knowledge exploration*

> **Ground Truth:** `docs/IES-SYSTEM-DESIGN.md`
>
> **Document Hierarchy:**
> 1. `docs/IES-SYSTEM-DESIGN.md` — WHY & HOW (cognitive architecture, operating model)
> 2. `docs/UNIFIED-PROJECT-SPEC-2025-12-09.md` — What's active vs archived
> 3. `docs/ARCHITECTURE-AND-INTERACTIONS.md` — Technical APIs and data flows
> 4. `docs/GAP-ANALYSIS-2025-12-09.md` — Implementation status
>
> **TL;DR:** IES Reader is ACTIVE. Readest is ARCHIVED.

## Four-Layer System

| Layer | Component | Purpose |
|-------|-----------|---------|
| 1 | Knowledge Graph | 179 books → entities/relationships (Neo4j) |
| 2 | Backend APIs | FastAPI, 411 tests passing |
| 3 | SiYuan Plugin | Dashboard, 5 thinking modes, flow exploration |
| 4 | IES Reader | E-book reader with entity overlay and flow panel |

## Current Sprint (Dec 9, 2025)

**Phase 2c: 98% Complete**

✅ Completed:
- Cross-app session sync (IES Reader ↔ SiYuan)
- Pass 2/3 enrichment pipeline (relationships + LLM)
- Extraction Engine with UI integration
- All 5 thinking templates
- Highlight sync with block attributes
- P1/P2 Reader integration (What's New, Timeline)

🔄 In Progress:
- Redis migration for session persistence
- Journey pattern analysis

## Quick Start

```bash
# Infrastructure
docker compose up -d

# Backend (port 8081)
cd ies/backend && uv run uvicorn ies_backend.main:app --reload --port 8081

# IES Reader (port 5173)
cd ies/reader && pnpm dev

# SiYuan Plugin (in worktree)
cd .worktrees/siyuan/ies/plugin && pnpm dev
```

## Project Structure

```
brain_explore/
├── ies/backend/          # FastAPI (Layer 2)
├── ies/reader/           # IES Reader (Layer 4)
├── library/graph/        # Neo4j client, entity extraction
├── .worktrees/siyuan/    # SiYuan plugin (Layer 3)
└── docs/                 # Documentation
```

## Key Commands

```bash
# Tests
cd ies/backend && uv run pytest

# Docker
docker compose up -d      # Start
docker compose ps         # Status

# Git
git log --oneline -10     # Recent commits
```

## Worktrees

| Location | Branch | Purpose |
|----------|--------|---------|
| `.` (root) | `master` | Backend APIs only |
| `.worktrees/siyuan/` | `feature/siyuan-evolution` | SiYuan plugin |
| `.worktrees/ies-reader/` | `feature/ies-reader-enhancement` | IES Reader |

**Archived:** `.worktrees/readest/` — DO NOT USE

## Critical Constraints

**DO NOT:**
- Work on features in master branch (use worktrees)
- Skip tests before committing
- Reference Readest in new code (use IES Reader)

**ALWAYS:**
- Check git status before starting
- Run tests after changes
- Use Serena symbolic tools for code exploration
- Check ground truth docs for architecture questions

## On-Demand Resources

For detailed implementation info, use these resources instead of expecting everything here:

| Need | Resource |
|------|----------|
| API endpoints | `docs/ARCHITECTURE-AND-INTERACTIONS.md` |
| Implementation gaps | `docs/GAP-ANALYSIS-2025-12-09.md` |
| Calibre integration | `docs/plans/2025-12-04-calibre-integration-design.md` |
| Pass 2/3 pipeline | `docs/plans/2025-12-09-pass-2-relationship-extraction.md` |
| Session sync design | `docs/plans/2025-12-09-context-sync-design.md` |
| Changelog | `docs/CHANGELOG.md` |

## Serena Memories

Query on-demand with `mcp__serena__read_memory`:

| Memory | Content |
|--------|---------|
| `project-status-dec9` | Current status, document hierarchy |
| `ies_architecture` | Technical implementation details |
| `deprecated-readest` | Warning about archived Readest |

## Working Style

Claude acts as project manager. Identify optimal next action and proceed — don't ask what to work on. User will redirect if needed.
<!-- END MANUAL -->

<!-- AUTO-MANAGED: build-commands -->
## Build Commands

| Component | Command |
|-----------|---------|
| Backend | `cd ies/backend && uv run uvicorn ies_backend.main:app --reload --port 8081` |
| Backend Tests | `cd ies/backend && uv run pytest` |
| IES Reader | `cd ies/reader && pnpm dev` |
| Docker | `docker compose up -d` |
| SiYuan Plugin | `cd .worktrees/siyuan/ies/plugin && pnpm dev` |
<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: architecture -->
## Architecture Quick Reference

> **Full details:** See `docs/ARCHITECTURE-AND-INTERACTIONS.md`

**Backend API Routes** (registered in `main.py`):

| Route | Purpose |
|-------|---------|
| `/context` | Context CRUD, parsing, search |
| `/questions` | Question CRUD, relevant passages |
| `/graph` | Entity search, facets, relationships |
| `/session-state` | Cross-app sync (IES Reader ↔ SiYuan) |
| `/highlights` | Highlight CRUD with SiYuan sync |
| `/visits` | "What's new" tracking |
| `/journey-timeline` | Exploration history |
| `/extraction` | Context-aware entity extraction |
| `/books` | Calibre catalog, covers, files |
| `/reframes` | Concept metaphors/analogies |
| `/templates` | Thinking mode templates |

**Key Services:**
- `SessionStateService` — Cross-app state (in-memory, needs Redis)
- `ExtractionEngine` — Context-aware entity extraction (600 lines)
- `HighlightSyncService` — Reader → SiYuan sync
- `PassageRankingService` — Question-driven reading

**Entity Types (14):**
- Domain: Concept, Person, Theory, Framework, Assessment
- Personal: Spark, Insight, Thread, FavoriteProblem, Reframe
- Patterns: Pattern, DynamicPattern, StoryInsight, SchemaBreak

**Question Engine (9 classes):**
Schema-Probe, Boundary, Dimensional, Causal, Counterfactual, Anchor, Perspective-Shift, Meta-Cognitive, Reflective-Synthesis

**IES Reader Components** (`ies/reader/src/`):
- `Reader.tsx` — epub.js wrapper with selection handling
- `FlowPanel.tsx` — Entity exploration panel
- `useSessionSync` — Backend state sync hook
- `useReadingPosition` — CFI-based position tracking
- `flowStore.ts` — Zustand state management

**SiYuan Plugin** (`.worktrees/siyuan/ies/plugin/src/`):
- `FlowMode.svelte` — Graph exploration (113KB)
- `ForgeMode.svelte` — Structured thinking (110KB)
- `ContextSyncService.ts` — Backend polling for cross-app sync
<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: conventions -->
<!-- Reserved for future use -->
<!-- END AUTO-MANAGED -->
