# FlowMode Enhancement - Wave 1 Specification

**Created:** 2025-12-06
**Status:** ACTIVE
**Parent Plan:** `docs/plans/2025-12-06-flowmode-enhancement-plan.md`

---

## PM Decisions on Open Questions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Visualization priority | **Trail View** (enhanced) | Simpler, builds on existing pattern. Map View deferred to Wave 3. |
| Synthesis scope | **Template-based first** | Faster to ship. LLM enhancement in Phase 4 full implementation. |
| Ingestion changes | **Defer to Wave 3** | Not blocking for core Flow functionality. |
| IES Reader | **SiYuan-first** | IES Reader just shipped, works well. Mirror after SiYuan validated. |

---

## Wave 1 Scope: Minimum Viable Flow Enhancement

**Goal:** Flow starts from context, produces structured notes

### Deliverables

1. **Phase 1: Contextual Awareness**
   - SiYuan EventBus integration (track open note)
   - Context menu: "Start Flow from this note"
   - Dashboard: "Continue from: [Current Note]" section

2. **Phase 2: Spark-Based Initiation (Orientation)**
   - SparkSource type definition
   - OrientationPhase component
   - Backend: `POST /flow/orientation` endpoint

3. **Phase 4: Basic Synthesis (structured note only)**
   - Template-based note generation
   - "Save to SiYuan" integration
   - Backend: `POST /flow/synthesize` endpoint

---

## Phase 1: Contextual Awareness

### 1.1 SiYuan EventBus Integration

**File:** `.worktrees/siyuan/ies/plugin/src/stores/contextStore.ts` (NEW)

```typescript
import { writable } from 'svelte/store';

interface NoteContext {
  noteId: string | null;
  noteTitle: string | null;
  notebookId: string | null;
  blockIds: string[];
  selectedText: string | null;
}

export const noteContext = writable<NoteContext>({
  noteId: null,
  noteTitle: null,
  notebookId: null,
  blockIds: [],
  selectedText: null
});

export function initContextTracking(plugin: Plugin): void {
  // Register loaded-protyle listener
  plugin.eventBus.on('loaded-protyle', (e) => {
    const protyle = e.detail.protyle;
    noteContext.set({
      noteId: protyle.block.rootID,
      noteTitle: protyle.title?.textContent || null,
      notebookId: protyle.notebookId,
      blockIds: [],
      selectedText: null
    });
  });

  // Track selection changes
  document.addEventListener('selectionchange', () => {
    const selection = window.getSelection();
    if (selection && selection.toString().trim()) {
      noteContext.update(ctx => ({
        ...ctx,
        selectedText: selection.toString()
      }));
    }
  });
}
```

### 1.2 Context Menu Integration

**File:** `.worktrees/siyuan/ies/plugin/src/index.ts` (MODIFY)

Add to plugin `onload()`:
```typescript
this.addEditorMenuItem({
  label: this.i18n.flowFromNote,
  icon: 'iconFlow',
  click: (element, event) => {
    const protyle = this.getProtyleFromElement(element);
    if (protyle) {
      openFlowWithContext({
        type: 'note',
        noteId: protyle.block.rootID,
        noteTitle: protyle.title?.textContent || 'Untitled'
      });
    }
  }
});

this.addEditorSelectionMenuItem({
  label: this.i18n.flowFromSelection,
  icon: 'iconFlow',
  click: (element, event) => {
    const selection = window.getSelection()?.toString();
    if (selection) {
      openFlowWithContext({
        type: 'selection',
        noteId: getCurrentNoteId(),
        text: selection,
        blockIds: getSelectedBlockIds()
      });
    }
  }
});
```

### 1.3 Dashboard Context Section

**File:** `.worktrees/siyuan/ies/plugin/src/views/Dashboard.svelte` (MODIFY)

Add below header, before other sections:
```svelte
{#if $noteContext.noteId}
  <section class="context-section">
    <h3>Continue Exploring</h3>
    <div class="context-card" on:click={() => startFlowFromContext()}>
      <div class="note-icon">📄</div>
      <div class="note-info">
        <span class="note-title">{$noteContext.noteTitle || 'Untitled Note'}</span>
        <span class="note-hint">Start Flow from this note</span>
      </div>
      <div class="arrow">→</div>
    </div>
  </section>
{/if}
```

