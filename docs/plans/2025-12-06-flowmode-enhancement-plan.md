# FlowMode Enhancement Plan

**Created:** 2025-12-06
**Status:** DRAFT - Awaiting Review
**Reference:** `Flow mode implementation guide.md`

## Executive Summary

Transform FlowMode from a "graph browser with questions" into a **Thinking Partnership Engine** that:
1. Never starts from zero (spark-based initiation)
2. Guides exploration through 4 phases
3. Produces synthesis artifacts (notes, diagrams, questions)
4. Integrates with capture queue and open notes

---

## Phase 1: Foundation - Contextual Awareness (Priority: CRITICAL)

**Goal:** Plugin knows what note is open and can start Flow from context

### 1.1 SiYuan EventBus Integration
- Register `loaded-protyle` listener for note changes
- Track `currentNoteId`, `currentNoteTitle`, `currentBlockId`
- Create `contextStore.ts` (Svelte store) for reactive state

### 1.2 Context Menu Integration
- Add "Start Flow from this note" to note context menu
- Add "Start Flow from selection" for text selections
- Wire to FlowMode with `initialContext` prop

### 1.3 Dashboard Context Section
- Show "Continue from: [Current Note Title]" when note is open
- One-click to launch FlowMode with note context

**Backend Changes:**
```
POST /flow/start-from-context
Input: { noteId, noteTitle, selectedText?, blockIds[]? }
Output: { entities[], suggestedStrands[], initialFlowSession }
```

**Estimated Effort:** 3-4 days

---

## Phase 2: Spark-Based Initiation (Priority: CRITICAL)

**Goal:** Flow never starts from blank - always from spark/capture/context

### 2.1 Spark Types
```typescript
type SparkSource =
  | { type: 'note', noteId: string, noteTitle: string }
  | { type: 'selection', noteId: string, text: string, blockIds: string[] }
  | { type: 'capture', captureId: string, rawText: string }
  | { type: 'highlight', bookId: string, location: string, text: string }
  | { type: 'entity', entityId: string, entityName: string };
```

### 2.2 Orientation Phase (NEW)
Replace current search-first UI with:
1. **Spark Display** - Show the context that triggered Flow
2. **Strand Proposals** - 3-5 AI-generated "story paths" to explore
3. **One-click selection** - Pick a strand to begin exploration

**Backend Changes:**
```
POST /flow/orientation
Input: { spark: SparkSource, userId: string }
Output: {
  extractedEntities: Entity[],
  suggestedStrands: [
    { id, name: "The Shame Loop", description, nodes[], edges[] },
    { id, name: "Executive Pathway", description, nodes[], edges[] },
    ...
  ]
}
```

**UI Changes:**
- New `OrientationPhase.svelte` component
- Spark card at top (always visible)
- Strand cards below (clickable to start exploration)

**Estimated Effort:** 5-7 days

---

## Phase 3: 4-Phase State Machine (Priority: HIGH)

**Goal:** Guided exploration with phase transitions

### 3.1 Phase Definitions
```typescript
type FlowPhase = 'orientation' | 'branching' | 'deepening' | 'synthesis';

interface FlowSession {
  id: string;
  spark: SparkSource;
  phase: FlowPhase;
  visitedNodes: string[];
  visitedEdges: string[];
  breadcrumbs: Breadcrumb[];
  insights: Insight[];
  selectedStrand?: Strand;
}
```

### 3.2 Phase Components
- `OrientationPhase.svelte` - Strand selection (Phase 2 above)
- `BranchingPhase.svelte` - Path exploration with contrast options
- `DeepeningPhase.svelte` - Node deep-dive with definitions, contradictions
- `SynthesisPhase.svelte` - Generate artifacts

### 3.3 Flow Verbs Implementation
| Verb | Trigger | Backend Endpoint |
|------|---------|------------------|
| `branch` | Click node → "Show branches" | `POST /flow/branch` |
| `zoom_out` | Button in toolbar | `POST /flow/zoom-out` |
| `zoom_in` | Click cluster | `POST /flow/zoom-in` |
| `contrast` | Select 2 nodes → "Compare" | `POST /flow/contrast` |
| `paths_between` | Select 2 nodes → "Find paths" | `POST /flow/paths-between` |
| `synthesize` | Button in toolbar | `POST /flow/synthesize` |

**Estimated Effort:** 7-10 days

---

## Phase 4: Synthesis Engine (Priority: CRITICAL)

**Goal:** Flow produces reusable artifacts

### 4.1 Synthesis Outputs
1. **Structured Note** - Markdown with headings, key points, evidence
2. **Diagram Spec** - Mermaid/GraphViz for visual representation
3. **Question List** - Generated questions for further exploration
4. **Model Narrative** - Prose explanation of discovered connections

