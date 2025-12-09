# Unified Project Spec — IES (Intelligent Exploration System)

**Created:** 2025-12-09
**Purpose:** Resolve documentation confusion and establish clear project direction

> **Ground Truth:** This document defers to `docs/IES-SYSTEM-DESIGN.md` for conceptual definitions.
> See that document for: cognitive architecture, operating model, entity lifecycle, interaction semantics.

---

## Executive Summary

**The Core Problem:** Documentation and memories reference both "Readest" and "IES Reader" inconsistently, causing agents to work on the wrong codebase.

**The Resolution:**
- **IES Reader** (`ies/reader/`) is the **ACTIVE** reader — a lightweight React/Vite app built specifically for this project
- **Readest** (`.worktrees/readest/`) is **ARCHIVED** — a forked Tauri/Next.js e-book reader that was too complex
- Work should happen in IES Reader, NOT Readest

---

## 1. Project Architecture

### Four-Layer System

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LAYER 4: IES READER (Active)                      │
│     React PWA • epub.js • Flow exploration • Question-driven UI      │
│     Location: ies/reader/ and .worktrees/ies-reader/                 │
├─────────────────────────────────────────────────────────────────────┤
│                    LAYER 3: SIYUAN PLUGIN                            │
│     Processing hub • Dashboard • 5 thinking modes • ForgeMode        │
│     Location: .worktrees/siyuan/ies/plugin/                          │
├─────────────────────────────────────────────────────────────────────┤
│                    LAYER 2: IES BACKEND                              │
│     FastAPI • Graph API • Question Engine • Context/Question CRUD    │
│     Location: ies/backend/                                           │
├─────────────────────────────────────────────────────────────────────┤
│                    LAYER 1: KNOWLEDGE GRAPH                          │
│     Neo4j • 300+ entities • Entity extraction • Calibre integration  │
│     Location: library/graph/ + calibre/                              │
└─────────────────────────────────────────────────────────────────────┘
```

### What Is NOT Part of Active Development

| Component | Location | Status | Notes |
|-----------|----------|--------|-------|
| Readest | `.worktrees/readest/` | ARCHIVED | Too complex (Tauri/Rust/Next.js), replaced by IES Reader |
| flowmode worktree | `.worktrees/flowmode/` | STALE | Old exploration, likely obsolete |
| readest-critique | `.worktrees/readest-critique/` | ARCHIVED | Analysis worktree |
| siyuan-arch | `.worktrees/siyuan-arch/` | ARCHIVED | Architecture exploration |
| ux-dev | `.worktrees/ux-dev/` | ARCHIVED | UX development worktree |

---

## 2. The Readest vs IES Reader Confusion

### Why This Happened

1. **Readest was forked** as a full-featured Tauri e-book reader (Dec 3-5)
2. **Significant work was done** on Readest: Flow mode, entity panel, journey capture
3. **IES Reader was created** (Dec 6-8) as a simpler React alternative
4. **Documentation wasn't updated** — Readest worktree CLAUDE.md still says "MVP COMPLETE"
5. **Serena memories** may still reference Readest as active

### The Truth

| Aspect | Readest | IES Reader |
|--------|---------|------------|
| **Technology** | Tauri + Rust + Next.js + Svelte | React + Vite + epub.js |
| **Complexity** | Very complex (full app) | Purpose-built, simple |
| **Status** | ARCHIVED Dec 6 | ACTIVE |
| **Last commits** | Dec 5 | Dec 8 |
| **Features** | Full e-book reader | IES-specific exploration |
| **Location** | `.worktrees/readest/readest/` | `ies/reader/` |

### What Exists in Each

**IES Reader (ACTIVE) — 19 source files:**
```
ies/reader/src/
├── App.tsx                      # Main app with LibraryBrowser/Reader routing
├── main.tsx                     # Entry point
├── components/
│   ├── Reader.tsx               # epub.js reader wrapper
│   ├── library/
│   │   ├── LibraryBrowser.tsx   # Calibre book browser
│   │   ├── BookCard.tsx         # Book display card
│   │   ├── SearchBar.tsx        # Search interface
│   │   └── IngestionQueueSheet.tsx
│   ├── flow/
│   │   ├── FlowPanel.tsx        # Side panel for exploration
│   │   ├── QuestionSelector.tsx # Question dropdown
│   │   ├── NotesSheet.tsx       # Note capture sheet
│   │   ├── NotesCapture.tsx     # Mobile FAB
│   │   ├── InteractiveQuestions.tsx
│   │   └── JourneyBreadcrumb.tsx
│   └── ui/
│       └── Sheet.tsx            # Bottom sheet component
├── hooks/
│   ├── useFlowLayout.ts         # Responsive mode detection
│   ├── useEntityLookup.ts       # Entity search
│   ├── useEntityHighlighter.ts  # Text highlighting
│   ├── useEntityOverlay.ts      # Overlay management
│   ├── useQuestionSync.ts       # Question sync
│   └── useIngestionQueue.ts     # Queue management
├── services/
│   ├── graphClient.ts           # Backend API client
│   ├── questionApi.ts           # Question CRUD
│   ├── contextApi.ts            # Context CRUD
│   ├── syncApi.ts               # Cross-app sync
│   └── offlineQueue.ts          # Offline support
└── store/
    ├── flowStore.ts             # Zustand state management
    └── ingestionQueueStore.ts   # Queue state
