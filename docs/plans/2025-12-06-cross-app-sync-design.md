# Cross-App Sync Design: IES Ecosystem
**Date:** December 6, 2025
**Status:** Design Complete — Ready for Implementation (Wave 2.3)
**Context:** Two frontend apps (IES Reader + SiYuan Plugin) sharing unified backend

---

## Executive Summary

**Current State (Wave 2.1-2.2 Complete):**
- Both apps use device ID → `/profile/login` → unified `user_id`
- Both save journeys via `POST /journeys` with entry point differentiation
- Schema transformation (camelCase → snake_case) handled in both clients
- Journey persistence works independently in each app

**Problem:**
- No real-time state synchronization between apps
- Journey data only syncs at persistence boundaries (save/load)
- No offline queue for unreachable backend
- No conflict resolution for concurrent operations

**Solution Philosophy:**
Keep it simple for Wave 2.3. Build on existing patterns. Defer complex sync until Wave 3+.

---

## 1. Sync Protocol Specification

### 1.1 What Gets Synced?

**NOW (Wave 2.3):**
```
✓ Journeys (completed exploration paths)
✓ User profile changes (cognitive dimensions)
✓ Entity explorations (which entities viewed, in which apps)
```

**FUTURE (Wave 3+):**
```
○ In-progress journeys (partial paths, live sync)
○ Entity annotations (highlights, notes)
○ User preferences (UI state, theme, panel widths)
○ Quick captures (sparks before backend persistence)
```

### 1.2 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Data Flow Diagram                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  IES Reader                         SiYuan Plugin               │
│  ┌────────────────┐                ┌────────────────┐          │
│  │ flowStore      │                │ Dashboard      │          │
│  │ (Zustand)      │                │ (Svelte)       │          │
│  └───────┬────────┘                └───────┬────────┘          │
│          │ graphClient                     │ siyuan-structure  │
│          │ saveJourney()                   │ saveJourney()     │
│          ▼                                 ▼                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Backend API (Shared Services)                   │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ POST        │  │ GET /journeys│  │ SessionStore │  │   │
│  │  │ /journeys   │  │ /user/{id}   │  │ (Redis 24h)  │  │   │
│  │  └──────┬──────┘  └──────┬───────┘  └──────────────┘  │   │
│  └─────────┼────────────────┼─────────────────────────────┘   │
│            ▼                ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Neo4j Persistence Layer                    │   │
│  │  Journey nodes with:                                    │   │
│  │  - user_id (unified identifier)                         │   │
│  │  - entry_point.type (reading vs siyuan-flow)           │   │
│  │  - started_at, ended_at (timestamps)                    │   │
│  │  - path[] (journey steps with dwell times)             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Sync Triggers:                                                │
│  ■ Journey end → POST /journeys (immediate)                    │
│  ■ Dashboard mount → GET /journeys/user/{id} (on load)         │
│  ■ Reader open book → GET /journeys/user/{id} (on load)        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Sync Triggers

**Immediate (Write Operations):**
- Journey end (Reader or SiYuan) → `POST /journeys`
- Profile update → `PATCH /profile/{user_id}`
- Entity exploration → Increment visit count (tracked in memory, persisted on journey save)

**Periodic (Read Operations):**
- Dashboard mount → Fetch recent journeys
- Reader book open → Fetch journey history for suggestions
- Manual refresh button → Full sync check

**NOT NEEDED YET:**
- WebSocket/SSE for live updates (Wave 3+)
- Polling intervals (no use case for background sync currently)

### 1.4 Sync Frequency Trade-off Matrix

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **On-demand only** (Wave 2.3) | Simple, no background overhead, matches current usage | Stale data until user action | ✅ **NOW** — Fits current app usage patterns |
| **5-min polling** | Fresh data, simple implementation | Wasted requests, battery drain | ❌ **DEFER** — No use case for background freshness |
| **WebSocket live sync** | Real-time, efficient for rapid changes | Complex, server overhead, reconnection logic | ❌ **DEFER** — No concurrent multi-app usage yet |
| **SSE server push** | One-way efficiency, simpler than WebSocket | Still needs reconnection, connection overhead | ⏸️ **FUTURE** — Good for notification-style updates |

