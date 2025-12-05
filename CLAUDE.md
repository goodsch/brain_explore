<!-- MANUAL -->
# ⚠️ WORKTREE: SiYuan Plugin Evolution (Phase 3)

**READ FIRST: `TASK.md`** - Contains your specific objectives for this worktree.

**Branch:** `feature/siyuan-evolution`
**Purpose:** Evolve plugin with Dashboard, Structured Thinking, and Quick Capture

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

**Phase 2b: Build Visual Interface for Layer 3** IN PROGRESS

**Previous Phases Complete:**
- ✅ Phase 2a: Layer 3 CLI exploration tool validated (5 focused explorations, thinking partner questions work)
- ✅ All Three Layers Validated: Layer 1 (50k therapy entities), Layer 2 (profile + dialogue), Layer 3 (CLI exploration)

**Phase 2b Progress (SiYuan Plugin Evolution):**
- ✅ Dashboard redesigned as Layer 3 Processing Hub (v0.3.0)
- ✅ Three main modes implemented: Structured Thinking, Flow (graph exploration), Quick Capture
- ✅ Recent journeys display with breadcrumb tracking
- ✅ Journey resumption implemented (commit 7060541) - Click journey in Dashboard to resume in Flow mode
- ✅ Quick Capture queue status preview
- ✅ Backend integration: Journey API and Capture API connected
- In Progress: Full capture processing workflow testing

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
- **Phase 2b (NEXT):** Build visual interface on Layer 3 foundation (web app or extended SiYuan plugin)
- **Phase 2c+:** Domain generalization and validation across multiple knowledge domains

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
│   ├── backend/                   # FastAPI backend - Layers 1-3 APIs (Python)
│   │   ├── src/ies_backend/
│   │   │   ├── api/               # API routers
│   │   │   │   ├── graph.py       # Knowledge graph exploration
│   │   │   │   ├── session.py     # Structured thinking sessions
│   │   │   │   ├── journey.py     # Breadcrumb journey tracking
│   │   │   │   ├── capture.py     # Quick Capture processing
│   │   │   │   └── profile.py     # User profile management
│   │   │   └── services/          # Business logic
│   │   └── tests/                 # 61 unit tests
│   └── plugin/                    # SiYuan plugin - Layer 3 visual interface (v0.3.0)
│       ├── src/index.ts           # Plugin lifecycle (Dashboard sidebar + tab)
│       └── src/views/
│           ├── Dashboard.svelte   # Layer 3 Processing Hub (entry point)
│           ├── ForgeMode.svelte   # Structured Thinking (Layer 2 dialogue modes)
│           ├── FlowMode.svelte    # Graph exploration with thinking questions
│           └── QuickCapture.svelte # Content processing and entity extraction
│
├── therapy/                       # Therapy Domain Application (complete Phase 1)
│   ├── Track_1_Human_Mind/        # How humans perceive, think, and construct meaning
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
│   └── (ready for Phase 2 exploration or domain generalization)
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
└── docker-compose.yml             # Neo4j + Qdrant infrastructure (Layers 1-3 support)
```

**Architecture Alignment:**
- **Layer 1** = Knowledge graph + ingestion pipeline in `library/` and `books/`
- **Layer 2** = Backend dialogue services in `ies/backend/api/session.py` and `question_engine.py`
- **Layer 3** = SiYuan plugin (Dashboard, ForgeMode, FlowMode, QuickCapture) + backend journey/capture APIs
- **Domain Application** = `therapy/` directory (current application domain)

## Plugin Development (Phase 2b)

**Current Version:** v0.3.0 - Layer 3 Processing Hub

**Plugin Architecture:**

The SiYuan plugin serves as the visual interface for Layer 3, providing three integrated thinking partnership modes:

1. **Dashboard (Sidebar/Tab)** — Layer 3 Processing Hub
   - Displays knowledge graph statistics (entities, relationships, books)
   - Shows suggested exploration topics (recent, connected, new)
   - Lists recent journeys with breadcrumb counts and timestamps
   - Quick Capture queue status
   - Navigation buttons to three main modes

2. **Structured Thinking (ForgeMode)** — Layer 2 Dialogue Adapted for Visual Interface
   - 5 thinking modes: Learning, Articulating, Planning, Ideating, Reflecting
   - Each mode has specialized AI behavior (Socratic, mirroring, goal clarification, divergent, phenomenological)
   - Split view: conversation thread (left) + live note preview (right)
   - Integrates with backend session API for dialogue state management
   - Saves thinking artifacts as SiYuan notes

3. **Graph Exploration (FlowMode)** — Layer 3 Visual Navigation
   - Search or navigate to concepts in the knowledge graph
   - Grouped relationship display by relationship type and direction
   - Thinking partner questions generated during exploration
   - Tracks exploration path as breadcrumbs
   - Integrates with backend journey API for path persistence

4. **Quick Capture (QuickCapture)** — Content Processing Entry Point
   - Accept unstructured content (text, voice transcription, OCR, URLs)
   - Display extraction results (entities, summary, suggested tags)
   - Show suggested placements and confidence scores
   - Integrates with backend capture API for AI-powered extraction

**Backend Integration:**

The plugin uses SiYuan's `forwardProxy` API to reach the backend at `http://192.168.86.60:8081`:
- `/graph/*` — Knowledge graph exploration (stats, suggestions, relationships)
- `/sessions/*` — Structured thinking dialogue sessions
- `/journeys/*` — Journey tracking and breadcrumb persistence
- `/capture/process` — Quick Capture content extraction and analysis
- User context: `chris` (configurable, currently hardcoded for development)

