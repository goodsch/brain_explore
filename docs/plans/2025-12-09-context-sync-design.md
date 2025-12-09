# Context Sync Design: IES Reader ↔ SiYuan Plugin

**Created:** 2025-12-09
**Status:** Design Phase
**Priority:** P0 — Critical Gap #4 (Cross-App Continuity)

---

## Executive Summary

**Problem:** IES Reader (React) and SiYuan plugin (Svelte) both manage exploration state independently. Users cannot seamlessly transition between apps (e.g., start question in Reader → continue in SiYuan).

**Solution:** Lightweight polling-based sync using existing `/session` API with state reconciliation. Each app polls for updates every 5 seconds when active, applies remote changes, and debounces local writes.

**Key Decisions:**
- **Polling (not WebSocket):** Simpler, stateless, works with existing backend
- **Session-based conflict resolution:** Last write wins with 3-second debounce
- **Optimistic UI:** Local changes apply immediately, sync in background
- **Active app detection:** Browser/window focus events determine poll frequency

---

## 1. Current State Analysis

### IES Reader State (flowStore.ts)

**Context State:**
```typescript
interface FlowStore {
  // Context
  currentContextId: string | null;
  currentContext: Context | null;
  selectedArea: string | null;

  // Question
  currentQuestionId: string | null;
  questions: FlowQuestion[];

  // Session tracking
  currentSessionId: string | null;
  currentEntity: { id: string; name: string } | null;
  journeyPath: JourneyStep[];
  readingPosition: ReadingPosition | null;
}
```

**Existing Session Sync:**
- Uses `syncApi` with `/session` endpoints
- Creates sessions on journey start
- Updates session periodically (debounced)
- Stores: entity, journey path, reading position
- **Gap:** No context_id, question_id, extraction profile sync

### SiYuan Plugin State (FlowMode.svelte)

**Context State:**
```typescript
// Context Mode State
let isContextMode = false;
let parsedContext: ParsedContext | null = null;
let savedContextId: string | null = null;
let activeQuestionIndex: number | null = null;

// Extraction state
let extractionResult: {...} | null = null;

// Session sync
let sessionId: string | null = null;
let lastSyncTime: number = 0;
```

**Current Sync Behavior:**
- Manual `syncSession()` function (debounced 3 seconds)
- No polling implementation
- No conflict resolution
- **Gap:** No bidirectional sync with Reader

---

## 2. Sync Strategy: Lightweight Polling

### Architecture

```
┌─────────────┐                    ┌─────────────┐
│ IES Reader  │                    │   SiYuan    │
│  (React)    │                    │   Plugin    │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  Poll every 5s (active)          │
       │  Poll every 30s (inactive)       │
       │                                  │
       ├──────────────┐  ┌───────────────┤
       │              │  │               │
       ▼              ▼  ▼               ▼
┌──────────────────────────────────────────┐
│     Backend /session API                 │
│  - GET /session/{id}                     │
│  - PATCH /session/{id}                   │
│  - GET /session/user/{user_id}/active    │
└──────────────────────────────────────────┘
```

### Why Polling (Not WebSocket)?

**Pros:**
- ✅ Stateless: No connection management
- ✅ Simple: Reuse existing `/session` API
- ✅ Resilient: Auto-recovers from disconnects
- ✅ Low overhead: 5-second interval sufficient

**Cons:**
- ❌ Slight delay: 5 seconds worst-case latency
- ❌ Polling overhead: But minimal with debouncing

**Decision:** Polling is sufficient for exploration context (not real-time chat). WebSocket adds complexity without clear benefit.

---

## 3. Session State Schema Extensions

### Extended SessionState API

**New Fields to Add:**

```typescript
interface ExplorationSession {
  // Existing fields
  id: string;
  user_id: string;
  app_source: 'reader' | 'siyuan';
  status: 'active' | 'paused' | 'completed';

  // NEW: Context sync
  context_id: string | null;           // Active context
  selected_question_id: string | null;  // Current question
  selected_area: string | null;         // Area of exploration

  // NEW: Extraction profile
  extraction_profile_id: string | null; // Shared extraction config

  // NEW: Conflict resolution
  last_modified_by: 'reader' | 'siyuan'; // Which app made last change
  version: number;                       // Increment on each update

  // Existing journey tracking
  current_entity_id: string | null;
  current_entity_name: string | null;
  journey_path: JourneyStep[];
  reading_position: ReadingPosition | null;

  created_at: string;
  updated_at: string;
}
```

