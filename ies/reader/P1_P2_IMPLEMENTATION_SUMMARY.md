# P1/P2 Features Implementation Summary

## Overview

Successfully implemented Reader UI integration for P1 (Visit Tracking + Relevant Passages) and P2 (Journey Timeline) backend features.

## Files Created (16 files)

### Type Definitions (1 file)
- **`src/types/api.ts`** (169 lines)
  - VisitScope, NewItemsSummary, NewItemsDetailResponse (Visit Tracking)
  - RankedPassage, PassageRankingRequest, PassageRankingResponse (Passages)
  - TimelineEntryType, TimelineGrouping, JourneyTimelineEntry, TimelineGroup, JourneyTimelineResponse (Timeline)
  - All types match backend Pydantic schemas exactly

### API Clients (2 files)
- **`src/services/visitApi.ts`** (131 lines)
  - `recordVisit()` - Record user visit to scope
  - `getNewItemsSummary()` - Summary of new items
  - `getNewItemsDetail()` - Detailed list of new items
  - `getLastVisit()` - Last visit timestamp
  - `clearVisits()` - Reset tracking (testing)

- **`src/services/timelineApi.ts`** (88 lines)
  - `getTimeline()` - Flexible filtering/grouping
  - `getContextTimeline()` - Timeline for specific context
  - `getUserTimeline()` - Timeline for specific user
  - `getStats()` - Timeline statistics

### API Client Extensions (1 file)
- **`src/services/questionApi.ts`** (Updated, +27 lines)
  - Added `getRelevantPassages()` method for passage ranking
  - Integrates with `/questions/{id}/rank-passages` endpoint

### Components (5 files + 5 CSS)

#### WhatsNewBadge
- **`src/components/flow/WhatsNewBadge.tsx`** (42 lines)
- **`src/components/flow/whats-new-badge.css`** (34 lines)
- Red badge showing count of new items
- Renders nothing if count === 0
- Loading spinner state

#### WhatsNewSection
- **`src/components/flow/WhatsNewSection.tsx`** (212 lines)
- **`src/components/flow/whats-new-section.css`** (156 lines)
- Collapsible groups: Questions, Highlights, Entities, Relationships
- Expandable rows with click-to-expand
- Empty state with refresh button
- Loading spinner

#### RelevantPassagesSection
- **`src/components/flow/RelevantPassagesSection.tsx`** (196 lines)
- **`src/components/flow/relevant-passages-section.css`** (221 lines)
- Ranked passages with relevance scores (0-100%)
- PassageCard subcomponent with expand/collapse
- Source attribution (book, author, chapter, page)
- Keywords matched + concepts mentioned badges
- "Go to passage" button (future: navigation integration)
- Empty state with hint

#### FlowPanelTabs
- **`src/components/flow/FlowPanelTabs.tsx`** (28 lines)
- **`src/components/flow/flow-panel-tabs.css`** (33 lines)
- Tab navigation: "Explore" | "Timeline"
- Active tab indicator with bottom border
- Seamless switching

#### JourneyTimeline
- **`src/components/flow/JourneyTimeline.tsx`** (185 lines)
- **`src/components/flow/journey-timeline.css`** (244 lines)
- Grouped timeline view with grouping selector (by day/week/session/context/flat)
- TimelineGroupView subcomponent with collapsible entries
- Entry type icons (🔍 entity_visit, ❓ question_asked, ✏️ highlight_created, etc.)
- Dwell time tracking
- Source attribution
- Statistics (total entries, time span, entity/question/highlight counts)
- Empty state

### State Management (1 file updated)
- **`src/store/flowStore.ts`** (Updated, +100 lines)
  - P1 state: `newItemsSummary`, `newItemsDetail`, `isLoadingNewItems`, `relevantPassages`, `isLoadingPassages`
  - P1 actions: `recordVisit()`, `fetchNewItemsSummary()`, `fetchNewItemsDetail()`, `clearNewItems()`, `fetchRelevantPassages()`, `clearRelevantPassages()`
  - P2 state: `journeyTimeline`, `isLoadingTimeline`, `activePanelTab`
  - P2 actions: `setActivePanelTab()`, `fetchTimeline()`, `clearTimeline()`

### Integration (2 files updated)
- **`src/components/flow/FlowPanel.tsx`** (Updated, +72 lines)
  - Integrated FlowPanelTabs at top
  - WhatsNewSection renders when `newItemsDetail` exists
  - RelevantPassagesSection renders when `currentQuestionId` is set
  - JourneyTimeline renders when `activePanelTab === 'timeline'`
  - useEffect: Auto-fetch relevant passages when question changes
  - useEffect: Auto-fetch timeline when tab switches to timeline

