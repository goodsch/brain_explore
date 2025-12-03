# Phase 2b Design: Plugin Extension for Visual Graph Exploration

**Status:** APPROVED
**Date:** December 2, 2025
**Approach:** Extend existing SiYuan plugin (Option A from original design)

---

## Summary

Extend the existing IES SiYuan plugin to add visual graph exploration (Layer 3). The plugin will have three views: Dashboard, Forge (dialogue), and Flow (exploration).

---

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Graph logic location | Backend API | Consistent with existing pattern; reusable by other clients |
| Thinking partner | Separate endpoint | UI controls when questions appear (at decision points) |
| Plugin structure | Dashboard + 2 modes | Clear separation of concerns; modes complement each other |
| Graph visualization | Radial layout | Fits sidebar width; cleaner than force-directed |
| Mode names | Forge / Flow | Evocative: shape ideas (Forge) vs navigate freely (Flow) |

---

## Backend Endpoints (New)

Add to `ies/backend/src/ies_backend/api/graph.py`:

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/graph/explore/{concept}` | GET | Related concepts + relationships | `{nodes: [], relationships: []}` |
| `/graph/search` | GET | Search concepts by text | `{results: [{name, type, score}]}` |
| `/graph/sources/{concept}` | GET | Supporting text chunks | `{sources: [{text, book, page}]}` |
| `/graph/stats` | GET | Graph statistics | `{entities: n, relationships: n, books: n}` |
| `/graph/suggestions` | GET | Dashboard topic suggestions | `{recent: [], connected: [], new: []}` |
| `/graph/thinking-partner` | POST | Generate reflection question | `{question: "..."}` |

### Request/Response Schemas

```python
# GET /graph/search?q=acceptance&limit=10
# Response:
{
    "results": [
        {"name": "acceptance", "type": "Concept", "score": 0.95},
        {"name": "radical acceptance", "type": "Concept", "score": 0.82}
    ]
}

# GET /graph/explore/acceptance?depth=1
# Response:
{
    "concept": "acceptance",
    "nodes": [
        {"name": "change", "type": "Concept", "labels": ["Concept"]},
        {"name": "hero", "type": "Concept", "labels": ["Concept"]}
    ],
    "relationships": [
        {"start": "acceptance", "type": "COMPONENT_OF", "end": "change"},
        {"start": "acceptance", "type": "SUPPORTS", "end": "hero"}
    ]
}

# POST /graph/thinking-partner
# Request:
{
    "concept": "acceptance",
    "path": ["grief", "loss", "acceptance"],
    "related": ["change", "hero", "surrender"]
}
# Response:
{
    "question": "What does acceptance feel like in your body compared to resignation?"
}
```

---

## Plugin Views

### Dashboard

Main landing view with:

```
┌─────────────────────────────────────┐
│  IES Explorer                       │
├─────────────────────────────────────┤
│  Graph Stats                        │
│  ├─ 50,234 entities                 │
│  ├─ 127,891 relationships           │
│  └─ 63 books indexed                │
├─────────────────────────────────────┤
│  Suggested Topics                   │
│  ├─ Recently Explored: grief, shame │
│  ├─ Most Connected: change, self    │
│  └─ New Concepts: metabolization    │
├─────────────────────────────────────┤
│  [  Forge  ]    [  Flow  ]          │
├─────────────────────────────────────┤
│  Recent Sessions                    │
│  ├─ Dec 2 - Acceptance exploration  │
│  └─ Dec 1 - Shame dialogue          │
└─────────────────────────────────────┘
```

**Components:**
- `Dashboard.svelte` - Main dashboard view
- Stats display (calls `/graph/stats`)
- Suggested topics (calls `/graph/suggestions`)
- Mode buttons (navigate to Forge/Flow)
- Recent sessions list

### Forge Mode (Layer 2 - Existing, Renamed)

The existing dialogue functionality (`ies-sidebar.svelte`), renamed from "Dialogue" to "Forge".

- AI-guided questioning
- Reveals thinking patterns
- Session management
- Entity extraction on end

No changes needed except renaming.

### Flow Mode (Layer 3 - New)

Visual graph exploration:

```
┌─────────────────────────────────────┐
│  Flow                    [← Back]   │
├─────────────────────────────────────┤
│  Search: [acceptance______] [Go]    │
├─────────────────────────────────────┤
│                                     │
│           ┌─────────┐               │
│    [change]│acceptance│[hero]       │
│           └─────────┘               │
│         [surrender] [grief]         │
│                                     │
│  COMPONENT_OF  SUPPORTS  RELATES_TO │
├─────────────────────────────────────┤
│  Path: grief → loss → acceptance    │
├─────────────────────────────────────┤
│  [💭 Think]              [💾 Save]  │
└─────────────────────────────────────┘
```

**Components:**
- `FlowMode.svelte` - Container for Flow exploration
- `ConceptSearch.svelte` - Search input with autocomplete
- `RadialGraph.svelte` - D3.js radial visualization
- `Breadcrumbs.svelte` - Exploration path display
- `ThinkingPartner.svelte` - Question display modal/panel

**Interactions:**
1. **Search** - Type concept name, get suggestions, select to explore
2. **Navigate** - Click any related concept to make it the new center
3. **Think** - Click button to request a thinking partner question
4. **Save** - Export exploration path as markdown

---

## Component Hierarchy

```
IESExplorerPlugin
├── index.ts (plugin entry, registers dock/tab)
└── views/
    ├── Dashboard.svelte
    │   ├── StatsDisplay.svelte
    │   ├── SuggestedTopics.svelte
    │   ├── ModeButtons.svelte
    │   └── RecentSessions.svelte
    ├── ForgeMode.svelte (existing ies-sidebar, renamed)
    └── FlowMode.svelte
        ├── ConceptSearch.svelte
        ├── RadialGraph.svelte
        ├── Breadcrumbs.svelte
        └── ThinkingPartner.svelte
