<!-- MANUAL -->
# ⚠️ WORKTREE: Readest Integration (Phase 2)

**READ FIRST: `TASK.md`** - Contains your specific objectives for this worktree.

**Branch:** `feature/readest-integration`
**Purpose:** Build Readest Flow mode for conceptual reading exploration

---

# brain_explore — Guided Knowledge Exploration System

*A domain-agnostic architecture for personalized, AI-guided exploration of large knowledge domains*

## What This Is

A three-layer system that enables people to think WITH an AI partner who adapts to their unique thinking style while exploring complex knowledge domains:

1. **Layer 1: Knowledge Graph Creation** — Pre-processing and ingestion pipeline
   - Ingests domain materials (texts, research, conceptual frameworks)
   - Creates a rich knowledge graph with 50k+ entities and relationships
   - Currently applied to therapy domain (50k entities already processed)
   - Domain-agnostic: can ingest and structure any knowledge domain

2. **Layer 2: Thinking Pattern Revelation & Personalized Dialogue** — Profile system + adaptive questioning
   - Adaptive questioning reveals HOW a person thinks (their patterns, assumptions, perspective)
   - Profile captures user's approach, preferences, and exploration patterns
   - Dialogue adapts to their unique thinking style, not generic prompts
   - Creates insight through understanding their distinctive perspective
   - Foundation for personalized guidance in downstream interactions

3. **Layer 3: Thinking Partnership Exploration** — Flow/Flo interface where understanding AND generation happen together
   - Interactive knowledge exploration where users engage with domain materials and knowledge graph
   - AI acts as a thinking partner—asking clarifying questions, surfacing connections, challenging assumptions
   - System documents the user's exploration path and thinking process as breadcrumbs
   - DUAL OUTCOME: Both deepen understanding of existing knowledge AND generate novel conceptualizations
   - User extracts and formalizes their own insights from the thinking partnership

**The Virtuous Cycle:** Layer 2 dialogue reveals thinking patterns that inform how Layer 3 personalizes exploration. Layer 3 exploration surfaces new concepts and connections the user generates. The thinking path becomes formalized concepts that enrich the knowledge graph and inform next sessions. Each cycle deepens both domain understanding and the personalization of the thinking partnership.

## Current Status

**Phase 2b: Build Visual Interface for Layer 3** MVP COMPLETE

**All Three Layers Validated:**
- ✅ Layer 1: Knowledge graph creation (50k therapy entities, ingestion pipeline proven)
- ✅ Layer 2: Profile system + adaptive dialogue (dialogue sessions proven to generate novel concepts)
- ✅ Layer 3: CLI exploration tool validated (5 focused explorations, thinking partner questions work)

**Phase 2b Implementation (Readest Integration):** MVP DELIVERED
- ✅ **Readest forked and integrated** — Tauri-based e-book reader with Rust backend + TypeScript/Svelte frontend
- ✅ **Flow Mode Store** — Complete Zustand state management with breadcrumb journey tracking
- ✅ **Graph API Client** — Entity lookup, relationships, sources, thinking partner questions integration
- ✅ **Journey Storage** — Local storage persistence for offline-safe exploration
- ✅ **Flow Panel Components** — Modular UI: EntitySection, RelationshipsSection, SourcesSection, QuestionsSection
- ✅ **Flow Mode Toggle** — Start/end journey lifecycle with backend sync
- ✅ **Text Selection Hook** — useFlowEntity for entity lookup from selected text
- ✅ **Text Selection Popup Integration** — Flow button added to text selection annotation popup (Annotator.tsx)
- ✅ **All Deliverables Complete** — See TASK.md for full checklist

**Phase 1 Achievement Summary:**
- ✅ **10/10 therapy exploration sessions completed** — Complete therapeutic dialogue cycle validated
- ✅ **11+ therapeutic concepts extracted and formalized** — Comprehensive framework discovered
- ✅ **Complete concept connection map** — Hierarchical relationships documented in CONNECTIONS.md
- ✅ **Extraction pipeline proven end-to-end** — Session → Transcript → Extraction → Formalization → Commit
- ✅ **Core hypothesis validated** — Personalized dialogue patterns directly affect concept discovery
- ✅ **IES backend (54/61 tests passing)** — Layers 1 & 2 working flawlessly
- ✅ **Therapy domain knowledge graph fully populated** — Neo4j with 50k entities, 63 books ingested

