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

- [ ] Fork Readest and set up development environment
- [ ] Add Flow mode toggle button to reader UI
- [ ] Create split-panel view for Flow mode
- [ ] Build Entity Panel component:
  - [ ] Definition section
  - [ ] Relationships section (grouped by type)
  - [ ] Other Sources section
  - [ ] Thinking Partner questions
- [ ] Integrate with backend Graph API
- [ ] Implement breadcrumb journey capture (local storage first)
- [ ] Add journey save to backend when Flow session ends

---

## Technology Stack

- **Framework:** Tauri (Rust backend + web frontend)
- **UI:** TypeScript + Svelte
- **Rendering:** foliate-js (EPUB, PDF)
- **Source:** https://github.com/readest/readest (MIT license)

---

## Key Files to Create

```
readest/                       # Forked Readest or new package
├── packages/
│   └── flow-mode/             # New Flow mode components
│       ├── EntityPanel.svelte
│       ├── FlowView.svelte
│       ├── JourneyTracker.ts
│       └── api/
│           └── graphClient.ts # Backend API client
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