- **`src/components/flow/index.ts`** (Updated, +5 exports)
  - Exported all new components

### Documentation (2 files)
- **`READER_INTEGRATION_GUIDE.md`** (237 lines)
  - Step-by-step guide for integrating into Reader.tsx
  - Code snippets for imports, hooks, useEffects
  - Testing instructions

- **`P1_P2_IMPLEMENTATION_SUMMARY.md`** (This file)

## Feature Breakdown

### P1: Visit Tracking ("What's New")
1. **Badge on Flow button** - Shows count of new items since last visit
2. **Visit recording** - Records when user opens Flow panel
3. **New items detection** - Compares timestamps to find new questions/highlights/entities/relationships
4. **What's New Section** - Collapsible UI in Flow panel showing detailed new items

### P1: Relevant Passages
1. **Auto-fetch on question select** - Triggers when `currentQuestionId` changes
2. **Passage ranking** - Backend TF-IDF-like algorithm ranks passages by relevance
3. **Keyword/concept matching** - Displays what terms matched in each passage
4. **Relevance scoring** - Visual indicator (0-100%) with opacity scaling
5. **Source attribution** - Book title, author, chapter, page
6. **Expandable text** - Show more/less for long passages

### P2: Journey Timeline
1. **Tab navigation** - Explore vs Timeline modes
2. **Grouped timeline** - By day/week/session/context/flat
3. **Entry type icons** - Visual distinction for 12 entry types
4. **Dwell time tracking** - Shows time spent on each entity
5. **Statistics** - Total entries, unique entities, time span, most active days
6. **Collapsible groups** - Click to expand/collapse timeline groups

## API Integration Points

All features connect to backend APIs defined in CLAUDE.md:

### Visit Tracking API (`/visits`)
- `POST /visits/record` - Record visit
- `GET /visits/new-items-summary/{scope}/{scope_id}` - Summary
- `POST /visits/new-items-detail` - Detailed list
- `GET /visits/last-visit/{scope}/{scope_id}` - Last visit timestamp

### Passage Ranking API (`/questions`)
- `GET /questions/{id}/rank-passages` - Ranked passages for question
  - Query params: `max_passages`, `min_score`, `source_ids`

### Journey Timeline API (`/journey-timeline`)
- `POST /journey-timeline` - Flexible timeline with filters
- `GET /journey-timeline/context/{context_id}` - Context-specific timeline
- `GET /journey-timeline/user/{user_id}` - User-specific timeline
- `GET /journey-timeline/stats` - Timeline statistics

## Data Flow

### Visit Tracking Flow
```
User opens book → Reader.tsx mounts
  ↓
fetchNewItemsSummary('book', calibreId) → visitApi.getNewItemsSummary()
  ↓
Badge displays count (if > 0)
  ↓
User clicks Flow button → toggleFlowPanel()
  ↓
recordVisit('book', calibreId) + fetchNewItemsDetail('book', calibreId)
  ↓
WhatsNewSection renders with detail
```

### Relevant Passages Flow
```
User selects question → setCurrentQuestionId(id)
  ↓
useEffect detects change
  ↓
fetchRelevantPassages(questionId) → questionApi.getRelevantPassages()
  ↓
Backend ranks passages via TF-IDF algorithm
  ↓
RelevantPassagesSection renders with ranked passages
```

### Journey Timeline Flow
```
User clicks Timeline tab → setActivePanelTab('timeline')
  ↓
useEffect detects tab change
  ↓
fetchTimeline() → timelineApi.getTimeline({ grouping: 'by_day' })
  ↓
Backend aggregates ContextJourneyEntry + BreadcrumbJourney + highlights
  ↓
JourneyTimeline renders with grouped entries
```

## State Management Pattern

All features follow Zustand pattern:

```typescript
// State
const { newItemsSummary, isLoadingNewItems, fetchNewItemsSummary } = useFlowStore();

// Actions return void (state updated internally)
useEffect(() => {
  fetchNewItemsSummary('book', calibreId);
}, [calibreId, fetchNewItemsSummary]);

// Components read state directly
<WhatsNewBadge summary={newItemsSummary} />
```

## Component Composition

```
FlowPanel
├── FlowPanelTabs (Explore | Timeline)
├── [Explore Tab]
│   ├── WhatsNewSection (if newItemsDetail exists)
│   ├── QuestionSelector
│   ├── RelevantPassagesSection (if currentQuestionId set)
│   └── Entity/Content Section
└── [Timeline Tab]
    └── JourneyTimeline
```

