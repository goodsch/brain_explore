<!-- MANUAL -->
# brain_explore — Intelligent Exploration System

A four-layer thinking partnership tool: Knowledge Graph → Backend APIs → SiYuan Plugin → IES Reader

## Current State

**Phase:** 3 - Remediation ✅ COMPLETE
**Health:** A → Highly Functional — All 5 Waves Complete
**Current Wave:** All waves complete (1-5)

### Wave 1 Blockers RESOLVED ✅
1. ~~THREE Neo4j clients~~ → `UnifiedGraphClient` (47 methods)
2. ~~User ID fragmented~~ → `/profile/login` endpoint
3. ~~Sessions lost on restart~~ → Redis-backed `SessionStore`

### Wave 2 Blockers RESOLVED ✅
4. ~~Frontend-backend wiring incomplete~~ → Both IES Reader and SiYuan now save journeys
5. ~~Cross-app sync design missing~~ → Design doc complete

### Wave 3 Blockers RESOLVED ✅
6. ~~No Journey UI for history view~~ → Dashboard shows recent journeys + synthesis endpoint
7. ~~No question feedback capture~~ → FeedbackService with Neo4j persistence
8. ~~No offline sync support~~ → Offline queues + sync indicators in both apps

### Wave 4 Blockers RESOLVED ✅
9. ~~No profile learning~~ → `apply_observation()` tracks engagement, updates hyperfocus_triggers
10. ~~No question selection optimization~~ → `get_user_effective_classes()` returns weighted preferences
11. ~~No reframe adaptation~~ → `get_user_reframe_preferences()` personalizes prompts

### Remaining Blockers
~~12. Zero test coverage on 4 critical services~~ → Wave 5 COMPLETE (63 new tests, 185 total)

### Next Phase: Enhancement
**Status:** Planning - FlowMode transformation from graph browser to Thinking Partnership Engine
**Plan:** `docs/plans/2025-12-06-flowmode-enhancement-plan.md`

**Key Initiatives:**
1. **Spark-based initiation** - Flow starts from context (notes, highlights, captures), never blank
2. **4-phase state machine** - Orientation → Branching → Deepening → Synthesis
3. **Synthesis artifacts** - Produces structured notes, diagrams, questions for SiYuan integration
4. **Visual exploration** - Multiple views (Trail, Map, Matrix, Timeline) for same data

**Reference:** See FlowMode plan for 7 phases across 3 waves (4-6 weeks total)

### Completed Plans
- Remediation: `docs/plans/2025-12-06-comprehensive-remediation-plan.md`
- IES Reader switch: `docs/plans/2025-12-06-readest-to-ies-reader-amendment.md`

### Active Design Work
- **Inbox System:** Phase 1-2 complete (queue + iOS integration + collaborative dialogue), Phase 3-4 remaining (browser/voice capture)
- **FlowMode Wave 1:** ✅ COMPLETE — Context-aware Flow initiation (Dec 6, 2025)
  - Context tracking store, context menu integration, Dashboard "Continue Exploring" section
  - Commit: 336470c (siyuan worktree), f949d54 (flowmode worktree)

### Recent Changes (Dec 6, 2025)

**FlowMode Wave 1: Context-Aware Flow Initiation** ✅ COMPLETE

Implemented spark-based Flow initiation replacing blank-slate exploration:

**Backend Schema Work:**
- `/home/chris/dev/projects/codex/brain_explore/ies/backend/src/ies_backend/schemas/inbox.py` (200 lines):
  - Added `SparkType` enum: NOTE, SELECTION, HIGHLIGHT, THOUGHT
  - Added `SparkSource` model with metadata for all spark types (note_id, block_ids, book_id, location)
  - Added `Spark` model representing live context that Flow latches onto
  - Integration with existing InboxItem schema for capture-based sparks

**Backend API Updates:**
- `/home/chris/dev/projects/codex/brain_explore/ies/backend/src/ies_backend/api/inbox.py` (110 lines):
  - Enhanced with dialogue endpoints: `POST /{inbox_id}/message`, `POST /{inbox_id}/resolve`
  - Full CRUD: create, list (with status filter), get, update, delete
  - Dual mounting: `/inbox/*` (canonical) + `/capture/*` (backward compat)
  - Resolution actions: link_to_concept, create_note, add_to_note, explore_in_flow, link_to_journey

**Backend Service Layer:**
- `/home/chris/dev/projects/codex/brain_explore/ies/backend/src/ies_backend/services/inbox_service.py` (970 lines):
  - InboxService with queue management and collaborative dialogue
  - AI integration: Claude Sonnet 4 for dialogue responses with fallback
  - Entity extraction with graph matching (sets `graph_match=True` flag)
  - Resolution routing to 5 destination types
  - Status lifecycle: QUEUED → IN_THINKING → INTEGRATED
  - **Bug fix (Dec 6):** `_record_to_inbox()` now correctly parses `dialogue` field from Neo4j JSON (lines 949-957, 968)

**SiYuan Plugin - Context Tracking:**
- `/home/chris/dev/projects/codex/brain_explore/.worktrees/siyuan/ies/plugin/src/stores/contextStore.ts` (193 lines NEW):
  - Svelte writable store tracking currently open note in SiYuan
  - EventBus integration: `loaded-protyle` listener captures note opens
  - Selection tracking: `selectionchange` event captures user text selections
  - `getSparkSource()` method returns spark metadata for Flow initiation
  - Derived stores: `hasNoteOpen`, `hasSelection`, `currentNoteTitle`
  - Lifecycle: `initContextTracking()` / `destroyContextTracking()`

**SiYuan Plugin - Dashboard Context UI:**
- `/home/chris/dev/projects/codex/brain_explore/.worktrees/siyuan/ies/plugin/src/views/Dashboard.svelte` (200 lines partial):
  - Imports `noteContext`, `hasNoteOpen`, `currentNoteTitle` from contextStore
  - Prepared for "Continue Exploring" section showing current note context
  - Integration point for spark-based Flow initiation from Dashboard
  - **Rename complete:** Changed QuickCapture → Inbox throughout (import, component, button title, section title)

