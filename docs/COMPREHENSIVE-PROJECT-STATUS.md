# brain_explore: Comprehensive Project Status

**Date:** December 5, 2025
**Status:** Phase 2c In Progress — Calibre Integration Complete, Entity Overlay Complete

---

## Executive Summary

**brain_explore** is a thinking partnership system that transforms how people explore complex knowledge domains. Instead of reading linearly or chatting with a generic AI, users think WITH an AI partner that adapts to their unique cognitive patterns while navigating a rich knowledge graph.

**The Core Insight:** "Instead of reading one book, you're reading a concept." The system surfaces all sources discussing any concept, enables non-linear exploration, and captures the user's thinking journey as breadcrumbs that reveal their patterns over time.

**Current Achievement:** All four architectural layers built and validated. Phase 2c delivering major integration features: Calibre as single source of truth, entity overlay highlighting in reader, reframe generation API.

---

## Architecture: Four Layers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       LAYER 4: READEST                                  │
│              Reading + Flow Exploration Interface                        │
│   • E-book reader with Flow mode toggle                                 │
│   • Entity overlay highlighting (Dec 5) with type-specific colors       │
│   • Calibre library browser (Dec 4) — browse, search, open books        │
│   • Split-panel: source text + entity panel with relationships          │
│   • Breadcrumb journey capture during reading sessions                  │
│   Status: MVP COMPLETE + Entity Overlay + Calibre Library               │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     LAYER 3: SIYUAN PLUGIN                              │
│                    Processing Hub (Dashboard)                            │
│   • Dashboard: stats, suggestions, recent journeys, capture queue       │
│   • ForgeMode: Template-driven structured thinking (Dec 5)              │
│   • 5 Thinking modes (Learning, Articulating, Planning, Ideating,       │
│     Reflecting) with mode-specific AI behaviors and templates           │
│   • Flow Mode: graph exploration with grouped relationships             │
│   • Quick Capture: content processing with entity extraction            │
│   • ReframesTab: view concept reframes (metaphors, analogies, stories)  │
│   Status: MVP COMPLETE + Template Integration                           │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       LAYER 2: BACKEND                                  │
│                 API, Dialogue, Profile Services                          │
│   • Graph API: entity search, exploration, sources, stats               │
│   • Books API (Dec 4): Calibre library catalog, file serving            │
│   • Entity API: by-book and by-calibre-id lookup with type filtering    │
│   • Reframe API (Dec 4): generate metaphors/analogies via Claude        │
│   • Template API (Dec 5): thinking templates for ForgeMode              │
│   • Personal Graph API: ADHD-friendly spark/insight capture             │
│   • Session API: structured thinking dialogue                           │
│   • Journey API: breadcrumb tracking and persistence                    │
│   Status: PRODUCTION READY (85/85 tests passing)                        │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    LAYER 1: KNOWLEDGE GRAPH                             │
│                     Neo4j + Qdrant + Calibre                             │
│   • Calibre library: 179 books (single source of truth)                 │
│   • Auto-ingestion daemon: processes books → entities automatically     │
│   • Current graph: 291 entities, 338 relationships (10 books indexed)   │
│   • Book corpus: 114 pre-processed + 179 Calibre library                │
│   • Vector embeddings for semantic search (Qdrant)                      │
│   Status: FULLY OPERATIONAL + Auto-Ingestion Running                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase Completion Summary

### Phase 0: Configuration Stabilization ✅
**Problem:** 40% of development time was meta-work (config sync, project switching)
**Solution:** Deleted active-project system, consolidated CLAUDE.md, moved to git history
**Result:** Configuration overhead dropped to <5%

### Phase 1: Core Hypothesis Validation ✅
**Goal:** Prove Layers 1 & 2 create genuine thinking partnership value
**Achieved:**
- 10/10 therapy exploration sessions completed
- 11 therapeutic concepts extracted and formalized
- Complete framework discovered (Narrow Window → Window as Condition for Depth)
- Pipeline validated: Session → Transcript → Extraction → Formalization → Commit