---

## Phase 2: Spark-Based Initiation

### 2.1 SparkSource Types

**File:** `ies/backend/src/ies_backend/schemas/flow.py` (NEW)

```python
from enum import Enum
from pydantic import BaseModel
from typing import Optional, Literal

class SparkType(str, Enum):
    NOTE = "note"
    SELECTION = "selection"
    CAPTURE = "capture"
    HIGHLIGHT = "highlight"
    ENTITY = "entity"

class SparkSource(BaseModel):
    type: SparkType
    # For note/selection sparks
    note_id: Optional[str] = None
    note_title: Optional[str] = None
    text: Optional[str] = None
    block_ids: Optional[list[str]] = None
    # For capture sparks
    capture_id: Optional[str] = None
    raw_text: Optional[str] = None
    # For highlight sparks
    book_id: Optional[str] = None
    location: Optional[str] = None
    # For entity sparks
    entity_id: Optional[str] = None
    entity_name: Optional[str] = None

class Strand(BaseModel):
    id: str
    name: str  # e.g., "The Shame Loop", "Executive Pathway"
    description: str
    starting_entities: list[str]  # Entity IDs to begin exploration

class OrientationRequest(BaseModel):
    spark: SparkSource
    user_id: str

class OrientationResponse(BaseModel):
    extracted_entities: list[dict]  # Entity summaries
    suggested_strands: list[Strand]
```

### 2.2 Orientation Endpoint

**File:** `ies/backend/src/ies_backend/api/flow.py` (NEW)

```python
from fastapi import APIRouter, Depends
from ..schemas.flow import OrientationRequest, OrientationResponse
from ..services.flow_service import FlowService

router = APIRouter(prefix="/flow", tags=["flow"])

@router.post("/orientation", response_model=OrientationResponse)
async def get_orientation(
    request: OrientationRequest,
    flow_service: FlowService = Depends()
) -> OrientationResponse:
    """Generate strand proposals from spark context."""
    return await flow_service.generate_orientation(request)
```

### 2.3 OrientationPhase Component

**File:** `.worktrees/siyuan/ies/plugin/src/views/flow/OrientationPhase.svelte` (NEW)

```svelte
<script lang="ts">
  import type { SparkSource, Strand } from '../types';

  export let spark: SparkSource;
  export let onSelectStrand: (strand: Strand) => void;

  let strands: Strand[] = [];
  let loading = true;

  onMount(async () => {
    const response = await fetchOrientation(spark);
    strands = response.suggested_strands;
    loading = false;
  });
</script>

<div class="orientation-phase">
  <!-- Spark Card (always visible) -->
  <div class="spark-card">
    <div class="spark-icon">{getSparkIcon(spark.type)}</div>
    <div class="spark-content">
      <span class="spark-label">Starting from:</span>
      <span class="spark-text">{getSparkText(spark)}</span>
    </div>
  </div>

  <!-- Strand Proposals -->
  {#if loading}
    <div class="loading">Finding exploration paths...</div>
  {:else}
    <div class="strands-grid">
      {#each strands as strand}
        <div class="strand-card" on:click={() => onSelectStrand(strand)}>
          <h4>{strand.name}</h4>
          <p>{strand.description}</p>
          <div class="entity-preview">
            {#each strand.starting_entities.slice(0, 3) as entity}
              <span class="entity-chip">{entity}</span>
            {/each}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
```

---

## Phase 4: Basic Synthesis

### 4.1 Synthesis Endpoint

**File:** `ies/backend/src/ies_backend/api/flow.py` (ADD)

```python
@router.post("/synthesize")
async def synthesize_session(
    request: SynthesizeRequest,
    flow_service: FlowService = Depends()
) -> SynthesizeResponse:
    """Generate synthesis artifacts from flow session."""
    return await flow_service.generate_synthesis(request)
```

### 4.2 Template-Based Synthesis

**File:** `ies/backend/src/ies_backend/services/flow_service.py` (NEW)