**Backend Changes Required:**

1. **Schema Update** (`ies/backend/src/ies_backend/schemas/session.py`):
   - Add `context_id`, `selected_question_id`, `selected_area`
   - Add `extraction_profile_id`
   - Add `last_modified_by`, `version`

2. **Service Update** (`ies/backend/src/ies_backend/services/session_service.py`):
   - Store new fields in in-memory storage
   - Increment `version` on each update
   - Return full state on GET

3. **No New Endpoints:** Existing `/session/*` endpoints sufficient

---

## 4. Conflict Resolution Strategy

### Last Write Wins with Debouncing

**Rules:**
1. **Local changes apply immediately** (optimistic UI)
2. **Debounce writes:** Wait 3 seconds after last local change before syncing
3. **Compare versions:** If remote `version > local version`, apply remote changes
4. **Merge strategy:** Remote changes win, but preserve local debounced writes

**Example Flow:**

```
Time  | Reader Action           | SiYuan Action          | Backend State
------|-------------------------|------------------------|----------------
0s    | Select question Q1      |                        | question=Q1, v=1
2s    | (debouncing...)         | Select question Q2     | question=Q2, v=2
3s    | Write Q1 → backend      | (Q2 already written)   | question=Q1, v=3 ❌ CONFLICT
3.1s  | Poll: receive Q2, v=2   |                        | question=Q2, v=2 ✅ Reader updates to Q2
```

**Conflict Detection:**

```typescript
function shouldApplyRemoteState(local: SessionState, remote: SessionState): boolean {
  // Apply if remote is newer AND different
  return remote.version > local.version &&
         !isEqual(remote, local);
}
```

---

## 5. Active App Detection

### Browser Focus Events (IES Reader)

```typescript
// In Reader.tsx or App component
useEffect(() => {
  const handleFocus = () => {
    setPollInterval(5000); // Active: 5 seconds
  };

  const handleBlur = () => {
    setPollInterval(30000); // Inactive: 30 seconds
  };

  window.addEventListener('focus', handleFocus);
  window.addEventListener('blur', handleBlur);

  return () => {
    window.removeEventListener('focus', handleFocus);
    window.removeEventListener('blur', handleBlur);
  };
}, []);
```

### SiYuan Plugin Focus Detection

```typescript
// In FlowMode.svelte
let isActive = true;
let pollInterval: NodeJS.Timeout | null = null;

function handleVisibilityChange() {
  isActive = !document.hidden;

  if (isActive) {
    startPolling(5000); // 5 seconds when active
  } else {
    startPolling(30000); // 30 seconds when inactive
  }
}

onMount(() => {
  document.addEventListener('visibilitychange', handleVisibilityChange);
  startPolling(5000);
});

onDestroy(() => {
  document.removeEventListener('visibilitychange', handleVisibilityChange);
  stopPolling();
});
```

---

## 6. Implementation: IES Reader

### 6.1 Hook: useContextSync()

**New file:** `ies/reader/src/hooks/useContextSync.ts`

