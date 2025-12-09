# IES Flow Mode + Knowledge Pipeline — Implementation Plan

**Created:** 2025-12-08
**Purpose:** Consolidated spec synthesizing all redux documents into a single actionable plan

---

## Core Vision

**The Problem:** You can't plan knowledge in advance. You don't know what you don't know.

**The Solution:** Facet decomposition on demand. When you look at any concept, AI shows you its components. You click to explore. The graph grows from curiosity, not planning.

**The Interaction:**
1. Open "ADHD" concept
2. See facets: `Diagnosis` | `Symptoms` | `Physiology` | `Time Perception` | `Treatment`
3. Click "Physiology" → becomes new focus
4. See sub-facets: `Dopamine` | `Prefrontal Cortex` | `Neural Circuitry`
5. Evidence from your books attaches as you explore

---

## What Already Exists

### Backend (Complete)
- Context service with CRUD operations
- Question service with graph relationships
- Journey service for event logging
- Neo4j knowledge graph with ~300 entities
- Entity extraction pipeline (Pass 1 complete)

### SiYuan Templates (Complete)
- Book Template (9 sections, highlight tracking)
- Theory Template (12 sections with Evidence Pool)
- Feynman Problem Template (12 sections)
- Concept Template (10 sections)
- Spark Template (5 sections, promotion tracking)
- Session Template (9 sections)
- Hub Pages (Theories, Sources, Problems)

### Attribute Schema (Complete)
```
Document:  custom-type, custom-id, custom-status, custom-context
Section:   custom-section, custom-section-id
Block:     custom-block-type, custom-processed, custom-source, custom-source-cfi,
           custom-entity-refs, custom-confidence
```

### Reader (Partial)
- Readest with library browsing
- Highlight capture (needs SiYuan sync)
- CFI support for jump-back

### SiYuan Plugin (Partial)
- Flow Mode panel exists
- Needs facet decomposition UI

---

## What Needs to Be Built

### Phase 1: Facet Decomposition Core

**Goal:** When viewing any entity, see its components and explore them.

#### 1.1 Backend: Facet Generation Endpoint

```python
POST /api/v1/entities/{entity_id}/facets

Request:
{
  "entity_type": "concept" | "problem" | "theory",
  "force_refresh": false
}

Response:
{
  "entity_id": "...",
  "facets": [
    {
      "id": "facet_123",
      "name": "Physiology",
      "type": "component",
      "exists_in_graph": true,
      "entity_id": "entity_456"  // if exists
    },
    {
      "id": "facet_124",
      "name": "Time Perception",
      "type": "component",
      "exists_in_graph": false,
      "entity_id": null
    }
  ],
  "cached": true,
  "generated_at": "2025-12-08T..."
}
```

