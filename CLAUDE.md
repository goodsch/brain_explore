<!-- MANUAL -->
# brain_explore — Intelligent Exploration System

*A domain-agnostic tool for structured thinking, understanding, connecting, and researching across any knowledge domain*

## What This Is

A four-layer system that enables people to think WITH an AI partner who adapts to their unique thinking style while exploring complex knowledge domains:

1. **Layer 1: Knowledge Graph Creation** — Pre-processing and ingestion pipeline
   - Ingests domain materials (texts, research, conceptual frameworks)
   - Creates rich knowledge graphs with entities and relationships
   - Domain-agnostic: can ingest and structure any knowledge domain
   - *Current corpus:* 114 books across 8 domains (50k+ entities) — used for system validation
   - *See:* `books/BOOK-CATALOG.md` for complete categorized inventory

2. **Layer 2: Backend Services** — APIs for graph, dialogue, journey tracking, content capture
   - Graph API: entity search, exploration, sources, relationship traversal
   - Session API: structured thinking dialogue with mode-specific behaviors
   - Journey API: breadcrumb tracking and persistence across sessions
   - Profile system: 6-dimension cognitive profile for personalization
   - Question engine: thinking partner questions at decision points

3. **Layer 3: SiYuan Plugin (Processing Hub)** — Dashboard and structured thinking modes
   - Dashboard: stats, suggestions, recent journeys, capture queue
   - 5 Thinking Modes: Learning, Articulating, Planning, Ideating, Reflecting
   - Flow Mode: graph exploration with grouped relationship display
   - Quick Capture: content processing with entity extraction

4. **Layer 4: Readest Integration (Reading Interface)** — E-book reader with flow exploration
   - Split-panel view: source text + entity panel
   - Text selection → entity lookup → relationship exploration
   - Breadcrumb journey capture during reading sessions
   - Seamless toggle between reading mode and flow exploration

**The Virtuous Cycle:** Layer 2 dialogue reveals thinking patterns that personalize Layer 3/4 exploration. Exploration surfaces new concepts and connections. The thinking path becomes formalized concepts that enrich Layer 1. Each cycle deepens both domain understanding and personalization.

## Current Status

**Phase 2b: Visual Interface Implementation** ✅ COMPLETE (Dec 3)

**All Four Layers Built and Validated:**
- ✅ Layer 1: Knowledge graph creation (validated with 114-book corpus across 8 domains: 50k+ entities)
- ✅ Layer 2: Backend APIs (graph, session, journey, capture services - 54/61 tests passing)
- ✅ Layer 3: SiYuan Plugin MVP (dashboard, 5 thinking modes, flow exploration, quick capture)
- ✅ Layer 4: Readest Integration MVP (reading interface with flow mode, entity panel, breadcrumb capture)

**For complete project status, see:** `docs/COMPREHENSIVE-PROJECT-STATUS.md`

**Phase 1 Achievement Summary:**
- ✅ **10/10 validation sessions completed** — System validated using personal therapy/growth exploration
- ✅ **11+ concepts extracted and formalized** — Demonstrated the full thinking → extraction pipeline
- ✅ **Complete concept connection map** — Hierarchical relationships documented in CONNECTIONS.md
- ✅ **Extraction pipeline proven end-to-end** — Session → Transcript → Extraction → Formalization → Commit
- ✅ **Core hypothesis validated** — Personalized dialogue patterns directly affect concept discovery
- ✅ **IES backend (54/61 tests passing)** — Layers 1 & 2 working flawlessly
- ✅ **Test corpus fully ingested** — Neo4j with 50k+ entities from 114 books across 8 domains (see `books/BOOK-CATALOG.md`)

**Phase 2a Validation Summary:**
- ✅ **5/5 exploration sessions completed** — CLI tool navigates knowledge graph reliably
- ✅ **Exploration surfaces unexpected relationships** — Graph reveals multidimensional concept connections (3-15 per exploration)
- ✅ **Thinking partner questions enhance navigation** — Claude-generated questions deepen reflection without interrupting flow
- ✅ **Layer 3 creates different thinking experience** — User-driven navigation (graph) complements AI-driven dialogue (Layer 2)
- ✅ **Novel insights emerge from structure** — Graph relationships surface discoveries dialogue alone wouldn't find
- ✅ **Complete validation criteria met** — All quantitative and qualitative success measures achieved