```typescript
import { useEffect, useRef, useState } from 'react';
import { useFlowStore } from '../store/flowStore';
import { syncApi } from '../services';

export interface SyncConfig {
  enabled: boolean;
  pollInterval: number; // milliseconds
  debounceMs: number;   // milliseconds
}

export function useContextSync(config: SyncConfig = {
  enabled: true,
  pollInterval: 5000,
  debounceMs: 3000,
}) {
  const store = useFlowStore();
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<number>(0);

  // Local state version tracking
  const localVersion = useRef(0);
  const writeDebounceTimer = useRef<NodeJS.Timeout | null>(null);
  const pollInterval = useRef<NodeJS.Timeout | null>(null);

  // Track local changes
  const currentState = {
    context_id: store.currentContextId,
    selected_question_id: store.currentQuestionId,
    selected_area: store.selectedArea,
    current_entity_id: store.currentEntity?.id,
    current_entity_name: store.currentEntity?.name,
    journey_path: store.journeyPath,
    reading_position: store.readingPosition,
  };

  /**
   * Write local state to backend (debounced)
   */
  const writeState = async () => {
    if (!store.currentSessionId || !store.userId) return;

    // Clear existing debounce timer
    if (writeDebounceTimer.current) {
      clearTimeout(writeDebounceTimer.current);
    }

    // Debounce: wait 3 seconds before writing
    writeDebounceTimer.current = setTimeout(async () => {
      setIsSyncing(true);
      try {
        await syncApi.updateSession(store.currentSessionId!, {
          ...currentState,
          last_modified_by: 'reader',
          version: localVersion.current + 1,
        });
        localVersion.current += 1;
        setLastSyncTime(Date.now());
      } catch (error) {
        console.error('[ContextSync] Write failed:', error);
      } finally {
        setIsSyncing(false);
      }
    }, config.debounceMs);
  };

  /**
   * Read remote state from backend (polling)
   */
  const readState = async () => {
    if (!store.currentSessionId) return;

    try {
      const session = await syncApi.getSession(store.currentSessionId);

      // Check if remote is newer
      if (session.version > localVersion.current) {
        console.log('[ContextSync] Applying remote state', {
          remote_version: session.version,
          local_version: localVersion.current,
        });

        // Apply remote changes to store
        if (session.context_id !== store.currentContextId) {
          store.setCurrentContextId(session.context_id);
        }
        if (session.selected_question_id !== store.currentQuestionId) {
          store.setCurrentQuestionId(session.selected_question_id);
        }
        if (session.selected_area !== store.selectedArea) {
          store.setSelectedArea(session.selected_area);
        }
        if (session.current_entity_id !== store.currentEntity?.id) {
          store.setCurrentEntity(
            session.current_entity_id
              ? { id: session.current_entity_id, name: session.current_entity_name || '' }
              : null
          );
        }

        // Update local version
        localVersion.current = session.version;
        setLastSyncTime(Date.now());
      }
    } catch (error) {
      console.error('[ContextSync] Read failed:', error);
    }
  };

  /**
   * Start polling for remote changes
   */
  const startPolling = (interval: number) => {
    stopPolling();
    pollInterval.current = setInterval(readState, interval);
  };

  /**
   * Stop polling
   */
  const stopPolling = () => {
    if (pollInterval.current) {
      clearInterval(pollInterval.current);
      pollInterval.current = null;
    }
  };

  // Effect: Write local changes (debounced)
  useEffect(() => {
    if (!config.enabled) return;
    writeState();
  }, [
    store.currentContextId,
    store.currentQuestionId,
    store.selectedArea,
    store.currentEntity,
  ]);

  // Effect: Start/stop polling based on config
  useEffect(() => {
    if (!config.enabled) return;

    startPolling(config.pollInterval);

    return () => {
      stopPolling();
      if (writeDebounceTimer.current) {
        clearTimeout(writeDebounceTimer.current);
      }
    };
  }, [config.enabled, config.pollInterval]);

  return {
    isSyncing,
    lastSyncTime,
    manualSync: readState,
  };
}
```

### 6.2 Integration: Reader.tsx

```typescript
import { useContextSync } from '../hooks/useContextSync';

export function Reader() {
  const [pollInterval, setPollInterval] = useState(5000);

  // Enable context sync
  const { isSyncing, lastSyncTime } = useContextSync({
    enabled: true,
    pollInterval,
    debounceMs: 3000,
  });

  // Adjust poll rate based on window focus
  useEffect(() => {
    const handleFocus = () => setPollInterval(5000);  // Active: 5s
    const handleBlur = () => setPollInterval(30000);  // Inactive: 30s

    window.addEventListener('focus', handleFocus);
    window.addEventListener('blur', handleBlur);

    return () => {
      window.removeEventListener('focus', handleFocus);
      window.removeEventListener('blur', handleBlur);
    };
  }, []);

  // ... rest of Reader component
}
```

---

## 7. Implementation: SiYuan Plugin

### 7.1 Service: contextSyncService.ts

**New file:** `.worktrees/siyuan/ies/plugin/src/services/contextSyncService.ts`

