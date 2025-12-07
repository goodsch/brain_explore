<!-- MANUAL -->
# brain_explore — Intelligent Exploration System

*A domain-agnostic tool for structured thinking, understanding, connecting, and researching across any knowledge domain*

## What This Is

A four-layer system that enables people to think WITH an AI partner who adapts to their unique thinking style while exploring complex knowledge domains:

1. **Layer 1: Knowledge Graph Creation** — Pre-processing and ingestion pipeline
   - Ingests domain materials (texts, research, conceptual frameworks)
   - Creates rich knowledge graphs with entities and relationships
   - Domain-agnostic: can ingest and structure any knowledge domain
   - *Current corpus:* 179 books in Calibre library, 10 indexed with entities (~300 entities) — used for system validation
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

**✅ 5-WAVE REMEDIATION SPRINT COMPLETE (Dec 6)**

**Comprehensive Backend Remediation:** All 8 pressure-tested components upgraded from D+ grade to production-ready. Foundation fixed, wiring complete, virtuous cycle operational.

**Wave Summary:**
- **Wave 1 (Foundation):** Unified graph client, user ID system, Redis session persistence
- **Wave 2 (Wiring):** Cross-app sync design, journey persistence from both apps
- **Wave 3 (Visibility):** Journey synthesis API, question feedback service, offline queues
- **Wave 4 (Learning):** Profile learning from sessions, question selection from feedback, reframe adaptation
- **Wave 5 (Quality):** 63 new tests, 185 total tests passing, 78% average coverage

**Key Architectural Changes:**
- **UnifiedGraphClient** — Single connection pool replacing 3 fragmented clients (1,476 lines, library/graph/unified_client.py)
  - Consolidates KnowledgeGraph, ADHDKnowledgeGraph, GraphService into one client
  - Preserves all 14 entity types (no schema collapse): Concept, Person, Theory, Framework, Assessment, Spark, Insight, Thread, FavoriteProblem, Reframe, Pattern, DynamicPattern, StoryInsight, SchemaBreak
  - Singleton driver pattern with optimal connection pooling (max 50 connections, 1-hour lifetime)
  - Cypher injection protection via ALLOWED_TYPES validation
  - Personal-domain bridge methods (SPARKED_BY relationships)
- **Enhanced Entity Extraction** — Reframe Layer support for cross-domain conceptual reframing (library/graph/entities.py)
  - 9 entity types: researcher, concept, theory, assessment, pattern, dynamic_pattern, story_insight, schema_break, reframe
  - 11 relationship types: cites, develops, supports, contradicts, operationalizes, component_of, METAPHOR_FOR, ANALOGOUS_TO, DEMONSTRATES, EMBODIES, RESONATES_WITH
  - Domain-agnostic extraction prompt prioritizing structural patterns over surface semantics
  - Reframe-specific fields: reframe_type (Metaphor/Analogy/Story/Pattern/Contrast), source_domain
  - Detects "shape words" (cycle, cascade, threshold, feedback), surprise cues (paradox, unexpected), analogy markers
- **Redis Session Store** — 24-hour TTL, session resumption, survives server restarts (232 lines)
- **Inbox Service** — Replaced capture system with unified inbox pipeline (inbox_service.py, inbox.py)
- **Flow Orientation Service** — Exploration strand management (flow_orientation_service.py)
- **Question Feedback Service** — Stores responses in Neo4j, enables learning loops (feedback_service.py)
- **Cross-App Journey Sync** — Both IES Reader and SiYuan persist journeys via `/journeys` API

**See:**
- `docs/plans/2025-12-06-comprehensive-remediation-plan.md` — Complete 5-wave strategy
- `docs/plans/2025-12-06-cross-app-sync-design.md` — Cross-app sync specification
- `docs/scratch/wave-{1-5}-complete.md` — Individual wave completion reports

---

**Phase 2c: Integration Features** ✅ COMPLETE (Dec 5-6)

**✅ SiYuan Plugin Remediation COMPLETE (Dec 5)**

Four-agent critical analysis (Dec 5) identified gaps between documented principles and implementation. **SiYuan remediation audit complete** - all critical items verified or addressed:

**Remediation Status:**
- ✅ **Questions Interactive** - `handleQuestionResponse()` creates full dialogue loop (ForgeMode lines 993-1075)
- ✅ **Question Classes Active** - `QUESTION_CLASS_HINTS` provides cognitive guidance (ForgeMode lines 1290-1360)
- ✅ **Domain-Agnostic** - Configurable notebook preferences (siyuan-structure.ts)
- ✅ **Backend Health Check** - Dashboard shows connection status (Dashboard lines 267-271)
- ✅ **Concept Extraction** - `ConceptExtractor.svelte` with graph formalization (commit 242ae72)
- ✅ **Energy Navigation** - Dashboard energy/resonance filters (Dashboard energy endpoints)
- ✅ **Error Handling** - Proper try/catch/finally patterns (QuickCapture lines 149-239)

**✅ PHASE 2c COMPLETE (Dec 5-6):**
- **SiYuan Remediation** — All critical items verified or addressed (Dec 5)
- **Readest Remediation** — All 5 critical bugs fixed, UX complete (Dec 5-6)
  - BUG-R01: Event listener memory leak (fixed with iframeDocsRef tracking + cleanup)
  - BUG-R02: Regex performance bomb (trie-based matcher implemented)
  - BUG-R03/R04: AbortController cleanup (implemented)
  - BUG-R05: Singleton stale config (config hash comparison implemented)
  - Entity click-to-flow: Full interaction loop working (iframeEventHandlers.ts → useEntityClick.ts)
  - Question response input: Complete with Cmd+Enter submit, journey tracking
  - Journey breadcrumbs: Visible in Flow panel, clickable navigation
  - IES design system: Integrated via globals.css import

**See:**
- `docs/CRITICAL-ANALYSIS-2025-12-05.md` — SiYuan plugin findings (remediation complete)
- `docs/ANALYSIS-READEST-2025-12-05.md` — Readest integration findings (remediation complete)
- `docs/PRESSURE-TEST-PLAN.md` — Systematic evaluation plan for remaining components
- `.worktrees/siyuan/TASK.md` — Complete remediation checklist with verification

**✅ IES MCP Server COMPLETE (Dec 7)**

Lightweight MCP server wrapping IES backend APIs for voice-driven ForgeMode sessions via Claude Desktop/mobile.

**Implementation:**
- `ies/mcp-server/server.py` — 363-line MCP server with 6 core tools (start_session, submit_response, end_session, get_question, list_templates, get_status)
- `ies/mcp-server/requirements.txt` — Dependencies: mcp>=1.0.0, httpx>=0.27.0
- `ies/mcp-server/README.md` — Setup, configuration, example conversation flow

**Architecture:**
- **Stateless wrapper:** All session state persists in Redis via backend session store (24-hour TTL)
- **Zero backend changes:** Uses existing `/session/*` and `/templates` endpoints from Wave 1 remediation
- **Voice-first UX:** Natural question-response dialogue with cognitive hints
- **Session recovery:** `get_question` and `get_status` tools enable context recovery after voice interruptions

**Integration:**
- Backend session API: Enhanced with state storage endpoints (`GET /session/state/{id}`, `POST /session/state/{id}`)
- Chat service: Redis-backed session persistence with context serialization
- Template system: Mode-to-template mapping (learning → learning-mechanism-map, articulating → articulating-clarify-intuition)

**Voice Interaction Flow:**
```
User: "Start a learning session about executive function"
Claude: [calls start_session] "What concept or system are you trying to understand?"
User: "How executive function relates to ADHD and self-regulation"
Claude: [calls submit_response] "List the key components or actors involved."
...
User: "That's enough for now"
Claude: [calls end_session] "Session complete! I extracted 3 concepts..."
```

**Setup:**
- Add to `~/.config/claude/claude_desktop_config.json` with IES_BACKEND_URL env var
- Prerequisites: Docker infrastructure (Neo4j, Redis, Qdrant) + backend running on port 8081
- Testing: `python ies/mcp-server/server.py` for debug mode, then restart Claude Desktop