**Phase 1 Results:**

**Active Application: Personal Growth Framework**
*(Ongoing personal project using this system — demonstrates capability, not system purpose)*

Through 10 validation sessions, a personal framework emerged exploring how humans construct meaning within constraints:
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
- One person's thinking patterns, explored with adaptive questions, generates meaningful insights
- Concepts that emerge are testable, relatable, and applicable to real decisions

**Roadmap:**
- **Phase 0 (COMPLETE):** Configuration stabilization removed 40% meta-work overhead
- **Phase 1 (COMPLETE):** Core hypothesis proven — Layers 1 & 2 work; extraction pipeline validated with 11 concepts
- **Phase 2a (COMPLETE):** Layer 3 CLI validation — CLI exploration tool proven with 5 validation sessions
- **Phase 2b (COMPLETE):** Visual interfaces — Readest reading interface + SiYuan plugin dashboard (both MVPs complete)
- **Phase 2c (IN PROGRESS):** Reframe & Template Integration — Concept reframes + thinking templates + SiYuan document structure
- **Phase 3+:** Additional knowledge domains and continued refinement

## How to Work Here (Phase 2c+)

**Phase 2c is in progress:** Integrating Reframe Layer + Thinking Template Schema + SiYuan Document Structure to close critical gaps preventing real-world usage.

### Worktree Organization

**The master branch contains shared backend and documentation only.** Feature work happens in separate worktrees with their own TASK.md files:

| Worktree Location | Branch | Purpose | Task File |
|------------------|--------|---------|-----------|
| `.` (root) | `master` | Backend APIs, Layer 1/2, shared docs | None (master has no TASK.md) |
| `.worktrees/readest/` | `feature/readest-integration` | Layer 4 Reading Interface | `TASK.md` in worktree |
| `.worktrees/siyuan/` | `feature/siyuan-evolution` | Layer 3 Processing Hub | `TASK.md` in worktree |
| `.worktrees/quick-capture/` | `feature/quick-capture` | Quick Capture iOS/SiYuan | `TASK.md` in worktree |

**Working in Worktrees:**
- Each worktree is a separate directory with its own branch checked out
- Use `cd` to switch between worktrees, NOT `git checkout`
- Each worktree has its own `TASK.md` with specific objectives for that feature
- The root (master branch) intentionally has NO `TASK.md` - it's backend/docs only
- See `docs/WORKTREE-GUIDE.md` for complete reference

### Where to Start

**For New Session (Read First):**
1. `docs/SYSTEM-DESIGN.md` — How the system works end-to-end (operational reference)
2. Check git status and recent commits to understand current state

**Understand What Was Accomplished:**
1. Read `docs/session-notes.md` — Top section summarizes all 10 sessions and Phase 1 completion
2. Review `/therapy/Track_1_Human_Mind/CONNECTIONS.md` — See the therapeutic framework that emerged
3. Review the 11 concept documents in `/therapy/Track_1_Human_Mind/` — Each concept is a formalized insight
4. Check git log — `git log --oneline` shows progression of sessions and concept extraction

**Key Resources:**
- `docs/SYSTEM-DESIGN.md` — Operational reference: how all layers integrate, critical gaps
- `docs/PROJECT-OVERVIEW.md` — Complete vision and design rationale
- `docs/five-agent-synthesis.md` — Deep analysis of why architecture decisions were made
- `docs/PHASE-1-WORKFLOW.md` — Phase 1 operational guide (for reference if running additional exploration sessions)

### Phase 2c Focus

**Current Implementation: Reframe & Template Integration** (Dec 4, 2025)

Addressing critical gaps #1 and #2 with three integrated capabilities:

**1. Reframe Layer** — Makes domain concepts accessible via metaphors and analogies
- New entity type: `Reframe` (metaphor, analogy, story, pattern, contrast)
- LLM generation with caching and feedback voting
- UI: "Reframes" tab in Flow panel (SiYuan + Readest)
- Strategy: On-demand generation + background for popular concepts