**Decision:** On-demand sync for Wave 2.3. Re-evaluate in Wave 3 if usage patterns show concurrent multi-app sessions.

---

## 2. Conflict Resolution Strategy

### 2.1 Conflict Scenarios

**Scenario 1: Same Entity Explored in Both Apps**
```
Timeline:
10:00 — User explores "Executive Function" in IES Reader (dwellTime: 120s)
10:05 — User explores "Executive Function" in SiYuan FlowMode (dwellTime: 90s)
```

**Resolution:**
- Both explorations saved as separate journey steps
- Timestamps preserve chronological order
- `entry_point.type` distinguishes source context (reading vs siyuan-flow)
- Analytics can aggregate by entity_id for total dwell time across apps

**Why This Works:**
- Each exploration has unique context (book passage vs flow map)
- Preserving both creates richer journey history
- No "winner" needed — both are valid data points

---

**Scenario 2: Overlapping Journey Timestamps**
```
Timeline:
14:00 — Start journey in IES Reader (book: "Driven to Distraction")
14:15 — Start journey in SiYuan (entry: FlowMode dashboard)
14:30 — End Reader journey (save to backend)
14:35 — End SiYuan journey (save to backend)
```

**Resolution:**
- Both journeys persisted independently (separate Neo4j Journey nodes)
- `started_at` and `ended_at` timestamps preserved exactly
- Journey listing sorted by `started_at DESC` shows chronological order
- UI can display both journeys side-by-side with timeline view

**Why This Works:**
- User legitimately switched contexts (reading → note-taking)
- Separate journeys = separate thinking sessions
- No conflict — this is expected behavior for multi-tool workflow

---

**Scenario 3: Device ID Collision (Theoretical)**
```
Edge Case:
Device A generates: device-1733522400-abc123
Device B generates: device-1733522400-abc123 (same timestamp + random)
```

**Resolution:**
- Probability: ~1 in 2.8 trillion (36^9 combinations)
- Detection: `/profile/login` checks if user_id exists with different metadata
- Mitigation: Append hostname or MAC address hash if collision detected
- Fallback: Generate new device ID and prompt user to choose primary device

**Implementation (FUTURE):**
```typescript
function getDeviceId(): string {
  const key = 'ies-reader-device-id';
  let deviceId = localStorage.getItem(key);

  if (!deviceId) {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substr(2, 9);
    const hostname = window.location.hostname;
    deviceId = `device-${timestamp}-${random}-${hashCode(hostname)}`;
    localStorage.setItem(key, deviceId);
  }

  return deviceId;
}
```

**Priority:** LOW — Defer to Wave 4+ (no reported collisions)

---

### 2.2 Conflict Resolution Rules

```yaml
Principle: "Append, Don't Overwrite"

Journey Steps:
  - Rule: All explorations preserved with timestamps
  - Conflict: None — chronological order is canonical
  - Storage: Separate JourneyStep nodes linked to Journey

Profile Updates:
  - Rule: Last write wins (timestamp-based)
  - Conflict: Concurrent dimension updates → most recent timestamp
  - Storage: Single UserProfile node, updated atomically
  - Mitigation: Debounce profile updates (500ms) to reduce conflicts

Entity Visit Counts:
  - Rule: Increment, never decrement
  - Conflict: None — visit_count is monotonic
  - Storage: Atomic counter in Neo4j (MERGE + SET count = count + 1)
```

---

## 3. Offline Queue Design

### 3.1 Offline Scenarios

**Common Cases:**
1. **Backend unreachable** — Docker services down, network unavailable
2. **High latency** — Request timeout (> 30s)
3. **Intermittent connection** — Airplane mode, tunnel passage

### 3.2 Queue Architecture