**Phase 2a Validation Summary:**
- ✅ **5/5 exploration sessions completed** — CLI tool navigates knowledge graph reliably
- ✅ **Exploration surfaces unexpected relationships** — Graph reveals multidimensional concept connections (3-15 per exploration)
- ✅ **Thinking partner questions enhance navigation** — Claude-generated questions deepen reflection without interrupting flow
- ✅ **Layer 3 creates different thinking experience** — User-driven navigation (graph) complements AI-driven dialogue (Layer 2)
- ✅ **Novel insights emerge from structure** — Graph relationships surface discoveries dialogue alone wouldn't find
- ✅ **Complete validation criteria met** — All quantitative and qualitative success measures achieved

**Phase 1 Results:**

**Therapy Framework Discovered:**
A complete therapeutic vision emerged through 10 sessions exploring how humans construct meaning within constraints:
1. **Narrow Window** — The window is universal, not pathology; constraint enables meaning
2. **Acceptance vs. Resignation** — Distinction is aliveness/energy, not external form
3. **Grief as Acceptance** — Loss reveals love; grief-with-presence preserves connection
4. **Metabolization of Difficulty** — Process by which pain becomes capacity (not elimination)
5. **Shame as Non-Acceptance** — Blocker to metabolization; prevents movement toward presence
6. **Authentic Presence** — Outcome of shame metabolization and nervous system re-regulation
7. **Nervous System Configurations** — Three states (hypervigilance, shutdown, regulated aliveness) determine capacity
8. **Nervous System as Gatekeeper** — Capacity emerges when nervous system is accessed
9. **Superpower in Weakness** — Adaptive trauma response becomes strength when metabolized
10. **Window as Condition for Depth** — Constraint itself enables meaning, beauty, presence

**Pipeline Validated:**
- Session → Transcript: ✅ Auto-saved by session runner
- Transcript → Extraction: ✅ Backend ExtractionService API works flawlessly
- Extraction → Interpretation: ✅ Manual concept document creation from key insights
- Concepts → Connections: ✅ CONNECTIONS.md maps relationships and threads
- Connections → Commit: ✅ Git history captures complete evolution

**What Learned:**
- The IES system (Layers 1 & 2) successfully creates genuine thinking partnership
- Personalized dialogue (informed by profile system) surfaces valuable conceptualizations
- The extraction → formalization pipeline works end-to-end
- One person's thinking patterns, explored with adaptive questions, generates profound therapeutic insights
- Concepts that emerge are testable, relatable, and therapeutically applicable

**Roadmap:**
- **Phase 0 (COMPLETE):** Configuration stabilization removed 40% meta-work overhead
- **Phase 1 (COMPLETE):** Core hypothesis proven — Layers 1 & 2 work; 11 concepts extracted; therapeutic framework coherent
- **Phase 2a (COMPLETE):** Layer 3 MVP validated — CLI exploration tool proven with 5 validation sessions; all layers working end-to-end
- **Phase 2b (MVP COMPLETE):** Readest Flow mode MVP delivered with full integration
  - Readest worktree (this): Flow mode interface, entity panel, journey tracking, text selection popup
  - SiYuan worktree (parallel): Processing hub development (Dashboard, Structured Thinking, Quick Capture)
- **Phase 2c:** User testing, refinement, and full integration between Readest + SiYuan + Backend
- **Phase 3+:** Domain generalization and validation across multiple knowledge domains

## How to Work Here (Phase 2b+)

Phase 1 is complete. All success criteria achieved. The core hypothesis is proven. Layers 1 & 2 work flawlessly.

### Where to Start

**Understand What Was Accomplished:**
1. Read `docs/session-notes.md` — Top section summarizes all 10 sessions and Phase 1 completion
2. Review `/therapy/Track_1_Human_Mind/CONNECTIONS.md` — See the therapeutic framework that emerged
3. Review the 11 concept documents in `/therapy/Track_1_Human_Mind/` — Each concept is a formalized insight
4. Check git log — `git log --oneline` shows progression of sessions and concept extraction

**Key Resources:**
- `docs/PROJECT-OVERVIEW.md` — Complete vision and design rationale
- `docs/five-agent-synthesis.md` — Deep analysis of why architecture decisions were made
- `docs/PHASE-1-WORKFLOW.md` — Phase 1 operational guide (for reference if running additional exploration sessions)