```typescript
import { apiGet, apiPost } from '../utils/siyuan-structure';

export interface ContextSyncState {
  context_id: string | null;
  selected_question_id: string | null;
  selected_area: string | null;
  current_entity_id: string | null;
  current_entity_name: string | null;
  extraction_profile_id: string | null;
  version: number;
}

export class ContextSyncService {
  private sessionId: string | null = null;
  private localVersion: number = 0;
  private pollInterval: NodeJS.Timeout | null = null;
  private writeDebounceTimer: NodeJS.Timeout | null = null;
  private backendUrl: string;

  // Callbacks for state changes
  private onStateChange: ((state: ContextSyncState) => void) | null = null;

  constructor(backendUrl: string) {
    this.backendUrl = backendUrl;
  }

  /**
   * Initialize sync with session ID
   */
  public init(sessionId: string, onStateChange: (state: ContextSyncState) => void) {
    this.sessionId = sessionId;
    this.onStateChange = onStateChange;
    this.startPolling(5000); // Start with 5-second interval
  }

  /**
   * Update local state and sync to backend (debounced)
   */
  public async updateState(state: Partial<ContextSyncState>) {
    if (!this.sessionId) return;

    // Clear existing debounce timer
    if (this.writeDebounceTimer) {
      clearTimeout(this.writeDebounceTimer);
    }

    // Debounce: wait 3 seconds before writing
    this.writeDebounceTimer = setTimeout(async () => {
      try {
        const response = await apiPost(
          `${this.backendUrl}/session/${this.sessionId}`,
          {
            ...state,
            last_modified_by: 'siyuan',
            version: this.localVersion + 1,
          }
        );
        this.localVersion = response.version;
      } catch (error) {
        console.error('[ContextSync] Write failed:', error);
      }
    }, 3000);
  }

  /**
   * Poll backend for remote changes
   */
  private async pollRemoteState() {
    if (!this.sessionId) return;

    try {
      const session = await apiGet(`${this.backendUrl}/session/${this.sessionId}`);

      // Check if remote is newer
      if (session.version > this.localVersion) {
        console.log('[ContextSync] Applying remote state', {
          remote_version: session.version,
          local_version: this.localVersion,
        });

        // Notify component of state change
        if (this.onStateChange) {
          this.onStateChange({
            context_id: session.context_id,
            selected_question_id: session.selected_question_id,
            selected_area: session.selected_area,
            current_entity_id: session.current_entity_id,
            current_entity_name: session.current_entity_name,
            extraction_profile_id: session.extraction_profile_id,
            version: session.version,
          });
        }

        this.localVersion = session.version;
      }
    } catch (error) {
      console.error('[ContextSync] Poll failed:', error);
    }
  }

  /**
   * Start polling with interval
   */
  public startPolling(interval: number) {
    this.stopPolling();
    this.pollInterval = setInterval(() => this.pollRemoteState(), interval);
  }

  /**
   * Stop polling
   */
  public stopPolling() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
  }

  /**
   * Clean up resources
   */
  public destroy() {
    this.stopPolling();
    if (this.writeDebounceTimer) {
      clearTimeout(this.writeDebounceTimer);
    }
  }
}
```

### 7.2 Integration: FlowMode.svelte

```typescript
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { ContextSyncService, type ContextSyncState } from '../services/contextSyncService';

  export let backendUrl: string;
  export let sessionId: string | null = null;

  let syncService: ContextSyncService | null = null;
  let isActive = true;

  // Existing state
  let isContextMode = false;
  let savedContextId: string | null = null;
  let activeQuestionIndex: number | null = null;

  /**
   * Handle remote state changes from Reader
   */
  function handleRemoteStateChange(state: ContextSyncState) {
    console.log('[FlowMode] Remote state changed:', state);

    // Update local state
    if (state.context_id !== savedContextId) {
      savedContextId = state.context_id;
      if (state.context_id) {
        // Auto-activate context mode if context arrives
        detectContextInDocument(state.context_id);
      }
    }

    if (state.selected_question_id) {
      // Find question index and select it
      // (Requires question ID mapping)
    }
  }

  /**
   * Push local state changes to backend
   */
  function syncLocalState() {
    if (!syncService) return;

    syncService.updateState({
      context_id: savedContextId,
      selected_question_id: activeQuestionIndex !== null
        ? parsedContext?.key_questions[activeQuestionIndex]
        : null,
      current_entity_id: focusedEntity?.name,
      current_entity_name: focusedEntity?.name,
    });
  }

  // Initialize sync service
  onMount(() => {
    if (sessionId && backendUrl) {
      syncService = new ContextSyncService(backendUrl);
      syncService.init(sessionId, handleRemoteStateChange);
    }

    // Adjust polling based on visibility
    document.addEventListener('visibilitychange', () => {
      isActive = !document.hidden;
      if (syncService) {
        syncService.startPolling(isActive ? 5000 : 30000);
      }
    });
  });

  onDestroy(() => {
    if (syncService) {
      syncService.destroy();
    }
  });

  // Watch for local changes and sync
  $: if (savedContextId !== null || activeQuestionIndex !== null) {
    syncLocalState();
  }
</script>
```