```python
class FlowService:
    def generate_synthesis(self, request: SynthesizeRequest) -> SynthesizeResponse:
        """Template-based synthesis (no LLM in Wave 1)."""

        # Build structured note from visited nodes
        sections = []

        # Section 1: Origin
        sections.append({
            "heading": "Starting Point",
            "content": self._format_spark(request.spark)
        })

        # Section 2: Key Concepts
        visited = self._get_visited_entities(request.visited_nodes)
        sections.append({
            "heading": "Key Concepts Explored",
            "content": self._format_entity_list(visited)
        })

        # Section 3: Connections Found
        sections.append({
            "heading": "Connections",
            "content": self._format_edges(request.visited_edges)
        })

        # Section 4: Insights Captured
        if request.insights:
            sections.append({
                "heading": "Insights",
                "content": self._format_insights(request.insights)
            })

        # Section 5: Questions for Further Exploration
        sections.append({
            "heading": "Open Questions",
            "content": self._generate_questions(visited)
        })

        return SynthesizeResponse(
            structured_note=StructuredNote(
                title=f"Flow Session: {request.spark.get_title()}",
                sections=sections,
                markdown=self._to_markdown(sections)
            ),
            questions=self._generate_question_list(visited)
        )
```

### 4.3 Save to SiYuan Integration

**File:** `.worktrees/siyuan/ies/plugin/src/views/flow/SynthesisPhase.svelte` (NEW)

```svelte
<script lang="ts">
  import { createNote } from '../utils/siyuan-structure';

  export let synthesis: SynthesisResult;

  async function saveToSiYuan() {
    const noteId = await createNote({
      notebook: getThinkingSessionsNotebook(),
      title: synthesis.structured_note.title,
      content: synthesis.structured_note.markdown
    });

    showNotification(`Saved to SiYuan: ${synthesis.structured_note.title}`);
    dispatch('saved', { noteId });
  }
</script>

<div class="synthesis-phase">
  <h3>Exploration Complete</h3>

  <div class="synthesis-preview">
    {@html marked(synthesis.structured_note.markdown)}
  </div>

  <div class="actions">
    <button class="primary" on:click={saveToSiYuan}>
      Save to SiYuan
    </button>
    <button on:click={() => dispatch('continue')}>
      Continue Exploring
    </button>
  </div>
</div>
```

---

## Backend Service Structure

```
ies/backend/src/ies_backend/
├── api/
│   └── flow.py              # NEW: Flow endpoints
├── schemas/
│   └── flow.py              # NEW: SparkSource, Strand, etc.
└── services/
    └── flow_service.py      # NEW: FlowService
```

---

## Testing Plan

### Unit Tests
- `test_flow_service.py`: Orientation generation, synthesis templates
- `test_flow_api.py`: Endpoint request/response validation

### Integration Tests
- Flow from note context → orientation → synthesis → save
- Flow from capture → orientation → synthesis

---

## Acceptance Criteria

### Phase 1 Complete When:
- [ ] Opening a note updates contextStore
- [ ] Context menu shows "Start Flow from this note"
- [ ] Dashboard shows current note context card
- [ ] Clicking context card opens FlowMode with spark

### Phase 2 Complete When:
- [ ] `/flow/orientation` returns 3-5 strands for any spark
- [ ] OrientationPhase displays spark card and strand options
- [ ] Selecting strand transitions to exploration

### Phase 4 Complete When:
- [ ] `/flow/synthesize` returns structured note markdown
- [ ] SynthesisPhase previews generated note
- [ ] "Save to SiYuan" creates note with correct content

---

## Estimated Timeline

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| 1.1 EventBus | 0.5 days | None |
| 1.2 Context Menu | 0.5 days | 1.1 |
| 1.3 Dashboard | 0.5 days | 1.1 |
| 2.1 Types | 0.5 days | None |
| 2.2 Orientation API | 1 day | 2.1 |
| 2.3 OrientationPhase | 1.5 days | 2.2 |
| 4.1-4.2 Synthesis API | 1 day | None |
| 4.3 SynthesisPhase | 1 day | 4.2 |
| Testing | 1 day | All |

**Total:** ~8 days

---

## Next Steps

1. Start with Phase 1.1 (SiYuan EventBus integration)
2. Create `contextStore.ts` in plugin
3. Test with SiYuan dev build