### 4.2 Backend Implementation
```
POST /flow/synthesize
Input: {
  sessionId: string,
  visitedNodes: string[],
  visitedEdges: string[],
  breadcrumbs: Breadcrumb[],
  insights: Insight[]
}
Output: {
  structuredNote: { title, sections[], markdown },
  diagram: { mermaidSpec, description },
  questions: Question[],
  narrative: string
}
```

### 4.3 SiYuan Integration
- "Save to SiYuan" button creates note from synthesis
- Auto-link to source spark/capture
- Add to appropriate notebook (Thinking Sessions or Models & Concepts)

**Estimated Effort:** 5-7 days

---

## Phase 5: Visual Views (Priority: MEDIUM)

**Goal:** Multiple visualization options for the same data

### 5.1 View Types
1. **Trail View** (Current, enhanced) - Vertical journey timeline
2. **Map View** - Graph visualization with D3/force-directed
3. **Matrix View** - 2-3 dimensional comparison grid
4. **Timeline View** - Developmental/historical progression

### 5.2 View Switcher
- Toolbar with view icons
- State preserved across view switches
- Current context highlighted in all views

**Estimated Effort:** 7-10 days (Map View alone is complex)

---

## Phase 6: Capture Integration (Priority: HIGH)

**Goal:** Seamless Capture → Think → Flow → Synthesize pipeline

### 6.1 Capture Queue → Flow Bridge
- From Dashboard capture queue, add "Explore in Flow" action
- Creates FlowSession with capture as spark
- Transitions capture status appropriately

### 6.2 Thinking Session → Flow Bridge
- After structured thinking session, "Open in Flow" button
- Uses thinking session's entities as spark context
- Links flow session back to thinking session

### 6.3 Flow → Capture Loop
- During Flow, "Capture this insight" creates new CaptureItem
- Insight becomes first-class node in graph
- New sparks can spawn sub-flows

**Estimated Effort:** 4-5 days

---

## Phase 7: Ingestion Pipeline Updates (Priority: MEDIUM)

**Goal:** Graph data supports Flow features

### 7.1 New Relationship Metadata
- `story_label` - Human-readable path description
- `contrast_notes` - What differs between connected concepts
- `developmental_order` - For timeline views

### 7.2 Graph Indices for Flow
- High-betweenness nodes (pivot points)
- Community detection (clusters for zoom)
- Conflict-rich subgraphs (interesting exploration)

### 7.3 Insight Nodes
- New entity type: `Insight`
- Links to user, session, source entities
- Participates in graph traversal

**Estimated Effort:** 3-4 days

---

## Implementation Order

### Wave 1: Minimum Viable Flow Enhancement (2 weeks)
1. Phase 1: Contextual Awareness
2. Phase 2: Spark-Based Initiation (Orientation)
3. Phase 4: Basic Synthesis (structured note only)

**Outcome:** Flow starts from context, produces notes

### Wave 2: Full State Machine (2 weeks)
1. Phase 3: 4-Phase State Machine
2. Phase 6: Capture Integration

**Outcome:** Complete guided exploration loop

### Wave 3: Visual & Polish (1-2 weeks)
1. Phase 5: Map View (priority visual)
2. Phase 7: Ingestion updates
3. Remaining Phase 5 views

**Outcome:** Visual exploration, full feature set

---

## Backend Endpoints Summary

| Endpoint | Phase | Purpose |
|----------|-------|---------|
| `POST /flow/start-from-context` | 1 | Initialize from note/selection |
| `POST /flow/orientation` | 2 | Generate strand proposals |
| `POST /flow/select-strand` | 2 | Begin exploration on strand |
| `POST /flow/branch` | 3 | Get branching options |
| `POST /flow/zoom-out` | 3 | Collapse to clusters |
| `POST /flow/zoom-in` | 3 | Expand cluster |
| `POST /flow/contrast` | 3 | Compare two concepts |
| `POST /flow/paths-between` | 3 | Find paths between nodes |
| `POST /flow/synthesize` | 4 | Generate artifacts |
| `POST /flow/add-insight` | 6 | Create insight node |

---

## Questions for Review

1. **Visualization priority:** Start with Map View (graph) or enhanced Trail View?
2. **Synthesis scope:** Full LLM generation or template-based first?
3. **Ingestion changes:** Required for Wave 1 or can defer?
4. **IES Reader:** Mirror these changes or SiYuan-first?

---

## Next Steps

1. Review and approve this plan
2. Use Codex for deep architectural reasoning on Phase 2-3
3. Begin Phase 1 implementation (contextual awareness)
4. Iterate based on findings