```

**Readest (ARCHIVED) — Much larger:**
- Full Tauri app with Rust backend
- 30+ reader components
- FoliateViewer, TTS, OPDS support
- Complex build system (pnpm + Tauri)

### Features to Potentially Migrate from Readest

Some Readest work may need to be ported to IES Reader:

| Feature | Readest Status | IES Reader Status | Action |
|---------|---------------|-------------------|--------|
| Entity overlay | Complete | Partial | May need enhancement |
| Entity click → Flow | Complete | Needs work | Port interaction pattern |
| Question responses | Complete | Basic | Enhance textarea/capture |
| Journey breadcrumbs | Complete | Basic | Port UI |
| Design system (colors) | Complete | Missing | Apply consistent styling |
| LocalStorage persistence | Complete | Missing | Port journeyStorage |
| AbortController cleanup | Fixed | Unknown | Verify implementation |
| Trie-based entity matching | Fixed | Unknown | Port if needed |

---

## 3. Current Implementation Status

### Backend (Layer 2) — 85% Complete

**Implemented:**
- ✅ Context CRUD (`/context/*`) — In-memory MVP
- ✅ Question CRUD (`/questions/*`) — In-memory MVP
- ✅ Answer blocks management
- ✅ Graph API (entity search, facets, evidence)
- ✅ Question Engine (9 question classes)
- ✅ Reframe API (metaphor generation)
- ✅ Template API (thinking templates)
- ✅ Books API (Calibre integration)
- ✅ Personal Graph API (ADHD-friendly capture)

**Needs Work:**
- 🔄 Neo4j persistence for Context/Question (currently in-memory)
- 🔄 Evidence extraction queue
- 🔄 Cross-app sync endpoints

### IES Reader (Layer 4) — 60% Complete

**Implemented:**
- ✅ LibraryBrowser with Calibre integration
- ✅ epub.js Reader with text selection
- ✅ FlowPanel with entity display
- ✅ QuestionSelector dropdown
- ✅ NotesSheet capture
- ✅ useFlowLayout responsive hook
- ✅ Question state in flowStore
- ✅ API clients (questionApi, contextApi)

**Needs Work:**
- 🔄 Entity overlay on text (highlighting)
- 🔄 Click entity → open Flow panel
- 🔄 Journey breadcrumb trail
- 🔄 LocalStorage persistence
- 🔄 Design system consistency
- 🔄 Mobile standalone mode (FlowPage)

### SiYuan Plugin (Layer 3) — 80% Complete

**Implemented:**
- ✅ Dashboard with stats
- ✅ 5 Thinking modes
- ✅ ForgeMode session runner
- ✅ Flow Mode navigation
- ✅ Facet decomposition
- ✅ Trail breadcrumbs
- ✅ Concept extraction wizard
- ✅ Session document creation
- ✅ Question/Context API clients (Dec 8)

**Needs Work:**
- 🔄 Evidence panel "Open in Reader" action
- 🔄 Cross-app sync with IES Reader

---

## 4. The Redux Spec — Implementation Roadmap

The `redux/` directory contains the canonical implementation plan. Here's status vs the Integration Checklist:

### Core Types (Section 2) — ✅ COMPLETE
- [x] Context type defined (`schemas/context.py`)
- [x] Question type defined (`schemas/question.py`)
- [x] AnswerBlock type defined
- [x] JourneyEntry type (partial)
- [x] ExtractionProfile (templates)

### Flow Mode v2 (Section 4) — 🔄 75% COMPLETE
- [x] Facet decomposition with AI generation
- [x] Trail navigation breadcrumbs
- [x] Question selector UI
- [ ] Context-aware extraction integration
- [ ] "New since last run" highlighting

### Reader v2 (Section 6) — 🔄 50% COMPLETE
- [x] Basic reading mode
- [x] Question/Context integration
- [ ] Left pane context summary
- [ ] Passage ranking for questions
- [ ] Auto-tagging notes with context

### Journey v2 (Section 7) — 🔄 40% COMPLETE
- [x] Basic journey logging
- [ ] Query/filter helpers
- [ ] Timeline view UI

### Extraction Engine (Section 5) — 🔄 30% COMPLETE
- [x] Entity extraction (Pass 1)
- [ ] Context-aware extraction
- [ ] Profile-based source filtering
- [ ] Question generation from extraction

---

## 5. Immediate Actions Required

### A. Documentation Cleanup (HIGH PRIORITY)

1. **Update Readest CLAUDE.md** — Mark as ARCHIVED
2. **Update master CLAUDE.md** — Remove Readest references in active sections
3. **Update Serena memories** — Remove/update stale Readest references
4. **Archive Readest worktree** — `git worktree remove .worktrees/readest` (after backup)

### B. Memory Updates

Create/update these Serena memories:

1. **`project-architecture-dec9`** — Current 4-layer architecture
2. **`ies-reader-status`** — What's implemented, what's missing
3. **`deprecated-readest`** — Explicit note that Readest is archived

### C. Feature Migration Priority

From Readest to IES Reader:

| Priority | Feature | Complexity | Files to Reference |
|----------|---------|------------|-------------------|
| 1 | Entity highlight click | Medium | `iframeEventHandlers.ts`, `useEntityClick.ts` |
| 2 | Journey persistence | Low | `journeyStorage.ts` |
| 3 | Design system colors | Low | `globals.css`, `EntityTypeFilter.tsx` |
| 4 | Question response capture | Medium | `QuestionsSection.tsx` |
| 5 | Entity overlay transformer | High | `entity.ts` (trie-based) |

---

## 6. Development Priorities (Next Sprint)

### Sprint 1: Foundation Fixes (1-2 days)

1. **Documentation cleanup** (this document + memory updates)
2. **Verify IES Reader builds and runs**
3. **Identify breaking issues in IES Reader**

### Sprint 2: Core Flow Loop (3-5 days)

1. **Entity overlay in IES Reader** — Port from Readest
2. **Click entity → Flow panel** — Complete interaction
3. **Journey breadcrumb trail** — Port UI
4. **LocalStorage persistence** — Port journeyStorage

### Sprint 3: Question Integration (3-5 days)

1. **Question response textarea** — Enhance NotesSheet
2. **Link responses to questions** — Backend integration
3. **Context-aware extraction** — Wire to Question Engine

### Sprint 4: Cross-App Sync (2-3 days)

1. **SiYuan → Reader sync** — Share questions/contexts
2. **Reader → SiYuan sync** — Share highlights/notes
3. **Test complete flow**

---

## 7. Gap Analysis

For detailed mapping of redux specifications to current implementation:

**See:** `docs/GAP-ANALYSIS-2025-12-09.md`

**Summary:** ~45% of redux specs implemented

| Priority | Gap | Status |
|----------|-----|--------|
| P0 | Context Note Parser | ❌ Not started |
| P0 | Extraction Engine | ❌ Not started |
| P0 | Reader → SiYuan Sync | ❌ Not started |
| P1 | ExtractionProfile schema | ❌ Not started |
| P1 | Journey query helpers | ❌ Not started |
| P1 | Passage ranking | ❌ Not started |

---

## 8. Key Files Reference

### IES Reader (Active)

| File | Purpose |
|------|---------|
| `ies/reader/src/App.tsx` | Main app, routing |
| `ies/reader/src/components/Reader.tsx` | epub.js wrapper |
| `ies/reader/src/components/flow/FlowPanel.tsx` | Side panel |
| `ies/reader/src/store/flowStore.ts` | Zustand state |
| `ies/reader/src/services/graphClient.ts` | API client |
| `ies/reader/src/hooks/useFlowLayout.ts` | Responsive mode |

### Backend APIs

| Endpoint | Purpose |
|----------|---------|
| `GET /questions/` | List questions |
| `POST /questions/` | Create question |
| `GET /context/` | List contexts |
| `POST /graph/entity/{name}/facets` | Get/generate facets |
| `GET /graph/entity/{name}/evidence` | Get evidence passages |

### Redux Specs

| File | Purpose |
|------|---------|
| `redux/START_HERE.md` | Overview |
| `redux/IMPLEMENTATION_PLAN.md` | Canonical plan |
| `redux/docs/IES_Integration_Checklist.md` | Task checklist |

---

## 9. Success Criteria

The project is "unified" when:

1. ✅ All CLAUDE.md files agree on what's active
2. ✅ No agent confusion about Readest vs IES Reader
3. ✅ Serena memories are accurate
4. ✅ IES Reader has feature parity with essential Readest features
5. ✅ End-to-end flow works: Read → Select → Explore → Capture → Sync

---

## Appendix: Worktree Quick Reference

```bash
# Active worktrees
cd /home/chris/dev/projects/codex/brain_explore                    # master (backend)
cd /home/chris/dev/projects/codex/brain_explore/.worktrees/ies-reader  # IES Reader
cd /home/chris/dev/projects/codex/brain_explore/.worktrees/siyuan      # SiYuan plugin

# Archived (do not use)
# .worktrees/readest/        — ARCHIVED
# .worktrees/flowmode/       — STALE
# .worktrees/readest-critique/  — ARCHIVED
# .worktrees/siyuan-arch/    — ARCHIVED
# .worktrees/ux-dev/         — ARCHIVED
```

---

*This document supersedes conflicting information in individual CLAUDE.md files.*
