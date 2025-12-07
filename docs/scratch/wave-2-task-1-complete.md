# Wave 2 Task 2.1 Completion Report

**Date:** 2025-12-06
**Task:** IES Reader-Backend Integration
**Status:** Complete

---

## Summary

Wired IES Reader to backend APIs for user authentication, journey persistence, and sync status feedback.

---

## Changes Made

### 1. flowStore.ts - Added userId and syncStatus

```typescript
// New state fields
userId: string | null;
syncStatus: SyncStatus;  // 'idle' | 'pending' | 'synced' | 'error'
lastSyncError: string | null;

// New actions
setUserId: (userId: string) => void;
setSyncStatus: (status: SyncStatus, error?: string) => void;
```

### 2. graphClient.ts - Added login and fixed saveJourney

**New methods:**
- `login(userId?: string)` - Calls `/profile/login` with device ID fallback
- `getJourneyHistory(userId, page)` - Fetches journey list

**Fixed:**
- `saveJourney(journey, userId)` - Now transforms camelCase to snake_case
  - `entityId` → `entity_id`
  - `entityName` → `entity_name`
  - `dwellTimeSeconds` → `dwell_time_seconds`
  - `sourcePassage` → `source_passage`

### 3. App.tsx - Added login flow

```typescript
useEffect(() => {
  async function login() {
    const profile = await graphClient.login();
    setUserId(profile.user_id);
  }
  login();
}, []);
```

### 4. Reader.tsx - Wired endJourney to saveJourney

```typescript
const toggleFlowPanel = useCallback(async () => {
  if (isFlowPanelOpen) {
    const journey = endJourney();
    if (journey && journey.path.length > 0 && userId) {
      setSyncStatus('pending');
      try {
        await graphClient.saveJourney(journey, userId);
        setSyncStatus('synced');
      } catch (error) {
        setSyncStatus('error', error.message);
      }
    }
  }
  // ...
});
```

### 5. FlowPanel.tsx - Added sync status indicator

Header now shows:
- ⏳ (pending) - Journey is being saved
- ✓ (synced) - Journey saved successfully
- ⚠ (error) - Save failed (hover for details)

---

## Files Modified

| File | Changes |
|------|---------|
| `ies/reader/src/store/flowStore.ts` | Added userId, syncStatus, setSyncStatus |
| `ies/reader/src/services/graphClient.ts` | Added login(), fixed saveJourney(), added getJourneyHistory() |
| `ies/reader/src/App.tsx` | Added login on mount, loading screen |
| `ies/reader/src/components/Reader.tsx` | Wired toggleFlowPanel to save journey |
| `ies/reader/src/components/flow/FlowPanel.tsx` | Added sync indicator |
| `ies/reader/src/components/flow/FlowPanel.css` | Sync indicator styles |
| `ies/reader/src/App.css` | Loading screen styles |

---

## Verification

### Build
```
✓ TypeScript compiles without errors
✓ Vite build succeeds (149 modules, 573KB bundle)
```

### Backend Tests
```
✓ tests/test_profile.py - 8/8 passed
✓ Journey endpoints verified via curl:
  - POST /journeys - creates journey
  - GET /journeys/user/{user_id} - returns journey list
```

### Manual Testing
```
1. Start backend: cd ies/backend && uv run uvicorn ies_backend.main:app --reload --port 8081
2. Start reader: cd ies/reader && npm run dev
3. Open http://localhost:5174
4. See "Connecting..." while login
5. Select book, open Flow Panel
6. Select text to trigger entity lookup
7. Close Flow Panel - journey saves to backend
8. Verify: curl http://localhost:8081/journeys/user/{device-id}
```

---

## Schema Mapping

| Frontend (camelCase) | Backend (snake_case) |
|---------------------|---------------------|
| `entryPoint` | `entry_point` |
| `entityId` | `entity_id` |
| `entityName` | `entity_name` |
| `dwellTimeSeconds` | `dwell_time_seconds` |
| `sourcePassage` | `source_passage` |

---

## Next Steps

- **Task 2.2:** SiYuan-Backend Integration
- **Task 2.3:** Cross-App Sync Design (documentation only)

---

## Notes

- Device ID is auto-generated and stored in localStorage (`ies-reader-device-id`)
- Journeys only save if `path.length > 0` (prevents empty journeys)
- Sync errors are displayed on hover over the ⚠ indicator