**SiYuan Plugin - Lifecycle Integration:**
- `/home/chris/dev/projects/codex/brain_explore/.worktrees/siyuan/ies/plugin/src/index.ts` (167 lines):
  - Added `initContextTracking()` call in `onLayoutReady()` (line 77)
  - Added `destroyContextTracking()` call in `onunload()` (line 117)
  - Context menu integration prepared for "Start Flow from this note"
  - Selection menu integration prepared for "Start Flow from selection"

**SiYuan Plugin - Inbox UI:**
- `/home/chris/dev/projects/codex/brain_explore/ies/plugin/src/views/Inbox.svelte` (200 lines partial):
  - Full collaborative dialogue UI with message thread display
  - AI suggestion buttons with confidence scores and action handlers
  - Source icons: 📱 iOS Shortcut, 🌐 Browser, 🎤 Voice, 📝 SiYuan, 📖 IES Reader, ✉️ Email
  - `handleSuggestionClick()` calls `/inbox/{id}/resolve` endpoint
  - Integration with Dashboard for queue display

**Design Specification:**
- `/home/chris/dev/projects/codex/brain_explore/docs/scratch/flowmode-wave-1-spec.md` (200 lines partial):
  - PM Decisions: Trail View first, template-based synthesis, SiYuan-first approach
  - Phase 1: Contextual Awareness (EventBus, context menu, Dashboard section)
  - Phase 2: Spark-Based Initiation (SparkSource types, Orientation phase)
  - Phase 4: Basic Synthesis (template notes, SiYuan integration)
  - Complete TypeScript/Python code examples for implementation

**Implementation Status:** ✅ WAVE 1 COMPLETE
- ✅ Backend schemas complete (SparkType, SparkSource, Spark)
- ✅ Context tracking store implemented with EventBus integration
- ✅ Plugin lifecycle wired (init/destroy context tracking)
- ✅ Inbox collaborative dialogue backend complete
- ✅ Inbox UI with dialogue and resolution actions
- ✅ Dashboard "Continue Exploring" UI complete (shows when note open)
- ✅ Context menu integration ("Start Flow from this note", "Start Flow from selection")
- ✅ Backend Orientation endpoint (`POST /flow/{id}/orientation`) — via FlowMode Phase 3
- ✅ OrientationPhase in FlowMode — via FlowMode Phase 4
- ✅ Synthesis endpoint (`POST /flow/{id}/synthesize`) — via FlowMode Phase 3

**Next Steps (Wave 2):**
1. Wire orientation endpoint to SparkSelector for context-based cluster generation
2. Template-based synthesis with SiYuan note creation
3. View toggles (Trail/Map/Matrix/Timeline full implementations)

---

## Project Manager Protocol

**Claude acts as PM.** Determine all next steps autonomously. Don't ask what to work on — identify optimal action and proceed.

### Decision Framework
1. Check `/docs/scratch/` for current wave status
2. Check `/docs/plans/` for execution strategy
3. Use TodoWrite for ALL task tracking
4. Use specialized agents per wave specification
5. Create scratch documents for cross-agent communication

### Required Skills
| Skill | When to Use |
|-------|-------------|
| `superpowers:verification-before-completion` | Before ANY "done" claim |
| `superpowers:test-driven-development` | ALL code changes |
| `superpowers:systematic-debugging` | Any bug investigation |
| `superpowers:requesting-code-review` | After each task |

### Agent Usage
| Wave | Agent Type | Purpose |
|------|------------|---------|
| 1 | `backend-developer` | Neo4j, Redis, APIs |
| 2-3 | `fullstack-developer` | Frontend-backend wiring |
| 2 | `system-architect` | Cross-app sync design |
| All | `critical-evaluator` | Wave verification |

### Sequential Thinking Tools (MANDATORY SELECTION)

Three MCP servers provide sequential thinking. Use the RIGHT one:

| Scenario | Tool | Why |
|----------|------|-----|
| **Architecture/design decisions** | `mcp__clear-thought__mental_models` | Explicit frameworks (trade-off-matrix, pre-mortem) |
| **Debugging/root cause analysis** | `mcp__clear-thought__mental_models` | five-whys, rubber-duck models |
| **Risk analysis** | `mcp__clear-thought__mental_models` | adversarial-thinking, pre-mortem |
| **Complex multi-MCP workflows** | `mcp__mcp-sequentialthinking-tools__sequentialthinking_tools` | Recommends which tools to call with confidence scores |
| **Simple reasoning chains** | `mcp__sequential-thinking__sequentialthinking` | Lower overhead, no tool coordination needed |
| **JS/TS prototyping** | `mcp__clear-thought__notebook` | Execute code cells inline |

**Clear Thought Mental Models (use by tag):**
- `debugging`: rubber-duck, five-whys
- `planning`: decomposition, abstraction-laddering
- `decision-making`: trade-off-matrix, opportunity-cost
- `risk-analysis`: pre-mortem, adversarial-thinking
- `architecture`: constraint-relaxation, inversion

**DO NOT** use basic `sequentialthinking` when:
- Making architecture decisions (use mental_models)
- Orchestrating multiple MCP tools (use sequentialthinking_tools)
- Debugging failures (use mental_models with five-whys)

### External AI Tools

| Tool | Skill | Best For |
|------|-------|----------|
| **Gemini CLI** | `gemini-cli` | Architecture analysis, web research (Google Search), code review (second opinion), parallel background tasks |
| **Codex** | `skill-codex` | Deep reasoning (high effort), complex design decisions, session-resumable analysis |

**When to use external AI:**
- Second opinion on implementation → `skill: gemini-cli` for code review
- Current docs/best practices → Gemini Google Search
- Complex trade-off analysis → `skill: skill-codex` with high reasoning
- Codebase understanding → Gemini codebase_investigator

