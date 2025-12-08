# Flow Mode Evolution Plan

**Goal:** Transform basic Context Layer MVP into full graph-interactive Flow Mode per `Flow_Graph_Interaction_Spec.md`.

**Date:** 2025-12-08

---

## Current State (MVP)

### Backend ✅
- `/context/parse` - Parse Context Note markdown
- `/context/save-parsed` - Persist to Neo4j
- `/context/{id}/search` - Keyword search returns Concept nodes + source books
- `/context/{id}/journey` - Log/retrieve journey entries
- `/graph/explore/{concept}` - Get entity + 1-hop neighbors (existing)

### Frontend (FlowMode.svelte) ✅
- Detects Context Note via `contextBlockId` prop
- Parses Key Questions, Areas, Core Concepts
- Renders question buttons
- Shows search results on click
- Basic CSS styling

### What's Missing
- ~~Entity Focus view (click result → entity details)~~ ✅ Done
- Facet system (entity → facets → sub-entities)
- ~~Trail navigation (breadcrumbs)~~ ✅ Done
- Journey panel (show interaction history)
- Graph Slice visualization

---

## Proposed Phases

### Phase 1: Navigation Foundation ✅ COMPLETE (Dec 8, 2025)
**Goal:** Enable clicking through Question → Entity with trail tracking.

**Backend:**
- [x] `/graph/explore/{concept}` already returns entity + 1-hop neighbors (used by navigateToEntity)
- [ ] Add facet templates for common entities (ADHD, EF, etc.) — Deferred to Phase 2

**Frontend:**
- [x] Add navigation state machine: `FocusState` = `'idle' | 'question' | 'entity' | 'facet'`
- [x] Implement Trail component (breadcrumb stack with click-to-navigate)
- [x] Create EntityFocus view component (shows name, type, description, neighbors, source books)
- [x] Wire search result clicks to `navigateToEntity()`
- [x] Wire Core Concepts chips to `navigateToEntity()`
- [x] Add comprehensive CSS styles for trail and entity focus

**Implementation Details:**
- `FlowMode.svelte` lines 113-250: Navigation functions (`pushTrail`, `popTrail`, `navigateToEntity`, `navigateBack`, etc.)
- `FlowMode.svelte` lines 847-942: Trail and EntityFocus UI components
- `FlowMode.svelte` lines 2350-2599: CSS styles for navigation components

**Data Flow:**
```
User clicks Q1 → searchForQuestion() → sets focusState='question' → pushes to trail
User clicks entity result →
  navigateToEntity() → fetches entity details → sets focusState='entity'
  Trail: [Context, Q1, "entity name"]
  Center: EntityFocus view with entity details + neighbors
User can click neighbors to continue navigation → trail grows
User can click trail items to navigate back
```

### Phase 2: Entity Enrichment (In Progress)
**Goal:** Show meaningful entity details with facets.

**Backend:**
- [x] Create `/graph/entity/{name}` endpoint with: (Dec 8, 2025)
  - Description (from KG)
  - Related concepts (1-hop with relationship types)
  - Source books with evidence snippets
- [ ] Define facet schema and storage
- [ ] Implement facet extraction (LLM-powered or template-based)

**Frontend:**
- [ ] EntityFocus shows: summary, facets list, related concepts
- [ ] FacetFocus view for drilling into facets
- [ ] "Pin as Key Concept" quick action

**Facet Templates (examples):**
```yaml
ADHD:
  - Diagnosis & Assessment
  - Symptoms & Presentation
  - Neurobiology
  - Executive Function
  - Time Perception
  - Treatment & Strategies

Executive Function:
  - Components (WM, inhibition, flexibility)
  - Development
  - Assessment
  - Impairments
  - Interventions
```

### Phase 3: Journey Integration
**Goal:** Show chronological interaction trace in UI.

**Backend:**
- [ ] Ensure all navigation actions log journey entries
- [ ] Add journey entry types: `question_select`, `entity_focus`, `facet_expansion`, `graph_traverse`

**Frontend:**
- [ ] JourneyPanel component (right side)
- [ ] Real-time updates as user navigates
- [ ] Filter by entry type
- [ ] Clickable entries to jump back

### Phase 4: Graph Visualization
**Goal:** Visual graph slice for spatial navigation.

**Backend:**
- [ ] `/graph/slice` endpoint returning nodes + edges for visualization
- [ ] Mark nodes as "new" vs "existing" in KG

**Frontend:**
- [ ] GraphSlice component using D3/Cytoscape/custom SVG
- [ ] Click node to navigate
- [ ] Highlight new discoveries
- [ ] ADHD-friendly: max 10-15 visible nodes

### Phase 5: Polish & ADHD Optimization
**Goal:** Ensure UI supports ADHD exploration patterns.

- [ ] "Back to Question" always visible
- [ ] "Promote to Key Question" quick action
- [ ] Session persistence (resume where you left off)
- [ ] Keyboard navigation
- [ ] Progress indicators

---

## Dependencies

```
Phase 1 (Navigation)
    ↓
Phase 2 (Entity Enrichment) ←── Can start facet backend work in parallel
    ↓
Phase 3 (Journey Panel) ←── Can start after Phase 1
    ↓
Phase 4 (Graph Viz) ←── Requires Phase 2 entity data
    ↓
Phase 5 (Polish)
```

**Parallelizable:**
- Phase 3 (Journey) can happen alongside Phase 2
- Backend facet work can happen alongside Phase 1 frontend

---

## Recommended Implementation Order

1. **Phase 1A: Navigation State** - Add state machine + Trail to FlowMode.svelte
2. **Phase 1B: EntityFocus View** - Basic entity display on click
3. **Phase 2A: Backend Entity Details** - Rich entity endpoint
4. **Phase 2B: Facet Templates** - Define facets for key entities
5. **Phase 3: Journey Panel** - Show interaction history
6. **Phase 4: Graph Slice** - Visual navigation
7. **Phase 5: Polish** - ADHD optimizations

---

## Technical Decisions Needed

1. **Facet Storage:**
   - Option A: Hardcoded templates per entity type
   - Option B: KG-stored facets as nodes
   - Option C: LLM-generated on demand
   - **Recommendation:** Start with A (templates), evolve to B

2. **Graph Visualization:**
   - Option A: D3.js force-directed
   - Option B: Cytoscape.js
   - Option C: Custom SVG
   - **Recommendation:** Cytoscape.js (good balance of features/complexity)

3. **State Management:**
   - Option A: Svelte stores
   - Option B: URL-based state
   - Option C: Both (stores + URL sync)
   - **Recommendation:** C for session persistence

---

## Success Criteria

Phase 1 complete when:
- User can click Q → see results → click entity → see entity details
- Trail shows navigation path
- Back button works

Phase 2 complete when:
- Entities show meaningful descriptions + facets
- Clicking facet shows related concepts

Full spec complete when:
- All 5 states from spec are implemented
- Journey panel shows full interaction history
- Graph slice visualizes 1-hop neighbors
- ADHD-friendly constraints applied
