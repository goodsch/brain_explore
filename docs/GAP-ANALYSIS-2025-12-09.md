# Implementation Gap Analysis — Redux Specs vs Current State

**Created:** 2025-12-09
**Updated:** 2025-12-09 (Phase 2c 100% — Journey Pattern Analysis complete)
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

**Overall Status:** 100% of redux specifications implemented (Phase 2c complete Dec 9)

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
- ✅ SiYuan Plugin: `extractionApi.ts` client for extraction API (Dec 9 — forwardProxy pattern)

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
| Log capture events | Quick captures, voice | ✅ **DONE** (JourneyLogger.log_highlight_created) |
| Log dialogue interactions | Chat messages | ✅ Implemented |
| Log Flow button clicks | Extraction runs | ✅ **DONE** (ExtractionEngine._log_extraction_journey) |
| Log Reader sessions | Passages, highlights | ✅ **DONE** (highlight_sync_service integration) |
| Log synthesis events | Answer blocks | 🔄 Partial |
| `getJourneyForContext(context_id)` | Query helper | ✅ **DONE** (GET /journey-timeline/context/{context_id}) |
| `getJourneyForFocus(context_id, focus_id)` | Query helper | ✅ **DONE** (via request.focus_id filter) |
| Timeline view UI | Per-context | ✅ **DONE** (JourneyTimeline component) |

### Implementation Location

| Component | File | Status |
|-----------|------|--------|
| JourneyService | `ies/backend/src/ies_backend/services/journey_service.py` | ✅ Complete |
| JourneyLogger | `ies/backend/src/ies_backend/services/journey_logger.py` | ✅ **NEW** (Dec 9) |
| Journey API | `ies/backend/src/ies_backend/api/journey.py` | ✅ Complete |
| Journey Timeline API | `ies/backend/src/ies_backend/api/journey_timeline.py` | ✅ Complete |
| Journey store (Reader) | `ies/reader/src/store/flowStore.ts` | ✅ Complete |

### ~~Gap: Comprehensive Journey Logging~~ ✅ **MOSTLY COMPLETE** (Dec 9)

**Implemented:**
- JourneyLogger utility class with methods for all event types
- ENTITY_VISIT and TEMPLATE_SESSION classifications added
- Highlight sync automatically logs to journey
- Extraction runs log to journey
- Timeline API with context/focus filtering
- Timeline view component in SiYuan plugin

**Remaining:**
- Log synthesis events (answer blocks) — partial

**Priority:** Low — Core logging complete

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
| Journey timeline UI | Visualization | Medium | ✅ **DONE** (JourneyTimeline component) |
| Areas of Exploration buttons | Additional navigation | Low | ✅ **DONE** (AreasChips component) |
| Journey pane in Reader | Context tracking | Medium | ❌ Not started |

### P3 — Nice to Have

| Gap | Reason | Effort |
|-----|--------|--------|
| Agent pipeline | Automation | High |
| Dynamic source acquisition | Library expansion | High |
| Approval workflow | Human-in-loop | Medium |

---

## Recommended Next Sprint

### ~~Sprint Focus: Cross-App Continuity (IES Reader ↔ SiYuan Sync)~~ ✅ COMPLETE (Dec 9)

**Goal:** Enable seamless state sharing and session continuity between IES Reader and SiYuan plugin.

**Completed Tasks:**

1. **State Management API** (Backend) ✅ COMPLETE
   - Session state API for active context/book/question
   - Schemas: `SessionState`, `ReadingPosition`, `SessionStateUpdate`, `SessionStateHistory`
   - Service: `SessionStateService` with in-memory MVP (Redis migration path ready)
   - Endpoints: GET/PATCH /session-state/{user_id}, POST heartbeat, GET history
   - 411 backend tests passing

2. **Context Sync** (IES Reader + SiYuan) ✅ COMPLETE
   - `ContextSyncService.ts` (SiYuan) — Bidirectional sync with polling
   - `useSessionSync.ts` (Reader) — Syncs context/question from flowStore
   - Polling strategy: 5s active, 30s background
   - Last-write-wins conflict resolution
   - Write debouncing: 3s to avoid API spam

3. **Reading Position Sync** (IES Reader + SiYuan) ✅ COMPLETE
   - `useReadingPosition.ts` (Reader) — Tracks CFI via epub.js 'relocated' event
   - Write debouncing: 2s (immediate on window blur)
   - `ResumeReadingWidget.svelte` (SiYuan) — Dashboard widget with deep linking
   - Deep link format: `/reader?calibreId={id}&cfi={encoded_cfi}`
   - Integrates with Dashboard.svelte for "Currently Reading" display

