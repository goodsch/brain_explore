# Quick Capture Design

**Date**: 2025-12-03
**Status**: Design Complete

---

## Overview

Minimal-friction thought capture from iPhone to SiYuan processing queue.

**Core insight**: Capture and processing are separate. Capture must be instant and frictionless. Processing happens later when user has time and context.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CAPTURE                                  │
│  Action Button → Shortcut → Type text → Submit                  │
│                      ↓                    ↓                      │
│              Apple Notes backup    POST to SiYuan API           │
│                                          ↓                      │
│                              Block added to /Capture Inbox      │
└─────────────────────────────────────────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────┐
│                         PROCESS (when ready)                     │
│  Open SiYuan → Plugin Dashboard → Capture Queue                 │
│                      ↓                                          │
│              Tap item → Process button                          │
│                      ↓                                          │
│              AI assistant extracts entities, suggests placement │
│                      ↓                                          │
│              Confirm → Routed to note/concept → Removed from Q  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. iOS Shortcut

**Trigger**: iPhone Action Button

**Flow**:
1. "Ask for Input" → text prompt
2. Append to Apple Notes "Capture Inbox" note (local backup)
3. POST to SiYuan API: `POST /api/block/appendBlock`
4. If success → Show "Captured ✓"
5. If fail → Show "Saved locally, will sync later"

**SiYuan API Call**:
```json
POST /api/block/appendBlock
{
  "parentID": "<capture-inbox-doc-id>",
  "dataType": "markdown",
  "data": "- [ ] {{timestamp}}\n  {{captured_text}}"
}
```

**Backup**: Apple Notes with dedicated "Capture Inbox" note. Shortcuts can append natively. Serves as offline fallback and audit trail.

---

## 2. SiYuan Capture Inbox

**Document**: `/Capture Inbox` (created by plugin on first run)

**Structure**:
```markdown
# Capture Inbox

- [ ] 2025-12-03 14:32
  Just realized acceptance isn't about giving up - connects to metabolization

- [ ] 2025-12-03 13:15
  Look up: Polyvagal theory + window of tolerance relationship

- [ ] 2025-12-02 22:41
  Book recommendation from podcast: "The Body Keeps the Score"
```

Each capture is a task block with:
- Checkbox (unchecked = unprocessed)
- Timestamp
- Raw captured text

---

## 3. Plugin Capture Queue View

**Location**: Dashboard → Capture Queue section (or dedicated tab)

**UI**:
```
┌─────────────────────────────────────────────────┐
│  CAPTURE QUEUE                        [3 items] │
├─────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────┐  │
│  │ "Just realized acceptance isn't about     │  │
│  │  giving up - connects to metabolization"  │  │
│  │  2 min ago                        [Process]│  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │ "Look up: Polyvagal theory + window of    │  │
│  │  tolerance relationship"                  │  │
│  │  1 hour ago                       [Process]│  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │ "Book recommendation from podcast:        │  │
│  │  'The Body Keeps the Score'"              │  │
│  │  Yesterday                        [Process]│  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Behavior**:
- Reads unchecked items from `/Capture Inbox` document
- Shows count badge on Dashboard
- Sorted by timestamp (newest first or oldest first - user preference)

---

## 4. Capture Mode (Processing View)

**Triggered by**: Tap "Process" on queue item

**UI**:
```
┌─────────────────────────────────────────────────────────────────┐
│  PROCESS CAPTURE                                         [Close]│
├─────────────────────────────────────────────────────────────────┤
│  Original:                                                      │
│  "Just realized acceptance isn't about giving up - connects     │
│   to metabolization"                                            │
├─────────────────────────────────────────────────────────────────┤
│  AI Assistant                                                   │
│  ────────────────────────────────────────────────────────────── │
│  I found these entities:                                        │
│  • Acceptance (existing concept)                                │
│  • Metabolization (existing concept)                            │
│                                                                 │
│  Suggested placements:                                          │
│  ○ Append to "Acceptance vs Resignation" note                   │
│  ○ Create new note "Acceptance-Metabolization Connection"       │
│  ○ Just link to both concepts                                   │
│                                                                 │
│  [Ask AI a question...]                                         │
├─────────────────────────────────────────────────────────────────┤
│  [Discard]                                      [Confirm & Route]│
└─────────────────────────────────────────────────────────────────┘
```

**Behavior**:
1. Opens with captured text displayed
2. AI processes: extracts entities, matches to graph, suggests placements
3. User can ask follow-up questions or adjust
4. Confirm → content routed → checkbox marked → removed from queue
5. Discard → checkbox marked → removed from queue (no routing)

---

## 5. Implementation Checklist

### iOS Shortcut (User setup)
- [ ] Create Shortcut "Quick Capture"
- [ ] Add "Ask for Input" action
- [ ] Add "Append to Note" action (Apple Notes backup)
- [ ] Add "Get Contents of URL" action (POST to SiYuan)
- [ ] Add "Show Result" action (confirmation)
- [ ] Assign to Action Button

### SiYuan Plugin
- [ ] Create `/Capture Inbox` document on plugin init (if not exists)
- [ ] Add Capture Queue component to Dashboard
- [ ] Implement queue item rendering (read from Capture Inbox)
- [ ] Add "Process" button per item
- [ ] Create Capture Mode view
- [ ] Integrate AI assistant for entity extraction
- [ ] Implement routing logic (append to note, create note, link)
- [ ] Mark checkbox on complete/discard

---

## 6. API Notes

**SiYuan APIs used**:
- `POST /api/block/appendBlock` - Add capture to inbox
- `GET /api/query/sql` - Query unchecked blocks in inbox
- `POST /api/attr/setBlockAttrs` - Mark checkbox as checked
- `POST /api/block/insertBlock` - Route content to destination

**No backend changes needed** - This design uses SiYuan directly as storage.

---

## 7. Future Enhancements (Parking Lot)

- Voice capture via Shortcut (transcription)
- Image capture with OCR
- Share sheet integration (capture from any app)
- Capture templates (book note, idea, task, etc.)
- Batch processing mode
- Sync indicator showing pending count on home screen widget
