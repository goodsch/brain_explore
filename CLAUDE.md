# brain_explore — Meta-Cognitive Exploration System

*Helping people understand how they think so they can achieve meaningful change*

## What This Is

A system for exploring therapeutic worldviews through three interconnected capabilities:

1. **Flow Mode** — Non-linear knowledge navigation with AI documentation
   - Start anywhere in the knowledge graph, follow threads of interest
   - AI documents your exploration path and connections made

2. **Thinking Pattern Identification** — Recognize cognitive patterns through observation
   - System observes where you navigate, what you connect, how you think
   - Builds a profile of your unique thinking style

3. **Therapeutic Dialogue** — Adaptive questioning based on identified patterns
   - Questions adapt to how you think, not generic prompts
   - Creates insight through understanding your unique perspective

**Why This Works:** These three layers reinforce each other. Flow Mode reveals patterns. Patterns inform dialogue. Dialogue surfaces concepts. Concepts expand knowledge graph. Knowledge graph enables deeper flow.

## Current Status

**Phase 0: Configuration Stabilization** ✅ COMPLETE

All success criteria met:
- IES backend: ✅ Production-ready (4,496 lines Python, 61 tests)
- IES plugin: ✅ Functional (14,092 lines TypeScript/Svelte)
- Core infrastructure: ✅ Complete (Neo4j with 48,987 entities)
- Configuration system: ✅ Cleaned up (40% overhead → <5%)

**Phase 0 Completion Summary:**
- Git repository initialized with all 732 files committed
- CLAUDE.md consolidated from 4 files (459+ lines) into 1 authoritative file (166 lines)
- Session notes system established (docs/session-notes.md for append-only reflection)
- Progress files archived (docs/archive/) to preserve history without cluttering active workspace
- Configuration overhead eliminated: removed .active-project tracking system
- Serena memories consolidated (11 → 4 essential files) for focus
- Parking lot created to enforce Phase 1 discipline (nothing new until core hypothesis is proven)
- 11 commits establishing clean git history for project tracking

**Next:** Phase 1 - Prove core hypothesis works through therapy exploration

## How to Work Here

### Before Starting Any Session

1. Read `docs/five-agent-synthesis.md` (15 min) - understand vision and Phase 1 plan
2. Check git log (`git log --oneline -10`) to see recent work
3. Review `docs/session-notes.md` for context from previous sessions
4. Verify you're not touching items in `docs/parking-lot.md` (reserved for Phase 1 completion)

### During Your Session

1. Work on one focused task at a time
2. Commit frequently (every 30-60 min): `git commit -m "..."`
3. At session end, update `docs/session-notes.md` with what you did

### After Your Session

1. Run: `git status` (verify everything is committed)
2. Append entry to `docs/session-notes.md` with:
   - What you accomplished
   - What you learned
   - Blockers you hit
   - What next session should focus on
   - Any decisions made affecting system design

**Workflow Note:** Git history is now the source of truth for what changed. Session notes are for reflection, decisions, and handoff context. Together they create a complete project memory.

## Project Structure

```
brain_explore/
├── ies/                           # Intelligent Exploration System
│   ├── backend/                   # FastAPI backend (4,496 lines Python)
│   │   ├── src/ies_backend/       # API, services, schemas
│   │   └── tests/                 # 61 unit tests
│   └── plugin/                    # SiYuan plugin (14,092 lines TS/Svelte)
│
├── therapy/                       # Therapy Framework (Content Layer)
│   └── (concepts, tracks, research)
│
├── library/                       # Shared: GraphRAG modules (Python)
├── scripts/                       # Shared: CLI tools
├── books/                         # Shared: 63 psychology/therapy books
│
├── docs/                          # Documentation
│   ├── five-agent-synthesis.md    # Vision, gaps, lessons, phased path
│   ├── true-vision-document.md    # Vision extraction and articulation
│   ├── session-notes.md           # Session reflection (append-only)
│   ├── parking-lot.md             # Future features (don't work on these)
│   └── archive/                   # Old progress files, archived memories
│
└── docker-compose.yml             # Neo4j + Qdrant infrastructure
```

## Key Resources

**Start Here:**
- `docs/five-agent-synthesis.md` — Complete analysis with vision, gaps, lessons, phased path

**Reference:**
- `docs/true-vision-document.md` — Vision extraction (why this system makes sense)
- `docs/timeline-analysis.md` — How project evolved (understand the journey)
- `docs/parking-lot.md` — Future features (what NOT to work on yet)

**Technical:**
- `ies/backend/README.md` — Backend setup and API
- `ies/plugin/README.md` — Plugin development
- `docker-compose.yml` — Infrastructure setup

## The Parking Lot

**Don't work on these until Phase 1 is complete:**
- Multi-domain framework generalization
- Advanced profile system (8 dimensions)
- Question engine (8 inquiry approaches)
- Flow Mode reading interface
- MCP server integration
- n8n integration
- Synapse component ports

**Rule:** Nothing new enters development until core vision is proven valuable through Phase 1 therapy exploration.

## Development Workflow

### Making Changes

```bash
# Make your changes to files
# ... edit code ...

# Commit frequently
git add .
git commit -m "Clear message about what changed and why"

# Update session notes at end of session
# Add entry to docs/session-notes.md with:
# - What accomplished
# - What learned
# - Blockers
# - Next steps
```

### Running Tests

```bash
cd ies/backend
uv run pytest                    # Run all tests
uv run pytest -v                 # Verbose output
uv run pytest tests/file.py      # Run specific test file
```

### Building Plugin

```bash
cd ies/plugin
npm install                      # Install dependencies
npm run build                    # Build plugin
npm run dev                      # Development mode
```

## Quick Commands

```bash
git log --oneline -20            # See recent commits
git diff                         # See uncommitted changes
git status                       # See current state
docker compose up -d             # Start Neo4j + Qdrant
docker compose down              # Stop services
```

## Questions?

See `docs/five-agent-synthesis.md` for comprehensive understanding of:
- What the vision actually is
- Why configuration was blocking work
- Why projects kept expanding
- What Synapse teaches us
- Clear phased path forward
