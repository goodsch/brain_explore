# Wave 2 Task 2.2 Completion Report

**Date:** 2025-12-06
**Task:** SiYuan Plugin-Backend Integration
**Status:** Complete

---

## Summary

Wired SiYuan plugin to backend APIs for user authentication, journey persistence, and exploration tracking.

---

## Changes Made

### 1. siyuan-structure.ts - Added backend integration functions

**New functions added (lines 1119-1231):**

```typescript
// Device ID generation for anonymous users
function getDeviceId(): string {
    const key = 'ies-siyuan-device-id';
    // localStorage-based persistence
}

// User profile interface
export interface UserProfile {
    user_id: string;
    created_at: string;
    last_active_at: string;
}

// Login via profile service
export async function login(userId?: string): Promise<UserProfile>

// Journey interfaces
export interface JourneyStep {
    entityId: string;
    entityName: string;
    timestamp: string;
    sourcePassage?: string;
    dwellTimeSeconds: number;
}

export interface JourneyData {
    entryPoint: { type: string; reference: string; };
    path: JourneyStep[];
}

// Save journey with schema transformation (camelCase -> snake_case)
export async function saveJourney(journey: JourneyData, userId: string): Promise<SavedJourney>

// Fetch journey history
export async function getJourneyHistory(userId: string, page: number = 1, limit: number = 20)
```

### 2. Dashboard.svelte - Added login flow

**Import updated (line 17):**
```typescript
import { promoteToInsight, getBackendUrl, checkBackendHealth, login } from '../utils/siyuan-structure';
```

**User ID variable (line 30):**
```typescript
let userId: string | null = null;  // Was: const USER_ID = 'chris'
```

**Login on mount (lines 371-379):**
```typescript
// Login to get user ID from profile service
try {
    const profile = await login();
    userId = profile.user_id;
    console.log('[IES] Logged in as:', userId);
} catch (e) {
    console.error('[IES] Login failed, journeys will not be saved:', e);
}
```

**Dynamic journey fetching (line 174):**
```typescript
const journeyEndpoint = userId ? `/journeys/user/${userId}` : null;
```

### 3. FlowMode.svelte - Added journey saving on exit

**New props and imports (lines 13, 18):**
```typescript
import { saveJourney, type JourneyData } from '../utils/siyuan-structure';
export let userId: string | null = null;
```

**Exploration tracking state (lines 31-32):**
```typescript
let explorationTimestamps: string[] = []; // Timestamps for each step
let explorationStartTime: number | null = null; // When exploration began
```

**Timestamp tracking in exploreConcept (lines 208-223):**
- Records exploration start time
- Tracks timestamp for each concept visited
- Handles path truncation on back-navigation

**Journey save on exit (lines 319-354):**
```typescript
async function handleBack() {
    if (explorationPath.length > 0 && userId) {
        const journey: JourneyData = {
            entryPoint: { type: 'siyuan-flow', reference: initialConcept || explorationPath[0] },
            path: explorationPath.map((conceptName, index) => ({
                entityId: conceptName,
                entityName: conceptName,
                timestamp: explorationTimestamps[index],
                dwellTimeSeconds: /* calculated from timestamps */
            }))
        };
        await saveJourney(journey, userId);
    }
    dispatch('back');
}
```

---

## Files Modified

| File | Changes |
|------|---------|
| `ies/plugin/src/utils/siyuan-structure.ts` | Added login, saveJourney, getJourneyHistory, interfaces |
| `ies/plugin/src/views/Dashboard.svelte` | Login on mount, dynamic userId, journey fetching |
| `ies/plugin/src/views/FlowMode.svelte` | userId prop, timestamp tracking, save on exit |

---

## Verification

### Build
```
pnpm build
47 modules transformed
dist/index.css  112.69 kB
dist/index.js   209.50 kB
built in 3.18s
Zip packing done
```

### Integration Pattern

Same pattern as Task 2.1 (IES Reader):
1. Device ID auto-generated and stored in localStorage (`ies-siyuan-device-id`)
2. Login via `/profile/login` endpoint on app mount
3. Journeys saved via `/journeys` endpoint on FlowMode exit
4. Schema transformation: camelCase (frontend) -> snake_case (backend)

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

- **Task 2.3:** Cross-App Sync Design (documentation only)

---

## Notes

- Journeys only save if `explorationPath.length > 0` (prevents empty journeys)
- Entry point type is `siyuan-flow` to distinguish from `reading` (IES Reader)
- Dwell time calculated from timestamps between exploration steps
- Save errors are logged but don't block navigation (graceful degradation)
