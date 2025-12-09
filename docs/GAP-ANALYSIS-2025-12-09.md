# Implementation Gap Analysis — Redux Specs vs Current State

**Created:** 2025-12-09
**Purpose:** Map redux specifications to implemented features, identify gaps, prioritize next work

> **Ground Truth:** For system design and semantics, see `docs/IES-SYSTEM-DESIGN.md`.
> This document focuses on implementation status vs redux specs.

---

## Executive Summary

The `redux/` directory contains detailed specifications for the Context + Question layer. This analysis compares those specs against the actual implementation to identify:

1. **What's done** — Features fully implemented
2. **What's partial** — Features started but incomplete
3. **What's missing** — Features not yet started
4. **Priority recommendations** — What to build next

**Overall Status:** ~45% of redux specifications implemented

---

## 1. Core Types & Schemas

### Specification (IES_Context_and_Question_Layer.md §1-2)

| Type | Required Fields | Status |
|------|-----------------|--------|
| **Context** | id, type, title, parent_context_id, status, key_questions, core_concepts, linked_sources, artifacts | ✅ Implemented |
| **Question** | id, context_id, parent_question_id, question_text, status, prerequisite_questions, related_concepts, linked_sources, answers | ✅ Implemented |
| **AnswerBlock** | id, question_id, content, quality | ✅ Implemented |
| **JourneyEntry** | id, timestamp, context_id, focus_id, classification, entity_links, source_links | 🔄 Partial |
| **ExtractionProfile** | context_id, core_concepts, synonyms, relation_types, domain_filters | ❌ Not implemented |

### Implementation Location

| Schema | File | Notes |
|--------|------|-------|
| Context | `ies/backend/src/ies_backend/schemas/context.py` | ✅ Complete with ContextType, ContextStatus enums |
| Question | `ies/backend/src/ies_backend/schemas/question.py` | ✅ Complete with QuestionStatus, QuestionSource enums |
| AnswerBlock | `ies/backend/src/ies_backend/schemas/question.py` | ✅ Nested in question schema |
| JourneyEntry | `ies/backend/src/ies_backend/schemas/journey.py` | 🔄 Basic, missing classification array |
| ExtractionProfile | — | ❌ Not implemented |

### Gap: ExtractionProfile

**What's missing:**
```python
# Needed in ies/backend/src/ies_backend/schemas/extraction.py
class ExtractionProfile(BaseModel):
    context_id: str
    core_concepts: list[str]
    synonyms: dict[str, list[str]]
    relation_types: list[str]
    domain_filters: list[str]
    question_overrides: dict[str, QuestionExtractionProfile] | None = None
```

**Priority:** Medium — Enables context-aware extraction

---

## 2. Context Note Conventions (SiYuan)

### Specification (IES_Integration_Checklist.md §3)

| Feature | Specified | Status |
|---------|-----------|--------|
| Store context_id in note | frontmatter/YAML or SiYuan attributes | 🔄 Partial |
| Parse `## Key Questions` section | Map bullets to Question nodes | ❌ Not implemented |
| Parse `## Areas of Exploration` section | Map to "area" entities | ❌ Not implemented |
| Parse `## Core Concepts` section | Map to KG Concept IDs | ❌ Not implemented |
| Create Question nodes from bullets | Auto-generate missing IDs | ❌ Not implemented |

### Implementation Location

| Component | File | Status |
|-----------|------|--------|
| Context Note parser | — | ❌ Not implemented |
| Section detection | — | ❌ Not implemented |
| Bullet → Question mapping | — | ❌ Not implemented |

### Gap: Context Note Parser

**What's missing:**
- Backend service to parse SiYuan markdown for Context Note structure
- API endpoint: `POST /context/parse` accepting markdown, returning structured Context
- SiYuan plugin integration to sync parsed content

**Priority:** High — Core to Flow Mode v2 workflow

---

## 3. Flow Mode v2

### Specification (IES_Flow_Reader_Journey_v2.md §1)

| Feature | Specified | Status |
|---------|-----------|--------|
| Detect Context Note is active | Check frontmatter/attributes | 🔄 Partial |
| Parse Key Questions as buttons | Clickable chips | ✅ Implemented (QuestionSelector) |
| Parse Areas of Exploration as buttons | Clickable chips | ❌ Not implemented |
| Core Concepts as shortcuts | Links to KG entities | ✅ Implemented (FlowPanel) |
| Context summary at top | Title, type, status | 🔄 Partial |
| Run Extraction button | Triggers context-aware extraction | ❌ Not implemented |
| Trail navigation | Breadcrumb path | ✅ Implemented |
| Facet decomposition | AI-generated facets | ✅ Implemented |
| "New since last run" highlighting | Mark new content | ❌ Not implemented |

