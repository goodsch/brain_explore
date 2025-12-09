<!-- MANUAL -->
# brain_explore — Intelligent Exploration System

*Domain-agnostic tool for structured thinking and knowledge exploration*

## What This Is

Four-layer system for AI-partnered knowledge exploration:

| Layer | Component | Purpose |
|-------|-----------|---------|
| 1 | Knowledge Graph | Ingests materials → entities/relationships (179 books, ~300 entities) |
| 2 | Backend APIs | Graph, dialogue, journeys, profiles (185 tests passing) |
| 3 | SiYuan Plugin | Dashboard, 5 thinking modes, flow exploration |
| 4 | IES Reader | Standalone e-book reader with entity overlay and flow panel |

**Note:** IES Reader replaced Readest (Dec 2025). Readest worktree is archived, no longer in active development.

**The Virtuous Cycle:** Dialogue reveals thinking patterns → personalized exploration → concept discovery → enriches graph → deeper exploration.

## Current Status

**Phase 2c: Flow v2 Complete** (Dec 8, 2025)

Completed:
- 5-wave backend remediation (all components production-ready)
- IES Reader Waves 1-3 (library, PWA, interactive, mobile UX)
- IES MCP Server (voice-driven ForgeMode via Claude Desktop)
- SiYuan remediation complete
- Conversation service (parse Claude exports → Neo4j)
- **Flow v2 Phase 1** — Dual-mode question-driven UI infrastructure (useFlowLayout hook, question state store, QuestionSelector component, FlowPage standalone, FlowPanel integration)
- **Flow v2 Phase 2** — Backend persistence for Contexts and Questions
  - Context/Question/AnswerBlock schemas
  - QuestionService & ContextCRUDService (in-memory MVP)
  - REST APIs: `/questions/*`, `/context/*`
  - IES Reader API clients (`questionApi.ts`, `contextApi.ts`)
  - SiYuan plugin API clients with forwardProxy pattern

In Progress:
- Cross-app sync (SiYuan → backend)
- Pass 2/3 enrichment pipeline

See `docs/CHANGELOG.md` for detailed history.

## Quick Start

```bash
# Start infrastructure
docker compose up -d

# Backend (port 8081)
cd ies/backend && uv run uvicorn ies_backend.main:app --reload --port 8081

# SiYuan plugin development
cd .worktrees/siyuan/ies/plugin && pnpm dev

# IES Reader development (port 5173)
cd .worktrees/ies-reader/ies/reader && pnpm dev
```

## Recent Changes (from fa7bb08)

**IES Reader Wave 3 Enhancements:**
- **Mobile UX**: Conditional FAB (floating action button) for note capture on mobile (<768px)
- **Text Selection Actions**: Quick action bar with entity lookup, note capture, and highlighting
- **CFI-Based Notes**: NotesSheet captures selected text with EPUB CFI (Canonical Fragment Identifier) for precise location tracking
- **Sheet Component**: Bottom sheet UI with framer-motion animations, portal rendering, touch-friendly targets
- **Removed Auto-Lookup**: Text selection no longer auto-triggers entity lookup (user-controlled via action bar)

## Project Layout

```
brain_explore/
├── ies/
│   ├── backend/          # FastAPI backend (Layer 2)
│   └── reader/           # IES Reader (Layer 4) - React PWA
├── calibre/library/      # Book catalog (179 books)
├── library/graph/        # Neo4j client, entity extraction
├── .worktrees/
│   ├── siyuan/          # SiYuan plugin (Layer 3)
│   └── ies-reader/      # IES Reader development worktree
└── docs/                 # Documentation
```

**IES Reader Architecture** (`ies/reader/src/`):
- **Components**: `Reader.tsx` (epub.js wrapper), `FlowPanel.tsx` (entity exploration), `NotesSheet.tsx` (mobile-first capture), `QuestionSelector.tsx` (question-driven exploration), `FlowPage.tsx` (standalone mobile interface)
- **Hooks**: `useEntityLookup` (graph queries), `useEntityOverlay` (book entities), `useEntityHighlighter` (epub annotations), `useFlowLayout` (responsive mode detection)
- **Store**: `flowStore.ts`/`flowModeStore.ts` (Zustand) - journey tracking, entity state, question state, sync status, overlay config
- **Services**: `questionApi.ts` (Question CRUD client), `contextApi.ts` (Context CRUD client), `graphClient.ts` (entity lookup)
- **Features**: Text selection → entity lookup/note capture, question-driven exploration, CFI-based highlights, dual-mode UI (desktop panel / mobile standalone), offline-first with queue, backend sync for contexts and questions