### Phase 2b Focus (Readest Worktree)

This worktree focuses specifically on **Layer 4: Reading + Flow Exploration Interface** in Readest.

**Completed:**
- Readest repository integrated as submodule
- Flow Mode MVP implemented with all core features
- Entity lookup, relationship navigation, breadcrumb journey capture
- Text selection popup with Flow button integration
- See TASK.md for complete deliverables checklist

**Next Priority (Phase 2c):**
- User testing of Flow mode in reading context
- UI/UX refinement based on user feedback
- Integration with SiYuan plugin (running in parallel worktree)
- Backend API optimization for journey persistence

### If Running Additional Exploration Sessions

The Phase 1 pipeline is fully documented and proven. To run additional sessions:

1. Reference `docs/PHASE-1-WORKFLOW.md` (complete operational guide)
2. Verify backend is healthy: `curl http://localhost:8081/health`
3. Verify Docker services running: `docker compose ps`
4. Run: `python scripts/run-session.py --topic "Your question"`
5. Follow extraction and formalization steps documented in PHASE-1-WORKFLOW.md
6. Append results to CONNECTIONS.md
7. Commit with clear message

**Project Memory:**
- `docs/PHASE-1-WORKFLOW.md` = Operational guide for sessions (proven, reusable)
- `docs/session-notes.md` = Complete session history and reflection
- `/therapy/Track_1_Human_Mind/` = All extracted concepts and connections
- Git history = Complete evolution of work
- Together these form complete, searchable project memory

## Project Structure

### Main Project (brain_explore/)

```
brain_explore/
├── ies/                           # Intelligent Exploration System (domain-agnostic layers)
│   ├── backend/                   # FastAPI backend - Layers 1-3 APIs (expanded Python services)
│   │   ├── src/ies_backend/
│   │   │   ├── api/               # API routers
│   │   │   │   ├── graph.py       # Knowledge graph exploration (Layer 1)
│   │   │   │   ├── journey.py     # Breadcrumb journey tracking (Layer 3)
│   │   │   │   ├── capture.py     # Quick Capture processing (Layer 3)
│   │   │   │   └── question_engine.py # Thinking partner questions (Layer 2)
│   │   │   └── services/          # Business logic
│   │   └── tests/                 # 61 unit tests
│   └── plugin/                    # SiYuan plugin - document interface (14,092 lines TS/Svelte)
│                                  # Layer 3 processing hub (Dashboard, Forge/Flow modes)
│
├── therapy/                       # Therapy Domain Application (complete Phase 1)
│   └── Track_1_Human_Mind/        # How humans perceive, think, and construct meaning (11 concepts + CONNECTIONS.md)
│
├── library/                       # Shared: GraphRAG modules, ingest pipeline (Python)
├── scripts/                       # Shared: CLI tools, session runners
├── books/                         # Shared: 63 psychology/therapy books (ingested to Layer 1)
├── docs/                          # Documentation
└── docker-compose.yml             # Neo4j + Qdrant infrastructure
```

### Readest Worktree (feature/readest-integration)

```
readest/
└── apps/
    └── readest-app/
        └── src/
            ├── app/reader/components/
            │   ├── FlowToggler.tsx           # Flow mode activation button
            │   ├── HeaderBar.tsx             # Reader header with Flow toggle
            │   ├── ReaderContent.tsx         # Main reader layout with Flow panel
            │   └── flowpanel/
            │       ├── FlowPanel.tsx         # Main flow panel container, layout, resizing
            │       ├── Header.tsx            # Panel header with pin/close controls
            │       ├── EntitySection.tsx     # Current entity display
            │       ├── RelationshipsSection.tsx   # Entity relationships
            │       ├── SourcesSection.tsx    # Source books and passages
            │       ├── QuestionsSection.tsx  # Thinking partner questions
            │       └── index.ts              # Component exports
            ├── hooks/
            │   └── useFlowEntity.ts          # Entity lookup and API integration
            ├── store/
            │   └── flowModeStore.ts          # Zustand: Flow state, journey tracking
            └── services/flow/
                ├── graphClient.ts            # Brain_explore API client
                ├── journeyStorage.ts         # Local storage persistence
                └── index.ts                  # Service exports
```

**Architecture Alignment:**
- **Layer 1** = Knowledge graph in main project `library/` and `books/`
- **Layer 2** = Backend services in main project `ies/backend/api/`
- **Layer 3** = Visual implementation in Readest worktree (Flow mode + Flow panel components)
- **Domain Application** = `therapy/` directory in main project