### Implementation Location

| Component | File | Status |
|-----------|------|--------|
| QuestionSelector | `ies/reader/src/components/flow/QuestionSelector.tsx` | ✅ |
| FlowPanel | `ies/reader/src/components/flow/FlowPanel.tsx` | ✅ |
| Trail breadcrumbs | `ies/reader/src/components/flow/JourneyBreadcrumb.tsx` | ✅ |
| FlowMode (SiYuan) | `.worktrees/siyuan/ies/plugin/src/views/FlowMode.svelte` | ✅ |
| Facet API | `ies/backend/src/ies_backend/api/graph.py` | ✅ |

### Gap: Context-Aware Extraction Integration

**What's missing:**
- "Run Extraction" button in Flow UI
- `runExtraction({ context_id, focus_id, profile })` function
- Extraction Engine service
- "New since last run" tracking and highlighting

**Priority:** High — Core value proposition of Flow v2

---

## 4. Extraction Engine

### Specification (IES_Integration_Checklist.md §5)

| Feature | Specified | Status |
|---------|-----------|--------|
| `runExtraction()` function | Full pipeline | ❌ Not implemented |
| Use profile.domain_filters | Filter sources | ❌ Not implemented |
| Use inverted index | Find relevant segments | ❌ Not implemented |
| Use embedding index | Refine candidates | ❌ Not implemented |
| LLM batch extraction | Extract concepts/relations | ❌ Not implemented |
| Write to KG | Concepts, relations, evidence | ✅ Existing (entity extraction) |
| Write to Question Graph | New subquestions | ❌ Not implemented |
| Write JourneyEntry | Log extraction run | 🔄 Partial |

### Implementation Location

| Component | File | Status |
|-----------|------|--------|
| Entity extraction | `library/graph/entities.py` | ✅ Basic |
| Inverted index | — | ❌ Not implemented |
| Embedding index | Qdrant available | 🔄 Infrastructure ready |
| Extraction service | — | ❌ Not implemented |

### Gap: Full Extraction Engine

**What's missing:**
```python
# Needed: ies/backend/src/ies_backend/services/extraction_engine.py
class ExtractionEngine:
    async def run_extraction(
        self,
        context_id: str,
        focus_id: str | None,
        profile: ExtractionProfile
    ) -> ExtractionResult:
        # 1. Filter sources by domain_filters
        # 2. Query inverted index for core_concepts + synonyms
        # 3. (Optional) Refine with embeddings
        # 4. Batch segments → LLM
        # 5. Parse response → concepts, relations, evidence, subquestions
        # 6. Write to KG and Question Graph
        # 7. Log JourneyEntry
        pass
```

**Priority:** High — Central to the system's value

---

## 5. Reader v2 (Question/Journey Mode)

### Specification (IES_Flow_Reader_Journey_v2.md §2)

| Feature | Specified | Status |
|---------|-----------|--------|
| Normal Library Reader | Existing behavior | ✅ Implemented |
| Question/Journey Reader mode | Context-driven | 🔄 Partial |
| Left pane: Context navigation | Title, questions, areas | 🔄 Partial (FlowPanel) |
| Center pane: Source view | Book/article content | ✅ Implemented |
| Right pane: Journey & Notes | Timeline, highlights | ❌ Not implemented |
| Passage ranking for questions | Suggest relevant passages | ❌ Not implemented |
| Auto-tag notes with context_id | On highlight | ❌ Not implemented |
| CFI preservation | Jump-back links | ✅ Implemented |

### Implementation Location

| Component | File | Status |
|-----------|------|--------|
| Reader | `ies/reader/src/components/Reader.tsx` | ✅ |
| FlowPanel | `ies/reader/src/components/flow/FlowPanel.tsx` | ✅ |
| NotesSheet | `ies/reader/src/components/flow/NotesSheet.tsx` | ✅ |
| Journey pane | — | ❌ Not implemented |
| Passage ranking | — | ❌ Not implemented |

### Gap: Journey Pane & Passage Ranking

**What's missing:**
- Right pane showing journey entries for current context
- Service to rank passages by relevance to active question
- Auto-tagging captured notes with context_id/focus_id

**Priority:** Medium — Enhances reading workflow

---

## 6. Journey v2

