# Cross-App Integration UX Analysis
**Date:** December 6, 2025
**Analyst:** UX Analyst Agent
**Component:** Cross-App Integration (Readest ↔ SiYuan ↔ Backend)
**Grade:** D (1.2/4.0)

---

## Executive Summary

Cross-app integration is **fundamentally broken**. While both Readest and SiYuan can connect to the backend independently, there is **zero state sharing between apps**. Users cannot:
- Continue reading sessions started in Readest from SiYuan
- See Readest exploration journeys in SiYuan Dashboard
- Access SiYuan-created concepts from Readest entity overlays
- Resume work across devices or apps

The "four-layer thinking partnership cycle" exists only on paper. In practice, users operate in **isolated silos**.

---

## User Story Completion: 1 of 4 (25%)

### ❌ Story 1: Continue Exploration Across Apps
**Scenario:** Start reading in Readest, click entity → see connections → want deeper thinking → open SiYuan ForgeMode

**What Happens:**
- Readest captures journey in `localStorage` (key: `readest_flow_journeys`)
- SiYuan has no access to browser localStorage
- ForgeMode starts from scratch with no context
- User must manually re-enter topic and entities

**What Should Happen:**
- Journey ID passed via URL or backend sync
- SiYuan loads journey context from backend
- ForgeMode pre-populates with entities from reading session
- Seamless handoff preserves all exploration state

**Evidence:**
- `flowModeStore.ts:174-190` — Journey only saved locally to Readest localStorage
- `journeyStorage.ts:37-64` — `saveJourneyToStorage()` uses browser localStorage exclusively
- `ForgeMode.svelte:90-100` — No journey import capability, no backend journey fetch
- `Dashboard.svelte:59-66` — Loads journeys from backend but no Readest sync

**Gap:** No backend journey sync, no cross-app state transfer mechanism.

---

### ❌ Story 2: See Unified Progress
**Scenario:** Reading in Readest creates journey → Open SiYuan Dashboard → Can I see what I explored?

**What Happens:**
- Readest journey exists only in browser localStorage
- SiYuan Dashboard queries backend `/personal/journeys` endpoint
- Backend has no record of Readest journey (never synced)
- Dashboard shows empty or stale journey list

**What Should Happen:**
- Readest auto-syncs completed journeys to backend
- SiYuan Dashboard displays all journeys (Readest + SiYuan)
- Journey cards show source app (Readest icon vs SiYuan icon)
- Click journey card loads full context regardless of origin

**Evidence:**
- `flowModeStore.ts:263-292` — `endJourney()` returns journey but doesn't sync to backend
- `journeyStorage.ts:119-126` — `getUnsyncedJourneys()` exists but never called
- `Dashboard.svelte:145-191` — `apiGet()` only fetches from backend, no localStorage fallback
- No background sync worker, no sync-on-close hook

**Gap:** Journey persistence is **local-only** with no backend sync implementation.

---

### ❌ Story 3: Access Knowledge from Either App
**Scenario:** Concepts created in SiYuan sessions → Open Readest, read new book → Do entity overlays show SiYuan-created concepts?

**What Happens:**
- ForgeMode saves concepts via `POST /concepts` (creates Neo4j nodes)
- Readest entity overlay queries `GET /graph/entities/by-calibre-id/{id}`
- Query returns entities from **book ingestion only**
- User-created concepts from sessions are invisible in Readest

**What Should Happen:**
- Entity overlay query includes user-created concepts
- Concepts created in sessions appear in book overlays
- Clicking user concept shows "Created in session: [link]"
- Bidirectional linking: session → concept, concept → session

**Evidence:**
- `ConceptExtractor.svelte:350-380` — Creates concepts with `source_session_id` but no book linking
- `graph_service.py:218-267` — `get_entities_by_calibre_id()` only queries `Book-[:MENTIONS]->Entity`
- No Cypher pattern for `Session-[:CREATED]->Concept` in entity queries
- Concept nodes exist in graph but unreachable from reading interface

**Gap:** Knowledge graph fragmentation — session concepts and book entities are **two separate universes**.

---

### ✅ Story 4: Handle Backend Unavailable (Partial)
**Scenario:** Backend is down or slow → Open Readest or SiYuan → What happens?

**What Works:**
- Readest: Journey saves to localStorage, gracefully degrades
- Readest: Entity overlay shows cached entities if available
- SiYuan: Dashboard displays backend status (Connected/Disconnected/Checking)
- Both apps show error messages instead of crashing

**What Doesn't Work:**
- No offline queue for failed backend writes
- No automatic retry on backend recovery
- SiYuan sessions cannot start without backend (no offline mode)
- Lost journeys during backend downtime (not synced when it recovers)