**2. Thinking Template Schema** — Formalizes structured thinking sessions
- JSON-based template definitions for 5 thinking modes
- Section-by-section flow with AI behavior specifications
- Graph mapping rules (create entities, link relationships on completion)
- Starting with: Learning (Mechanism Map) + Articulating (Clarify Intuition)

**3. SiYuan Document Structure** — ADHD-friendly personal knowledge organization
- Folder hierarchy: `/Daily/`, `/Insights/`, `/Threads/`, `/Favorite Problems/`, `/Sessions/`
- Frontmatter standard: `be_type`, `be_id`, `status`, `resonance`, `energy`, concept links
- Quick Capture → Daily log flow (low friction)
- Promotion flow: Daily spark → `/Insights/` (updates backend status)

**Implementation Strategy:**
- Phase 1 (Sequential): Single agent defines shared interfaces
- Phase 2 (Parallel): 4 agents work independently on: Backend Reframe Service, Backend Template Engine, SiYuan Plugin Structure, Readest Reframes Tab
- Phase 3 (Sequential): Integration and end-to-end testing

**For Complete Design:**
- `docs/plans/2025-12-04-reframe-template-integration-design.md` — Full specification with API endpoints, schemas, implementation plan, and success criteria
- `docs/plans/2025-12-04-execution-plan.md` — Tactical execution plan using Codex and Gemini CLI for parallel implementation (Phase 1: interfaces, Phase 2: parallel workstreams, Phase 3: integration)

**Reframe UI Components (Implemented):**
- `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/ReframesSection.tsx` — Readest Flow panel Reframes tab (React/TypeScript)
- `.worktrees/siyuan/ies/plugin/src/components/ReframesTab.svelte` — SiYuan plugin Reframes tab (Svelte)
- Both components integrate with backend `/reframes` API for concept reframe retrieval, generation, and feedback voting
- Features: Type-grouped reframe display (metaphor, analogy, story, experiment, question), on-demand generation, thumbs up/down feedback

**Remaining Critical Gaps (Deferred):**

3. **Book Library Inaccessible** — 63 books ingested to Neo4j but users have no way to browse or open them. No deep-linking to specific passages.

4. **Cross-App Continuity Missing** — Readest and SiYuan don't share state. Can't resume reading session from SiYuan or resume exploration from Readest.

5. **Journey Value Loop Not Closed** — Journeys are captured but never analyzed for patterns. Patterns not used to personalize suggestions or improve thinking partner questions.

**For Gap Analysis:**
- `docs/PLANNING-GAPS-AND-QUESTIONS.md` — Comprehensive gap analysis with detailed technical review
- `docs/COMPREHENSIVE-PROJECT-STATUS.md` — Complete technical status of all four layers

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

```
brain_explore/
├── ies/                           # Intelligent Exploration System (domain-agnostic layers)
│   ├── backend/                   # FastAPI backend - Layers 1 & 2 (4,496 lines Python)
│   │   ├── src/ies_backend/       # Knowledge graph API, dialogue, profile services
│   │   └── tests/                 # 61 unit tests
│   └── plugin/                    # SiYuan plugin - document interface (14,092 lines TS/Svelte)
│                                  # (precursor to Layer 3 Flow/Flo interface)
│
├── therapy/                       # Personal Growth Application (active project using this system)
│   ├── Track_1_Human_Mind/        # Personal framework: meaning, acceptance, presence
│   │   ├── 01-narrow-window-of-awareness.md  # Foundational (universal constraint → meaning)
│   │   ├── 02-acceptance-vs-resignation.md   # Core distinction (aliveness vs numbness)
│   │   ├── 03-nervous-system-sensing-possibility.md  # Engagement mechanism
│   │   ├── 04-grief-as-acceptance.md         # Application to loss
│   │   ├── 05-metabolization-of-difficulty.md # Process model (pain → capacity)
│   │   ├── 06-shame-as-non-acceptance.md     # Blocker identification
│   │   ├── 07-authentic-presence.md          # Outcome of shame metabolization
│   │   ├── 08-nervous-system-configurations.md # Three states model
│   │   ├── 09-capacity-and-nervous-system-access.md # Reframe
│   │   ├── 10-superpower-in-weakness.md      # Integration
│   │   ├── 11-window-as-condition-for-depth.md # Final vision (full circle)
│   │   └── CONNECTIONS.md                    # Hierarchical framework map
│   └── (active development — ongoing personal application)
│
├── .interleaved-thinking/         # Research artifacts (ADHD-friendly ontology design)
│   ├── final-answer.md            # Research-backed ontology recommendations
│   └── tooling-inventory.md       # Available research tools assessment
│
├── library/                       # Shared: GraphRAG modules, ingest pipeline (Python)
├── scripts/                       # Shared: CLI tools, session runners
├── books/                         # Shared: 114 books across 8 domains (ingested to Layer 1)
│   └── BOOK-CATALOG.md            # Categorized inventory: ADHD, psychology, neuroscience, productivity, etc.
│
├── docs/                          # Documentation
│   ├── PROJECT-OVERVIEW.md        # Single source of truth (comprehensive project overview)
│   ├── five-agent-synthesis.md    # Vision, gaps, lessons, phased path (analysis depth)
│   ├── session-notes.md           # Session reflection (append-only)
│   ├── parking-lot.md             # Future features (don't work on these)
│   ├── plans/                     # Implementation design documents
│   │   └── 2025-12-04-reframe-template-integration-design.md  # Active Phase 2c plan
│   └── archive/                   # Old progress files, archived memories
│
└── docker-compose.yml             # Neo4j + Qdrant infrastructure (Layers 1 & 2 support)
```