**When NOT to use:**
- Simple tasks (overhead not worth it)
- Already have context loaded
- Need immediate response (rate limits apply)

### Scratch Document Protocol
Each wave produces in `/docs/scratch/`:
- `wave-N-spec.md` — Input specification
- `wave-N-decisions.md` — Decisions during implementation
- `wave-N-blockers.md` — Issues for escalation
- `wave-N-complete.md` — Completion verification

---

## Architecture

```
Layer 1: Knowledge Graph (Neo4j + Qdrant)
├── library/graph/          # Graph clients (UNIFY THESE)
├── calibre/                # Book catalog (179 books)
└── scripts/ingest*.py      # Ingestion pipeline

Layer 2: Backend APIs (FastAPI)
├── ies/backend/src/ies_backend/api/     # 8 routers (inbox dual-mounted at /inbox + /capture)
├── ies/backend/src/ies_backend/services/ # Business logic (inbox_service.py 970 lines, thinking_service.py)
└── ies/backend/tests/                   # 194 tests (Wave 5: +63, Inbox: +9)

Layer 3: SiYuan Plugin (Svelte)
└── .worktrees/siyuan/ies/plugin/src/
    ├── views/              # ForgeMode, FlowMode, Dashboard
    └── utils/              # Backend integration

Layer 4: IES Reader (React + Vite) — REPLACES READEST
└── ies/reader/src/
    ├── components/         # Reader, FlowPanel
    ├── hooks/              # useEntityLookup
    ├── services/           # graphClient (backend integration)
    └── store/              # flowStore (Zustand state management)
```

---

## Essential Commands

```bash
# Services
docker compose up -d              # Start Neo4j, Qdrant, SiYuan
cd ies/backend && uv run uvicorn ies_backend.main:app --reload --port 8081

# Testing
cd ies/backend && uv run pytest   # Backend tests (122)

# Frontend Clients
cd ies/reader && npm run dev -- --host  # IES Reader (http://localhost:5173)
cd .worktrees/siyuan/ies/plugin && pnpm build  # SiYuan plugin

# Git
git status && git log --oneline -5  # Check state
```

---

## IES Reader (Standalone App)

**Location:** `ies/reader/`
**Tech Stack:** React 19 + Vite + TypeScript + Zustand
**Purpose:** Lightweight EPUB reader with knowledge graph integration

### Key Features
- EPUB reading via `react-reader` (epubjs wrapper)
- Text selection triggers entity lookup in knowledge graph
- Flow Panel with entity details, relationships, sources
- Journey tracking (breadcrumb trail of explored entities)
- Thinking Partner questions generated per entity

### Architecture
```
ies/reader/
├── src/
│   ├── App.tsx                      # Book selector + login + Reader launcher (163 lines)
│   ├── App.css                      # Book selector styling (149 lines)
│   ├── main.tsx                     # React entry point
│   ├── index.css                    # Global styles (68 lines)
│   ├── components/
│   │   ├── Reader.tsx               # EPUB reader + toolbar + Flow toggle (125 lines)
│   │   ├── Reader.css               # Reader styling (94 lines)
│   │   └── flow/
│   │       ├── FlowPanel.tsx        # Entity exploration sidebar (174 lines)
│   │       └── FlowPanel.css        # Flow Panel styling (287 lines)
│   ├── hooks/
│   │   └── useEntityLookup.ts       # Entity search & navigation (122 lines)
│   ├── services/
│   │   ├── graphClient.ts           # Backend API client (220 lines)
│   │   └── offlineQueue.ts          # Offline operation queue (329 lines)
│   └── store/
│       └── flowStore.ts             # Zustand state manager (202 lines)
├── package.json                     # Dependencies: react 19, epubjs, zustand
├── vite.config.ts                   # Vite config with Gutenberg proxy
├── tsconfig.json                    # TypeScript config
└── index.html                       # HTML entry point
```

**Total:** ~1,933 lines of TypeScript/React code (excl. CSS)

### Backend Integration
- **Entity Search:** `GET /graph/search?q={text}`
- **Entity Details:** `GET /graph/explore/{id}`
- **Questions:** `POST /question-engine/questions`
- **Journey Save:** `POST /journeys`

### Current State (Updated: Dec 6, 2025)
**Status:** ✅ IMPLEMENTED - Full working app (commit bb221b8, 5,741 lines)

- **Reading:** Fully functional EPUB reader with Gutenberg proxy integration
  - Sample books: Alice in Wonderland, Pride & Prejudice, Frankenstein
  - Local EPUB file upload support via file picker
  - React Reader (epubjs wrapper) with location persistence
- **Entity Lookup:** Text selection triggers knowledge graph search with entity details
  - `rendition.on('selected')` event captures user selections
  - Auto-opens Flow Panel on successful entity match
- **Flow Panel:** Displays entity info, relationships, sources, and thinking partner questions
  - Resizable sidebar (default 400px width)
  - Entity type badges, summaries, relationship lists
  - Book sources with chapter/page references
  - Question cards with type indicators (clarifying/connecting/challenging)
- **Journey Tracking:** In-memory breadcrumb trail with dwell time calculation
  - Started on book open, persisted on Flow Panel close
  - Sync status indicator with offline queue support
- **Styling:** Complete UI with responsive design, hover states, and visual polish
  - Dark theme with gradient backgrounds
  - Smooth transitions and loading states
  - Accessible button states and focus indicators

### Implementation Details
**Text Selection Flow:**
1. User selects text in EPUB → `rendition.on('selected')` event fires
2. `useEntityLookup.lookupEntity()` searches backend via `graphClient.searchEntities()`
3. Entity details fetched via `graphClient.exploreEntity(id)`
4. Thinking partner questions generated via `graphClient.getThinkingPartnerQuestions()`
5. Journey step added to `flowStore` with timestamp and source passage

**State Management (Zustand):**
- `flowStore.ts` manages: current entity, relationships, sources, questions, journey tracking
- Journey includes: entry point (book title), path (entity steps), dwell time per step
- Journey can be ended and returned as `BreadcrumbJourney` object for backend persistence

