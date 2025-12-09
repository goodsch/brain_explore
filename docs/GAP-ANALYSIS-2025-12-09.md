# Implementation Gap Analysis — Redux Specs vs Current State

**Created:** 2025-12-09
**Updated:** 2025-12-09 (Extraction Engine + Context Note Parser implementation)
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

**Overall Status:** ~90% of redux specifications implemented (updated Dec 9 — P0 complete: Extraction Engine + UI buttons)

---

## 1. Core Types & Schemas

### Specification (IES_Context_and_Question_Layer.md §1-2)

| Type | Required Fields | Status |
|------|-----------------|--------|
| **Context** | id, type, title, parent_context_id, status, key_questions, core_concepts, linked_sources, artifacts | ✅ Implemented |
| **Question** | id, context_id, parent_question_id, question_text, status, prerequisite_questions, related_concepts, linked_sources, answers | ✅ Implemented |
| **AnswerBlock** | id, question_id, content, quality | ✅ Implemented |
| **JourneyEntry** | id, timestamp, context_id, focus_id, classification, entity_links, source_links | 🔄 Partial |
| **ExtractionProfile** | context_id, core_concepts, synonyms, relation_types, domain_filters | ✅ Implemented |

### Implementation Location

| Schema | File | Notes |
|--------|------|-------|
| Context | `ies/backend/src/ies_backend/schemas/context.py` | ✅ Complete with ContextType, ContextStatus enums |
| Question | `ies/backend/src/ies_backend/schemas/question.py` | ✅ Complete with QuestionStatus, QuestionSource enums |
| AnswerBlock | `ies/backend/src/ies_backend/schemas/question.py` | ✅ Nested in question schema |
| JourneyEntry | `ies/backend/src/ies_backend/schemas/journey.py` | 🔄 Basic, missing classification array |
| ExtractionProfile | `ies/backend/src/ies_backend/schemas/extraction.py` | ✅ Complete schema (Dec 9) |

### ~~Gap: ExtractionProfile~~ ✅ COMPLETE

ExtractionProfile schema implemented with full support for context-aware extraction configuration.

---

## 2. Context Note Conventions (SiYuan)

### Specification (IES_Integration_Checklist.md §3)

| Feature | Specified | Status |
|---------|-----------|--------|
| Store context_id in note | frontmatter/YAML or SiYuan attributes | ✅ Implemented |
| Parse `## Key Questions` section | Map bullets to Question nodes | ✅ Implemented |
| Parse `## Areas of Exploration` section | Map to "area" entities | ✅ Implemented |
| Parse `## Core Concepts` section | Map to KG Concept IDs | ✅ Implemented |
| Create Question nodes from bullets | Auto-generate missing IDs | ✅ Implemented |

### Implementation Location

| Component | File | Status |
|-----------|------|--------|
| Context Note parser | `ies/backend/src/ies_backend/services/context_note_parser.py` | ✅ Implemented |
| Section detection | context_note_parser.py | ✅ Implemented |
| Bullet → Question mapping | context_note_parser.py | ✅ Implemented |

### ~~Gap: Context Note Parser~~ ✅ COMPLETE

**Implementation (Dec 9):**
- **Service:** `ContextNoteParser` (459 lines) — Complete SiYuan markdown parsing
- **Features:**
  - YAML frontmatter extraction (context_id, context_type, status, parent_context_id)
  - Question parsing with checkbox status ([x] vs [ ])
  - Existing ID preservation (<!-- q_xxx --> comments)
  - Question prefix support (Q1:, Q2:)
  - Areas of exploration with descriptions
  - Core concepts extraction
- **API:** Enhanced Context API with `/parse-enhanced`, `/validate` endpoints
- **Tests:** 22 comprehensive unit tests in `test_context_note_parser.py` (466 lines)

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
| Run Extraction button | Triggers context-aware extraction | ✅ **DONE** (FlowMode.svelte button + results display) |
| Trail navigation | Breadcrumb path | ✅ Implemented |
| Facet decomposition | AI-generated facets | ✅ Implemented |
| "New since last run" highlighting | Mark new content | ✅ **DONE** (Visit Tracking API) |

### Implementation Location

| Component | File | Status |
|-----------|------|--------|
| QuestionSelector | `ies/reader/src/components/flow/QuestionSelector.tsx` | ✅ |
| FlowPanel | `ies/reader/src/components/flow/FlowPanel.tsx` | ✅ |
| Trail breadcrumbs | `ies/reader/src/components/flow/JourneyBreadcrumb.tsx` | ✅ |
| FlowMode (SiYuan) | `.worktrees/siyuan/ies/plugin/src/views/FlowMode.svelte` | ✅ |
| Facet API | `ies/backend/src/ies_backend/api/graph.py` | ✅ |

