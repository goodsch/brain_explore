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

**Phase 2c: Integration Features** 🔄 IN PROGRESS (75% complete, Dec 8)

**⚠️ CRITICAL FINDING (Dec 5): Implementation-Principle Gap Discovered**

Four-agent critical analysis of SiYuan plugin revealed catastrophic disconnect between documented principles and actual implementation. Infrastructure exists but core principles not delivered:
- Questions displayed passively (no response capture, no dialogue)
- Question classes exist but don't guide cognition (decorative badges only)
- ADHD metadata captured but no energy-based navigation
- Virtuous cycle incomplete (no concept extraction flow)
- Domain hardcoding ("Therapy" in notebook preferences)

**See:** `docs/CRITICAL-ANALYSIS-2025-12-05.md` for full findings
**See:** `docs/PRESSURE-TEST-PLAN.md` for systematic evaluation of all components

**Current Priority:** Remediate SiYuan plugin, then pressure test remaining components.

---

**All Four Layers Built (But Principle Alignment Unverified):**
- ✅ Layer 1: Calibre library (179 books) + auto-ingestion daemon → 291 entities, 338 relationships (10 books indexed)
- ✅ Layer 2: Backend APIs complete — 85/85 tests passing (Books, Reframe, Template, Personal, Graph APIs)
- ⚠️ Layer 3: SiYuan Plugin — **NEEDS REMEDIATION** (design system, question interaction, principle alignment)
- 🔍 Layer 4: Readest — **PENDING PRESSURE TEST**

**Latest (Dec 8):**
- ✅ **Flow Mode Navigation Foundation (Phase 1)** — Graph traversal with trail tracking
  - Navigation state machine: `FocusState` = 'idle' | 'question' | 'entity' | 'facet'
  - Trail component (breadcrumbs): Context → Question → Entity with click-to-navigate
  - EntityFocus view: name, type, description, neighbors (clickable), source books
  - Functions: `navigateToEntity()`, `navigateBack()`, `pushTrail()`, `popTrail()`
  - Sections hide when in entity focus for clean UI
  - Commit: `58f1c94` in SiYuan worktree
- ✅ **Context Layer MVP** — Question-driven exploration for Flow Mode
  - Backend: `/context` API with parse, save, search, journey endpoints
  - Types: Context, Question, ContextJourneyEntry schemas in `schemas/context.py`
  - Parser: Detects Context Notes via `## Key Questions`, `## Areas of Exploration`, `## Core Concepts` sections
  - Search: Keyword-based entity lookup using context concepts + question terms
  - Flow Mode: New `contextBlockId` prop, Context Panel with clickable question buttons
  - 191 backend tests passing

**Dec 5:**
- ✅ **Question Engine Nine Classes Implementation (Commit 1d1ca9f)** — Backend question classification system complete
  - QuestionClass enum with 9 classes mapped to AST thinking modes
  - APPROACH_TO_CLASSES mapping: inquiry approaches generate specific question types
  - New endpoints: `/question-classes` (list all with descriptions), `/approach-classes` (show approach→class mappings)
  - ClassifiedQuestion schema for tagged questions with cognitive function labels
  - Integration with ForgeMode: state detection, approach selection, question generation all use class system
- ✅ **AST Folder Structure and Session Persistence (Commit c97aaf7, updated dfe3ced)** — SiYuan plugin creates structured session documents with complete 10-folder hierarchy
  - **Complete STRUCTURE_FOLDERS:** /Daily/, /Seedlings/ (7 subcategories), /Sessions/ (5 mode folders), /Flow_Maps/, /Concepts/, /Insights/, /Favorite_Problems/, /Projects/, /Archive/, /System/ (Templates + Example_Notes)
  - createSessionDocument() function: saves sessions with frontmatter (be_type, be_id, mode, topic, status, resonance, energy)
  - Session documents include: section responses (template-driven), full conversation transcript, entities extracted, graph mapping status
  - ForgeMode integration: sessions auto-save to SiYuan on completion with timestamp and mode-specific folder placement
- ✅ **IES AST Mode and Question Engine** — 20 SiYuan documents created defining structured thinking architecture
  - Four thinking modes: Discovery (schema surfacing), Dialogue (model building), Flow (associative exploration), AST (assisted structured thinking)
  - Nine question classes: Schema-Probe, Boundary, Dimensional, Causal, Counterfactual, Anchor, Perspective-Shift, Meta-Cognitive, Reflective-Synthesis
  - Mode Transition Engine specifications for automatic mode switching
  - ADHD-friendly folder structure: /Daily, /Insights, /Threads, /Favorite Problems, /Concepts
  - Complete data schemas: Seed Schema, Concept Schema, Block Attributes, Note Templates

**For complete project status, see:** `docs/COMPREHENSIVE-PROJECT-STATUS.md`

**Phase 1 Achievement Summary:**
- ✅ **10/10 validation sessions completed** — System validated using personal therapy/growth exploration
- ✅ **11+ concepts extracted and formalized** — Demonstrated the full thinking → extraction pipeline
- ✅ **Complete concept connection map** — Hierarchical relationships documented in CONNECTIONS.md
- ✅ **Extraction pipeline proven end-to-end** — Session → Transcript → Extraction → Formalization → Commit
- ✅ **Core hypothesis validated** — Personalized dialogue patterns directly affect concept discovery
- ✅ **IES backend (85/85 tests passing)** — All APIs production-ready
- ✅ **Calibre integration complete** — 179 books, auto-ingestion daemon running

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
- **Phase 2c (75% COMPLETE):** Calibre integration + Entity overlay + Reframe API + Template API + ForgeMode + Context Layer
- **Phase 3+:** Cross-app sync, journey analysis, additional domains

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
- `docs/SYSTEM-DESIGN.md` — Operational reference: how all layers integrate, critical gaps, SiYuan AST structure (4 modes, 9 question classes)
- `docs/PROJECT-OVERVIEW.md` — Complete vision and design rationale, IES Question Engine preview
- `docs/five-agent-synthesis.md` — Deep analysis of why architecture decisions were made
- `docs/PHASE-1-WORKFLOW.md` — Phase 1 operational guide (for reference if running additional exploration sessions)
- `IES AST SiYuan structure.md` — Tracking document for 20 SiYuan notebook pages defining AST mode architecture
- `docs/IES question engine expansion.md` — Complete Question Engine specification (referenced by SiYuan documents)

### Phase 2c Focus

**Current Implementation: Integration Features** (Dec 4-5, 2025)

**Completed in Phase 2c:**
- ✅ **Calibre Integration** — Single source of truth for book catalog (179 books)
- ✅ **Books API** — Catalog, search, covers, file serving via HTTP
- ✅ **Auto-Ingestion Daemon** — Background processing, 10/179 books indexed
- ✅ **Entity Overlay** — Inline highlighting in Readest with type-specific colors
- ✅ **Calibre Library Browser** — Browse/search/open books in Readest
- ✅ **Reframe API** — Claude-generated metaphors/analogies with caching
- ✅ **Template API** — Structured thinking templates for ForgeMode
- ✅ **ReframesTab** — UI components in SiYuan and Readest

**Remaining:**
- 🔄 Pass 2/3 enrichment (relationships, LLM enrichment)
- 🔄 Cross-app continuity (Readest ↔ SiYuan sync)
- 🔄 SiYuan document structure implementation

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

**Entity Overlay Flow Mode (Dec 4)** — Next Phase 2c workstream: Auto-annotated entity highlighting in book text
- Backend: `GET /graph/entities/by-book/{hash}` endpoint returns all entities mentioned in a book (sorted by frequency)
- Frontend: Content transformer wraps entity names in styled `<span>` elements for type-based highlighting
- UI: Entity type filter controls show/hide Concept/Person/Theory/Framework/Assessment
- Click interaction: Clicking highlighted entity opens flow panel with entity connections
- Full implementation plan: `docs/plans/2025-12-04-entity-overlay-flow-mode.md` (6-task TDD plan with code examples)

**Remaining Critical Gaps (Deferred):**