**Scope:**
- ✅ ForgeMode sessions (5 thinking modes with template-driven questions)
- ✅ Session lifecycle management (start, respond, end, status)
- ✅ Context recovery (get_question for resumption)
- ⏸ Source search/download (Anna's Archive, Arxiv) — deferred to future
- ⏸ Flow Mode exploration — deferred to future

**Impact:** Makes ForgeMode accessible outside SiYuan plugin, enabling voice-first structured thinking workflows on mobile and desktop.

---

**✅ IES Reader Wave 1 COMPLETE (Dec 6)**
**See:** Commit 5329ec2 — Calibre library browser, PWA with offline support, IES design system, responsive layout

**📋 SiYuan Plugin Enhancements Design (Dec 6)**
**Status:** Design Complete
**Plan:** `docs/plans/2025-12-06-siyuan-plugin-enhancements-design.md`
**Purpose:** Two new features to reduce friction in SiYuan plugin workflows:
1. **Quick Plan Generation** — One-shot implementation plans from a single prompt (no full ForgeMode dialogue required)
2. **Transcript Upload** — Import external AI chat transcripts (ChatGPT, Claude.ai) as full IES sessions with entity extraction and graph integration

**Purpose:** Enable ForgeMode structured thinking sessions via Claude Desktop/mobile voice interface.

**Core MCP Tools (Session Lifecycle):**
- `start_session` — Begin ForgeMode session with mode + topic → POST /session/start
- `submit_response` — Answer current question, get next → POST /session/respond
- `end_session` — Complete session, trigger extraction → POST /session/end
- `get_question` — Get current question + hints (context recovery) → GET /session/{id}/current
- `list_templates` — Available thinking modes → GET /templates
- `get_status` — Session state, progress, history → GET /session/{id}

**Source Access Tools (Optional Extension):**
- `search_books` — Search Anna's Archive for books by title/author/topic
- `search_papers` — Search Arxiv for research papers
- `download_source` — Download and optionally auto-ingest to Calibre library
- `get_source_status` — Check ingestion status of downloaded source

**Architecture:**
- **Stateless wrapper:** Single Python file (~150 lines), wraps existing backend APIs
- **No backend changes:** Uses existing `/session/*`, `/templates` endpoints from Wave 1 remediation
- **Redis persistence:** Session state survives voice interruptions and app restarts
- **Voice-first UX:** Natural conversation flow with question-response dialogue
- **Auto-ingestion:** Downloaded sources → Calibre → auto_ingest_daemon → knowledge graph

**Voice Interaction Example:**
```
User: "Start a learning session about executive function"
Claude: [calls start_session] "First question: What do you already know...?"
User: "It's about self-regulation and planning..."
Claude: [calls submit_response] "Good foundation. Next: What specific aspect...?"
...
User: "I think that's enough for now"
Claude: [calls end_session] "Session complete. I extracted 3 concepts..."
```

**Setup:**
- File: `ies/mcp-server/server.py` + requirements.txt (mcp, httpx, arxiv)
- Config: `~/.config/claude/claude_desktop_config.json` with IES_BACKEND_URL env var
- Testing: Start infrastructure + backend → debug server.py → restart Claude Desktop

**Scope:**
- **In scope:** ForgeMode (5 thinking modes), source search/download, auto-ingestion
- **Out of scope (future):** Flow Mode exploration, spark/insight capture, free dialogue sessions

---

**All Four Layers Status:**
- ✅ Layer 1: Calibre library (179 books) + auto-ingestion daemon → 291 entities, 338 relationships (10 books indexed)
- ✅ Layer 2: Backend APIs complete — **185/185 tests passing** (Books, Reframe, Template, Personal, Graph, Inbox, Journey, Session, Thinking, Flow APIs)
- ✅ Layer 3: SiYuan Plugin — **REMEDIATION COMPLETE** (interactive questions, cognitive guidance, ADHD navigation, concept extraction)
- ✅ Layer 4: Readest — **REMEDIATION COMPLETE** (entity click-to-flow, question responses, journey breadcrumbs, IES design system)

**Latest (Dec 7):**
- ✅ **IES MCP Server Implementation Complete** — Voice-driven ForgeMode sessions via Claude Desktop/mobile:
  - **Implementation files:**
    - `ies/mcp-server/server.py` (363 lines) — MCP server with 6 core tools for session lifecycle management
    - `ies/mcp-server/README.md` (108 lines) — Setup documentation with example conversation flow
    - `ies/mcp-server/requirements.txt` — Dependencies: mcp>=1.0.0, httpx>=0.27.0
  - **Backend enhancements:**
    - `ies/backend/src/ies_backend/api/session.py` — New state management endpoints: `GET /session/state/{id}`, `POST /session/state/{id}`
    - `ies/backend/src/ies_backend/services/chat_service.py` — Enhanced with Redis session persistence, context serialization for MCP integration
  - **Core MCP tools (6 implemented):**
    - `start_session` — Creates session with mode + topic, loads user context, generates personalized greeting
    - `submit_response` — Records user response, advances to next template section, returns next question
    - `end_session` — Marks session complete, triggers entity extraction (future integration)
    - `get_question` — Retrieves current question for context recovery after voice interruptions
    - `list_templates` — Returns available thinking modes (learning, articulating, planning, ideating, reflecting)
    - `get_status` — Shows session progress, history, and completion state
  - **Template system:**
    - Mode-to-template mapping: learning → learning-mechanism-map, articulating → articulating-clarify-intuition
    - Question class hints: 9 cognitive guidance prompts (schema_probe, boundary, dimensional, causal, counterfactual, anchor, perspective_shift, meta_cognitive, reflective_synthesis)
    - Section-by-section progress tracking with total sections count
  - **State management:**
    - All session state persists in Redis via backend session store (24-hour TTL with auto-extension)
    - Stateless MCP server design — no local state, all state via backend API calls
    - Session recovery: `_get_session()`, `_update_session()` helper functions for Redis interaction
  - **Integration pattern:**
    - MCP server → Backend API (`httpx` async requests with 30-60s timeouts)
    - Backend → Redis (session persistence with TTL)
    - Backend → Neo4j (future: entity extraction on session end)
  - **Voice workflow:**
    1. User starts session via voice → `start_session` creates session in Redis with user context
    2. MCP server fetches template, returns first question to Claude
    3. User responds → `submit_response` records response, advances section index, returns next question
    4. Repeat until user says "done" → `end_session` marks complete
    5. If interrupted: `get_question` or `get_status` recovers context from Redis
  - **Claude Desktop setup:**
    - Add to `~/.config/claude/claude_desktop_config.json` with IES_BACKEND_URL env var
    - Server runs via `python` command with absolute path to server.py
    - Prerequisites: Docker infrastructure (Neo4j, Redis, Qdrant) + backend on port 8081
  - **Scope delivered:**
    - ✅ ForgeMode sessions with 2 active templates (learning, articulating)
    - ✅ Session lifecycle management (start, respond, end)
    - ✅ Context recovery after interruptions
    - ⏸ Source search/download deferred (Anna's Archive, Arxiv integration)
    - ⏸ Flow Mode exploration deferred (future enhancement)
  - **Impact:** ForgeMode now accessible via voice on Claude Desktop and mobile, enabling hands-free structured thinking sessions without SiYuan plugin dependency

**Latest (Dec 6):**
- 📋 **SiYuan Plugin Enhancements Design Complete** — Two workflow efficiency features:
  - **Design document:** `docs/plans/2025-12-06-siyuan-plugin-enhancements-design.md` (200 lines)
  - **Quick Plan Generation:** One-shot implementation plans from single prompt without full ForgeMode dialogue
    - **User flow:** Click "Quick Plan" button → Enter prompt → Backend generates structured plan → New document in `/Sessions/Planning/`
    - **Output format:** Markdown with Overview, Tasks (nested checkboxes), Success Criteria, Related Entities
    - **Backend endpoint:** `POST /session/quick-plan` with prompt and user_id, returns plan_markdown and detected_entities
    - **UI location:** Dashboard toolbar + ForgeMode header button
    - **Purpose:** Reduces friction for simple planning tasks where full dialogue is overkill
  - **Transcript Upload:** Import external AI chat transcripts as full IES sessions
    - **Input methods:** Drag & drop .md file, file picker, or paste into textarea
    - **Processing flow:** Parse conversation turns → Detect thinking mode → Extract entities → Generate summary → Create session document
    - **Supported formats:** ChatGPT (`**User:**`/`**Assistant:**`), Claude (`Human:`/`Assistant:`), Generic (`User:`/`AI:`)
    - **Backend endpoint:** `POST /session/import` with markdown, source, user_id; returns session_id, detected_mode, turn_count, entities_extracted, summary
    - **UI location:** Dashboard dedicated upload zone with drop area and paste textarea
    - **Purpose:** Enables users to bring external thinking sessions into IES knowledge graph for entity extraction and relationship discovery
  - **Success criteria:** Quick Plan: <5s generation, correct folder placement, entity linking; Transcript Upload: All input methods work, correct parsing, mode detection, entity extraction
  - **Implementation:** Backend endpoints use Claude Sonnet for generation/extraction, reuse existing extraction service, create session documents with proper frontmatter
  - **Impact:** Lowers barrier to entry for planning tasks, enables knowledge graph enrichment from external thinking sessions (ChatGPT/Claude.ai)
- 📋 **IES MCP Server Design Complete** — Voice-driven ForgeMode thinking sessions via Claude Desktop/mobile:
  - **Design document:** `docs/plans/2025-12-06-ies-mcp-server-design.md` (297 lines)
  - **Purpose:** Enable ForgeMode sessions via voice commands through Claude Desktop or mobile app
  - **Core session tools (6):** start_session, submit_response, end_session, get_question, list_templates, get_status
  - **Source access tools (4):** search_books (Anna's Archive), search_papers (Arxiv), download_source, get_source_status
  - **Architecture:** Lightweight Python wrapper (~150 lines) calling existing backend `/session/*` and `/templates` endpoints
  - **Stateless design:** No session state in MCP server — all state persists in Redis via backend session store
  - **Zero backend changes:** Leverages existing Redis session persistence from Wave 1 remediation
  - **Auto-ingestion flow:** Downloaded books/papers → Calibre ingest folder → auto_ingest_daemon → knowledge graph
  - **Scope:** ForgeMode (5 thinking modes) + source search/download; Flow Mode/sparks deferred to future
  - **Voice interaction:** Start sessions, answer questions, review progress, search/download sources — all via voice
  - **Context recovery:** `get_question` and `get_status` tools enable session resumption after voice interruptions or app restarts
  - **External integrations:** Uses existing `mcp__annas__search` and `mcp__annas__download` for Anna's Archive, `arxiv` package for papers
  - **Implementation:** Single file `ies/mcp-server/server.py` + requirements.txt (mcp, httpx, arxiv)
  - **Setup:** Claude Desktop configuration points to local Python script with IES_BACKEND_URL env var
  - **Impact:** Makes ForgeMode accessible outside SiYuan plugin, enabling voice-first structured thinking + source discovery workflows
- ✅ **5-Wave Remediation Sprint Complete (Commit 1fc56ec)** — Comprehensive backend remediation addressing all pressure test findings:
  - **Root causes fixed:** 3 fragmented Neo4j clients unified, user ID fragmentation resolved, stateless backend replaced with Redis persistence
  - **Wave 1 (Foundation):**
    - `library/graph/unified_client.py` (1,476 lines) — Single connection pool, all 14 entity types preserved, Cypher injection protection, 4 new bridge methods
    - `ies/backend/src/ies_backend/services/session_store.py` (232 lines) — Redis-backed sessions with 24-hour TTL
    - `ies/backend/src/ies_backend/api/profile.py` — `/login` endpoint for user ID unification (device ID → unified user_id)
    - `docker-compose.yml` — Redis service added (port 6379)
    - Tests: 19 UnifiedGraphClient tests, 12 session store tests, 2 profile login tests
  - **Wave 2 (Wiring):**
    - `docs/plans/2025-12-06-cross-app-sync-design.md` — Complete cross-app sync specification
    - IES Reader: `graphClient.saveJourney()` now persists to backend (not just localStorage)
    - SiYuan Plugin: Flow exploration journeys saved via `/journeys` API
    - Both apps use `/profile/login` for unified user_id
  - **Wave 3 (Visibility):**
    - `ies/backend/src/ies_backend/services/feedback_service.py` (174 lines) — Question feedback storage in Neo4j
    - `ies/backend/src/ies_backend/api/journey.py` — Journey synthesis endpoint with Claude Sonnet 4
    - Offline queue design for both apps (deferred to implementation)
  - **Wave 4 (Learning):**
    - Profile learning from session patterns (session → profile dimension updates)
    - Question selection weighted by feedback (thumbs up/down → question class weights)
    - Reframe prompt adaptation (user preferences → generation strategy)
  - **Wave 5 (Quality):**
    - 63 new tests: journey_service (15), chat_service (13), personal_graph_service (15), graph_service (20)
    - Total: 185/185 tests passing (up from 122)
    - Coverage: journey_service (78%), chat_service (50%), personal_graph_service (91%), graph_service (95%)
  - **Infrastructure Changes:**
    - Capture system removed, replaced with Inbox service (`ies/backend/src/ies_backend/services/inbox_service.py`, `ies/backend/src/ies_backend/api/inbox.py`)
    - Flow orientation service added (`ies/backend/src/ies_backend/services/flow_orientation_service.py`) for exploration strand management
    - All 8 pressure-tested components upgraded from D+ grade to production-ready
  - **Impact:** Virtuous cycle now operational — journeys persist, feedback informs questions, profile learns from sessions, cross-app state synchronized

**Latest (Dec 5):**
- ✅ **Session API Refinements** — Enhanced session processing for improved entity extraction and schema alignment:
  - `ies/backend/src/ies_backend/api/session.py`: Updated endpoint documentation and type hints (200 lines)
  - `ies/backend/src/ies_backend/schemas/entity.py`: Enhanced entity schemas with session context support (200 lines)
  - `/session/end` endpoint: Returns `SessionEndResponse` with enhanced fields (entities_created, entities_updated, key_insights, open_questions)
  - Integration: ForgeMode session completion flow uses updated schemas for concept extraction wizard
  - Fields: `doc_id`, `entities_extracted` (count), `summary` (key insights), plus detailed entity/insight lists for UI display
- ✅ **SiYuan Plugin Structure Refinements** — Enhanced domain-agnostic configuration and session document metadata:
  - `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts`: Updated session document creation with ShapingBlockMeta support (769 lines)
  - **10-folder structure complete:** Added `/System/` folder with Templates and Example_Notes subfolders (Package's 07_System)
  - **Backend health check fix:** Aligned `BackendHealth` interface with Dashboard expectations (`ok`, `backendUrl`, `checkedAt`, `message` fields)
  - **Notebook preferences:** Added 'IES' to default notebook names for better domain-agnostic alignment
  - **Error handling enhancement:** `callBackendApi()` now properly throws errors instead of returning null, with detailed logging
  - **Purpose:** Completes merged architecture with full Package 07_System layer, fixes health check interface mismatch
- ✅ **SiYuan Architecture Implementation (Commit 4ce8b11)** — Merged IES Architecture Package structure with ADHD-friendly current implementation
  - **Design Document:** `docs/plans/2025-12-05-siyuan-architecture-merge-design.md` — Complete merge strategy (301 lines)
  - **Comparison Analysis:** `docs/ARCHITECTURE-COMPARISON.md` — Detailed gap analysis (556 lines) comparing architectures
  - **Implementation Files:**
    - `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts` — STRUCTURE_FOLDERS array updated to 9-folder merged hierarchy (lines 32-71)
    - `.worktrees/siyuan/ies/plugin/src/types/blocks.ts` — Complete TypeScript type system for block schemas (250 lines)
    - `.worktrees/siyuan/ies/plugin/src/index.ts` — Plugin lifecycle unchanged (structure initialization on load)
  - **Merged 9-Folder Structure (IMPLEMENTED):**
    - `/Daily/` — Quick captures (Package's 00_Inbox)
    - `/Seedlings/` — Atomic ideas with 7 subcategories (Questions, Observations, Moments, Schemas, Contradictions, What_Ifs, Insights)
    - `/Sessions/` — Mode-specific thinking (Learning, Articulating, Planning, Ideating, Reflecting)
    - `/Flow_Maps/` — Visual maps (Package's 03_Flow_Maps)
    - `/Concepts/` — Canonical concepts (aligned)
    - `/Insights/` — Promoted/validated insights (current)
    - `/Favorite_Problems/` — ADHD anchor questions (current)
    - `/Projects/` — Active work (Package's 05_Projects)
    - `/Archive/` — Retired material (Package's 06_Archive)
  - **Block Type System (IMPLEMENTED):**
    - 6 formal block types: `seed`, `shaping`, `map`, `concept`, `decision`, `log_entry`
    - 7 idea types for seedlings: `question`, `insight`, `observation`, `moment`, `schema`, `contradiction`, `what_if`
    - TypeScript interfaces: `QuickCaptureMeta`, `SeedBlockMeta`, `ShapingBlockMeta`, `MapBlockMeta`, `ConceptBlockMeta`, `DecisionBlockMeta`, `LogEntryMeta`
    - Seedling folder mapping: `SEEDLING_FOLDER_MAP` maps idea types to Seedlings subfolders
  - **Two Status Systems (IMPLEMENTED):**
    - `capture_status`: `raw` → `classified` → `processed` (AI processing state)
    - `status`: `captured` → `exploring` → `anchored` (user engagement state)
    - Enums: `CaptureStatus`, `UserStatus`, `ResonanceSignal`, `EnergyLevel`
  - **Metadata Storage:** Both YAML frontmatter AND SiYuan attributes (design decision, implementation pending)
  - **Dual Insights Folders:** Seedlings/Insights (raw "aha" moments) vs /Insights/ (promoted/validated)
  - **Preserved ADHD Features:** energy_level, resonance_signal, exploration_visits, backend linking (be_id, be_type)
  - **Repository Guidelines:** `AGENTS.md` created documenting IES SiYuan Architecture Package expert context for AI agents
- ✅ **Architecture Comparison Analysis** — Comprehensive evaluation of IES SiYuan Architecture Package vs. current implementation
  - `docs/ARCHITECTURE-COMPARISON.md`: 486-line detailed comparison across all architectural dimensions
  - **Key Finding:** The two architectures are **complementary, not competing**
  - Architecture Package provides the **SiYuan document structure** we've been missing (Gap #1 in SYSTEM-DESIGN.md)
  - Current implementation provides the **backend intelligence and cross-app integration** the Package assumes but doesn't define
  - **7-Layer Package Structure:** `/00_Inbox/` → `/01_Seedlings/` → `/02_Shaping/` → `/03_Flow_Maps/` → `/04_Concepts/` → `/05_Projects/` → `/06_Archive/` + `/07_System/`
  - **Defining Feature:** Quick Capture system with status lifecycle (raw → classified → processed) and AI boundary clarification
  - **6 Formal Block Schemas:** seed-block, shaping-block, map-block, concept-block, decision-block, log-entry-block
  - **Hybrid Migration Strategy:** Preserve ADHD-friendly features (energy levels, resonance signals, backend APIs, Question Engine) while adopting Quick Capture lifecycle, Seedling types, formal block schemas, Project structure, Flow Maps, Archive system
  - **Implementation Priority:** Foundation (STRUCTURE_FOLDERS, Quick Capture schema, status lifecycle) → UI Components (Queue sidebar, Process workflow, Seedling type selection) → Templates → Integration
  - Reference implementation available in `IES_SiYuan_Architecture_Package_QuickCaptureUpdated/`
- ✅ **UX Development Worktree Created** — New worktree for unified design system work
  - `.worktrees/ux-dev/` on branch `feature/ux-development`
  - **Purpose:** Create unified "IES Design System" across SiYuan Plugin (Svelte) and Readest (React/Next.js)
  - **Problem:** Each interface built independently with different color palettes, typography, spacing, animations, component styles
  - **Goal:** Consistent experience, ADHD-friendly visual patterns, clear hierarchy, reduced cognitive load
  - **Priority 1:** Design system audit — extract current tokens, identify inconsistencies, define unified token set
  - **Priority 2:** Implementation — unified color system, typography, spacing, animations, component library
  - **Shared tokens:** CSS custom properties work in both Svelte and React ecosystems
  - TASK.md documents complete design system audit and implementation plan
- ✅ **Unified Design System Specification** — Complete design token system (801 lines)
  - `docs/plans/UNIFIED-DESIGN-SYSTEM.md`: Comprehensive design system specification with "Contemplative Knowledge Space" philosophy
  - **Aesthetic:** The Reading Room — intellectual warmth meeting focused clarity (quiet afternoon in well-curated library)
  - **Typography:** 4-font system (Crimson Pro display, Nunito body, Inter UI, JetBrains Mono code) with Major Third scale (1.25 ratio, 15px base)
  - **Colors:** Warm paper tones (#f8f6f3 deep, #fffef9 base), amber accent (#d4a574), sage secondary (#7a9987), soft violet tertiary (#9d8fb5)
  - **Entity type colors:** Blue Concept (#2563eb), Green Person (#059669), Purple Theory (#7c3aed), Orange Framework (#ea580c), Red Assessment (#dc2626)
  - **Spacing:** 8px base unit, 11-step scale (0.5x to 12x) for consistent rhythm
  - **Shadows:** 6-level elevation system (xs to glow) for depth perception
  - **Animations:** 4 durations (instant 100ms, fast 200ms, base 300ms, slow 500ms) with ease-out default
  - **Component patterns:** Cards, buttons, badges, forms, modals with semantic states
  - **Implementation:** CSS custom properties compatible with both Svelte and React, dark theme overrides, ADHD-friendly hierarchy
- ✅ **IES Design System Integration** — Main plugin stylesheet now imports comprehensive design system
  - `.worktrees/siyuan/ies/plugin/src/index.scss`: Added `@import './styles/design-system.scss'` for unified styling
  - Integrates "Contemplative Knowledge Space" design philosophy across all plugin components
  - Provides CSS variables for colors, spacing, shadows, transitions, and animations
  - Part of SiYuan plugin remediation effort to improve design consistency
  - Design system location: `.worktrees/siyuan/ies/plugin/src/styles/design-system.scss`
- 📋 **IES Design System v2 — Modern Information Space** (Dec 6) — Design complete, replaces "Contemplative Knowledge Space":
  - `docs/plans/2025-12-06-ies-design-system-v2.md`: Complete specification (417 lines) with modern dark-mode-first aesthetic
  - **Philosophy shift:** From warm reading room → sleek modern information space (Linear/Raycast/Arc inspired)
  - **Color system:** Dark mode default (#0f0f10 near-black base, #1a1a1c elevated surfaces), entity colors as primary accents
  - **Typography:** Sans-serif only (Inter for UI, JetBrains Mono for code), no serifs in interface
  - **Visual language:** Glass effects (backdrop blur), bold entity colors, smooth fast transitions (150-200ms)
  - **Information density:** Tight spacing, collapsible sections, no wasted whitespace
  - **Components:** Floating panels with glass effect, entity badges with gradients, keyboard shortcut indicators
  - **Entity colors bolder:** Concept (#3b82f6 blue), Person (#10b981 green), Theory (#8b5cf6 purple), Framework (#f59e0b amber), Assessment (#ef4444 red)
  - **Gradients for active states:** `--gradient-concept` (linear blue), `--gradient-person` (linear green), etc.
  - **Layout patterns:** Mobile full-screen app with sticky headers, dynamic viewport height (100dvh)
  - **Migration notes:** Warm tones → dark tones, Crimson Pro → Inter, amber accent → entity colors, calm → alive
  - **Status:** Design complete, implementation pending (replaces existing design-system.scss)
- ✅ **Domain-Agnostic SiYuan Structure** — Removed therapy-specific hardcoding from notebook selection
  - User-configurable notebook preferences via localStorage `ies.preferredNotebooks`
  - Default notebooks: `['Personal', 'Knowledge', 'Notes', 'Intelligent Exploration System']` (domain-agnostic)
  - Helper functions: `setPreferredNotebooks()`, `getPreferredNotebooks()` for runtime customization
  - Notebook resolution: First matching open notebook by preference, falls back to first available
  - Backend URL configuration via `ies.backendUrl` localStorage key with `setBackendUrl()` helper
- ✅ **Personal Graph Integration** — Complete backend API integration for ADHD-friendly capture
  - `createSparkWithBackend()`: Creates spark in backend + SiYuan block with bidirectional linking
  - `promoteToInsight()`: Promotes spark to insight in backend + moves SiYuan doc to /Insights/ folder
  - `getPersonalStats()`: Retrieves personal graph statistics (total sparks, insights, status distribution)
  - `visitSpark()`: Records visit for recency-based navigation
  - Block attributes synced: `custom-be_id`, `custom-be_type`, `custom-status` for backend linking
- ✅ **Question Engine Nine Classes Implementation (Commit 1d1ca9f)** — Backend question classification system complete
  - QuestionClass enum with 9 classes mapped to AST thinking modes
  - APPROACH_TO_CLASSES mapping: inquiry approaches generate specific question types
  - New endpoints: `/question-classes` (list all with descriptions), `/approach-classes` (show approach→class mappings)
  - ClassifiedQuestion schema for tagged questions with cognitive function labels
  - Integration with ForgeMode: state detection, approach selection, question generation all use class system
- ✅ **AST Folder Structure and Session Persistence (Commit c97aaf7)** — SiYuan plugin now creates structured session documents
  - Expanded STRUCTURE_FOLDERS: /Concepts/ + mode-specific /Sessions/{mode}/ folders (Learning, Articulating, Planning, Ideating, Reflecting)
  - createSessionDocument() function: saves sessions with frontmatter (be_type, be_id, mode, topic, status, question_classes_used)
  - Session documents include: section responses (template-driven), full conversation transcript, entities extracted, graph mapping status
  - ForgeMode integration: sessions auto-save to SiYuan on completion with timestamp and mode-specific folder placement
  - Enhanced YAML serialization: Proper handling of arrays, nested objects, dates, null values
- ✅ **IES AST Mode and Question Engine** — 20 SiYuan documents created defining structured thinking architecture
  - Four thinking modes: Discovery (schema surfacing), Dialogue (model building), Flow (associative exploration), AST (assisted structured thinking)
  - Nine question classes: Schema-Probe, Boundary, Dimensional, Causal, Counterfactual, Anchor, Perspective-Shift, Meta-Cognitive, Reflective-Synthesis
  - Mode Transition Engine specifications for automatic mode switching
  - ADHD-friendly folder structure: /Daily, /Insights, /Threads, /Favorite Problems, /Concepts
  - Complete data schemas: Seed Schema, Concept Schema, Block Attributes, Note Templates
- 📋 **SiYuan Settings Panel Design** — Configuration UI specification for plugin preferences
  - Ollama integration: Local AI with auto-discovered models for chat + embeddings
  - Cloud provider support: OpenAI/Anthropic API key + model selection
  - Connection management: Backend URL + Ollama URL configuration with status indicators
  - Domain-agnostic notebook preferences: User-configurable preferred notebooks list
  - Settings stored locally in SiYuan plugin data, API keys never sent to backend
  - Design doc: `docs/plans/2025-12-05-siyuan-settings-panel-design.md` (177 lines)

**For complete project status, see:** `docs/COMPREHENSIVE-PROJECT-STATUS.md`

**Phase 1 Achievement Summary:**
- ✅ **10/10 validation sessions completed** — System validated using personal therapy/growth exploration
- ✅ **11+ concepts extracted and formalized** — Demonstrated the full thinking → extraction pipeline
- ✅ **Complete concept connection map** — Hierarchical relationships documented in CONNECTIONS.md
- ✅ **Extraction pipeline proven end-to-end** — Session → Transcript → Extraction → Formalization → Commit
- ✅ **Core hypothesis validated** — Personalized dialogue patterns directly affect concept discovery
- ✅ **IES backend (94/94 tests passing)** — All APIs production-ready including Flow Mode capture → thinking → flow pipeline
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
- **Phase 2c (65% COMPLETE):** Calibre integration + Entity overlay + Reframe API + Template API + ForgeMode
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
| `.worktrees/readest-critique/` | `feature/readest-critique` | Readest Four-Agent Pressure Test | `TASK.md` in worktree |
| `.worktrees/ux-dev/` | `feature/ux-development` | Unified Design System (SiYuan + Readest visual consistency) | `TASK.md` in worktree |

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
└── docker-compose.yml             # Full infrastructure stack (5 services)
```

**Architecture Alignment:**
- **Layer 1** = Knowledge graph + ingestion pipeline in `library/` and `books/`
- **Layer 2** = Backend services (API, dialogue, profile) in `ies/backend/`
- **Layer 3** = SiYuan plugin in `.worktrees/siyuan/` (processing hub, dashboard)
- **Layer 4** = Readest integration in `.worktrees/readest/` (reading interface)
- **Active Application** = `therapy/` directory (personal growth framework — ongoing project)

**Docker Infrastructure Stack:**

The `docker-compose.yml` orchestrates six services supporting all four layers:

1. **Qdrant** (Vector Store - Layer 1)
   - Container: `brain_explore_qdrant`
   - Ports: 6333 (REST API), 6334 (gRPC)
   - Purpose: Embedding storage for entity and concept search
   - Data: `./data/qdrant`

2. **Neo4j** (Graph Database - Layer 1)
   - Container: `brain_explore_neo4j`
   - Ports: 7474 (Browser), 7687 (Bolt protocol)
   - Auth: neo4j/brainexplore
   - APOC plugin enabled for advanced graph operations
   - Data: `./data/neo4j`

3. **Calibre Web** (Book Catalog - Layer 1)
   - Container: `brain_explore_calibre`
   - Port: 8083 (Web UI)
   - Purpose: Single source of truth for book library (179 books)
   - Features: Auto-import from `/downloads`, metadata management
   - Library: `./calibre/library` (SQLite + epub/pdf files)
   - Ingest: `./calibre/ingest` (incoming books directory)

4. **SiYuan** (Processing Hub - Layer 3)
   - Container: `brain_explore_siyuan`
   - Port: 6806 (Web UI)
   - Purpose: Personal knowledge management with IES plugin integration
   - **Workspace:** `./data/siyuan/workspace`
   - **Plugins:** `./data/siyuan/workspace/data/plugins/` (install IES plugin here)
   - **Themes:** `./data/siyuan/workspace/data/themes/`
   - **Notebooks:** `./data/siyuan/workspace/data/` (each notebook is a folder)
   - Auth bypass enabled for development
   - Note: Plugin runs client-side, communicates with backend via forwardProxy

5. **Redis** (Session Store - Layer 2)
   - Container: `brain_explore_redis`
   - Port: 6379 (Redis protocol)
   - Purpose: Persistent session storage with 24-hour TTL
   - Features: AOF persistence, session resumption across server restarts
   - Data: `./data/redis`
   - Added in Wave 1 remediation (Dec 6)

6. **Readest** (Reading Interface - Layer 4)
   - Run locally: `cd .worktrees/readest/readest/apps/readest-app && pnpm dev`
   - Port: 3000 (dev server)
   - Purpose: E-book reader with entity overlay and flow exploration
   - Note: Not containerized — Tauri desktop app runs better natively for development

**Service Dependencies:**
- Backend APIs (Layer 2) run on host at port 8081, connect to Qdrant + Neo4j + Redis
- SiYuan plugin uses forwardProxy to call backend APIs from browser context
- Readest calls backend APIs directly via HTTP (localhost:8081 or network IP)
- Calibre integration uses `calibre_id` as universal book identifier across all systems
- Redis stores session state with 24-hour TTL and extension on activity

**Quick Start:**
```bash
docker compose up -d             # Start all 6 services
docker compose ps                # Check service status
docker compose down              # Stop all services
```

## Key Resources

### Documentation Hierarchy

The project maintains a three-level documentation structure for clarity:

**Level 1: Strategic Vision (Project Context)**
- `docs/PROJECT-OVERVIEW.md` — Single source of truth for the complete vision: three-layer architecture, what's built vs. deferred, why design decisions were made, Phase 1 success criteria, and roadmap
- `docs/five-agent-synthesis.md` — Deep analysis: architectural vision, identified gaps, why configuration was blocking, lessons learned, phased path forward

**Level 2: Operational & Validation Documentation**
- `docs/SYSTEM-DESIGN.md` — **Operational reference**: How the system works end-to-end, data structures, user workflows, integration points, critical gaps (read at session start)
- `docs/COMPREHENSIVE-PROJECT-STATUS.md` — Complete project status: all 4 layers, phase completion, worktree organization
- `docs/ARCHITECTURE-COMPARISON.md` — **Architecture Analysis** (556 lines): Comprehensive comparison between IES SiYuan Architecture Package (7-layer structure with Quick Capture system) and current four-layer implementation; identifies complementary strengths and hybrid migration strategy
- `docs/CRITICAL-ANALYSIS-2025-12-05.md` — **SiYuan Plugin Analysis** (Grade: D, 1.6/4.0): Infrastructure exists but core principles not delivered (questions displayed passively, no response capture, decorative question badges, missing ADHD navigation, incomplete virtuous cycle, domain hardcoding)
- `docs/ANALYSIS-READEST-2025-12-05.md` — **Readest Integration Analysis** (Grade: D+, 1.8/4.0): Same catastrophic pattern as SiYuan; entity highlights non-interactive, journey tracking invisible, 15 bugs (2 critical), design system disconnect
- `docs/PRESSURE-TEST-PLAN.md` — **Systematic evaluation plan**: Four-agent testing pattern for all components (Design Reviewer, Principle Evaluator, Bug Hunter, UX Analyst); 8 components analyzed
- `docs/plans/2025-12-06-comprehensive-remediation-plan.md` — **5-Wave Remediation Strategy**: Root cause analysis, dependency graph, execution order (Foundation → Wiring → Visibility → Learning → Quality)
- `docs/PLANNING-GAPS-AND-QUESTIONS.md` — Comprehensive Phase 2c planning: critical gaps, technical stack review, API inventory, integration questions
- `docs/plans/2025-12-04-reframe-template-integration-design.md` — Phase 2c implementation: Reframe Layer + Thinking Templates + SiYuan document structure
- `docs/plans/2025-12-04-calibre-integration-design.md` — Calibre integration architecture: single source of truth for book catalog with universal calibre_id identifier; multi-pass ingestion pipeline (structure → relationships → enrichment); backend APIs complete (Dec 4)
- `docs/plans/2025-12-04-readest-calibre-library-view.md` — **Phase 4 UI design**: Readest library browser modal with search, entity badge filter, and direct book opening (Dec 4)
- `docs/plans/2025-12-06-ies-reader-wave1-design.md` — **IES Reader Wave 1 Enhancement**: Calibre library integration, PWA configuration, IES design system application, responsive layout (Dec 6)
- `docs/plans/UNIFIED-DESIGN-SYSTEM.md` — **Complete design system specification** (801 lines): "Contemplative Knowledge Space" aesthetic with typography system, color palette, spacing scale, shadows, animations, component patterns; CSS custom properties for Svelte/React compatibility
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
- `docker-compose.yml` — Full infrastructure stack (6 services: Qdrant, Neo4j, Redis, Calibre, SiYuan, Readest)

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

### Building SiYuan Plugin

```bash
cd .worktrees/siyuan/ies/plugin
pnpm install                     # Install dependencies
pnpm build                       # Build plugin
pnpm dev                         # Development mode

# Install built plugin to SiYuan workspace:
cp -r dist/* ./data/siyuan/workspace/data/plugins/ies/
```

## Quick Commands

```bash
# Git
git log --oneline -20            # See recent commits
git diff                         # See uncommitted changes
git status                       # See current state

# Docker services (Qdrant, Neo4j, Calibre, SiYuan)
docker compose up -d             # Start all services
docker compose ps                # Check service status
docker compose down              # Stop all services
docker compose logs siyuan       # View SiYuan container logs

# Readest (run locally, not in Docker)
cd .worktrees/readest/readest/apps/readest-app && pnpm dev

# SiYuan data paths (inside Docker volume)
# Plugins: ./data/siyuan/workspace/data/plugins/
# Themes:  ./data/siyuan/workspace/data/themes/
# Notes:   ./data/siyuan/workspace/data/
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

**Recent Changes (Dec 6):**
- **Flow Orientation Service (New Backend Feature)** — Context-aware exploration strand generation for Flow Mode initiation:
  - `ies/backend/src/ies_backend/services/flow_orientation_service.py`: New service for generating exploration strands from spark context (194 lines)
  - **Purpose:** Analyzes note content, text selections, or thoughts to suggest 3-5 exploration paths through knowledge graph
  - **Three-step process:**
    1. Extract text from OrientationRequest (selected text → note title → empty)
    2. Search knowledge graph for matching entities via GraphService.search_concepts()
    3. Generate strands based on entity types and relationships
  - **Strand generation strategies:**
    - Primary concept deep dive (first matched entity + top 3 connections)
    - Connecting the dots (relationships between top 4 entities)
    - Type-specific perspective (Person/Framework/Theory lens)
    - Practical application (mechanisms and patterns)
  - **Default strands:** Free Exploration, Recent Discoveries, Core Frameworks (when no entities match)
  - **Entity matching:** Tries full text search first, falls back to individual word matching for longer text (>3 words)
  - **Deduplication:** Tracks seen entity IDs to prevent duplicate strand suggestions
  - **Integration:** New `/flow/orientation` endpoint in flow_session.py API router
  - **Schemas:** OrientationRequest (spark context), OrientationResponse (entities + strands), Strand, EntitySummary
  - **Impact:** Enables ADHD-friendly Flow initiation from SiYuan notes with low-friction context capture
- **Inbox Service (New Backend Feature)** — Quick capture processing with AI entity extraction and placement suggestions:
  - `ies/backend/src/ies_backend/services/inbox_service.py`: New service for processing inbox items with AI-powered entity extraction (200+ lines)
  - **Purpose:** Processes quick captures (notes, thoughts, highlights) to extract entities and suggest SiYuan folder placements
  - **Two extraction modes:**
    - AI-powered (Anthropic Claude Sonnet 4): Extracts entities with type/confidence, generates summary, tags
    - Simple fallback: Regex-based capitalized phrase extraction when ANTHROPIC_API_KEY unavailable
  - **Entity extraction format:** `ENTITIES: [name]: [type] (confidence 0-1)` with types: concept, person, theory, framework, practice
  - **Graph matching:** Cross-references extracted entities with knowledge graph via GraphService.search_concepts()
  - **Placement suggestions:** Recommends SiYuan folders based on content analysis and graph context
  - **Schemas:** InboxProcessRequest, InboxProcessResponse, ExtractedEntity (with graph_match flag), SuggestedPlacement
  - **Keyword detection:** Hardcoded therapy/psychology keywords for tag extraction (acceptance, grief, shame, etc.)
  - **TODO:** Make keyword detection domain-agnostic or user-configurable
  - **Integration:** Supports Quick Capture workflow (Daily folder → classification → placement)
  - **Impact:** Reduces friction in ADHD capture-to-organization pipeline with intelligent routing
- **Flow Session API Enhancement** — Added orientation endpoint for Flow Mode spark context analysis:
  - `ies/backend/src/ies_backend/api/flow_session.py`: New POST `/flow/orientation` endpoint (lines 66-77)
  - **Purpose:** Generate exploration strand proposals from current context (note, selection, thought)
  - **Request schema:** OrientationRequest with spark_type, user_id, and optional context fields (note_id, note_title, text, block_ids, book_id, location)
  - **Response schema:** OrientationResponse with extracted_entities and suggested_strands arrays
  - **Integration:** FlowOrientationService.generate_orientation() orchestrates entity extraction and strand generation
  - **Use case:** User right-clicks SiYuan note → "Start Flow from this note" → Backend analyzes note context → Suggests 3-5 exploration paths
- **Flow Session Schemas Extension** — New schemas for orientation phase:
  - `ies/backend/src/ies_backend/schemas/flow_session.py`: Added orientation-specific schemas (lines 114-168)
  - **Strand schema:** id, name (e.g., "The Shame Loop"), description, starting_entities list
  - **EntitySummary schema:** id, name, type, summary, connection_count (lightweight for UI display)
  - **OrientationRequest:** Captures spark context with flexible field support (at least one context field required)
  - **OrientationResponse:** Returns extracted entities and suggested strands for UI presentation
  - **Naming convention:** All field aliases use camelCase for JavaScript/TypeScript frontend compatibility
- **SiYuan Plugin Context Menu Integration** — Flow initiation from document titles with orientation support:
  - `.worktrees/siyuan/ies/plugin/src/index.ts`: Context menu handler for "Start Flow from this note" (lines 176-200)
  - **User flow:** Right-click note title → Select "Start Flow from this note" → Opens IES with Flow Mode pre-loaded
  - **Context capture:** Extracts noteId (protyle.block.rootID), noteTitle (protyle.title.editElement.textContent), notebookId
  - **State management:** Updates noteContext store with current note before opening Flow
  - **Integration:** Calls openFlowWithContext() to transition to Flow view with orientation request
  - **Icon:** Uses 'iconFlow' custom SVG icon in context menu
  - **Purpose:** Low-friction Flow initiation directly from SiYuan documents (no manual navigation required)
- **Dashboard Quick Capture Queue** — Enhanced capture status filtering with visual status indicators:
  - `.worktrees/siyuan/ies/plugin/src/views/Dashboard.svelte`: Added capture_status filtering for Quick Capture queue (lines 104-141)
  - **Filter options:** All, Raw (⬜), Classified (🔄), Processed (✅) with emoji indicators
  - **CaptureStatus type:** Imported from types/blocks with CAPTURE_STATUS_LABELS mapping
  - **Computed filter:** Reactive `filteredCaptureQueue` based on captureStatusFilter selection
  - **Queue display:** Shows title, content_preview, captured_at, capture_status, resonance_signal, energy_level
  - **Integration:** Supports Quick Capture → Inbox workflow with AI classification tracking
  - **Purpose:** ADHD-friendly queue management with visual status progression (raw → classified → processed)
- **Context Store (SiYuan Plugin)** — New reactive store for tracking current note context:
  - `.worktrees/siyuan/ies/plugin/src/stores/contextStore.ts`: Writable store for noteContext with helper functions
  - **State fields:** noteId (SiYuan block ID), noteTitle (document title), notebookId (parent notebook)
  - **Exported helpers:** hasNoteOpen (derived store checking if noteId exists), currentNoteTitle (derived store for title access)
  - **Context tracking:** initContextTracking() and destroyContextTracking() lifecycle hooks
  - **Integration:** Used by context menu handlers and Flow Mode for orientation request building
  - **Purpose:** Preserves user's current location when initiating Flow from notes
- **Backend Book Streaming Fix (Dec 6)** — Fixed epub.js inline reading with StreamingResponse:
  - **Commit:** `72f6228: fix(reader): Add missing proxy config and error handling for book loading`
  - **Problem:** FileResponse with Content-Disposition header caused epub.js to download instead of reading inline
  - **Solution:** StreamingResponse with 64KB chunks, no Content-Disposition header
  - **Implementation (books.py, lines 105-132):**
    - Changed return type from `FileResponse` to `StreamingResponse`
    - Generator function `file_iterator()` yields 64KB chunks for memory efficiency
    - Headers: Content-Type (application/epub+zip or application/pdf), Content-Length only
    - Media type determined by file extension (.epub vs .pdf)
  - **Impact:** epub.js can now read book files directly in browser without download prompts
  - **Related:** Works with updated vite proxy config (all endpoints now use 127.0.0.1 instead of localhost)
- **Vite Proxy Configuration Enhancement (Dec 6)** — Fixed IPv6 resolution issues and added health check endpoint:
  - **Commit:** `72f6228: fix(reader): Add missing proxy config and error handling for book loading`
  - **Problem:** `localhost` resolves to IPv6 `::1` on some systems, causing backend connection failures
  - **Solution:** Use `127.0.0.1` explicitly for all backend proxies (vite.config.ts lines 131-165)
  - **Updated proxies:** `/api`, `/books`, `/graph`, `/profile`, `/question-engine`, `/journeys` (all now 127.0.0.1:8081)
  - **New proxy added:** `/health` endpoint for backend availability checks
  - **Pattern:** All proxies use `target: 'http://127.0.0.1:8081'` with `changeOrigin: true`
  - **Impact:** Reliable backend connection across different OS network configurations
  - **Related:** Complements StreamingResponse fix for complete book loading flow
- **Reader Error Handling Enhancement (Dec 6)** — Improved loading timeout with better state management:
  - **Commit:** `72f6228: fix(reader): Add missing proxy config and error handling for book loading`
  - **Enhanced Timeout System (Reader.tsx, lines 24-44):**
    - 15-second loading timeout with console logging for debugging
    - `useEffect` cleanup prevents timeout from triggering after component unmount
    - Conditional execution: only runs if loading and no existing error
    - Console markers: `[Reader] Starting 15s loading timeout...` and `[Reader] Loading timeout reached!`
  - **Error Recovery Flow (Reader.tsx, lines 156-181):**
    - Dedicated error overlay with AlertCircle icon (lucide-react)
    - "Try Again" button resets error state and forces re-render by toggling location to 0
    - "Back to Library" button conditionally shown when onClose callback provided
    - Error actions div groups buttons with proper spacing
  - **Loading State Coordination (Reader.tsx, line 148):**
    - Loading overlay now checks `isLoading && !loadError` to prevent simultaneous display
    - Error state takes precedence over loading state for better UX
  - **ReactReader Conditional Rendering (Reader.tsx, line 184):**
    - Entire reader content wrapped in `{!loadError && ...}` to hide on error
    - Prevents epub.js from attempting to load when in error state
    - `loadingView` prop added to ReactReader for custom loading display (lines 199-203)
  - **State Management Pattern:**
    - Three states: `isLoading` (boolean), `loadError` (string | null), `location` (string | number)
    - Error recovery resets: `setLoadError(null)`, `setIsLoading(true)`, `setLocation(0)`
    - Location reset to 0 forces ReactReader to re-mount and retry
  - **Debug Logging:**
    - Mount logging with URL, title, calibreId (lines 25-28)
    - getRendition success logging: `[Reader] getRendition called - book loaded successfully!` (line 64)
    - Timeout logging for diagnosing slow network/missing files
  - **Impact:**
    - Users see specific error messages instead of infinite loading spinners
    - Retry mechanism with proper state reset enables recovery without full page reload
    - Debug logs help diagnose book loading issues in production
  - **Related:** Part of Wave 1 production readiness improvements alongside PWA and library browser features
- **✅ IES Reader Wave 1 Complete (Dec 6)** — Standalone React app transformed into production-ready PWA with Calibre library integration:
  - **Commit:** `5329ec2: feat(reader): Wave 1 enhancement - Library browser, PWA, design system`
  - **Total changes:** 23 files, +9,038 lines, -2,761 lines (net +6,277 lines)
  - **Package updates:** Added `vite-plugin-pwa@1.2.0`, `lucide-react@0.556.0`, `@types/node@24.10.1`
  - **New components (library/):**
    - `LibraryBrowser.tsx` (222 lines) — Grid view with search, filter controls, install prompt
    - `BookCard.tsx` (60 lines) — Cover images, entity count badges, loading states
    - `SearchBar.tsx` (79 lines) — Debounced search with responsive styling
    - `index.ts` (3 lines) — Clean module exports
  - **PWA Configuration (vite.config.ts):**
    - Full PWA manifest with 192px/512px icons, splash screens, theme colors
    - Workbox runtime caching: book files (CacheFirst, 30 days), covers (CacheFirst, 7 days), API (NetworkFirst, 1 hour)
    - Service worker auto-update with dev mode enabled
    - Backend proxy: `/books`, `/graph`, `/profile`, `/question-engine`, `/journeys` all route to localhost:8081
  - **Design System Integration:**
    - `src/styles/design-system.css` (561 lines) — Complete IES Design System tokens
    - Typography: Crimson Pro (display), Nunito (body), Inter (UI), JetBrains Mono (code)
    - Colors: Warm paper tones (#FDFBF7), amber accent (#D4A574), entity-specific colors
    - Spacing: 8px base unit with 11-step scale, 6-level shadow system
    - Animations: 4 durations (instant/fast/base/slow) with consistent easing
  - **App Architecture Refactor:**
    - `App.tsx` (99 lines) — State machine: login → library browser → reader
    - Login flow with automatic device ID generation
    - Calibre book selection vs local file upload
    - Proper URL cleanup for blob URLs on book close
  - **Reader Updates:**
    - `Reader.tsx` (131 lines) — Accept `calibreId` prop for backend integration
    - `Reader.css` (133 lines) — Responsive toolbar, Flow Panel toggle, mobile-friendly
  - **Flow Panel Enhancements:**
    - `FlowPanel.tsx` (194 lines) — Improved empty states, loading indicators
    - `FlowPanel.css` (368 lines) — IES Design System integration, smooth transitions
  - **Library Browser Features:**
    - Grid/list view toggle (responsive breakpoints: mobile 1 col, tablet 2 cols, desktop 3-4 cols)
    - Real-time search with debouncing (500ms delay)
    - Filter: "All books" vs "Indexed only" (entity_count > 0)
    - Backend availability indicator (online/offline status)
    - PWA install prompt with "Add to Home Screen" button
    - Empty states for no books/no indexed books
  - **GraphClient Updates:**
    - `graphClient.ts` (185 lines total, +65 lines) — New Calibre integration
    - `CalibreBook` interface: calibre_id, title, author, path, format, cover_url, file_url, entity_count, indexed
    - `BooksResponse` interface for paginated results
    - `getBooks(search?)` method for catalog retrieval
    - `getBookCoverUrl(calibre_id)` helper for cover images
    - `getBookFileUrl(calibre_id)` helper for epub/pdf download
  - **State Management:**
    - `flowStore.ts` (154 lines, +7 lines) — Enhanced journey tracking with Calibre context
  - **Styling System:**
    - `App.css` (34 lines) — Loading screen, library layout, responsive grid
    - `index.css` (32 lines) — Global resets, design system imports, font loading
    - `LibraryBrowser.css` (413 lines) — Complete library UI with header, grid, cards, filters
  - **Assets:**
    - `/public/icons/icon.svg` (39 lines) — Brain icon with gradient
    - `/public/icons/icon-192.png`, `icon-512.png` — PWA icons
    - `/public/apple-touch-icon.png` — iOS home screen icon
  - **Performance Optimizations:**
    - Manual chunk splitting: `react-vendor`, `epub-vendor` bundles
    - Lazy image loading with skeleton states
    - Memoized BookCard components
    - Service worker caching strategies per content type
  - **Mobile Support:**
    - `vite dev --host` exposes dev server on network for mobile testing
    - Responsive breakpoints: 480px (mobile), 768px (tablet), 1024px (desktop)
    - Touch-friendly card interactions
    - Bottom-sheet style Flow Panel on mobile (future: Wave 2)
  - **Code Quality:**
    - TypeScript strict mode throughout
    - Accessibility: ARIA labels, semantic HTML, keyboard navigation
    - Error boundaries: offline handling, missing covers, backend unavailable
    - Loading states: skeletons, spinners, connection indicators
  - **Line Count Breakdown:**
    - TypeScript: 1,368 lines (12 files)
    - CSS: 1,308 lines (6 files)
    - Total: 2,676 lines in `ies/reader/src/`
  - **Impact:** IES Reader is now a fully installable PWA with offline reading support, Calibre library integration, and professional UX matching IES Design System
  - **Wave 1 Success Criteria Met:**
    - ✅ Calibre library browser with search/filter
    - ✅ PWA installable with service worker caching
    - ✅ IES Design System applied throughout
    - ✅ Responsive layout (mobile/tablet/desktop)
    - ✅ Production-ready code quality
- **Tauri Dynamic Import Pattern (Dec 6)** — Fixed static Tauri imports breaking web mode across auth and settings:
  - `.worktrees/readest/readest/apps/readest-app/src/app/auth/utils/nativeAuth.ts`: Removed static `import { type as osType }`, replaced with dynamic `await import('@tauri-apps/plugin-os')` inside `authWithSafari()` function (lines 13-14)
  - `.worktrees/readest/readest/apps/readest-app/src/app/auth/utils/appleIdAuth.ts`: Same pattern in `getAppleIdAuth()` function (lines 27-28)
  - `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/KOSyncSettings.tsx`: Dynamic import inside `getOsName()` async function with fallback to `getOSPlatform()` for web (lines 91-92)
  - **Problem:** Static Tauri imports execute module-level code requiring Tauri APIs, causing crashes when running in browser context (`pnpm dev` for web debugging)
  - **Solution:** Dynamic imports `await import('@tauri-apps/plugin-os')` only execute when functions are called in actual Tauri environment
  - **Pattern:** Move Tauri imports inside async functions that only run in Tauri context, with graceful fallback for web
  - **Impact:** Readest can now run in both Tauri (desktop/mobile apps) and web modes without crashes
  - **Related:** Follows same pattern as `nativeAppService.ts` (commit 51b8ee3) and `environment.ts` (commit 7c9ca46) for Tauri/web compatibility
- **✅ Readest Remediation Complete (Dec 5-6)** — All critical bugs fixed, core UX features implemented:
  - `.worktrees/readest/TASK.md`: Status updated to REMEDIATION COMPLETE (Dec 5-6)
  - **BUG-R01 Fix:** Event listener memory leak resolved with proper cleanup (FoliateViewer.tsx lines 102-113)
    - Implemented `iframeDocsRef` Map tracking for all iframe documents and their event listeners
    - Added cleanup function in useEffect to remove all 9 event listener types (keydown, keyup, mousedown, mouseup, click, wheel, touchstart, touchmove, touchend)
    - Prevents memory accumulation during book navigation and page rendering
  - **All Priority 1 bugs resolved:** BUG-R01 (memory leak), BUG-R02 (regex performance), BUG-R03/R04 (AbortController), BUG-R05 (singleton stale config)
  - **All Priority 2 UX features complete:** Entity highlights clickable, question response input, journey breadcrumbs visible, state persistence
  - **Priority 3 design system integration:** IES design system imported, entity colors aligned, typography applied
  - **Success criteria met:** Thinking partnership (questions interactive), ADHD-friendly (entity overlay), virtuous cycle (journey tracking), design cohesion (IES system)
  - **Impact:** Readest Layer 4 now production-ready for user testing
- **Session API Refinements** — Enhanced session processing for improved entity extraction and schema alignment:
  - `ies/backend/src/ies_backend/api/session.py`: Updated endpoint documentation and type hints (200 lines)
  - `ies/backend/src/ies_backend/schemas/entity.py`: Enhanced entity schemas with session context support (200 lines)
  - `/session/end` endpoint: Returns `SessionEndResponse` with enhanced fields (entities_created, entities_updated, key_insights, open_questions)
  - Integration: ForgeMode session completion flow uses updated schemas for concept extraction wizard
  - Fields: `doc_id`, `entities_extracted` (count), `summary` (key insights), plus detailed entity/insight lists for UI display
- **SiYuan Plugin Structure Refinements** — Enhanced domain-agnostic configuration and session document metadata:
  - `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts`: Updated session document creation with ShapingBlockMeta support (769 lines)
  - **10-folder structure complete:** Added `/System/` folder with Templates and Example_Notes subfolders (Package's 07_System)
  - **Backend health check fix:** Aligned `BackendHealth` interface with Dashboard expectations (`ok`, `backendUrl`, `checkedAt`, `message` fields)
  - **Notebook preferences:** Added 'IES' to default notebook names for better domain-agnostic alignment
  - **Error handling enhancement:** `callBackendApi()` now properly throws errors instead of returning null, with detailed logging
  - **Purpose:** Completes merged architecture with full Package 07_System layer, fixes health check interface mismatch
- **ForgeMode Interactive Question-Response System (Phase 4 Remediation)** — Implements active cognitive guidance instead of passive question display:
  - `.worktrees/siyuan/ies/plugin/src/views/ForgeMode.svelte`: Complete interactive question-response workflow (1400+ lines)
  - **Question-response card:** `.question-response-card` component with class-specific colored borders, expandable hint section, textarea for user response
  - **Cognitive hints:** `QUESTION_CLASS_HINTS` provides class-specific guidance prompts (e.g., Schema-Probe: "Try listing the main categories, components, or buckets")
  - **Response starters:** Optional sentence starters to reduce friction (e.g., "The main parts are...", "This happens because...")
  - **Interactive flow:** User sees question → expands for hints → types response → submits → AI processes response → generates follow-up
  - **Session tracking:** Question-response exchanges captured in `questionResponseHistory` for transcript inclusion
  - **Impact:** Addresses critical finding "Questions displayed passively" — questions now drive active dialogue with cognitive scaffolding
  - **UI styling:** Complete CSS system (~440 lines) with `.qrc-header`, `.qrc-question`, `.qrc-hint`, `.qrc-input`, `.qrc-starter`/`.qrc-skip`/`.qrc-respond` buttons
- **Flow Mode Backend Implementation (Commits 4889fed, 4ad076d)** — Complete backend services for capture → thinking → flow visualization pipeline:
  - **Implementation Plan:** `docs/plans/2025-12-05-flow-mode-implementation-plan.md` — Three-layer loop architecture (ephemeral capture → structured thinking → visual flow)
  - **New API Endpoints:** Three new routers registered in `ies/backend/src/ies_backend/main.py`
    - `/capture` — Quick capture queue management (create, list, update, delete, process)
    - `/thinking` — Thinking session lifecycle (start, step, complete)
    - `/flow` — Flow session lifecycle (openFromSession, step, synthesize, journey)
  - **CaptureService:** `ies/backend/src/ies_backend/services/capture_service.py` (220 lines) — Capture queue management
    - `create_capture()` — Creates CaptureItem node in Neo4j with status tracking
    - `list_captures(status)` — Retrieves captures filtered by status (queued, in_thinking, integrated)
    - `update_capture()` — Updates status, entities, topics during processing
    - `process_capture()` — Legacy endpoint for intelligent content routing
    - Schema creation: `CaptureItem` nodes with raw_text, source, status, context_snippet, entities, topics
  - **ThinkingService:** `ies/backend/src/ies_backend/services/thinking_service.py` (215 lines) — Structured thinking sessions
    - `start_session()` — Creates ThinkingSession node linked to CaptureItem, updates capture status to in_thinking
    - `record_breadcrumb()` — Tracks user thinking steps (angles, insights) during session
    - `complete_session()` — Marks session complete, updates capture status to integrated
    - Schema creation: `ThinkingSession` nodes with capture_id, siyuan_note_id, angles, entities, breadcrumbs
  - **FlowSessionService:** `ies/backend/src/ies_backend/services/flow_session_service.py` (342 lines) — Flow lifecycle and synthesis
    - `open_from_thinking_session()` — Creates FlowSession node in Neo4j, fetches initial graph view, links to ThinkingSession
    - `record_step()` — Updates breadcrumbs, visited_nodes, visited_edges during exploration
    - `generate_synthesis()` — Uses Claude Sonnet 4 to synthesize insights from journey breadcrumbs
    - Schema creation: `FlowSession` nodes with origin, visited tracking, breadcrumbs, insights
    - Integration: Connects ThinkingSession → FlowSession via `FROM_THINKING` relationship
  - **Schemas:** Complete Pydantic schemas for all three layers
    - `ies/backend/src/ies_backend/schemas/capture.py` — CaptureItem, CaptureCreateRequest, CaptureStatus enum, CaptureSource enum
    - `ies/backend/src/ies_backend/schemas/thinking.py` — ThinkingSession, Angle, Breadcrumb, ThinkingStatus enum
    - `ies/backend/src/ies_backend/schemas/flow_session.py` — FlowSession, FlowOrigin, FlowInitialView, GraphNode, GraphEdge, RecommendedPath
  - **Tests:** `ies/backend/tests/test_thinking_and_flow.py` (265 lines) — 5 tests for full capture → thinking → flow pipeline (all passing)
    - `test_create_capture` — Validates capture creation with entities and topics
    - `test_start_thinking_session` — Validates session creation linked to capture
    - `test_complete_thinking_session` — Validates breadcrumb tracking and completion
    - `test_open_flow_from_session` — Validates flow session creation from thinking session
    - `test_record_flow_step` — Validates breadcrumb tracking during flow exploration
  - **Test Results:** 94/94 backend tests passing (11 new tests: 6 capture, 5 thinking/flow)
  - **Key Design:** Flow doesn't start from zero - it starts from a Spark (current context, highlight, thought) → structured processing → graph exploration
  - **Three-Layer Loop:**
    1. Ephemeral Capture — Quick spark capture without derailing current task (CaptureItem with status: queued)
    2. Structured Thinking Session — AI-prompted meaning extraction from captures (ThinkingSession with angles, breadcrumbs)
    3. Visual Flow Exploration — Graph-based exploration from integrated captures (FlowSession with journey synthesis)
  - **Data Flow:** CaptureItem (queued → in_thinking → integrated) → ThinkingSession (angles, breadcrumbs, entities) → FlowSession (origin, visited nodes/edges, synthesis)
- **Architecture Merge Phase 1: Foundation Implementation (Commit 30df4d6)** — Merged architecture implemented in SiYuan plugin TypeScript layer:
  - **New Block Schema Types:** `.worktrees/siyuan/ies/plugin/src/types/blocks.ts` — Complete TypeScript definitions (272 lines)
    - **Two status systems:** `CaptureStatus` type (AI: raw→classified→processed) and `UserStatus` type (user: captured→exploring→anchored)
    - **Six formal block types:** `BlockType` union (seed, shaping, map, concept, decision, log_entry)
    - **Seven seedling idea types:** `IdeaType` union (question, insight, observation, moment, schema, contradiction, what_if, other)
    - **ADHD extensions:** `ResonanceSignal` enum (8 signals: Spark, Curiosity, Delight, Concern, Tension, Dread, Clarity, Stuck), `EnergyLevel` enum (3 levels: Low, Medium, High)
    - **Clarity/Confidence levels:** `ClarityLevel` (fuzzy, partial, clear), `ConfidenceLevel` (low, medium, high) for tracking idea maturity
    - **Capture system types:** `CaptureChannel` (phone, readest, web, voice, other), `CaptureSource` (ios_shortcut, readest, browser_extension, mcp_tool, manual)
    - **Metadata interfaces:** `BaseMeta` (shared fields), `QuickCaptureMeta` (captures), `SeedBlockMeta` (seedlings), `ShapingBlockMeta` (dialogue), `MapBlockMeta` (visual), `ConceptBlockMeta` (canonical), `DecisionBlockMeta` (projects), `LogEntryMeta` (activity)
    - **Helper constants:** `IDEA_TYPE_LABELS` (human-readable), `IDEA_TYPE_ICONS` (emoji), `CAPTURE_STATUS_LABELS`, `USER_STATUS_LABELS`, `SEEDLING_FOLDER_MAP` (type → folder path)
    - **Union type:** `BlockMeta` covers all possible metadata schemas for type safety
  - **Merged Folder Structure:** `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts` — Updated STRUCTURE_FOLDERS array (71 lines)
    - **9 top-level folders implemented:** Daily, Seedlings (with 7 subcategories), Sessions (5 modes), Flow_Maps, Concepts, Insights, Favorite_Problems, Projects, Archive
    - **Seedling subfolders:** Questions, Observations, Moments, Schemas, Contradictions, What_Ifs, Insights (raw "aha" moments)
    - **Session mode folders:** Learning, Articulating, Planning, Ideating, Reflecting
    - **Dual Insights design:** Seedlings/Insights (raw) vs /Insights/ (promoted/validated)
    - **Domain-agnostic notebook preferences:** Maintained `getPreferredNotebookNames()` with settings store integration
    - **Backend integration preserved:** `callBackendApi()`, health checking, personal graph functions all intact
  - **Plugin Lifecycle Updated:** `.worktrees/siyuan/ies/plugin/src/index.ts` — Auto-folder creation temporarily disabled (line 76 comment)
    - User requested pause for manual notebook reorganization before auto-creation runs
    - Will re-enable via uncommenting `ensureNotebookStructure()` call after cleanup
    - Plugin instance passing to Dashboard for settings persistence maintained
  - **Implementation Status:** Foundation complete (types + folder structure + imports), UI components next phase
  - **Design Documents:**
    - `docs/plans/2025-12-05-siyuan-architecture-merge-design.md` — Complete merge strategy (301 lines)
    - `docs/ARCHITECTURE-COMPARISON.md` — Detailed comparison analysis (556 lines)
    - `AGENTS.md` — Repository guidelines with IES SiYuan Architecture expert context
  - **Next Phase:** UI Components (Quick Capture Queue sidebar, Process workflow, Seedling type selection)
  - **Preserved ADHD Features:** energy_level, resonance_signal, exploration_visits, backend linking (be_id, be_type)
- **SiYuan Architecture Merge Design (Commit 4ce8b11)** — Design decisions for merging IES Architecture Package with current implementation:
  - **Design Document:** `docs/plans/2025-12-05-siyuan-architecture-merge-design.md` — Complete merge strategy (301 lines)
  - **Comparison Analysis:** `docs/ARCHITECTURE-COMPARISON.md` — Detailed gap analysis (486 lines) comparing architectures
  - **Key Decision:** Hybrid merge preserving ADHD features while adopting Quick Capture system
  - **Two Status Fields:** `capture_status` (AI: raw→classified→processed) vs `status` (user: captured→exploring→anchored)
  - **Metadata Storage:** Both YAML frontmatter AND SiYuan attributes (synced) — YAML for readability, attributes for SQL queries
  - **Implementation Priority:** Foundation (STRUCTURE_FOLDERS, Quick Capture schema, status lifecycle) → UI Components (Queue sidebar, Process workflow, Seedling type selection) → Templates → Integration
- **SiYuan Architecture Evolution Package** — New comprehensive 7-layer structure proposal with formal block schemas and Quick Capture system:
  - **Documentation:** `docs/ARCHITECTURE-COMPARISON.md` — Complete comparison matrix (486 lines) between current implementation and new architecture package
  - **Reference Implementation:** `IES_SiYuan_Architecture_Package_QuickCaptureUpdated/` — Templates, schemas, and directives for evolved structure
  - **Key Shift:** From emotional resonance capture (sparks) to cognitive atomic units (seedlings) with structured processing workflows
  - **New 7-Layer Structure:**
    1. `/00_Inbox/` — Ephemeral capture with Quick Capture system (status: raw → classified → processed)
    2. `/01_Seedlings/` — Atomic ideas in 7 categories (Observations, Questions, Contradictions, What_Ifs, Insights, Moments, Schemas)
    3. `/02_Shaping/` — Dialogue-mode guided questioning (Dialogue Sessions, Cognitive Excavations, Internal Models, Mini Syntheses)
    4. `/03_Flow_Maps/` — Non-linear exploration (Perspectives, Concept Maps, Systems, Schemas, Timelines)
    5. `/04_Concepts/` — Canonical knowledge graph with 11 domain folders (IES, Emotion, Cognition, ADHD, Therapy, Self, Motivation, Other_People, Environment, Tools, Systems)
    6. `/05_Projects/` — Active work structures (8-page template: README, Goals, Questions, Plan, Status, Decisions, Research, Maps, Logs)
    7. `/06_Archive/` — Retired/superseded material with reasons and dates
    8. `/07_System/` — Meta-layer (Templates, Example Notes, Block Schemas, Quick Capture Schema, AI Directives, Dataflow docs)
  - **6 Formal Block Schemas:** seed-block (atomic ideas), shaping-block (dialogue segments), map-block (visual representations), concept-block (canonical definitions), decision-block (project decisions), log-entry-block (activity records)
  - **Quick Capture System (Defining Feature):**
    - Status lifecycle: raw (just landed) → classified (AI metadata added) → processed (user decided placement)
    - AI boundaries: Automatic (add auto_summary, auto_labels, linked_concepts) vs. Interactive (move blocks, split seedlings, attach to projects, mark processed)
    - Capture channels: phone, Readest, web, voice, other
    - Schema fields: quick_capture, capture_channel, capture_source, capture_time, capture_status, auto_summary, auto_labels, linked_concepts, optional book metadata
  - **Migration Strategy:** Hybrid approach preserving ADHD-friendly features (energy levels, resonance signals, backend API integration, Question Engine) while adding Quick Capture lifecycle, Seedling types, formal block schemas, Project structure, Flow Maps, Archive system
  - **Implementation Priority:** Foundation (update STRUCTURE_FOLDERS, add Quick Capture schema, status lifecycle) → UI Components (Quick Capture Queue sidebar, "Process this capture" workflow, Seedling type selection) → Templates (port Markdown templates, Concept Page structure, Flow Map templates) → Integration (backend APIs, AI classification, health checks)
- **Interactive Thinking Partner Questions (Readest)** — Expandable question-response system with journey tracking:
  - `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/QuestionsSection.tsx` — Interactive Q&A with journey tracking (210 lines)
  - **Expandable questions:** Click to reveal textarea for response input (useState expandedIndex tracking)
  - **Response submission:** Cmd/Ctrl+Enter shortcut (handleKeyDown), tracks exchanges in journey breadcrumb
  - **Question types:** Visual labels for clarifying/connecting/challenging questions with type-specific styling
  - **Bookmark feature:** Save questions as journey marks for later reflection (addJourneyMark)
  - **Submitted responses tracked:** UI shows submitted answers in green success card, clears input after submission
  - **Auto-focus:** Textarea automatically focused when question expanded (useRef with setTimeout)
  - **Related entities:** Shows related entity chips when question has relatedEntities array
  - **Integration:** Questions section in FlowPanel.tsx shows thinking partner questions from backend
- **Journey Breadcrumb Visualization (Readest)** — Makes invisible knowledge journeys visible and navigable:
  - `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/JourneyBreadcrumb.tsx` — Shows last 5 journey steps with entity names, dwell time, overflow count (98 lines)
  - **Step navigation:** Click any breadcrumb step to revisit that entity in Flow panel (handleStepClick function)
  - **Dwell time display:** Inline time indicators (seconds/minutes) show engagement per entity with LuClock icon
  - **Journey marks counter:** Displays count of saved notes/annotations/questions from exploration
  - **Overflow handling:** Shows "+N more" when journey path exceeds 5 steps
  - **Integration:** Integrated into FlowPanel.tsx with LuRoute icon header section
  - **Purpose:** Addresses UX gap where journeys were tracked but never shown to user
- **Flow Panel Component Reorganization (Readest)** — Clean module structure for Flow panel subsystems:
  - `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/index.ts` — Centralized exports for 7 components
  - **Exported components:** FlowPanel, FlowPanelHeader, EntitySection, RelationshipsSection, SourcesSection, QuestionsSection, JourneyBreadcrumb
  - **Benefits:** Enables clean imports `import { FlowPanel, JourneyBreadcrumb } from './flowpanel'`, modular architecture where each section is independently fetchable and testable
  - **Integration:** ReaderContent.tsx imports FlowPanel from index, all Flow panel features accessed through single import point
- **Dashboard Energy-Based Navigation (SiYuan)** — ADHD-friendly spark filtering with dynamic backend configuration:
  - `.worktrees/siyuan/ies/plugin/src/views/Dashboard.svelte` — Energy filters (low/medium/high) and resonance filters (8 emotional signals) for mood-appropriate navigation
  - **Energy filters:** All, Low (🔋), Medium (⚡), High (🔥) with mutually exclusive selection
  - **Resonance filters:** 8 emotional signals (curious, excited, surprised, moved, disturbed, unclear, connected, validated) with emoji labels
  - **Backend health checking:** Connected/Checking/Disconnected status with manual retry, 30-second cache TTL
  - **Flow mode concept navigation:** Clicking suggestions in "Most Connected" or "Novel Concepts" passes concept name to FlowMode for pre-selected exploration
  - **API endpoints:** `/personal/sparks/by-energy/{level}`, `/personal/sparks/by-resonance/{signal}` for filtered spark retrieval
  - **Empty state handling:** Shows friendly message when filters return no results with "Show all sparks" option
- **Complete Entity Click-to-Flow Interaction System (Readest)** — Full event loop from text overlay to exploration:
  - `.worktrees/readest/readest/apps/readest-app/src/app/reader/hooks/useEntityClick.ts` — Event listener hook handles entity-click events from iframe content (88 lines)
  - **Event flow:** Entity highlighted → User clicks → Event dispatched → Flow panel opens → Entity fetched → Journey step added
  - **Temporary display:** Shows "Loading..." while fetching full details from knowledge graph
  - **Graceful fallback:** If entity not in graph, displays helpful message explaining extraction status
  - **Integration points:**
    - useEntityClick() called in ReaderContent.tsx (line 52) to wire up event handling
    - iframeEventHandlers.ts dispatches 'entity-click' events from iframe content
    - useFlowEntity.ts hook provides entity search/fetch capabilities
    - graphClient.ts handles backend API calls for entity data
    - flowModeStore.ts manages state: currentEntity, journey steps, loading states
  - **Critical bug fix (BUG-R03):** AbortController pattern prevents memory leaks from cancelled entity fetches
  - Works with entity transformer overlay system for seamless click-to-explore experience
- **Entity Transformer Performance Fix (Readest)** — Eliminated catastrophic backtracking with trie-based matching:
  - `.worktrees/readest/readest/apps/readest-app/src/services/transformers/entity.ts` — Trie-based entity matching prevents O(n*m) catastrophic backtracking (BUG-R02)
  - **buildEntityTrie():** Constructs case-insensitive trie from entity names supporting multi-word phrases
  - **processTextWithTrie():** Linear O(n) text scan with efficient phrase matching
  - **Multi-word support:** Handles "executive function", "cognitive behavioral therapy" etc.
  - **Longest match preference:** Trie prioritizes longer entity names when overlapping
  - **Impact:** Eliminates browser freezes when highlighting books with 100+ entities (previously caused 5-10 second hangs)
  - **Algorithm change:** From regex alternations `(entity1|entity2|...)` (exponential) to token-based trie lookup (linear)
- **Journey Breadcrumb Visualization (Readest)** — Makes invisible knowledge journeys visible and navigable:
  - `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/JourneyBreadcrumb.tsx` — Shows last 5 journey steps with entity names, dwell time, overflow count (98 lines)
  - **Step navigation:** Click any breadcrumb step to revisit that entity in Flow panel (handleStepClick function)
  - **Dwell time display:** Inline time indicators (seconds/minutes) show engagement per entity with LuClock icon
  - **Journey marks counter:** Displays count of saved notes/annotations/questions from exploration
  - **Overflow handling:** Shows "+N more" when journey path exceeds 5 steps
  - **Integration:** Integrated into FlowPanel.tsx with LuRoute icon header section
  - **Purpose:** Addresses UX gap where journeys were tracked but never shown to user
- **Interactive Thinking Partner Questions (Readest)** — Expandable question-response system with journey tracking:
  - `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/QuestionsSection.tsx` — Interactive Q&A with journey tracking (210 lines)
  - **Expandable questions:** Click to reveal textarea for response input (useState expandedIndex tracking)
  - **Response submission:** Cmd/Ctrl+Enter shortcut (handleKeyDown), tracks exchanges in journey breadcrumb
  - **Question types:** Visual labels for clarifying/connecting/challenging questions with type-specific styling
  - **Bookmark feature:** Save questions as journey marks for later reflection (addJourneyMark)
  - **Submitted responses tracked:** UI shows submitted answers in green success card, clears input after submission
  - **Auto-focus:** Textarea automatically focused when question expanded (useRef with setTimeout)
  - **Related entities:** Shows related entity chips when question has relatedEntities array
  - **Integration:** Questions section in FlowPanel.tsx shows thinking partner questions from backend
- **Flow Panel Component Reorganization (Readest)** — Clean module structure for Flow panel subsystems:
  - `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/index.ts` — Centralized exports for 7 components
  - **Exported components:** FlowPanel, FlowPanelHeader, EntitySection, RelationshipsSection, SourcesSection, QuestionsSection, JourneyBreadcrumb
  - **Benefits:** Enables clean imports `import { FlowPanel, JourneyBreadcrumb } from './flowpanel'`, modular architecture where each section is independently fetchable and testable
  - **Integration:** ReaderContent.tsx imports FlowPanel from index, all Flow panel features accessed through single import point
- **Dashboard Energy-Based Navigation (SiYuan)** — ADHD-friendly spark filtering with dynamic backend configuration:
  - `.worktrees/siyuan/ies/plugin/src/views/Dashboard.svelte` — Energy filters (low/medium/high) and resonance filters (8 emotional signals) for mood-appropriate navigation
  - **Energy filters:** All, Low (🔋), Medium (⚡), High (🔥) with mutually exclusive selection
  - **Resonance filters:** 8 emotional signals (curious, excited, surprised, moved, disturbed, unclear, connected, validated) with emoji labels
  - **Backend health checking:** Connected/Checking/Disconnected status with manual retry, 30-second cache TTL
  - **Flow mode concept navigation:** Clicking suggestions in "Most Connected" or "Novel Concepts" passes concept name to FlowMode for pre-selected exploration
  - **API endpoints:** `/personal/sparks/by-energy/{level}`, `/personal/sparks/by-resonance/{signal}` for filtered spark retrieval
  - **Empty state handling:** Shows friendly message when filters return no results with "Show all sparks" option
- **Domain-Agnostic Notebook Configuration (SiYuan)** (commit 5e3ad8b) — Removed hardcoded therapy-specific notebook names:
  - `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts`: Replaced `PREFERRED_NOTEBOOK_NAMES` with `DEFAULT_NOTEBOOK_NAMES` and `getPreferredNotebookNames()`
  - **User-configurable preferences:** Users can customize via localStorage `ies.preferredNotebooks` as JSON array
  - **Default names now domain-agnostic:** "Personal", "Knowledge", "Notes", "Intelligent Exploration System" (removed "Therapy", "Therapy Framework", "Framework Project")
  - **Backward compatible:** Falls back to defaults if localStorage is unavailable or parse fails
  - **Improved health checking:** Added `BackendHealth` interface, `cachedHealthStatus` variable, and `HEALTH_CACHE_TTL_MS` constant (30 seconds)
  - **Backend URL context comments:** Added clarification that SiYuan runs in Docker on 192.168.86.60, forwardProxy makes requests FROM container using host IP
  - **Question class tracking in sessions:** Added `questionClassesUsed?: string[]` field to `SessionDocumentOptions` interface
  - **Session document frontmatter:** Sessions now include `question_classes_used` array in YAML frontmatter when question classes are tracked
  - **Impact:** Plugin now works across any domain without therapy-specific assumptions, aligns with project goal of domain-agnostic architecture
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

---

### 📚 Detailed Architecture Documentation

**Full architecture documentation lives in SiYuan for better organization and searchability.**

> **📖 Access:** Open SiYuan → IES notebook → `/System/` folder
> - **Backend API Reference** — All 6 backend APIs with endpoints, schemas, and integration points
> - **Knowledge Graph Architecture** — Domain vs Personal graph systems, entity types, relationships
> - **Calibre Integration** — Book catalog, ingestion pipeline, Readest library browser
> - **SiYuan Plugin Architecture** — Folder structure, block types, ForgeMode, Dashboard

**Quick Reference (for immediate context):**

| System | Purpose | Key Files |
|--------|---------|-----------|
| Domain Graph | Books/research (179 books, 291 entities) | `library/graph/neo4j_client.py` |
| Personal Graph | ADHD-friendly sparks/insights | `library/graph/adhd_graph_client.py` |
| Backend APIs | 6 routers: reframe, personal, template, question-engine, books, concepts | `ies/backend/src/ies_backend/api/` |
| SiYuan Plugin | 9-folder structure, 6 block types, ForgeMode | `.worktrees/siyuan/ies/plugin/` |
| Calibre | Single source of truth, calibre_id universal | `scripts/ingest_calibre.py` |

### Layer 3 & 4: SiYuan + Readest Architecture

> **📖 See SiYuan:** IES notebook → `/System/SiYuan Plugin Architecture`
>
> Covers: 9-folder structure, 6 block types, Dashboard energy navigation, Settings panel, ForgeMode, Question Engine integration

---

### Layer 2: Backend APIs

> **📖 See SiYuan:** IES notebook → `/System/Backend API Reference`
>
> Covers: Reframe API, Personal Graph API, Template API, Question Engine API, Books API, Concept API

---

### Calibre Integration

> **📖 See SiYuan:** IES notebook → `/System/Calibre Integration`
>
> Covers: Book catalog (179 books), ingestion pipeline, Readest library browser, calibre_id universal identifier

<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: conventions -->
<!-- This section will be automatically updated by auto-memory plugin -->
<!-- END AUTO-MANAGED -->