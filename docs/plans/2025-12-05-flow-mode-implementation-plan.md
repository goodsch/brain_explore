# Flow Mode Implementation Plan

**Date:** 2025-12-05
**Source:** Flow mode implementation guide.md (ChatGPT conversation)
**Approach:** Parallel implementation - Codex (backend) + Claude Code (frontend/integration)

## Overview

Flow mode transforms IES from a "pick from menu" system to a "spark-based exploration" system. Key insight: **Flow doesn't start from zero - it starts from a Spark** (current context, highlight, thought).

## Core Concepts

### The Three-Layer Loop
1. **Ephemeral Capture** - Quick capture of sparks without derailing current task
2. **Structured Thinking Session** - Come back to captures, extract meaning with AI prompting
3. **Visual Flow / Exploration** - Graph-based exploration from integrated captures

### Key Data Structures

```typescript
// Spark = live piece of context that Flow latches onto
interface Spark {
  id: string;
  type: 'note' | 'selection' | 'highlight' | 'thought';
  text: string;
  source: {
    type: 'siyuan' | 'readest' | 'phone' | 'assistant';
    noteId?: string;
    blockIds?: string[];
    bookId?: string;
    location?: string;
  };
  capturedAt: string;
}

// CaptureItem = everything captured for later processing
interface CaptureItem {
  id: string;
  rawText: string;
  source: 'phone' | 'siyuan' | 'readest' | 'assistant-interruption';
  capturedAt: string;
  status: 'queued' | 'in_thinking' | 'integrated';
  contextSnippet?: string;
  autoExtracted?: {
    entities: string[];
    topics: string[];
  };
}

// ThinkingSession = structured processing of a capture
interface ThinkingSession {
  id: string;
  captureId: string;
  createdAt: string;
  status: 'active' | 'paused' | 'completed';
  siyuanNoteId: string;
  angles: Array<{
    id: string;
    title: string;
    description: string;
  }>;
  entities: string[];
  breadcrumbs: Breadcrumb[];
}

// FlowSession = visual exploration from thinking session
interface FlowSession {
  id: string;
  origin: {
    type: 'thinking-session-note' | 'spark' | 'concept';
    siyuanNoteId?: string;
    captureId?: string;
    conceptId?: string;
  };
  visitedNodes: string[];
  visitedEdges: string[];
  breadcrumbs: Breadcrumb[];
  insights: string[];
}

// Breadcrumb = single step in exploration journey
interface Breadcrumb {
  id: string;
  timestamp: string;
  nodeId?: string;
  edgeId?: string;
  fromSpark?: string;
  userNote?: string;
  summary?: string;
}
```

## Implementation Phases

### Phase 1: Backend - Capture Queue Service (CODEX)

**Location:** `ies/backend/src/ies_backend/`

**New Files:**
- `schemas/capture.py` - CaptureItem, Spark schemas
- `services/capture_service.py` - Capture queue management
- `api/capture.py` - REST endpoints

**Endpoints:**
```
POST /capture                    - Create capture from any source
GET  /capture?status=queued      - List queued captures (triage view)
GET  /capture/{id}               - Get single capture
PATCH /capture/{id}              - Update status, attach entities
DELETE /capture/{id}             - Remove capture
```

**Database:** Store in Neo4j as `(:CaptureItem)` nodes with relationships to extracted entities.

### Phase 2: Backend - Thinking Session Service (CODEX)

**Location:** `ies/backend/src/ies_backend/`

**New Files:**
- `schemas/thinking.py` - ThinkingSession, Angle schemas
- `services/thinking_service.py` - Session orchestration with LLM
- `api/thinking.py` - REST endpoints

**Endpoints:**
```
POST /thinking/start             - Start session from captureId
GET  /thinking/{id}              - Get session state
POST /thinking/{id}/step         - Record breadcrumb during thinking
POST /thinking/{id}/complete     - Mark session complete
```

**LLM Integration:**
- Extract entities/topics from capture text
- Generate 3-5 "angles" to explore
- Suggest SiYuan note structure
- Create graph connections on completion

### Phase 3: Backend - Flow Session Integration (CODEX)

**Location:** `ies/backend/src/ies_backend/`

**New Files:**
- `schemas/flow_session.py` - FlowSession schema updates
- `services/flow_session_service.py` - Flow session management
- `api/flow_session.py` - REST endpoints

**Endpoints:**
```
POST /flow/openFromSession       - Open Flow from thinking session
POST /flow/{id}/step             - Record step in flow exploration
POST /flow/{id}/synthesize       - Generate synthesis from journey
GET  /flow/{id}/journey          - Get complete journey with breadcrumbs
```

### Phase 4: SiYuan Plugin - Capture UI (CLAUDE CODE)

**Location:** `.worktrees/siyuan/ies/plugin/`

**Components:**
- `components/CaptureQueue.svelte` - Triage view for queued captures
- `components/CaptureCard.svelte` - Individual capture card
- `components/SparkButton.svelte` - Quick capture from selection/note

**Features:**
- "Capture as Spark" command on blocks/selections
- Capture queue sidebar showing pending items
- Status indicators (queued → thinking → integrated)
- Click to start Thinking Session

### Phase 5: SiYuan Plugin - Thinking Session UI (CLAUDE CODE)

**Location:** `.worktrees/siyuan/ies/plugin/`

**Components:**
- `views/ThinkingMode.svelte` - Main thinking session interface
- `components/AngleSelector.svelte` - Choose exploration angles
- `components/ThinkingBreadcrumb.svelte` - Journey visualization