**Backend Architecture** (`ies/backend/src/ies_backend/`):
- **Schemas**: `schemas/context.py` (Context, ContextCreate, ContextUpdate, ContextType, ContextStatus), `schemas/question.py` (Question, QuestionCreate, QuestionUpdate, QuestionStatus, QuestionSource, AnswerBlock)
- **Services**: `services/context_crud_service.py` (ContextCRUDService - in-memory MVP), `services/question_service.py` (QuestionService - in-memory MVP)
- **APIs**: `api/questions.py` (Question CRUD endpoints with answer block management), `api/context.py` (Context CRUD endpoints)
- **Features**: RESTful CRUD for contexts and questions, filtering by type/status/source, question-context relationships, answer blocks for question responses

**Worktrees:** Feature work happens in worktrees, not master branch.
- `.worktrees/siyuan/` → SiYuan plugin on `feature/siyuan-evolution`
- `.worktrees/ies-reader/` → IES Reader on `feature/ies-reader-enhancement` (ACTIVE)
- `.worktrees/readest/` → Archived (replaced by IES Reader)
- Master branch → Backend only

## Key Commands

```bash
# Tests
cd ies/backend && uv run pytest

# Docker
docker compose up -d      # Start
docker compose ps         # Status
docker compose down       # Stop

# Git
git log --oneline -10     # Recent commits
git status                # Current state
```

## Critical Constraints

**DO NOT:**
- Work on features in master branch (use worktrees)
- Skip tests before committing
- Add therapy-specific hardcoding (system is domain-agnostic)

**ALWAYS:**
- Check git status before starting work
- Run tests after changes: `uv run pytest`
- Use Serena symbolic tools for code exploration
- Check `docs/SYSTEM-DESIGN.md` for architecture questions

## Key Resources

| Resource | Purpose |
|----------|---------|
| `docs/SYSTEM-DESIGN.md` | Architecture and data flows |
| `docs/CHANGELOG.md` | Development history |
| `docs/plans/2025-12-08-flow-v2-phase1-implementation.md` | Flow v2 Phase 1 TDD implementation plan (5 tasks) - COMPLETED |
| `docs/plans/2025-12-08-flow-v2-phase2-implementation.md` | Flow v2 Phase 2 backend persistence plan (6 tasks) - IN PROGRESS |
| `docs/plans/` | Feature design documents |
| `ies/backend/src/ies_backend/schemas/question.py` | Question, QuestionStatus, QuestionSource, AnswerBlock schemas |
| `ies/backend/src/ies_backend/schemas/context.py` | Context, ContextType, ContextStatus schemas |
| `ies/backend/src/ies_backend/services/question_service.py` | QuestionService CRUD implementation |
| `ies/backend/src/ies_backend/services/context_crud_service.py` | ContextCRUDService CRUD implementation |
| `ies/backend/src/ies_backend/api/questions.py` | Question REST API endpoints (CRUD + answer blocks) |
| `.worktrees/ies-reader/ies/reader/src/services/questionApi.ts` | IES Reader Question API client |
| `.worktrees/ies-reader/ies/reader/src/services/contextApi.ts` | IES Reader Context API client |
| `.worktrees/ies-reader/ies/reader/src/services/index.ts` | Services barrel export |
| `ies/reader/src/components/Reader.tsx` | Main reader component, text selection handling |
| `ies/reader/src/store/flowStore.ts` | Global state: journeys, entities, sync |
| Serena memory: `true_vision` | Core project vision |

## IES Reader Key Patterns

**Text Selection Flow:**
1. User selects text in epub.js rendition
2. `Reader.tsx` captures selection via `rendition.on('selected')` event
3. Selection context stored with CFI range and position
4. Quick action bar shows: entity lookup, note capture, highlight
5. Actions integrate with flowStore for journey tracking

**Context & Question Management:**
- `contextApi.ts` provides client for Context CRUD (list, get, create with type filtering)
- `questionApi.ts` provides client for Question CRUD (create, list by context/source, update status, manage answer blocks)
- `useFlowLayout()` hook returns responsive mode: `{ mode: 'panel' | 'standalone', isMobile, isDesktop }`
- `FlowQuestion` store tracks current question, parent relationships, and prerequisite questions
- Services barrel export (`services/index.ts`) provides unified access to all API clients