## Key Resources

### Documentation Hierarchy

The project maintains a three-level documentation structure for clarity:

**Level 1: Strategic Vision (Project Context)**
- `docs/PROJECT-OVERVIEW.md` — Single source of truth for the complete vision: three-layer architecture, what's built vs. deferred, why design decisions were made, Phase 1 success criteria, and roadmap
- `docs/five-agent-synthesis.md` — Deep analysis: architectural vision, identified gaps, why configuration was blocking, lessons learned, phased path forward

**Level 2: Operational & Validation Documentation**
- `docs/PHASE-1-WORKFLOW.md` — Complete operational guide for running dialogue sessions (proven, reusable for Phase 2+ exploration)
- `docs/PHASE-2A-VALIDATION.md` — Layer 3 CLI exploration tool validation plan with 5 focused explorations
- `docs/PHASE-2A-VALIDATION-RESULTS.md` — Complete validation results; all criteria met; Layer 3 proven functional
- Architecture guidance for Phase 2b based on validated Layer 3 patterns

**Level 3: Implementation & Reflection**
- `therapy/Track_1_Human_Mind/` — 11 extracted concept documents with CONNECTIONS.md (complete Phase 1 output)
- `scripts/explore.py` — Layer 3 CLI tool for knowledge graph navigation with thinking partner questions
- `docs/session-notes.md` — Complete session history: Phase 1 (10 sessions), Phase 2a (5 validation explorations), and learnings
- Git history — Commits show progression: Phase 1 sessions → Phase 1 completion → Phase 2a validation → ready for Phase 2b

### Supporting References

**For This Worktree:**
- `TASK.md` — Complete task briefing and deliverables for this worktree
- `readest/README.md` — Readest project documentation
- `readest/apps/readest-app/` — Main application code

**For Main Project Context:**
- `../docs/parking-lot.md` — Future features roadmap
- `../CLAUDE.md` (main project) — Overall project instructions

**Technical Setup:**
- `../ies/backend/README.md` — Backend API setup (from main project)
- `../docker-compose.yml` — Infrastructure (Neo4j + Qdrant) in main project

## The Parking Lot

**Explicitly Deferred to Phase 2c+:**
- **Multi-domain framework generalization** — Apply thinking partnership system to other knowledge domains beyond therapy
- **Advanced profile system (8 dimensions)** — Expand user profile complexity for finer personalization
- **Question engine (8 inquiry approaches)** — Formalize diverse questioning methodologies
- **Post-processing pipeline** — Enrich graph with Phase 1 conceptual frameworks and bidirectional linking
- **MCP server integration** — Connect system to Claude via Model Context Protocol
- **n8n integration** — Workflow automation for concept extraction and formalization
- **Synapse component ports** — Migrate components to alternative front-end frameworks

**Current Phase 2b Focus:**
- Layer 3 validation proved the CLI exploration works well
- Next: Build visual interface (web app or extended SiYuan plugin) to show relationships, allow note capture
- Then: Evaluate if Phase 1 concepts should enrich the knowledge graph with bidirectional linking

**Rule:** Phase 2b focuses on building the visual interface for Layer 3. Domain generalization waits until after visual validation. Nothing enters development until visual interface is tested with users.

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

## The Three-Layer Thinking Partnership Cycle

This is how the system creates value through personalized thinking partnership:

**Layer 2 → Layer 3 Feedback:**
- Layer 2 dialogue reveals HOW someone thinks (their patterns, what they're drawn to, what they avoid)
- This personalization profile directly informs Layer 3 exploration guidance
- Questions in Layer 3 aren't generic—they're shaped by patterns revealed in Layer 2

**Layer 3 Exploration → Concept Extraction:**
- In Layer 3, the thinking partner asks clarifying questions and surfaces connections
- The user generates novel conceptualizations through this guided thinking
- The exploration path and thinking artifacts are documented as breadcrumbs
- Those breadcrumbs become the raw material for extracting formalized concepts

**Concept Formalization → Layer 1 Enrichment:**
- Extracted concepts are formalized and added to the knowledge graph (Layer 1)
- The next session starts with enriched knowledge and refined personalization
- The cycle deepens: better profile → more personalized guidance → deeper generation

**Phase 1 validates this complete cycle** by running sessions where dialogue reveals patterns, those patterns guide personalized exploration, and the thinking partnership generates extractable concepts.

## Phase 2b Implementation Details

### Flow Mode Architecture (Readest Integration)

**State Management (flowModeStore.ts):**
- Zustand store centralizes all Flow mode state
- Tracks: current entity, relationships, sources, thinking partner questions
- Journey tracking: start time, current step time, dwell time calculation
- Panel state: width, pinned status, loading states

**Data Flow:**
1. User selects text in reader
2. useFlowEntity hook searches for matching entities
3. GraphAPIClient fetches entity details from brain_explore backend
4. Store updated with entity, relationships, sources
5. Thinking partner questions fetched asynchronously
6. Journey step added to breadcrumb trail

**Journey Persistence:**
- journeyStorage.ts provides local storage fallback
- On journey end: save to local storage first (offline-safe)
- Then async sync to backend (non-blocking)
- Handles graceful degradation if backend unavailable

**UI Components:**
- FlowPanel: Main container with resizable drag handle, pin/close controls
- EntitySection: Current entity name, type, summary
- RelationshipsSection: Shows related entities with relationship type
- SourcesSection: Books and passages discussing the entity
- QuestionsSection: Thinking partner questions to deepen exploration
- Responsive design: Full-width on mobile, 20-50% width on desktop

**Backend Integration:**
- GraphAPIClient connects to brain_explore API (http://localhost:8081/api/v1)
- Endpoints used: `/graph/entity/{id}`, `/graph/search`, `/graph/explore/{id}`, `/graph/sources/{id}`, `/question-engine/question`, `/journeys`
- Timeout handling: 10s default timeout with graceful error handling
- Configurable base URL for different environments

### Key Implementation Decisions

1. **Local Storage First** — Journeys saved locally before backend sync ensures no data loss in offline mode
2. **Zustand for State** — Centralized, predictable state management; easy to add persistence
3. **Modular Components** — Each section independently fetchable; easy to extend with new data types
4. **Drag Resizing** — Users can adjust flow panel width; pinning allows keeping it visible while navigating
5. **Async Questions** — Thinking partner questions fetched non-blocking, populated after entity loads
6. **Dwell Time Tracking** — Measures engagement per entity; important for understanding exploration patterns

## Key Concept: Domain-Agnostic Architecture with Therapy Application

This project builds a **general thinking partnership system** (Layers 1-3) applied to the **therapy domain** in Phase 1.

- **Layer 1** (Knowledge Graph) — Domain-agnostic ingestion and graph creation
- **Layer 2** (Profile & Dialogue) — Domain-agnostic personalization and thinking pattern recognition
- **Layer 3** (Flow/Flo) — Domain-agnostic thinking partnership interface (Phase 2+)
- **Therapy** — Current instantiation domain for proof-of-concept and validation

This means:
- The architecture should never make therapy-specific assumptions in core systems
- Therapy is a test domain for proving the thinking partnership approach works
- Layer 1 can be retargeted to any knowledge domain (scientific, legal, creative, etc.)
- Post-Phase 1, the system can be applied to other domains with new knowledge graphs
- The three-layer cycle works for any domain where personalized thinking partnership has value

## Working Style

**Claude acts as project manager.** Always choose the optimal next step in development rather than asking what to do next. Present the decision and proceed; user will confirm or redirect if needed.

- Don't ask "what would you like to work on?"
- Do identify the highest-value next action and take it
- Explain briefly why this is the optimal next step
- Ask for confirmation to proceed before doing so

## Questions?

See `docs/PROJECT-OVERVIEW.md` for comprehensive understanding of:
- The complete vision (three-layer architecture + domain-agnostic design)
- What's built vs. deferred (Layers 1 & 2 done, Layer 3 in parking lot)
- Why configuration was blocking work
- Architecture and data flow
- Phase 1 plan and success criteria
- Known limitations and open questions

For deeper context on the five-agent analysis, see `docs/five-agent-synthesis.md`.
<!-- END MANUAL -->

<!-- AUTO-MANAGED: build-commands -->
<!-- This section will be automatically updated by auto-memory plugin -->
<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: architecture -->
<!-- This section will be automatically updated by auto-memory plugin -->
<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: conventions -->
<!-- This section will be automatically updated by auto-memory plugin -->
<!-- END AUTO-MANAGED -->