3. **Book Library Now Accessible** (Gap addressed Dec 4) — Calibre integration design provides single source of truth for book catalog
   - Solution: Calibre library as canonical book source with calibre_id as universal identifier
   - Backend: Book catalog API, entity lookup by calibre_id, book cover fetching
   - Frontend: Readest library browser with book selection
   - Ingestion: Multi-pass pipeline (structure → relationships → enrichment) with status tracking
   - See: `docs/plans/2025-12-04-calibre-integration-design.md` for complete architecture

4. **Cross-App Continuity Missing** — Readest and SiYuan don't share state. Can't resume reading session from SiYuan or resume exploration from Readest.

5. **Journey Value Loop Not Closed** — Journeys are captured but never analyzed for patterns. Patterns not used to personalize suggestions or improve thinking partner questions.

**For Gap Analysis:**
- `docs/PLANNING-GAPS-AND-QUESTIONS.md` — Comprehensive gap analysis with detailed technical review
- `docs/COMPREHENSIVE-PROJECT-STATUS.md` — Complete technical status of all four layers
- `docs/plans/2025-12-04-calibre-integration-design.md` — Calibre integration: single source of truth for book catalog and entity indexing

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
├── calibre/                       # Calibre book library (Layer 1 source of truth)
│   ├── config/                    # Calibre Web configuration
│   ├── library/                   # SQLite metadata + book files (epub/pdf)
│   └── ingest/                    # Incoming books directory for processing
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
│   │   ├── 2025-12-04-reframe-template-integration-design.md  # Phase 2c: Reframe + Templates
│   │   ├── 2025-12-04-calibre-integration-design.md  # Calibre integration architecture
│   │   └── 2025-12-04-readest-calibre-library-view.md  # Phase 4: Readest library browser (UI design)
│   └── archive/                   # Old progress files, archived memories
│
└── docker-compose.yml             # Neo4j + Qdrant + Calibre infrastructure (Layers 1 & 2 support)
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
- `docs/plans/2025-12-04-reframe-template-integration-design.md` — Phase 2c implementation: Reframe Layer + Thinking Templates + SiYuan document structure
- `docs/plans/2025-12-04-calibre-integration-design.md` — Calibre integration architecture: single source of truth for book catalog with universal calibre_id identifier; multi-pass ingestion pipeline (structure → relationships → enrichment); backend APIs complete (Dec 4)
- `docs/plans/2025-12-04-readest-calibre-library-view.md` — **Phase 4 UI design**: Readest library browser modal with search, entity badge filter, and direct book opening (Dec 4)
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
- IES AST Mode implementation (specifications complete Dec 5, SiYuan notebook created)

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

