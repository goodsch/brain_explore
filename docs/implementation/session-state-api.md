# Session State API - Implementation Plan

**Created:** 2025-12-09
**Status:** Design Complete, Ready for Integration
**Purpose:** Cross-app session continuity between IES Reader and SiYuan plugin

---

## Overview

The Session State API tracks active session state (context, question, reading position) across IES frontends to enable seamless transitions. Users can start reading in IES Reader, switch to SiYuan for exploration, then return to IES Reader at the same position.

## Files Created

### 1. Schemas (`ies/backend/src/ies_backend/schemas/session_state.py`)

**Models:**
- `ReadingPosition` - CFI-based reading position with calibre_id, cfi, chapter, progress
- `SessionState` - Active session with user_id, active_context_id, active_question_id, current_book, timestamps
- `SessionStateUpdate` - Partial update schema (all fields optional)
- `SessionStateHistory` - Historical state snapshot with change_type tracking
- `HeartbeatRequest/Response` - Keep-alive mechanism
- `SessionStateHistoryResponse` - List of historical states

**Key Features:**
- All timestamps are datetime (UTC)
- Supports null values to clear fields
- CFI (Canonical Fragment Identifier) for EPUB position tracking
- Change type tracking: context_opened, question_selected, book_opened, reading_progress, session_ended

### 2. Service (`ies/backend/src/ies_backend/services/session_state_service.py`)

**Class:** `SessionStateService`

**Storage:**
- In-memory MVP: `dict[user_id, SessionState]`
- History storage: `dict[user_id, list[SessionStateHistory]]` (newest first)
- Migration path: Redis for production (multi-instance support + persistence)

**Methods:**
- `get_state(user_id)` - Get current session state
- `update_state(user_id, update)` - Partial state update with history tracking
- `heartbeat(request)` - Update last_activity_at without changing state
- `get_history(user_id, limit)` - Get recent state changes
- `clear_state(user_id)` - Clear session (records session_ended to history)
- `is_session_active(user_id)` - Check if session is within timeout window
- `_record_history(...)` - Internal: Record state change to history

**Configuration:**
- `SESSION_TIMEOUT = 30 minutes` - Session considered inactive after this
- `MAX_HISTORY_PER_USER = 100` - Trim history beyond this

**History Tracking:**
- Records change_type on every state update
- Trims history to MAX_HISTORY_PER_USER (keeps newest)
- Enables "Resume where you left off" features

### 3. Router (`ies/backend/src/ies_backend/api/session_state.py`)

**Endpoints:**

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/session-state/{user_id}` | Get current state |
| PATCH | `/session-state/{user_id}` | Update partial state |
| POST | `/session-state/{user_id}/heartbeat` | Update last_activity_at |
| GET | `/session-state/{user_id}/history` | Get recent state changes |
| DELETE | `/session-state/{user_id}` | Clear session state |
| GET | `/session-state/{user_id}/is-active` | Check if session active |

**Prefix:** `/session-state`
**Tags:** `["session_state"]`

---

## Integration Steps

### Backend Integration

1. **Register router in main.py**
   ```python
   from .api.session_state import router as session_state_router
   app.include_router(session_state_router, prefix="")
   ```

2. **Export schemas**
   Add to `ies/backend/src/ies_backend/schemas/__init__.py`:
   ```python
   from .session_state import (
       SessionState,
       SessionStateUpdate,
       ReadingPosition,
       SessionStateHistory,
       SessionStateHistoryResponse,
       HeartbeatRequest,
       HeartbeatResponse,
   )
   ```

3. **Verify OpenAPI docs**
   - Start backend: `cd ies/backend && uv run uvicorn ies_backend.main:app --reload --port 8081`
   - Visit: http://localhost:8081/docs
   - Check `/session-state` endpoints appear

### IES Reader Integration

**File:** `ies/reader/src/services/sessionStateApi.ts`

```typescript
export interface ReadingPosition {
  calibre_id: number;
  cfi: string;
  chapter_title?: string;
  page_number?: number;
  progress_percent?: number;
  last_read_at: string; // ISO timestamp
}