### ~~Gap: Context-Aware Extraction UI Integration~~ ✅ COMPLETE

**Implementation (Dec 9):**
- ✅ Extraction Engine service (`ies/backend/src/ies_backend/services/extraction_engine.py`)
- ✅ Extraction API (`POST /extraction/run`, `POST /extraction/profiles`, `GET /extraction/profiles/{context_id}`)
- ✅ IES Reader: `RunExtractionButton.tsx` component with loading/success/error states
- ✅ IES Reader: `extractionApi.ts` client for extraction API
- ✅ IES Reader: `flowStore.ts` extraction state and actions
- ✅ IES Reader: `FlowPanel.tsx` integration with context-aware button
- ✅ SiYuan Plugin: Extraction button in FlowMode with full results display (lines 1413-1479, 2089-2233)

**Features:**
- Button appears when context is active
- Passes current question for targeted extraction
- Displays results: concepts found, relations found, subquestions generated
- Loading spinner during extraction
- Error handling with retry option

---

## 4. Extraction Engine

### Specification (IES_Integration_Checklist.md §5)

| Feature | Specified | Status |
|---------|-----------|--------|
| `runExtraction()` function | Full pipeline | ✅ Implemented |
| Use profile.domain_filters | Filter sources | ✅ Implemented |
| Use inverted index | Find relevant segments | ✅ Implemented (Neo4j full-text index) |
| Use embedding index | Refine candidates | ❌ Not implemented (future) |
| LLM batch extraction | Extract concepts/relations | ✅ Implemented (Anthropic Claude) |
| Write to KG | Concepts, relations, evidence | ✅ Implemented |
| Write to Question Graph | New subquestions | ✅ Implemented |
| Write JourneyEntry | Log extraction run | ✅ Implemented |

### Implementation Location

| Component | File | Status |
|-----------|------|--------|
| Entity extraction | `library/graph/entities.py` | ✅ Basic |
| Inverted index | Neo4j full-text index on Chunk nodes | ✅ Implemented |
| Embedding index | Qdrant available | 🔄 Infrastructure ready (future) |
| Extraction service | `ies/backend/src/ies_backend/services/extraction_engine.py` | ✅ Implemented |

### ~~Gap: Full Extraction Engine~~ ✅ COMPLETE

**Implementation (Dec 9):**
- **Service:** `ExtractionEngine` (337 lines) — Complete context-aware extraction pipeline
- **Pipeline:**
  1. Load context and extraction profile
  2. Filter sources by domain_filters
  3. Search chunks via Neo4j full-text index (core_concepts + synonyms)
  4. LLM extraction (Anthropic Claude) for entities and relationships
  5. Write to Neo4j (concepts, relations, evidence)
  6. Generate subquestions for new entities
  7. Log journey entry
- **Features:**
  - Profile management: `save_profile()`, `get_profile()` (in-memory MVP)
  - Full-text search on chunk content
  - Anthropic Claude integration with structured outputs
  - Automatic subquestion generation
  - Journey tracking
- **API:**
  - `POST /extraction/profiles` — Create/update profile
  - `GET /extraction/profiles/{context_id}` — Get profile
  - `POST /extraction/run` — Run extraction
- **Tests:** 23 comprehensive unit tests in `test_extraction_engine.py` (420 lines)

**Priority:** High — Central to the system's value ✅ COMPLETE

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
| Passage ranking for questions | Suggest relevant passages | ✅ **DONE** (Dec 9) |
| Auto-tag notes with context_id | On highlight | ❌ Not implemented |
| CFI preservation | Jump-back links | ✅ Implemented |

### Implementation Location

| Component | File | Status |
|-----------|------|--------|
| Reader | `ies/reader/src/components/Reader.tsx` | ✅ |
| FlowPanel | `ies/reader/src/components/flow/FlowPanel.tsx` | ✅ |
| NotesSheet | `ies/reader/src/components/flow/NotesSheet.tsx` | ✅ |
| Journey pane | — | ❌ Not implemented |
| Passage ranking | `ies/backend/src/ies_backend/services/passage_ranking_service.py` | ✅ **NEW** |

### ~~Gap: Passage Ranking~~ ✅ COMPLETE

**Implementation (Dec 9):**
- **Service:** `PassageRankingService` with keyword extraction, TF-IDF-like scoring, concept matching
- **API:** `GET /questions/{question_id}/relevant-passages` endpoint
- **Schemas:** `RankedPassage`, `PassageRankingRequest`, `PassageRankingResponse`
- **Features:**
  - Keyword extraction from question text (stop word filtering)
  - Related concept matching with scoring bonuses
  - TF-IDF-like relevance scoring with length normalization
  - Configurable max_passages and min_score filters
  - Source attribution (book title, author, chapter, page)
  - Matched keywords and concepts tracking