## CSS Architecture

All components use BEM naming convention:

- Block: `.whats-new-section`
- Element: `.whats-new-section__header`
- Modifier: `.whats-new-section__chevron--expanded`

Color palette matches existing IES design:
- Primary: `#3b82f6` (blue-500)
- Secondary: `#8b5cf6` (purple-500)
- Success: `#10b981` (green-500)
- Danger: `#dc2626` (red-600)
- Gray scale: `#111827` → `#f9fafb`

## Remaining Integration Work

### Required Changes in Reader.tsx

1. **Add import:**
   ```typescript
   import { WhatsNewBadge } from './flow/WhatsNewBadge';
   ```

2. **Add store hooks:**
   ```typescript
   const {
     // ... existing hooks
     newItemsSummary,
     fetchNewItemsSummary,
     fetchNewItemsDetail,
     recordVisit,
   } = useFlowStore();
   ```

3. **Add useEffects:**
   ```typescript
   // Fetch summary on mount for badge
   useEffect(() => {
     if (calibreId) {
       fetchNewItemsSummary('book', String(calibreId));
     }
   }, [calibreId, fetchNewItemsSummary]);

   // Record visit when Flow panel opens
   useEffect(() => {
     if (isFlowPanelOpen && calibreId) {
       recordVisit('book', String(calibreId));
       fetchNewItemsDetail('book', String(calibreId));
     }
   }, [isFlowPanelOpen, calibreId, recordVisit, fetchNewItemsDetail]);
   ```

4. **Update Flow button (line 295-302):**
   ```typescript
   <button
     className={`reader-flow-toggle ${isFlowPanelOpen ? 'active' : ''}`}
     onClick={toggleFlowPanel}
     title="Toggle Flow Mode"
   >
     <Globe size={18} />
     <span className="reader-flow-label">Flow</span>
     <WhatsNewBadge summary={newItemsSummary} />
   </button>
   ```

See `READER_INTEGRATION_GUIDE.md` for complete instructions.

## Testing Checklist

- [ ] Backend running with P1/P2 endpoints
- [ ] Open book in reader
- [ ] Verify What's New badge appears (if items exist)
- [ ] Click Flow button → verify visit recorded
- [ ] Verify What's New section displays
- [ ] Select question → verify Relevant Passages appear
- [ ] Click Timeline tab → verify timeline loads
- [ ] Close and reopen book → verify badge count reflects new items
- [ ] Test on mobile (responsive behavior)
- [ ] Test empty states (no new items, no passages, no timeline)
- [ ] Test loading states (spinners)
- [ ] Test error handling (API failures)

## Performance Considerations

1. **Lazy loading** - Timeline only fetches when tab is active
2. **Passage fetching** - Only fetches when question selected, clears when question deselected
3. **Visit tracking** - Lightweight API calls (summary vs detail)
4. **Component memoization** - Consider adding React.memo to PassageCard if performance issues
5. **Pagination** - Timeline supports offset/limit (not yet implemented in UI)

## Future Enhancements

1. **Passage navigation** - "Go to passage" button should navigate to CFI location
2. **Timeline filtering** - Filter by entry type, date range
3. **Timeline search** - Search within timeline entries
4. **Infinite scroll** - For long timelines
5. **Timeline export** - Export journey history as JSON/markdown
6. **Visit tracking for entities** - Track entity-level visits
7. **Context-aware passages** - Filter passages by current context
8. **Passage bookmarking** - Save passages for later review

## Git Commit Message

```
feat: Add P1/P2 features - visit tracking, relevant passages, journey timeline

Implements Reader UI integration for:
- P1: Visit Tracking API + What's New section
- P1: Passage Ranking API + Relevant Passages section
- P2: Journey Timeline API + Timeline view

New components:
- WhatsNewBadge (red badge on Flow button)
- WhatsNewSection (collapsible new items)
- RelevantPassagesSection (ranked passages with relevance scores)
- FlowPanelTabs (Explore | Timeline navigation)
- JourneyTimeline (grouped timeline with entry type icons)

API clients:
- visitApi (visit tracking)
- timelineApi (journey timeline)
- questionApi extended (passage ranking)

Store enhancements:
- flowStore extended with P1/P2 state and actions

Files created: 16 (5 components + 5 CSS + 3 API clients + 2 docs + 1 types)
Files updated: 4 (flowStore, FlowPanel, questionApi, component index)
```