export interface SessionState {
  user_id: string;
  active_context_id?: string;
  active_question_id?: string;
  current_book?: ReadingPosition;
  last_activity_at: string;
  created_at: string;
  updated_at: string;
}

export class SessionStateApiClient {
  private baseURL = 'http://localhost:8081';

  async getState(userId: string = 'default_user'): Promise<SessionState | null> {
    const res = await fetch(`${this.baseURL}/session-state/${userId}`);
    if (res.status === 404) return null;
    return res.json();
  }

  async updateState(userId: string, update: Partial<SessionState>): Promise<SessionState> {
    const res = await fetch(`${this.baseURL}/session-state/${userId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(update),
    });
    return res.json();
  }

  async heartbeat(userId: string): Promise<void> {
    await fetch(`${this.baseURL}/session-state/${userId}/heartbeat`, {
      method: 'POST',
    });
  }

  async getHistory(userId: string, limit: number = 20) {
    const res = await fetch(`${this.baseURL}/session-state/${userId}/history?limit=${limit}`);
    return res.json();
  }
}

export const sessionStateApi = new SessionStateApiClient();
```

**Integration Points:**

1. **Reader.tsx** - Update reading position on page turn:
   ```typescript
   useEffect(() => {
     if (rendition) {
       rendition.on('relocated', (location) => {
         sessionStateApi.updateState('default_user', {
           current_book: {
             calibre_id: currentBook.calibreId,
             cfi: location.start.cfi,
             chapter_title: location.chapter?.label,
             progress_percent: location.start.percentage * 100,
             last_read_at: new Date().toISOString(),
           }
         });
       });
     }
   }, [rendition, currentBook]);
   ```

2. **flowStore.ts** - Update active context/question:
   ```typescript
   setActiveContext: (contextId: string) => {
     set({ activeContext: contextId });
     sessionStateApi.updateState('default_user', {
       active_context_id: contextId,
     });
   },

   setActiveQuestion: (questionId: string) => {
     set({ activeQuestion: questionId });
     sessionStateApi.updateState('default_user', {
       active_question_id: questionId,
     });
   },
   ```

3. **App startup** - Restore session state:
   ```typescript
   useEffect(() => {
     sessionStateApi.getState('default_user').then(state => {
       if (state?.current_book) {
         // Restore reading position
         openBook(state.current_book.calibre_id, state.current_book.cfi);
       }
       if (state?.active_context_id) {
         flowStore.setActiveContext(state.active_context_id);
       }
     });
   }, []);
   ```

4. **Heartbeat interval** - Keep session alive:
   ```typescript
   useEffect(() => {
     const interval = setInterval(() => {
       sessionStateApi.heartbeat('default_user');
     }, 5 * 60 * 1000); // Every 5 minutes
     return () => clearInterval(interval);
   }, []);
   ```

### SiYuan Plugin Integration

**File:** `.worktrees/siyuan/ies/plugin/src/services/sessionStateApi.ts`

```typescript
import { apiGet, apiPatch, apiPost } from '../utils/api';

export const SessionStateApi = {
  async getState(userId: string = 'default_user') {
    return apiGet(`/session-state/${userId}`);
  },

  async updateState(userId: string, update: any) {
    return apiPatch(`/session-state/${userId}`, update);
  },

  async heartbeat(userId: string = 'default_user') {
    return apiPost(`/session-state/${userId}/heartbeat`, {});
  },

  async getHistory(userId: string, limit: number = 20) {
    return apiGet(`/session-state/${userId}/history?limit=${limit}`);
  },
};
```

**Integration Points:**

1. **FlowMode.svelte** - Update active context when Context Mode opens:
   ```typescript
   async function enterContextMode(contextId: string) {
     await SessionStateApi.updateState('default_user', {
       active_context_id: contextId,
     });
     // ... existing context mode logic
   }
   ```

2. **Dashboard.svelte** - Show "Resume where you left off":
   ```typescript
   let sessionState = null;

   onMount(async () => {
     sessionState = await SessionStateApi.getState('default_user');
     if (sessionState?.current_book) {
       // Show "Resume reading" button
     }
   });
   ```

---

## Testing Strategy

### Unit Tests

**File:** `ies/backend/tests/test_session_state_service.py`

Test cases:
1. `test_create_new_session_state` - First state creation
2. `test_update_context` - Update active context
3. `test_update_reading_position` - Update reading position
4. `test_heartbeat_creates_session` - Heartbeat on first call
5. `test_heartbeat_updates_timestamp` - Heartbeat updates last_activity_at
6. `test_session_timeout` - Session inactive after 30 minutes
7. `test_history_tracking` - State changes recorded to history
8. `test_history_limit` - History trimmed to MAX_HISTORY_PER_USER
9. `test_clear_state` - Clear state records session_ended
10. `test_multiple_users` - Isolated state per user

### Integration Tests

**File:** `ies/backend/tests/test_session_state_api.py`

Test cases:
1. `test_get_state_404_when_no_session` - GET returns 404 initially
2. `test_patch_creates_session` - PATCH creates state if missing
3. `test_patch_updates_context` - PATCH updates context_id
4. `test_heartbeat_endpoint` - POST heartbeat works
5. `test_history_endpoint` - GET history returns changes
6. `test_delete_clears_state` - DELETE clears state

### End-to-End Tests

**Scenario 1: IES Reader → SiYuan continuity**
1. Open book in IES Reader (calibre_id=42, cfi=X)
2. Reader updates session state via PATCH
3. Open SiYuan plugin
4. SiYuan fetches session state via GET
5. SiYuan shows "Resume reading: Book Title (Chapter 3)"
6. Click "Resume" → Opens IES Reader at exact CFI position

**Scenario 2: Context exploration continuity**
1. Open context in SiYuan (context_id=ctx_abc)
2. SiYuan updates session state via PATCH
3. Open IES Reader
4. Reader fetches session state via GET
5. Reader shows Flow Panel with active context
6. Select question in Reader
7. Reader updates session state via PATCH
8. Switch back to SiYuan
9. SiYuan fetches updated state → Shows active question

---

## Migration to Redis

**When:** After MVP validation, before multi-user deployment

**Redis Schema:**
```
session:state:{user_id} -> JSON(SessionState)
session:history:{user_id} -> LIST[JSON(SessionStateHistory)] (LPUSH, LTRIM)
```

**Service Changes:**
- Replace `self._states` dict with Redis hash operations
- Replace `self._history` dict with Redis list operations
- Add Redis client dependency injection
- Keep same service interface (no API changes needed)

**Benefits:**
- Persistence across backend restarts
- Multi-instance support (load balancing)
- Automatic TTL for inactive sessions
- Pub/Sub for real-time session updates

---

## Success Criteria

1. ✅ **Schemas defined** - ReadingPosition, SessionState, Update, History schemas
2. ✅ **Service implemented** - In-memory storage with history tracking
3. ✅ **API endpoints created** - GET, PATCH, POST heartbeat, GET history, DELETE
4. ⏳ **Router registered** - Added to main.py
5. ⏳ **Tests passing** - Unit + integration tests
6. ⏳ **Reader integration** - CFI position sync
7. ⏳ **SiYuan integration** - Context/question sync
8. ⏳ **End-to-end validation** - Cross-app continuity works

---

## Next Steps

1. Register router in `ies/backend/src/ies_backend/main.py`
2. Export schemas in `ies/backend/src/ies_backend/schemas/__init__.py`
3. Write unit tests (`test_session_state_service.py`)
4. Write integration tests (`test_session_state_api.py`)
5. Create IES Reader TypeScript client
6. Integrate Reader position tracking
7. Create SiYuan TypeScript client
8. Integrate SiYuan context tracking
9. Test end-to-end workflows
10. Document in CHANGELOG.md

---

## Related Documentation

- **GAP-ANALYSIS.md** - Cross-App Continuity gap (now addressed)
- **IES-SYSTEM-DESIGN.md** - Cross-app interaction patterns
- **ARCHITECTURE-AND-INTERACTIONS.md** - Session management architecture
- **Reader CFI tracking** - `ies/reader/src/components/Reader.tsx`
- **SiYuan Context Mode** - `.worktrees/siyuan/ies/plugin/src/views/FlowMode.svelte`