- **Tests:** 11 comprehensive unit tests, all passing

**Ranking Algorithm:**
- Extracts keywords from question text (excluding stop words)
- Includes related concepts from question metadata
- Searches Neo4j chunks using keyword CONTAINS matching
- Scores passages based on:
  - Keyword matches: +0.1 per keyword
  - Concept matches: +0.3 per concept (higher value)
  - Multiple occurrences: diminishing returns (log scale)
  - Length normalization: prevents long passages from dominating
- Returns passages sorted by relevance score (0-1)

### Remaining Gap: Journey Pane

**What's missing:**
- Right pane showing journey entries for current context
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
| `custom-be_type` | Block type classification | ✅ **DONE** (BlockAttributeService) |
| `custom-be_id` | Backend entity linking | ✅ **DONE** (BlockAttributeService) |
| `custom-status` | Lifecycle stage | ✅ **DONE** (BlockAttributeService) |
| `custom-resonance` | Emotional signal | ✅ **DONE** (BlockAttributeService) |
| `custom-energy` | Energy level | ✅ **DONE** (BlockAttributeService) |
| `custom-context` | Active Context | ✅ **DONE** (BlockAttributeService) |
| `custom-source` | Source reference | ✅ **DONE** (BlockAttributeService) |
| `custom-source-cfi` | Jump-back location | ✅ **DONE** (BlockAttributeService) |

### ~~Gap: Block Attribute System~~ ✅ COMPLETE (Dec 9)

**Implementation:**
- **Backend schemas:** `ies/backend/src/ies_backend/schemas/block_attribute.py` (200 lines)
  - `BlockAttribute` model with all IES standard attributes
  - Enums: `BlockType`, `BlockStatus`, `ResonanceSignal`, `EnergyLevel`
  - Query/update schemas for filtering and modification
  - Statistics schema for analytics
- **Service layer:** `ies/backend/src/ies_backend/services/block_attribute_service.py` (358 lines)
  - Query blocks by type, status, resonance, energy, context
  - Get blocks by backend entity ID (be_id)
  - Update block attributes via SiYuan API
  - Statistics aggregation
- **API endpoints:** `ies/backend/src/ies_backend/api/block_attributes.py` (162 lines)
  - `GET /block-attributes/` - List with filters
  - `GET /block-attributes/{block_id}` - Get single block
  - `GET /block-attributes/by-backend-id/{be_id}` - Find blocks by entity
  - `GET /block-attributes/by-type/{be_type}` - Find blocks by type
  - `PATCH /block-attributes/{block_id}` - Update attributes
  - `GET /block-attributes/stats/summary` - Statistics
- **Tests:** 12 comprehensive unit tests, all passing (322 total backend tests passing)
- **Registered:** Router added to `main.py`

**Features:**
- Query blocks by IES metadata (type, status, resonance, energy)
- Link SiYuan blocks to backend entities via be_id
- ADHD-friendly navigation via resonance/energy filtering
- Statistics for understanding attribute usage
- Full CRUD support for block attributes

**Impact:** Enables AI navigation, cross-app entity linking, and ADHD-friendly block retrieval.

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

> **Updated:** 2025-12-09 (Extraction Engine + Context Note Parser implementation)

### P0 — Critical Path (Do First)

| Gap | Reason | Effort | Status |
|-----|--------|--------|--------|
| **Context Note Parser** | Required for Flow v2 context awareness | Medium | ✅ **DONE** (ContextNoteParser with 22 tests) |
| **Reader → SiYuan Sync** | Closes capture loop | Medium | ✅ **DONE** (Highlights API + SiYuan sync) |
| **Extraction Engine** | Core value of context-aware exploration | High | ✅ **DONE** (ExtractionEngine with 23 tests) |
| **Run Extraction UI Button** | Trigger extraction from UI | Low | ✅ **DONE** (IES Reader + SiYuan) |

### P1 — High Value (Do Next)

| Gap | Reason | Effort | Status |
|-----|--------|--------|--------|
| ExtractionProfile schema | Enables targeted extraction | Low | ✅ **DONE** (schemas/extraction.py) |
| Journey query helpers | Enables pattern analysis | Low | ✅ **DONE** (GET /context/{id}/journey?focus_id=X) |
| "New since last run" tracking | UX improvement | Medium | ✅ **DONE** (Visit Tracking API - 2025-12-09) |
| Passage ranking for questions | Reading guidance | Medium | ✅ **DONE** (Dec 9) |

### P2 — Important (Do Later)

