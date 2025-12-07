# IES Reader Wave 3 Enhancement Design

**Created:** 2025-12-07
**Status:** DRAFT
**Scope:** Mobile optimization + Ingestion queue UI + Notes/annotations UX

---

## Executive Summary

Optimize the IES Reader for mobile-first usage by removing desktop-centric navigation, adding ingestion queue visibility, and implementing touch-friendly annotation workflows.

**Wave Recap:**
- **Wave 1 (COMPLETE):** Library + PWA + Design system
- **Wave 2 (COMPLETE):** Interactive reading (questions, notes, entity overlay, journey breadcrumbs)
- **Wave 3 (this design):** Mobile optimization + queue UI + notes UX refinement

---

## Section 1: Remove Navigation Arrows

**The Problem:**
`react-reader` renders left/right navigation buttons by default. These waste screen space on mobile where swipe gestures are natural. The arrows also create click conflicts with the Flow panel toggle.

**Current State (Reader.tsx:216-233):**
- `ReactReader` component renders default nav buttons
- CSS styles nav buttons but doesn't hide them on mobile
- Swipe gestures already work via epub.js (no code change needed)

**The Solution:**

### 1.1 CSS-Only Hide on Mobile

Add to `Reader.css`:
```css
/* Hide react-reader nav arrows on mobile - swipe instead */
@media (max-width: 767px) {
  .reader-content button[aria-label*="previous"],
  .reader-content button[aria-label*="next"],
  .reader-content button[aria-label*="Previous"],
  .reader-content button[aria-label*="Next"] {
    display: none !important;
  }
}
```

**Why CSS-only?**
- No React component changes needed
- Keeps arrows on desktop for mouse users
- Instant to implement and test

### 1.2 Optional: Tap Zone Toggle (Accessibility)

For users who struggle with swipe gestures, add an optional tap-zone mode in settings:

```tsx
// Reader.tsx - future enhancement
const [useTapZones, setUseTapZones] = useState(false);

// Render invisible tap targets on left/right 20% of screen
{useTapZones && (
  <>
    <div className="reader-tap-zone left" onClick={prevPage} />
    <div className="reader-tap-zone right" onClick={nextPage} />
  </>
)}
```

**Deferred:** This is optional and can be added later if users request it.

---

## Section 2: Ingestion Queue UI

**The Problem:**
Users can queue books for entity extraction (Wave 2 feature: `POST /books/{id}/queue-ingest`) but there's no way to:
- See overall queue progress
- View processing status
- Know when a book is ready for entity overlay

**Backend Status (books.py:178-289):**
- `POST /books/{calibre_id}/queue-ingest` — Queue a book
- `GET /books/ingestion-queue` — List all queued items with status
- `DELETE /books/{calibre_id}/queue-ingest` — Cancel queued item

Queue item schema:
```typescript
interface IngestionQueueItem {
  calibre_id: number;
  title: string;
  author: string;
  queued_at: string;        // ISO timestamp
  status: 'queued' | 'processing' | 'completed' | 'failed';
}
```

**The Solution:**

### 2.1 Queue Status in Library Header

Add a queue indicator pill to `LibraryBrowser.tsx` header:

```tsx
// In header, next to search bar
<button
  className="library-queue-indicator"
  onClick={() => setShowQueueSheet(true)}
>
  <Clock size={16} />
  <span>{queueStats.processing}/{queueStats.total}</span>
</button>
```

Visual states:
- **Empty queue:** Hidden
- **Items queued:** `🕐 3 queued` (neutral)
- **Processing:** `⚙️ 1/3 processing` (pulsing animation)
- **Failed items:** `⚠️ 1 failed` (warning color)

### 2.2 Queue Sheet Component (New)

Create `components/library/IngestionQueueSheet.tsx`:

