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

**Phase 1: Prove Core Hypothesis** 🚀 IN PROGRESS (Dec 2)

**Architecture Complete:**
- ✅ Layer 1: Knowledge graph creation (50k therapy entities already processed, ingestion pipeline built)
- ✅ Layer 2: Profile system + adaptive dialogue (backend functional, dialogue working)
- ⏳ Layer 3: Flow/Flo exploration interface (not yet built - deferred to Phase 2+)

**What's Working (Verified Today):**
- ✅ IES backend running on :8081 (54/61 tests passing)
- ✅ Therapy domain knowledge graph fully populated (Neo4j with 50k entities)
- ✅ Adaptive dialogue system functional (Layer 2)
- ✅ Profile system capturing user's thinking patterns and state
- ✅ SiYuan plugin builds and connects to backend
- ✅ First therapy session completed successfully
- ✅ First therapeutic concept extracted and documented

**Current Phase 1 Focus:**
Run therapy exploration sessions (Layers 1 & 2) where personalized dialogue guides thinking, extraction of therapeutic concepts from that thinking happens, and concepts are formalized. Follow the complete pipeline in `docs/PHASE-1-WORKFLOW.md`:
1. Run session with `python scripts/run-session.py --topic "..."`
2. Extract entities from transcript via backend API
3. Formalize solid/developing concepts into concept documents
4. Document connections in CONNECTIONS.md
5. Commit frequently

**Complete workflow with checklists:** See `docs/PHASE-1-WORKFLOW.md` (your day-to-day reference)

**Phase 1 Success Criteria:**
- 10 documented therapy exploration sessions (1/10 complete)
- 20-30 therapeutic concepts extracted from those sessions and formalized (1/20 complete)
- Evidence that personalized dialogue patterns affect what concepts are discovered
- Clear documentation of the extraction → formalization pipeline
- Validation that concept generation through thinking partnership creates novel, valuable insights
- Proof that system approach works before Layer 3 investment

**Roadmap:**
- **Phase 0 (COMPLETE):** Configuration stabilization removed 40% meta-work overhead
- **Phase 1 (RUNNING):** Prove core hypothesis works with Layers 1 & 2 in therapy domain (7-10 days)
- **Phase 2:** Build Layer 3 (Flow/Flo interface) once hypothesis is proven
- **Phase 2+:** Domain generalization and additional capabilities based on learning

## How to Work Here (Phase 1)

### Before Starting a Therapy Exploration Session

1. Read `docs/PHASE-1-WORKFLOW.md` (10 min) - complete checklist and pipeline reference
2. Check `docs/PROJECT-OVERVIEW.md` for overall vision and architecture context
3. Verify backend is healthy: `curl http://localhost:8081/health`
4. Verify Docker services running: `docker compose ps`
5. Have a genuine therapeutic question ready to explore

### During Your Session

**Follow the complete pipeline in `docs/PHASE-1-WORKFLOW.md`:**
1. Run therapy exploration: `python scripts/run-session.py --topic "Your question"`
2. Engage authentically (5-10 exchanges, 20-30 minutes typical)
3. Type "done" when complete; transcript auto-saves
4. Extract entities from transcript using backend API
5. Review extracted entities and decide which to formalize
6. Create concept documents for solid/developing concepts
7. Update CONNECTIONS.md to document relationships
8. Commit: `git add ... && git commit -m "docs: session N - extracted concepts..."`

### After Your Session

1. Update progress tracking in session notes (X/10 sessions, Y/20-30 concepts)
2. Run: `git status` (verify everything is committed)
3. Append entry to `docs/session-notes.md` with:
   - What you accomplished (sessions run, concepts extracted)
   - What you learned (insights, thinking patterns)
   - Blockers you hit
   - What next session should focus on
   - How your thinking patterns influenced discoveries

**Workflow Note:** `docs/PHASE-1-WORKFLOW.md` is your day-to-day operational guide. Git history tracks code changes. Session notes track reflection and learning. Together they create complete project memory.

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

**Primary References (Start Here):**
- `docs/PHASE-1-WORKFLOW.md` — Complete operational guide: session pipeline, extraction, formalization, connections, troubleshooting. DAY-TO-DAY REFERENCE.
- `docs/PROJECT-OVERVIEW.md` — Complete project overview: vision, architecture, what's built, Phase 1 plan. Single source of truth.

**For Phase 1 Execution (Right Now):**
- `docs/PHASE-1-WORKFLOW.md` — Complete pipeline with checklists and examples (session → extraction → formalization → connections → git)
  - Step 1: Run therapy exploration sessions
  - Step 2: Extract entities using backend service
  - Step 3: Interpret extracted entities (decision criteria)
  - Step 4: Formalize concepts into documents
  - Step 5: Document connections between concepts
  - Step 6: Commit to git
  - Includes complete workflow checklist for each session
- `scripts/run-session.py` — Session runner script (use to quickly start therapy sessions)
- `therapy/Track_1_Human_Mind/` — Concept documents and CONNECTIONS.md
- `docs/session-notes.md` — Reflection log (append-only, after each session)

**For Deep Understanding:**
- `docs/five-agent-synthesis.md` — Comprehensive analysis with vision, gaps, configuration problems, phased path

**Reference & Constraints:**
- `docs/parking-lot.md` — Future features (what NOT to work on yet)
- `CLAUDE.md` (this file) — Quick reference guide

**Technical:**
- `ies/backend/README.md` — Backend setup and API
- `docker-compose.yml` — Infrastructure setup

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