### Specification (IES_Integration_Checklist.md §7)

| Feature | Specified | Status |
|---------|-----------|--------|
| Log capture events | Quick captures, voice | 🔄 Partial |
| Log dialogue interactions | Chat messages | ✅ Implemented |
| Log Flow button clicks | Extraction runs | ❌ Not implemented |
| Log Reader sessions | Passages, highlights | ❌ Not implemented |
| Log synthesis events | Answer blocks | ❌ Not implemented |
| `getJourneyForContext(context_id)` | Query helper | ❌ Not implemented |
| `getJourneyForFocus(context_id, focus_id)` | Query helper | ❌ Not implemented |
| Timeline view UI | Per-context | ❌ Not implemented |

### Implementation Location

| Component | File | Status |
|-----------|------|--------|
| JourneyService | `ies/backend/src/ies_backend/services/journey_service.py` | ✅ Basic |
| Journey API | `ies/backend/src/ies_backend/api/journey.py` | ✅ Basic |
| Journey store (Reader) | `ies/reader/src/store/flowStore.ts` | ✅ Basic |

### Gap: Comprehensive Journey Logging

**What's missing:**
- Event types for all specified categories
- Query helpers for context/focus filtering
- Timeline view component

**Priority:** Medium — Important for pattern analysis

---

## 7. SiYuan Block Attributes

### Specification (IES_Knowledge_Pipeline_Design.md)

| Attribute | Purpose | Status |
|-----------|---------|--------|
| `custom-type` | Note classification | 🔄 Partial (used in ForgeMode) |
| `custom-id` | Unique identifier | 🔄 Partial |
| `custom-status` | Lifecycle stage | 🔄 Partial |
| `custom-context` | Active Feynman problem | ❌ Not implemented |
| `custom-section` | Section type | ❌ Not implemented |
| `custom-block-type` | highlight/insight/reaction | ❌ Not implemented |
| `custom-source` | Source reference | ❌ Not implemented |
| `custom-source-cfi` | Jump-back location | ❌ Not implemented |
| `custom-entity-refs` | Linked entities | ❌ Not implemented |
| `custom-resonance` | Emotional signal | ❌ Not implemented |
| `custom-energy` | Capture energy level | ❌ Not implemented |
| `custom-processed` | Agent processing status | ❌ Not implemented |

### Gap: Block Attribute System

**What's missing:**
- Consistent attribute schema across all SiYuan notes
- Attribute writer utilities in plugin
- Query utilities to find blocks by attributes

**Priority:** Medium — Enables AI navigation and processing

---

## 8. Agent Pipeline

### Specification (IES_Knowledge_Pipeline_Design.md)

| Agent | Purpose | Status |
|-------|---------|--------|
| Intake Agent | Entity extraction, initial connections | ❌ Not implemented |
| Enrichment Agent | Gap detection, synthesis drafts | ❌ Not implemented |
| Synthesis Agent | Generate narratives, create hard notes | ❌ Not implemented |
| Processing Queue | Job management | ❌ Not implemented |
| Approval Workflow | Auto-approve vs manual | ❌ Not implemented |

### Gap: Full Agent System

**What's missing:**
- Agent orchestration service
- Processing queue with job status
- Approval thresholds and workflow
- Agent implementations

**Priority:** Low — Can work without initially

---

## 9. Reader → SiYuan Sync

### Specification (IES_Knowledge_Pipeline_Design.md)

| Feature | Specified | Status |
|---------|-----------|--------|
| Highlight export API | From Reader | ❌ Not implemented |
| Book Note auto-creation | On first highlight | ❌ Not implemented |
| Highlight → SiYuan block | With attributes | ❌ Not implemented |
| CFI preservation | For jump-back | ✅ In Reader (not synced) |
| Context awareness | Track active problem | ❌ Not implemented |

### Gap: Sync Pipeline

**What's missing:**
- API endpoint for Reader to push highlights
- Service to find/create Book Note in SiYuan
- Transform highlight to SiYuan block with attributes

**Priority:** High — Closes reading → capture loop

---

## 10. Dynamic Source Acquisition

### Specification (IES_Integration_Checklist.md §9)

| Feature | Specified | Status |
|---------|-----------|--------|
| `searchSources(query, typeFilters)` | Search external sources | ❌ Not implemented |
| `downloadSource(handle)` | Fetch book/paper | ❌ Not implemented |
| `ingestSource(file_or_url)` | Add to library | ✅ Partial (Calibre manual) |
| Context gap detection | Propose source acquisition | ❌ Not implemented |