**Evidence:**
- `flowModeStore.ts:340-406` — `fetchEntitiesForBook()` sets error state, no retry logic
- `Dashboard.svelte:267-271` — Health check shows status but no recovery workflow
- `ForgeMode.svelte:200-250` — Sessions require backend, no offline cache
- No service worker, no background sync API usage

**Partial Credit:** Error handling exists but recovery workflows missing.

---

## UX Checklist Status

| Item | Status | Evidence |
|------|--------|----------|
| Cross-app navigation is intuitive | ❌ | No handoff mechanism exists |
| Progress syncs automatically | ❌ | Local storage only, no backend sync |
| Session context preserved across apps | ❌ | Zero state transfer between apps |
| Backend failures handled gracefully | ⚠️ | Error messages shown but no recovery |
| No user-visible data loss | ❌ | Journeys lost if browser cleared |
| Consistent visual language | ⚠️ | Design systems diverged (partial fix) |
| Error messages are helpful | ✅ | Clear error states in both apps |

**Score:** 1.5/7 (21%)

---

## Friction Points in Cross-App Workflows

### Critical Friction

1. **Manual Context Re-Entry**
   - User explores 5 entities in Readest
   - Opens SiYuan to do structured thinking
   - Must manually type topic and entities again
   - **Impact:** Breaks flow, high cognitive load, users abandon cross-app workflows

2. **Invisible Journey History**
   - User spends 30 minutes exploring in Readest
   - Journey saved to localStorage only
   - Opens SiYuan Dashboard → no record of exploration
   - **Impact:** Feels like work was lost, reduces trust in system

3. **One-Way Knowledge Graph**
   - User formalizes 3 concepts in SiYuan session
   - Opens Readest to read related book
   - Entity overlay doesn't show user concepts
   - **Impact:** Knowledge graph fragmentation, virtuous cycle broken

### High Friction

4. **No Device Continuity**
   - User reads on iPad (Readest)
   - Opens laptop (SiYuan)
   - Zero state transfer (localStorage is device-local)
   - **Impact:** Multi-device workflow impossible

5. **Backend Downtime = Data Loss**
   - Backend unavailable during reading session
   - Journey captured locally but never synced
   - User closes browser → journey gone forever
   - **Impact:** Unpredictable data loss, system unreliability

6. **No Cross-App Notifications**
   - SiYuan session creates 5 new concepts
   - Readest reading interface has no awareness
   - User doesn't know new knowledge exists
   - **Impact:** Missed opportunities for exploration

### Medium Friction

7. **Visual Inconsistency**
   - Readest: React + Tailwind + custom CSS
   - SiYuan: Svelte + custom SCSS + different color palette
   - Same entity types styled differently
   - **Impact:** Cognitive load, feels like different systems

8. **Duplicate Configuration**
   - Backend URL configured separately in each app
   - Readest: flowModeStore defaults
   - SiYuan: localStorage `ies.backendUrl`
   - **Impact:** Configuration drift, connection failures

---

## Missing Capabilities

### 1. Backend Journey Sync (Critical)

**What's Missing:**
- `POST /journeys` endpoint exists but never called
- No sync worker in Readest
- No "sync now" button for manual sync
- No background sync on page unload

**Impact:** Journey data trapped in browser localStorage.

**Location:**
- `flowModeStore.ts:263-292` — `endJourney()` returns journey locally
- `journeyStorage.ts:119-126` — `getUnsyncedJourneys()` exists but orphaned
- `graphClient.ts:200-220` — `saveJourney()` method exists but never called from store

**Fix Required:**
```typescript
// In flowModeStore.ts endJourney()
const completedJourney = { ...state.currentJourney, endedAt: ... };
saveJourneyToStorage(completedJourney); // Local first
await graphClient.saveJourney(completedJourney); // Then backend
```

---

### 2. Cross-App State Transfer (Critical)

**What's Missing:**
- No URL scheme for passing state (`siyuan://forge?journey=abc123`)
- No shared session storage between apps
- No backend "active session" endpoint
- No QR code handoff for mobile → desktop

**Impact:** Zero state transfer between apps.

**Architecture Gap:**
```
Current:
Readest localStorage → [ NO BRIDGE ] ← SiYuan localStorage

Needed:
Readest → Backend Session API ← SiYuan
        ↓                      ↓
    Journey Sync          Journey Sync
```

---

### 3. Unified Concept Graph (Critical)

