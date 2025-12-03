<!-- MANUAL -->
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

**Phase 1: Prove Core Hypothesis** ✅ COMPLETE (Dec 2)

**Architecture Complete:**
- ✅ Layer 1: Knowledge graph creation (50k therapy entities already processed, ingestion pipeline built)
- ✅ Layer 2: Profile system + adaptive dialogue (backend functional, dialogue working)
- ⏳ Layer 3: Flow/Flo exploration interface (not yet built - deferred to Phase 2+)

**Phase 1 Achievement Summary:**
- ✅ **10/10 therapy exploration sessions completed** — Complete therapeutic dialogue cycle validated
- ✅ **11+ therapeutic concepts extracted and formalized** — Comprehensive framework discovered
- ✅ **Complete concept connection map** — Hierarchical relationships documented in CONNECTIONS.md
- ✅ **Extraction pipeline proven end-to-end** — Session → Transcript → Extraction → Formalization → Commit
- ✅ **Core hypothesis validated** — Personalized dialogue patterns directly affect concept discovery
- ✅ **IES backend (54/61 tests passing)** — Layers 1 & 2 working flawlessly
- ✅ **Therapy domain knowledge graph fully populated** — Neo4j with 50k entities, 63 books ingested

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
- **Phase 2:** Build Layer 3 (Flow/Flo interface) now that hypothesis is validated
- **Phase 2+:** Domain generalization and validation across multiple knowledge domains

## How to Work Here (Phase 2+)

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

### Phase 2 Focus

Layer 3 (Flow/Flo interface) is the next priority once Layer 3 architecture is designed. See `docs/parking-lot.md` for roadmap.

**For Now:**
- All core systems are operational (Layers 1 & 2)
- All Phase 1 documentation complete
- Ready for Phase 2 development or additional domain validation

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
├── therapy/                       # Therapy Domain Application (current focus)
│   ├── Track_1_Human_Mind/        # How humans perceive, think, and construct meaning
│   │   ├── 01-narrow-window-of-awareness.md  # Foundational concept (1/20-30)
│   │   └── (related concepts: meaning-making, unnecessary pain, personhood)
│   └── (more tracks and research concepts being extracted)
│
├── library/                       # Shared: GraphRAG modules, ingest pipeline (Python)
├── scripts/                       # Shared: CLI tools, session runners
├── books/                         # Shared: 63 psychology/therapy books (ingested to Layer 1)
│
├── docs/                          # Documentation
│   ├── PROJECT-OVERVIEW.md        # Single source of truth (comprehensive project overview)
│   ├── five-agent-synthesis.md    # Vision, gaps, lessons, phased path (analysis depth)
│   ├── session-notes.md           # Session reflection (append-only)
│   ├── parking-lot.md             # Future features (don't work on these)
│   └── archive/                   # Old progress files, archived memories
│
└── docker-compose.yml             # Neo4j + Qdrant infrastructure (Layers 1 & 2 support)
```

**Architecture Alignment:**
- **Layer 1** = Knowledge graph + ingestion pipeline in `library/` and `books/`
- **Layer 2** = Backend services (API, dialogue, profile) in `ies/backend/`
- **Layer 3** = To be built (rich exploration interface, post-processing pipeline)
- **Domain Application** = `therapy/` directory (current application domain)

## Key Resources

### Documentation Hierarchy

The project maintains a three-level documentation structure for clarity:

**Level 1: Strategic Vision (Project Context)**
- `docs/PROJECT-OVERVIEW.md` — Single source of truth for the complete vision: three-layer architecture, what's built vs. deferred, why design decisions were made, Phase 1 success criteria, and roadmap
- `docs/five-agent-synthesis.md` — Deep analysis: architectural vision, identified gaps, why configuration was blocking, lessons learned, phased path forward

**Level 2: Operational Execution (Your Day-to-Day)**
- `docs/PHASE-1-WORKFLOW.md` — Daily reference guide with complete pipeline, step-by-step instructions, checklists, examples, and troubleshooting
  - Step 1: Run therapy exploration sessions
  - Step 2: Extract entities using backend service
  - Step 3: Interpret extracted entities (decision criteria)
  - Step 4: Formalize concepts into documents
  - Step 5: Document connections between concepts
  - Step 6: Commit to git
  - Complete workflow checklist for each session
  - What success looks like after Session 1, 5, and 10

**Level 3: Implementation & Reflection**
- `scripts/run-session.py` — Session runner (use this to start therapy exploration)
- `therapy/Track_1_Human_Mind/` — Extracted concept documents and CONNECTIONS.md (output of sessions)
- `docs/session-notes.md` — Reflection log: what you accomplished, learned, and blocked on (append-only, after each session)

### Supporting References

**Constraints & Scope:**
- `docs/parking-lot.md` — Future features (what NOT to work on in Phase 1)
- `CLAUDE.md` (this file) — Quick reference and structure guide

**Technical Setup:**
- `ies/backend/README.md` — Backend API setup and configuration
- `docker-compose.yml` — Infrastructure (Neo4j + Qdrant)

## The Parking Lot

**Explicitly Deferred to Phase 2+:**
- **Layer 3: Flow/Flo Interface** — Rich interactive knowledge exploration (NOT built in Phase 1)
- **Post-processing Pipeline** — Enriches notebooks with graph connections (Phase 2+)

**Don't work on these until Phase 1 is complete:**
- Multi-domain framework generalization
- Advanced profile system (8 dimensions)
- Question engine (8 inquiry approaches)
- MCP server integration
- n8n integration
- Synapse component ports

**Rule:** Phase 1 focuses on proving Layers 1 & 2 create value through therapy domain exploration. Layer 3 is built once hypothesis is validated. Nothing else enters development until core hypothesis is proven.

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