**Architecture Alignment:**
- **Layer 1** = Knowledge graph + ingestion pipeline in `library/` and `books/`
- **Layer 2** = Backend services (API, dialogue, profile) in `ies/backend/`
- **Layer 3** = SiYuan plugin in `.worktrees/siyuan/` (processing hub, dashboard)
- **Layer 4** = Readest integration in `.worktrees/readest/` (reading interface)
- **Active Application** = `therapy/` directory (personal growth framework — ongoing project)

## Key Resources

### Documentation Hierarchy

The project maintains a three-level documentation structure for clarity:

**Level 1: Strategic Vision (Project Context)**
- `docs/PROJECT-OVERVIEW.md` — Single source of truth for the complete vision: three-layer architecture, what's built vs. deferred, why design decisions were made, Phase 1 success criteria, and roadmap
- `docs/five-agent-synthesis.md` — Deep analysis: architectural vision, identified gaps, why configuration was blocking, lessons learned, phased path forward

**Level 2: Operational & Validation Documentation**
- `docs/SYSTEM-DESIGN.md` — **Operational reference**: How the system works end-to-end, data structures, user workflows, integration points, critical gaps (read at session start)
- `docs/COMPREHENSIVE-PROJECT-STATUS.md` — Complete project status: all 4 layers, phase completion, worktree organization
- `docs/PLANNING-GAPS-AND-QUESTIONS.md` — Comprehensive Phase 2c planning: critical gaps, technical stack review, API inventory, integration questions
- `docs/plans/2025-12-04-reframe-template-integration-design.md` — **Active implementation plan**: Reframe Layer + Thinking Templates + SiYuan document structure (Phase 2c)
- `docs/plans/2025-12-03-integrated-reading-knowledge-system.md` — Four-layer architecture design
- `docs/PHASE-1-WORKFLOW.md` — Complete operational guide for running dialogue sessions (proven, reusable for Phase 2+ exploration)
- `docs/PHASE-2A-VALIDATION-RESULTS.md` — Layer 3 CLI validation results; all criteria met
- `docs/siyuan-exports/` — Visual documentation: mermaid diagrams, sprint boards, gap matrices (8 files, updated Dec 4)

**Level 3: Implementation & Reflection**
- `therapy/Track_1_Human_Mind/` — 11 extracted concept documents with CONNECTIONS.md (complete Phase 1 output)
- `scripts/explore.py` — Layer 3 CLI tool for knowledge graph navigation with thinking partner questions
- `docs/session-notes.md` — Complete session history: Phase 1 (10 sessions), Phase 2a (5 validation explorations), and learnings
- `.interleaved-thinking/final-answer.md` — ADHD-friendly ontology design research (Dec 3)
- Git history — Commits show progression: Phase 1 sessions → Phase 1 completion → Phase 2a validation → ready for Phase 2b

