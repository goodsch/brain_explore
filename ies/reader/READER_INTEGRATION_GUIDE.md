# Reader Integration Guide for P1/P2 Features

This document describes how to integrate the P1/P2 features (What's New, Relevant Passages, Journey Timeline) into the Reader component.

## Changes Required in `src/components/Reader.tsx`

### 1. Add imports

```typescript
import { WhatsNewBadge } from './flow/WhatsNewBadge';
```

### 2. Add store hooks (after line 93)

```typescript
const {
  isFlowPanelOpen,
  setFlowPanelOpen,
  flowPanelWidth,
  startJourney,
  endJourney,
  userId,
  setSyncStatus,
  // Add P1 features
  newItemsSummary,
  fetchNewItemsSummary,
  fetchNewItemsDetail,
  recordVisit,
} = useFlowStore();
```

### 3. Add visit tracking on mount (new useEffect after line 98)

```typescript
// Fetch "What's New" on mount and record visit when Flow panel opens
useEffect(() => {
  if (calibreId) {
    // Fetch summary for badge display
    fetchNewItemsSummary('book', String(calibreId));
  }
}, [calibreId, fetchNewItemsSummary]);

useEffect(() => {
  if (isFlowPanelOpen && calibreId) {
    // Record visit when Flow panel opens
    recordVisit('book', String(calibreId));
    // Fetch detailed items for What's New section
    fetchNewItemsDetail('book', String(calibreId));
  }
}, [isFlowPanelOpen, calibreId, recordVisit, fetchNewItemsDetail]);
```

### 4. Update Flow toggle button (around line 295-302)

Replace the Flow button section with:

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

## Features Implemented

### P1 Features

1. **Visit Tracking**
   - Records when user visits a book via Flow panel
   - Tracks "new since last visit" for questions, highlights, entities

2. **What's New Section**
   - Displays in FlowPanel when items exist
   - Shows collapsible groups: Questions, Highlights, Entities, Relationships
   - Includes refresh button

3. **What's New Badge**
   - Red badge on Flow button showing count of new items
   - Renders nothing if count === 0
   - Shows spinner while loading

4. **Relevant Passages**
   - Automatically fetches when question is selected
   - Displays ranked passages with relevance scores
   - Shows source attribution, keywords matched, concepts mentioned
   - Expandable passage text with "Show more/less"

### P2 Features

1. **Journey Timeline Tab**
   - Tab navigation: "Explore" | "Timeline"
   - Timeline view with grouping options (by day, week, session, context, flat)
   - Entry type icons for visual distinction
   - Dwell time tracking
   - Collapsible groups with statistics

2. **Flow Panel Tabs**
   - Seamless switching between exploration and timeline views
   - Active tab indicator with bottom border
   - Persists state in Zustand store

## API Integration

All features integrate with backend APIs:

- `/visits/*` - Visit tracking endpoints
- `/questions/{id}/rank-passages` - Passage ranking
- `/journey-timeline/*` - Timeline aggregation

## State Management

New Zustand store state (in `flowStore.ts`):

```typescript
// P1: Visit tracking
newItemsSummary: NewItemsSummary | null
newItemsDetail: NewItemsDetailResponse | null
isLoadingNewItems: boolean
recordVisit: (scope, scopeId) => Promise<void>
fetchNewItemsSummary: (scope, scopeId) => Promise<void>
fetchNewItemsDetail: (scope, scopeId, limit?) => Promise<void>

// P1: Relevant passages
relevantPassages: PassageRankingResponse | null
isLoadingPassages: boolean
fetchRelevantPassages: (questionId, maxPassages?) => Promise<void>
clearRelevantPassages: () => void

// P2: Journey timeline
journeyTimeline: JourneyTimelineResponse | null
isLoadingTimeline: boolean
activePanelTab: 'explore' | 'timeline'
setActivePanelTab: (tab) => void
fetchTimeline: (contextId?, grouping?) => Promise<void>
clearTimeline: () => void
```

## Component Exports

All new components are exported from `src/components/flow/index.ts`:

- `WhatsNewBadge`
- `WhatsNewSection`
- `RelevantPassagesSection`
- `FlowPanelTabs`
- `JourneyTimeline`

## CSS Files Created

- `whats-new-badge.css`
- `whats-new-section.css`
- `relevant-passages-section.css`
- `flow-panel-tabs.css`
- `journey-timeline.css`

## Testing

To test the implementation:

1. Open a book in the reader
2. Click the Flow button - should see What's New badge if items exist
3. Open Flow panel - What's New section should display
4. Select a question - Relevant Passages section should appear below
5. Click Timeline tab - should show journey history
6. Close and reopen book - badge count should reflect new items since last visit

## Files Created

### API Clients
- `src/types/api.ts` - Type definitions matching backend schemas
- `src/services/visitApi.ts` - Visit tracking API client
- `src/services/timelineApi.ts` - Journey timeline API client
- `src/services/questionApi.ts` - Extended with passage ranking

### Components
- `src/components/flow/WhatsNewBadge.tsx` + CSS
- `src/components/flow/WhatsNewSection.tsx` + CSS
- `src/components/flow/RelevantPassagesSection.tsx` + CSS
- `src/components/flow/FlowPanelTabs.tsx` + CSS
- `src/components/flow/JourneyTimeline.tsx` + CSS

### Updated Files
- `src/store/flowStore.ts` - Added P1/P2 state and actions
- `src/components/flow/FlowPanel.tsx` - Integrated all new components
- `src/components/flow/index.ts` - Added exports

## Next Steps

1. Update Reader.tsx with the changes outlined in this document
2. Test with backend running (backend must have P1/P2 endpoints active)
3. Verify visit tracking persists across sessions
4. Test responsive behavior on mobile
5. Add error handling for API failures
