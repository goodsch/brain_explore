# Discovery Report: IES UI/UX Component Inventory

> Phase 1 Analysis - December 9, 2025

## Executive Summary

This report documents all user-facing components, interaction points, and current UX patterns across the IES system. Analysis covered ~14,000 lines of UI code across two applications.

---

## 1. IES Reader (React)

**Total Code:** ~3,500 lines (components + hooks + store)
**Architecture:** React + Zustand + CSS Modules

### 1.1 Component Hierarchy

```
App
├── LibraryBrowser
│   └── CalibreDialog (book catalog)
└── Reader (Main Container)
    ├── reader-toolbar
    │   ├── Back button
    │   ├── Book title
    │   └── Flow toggle + WhatsNewBadge
    ├── reader-content
    │   └── ReactReader (epub.js)
    ├── reader-fab-note (mobile only)
    ├── FlowPanel (sidebar)
    │   ├── FlowPanelTabs (Explore | Timeline)
    │   ├── WhatsNewSection
    │   ├── RunExtractionButton
    │   ├── AreasChips
    │   ├── QuestionSelector
    │   ├── RelevantPassagesSection
    │   └── JourneyTimeline
    ├── NotesSheet (bottom modal)
    └── reader-selection-bar (floating)
```

### 1.2 Key Components

| Component | Lines | Purpose | Interactions |
|-----------|-------|---------|--------------|
| Reader.tsx | 469 | EPUB wrapper | Selection, navigation, highlights |
| FlowPanel.tsx | 191 | Side panel container | Tab switching, refresh |
| QuestionSelector.tsx | 190 | Question CRUD | Create, select, dropdown |
| WhatsNewSection.tsx | 205 | New items display | Expand/collapse groups |
| RelevantPassagesSection.tsx | 181 | Ranked passages | Expand cards, navigate |
| JourneyTimeline.tsx | 178 | Exploration history | Grouping, expand entries |
| NotesSheet.tsx | 116 | Note capture modal | Type selection, text input |

### 1.3 State Management (flowStore.ts - 431 lines)

**State Categories:**
- UI State: `isFlowPanelOpen`, `flowPanelWidth`, `activePanelTab`
- User/Session: `userId`, `currentSessionId`, `syncStatus`
- Context: `currentContextId`, `questions`, `currentQuestionId`
- Content: `newItemsSummary`, `relevantPassages`, `journeyTimeline`
- Cross-App: `journeyTrail`, `lastAppSource`

### 1.4 Hooks

| Hook | Lines | Purpose |
|------|-------|---------|
| useSessionSync | 297 | Cross-app state sync (5s/30s polling) |
| useReadingPosition | 188 | CFI tracking with debounce |
| useQuestionSync | 131 | Question load/create |
| useFlowLayout | 62 | Responsive mode detection |
| useEntityLookup | 5 | **STUB - NOT IMPLEMENTED** |
| useEntityOverlay | 3 | **STUB - NOT IMPLEMENTED** |
| useEntityHighlighter | 3 | **STUB - NOT IMPLEMENTED** |

### 1.5 Styling

**Design System:** `/src/styles/design-system.css`
- Dark theme primary (reader)
- Warm paper tones (flow panel)
- Entity type colors (5 types)
- Glass morphism effects

**Pain Points:**
- Theme mismatch between reader (dark) and panel (light)
- Mixed CSS modules + Tailwind classes
- Flow panel colors not in design system

---

## 2. SiYuan Plugin (Svelte)

**Total Code:** ~10,377 lines
**Architecture:** Svelte + TypeScript + SCSS

### 2.1 Component Hierarchy

```
Dashboard.svelte
├── FlowMode.svelte (3,251 lines) - CRITICAL
│   ├── Search panel
│   ├── Entity focus panel
│   │   ├── ReframesTab
│   │   ├── EvidenceSection
│   │   ├── QuestionsSection
│   │   └── HighlightsSection
│   ├── Context mode panel
│   └── Trail navigation
├── ForgeMode.svelte (3,123 lines)
│   ├── Mode selector (5 modes)
│   ├── Conversation panel
│   ├── Progress panel
│   └── ConceptExtractor
├── QuickCapture.svelte (1,040 lines)
├── Inbox.svelte (782 lines)
└── SettingsPanel.svelte
```