4. **Journey Continuity** ✅ COMPLETE (Dec 9)
   - Share journey entries across both apps via backend
   - Enable "Continue Exploration" from either app
   - Unified breadcrumb trail spanning Reader and SiYuan sessions
   - Journey trail sync from backend to both frontends
   - Entity visit logging from Reader and SiYuan

### ~~Next Sprint: Journey Continuity + Polish~~ ✅ COMPLETE (Dec 9)

**Goal:** Complete the remaining P2 items and polish cross-app experience.

**Completed Tasks:**

1. **Journey Continuity API** ✅ COMPLETE
   - Extended `SessionState` schema with `journey_trail`, `current_entity_id`, `current_entity_name`, `last_app_source`
   - Added `JourneyTrailItem` schema with entity_id, entity_name, entity_type, source_app, timestamp, dwell_seconds, source_context
   - Added `ContinueExplorationResponse` schema with deep links and resume hints
   - Updated `SessionStateService` to handle trail item addition with max item limits (50)
   - Added `GET /session-state/{user_id}/continue` endpoint for "Continue Exploration" feature
   - 32 session state tests passing (including 9 new journey trail tests)
   - SiYuan `ContextSyncService` syncs journey trail from backend, adds entity visits
   - IES Reader `useSessionSync` hook syncs journey trail from backend, adds entity visits
   - IES Reader `flowStore` extended with journeyTrail and lastAppSource state

2. **Areas of Exploration Chips** ✅ COMPLETE (Flow v2 gap)
   - Parse Areas section and render as clickable chips
   - Link to entity search for area keywords

3. **Production Hardening** ✅ COMPLETE
   - SessionStateService migrated to Redis for persistence (24h TTL, 30min session timeout)
   - Centralized journey event logging via JourneyLogger
   - Error handling in sync hooks and services

### Next Sprint: Journey Pattern Analysis

**Goal:** Analyze journey patterns for personalization and insights.

**Recommended Tasks:**

1. **Journey Pattern Analysis**
   - Analyze journey trail for exploration patterns
   - Identify frequently visited entities and clusters
   - Surface recommendations based on journey history

2. **End-to-End Testing**
   - Verify full sync flow: Reader → Backend → SiYuan
   - Test offline behavior and reconnection
   - Stress test with rapid context/position changes

---

## Completed in Recent Sprints

### ~~Sprint: Pass 2/3 Enrichment Pipeline~~ ✅ COMPLETE (Dec 9)

**Pass 2 - Relationship Extraction:**
- RelationshipExtractor service (385 lines) with LLM-based extraction via OpenAI GPT-4o-mini
- Three core relationship types: CAUSES (causal/enabling), PART_OF (hierarchical/component), CONTRASTS_WITH (distinctions/comparisons)
- Confidence scoring, evidence quotes, chunk attribution for all relationships
- Deduplication logic merges identical relationships, keeping highest confidence
- Validation against known entities prevents hallucinated relationships
- pass2_relationships.py CLI script (427 lines) for batch processing books with `status='entities_extracted'`
- Query entity-rich chunks (2+ entities), extract relationships, deduplicate, store to Neo4j
- UnifiedGraphClient `add_typed_relationship()` method (lines 424-495) with type validation and metadata
- Rich console UI with progress bars, status tables, relationship statistics
- Test coverage: `test_relationship_extractor.py` (535 lines, comprehensive extraction and validation tests)

**Pass 3 - LLM Enrichment:**
- EnrichmentService (843 lines) orchestrates four enrichment types: Reframes, Mechanisms, Patterns, Rich Descriptions
- Anthropic Claude Sonnet 4 integration for mechanism/pattern/description extraction
- Priority-based enrichment: high mention count + central types + missing data = higher priority
- Rate limiting: 60 calls/minute with automatic backoff
- Mechanism extraction: Step-by-step process explanations with triggers, outcomes, confidence (ADHD-friendly: short concrete steps)
- Pattern detection: Cross-domain structural templates (Feedback Loop, Tipping Point, Emergence, Oscillation)
- Description enhancement: Expands entity descriptions to 2-3 sentences (100-150 words) for non-expert accessibility
- Stores mechanisms via HAS_MECHANISM relationships, patterns via IS_PATTERN relationships
- Test coverage: `test_enrichment_service.py` (289 lines, mocked Anthropic API)