**Recent Changes (Dec 5):**
- **SiYuan Plugin Structure Refinements** — Enhanced domain-agnostic configuration and session document metadata:
  - `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts`: Updated session document creation with ShapingBlockMeta support (769 lines)
  - **10-folder structure complete:** Added `/System/` folder with Templates and Example_Notes subfolders (Package's 07_System)
  - **Backend health check fix:** Aligned `BackendHealth` interface with Dashboard expectations (`ok`, `backendUrl`, `checkedAt`, `message` fields)
  - **Notebook preferences:** Added 'IES' to default notebook names for better domain-agnostic alignment
  - **Error handling enhancement:** `callBackendApi()` now properly throws errors instead of returning null, with detailed logging
  - **Purpose:** Completes merged architecture with full Package 07_System layer, fixes health check interface mismatch
- **Backend Health Check Bug Fix** — Fixed `checkBackendHealth()` function interface alignment with Dashboard component:
  - `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts`: Updated `BackendHealth` interface and function signature
  - **Interface change:** From `{ status: string, timestamp?: string }` to `{ ok: boolean, backendUrl: string, checkedAt: number, message?: string }`
  - **Signature change:** From `checkBackendHealth(force = false)` to `checkBackendHealth(options: { force?: boolean } = {})`
  - **Return value:** Now consistently returns `BackendHealth` object with `ok` (boolean), `backendUrl` (string), `checkedAt` (timestamp), and optional `message`
  - **Impact:** Fixes Dashboard.svelte which calls `checkBackendHealth({ force })` and expects `ok`, `backendUrl`, `message` properties
  - **Cache behavior:** 30-second TTL caching unchanged, maintains reduced API overhead
- **Concept Extraction and Formalization (Commit 242ae72)** — Completes the IES virtuous cycle: sessions → extract entities → formalize concepts → enrich knowledge graph
  - **Backend API:** New `/concepts` endpoint (POST, GET, GET/{name}) with Neo4j persistence
  - **Schemas:** `CreateConceptRequest`, `ConceptResponse`, `ConceptType` enum (concept, theory, framework, mechanism, pattern, distinction), `RelationshipType` enum (supports, contradicts, component_of, operationalizes, develops, enables, contrasts_with)
  - **ConceptService:** `ies/backend/src/ies_backend/services/concept_service.py` (200 lines) — Neo4j integration for concept persistence with relationship creation
  - **ConceptExtractor Component:** `.worktrees/siyuan/ies/plugin/src/components/ConceptExtractor.svelte` (600+ lines) — 4-step wizard interface
    - **Step 1 - Select:** Choose from extracted entities or start from scratch
    - **Step 2 - Define:** Concept type, name, description, aliases
    - **Step 3 - Relate:** Add relationships to existing concepts with evidence
    - **Step 4 - Review:** Confirm before dual save (Neo4j + SiYuan)
  - **ForgeMode Integration:** Session completion flow now offers concept extraction for each entity
    - "Quick" button: Simple name+description dialog for rapid capture
    - "Advanced" button: Full wizard with relationships and aliases
  - **createConceptDocument():** New function in `siyuan-structure.ts` creates `/Concepts/` documents with ConceptBlockMeta frontmatter (block_type: 'concept', concept_id, concept_type, related_concepts, version)
  - **Dual Save Pattern:** Concept saved to both Neo4j graph (with relationships) AND SiYuan document (for editing/expansion)
  - **Session Evidence:** Supports source_session_id and source_quotes linking concepts back to the session where they emerged
  - **Impact:** Addresses critical finding "Virtuous cycle incomplete" — thinking sessions now feed back into Layer 1 knowledge graph
- **ForgeMode Comprehensive UI Styling (Commit 25a4f21)** — Complete CSS system for all ForgeMode components (~440 lines total):
  - `.worktrees/siyuan/ies/plugin/src/views/ForgeMode.svelte`: Comprehensive styling addressing all previously unstyled components
  - **Setup section:** `.forge-setup`, `.mode-selector`, `.mode-option` (selected/hover states), `.topic-input`, `.start-btn`
  - **Conversation area:** `.forge-main`, `.forge-conversation`, `.forge-msg` (user/assistant variants), `.forge-loading` (spinner animation), `.forge-error`, `.forge-actions`
  - **Template progress panel:** `.forge-progress`, `.progress-header`, `.progress-sections`, `.progress-section` (current/completed states), `.progress-footer`, `.progress-actions`
  - **Question class system:** `.question-class-badges`, `.question-class-badge`, `.question-classes-bar` for visual tracking
  - **Cognitive coverage:** `.cognitive-coverage`, `.coverage-bars`, `.coverage-bar` (label/track/fill components), `.coverage-percent`
  - **Interactive question-response card:** `.question-response-card` with class-colored borders, `.qrc-header`, `.qrc-question`, `.qrc-hint` (cognitive guidance), `.qrc-input` (focus states), `.qrc-starter`/`.qrc-skip`/`.qrc-respond` buttons, `.qrc-history`
  - **Design system integration:** Uses CSS custom properties (--accent, --secondary, --bg-elevated, --radius-md, --space-N, --shadow-md), dark theme support
  - **Interactive functionality:** Pairs with `handleQuestionResponse()` function for full question-answer dialogue workflow
  - **Impact:** Addresses critical analysis finding - all UI components now properly styled, moving from "passive display" to complete interactive system
- **IES AST Mode Documentation** (commit 3b347fc) — Comprehensive SiYuan notebook structure defining assisted structured thinking architecture:
  - `IES AST SiYuan structure.md`: Tracking document for 20 new SiYuan pages across 6 sections (Modes, Question Engine, Data Schemas, Specs, Templates, Workflows)
  - **Four thinking modes:** Discovery (schema surfacing), Dialogue (model building), Flow (associative exploration), AST (assisted structured thinking)
  - **Nine question classes:** Schema-Probe (hidden structure), Boundary (clarify edges), Dimensional (introduce spectra), Causal (mechanisms), Counterfactual (what-if), Anchor (concrete instances), Perspective-Shift (viewpoint change), Meta-Cognitive (thinking patterns), Reflective-Synthesis (integration)
  - **Mode Transition Engine:** Automatic mode switching based on interaction cadence, cognitive load markers, and resonance hits
  - **User Cognition Model integration:** 6-dimension profile drives template defaults and question class selection
  - **ADHD-friendly folder structure:** `/Daily/` (zero-friction capture), `/Insights/` (promoted sparks), `/Threads/` (exploration paths), `/Favorite Problems/` (anchor questions), `/Concepts/` (knowledge graph nodes)
  - **Data Schemas:** Seed Schema (atomic insights), Concept Schema (persistent ideas with causal structure), Block Attributes (SiYuan metadata standards), Note Templates (per-mode session templates)
  - **Integration:** AST mode bridges ForgeMode templates with Flow exploration, provides canonical placement for sparks/insights
  - **Documentation updates:** SYSTEM-DESIGN.md adds Section 3.7 (SiYuan AST Structure), PROJECT-OVERVIEW.md adds IES Question Engine preview, COMPREHENSIVE-PROJECT-STATUS.md updated with documentation status
  - **Source:** Based on IES Question Engine expansion spec synthesized with existing ADHD ontology design research

**Recent Changes (Dec 4):**
- **Entity Overlay UI Redesign** (commits 0b646cf, fddd8f0, 8887e90) — Enhanced user experience with pill-based controls and Flow Panel integration:
  - `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/EntityTypeFilter.tsx`: Complete redesign from checkbox-based to pill-based UI (122 lines)
  - **Master toggle redesign:** Replaced checkbox with prominent ON/OFF button featuring eye icons (LuEye/LuEyeOff from react-icons)
  - **Pill controls:** Interactive type-specific pills replace traditional checkboxes for more intuitive visual feedback
  - **Active state styling:** Pills show type-specific colors with 12% opacity backgrounds when active, muted appearance when inactive
  - **Status indicator:** Centered display shows entity count ("X entities in this book"), loading spinner, error messages, or "Book not indexed" warning
  - **Disabled interaction:** Pills are properly disabled when overlay is off to prevent user confusion
  - **Flow Panel integration:** EntityTypeFilter positioned at top of Flow Panel (FlowPanel.tsx lines 156-159) for immediate access
  - **Flow Panel components updated:** EntitySection, RelationshipsSection, SourcesSection, QuestionsSection, Header all refined with type-specific badges and consistent styling
  - **CSS styling system:** Complete entity overlay styling in `globals.css` (lines 559-618 for filter controls, 756-855 for inline highlights)
  - **Type-specific colors:** Blue (Concept #2563eb), Green (Person #059669), Purple (Theory #7c3aed), Orange (Framework #ea580c), Red (Assessment #dc2626)
  - **Hover effects:** Underline decoration appears on hover with type-specific color transitions for both pills and inline highlights
  - **Visual consistency:** All Flow Panel sections now use consistent design language with flow-card, flow-section-header, relationship-badge classes
- **Template API for ForgeMode Integration** (commit 9fcc171) — New backend endpoint enables structured thinking sessions:
  - `ies/backend/src/ies_backend/api/template.py`: New FastAPI router with `GET /templates/{template_id}` endpoint (24 lines)
  - Returns `ThinkingTemplate` schema with sections, graph mapping rules, and AI behavior specifications
  - Registered in `ies/backend/src/ies_backend/main.py` with `/templates` prefix
  - Integration: `.worktrees/siyuan/ies/plugin/src/views/ForgeMode.svelte` fetches templates via SiYuan forwardProxy
  - Available templates: `learning-mechanism-map` (understand mechanisms), `articulating-clarify-intuition` (clarify vague thoughts)
  - Enables template-driven sessions with section-by-section progress tracking in ForgeMode UI
- **Auto Ingestion Daemon Operational** — Fixed critical Book-Entity relationship structure for full entity overlay compatibility:
  - `scripts/auto_ingest_daemon.py`: Fixed MENTIONS relationship creation between Book and Entity nodes (lines 150-156)
  - **Problem:** Auto-ingested books had entities but missing direct Book→MENTIONS→Entity relationships required by entity overlay feature
  - **Solution:** After entity extraction, daemon now creates MENTIONS relationships for each entity: `MATCH (b:Book {calibre_id: $calibre_id}) MATCH (e) WHERE e.name = $entity_name MERGE (b)-[:MENTIONS]->(e)`
  - **Impact:** Books processed by daemon now fully support entity overlay in Readest reading interface
  - **Results:** Successfully processed 9 out of 10 Calibre books with entity counts ranging from 6 to 169 entities per book
  - **Graph structure:** Now matches expected schema for `GET /graph/entities/by-calibre-id/{calibre_id}` endpoint
  - **Daemon status:** Background processing operational, running every 5 minutes with comprehensive entity extraction and proper Book-Entity linking
  - **Entity overlay requirement:** Books must be opened via Calibre Library dialog in Readest (not local library) to access indexed content
  - **SiYuan integration:** Suggestions API working and returns both connected entity suggestions and new entity recommendations
- **Tauri Runtime Detection Enhancement** — Fixed browser crashes with deep object validation (commit 7c9ca46):
  - `.worktrees/readest/readest/apps/readest-app/src/services/environment.ts`: Enhanced `isTauriAppPlatform()` with five-point validation
  - Problem: Setting `NEXT_PUBLIC_APP_PLATFORM=tauri` alone caused app to attempt Tauri API calls in browser context, leading to crashes
  - Root cause: Partial `__TAURI_INTERNALS__` objects can exist in browser context without full Tauri functionality
  - Solution: Five-point validation ensures BOTH environment configuration AND complete Tauri runtime availability
  - Implementation checks:
    1. `process.env.NEXT_PUBLIC_APP_PLATFORM === 'tauri'` — Environment configured for Tauri
    2. `typeof window !== 'undefined'` — Browser context exists (prevents SSR errors)
    3. `window.__TAURI_INTERNALS__ !== undefined` — Tauri object exists
    4. `typeof internals === 'object' && internals !== null` — Valid object structure
    5. `typeof internals.invoke === 'function'` — Critical: Full Tauri API available with invoke function
  - Rationale: Previous simple check (`'__TAURI_INTERNALS__' in window`) was insufficient because partial objects can exist without invoke capability
  - Safety: Each validation step builds on previous, preventing TypeError exceptions in edge cases
  - Impact: App gracefully falls back to WebAppService when running in browser, even if environment variable is incorrectly set
  - Use case: Enables running `pnpm dev` in browser for debugging without breaking Tauri-specific code paths
  - Pattern: `getNativeAppService()` catches Tauri plugin load failures and falls back to WebAppService
  - Related: `.worktrees/readest/readest/apps/readest-app/src/services/nativeAppService.ts` uses dynamic import for `@tauri-apps/plugin-os`
- **Readest Native Service Dynamic Import Fix** (commit 51b8ee3) — Fixed browser/Tauri context compatibility with dynamic plugin loading:
  - `.worktrees/readest/readest/apps/readest-app/src/services/nativeAppService.ts`: Removed static import of `@tauri-apps/plugin-os`, replaced with dynamic import
  - Problem: Static `import { type as osType } from '@tauri-apps/plugin-os'` executes module-level code requiring Tauri APIs, causing Next.js build failures in browser context
  - Solution: Dynamic import pattern with async initialization
  - Implementation: `initOsType()` async function calls `await import('@tauri-apps/plugin-os')` and caches result in `_osType` variable
  - Execution: `initOsType()` invoked at start of `NativeAppService.init()` method, which only runs in actual Tauri environment
  - Impact: All 20+ OS-type-dependent properties converted from static values to getters calling `getOsType()` (e.g., `override get isAndroidApp() { return getOsType() === 'android'; }`)
  - Pattern: Dynamic import ensures Tauri plugin only loads when running in Tauri, not during Next.js bundling for browser
  - Result: Eliminates module-level code execution that fails in browser/SSR contexts
- **Relationship Type Sanitization** — Enhanced Neo4j relationship creation with robust type validation:
  - `library/graph/neo4j_client.py`: `add_relationship()` method now sanitizes relationship types before creating Neo4j relationships
  - Replaces spaces and hyphens with underscores (e.g., "RELATED TO" → "RELATED_TO")
  - Removes invalid characters using regex (only A-Z, 0-9, underscore allowed in Neo4j relationship types)
  - Fallback to "RELATED_TO" for empty/invalid types
  - Prevents Neo4j Cypher syntax errors during ingestion from malformed relationship type names
- **GraphService Entity Query Fix** (Dec 4) — Critical alignment between ingestion and query patterns:
  - **Problem:** Entity overlay failing because queries used old Book<-Chunk->Entity pattern while ingestion creates direct Book->Entity relationships
  - **Solution:** Modified `get_entities_by_calibre_id()` and `get_entities_by_book()` to use `MATCH (b)-[:MENTIONS]->(e)` pattern
  - **Root cause:** `scripts/ingest_calibre.py` creates direct Book-MENTIONS->Entity relationships without intermediate Chunk nodes
  - **Impact:** Entity overlay now works correctly by matching actual graph structure created during book ingestion
  - **Pattern change:** From `MATCH (b)<-[:BELONGS_TO]-(chunk)-[:MENTIONS]->(e)` to `MATCH (b)-[:MENTIONS]->(e)`
  - **Files changed:** `ies/backend/src/ies_backend/services/graph_service.py` lines 218 and 267
- **Calibre Integration Phase 3 Complete (Commit 3c2efde)** — Multi-pass ingestion pipeline for Calibre books into Neo4j:
  - Ingestion script: `scripts/ingest_calibre.py` — Extracts entities from Calibre books and stores in Neo4j with `calibre_id` as primary identifier (263 lines)
  - Multi-pass pipeline: Pass 1 (structure: Book node + chunks + entities + MENTIONS relationships → status: entities_extracted)
  - Future passes: Pass 2 (relationships), Pass 3 (LLM enrichment with reframes, mechanisms, patterns)
  - Migration script: `scripts/match_calibre_ids.py` — Matches existing Neo4j Book nodes to Calibre books by title/author similarity for one-time migration (167 lines)
  - KnowledgeGraph updates: `add_book()` accepts `calibre_id` parameter, `book_exists()` checks by calibre_id, `update_book_status()` tracks processing lifecycle
  - Entity extraction: Uses existing `EntityExtractor` from `library/graph/entities.py` with OpenAI
  - Status lifecycle: `pending → chunked → entities_extracted → relationships_mapped → enriched`
  - CLI features: `--id` (single book), `--test` (one book test), `--status` (processing stats), `--limit` (batch size)
  - Library path: `/home/chris/Documents/calibre` (179 books)
- **Calibre Integration Phase 2 Complete (Commit 9542ec2, updated 6d607af)** — Backend APIs for Calibre book library access:
  - New `CalibreService` queries Calibre `metadata.db` SQLite database with `get_book_file_path()` method (128 lines)
  - New `Book` schema with `calibre_id`, `title`, `author`, `path` (Pydantic model)
  - Books API: `GET /books`, `GET /books?search=`, `GET /books/{calibre_id}`, `GET /books/{calibre_id}/cover` (125 lines)
  - **File serving endpoints:** `HEAD /books/{calibre_id}/file` (metadata only), `GET /books/{calibre_id}/file` (epub/pdf download)
  - File serving: Prefers epub over pdf, serves with correct media types (application/epub+zip or application/pdf)
  - GraphService: New `get_entities_by_calibre_id()` method for direct Calibre ID entity lookup (47 lines)
  - Entity API: New `GET /graph/entities/by-calibre-id/{calibre_id}` endpoint (20 lines)
  - Tests: 85/85 backend tests passing (6 CalibreService tests, 6 Books API tests, 3 entity endpoint tests)
  - Eliminates hash/title matching fragility by using Calibre as single source of truth
- **Backend Refactoring** (commit a9ce87b) — Enhanced session processing and state detection:
  - New `SessionService` extracted from `session.py` for cleaner separation of concerns (142 lines)
  - Orchestrates session extraction, storage, and template mapping pipeline
  - Enhanced `StateDetectionService` with improved word boundary matching for marker detection
  - Added context handling for repetition detection and emotional state analysis
  - Book entities API: Added `title` query parameter for dual identifier strategy (hash OR title matching)
  - ADHD ontology exports: Added `Reframe` and `ReframeType` to `library/graph/__init__.py`
  - Schema updates: Additional entity fields for session processing
  - Tests: 70/70 backend tests passing (all question_engine tests fixed)
- **Entity Overlay Feature Complete** (commit 3a513b2) — Real-time entity highlighting in Readest reading interface:
  - Backend: GET `/graph/entities/by-book/{book_hash}` endpoint returns entities sorted by mention frequency
  - GraphService: `get_entities_by_book()` method with entity type filtering support
  - Frontend: Entity overlay transformer wraps entity mentions in styled spans for inline highlighting
  - UI: EntityTypeFilter component with master toggle and per-type visibility controls (Concept, Person, Theory, Framework, Assessment)
  - State: flowModeStore manages overlay state, entity fetching, and type filtering
  - Integration: FoliateViewer auto-fetches entities on book load, transforms HTML content with entity highlights
  - Tests: 70/70 backend tests passing (3 new tests for book_entities endpoint)
- **Phase 2c Backend Complete** (commit 46bc30b) — Three integrated backend services addressing critical gaps #1 and #2:
  - Reframe API (`/reframes`) — Concept reframes via Claude Sonnet 4 with caching and feedback voting
  - Personal Graph API (`/personal`) — ADHD-friendly spark/insight capture with resonance and energy-based retrieval
  - Template Service — JSON-based thinking templates with validation and graph mapping execution
- Updated `library/graph/__init__.py` to export unified graph API with ADHD-friendly ontology implementation for personal knowledge capture.
- **SiYuan Structure Documentation** (Dec 5) — Comprehensive documentation of IES SiYuan notebook organization:
  - `IES AST SiYuan structure.md`: Tracking document for 20 created SiYuan pages across 6 major sections
  - **Core Navigation:** Project Index with unified entry point and quick navigation
  - **Modes Section:** 4 thinking modes documented (Discovery, Dialogue, Flow, AST) + Mode Transition Engine specification
  - **Question Engine:** Complete documentation of 9 question classes (Schema-Probe, Boundary, Dimensional, Causal, Counterfactual, Anchor, Perspective-Shift, Meta-Cognitive, Reflective-Synthesis)
  - **Data Schemas:** 5 schema specifications (Seed Schema, Concept Schema, Block Attributes, Note Templates, Folder Structure Standards)
  - **ADHD-Friendly Folders:** 5 folder templates documented (`/Daily/`, `/Insights/`, `/Threads/`, `/Favorite Problems/`, `/Concepts/`)
  - **Integration Specifications:** User Cognition Model, mode transition rules, question routing by mode, SiYuan block attribute standards
  - **Notebook ID:** `Intelligent Exploration System` (20251201113102-ctr4bco)
  - **Source:** Based on ChatGPT Question Engine expansion spec synthesized with existing IES architecture and ADHD-friendly ontology research

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

### Layer 3: SiYuan Plugin Architecture (Phase 2c - Dec 5)

**AST Folder Structure:**

The plugin creates an ADHD-friendly folder hierarchy in SiYuan notebooks for session persistence and knowledge organization:

```
/Daily/                   # Daily log for low-friction capture
/Insights/                # Promoted insights from sparks
/Threads/                 # Active exploration threads
/Favorite Problems/       # Anchor questions (Feynman-inspired)
/Concepts/                # Formalized concepts
/Sessions/                # AST session documents (mode-specific)
  ├── Learning/           # Learning mode sessions
  ├── Articulating/       # Articulating mode sessions
  ├── Planning/           # Planning mode sessions
  ├── Ideating/           # Ideating mode sessions
  └── Reflecting/         # Reflecting mode sessions
```

**Question Class Tracking in ForgeMode (Dec 5):**

ForgeMode now tracks which question classes are used during sessions and displays them with visual badges:

**Question Class Labels:**
- **Schema-Probe (🏗️)** — Structure questions (blue #4a90d9)
- **Boundary (🔲)** — Edge/limit questions (purple #7b68ee)
- **Dimensional (📐)** — Spectrum questions (teal #20b2aa)
- **Causal (⚡)** — Mechanism questions (tan #f4a460)
- **Counterfactual (🔮)** — What-if questions (orchid #da70d6)
- **Anchor (⚓)** — Concrete example questions (green #3cb371)
- **Perspective-Shift (👁️)** — Viewpoint change questions (brown #cd853f)
- **Meta-Cognitive (🧠)** — Thinking pattern questions (gray #778899)
- **Reflective-Synthesis (🔗)** — Integration questions (blue #6495ed)

**Features:**
- Questions generated with classified question classes from Question Engine
- Visual emoji badges displayed inline with questions during session
- `questionClassesUsed` array tracks all classes used in session
- `lastQuestionClass` stores most recent question class
- Question classes included in session document frontmatter
- Session results display question types with human-readable labels

**Implementation:**
- `.worktrees/siyuan/ies/plugin/src/views/ForgeMode.svelte` lines 107-127 (QUESTION_CLASS_LABELS), 405-415 (tracking), 437-445 (display)
- Question class tracking integrated with Question Engine API calls
- Supports both classified_questions (new format) and fallback to plain questions array

**Session Document Creation (ForgeMode):**

When a ForgeMode session completes, `createSessionDocument()` saves structured documents with:

**Frontmatter (YAML):**
```yaml
be_type: "session"
be_id: "session_abc123"
mode: "learning"
topic: "Understanding executive function"
status: "completed"
created: "2025-12-05T01:42:00Z"
template_id: "learning-mechanism-map"
template_name: "Mechanism Map"
entities_extracted: 12
graph_mapping_executed: true
question_classes_used: ["schema_probe", "causal", "anchor"]
```

**Document Contents:**
1. **Topic Section** — Session topic, thinking mode, template name (if applicable), date
2. **Section Responses** — Template-driven responses by section ID (if template-based session)
   - Section IDs formatted as human-readable headings
   - Example: "understanding_prerequisites" → "Understanding Prerequisites"
3. **Conversation Transcript** — Full user/AI message exchange with role labels
   - Formatted: **You:** / **AI:** with horizontal rules between messages
   - Includes thinking partner questions with emoji badges
4. **Session Results** — Summary of session outcomes
   - Entities extracted count
   - Graph mapping status (✓ if executed)
   - Question types used with human-readable labels (Structure, Causal, Anchor, etc.)

**Implementation:**
- `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts` — `createSessionDocument()` function (lines 499-638)
  - MODE_FOLDER_MAP: Maps thinking modes to folder paths
  - SessionDocumentOptions interface: Full type safety for session data
  - serializeFrontmatter(): YAML serialization with proper type handling
  - Question class labels: Converts snake_case to readable names
- `.worktrees/siyuan/ies/plugin/src/views/ForgeMode.svelte` — Calls `createSessionDocument()` on session end (lines 480-491)
  - Passes template data, section responses, transcript, question classes used
  - Displays success message with entity count and question types
- Notebook selection: Prefers "Personal", "Therapy", or first open notebook
- File path: `/Sessions/{mode}/{YYYY-MM-DD-HHMM-topic}.md`
- Block attributes: `custom-be_type`, `custom-be_id`, `custom-mode`, `custom-status` for backend linking

**Purpose:**
- Persistent record of thinking sessions for later review
- Breadcrumb trail showing evolution of understanding
- Raw material for concept extraction and formalization
- Training data for Mode Transition Engine pattern learning
- Question class analytics for understanding thinking patterns

---

### Layer 2: Phase 2c Backend APIs (Dec 5)

Six integrated backend services addressing critical gaps #1-#3, all registered in `ies/backend/src/ies_backend/main.py`:

**1. Reframe API** (`/reframes`) — Makes domain concepts accessible via metaphors, analogies, stories, patterns, and contrasts

**Endpoints:**
- `GET /concepts/{concept_id}/reframes` - Retrieve cached reframes
- `POST /concepts/{concept_id}/reframes/generate` - Generate 1-10 reframes via Claude Sonnet 4
- `POST /reframes/{reframe_id}/feedback` - Vote helpful/confusing

**Entity Type:** `Reframe` (Neo4j, linked to concepts via `HAS_REFRAME`)

**Reframe Types:** `metaphor`, `analogy`, `story`, `pattern`, `contrast`

**Implementation:**
- `ies/backend/src/ies_backend/api/reframe.py` - FastAPI router (55 lines)
- `ies/backend/src/ies_backend/services/reframe_service.py` - Service with Claude Sonnet 4 integration
- `ies/backend/src/ies_backend/schemas/reframe.py` - Pydantic schemas
- `ies/backend/tests/test_reframe_service.py` - Unit tests

**Frontend Integration:**
- SiYuan: `.worktrees/siyuan/ies/plugin/src/components/ReframesTab.svelte`
- Readest: `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/ReframesSection.tsx`

---

**2. Personal Graph API** (`/personal`) — ADHD-friendly personal knowledge capture with emotional resonance and energy tracking

**Core Endpoints:**
- `POST /personal/sparks` - Create spark (raw resonance capture with optional SiYuan block linking)
- `GET /personal/sparks/{spark_id}` - Retrieve spark by ID
- `POST /personal/sparks/{spark_id}/visit` - Record visit for recency tracking
- `POST /personal/sparks/{spark_id}/promote` - Promote spark to insight (status: captured → anchored)

**ADHD-Friendly Retrieval:**
- `GET /personal/sparks/by-resonance/{signal}` - Find by emotional state (8 signals: curious, excited, surprised, moved, disturbed, unclear, connected, validated)
- `GET /personal/sparks/by-energy/{level}` - Find by energy level (low/medium/high) for mood-appropriate navigation
- `GET /personal/sparks/unvisited` - Surface forgotten captures

**Statistics:**
- `GET /personal/stats` - Personal graph stats (spark count, insight count, resonance distribution)

**Implementation:**
- `ies/backend/src/ies_backend/api/personal.py` - FastAPI router (130 lines)
- `ies/backend/src/ies_backend/services/personal_graph_service.py` - Service layer (leverages `library.graph.ADHDKnowledgeGraph`)
- `ies/backend/src/ies_backend/schemas/personal.py` - Pydantic schemas

---

**3. Template API** (`/templates`) — JSON-based thinking templates with validation and graph mapping

**Endpoints:**
- `GET /templates/{template_id}` - Retrieve thinking template by ID (returns `ThinkingTemplate` schema)

**Available Templates:**
- `learning-mechanism-map` - Learning mode: understand how something works
- `articulating-clarify-intuition` - Articulating mode: clarify vague intuitions

**Features:**
- JSON Schema validation (`schemas/thinking-template.schema.json`)
- Template loading with Pydantic validation fallback
- Graph mapping execution (`create_or_link`, `update_journey` actions)
- Two reference templates provided:
  - `schemas/templates/learning-mechanism-map.json` - Learning mode: mechanism map
  - `schemas/templates/articulating-clarify-intuition.json` - Articulating mode: clarify intuition

**Implementation:**
- `ies/backend/src/ies_backend/api/template.py` - FastAPI router (24 lines) with GET endpoint
- `ies/backend/src/ies_backend/services/template_service.py` - Template loading and execution (150 lines)
- `ies/backend/src/ies_backend/schemas/template.py` - Template structure definitions
- `ies/backend/tests/test_template_service.py` - Unit tests
- Registered in `ies/backend/src/ies_backend/main.py` with `/templates` prefix

**Frontend Integration:**
- SiYuan: `.worktrees/siyuan/ies/plugin/src/views/ForgeMode.svelte` - Fetches templates via `apiGet()` with SiYuan forwardProxy
- Template-driven session state: currentSectionIndex, sectionResponses tracking
- Thinking modes mapped to template IDs: `learning` → `learning-mechanism-map`, `articulating` → `articulating-clarify-intuition`

**JSON Schema:** `schemas/thinking-template.schema.json` defines:
- 5 thinking modes: `learning`, `articulating`, `planning`, `ideating`, `reflecting`
- Section structure: `id`, `prompt`, `input_type` (concept_search/freeform/selection), `ai_behavior`, `required`
- Graph mapping actions: `create_or_link`, `update_journey` with metadata and relationship specs

---

**3b. Question Engine API** (`/question-engine`) — Adaptive question generation with nine cognitive function classes (Dec 5)

**Nine Question Classes (IES Question Engine expansion):**

Each class has distinct cognitive function and maps to specific AST thinking modes:

1. **Schema-Probe** — Surfaces hidden structure (lists, buckets, taxonomies)
   - Maps to: Discovery, Learning modes
   - Example: "What are the main categories here?", "What's the underlying structure?"

2. **Boundary** — Clarifies edges/limits to avoid scope creep
   - Maps to: Discovery, Articulating modes
   - Example: "What's NOT included?", "Where does this end?"

3. **Dimensional** — Introduces spectra/coordinates for precise positioning
   - Maps to: Discovery, Planning modes
   - Example: "On a spectrum from X to Y, where is this?", "What dimensions matter here?"

4. **Causal** — Pushes for mechanisms, prerequisites, sequences
   - Maps to: Dialogue, Learning modes
   - Example: "What causes this?", "What has to happen first?", "How does A lead to B?"

5. **Counterfactual** — "What if" deviations to expose assumptions
   - Maps to: Dialogue, Ideating modes
   - Example: "What if the opposite were true?", "Imagine this failed - why?"

6. **Anchor** — Grounds abstractions in concrete instances
   - Maps to: Dialogue, Reflecting modes
   - Example: "Can you give a specific example?", "When did you experience this?"

7. **Perspective-Shift** — Forces viewpoint changes (roles, time, system level)
   - Maps to: Flow, Ideating modes
   - Example: "How would X see this?", "Zoom out - what's the bigger picture?"

8. **Meta-Cognitive** — Checks thinking patterns directly
   - Maps to: AST, Reflecting modes
   - Example: "How confident are you?", "Where do you feel stuck?", "What's your energy level?"

9. **Reflective-Synthesis** — Integration statements tying threads together
   - Maps to: AST, Articulating modes
   - Example: "What's the main insight here?", "How do these pieces connect?"

**Endpoints:**
- `POST /question-engine/detect-state` - Detect user cognitive/emotional state (flowing, stuck, overwhelmed, exploring, etc.)
- `POST /question-engine/select-approach` - Select inquiry approach based on state (Socratic, Solution-Focused, Phenomenological, Systems, Metacognitive)
- `GET /question-engine/templates/{approach}` - Get question templates for specific approach
- `POST /question-engine/generate-questions` - Generate profile-adapted questions (orchestrates full pipeline)
- `GET /question-engine/question-classes` - List all 9 question classes with descriptions
- `GET /question-engine/approach-classes` - Show approach→class mappings

**APPROACH_TO_CLASSES Mapping:**
- **Socratic** → Schema-Probe, Boundary, Causal
- **Solution-Focused** → Anchor, Dimensional
- **Phenomenological** → Anchor, Meta-Cognitive
- **Systems** → Causal, Perspective-Shift, Dimensional
- **Metacognitive** → Meta-Cognitive, Reflective-Synthesis

**Implementation:**
- `ies/backend/src/ies_backend/api/question_engine.py` - FastAPI router with question class endpoints (400 lines)
  - Endpoints: detect-state, select-approach, templates/{approach}, generate-questions, approaches, categories, question-classes, approach-classes
  - Full pipeline orchestration with profile adaptation and question classification
- `ies/backend/src/ies_backend/schemas/question_engine.py` - QuestionClass enum, ClassifiedQuestion, APPROACH_TO_CLASSES, CLASS_TO_MODES mappings (251 lines)
  - Nine question classes with descriptions and mode mappings
  - APPROACH_TO_CLASSES: Maps inquiry approaches to question classes they generate
  - STATE_TO_APPROACHES: Maps user states to recommended inquiry approaches
- `ies/backend/src/ies_backend/services/state_detection_service.py` - State detection logic
- `ies/backend/src/ies_backend/services/approach_selection_service.py` - Approach selection logic
- `ies/backend/src/ies_backend/services/question_templates_service.py` - Template library

**ForgeMode Integration (SiYuan Plugin):**
- State detection: analyzes last 3 user messages → determines cognitive state
- Approach selection: maps thinking mode to inquiry approach with hints (learning→socratic, articulating→phenomenological, etc.)
- Question generation: generates 1 thinking partner question per AI response using detected state + selected approach
- Questions are classified with QuestionClass tags for Mode Transition Engine tracking
- Session documents record question classes used for pattern analysis

**Usage Flow:**
1. ForgeMode detects user state from recent messages
2. Selects inquiry approach based on state + thinking mode
3. Generates question using approach + context (topic, section, user/AI messages)
4. Question tagged with QuestionClass for mode transition decisions
5. Session document records question classes for analysis

---

**4. Concept API** (`/concepts`) — Knowledge graph formalization (completes virtuous cycle)

**Endpoints:**
- `POST /concepts` - Create new concept with relationships (returns `ConceptResponse`)
- `GET /concepts` - List concepts with optional search/filter (search, concept_type, limit params)
- `GET /concepts/{concept_name}` - Get concept details with relationships

**Concept Types:** `concept`, `theory`, `framework`, `mechanism`, `pattern`, `distinction`

**Relationship Types:** `supports`, `contradicts`, `component_of`, `operationalizes`, `develops`, `enables`, `contrasts_with`

**Features:**
- Neo4j persistence with automatic node label mapping (Concept/Theory/Framework)
- Relationship creation between concepts with evidence field
- Source tracking: links concepts back to session_id and source_quotes from thinking sessions
- Alias support for alternative concept names
- Duplicate detection prevents concept name collisions

**Implementation:**
- `ies/backend/src/ies_backend/api/concept.py` - FastAPI router (74 lines)
- `ies/backend/src/ies_backend/services/concept_service.py` - ConceptService with Neo4j integration (200+ lines)
- `ies/backend/src/ies_backend/schemas/concept.py` - CreateConceptRequest, ConceptResponse, ConceptType, RelationshipType enums
- Registered in `ies/backend/src/ies_backend/main.py` with `/concepts` prefix

**Frontend Integration:**
- SiYuan: `.worktrees/siyuan/ies/plugin/src/components/ConceptExtractor.svelte` - 4-step wizard for concept formalization
- ForgeMode: Integrated into session completion flow (Quick + Advanced buttons per entity)
- Dual save: Neo4j graph node + SiYuan document in `/Concepts/` folder

**Virtuous Cycle:**
1. Thinking session generates entities
2. User formalizes entities into concepts (with wizard)
3. Concepts saved to Neo4j with relationships
4. Next session can reference formalized concepts
5. Knowledge graph grows from thinking artifacts

---

**5. Entity Overlay API** (`/graph/entities/by-book`) — Real-time entity highlighting for reading interface

**Current Implementation:**
- `GET /graph/entities/by-book/{book_hash}` - Retrieve all entities mentioned in a specific book
- Query parameters: `title` (optional fallback), `types` (optional filter), `limit` (default 500, max 1000)
- Matching strategy: Primary by `hash` property, fallback to title substring match
- **Fixed:** Query pattern now uses direct Book-MENTIONS->Entity relationships (aligned with ingestion pipeline)

**Migration to Calibre Integration (Dec 4):**
- **New endpoint:** `GET /graph/entities/by-calibre-id/{calibre_id}` - Direct lookup by Calibre book ID
- Eliminates hash/title matching fragility by using Calibre as single source of truth
- See Calibre Integration section below for complete architecture

**Response Format:**
```json
{
  "book_hash": "string",
  "entities": [
    {
      "name": "Executive Function",
      "type": "Concept",
      "mention_count": 142
    }
  ],
  "total": 500
}
```

**Implementation:**
- `ies/backend/src/ies_backend/api/book_entities.py` - FastAPI router (51 lines) with title query parameter
- `ies/backend/src/ies_backend/services/graph_service.py` - `get_entities_by_book()` method with dual matching strategy (hash OR title)
- `ies/backend/tests/test_book_entities.py` - 3 unit tests (all passing)

**Frontend Integration (Readest):**
- `.worktrees/readest/readest/apps/readest-app/src/services/transformers/entity.ts` - HTML transformer wraps entity names in styled `<span>` elements
- `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/EntityTypeFilter.tsx` - Enhanced pill-based UI component (122 lines, Dec 4 redesign)
  - **Master toggle:** ON/OFF button with eye icons (LuEye/LuEyeOff) replacing checkbox
  - **Pill controls:** Interactive type-specific pills replace traditional checkboxes (5 types: Concept, Person, Theory, Framework, Assessment)
  - **Visual feedback:** Active pills show type-specific colors with 12% opacity backgrounds, inactive pills are muted
  - **Status indicator:** Centered display shows entity count, loading spinner, error message, or "Book not indexed" warning
  - **Disabled state:** Pills are disabled when overlay is off, preventing interaction confusion
  - **CSS integration:** Uses `.entity-type-pill` classes with color variants (`.entity-type-concept`, `.entity-type-person`, etc.)
- `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/FlowPanel.tsx` - Main flow panel container with EntityTypeFilter integrated at top (lines 156-159)
  - EntityTypeFilter always visible above entity content for quick overlay control
  - Positioned before entity details section for immediate access
- `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/EntitySection.tsx` - Entity header card with type-specific badges (53 lines)
- `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/RelationshipsSection.tsx` - Grouped relationship display with type badges (104 lines)
- `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/SourcesSection.tsx` - Source book links with chapter and page info (65 lines)
- `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/QuestionsSection.tsx` - Expandable thinking partner questions with type labels (136 lines)
- `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/Header.tsx` - Flow panel header with pin/close controls (58 lines)
- `.worktrees/readest/readest/apps/readest-app/src/store/flowModeStore.ts` - Comprehensive Zustand state management (380+ lines)
  - Entity overlay state: enabled, entities array, visible types, loading, error
  - Actions: setEntityOverlayEnabled, toggleEntityType, setVisibleTypes
  - fetchEntitiesForBook() with dynamic API host resolution (localhost or network IP)
  - Journey tracking integration (breadcrumb journey with dwell time)
- `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/FoliateViewer.tsx` - Auto-fetches entities on book load, applies transformer
- `.worktrees/readest/readest/apps/readest-app/src/styles/globals.css` - Complete entity overlay styling system (lines 559-618, 756-855)
  - **Filter controls:** `.entity-filter-container`, `.flow-master-toggle` for overlay UI
  - **Type pills:** `.entity-type-pill` base class with `:hover`, `.active`, `.disabled` states
  - **Type-specific colors:** Blue (Concept), Green (Person), Purple (Theory), Orange (Framework), Red (Assessment)
  - **Inline highlights:** `.entity-concept`, `.entity-person`, `.entity-theory`, `.entity-framework`, `.entity-assessment` for text overlay
  - **Hover effects:** Underline decoration appears on hover, type-specific color changes

**Network Access Support:**
- `fetchEntitiesForBook()` dynamically determines API host based on `window.location.hostname`
- When accessed via network IP (e.g., `192.168.86.60:3002`), uses same hostname for backend API (`192.168.86.60:8081`)
- Localhost access continues to use `localhost:8081` for API calls
- Enables entity overlay when accessing Readest from other devices on the network (e.g., iPad)

**Usage Flow:**
1. Book loads in Readest reader
2. FoliateViewer fetches entities from backend using `book_hash` and `title` (dual identifier strategy)
3. flowModeStore resolves API host dynamically (localhost or network IP)
4. Backend attempts hash match first, falls back to title-based matching if needed
5. Entity transformer processes HTML content, wrapping entity names in styled spans
6. User toggles overlay on/off and filters visible entity types via EntityTypeFilter component
7. Entities highlighted inline in text according to type (color-coded)

---

### Calibre Integration: Single Source of Truth (Phase 2 Backend Complete - Dec 4)

**Problem Solved:** Books exist with different identifiers (Calibre integer ID, Neo4j file path, Readest UUID), causing entity overlay failures when identifiers don't match.

**Solution:** Calibre library as canonical book source with `calibre_id` as universal identifier across all systems.

**Architecture:**

```
Calibre (Source of Truth)
├── metadata.db (SQLite catalog) - 179 books
└── Author/Book folders (epub/pdf files)
         │
         ├─→ Ingestion Pipeline → Neo4j (Book nodes with calibre_id) [Phase 3]
         ├─→ IES Backend → Book catalog API + entity lookup by calibre_id [COMPLETE]
         └─→ Readest → Browse books, open files, entity overlay [Phase 4]
```

**Docker Service (Already Running):**
- Container: `calibre-web-automated` (Up 23+ hours)
- Port: 8083 (web UI)
- Library: `/home/chris/Documents/calibre` (179 books)
- Ingest: `/home/chris/Documents/ingest`

**Backend APIs (PHASE 2 COMPLETE - Dec 4, Commit 9542ec2):**

**5. Books API** (`/books`) — Calibre library catalog access

**Endpoints:**
- `GET /books` - List all books from Calibre (default limit 100, max 500)
- `GET /books?search=ADHD` - Search books by title/author
- `GET /books/{calibre_id}` - Get single book by Calibre ID
- `GET /books/{calibre_id}/cover` - Fetch book cover image (JPEG)
- `HEAD /books/{calibre_id}/file` - Get file metadata (size, type) without body for size checking
- `GET /books/{calibre_id}/file` - Serve book file (epub or pdf) for web browser access
- `GET /graph/entities/by-calibre-id/{calibre_id}` - Entity lookup by Calibre ID (new endpoint in book_entities.py)

**Implementation:**
- `ies/backend/src/ies_backend/services/calibre_service.py` - CalibreService queries metadata.db (128 lines)
  - `list_books(search, limit)` - Query books table with optional title/author search
  - `get_book(calibre_id)` - Fetch single book by ID
  - `get_cover_path(calibre_id)` - Locate cover.jpg in book folder
  - `get_book_file_path(calibre_id)` - Locate epub/pdf file in book folder (prefers epub)
- `ies/backend/src/ies_backend/api/books.py` - FastAPI router (125 lines)
  - Library path: `/home/chris/Documents/calibre` (hardcoded, TODO: environment variable)
  - HEAD endpoint returns Content-Length, Content-Type, Content-Disposition headers for file metadata
  - GET endpoint serves files with proper media types (application/epub+zip or application/pdf)
  - All endpoints properly handle 404s for missing books/covers/files
- `ies/backend/src/ies_backend/schemas/calibre.py` - Book schema (Pydantic, 13 lines)
- `ies/backend/src/ies_backend/services/graph_service.py` - Added `get_entities_by_calibre_id()` method (47 lines)
  - Queries Neo4j: `MATCH (b:Book) WHERE b.calibre_id = $calibre_id`
  - Returns entities with mention counts sorted by frequency
- `ies/backend/src/ies_backend/api/book_entities.py` - Added `/entities/by-calibre-id/{calibre_id}` endpoint (20 lines)
  - Returns `CalibreEntitiesResponse` with calibre_id, entities list, total count
- `ies/backend/tests/test_calibre_service.py` - 6 unit tests (mocked SQLite)
- `ies/backend/tests/test_books_api.py` - 6 unit tests (mocked service)
- `ies/backend/tests/test_book_entities.py` - 3 new tests for calibre_id endpoint
- Tests: 85/85 passing (15 new Calibre-related tests)

**Schema:**
```python
class Book(BaseModel):
    calibre_id: int
    title: str
    author: str
    path: str
```

**Migration Script (Ready to Run):**
- `scripts/match_calibre_ids.py` — One-time migration to add `calibre_id` to existing Neo4j Book nodes (167 lines)
- **Matching Strategy:**
  - Normalizes titles (removes subtitles, punctuation, lowercase)
  - Calculates string similarity (SequenceMatcher 0-1 score)
  - Boosts score +0.1 if author names overlap
  - Auto-matches if score >= 0.7 (configurable `MATCH_THRESHOLD`)
- **Process:**
  1. Load all books from Calibre `metadata.db`
  2. Load all Book nodes from Neo4j
  3. Find best match for each Neo4j book using similarity scoring
  4. Display matched pairs with scores for review
  5. Prompt for confirmation before updating
  6. Execute Cypher: `MATCH (b:Book) WHERE elementId(b) = $id SET b.calibre_id = $calibre_id`
- **Usage:** `python scripts/match_calibre_ids.py` (interactive, requires confirmation)

**Multi-Pass Ingestion Pipeline (Phase 3 - COMPLETE):**

**Ingestion Script:** `scripts/ingest_calibre.py` (263 lines) — Extracts entities from Calibre books and stores in Neo4j

**Auto Ingestion Daemon:** `scripts/auto_ingest_daemon.py` (272 lines) — Continuous background processing with proper Book-Entity relationships

**Pass 1 (Structure) - IMPLEMENTED:**
- Create Book node with `calibre_id` as primary identifier
- Extract text and chunk (max 512 tokens, 50 token overlap)
- Extract entities via OpenAI (Concept, Person, Theory, Framework, Assessment)
- **FIXED (Dec 4):** Create MENTIONS relationships between Book and Entity nodes (lines 150-156)
- Status: `pending → chunked → entities_extracted`

**Pass 2 (Relationships) - FUTURE:**
- Extract causal relationships (CAUSES, ENABLES)
- Extract component relationships (PART_OF)
- Extract contrast relationships (CONTRASTS_WITH)
- Status: `entities_extracted → relationships_mapped`

**Pass 3 (Enrichment - LLM) - FUTURE:**
- Generate reframes via Reframe API
- Extract mechanisms and patterns
- Add rich descriptions
- Status: `relationships_mapped → enriched`

**CLI Usage:**
```bash
# Manual ingestion
python scripts/ingest_calibre.py               # Process all books
python scripts/ingest_calibre.py --id 42       # Process single book by calibre_id
python scripts/ingest_calibre.py --test        # Test with one book
python scripts/ingest_calibre.py --status      # Show processing stats
python scripts/ingest_calibre.py --limit 10    # Process 10 books

# Automated daemon (RECOMMENDED)
python scripts/auto_ingest_daemon.py &         # Background daemon (5-minute polls)
python scripts/auto_ingest_daemon.py --once    # Single batch run
python scripts/auto_ingest_daemon.py --batch-size 10  # Custom batch size

# Management utilities
python scripts/manage_ingestion.py start       # Start daemon + watcher
python scripts/manage_ingestion.py stop        # Stop all services
python scripts/manage_ingestion.py status      # Show running services
python scripts/check_ingestion.py              # View processing status table
python scripts/calibre_watcher.py &            # Watch for Calibre library changes
```

**Features:**
- Skips books already processed (checks `book_exists(calibre_id)`)
- Progress tracking with Rich console output
- Chunk limit (50 chunks per book to avoid excessive API calls)
- Stats tracking: sections extracted, chunks created, entities found, relationships added
- Status updates: `update_book_status(calibre_id, status)`
- **Auto daemon:** Continuous polling, background processing, comprehensive logging

**Management Scripts (Added Dec 4):**
- `scripts/manage_ingestion.py` — Start/stop/status for automated ingestion services (80 lines)
- `scripts/check_ingestion.py` — Display Rich table of book processing status with entity counts (80 lines)
- `scripts/calibre_watcher.py` — File system watcher for Calibre metadata.db and ingest directory changes (120 lines)

**Neo4j Schema (Updated):**
```cypher
(:Book {
  calibre_id: 42,              # Primary identifier (integer)
  title: "...",
  author: "...",
  path: "/calibre-library/Author/Title (42)/book.epub",
  processing_status: "entities_extracted",  # pending → chunked → entities_extracted
  has_entities: true
})
```

**KnowledgeGraph Client Updates:**
- `add_book(title, author, path, calibre_id, processing_status)` - Accepts `calibre_id` parameter
- `book_exists(calibre_id)` - Checks if book with `calibre_id` exists
- `update_book_status(calibre_id, status)` - Updates processing status

**Readest Integration (Phase 4 - COMPLETE - Dec 4, Commit 51b8ee3):**

**User Flow:**
- **Import Menu:** Import menu → "From Calibre Library" → Modal with searchable book grid → Click book → Opens in reader with entity overlay
- **Settings Menu:** Settings (gear icon) → "Calibre Library" → Modal with searchable book grid → Click book → Opens in reader with entity overlay

**UI Components (Implemented):**
- `.worktrees/readest/readest/apps/readest-app/src/app/library/components/CalibreDialog.tsx` — Main modal with book grid, search, filtering (238 lines)
  - Fetches full catalog on open (`GET /books?limit=500`)
  - Correctly parses API response: `setBooks(data.books || [])` (API returns `{ books: [...], total: N }`, not raw array)
  - Batched entity count fetching (10 books at a time to avoid API overload)
  - Client-side search filtering (catalog is ~179 books)
  - "Has entities only" checkbox filter
  - Opens book via backend URL (`/books/{calibre_id}/file`) enabling web browser access (no filesystem dependency)
- `.worktrees/readest/readest/apps/readest-app/src/app/library/components/CalibreBookCard.tsx` — Individual card with cover, title, author, entity badge (98 lines)
  - Cover image with loading spinner and error fallback
  - Entity badge: green dot + count (>= 0), or "Not indexed" (-1), or spinner (null)
  - Responsive design with hover states
- `.worktrees/readest/readest/apps/readest-app/src/app/library/components/CalibreSearchBar.tsx` — Search input + "Has entities only" filter (69 lines)
  - Debounced search (300ms)
  - Clear button when search active
  - Filter toggle with result count display

**Key Features:**
- Search books by title/author (debounced 300ms)
- "Has entities" filter shows only indexed books
- Entity badge: green dot + count, or gray "Not indexed"
- Responsive grid (4 cols desktop, 2 cols mobile)
- Click book → fetches file via backend API (`/books/{calibre_id}/file`) for web browser compatibility
- `calibre_id` stored in Readest Book object
- Entity overlay uses calibreId for reliable entity fetching
- Dynamic API host resolution (localhost or network IP, same as flowModeStore)
- Backend serves epub/pdf files with correct media types for browser download/viewing

**Modified Files:**
- `.worktrees/readest/readest/apps/readest-app/src/app/library/components/ImportMenu.tsx` — Added "From Calibre Library" menu item with IoLibrary icon (71 lines total)
- `.worktrees/readest/readest/apps/readest-app/src/app/library/components/SettingsMenu.tsx` — Added "Calibre Library" menu item and `onOpenCalibreLibrary` callback handler (200+ lines total)
- `.worktrees/readest/readest/apps/readest-app/src/app/library/components/LibraryHeader.tsx` — Wired up `onOpenCalibreLibrary` callback to SettingsMenu (100+ lines total)
- `.worktrees/readest/readest/apps/readest-app/src/app/library/page.tsx` — Added `showCalibreDialog` state and CalibreDialog render (500+ lines total)
- `.worktrees/readest/readest/apps/readest-app/src/types/book.ts` — Added `calibreId?: number` to Book interface (46 lines total)
- `.worktrees/readest/readest/apps/readest-app/src/store/flowModeStore.ts` — Updated `fetchEntitiesForBook()` to use calibreId parameter for entity lookup (380+ lines total)

**Implementation Phases:**
- **Phase 1:** Docker infrastructure + Calibre service setup ✅ (already running)
- **Phase 2:** Backend APIs (`/books`, `/books/{id}/cover`, `/books/{id}/file`, calibre_id entity endpoint) ✅ COMPLETE
- **Phase 3:** Ingestion pipeline (Pass 1: entity extraction) ✅ COMPLETE
- **Phase 4:** Readest Library view + calibre_id integration + web browser book access ✅ COMPLETE (Dec 4, Commit 51b8ee3)
- **Phase 5:** Enrichment passes (Pass 2: relationships, Pass 3: reframes) — NOT STARTED

**Design Documents:**
- `docs/plans/2025-12-04-calibre-integration-design.md` — Overall architecture
- `docs/plans/2025-12-04-readest-calibre-library-view.md` — Phase 4 UI design and implementation plan (Dec 4)

**Related:**
- Reframe API (Phase 2c) will be used by Pass 3 enrichment
- Ingestion pipeline integrates with existing `library/graph/entities.py` extraction logic
- Serena memory: `calibre-integration-design-dec4.md`

<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: conventions -->
<!-- This section will be automatically updated by auto-memory plugin -->
<!-- END AUTO-MANAGED -->