# Wave 3: Visibility — Specification

**Date:** 2025-12-06
**Status:** READY FOR IMPLEMENTATION
**Dependencies:** Wave 1 (Foundation) ✅, Wave 2 (Wiring) ✅

---

## Executive Summary

Wave 3 brings user visibility into the system's operation. Users can see their exploration history across apps, provide feedback on generated questions, and trust the system to handle offline scenarios gracefully.

**Goal:** Make the thinking partnership visible and resilient.

---

## Task 3.1: Journey UI

### Problem
- No way to view past exploration journeys
- No synthesis of what was learned
- No visual distinction between app sources

### Deliverables

#### 3.1.1: SiYuan Dashboard — Journey History Section
**Location:** `.worktrees/siyuan/ies/plugin/src/views/Dashboard.svelte`

**Features:**
- "Recent Journeys" section showing last 10 journeys
- Entry point icon: 📖 (reading) vs 🗺️ (siyuan-flow)
- Journey path preview (entity names joined with →)
- Duration display (calculated from dwellTime sum)
- "View Details" expander for full path
- Pagination controls (load more)

**API Integration:**
```typescript
GET /journeys/user/{user_id}?page=1&limit=10
```

#### 3.1.2: IES Reader — Journey History Panel
**Location:** `ies/reader/src/components/flow/FlowPanel.tsx`

**Features:**
- New "History" tab alongside "Flow" tab
- Same design as SiYuan (consistency)
- Filter by entry_point type (reading only, all)
- Click journey → load entity path for resumption

#### 3.1.3: Journey Synthesis Display
**Backend:** New endpoint for journey synthesis
**Location:** `ies/backend/src/ies_backend/api/journey.py`

**Features:**
```python
GET /journeys/{journey_id}/synthesis
Response:
{
  "summary": "Explored Executive Function starting from 'Driven to Distraction',
              connecting through Working Memory to Dopamine regulation.",
  "entities_explored": ["Executive Function", "Working Memory", "Dopamine"],
  "total_dwell_time": 847,  # seconds
  "insights_count": 2,
  "source_books": ["Driven to Distraction"]
}
```

---

## Task 3.2: Question Feedback Capture

### Problem
- Questions generated but no feedback captured
- No learning from user responses
- No way to improve question selection

### Deliverables

#### 3.2.1: Feedback Endpoint
**Location:** `ies/backend/src/ies_backend/api/question_engine.py`

**New Endpoint:**
```python
POST /question-engine/feedback
Request:
{
  "question_id": "q-123",
  "user_id": "device-xxx",
  "entity_id": "concept-456",
  "question_text": "What assumptions underlie your current approach?",
  "response_type": "helpful" | "not_helpful" | "led_to_insight" | "skip",
  "response_text": "Optional user comment",
  "session_id": "session-789",
  "timestamp": "2025-12-06T14:30:00Z"
}

Response:
{
  "feedback_id": "fb-abc",
  "recorded": true
}
```

#### 3.2.2: Feedback Storage
**Location:** Neo4j graph

**Schema:**
```cypher
(f:QuestionFeedback {
  id: "fb-abc",
  question_text: "...",
  response_type: "led_to_insight",
  response_text: "...",
  created_at: datetime()
})-[:GIVEN_BY]->(u:UserProfile)
(f)-[:ABOUT_ENTITY]->(e:Entity)
(f)-[:IN_SESSION]->(s:Session)
```

#### 3.2.3: Frontend Integration
**IES Reader:** Add feedback buttons to each question in FlowPanel
**SiYuan:** Add feedback buttons to ThinkingPartner questions

**UI:**
```
┌─────────────────────────────────────────┐
│ What assumptions underlie your current  │
│ approach to this challenge?             │
│                                         │
│ [👍 Helpful] [👎 Not Helpful] [💡 Insight!] │
└─────────────────────────────────────────┘
```

---

## Task 3.3: Cross-App Sync Implementation

### Problem (from Cross-App Sync Design)
- No offline queue for unreachable backend
- Failed saves lost silently
- No way to manually retry

### Deliverables

#### 3.3.1: Offline Queue — IES Reader
**Location:** `ies/reader/src/services/offlineQueue.ts` (new file)