**What's Missing:**
- Entity overlay queries ignore user-created concepts
- No `RELATED_TO_BOOK` relationships from session concepts to books
- No UI for "Concepts from your sessions" in entity panel
- No automatic concept linking during ingestion

**Impact:** Session concepts invisible in reading interface.

**Query Gap:**
```cypher
// Current: Only book-ingested entities
MATCH (b:Book)-[:MENTIONS]->(e)
WHERE b.calibre_id = $calibre_id

// Needed: Book entities + user concepts
MATCH (b:Book)-[:MENTIONS]->(e)
WHERE b.calibre_id = $calibre_id
UNION
MATCH (b:Book)<-[:SOURCE_BOOK]-(c:Concept)
WHERE b.calibre_id = $calibre_id
RETURN e.name, e.type, 'book_entity' as origin
UNION
RETURN c.name, c.concept_type, 'user_created' as origin
```

---

### 4. Offline Resilience (High)

**What's Missing:**
- No service worker for offline capability
- No request queue for failed backend writes
- No automatic retry on reconnection
- No "pending sync" UI indicator

**Impact:** Data loss during backend downtime.

**Pattern Needed:**
```typescript
// Queue failed requests
const syncQueue = [];
try {
  await backend.post('/journeys', journey);
} catch (error) {
  syncQueue.push({ endpoint: '/journeys', data: journey });
  showMessage('Saved locally, will sync when online');
}

// Retry on reconnection
window.addEventListener('online', async () => {
  for (const req of syncQueue) {
    await backend.post(req.endpoint, req.data);
  }
});
```

---

### 5. Cross-App Notifications (Medium)

**What's Missing:**
- No WebSocket for real-time updates
- No polling for "new concepts available"
- No badge count on Dashboard for unread journeys
- No desktop notifications

**Impact:** User unaware of knowledge graph changes.

---

### 6. Unified Settings (Low)

**What's Missing:**
- Backend URL configured separately in each app
- User profile exists in backend but not synced to apps
- No central "IES Settings" that both apps share

**Impact:** Configuration drift, manual duplication.

---

## Specific Improvements Needed

### Immediate (P0)

1. **Backend Journey Sync**
   - File: `flowModeStore.ts:263-292`
   - Change: Call `graphClient.saveJourney()` in `endJourney()`
   - Effort: 2 hours
   - Impact: HIGH — Enables cross-app journey visibility

2. **Unified Entity Query**
   - File: `graph_service.py:218-267`
   - Change: UNION query for book entities + session concepts
   - Effort: 4 hours
   - Impact: HIGH — Closes virtuous cycle

3. **Journey Import in ForgeMode**
   - File: `ForgeMode.svelte:90-100`
   - Change: Add "Load from journey" button, fetch journey by ID
   - Effort: 6 hours
   - Impact: HIGH — Enables cross-app context transfer

### Short-Term (P1)

4. **Backend Health Recovery**
   - Files: `flowModeStore.ts`, `Dashboard.svelte`
   - Change: Retry failed requests on reconnection
   - Effort: 8 hours
   - Impact: MEDIUM — Reduces data loss

5. **Cross-App Deep Links**
   - Files: `ForgeMode.svelte`, URL routing
   - Change: Support `siyuan://forge?journey=abc123` URL scheme
   - Effort: 12 hours
   - Impact: MEDIUM — Enables click-to-handoff

6. **Journey Badge in Dashboard**
   - File: `Dashboard.svelte:59-66`
   - Change: Show unread journey count, poll backend
   - Effort: 4 hours
   - Impact: LOW — Improves awareness

### Long-Term (P2)

7. **Service Worker + Offline Queue**
   - Files: New service worker, all API calls
   - Change: Implement offline-first architecture
   - Effort: 40 hours
   - Impact: HIGH — Full offline support

8. **WebSocket Real-Time Sync**
   - Files: Backend WebSocket server, both frontends
   - Change: Push updates when knowledge graph changes
   - Effort: 60 hours
   - Impact: MEDIUM — Real-time collaboration

9. **Unified Settings API**
   - Files: Backend `/settings` endpoint, both apps
   - Change: Central settings storage with app-specific overrides
   - Effort: 20 hours
   - Impact: LOW — Reduces configuration friction

---

## Overall Cross-App UX Grade: D (1.2/4.0)

### Grading Breakdown

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| State Transfer | 0/4 (F) | 30% | 0.00 |
| Progress Visibility | 0.5/4 (F) | 25% | 0.13 |
| Knowledge Integration | 0/4 (F) | 25% | 0.00 |
| Error Resilience | 2/4 (C-) | 10% | 0.20 |
| Visual Consistency | 2.5/4 (C) | 5% | 0.13 |
| Configuration Ease | 2/4 (C-) | 5% | 0.10 |
| **Total** | **1.2/4.0** | **100%** | **D (30%)** |