```

---

## Data Flow

```
User Action (search/click)
    ↓
FlowMode.svelte (dispatch)
    ↓
ies-graph.ts (API client)
    ↓
IES Backend (/graph/* endpoints)
    ↓
KnowledgeGraph class (Neo4j)
    ↓
Response → FlowMode → RadialGraph (render)
```

---

## New Files

### Backend
- `ies/backend/src/ies_backend/api/graph.py` - Graph API endpoints
- `ies/backend/src/ies_backend/schemas/graph.py` - Pydantic schemas

### Plugin
- `ies/plugin/src/ies-graph.ts` - Graph API client
- `ies/plugin/src/views/Dashboard.svelte`
- `ies/plugin/src/views/FlowMode.svelte`
- `ies/plugin/src/components/ConceptSearch.svelte`
- `ies/plugin/src/components/RadialGraph.svelte`
- `ies/plugin/src/components/Breadcrumbs.svelte`
- `ies/plugin/src/components/ThinkingPartner.svelte`
- `ies/plugin/src/components/StatsDisplay.svelte`
- `ies/plugin/src/components/SuggestedTopics.svelte`
- `ies/plugin/src/stores/flow-session.ts` - Flow mode state

---

## MVP Scope

### In Scope
- Backend: 6 graph endpoints
- Dashboard: stats, suggestions, mode buttons, recent sessions
- Forge: existing dialogue (renamed)
- Flow: search, radial graph, navigation, breadcrumbs, thinking partner, save

### Not in MVP
- Source text viewing in Flow (show in later iteration)
- Session history/replay
- SiYuan notes integration (clip insights to notes)
- Relationship type filtering
- Multiple concept comparison
- Advanced search (filters, boolean)

---

## Success Criteria

### Quantitative
- [ ] All 6 graph endpoints return correct data
- [ ] Dashboard loads in <1 second
- [ ] Flow exploration works for 5 test concepts
- [ ] Radial graph renders up to 20 related nodes
- [ ] Thinking partner generates relevant questions

### Qualitative
- [ ] Flow mode feels like exploration, not search
- [ ] Radial visualization is readable and intuitive
- [ ] Mode switching (Dashboard ↔ Forge ↔ Flow) is smooth
- [ ] Same insights discoverable as Phase 2a CLI

---

## Implementation Order

1. **Backend endpoints** (4-6 hours)
   - Add graph.py router
   - Implement all 6 endpoints
   - Test with existing CLI

2. **Plugin restructure** (2-3 hours)
   - Create views/ directory
   - Move existing sidebar to ForgeMode.svelte
   - Create Dashboard.svelte shell
   - Update index.ts routing

3. **Dashboard** (3-4 hours)
   - Stats display
   - Suggested topics
   - Mode buttons
   - Recent sessions

4. **Flow mode - core** (6-8 hours)
   - ConceptSearch component
   - RadialGraph visualization (D3.js)
   - Click navigation
   - Breadcrumbs

5. **Flow mode - polish** (4-5 hours)
   - Thinking partner integration
   - Save exploration
   - Error handling
   - Loading states

6. **Testing & refinement** (4-6 hours)
   - 5 validation explorations
   - Bug fixes
   - UX polish

**Total estimate: 23-32 hours**

---

## Dependencies

- D3.js (for radial graph visualization)
- Existing: Svelte, SiYuan plugin SDK, Anthropic API

---

## Open Questions (Resolved)

1. ~~Where should graph logic live?~~ → Backend API
2. ~~Thinking partner bundled or separate?~~ → Separate endpoint
3. ~~Plugin UI structure?~~ → Dashboard + Forge + Flow
4. ~~Graph visualization approach?~~ → Radial layout
5. ~~Mode names?~~ → Forge / Flow
6. ~~Dashboard "interesting" topics?~~ → Recent + most-connected + new

---

## Next Steps

1. Create implementation plan with detailed tasks
2. Set up git worktree for isolated development
3. Start with backend endpoints
4. Iterate through plugin components

---

**Document Status:** Design complete, approved for implementation
**Author:** Claude Code + Chris
**Last Updated:** December 2, 2025