```tsx
interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export function IngestionQueueSheet({ isOpen, onClose }: Props) {
  const { items, refresh, cancelItem, retryItem } = useIngestionQueue();

  return (
    <Sheet isOpen={isOpen} onClose={onClose}>
      <SheetHeader>
        <h3>Entity Extraction Queue</h3>
        <span className="queue-count">{items.length} books</span>
      </SheetHeader>

      <SheetContent>
        {items.map(item => (
          <QueueItem
            key={item.calibre_id}
            item={item}
            onCancel={() => cancelItem(item.calibre_id)}
            onRetry={() => retryItem(item.calibre_id)}
          />
        ))}
      </SheetContent>
    </Sheet>
  );
}
```

**QueueItem displays:**
- Book title + author
- Status badge with color (queued=gray, processing=blue pulse, completed=green, failed=red)
- Relative time (`queued 5 min ago`)
- Actions: Cancel (if queued), Retry (if failed)

### 2.3 Zustand Store for Queue State

Create `store/ingestionQueueStore.ts`:

```typescript
interface IngestionQueueState {
  items: IngestionQueueItem[];
  isLoading: boolean;
  lastFetch: number | null;

  // Derived stats
  queuedCount: number;
  processingCount: number;
  failedCount: number;

  // Actions
  fetchQueue: () => Promise<void>;
  queueBook: (calibreId: number) => Promise<void>;
  cancelBook: (calibreId: number) => Promise<void>;
  retryBook: (calibreId: number) => Promise<void>;
}
```

### 2.4 Polling Hook

Create `hooks/useIngestionQueue.ts`:

```typescript
export function useIngestionQueue(pollIntervalMs = 10000) {
  const { items, fetchQueue, isLoading } = useIngestionQueueStore();

  useEffect(() => {
    fetchQueue(); // Initial fetch

    const interval = setInterval(() => {
      fetchQueue();
    }, pollIntervalMs);

    return () => clearInterval(interval);
  }, [pollIntervalMs]);

  return { items, isLoading, refresh: fetchQueue };
}
```

### 2.5 BookCard Integration

Update `BookCard.tsx` to show queue status:

```tsx
// Already implemented in Wave 2, enhance with status details
{queueStatus === 'processing' && (
  <div className="book-card-badge book-card-badge-processing">
    <Loader2 size={12} className="animate-spin" />
    Processing...
  </div>
)}

{queueStatus === 'failed' && (
  <button
    className="book-card-badge book-card-badge-failed"
    onClick={handleRetry}
  >
    <AlertCircle size={12} />
    Retry
  </button>
)}
```

---

## Section 3: Mobile Notes & Annotations

**The Problem:**
Current `NotesCapture.tsx` works but isn't optimized for mobile:
- Buried inside FlowPanel (requires opening panel first)
- Small textarea not thumb-friendly
- No quick-capture from reading without opening Flow
- No integration with text selection

**The Solution:**

### 3.1 Floating Action Button (FAB)

Add a mobile-only FAB for quick note capture:

```tsx
// Reader.tsx - add near FlowPanel
{isMobile && (
  <button
    className="reader-fab-note"
    onClick={() => setShowNotesSheet(true)}
    aria-label="Quick capture"
  >
    <PenLine size={24} />
  </button>
)}
```

**CSS positioning:**
```css
.reader-fab-note {
  position: fixed;
  right: var(--ies-space-4);
  bottom: calc(var(--ies-space-4) + env(safe-area-inset-bottom));
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--ies-accent);
  color: white;
  box-shadow: var(--ies-shadow-lg);
  z-index: var(--ies-z-fab);

  /* Only show on mobile */
  display: none;
}

@media (max-width: 767px) {
  .reader-fab-note {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
```

### 3.2 Notes Bottom Sheet

Create `components/flow/NotesSheet.tsx`:

```tsx
export function NotesSheet({ isOpen, onClose }: Props) {
  const { currentEntity, addJourneyStep } = useFlowStore();
  const [noteInput, setNoteInput] = useState('');
  const [noteType, setNoteType] = useState<'thought' | 'question' | 'insight'>('thought');

  return (
    <Sheet isOpen={isOpen} onClose={onClose} snapPoints={['50%', '90%']}>
      <SheetContent>
        {/* Note type chips */}
        <div className="notes-type-chips">
          <Chip active={noteType === 'thought'} onClick={() => setNoteType('thought')}>
            💭 Thought
          </Chip>
          <Chip active={noteType === 'question'} onClick={() => setNoteType('question')}>
            ❓ Question
          </Chip>
          <Chip active={noteType === 'insight'} onClick={() => setNoteType('insight')}>
            💡 Insight
          </Chip>
        </div>

        {/* Large touch-friendly textarea */}
        <textarea
          className="notes-sheet-input"
          placeholder="What are you thinking?"
          value={noteInput}
          onChange={(e) => setNoteInput(e.target.value)}
          rows={4}
          autoFocus
        />

        {/* Context indicator */}
        {currentEntity && (
          <div className="notes-context">
            Connected to: <strong>{currentEntity.name}</strong>
          </div>
        )}

        {/* Submit bar - sticky at bottom */}
        <div className="notes-sheet-footer">
          <button onClick={onClose} className="ies-btn ies-btn-ghost">
            Cancel
          </button>
          <button onClick={handleSubmit} className="ies-btn ies-btn-primary">
            <Send size={16} /> Capture
          </button>
        </div>
      </SheetContent>
    </Sheet>
  );
}
```

### 3.3 Text Selection → Note Integration

When user selects text in epub, offer to capture as note:

```tsx
// Reader.tsx - enhance selection handler
rend.on('selected', (_cfiRange: string, contents: any) => {
  const selection = contents.window.getSelection();
  const selectedText = selection?.toString().trim();

  if (selectedText && selectedText.length > 2) {
    // Show quick action bar above selection
    setSelectionContext({
      text: selectedText,
      position: getSelectionPosition(contents),
    });
  }
});
```

**Selection action bar:**
```tsx
{selectionContext && (
  <div
    className="reader-selection-bar"
    style={{ top: selectionContext.position.top }}
  >
    <button onClick={() => lookupEntity(selectionContext.text)}>
      <Search size={14} /> Look up
    </button>
    <button onClick={() => captureAsNote(selectionContext.text)}>
      <PenLine size={14} /> Note
    </button>
    <button onClick={() => highlightText(selectionContext)}>
      <Highlighter size={14} /> Highlight
    </button>
  </div>
)}
```

### 3.4 Swipe-to-Delete Notes

Add swipe gesture to note items in list:

```css
.notes-captured-item {
  touch-action: pan-x;
  transition: transform 0.2s ease;
}

.notes-captured-item.swiping {
  transform: translateX(var(--swipe-offset));
}

.notes-captured-item-delete {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 80px;
  background: var(--ies-error);
  display: flex;
  align-items: center;
  justify-content: center;
}
```

### 3.5 Offline Note Queue

Extend existing offline queue to handle notes:

```typescript
// services/offlineQueue.ts - add note operations
interface NoteOperation {
  type: 'note';
  data: {
    content: string;
    noteType: 'thought' | 'question' | 'insight';
    entityId?: string;
    entityName?: string;
    bookCalibreId?: number;
    selectedText?: string;
    timestamp: string;
  };
}

// Add to operation union type
type OfflineOperation = JourneyOperation | NoteOperation;
```

---

## Section 4: General Mobile UX Improvements

### 4.1 Touch Target Sizing

Audit and fix all interactive elements:

```css
/* Ensure 44px minimum touch targets */
.ies-btn,
.flow-relationship-link,
.notes-type-chips button,
.library-filter-btn,
.book-card {
  min-height: 44px;
  min-width: 44px;
}

/* Increase tap area without changing visual size */
.flow-section-title button::before {
  content: '';
  position: absolute;
  inset: -8px;
}
```

### 4.2 Safe Area Handling

Already implemented in Reader.css, verify all fixed elements:

```css
/* All fixed/sticky elements need safe areas */
.reader-toolbar {
  padding-top: calc(var(--ies-space-3) + env(safe-area-inset-top));
}

.reader-fab-note,
.notes-sheet-footer {
  padding-bottom: env(safe-area-inset-bottom);
}
```

### 4.3 Bottom Sheet Base Component

Create reusable `Sheet` component for mobile patterns:

```tsx
// components/ui/Sheet.tsx
interface SheetProps {
  isOpen: boolean;
  onClose: () => void;
  snapPoints?: string[];  // e.g., ['25%', '50%', '90%']
  children: React.ReactNode;
}

export function Sheet({ isOpen, onClose, snapPoints = ['50%'], children }: SheetProps) {
  const [currentSnap, setCurrentSnap] = useState(0);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="sheet-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Sheet */}
          <motion.div
            className="sheet"
            initial={{ y: '100%' }}
            animate={{ y: `calc(100% - ${snapPoints[currentSnap]})` }}
            exit={{ y: '100%' }}
            drag="y"
            dragConstraints={{ top: 0 }}
            onDragEnd={handleDragEnd}
          >
            <div className="sheet-handle" />
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
```

### 4.4 Disable Horizontal Scroll in Panels

Prevent swipe conflicts:

```css
.flow-panel,
.notes-sheet,
.queue-sheet {
  overscroll-behavior: contain;
  touch-action: pan-y;
}
```

---

## Section 5: File Structure

**New Files:**
```
ies/reader/src/
├── components/
│   ├── library/
│   │   └── IngestionQueueSheet.tsx      # NEW
│   ├── flow/
│   │   └── NotesSheet.tsx               # NEW
│   └── ui/
│       └── Sheet.tsx                    # NEW: Reusable bottom sheet
├── store/
│   └── ingestionQueueStore.ts           # NEW
├── hooks/
│   └── useIngestionQueue.ts             # NEW
```

**Modified Files:**
```
├── components/
│   ├── Reader.tsx                       # Add FAB, selection bar
│   ├── Reader.css                       # Hide arrows, FAB styles
│   ├── library/
│   │   ├── LibraryBrowser.tsx           # Queue indicator
│   │   ├── LibraryBrowser.css           # Queue indicator styles
│   │   └── BookCard.tsx                 # Enhanced queue status
│   └── flow/
│       ├── NotesCapture.tsx             # Swipe-to-delete
│       └── FlowPanel.css                # Touch target fixes
├── services/
│   └── offlineQueue.ts                  # Add note operations
```

---

## Section 6: Implementation Order

1. **Remove nav arrows** (30 min)
   - Add CSS media query to hide arrows on mobile
   - Test swipe navigation works

2. **Ingestion queue store + hook** (1 hour)
   - Create Zustand store
   - Create polling hook
   - Test with mock data

3. **Queue indicator + sheet** (2 hours)
   - Add header indicator to LibraryBrowser
   - Build IngestionQueueSheet component
   - Wire to store

4. **Sheet base component** (1 hour)
   - Create reusable Sheet with drag behavior
   - Add backdrop and animations

5. **Notes sheet + FAB** (2 hours)
   - Build NotesSheet using Sheet base
   - Add FAB to Reader
   - Connect to existing notes logic

6. **Selection bar** (1 hour)
   - Add selection handler integration
   - Build quick action bar UI

7. **Touch target audit** (30 min)
   - Review all buttons/links
   - Add minimum sizes

8. **Polish & test** (1 hour)
   - Test on actual mobile device
   - Fix edge cases

---

## Dependencies to Add

```json
{
  "dependencies": {
    "framer-motion": "^11.0.0"  // For sheet animations
  }
}
```

Note: `framer-motion` may already be in Readest's shared deps - check before adding.

---

## Success Criteria

- [ ] No navigation arrows visible on mobile (swipe works)
- [ ] Queue indicator shows in library header when items present
- [ ] Can view full queue in bottom sheet
- [ ] FAB visible on mobile for quick note capture
- [ ] Notes sheet opens with large touch-friendly input
- [ ] Text selection shows action bar with Note option
- [ ] All buttons meet 44px minimum touch target
- [ ] Safe areas respected on notched devices
- [ ] Swipe navigation not blocked by panels

---

## Future Considerations (Out of Scope)

- **Haptic feedback** on note capture (requires native integration)
- **Voice-to-text** input for notes
- **Drag-to-reorder** notes list
- **Highlight sync** with SiYuan plugin
- **Reading progress sync** across devices