### Rationale

**State Transfer (0/4):** Zero mechanisms for cross-app state handoff. Journey data trapped in localStorage. Manual re-entry required.

**Progress Visibility (0.5/4):** Journeys invisible across apps. Dashboard shows backend journeys only. Readest journeys never synced.

**Knowledge Integration (0/4):** Session concepts unreachable from reading interface. Graph fragmentation breaks virtuous cycle.

**Error Resilience (2/4):** Error states displayed but no recovery workflows. Data loss during backend downtime.

**Visual Consistency (2.5/4):** Recent design system work improved alignment but inconsistencies remain (entity colors, type badges).

**Configuration Ease (2/4):** Backend URL configured separately in each app. No unified settings.

---

## Critical User Experience Failures

### 1. The Broken Virtuous Cycle

**Documented Promise:**
> "Layer 2 dialogue reveals thinking patterns → Layer 3/4 exploration surfaces concepts → Concepts enrich Layer 1 graph → Next session starts enriched"

**Actual Reality:**
- Readest journeys never reach backend
- SiYuan concepts never reach Readest
- Knowledge graph is **write-only from each app's perspective**
- Users cannot see their own work across apps

**Impact:** The core value proposition is **non-functional**.

---

### 2. Multi-Device Workflow Impossible

**User Expectation:**
- Read on iPad during commute (Readest)
- Continue thinking on laptop at desk (SiYuan)
- Seamless handoff between devices

**Current Reality:**
- Journey trapped in iPad browser localStorage
- Laptop SiYuan has zero context
- User must screenshot entities or email themselves notes

**Impact:** System only works on single device, single app session.

---

### 3. Silent Data Loss

**Failure Mode:**
- User explores for 30 minutes in Readest
- Backend is down (they don't notice)
- Journey saved to localStorage
- User clears browser cache → journey gone

**Impact:** Unpredictable data loss with no warning.

---

## Comparison to Documented Architecture

### What the Docs Say

From `CLAUDE.md`:
> "The Virtuous Cycle: Layer 2 dialogue reveals thinking patterns that personalize Layer 3/4 exploration. Exploration surfaces new concepts and connections. The thinking path becomes formalized concepts that enrich Layer 1. Each cycle deepens both domain understanding and personalization."

From `SYSTEM-DESIGN.md`:
> "Cross-app continuity: Readest and SiYuan share backend state. Journeys sync automatically. Concepts created in sessions appear in reading overlays."

### What Actually Exists

- ❌ No journey sync implementation
- ❌ No cross-app state transfer
- ❌ No unified concept graph query
- ❌ No backend recovery workflow
- ⚠️ Partial visual consistency (recent work)
- ✅ Both apps can connect to backend independently

**Documentation Grade: D** — Architecture diagrams show full integration, implementation delivers isolated apps.

---

## Recommendations

### Tactical (Fix This Week)

1. **Implement Journey Sync** — Add `graphClient.saveJourney()` call to `endJourney()` in Readest
2. **Unified Entity Query** — Update `get_entities_by_calibre_id()` to UNION book + session concepts
3. **Journey Import UI** — Add "Load journey" button to ForgeMode with backend fetch

**Effort:** 12 hours
**Impact:** Closes virtuous cycle gap, enables basic cross-app workflows

### Strategic (Fix This Month)

4. **Offline Queue** — Implement request retry on backend reconnection
5. **Cross-App Deep Links** — Support URL handoff between apps
6. **Journey Badge** — Show unread journey count in SiYuan Dashboard

**Effort:** 24 hours
**Impact:** Reduces data loss, improves cross-app awareness

### Architectural (Future Phase)

7. **Service Worker** — Full offline-first architecture with background sync
8. **WebSocket Sync** — Real-time updates across apps and devices
9. **Unified Settings** — Central backend settings API

**Effort:** 120 hours
**Impact:** Production-ready cross-app experience

---

## Conclusion

Cross-app integration **does not exist** beyond both apps calling the same backend. There is no state sharing, no journey sync, no unified knowledge graph. The documented "four-layer thinking partnership cycle" is **aspirational fiction**.

Users experience two isolated apps that happen to share a database, not an integrated knowledge exploration system.

**Minimum viable fix:** Journey sync + unified entity query (12 hours).
**Production ready:** Full offline support + real-time sync (120+ hours).

Current state is **not shippable** for any user expecting cross-app workflows.

---

**End of Analysis**
