# Sprint 3: Reader Sync Implementation Plan

**Created:** 2025-12-08
**Status:** Planning Complete
**Goal:** Cross-app continuity between SiYuan plugin and ies-reader

---

## Executive Summary

Reader Sync enables cross-app continuity between the SiYuan plugin and ies-reader (Readest). Users can resume reading sessions from SiYuan and resume explorations from the reader. This addresses **Gap 4: Cross-App Continuity Missing**.

---

## 1. Architecture Overview

### Current State

**ies-reader (flowModeStore.ts):**
- Zustand store with journey tracking
- `BreadcrumbJourney` with path, marks, thinking partner exchanges
- `JourneyStep` tracks entity_id, entity_name, timestamp, source_passage, dwell_time
- Local state only - no persistence on navigation

**SiYuan Plugin (FlowMode.svelte):**
- Svelte stores for session and context
- Trail-based navigation with `TrailItem[]`
- `FocusState` machine: idle | question | entity | facet
- No journey persistence

**Backend APIs (Already Exist):**
- `/journeys` - Full CRUD for `BreadcrumbJourney`
- `/flow` - FlowSession management with breadcrumb recording
- `/context/{id}/journey` - Context-specific journey entries

### Proposed Architecture

```
                    ┌─────────────────────────────────────┐
                    │           IES Backend               │
                    │                                     │
                    │  ┌─────────────────────────────┐    │
                    │  │     Exploration Session     │    │
                    │  │         (Neo4j)             │    │
                    │  │  - session_id               │    │
                    │  │  - user_id                  │    │
                    │  │  - app_source (reader/siyuan)│   │
                    │  │  - current_entity_id        │    │
                    │  │  - reading_position (CFI)   │    │
                    │  │  - journey_path[]           │    │
                    │  │  - updated_at               │    │
                    │  │  - status (active/paused)   │    │
                    │  └─────────────────────────────┘    │
                    │                                     │
                    │  GET  /sync/sessions               │
                    │  POST /sync/sessions               │
                    │  PUT  /sync/sessions/{id}          │
                    │  GET  /sync/sessions/{id}/resume   │
                    └──────────────┬──────────────────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                      │                      │
    ┌───────▼───────┐      ┌───────▼───────┐      ┌───────▼───────┐
    │  ies-reader   │      │    SiYuan     │      │ Deep Links    │
    │   (Readest)   │      │    Plugin     │      │               │
    │               │      │               │      │ readest://    │
    │ syncService   │◄────►│ syncService   │      │ siyuan://     │
    │  - push()     │      │  - push()     │      │               │
    │  - pull()     │      │  - pull()     │      │               │
    │  - onEvent()  │      │  - onEvent()  │      │               │
    └───────────────┘      └───────────────┘      └───────────────┘
```

---

## 2. Data Model

### ExplorationSession Schema

```python
class AppSource(str, Enum):
    READER = "reader"
    SIYUAN = "siyuan"

class SessionStatus(str, Enum):
    ACTIVE = "active"      # Currently being explored
    PAUSED = "paused"      # User left, can resume
    COMPLETED = "completed" # User explicitly ended

class ReadingPosition(BaseModel):
    book_hash: str
    calibre_id: int | None = None
    cfi: str | None = None
    chapter: str | None = None
    progress_percent: float | None = None

class ExplorationSession(BaseModel):
    id: str
    user_id: str
    app_source: AppSource
    created_at: datetime
    updated_at: datetime
    status: SessionStatus = SessionStatus.ACTIVE

    # Current state
    current_entity_id: str | None = None
    current_entity_name: str | None = None
    reading_position: ReadingPosition | None = None

    # Journey
    journey_path: list[JourneyStep] = []
    trail_stack: list[dict] = []

    # Resume
    resume_hint: str | None = None
```

---

## 3. API Endpoints

### New `/sync` Router

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/sync/sessions` | Create or update session |
| GET | `/sync/sessions/active` | Get active/paused sessions |
| GET | `/sync/sessions/{id}` | Get specific session |
| GET | `/sync/sessions/{id}/resume` | Get resume data for target app |
| PUT | `/sync/sessions/{id}/status` | Update session status |

---

## 4. Implementation Phases

### Phase 1: Backend Sync Service (3-4 days)

1. **Create Schemas** - `ies/backend/src/ies_backend/schemas/sync.py`
2. **Create Service** - `ies/backend/src/ies_backend/services/sync_service.py`
3. **Create API Router** - `ies/backend/src/ies_backend/api/sync.py`
4. **Write Tests** - `ies/backend/tests/test_sync_service.py`

### Phase 2: Reader Integration (3-4 days)

1. **Create SyncService** - `src/services/syncService.ts`
2. **Extend flowModeStore** - Add `sessionId`, auto-sync on navigation
3. **Add Resume UI** - "Resume in SiYuan" button in FlowPanel
4. **Handle Deep Links** - URL params for session resume

### Phase 3: SiYuan Integration (3-4 days)

1. **Create SyncService** - `src/services/syncService.ts`
2. **Extend FlowMode** - Sync trail changes to backend
3. **Add Dashboard UI** - "Resume Reading Sessions" section
4. **Handle Deep Links** - `siyuan://` protocol handling

---

## 5. Sync Triggers

### Push Events

| Event | ies-reader | SiYuan |
|-------|------------|--------|
| Entity navigation | Immediate | Immediate |
| Reading position | Debounced (5s) | N/A |
| Journey step | Immediate | Immediate |
| Panel open/close | Status update | Status update |
| App close | Pause session | Pause session |

### Pull Events

| Scenario | Action |
|----------|--------|
| App launch | Fetch active sessions |
| Flow panel open | Check resumable sessions |
| Manual refresh | "Sync" button |

---

## 6. Deep Link Formats

**Reader → SiYuan:**
```
siyuan://blocks/{note_id}?ies-session={session_id}&entity={entity_id}
```

**SiYuan → Reader:**
```
readest://open?bookHash={hash}&cfi={cfi}&ies-session={session_id}&entity={entity_id}
```

**Web fallback:**
```
http://localhost:3002/reader/{bookHash}?session={session_id}&entity={entity_id}&cfi={cfi}
```

---

## 7. Testing Strategy

### Unit Tests
- SyncService CRUD operations
- Deep link generation/parsing
- Debounce behavior
- Conflict resolution

### Integration Tests
- Create in reader → resume in SiYuan
- Create in SiYuan → resume in reader
- Multiple sessions per user
- Session timeout/cleanup

### E2E Tests
1. Open book, explore entity, resume in SiYuan
2. Start SiYuan exploration, resume in reader
3. Close mid-exploration, verify resume
4. Switch apps repeatedly, verify consistency

---

## 8. Edge Cases

### Offline Handling
- Queue sync operations
- Replay on reconnection
- Show "Sync pending" indicator

### Conflict Resolution
- Use `updated_at` for last-write-wins on position
- Merge journey steps (never lose data)

### Stale Sessions
- Auto-pause after 30 min inactivity
- Show "Last active X ago"
- Archive option for old sessions

---

## Key Files

| File | Purpose |
|------|---------|
| `ies/backend/src/ies_backend/schemas/sync.py` | New sync schemas |
| `ies/backend/src/ies_backend/api/sync.py` | New API router |
| `.worktrees/ies-reader/.../store/flowModeStore.ts` | Extend with sync |
| `.worktrees/siyuan/.../views/FlowMode.svelte` | Extend with sync |
| `.worktrees/siyuan/.../views/Dashboard.svelte` | Resume UI |
