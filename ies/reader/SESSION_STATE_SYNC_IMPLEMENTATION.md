# Session State Sync Implementation - IES Reader

**Date:** 2025-12-09
**Status:** Complete

## Overview

Implemented cross-app continuity between IES Reader and SiYuan plugin by syncing session state (active context, question, and reading position) to the backend.

## Files Created

### 1. `src/services/sessionStateApi.ts` (156 lines)

TypeScript API client for `/session-state` backend endpoints.

**Exports:**
- `sessionStateApi` — Singleton instance
- `SessionStateApiClient` — Class for testing/custom instances
- Types: `SessionState`, `SessionStateUpdate`, `ReadingPosition`, `SessionStateHistory`, `HeartbeatResponse`, `SessionStateHistoryResponse`

**Methods:**
- `getState(userId)` — Get current session state
- `updateState(userId, update)` — Partial state update (null to clear fields)
- `heartbeat(userId)` — Update activity timestamp without full sync
- `getHistory(userId, limit?)` — Get session history for resume features

**API Base:** `VITE_API_URL` or `http://localhost:8081`

---

### 2. `src/hooks/useSessionSync.ts` (227 lines)

React hook for syncing context_id and question_id from flowStore to backend.

**Features:**
- Adaptive polling: 5s when active, 30s when backgrounded
- Write debouncing: 3 seconds to reduce API calls
- Visibility change handling: Immediate write on backgrounding, poll on foregrounding
- Independent heartbeat: 60s interval for activity tracking
- State comparison: Only syncs when values change

**Options:**
```typescript
interface UseSessionSyncOptions {
  userId?: string;              // default: 'default_user'
  enabled?: boolean;            // default: true
  activePollInterval?: number;  // default: 5000ms
  backgroundPollInterval?: number; // default: 30000ms
  writeDebounce?: number;       // default: 3000ms
}
```

**Returned Actions:**
- `writeState()` — Force immediate write
- `sendHeartbeat()` — Manual heartbeat

**Integration:**
- Watches `flowStore.currentContextId` and `flowStore.currentQuestionId`
- Updates local state when backend has different values (SiYuan changed them)
- Maintains `lastSyncedStateRef` to avoid redundant API calls

---

### 3. `src/hooks/useReadingPosition.ts` (183 lines)

React hook for tracking reading position via epub.js `relocated` event.

**Features:**
- Hooks into `rendition.on('relocated')` for position changes
- Debounces writes: 2 seconds to reduce API calls
- Immediate save on `window.blur` (user switching apps)
- Extracts comprehensive position data:
  - CFI (Canonical Fragment Identifier)
  - Chapter title (from TOC)
  - Page number (if available)
  - Progress percentage (0-100)
  - Timestamp

**Options:**
```typescript
interface UseReadingPositionOptions {
  rendition: Rendition | null;
  calibreId?: number;
  userId?: string;           // default: 'default_user'
  enabled?: boolean;         // default: true
  debounceMs?: number;       // default: 2000ms
}
```

**Returned Actions:**
- `getCurrentPosition()` — Extract current position on demand
- `writePosition(position)` — Manual position save

**Integration:**
- Calls `sessionStateApi.updateState(userId, { current_book: position })`
- Compatible with backend `ReadingPosition` schema

---

### 4. `src/components/Reader.tsx` (updated)

Wired up both hooks in the Reader component.

**Changes:**
- Added imports for `useSessionSync` and `useReadingPosition`
- Called `useSessionSync({ userId, enabled: true })` at component mount
- Called `useReadingPosition({ rendition, calibreId, userId, enabled: true })` when rendition is ready
- Both hooks run independently and handle their own sync logic

**Lines:**
- Line 12: Import `useSessionSync`
- Line 13: Import `useReadingPosition`
- Lines 108-112: Session sync hook invocation
- Lines 114-120: Reading position hook invocation

---

### 5. `src/services/index.ts` (updated)

Added sessionStateApi exports to services barrel.