### Technical Implementation

**Dependencies (package.json):**
- `react@19.2.0` + `react-dom@19.2.0` - Latest React with compiler support
- `epubjs@0.3.93` - EPUB parsing and rendering engine
- `react-reader@2.0.15` - React wrapper for epubjs with hooks API
- `zustand@5.0.9` - Lightweight state management (simpler than Redux)
- `vite@7.2.4` - Fast build tool with HMR
- `typescript@5.9.3` - Type safety across components

**Key Patterns:**
1. **Service Layer** (`services/graphClient.ts`):
   - Centralized API client with typed interfaces
   - Device ID generation for anonymous users (localStorage)
   - Backend availability check with 5s timeout
   - Offline queue integration for resilience

2. **State Management** (`store/flowStore.ts`):
   - Zustand store with typed state and actions
   - Journey lifecycle: `startJourney()` → `addJourneyStep()` → `endJourney()`
   - Dwell time calculation via timestamp deltas
   - Sync status tracking for UI feedback

3. **Offline Resilience** (`services/offlineQueue.ts`):
   - localStorage-backed queue (max 50 ops, 3 retries)
   - Exponential backoff: 5s, 30s, 2min delays
   - Operation types: journey, profile, feedback
   - Automatic processing on backend reconnect
   - Quota-exceeded handling (prunes failed ops)

4. **Entity Lookup** (`hooks/useEntityLookup.ts`):
   - Debounced search to avoid API spam
   - Parallel entity details + questions fetch
   - Journey step added on successful lookup
   - Error boundary for API failures

**Wave 3 Enhancements (Dec 6, 2025):**
- Offline queue implementation (329 lines)
- Sync status indicators in Flow Panel header
- Question feedback capture via backend API
- Click-to-retry sync for queued operations

### Outstanding Issues
- **No automated test coverage** for Flow Panel, entity lookup, or journey tracking
- **No E2E tests** for EPUB reading flow or text selection handling
- **No performance benchmarks** for large EPUBs or entity search latency

---

## Inbox (External-First Capture)

**Status:** ✅ IMPLEMENTED — Phase 1-2 Complete (Queue + Collaborative Dialogue)
**Location:** `ies/backend/src/ies_backend/services/inbox_service.py` (970 lines), `api/inbox.py` (109 lines)
**Frontend:** `ies/plugin/src/views/Inbox.svelte` (782 lines)
**Schemas:** `ies/backend/src/ies_backend/schemas/inbox.py` (338 lines)
**Design:** `docs/plans/2025-12-06-inbox-redesign.md`
**Purpose:** External-first capture system with AI-powered collaborative processing and intelligent routing

### Implementation Status

**Phase 1: Queue Management + External Capture** ✅
- InboxService with CRUD operations (create, list, update, delete)
- Dual-mounted API paths: `/inbox` (canonical) + `/capture` (backward compat)
- Neo4j persistence for InboxItem nodes with dialogue history
- Auto-extraction of entities and topics from captured text
- Status lifecycle: QUEUED → IN_THINKING → INTEGRATED
- iOS Shortcut integration for "Hey Siri, capture thought" workflow
- 9 tests passing (inbox service + flow integration)

**Phase 2: Collaborative Dialogue Processing** ✅ (Dec 6, 2025)
- AI-powered dialogue system using Claude Sonnet 4 (fallback when unavailable)
- `add_dialogue_message()` endpoint with real-time AI responses
- Contextual suggestions with confidence scores (link_to_concept, create_note, explore_in_flow, etc.)
- Graph integration: matches extracted entities against knowledge graph
- Full SiYuan UI implementation with inline dialogue, suggestion buttons, source icons
- Manual capture from within SiYuan (secondary workflow)
- **Critical bug fix:** Dialogue persistence now working (messages return from Neo4j to frontend)

**Phase 3-4: Remaining** (Planned)
- Browser extension capture (Chrome/Firefox)
- Voice capture with Whisper transcription
- Email/SMS forwarding integration

### Core Concept

**Captures rarely originate in SiYuan.** They come from external sources — iOS shortcuts, browser extensions, voice notes — at moments when the user can't process them. The Inbox is where these wait until the user has time and context to process them collaboratively.

**Design Principle:** Capture is instant and external. Processing is collaborative and contextual.

### Implemented Architecture (Phase 1-2)

**Backend Services:**
- **InboxService** (`inbox_service.py`, 970 lines):
  - **Queue Management:**
    - `create_inbox()` — Create inbox item with auto-extraction
    - `list_inbox(status)` — List by QUEUED/IN_THINKING/INTEGRATED
    - `get_inbox(id)` — Fetch single item with dialogue history
    - `update_inbox(id, request)` — Update status/metadata
    - `delete_inbox(id)` — Remove item
  - **Collaborative Dialogue (Phase 2):**
    - `add_dialogue_message(inbox_id, content)` — Add user message, get AI response with suggestions
    - `_generate_dialogue_response()` — AI analysis using Claude Sonnet 4 (model: claude-sonnet-4-20250514)
    - `_fallback_dialogue_response()` — Simple responses when AI unavailable
    - `_parse_suggestions()` — Extract action suggestions from AI response
  - **Resolution Actions:**
    - `resolve_inbox(inbox_id, request)` — Route to destination (concept, note, flow, journey)
    - `_resolve_link_to_concept()` — Create LINKED_TO relationship with concept
    - `_resolve_create_note()` — Prepare structured note with dialogue history
    - `_resolve_add_to_note()` — Append to existing SiYuan note
    - `_resolve_explore_in_flow()` — Escalate to FlowMode via ThinkingService
    - `_resolve_link_to_journey()` — Associate with active journey
  - **Entity Extraction:**
    - `process_inbox()` — Legacy quick-capture processing (preserved for backward compat)
    - `_ai_extract()` — Claude Sonnet 4 extracts entities, summary, tags
    - `_simple_extract()` — Regex-based fallback (capitalized phrases)
    - Auto-extracts entities/topics, links to knowledge graph via `MENTIONS` relationships
    - Graph matching: checks extracted entities against Neo4j concepts, sets `graph_match=True` flag