### Gap: Source Acquisition Pipeline

**Priority:** Low — Nice to have, not core

---

## Priority Matrix

> **Updated:** 2025-12-09 (commit 3fd956b)

### P0 — Critical Path (Do First)

| Gap | Reason | Effort | Status |
|-----|--------|--------|--------|
| **Context Note Parser** | Required for Flow v2 context awareness | Medium | ✅ **DONE** (ContextService.parse_context_note) |
| **Reader → SiYuan Sync** | Closes capture loop | Medium | ✅ **DONE** (Highlights API + SiYuan sync) |
| **Extraction Engine** | Core value of context-aware exploration | High | ❌ Not started |

### P1 — High Value (Do Next)

| Gap | Reason | Effort | Status |
|-----|--------|--------|--------|
| ExtractionProfile schema | Enables targeted extraction | Low | ✅ **DONE** (schemas/extraction.py) |
| Journey query helpers | Enables pattern analysis | Low | ❌ Not started |
| "New since last run" tracking | UX improvement | Medium | ❌ Not started |
| Passage ranking for questions | Reading guidance | High | ❌ Not started |

### P2 — Important (Do Later)

| Gap | Reason | Effort |
|-----|--------|--------|
| Block attribute system | AI navigation | Medium |
| Journey timeline UI | Visualization | Medium |
| Areas of Exploration buttons | Additional navigation | Low |

### P3 — Nice to Have

| Gap | Reason | Effort |
|-----|--------|--------|
| Agent pipeline | Automation | High |
| Dynamic source acquisition | Library expansion | High |
| Approval workflow | Human-in-loop | Medium |

---

## Recommended Next Sprint

### ~~Sprint Focus: Close the Capture Loop~~ ✅ COMPLETE

> **Completed:** 2025-12-09 (commit 3fd956b)

The capture loop is now closed:
- Highlights API: Full CRUD + batch sync
- SiYuan sync: Book Notes with highlights
- Reader integration: highlightApi.ts client

### Sprint Focus: Extraction Engine (NEW)

**Goal:** Context-aware extraction that uses ExtractionProfile to find relevant content.

**Tasks:**

1. **Extraction Engine Service** (Backend)
   - `POST /extraction/run` — Accept context_id, focus_id, profile
   - Use profile.domain_filters to select sources
   - Use profile.core_concepts + synonyms for keyword matching
   - LLM batch extraction for concepts/relations

2. **Journey Query Helpers** (Backend)
   - `GET /journey?context_id=X` — Filter by context
   - `GET /journey?focus_id=X` — Filter by question/area

3. **"Run Extraction" Button** (UI)
   - Add to FlowPanel in IES Reader
   - Add to FlowMode in SiYuan plugin

---

## Previous Sprint (Completed)

### Sprint Focus: Close the Capture Loop ✅

**Goal:** Highlights captured in Reader appear in SiYuan Book Notes and can be queried.

**Tasks:**

1. **Highlight Sync API** (Backend) ✅
   - `POST /highlights` — Full CRUD with CFI tracking
   - Service creates Book Note in SiYuan
   - Transform to SiYuan block with attributes

2. **Reader Highlight Export** (IES Reader) ✅
   - highlightApi.ts client
   - Include CFI, current entity context, book calibre_id

3. **Book Note Template** (SiYuan)
   - Create standard template with sections
   - Auto-create from Calibre metadata

4. **Basic Query Helpers** (Backend)
   - `GET /journey?context_id=X` — Filter by context
   - `GET /highlights?book_id=X` — Get highlights for book

**Success Criteria:**
- Highlight in Reader → SiYuan Book Note in <30 seconds
- Can query all highlights for a context
- CFI preserved for jump-back

---

## Files to Create

Based on this analysis, these new files are needed:

```
ies/backend/src/ies_backend/
├── schemas/
│   └── extraction.py          # ExtractionProfile, ExtractionResult
├── services/
│   ├── extraction_engine.py   # Context-aware extraction
│   ├── highlight_sync.py      # Reader → SiYuan sync
│   └── context_note_parser.py # Parse SiYuan Context Notes
└── api/
    └── sync.py                # Sync endpoints (enhance existing)

.worktrees/siyuan/ies/plugin/src/
├── services/
│   └── highlight-receiver.ts  # Receive and store highlights
└── utils/
    └── book-note.ts           # Book Note creation/update
```

---

*This analysis maps the redux specifications to implementation reality. Use it to prioritize development work.*
