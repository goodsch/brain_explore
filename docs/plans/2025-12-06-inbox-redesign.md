# Inbox Redesign: External-First Capture with Collaborative Processing

**Date:** 2025-12-06
**Status:** Design
**Replaces:** Quick Capture System

---

## Core Insight

Captures rarely originate directly in SiYuan. They come from external sources — iOS shortcuts, browser extensions, voice notes — at moments when the user can't process them. The Inbox is the staging area where these captures wait until the user has time and context to process them collaboratively with the AI assistant.

**Design Principle:** Capture is instant and external. Processing is collaborative and contextual.

---

## Renamed Concepts

| Old Name | New Name | Rationale |
|----------|----------|-----------|
| Quick Capture | Inbox | Implies "unprocessed items needing attention," no assumption about source |
| Quick Capture UI | Inbox View | Where items are reviewed and processed |
| Capture Queue | Inbox | Same concept, cleaner name |
| Process button | Process | Opens collaborative dialogue |

---

## Flow Architecture

### External-First Capture

```
EXTERNAL SOURCES (Primary)
├── iOS Shortcuts — "Hey Siri, capture this thought"
├── Browser Extension — Highlight + capture
├── Share Sheet — From any app
├── Voice Notes — Transcribed async
└── Email/SMS forward (future)
        ↓
    POST /inbox (minimal payload)
    {
      text: "raw capture",
      source: "ios_shortcut",
      captured_at: timestamp,
      context?: { url, app, location }
    }
        ↓
    INBOX (Neo4j: InboxItem nodes)
    Status: unprocessed
        ↓
    User opens SiYuan → Inbox View
        ↓
    Selects item → Collaborative Processing
        ↓
    AI dialogue to understand & contextualize
        ↓
    Route to destination (note, concept, journey, new note)
        ↓
    Status: processed → removed from Inbox
```

### Direct Capture (Secondary)

```
SIYUAN (Secondary)
├── Inbox View → "Add" button
├── Keyboard shortcut
└── Right-click → "Send to Inbox"
        ↓
    Same flow as external
```

---

## Inbox View Design

### List View (Default)

```
┌─────────────────────────────────────────────────────────────┐
│ Inbox (3)                                    [+] [Settings] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ "that thing about dopamine and task switching that     │ │
│ │ I read about — seemed important for understanding..."  │ │
│ │                                                        │ │
│ │ 📱 iOS Shortcut • 2 hours ago                          │ │
│ │                                                        │ │
│ │ [Process]  [Explore in Flow]  [···]                    │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ "https://www.nature.com/articles/adhd-research-2024"   │ │
│ │                                                        │ │
│ │ 🌐 Browser • yesterday                                 │ │
│ │ Preview: "New findings on executive function..."       │ │
│ │                                                        │ │
│ │ [Process]  [Explore in Flow]  [···]                    │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ "Book recommendation from Sarah: 'Scattered Minds'"    │ │
│ │                                                        │ │
│ │ 📱 iOS Shortcut • 3 days ago                           │ │
│ │                                                        │ │
│ │ [Process]  [Explore in Flow]  [···]                    │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Source Icons

| Source | Icon | Example |
|--------|------|---------|
| iOS Shortcut | 📱 | Voice capture, quick thought |
| Browser | 🌐 | URL, highlight, article |
| Voice Note | 🎤 | Transcribed audio |
| SiYuan Direct | 📝 | Added from within app |
| Email | ✉️ | Forwarded content |

---

## Collaborative Processing

### Inline Dialogue (Primary)

When user clicks **[Process]**, the item expands into a dialogue:

```
┌─────────────────────────────────────────────────────────────┐
│ Processing                                          [Close] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ "that thing about dopamine and task switching that     │ │
│ │ I read about — seemed important for understanding..."  │ │
│ │ 📱 iOS Shortcut • 2 hours ago                          │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ 🤖 What were you thinking about when you captured this?    │
│    I notice "dopamine" and "task switching" — is this      │
│    about:                                                  │
│    • How ADHD affects focus?                               │
│    • Medication mechanisms?                                │
│    • Strategies you want to try?                           │
│    • Something you read/heard?                             │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ It was from a podcast about why ADHD makes it hard to  │ │
│ │ switch between tasks even when you want to...          │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ 🤖 That sounds like task-switching cost / cognitive        │
│    inertia. I found a related concept in your graph:       │
│                                                             │
│    📊 "Hyperfocus" — 3 connections                         │
│    📊 "Executive Function" — 7 connections                 │
│                                                             │
│    Should I:                                               │
│    • Add this as a note linked to "Executive Function"?    │
│    • Create a new concept "Task Switching Cost"?           │
│    • Save the podcast reference to find later?             │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ [Link to Executive Function]  [Create New Concept]         │
│                                                             │
│ [This needs deeper exploration →]                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Dialogue Principles

1. **AI asks first** — Never assume; ask what the user was thinking
2. **Surface connections** — Show related concepts from the knowledge graph
3. **Offer concrete options** — Not open-ended, but actionable choices
4. **Escape hatch visible** — "This needs deeper exploration" always available

### Complexity Scaling