**Implementation:**
```typescript
interface QueuedOperation {
  id: string;
  userId: string;
  operationType: 'journey' | 'profile' | 'feedback';
  payload: any;
  endpoint: string;
  timestamp: string;
  retryCount: number;
  lastError?: string;
}

class OfflineQueue {
  MAX_RETRIES = 3;
  RETRY_DELAYS = [5000, 30000, 120000]; // 5s, 30s, 2min
  QUEUE_KEY = 'ies-reader-offline-queue';

  async saveOperation(op: Omit<QueuedOperation, 'id' | 'retryCount'>): Promise<void>
  async processQueue(): Promise<ProcessResult>
  async isBackendAvailable(): Promise<boolean>
}
```

#### 3.3.2: Offline Queue — SiYuan
**Location:** `.worktrees/siyuan/ies/plugin/src/utils/offlineQueue.ts` (new file)

Same implementation pattern as IES Reader, different storage key.

#### 3.3.3: Sync Status Indicators
**IES Reader FlowPanel:**
```typescript
// In FlowPanel header
<div className="sync-status">
  {syncStatus === 'syncing' && <span>↻ Syncing...</span>}
  {syncStatus === 'offline' && <span>⚠️ Offline ({queuedCount} pending)</span>}
  {syncStatus === 'error' && <span>❌ Sync failed</span>}
  {syncStatus === 'synced' && <span>✓ Synced</span>}
</div>
```

**SiYuan Dashboard:**
```svelte
{#if syncStatus === 'offline'}
  <div class="status-banner warning">
    Offline — {queuedCount} changes pending
    <button on:click={retrySyncNow}>Retry</button>
  </div>
{/if}
```

#### 3.3.4: Manual Refresh Button
Both apps get explicit "Refresh" button to:
- Check backend health
- Process offline queue
- Reload journey history

---

## Implementation Order

1. **3.3 Cross-App Sync** — Foundation for resilient operations
2. **3.1 Journey UI** — Depends on reliable sync for history
3. **3.2 Question Feedback** — Uses offline queue for resilience

---

## Success Criteria

### Functional
- [ ] Journey history shows in both apps with cross-app entries
- [ ] Journey synthesis generates meaningful summaries
- [ ] Question feedback persists to Neo4j
- [ ] Offline queue stores up to 50 operations
- [ ] Retry logic works with exponential backoff
- [ ] Sync status accurately reflects queue state

### Non-Functional
- [ ] No data loss during offline periods
- [ ] Queue processing < 10 seconds for 10 operations
- [ ] UI remains responsive during sync

---

## Agent Assignment

| Task | Agent Type | Focus |
|------|------------|-------|
| 3.3 Offline Queue | `fullstack-developer` | Both frontend implementations |
| 3.1 Journey UI | `fullstack-developer` | SiYuan + IES Reader UI |
| 3.2 Question Feedback | `backend-developer` | Neo4j schema + API |

---

## Files to Modify/Create

### New Files
- `ies/reader/src/services/offlineQueue.ts`
- `.worktrees/siyuan/ies/plugin/src/utils/offlineQueue.ts`
- `ies/backend/src/ies_backend/services/feedback_service.py`

### Modified Files
- `ies/reader/src/components/flow/FlowPanel.tsx` — History tab, feedback buttons
- `ies/reader/src/store/flowStore.ts` — Sync status state
- `ies/reader/src/services/graphClient.ts` — Offline queue integration
- `.worktrees/siyuan/ies/plugin/src/views/Dashboard.svelte` — Journey history
- `.worktrees/siyuan/ies/plugin/src/views/FlowMode.svelte` — Feedback buttons
- `ies/backend/src/ies_backend/api/question_engine.py` — Feedback endpoint
- `ies/backend/src/ies_backend/api/journey.py` — Synthesis endpoint

---

## Testing Requirements

### Unit Tests
- Offline queue persistence (localStorage mock)
- Retry logic (clock mocking)
- Queue size limits

### Integration Tests
- Backend health check endpoint
- Feedback endpoint persistence
- Journey synthesis generation

### Manual Tests
- Kill backend → perform operations → restart → verify sync
- Rapid offline/online toggling
- Cross-app journey display

---

**Document Status:** Ready for Implementation
**Next Step:** Begin Task 3.3 (Offline Queue)
**Owner:** Orchestrating Agent