```typescript
// Shared localStorage queue structure (both apps)
interface QueuedOperation {
  id: string;                    // uuid for deduplication
  userId: string;                // user who owns this operation
  operationType: 'journey' | 'profile' | 'visit';
  payload: any;                  // operation-specific data
  endpoint: string;              // POST /journeys, PATCH /profile, etc.
  timestamp: string;             // when operation was queued
  retryCount: number;            // failed attempt counter
  lastError?: string;            // last failure message
}

// Example queue entry
{
  "id": "op-1733522400-abc123",
  "userId": "device-1733520000-xyz789",
  "operationType": "journey",
  "payload": {
    "user_id": "device-1733520000-xyz789",
    "entry_point": { "type": "reading", "reference": "Driven to Distraction" },
    "path": [ /* journey steps */ ]
  },
  "endpoint": "/journeys",
  "timestamp": "2025-12-06T14:30:00Z",
  "retryCount": 0
}
```

### 3.3 Queue Storage Location

**Option 1: Separate Queue per App**
```
localStorage['ies-reader-offline-queue']
localStorage['ies-siyuan-offline-queue']
```
**Pros:** Simple, no cross-contamination
**Cons:** Duplicate operations if both apps queue same data

**Option 2: Shared Queue with App Tags**
```
localStorage['ies-offline-queue']
  └─ operations: [{ appSource: 'reader', ... }, { appSource: 'siyuan', ... }]
```
**Pros:** Deduplication possible, unified sync
**Cons:** More complex, potential queue corruption

**Decision:** **Option 1** — Separate queues for Wave 2.3. Simpler, safer, no deduplication needed yet.

### 3.4 Retry Logic

```typescript
class OfflineQueue {
  MAX_RETRIES = 3;
  RETRY_DELAYS = [5000, 30000, 120000]; // 5s, 30s, 2min

  async processQueue(): Promise<void> {
    const queue = this.loadQueue();

    for (const op of queue) {
      try {
        await this.executeOperation(op);
        this.removeFromQueue(op.id);
      } catch (error) {
        op.retryCount++;
        op.lastError = error.message;

        if (op.retryCount >= this.MAX_RETRIES) {
          // Move to failed queue for manual review
          this.moveToFailedQueue(op);
          this.removeFromQueue(op.id);
        } else {
          // Schedule retry with exponential backoff
          this.updateQueue(op);
          setTimeout(
            () => this.retryOperation(op),
            this.RETRY_DELAYS[op.retryCount - 1]
          );
        }
      }
    }
  }

  async retryOperation(op: QueuedOperation): Promise<void> {
    // Attempt operation again
    await this.processQueue();
  }
}
```

### 3.5 Queue Reconciliation on Reconnect

```
┌────────────────────────────────────────────────────────────────┐
│              Reconnection Sync Flow                            │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  1. Detect Backend Available                                  │
│     - Health check succeeds (GET /health)                     │
│     - Or first successful API call                            │
│                                                                │
│  2. Load Offline Queue                                        │
│     - Parse localStorage['ies-reader-offline-queue']          │
│     - Sort by timestamp (oldest first)                        │
│                                                                │
│  3. Process Operations Sequentially                           │
│     - Execute each operation in order                         │
│     - Wait for success before next operation                  │
│     - On failure: retry logic (see 3.4)                       │
│                                                                │
│  4. Remove Successful Operations                              │
│     - Delete from queue after 200 OK response                 │
│     - Keep failed operations for retry                        │
│                                                                │
│  5. Display Sync Status                                       │
│     - Show toast: "Synced 3 journeys from offline queue"      │
│     - Or error: "1 journey failed to sync (retry later)"      │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 3.6 UI Indicators

**IES Reader (flowStore):**
```typescript
interface SyncState {
  status: 'idle' | 'syncing' | 'offline' | 'error';
  queuedOperations: number;
  lastSyncTime: string | null;
  syncError: string | null;
}

// Display in Flow Panel header
{syncState.status === 'offline' && (
  <div className="sync-warning">
    ⚠️ Offline — {syncState.queuedOperations} changes queued
  </div>
)}

