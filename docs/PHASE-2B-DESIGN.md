# Phase 2b Design: Layer 3 Visual Interface

**Status:** DESIGN READY FOR IMPLEMENTATION
**Date:** December 2, 2025
**Prerequisite:** Phase 2a validation complete ✅

---

## What Phase 2b Is

Phase 2a proved that CLI-based graph exploration creates value. Phase 2b builds a **visual interface** that makes exploration richer and more integrated with note-taking.

**Not a rewrite:** Phase 2b uses the same backend APIs, same thinking partner logic, same exploration model. It just adds a UI.

---

## Phase 2a Learnings That Inform Phase 2b

### 1. Relationship Types Matter
Phase 2a exploration showed relationships but users had to infer their meaning:
- `acceptance --[COMPONENT_OF]--> change`
- `shame --[SUPPORTS]--> self-compassion`

**Phase 2b solution:** Visually distinguish relationship types and explain what they mean

### 2. Graph Structure Reveals Complexity
The thinking partner worked well because it made users pause and reflect. Phase 2a questions worked at **decision points** (choosing what to explore next).

**Phase 2b solution:** Show decision points visually; let AI questions appear when user is about to navigate

### 3. Sparse vs. Rich Areas Need Different Treatment
- Rich: acceptance, shame, change (many connections)
- Sparse: metabolization, nervous system configs (few/no connections)

**Phase 2b solution:** Adaptive depth display; toggle between detail view (rich) and question-driven view (sparse)

### 4. Integration With Notes is Critical
Users exploring find insights but have nowhere to capture them during the flow.

**Phase 2b solution:** Bidirectional link to SiYuan; let users clip insights to their notes

---

## Architecture Decision: Option B (Standalone Web App)

### Comparison of Options

| Aspect | Option A (SiYuan Plugin) | Option B (Web App) | Winner |
|--------|-------------------------|-------------------|--------|
| **Dev Speed** | 30-40 hrs (modify existing) | 40-50 hrs (new codebase) | A (10 hrs faster) |
| **Code Quality** | Complex (14k lines already) | Clean slate | B |
| **Maintenance** | Tied to plugin updates | Independent | B |
| **UX Design** | Constrained by plugin UI | Full control | B |
| **User Context** | Integrated with notes | Separate app | A |
| **Iteration Speed** | Slower (plugin constraints) | Faster (no constraints) | B |
| **Testing** | More complex | Simpler | B |
| **Future Features** | Limited by plugin architecture | Unlimited | B |

### Recommendation: **Option B (Standalone Web App)**

**Rationale:**
1. Phase 1 proved the core value (dialogue)
2. Phase 2a proved exploration creates value
3. Phase 2b should optimize for **exploration UX**, not minimize development time
4. A 10-hour time difference is worth cleaner code that's easier to iterate on
5. Web app can integrate with SiYuan later (bidirectional API)

**Risk:** Extra 10 hours development
**Benefit:** Better foundation for Phase 3+ features (multi-user, domain expansion, analytics)

---

## Phase 2b Technical Architecture

### Frontend Stack
- **Framework:** React (Vue alternative if preference)
- **Visualization:** D3.js or similar for graph rendering
- **Real-time:** WebSocket for thinking partner questions
- **State:** Zustand or similar (lightweight)

### Backend Integration
Uses existing IES backend APIs:
- `/chat` endpoint for thinking partner questions
- Knowledge graph APIs for navigation
- `/session/process` for saving exploration sessions

### Data Flow

```
User Action
    ↓
React UI (show visual graph, relationships)
    ↓
IES Backend API (navigate, search)
    ↓
Neo4j Graph (return concepts, relationships)
    ↓
React UI (render next level of graph)
    ↓
[User decision point]
    ↓
Claude API (generate thinking partner question)
    ↓
React UI (overlay question on graph)
    ↓
[User explores or captures insight]
```

---

## Phase 2b MVP Features

### Core Features (MVP)
1. **Concept Search** — Find starting point
2. **Graph Visualization** — Show related concepts and relationships
3. **Navigation** — Click to explore related concept
4. **Thinking Partner** — AI questions at decision points
5. **Breadcrumb Trail** — Show exploration path visually
6. **Save Session** — Export exploration to markdown and/or SiYuan

### Nice-to-Have (Phase 2b+)
- Multiple relationship type display
- Connection strength visualization
- Search across multiple concepts
- Comparison view (two concepts side-by-side)
- Historical exploration replay
- Integration with phase 1 concepts (create backlinks)

### Not in Phase 2b
- Multi-user support
- Advanced analytics
- Domain generalization
- Full PDF reading integration
- MCP server integration

---

## Design Mockup Structure

### Main Interface Layout

```
┌─────────────────────────────────────────────────────────┐
│ Concept Explorer                              [Search]  │
├────────────────────┬────────────────────────────────────┤
│                    │                                    │
│   Search Results   │   Graph Visualization              │
│   or Starting      │   (center: current concept)        │
│   Concepts         │   (surrounding: related concepts)  │
│                    │   (labels: relationship types)     │
│                    │                                    │
│   [acceptance]     │      ┌─────────────────┐           │
│   [shame]          │      │    acceptance    │           │
│   [change]         │      │    (current)     │           │
│                    │      └─────────────────┘           │
│                    │       ↙         ↘                 │
│                    │    [change]   [hero]              │
│                    │    COMPONENT   SUPPORTS           │
│                    │                                    │
├────────────────────┼────────────────────────────────────┤
│ Exploration Path   │                                    │
│ 1. acceptance      │ [Thinking Partner Question Modal]  │
│ 2. change          │ "What does it feel like in your   │
│ 3. hero            │ body when you truly accept        │
│                    │ something you've been trying..."  │
│ [Save] [Export]    │                                    │
└────────────────────┴────────────────────────────────────┘
```

