# Cross-App User Journey Analysis: IES Reader ↔ SiYuan Plugin

**Analysis Date:** December 9, 2025
**Analyst:** Senior Technical Auditor
**Components Reviewed:**
- Backend: `/ies/backend/src/ies_backend/api/session_state.py`
- Backend: `/ies/backend/src/ies_backend/services/session_state_service.py`
- Backend: `/ies/backend/src/ies_backend/schemas/session_state.py`
- Reader: `/ies/reader/src/hooks/useSessionSync.ts`
- SiYuan: `/.worktrees/siyuan/ies/plugin/src/services/ContextSyncService.ts`

---

## Executive Summary

The cross-app session sync implementation is **architecturally sound but operationally immature**. The technical foundation for seamless Reader ↔ SiYuan handoff exists, but critical UX gaps create confusion, data loss risks, and poor user experience during app transitions.

**Critical Finding:** Users have no visibility into sync status, conflict resolution, or session ownership. The system operates entirely behind the scenes with no error recovery UI, leading to silent failures when network issues occur.

---

## State Transfer Matrix

| State Field | Reader → SiYuan | SiYuan → Reader | Latency | Persistence | Evidence |
|-------------|-----------------|-----------------|---------|-------------|----------|
| **active_context_id** | ✅ Full | ✅ Full | 5-30s | 24h Redis | Both apps poll/push this field |
| **active_question_id** | ✅ Full | ✅ Full | 5-30s | 24h Redis | Both apps poll/push this field |
| **current_book** | ✅ Full (CFI) | 🟡 Read-only | 5-30s | 24h Redis | Reader writes, SiYuan reads only |
| **current_entity_id** | 🟡 Via trail | 🟡 Via trail | 5-30s | 24h Redis | Indirect, set by journey trail |
| **current_entity_name** | 🟡 Via trail | 🟡 Via trail | 5-30s | 24h Redis | Indirect, set by journey trail |
| **journey_trail** | 🔴 Read-only | ✅ Full write | 5-30s | 24h Redis | **ASYMMETRIC: Reader can't write trail** |
| **last_app_source** | ✅ Full | ✅ Full | 5-30s | 24h Redis | Set by `add_trail_item.source_app` |
| **last_activity_at** | ✅ Heartbeat | ✅ Heartbeat | 5-30s | 24h Redis | Both apps send heartbeats (60s interval) |

### 🔴 Critical State Transfer Gaps

1. **Journey Trail Asymmetry:**
   - **Problem:** Reader can ONLY read journey trail, cannot write. SiYuan is sole writer.
   - **Evidence:** `useSessionSync.ts` line 123-129 reads `remoteTrail` and calls `setJourneyTrail()`, but has no write logic.
   - **Impact:** Reader entity visits are invisible to SiYuan unless manually added via `addEntityVisit()`.
   - **Location:** Reader calls `addEntityVisit()` at line 174-206, but this is NOT automatic—requires manual UI trigger.

2. **Reading Position Isolation:**
   - **Problem:** SiYuan cannot update `current_book` field. Reader position is write-only from Reader.
   - **Evidence:** `ContextSyncService.ts` has no code to update `current_book`.
   - **Impact:** SiYuan can't suggest "return to reading at this passage" because it can't write reading positions.

3. **Entity Focus Ambiguity:**
   - **Problem:** `current_entity_id` is set ONLY via `add_trail_item`, not via direct field updates.
   - **Evidence:** `session_state_service.py` lines 165-168: "Set the entity tracking automatically" when trail item added.
   - **Impact:** If Reader focuses on entity WITHOUT adding trail item, SiYuan won't know about it.

---

## Journey 1: Reader → SiYuan (Continue Exploration)

**User Scenario:** User is reading a book, highlights an entity, wants to explore relationships in SiYuan.

