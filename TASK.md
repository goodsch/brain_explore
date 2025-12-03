# Readest Worktree Task Briefing

**Branch:** `feature/readest-integration`
**Phase:** 2 - Readest MVP
**Focus:** Layer 4 - Reading + Flow Exploration Interface

---

## What This Worktree Is For

This worktree develops **Readest integration** - adding Flow mode to the Readest e-book reader that enables conceptual exploration of the knowledge graph while reading.

**Core Insight:** "Instead of reading one book, you're reading a concept." Flow mode surfaces all sources discussing the current entity, transforming reading from linear consumption into conceptual exploration.

---

## Goals

1. **Flow Mode Toggle** - Button/gesture to switch from linear reading to split-panel Flow view
2. **Entity Panel** - Right panel showing definition, relationships, sources, thinking partner questions
3. **Breadcrumb Journey Capture** - Track user's exploration path through entities
4. **Graph API Integration** - Connect to backend for entity data

---

## Architecture Context

```
Layer 4: READEST (THIS WORKTREE) - Reading + Flow exploration
Layer 3: SIYUAN PLUGIN          - Processing hub (separate worktree)
Layer 2: BACKEND                - API already extended with journey/capture endpoints
Layer 1: KNOWLEDGE GRAPH        - Neo4j with 50k+ entities
```

---

## Available Backend Endpoints

The main branch already has these endpoints ready for use:

### Graph API (existing)
- `GET /graph/entity/{id}` - Get entity details
- `GET /graph/explore/{entity_id}?depth=1&limit=20` - Neighborhood exploration
- `GET /graph/sources/{entity_id}` - Book references for entity

### Journey API (new - just created)
- `POST /journeys` - Save breadcrumb journey
- `GET /journeys/{id}` - Retrieve journey
- `GET /journeys/user/{user_id}` - List user's journeys
- `PATCH /journeys/{id}` - Update journey
- `DELETE /journeys/{id}` - Delete journey

### Question Engine (existing)
- `POST /question-engine/question` - Get thinking partner question for entity

---

## Key Data Structures

### BreadcrumbJourney (capture this during Flow sessions)
```typescript
interface BreadcrumbJourney {
  id: string;
  user_id: string;
  started_at: string;
  ended_at?: string;
  entry_point: {
    type: 'book' | 'search' | 'dashboard';
    reference: string;
  };
  path: Array<{
    entity_id: string;
    entity_name: string;
    timestamp: string;
    source_passage?: string;
    dwell_time_seconds: number;
  }>;
  marks: Array<{
    type: 'highlight' | 'annotation' | 'question';
    entity_id: string;
    content: string;
    timestamp: string;
  }>;
  thinking_partner_exchanges: Array<{
    question: string;
    response?: string;
    timestamp: string;
  }>;
}
```

---

## Deliverables Checklist

- [x] Fork Readest and set up development environment
- [x] Add Flow mode toggle button to reader UI (FlowToggler.tsx in HeaderBar)
- [x] Create split-panel view for Flow mode (FlowPanel.tsx - resizable, pinnable)
- [x] Build Entity Panel component:
  - [x] Definition section (EntitySection.tsx)
  - [x] Relationships section grouped by type (RelationshipsSection.tsx)
  - [x] Other Sources section (SourcesSection.tsx)
  - [x] Thinking Partner questions (QuestionsSection.tsx)
- [x] Integrate with backend Graph API (graphClient.ts)
- [x] Implement breadcrumb journey capture (journeyStorage.ts + flowModeStore)
- [x] Add journey save to backend when Flow session ends (FlowToggler)
- [x] Text selection triggers Flow lookup (Flow button in AnnotationPopup)

---

## Technology Stack

- **Framework:** Tauri (Rust backend + web frontend)
- **UI:** TypeScript + Svelte
- **Rendering:** foliate-js (EPUB, PDF)
- **Source:** https://github.com/readest/readest (MIT license)

---

## Key Files Created

```
readest/apps/readest-app/src/
├── store/
│   └── flowModeStore.ts           # Zustand store for Flow mode state & journey tracking
├── services/flow/
│   ├── graphClient.ts             # Backend API client for knowledge graph
│   └── journeyStorage.ts          # Local storage persistence for journeys
├── hooks/
│   └── useFlowEntity.ts           # Entity lookup hook integrating API + store
└── app/reader/components/
    ├── FlowToggler.tsx            # Toggle button for Flow mode in HeaderBar
    ├── flowpanel/
    │   ├── FlowPanel.tsx          # Main split-panel container (resizable, pinnable)
    │   ├── Header.tsx             # Panel header with title and close button
    │   ├── EntitySection.tsx      # Entity definition display
    │   ├── RelationshipsSection.tsx # Grouped relationships with navigation
    │   ├── SourcesSection.tsx     # Book sources discussing entity
    │   ├── QuestionsSection.tsx   # Thinking partner questions
    │   └── index.ts               # Exports
    └── annotator/
        └── Annotator.tsx          # Modified - Flow button added to selection popup
```

---

## Design Document Reference

Full design details: `docs/plans/2025-12-03-integrated-reading-knowledge-system.md`

Key sections:
- Section 2: Readest Integration (Layer 4)
- Section 2.3: Flow Mode details
- Section 2.4: Breadcrumb Journey Capture
- Section 7.1: Readest ↔ Backend API contracts

---

## Backend Health Check

Before starting, verify backend is running:
```bash
curl http://localhost:8081/health
# Should return: {"status": "healthy"}
```

---

## Integration Notes

- This worktree focuses on the reading interface only
- SiYuan plugin work happens in `.worktrees/siyuan`
- Backend is on main branch - pull updates as needed
- Sync between Readest and SiYuan is Phase 4 (later)
