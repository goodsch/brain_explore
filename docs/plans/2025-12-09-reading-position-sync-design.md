# Reading Position Sync Design

**Date:** December 9, 2025
**Status:** Design Complete, Ready for Implementation
**Priority:** High (Cross-App Continuity Gap)

## Problem Statement

Users cannot resume reading sessions across applications:
- IES Reader tracks reading position internally (CFI) but doesn't persist to backend
- SiYuan plugin has no visibility into what user is currently reading
- No "Resume Reading" widget to return to books mid-chapter
- Cross-app continuity (Gap #4) partially blocked by missing position sync

## Solution Overview

Extend the existing `ExplorationSession` model to include persistent reading position with CFI (Canonical Fragment Identifier) tracking. Enable SiYuan to display "Currently Reading" / "Resume Reading" widgets with deep links back to Reader.

## Architecture

### 1. Data Model Extension

**Existing Schema** (`syncApi.ts`, lines 14-20):
```typescript
export interface ReadingPosition {
    book_hash: string;
    calibre_id?: number;
    cfi?: string;
    chapter?: string;
    progress_percent?: number;
}
```

**Enhancement Needed** (add to schema):
```typescript
export interface ReadingPosition {
    book_hash: string;
    calibre_id: number;           // Required: single source of truth
    cfi: string;                  // Required: precise location
    chapter?: string;             // Optional: human-readable context
    progress_percent?: number;    // Optional: visual indicator
    page_label?: string;          // Optional: "Page 42 of 300"
    section_title?: string;       // Optional: chapter/section name
    updated_at: string;           // Required: ISO timestamp for recency
}
```

**Backend Session Schema** (Python, mirrors TypeScript):
```python
class ReadingPosition(BaseModel):
    """Book reading position with CFI."""
    book_hash: str
    calibre_id: int
    cfi: str
    chapter: str | None = None
    progress_percent: float | None = None
    page_label: str | None = None
    section_title: str | None = None
    updated_at: str  # ISO 8601 timestamp
```

**Session Store Enhancement** (`session_store.py`):
- Already supports `ExplorationSession` with `reading_position` field
- Redis TTL (24 hours) extends on activity
- Session includes: `app_source`, `current_entity_id`, `journey_path`, `reading_position`

### 2. Position Tracking Hook (IES Reader)

**Location:** `ies/reader/src/hooks/useReadingPosition.ts`

```typescript
import { useCallback, useRef, useEffect } from 'react';
import { useFlowStore } from '../store/flowStore';
import type { Rendition } from 'epubjs';

interface UseReadingPositionOptions {
    calibreId?: number;
    bookTitle?: string;
    debounceMs?: number;
}

export function useReadingPosition(
    rendition: Rendition | null,
    options: UseReadingPositionOptions
) {
    const { setReadingPosition, updateSession } = useFlowStore();
    const { calibreId, bookTitle, debounceMs = 2000 } = options;

    // Debounce timer
    const updateTimerRef = useRef<NodeJS.Timeout | null>(null);

    // Last saved CFI (avoid redundant updates)
    const lastCfiRef = useRef<string | null>(null);

    /**
     * Extract chapter and progress metadata from rendition.
     */
    const extractMetadata = useCallback((cfi: string) => {
        if (!rendition) return {};

        const location = rendition.currentLocation();
        if (!location) return {};

        return {
            chapter: location.start?.displayed?.page || undefined,
            progress_percent: location.start?.percentage
                ? location.start.percentage * 100
                : undefined,
            section_title: location.start?.displayed?.chapter || undefined,
            page_label: location.start?.displayed?.page
                ? `Page ${location.start.displayed.page}`
                : undefined,
        };
    }, [rendition]);

    /**
     * Update reading position with debouncing.
     */
    const updatePosition = useCallback((cfi: string) => {
        if (!calibreId) return;
        if (cfi === lastCfiRef.current) return; // Skip if unchanged

        // Clear existing timer
        if (updateTimerRef.current) {
            clearTimeout(updateTimerRef.current);
        }

        // Debounce: update after 2s of no movement
        updateTimerRef.current = setTimeout(() => {
            const metadata = extractMetadata(cfi);

            setReadingPosition({
                book_hash: String(calibreId),
                calibre_id: calibreId,
                cfi,
                updated_at: new Date().toISOString(),
                ...metadata,
            });

            // Trigger session update to persist to backend
            updateSession();

            lastCfiRef.current = cfi;

            console.log('[Reading Position] Updated:', {
                calibreId,
                cfi,
                ...metadata,
            });
        }, debounceMs);
    }, [calibreId, debounceMs, extractMetadata, setReadingPosition, updateSession]);

    /**
     * Save position immediately (on app close/blur).
     */
    const saveImmediately = useCallback(() => {
        if (updateTimerRef.current) {
            clearTimeout(updateTimerRef.current);
            updateTimerRef.current = null;
        }

        const currentLocation = rendition?.currentLocation();
        if (currentLocation && calibreId) {
            const cfi = currentLocation.start.cfi;
            const metadata = extractMetadata(cfi);

            setReadingPosition({
                book_hash: String(calibreId),
                calibre_id: calibreId,
                cfi,
                updated_at: new Date().toISOString(),
                ...metadata,
            });

            updateSession();
            lastCfiRef.current = cfi;

            console.log('[Reading Position] Saved immediately');
        }
    }, [rendition, calibreId, extractMetadata, setReadingPosition, updateSession]);

    /**
     * Setup: Listen for location changes from epub.js
     */
    useEffect(() => {
        if (!rendition) return;

        const handleLocationChanged = (location: any) => {
            const cfi = location.start?.cfi;
            if (cfi) {
                updatePosition(cfi);
            }
        };

        rendition.on('relocated', handleLocationChanged);

        return () => {
            rendition.off('relocated', handleLocationChanged);
        };
    }, [rendition, updatePosition]);

    /**
     * Cleanup: Save position on unmount, blur, or beforeunload
     */
    useEffect(() => {
        const handleBeforeUnload = () => {
            saveImmediately();
        };

        const handleVisibilityChange = () => {
            if (document.hidden) {
                saveImmediately();
            }
        };

        window.addEventListener('beforeunload', handleBeforeUnload);
        document.addEventListener('visibilitychange', handleVisibilityChange);

        return () => {
            saveImmediately(); // Save on component unmount
            window.removeEventListener('beforeunload', handleBeforeUnload);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
        };
    }, [saveImmediately]);

    return {
        updatePosition,
        saveImmediately,
    };
}
```

**Integration into Reader.tsx** (lines 87-168):

```typescript
// Add after existing hooks (line ~105)
import { useReadingPosition } from '../hooks/useReadingPosition';

// Inside Reader component:
const { updatePosition, saveImmediately } = useReadingPosition(rendition, {
    calibreId,
    bookTitle: title,
    debounceMs: 2000, // 2 seconds
});

// Hook automatically handles position tracking
// No manual calls needed - listens to rendition.on('relocated')
```

### 3. Backend API Enhancement

**New Endpoint:** `GET /sync/sessions/resume` (retrieve resumable sessions)

**Location:** `ies/backend/src/ies_backend/api/flow_session.py` (or new dedicated file)

```python
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Query
from ies_backend.services.session_store import session_store
from ies_backend.schemas.flow_session import ExplorationSession

router = APIRouter()

@router.get("/sync/sessions/resume")
async def get_resumable_sessions(
    user_id: str = Query(..., description="User ID"),
    include_paused: bool = Query(default=True),
    max_age_hours: int = Query(default=48, description="Max session age in hours"),
) -> list[ExplorationSession]:
    """Get active reading sessions for 'Resume Reading' widgets.

    Returns sessions:
    - With reading_position set (calibre_id + cfi)
    - Updated within max_age_hours
    - Status: active or paused (if include_paused=True)
    - Sorted by updated_at desc (most recent first)
    """
    all_sessions = await session_store.list_user_sessions(user_id)

    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

    resumable = []
    for session_summary in all_sessions:
        # Fetch full session data
        session = await session_store.get(session_summary["session_id"])
        if not session:
            continue

        # Filter criteria
        reading_pos = session.get("reading_position")
        if not reading_pos:
            continue
        if not reading_pos.get("calibre_id") or not reading_pos.get("cfi"):
            continue

        status = session.get("status", "active")
        if status == "completed":
            continue
        if status == "paused" and not include_paused:
            continue

        updated_at_str = session.get("last_activity") or session.get("updated_at")
        if updated_at_str:
            updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
            if updated_at < cutoff_time:
                continue

        resumable.append(session)

    # Sort by last_activity desc
    resumable.sort(
        key=lambda s: s.get("last_activity", s.get("updated_at", "")),
        reverse=True
    )

    return resumable
```

**Existing Endpoint:** `PUT /sync/sessions/{session_id}` (already handles reading_position)

- Current implementation in `syncApi.ts` (lines 183-203) supports updating `reading_position`
- Backend `session_store.py` already persists position to Redis with 24h TTL

### 4. SiYuan Resume Reading Widget

**Location:** `.worktrees/siyuan/ies/plugin/src/components/ResumeReadingWidget.svelte`

```svelte
<script lang="ts">
    import { onMount } from 'svelte';
    import { callBackendApi } from '../utils/siyuan-structure';
    import type { ExplorationSession } from '../services/syncService';

    let resumableSessions: ExplorationSession[] = [];
    let isLoading = true;
    let error: string | null = null;

    // User ID (fetch from settings or profile service)
    const userId = 'default_user'; // TODO: Get from actual user profile

    async function fetchResumableSessions() {
        isLoading = true;
        error = null;

        try {
            const response = await callBackendApi({
                endpoint: `/sync/sessions/resume?user_id=${userId}&max_age_hours=48`,
                method: 'GET',
            });

            if (response.ok) {
                resumableSessions = response.data || [];
            } else {
                error = `Failed to fetch sessions: ${response.status}`;
            }
        } catch (err) {
            error = `Error: ${err.message}`;
            console.error('[Resume Reading] Fetch error:', err);
        } finally {
            isLoading = false;
        }
    }

    function formatTimeAgo(isoString: string): string {
        const now = Date.now();
        const updated = new Date(isoString).getTime();
        const diffMs = now - updated;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);

        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return `${Math.floor(diffHours / 24)}d ago`;
    }

    function getReaderDeepLink(session: ExplorationSession): string {
        const pos = session.reading_position;
        if (!pos) return '';

        const baseUrl = window.location.hostname === 'localhost'
            ? 'http://localhost:5173'
            : `http://${window.location.hostname}:5173`;

        // Deep link format: /reader?calibreId={id}&cfi={cfi}
        const cfiEncoded = encodeURIComponent(pos.cfi);
        return `${baseUrl}/reader?calibreId=${pos.calibre_id}&cfi=${cfiEncoded}`;
    }

    function openInReader(session: ExplorationSession) {
        const link = getReaderDeepLink(session);
        if (link) {
            window.open(link, '_blank');
        }
    }

    onMount(() => {
        fetchResumableSessions();

        // Refresh every 5 minutes
        const interval = setInterval(fetchResumableSessions, 5 * 60 * 1000);
        return () => clearInterval(interval);
    });