- **ThinkingService** (`thinking_service.py`, 350 lines):
  - `start_session(capture_id)` — Convert inbox item to thinking session
  - `get_session(session_id)` — Fetch session with breadcrumbs
  - `record_breadcrumb(session_id, step)` — Track exploration path
  - `complete_session(session_id, summary)` — Mark complete, integrate inbox item
  - Generates 3-5 exploration angles using AI or fallback heuristics
  - Suggests SiYuan note template with structured sections
  - Updates inbox status: QUEUED → IN_THINKING → INTEGRATED

**Data Models** (`schemas/inbox.py`, 338 lines):
- **Core Types:**
  - `InboxItem`: Queue item with raw_text, source, captured_at, status, auto_extracted, dialogue
  - `InboxStatus`: QUEUED, IN_THINKING, INTEGRATED
  - `InboxSource`: IOS_SHORTCUT, BROWSER, VOICE, EMAIL, SIYUAN, IES_READER (+ legacy: PHONE, READEST)
  - `InboxType`: TEXT, VOICE, IMAGE, LINK (capture content type)
  - `PlacementType`: NOTE, CONCEPT, JOURNEY, NEW_NOTE (routing destinations)
- **Dialogue System:**
  - `DialogueMessage`: role (user/assistant), content, timestamp, suggestions[]
  - `DialogueSuggestion`: label, action, target_id, target_name, confidence
  - `DialogueRole`: USER, ASSISTANT
- **Resolution:**
  - `ResolutionAction`: LINK_TO_CONCEPT, CREATE_NOTE, ADD_TO_NOTE, EXPLORE_IN_FLOW, LINK_TO_JOURNEY
  - `ResolveRequest`: action, target_id, target_name
  - `ResolveResponse`: success, action, message, target_id, note_id
- **Additional:**
  - `Spark`: Live context that Flow latches onto (note, selection, highlight, thought)
  - `AutoExtracted`: Entities and topics extracted from text
  - `ExtractedEntity`: name, type, confidence, graph_match flag
  - `SuggestedPlacement`: target_type, target_id, confidence, preview, rationale
  - `InboxProcessRequest/Response`: AI-powered processing (legacy endpoint preserved)

**API Endpoints** (`api/inbox.py`, 109 lines):
Dual-mounted for migration: `/inbox/*` (canonical) + `/capture/*` (backward compatible)

- **Queue Management:**
  - `POST /inbox` — Create inbox item (external sources use this)
  - `GET /inbox?status={status}` — List inbox items (default: QUEUED)
  - `GET /inbox/{id}` — Get single item with dialogue history
  - `PATCH /inbox/{id}` — Update status/metadata
  - `DELETE /inbox/{id}` — Delete item
- **Collaborative Processing (Phase 2):**
  - `POST /inbox/{id}/message` — Add user message to dialogue, get AI response with suggestions
  - `POST /inbox/{id}/resolve` — Resolve inbox item to destination (5 action types)
  - `POST /inbox/process` — Legacy AI processing endpoint (backward compat: `/capture/process`)

**SiYuan Plugin Integration:**
- **Inbox.svelte** (782 lines): Full collaborative dialogue UI
  - **Queue View:**
    - List of inbox items with source icons (📱🌐🎤📝📖✉️💡📥)
    - Time formatting (just now, Xm ago, Xh ago, date)
    - Auto-extracted entities preview
    - Manual capture via "+" button (secondary workflow)
  - **Dialogue View:**
    - Original capture preview with source icon and context snippet
    - Message thread (user/assistant with distinct styling)
    - AI suggestions as actionable buttons with confidence scores
    - Real-time message sending (Enter key or send button)
    - Loading states with animated dots
  - **Resolution Actions:**
    - `handleSuggestionClick()` — Calls `/inbox/{id}/resolve` endpoint
    - Action-specific UI updates (create_note, explore_in_flow, link_to_concept, etc.)
    - Removes from queue on successful resolution
    - Dispatches `openFlow` event for FlowMode escalation
  - **API Integration:**
    - SiYuan proxy wrapper for all backend calls (GET, POST, PATCH)
    - Error handling with user-friendly messages
    - Confidence color coding (green >=70%, yellow >=40%, gray <40%)
- **Dashboard.svelte**: Shows inbox queue count + quick access to pending items

**Tests:**
- `test_inbox.py`: 5 tests (create, list, update, delete, filtering)
- `test_thinking_and_flow.py`: 4 tests (start session, breadcrumbs, completion, inbox status)

### Key Implementation Patterns

**AI Integration (Dual-Mode):**
- Primary: Claude Sonnet 4 (`claude-sonnet-4-20250514`) via Anthropic API
- Fallback: Simple pattern matching (regex + keyword extraction) when API unavailable
- Check: `ANTHROPIC_AVAILABLE = bool(os.getenv("ANTHROPIC_API_KEY"))`
- Graceful degradation in dialogue, entity extraction, and suggestion generation

**Dialogue Flow:**
1. User selects inbox item → Auto-triggers initial AI analysis ("What is this about?")
2. User sends message → Backend calls `add_dialogue_message()`
3. AI analyzes content + conversation history + knowledge graph context
4. Response includes conversational text + structured suggestions (JSON parsing from AI output)
5. User clicks suggestion → `resolve_inbox()` routes to destination
6. Item status updated: QUEUED → IN_THINKING (if escalated to Flow) or INTEGRATED (if resolved)

**Graph Integration:**
- Entity extraction matches against Neo4j via `GraphService.search_concepts()`
- Sets `graph_match=True` flag on entities that exist in knowledge graph
- Creates `MENTIONS` relationships between InboxItem and Concept nodes
- Resolution creates `LINKED_TO` or `PART_OF` relationships (depending on action)