### 2.2 Flow Mode Architecture

**State Machine:**
```typescript
type FocusState = 'idle' | 'question' | 'entity' | 'facet'
```

**Navigation Pattern:**
- Stack-based trail navigation
- Single entity focus (exclusive)
- Card-based relationship display
- NO GRAPH VISUALIZATION

**Key Functions:**
- `navigateToEntity(name, addToTrail)` - Fetch & display entity
- `navigateToFacet(entity, facet)` - Show facet entities
- `navigateToTrailIndex(i)` - Jump back in history
- `navigateBack()` - Pop trail stack

### 2.3 Forge Mode (Thinking Sessions)

**5 Thinking Modes:**
| Mode | Icon | Template | AI Approach |
|------|------|----------|-------------|
| Learning | 📚 | mechanism-map | Socratic |
| Articulating | 💭 | clarify-intuition | Mirroring |
| Planning | 🎯 | (none) | Solution-focused |
| Ideating | 💡 | (none) | Divergent |
| Reflecting | 🪞 | (none) | Phenomenological |

**9 Question Classes:**
| Class | Color | Cognitive Function |
|-------|-------|-------------------|
| Schema-Probe | #4a90d9 | Structure discovery |
| Boundary | #7b68ee | Edge clarification |
| Dimensional | #20b2aa | Spectrum positioning |
| Causal | #d4874a | Mechanism tracing |
| Counterfactual | #da70d6 | What-if exploration |
| Anchor | #3cb371 | Concrete grounding |
| Perspective-Shift | #cd853f | Viewpoint change |
| Meta-Cognitive | #778899 | Thinking patterns |
| Reflective-Synthesis | #6495ed | Integration |

### 2.4 Design System

**Files:**
- `_design-tokens.css` (32KB)
- `design-system.scss` (8.1KB)
- `colors.css`, `typography.css`, `spacing.css`, `animations.css`

**Color Palette:**
```css
/* Backgrounds (Warm scholarly) */
--bg-deep: #f5f2ed
--bg-base: #faf8f5
--bg-elevated: #ffffff

/* Text */
--text-primary: #2d2a26
--text-secondary: #5c5650
--text-muted: #8a847b

/* Accent */
--accent-primary: #c9872e (Amber)
--accent-secondary: #5a8a7a (Sage)
--accent-tertiary: #8b7aa0 (Violet)

/* Entity Types */
--entity-concept: #2563eb
--entity-person: #059669
--entity-theory: #7c3aed
--entity-framework: #ea580c
--entity-assessment: #dc2626
```

---

## 3. Interaction Point Catalog

### 3.1 Click Interactions (Total: ~100)

**Reader:**
- Text selection → Action bar
- Flow toggle → Panel open/close
- Question select → Load passages
- Passage expand → Show full text
- Timeline entry → View details
- Highlight button → Create annotation

**SiYuan:**
- Entity card → Navigate to entity
- Neighbor → Navigate deeper
- Facet chip → Show facet entities
- Trail item → Jump back
- Tab → Switch content
- Mode button → Select thinking mode

### 3.2 Input Interactions

| Field | Component | Behavior |
|-------|-----------|----------|
| Search | FlowMode | Debounced (300ms) |
| Topic | ForgeMode | Required validation |
| Message | ForgeMode | Auto-grow textarea |
| Note | NotesSheet | Pre-fill from selection |
| Question | QuestionSelector | Create + auto-select |

### 3.3 Drag/Pan/Zoom

**Current:** NONE IMPLEMENTED

**Opportunity:** This is the core gap for movement-based navigation

### 3.4 Keyboard Shortcuts

**Current:** Minimal
- Enter - Submit search/form
- Escape - Close dropdown/modal

**Missing:**
- Arrow key navigation
- Tab focus management
- Vim-style shortcuts

---

## 4. Cross-App Sync Architecture

### 4.1 Session State API

**Endpoint:** `/session-state/{user_id}`