**Mobile Detection & Responsive Modes:**
```typescript
// useFlowLayout hook pattern
const layout = useFlowLayout();
// Returns: { mode: 'panel' | 'standalone', isMobile, isTablet, isDesktop, setMode }

// Component conditional rendering
{layout.isMobile && layout.mode === 'standalone' && <FlowPage />}
{!layout.isMobile && <FlowPanel />}
```

**Question-Driven Exploration:**
- QuestionSelector dropdown allows create/select operations
- Questions grouped by source (reader-created vs siyuan-created)
- Question status: open → partial → answered → modeled
- Answer blocks tracked separately for each question
- FlowPanel integrates selector with entity exploration context

**API Client Pattern (TypeScript):**
```typescript
// Singleton pattern with class export for testing
export const questionApi = new QuestionApiClient();
export { QuestionApiClient };

// Usage
const questions = await questionApi.list({ context_id: ctx.id });
const question = await questionApi.create({ context_id: ctx.id, text: "..." });
const updated = await questionApi.update(id, { status: 'answered' });
```

**Note Capture with CFI:**
- NotesSheet accepts `initialNoteData: { text: string; cfiRange: string }`
- CFI enables future features: return-to-passage, passage linking
- Notes tagged by type: thought/question/insight
- Connected to currentEntity for journey context

## Flow v2 Phase 2: Implementation Details

Phase 2 implements backend persistence for the question-driven UI built in Phase 1.

**What Phase 2 Delivers:**
1. Backend schemas for Context, Question, AnswerBlock (with enums for types/statuses)
2. In-memory CRUD services (QuestionService, ContextCRUDService) - MVP before Neo4j migration
3. REST API endpoints for all CRUD operations with filtering support
4. TypeScript API clients for IES Reader (questionApi.ts, contextApi.ts)
5. Integration between reader UI and backend persistence
6. Test coverage for all service operations

**Data Model:**
- **Context:** id, type (feynman_problem/project/theory/concept_cluster/life_area), title, status (idea/active/paused/archived), parent_context_id, key_questions, core_concepts, linked_sources, artifacts, siyuan_doc_id
- **Question:** id, context_id, text, status (open/partial/answered/modeled), source (siyuan/reader/ai-suggested/dialogue), parent_question_id, prerequisite_questions, related_concepts, linked_sources, siyuan_block_id
- **AnswerBlock:** id, question_id, content (markdown), quality (draft/good_enough/polished)

**API Endpoints:**
- `POST /questions/` — Create question
- `GET /questions/` — List with filters (context_id, source, status, limit)
- `GET /questions/{id}` — Get single question
- `PATCH /questions/{id}` — Update question
- `DELETE /questions/{id}` — Delete question
- `GET /questions/{id}/answers` — List answers for question
- `POST /questions/{id}/answers` — Create answer block

**Implementation Status:**
- ✅ Schemas: Context, Question, AnswerBlock with validation
- ✅ Services: QuestionService, ContextCRUDService with full CRUD
- ✅ APIs: Question endpoints complete, context endpoints ready for registration
- ✅ TypeScript clients: questionApi.ts (QuestionApiClient), contextApi.ts (ContextApiClient)
- ✅ Tests: test_question_service.py, test_context_crud_service.py
- 🔄 Next: Register context router in main.py, SiYuan plugin integration, Neo4j migration path

**Future Work (Phase 2 Extension/Phase 3):**
- Replace in-memory storage with Neo4j persistence
- Extraction Engine integration (context-aware extraction)
- AI-generated subquestions
- Context Note parsing from SiYuan markdown
- Journey logging for question events
- Dynamic source acquisition

## Working Style

Claude acts as project manager. Identify optimal next action and proceed — don't ask what to work on. User will redirect if needed.

## Context Efficiency

This CLAUDE.md is intentionally brief. For details:
- **History:** `docs/CHANGELOG.md`
- **Architecture:** Use `mcp__serena__read_memory` with `ies_architecture`
- **Implementation:** Read code with Serena symbolic tools
- **Plans:** Check `docs/plans/` directory
- **Phase 2 Spec:** `docs/plans/2025-12-08-flow-v2-phase2-implementation.md`
<!-- END MANUAL -->
