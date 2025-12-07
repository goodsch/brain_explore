# Wave 2 Task 2.3 Completion Report

**Date:** 2025-12-06
**Task:** Cross-App Sync Design
**Status:** Complete

---

## Summary

Designed the cross-app synchronization mechanism for IES Reader and SiYuan Plugin sharing a unified backend.

---

## Deliverable

**Created:** `docs/plans/2025-12-06-cross-app-sync-design.md`

---

## Design Contents

### 1. Sync Protocol Specification
- **What syncs NOW:** Completed journeys, profile changes, entity explorations
- **What syncs LATER:** In-progress journeys, annotations, preferences
- Data flow diagram with both apps → backend → Neo4j

### 2. Conflict Resolution Strategy
- Same entity in both apps: Preserve as separate journey steps with timestamps
- Overlapping journeys: Separate nodes, chronologically sorted
- Device ID collisions: Theoretical only (1 in 2.8 trillion), deferred

### 3. Offline Queue Design
- Separate localStorage queues per app (simpler, safer)
- Retry logic: 3 attempts with exponential backoff (5s → 30s → 2min)
- Queue limits: Max 50 operations, oldest discarded when full
- UI indicators: Sync status badges in both apps

### 4. Event Notification System
- **NOW (Wave 2.3):** On-demand only (refresh button, mount triggers)
- **FUTURE (Wave 3+):** SSE for one-way push notifications
- Trade-off matrix: polling vs WebSocket vs SSE vs on-demand

### 5. Security Considerations
- Device ID privacy: Anonymous by default, no PII
- Rate limiting: Defer to Wave 3 (20 journeys/min recommended)
- App-scoped permissions: Defer to Wave 4

### 6. Cross-App Features (Phase 2+ considerations)
- SiYuan showing Reader journeys with source icons
- Reader resuming SiYuan explorations
- Unified timeline view

---

## Implementation Timeline (From Design)

**Wave 2.3 Implementation Items (16 hours):**
1. Offline queue in IES Reader (4h)
2. Offline queue in SiYuan (3h)
3. Journey history API testing (2h)
4. Cross-app journey display in Dashboard (3h)
5. Integration testing (4h)

**Note:** These are optional enhancements. The core design is complete.

---

## Wave 2 Overall Status

| Task | Status |
|------|--------|
| 2.1 IES Reader-Backend | Complete |
| 2.2 SiYuan-Backend | Complete |
| 2.3 Cross-App Sync Design | Complete |

---

## Next Steps

Wave 2 is complete. Ready for:
- **Wave 3:** Visibility (Journey UI, Question feedback, Cross-app sync implementation)
- **Wave 4:** Learning (Profile updates from sessions, Prompt adaptation)
- **Wave 5:** Quality (Test suites, E2E tests, Documentation)