**Synced State:**
```typescript
{
  active_context_id: string | null
  active_question_id: string | null
  current_book: {
    book_id: string
    cfi: string  // EPUB position
    chapter: string
    progress: number
  }
  current_entity_id: string | null
  journey_trail: JourneyTrailItem[]
  last_app_source: 'reader' | 'siyuan'
  last_activity_at: timestamp
}
```

### 4.2 Polling Strategy

| App | Active | Background |
|-----|--------|------------|
| Reader | 5s | 30s |
| SiYuan | 5s | 30s |

**Write Debounce:** 3s

### 4.3 Journey Trail Item

```typescript
{
  entity_id: string
  entity_name: string
  entity_type: string
  source_app: 'reader' | 'siyuan'
  timestamp: ISO string
  dwell_seconds: number
  source_context: string
}
```

---

## 5. Current UX Patterns

### 5.1 Strengths

1. **Glass morphism design** - Modern depth hierarchy
2. **Entity type colors** - Consistent visual language
3. **Breadcrumb trail** - Clear navigation history
4. **Cross-app sync** - Seamless state sharing
5. **Question class tracking** - Cognitive coverage visibility
6. **Responsive breakpoints** - Mobile considerations

### 5.2 Pattern Issues

| Pattern | Problem | Severity |
|---------|---------|----------|
| Card navigation | No spatial graph view | CRITICAL |
| Theme split | Dark reader vs light panel | HIGH |
| Stub hooks | Entity lookup broken | HIGH |
| Modal nesting | ConceptExtractor over dialogs | MEDIUM |
| Filter disconnect | Area chips don't filter | MEDIUM |
| Dense badges | 9 question classes | MEDIUM |
| Mobile panels | No collapse behavior | MEDIUM |

---

## 6. API Integration Summary

### 6.1 Graph Endpoints

| Endpoint | Purpose | Used By |
|----------|---------|---------|
| GET /graph/search | Entity search | FlowMode |
| GET /graph/entity/{name} | Entity details | FlowMode |
| GET /graph/entity/{name}/facets | Facet list | FlowMode |
| GET /graph/entity/{name}/neighbors | Related entities | FlowMode |
| POST /reframes/generate | Create metaphors | ReframesTab |

### 6.2 Session Endpoints

| Endpoint | Purpose | Used By |
|----------|---------|---------|
| GET /session-state/{id} | Get state | Both apps |
| PATCH /session-state/{id} | Update state | Both apps |
| POST /session-state/{id}/heartbeat | Keep alive | Both apps |
| GET /session-state/{id}/continue | Journey data | Both apps |

### 6.3 Question Engine

| Endpoint | Purpose | Used By |
|----------|---------|---------|
| POST /question-engine/detect-state | User state | ForgeMode |
| POST /question-engine/generate-questions | Next question | ForgeMode |
| GET /question-engine/question-classes | Class list | ForgeMode |

---

## 7. Files for Redesign

### 7.1 Critical Priority

| File | Lines | Why Critical |
|------|-------|--------------|
| FlowMode.svelte | 3,251 | Main redesign target |
| ForgeMode.svelte | 3,123 | Session UI improvements |
| flowStore.ts | 431 | State architecture |
| design-system.css | ~500 | Token consolidation |

### 7.2 High Priority

| File | Lines | Why Important |
|------|-------|---------------|
| Reader.tsx | 469 | Selection handling |
| FlowPanel.tsx | 191 | Panel architecture |
| QuestionSelector.tsx | 190 | CRUD patterns |
| ContextSyncService.ts | 500+ | Sync logic |

---

## 8. Recommendations Summary

### Immediate Actions
1. Implement graph visualization in FlowMode
2. Unify theme across reader and panel
3. Complete entity lookup hooks
4. Add keyboard navigation

### Design System
1. Consolidate duplicate color definitions
2. Document interactive states
3. Create component size scale
4. Define animation choreography

### Novel Interactions
1. Pan/zoom for graph navigation
2. Momentum-based scrolling
3. Gesture vocabulary for exploration
4. Physics-based node attraction

---

*End of Discovery Report*