| Capture Type | Typical Flow | Destination |
|--------------|--------------|-------------|
| **Simple** (quote, quick thought) | 1-2 exchanges → route | Append to existing note |
| **Medium** (needs context) | 2-4 exchanges → clarify → route | New note or concept link |
| **Complex** (sparks curiosity) | Recognize early → "Explore in Flow" | FlowMode session |

---

## "Explore in Flow" Transition

When a capture needs deeper exploration (user clicks or AI suggests):

```
InboxItem
    ↓
Create Spark: { type: 'capture', captureId, rawText }
    ↓
POST /flow/session
    ↓
FlowMode opens with Orientation phase
    ↓
InboxItem.status = 'in_thinking'
    ↓
... FlowMode session ...
    ↓
Synthesis generated
    ↓
InboxItem.status = 'processed' → removed from Inbox
```

The capture becomes the **spark** that ignites the FlowMode session.

---

## Data Model Updates

### InboxItem (renamed from CaptureItem)

```python
class InboxItem(BaseModel):
    id: str
    text: str
    source: InboxSource  # ios_shortcut, browser, voice, siyuan, email
    captured_at: datetime
    status: InboxStatus  # unprocessed, processing, in_flow, processed

    # Source context (optional, depends on source)
    source_context: Optional[SourceContext]

    # Processing dialogue (built up during collaborative processing)
    dialogue: list[DialogueMessage] = []

    # AI-extracted (populated during processing)
    extracted_entities: list[ExtractedEntity] = []
    suggested_placement: Optional[Placement] = None

    # Resolution
    resolved_to: Optional[Resolution] = None  # note_id, concept_id, journey_id
    resolved_at: Optional[datetime] = None
```

### InboxStatus

```python
class InboxStatus(str, Enum):
    UNPROCESSED = "unprocessed"  # Just arrived, waiting
    PROCESSING = "processing"    # User opened dialogue
    IN_FLOW = "in_flow"          # Escalated to FlowMode
    PROCESSED = "processed"      # Routed to destination
```

### DialogueMessage

```python
class DialogueMessage(BaseModel):
    role: Literal["assistant", "user"]
    content: str
    timestamp: datetime
    suggestions: Optional[list[Suggestion]] = None  # For assistant messages
```

---

## API Endpoints

### Inbox CRUD

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/inbox` | Create new inbox item (from external source) |
| GET | `/inbox` | List inbox items (filterable by status) |
| GET | `/inbox/{id}` | Get single item with dialogue history |
| DELETE | `/inbox/{id}` | Remove item (after processing or manual archive) |

### Processing

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/inbox/{id}/message` | Add user message to dialogue |
| POST | `/inbox/{id}/process` | Trigger AI response in dialogue |
| POST | `/inbox/{id}/resolve` | Mark as processed with destination |
| POST | `/inbox/{id}/to-flow` | Escalate to FlowMode |

---

## External Source Integration

### iOS Shortcuts

```
Shortcut: "Capture Thought"
1. Show input prompt: "What's on your mind?"
2. Get text input
3. POST to https://api.ies.local/inbox
   {
     "text": [input],
     "source": "ios_shortcut",
     "source_context": {
       "device": "iPhone",
       "location": [optional]
     }
   }
4. Show confirmation: "Saved to Inbox"
```

### Browser Extension (Future)

```javascript
// On highlight + keyboard shortcut
chrome.runtime.sendMessage({
  action: 'capture',
  text: window.getSelection().toString(),
  url: window.location.href,
  title: document.title
});

// Background script POSTs to /inbox
```

### Voice Capture (Future)

```
1. iOS Shortcut records voice
2. Whisper API transcribes
3. POST to /inbox with source: "voice"
4. Include audio_url for playback during processing
```

---

## Implementation Phases

### Phase 1: Rename & Restructure (1-2 days)
- [ ] Rename QuickCapture.svelte → Inbox.svelte
- [ ] Update schemas: CaptureItem → InboxItem
- [ ] Update API routes: /capture → /inbox
- [ ] Update CLAUDE.md and docs

### Phase 2: External Source Support (2-3 days)
- [ ] iOS Shortcut template creation
- [ ] Test POST /inbox from external sources
- [ ] Source icon display in Inbox view

### Phase 3: Collaborative Processing UI (3-5 days)
- [ ] Inline dialogue expansion
- [ ] AI first-message generation
- [ ] User response input
- [ ] Graph entity matching display
- [ ] Placement option buttons

### Phase 4: Resolution Routing (2-3 days)
- [ ] "Link to concept" action
- [ ] "Create new note" action
- [ ] "Append to note" action
- [ ] Status transition to processed

### Phase 5: FlowMode Integration (1-2 days)
- [ ] "Explore in Flow" button
- [ ] Spark creation from InboxItem
- [ ] Status sync (in_flow → processed)

---

## Success Metrics

- **Capture latency:** < 2 seconds from thought to saved
- **Processing completion:** > 80% of items processed within 48 hours
- **Flow escalation:** ~20% of items warrant deeper exploration
- **Zero friction:** No required fields at capture time

---

## Open Questions

1. **Dialogue persistence:** Keep full dialogue history or just final resolution?
2. **Bulk operations:** Select multiple items for batch archive/delete?
3. **Notification:** Alert when Inbox has items waiting > 24 hours?
4. **Offline capture:** Queue on device, sync when connected?