---

## 8. User Experience Flows

### Flow 1: Reader → SiYuan Context Handoff

```
1. User opens book in Reader
2. User selects context "Understanding Executive Function"
   → flowStore.setCurrentContextId()
   → useContextSync writes to backend (debounced 3s)
3. User switches to SiYuan
   → SiYuan polls backend (5s interval)
   → Receives context_id
   → FlowMode auto-activates context mode
   → Displays context panel with key questions
4. User clicks question in SiYuan
   → Updates activeQuestionIndex
   → syncService.updateState() writes to backend (debounced)
5. User switches back to Reader
   → Reader polls backend
   → Receives selected_question_id
   → QuestionSelector auto-selects question
   → FlowPanel shows relevant passages
```

### Flow 2: SiYuan → Reader Question Continuation

```
1. User creates new question in SiYuan Context Note
   → Question saved via /questions API
2. User opens Reader
   → Reader polls /session
   → Detects new context_id + selected_question_id
   → QuestionSelector displays question
   → User reads relevant passages
3. User highlights text in Reader
   → Highlight saved with question_id link
   → Journey entry logged
4. User returns to SiYuan
   → Polls backend
   → "What's New" badge shows new highlight
   → Timeline displays reading activity
```

---

## 9. Edge Cases & Failure Modes

### Edge Case 1: Simultaneous Edits

**Scenario:** Both apps change context at same time (within 3s debounce window)

**Handling:**
- Last write wins based on `version` field
- Losing app receives update on next poll
- User sees brief flicker as UI reconciles

**Mitigation:**
- Show sync indicator when state changes remotely
- Optional: Show toast "Context updated in [other app]"

### Edge Case 2: Offline Mode

**Scenario:** Backend unreachable (network down, server restart)

**Handling:**
- Polling fails gracefully (logged, not shown)
- Local state remains functional
- When backend returns, next poll syncs state

**Mitigation:**
- Store `lastSuccessfulSync` timestamp
- Show "Sync paused" indicator if >60 seconds offline

### Edge Case 3: Stale Session

**Scenario:** User has session from yesterday, both apps try to sync

**Handling:**
- Backend marks sessions as `stale` after 24 hours
- Apps create new session on first action
- Old session archived

**Mitigation:**
- `GET /session/user/{user_id}/active` returns most recent active session
- Apps resume latest session on startup

---

## 10. Performance Considerations

### Network Overhead

**Polling Cost:**
- Request size: ~200 bytes (session ID + headers)
- Response size: ~500 bytes (full session state)
- Frequency: Every 5 seconds (active), 30 seconds (inactive)

**Daily Traffic (Single User):**
- Active hours (8h): 8 * 3600 / 5 = 5,760 requests = 2.8 MB
- Inactive hours (16h): 16 * 3600 / 30 = 1,920 requests = 0.9 MB
- **Total:** ~3.7 MB/day per user

**Impact:** Negligible for modern networks.

### Backend Load

**Scenario:** 100 concurrent users

- Requests/second: 100 users / 5s interval = 20 req/s
- Backend: FastAPI handles 1000+ req/s on single core
- **Impact:** Minimal

### Memory

**Per-session storage:** ~1 KB (in-memory)
- 100 users = 100 KB
- **Impact:** Negligible

---

## 11. Testing Strategy

### Unit Tests

**Reader:**
- `useContextSync.test.ts`:
  - ✅ Debounces writes correctly
  - ✅ Polls at correct interval
  - ✅ Applies remote state when version > local
  - ✅ Ignores remote state when version <= local
  - ✅ Adjusts poll rate on focus/blur

**SiYuan:**
- `contextSyncService.test.ts`:
  - ✅ Initializes with session ID
  - ✅ Calls onStateChange callback on remote update
  - ✅ Debounces updateState calls
  - ✅ Cleans up timers on destroy

### Integration Tests

**Backend:**
- `test_session_sync.py`:
  - ✅ Two apps write sequentially → versions increment
  - ✅ Concurrent writes → last write wins
  - ✅ Stale session detection

**E2E:**
- Manual testing:
  1. Open Reader + SiYuan side-by-side
  2. Change context in Reader → verify SiYuan updates within 5s
  3. Change question in SiYuan → verify Reader updates within 5s
  4. Switch focus between apps → verify poll rate changes

---

## 12. Implementation Phases