**Implementation:**
- Check cache first (facets don't change often)
- If miss: call LLM with entity context
- Prompt: "What are the key components/facets of {entity_name}? Return as JSON array."
- Match facets against existing KG entities
- Cache result with TTL (24h or until entity updated)

#### 1.2 Backend: Create Entity from Facet

```python
POST /api/v1/entities

Request:
{
  "name": "Dopamine",
  "type": "concept",
  "parent_entity_id": "entity_physiology",
  "relationship": "component_of",
  "source": "facet_decomposition"
}

Response:
{
  "id": "entity_789",
  "name": "Dopamine",
  ...
}
```

**Implementation:**
- Create entity node in Neo4j
- Create relationship edge to parent
- Queue for evidence extraction (Phase 2)

#### 1.3 SiYuan Plugin: Facet Display

**UI Component:**
```
┌─────────────────────────────────┐
│ Focus: ADHD                     │
├─────────────────────────────────┤
│ Components:                     │
│ [Diagnosis] [Symptoms]          │
│ [Physiology] [Time Perception]  │
│ [Executive Function] [Treatment]│
├─────────────────────────────────┤
│ Related Questions:              │
│ • Why does ADHD affect time?    │
│ • How does medication work?     │
├─────────────────────────────────┤
│ [Expand] [View Evidence]        │
└─────────────────────────────────┘
```

**Behavior:**
- On note open: detect entity type from `custom-type` attribute
- Call `/api/v1/entities/{id}/facets`
- Display facets as clickable chips
- Chips show badge if entity exists in graph
- Click: set as new focus (update panel) or open note

#### 1.4 Trail Navigation

**Left Panel Addition:**
```
Trail: ADHD → Physiology → Dopamine
       [^]      [^]         [*]
```

- Clickable breadcrumbs
- Current focus marked
- "Back" goes up trail
- Trail persists in session

---

### Phase 2: Evidence Attachment

**Goal:** Connect source highlights to entities as you explore.

#### 2.1 Backend: Evidence Search Endpoint

```python
GET /api/v1/entities/{entity_id}/evidence

Response:
{
  "entity_id": "...",
  "evidence": [
    {
      "id": "ev_001",
      "source_id": "book_stolen_focus",
      "source_title": "Stolen Focus",
      "chunk_text": "Dopamine plays a crucial role in...",
      "location": { "cfi": "/6/4[chap03]...", "page": 42 },
      "confidence": 0.85,
      "extracted_at": "2025-12-08T..."
    }
  ],
  "total_count": 12,
  "sources_searched": 5
}
```

**Implementation:**
- Query inverted index for entity name + aliases
- Return ranked chunks with source metadata
- Include CFI for jump-back to Reader

#### 2.2 Background Evidence Extraction

**Trigger:** When entity is created or first focused

**Process:**
1. Queue entity for evidence extraction
2. Search sources for entity mentions
3. Extract relevant chunks
4. Score relevance (keyword + embedding)
5. Store as evidence links in Neo4j
6. Update entity `custom-processed` status

**Priority Queue:**
- Entities you've clicked get priority
- New entities from facet decomposition queued lower
- Background processing during idle time

#### 2.3 SiYuan Plugin: Evidence Panel

**UI Addition:**
```
┌─────────────────────────────────┐
│ Evidence for: Dopamine          │
├─────────────────────────────────┤
│ From "Stolen Focus" (p.42):     │
│ "Dopamine plays a crucial..."   │
│ [Open in Reader] [Add to Note]  │
├─────────────────────────────────┤
│ From "ADHD 2.0" (p.87):         │
│ "The dopamine hypothesis..."    │
│ [Open in Reader] [Add to Note]  │
├─────────────────────────────────┤
│ 10 more passages available      │
│ [Show More]                     │
└─────────────────────────────────┘
```

---

### Phase 3: Reader Integration

**Goal:** Highlights flow from Reader → SiYuan → Evidence Pool

#### 3.1 Highlight Sync Service

**Flow:**
```
Reader highlight → IES Backend → SiYuan Book Note
                              → Processing Queue
```

**Highlight Record:**
```json
{
  "id": "hl_001",
  "book_id": "calibre:123",
  "text": "Attention is the beginning of devotion.",
  "note": "Connects to Entry Point Theory",
  "cfi": "/6/4[chap01]!/4/2/1:0",
  "created_at": "2025-12-08T14:30:00Z",
  "context_id": "problem_start_zero",
  "processed": false
}
```

#### 3.2 Highlight Processing

**On new highlight:**
1. Append to Book Note's `## Highlights` section
2. Extract entity mentions (light NER)
3. Match to existing KG entities
4. Queue for deeper processing if confidence low

**Processed highlight in SiYuan:**
```markdown
> "Attention is the beginning of devotion." — Mary Oliver
{: custom-block-type="highlight" custom-id="HL_001" custom-source="calibre:123" custom-source-cfi="/6/4..." custom-entity-refs="attention,devotion,entry-point" custom-processed="true" }
```

#### 3.3 Book Note Auto-Creation

**On first highlight from a book:**
1. Check if Book Note exists
2. If not: create from Book Template
3. Fill metadata from Calibre
4. Set `custom-status="reading"`

---

### Phase 4: Question Graph Integration

**Goal:** Questions emerge from exploration and connect to evidence.

#### 4.1 Question Extraction from Facets

**During facet decomposition:**
- Identify facets that are questions vs. concepts
- "Why does ADHD affect time?" → Question node
- "Time Perception" → Concept node

**Question fields:**
```json
{
  "id": "q_001",
  "text": "Why does ADHD affect time perception?",
  "type": "why",
  "status": "unknown",
  "parent_entity_id": "entity_adhd",
  "related_concept_ids": ["entity_time_perception", "entity_adhd"],
  "evidence_count": 0,
  "confidence": 0.0
}
```

#### 4.2 Question Status Updates

**As evidence accumulates:**
- `unknown` → 0 evidence passages
- `partial` → 1-5 evidence passages
- `answered` → 5+ passages + user confirmation

**Display in Flow panel:**
```
Questions:
• Why does ADHD affect time? [partial - 3 sources]
• How does medication work? [unknown]
```

---

## Implementation Order

### Sprint 1: Facet Core (1-2 weeks) ✅ COMPLETE
- [x] Backend: `/entities/{id}/facets` endpoint with AI generation
- [x] Backend: Facet caching (persisted to Neo4j)
- [x] Backend: Create entity from facet endpoint (`POST /entity`)
- [x] Plugin: Facet display component (FlowMode.svelte lines 1106, 1403 - clickable chips)
- [x] Plugin: Trail breadcrumbs (FlowMode.svelte - trailStack, standaloneTrailStack)

### Sprint 2: Evidence (1-2 weeks) ✅ COMPLETE
- [x] Backend: `/entities/{id}/evidence` endpoint (GET /graph/entity/{name}/evidence)
- [x] Backend: Evidence extraction queue (Chunk→Entity MENTIONS population) — `scripts/enrich_chunk_evidence.py`
- [x] Backend: Inverted index queries (two-tier: chunks then book mentions)
- [x] Plugin: Evidence panel component (EvidenceSection.svelte - lines 1149, 1455)
- [x] Plugin: "Open in Reader" action — Deferred (not needed per user feedback)

### Sprint 3: Reader Sync (1-2 weeks) ✅ COMPLETE
- [x] Backend: Highlight sync endpoint (`/highlights` API with CRUD + batch sync)
- [x] Backend: Book Note auto-creation (`SiYuanClient.create_book_note()` + auto-append highlights)
- [x] Reader: Export highlights to IES (`highlightApi.ts` client + Reader integration)
- [x] Plugin: Highlight display in Book Notes (`HighlightsSection.svelte` + `highlightApi.ts`)

### Sprint 4: Questions + Clarification (1-2 weeks)
- [ ] Backend: Question extraction from facets
- [ ] Backend: Question status tracking
- [ ] Backend: Guided clarification endpoint (pre-decomposition dialogue)
- [ ] Plugin: Question display in Flow panel
- [ ] Plugin: "Mark as answered" action
- [ ] Plugin: Clarification dialogue before facet generation

**Clarification Flow (from System Summary):**
When user opens a new question/concept for exploration:
1. Brief dialogue: "What specifically do you want to understand about X?"
2. AI clarifies: What is being asked, why it matters, what's unclear
3. Identify prerequisite concepts
4. Then proceed to facet decomposition

### Sprint 5: Journey Persistence (1-2 weeks)
- [ ] Backend: Journey export endpoint (`POST /journeys/export`)
- [ ] Backend: Journey resumption endpoint (`GET /journeys/{id}/resume`)
- [ ] Plugin: "Save Journey" action in Flow panel
- [ ] Plugin: Journey browser in `/Flow_Outputs/Journeys/`
- [ ] Plugin: "Resume Journey" with suggested next steps
- [ ] SiYuan: Journey document template

**Journey Record Structure:**
```markdown
# Journey: Understanding ADHD Physiology
Date: 2025-12-09
Starting Question: "How does ADHD affect the brain?"

## Path
1. ADHD (focus) → decomposed
2. Physiology (clicked) → decomposed
3. Dopamine (clicked) → evidence found
4. Prefrontal Cortex (clicked)

## Sources Consulted
- "Stolen Focus" (p.42, p.87)
- "ADHD 2.0" (p.15)

## Insights Captured
- Connection between dopamine and motivation
- PFC development differences

## Suggested Next Steps
- Explore: Executive Function (related to PFC)
- Question: How does medication affect dopamine?
```

### Sprint 6: Multi-Source Flow Reader (2-3 weeks) — FUTURE
- [ ] Reader: Question-driven reading mode
- [ ] Reader: Cross-book passage navigation by entity
- [ ] Backend: Multi-source evidence aggregation
- [ ] Backend: Source recommendation when evidence is thin
- [ ] Plugin: "Open in Flow Reader" action

**Multi-Source Reading (from System Summary):**
- Start from question, not book
- See passages from *multiple* sources organized by entity/sub-question
- Navigate across books following conceptual threads
- Recommend new sources when coverage is incomplete

---

## Architecture Decisions

### Caching Strategy
- Facets: Cache 24h, invalidate on entity update
- Evidence: Cache 1h, refresh on focus
- Highlights: Real-time sync, no cache

### Processing Priority
1. Entities user clicks (immediate)
2. Facets of focused entity (background, high priority)
3. New highlights (background, medium priority)
4. Full library scan (background, low priority)

### Storage
- Entities + Relations: Neo4j
- Facet cache: Redis or SQLite
- Highlights: PostgreSQL (existing)
- Processing queue: Redis or PostgreSQL

### LLM Calls
- Facet decomposition: GPT-4 or Claude (quality matters)
- Entity extraction from highlights: GPT-3.5 (speed matters)
- Batch where possible to reduce costs

---

## Success Criteria

1. **Exploration Flow:** Open ADHD → see facets → click Physiology → see sub-facets → find evidence. All in <2 seconds per step.

2. **Graph Growth:** After 1 hour of exploration, 20+ new entity nodes with relationships.

3. **Evidence Connection:** 80% of explored entities have at least 1 evidence passage within 5 minutes.

4. **Reader Integration:** Highlight in Reader → appears in SiYuan within 30 seconds.

5. **No Pre-Planning:** User never has to define structure upfront. It emerges from exploration.

6. **Journey Persistence:** Any exploration session can be saved and resumed later with full context restored.

7. **Clarification Value:** Pre-exploration dialogue surfaces at least 1 prerequisite concept or clarifying question per session.

8. **Multi-Source Navigation (Future):** Given a question, surface relevant passages from 3+ sources in under 5 seconds.

---

## Files Superseded by This Plan

These documents are now consolidated here:
- `redux/docs/IES_Context_and_Question_Layer.md` (concepts integrated)
- `redux/docs/IES_Integration_Checklist.md` (tasks updated)
- `redux/docs/IES_Flow_Reader_Journey_v2.md` (behavior spec integrated)
- `redux/docs/IES_Knowledge_Pipeline_Design.md` (pipeline integrated)
- `redux/Flow_Graph_Interaction_Spec.md` (UX integrated)
- `redux/IES_Flow_Claude/*` (formal specs integrated)

**This document is the canonical implementation plan.**

---

## Open Questions

1. **SiYuan vs. Neo4j as source of truth?**
   - Proposal: Neo4j is truth, SiYuan is view. Sync on change.

2. **How to handle conflicting facets?**
   - Proposal: Show AI suggestions, let user confirm/reject.

3. **Offline support?**
   - Proposal: Cache aggressively, queue syncs for later.

4. **Cost management for LLM calls?**
   - Proposal: Aggressive caching, batch processing, use cheaper models where quality allows.

5. **Journey storage location?**
   - Proposal: Journey metadata in Neo4j (for graph queries), full document in SiYuan `/Flow_Outputs/Journeys/`.

6. **Source acquisition recommendations?**
   - Proposal: When evidence coverage is thin, query external APIs (OpenLibrary, arXiv) for suggestions. User confirms before adding to Calibre.

---

## Alignment with System Summary

This plan now incorporates all major workflows from `System_Summary_FULL.md`:

| System Summary Section | Plan Coverage |
|------------------------|---------------|
| §2A: Exploring a New Question | Sprint 4 (clarification) + Sprint 1-2 (facets/evidence) |
| §2A.5: Flow Mode | Sprint 1 (facets) + Sprint 2 (evidence) |
| §2A.6: Reader Integration | Sprint 3 (highlight sync) + Sprint 6 (multi-source) |
| §2A.7: Journey Tracking | Sprint 5 (journey persistence) |
| §2B: Reading With Flow Overlay | Existing entity overlay (complete) |
| §2C: Reviewing Past Journeys | Sprint 5 (journey browser/resume) |

**Key additions from System Summary review (Dec 9):**
- Guided clarification dialogue before facet decomposition
- Journey persistence with resumption
- Multi-source Flow Reader mode (future phase)