**State Management:**
- Neo4j stores dialogue as JSON array in `InboxItem.dialogue` property
- Dialogue parsed on read via `_record_to_inbox()` helper (lines 949-957)
  - Handles both list and JSON string formats from Neo4j
  - Validates each message via `DialogueMessage.model_validate()`
  - Returns empty array on parse errors (graceful degradation)
- Status transitions enforce lifecycle: QUEUED → IN_THINKING → INTEGRATED
- Resolution actions update status atomically with relationship creation

**Frontend Integration:**
- SiYuan proxy wrapper handles all backend calls (GET/POST/PATCH via `/api/network/forwardProxy`)
- Error boundary with user-friendly messages (proxy errors vs backend errors)
- Real-time UI updates via local state mutation after successful API calls
- Event dispatch for cross-component communication (e.g., `openFlow` for FlowMode escalation)

### Renamed Concepts

| Old Name | New Name | Rationale |
|----------|----------|-----------|
| Quick Capture | Inbox | Implies "unprocessed items needing attention" |
| Quick Capture UI | Inbox View | Where items are reviewed and processed |
| Capture Queue | Inbox | Cleaner, more intuitive name |
| Process button | Process | Opens collaborative dialogue |

### Flow Architecture (Design + Phase 1)

```
EXTERNAL SOURCES (Primary)
├── iOS Shortcuts — "Hey Siri, capture this thought"
├── Browser Extension — Highlight + capture from web
├── Voice Notes — Transcribed async via Whisper
├── Share Sheet — From any iOS/Android app
└── Email/SMS forward (future)
        ↓
    POST /inbox
    { text, source, captured_at, context? }
        ↓
    INBOX (Neo4j: InboxItem nodes)
    Status: unprocessed
        ↓
    User opens SiYuan → Inbox View
        ↓
    Selects item → [Process] button
        ↓
    AI asks clarifying questions
    User responds in dialogue
    AI surfaces graph connections
        ↓
    Route to destination (note, concept, journey, new note)
        ↓
    Status: processed → removed from Inbox
```

**Direct Capture (Secondary):**
- SiYuan Inbox View → "Add" button
- Keyboard shortcut within SiYuan
- Right-click → "Send to Inbox"

### Collaborative Processing

**Dialogue Principles:**
1. **AI asks first** — Never assume; ask what the user was thinking
2. **Surface connections** — Show related concepts from knowledge graph
3. **Offer concrete options** — Actionable choices, not open-ended questions
4. **Escape hatch visible** — "This needs deeper exploration" always available

**Complexity Scaling:**
| Capture Type | Typical Flow | Destination |
|--------------|--------------|-------------|
| **Simple** (quote, thought) | 1-2 exchanges → route | Append to existing note |
| **Medium** (needs context) | 2-4 exchanges → clarify → route | New note or concept link |
| **Complex** (sparks curiosity) | Recognize early → "Explore in Flow" | FlowMode session |

### Inbox View Design

**List View (Default):**
```
┌─────────────────────────────────────────────────────────────┐
│ Inbox (3)                                    [+] [Settings] │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ "that thing about dopamine and task switching that     │ │
│ │ I read about — seemed important for understanding..."  │ │
│ │                                                        │ │
│ │ 📱 iOS Shortcut • 2 hours ago                          │ │
│ │ [Process]  [Explore in Flow]  [···]                    │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ "https://www.nature.com/articles/adhd-research-2024"   │ │
│ │ 🌐 Browser • yesterday                                 │ │
│ │ Preview: "New findings on executive function..."       │ │
│ │ [Process]  [Explore in Flow]  [···]                    │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Source Icons:**
- 📱 iOS Shortcut — Voice capture, quick thought
- 🌐 Browser — URL, highlight, article
- 🎤 Voice Note — Transcribed audio
- 📝 SiYuan Direct — Added from within app
- ✉️ Email — Forwarded content

**Processing Dialogue (Inline):**
```
┌─────────────────────────────────────────────────────────────┐
│ Processing                                          [Close] │
├─────────────────────────────────────────────────────────────┤
│ 🤖 What were you thinking about when you captured this?    │
│    I notice "dopamine" and "task switching" — is this:     │
│    • How ADHD affects focus?                               │
│    • Medication mechanisms?                                │
│    • Strategies you want to try?                           │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ It was from a podcast about why ADHD makes it hard...  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ 🤖 That sounds like task-switching cost / cognitive        │
│    inertia. I found related concepts in your graph:        │
│    📊 "Hyperfocus" — 3 connections                         │
│    📊 "Executive Function" — 7 connections                 │
│                                                             │
│    Should I:                                               │
│    • Add this as a note linked to "Executive Function"?    │
│    • Create a new concept "Task Switching Cost"?           │
│                                                             │
│ [Link to Executive Function]  [Create New Concept]         │
│ [This needs deeper exploration →]                          │
└─────────────────────────────────────────────────────────────┘
```

### API Endpoints

**Inbox CRUD:**
- `POST /inbox` — Create new inbox item (from external source)
- `GET /inbox` — List inbox items (filterable by status)
- `GET /inbox/{id}` — Get single item with dialogue history
- `DELETE /inbox/{id}` — Remove item (after processing or manual archive)

**Processing:**
- `POST /inbox/{id}/message` — Add user message to dialogue
- `POST /inbox/{id}/process` — Trigger AI response in dialogue
- `POST /inbox/{id}/resolve` — Mark as processed with destination
- `POST /inbox/{id}/to-flow` — Escalate to FlowMode

### Data Model

```python
class InboxItem(BaseModel):
    id: str
    text: str
    source: InboxSource  # ios_shortcut, browser, voice, siyuan, email
    captured_at: datetime
    status: InboxStatus  # unprocessed, processing, in_flow, processed

    # Source context (optional, depends on source)
    source_context: Optional[SourceContext]  # URL, app, location, etc.

    # Processing dialogue (built up during collaborative processing)
    dialogue: list[DialogueMessage] = []

    # AI-extracted (populated during processing)
    extracted_entities: list[ExtractedEntity] = []
    suggested_placement: Optional[Placement] = None

    # Resolution
    resolved_to: Optional[Resolution] = None  # note_id, concept_id, journey_id
    resolved_at: Optional[datetime] = None

