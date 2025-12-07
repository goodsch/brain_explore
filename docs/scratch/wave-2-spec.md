# Wave 2 Specification: Frontend-Backend Wiring

**Date:** 2025-12-06
**Status:** In Progress
**Depends on:** Wave 1 (Complete)

---

## Overview

Wave 2 wires the frontend applications (IES Reader, SiYuan) to backend APIs. The core goal is to make data flow bidirectionally so journeys are persisted, entities come from the knowledge graph, and user identity is unified.

---

## Task 2.1: IES Reader-Backend Integration

### Current State

**Working:**
- EPUB reading with text selection
- Flow Panel with entity display
- In-memory journey tracking
- graphClient methods exist for backend calls

**Broken:**
- `endJourney()` never calls `saveJourney()` (Reader.tsx:56)
- No `user_id` in flowStore or journey data
- Schema mismatch: frontend camelCase vs backend snake_case
- No sync status indicator
- No login flow
- `saveJourney()` path may be incorrect

### Schema Alignment

Frontend `BreadcrumbJourney`:
```typescript
interface BreadcrumbJourney {
  id: string;
  startedAt: string;
  endedAt?: string;
  entryPoint: { type: string; reference: string; };
  path: JourneyStep[];  // entityId, entityName, timestamp, sourcePassage, dwellTimeSeconds
}
```

Backend `JourneyCreateRequest`:
```python
class JourneyCreateRequest:
    user_id: str                    # MISSING in frontend
    entry_point: EntryPoint         # { type, reference, context }
    path: list[JourneyStep]         # entity_id, entity_name, timestamp, source_passage, dwell_time_seconds
    marks: list[JourneyMark]        # Optional
    thinking_partner_exchanges: list[ThinkingPartnerExchange]  # Optional
    title: str | None
    tags: list[str]
    notes: str | None
```

### Implementation Steps

#### 2.1.1: Add user_id to flowStore
- Add `userId: string | null` to FlowModeState
- Add `setUserId: (id: string) => void` action
- Pass user_id to all backend calls

#### 2.1.2: Add login flow to App.tsx
- On app load, call `/profile/login` with device ID or stored ID
- Store returned user_id in flowStore
- Show loading state during login

#### 2.1.3: Fix graphClient.saveJourney()
- Add transformation from camelCase to snake_case
- Include user_id in request body
- Handle errors with retry queue

#### 2.1.4: Wire endJourney to saveJourney
- In Reader.tsx:toggleFlowPanel, call `graphClient.saveJourney()`
- Pass user_id from flowStore
- Add error handling

#### 2.1.5: Add sync status indicator
- Add `syncStatus: 'idle' | 'pending' | 'synced' | 'error'` to flowStore
- Display indicator in FlowPanel header
- Track pending saves for retry

#### 2.1.6: Add journey history fetch
- Add `loadJourneyHistory()` to graphClient
- Fetch on FlowPanel open (optional, future enhancement)

### Files to Modify
- `ies/reader/src/store/flowStore.ts` - Add userId, syncStatus
- `ies/reader/src/services/graphClient.ts` - Fix saveJourney, add transforms
- `ies/reader/src/components/Reader.tsx` - Wire endJourney to save
- `ies/reader/src/components/flow/FlowPanel.tsx` - Add sync indicator
- `ies/reader/src/App.tsx` - Add login flow

### Verification
```bash
# Start services
docker compose up -d
cd ies/backend && uv run uvicorn ies_backend.main:app --reload --port 8081 &
cd ies/reader && npm run dev

# Test flow:
# 1. Open reader, verify login call to /profile/login
# 2. Select text, verify entity lookup
# 3. Close Flow Panel, verify journey saves to backend
# 4. Check backend: curl http://localhost:8081/journeys/user/test-user
```

---

## Task 2.2: SiYuan-Backend Integration

**Location:** `.worktrees/siyuan/ies/plugin/src/`

### Current State
- Plugin exists with ForgeMode, FlowMode, Dashboard views
- Backend calls exist via `callBackendApi()`
- No journey history display from backend
- Errors return null (silent failures)

### Implementation Steps

#### 2.2.1: Fix callBackendApi error handling
- Return structured error instead of null
- Surface errors in UI

#### 2.2.2: Wire FlowMode to journey API
- Record exploration as journey via `/journeys` endpoint
- Pass user_id

#### 2.2.3: Wire Dashboard to journey history
- Fetch journey list from `/journeys/user/{user_id}`
- Display in Dashboard view

### Files to Modify
- `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts`
- `.worktrees/siyuan/ies/plugin/src/views/FlowMode.svelte`
- `.worktrees/siyuan/ies/plugin/src/views/Dashboard.svelte`

---

## Task 2.3: Cross-App Sync Design

### Requirements
- IES Reader and SiYuan both record journeys to same backend
- User identity unified via profile service
- Journey started in Reader visible in SiYuan Dashboard
- No real-time sync needed (refresh to see updates)

### Design
**Simplified approach (no WebSocket):**
1. All apps call same backend endpoints
2. All apps use same user_id from profile service
3. Dashboard refreshes on open to show latest journeys
4. No offline queue in Phase 1 (network required)

### Implementation Notes
- SiYuan plugin gets user_id from stored config or `/profile/login`
- IES Reader generates device ID for anonymous users
- Both save to `/journeys` with user_id
- Both fetch from `/journeys/user/{user_id}`

---

## Agent Assignments

| Task | Agent Type | Priority |
|------|------------|----------|
| 2.1.1-2.1.6 | fullstack-developer | High (do first) |
| 2.2.1-2.2.3 | fullstack-developer | Medium |
| 2.3 | Documented (no code) | Low |

---

## Success Criteria

- [ ] IES Reader saves journeys to backend on Flow Panel close
- [ ] IES Reader shows sync status (pending/synced/error)
- [ ] Backend `/journeys/user/{user_id}` returns saved journeys
- [ ] No console errors during normal operation
- [ ] Schema transformation correct (camelCase → snake_case)