</script>

<div class="resume-reading-widget">
    <h3 class="widget-header">
        <span class="icon">📖</span>
        Currently Reading
    </h3>

    {#if isLoading}
        <div class="loading">Loading...</div>
    {:else if error}
        <div class="error">{error}</div>
    {:else if resumableSessions.length === 0}
        <div class="empty">No active reading sessions</div>
    {:else}
        <div class="session-list">
            {#each resumableSessions as session}
                {@const pos = session.reading_position}
                <button class="session-card" on:click={() => openInReader(session)}>
                    <div class="book-info">
                        <div class="book-title">{pos.section_title || 'Untitled Book'}</div>
                        <div class="book-meta">
                            {#if pos.chapter}
                                <span class="chapter">{pos.chapter}</span>
                            {/if}
                            {#if pos.progress_percent}
                                <span class="progress">{pos.progress_percent.toFixed(0)}% complete</span>
                            {/if}
                        </div>
                    </div>
                    <div class="session-meta">
                        <span class="time-ago">{formatTimeAgo(session.last_activity || session.updated_at)}</span>
                        <span class="resume-btn">Resume →</span>
                    </div>
                </button>
            {/each}
        </div>
    {/if}
</div>

<style>
    .resume-reading-widget {
        background: var(--b3-theme-surface);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }

    .widget-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 0 0 12px 0;
        font-size: 14px;
        font-weight: 500;
        color: var(--b3-theme-on-surface);
    }

    .icon {
        font-size: 18px;
    }

    .loading, .error, .empty {
        padding: 12px;
        text-align: center;
        color: var(--b3-theme-on-surface-variant);
        font-size: 13px;
    }

    .error {
        color: var(--b3-theme-error);
    }

    .session-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .session-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px;
        background: var(--b3-theme-surface-variant);
        border: 1px solid var(--b3-theme-outline);
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;
        text-align: left;
        width: 100%;
    }

    .session-card:hover {
        background: var(--b3-theme-surface-container-highest);
        border-color: var(--b3-theme-primary);
    }

    .book-info {
        flex: 1;
        min-width: 0;
    }

    .book-title {
        font-weight: 500;
        color: var(--b3-theme-on-surface);
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .book-meta {
        display: flex;
        gap: 12px;
        font-size: 12px;
        color: var(--b3-theme-on-surface-variant);
    }

    .session-meta {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 4px;
    }

    .time-ago {
        font-size: 11px;
        color: var(--b3-theme-on-surface-variant);
    }

    .resume-btn {
        font-size: 12px;
        color: var(--b3-theme-primary);
        font-weight: 500;
    }
</style>
```

**Integration into Dashboard.svelte** (lines 72-74):

```svelte
<script lang="ts">
    import ResumeReadingWidget from '../components/ResumeReadingWidget.svelte';

    // ... existing code ...
</script>

<div class="dashboard-content">
    <!-- Add above recent journeys section -->
    <ResumeReadingWidget />

    <!-- Existing sections -->
    <div class="recent-journeys">...</div>
    <!-- ... -->
</div>
```

### 5. Deep Link Format

**URL Pattern:** `http://localhost:5173/reader?calibreId={id}&cfi={encoded_cfi}`

**Example:** `http://localhost:5173/reader?calibreId=42&cfi=epubcfi(%2F6%2F4%5B...%5D)`

**Reader.tsx Enhancement** (handle query params):

```typescript
// Add to Reader component
import { useSearchParams } from 'react-router-dom';

export function Reader({ url, title, calibreId, onClose }: ReaderProps) {
    const [searchParams] = useSearchParams();
    const initialCfi = searchParams.get('cfi');

    const [location, setLocation] = useState<string | number>(
        initialCfi ? decodeURIComponent(initialCfi) : 0
    );

    // ... rest of component

    useEffect(() => {
        if (initialCfi && rendition) {
            // Navigate to saved CFI on mount
            rendition.display(decodeURIComponent(initialCfi));
            console.log('[Reader] Restored position:', initialCfi);
        }
    }, [initialCfi, rendition]);
}
```

**Router Setup** (if using React Router):

```typescript
// In main routing file
<Route path="/reader" element={
    <Reader
        url={/* derive from query params */}
        calibreId={/* from searchParams.calibreId */}
    />
} />
```

## Implementation Checklist

### Phase 1: Backend Position Persistence (1-2 hours)
- [ ] Enhance `ReadingPosition` schema with required fields (`calibre_id`, `cfi`, `updated_at`)
- [ ] Add `GET /sync/sessions/resume` endpoint to `flow_session.py` router
- [ ] Test endpoint with curl/Postman (create session, update position, retrieve)
- [ ] Verify Redis persistence with TTL extension

### Phase 2: Reader Position Tracking (2-3 hours)
- [ ] Create `useReadingPosition.ts` hook with debouncing
- [ ] Integrate hook into `Reader.tsx` after rendition setup
- [ ] Test debounce behavior (2s delay, immediate save on blur)
- [ ] Verify position updates in Redux DevTools / flowStore state
- [ ] Test CFI restoration on page reload

### Phase 3: SiYuan Widget (2-3 hours)
- [ ] Create `ResumeReadingWidget.svelte` component
- [ ] Implement `fetchResumableSessions()` with backend API call
- [ ] Add time formatting (`formatTimeAgo`) and deep link generation
- [ ] Integrate into `Dashboard.svelte` above recent journeys
- [ ] Test "Resume" button opens Reader at saved CFI

### Phase 4: Deep Link Navigation (1-2 hours)
- [ ] Parse `?calibreId={id}&cfi={cfi}` query params in Reader
- [ ] Set `initialCfi` as starting location for epub.js
- [ ] Test navigation from SiYuan → Reader with CFI restoration
- [ ] Verify cross-device compatibility (localhost vs network IP)

### Phase 5: Testing & Polish (1-2 hours)
- [ ] Test full flow: Reader → position save → SiYuan widget → resume
- [ ] Test edge cases: multiple books, stale sessions, missing CFI
- [ ] Test mobile UX (ResumeReadingWidget responsive layout)
- [ ] Verify session TTL (24h expiry, 48h max age filter)
- [ ] Document usage in `docs/SYSTEM-DESIGN.md`

**Total Estimate:** 7-12 hours

## Success Criteria

1. **Position Persistence:** Reading position saved to Redis with 2s debounce + immediate save on blur
2. **SiYuan Visibility:** Dashboard shows "Currently Reading" widget with book title, progress, time ago
3. **Deep Link Navigation:** Clicking "Resume" opens Reader at exact saved CFI
4. **Cross-Device Support:** Works with localhost and network IP (e.g., iPad on same network)
5. **Session Lifecycle:** Positions expire after 24h inactivity, filtered out after 48h
6. **No Breaking Changes:** Existing ExplorationSession functionality unchanged

## Future Enhancements (Deferred)

1. **Book Cover Thumbnails:** Display cover images in ResumeReadingWidget
2. **Multi-User Support:** User-specific resume sessions (currently uses `default_user`)
3. **Progress Bar:** Visual progress indicator in widget (0-100%)
4. **Last Read Sentence:** Show snippet of last read text for context
5. **Sync Across Devices:** Real-time position sync via WebSocket (currently polling)
6. **Reading Streak Tracking:** Days in a row user has read

## References

**Existing Code:**
- `ies/reader/src/components/Reader.tsx` (lines 157-168) — Current locationChanged handler
- `ies/reader/src/store/flowStore.ts` (lines 79-86, 206, 286) — readingPosition state
- `ies/reader/src/services/syncApi.ts` (lines 14-20, 62-69) — ReadingPosition interface
- `ies/backend/src/ies_backend/services/session_store.py` — Redis session persistence
- `.worktrees/siyuan/ies/plugin/src/views/Dashboard.svelte` (lines 72-74) — Resume sessions state

**Related Design:**
- CFI (Canonical Fragment Identifier) spec: https://idpf.org/epub/linking/cfi/
- epub.js Rendition API: https://github.com/futurepress/epub.js/wiki/
