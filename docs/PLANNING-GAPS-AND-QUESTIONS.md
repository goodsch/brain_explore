# Planning Gaps and Technical Review

**Purpose:** Comprehensive reference for moving forward without slowdowns.
**Created:** December 4, 2025
**Status:** Draft for review

---

## Table of Contents

1. [Critical Gaps Blocking Real Usage](#1-critical-gaps-blocking-real-usage)
2. [Technical Stack Review](#2-technical-stack-review)
3. [API Review](#3-api-review)
4. [SiYuan Plugin Review](#4-siyuan-plugin-review)
5. [Readest Interface Review](#5-readest-interface-review)
6. [Component Interaction Map](#6-component-interaction-map)
7. [Probing Questions (Need Answers)](#7-probing-questions-need-answers)
8. [UX Tweaks Needed](#8-ux-tweaks-needed)
9. [Alignment Check](#9-alignment-check)

---

## 1. Critical Gaps Blocking Real Usage

### Gap 1: SiYuan Document Structure (UNDEFINED)

**What's missing:** No defined place for personal knowledge artifacts to go.

**Current state:**
- We have ADHD ontology types: `spark`, `insight`, `thread`, `favorite_problem`
- We have `ADHDKnowledgeGraph` client with schema versioning
- We have Quick Capture UI in plugin
- **BUT:** Where do captured items actually live in SiYuan?

**Questions to resolve:**
- [ ] Which notebook should sparks/insights live in?
- [ ] One file per spark, or daily log, or something else?
- [ ] How do threads map to SiYuan documents?
- [ ] Where do favorite_problems get stored and displayed?
- [ ] What templates are needed for each entity type?
- [ ] How do breadcrumb journeys become visible in SiYuan?

**Proposed structure (needs validation):**
```
/brain_explore/                    # SiYuan notebook
├── /Sparks/                       # Raw captures
│   └── 2025-12-04.md              # Daily log? Or individual files?
├── /Insights/                     # Promoted sparks (formalized)
├── /Threads/                      # Exploration paths
├── /Favorite Problems/            # Navigation anchors (Feynman-style)
├── /Journeys/                     # Reading session breadcrumbs
└── /Concepts/                     # Personal concept development
```

---

### Gap 2: Personal Graph ↔ UI Not Connected

**What's missing:** ADHD ontology exists in code but isn't wired to any frontend.

**Current state:**
- `ADHDKnowledgeGraph` client: ✅ Built
- Backend API endpoints for personal graph: ❌ Not created
- SiYuan plugin calls personal graph: ❌ Not connected
- Readest calls personal graph: ❌ Not connected

**What needs building:**
- [ ] Backend API routes for personal knowledge CRUD
- [ ] Store personal sparks/insights from Quick Capture
- [ ] Display resonance signals in UI
- [ ] Navigate by energy level
- [ ] Track visits to entities

---

### Gap 3: Book Library Inaccessible

**What's missing:** 63 books ingested but users can't browse or open them.

**Current state:**
- Books ingested to Neo4j: ✅
- Backend knows about books: ✅
- UI to browse book library: ❌
- Way to open book from concept: ❌
- Way to jump to passage from source reference: ❌

**Questions:**
- [ ] Where do books physically live? (filesystem path)
- [ ] How does Readest find and open them?
- [ ] Can we deep-link to a specific passage?
- [ ] Should book browser be in SiYuan, Readest, or both?

---

### Gap 4: Cross-App Continuity Missing

**What's missing:** Readest and SiYuan don't share state.

**Current state:**
- Readest saves journeys to backend: ✅ (partial)
- SiYuan loads journeys from backend: ✅ (partial)
- Real-time sync between apps: ❌
- Resume reading session from SiYuan: ❌
- Resume exploration from where you left off in Readest: ❌

**Questions:**
- [ ] What's the sync mechanism? Polling? WebSocket? Manual refresh?
- [ ] What state needs to sync? (journeys, current entity, captures)
- [ ] What happens when offline?

---

### Gap 5: Journey Value Loop Not Closed

**What's missing:** Journeys are captured but never used to improve experience.

**Current state:**
- Journeys saved: ✅
- Journeys displayed in dashboard: ✅
- Journeys analyzed for patterns: ❌
- Patterns used to personalize suggestions: ❌
- Patterns used to improve questions: ❌

---

## 2. Technical Stack Review

### Backend (Layer 2)

| Component | Technology | Status | Notes |
|-----------|------------|--------|-------|
| Framework | FastAPI (Python) | ✅ Solid | Good choice for API-first |
| Database | Neo4j 5.x | ✅ Working | 50k entities, performant |
| Vector Store | Qdrant | ✅ Working | Semantic search functional |
| LLM | Claude API | ✅ Working | Question engine uses it |
| Tests | pytest | ⚠️ 54/61 | 7 failing tests need attention |
| Package Manager | uv | ✅ Working | Fast, reliable |

**Backend concerns:**
- [ ] Which 7 tests are failing? Are they blocking?
- [ ] Is there rate limiting on Claude API calls?
- [ ] What's the latency on thinking partner questions?
- [ ] Is there caching for repeated entity lookups?

### SiYuan Plugin (Layer 3)

| Component | Technology | Status | Notes |
|-----------|------------|--------|-------|
| Framework | Svelte | ✅ Working | Reactive, lightweight |
| TypeScript | Yes | ✅ Working | Type safety |
| Build | Vite | ✅ Working | Fast builds |
| Styling | SCSS | ✅ Working | Design system in place |
| API Calls | forwardProxy | ⚠️ Limitation | SiYuan's proxy required |

**Plugin concerns:**
- [ ] forwardProxy adds latency - is this noticeable?
- [ ] How does the plugin handle backend being down?
- [ ] What's the deploy story? (Currently manual mirror to Docker)
- [ ] Is hot reload working in dev mode?

### Readest (Layer 4)

| Component | Technology | Status | Notes |
|-----------|------------|--------|-------|
| Framework | Tauri | ✅ Working | Rust backend + web frontend |
| Frontend | TypeScript/Svelte | ✅ Working | Same as plugin (good) |
| State | Zustand | ✅ Working | flowModeStore |
| Rendering | foliate-js | ✅ Working | EPUB/PDF support |
| Storage | localStorage | ✅ Working | Journey fallback |

**Readest concerns:**
- [ ] Is Readest building from source or using releases?
- [ ] How are updates managed when upstream Readest changes?
- [ ] Mobile support? (Tauri has some mobile capability)
- [ ] What file formats beyond EPUB/PDF?

---

## 3. API Review

### Currently Implemented

| Endpoint | Method | Working | Used By |
|----------|--------|---------|---------|
| `/graph/stats` | GET | ✅ | Dashboard |
| `/graph/search` | GET | ✅ | Search bars |
| `/graph/explore/{id}` | GET | ✅ | Flow mode |
| `/graph/sources/{id}` | GET | ✅ | Sources section |
| `/graph/suggestions` | GET | ✅ | Dashboard topics |
| `/graph/thinking-partner` | POST | ✅ | Questions section |
| `/journeys` | POST | ✅ | Journey save |
| `/journeys/{id}` | GET | ✅ | Journey load |
| `/journeys/user/{id}` | GET | ✅ | Dashboard list |
| `/capture/process` | POST | ⚠️ | Quick Capture (untested e2e) |
| `/session` | POST | ✅ | Structured Thinking |
| `/session/{id}/message` | POST | ✅ | Dialogue |
| `/profile/{id}` | GET/PUT | ⚠️ | Profile (limited use) |

### Missing APIs

| Needed For | Endpoint | Purpose |
|------------|----------|---------|
| Personal graph | `/personal/sparks` | CRUD for sparks |
| Personal graph | `/personal/insights` | CRUD for insights |
| Personal graph | `/personal/threads` | CRUD for threads |
| Personal graph | `/personal/favorite-problems` | CRUD for anchor questions |
| Personal graph | `/personal/visit` | Track entity visits |
| Book library | `/books` | List available books |
| Book library | `/books/{id}/passages` | Get specific passages |
| Cross-app | `/sync/state` | Current session state |

---

## 4. SiYuan Plugin Review

### Current Architecture

```
Plugin Entry (index.ts)
    │
    ├── Sidebar Icon → Opens Dashboard tab
    │
    └── Dashboard.svelte (Hub)
            │
            ├── ForgeMode.svelte (Structured Thinking)
            │   └── 5 modes: Learning, Articulating, Planning, Ideating, Reflecting
            │
            ├── FlowMode.svelte (Graph Exploration)
            │   └── Entity → Relationships → Sources → Questions
            │
            └── QuickCapture.svelte (Content Processing)
                └── Input → Extract → Suggest → Route
```

### Views and How They Work

**Dashboard:**
- Shows graph stats (entities, relationships, books)
- Lists suggested exploration topics
- Shows recent journeys with resumption
- Queue preview for captures
- Navigation to three modes

**FlowMode (Graph Exploration):**
- Search or browse concepts
- Relationships grouped by type (incoming/outgoing)
- Thinking partner questions at decision points
- Breadcrumb path visible and clickable
- Journey tracking automatic

**ForgeMode (Structured Thinking):**
- Mode selector at top
- Single-pane conversation view
- Mode-specific AI behavior
- Note preview planned but not implemented

**QuickCapture:**
- Text input area
- Process button → calls capture API
- Shows extracted entities
- Shows suggested placements
- Confirmation to route

### Plugin Gaps & Questions

- [ ] **Note integration:** How does output become a SiYuan note?
- [ ] **Block creation:** Does plugin create blocks programmatically?
- [ ] **Notebook selection:** Which notebook do captures go to?
- [ ] **Template system:** Are there note templates?
- [ ] **Bidirectional links:** Can we create `[[concept]]` style links?
- [ ] **Sidebar persistence:** Does state persist when tab closes?

### How Plugin Interacts with SiYuan

| Operation | API Used | Working |
|-----------|----------|---------|
| Create document | `createDocWithMd` | ⚠️ Unclear |
| Insert block | `insertBlock` | ⚠️ Unclear |
| Read block | `getBlockKramdown` | ⚠️ Unclear |
| Search | `sql` query | ⚠️ Unclear |
| Forward API call | `forwardProxy` | ✅ Working |

---

## 5. Readest Interface Review

### Current Architecture

```
Reader Component Tree
    │
    ├── HeaderBar.tsx
    │   └── FlowToggler.tsx (Toggle button)
    │
    ├── ReaderContent.tsx
    │   ├── Book View (foliate-js)
    │   └── FlowPanel.tsx (Split panel when active)
    │       ├── Header.tsx (Pin/close controls)
    │       ├── EntitySection.tsx
    │       ├── RelationshipsSection.tsx
    │       ├── SourcesSection.tsx
    │       └── QuestionsSection.tsx
    │
    └── Annotator.tsx
        └── Selection popup with "Flow" button
```

### User Flow (Current)

1. Open book in Readest
2. Read normally
3. Select text → popup appears with "Flow" button
4. Click Flow → Panel opens with entity lookup
5. See definition, relationships, sources, questions
6. Click related entity → navigate
7. Breadcrumb trail accumulates
8. Close Flow mode → journey saved

### UX Issues Identified

- [ ] **Discovery:** How do users know Flow mode exists?
- [ ] **Entry point:** Is text selection the only way in?
- [ ] **Panel size:** Default width might be wrong
- [ ] **Navigation:** Clicking relationship should jump there (does it?)
- [ ] **Back navigation:** Can you go back in breadcrumb trail?
- [ ] **Source linking:** Can you jump to passage in book from source?
- [ ] **Keyboard shortcuts:** Are there any?
- [ ] **Mobile:** Does this work on mobile Readest?

### Readest UX Tweaks Requested

```
[Space for your specific tweaks - please add what you want to change]

Examples to consider:
- Panel default width (current: 20-50% range)
- Animation timing
- Color scheme integration with book theme
- Question prominence
- Relationship grouping labels
- Source passage preview length
- Empty state messaging
```

---

## 6. Component Interaction Map

### Data Flow Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER ACTIONS                                   │
└─────────────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ READ IN READEST │  │ THINK IN SIYUAN │  │ CAPTURE THOUGHT │
│                 │  │                 │  │                 │
│ • Open book     │  │ • Dashboard     │  │ • Quick Capture │
│ • Select text   │  │ • Forge mode    │  │ • Voice note    │
│ • Toggle Flow   │  │ • Flow mode     │  │ • Photo/link    │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         BACKEND APIS                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Graph    │  │ Session  │  │ Journey  │  │ Capture  │  │ Profile  │  │
│  │ API      │  │ API      │  │ API      │  │ API      │  │ API      │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┼────────┘
        │             │             │             │             │
        └─────────────┴──────┬──────┴─────────────┴─────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       KNOWLEDGE GRAPHS                                   │
│  ┌────────────────────────────┐  ┌────────────────────────────┐        │
│  │    DOMAIN GRAPH (Neo4j)    │  │   PERSONAL GRAPH (Neo4j)   │        │
│  │                            │  │                            │        │
│  │ • 50k entities from books  │  │ • sparks, insights         │  ❌    │
│  │ • 125k relationships       │  │ • threads, favorite_probs  │  NOT   │
│  │ • concept, theory, etc.    │  │ • resonance, energy        │  WIRED │
│  └────────────────────────────┘  └────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
```

### Cross-App State (Current vs. Needed)

| State | Stored Where | Readest Access | SiYuan Access |
|-------|--------------|----------------|---------------|
| Current entity | flowModeStore (Readest) | ✅ | ❌ |
| Journey path | Backend + localStorage | ✅ | ✅ (read only) |
| User profile | Backend | ⚠️ Not used | ⚠️ Limited |
| Sparks/Insights | ADHD graph | ❌ | ❌ |
| Capture queue | SiYuan blocks? | ❌ | ⚠️ Unclear |
| Session context | Backend | ⚠️ | ✅ |

---

## 7. Probing Questions (Need Answers)

### Architecture Questions

1. **Single source of truth:** Is the backend the authority, or can apps have local state that conflicts?

2. **Offline behavior:** What works offline? What fails gracefully?

3. **User identity:** Is `chris` hardcoded everywhere? How does multi-user work?

4. **Real-time sync:** Do we need WebSockets for cross-app updates?

### SiYuan Integration Questions

5. **Document creation:** When Quick Capture routes to "new concept," what notebook/path?

6. **Block types:** Should sparks be SiYuan blocks, documents, or both?

7. **Database queries:** Can we query SiYuan's SQLite for existing concepts?

8. **Backlinks:** How do we create bidirectional references in SiYuan?

9. **Deploy pipeline:** Is manual mirror to Docker acceptable long-term?

### Readest Questions

10. **Book library:** Where are the 63 books stored? Can Readest access them?

11. **Deep linking:** Can we link directly to a passage (CFI or similar)?

12. **Upstream sync:** How do we handle Readest upstream updates?

13. **Build process:** Dev build vs. production build workflow?

### UX Questions

14. **Entry points:** Is "select text → Flow" discoverable enough?

15. **Journey visibility:** Should breadcrumb trail always be visible?

16. **Questions timing:** Should questions appear immediately or on demand?

17. **Mobile priority:** Which app is more important on mobile?

### Data Questions

18. **Personal → Domain:** Can personal insights become domain concepts?

19. **Journey analytics:** What patterns should we extract from journeys?

20. **Profile evolution:** How does the 6-dimension profile update over time?

---

## 8. UX Tweaks Needed

### Readest Flow Mode

| Area | Current | Issue | Proposed |
|------|---------|-------|----------|
| Panel width | 20-50% range | Might be too wide/narrow | [Need your input] |
| Entry discovery | Text selection only | Not obvious | Add header button? |
| Relationship click | Navigates | Might lose context | Open in new panel? |
| Question visibility | Always visible | Takes space | Collapse by default? |
| Source passage | Summary | Too short? | Show more context? |
| Empty state | Generic message | Not helpful | Suggest actions |
| Animation | Standard | [Your preference] | [Your preference] |
| Dark mode | Follows system | [Working?] | [Verify] |

### SiYuan Plugin

| Area | Current | Issue | Proposed |
|------|---------|-------|----------|
| Dashboard layout | Three columns | Mobile unfriendly | Responsive stack? |
| Journey resumption | Click to load | Unclear it's clickable | Better affordance |
| Mode switching | Buttons | Extra clicks | Tabs? Sidebar? |
| Capture feedback | Basic | Need progress indicator | Loading states |
| Error handling | Basic | Silent failures | Toast notifications |

---

## 9. Alignment Check

### Strategy Alignment

| Decision | Current State | Aligned? | Notes |
|----------|---------------|----------|-------|
| Domain-agnostic core | ✅ No therapy assumptions in code | ✅ | Good |
| ADHD-friendly design | ✅ Resonance signals, energy levels | ✅ | Research-backed |
| Four-layer architecture | ✅ All layers built | ✅ | Clean separation |
| Thinking partnership focus | ✅ Questions, breadcrumbs | ✅ | Core value prop |
| User-driven exploration | ⚠️ | ⚠️ | Need more user control |

### Technical Alignment

| Choice | Rationale | Still Valid? | Reconsider? |
|--------|-----------|--------------|-------------|
| Neo4j for both graphs | Unified query language | ✅ Yes | No |
| FastAPI backend | Python ecosystem, async | ✅ Yes | No |
| Svelte for frontends | Reactive, lightweight | ✅ Yes | No |
| SiYuan as hub | Note-taking integration | ⚠️ Uncertain | Maybe |
| Readest fork | E-book + Flow mode | ✅ Yes | No |
| localStorage fallback | Offline resilience | ✅ Yes | No |

### Feature Alignment

| Planned Feature | Current Priority | Should Change? |
|-----------------|------------------|----------------|
| Graph exploration | High | No |
| Structured thinking | High | No |
| Quick capture | High | No |
| Personal graph | Medium → High | Yes, blocks usage |
| Book browser | Medium | Maybe |
| Cross-app sync | Medium | Maybe |
| Profile personalization | Low | No (works enough) |
| Journey analytics | Low | No |

---

## Next Actions

### Immediate (Unblock Usage)

1. **Define SiYuan structure** - Where do sparks/insights go?
2. **Wire personal graph** - Backend APIs + frontend integration
3. **Test Quick Capture e2e** - Verify full flow works

### Near-Term (Polish)

4. **UX tweaks** - Based on your input in Section 8
5. **Cross-app basic sync** - Journey visibility in both apps
6. **Book access** - At least list what's available

### Deferred (Phase 2c+)

7. Journey analytics
8. Profile personalization
9. Multi-domain support

---

## Document Status

- [x] Gaps identified
- [x] Technical stack reviewed
- [x] APIs documented
- [x] Plugin architecture documented
- [x] Readest architecture documented
- [x] Interaction map created
- [x] Probing questions listed
- [ ] **YOUR INPUT NEEDED:** UX tweaks specifics
- [ ] **YOUR INPUT NEEDED:** Answers to probing questions
- [ ] **YOUR INPUT NEEDED:** Priority adjustments

---

*This document should be updated as decisions are made.*