**Exports:**
- `sessionStateApi`, `SessionStateApiClient`
- All session state types
- `ReadingPosition as SessionReadingPosition` (alias to avoid conflict with syncApi's ReadingPosition)

---

## Architecture

### Data Flow

```
User Interaction (Context/Question change in UI)
  ↓
flowStore (currentContextId, currentQuestionId)
  ↓
useSessionSync (watches store, debounces writes)
  ↓
sessionStateApi.updateState({ active_context_id, active_question_id })
  ↓
Backend /session-state/{user_id} (PATCH)
  ↓
PostgreSQL/In-Memory Store
  ↓
Poll interval (5s active / 30s background)
  ↓
sessionStateApi.getState()
  ↓
Update flowStore if values differ (SiYuan changed them)
```

```
epub.js rendition 'relocated' event
  ↓
useReadingPosition (extracts CFI, chapter, progress)
  ↓
Debounce 2s (or immediate on window.blur)
  ↓
sessionStateApi.updateState({ current_book: ReadingPosition })
  ↓
Backend /session-state/{user_id} (PATCH)
  ↓
PostgreSQL/In-Memory Store
```

### Polling Strategy

**Active (foreground):**
- Poll every 5 seconds
- Catch changes from SiYuan within 5s

**Backgrounded (tab hidden):**
- Poll every 30 seconds
- Reduce API load when user is not viewing reader
- Write any pending changes before backgrounding

**Heartbeat:**
- Independent 60s interval
- Keeps session alive without full sync
- Updates `last_activity_at` timestamp

### Debouncing Strategy

**Session state (context/question):**
- 3 second debounce
- Prevents rapid-fire API calls during question selection
- Immediate write on visibility change (backgrounding)

**Reading position (CFI):**
- 2 second debounce
- Prevents API calls on every page turn
- Immediate write on `window.blur` (user switching apps)

---

## Backend Integration

**Endpoint:** `GET/PATCH /session-state/{user_id}`

**Request Schema (PATCH):**
```json
{
  "active_context_id": "ctx_123" | null,
  "active_question_id": "q_456" | null,
  "current_book": {
    "calibre_id": 42,
    "cfi": "epubcfi(/6/4[chap01ref]!/4/2/1:0)",
    "chapter_title": "Chapter 1",
    "page_number": 15,
    "progress_percent": 12.5,
    "last_read_at": "2025-12-09T10:30:00Z"
  } | null
}
```

**Response Schema:**
```json
{
  "user_id": "default_user",
  "active_context_id": "ctx_123",
  "active_question_id": "q_456",
  "current_book": { ... },
  "last_activity_at": "2025-12-09T10:30:00Z",
  "created_at": "2025-12-09T09:00:00Z",
  "updated_at": "2025-12-09T10:30:00Z"
}
```

---

## Testing Notes

**Manual Testing Checklist:**

1. **Context Sync:**
   - Open IES Reader
   - Select a context in Flow Panel
   - Wait 3 seconds
   - Check backend: `GET /session-state/default_user`
   - Verify `active_context_id` matches

2. **Question Sync:**
   - Select a question in QuestionSelector
   - Wait 3 seconds
   - Check backend: verify `active_question_id`

3. **Reading Position:**
   - Turn pages in reader
   - Wait 2 seconds after stopping
   - Check backend: verify `current_book.cfi` updated
   - Verify `progress_percent` increases

4. **Backgrounding:**
   - Change context/question
   - Switch to another tab immediately (before 3s debounce)
   - Check backend: verify immediate write occurred

5. **Cross-App Continuity (with SiYuan):**
   - Open IES Reader with a context
   - Open SiYuan plugin, change to different context
   - Wait 5 seconds
   - Check IES Reader: flowStore should update to match SiYuan

6. **Heartbeat:**
   - Open IES Reader
   - Wait 60 seconds without interaction
   - Check backend: `last_activity_at` should update every 60s

---

## Performance Considerations

**API Call Frequency:**
- **Writes:** Max 1 per 3s (context/question), 1 per 2s (position)
- **Reads (polls):** 12 per minute (active), 2 per minute (background)
- **Heartbeats:** 1 per minute
- **Total (active):** ~15-20 API calls/minute per user

**Optimizations:**
- State comparison prevents redundant writes
- Debouncing reduces write frequency
- Adaptive polling saves API calls when backgrounded
- Heartbeat uses lightweight POST endpoint

**Network Impact:**
- Average request size: ~500 bytes (JSON)
- Average response size: ~800 bytes
- Bandwidth: ~20 KB/minute per active user

---

## Known Limitations

1. **User ID Hardcoded:** Currently uses `userId || 'default_user'`. Multi-user support requires proper authentication.

2. **Conflict Resolution:** If both Reader and SiYuan change state simultaneously, last write wins. No CRDT or OT strategy.

3. **Offline Support:** Hooks are disabled when backend is unreachable. No offline queue for session state (unlike highlights).

4. **Poll Delay:** Changes from SiYuan take up to 5s to appear in Reader (poll interval). Real-time sync would require WebSockets.

5. **Chapter Detection:** Chapter title extraction depends on epub.js TOC parsing. May fail for malformed EPUB files.

---

## Future Enhancements

1. **WebSocket Integration:** Real-time sync instead of polling (would eliminate 5s delay).

2. **Conflict Resolution:** Operational Transform or CRDT for simultaneous edits.

3. **Offline Queue:** Store state changes in IndexedDB when offline, sync on reconnect.

4. **User Authentication:** Replace `default_user` with actual user IDs from auth system.

5. **Progressive Enhancement:** Gracefully degrade to local-only mode if backend is down.

6. **Analytics:** Track session duration, reading speed, navigation patterns for insights.

---

## Dependencies

**Runtime:**
- `zustand` — flowStore state management
- `epubjs` — epub.js Rendition type and events
- `react` — useEffect, useCallback, useRef hooks

**Types:**
- Backend schemas from `ies/backend/src/ies_backend/schemas/session_state.py`
- Aligned with SessionState, ReadingPosition, SessionStateUpdate

**Dev:**
- TypeScript 5.x
- ESLint (follows existing IES Reader config)

---

## Related Files

**Backend:**
- `ies/backend/src/ies_backend/api/session_state.py` — API endpoints
- `ies/backend/src/ies_backend/schemas/session_state.py` — Schemas
- `ies/backend/src/ies_backend/services/session_state_service.py` — Service layer

**Frontend (existing):**
- `ies/reader/src/store/flowStore.ts` — Context/question state
- `ies/reader/src/services/contextApi.ts` — Context API client (pattern reference)
- `ies/reader/src/services/questionApi.ts` — Question API client (pattern reference)

**Documentation:**
- `docs/IES-SYSTEM-DESIGN.md` — Ground truth (session management section)
- `docs/ARCHITECTURE-AND-INTERACTIONS.md` — Cross-app continuity design
- `docs/GAP-ANALYSIS-2025-12-09.md` — Implementation status tracking