| Step | User Expectation | Actual Behavior | Gap/Friction | Severity |
|------|------------------|-----------------|--------------|----------|
| 1. Highlight entity in Reader | Entity name highlights, clickable | ✅ Works (entity overlay feature) | None | - |
| 2. Click entity → Flow Panel opens | See entity name, type, description | ✅ Works (FlowPanel.tsx) | None | - |
| 3. Explore relationships in Reader | See related entities, sources | ✅ Works (RelationshipsSection.tsx) | None | - |
| 4. User thinks: "I want deeper exploration in SiYuan" | Open SiYuan, see SAME entity automatically | 🔴 NO TRANSFER—SiYuan shows nothing | **Reader doesn't write entity focus to backend** | 🔴 CRITICAL |
| 5. User manually searches for entity in SiYuan | Type entity name in search | ✅ Works (but loses context) | Tedious manual re-entry | 🟡 MEDIUM |
| 6. User opens entity in SiYuan Flow Mode | See relationships, trail | 🟡 Trail is EMPTY (Reader didn't write it) | Lost exploration context | 🟠 HIGH |

### Root Cause Analysis

**Why Reader entity clicks don't transfer to SiYuan:**

1. **No automatic trail writing:** `useSessionSync.ts` provides `addEntityVisit()` function (line 174-206) but **nothing calls it automatically**.
2. **Missing FlowPanel integration:** `FlowPanel.tsx` and entity components have no code to call `addEntityVisit()` when user clicks entity.
3. **Manual intervention required:** Developer must wire up `addEntityVisit()` to every entity click event—this was not done.

**Evidence:**
- `useSessionSync.ts` line 174: `const addEntityVisit = useCallback(async (entityId, entityName, options) => { ... })`
- No references to this function in `FlowPanel.tsx`, `EntitySection.tsx`, or `RelationshipsSection.tsx`.
- Journey trail remains empty because no component adds to it.

---

## Journey 2: SiYuan → Reader (Dive Into Source)

**User Scenario:** User is exploring entity in SiYuan Flow Mode, wants to read original passage in book.

| Step | User Expectation | Actual Behavior | Gap/Friction | Severity |
|------|------------------|-----------------|--------------|----------|
| 1. User clicks entity in SiYuan Flow Mode | Entity details panel opens | ✅ Works | None | - |
| 2. User sees "Sources" section with book titles | Click book title to jump to passage | 🔴 NO DEEP LINK—No way to open Reader at this location | **Deep links not implemented** | 🔴 CRITICAL |
| 3. User manually opens Reader | Reader opens to library or last position | 🟡 Wrong book, wrong position | Lost source context | 🟠 HIGH |
| 4. User searches for entity in Reader | Highlight entity, find passage | 🟡 Tedious, error-prone | Manual hunt for needle in haystack | 🟡 MEDIUM |
| 5. User wishes: "Why can't SiYuan just OPEN the passage?" | Deep link like `reader://calibreId=42&entity=concept_123` | 🔴 Not implemented | **No URL scheme handler** | 🔴 CRITICAL |

### Root Cause Analysis

**Why SiYuan can't deep-link to Reader:**

1. **No URL scheme:** Reader has no `reader://` protocol handler or query parameter parsing for entity focus.
2. **No "Open in Reader" UI:** SiYuan sources section shows book titles but no clickable action to open Reader.
3. **Backend provides deep links but UIs don't use them:** `GET /session-state/{user_id}/continue` returns `reader_deep_link` and `siyuan_deep_link` (lines 419-449) but **neither frontend implements deep link handling**.

**Evidence:**
- `session_state_service.py` lines 428-440 generate `reader_deep_link` with calibreId, entity, and CFI.
- No code in Reader to parse URL params and focus entity on load.
- No code in SiYuan to render "Open in Reader" buttons using deep links.

---

## Journey 3: Parallel Usage (Both Apps Open)

**User Scenario:** User has Reader on left screen, SiYuan on right screen, switching between reading and exploration.

| Step | User Expectation | Actual Behavior | Gap/Friction | Severity |
|------|------------------|-----------------|--------------|----------|
| 1. Change context in SiYuan | Reader sees new context within 5s | 🟡 Works BUT no visual feedback | Silent update, user unaware | 🟡 MEDIUM |
| 2. Change question in Reader | SiYuan sees new question within 5s | 🟡 Works BUT no visual feedback | Silent update, user unaware | 🟡 MEDIUM |
| 3. Both apps update same field simultaneously | Last-write-wins (race condition) | 🔴 CONFLICT—One app's change silently overwritten | **No conflict UI** | 🔴 CRITICAL |
| 4. Network interruption | Sync stops silently | 🔴 NO ERROR MESSAGE—Apps drift out of sync | **No connection indicator** | 🔴 CRITICAL |
| 5. User makes changes in Reader while offline | User expects sync when reconnected | 🔴 LOST—Changes from 3s debounce window are dropped | **No retry on network restore** | 🟠 HIGH |
| 6. User switches tabs (Reader backgrounded) | Poll interval slows to 30s | ✅ Works (battery optimization) | None, but no user feedback | 🟢 LOW |

### Root Cause Analysis

**Why parallel usage has conflicts and silent failures:**

1. **No sync status indicator:** Neither app shows "Syncing", "Synced", "Offline", or "Conflict" states.
2. **No conflict resolution UI:** Last-write-wins is implemented (lines 140-142 in ContextSyncService: "if remoteTimestamp > lastSyncTimestamp") but user has no way to see or resolve conflicts.
3. **No retry logic:** Both `useSessionSync.ts` and `ContextSyncService.ts` log errors to console but don't retry or queue writes.
4. **No offline queue:** When `writeState()` fails (line 78 in useSessionSync), the change is lost forever.

**Evidence:**
- `useSessionSync.ts` line 78: `console.error('[useSessionSync] Failed to write state:', error);` — No retry.
- `ContextSyncService.ts` line 152: `this.syncError = err instanceof Error ? err.message : 'Unknown sync error';` — Stored but never displayed.
- No UI components subscribe to `syncError` state.

---

## Journey 4: Session Handoff (Morning → Evening)

**User Scenario:** User explores in morning (both apps), closes everything, returns 8 hours later.

| Step | User Expectation | Actual Behavior | Gap/Friction | Severity |
|------|------------------|-----------------|--------------|----------|
| 1. User closes Reader and SiYuan at 9am | Session saved automatically | ✅ Works (Redis persistence, 24h TTL) | None | - |
| 2. User returns at 5pm (8 hours later) | "Resume where you left off" prompt | 🔴 NO RESUME UI—Apps open to default state | **No continuation widget** | 🔴 CRITICAL |
| 3. User manually opens last context | Search for context name | 🟡 Works but tedious | No recent activity list | 🟡 MEDIUM |
| 4. User wonders: "Where was I?" | Timeline of morning's exploration | 🔴 NO TIMELINE UI—History exists in backend but not shown | **`GET /session-state/{user_id}/history` unused** | 🟠 HIGH |
| 5. User wants to know primary app | See "Last active in SiYuan at 8:47am" | 🟡 Backend tracks `last_app_source` but UI doesn't show it | Hidden metadata | 🟡 MEDIUM |
| 6. Session times out after 30min inactivity | User expects session to persist | ✅ Works (30min timeout, 24h TTL) | None, but no timeout warning | 🟢 LOW |

### Root Cause Analysis

**Why session handoff has no UX:**

1. **Backend has full continuation API but UIs don't use it:** `GET /session-state/{user_id}/continue` (line 164-190 in API) returns:
   - `has_active_exploration: bool`
   - `current_entity_id/name`
   - `journey_trail` (last 10 items)
   - `reader_deep_link` and `siyuan_deep_link`
   - `resume_hint` (human-readable string)
   - **NONE of this data is rendered in either UI.**

2. **No "Resume Exploration" widget:** Neither Reader nor SiYuan checks for active session on startup.

3. **No timeline view:** `GET /session-state/{user_id}/history` (line 120-138 in API) returns:
   - List of `SessionStateHistory` with `change_type`, `timestamp`, `context_id`, `question_id`, `book_position`
   - **No UI component consumes this endpoint.**

**Evidence:**
- `session_state.py` line 164: `@router.get("/{user_id}/continue", response_model=ContinueExplorationResponse)`
- No references to `/continue` endpoint in Reader or SiYuan code.
- No references to `/history` endpoint in Reader or SiYuan code.

---

## Journey 5: Error Recovery

**User Scenario:** Reader loses backend connection mid-session.

| Step | User Expectation | Actual Behavior | Gap/Friction | Severity |
|------|------------------|-----------------|--------------|----------|
| 1. Backend goes down (port 8081 unreachable) | Visual indicator: "Offline" | 🔴 NOTHING—App appears normal | Silent failure | 🔴 CRITICAL |
| 2. User changes context in Reader | Change saved locally, synced when reconnected | 🔴 LOST—No local cache, no retry queue | **Data loss** | 🔴 CRITICAL |
| 3. User switches to SiYuan | SiYuan shows stale state from last successful poll | 🔴 NO INDICATOR—User thinks state is current | Operates on stale data | 🔴 CRITICAL |
| 4. Backend comes back online | Automatic reconnection and sync | 🟡 Sync resumes BUT no recovery of lost changes | Partial recovery | 🟠 HIGH |
| 5. User wonders: "Did my changes save?" | Confirmation message or sync history | 🔴 NO FEEDBACK—User has no way to know | Uncertainty, distrust | 🟠 HIGH |
| 6. User manually refreshes page | State restored from backend | ✅ Works (if backend was never down) | None for this step | - |

### Root Cause Analysis

**Why error recovery fails catastrophically:**

1. **No connection state tracking:** Neither `useSessionSync.ts` nor `ContextSyncService.ts` tracks online/offline status.
2. **No local persistence:** Changes are written directly to backend with no localStorage/IndexedDB fallback.
3. **No retry queue:** Failed writes are logged but not queued for retry.
4. **No error UI:** Both services set `syncError` state but no components display it.

**Evidence:**
- `useSessionSync.ts` line 78: `console.error('[useSessionSync] Failed to write state:', error);` — Logs but doesn't retry.
- `ContextSyncService.ts` line 152-154: Sets `this.syncError` but never renders it.
- No `navigator.onLine` checks or retry timers.

---

## Journey 6: Journey Trail Continuity

**User Scenario:** User visits Entity A (Reader) → Entity B (SiYuan) → Entity C (Reader), wants to see full cross-app trail.

| Step | User Expectation | Actual Behavior | Gap/Friction | Severity |
|------|------------------|-----------------|--------------|----------|
| 1. Click Entity A in Reader | Entity A added to trail | 🔴 NOT AUTOMATIC—Developer must call `addEntityVisit()` manually | **No auto-tracking** | 🔴 CRITICAL |
| 2. Open SiYuan, click Entity B | Entity B added to trail | ✅ Works (ContextSyncService.addEntityVisit, line 347-380) | None IF manually called | 🟡 MEDIUM |
| 3. Return to Reader, click Entity C | Entity C added to trail | 🔴 NOT AUTOMATIC—Same problem as step 1 | **No auto-tracking** | 🔴 CRITICAL |
| 4. View trail in SiYuan | See [Entity C, Entity B, Entity A] (newest first) | 🔴 EMPTY or incomplete—Reader visits missing | Lost cross-app context | 🔴 CRITICAL |
| 5. Click trail item to navigate back | Jump to that entity | 🔴 NO UI—Trail exists in state but not rendered | **No breadcrumb component** | 🔴 CRITICAL |
| 6. View trail in Reader | See same [Entity C, Entity B, Entity A] | 🔴 Trail read-only in Reader, no navigation UI | **Asymmetric feature** | 🟠 HIGH |

### Root Cause Analysis

**Why journey trail is broken:**

1. **Manual tracking in Reader:** `useSessionSync.ts` provides `addEntityVisit()` but no component calls it automatically.
   - **Location:** FlowPanel needs to call `addEntityVisit()` when entity is opened.
   - **Missing code:** `FlowPanel.tsx` line ~200 needs: `sessionSync.addEntityVisit(entityId, entityName, { entityType, dwellSeconds })`

2. **No trail UI in either app:**
   - **Backend provides trail:** `SessionState.journey_trail` is populated (line 86-93 in schema).
   - **SiYuan reads trail:** `ContextSyncService.ts` line 189-191 syncs `journey_trail` to local state.
   - **Reader reads trail:** `useSessionSync.ts` line 124-129 syncs `journey_trail` to flowStore.
   - **NO UI COMPONENT RENDERS IT.**

3. **No dwell time tracking:** Backend supports `dwell_seconds` (line 32 in schema) but no frontend tracks how long user focused on entity.

**Evidence:**
- `JourneyTrailItem` schema (line 20-34) has `dwell_seconds` field.
- No timer logic in FlowPanel or ContextSyncService to track focus duration.
- No breadcrumb component in either app.

---

## State Transfer Latency Analysis

### Polling Intervals

| Condition | Reader | SiYuan | Analysis |
|-----------|--------|--------|----------|
| App visible/active | 5s | 5s | ✅ Reasonable for real-time feel |
| App backgrounded | 30s | 30s | ✅ Battery optimization, acceptable lag |
| Heartbeat interval | 60s | N/A | ✅ Keeps session alive, prevents 30min timeout |

### Write Debounce

| App | Debounce | Analysis |
|-----|----------|----------|
| Reader | 3s | ✅ Reduces API calls, acceptable for context/question changes |
| SiYuan | Immediate push | 🟡 More aggressive, could cause write storms |

### Observed Latency Scenarios

1. **Best case (both apps visible, no debounce):**
   - SiYuan changes context → 0s write → Reader polls within 5s → **5s total lag**
   - ✅ Acceptable for cross-app coordination.

2. **Worst case (Reader backgrounded, debounce active):**
   - Reader changes context → 3s debounce → Write → SiYuan polls 30s later → **33s total lag**
   - 🟡 Acceptable for background sync, but user expects instant sync if both apps visible.

3. **Conflict case (simultaneous writes):**
   - Reader writes at T=0s → SiYuan writes at T=1s → Last write wins (SiYuan)
   - 🔴 Reader's change silently overwritten, no conflict UI.

---

## Data Loss Scenarios

### 🔴 CRITICAL: Network Interruption During Debounce Window

**Scenario:**
1. User changes context in Reader at T=0s
2. Debounce timer starts (3s)
3. Network fails at T=1s
4. Debounce fires at T=3s → Write fails → **Change lost forever**

**Evidence:**
- `useSessionSync.ts` line 77-79: `await sessionStateApi.updateState(userId, update);` catches error but doesn't retry.
- No localStorage backup.
- No write queue.

**Impact:** User loses work silently.

### 🔴 CRITICAL: Session Timeout Without Warning

**Scenario:**
1. User reads for 25 minutes (no entity clicks, no context changes)
2. Heartbeat sent at 20min, 21min, ... 29min (every 60s)
3. User idle for 30 minutes → Session times out
4. User returns, makes changes → **New session created, old journey trail lost**

**Evidence:**
- `session_state_service.py` line 39: `SESSION_TIMEOUT = timedelta(minutes=30)`
- No UI warning at 25min ("Session will expire in 5 minutes")
- Heartbeat keeps session alive (line 195-237) but only if user is actively using app.

**Impact:** Lost exploration context after timeout.

### 🟠 HIGH: Race Condition During Simultaneous Updates

**Scenario:**
1. Reader and SiYuan both polling at 5s intervals
2. User changes context in Reader at T=0s → Write starts
3. User changes question in SiYuan at T=0.5s → Write starts
4. Reader write completes at T=1s (context updated)
5. SiYuan write completes at T=1.5s → **Overwrites context with old value**

**Evidence:**
- `session_state_service.py` line 129-132: Updates are applied independently, not merged atomically.
- Last write wins, no version vectors or CRDTs.

**Impact:** Silently loses user's context change from Reader.

---

## Synchronization Feedback Analysis

### Current Feedback (What Users See)

| Event | Reader Feedback | SiYuan Feedback | Severity |
|-------|----------------|-----------------|----------|
| Sync in progress | NONE | NONE | 🔴 CRITICAL |
| Sync succeeded | NONE | NONE | 🔴 CRITICAL |
| Sync failed | NONE (logs to console) | NONE (logs to console) | 🔴 CRITICAL |
| Conflict occurred | NONE | NONE | 🔴 CRITICAL |
| Network offline | NONE | NONE | 🔴 CRITICAL |
| Session timeout approaching | NONE | NONE | 🟠 HIGH |

### Available Backend Data (Not Used)

Both services track sync state but don't expose it to UI:

**Reader (`useSessionSync.ts`):**
- No `isSyncing` state exported
- No `lastSyncError` state exported
- No `lastSyncTimestamp` state exported

**SiYuan (`ContextSyncService.ts`):**
- `isSyncing: boolean` exists (line 55)
- `syncError: string | null` exists (line 56)
- `lastSyncedAt: number` exists (line 299)
- **But no UI components subscribe to this state**

**Evidence:**
- `ContextSyncService.ts` line 288-301: `getState()` returns full sync state.
- No `<SyncStatusIndicator />` component exists.

---

## Reliability Assessment

### What Works Well ✅

1. **Redis persistence:** 24h TTL ensures sessions survive app restarts.
2. **Heartbeat mechanism:** 60s heartbeat prevents premature timeouts.
3. **Visibility-based polling:** Battery optimization (5s active, 30s background).
4. **Field-level updates:** Partial updates work correctly (`PATCH` with only changed fields).
5. **Journey trail max length:** 50-item cap prevents unbounded growth.
6. **CFI-based reading positions:** Precise EPUB location tracking.

### What Fails ❌

1. **No sync status UI:** Users operate blind.
2. **No conflict resolution:** Last-write-wins is silent and lossy.
3. **No error recovery:** Network failures = data loss.
4. **No offline queue:** Changes made while offline are lost.
5. **No deep linking:** Can't jump between apps to specific entities/books.
6. **No journey trail UI:** Exists in backend but invisible to users.
7. **No automatic entity tracking:** Developer must manually wire up `addEntityVisit()`.

---

## Critical Sync Gaps Summary

### 🔴 CRITICAL (Blocks Real-World Use)

1. **No sync status indicator**
   - **Impact:** Users can't tell if changes saved or if apps are out of sync.
   - **Location:** Both apps need `<SyncStatusBadge>` component.

2. **No error recovery UI**
   - **Impact:** Network failures cause silent data loss.
   - **Location:** Need retry queue and offline mode handling.

3. **No deep linking**
   - **Impact:** Can't seamlessly jump between apps to continue exploration.
   - **Location:** Reader needs URL param parsing, SiYuan needs "Open in Reader" buttons.

4. **Journey trail not auto-tracked in Reader**
   - **Impact:** Cross-app exploration trail is incomplete.
   - **Location:** `FlowPanel.tsx` needs to call `addEntityVisit()` on entity focus.

5. **No journey trail UI**
   - **Impact:** Users can't see or navigate their exploration path.
   - **Location:** Need `<BreadcrumbTrail>` component in both apps.

6. **No conflict resolution UI**
   - **Impact:** Simultaneous edits silently overwrite each other.
   - **Location:** Need conflict detection and merge UI.

### 🟠 HIGH (Degrades Experience)

7. **No session resumption UI**
   - **Impact:** Users must manually re-establish context after closing apps.
   - **Location:** Need "Resume Exploration" widget using `/continue` endpoint.

8. **No activity timeline**
   - **Impact:** Users can't review their exploration history.
   - **Location:** Need timeline component using `/history` endpoint.

9. **No session timeout warning**
   - **Impact:** Sessions expire without notice, losing context.
   - **Location:** Need "Session expires in 5min" toast.

10. **Reading position write-only from Reader**
    - **Impact:** SiYuan can't suggest "return to this passage".
    - **Location:** Need SiYuan reading position write capability.

### 🟡 MEDIUM (Usability Friction)

11. **No dwell time tracking**
    - **Impact:** Can't analyze which entities user spent time on.
    - **Location:** Need focus/blur timers in FlowPanel and ContextSyncService.

12. **No last-app-source indicator**
    - **Impact:** Users can't see which app was last active.
    - **Location:** Backend tracks it, UI should show it.

13. **Silent sync after backgrounding**
    - **Impact:** User doesn't know sync slowed to 30s when tab backgrounded.
    - **Location:** Toast: "Tab backgrounded, sync slowed to 30s".

---

## User Confusion Points

Based on journey analysis, users will be confused by:

1. **"Did my change save?"**
   - No confirmation message after context/question change.
   - Recommendation: Toast "Context synced to SiYuan" or sync indicator turns green.

2. **"Why doesn't SiYuan show my entity?"**
   - Reader entity clicks don't auto-add to journey trail.
   - Recommendation: Auto-call `addEntityVisit()` on entity focus.

3. **"Where's my exploration from this morning?"**
   - No resume UI on app startup.
   - Recommendation: "Resume Exploration" card using `/continue` endpoint.

4. **"Which app should I use?"**
   - No indication of which app was last active or where state lives.
   - Recommendation: Show "Last active in SiYuan 2 hours ago" in Reader.

5. **"How do I open this in the Reader?"**
   - SiYuan shows sources but no way to jump to Reader.
   - Recommendation: "Open in Reader" button using deep links.

6. **"Why did my change disappear?"**
   - Simultaneous writes cause silent conflicts.
   - Recommendation: Conflict indicator: "SiYuan overwrote your context change. Undo?"

---

## Recommended Improvements

### Priority 1: Visibility (1-2 weeks)

**Make sync observable to users**

1. **Sync Status Indicator**
   - Component: `<SyncStatusBadge>` in both apps
   - States: "Syncing", "Synced", "Offline", "Error", "Conflict"
   - Location: Top-right corner, always visible
   - Implementation: Subscribe to service state (`isSyncing`, `syncError`, `lastSyncedAt`)

2. **Error Toast Notifications**
   - Event: `syncError` changes from null to string
   - Message: "Sync failed: [error message]. Retrying..."
   - Actions: "Retry Now" button, "Dismiss" button

3. **Session Timeout Warning**
   - Event: `last_activity_at` > 25 minutes ago
   - Message: "Session will expire in 5 minutes. Continue?"
   - Action: Send heartbeat when user clicks "Continue"

### Priority 2: Deep Linking (2-3 weeks)

**Enable seamless app-to-app navigation**

1. **Reader Deep Link Handler**
   - Parse URL params on load: `?calibreId=42&entity=concept_123&cfi=...`
   - Open book, focus entity, highlight passage
   - Implementation: `useEffect` in Reader root component

2. **SiYuan "Open in Reader" Buttons**
   - Location: Sources section of entity panel
   - Action: Generate `reader://` deep link using `/continue` endpoint
   - Implementation: Button component that calls `window.open(readerDeepLink)`

3. **"Resume Exploration" Widget**
   - Location: Both apps, shown on startup if `has_active_exploration=true`
   - Content: "Continue exploring [entity name] from [app]"
   - Action: Deep link to other app or restore state in current app

### Priority 3: Journey Trail UI (1-2 weeks)

**Make exploration path visible and navigable**

1. **Breadcrumb Trail Component**
   - Render `journey_trail` as clickable breadcrumbs
   - Location: Top of Flow Panel in both apps
   - Click action: Navigate to that entity
   - Display: Entity name, app icon (Reader/SiYuan), timestamp

2. **Auto-Track Entity Visits**
   - Reader: Call `addEntityVisit()` when FlowPanel opens entity
   - SiYuan: Call `addEntityVisit()` when Flow Mode focuses entity
   - Track dwell time: Start timer on focus, stop on blur

3. **Activity Timeline View**
   - Endpoint: `GET /session-state/{user_id}/history`
   - Display: Vertical timeline with icons for context_opened, question_selected, book_opened, entity_visited
   - Click action: Restore that state (deep link or API call)

### Priority 4: Conflict Resolution (3-4 weeks)

**Handle simultaneous edits gracefully**

1. **Optimistic Locking**
   - Add `version: number` to `SessionState` schema
   - Backend: Increment version on every write
   - Frontend: Include `expected_version` in update request
   - Backend: Return 409 Conflict if version mismatch

2. **Conflict UI**
   - Event: 409 Conflict response from backend
   - Message: "Your change conflicts with [other app]. Which version to keep?"
   - Options: "Keep mine", "Use theirs", "Merge"

3. **Last-Write Metadata**
   - Add `last_updated_by: AppSource` and `last_updated_at: datetime` to each field
   - Display: "Context was changed by SiYuan 2 minutes ago"

### Priority 5: Error Recovery (2-3 weeks)

**Prevent data loss from network issues**

1. **Offline Queue**
   - Store failed writes in `localStorage` with timestamp
   - Retry on reconnection (navigator.onLine event)
   - Max queue size: 100 items, oldest dropped first

2. **Network Status Detection**
   - Listen to `navigator.onLine` events
   - Poll backend `/health` endpoint every 10s
   - UI: "Offline" badge when network down

3. **Retry Logic**
   - Exponential backoff: 1s, 2s, 4s, 8s, 16s, 30s (max)
   - Max retries: 6 attempts
   - User action: "Force Retry Now" button

---

## State Schema Recommendations

### Current Schema Gaps

1. **No version field:** Can't detect conflicts.
2. **No last-write metadata:** Can't show who changed what.
3. **No sync status:** Can't tell if state is fresh or stale.

### Proposed Schema Additions

```typescript
interface SessionState {
  // ... existing fields ...

  // Conflict detection
  version: number;  // Incremented on every write

  // Last-write tracking (per field)
  active_context_updated_by?: AppSource;
  active_context_updated_at?: datetime;
  active_question_updated_by?: AppSource;
  active_question_updated_at?: datetime;

  // Sync metadata
  sync_status: 'synced' | 'syncing' | 'error';
  sync_error?: string;
  last_successful_sync_at?: datetime;
}
```

### Proposed History Schema Enhancement

```typescript
interface SessionStateHistory {
  // ... existing fields ...

  // Add app source to history
  updated_by: AppSource;

  // Add change payload for rollback
  before_value?: any;
  after_value?: any;
}
```

---

## Technical Debt Assessment

### Code Quality Issues

1. **Inconsistent error handling:**
   - Reader: Logs errors but doesn't set state
   - SiYuan: Sets `syncError` state but doesn't display it
   - **Recommendation:** Standardize error handling pattern.

2. **Asymmetric journey trail:**
   - Reader: Read-only (polls trail)
   - SiYuan: Read-write (adds trail items)
   - **Recommendation:** Both apps should write trail.

3. **Manual integration required:**
   - Developer must wire up `addEntityVisit()` calls
   - **Recommendation:** Make tracking automatic via hooks.

4. **No TypeScript types shared:**
   - Reader uses `SessionState` from `sessionStateApi.ts`
   - SiYuan uses `SessionState` from `sessionStateApi.ts`
   - Both independently defined (risk of drift)
   - **Recommendation:** Shared types package.

### Architecture Concerns

1. **Redis as single source of truth:**
   - ✅ Good: Persistence, fast reads
   - 🔴 Bad: No backup if Redis fails
   - **Recommendation:** Add PostgreSQL persistence for critical state.

2. **Polling vs. WebSocket:**
   - ✅ Good: Simple, reliable
   - 🔴 Bad: 5-30s latency, battery drain
   - **Recommendation:** Evaluate WebSocket for real-time sync.

3. **No CRDT or OT:**
   - ✅ Good: Simple last-write-wins
   - 🔴 Bad: Conflicts cause data loss
   - **Recommendation:** Use CRDT for journey trail (append-only log).

---

## Conclusion

The cross-app sync **infrastructure is production-grade** (Redis, heartbeats, TTL, polling), but the **user experience is pre-alpha**. Users have no visibility into what's happening, no way to recover from errors, and no tools to navigate their exploration journey across apps.

**The system works technically but fails practically.**

### Immediate Actions (Week 1)

1. Add sync status indicator to both apps
2. Add error toast notifications
3. Wire up `addEntityVisit()` to FlowPanel entity clicks
4. Add breadcrumb trail component

### Short-Term Actions (Weeks 2-4)

5. Implement deep linking (Reader URL params, SiYuan buttons)
6. Add "Resume Exploration" widget using `/continue` endpoint
7. Add activity timeline using `/history` endpoint
8. Add session timeout warning

### Medium-Term Actions (Weeks 5-8)

9. Implement conflict detection with optimistic locking
10. Add offline queue and retry logic
11. Add dwell time tracking
12. Migrate to WebSocket for sub-second sync

Without these improvements, users will experience:
- Silent data loss
- Confusion about app state
- Manual re-entry of context
- Frustration with "broken" sync

**The technical foundation is solid. The UX layer is missing.**