**Therapeutic Framework Discovered:**
1. **Narrow Window** — Universal constraint enables meaning (not pathology)
2. **Acceptance vs. Resignation** — Aliveness/energy distinguishes the two
3. **Grief as Acceptance** — Loss reveals love; presence preserves connection
4. **Metabolization of Difficulty** — Pain becomes capacity (not eliminated)
5. **Shame as Non-Acceptance** — Blocks metabolization and movement
6. **Authentic Presence** — Outcome of shame metabolization
7. **Nervous System Configurations** — Three states determine capacity
8. **Nervous System as Gatekeeper** — Capacity requires nervous system access
9. **Superpower in Weakness** — Trauma response becomes strength
10. **Window as Condition for Depth** — Constraint enables meaning and beauty
11. **Nervous System Sensing Possibility** — How the body knows before the mind

### Phase 2a: Layer 3 CLI Validation ✅
**Goal:** Prove graph exploration creates different value from dialogue
**Achieved:**
- 5/5 validation explorations completed
- Graph reveals dimensional complexity dialogue misses
- Thinking partner questions work at decision points
- Novel insights emerge from structure (e.g., shame→self-compassion paradox)

### Phase 2b: Visual Interface Implementation ✅
**Goal:** Build visual interfaces for Layer 3 exploration

**Readest Integration (Layer 4):**
- Flow mode toggle in reader header
- Split-panel view (resizable, pinnable)
- Entity panel: definition, relationships, sources, questions
- Text selection → entity lookup
- Breadcrumb journey capture
- Local storage fallback for offline

**SiYuan Plugin Evolution (Layer 3):**
- Dashboard as central hub
- 5 Structured Thinking modes
- Flow mode with grouped relationship display
- Quick Capture with entity extraction
- Journey resumption from dashboard
- "Contemplative Knowledge Space" design system

### Phase 2c: Integration Features 🔄 IN PROGRESS (65% complete)
**Goal:** Close critical gaps preventing real-world usage

**Completed (Dec 4-5):**
- ✅ **Calibre Integration** — Single source of truth for book catalog
  - CalibreService queries metadata.db (179 books)
  - Books API: catalog, search, covers, file serving
  - Book files servable via HTTP (no filesystem access needed)
  - calibre_id as universal identifier across all systems
- ✅ **Multi-Pass Ingestion Pipeline** — Automated book→entity extraction
  - Pass 1: structure + entities (IMPLEMENTED)
  - Auto-ingestion daemon running (5-minute polls)
  - 10/179 books indexed with 291 entities
- ✅ **Entity Overlay** — Inline highlighting in reading interface
  - Type-specific colors (Concept=blue, Person=green, Theory=purple, etc.)
  - Pill-based filter UI with master toggle
  - Click entity → opens Flow Panel with connections
- ✅ **Readest Calibre Library Browser** — Browse and open Calibre books
  - Searchable grid view with covers
  - Entity badge shows indexed status
  - Opens books via backend API (browser-compatible)
- ✅ **Reframe API** — Generate accessible explanations via Claude
  - Types: metaphor, analogy, story, pattern, contrast
  - Caching and feedback voting
  - UI components in both Readest and SiYuan
- ✅ **Template API** — Structured thinking templates for ForgeMode
  - JSON schema with sections, AI behaviors, graph mapping
  - Two templates: learning-mechanism-map, articulating-clarify-intuition
  - ForgeMode fetches and renders templates
- ✅ **SiYuan AST documentation set** — 20 notebook pages built across six sections (Structure, Modes, Question Engine, Schemas, Templates, Workflows)
  - Lives inside SiYuan notebook *Intelligent Exploration System* (`20251201113102-ctr4bco`)
  - Documents Discovery/Dialog/Flow/AST modes, ADHD-friendly folders, and mode transition guardrails
  - Mirrors specs in `docs/IES AST SiYuan structure.md` and `docs/IES question engine expansion.md` for Git-tracked reference

**In Progress:**
- 🔄 **Pass 2/3 Enrichment** — Relationship extraction and LLM enrichment
- 🔄 **Cross-App Continuity** — Sync state between Readest and SiYuan

---

## Current Worktree Organization

| Location | Branch | Purpose | Status |
|----------|--------|---------|--------|
| `/brain_explore/` | `master` | Backend APIs, shared docs | Active development |
| `.worktrees/readest/` | `feature/readest-integration` | Layer 4 Reading Interface | Entity Overlay + Calibre |
| `.worktrees/siyuan/` | `feature/siyuan-evolution` | Layer 3 Processing Hub | ForgeMode Templates |