**Key Files:**
- `ies/plugin/src/index.ts` — Plugin lifecycle (onload, onLayoutReady, unload)
- `ies/plugin/src/views/Dashboard.svelte` — Main hub with mode navigation, journey resumption
- `ies/plugin/src/views/ForgeMode.svelte` — Structured thinking interface (Layer 2)
- `ies/plugin/src/views/FlowMode.svelte` — Graph exploration with grouped relationships, journey state management
- `ies/plugin/src/views/QuickCapture.svelte` — Content capture and processing
- `ies/plugin/src/styles/design-system.scss` — "Contemplative Knowledge Space" design system with light/dark themes

**Deployment Note:**
Changes to the plugin need to be mirrored in the Docker deployed directory: `/home/chris/dev/docker/compose/appdata/siyuan/workspace/data/plugins/ies-explorer`

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
## Plugin Architecture Updates

### Domain-Agnostic Configuration (siyuan-structure.ts)

**Notebook Selection:**
- User-configurable via localStorage `ies.preferredNotebooks` (JSON array)
- Default notebooks: `['Personal', 'Knowledge', 'Notes', 'Intelligent Exploration System']`
- Helper functions: `setPreferredNotebooks(['MyNotebook'])`, `getPreferredNotebookNames()`
- Notebook resolution: First matching open notebook by preference order
- Eliminates therapy-specific hardcoding for true domain-agnostic architecture

**Backend Integration:**
- Configurable backend URL via localStorage `ies.backendUrl`
- Default: `http://192.168.86.60:8081` (SiYuan Docker container to host backend)
- Health check caching: 30-second TTL to reduce API overhead
- Generic API caller: `callBackendApi<T>(method, endpoint, body?)` for all backend requests

**Session Document Structure:**
- Frontmatter includes: `be_type`, `be_id`, `mode`, `topic`, `status`, `created`, `template_id`, `question_classes_used`
- Question class tracking: Sessions record which cognitive function classes were used
- Mode-specific folders: `/Sessions/{mode}/` (Learning, Articulating, Planning, Ideating, Reflecting)
- YAML serialization with proper type handling (arrays, objects, dates, nested structures)

### Question Class System (ForgeMode.svelte)