class InboxStatus(str, Enum):
    UNPROCESSED = "unprocessed"  # Just arrived, waiting
    PROCESSING = "processing"    # User opened dialogue
    IN_FLOW = "in_flow"          # Escalated to FlowMode
    PROCESSED = "processed"      # Routed to destination

class DialogueMessage(BaseModel):
    role: Literal["assistant", "user"]
    content: str
    timestamp: datetime
    suggestions: Optional[list[Suggestion]] = None  # For assistant messages
```

### FlowMode Integration ("Explore in Flow")

When a capture needs deeper exploration:
1. User clicks "Explore in Flow" or AI recognizes complexity
2. Create Spark: `{ type: 'capture', captureId, rawText }`
3. `POST /flow/session` → FlowMode opens with Orientation phase
4. InboxItem status → `in_flow`
5. FlowMode session progresses through 4 phases
6. Synthesis generated → InboxItem status → `processed`
7. Item removed from Inbox

**The capture becomes the spark that ignites the FlowMode session.**

### External Source Integration

**iOS Shortcuts** ✅ IMPLEMENTED
- **Setup Guide:** `docs/ios-shortcut-setup.md`
- **Shortcut Name:** "Capture Thought" (customizable)
- **Trigger:** "Hey Siri, Capture Thought" or home screen icon
- **Flow:**
  1. "Ask for Input" action: "What's on your mind?"
  2. POST to `http://[SERVER_IP]:8081/inbox`
     - Body: `{ "text": "[input]", "source": "ios_shortcut", "context": { "device": "iPhone" } }`
     - Headers: `Content-Type: application/json`
  3. Show notification: "Saved to Inbox"
- **Variations:**
  - Voice: Replace "Ask for Input" with "Dictate Text"
  - Link: Enable Share Sheet, use `Shortcut Input` for URLs
  - Location: Add current location to context
- **Network:** Requires same WiFi as backend server (192.168.86.60:8081)
- **Offline Support:** Can save to Notes app, sync later with separate shortcut

**Browser Extension (Future):**
- Highlight text + keyboard shortcut → capture
- Sends selected text, URL, page title to `/inbox`

**Voice Capture (Planned):**
- iOS Shortcut records voice
- Whisper API transcribes
- POSTs to `/inbox` with `source: "voice"` and `audio_url` for playback

### Implementation Phases

**Phase 1: Rename & Restructure (1-2 days)**
- Rename QuickCapture.svelte → Inbox.svelte
- Update schemas: CaptureItem → InboxItem
- Update API routes: /capture → /inbox
- Update CLAUDE.md and docs

**Phase 2: External Source Support (2-3 days)**
- iOS Shortcut template creation
- Test POST /inbox from external sources
- Source icon display in Inbox view

**Phase 3: Collaborative Processing UI (3-5 days)**
- Inline dialogue expansion
- AI first-message generation
- User response input
- Graph entity matching display
- Placement option buttons

**Phase 4: Resolution Routing (2-3 days)**
- "Link to concept" action
- "Create new note" action
- "Append to note" action
- Status transition to processed

**Phase 5: FlowMode Integration (1-2 days)**
- "Explore in Flow" button
- Spark creation from InboxItem
- Status sync (in_flow → processed)

### Success Metrics
- **Capture latency:** < 2 seconds from thought to saved
- **Processing completion:** > 80% of items processed within 48 hours
- **Flow escalation:** ~20% of items warrant deeper exploration
- **Zero friction:** No required fields at capture time

### Outstanding Work
- [ ] Rename `/capture` → `/inbox` endpoints (Phase 1)
- [ ] Rename `CaptureService` → `InboxService` (Phase 1)
- [ ] Implement collaborative dialogue UI (Phase 3)
- [ ] iOS Shortcut template (Phase 2)
- [ ] Browser extension (Future)
- [ ] Voice transcription integration (Future)
- [ ] Test coverage for InboxService (All phases)

---

## Key Documents

| Purpose | Location |
|---------|----------|
| **Inbox redesign** | `docs/plans/2025-12-06-inbox-redesign.md` |
| **FlowMode enhancement plan** | `docs/plans/2025-12-06-flowmode-enhancement-plan.md` |
| Remediation plan | `docs/plans/2025-12-06-comprehensive-remediation-plan.md` |
| Cross-app sync design | `docs/plans/2025-12-06-cross-app-sync-design.md` |
| IES Reader switch | `docs/plans/2025-12-06-readest-to-ies-reader-amendment.md` |
| Pressure test results | `docs/PRESSURE-TEST-PLAN.md` |
| System design | `docs/SYSTEM-DESIGN.md` |
| Archived history | `docs/archive/CLAUDE-historical-2025-12-06.md` |

---

## Wave Status

### Wave 1: Foundation ✅ COMPLETE (Dec 6)
- [x] Neo4j client unification — `UnifiedGraphClient` (1,476 lines, 47 methods)
- [x] User ID unification — `/profile/login` endpoint
- [x] Session persistence (Redis) — `SessionStore` with 24h TTL

**Tests:** 108/108 passing | **Docs:** `docs/scratch/wave-1-complete.md`

### Wave 2: Wiring ✅ COMPLETE (Dec 6)

**2.1: IES Reader-Backend Integration** ✅
- ✅ **IMPLEMENTED:** Full standalone React app (commit bb221b8, 5,741 lines)
- Login flow via `/profile/login`, journey persistence, sync status indicators
- EPUB reading with text selection → entity lookup → Flow Panel workflow
- Offline queue with exponential backoff and localStorage persistence

**2.2: SiYuan-Backend Integration** ✅
- Login flow, journey persistence on FlowMode exit, dynamic userId

**2.3: Cross-App Sync Design** ✅
- Design doc: `docs/plans/2025-12-06-cross-app-sync-design.md`
- Covers: sync protocol, conflict resolution, offline queue, event notifications, security