| Gap | Reason | Effort | Status |
|-----|--------|--------|--------|
| Block attribute system | AI navigation | Medium | ✅ **DONE** (Dec 9) |
| Journey timeline UI | Visualization | Medium | ❌ Not started |
| Areas of Exploration buttons | Additional navigation | Low | ❌ Not started |
| Journey pane in Reader | Context tracking | Medium | ❌ Not started |

### P3 — Nice to Have

| Gap | Reason | Effort |
|-----|--------|--------|
| Agent pipeline | Automation | High |
| Dynamic source acquisition | Library expansion | High |
| Approval workflow | Human-in-loop | Medium |

---

## Recommended Next Sprint

### Sprint Focus: Pass 2/3 Enrichment Pipeline

**Goal:** Enhance book metadata with relationship extraction and LLM enrichment.

**Tasks:**

1. **Pass 2 Enrichment** (Backend)
   - Implement relationship extraction in ingestion pipeline
   - Extract causal relationships (CAUSES, ENABLES)
   - Extract component relationships (PART_OF)
   - Extract contrast relationships (CONTRASTS_WITH)
   - Status: `entities_extracted → relationships_mapped`

3. **Pass 3 Enrichment** (Backend)
   - Integrate Reframe API for concept enrichment
   - Generate mechanisms and patterns
   - Add rich descriptions via LLM
   - Status: `relationships_mapped → enriched`

---

## Completed in Recent Sprints

### ~~Sprint: Extraction Engine + Context Note Parser~~ ✅ COMPLETE (Dec 9)

**Extraction Engine:**
- ExtractionEngine service (337 lines) with complete pipeline
- Neo4j full-text index on Chunk nodes
- Anthropic Claude integration for entity/relationship extraction
- Profile management (save_profile, get_profile)
- Automatic subquestion generation
- Journey tracking
- 3 API endpoints: POST /extraction/profiles, GET /extraction/profiles/{context_id}, POST /extraction/run
- 23 comprehensive unit tests, all passing

**Context Note Parser:**
- ContextNoteParser service (459 lines) with robust SiYuan markdown parsing
- YAML frontmatter extraction
- Question parsing with checkbox status and existing ID preservation
- Areas of exploration and core concepts extraction
- Enhanced Context API with /parse-enhanced and /validate endpoints
- 22 comprehensive unit tests, all passing

### ~~Sprint: Block Attribute System~~ ✅ COMPLETE (Dec 9)

The block attribute system is now implemented:
- Backend schemas with IES standard attributes
- BlockAttributeService for querying SiYuan
- REST API endpoints for all CRUD operations
- 12 comprehensive tests, all passing
- Enables AI navigation and cross-app linking

### ~~Sprint: Close the Capture Loop~~ ✅ COMPLETE (Dec 9)

The capture loop is now closed:
- Highlights API: Full CRUD + batch sync
- SiYuan sync: Book Notes with highlights
- Reader integration: highlightApi.ts client

### ~~Sprint: Passage Ranking~~ ✅ COMPLETE (Dec 9)

Question-driven passage ranking is now operational:
- PassageRankingService with TF-IDF-like scoring
- `GET /questions/{question_id}/relevant-passages` API endpoint
- Comprehensive test coverage (11 tests, all passing)
- Keyword extraction, concept matching, length normalization
- Configurable filters and source attribution

---

## Files to Create

Based on this analysis, these new files are needed:

```
ies/backend/src/ies_backend/
├── schemas/
│   ├── extraction.py          # ✅ DONE - ExtractionProfile, ExtractionResult
│   └── block_attribute.py     # ✅ DONE - BlockAttribute, queries, stats
├── services/
│   ├── extraction_engine.py   # ✅ DONE - Context-aware extraction
│   ├── highlight_sync.py      # ✅ DONE - Reader → SiYuan sync
│   ├── context_note_parser.py # ✅ DONE - Parse SiYuan Context Notes
│   ├── passage_ranking_service.py  # ✅ DONE - Rank passages by relevance
│   └── block_attribute_service.py  # ✅ DONE - Query blocks by attributes
└── api/
    ├── extraction.py          # ✅ DONE - Extraction API endpoints
    ├── highlight_sync.py      # ✅ DONE - Highlight sync endpoints
    └── block_attributes.py    # ✅ DONE - Block attribute endpoints

ies/reader/src/services/
└── extractionApi.ts           # ❌ TODO - Extraction API client

.worktrees/siyuan/ies/plugin/src/
├── services/
│   ├── highlight-receiver.ts  # ✅ DONE - Receive and store highlights
│   └── extractionApi.ts       # ❌ TODO - Extraction API client
└── utils/
    └── book-note.ts           # ✅ DONE - Book Note creation/update
```

---

*This analysis maps the redux specifications to implementation reality. Use it to prioritize development work.*