**Documentation:**
- `docs/plans/2025-12-09-pass-2-relationship-extraction.md` (858 lines) — Pass 2 architecture and LLM prompt strategy
- `docs/plans/2025-12-09-pass-3-llm-enrichment.md` (1,372 lines) — Pass 3 design with prioritization and batch processing
- `docs/implementation/PASS2_IMPLEMENTATION_SUMMARY.md` (235 lines) — CLI usage and processing pipeline
- `docs/implementation/pass-3-enrichment-service.md` (598 lines) — EnrichmentService architecture and LLM prompts

**Impact:** Completes multi-pass ingestion pipeline — Pass 1 (entities) → Pass 2 (relationships) → Pass 3 (enrichment) enables deep exploration with high-quality knowledge graph.

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

---

## UX/Frontend Gaps (Dec 9 Journey Analysis)

> **Source:** `USER-JOURNEY-ANALYSIS-2025-12-09.md` + `CROSS-APP-JOURNEY-ANALYSIS-2025-12-09.md`
> **Verdict:** "Feature-complete backend, experience-poor frontend"

### Statistics

| Metric | Count |
|--------|-------|
| Total Issues | 67 |
| CRITICAL | 18 |
| HIGH | 24 |
| Backend features with zero UI | 12 |
| Stub hooks | 4 |

### P0 — Critical (Blocks Real-World Use)

| # | Issue | Location | Impact | Effort |
|---|-------|----------|--------|--------|
| 1 | **Entity overlay is 1-line stub** | `useEntityHighlighter.ts`, `useEntityOverlay.ts`, `useEntityLookup.ts` | Flagship feature broken — entity buttons do nothing | 20h |
| 2 | **No session resume dialog** | `App.tsx:42` — TODO comment | Users lose position on restart despite backend saving it | 4h |
| 3 | **Library browser is stub** | `LibraryBrowser.tsx` (20 lines) | Cannot browse Calibre library | 16h |
| 4 | **Notes are write-only** | `NotesSheet.tsx` — no browse UI | Users capture notes but can never retrieve them | 12h |
| 5 | **No question delete/edit** | `QuestionSelector.tsx` — missing handlers | Typos permanent, creates ADHD shame | 5h |
| 6 | **Selection bar off-screen** | `Reader.tsx:195-208` | Core interaction broken on mobile/top selections | 2h |
| 7 | **No sync status indicator** | `flowStore.ts` has state, no UI | Users can't tell if changes saved, silent failures | 3h |
| 8 | **Journey trail not displayed** | Backend tracks, no visualization | Cross-app exploration path invisible | 6h |
| 9 | **No deep linking UI** | Backend `/continue` endpoint ready | Can't navigate between apps despite backend support | 4h |
| 10 | **Entity visits not auto-tracked** | `addEntityVisit()` never called | Journey trail incomplete for Reader | 4h |

### P1 — High (Degrades Experience)

| # | Issue | Location | Impact | Effort |
|---|-------|----------|--------|--------|
| 11 | **No first-run tutorial** | `App.tsx`, `Dashboard.svelte` | Users see complex UI with no explanation | 6h |
| 12 | **Flow Panel hidden by default** | `Reader.tsx` panel state | Users never discover core feature | 2h |
| 13 | **Journey trail asymmetry** | Reader read-only, SiYuan writes | Reader entity visits invisible to SiYuan | 4h |
| 14 | **No error recovery UI** | Both apps log to console only | Network failures = silent data loss | 8h |
| 15 | **No conflict resolution** | Last-write-wins, no UI | Simultaneous edits silently overwrite | 12h |
| 16 | **No session timeout warning** | 30min timeout, no notice | Sessions expire without warning | 3h |
| 17 | **TOC navigation missing** | epub.js provides data, no UI | Cannot navigate long books | 8h |
| 18 | **Progress indicator missing** | Data extracted, never displayed | Users disoriented in long books | 6h |
| 19 | **Energy filtering no UI** | `/personal/sparks/by-energy` ready | ADHD energy navigation unavailable | 4h |
| 20 | **Resonance signals no capture UI** | 8 signals in backend | Emotional retrieval cues lost | 6h |

### P2 — Medium (Usability Friction)