**To work in a specific area:**
```bash
cd /home/chris/dev/projects/codex/brain_explore              # Backend/shared
cd /home/chris/dev/projects/codex/brain_explore/.worktrees/readest  # Readest
cd /home/chris/dev/projects/codex/brain_explore/.worktrees/siyuan   # SiYuan plugin
```

---

## Technical Stack

### Backend (Layer 2)
- **Framework:** FastAPI (Python)
- **Database:** Neo4j 5.x (graph)
- **Vector Store:** Qdrant (semantic search)
- **LLM:** Claude API (dialogue, questions, reframes)
- **Tests:** 85/85 passing (Dec 5)
- **Port:** 8081

### SiYuan Plugin (Layer 3)
- **Framework:** Svelte + TypeScript
- **Target:** SiYuan note-taking app
- **Design System:** "Contemplative Knowledge Space"
- **Deployment:** Mirror to Docker deployed directory

### Readest (Layer 4)
- **Framework:** Next.js + React + TypeScript
- **Desktop:** Tauri (Rust wrapper)
- **Rendering:** foliate-js (EPUB, PDF)
- **State:** Zustand (flowModeStore)
- **Source:** https://github.com/readest/readest (MIT)

### Infrastructure
- **Orchestration:** Docker Compose
- **Services:** Neo4j, Qdrant, Backend, Calibre-Web
- **Calibre Library:** 179 books, auto-ingestion daemon
- **Current Graph:** 291 entities, 338 relationships (10 books indexed)

---

## Key Files Reference

### Documentation
| File | Purpose |
|------|---------|
| `docs/PROJECT-OVERVIEW.md` | Original vision and Phase 1 plan |
| `docs/plans/2025-12-03-integrated-reading-knowledge-system.md` | Four-layer architecture design |
| `docs/plans/2025-12-04-calibre-integration-design.md` | Calibre as single source of truth |
| `docs/plans/2025-12-04-reframe-template-integration-design.md` | Phase 2c integration design |
| `docs/IES AST SiYuan structure.md` | SiYuan notebook layout, mode transitions, folder strategy |
| `docs/IES question engine expansion.md` | 9-question-class taxonomy powering AST mode |
| `docs/session-notes.md` | Complete session history |
| `docs/PHASE-2A-VALIDATION-RESULTS.md` | Layer 3 CLI validation |

### Backend APIs (Phase 2c)
| File | Purpose |
|------|---------|
| `ies/backend/src/ies_backend/api/books.py` | Calibre library catalog API |
| `ies/backend/src/ies_backend/api/book_entities.py` | Entity lookup by book/calibre_id |
| `ies/backend/src/ies_backend/api/reframe.py` | Reframe generation API |
| `ies/backend/src/ies_backend/api/template.py` | Thinking template API |
| `ies/backend/src/ies_backend/api/personal.py` | Personal graph API |
| `ies/backend/src/ies_backend/services/calibre_service.py` | Calibre DB queries |

### Ingestion Scripts
| File | Purpose |
|------|---------|
| `scripts/ingest_calibre.py` | Manual book ingestion CLI |
| `scripts/auto_ingest_daemon.py` | Automated background processing |
| `scripts/check_ingestion.py` | View processing status table |
| `scripts/manage_ingestion.py` | Start/stop ingestion services |

### Readest Code (Readest worktree)
| File | Purpose |
|------|---------|
| `src/app/library/components/CalibreDialog.tsx` | Calibre library browser |
| `src/app/reader/components/EntityTypeFilter.tsx` | Entity overlay controls |
| `src/app/reader/components/flowpanel/` | Flow Panel components |
| `src/store/flowModeStore.ts` | Flow state management |
| `src/services/transformers/entity.ts` | Entity highlight transformer |

---

## Available Backend Endpoints

### Graph API
```
GET  /graph/stats                           # Knowledge graph statistics
GET  /graph/search?q={query}                # Entity search
GET  /graph/explore/{entity_id}             # Neighborhood exploration
GET  /graph/sources/{entity_id}             # Book references
GET  /graph/suggestions                     # Dashboard topics
POST /graph/thinking-partner                # AI questions for entity
```

### Books API (NEW - Dec 4)
```
GET  /books                                 # List all books from Calibre
GET  /books?search={query}                  # Search by title/author
GET  /books/{calibre_id}                    # Get single book
GET  /books/{calibre_id}/cover              # Fetch cover image
HEAD /books/{calibre_id}/file               # File metadata (size, type)
GET  /books/{calibre_id}/file               # Serve epub/pdf file
```