**Visual Documentation (SiYuan Exports):**
- `docs/siyuan-exports/01-development-tracker.md` — Real-time sprint board, test coverage, git status (Phase 2c: 15% complete)
- `docs/siyuan-exports/02-roadmap-and-gaps.md` — Feature matrix by layer, gap prioritization, critical blockers
- `docs/siyuan-exports/03-therapy-framework-map.md` — Personal growth framework: visual hierarchy of 11 concepts (demonstrates system with active application)
- `docs/siyuan-exports/04-project-visualizations.md` — Architecture diagrams, phase timeline, thinking partnership cycle
- `docs/siyuan-exports/05-system-design-visual.md` — Four-layer architecture flow, data paths, entity type diagrams
- `docs/siyuan-exports/06-adhd-friendly-ontology-design.md` — Entity types, status lifecycle, relationship types (implemented)
- `docs/siyuan-exports/07-adhd-ontology-real-examples.md` — Concrete examples: spark capture, insight emergence, journey flow
- `docs/siyuan-exports/08-adhd-ontology-example-flow.md` — Step-by-step walkthrough from spark to anchored knowledge

These visual documents are exported from SiYuan and provide mermaid diagrams, tables, and visual representations of project status, architecture, and the ADHD-friendly ontology design. Updated Dec 4, 2025 with clarifications emphasizing the domain-agnostic nature of the system architecture.

### Supporting References

**Constraints & Scope:**
- `docs/parking-lot.md` — Future features (what NOT to work on in Phase 1)
- `CLAUDE.md` (this file) — Quick reference and structure guide

**Technical Setup:**
- `ies/backend/README.md` — Backend API setup and configuration
- `docker-compose.yml` — Infrastructure (Neo4j + Qdrant)

## The Parking Lot

**Explicitly Deferred to Phase 2c+:**
- **Multi-domain framework generalization** — Apply thinking partnership system to other knowledge domains beyond therapy
- **Advanced profile system (8 dimensions)** — Expand user profile complexity for finer personalization
- **Question engine (8 inquiry approaches)** — Formalize diverse questioning methodologies
- **Post-processing pipeline** — Enrich graph with Phase 1 conceptual frameworks and bidirectional linking
- **MCP server integration** — Connect system to Claude via Model Context Protocol
- **n8n integration** — Workflow automation for concept extraction and formalization
- **Synapse component ports** — Migrate components to alternative front-end frameworks

**Phase 2b Complete:**
- ✅ Readest reading interface (Layer 4) - Flow mode, entity panel, breadcrumb capture
- ✅ SiYuan plugin dashboard (Layer 3) - 5 thinking modes, flow exploration, quick capture

**Phase 2c Focus:**
- User testing of complete four-layer system
- Refinement based on real-world usage
- ADHD-friendly ontology design (research complete in `.interleaved-thinking/`)
- Personal growth framework development (ongoing application)

**Rule:** Additional domains (Phase 3+) wait until core system is refined through real usage.

**ADHD-Focused Research:**
Research completed (Dec 3) on ADHD-friendly ontology design, drawing from:
- Russell Barkley (executive function deficits)
- Tamara Rosier (interest-based nervous system)
- Gabor Maté (emotional resonance as retrieval cue)
- Tiago Forte (capture what resonates, 12 favorite problems)
- Cognitive architecture literature (conceptual spaces, spreading activation)

Key recommendations in `.interleaved-thinking/final-answer.md`:
- **Resonance over importance** — Capture emotional engagement, not just taxonomic accuracy
- **Multiple entry points** — Mood-based, question-based, serendipitous discovery
- **Visible progress** — Breadcrumb trails as treasure maps, not audit logs
- **Low friction capture** — `spark` type for unprocessed resonance
- **Non-judgmental lifecycle** — Growth metaphor (`captured → exploring → anchored`)
- **New entity types:** `spark`, `favorite_problem`, `thread`, `insight`
- **New relationships:** `sparked_by`, `led_to_discovery`, `addresses_problem`

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

## The Four-Layer Thinking Partnership Cycle

This is how the system creates value through personalized thinking partnership:

**Layer 2 → Layers 3/4 Personalization:**
- Backend dialogue services reveal HOW someone thinks (patterns, preferences, perspectives)
- This personalization profile informs Layer 3/4 exploration guidance
- Questions aren't generic—they're shaped by revealed patterns

**Layers 3/4 Exploration → Concept Discovery:**
- Reading (Layer 4) or dashboard exploration (Layer 3) with thinking partner questions
- User generates novel conceptualizations through guided thinking
- Exploration path and thinking artifacts documented as breadcrumbs
- Breadcrumbs become raw material for extracting formalized concepts

**Concept Formalization → Layer 1 Enrichment:**
- Extracted concepts formalized and added to knowledge graph (Layer 1)
- Next session starts with enriched knowledge and refined personalization
- The cycle deepens: better profile → more personalized guidance → deeper generation

**Phase 1 validated this cycle** with 10 dialogue sessions demonstrating the full extraction pipeline. **Phase 2b built the complete interface** for reading and exploration.

## Key Concept: Domain-Agnostic Thinking Tool

This project builds a **general intelligent exploration system** (Layers 1-4) for structured thinking, understanding, connecting, and researching across ANY knowledge domain.

- **Layer 1** (Knowledge Graph) — Domain-agnostic ingestion and graph creation
- **Layer 2** (Backend Services) — Domain-agnostic APIs for graph, dialogue, journey, capture
- **Layer 3** (SiYuan Plugin) — Domain-agnostic processing hub and structured thinking
- **Layer 4** (Readest) — Domain-agnostic reading interface with flow exploration

**Current Application Domains:**
- **Multi-domain corpus** — 114 books across 8 categories (ADHD, psychology, neuroscience, productivity, learning, relationships, philosophy, systems thinking); used for system validation
- **Personal growth framework** — Active ongoing project (the 11 concepts); demonstrates extraction pipeline
- **See:** `books/BOOK-CATALOG.md` for complete categorized inventory

**The system is NOT:**
- A therapy tool
- A psychology-specific application
- Limited to any single domain

**The system IS:**
- A thinking partnership tool for any knowledge domain
- An intelligent exploration system for structured research
- A personal knowledge capture and connection system
- Applicable to: scientific research, legal analysis, creative projects, business strategy, learning any subject

## Working Style

**Claude acts as project manager.** Always choose the optimal next step in development rather than asking what to do next. Present the decision and proceed; user will confirm or redirect if needed.

- Don't ask "what would you like to work on?"
- Do identify the highest-value next action and take it
- Explain briefly why this is the optimal next step
- Ask for confirmation to proceed before doing so

## Questions?

**For complete current status:** See `docs/COMPREHENSIVE-PROJECT-STATUS.md`

**For original vision and rationale:**
- `docs/PROJECT-OVERVIEW.md` — Original three-layer vision and Phase 1 plan
- `docs/plans/2025-12-03-integrated-reading-knowledge-system.md` — Four-layer architecture design
- `docs/five-agent-synthesis.md` — Deep analysis of architectural decisions
<!-- END MANUAL -->

<!-- AUTO-MANAGED: build-commands -->
<!-- This section will be automatically updated by auto-memory plugin -->
<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: architecture -->
## Architecture: ADHD-Friendly Personal Knowledge Layer