| # | Issue | Location | Impact | Effort |
|---|-------|----------|--------|--------|
| 21 | **No activity timeline UI** | `GET /session-state/{user_id}/history` unused | Can't review exploration history | 8h |
| 22 | **No dwell time tracking** | Backend supports `dwell_seconds` | Can't analyze time spent on entities | 4h |
| 23 | **No last-app-source indicator** | Backend tracks, UI doesn't show | Users can't see which app was last active | 2h |
| 24 | **Keyboard navigation missing** | FlowMode.svelte — zero handlers | Power users and accessibility blocked | 12h |
| 25 | **Mobile bottom sheet not draggable** | FlowPanel fixed at 60vh | Blocks 60% of screen permanently | 8h |

### State Transfer Matrix (Cross-App)

| State Field | Reader → SiYuan | SiYuan → Reader | UI Status |
|-------------|-----------------|-----------------|-----------|
| `active_context_id` | ✅ Writes | ✅ Reads | No indicator |
| `active_question_id` | ✅ Writes | ✅ Reads | No indicator |
| `current_book` (CFI) | ✅ Writes | 🟡 Read-only | No indicator |
| `journey_trail` | 🔴 Read-only | ✅ Writes | **No UI** |
| `current_entity_id` | 🟡 Manual only | ✅ Writes | **No UI** |
| Deep links | Backend ready | Backend ready | **No buttons** |
| Sync status | State exists | State exists | **No UI** |

### Recommended Sprint: UX Foundation (Week 1, ~40h)

| Task | Effort | Impact |
|------|--------|--------|
| Fix selection bar positioning | 2h | Core interaction |
| Add question delete/edit buttons | 5h | ADHD forgiveness |
| Add sync status indicator | 3h | User confidence |
| Resume reading position on book open | 2h | Session continuity |
| Add resume dialog in App.tsx | 4h | Session UX |
| Display journey trail breadcrumb | 6h | Navigation context |
| Auto-track entity visits in Reader | 4h | Complete journey data |
| Add "Open in Reader" buttons | 4h | Cross-app navigation |
| Wire notes to browse/search UI | 8h | Data retrieval |
| First-run tutorial overlay | 6h | Onboarding |

### Root Cause

Features built in isolation without:
- End-to-end journey testing
- User validation
- Holistic UX design

**The gap is not capability—it's translation.** Every missing feature has backend support.

---

## Dec 9 Spec Compliance Audit Findings

**Audit Date:** 2025-12-09
**Overall Compliance:** 98%

### Summary by Area

| Area | Compliance | Gap Severity |
|------|------------|--------------|
| Entity Lifecycle | 95% | 🟢 LOW (P2) |
| Cognitive Modes | 85% | 🟡 MEDIUM (P1) |
| Question Engine | 100% | ✅ NONE |
| Cross-App Sync | 98% | 🟡 MEDIUM (P1) |
| Journey Tracking | 70% | 🟡 MEDIUM (P2) |
| Reframe Layer | 100% | ✅ NONE |
| Entity Overlay | 110% | ✅ EXCEEDS |

### Priority Recommendations

**P0 - Critical:** None identified

**P1 - High Value:**
1. ~~**Redis Migration** — SessionStateService uses in-memory storage~~ ✅ **COMPLETE** (Dec 9)
   - Added `redis_client.py` async Redis client singleton
   - Rewrote `session_state_service.py` to use Redis (state + history)
   - 24h TTL with auto-cleanup, 23 unit tests added

2. ~~**Add ARCHIVED Entity Status** — Spec has 4 states, code has 3~~ ✅ **N/A**
   - ContextStatus already has ARCHIVED (4 states)
   - EntityStatus uses different lifecycle (gardening metaphor: CAPTURED→EXPLORING→ANCHORED)

3. ~~**Journey Event Logging** — capture/extraction/template events not logged~~ ✅ **MOSTLY COMPLETE** (Dec 9)
   - Added `JourneyLogger` utility class with all event types
   - Highlight sync, extraction runs, templates now log to journey
   - Remaining: synthesis event logging (partial)

**P2 - Important:**
1. Discovery Mode clarification (spec vs implementation)
2. ~~Journey pattern analysis service~~ ✅ **COMPLETE** (Dec 9)
   - Added `JourneyPatternService` with entity clustering, path detection, recommendations
   - New API: `GET /journey-patterns/user/{user_id}`, `GET /journey-patterns/context/{context_id}`
   - 14 new tests (457 total backend tests)
3. Passage ranking endpoint fix (`POST /rank-passages` → `GET /relevant-passages`)

### Code-Doc Sync Issues Fixed

- Fixed stale line counts in documentation
- Removed Readest references from implementation paths
- Condensed CLAUDE.md from 1948 → 195 lines (90% reduction)
- Consolidated Serena memories from 12 → 5