### Entity API
```
GET  /graph/entities/by-book/{book_hash}    # Entities by book hash
GET  /graph/entities/by-calibre-id/{id}     # Entities by Calibre ID
```

### Reframe API (NEW - Dec 4)
```
GET  /concepts/{id}/reframes                # Get cached reframes
POST /concepts/{id}/reframes/generate       # Generate via Claude
POST /reframes/{id}/feedback                # Vote helpful/confusing
```

### Template API (NEW - Dec 5)
```
GET  /templates/{template_id}               # Get thinking template
```

### Personal Graph API (NEW - Dec 4)
```
POST /personal/sparks                       # Create spark
GET  /personal/sparks/{id}                  # Get spark
POST /personal/sparks/{id}/visit            # Record visit
POST /personal/sparks/{id}/promote          # Promote to insight
GET  /personal/sparks/by-resonance/{signal} # Find by emotional state
GET  /personal/sparks/by-energy/{level}     # Find by energy level
GET  /personal/stats                        # Personal graph stats
```

### Journey API
```
POST   /journeys                            # Save breadcrumb journey
GET    /journeys/{id}                       # Retrieve journey
GET    /journeys/user/{user_id}             # List user's journeys
PATCH  /journeys/{id}                       # Update journey
DELETE /journeys/{id}                       # Delete journey
```

### Session API
```
POST /session                               # Start structured thinking session
POST /session/{id}/message                  # Send message in session
GET  /session/context/{user_id}             # Load session context
```

---

## Current Graph Statistics (Dec 5)

```json
{
  "entities": 291,
  "relationships": 338,
  "books": 10,
  "node_counts": {
    "Concept": 134,
    "Researcher": 118,
    "Theory": 22,
    "Book": 10,
    "Assessment": 7
  },
  "relationship_counts": {
    "MENTIONS": 324,
    "COMPONENT_OF": 4,
    "SUPPORTS": 4,
    "DEVELOPS": 3,
    "CONTRADICTS": 2,
    "CITES": 1
  }
}
```

**Note:** This reflects the new Calibre-based ingestion. 10 books have been indexed so far. The auto-ingestion daemon is processing additional books in the background.

---

## Next Steps (Phase 2c Completion)

### Immediate Priorities
1. **Continue Auto-Ingestion** — Let daemon process remaining 169 books
2. **Pass 2 Implementation** — Extract relationships between entities
3. **Pass 3 Enrichment** — Generate reframes for popular concepts

### Near-Term
4. **Cross-App Continuity** — Sync journeys between Readest and SiYuan
5. **User Testing** — Get feedback on complete Flow experience
6. **Performance Optimization** — Profile API calls, optimize slow queries

### Deferred (Parking Lot)
- Multi-domain framework generalization
- Advanced profile system (8 dimensions)
- Question engine (8 inquiry approaches)
- MCP server integration
- n8n workflow automation

---

## Quick Commands

```bash
# Verify backend health
curl http://localhost:8081/health

# Check graph stats
curl http://localhost:8081/graph/stats

# Start infrastructure
docker compose up -d

# Run backend
cd ies/backend && uv run uvicorn ies_backend.main:app --host 0.0.0.0 --port 8081

# Run backend tests
cd ies/backend && uv run pytest

# Check ingestion status
python scripts/check_ingestion.py

# Start auto-ingestion daemon
python scripts/auto_ingest_daemon.py &

# Build plugin
cd ies/plugin && npm run build

# Check worktree status
git worktree list
```

---

## Project Health Summary

| Metric | Status |
|--------|--------|
| Backend Tests | 85/85 passing |
| API Health | All endpoints working |
| Calibre Library | 179 books |
| Books Indexed | 10/179 (auto-ingestion running) |
| Current Entities | 291 |
| Current Relationships | 338 |
| Layer 1 | ✅ Operational + Auto-Ingestion |
| Layer 2 | ✅ Production Ready |
| Layer 3 | ✅ MVP + Templates |
| Layer 4 | ✅ MVP + Entity Overlay + Calibre |
| Documentation | ✅ Up to date |

**Overall Status:** Phase 2c 65% complete. Major integration features delivered. Auto-ingestion building graph in background.

---

*Last Updated: December 5, 2025*
