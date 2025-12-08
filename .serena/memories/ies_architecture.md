# IES Architecture — Current State (Dec 8, 2025)

## Sprint Status (Updated Dec 8)

| Sprint | Feature | Backend | IES Reader | SiYuan | Status |
|--------|---------|---------|------------|--------|--------|
| 1 | AI Facet Decomposition | ✅ | - | ✅ AddFacetForm | Complete |
| 2 | Evidence Display | ✅ | ✅ EvidenceSection | ✅ EvidenceSection | Complete |
| 3 | Cross-App Sync | ✅ | Pending | Pending | Backend done |

**Test Count:** 234 backend tests passing

## Sync Service (Sprint 3 - Dec 8)

Cross-app continuity between SiYuan and IES Reader.

**Schemas (`sync.py`):**
- `ExplorationSession`: id, user_id, app_source, status, journey_path, trail_stack
- `ReadingPosition`: book_hash, calibre_id, cfi, chapter, progress_percent
- `JourneyStep`: entity_id, entity_name, timestamp, dwell_time

**API (`/sync`):**
- `POST /sessions` — Create/update session
- `GET /sessions/active` — Active/paused sessions
- `GET /sessions/{id}/resume` — Resume data with deep link

**Deep Links:**
- `readest://open?bookHash={hash}&cfi={cfi}&ies-session={id}`
- `siyuan://blocks/{note_id}?ies-session={id}&entity={entity_id}`

## Four-Layer System

| Layer | Component | Status | Key Files |
|-------|-----------|--------|-----------|
| 1 | Knowledge Graph | Production | `library/graph/unified_client.py` (1,476 lines) |
| 2 | Backend APIs | 234 tests passing | `ies/backend/src/ies_backend/` |
| 3 | SiYuan Plugin | Remediation complete | `.worktrees/siyuan/ies/plugin/` |
| 4 | Readest | Wave 2 complete, Wave 3 in progress | `.worktrees/readest/` |

## Backend API Routes (Layer 2)

| Route | Purpose |
|-------|---------|
| `/context` | Context Notes: parse, save, search, journey (NEW Dec 8) |
| `/graph` | Entity search, exploration, relationships |
| `/session` | Thinking sessions, ForgeMode |
| `/journeys` | Breadcrumb tracking, synthesis |
| `/profile` | User profiles, login |
| `/books` | Calibre catalog, covers, file serving |
| `/templates` | Thinking mode templates |
| `/reframes` | Concept metaphors/analogies |
| `/personal` | Sparks, insights, ADHD-friendly capture |
| `/flow` | Flow session lifecycle |
| `/inbox` | Quick capture processing |
| `/sync` | Cross-app session sync (NEW Dec 8) |

## Key Services

- **UnifiedGraphClient** — Single Neo4j connection pool, 14 entity types preserved
- **SessionStore** — Redis-backed sessions, 24-hour TTL
- **FlowOrientationService** — Exploration strand generation
- **InboxService** — AI entity extraction from captures
- **FeedbackService** — Question response tracking

## Entity Types (14 total)

Domain: Concept, Person, Theory, Framework, Assessment
Personal: Spark, Insight, Thread, FavoriteProblem, Reframe
Patterns: Pattern, DynamicPattern, StoryInsight, SchemaBreak

## SiYuan Plugin Structure

9-folder hierarchy:
- `/Daily/` — Quick captures
- `/Seedlings/` — Atomic ideas (7 subcategories)
- `/Sessions/` — Mode-specific thinking (5 modes)
- `/Flow_Maps/` — Visual exploration
- `/Concepts/` — Canonical concepts
- `/Insights/` — Promoted insights
- `/Favorite_Problems/` — Anchor questions
- `/Projects/` — Active work
- `/Archive/` — Retired material

## Reframe Layer Pipeline (Dec 7, 2025)

| Pass | File | Purpose |
|------|------|---------|
| Pass 1 | `library/graph/entities.py` | Extract 9 entity types from text |
| Pass 2 | `library/graph/reframe_mapper.py` | Cross-domain resonance check ("ADHD Leap") |
| Pass 3 | `library/graph/reframe_generator.py` | Generate reframes for dense concepts |

**Integration:** `scripts/auto_ingest_daemon.py` runs Pass 1 + Pass 2 automatically.

**Run Pass 3:** `python -m library.graph.reframe_generator 10`

## Context Layer (Dec 8, 2025)

Question-driven exploration mode for Flow. Contexts are "places where attention lives."

**Context Types:** feynman_problem, project, theory, concept_cluster, life_area

**Context Note Structure (SiYuan):**
- `## Key Questions` — Clickable question buttons in Flow
- `## Areas of Exploration` — Topic areas to investigate  
- `## Core Concepts` — Clickable concept chips

**Backend (`/context`):**
- `POST /parse` — Detect Context Note from markdown
- `POST /save-parsed` — Save parsed context to Neo4j
- `GET /{id}` — Get context by ID
- `POST /{id}/search` — Keyword search based on context concepts
- `GET /{id}/journey` — Journey entries for context

**Flow Mode Integration:**
- `contextBlockId` prop detects Context Notes on mount
- Context Panel shows questions as clickable buttons
- Question click → keyword search → show related entities
- Core Concepts clickable to explore in normal Flow

**Phase 1: Navigation Foundation (Dec 8):**
- Navigation state machine: `FocusState` = 'idle' | 'question' | 'entity' | 'facet'
- Trail navigation (breadcrumbs) showing path: Context → Question → Entity
- EntityFocus view: name, type, description, neighbors, source books
- Click entity neighbors to continue graph traversal
- Click trail items to navigate back to any point

**Phase 2: Standalone Navigation (Dec 8):**
- Fixed plugin → backend connection using `forwardProxy` pattern for Docker CORS
- Standalone entity panel: search → click entity → view details outside Context Mode
- Standalone facet panel: entity → click facet → view facet entities
- Entity panel shows: type badge, name, description, facets, related concepts, source books
- Facet panel shows: parent entity, facet name, entities in facet
- Search results hidden when viewing entity/facet (`focusState === 'idle'` only)
- Full navigation flow: search → entity → facet → back to entity → back to search

**Files:**
- `ies/backend/src/ies_backend/schemas/context.py`
- `ies/backend/src/ies_backend/services/context_service.py`
- `ies/backend/src/ies_backend/api/context.py`
- `.worktrees/siyuan/ies/plugin/src/views/FlowMode.svelte` (extended)

## IES Reader Features

- Calibre library browser with search/filter
- PWA with offline support
- Entity overlay (inline highlighting)
- Flow panel (relationships, sources, questions)
- Interactive questions with Cmd+Enter response
- Journey breadcrumbs (visible navigation trail)
- Notes capture with entity context

## Docker Services

```yaml
brain_explore_neo4j     # 7474, 7687
brain_explore_qdrant    # 6333, 6334
brain_explore_redis     # 6379
brain_explore_calibre   # 8083
brain_explore_siyuan    # 6806
```

## Integration Points

- Calibre → Neo4j: `calibre_id` as universal book identifier
- Backend → Redis: Session state persistence
- SiYuan ↔ Backend: forwardProxy from Docker
- Readest ↔ Backend: Direct HTTP (localhost:8081)