{syncState.status === 'syncing' && (
  <div className="sync-progress">
    ↻ Syncing {syncState.queuedOperations} changes...
  </div>
)}
```

**SiYuan Plugin (Dashboard):**
```svelte
{#if syncStatus === 'offline'}
  <div class="status-banner warning">
    <Icon name="cloud-off" />
    <span>Backend offline — Changes saved locally</span>
    <button on:click={retrySyncNow}>Retry Sync</button>
  </div>
{/if}
```

---

## 4. Event Notification System

### 4.1 Notification Options Analysis

**Trade-off Matrix:**

| Approach | Complexity | Latency | Server Load | Battery Impact | Use Cases |
|----------|------------|---------|-------------|----------------|-----------|
| **Polling** | Low (1) | High (5s+) | Medium | Medium-High | Dashboard stats |
| **WebSocket** | High (4) | Instant | Medium | Medium | Multi-device editing |
| **SSE** | Medium (2) | Instant | Low | Low | One-way notifications |
| **On-demand** | Lowest (0) | User-triggered | Lowest | None | Current Wave 2.3 |

### 4.2 Recommendation: On-Demand for Wave 2.3

**Rationale:**
- Current usage: Single user, single device, sequential app switching
- No concurrent multi-app sessions observed
- Journeys only need sync at completion (not live)
- Dashboard shows stale data until refresh (acceptable UX)

**Implementation:**
```typescript
// IES Reader: Refresh button in Flow Panel
<button onClick={() => flowStore.refreshJourneyHistory(userId)}>
  <Icon name="refresh" /> Refresh Journeys
</button>

// SiYuan: Dashboard auto-refreshes on mount
onMount(async () => {
  const profile = await login(deviceId);
  const journeys = await getJourneyHistory(profile.user_id);
  // Display journeys in Dashboard
});
```

### 4.3 Future Upgrade Path (Wave 3+)

**Scenario:** User wants live journey sync between devices

**Upgrade to SSE:**
```
Backend (FastAPI SSE):
@router.get("/events/{user_id}")
async def stream_events(user_id: str):
    async def event_generator():
        while True:
            # Check for new journeys
            journeys = await JourneyService.list_recent(user_id, since=last_check)
            if journeys:
                yield f"data: {json.dumps({'type': 'journey_saved', 'data': journeys})}\n\n"
            await asyncio.sleep(5)  # 5-second check interval

    return EventSourceResponse(event_generator())

Frontend (EventSource API):
const eventSource = new EventSource(`/events/${userId}`);
eventSource.onmessage = (event) => {
  const { type, data } = JSON.parse(event.data);
  if (type === 'journey_saved') {
    flowStore.appendJourneys(data);
  }
};
```

**Benefits:**
- One-way push (server → clients)
- Auto-reconnects on disconnect
- Lower overhead than WebSocket

**Costs:**
- Persistent connection per active client
- Redis pub/sub for multi-worker coordination

**Decision:** Defer to Wave 3+ until usage patterns justify complexity.

---

## 5. Security Considerations

### 5.1 Device ID Privacy

**Current Implementation:**
```typescript
// Both apps use same device ID generation
function getDeviceId(): string {
  const key = 'ies-{app}-device-id';  // app = 'reader' or 'siyuan'
  let deviceId = localStorage.getItem(key);
  if (!deviceId) {
    deviceId = `device-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem(key, deviceId);
  }
  return deviceId;
}
```

**Security Properties:**
- **No PII:** Device ID is ephemeral, not linked to identity
- **Single device binding:** localStorage scoped to origin
- **Anonymous by default:** User can use system without account
- **Revocable:** Clear localStorage = new identity

**Risks:**
- **Device theft:** Attacker gains access to user's journey history
- **Browser profile sharing:** Multiple people on same device = shared identity

**Mitigations (FUTURE):**
- Optional authentication layer (Supabase, Auth0)
- Biometric confirmation for sensitive operations
- Session timeout (auto-logout after 24h inactivity)

**Priority:** LOW — Single-user personal tool, no sensitive data

### 5.2 Cross-App Data Access Controls

**Current Model: Fully Open**
- Both apps share same `/profile/login` endpoint
- Both apps access same journeys via `/journeys/user/{user_id}`
- No app-specific scoping or permissions

**Risk:**
- Malicious plugin could read/write all journey data
- No isolation between apps

**Future Model: App-Scoped Permissions (Wave 4+)**
```python
# Backend schema update
class AppPermission(str, Enum):
    READER = "reader"
    SIYUAN = "siyuan"
    ADMIN = "admin"

class Journey(BaseModel):
    created_by_app: AppPermission
    visible_to_apps: list[AppPermission]

# API authentication
@router.post("/journeys")
async def create_journey(
    request: JourneyCreateRequest,
    app_id: str = Header(..., alias="X-App-ID")
):
    # Verify app_id is valid (reader, siyuan, admin)
    # Set created_by_app and visible_to_apps
    pass
```

**Trade-off:**
- **Pro:** Better security isolation, granular control
- **Con:** Complex permission model, shared data becomes harder
- **Decision:** Defer until multi-app marketplace or enterprise deployment

### 5.3 Rate Limiting for Sync Operations

**Current State:** No rate limiting

**Risk Scenarios:**
- Infinite retry loop drains API quota
- Malicious script floods backend with fake journeys
- Offline queue explosion (1000+ queued operations)

**Mitigation (Wave 3):**
```python
# Backend rate limiter (FastAPI)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/journeys")
@limiter.limit("20/minute")  # Max 20 journey saves per minute per IP
async def create_journey(request: Request, journey: JourneyCreateRequest):
    pass
```

**Limits (Recommended):**
- Journeys: 20/min per user_id
- Profile updates: 10/min per user_id
- Entity visits: 100/min per user_id (high-frequency operation)

**Priority:** MEDIUM — Implement in Wave 3 before opening to external users

---

## 6. Cross-App Features (Phase 2+ Considerations)

### 6.1 SiYuan Showing IES Reader Journeys

**Use Case:**
User explores "Executive Function" in IES Reader while reading "Driven to Distraction". Later, opens SiYuan Dashboard and wants to see this journey.

**Implementation (FUTURE):**
```svelte
<!-- Dashboard.svelte: Recent Journeys Section -->
<script>
let recentJourneys = [];

onMount(async () => {
  const journeys = await getJourneyHistory(userId, page=1, limit=10);
  recentJourneys = journeys.journeys;
});
</script>

<div class="recent-journeys">
  <h3>Recent Explorations</h3>
  {#each recentJourneys as journey}
    <div class="journey-card" class:from-reader={journey.entry_point.type === 'reading'}>
      <div class="journey-header">
        {#if journey.entry_point.type === 'reading'}
          📖 Reading: {journey.entry_point.reference}
        {:else}
          🗺️ Flow Map: {journey.entry_point.reference}
        {/if}
      </div>
      <div class="journey-path">
        {journey.path.map(s => s.entity_name).join(' → ')}
      </div>
      <button on:click={() => resumeJourney(journey)}>Resume</button>
    </div>
  {/each}
</div>
```

**Features:**
- Visual distinction (📖 vs 🗺️ icon) for entry point type
- Journey preview (entity names in path)
- "Resume" button opens relevant app with entity pre-loaded

### 6.2 IES Reader Resuming from SiYuan Explorations

**Use Case:**
User explores concept in SiYuan FlowMode, discovers related book entity. Clicks "Read in Context" button to jump to book passage in IES Reader.

**Implementation (FUTURE):**
```typescript
// FlowPanel: Entity Source Section
{entity.sources.map(source => (
  <div key={source.bookId} className="source-link">
    <span>{source.bookTitle}</span>
    {source.pageRange && <span className="page-range">p. {source.pageRange}</span>}

    {/* New: Open in Reader button */}
    <button onClick={() => openInReader(source.bookId, entity.id)}>
      📖 Read in Context
    </button>
  </div>
))}

async function openInReader(bookId: string, entityId: string) {
  // Navigate to IES Reader with deep link
  const readerUrl = `/reader?book=${bookId}&entity=${entityId}`;
  window.location.href = readerUrl;

  // Or use browser messaging if both apps open
  window.postMessage({
    type: 'OPEN_BOOK',
    bookId,
    highlightEntity: entityId
  }, '*');
}
```

**Deep Link Format:**
```
/reader?book=calibre:42&entity=concept_123
  → Opens "Driven to Distraction" (calibre_id: 42)
  → Scrolls to first mention of entity concept_123
  → Highlights entity in text with entity overlay
```

### 6.3 Unified Exploration History View

**Use Case:**
User wants chronological view of ALL explorations across both apps to track learning journey.

**Implementation (FUTURE):**
```
┌────────────────────────────────────────────────────────────────┐
│          Exploration Timeline (Unified View)                   │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Today, 2:30 PM — 📖 Reading Session (15 min)                 │
│    Driven to Distraction → Executive Function → ADHD          │
│    [View in Reader]                                            │
│                                                                │
│  Today, 10:15 AM — 🗺️ Flow Map Session (8 min)               │
│    Dashboard → Acceptance → Grief → Metabolization            │
│    [View in SiYuan]                                            │
│                                                                │
│  Yesterday, 4:00 PM — 📖 Reading Session (22 min)             │
│    The ADHD Effect on Marriage → Communication → Shame        │
│    [View in Reader]                                            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Backend Support:**
```python
@router.get("/journeys/timeline/{user_id}")
async def get_timeline(
    user_id: str,
    days: int = 7,  # Last N days
    app_filter: str | None = None  # 'reader', 'siyuan', or None for both
) -> TimelineResponse:
    """Get chronological journey timeline across all apps."""
    journeys = await JourneyService.list_journeys(user_id, days=days)

    if app_filter:
        # Filter by entry_point.type
        journeys = [j for j in journeys if j.entry_point.type == app_filter]

    return TimelineResponse(
        user_id=user_id,
        journeys=journeys,
        total_exploration_time=sum(j.duration for j in journeys)
    )
```

**Priority:** MEDIUM — Good feature for Wave 3 (enhances cross-app value proposition)

---

## 7. Implementation Plan

### 7.1 Wave 2.3 Scope (NOW)

**Goal:** Reliable offline queue + basic cross-app journey visibility

**Tasks:**
1. **Offline Queue (IES Reader)** — 4 hours
   - Add `OfflineQueue` class to `graphClient.ts`
   - Implement `saveJourney()` with queue fallback
   - Add retry logic with exponential backoff
   - Display sync status in Flow Panel header

2. **Offline Queue (SiYuan)** — 3 hours
   - Add `OfflineQueue` class to `siyuan-structure.ts`
   - Implement `saveJourney()` with queue fallback
   - Add retry logic (same pattern as Reader)
   - Display sync status in Dashboard

3. **Journey History API** — 2 hours
   - Already implemented: `GET /journeys/user/{user_id}`
   - Test with multiple entry_point types
   - Verify sorting by `started_at DESC`

4. **Cross-App Journey Display (SiYuan)** — 3 hours
   - Add "Recent Journeys" section to Dashboard
   - Fetch all journeys (both `reading` and `siyuan-flow`)
   - Display with app-specific icons
   - Add "from IES Reader" badge for reading journeys

5. **Testing** — 4 hours
   - Offline queue persistence (localStorage)
   - Retry logic (simulate failed API calls)
   - Queue deduplication (same operation queued twice)
   - Cross-app journey listing (both entry types visible)

**Total Estimate:** 16 hours (~2 days)

### 7.2 Wave 3 Scope (FUTURE)

**Goal:** Real-time sync + advanced conflict resolution

**Features:**
- SSE event stream for live journey updates
- Backend rate limiting (slowapi)
- Device ID collision detection
- App-scoped permissions (reader vs siyuan)
- Timeline view (unified exploration history)

**Estimate:** 40 hours (~1 week)

### 7.3 Wave 4+ Scope (LATER)

**Goal:** Multi-device support + enterprise features

**Features:**
- WebSocket for bidirectional sync
- Multi-device identity management
- Encrypted journey storage
- Cross-app deep linking
- Advanced analytics (entity co-occurrence, journey patterns)

**Estimate:** 80+ hours (~2-3 weeks)

---

## 8. Success Criteria

### Wave 2.3 (NOW)

**Functional:**
- ✅ Journey saved in IES Reader appears in SiYuan Dashboard within 5 seconds of refresh
- ✅ Offline queue stores max 50 operations, oldest discarded when full
- ✅ Retry logic attempts 3 times with exponential backoff (5s, 30s, 2min)
- ✅ Failed operations move to failed queue after 3 attempts
- ✅ Sync status indicator shows: idle, syncing, offline, error states

**Non-Functional:**
- ✅ No data loss during offline periods (localStorage persists)
- ✅ Queue processing completes in < 10 seconds for 10 queued operations
- ✅ UI remains responsive during background sync (async processing)

### Wave 3 (FUTURE)

**Functional:**
- SSE event stream delivers journey updates in < 1 second
- Timeline view shows mixed journeys sorted chronologically
- Rate limiting prevents > 20 journeys/minute abuse

**Non-Functional:**
- SSE reconnects automatically within 5 seconds of disconnect
- Backend handles 100 concurrent SSE connections without degradation

---

## 9. Open Questions

1. **Queue Size Limit:** 50 operations or unlimited with LRU eviction?
   - **Decision:** 50 operations max, oldest discarded. Prevents localStorage bloat.

2. **Duplicate Journey Detection:** Should queue deduplicate identical journeys?
   - **Decision:** No. Each journey is timestamp-unique. User can manually delete duplicates.

3. **Cross-Device Sync:** What if same user_id on multiple devices?
   - **Decision:** Defer to Wave 4. Current single-device assumption holds.

4. **Offline Queue Visibility:** Should UI show queued operations list?
   - **Decision:** Wave 2.3 shows count only. Wave 3 adds expandable queue viewer.

---

## Appendix A: Data Schemas

### Journey (Backend)
```python
class BreadcrumbJourney(BaseModel):
    id: str | None = None
    user_id: str
    started_at: datetime
    ended_at: datetime | None = None
    entry_point: EntryPoint  # type: 'reading' | 'siyuan-flow'
    path: list[JourneyStep]
    marks: list[JourneyMark] = []
    thinking_partner_exchanges: list[ThinkingPartnerExchange] = []
    title: str | None = None
    tags: list[str] = []
    notes: str | None = None
    processed: bool = False
    siyuan_note_id: str | None = None
```

### OfflineQueue (Frontend localStorage)
```typescript
interface OfflineQueue {
  version: string;  // Schema version for migrations
  operations: QueuedOperation[];
  failed: QueuedOperation[];
  lastProcessedAt: string | null;
}

interface QueuedOperation {
  id: string;
  userId: string;
  operationType: 'journey' | 'profile' | 'visit';
  payload: any;
  endpoint: string;
  timestamp: string;
  retryCount: number;
  lastError?: string;
}
```

---

## Appendix B: ASCII Diagrams

### Offline Queue State Machine
```
┌─────────────────────────────────────────────────────────────────┐
│                   Queue Operation Lifecycle                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Created] ──────────────────────────────────────────────────> │
│      │                                                          │
│      ▼                                                          │
│  [Queued in localStorage]                                       │
│      │                                                          │
│      ▼                                                          │
│  [Backend Available?]                                           │
│      │                                                          │
│      ├──YES──> [Execute Operation]                             │
│      │               │                                          │
│      │               ├──SUCCESS──> [Remove from Queue] ──> END │
│      │               │                                          │
│      │               └──FAILURE──> [Retry Count++]             │
│      │                               │                          │
│      │                               ├──< 3 attempts──> [Wait] │
│      │                               │    (exponential backoff)│
│      │                               │         │                │
│      │                               │         └──> [Retry]    │
│      │                               │                          │
│      │                               └──>= 3 attempts──> [Move  │
│      │                                    to Failed Queue]      │
│      │                                                          │
│      └──NO──> [Wait for Reconnect]                             │
│                      │                                          │
│                      └──> [Backend Available?] (loop)           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

**Document Status:** Design Complete
**Next Step:** Begin Wave 2.3 implementation starting with IES Reader offline queue
**Owner:** System Architect
**Last Updated:** December 6, 2025
