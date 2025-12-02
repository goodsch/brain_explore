# IES SiYuan Plugin Design

*Date: 2025-12-01*
*Status: Design Complete, Ready for Implementation*

---

## Overview

A SiYuan plugin for IES (Intelligent Exploration System) Develop mode — Socratic questioning that adapts to the user's cognitive profile, captures insights, and builds a knowledge graph.

**MVP Scope:** Single-mode (Develop) chat interface with session lifecycle management.

**Base:** Fork of [siyuan-plugin-copilot](https://github.com/Achuan-2/siyuan-plugin-copilot) (already cloned to `ies/reference/siyuan-plugin-copilot`)

---

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    SiYuan (Desktop)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              IES Plugin (forked from copilot)        │   │
│  │  ┌─────────────────┐  ┌──────────────────────────┐  │   │
│  │  │  Session Mgmt   │  │     Chat Sidebar         │  │   │
│  │  │  - Start button │  │     - Messages           │  │   │
│  │  │  - End button   │  │     - Streaming          │  │   │
│  │  │  - History      │  │     - Input              │  │   │
│  │  └─────────────────┘  └──────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP (port 8081)
┌────────────────────────────────────────────────────────────┐
│                    IES Backend (existing)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Profile    │  │   Question   │  │   Session        │  │
│  │   Service    │  │   Engine     │  │   Processing     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│                              │                              │
│                              ▼                              │
│                    Claude API (via backend)                 │
└────────────────────────────────────────────────────────────┘
```

**Key decisions:**
- **Direct HTTP** to backend (port 8081) for MVP; WebSocket streaming later
- **Backend proxies Claude** — Question Engine logic stays server-side
- **Explicit session buttons** — Clear user intent for start/end
- **Right sidebar dock** — Persistent, collapsible, matches copilot pattern

---

## Plugin Structure

```
ies/plugin/
├── plugin.json              # Manifest (name: "ies-explorer")
├── src/
│   ├── index.ts             # Plugin entry (dock registration)
│   ├── ies-sidebar.svelte   # Main sidebar (adapted from ai-sidebar)
│   ├── ies-chat.ts          # IES backend client
│   ├── components/
│   │   ├── SessionControls.svelte  # Start/End buttons + status
│   │   ├── ChatMessages.svelte     # Message display
│   │   └── SessionManager.svelte   # History (reuse from copilot)
│   ├── stores/
│   │   └── session.ts       # Session state
│   └── api.ts               # SiYuan API helpers (reuse)
├── i18n/
│   ├── en_US.json
│   └── zh_CN.json
└── package.json
```

**Simplifications from copilot:**
- Remove multi-provider support (IES backend only)
- Remove model selector (backend handles this)
- Remove tool selector (Question Engine handles approach)
- Add session lifecycle controls

---

## API Endpoints

### New Backend Endpoints

```typescript
// Start session - returns context + greeting
POST /session/start
Request:  { user_id: string }
Response: {
  session_id: string,
  profile_summary: string,      // "High pattern-first, capacity 7/10"
  recent_context: string,       // "Last session: explored emotional regulation"
  greeting: string              // AI's opening message
}

// Chat turn - sends message, gets response
POST /session/chat
Request:  { session_id: string, message: string }
Response: SSE stream of AI response chunks

// End session - triggers extraction (existing, may need adaptation)
POST /session/end
Request:  { session_id: string, transcript: Message[] }
Response: {
  doc_id: string,               // SiYuan doc created
  entities_extracted: number,
  summary: string
}
```

### Data Flow

1. User clicks "Start Session"
2. Plugin calls `/session/start` → gets context + greeting
3. User sends message → Plugin calls `/session/chat` → streams response
4. Repeat step 3 for conversation
5. User clicks "End Session"
6. Plugin calls `/session/end` with full transcript
7. Backend extracts entities, creates SiYuan doc, returns summary

---

## Session State

```typescript
// stores/session.ts
interface IESSession {
  id: string | null;
  status: 'idle' | 'active' | 'ending';
  messages: Message[];
  profile: {
    summary: string;
    capacity: number;
  } | null;
  startedAt: number | null;
}

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
}
```

---

## UI Layout

### SessionControls Component

```
┌─────────────────────────────────────────┐
│  IES Develop Mode                       │
├─────────────────────────────────────────┤
│  [Start Session]     (when idle)        │
│  ──────────────────────────────────     │
│  ● Active (12:34)    [End Session]      │
│  Capacity: 7/10                         │
└─────────────────────────────────────────┘
```

### Full Sidebar Layout

```
┌─────────────────────────────────────────┐
│ Header: Mode label + History button     │
├─────────────────────────────────────────┤
│ SessionControls (Start/End + status)    │
├─────────────────────────────────────────┤
│                                         │
│ Chat Messages (scrollable)              │
│   - AI greeting                         │
│   - User message                        │
│   - AI response (streaming)             │
│   - ...                                 │
│                                         │
├─────────────────────────────────────────┤
│ Input: [Type message...] [Send]         │
│ (disabled when session not active)      │
└─────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Fork & Scaffold
- Copy siyuan-plugin-copilot to `ies/plugin/`
- Rename to "ies-explorer", update plugin.json
- Strip multi-provider code, keep single IES provider
- Verify it builds and loads in SiYuan

### Phase 2: Backend Endpoints
- Add `POST /session/start` endpoint
- Add `POST /session/chat` endpoint (streaming)
- Verify `/session/end` works for extraction

### Phase 3: Plugin Integration
- Create `ies-chat.ts` - IES backend client
- Create `SessionControls.svelte` - Start/End buttons
- Wire up session state store
- Connect chat to backend streaming

### Phase 4: Polish
- Handle errors gracefully
- Add loading states
- Test end-to-end flow
- Basic i18n

---

## Reference Materials

Located in `ies/reference/`:
- `siyuan-plugin-copilot/` — Primary reference (full chat plugin)
- `plugin-sample-vite-svelte/` — Official Vite+Svelte template
- `plugin-sample/` — Basic plugin template
- `petal/` — SiYuan frontend API
- `agentpluginresources.md` — Links to docs

---

## Success Criteria

MVP is complete when:
1. Plugin loads in SiYuan as dock sidebar
2. User can start a session (loads profile context)
3. User can chat with streaming responses
4. User can end session (triggers entity extraction)
5. Session history persists across restarts

---

## Future Enhancements (Post-MVP)

- **Explore mode** — Browse knowledgebase, entity pages
- **Synthesize mode** — Build integrated theories
- **WebSocket streaming** — Replace HTTP polling
- **Entity display** — Show entities emerging in sidebar
- **Document integration** — Context from current note