### Phase 1: Backend Extensions (1-2 hours)

- [ ] Update `ExplorationSession` schema with new fields
- [ ] Update `SessionService` to store/return new fields
- [ ] Increment `version` on each PATCH
- [ ] Write unit tests for version handling

### Phase 2: IES Reader Sync (2-3 hours)

- [ ] Implement `useContextSync()` hook
- [ ] Integrate into `Reader.tsx` or `App.tsx`
- [ ] Add focus/blur event listeners for poll rate adjustment
- [ ] Add sync indicator UI (optional)
- [ ] Write unit tests for hook

### Phase 3: SiYuan Plugin Sync (2-3 hours)

- [ ] Implement `ContextSyncService` class
- [ ] Integrate into `FlowMode.svelte`
- [ ] Add visibility change listener for poll rate
- [ ] Handle remote state updates
- [ ] Write unit tests for service

### Phase 4: Testing & Polish (2-3 hours)

- [ ] E2E testing with both apps open
- [ ] Handle edge cases (offline, stale sessions)
- [ ] Add user feedback (sync indicators, toasts)
- [ ] Performance testing with multiple tabs
- [ ] Documentation updates

**Total Estimated Effort:** 7-11 hours

---

## 13. Alternative Approaches Considered

### Alternative 1: WebSocket Bidirectional Sync

**Pros:**
- Real-time updates (<100ms latency)
- No polling overhead

**Cons:**
- ❌ Complex: Connection management, reconnect logic
- ❌ Stateful: Requires backend connection tracking
- ❌ New infrastructure: WebSocket endpoint needed

**Decision:** Overkill for exploration context. Polling sufficient.

### Alternative 2: Shared IndexedDB/LocalStorage

**Pros:**
- No network overhead
- Instant sync within same browser

**Cons:**
- ❌ Browser-only: Doesn't work across devices
- ❌ No persistence: Lost on browser clear
- ❌ Complex: Cross-tab messaging needed

**Decision:** Doesn't solve cross-device use case.

### Alternative 3: Manual "Resume Session" Button

**Pros:**
- ✅ Simple: No automatic sync complexity
- ✅ Explicit: User controls when to resume

**Cons:**
- ❌ Poor UX: Extra step, breaks flow
- ❌ Discovery: Users may not know session exists

**Decision:** Good fallback, but automatic sync is better UX.

---

## 14. Open Questions

1. **Extraction Profile Sync:**
   - Q: Should extraction profiles be synced automatically?
   - A: Yes, but defer to P1. Start with context/question sync only.

2. **Reading Position Sync:**
   - Q: Sync CFI position when question changes?
   - A: Yes, already part of existing `readingPosition` field.

3. **Conflict UI Feedback:**
   - Q: Show toast when remote state overrides local?
   - A: P1 nice-to-have. Start with silent reconciliation.

4. **Session Expiry:**
   - Q: When should sessions be marked stale?
   - A: After 24 hours inactive. Backend cleanup job.

---

## 15. Success Criteria

**P0 (MVP):**
- [ ] User selects context in Reader → SiYuan reflects change within 10 seconds
- [ ] User selects question in SiYuan → Reader reflects change within 10 seconds
- [ ] No conflicts when apps updated sequentially (debounced)
- [ ] Poll rate adjusts based on app focus (5s active, 30s inactive)

**P1 (Polish):**
- [ ] Sync indicator shows when state changes remotely
- [ ] Offline mode degrades gracefully (no errors shown)
- [ ] Extraction profiles sync automatically
- [ ] Session resume on app restart

**P2 (Future):**
- [ ] Real-time sync via WebSocket (if needed)
- [ ] Cross-device sync (mobile ↔ desktop)
- [ ] Collaborative sessions (multiple users)

---

## 16. References

**Related Docs:**
- `docs/GAP-ANALYSIS-2025-12-09.md` — Gap #4: Cross-App Continuity
- `ies/reader/src/store/flowStore.ts` — Reader state management
- `.worktrees/siyuan/ies/plugin/src/views/FlowMode.svelte` — SiYuan state
- `ies/reader/src/services/syncApi.ts` — Existing session sync

**Backend API:**
- `GET /session/{id}` — Fetch session state
- `PATCH /session/{id}` — Update session state
- `GET /session/user/{user_id}/active` — Get active sessions

---

*This design enables seamless exploration continuity across IES Reader and SiYuan plugin using lightweight polling with optimistic UI updates.*