**Features:**
- Start from capture queue item
- Display 3-5 "angles" as clickable strands
- AI-guided prompting during session
- Auto-create SiYuan note with structure
- Connect to existing concepts in graph

### Phase 6: Integration - Flow from Thinking (CLAUDE CODE)

**Updates to:**
- `views/FlowMode.svelte` - Accept thinking session as entry point
- `stores/flowModeStore.ts` - Track origin (spark/thinking/concept)

**Features:**
- "Open in Flow" button after thinking session
- Visual cluster around new concept
- Journey breadcrumbs showing spark → thinking → flow path
- Synthesis button to generate structured note

## Work Division

### CODEX Tasks (Backend Python)
1. ✅ Define Pydantic schemas for Capture, ThinkingSession, FlowSession
2. ✅ Implement CaptureService with Neo4j storage
3. ✅ Implement capture API endpoints
4. ✅ Implement ThinkingService with LLM integration
5. ✅ Implement thinking API endpoints
6. ✅ Implement FlowSessionService updates
7. ✅ Implement flow session API endpoints
8. ✅ Add tests for all services

### CLAUDE CODE Tasks (Frontend TypeScript/Svelte)
1. ✅ Update types/blocks.ts with Capture/Thinking types
2. ✅ Create CaptureQueue.svelte component
3. ✅ Add "Capture as Spark" command
4. ✅ Create ThinkingMode.svelte view
5. ✅ Update FlowMode.svelte for thinking integration
6. ✅ Wire up API calls via forwardProxy
7. ✅ Add journey breadcrumb visualization

## API Contracts

### POST /capture
```json
// Request
{
  "rawText": "Flow doesn't start from zero because I can't start from zero...",
  "source": "assistant-interruption",
  "contextSnippet": "During discussion about IES architecture..."
}

// Response
{
  "id": "capture-1234",
  "rawText": "...",
  "source": "assistant-interruption",
  "capturedAt": "2025-12-05T10:30:00Z",
  "status": "queued",
  "autoExtracted": {
    "entities": ["entry-point-dependence", "choice-paralysis"],
    "topics": ["ADHD", "tool-design"]
  }
}
```

### POST /thinking/start
```json
// Request
{
  "captureId": "capture-1234"
}

// Response
{
  "session": {
    "id": "thinking-9012",
    "captureId": "capture-1234",
    "createdAt": "2025-12-05T14:15:00Z",
    "status": "active",
    "siyuanNoteId": "note-think-entry-point-dependence",
    "angles": [
      {
        "id": "angle-1",
        "title": "Entry-point dependence",
        "description": "Your difficulty initiating when asked to choose from a blank set."
      },
      {
        "id": "angle-2",
        "title": "Tool implications",
        "description": "Why tools must attach to current context instead of starting with a menu."
      }
    ],
    "entities": ["entry-point-dependence", "choice-paralysis"],
    "breadcrumbs": []
  },
  "siyuanTemplateSuggestion": {
    "title": "Thinking – Entry-point dependence (2025-12-05)",
    "headings": [
      "Spark text",
      "Decomposed ideas",
      "Angles to explore",
      "Connections to existing concepts",
      "Insights / reframes"
    ]
  }
}
```

### POST /flow/openFromSession
```json
// Request
{
  "thinkingSessionId": "thinking-9012"
}

// Response
{
  "flowSession": {
    "id": "flow-session-333",
    "origin": {
      "type": "thinking-session-note",
      "siyuanNoteId": "note-think-entry-point-dependence",
      "captureId": "capture-1234"
    },
    "visitedNodes": ["entry-point-dependence"],
    "visitedEdges": [],
    "breadcrumbs": []
  },
  "initialView": {
    "centerNode": "entry-point-dependence",
    "neighborNodes": [
      {"id": "executive-function-initiation", "label": "Executive function: initiation"},
      {"id": "choice-paralysis", "label": "Choice paralysis"}
    ],
    "edges": [
      {"id": "edge-1", "source": "entry-point-dependence", "target": "executive-function-initiation", "type": "relates-to"}
    ],
    "recommendedPaths": [
      {"id": "path-1", "name": "Mechanism Path", "nodes": ["entry-point-dependence", "executive-function-initiation"]}
    ]
  }
}
```

## SiYuan Document Templates

### Thinking Session Note
```markdown
# Thinking – {{concept}} ({{date}})

@meta
- Capture ID:: {{captureId}}
- Thinking Session ID:: {{sessionId}}
- Status:: active
- Spark Source:: {{source}}

---

## Spark text

> {{rawText}}

---

## Decomposed ideas

-

---

## Angles to explore

1. {{angle1.title}} - {{angle1.description}}
2. {{angle2.title}} - {{angle2.description}}

---

## Connections to existing concepts

- [[Concept1]]
- [[Concept2]]

---

## Insights / reframes

-

---

## Next actions / questions

-
```

## Success Criteria

1. **Capture works from multiple sources:** SiYuan selection, Readest highlight, assistant interruption
2. **Zero-friction capture:** Single action to save spark without derailing current task
3. **Thinking sessions produce structure:** Raw capture → decomposed ideas → connected concepts
4. **Flow starts from thinking:** Visual exploration naturally follows from thinking session
5. **Journey is visible:** User can see spark → thinking → flow → synthesis path
6. **Graph is enriched:** New concepts and relationships added to knowledge graph

## Next Steps

1. **Codex:** Start with Phase 1 - Capture Queue backend
2. **Claude Code:** Start with Phase 4 - Capture UI components
3. **Sync point:** After capture works end-to-end
4. **Continue parallel:** Thinking and Flow phases