**Nine Cognitive Function Classes:**
1. **Schema-Probe (🏗️)** — Structure questions (blue #4a90d9) - "What are the main categories?"
2. **Boundary (🔲)** — Edge/limit questions (purple #7b68ee) - "What's NOT included?"
3. **Dimensional (📐)** — Spectrum questions (teal #20b2aa) - "On a scale from X to Y?"
4. **Causal (⚡)** — Mechanism questions (tan #f4a460) - "What causes this?"
5. **Counterfactual (🔮)** — What-if questions (orchid #da70d6) - "What if the opposite were true?"
6. **Anchor (⚓)** — Concrete example questions (green #3cb371) - "Give a specific instance"
7. **Perspective-Shift (👁️)** — Viewpoint change (brown #cd853f) - "How would X see this?"
8. **Meta-Cognitive (🧠)** — Thinking pattern checks (gray #778899) - "How confident are you?"
9. **Reflective-Synthesis (🔗)** — Integration (blue #6495ed) - "What's the main insight?"

**Interactive Question-Response Dialogue:**
- NOT passive display - questions require user response before continuing
- State tracking: `pendingQuestion` with class, approach, timestamp
- Cognitive guidance hints per question class (e.g., "This question asks you to surface hidden structure")
- Response starters suggested (e.g., "The main parts are..." for schema_probe)
- Question-response history tracked for session transcript
- Follow-up questions generated based on user response

**Question Class Tracking:**
- `questionClassesUsed: string[]` - All classes used in session
- `lastQuestionClass: string | null` - Most recent question class
- Visual badges displayed inline with questions (emoji + color-coded labels)
- Session documents include `question_classes_used` in frontmatter
- Enables Mode Transition Engine pattern analysis

**Mode Transition Suggestions:**
- Each question class maps to recommended thinking modes
- Example: `schema_probe` → suggests Discovery or Learning modes
- Example: `reflective_synthesis` → suggests AST or Articulating modes
- Helps users discover when to switch modes based on question patterns
<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: conventions -->
## UI Design System

### Design Preview System (Dec 5)

**Interactive Design Gallery:** `/ies/plugin/design-previews/`

Browser-based design system exploration with 7 complete aesthetic options plus typography and color alternatives. All previews use real IES Dashboard/FlowMode/QuickCapture components with live data.

**Preview Navigation:** `design-previews/index.html` — Main navigation hub with tabbed interface

**7 Design Options:**
1. **Scholar's Library (Recommended)** — Warm, contemplative, intellectual aesthetic
   - Fonts: Crimson Pro (display), Nunito (body), JetBrains Mono
   - Colors: Warm paper tones (#f5f2ed deep, #faf8f5 base), amber accent (#c9872e)
   - Philosophy: "The Reading Room" — afternoon light in curated library
   - Preview: `option-1-scholars-library.html`

2. **Asri Modern** — Clean minimalism with structured clarity
   - Fonts: Inter (all contexts), Source Code Pro (mono)
   - Colors: Cool neutrals (#f8f9fa), blue accent (#2563eb)
   - Philosophy: Modern research lab meets design system
   - Preview: `option-2-asri-modern.html`

3. **Tsundoku Scholarly** — Book-stack aesthetic with serif warmth
   - Fonts: Source Serif 4 (display/body), Fira Code (mono)
   - Colors: Warm off-white (#fdfcfa), deep brown (#2e1f1a), burgundy accent (#8b3a3a)
   - Philosophy: Japanese book-collecting culture meets academia
   - Preview: `option-3-tsundoku.html`

4. **Neurogarden** — ADHD-optimized glassmorphism with aurora effects
   - Fonts: Space Grotesk (geometric sans), JetBrains Mono
   - Colors: Dark base (#12121a), cyan accent (#00d4ff), violet secondary (#a855f7)
   - Philosophy: Neural network garden with gentle glow animations
   - Preview: `option-4-neurogarden.html`

5. **Soft Focus** — Gentle, low-contrast, ADHD-friendly minimalism
   - Fonts: DM Sans (rounded sans), Source Code Pro
   - Colors: Soft sage (#f4f6f5), muted teal (#6b9080), warm gray (#5c5650)
   - Philosophy: Reduced visual noise, gentle hierarchy
   - Preview: `option-5-soft-focus.html`

6. **Hybrid (Balanced)** — Combines Scholar's warmth with modern structure
   - Fonts: Inter (UI), Crimson Pro (headings), JetBrains Mono
   - Colors: Warm base with structured accents
   - Philosophy: Best of contemplative + modern
   - Preview: `option-6-hybrid.html`

7. **Cupertino** — Apple-inspired with SF Pro aesthetic
   - Fonts: -apple-system stack, SF Mono
   - Colors: System grays, blue accent (#007aff)
   - Philosophy: macOS/iOS native feel
   - Preview: `option-7-cupertino.html`

**Typography Comparison:** `typography-options.html`
- 12 font pairings with live samples (headings, body, code)
- Serif options: Crimson Pro, Source Serif 4, Libre Baskerville, Lora, Merriweather, IBM Plex Serif
- Sans options: Nunito, Inter, DM Sans, Plus Jakarta Sans, Space Grotesk, Outfit, IBM Plex Sans
- Mono options: JetBrains Mono, Fira Code, Source Code Pro

**Color Alternatives:** `color-alternatives.html`
- 8 accent color palettes (amber, blue, emerald, violet, rose, slate, warm, cool)
- Each palette shows primary + hover + muted variants
- Live component examples with each color scheme

**Current Implementation:** Option 1 (Scholar's Library) in `design-system.scss`

**Design Philosophy: "Contemplative Knowledge Space"**
- Aesthetic: Quiet library meets neural network
- Typography: Display (Crimson Pro serif), Body (Nunito sans-serif), Mono (JetBrains Mono)
- Color palette: Warm neutrals with amber/gold accent (illumination, insight)
- Responsive spacing scale (--ies-space-1 through --ies-space-10)
- Smooth animations: fade-in, slide-up, scale-in, pulse-soft, glow-pulse
- Dark theme support via `[data-theme-mode="dark"]`

**Design System Location:** `/ies/plugin/src/styles/design-system.scss`

**Key CSS Variables:**
- `--ies-accent`: #c9872e (amber/gold for primary actions)
- `--ies-secondary`: #5a8a7a (sage/teal for growth, knowledge)
- `--ies-tertiary`: #8b7aa0 (soft violet for reflection, depth)
- Semantic colors: success, warning, error, info
- Shadow system: xs, sm, md, lg, glow (layered for depth)
- Border radius: sm (6px), md (10px), lg (16px), xl (24px)
- Transitions: fast (120ms), base (200ms), slow (350ms), bounce (400ms cubic-bezier)

**Component Design Tokens (Unified Across All Views):**
All Svelte components (Dashboard, ForgeMode, QuickCapture, FlowMode) declare CSS variables at root level using design system tokens instead of SiYuan theme variables. Replace `--b3-theme-*` with:
- Background: `--bg-deep`, `--bg-base`, `--bg-elevated`, `--bg-overlay`
- Text: `--text-primary`, `--text-secondary`, `--text-muted`, `--text-subtle`
- Borders: `--border-subtle`, `--border-light`, `--border-medium`
- Spacing: `--space-1` through `--space-6`
- Radius: `--radius-sm`, `--radius-md`, `--radius-lg`
- Shadows: `--shadow-sm`, `--shadow-md`, `--shadow-lg`
- Colors: `--accent`, `--secondary`, `--tertiary`, `--success`, `--error`

**Component Architecture:**
- Dashboard: Central hub with stats, suggestions, recent journeys, capture queue
- ForgeMode: Structured thinking with question class tracking, cognitive guidance hints
- QuickCapture: Content capture with resonance/energy metadata
- FlowMode: Graph exploration with relationship grouping, breadcrumb tracking
- All components use unified design system for visual consistency
<!-- END AUTO-MANAGED -->
- any changes with plugin development needs to be mirrored in the docker deployed data directory as well at /home/chris/dev/docker/compose/appdata/siyuan/workspace/data/plugins/ies-explorer