### Key Interactions

1. **Search:** User enters concept → get matches → click to start
2. **Explore:** Click concept → see related → choose next
3. **Think:** At decision points, AI question appears → user reflects
4. **Capture:** Save insight → added to markdown or SiYuan
5. **Review:** See breadcrumb path → jump to earlier concept → alternative route

---

## Success Criteria (Phase 2b)

### Quantitative
- [ ] Web app loads exploration in <2 seconds
- [ ] Relationships render visually for all tested concepts
- [ ] Thinking partner questions generated at decision points
- [ ] 5 full explorations completed (same as Phase 2a)
- [ ] No errors or crashes during exploration

### Qualitative
- [ ] Visual relationships are easier to understand than CLI text
- [ ] Interface feels like exploration, not search
- [ ] Thinking partner questions feel natural (not popping unexpectedly)
- [ ] Users discover same insights as Phase 2a (validation that UI improves, not breaks)
- [ ] Integration point with notes feels natural (or planned for future)

### Comparative (vs. Phase 2a CLI)
- [ ] Same insights discovered but in less time
- [ ] Graph visualization reveals patterns CLI didn't
- [ ] Visual interface adds value without adding confusion
- [ ] Would users prefer this to CLI? (Yes)

---

## Implementation Plan

### Phase 2b Scope: 40-50 hours

#### Week 1: Setup & Basic Navigation (12-15 hours)
- [ ] React project scaffolding
- [ ] Connect to IES backend `/search` and `/graph` endpoints
- [ ] Build concept search component
- [ ] Build basic graph visualization (node + related nodes)
- [ ] Implement click-to-navigate

#### Week 2: Thinking Partner & Polish (15-18 hours)
- [ ] Integrate thinking partner questions
- [ ] Build breadcrumb trail display
- [ ] Add relationship type labels
- [ ] Session save/export functionality
- [ ] UI polish and error handling

#### Week 3: Testing & Iteration (12-15 hours)
- [ ] 5 validation explorations (same as Phase 2a)
- [ ] Bug fixes and UX refinement
- [ ] Performance optimization
- [ ] Documentation

#### Buffer (5-10 hours)
- [ ] Unexpected complexity
- [ ] Additional polish
- [ ] Future-proofing

**Total: 44-58 hours (estimate)**

---

## Deployment Model

### Development
- Local React dev server
- Connect to running IES backend (localhost:8081)
- Test with therapy knowledge graph

### Deployment
- Build static React bundle
- Serve from simple HTTP server or S3
- Backend remains at :8081

### Future Integration
- Can integrate with SiYuan later (API calls back to SiYuan for note capture)
- Can be deployed standalone or embedded

---

## Phase 2b Success Looks Like

After Phase 2b completion, the system has:

1. **Visual graph exploration** — Users can see relationships visually
2. **Guided navigation** — AI asks thinking partner questions at the right moments
3. **Integrated insight capture** — Users can save discoveries to notes
4. **Validated approach** — Same exploration produces same insights as CLI but faster/better
5. **Foundation for Phase 3** — Clean web architecture ready for multi-user, analytics, domain expansion

---

## Open Questions For Phase 2b Design

### 1. How Much Graph Detail to Show?
- Show all relationships at once (cluttered)?
- Show only first-degree relationships (limited)?
- Toggle between detail and simplified views?

**Recommendation:** Start with first-degree only, add toggle for depth

### 2. How To Handle Sparse Areas?
- Some concepts (metabolization) have no graph connections
- In sparse areas, what does the UI show?

**Recommendation:** Show what exists; thinking partner helps when nothing visible

### 3. Where Does Insight Capture Happen?
- In-graph annotation?
- Separate note editor?
- Integration with SiYuan?

**Recommendation:** Phase 2b: Simple text capture → save to markdown. Phase 2b+: SiYuan integration

### 4. How To Show Relationship Strength?
- Graph can show some relationships are stronger than others
- Line thickness? Color? Labels?

**Recommendation:** Start with labels; thickness if time allows

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Graph visualization complexity | High | Use D3.js library; start simple |
| Integration with IES backend | Medium | APIs already exist; test early |
| Thinking partner timing | Medium | Test question placement during Phase 2b |
| Performance with large graphs | Low | Lazy load relationships; pagination |
| React learning curve | Low | Use CRA; straightforward architecture |

---

## Parking Lot (Not Phase 2b)

These are explicitly deferred:
- Advanced analytics and pattern visualization
- Multi-concept comparison
- Historical exploration replay
- Advanced search (filters, boolean)
- Integration with other domains
- Mobile UI

---

## Recommendation & Next Steps

### Immediate
1. ✅ Phase 2a validation complete
2. Approve Phase 2b design (web app, 40-50 hours)
3. Create tech stack document (React, D3, specific libraries)
4. Set up project scaffolding

### Phase 2b Kickoff
1. Week 1: Basic navigation + graph visualization
2. Week 2: Thinking partner + session management
3. Week 3: Testing + refinement

### Phase 2b Success Criteria
- Same 5 explorations produce same insights as Phase 2a
- Visual interface adds value without adding confusion
- Ready for Phase 3 (either multi-user or domain expansion)

---

## Architecture Timeline

```
Phase 1 (Complete)          ✅ Dialogue + Concepts
Phase 2a (Complete)         ✅ CLI Exploration
Phase 2b (Ready)            → Visual Interface (Web App)
Phase 3 (Planned)           → Multi-Domain or Multi-User
Phase 4+ (Future)           → Analytics, Advanced Features
```

---

**Document Status:** Design complete, ready for implementation
**Author:** Claude Code
**Last Updated:** December 2, 2025
**Recommendation:** Proceed to Phase 2b with Option B (Standalone Web App)