**Docs:** `docs/scratch/wave-2-complete.md`

### Wave 3: Visibility ✅ COMPLETE (Dec 6)

**3.1: Journey UI** ✅
- [x] History view in SiYuan Dashboard (Recent Explorations section)
- [x] Journey synthesis endpoint (`POST /journeys/{id}/synthesize`) — AI-powered summary with Claude Sonnet 4
- [x] Journey history endpoint (`GET /journeys/user/{user_id}`) — Paginated journey list
- **Implementation:** `JourneyService.generate_synthesis()` analyzes path, marks, thinking partner exchanges
- **Fallback:** Basic summary when AI unavailable

**3.2: Question Feedback Capture** ✅
- [x] FeedbackService with Neo4j persistence (`QuestionFeedback` nodes)
- [x] `POST /question-engine/feedback` endpoint
- [x] FeedbackType enum: HELPFUL, NOT_HELPFUL, LED_TO_INSIGHT
- [x] Statistics: `get_feedback_stats()`, `get_effective_question_classes()`
- **Links:** Feedback nodes connected to UserProfile, Entity, Session via relationships
- **Tests:** 5 tests in `test_feedback_service.py` (all passing)

**3.3: Cross-App Sync Implementation** ✅
- [x] Offline queue for IES Reader (`ies/reader/src/services/offlineQueue.ts`)
  - localStorage persistence (max 50 operations, 3 retry limit)
  - Exponential backoff: 5s, 30s, 2min delays
  - Automatic processing on backend reconnection
- [x] Offline queue for SiYuan (`.worktrees/siyuan/ies/plugin/src/utils/offlineQueue.ts`)
  - Matching retry logic and persistence strategy
  - Integration with `siyuan-structure.ts` for journey/session saves
- [x] Sync status indicators in both apps
  - **IES Reader:** FlowPanel header shows pending/synced/error/offline states
  - **SiYuan:** Dashboard header shows queue status with retry button
  - **Offline indicator:** Shows queue count, click to retry manually

**Tests:** 113/113 passing | **Docs:** `docs/scratch/wave-3-complete.md`

### Wave 4: Learning ✅ COMPLETE (Dec 6)

**4.1: Profile Learning from Sessions** ✅
- [x] Extended `ProfileObservation` schema with engagement metrics:
  - `time_per_entity`: Tracks seconds spent per entity/topic
  - `thinking_partner_exchanges`: Count of question exchanges
  - `insights_count`: Number of insights during session
- [x] Added `ApproachEffectivenessEntry` schema for tracking approach success:
  - `average_score`: Running average (0-10 scale)
  - `sample_size`: Number of sessions tracked
  - `last_updated`: Timestamp of latest update
- [x] Implemented `apply_observation()` learning logic with thresholds:
  - `DEEP_ENGAGEMENT_SECONDS=300` (5 min per entity = deep engagement)
  - `MIN_EXCHANGES_FOR_ENGAGEMENT=3` (thinking partner exchanges)
  - `HIGH_ENERGY_SIGNALS={"hyperfocused", "deep_engagement", "flow", "energized"}`
  - `MAX_HYPERFOCUS_TRIGGERS=20` (prunes oldest when exceeded)
- [x] Running average calculation for approach effectiveness scores
- [x] Hyperfocus triggers updated only on deep engagement criteria
- **Files Modified:** `ies/backend/src/ies_backend/schemas/profile.py`, `ies/backend/src/ies_backend/services/profile_service.py`
- **Tests Added:** 5 tests in `test_profile.py` (engagement tracking, trigger updates, effectiveness tracking)

**4.2: Question Selection Optimization** ✅
- [x] Added `get_user_effective_classes(user_id, min_sample=5)` to FeedbackService
- [x] Calculates effectiveness: `(helpful + insight) / (total * 2)`
  - Range: 0.0 (no helpful/insight) to 1.0 (all helpful+insight)
  - Normalizes by doubling denominator (max = helpful + insight)
- [x] Filters classes with insufficient samples (< min_sample)
- [x] Returns `dict[str, float]` for weighted question selection
- [x] Neo4j query aggregates feedback by question class and user
- **Files Modified:** `ies/backend/src/ies_backend/services/feedback_service.py`
- **Tests Added:** 2 tests in `test_feedback_service.py` (effective classes, insufficient data handling)

**4.3: Reframe Prompt Adaptation** ✅
- [x] Added `get_user_reframe_preferences(user_id)` to ReframeService
- [x] Thresholds: >= 60% helpful = preferred, < 30% helpful = avoid
- [x] Returns: `{preferred_types, preferred_domains, avoid_types}`
- [x] Queries `ReframeFeedback` nodes linked to user via Neo4j
- [x] Aggregates by type and domain for personalization
- **Files Modified:** `ies/backend/src/ies_backend/services/reframe_service.py`
- **Tests Added:** 2 tests in `test_reframe_service.py` (preferences extraction, empty history handling)

**Tests:** 122/122 passing (+9 from Wave 3) | **Docs:** `docs/scratch/wave-4-complete.md`
**Test Breakdown:** 5 profile learning + 2 question selection + 2 reframe adaptation = 9 new tests

### Wave 5: Quality ✅ COMPLETE (Dec 6)

**5.1: Test Suites for Critical Services** ✅
- [x] journey_service.py — 15 tests (78% coverage)
- [x] chat_service.py — 13 tests (50% coverage, chat_stream is integration territory)
- [x] personal_graph_service.py — 15 tests (91% coverage)
- [x] graph_service.py — 20 tests (95% coverage)

**Tests:** 185/185 passing (+63 from Wave 4) | **Docs:** `docs/scratch/wave-5-complete.md`

---

## All Waves Complete

The remediation plan is now **COMPLETE**. System is at health grade **A** with:
- All 12 blockers resolved
- 185 passing tests
- 4-layer architecture fully operational

<!-- END MANUAL -->