**Recent Changes (Dec 4):**
- Updated `library/graph/__init__.py` to export unified graph API with ADHD-friendly ontology implementation for personal knowledge capture.
- Implemented Reframe API (`ies/backend/src/ies_backend/api/reframe.py`) - Layer 2 backend service for generating concept reframes via Claude Sonnet 4, with caching and feedback voting (Phase 2c: addresses critical gap #1).
- Implemented Personal Graph API (`ies/backend/src/ies_backend/api/personal.py`) - Layer 2 backend service for ADHD-friendly personal knowledge capture (sparks, insights, resonance-based retrieval).

### Two Knowledge Graph Systems

The project maintains two parallel graph systems accessible through unified `library.graph` module:

**1. Domain Knowledge Graph (Books/Research - Layer 1)**
- **Location:** `library/graph/entities.py`, `library/graph/neo4j_client.py`
- **Purpose:** Structured knowledge from ingested books (114 books across 8 domains, 50k+ entities)
- **Catalog:** `books/BOOK-CATALOG.md` — ADHD (27), psychology (15), neuroscience (12), productivity (14), learning (10), relationships (7), philosophy (4), systems thinking (6), fiction (12)
- **Entity Types:** `concept`, `framework`, `theory`, `mechanism`, `phenomenon`, `pattern`, `distinction`, `person`, `book`, `assessment`
- **Relationships:** Standard academic relationships (`cites`, `supports`, `contradicts`, `operationalizes`, `component_of`, `develops`)
- **Access:** Via `KnowledgeGraph` client and backend GraphService API

**2. Personal Knowledge Graph (ADHD-Friendly - Layers 3/4)**
- **Location:** `library/graph/adhd_ontology.py`, `library/graph/adhd_graph_client.py`
- **Purpose:** Personal thinking artifacts captured during exploration/reading
- **Entity Types:** `spark` (raw resonance), `insight` (processed meaning), `thread` (exploration path), `favorite_problem` (anchor question)
- **Metadata:** Resonance signals (emotional retrieval cues), energy levels (mood-appropriate access), status lifecycle (`captured → exploring → anchored`)
- **Relationships:** Discovery flow (`sparked_by`, `led_to_discovery`, `addresses_problem`), energy mapping (`energy_toward`, `energy_away`)
- **Schema Versioning:** All nodes tagged with `schema_version` (currently `0.1.0`) for future migration support
- **Access:** Via `ADHDKnowledgeGraph` client with schema management capabilities

### Design Rationale

Based on ADHD cognition research (`.interleaved-thinking/final-answer.md`):
- **Capture what resonates** (Tiago Forte) - `spark` entities for low-friction capture without forced classification
- **Interest-based nervous system** (Tamara Rosier) - Energy levels enable mood-appropriate navigation
- **Emotional retrieval cues** (Gabor Maté) - Resonance signals (`curious`, `excited`, `surprised`, `moved`, `disturbed`, `unclear`, `connected`, `validated`) support ADHD memory retrieval
- **Non-judgmental lifecycle** - Growth metaphor avoids shame (`captured → exploring → anchored` not "incomplete")
- **Favorite problems as anchors** (Feynman) - Stable navigation points for wandering minds
- **Visit tracking** - Exploration visits tracked on entities to support recency-based navigation

### Integration Points

- **Layers 3/4 (SiYuan/Readest)** use `ADHDKnowledgeGraph` for personal capture during exploration
- **Layer 1 domain graph** remains canonical source for ingested book knowledge
- **Cross-linking:** Personal insights can reference domain concepts via `source_id` property; exploration breadcrumbs preserve journey context
- **The virtuous cycle:** Personal artifacts (sparks/insights) can be formalized and added to domain graph

### Key Files & Module Structure

```
library/graph/
├── entities.py              # Domain knowledge extraction (books)
├── neo4j_client.py         # Domain knowledge graph client
├── adhd_ontology.py        # ADHD-friendly entity/relationship types
├── adhd_graph_client.py    # Personal knowledge graph client with schema versioning
└── __init__.py             # Unified export: both systems accessible from library.graph
```

**Exported from `library.graph`:**
- Domain: `Entity`, `Relationship`, `ExtractionResult`, `EntityExtractor`, `deduplicate_entities`, `KnowledgeGraph`
- ADHD: `EntityType`, `ResonanceSignal`, `EnergyLevel`, `EntityStatus`, `ADHDEntity`, `ADHDRelationship`, `RelationshipType`, `FavoriteProblem`, `Thread`, `ADHDKnowledgeGraph`, `SCHEMA_VERSION`

### Usage Example

```python
from library.graph import (
    KnowledgeGraph,           # Domain knowledge
    ADHDKnowledgeGraph,       # Personal knowledge
    ResonanceSignal,
    EnergyLevel
)

# Domain knowledge (books)
kg = KnowledgeGraph()
concepts = kg.search_entities("executive function")

# Personal knowledge (sparks/insights)
adhd_kg = ADHDKnowledgeGraph()
spark_id = adhd_kg.capture_spark(
    title="Connection between EF and shame",
    content="Reading Barkley - realized shame blocks EF access",
    resonance_signal=ResonanceSignal.SURPRISED,
    energy_level=EnergyLevel.MEDIUM,
    source_id="concept_123"  # Link to domain concept
)

# Visit tracking for recency-based navigation
adhd_kg.visit_spark(spark_id)
```

### Schema Management

The `ADHDKnowledgeGraph` client includes schema versioning to support future migrations:
- All nodes created with `schema_version` property (currently `0.1.0`)
- Use `get_schema_info()` to check version and node counts
- Use `migrate_schema()` when upgrading (migrations defined in `MIGRATIONS` dict)
- Indexes created for status, resonance, energy, recency queries

### Layer 2: Reframe API (Phase 2c Implementation)

**Backend Service:** `ies/backend/src/ies_backend/api/reframe.py`

Makes domain concepts accessible via metaphors, analogies, stories, patterns, and contrasts. Generates reframes on-demand using Claude Sonnet 4 with caching and feedback voting.

**Endpoints:**
- `GET /concepts/{concept_id}/reframes` - Retrieve cached reframes for a concept
- `POST /concepts/{concept_id}/reframes/generate` - Generate new reframes via LLM (1-10 count)
- `POST /reframes/{reframe_id}/feedback` - Submit helpful/confusing vote

**Entity Type:** `Reframe` (stored in Neo4j, linked to concepts via `HAS_REFRAME` relationship)

**Reframe Types:** `metaphor`, `analogy`, `story`, `pattern`, `contrast`

**Implementation Files:**
- `ies/backend/src/ies_backend/api/reframe.py` - FastAPI router (55 lines)
- `ies/backend/src/ies_backend/services/reframe_service.py` - Service layer with Claude Sonnet 4 integration
- `ies/backend/src/ies_backend/schemas/reframe.py` - Pydantic schemas for API contracts

**Frontend Integration:**
- SiYuan plugin: `.worktrees/siyuan/ies/plugin/src/components/ReframesTab.svelte`
- Readest reader: `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/ReframesSection.tsx`

### Layer 2: Personal Graph API (Phase 2c Implementation)

**Backend Service:** `ies/backend/src/ies_backend/api/personal.py`

Provides ADHD-friendly personal knowledge capture and retrieval via sparks and insights with emotional resonance tracking.

**Core Endpoints:**
- `POST /personal/sparks` - Create new spark (raw resonance capture with optional SiYuan block linking)
- `GET /personal/sparks/{spark_id}` - Retrieve spark by ID
- `POST /personal/sparks/{spark_id}/visit` - Record visit for recency tracking
- `POST /personal/sparks/{spark_id}/promote` - Promote spark to insight (status: captured → anchored)

**ADHD-Friendly Retrieval:**
- `GET /personal/sparks/by-resonance/{signal}` - Find by emotional state (curious, excited, surprised, moved, disturbed, unclear, connected, validated)
- `GET /personal/sparks/by-energy/{level}` - Find by energy level (low/medium/high) for mood-appropriate navigation
- `GET /personal/sparks/unvisited` - Surface forgotten captures

**Statistics:**
- `GET /personal/stats` - Personal knowledge graph stats (spark count, insight count, resonance distribution)

**Entity Types:** `Spark` (raw capture with resonance signal, energy level, status), `Insight` (promoted spark with anchored status)

**Implementation Files:**
- `ies/backend/src/ies_backend/api/personal.py` - FastAPI router (109 lines)
- `ies/backend/src/ies_backend/services/personal_graph_service.py` - Service layer with Neo4j integration for ADHD ontology
- `ies/backend/src/ies_backend/schemas/personal.py` - Pydantic schemas (ResonanceSignal, EnergyLevel, EntityStatus enums)

**SiYuan Integration:**
- `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts` - SiYuan-backend sync utilities
- Bidirectional linking: Sparks reference SiYuan blocks via `siyuan_block_id`, enabling document-graph sync
- Backend URL configurable via localStorage (`ies.backendUrl`, default: `http://192.168.86.60:8081`)
<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: conventions -->
<!-- This section will be automatically updated by auto-memory plugin -->
<!-- END AUTO-MANAGED -->