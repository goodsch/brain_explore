# IES Architecture & User Interaction Maps

**Created:** 2025-12-09
**Purpose:** Complete system architecture and user interaction documentation

> **Ground Truth:** This document covers technical structure. For conceptual foundations (why, operating model, semantics), see `docs/IES-SYSTEM-DESIGN.md`.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Layer 1: Knowledge Graph](#2-layer-1-knowledge-graph)
3. [Layer 2: Backend APIs](#3-layer-2-backend-apis)
4. [Layer 3: SiYuan Plugin](#4-layer-3-siyuan-plugin)
5. [Layer 4: IES Reader](#5-layer-4-ies-reader)
6. [Data Flow Diagrams](#6-data-flow-diagrams)
7. [User Interaction Maps](#7-user-interaction-maps)
8. [State Management](#8-state-management)
9. [API Reference](#9-api-reference)

---

## 1. System Overview

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACES                                  │
├─────────────────────────────────┬────────────────────────────────────────────┤
│      LAYER 4: IES READER        │         LAYER 3: SIYUAN PLUGIN             │
│  ┌─────────────────────────┐    │    ┌──────────────────────────────┐        │
│  │    LibraryBrowser       │    │    │         Dashboard            │        │
│  │  ┌───────────────────┐  │    │    │   ┌────────┬────────────┐    │        │
│  │  │  BookCard Grid    │  │    │    │   │ Stats  │ Suggestions│    │        │
│  │  └───────────────────┘  │    │    │   └────────┴────────────┘    │        │
│  └─────────────────────────┘    │    └──────────────────────────────┘        │
│  ┌─────────────────────────┐    │    ┌──────────────────────────────┐        │
│  │      Reader + Flow      │    │    │         ForgeMode            │        │
│  │  ┌────────┬──────────┐  │    │    │   ┌────────────────────┐     │        │
│  │  │  EPUB  │FlowPanel │  │    │    │   │ 5 Thinking Modes   │     │        │
│  │  │ Viewer │ Entity   │  │    │    │   │ Template Sessions  │     │        │
│  │  │        │ Panel    │  │    │    │   │ Question Engine    │     │        │
│  │  └────────┴──────────┘  │    │    │   └────────────────────┘     │        │
│  └─────────────────────────┘    │    └──────────────────────────────┘        │
│  ┌─────────────────────────┐    │    ┌──────────────────────────────┐        │
│  │     Mobile: FlowPage    │    │    │          FlowMode            │        │
│  │  ┌───────────────────┐  │    │    │   ┌────────────────────┐     │        │
│  │  │ QuestionSelector  │  │    │    │   │ Entity Navigation  │     │        │
│  │  │ NotesSheet        │  │    │    │   │ Facet Decomposition│     │        │
│  │  └───────────────────┘  │    │    │   │ Trail Breadcrumbs  │     │        │
│  └─────────────────────────┘    │    │   └────────────────────┘     │        │
│                                 │    └──────────────────────────────┘        │
├─────────────────────────────────┴────────────────────────────────────────────┤
│                           LAYER 2: BACKEND APIs                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │   Graph API  │ │  Context API │ │ Question API │ │ Question     │        │
│  │  /graph/*    │ │  /context/*  │ │ /questions/* │ │ Engine API   │        │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │  Journey API │ │  Books API   │ │ Reframe API  │ │ Personal API │        │
│  │  /journeys/* │ │  /books/*    │ │ /reframes/*  │ │ /personal/*  │        │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘        │
├──────────────────────────────────────────────────────────────────────────────┤
│                       LAYER 1: KNOWLEDGE GRAPH                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                           Neo4j Database                                │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │  │
│  │  │  Domain Graph   │  │  Personal Graph │  │    Calibre      │         │  │
│  │  │  (Book Entities)│  │  (ADHD-Friendly)│  │    (179 Books)  │         │  │
│  │  │  ~300 entities  │  │  Sparks/Insights│  │    SQLite       │         │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘         │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Layer 4** | React + Vite + epub.js + Zustand | IES Reader PWA |
| **Layer 3** | TypeScript + Svelte + SiYuan API | SiYuan Plugin |
| **Layer 2** | FastAPI + Python 3.11 | Backend APIs |
| **Layer 1** | Neo4j + SQLite (Calibre) | Knowledge Graph |
| **Infra** | Docker Compose | Neo4j, Qdrant |

---

## 2. Layer 1: Knowledge Graph

### Component Architecture

```
library/graph/
├── Domain Knowledge (Books)
│   ├── entities.py          # Entity extraction from text
│   ├── neo4j_client.py      # Neo4j connection wrapper
│   └── unified_client.py    # Unified graph operations
│
├── Personal Knowledge (ADHD-Friendly)
│   ├── adhd_ontology.py     # Entity types, relationships, signals
│   └── adhd_graph_client.py # Personal graph operations
│
├── Reframes
│   ├── reframe_generator.py # LLM-based metaphor generation
│   └── reframe_mapper.py    # Reframe-to-concept mapping
│
└── Conversations
    └── conversation_parser.py # Parse Claude exports
```

### Entity Types

```
DOMAIN ENTITIES (from books)          PERSONAL ENTITIES (ADHD-friendly)
┌─────────────────────────┐           ┌─────────────────────────┐
│ • Concept               │           │ • Spark (raw resonance) │
│ • Theory                │           │ • Insight (processed)   │
│ • Framework             │           │ • Thread (exploration)  │
│ • Mechanism             │           │ • Favorite Problem      │
│ • Person                │           │                         │
│ • Book                  │           │ Metadata:               │
│ • Assessment            │           │ • Resonance signal      │
│ • Pattern               │           │ • Energy level          │
│ • Distinction           │           │ • Status lifecycle      │
└─────────────────────────┘           └─────────────────────────┘
```

### Neo4j Schema

```cypher
// Domain Entities
(:Book {calibre_id, title, author, processing_status})
(:Concept {name, type, description})
(:Person {name, field})
(:Theory {name, description})
(:Framework {name, components})

// Relationships
(b:Book)-[:MENTIONS]->(e:Entity)
(c1:Concept)-[:SUPPORTS|CONTRADICTS|COMPONENT_OF]->(c2:Concept)
(p:Person)-[:DEVELOPED]->(t:Theory)

// Personal Graph
(:Spark {title, content, resonance_signal, energy_level, status})
(:Insight {title, content, source_id})
(:Thread {title, description})
(:FavoriteProblem {question, status})

(s:Spark)-[:LED_TO_DISCOVERY]->(i:Insight)
(i:Insight)-[:ADDRESSES_PROBLEM]->(fp:FavoriteProblem)
```

---

## 3. Layer 2: Backend APIs

### Service Architecture

```
ies/backend/src/ies_backend/
├── api/                          # FastAPI Routers
│   ├── graph.py                  # Entity search, facets, evidence
│   ├── questions.py              # Question CRUD + answer blocks
│   ├── context.py                # Context CRUD
│   ├── question_engine.py        # Adaptive question generation
│   ├── journey.py                # Breadcrumb tracking
│   ├── books.py                  # Calibre integration
│   ├── reframe.py                # Metaphor generation
│   ├── personal.py               # ADHD-friendly capture
│   ├── template.py               # Thinking templates
│   ├── session.py                # Dialogue sessions
│   ├── sync.py                   # Cross-app sync
│   └── conversations.py          # Claude export parsing
│
├── services/                     # Business Logic
│   ├── graph_service.py          # Neo4j operations
│   ├── question_service.py       # Question management
│   ├── context_crud_service.py   # Context management
│   ├── calibre_service.py        # Calibre library access
│   ├── reframe_service.py        # LLM reframe generation
│   ├── personal_graph_service.py # Personal knowledge ops
│   ├── template_service.py       # Template loading/execution
│   ├── journey_service.py        # Journey persistence
│   ├── extraction_service.py     # Entity extraction
│   └── neo4j_client.py           # Database connection
│
└── schemas/                      # Pydantic Models
    ├── graph.py                  # Entity, Facet, Evidence
    ├── question.py               # Question, AnswerBlock
    ├── context.py                # Context, ContextType
    ├── question_engine.py        # QuestionClass, ClassifiedQuestion
    ├── journey.py                # JourneyEntry, JourneyStep
    ├── reframe.py                # Reframe, ReframeType
    ├── personal.py               # Spark, Insight, Thread
    └── template.py               # ThinkingTemplate, Section
```

### API Endpoint Map

```
/api/v1/
├── /graph/
│   ├── GET  /entity/{name}                    # Get entity details
│   ├── GET  /entity/{name}/facets             # Get/generate facets
│   ├── GET  /entity/{name}/evidence           # Get evidence passages
│   ├── GET  /entities/by-calibre-id/{id}      # Entities for book
│   ├── POST /entity                           # Create from exploration
│   └── GET  /search?q=                        # Search entities
│
├── /questions/
│   ├── GET  /                                 # List questions
│   ├── POST /                                 # Create question
│   ├── GET  /{id}                             # Get question
│   ├── PATCH /{id}                            # Update question
│   ├── DELETE /{id}                           # Delete question
│   ├── GET  /{id}/answers                     # List answers
│   └── POST /{id}/answers                     # Add answer block
│
├── /context/
│   ├── GET  /                                 # List contexts
│   ├── POST /                                 # Create context
│   ├── GET  /{id}                             # Get context
│   ├── PATCH /{id}                            # Update context
│   └── DELETE /{id}                           # Delete context
│
├── /question-engine/
│   ├── POST /detect-state                     # Detect cognitive state
│   ├── POST /select-approach                  # Select inquiry approach
│   ├── POST /generate-questions               # Generate adapted questions
│   ├── GET  /question-classes                 # List 9 question classes
│   └── GET  /approach-classes                 # Approach→class mappings
│
├── /books/
│   ├── GET  /                                 # List Calibre books
│   ├── GET  /{calibre_id}                     # Get book details
│   ├── GET  /{calibre_id}/cover               # Get cover image
│   └── GET  /{calibre_id}/file                # Serve epub/pdf
│
├── /reframes/
│   ├── GET  /concepts/{id}/reframes           # Get reframes
│   ├── POST /concepts/{id}/reframes/generate  # Generate reframes
│   └── POST /reframes/{id}/feedback           # Vote helpful/confusing
│
├── /personal/
│   ├── POST /sparks                           # Create spark
│   ├── GET  /sparks/{id}                      # Get spark
│   ├── POST /sparks/{id}/visit                # Record visit
│   ├── POST /sparks/{id}/promote              # Promote to insight
│   ├── GET  /sparks/by-resonance/{signal}     # Find by emotion
│   ├── GET  /sparks/by-energy/{level}         # Find by energy
│   └── GET  /stats                            # Personal graph stats
│
├── /journeys/
│   ├── GET  /                                 # List journeys
│   ├── POST /                                 # Create journey
│   ├── GET  /{id}                             # Get journey
│   ├── POST /{id}/steps                       # Add step
│   └── PATCH /{id}/end                        # End journey
│
├── /templates/
│   └── GET  /{template_id}                    # Get thinking template
│
└── /sync/
    ├── POST /reader-to-siyuan                 # Sync reader → SiYuan
    └── POST /siyuan-to-reader                 # Sync SiYuan → reader
```

---

## 4. Layer 3: SiYuan Plugin

### Component Architecture

```
ies/plugin/src/
├── views/                        # Main UI Views
│   ├── Dashboard.svelte          # Stats, suggestions, recent
│   ├── ForgeMode.svelte          # 5 thinking mode sessions
│   ├── FlowMode.svelte           # Entity exploration
│   ├── QuickCapture.svelte       # Fast content capture
│   └── Inbox.svelte              # Capture queue processing
│
├── components/                   # Reusable Components
│   ├── ConceptExtractor.svelte   # 4-step concept wizard
│   ├── EvidenceSection.svelte    # Evidence display
│   ├── ReframesTab.svelte        # Reframe display/voting
│   ├── AddFacetForm.svelte       # Add new facet
│   ├── SessionControls.svelte    # Session start/stop
│   └── SessionManager.svelte     # Session history
│
├── stores/                       # Svelte Stores
│   └── (state management)
│
├── services/                     # API Clients
│   └── (backend communication)
│
├── utils/                        # Utilities
│   └── siyuan-structure.ts       # Folder creation, doc saving
│
├── api.ts                        # Backend API client
├── ies-chat.ts                   # Chat interface
├── ies-sidebar.svelte            # Main sidebar entry
└── index.ts                      # Plugin entry point
```

### ForgeMode: 5 Thinking Modes

```
┌─────────────────────────────────────────────────────────────────┐
│                        FORGEMODE                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│
│  │ LEARNING │ │ARTICULAT-│ │ PLANNING │ │ IDEATING │ │REFLECT-││
│  │          │ │   ING    │ │          │ │          │ │  ING   ││
│  │ Mechanism│ │ Clarify  │ │ Project  │ │ Creative │ │ Review ││
│  │   Map    │ │Intuition │ │  Plan    │ │ Brainstorm│ │Session ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘│
│                                                                  │
│  Template-Driven Sessions:                                       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. Select Mode → Load Template                              ││
│  │ 2. Section-by-Section Progress                              ││
│  │ 3. Question Engine Integration (9 classes)                  ││
│  │ 4. Session Document Auto-Save to /Sessions/{mode}/          ││
│  │ 5. Entity Extraction → Concept Formalization                ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### FlowMode: Entity Exploration

```
┌─────────────────────────────────────────────────────────────────┐
│                        FLOWMODE                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Trail: [ADHD] → [Physiology] → [Dopamine]                      │
│  ─────────────────────────────────────────                      │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ FOCUS: Dopamine                                    [Concept]││
│  │                                                              ││
│  │ Description: Neurotransmitter involved in reward...         ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ FACETS:                                                     ││
│  │ [Function ✓] [Pathways ✓] [Medications] [Deficiency]        ││
│  │                                                              ││
│  │ ✓ = exists in graph   (click to navigate)                   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ RELATED QUESTIONS:                                          ││
│  │ • Why does ADHD affect dopamine levels?                     ││
│  │ • How do stimulants increase dopamine?                      ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ EVIDENCE: (3 passages)                                      ││
│  │ • "Stolen Focus" p.42: "Dopamine plays a crucial..."        ││
│  │ • "ADHD 2.0" p.87: "The dopamine hypothesis..."             ││
│  │   [Open in Reader]  [Add to Note]                           ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  [Expand Facet]  [View Reframes]  [Add Note]                    │
└─────────────────────────────────────────────────────────────────┘
```

### SiYuan Folder Structure (Auto-Created)

```
/IES Notebook/
├── /Daily/                    # Daily log (zero-friction capture)
├── /Seedlings/                # 7 subcategories for growing ideas
│   ├── /Observations/
│   ├── /Questions/
│   ├── /Connections/
│   ├── /Hunches/
│   ├── /Contradictions/
│   ├── /Patterns/
│   └── /Experiments/
├── /Sessions/                 # ForgeMode session documents
│   ├── /Learning/
│   ├── /Articulating/
│   ├── /Planning/
│   ├── /Ideating/
│   └── /Reflecting/
├── /Flow_Maps/                # Flow exploration maps
├── /Concepts/                 # Formalized concepts
├── /Insights/                 # Promoted insights
├── /Favorite_Problems/        # Anchor questions
├── /Projects/                 # Project contexts
├── /Archive/                  # Completed/archived
└── /System/                   # Templates + examples
    ├── /Templates/
    └── /Example_Notes/
```

---

## 5. Layer 4: IES Reader

### Component Architecture

```
ies/reader/src/
├── App.tsx                       # Main app, routing
├── main.tsx                      # Entry point
│
├── components/
│   ├── Reader.tsx                # epub.js wrapper
│   │
│   ├── library/                  # Library Browser
│   │   ├── LibraryBrowser.tsx    # Book grid + search
│   │   ├── BookCard.tsx          # Individual book card
│   │   ├── SearchBar.tsx         # Search interface
│   │   └── IngestionQueueSheet.tsx # Queue status
│   │
│   ├── flow/                     # Flow Exploration
│   │   ├── FlowPanel.tsx         # Side panel container
│   │   ├── QuestionSelector.tsx  # Question dropdown
│   │   ├── NotesSheet.tsx        # Note capture sheet
│   │   ├── NotesCapture.tsx      # Mobile FAB
│   │   ├── InteractiveQuestions.tsx # Question display
│   │   └── JourneyBreadcrumb.tsx # Trail display
│   │
│   └── ui/
│       └── Sheet.tsx             # Bottom sheet component
│
├── hooks/
│   ├── useFlowLayout.ts          # Responsive mode detection
│   ├── useEntityLookup.ts        # Entity search
│   ├── useEntityHighlighter.ts   # Text highlighting
│   ├── useEntityOverlay.ts       # Overlay management
│   ├── useQuestionSync.ts        # Question sync
│   └── useIngestionQueue.ts      # Queue management
│
├── services/
│   ├── graphClient.ts            # Backend API client
│   ├── questionApi.ts            # Question CRUD
│   ├── contextApi.ts             # Context CRUD
│   ├── syncApi.ts                # Cross-app sync
│   └── offlineQueue.ts           # Offline support
│
└── store/
    ├── flowStore.ts              # Main Zustand store
    └── ingestionQueueStore.ts    # Queue state
```

### Reader Layout Modes

```
DESKTOP (>1024px)                    MOBILE (<640px)
┌─────────────────────────────┐      ┌─────────────────────┐
│ ┌───────────┬─────────────┐ │      │                     │
│ │           │             │ │      │     EPUB READER     │
│ │   EPUB    │   FLOW      │ │      │                     │
│ │  READER   │   PANEL     │ │      │                     │
│ │           │             │ │      │                     │
│ │           │ • Entity    │ │      │   [FAB: Notes]      │
│ │           │ • Questions │ │      └─────────────────────┘
│ │           │ • Evidence  │ │              │
│ │           │ • Reframes  │ │              ▼ (tap FAB)
│ └───────────┴─────────────┘ │      ┌─────────────────────┐
│        Resizable (20-50%)   │      │     FLOW PAGE       │
└─────────────────────────────┘      │  (Full Screen)      │
                                     │ • QuestionSelector  │
                                     │ • Entity Panel      │
                                     │ • Notes Sheet       │
                                     └─────────────────────┘
```

### FlowStore State Structure

```typescript
interface FlowStore {
  // Panel State
  flowPanelOpen: boolean;
  flowPanelWidth: number;
  flowPanelPinned: boolean;

  // Entity State
  currentEntity: Entity | null;
  relationships: Relationship[];
  sources: Source[];
  questions: ThinkingQuestion[];
  facets: Facet[];
  evidence: Evidence[];
  reframes: Reframe[];

  // Question State (Flow v2)
  flowQuestions: FlowQuestion[];
  currentQuestionId: string | null;
  parentQuestionId: string | null;

  // Journey State
  journeyId: string | null;
  journeySteps: JourneyStep[];
  journeyStartTime: number | null;
  currentStepTime: number | null;

  // Overlay State
  entityOverlayEnabled: boolean;
  overlayEntities: OverlayEntity[];
  visibleEntityTypes: string[];

  // Sync State
  userId: string | null;
  syncStatus: 'idle' | 'syncing' | 'error';
  lastSyncTime: number | null;

  // Actions
  setCurrentEntity: (entity: Entity) => void;
  fetchEntityDetails: (name: string) => Promise<void>;
  addJourneyStep: (step: JourneyStep) => void;
  // ... more actions
}
```

---

## 6. Data Flow Diagrams

### 6.1 Reading → Exploration Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    READING → EXPLORATION FLOW                     │
└──────────────────────────────────────────────────────────────────┘

User Action                    System Response
───────────                    ───────────────
    │
    ▼
┌─────────────┐
│ Open Book   │
│ from Calibre│
└─────────────┘
    │
    ├───────────────────────────────────────────────┐
    ▼                                               ▼
┌─────────────┐                           ┌─────────────────┐
│ IES Reader  │                           │ Backend API     │
│ loads epub  │                           │ GET /books/{id} │
└─────────────┘                           └─────────────────┘
    │                                               │
    ▼                                               ▼
┌─────────────┐                           ┌─────────────────┐
│ Fetch book  │ ─────────────────────────▶│ GET /entities/  │
│ entities    │                           │ by-calibre-id   │
└─────────────┘                           └─────────────────┘
    │                                               │
    ▼                                               ▼
┌─────────────┐                           ┌─────────────────┐
│ Apply entity│◀──────────────────────────│ Return entities │
│ overlay     │                           │ with types      │
└─────────────┘                           └─────────────────┘
    │
    ▼
┌─────────────┐
│ User selects│
│ text        │
└─────────────┘
    │
    ├────────────────┬────────────────────┐
    ▼                ▼                    ▼
┌─────────┐    ┌─────────┐          ┌─────────┐
│ Entity  │    │ Note    │          │Highlight│
│ Lookup  │    │ Capture │          │ Text    │
└─────────┘    └─────────┘          └─────────┘
    │                │
    ▼                ▼
┌─────────────┐  ┌─────────────────┐
│ Open Flow   │  │ Save to Journey │
│ Panel       │  │ POST /journeys/ │
└─────────────┘  │ {id}/steps      │
    │            └─────────────────┘
    ▼
┌─────────────┐
│ Fetch entity│
│ details,    │
│ facets,     │
│ evidence    │
└─────────────┘
```

### 6.2 ForgeMode Session Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    FORGEMODE SESSION FLOW                         │
└──────────────────────────────────────────────────────────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ 1. Select   │────▶│ 2. Load     │────▶│ 3. Start    │
│    Mode     │     │   Template  │     │   Session   │
│ (Learning)  │     │   from API  │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                    ┌─────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SESSION LOOP                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │ 4. Display   │────▶│ 5. User      │────▶│ 6. Question  │    │
│  │    Section   │     │    Response  │     │    Engine    │    │
│  │    Prompt    │     │              │     │    Call      │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│         ▲                                          │            │
│         │                                          ▼            │
│         │                                  ┌──────────────┐    │
│         │                                  │ 7. Generate  │    │
│         │                                  │    Thinking  │    │
│         │                                  │    Partner Q │    │
│         │                                  └──────────────┘    │
│         │                                          │            │
│         └──────────────────────────────────────────┘            │
│                   (repeat for each section)                      │
└─────────────────────────────────────────────────────────────────┘
                                              │
                    ┌─────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SESSION END                                   │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │ 8. Extract   │────▶│ 9. Offer     │────▶│ 10. Save to  │    │
│  │    Entities  │     │    Concept   │     │    SiYuan    │    │
│  │              │     │    Wizard    │     │    Document  │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│                                                    │            │
│                                                    ▼            │
│                                            ┌──────────────┐    │
│                                            │ /Sessions/   │    │
│                                            │ {mode}/      │    │
│                                            │ {date}.md    │    │
│                                            └──────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 Facet Decomposition Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    FACET DECOMPOSITION FLOW                       │
└──────────────────────────────────────────────────────────────────┘

┌─────────────┐
│ User opens  │
│ entity:     │
│ "ADHD"      │
└─────────────┘
      │
      ▼
┌─────────────┐     ┌─────────────────────────────────────────────┐
│ GET /entity/│────▶│ Backend: Check if facets exist in Neo4j    │
│ ADHD/facets │     └─────────────────────────────────────────────┘
└─────────────┘                            │
                          ┌────────────────┴────────────────┐
                          ▼                                 ▼
                   [Facets Exist]                    [No Facets]
                          │                                 │
                          │                                 ▼
                          │                    ┌─────────────────────┐
                          │                    │ Call LLM (Claude)   │
                          │                    │ "What are the key   │
                          │                    │ facets of ADHD?"    │
                          │                    └─────────────────────┘
                          │                                 │
                          │                                 ▼
                          │                    ┌─────────────────────┐
                          │                    │ Parse LLM response  │
                          │                    │ into facet objects  │
                          │                    └─────────────────────┘
                          │                                 │
                          │                                 ▼
                          │                    ┌─────────────────────┐
                          │                    │ Match facets to     │
                          │                    │ existing KG entities│
                          │                    └─────────────────────┘
                          │                                 │
                          │                                 ▼
                          │                    ┌─────────────────────┐
                          │                    │ Cache facets in     │
                          │                    │ Neo4j (24h TTL)     │
                          │                    └─────────────────────┘
                          │                                 │
                          ▼                                 ▼
                   ┌─────────────────────────────────────────────┐
                   │              Return Facets                  │
                   │  [Diagnosis ✓] [Symptoms ✓] [Physiology]    │
                   │  [Time Perception] [Treatment]              │
                   │                                              │
                   │  ✓ = exists in graph (has entity_id)        │
                   └─────────────────────────────────────────────┘
                                        │
                                        ▼
                              ┌─────────────────┐
                              │ User clicks     │
                              │ [Physiology]    │
                              └─────────────────┘
                                        │
                          ┌─────────────┴─────────────┐
                          ▼                           ▼
                   [Has entity_id]            [No entity_id]
                          │                           │
                          ▼                           ▼
                   ┌─────────────┐            ┌─────────────┐
                   │ Navigate to │            │ POST /entity│
                   │ existing    │            │ Create new  │
                   │ entity      │            │ entity from │
                   └─────────────┘            │ facet       │
                                              └─────────────┘
```

---

## 7. User Interaction Maps

### 7.1 Primary User Journeys

```
┌──────────────────────────────────────────────────────────────────┐
│                    PRIMARY USER JOURNEYS                          │
└──────────────────────────────────────────────────────────────────┘

JOURNEY 1: READING EXPLORATION
──────────────────────────────
Library → Book → Read → Select Text → Explore Entity → Follow Facets
   │                        │              │               │
   └── Browse Calibre       └── Highlight  └── See Graph   └── Deep Dive
       books                    text           connections     into topic


JOURNEY 2: STRUCTURED THINKING (ForgeMode)
──────────────────────────────────────────
Dashboard → Select Mode → Topic → Section Work → Entity Extract → Concept Save
    │           │            │          │              │              │
    └── See     └── Learning └── Enter  └── Template-  └── Review     └── Neo4j +
        stats       Articulat   topic       guided         entities       SiYuan
                    Planning                session


JOURNEY 3: FLOW EXPLORATION (SiYuan)
────────────────────────────────────
Dashboard → Flow Mode → Search → Entity Focus → Facets → Evidence → Notes
    │           │          │          │           │          │        │
    └── Quick   └── Open   └── Find   └── View    └── Drill  └── Book └── Capture
        access      panel      concept   details     down       passages   insights


JOURNEY 4: QUICK CAPTURE
────────────────────────
Spark → Inbox → Process → Promote → Concept/Insight
  │       │        │         │           │
  └── Low └── Queue└── Review└── Decide  └── Formalize
      friction     captures   context       to graph
```

### 7.2 Detailed Interaction: Reading Exploration

```
┌──────────────────────────────────────────────────────────────────┐
│              READING EXPLORATION - DETAILED FLOW                  │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: LIBRARY                                                  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ [Search: ____________]  [Has Entities Only: ☑]          │    │
│  │                                                          │    │
│  │ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │    │
│  │ │ [Cover]  │  │ [Cover]  │  │ [Cover]  │  │ [Cover]  │ │    │
│  │ │ ADHD 2.0 │  │ Stolen   │  │ Driven   │  │ Scattered│ │    │
│  │ │ •142 ent │  │ Focus    │  │ to       │  │ Minds    │ │    │
│  │ │          │  │ •89 ent  │  │ Distract │  │ •67 ent  │ │    │
│  │ └──────────┘  └──────────┘  └──────────┘  └──────────┘ │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  User clicks "ADHD 2.0"                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: READER WITH ENTITY OVERLAY                               │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ [← Back]  ADHD 2.0  Ch.3 The Neuroscience    [Flow: ON]     ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │                                                              ││
│  │ The role of [DOPAMINE] in ADHD has been studied for         ││
│  │ decades. When [EXECUTIVE FUNCTION] is impaired, people      ││
│  │ struggle with [WORKING MEMORY] and [ATTENTION REGULATION].  ││
│  │                                                              ││
│  │ [Dr. Russell Barkley] proposed that ADHD is fundamentally   ││
│  │ a disorder of [SELF-REGULATION], not simply attention.      ││
│  │                                                              ││
│  │ Legend: [Concept] [Person] [Theory]                         ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  User clicks highlighted [DOPAMINE]                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: FLOW PANEL (opens beside reader)                         │
│                                                                  │
│  ┌───────────────────────┬─────────────────────────────────────┐│
│  │                       │ DOPAMINE                    [Concept]││
│  │   ...reader text...   │                                      ││
│  │                       │ Neurotransmitter involved in reward  ││
│  │                       │ and motivation pathways.             ││
│  │                       │                                      ││
│  │                       │ ─────────────────────────────────────││
│  │                       │ FACETS:                              ││
│  │                       │ [Function ✓] [Pathways ✓]            ││
│  │                       │ [Medications] [Deficiency]           ││
│  │                       │                                      ││
│  │                       │ ─────────────────────────────────────││
│  │                       │ RELATED:                             ││
│  │                       │ • ADHD (component_of)                ││
│  │                       │ • Reward System (part_of)            ││
│  │                       │ • Stimulants (affected_by)           ││
│  │                       │                                      ││
│  │                       │ ─────────────────────────────────────││
│  │                       │ QUESTIONS:                           ││
│  │                       │ • How does dopamine affect focus?    ││
│  │                       │ • Why do stimulants help ADHD?       ││
│  │                       │                                      ││
│  │                       │ [Add Note] [View Evidence]           ││
│  └───────────────────────┴─────────────────────────────────────┘│
│                                                                  │
│  User clicks facet [Function ✓]                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: NAVIGATE TO FACET ENTITY                                 │
│                                                                  │
│  Trail: [Dopamine] → [Function]                                  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ DOPAMINE FUNCTION                              [Mechanism]   ││
│  │                                                              ││
│  │ Dopamine functions primarily in the mesolimbic and          ││
│  │ mesocortical pathways, regulating reward, motivation,       ││
│  │ and executive function.                                      ││
│  │                                                              ││
│  │ ────────────────────────────────────────────────────────────││
│  │ SUB-FACETS:                                                  ││
│  │ [Reward Processing] [Motivation] [Motor Control]            ││
│  │                                                              ││
│  │ ────────────────────────────────────────────────────────────││
│  │ EVIDENCE: (5 passages from your books)                      ││
│  │                                                              ││
│  │ "Stolen Focus" p.42:                                        ││
│  │ "Dopamine plays a crucial role in sustaining attention..."  ││
│  │ [Jump to Passage]                                            ││
│  │                                                              ││
│  │ "ADHD 2.0" p.67:                                            ││
│  │ "The dopamine reward system is fundamentally altered..."    ││
│  │ [Jump to Passage]                                            ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  [← Back]  [Add Note]  [Create Question]                        │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3 Mobile Interaction Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    MOBILE INTERACTION FLOW                        │
└──────────────────────────────────────────────────────────────────┘

PORTRAIT MODE (<640px)
──────────────────────

┌─────────────────┐
│                 │
│   EPUB READER   │
│                 │
│  (full screen)  │
│                 │
│                 │
│   [Selected     │
│    text shows   │
│    action bar]  │
│                 │
│         [FAB]───┼──▶ Tap to open FlowPage
└─────────────────┘

        │
        ▼ (FAB tapped)

┌─────────────────┐
│   FLOW PAGE     │
│  (full screen)  │
├─────────────────┤
│ Question:       │
│ [▼ Select...]   │
│                 │
│ ─────────────── │
│                 │
│ Entity: ADHD    │
│ • Description   │
│ • Facets        │
│ • Related       │
│                 │
│ ─────────────── │
│                 │
│ [Notes] [Back]  │
└─────────────────┘

        │
        ▼ (Notes tapped)

┌─────────────────┐
│   NOTES SHEET   │
│  (slides up)    │
├─────────────────┤
│                 │
│ Type:           │
│ [Thought]       │
│ [Question]      │
│ [Insight]       │
│                 │
│ ─────────────── │
│                 │
│ [Your note...   │
│  ____________   │
│  ____________]  │
│                 │
│ [Cancel] [Save] │
└─────────────────┘
```

---

## 8. State Management

### 8.1 IES Reader State (Zustand)

```typescript
// flowStore.ts - Complete State Shape

interface FlowState {
  // === PANEL STATE ===
  flowPanelOpen: boolean;
  flowPanelWidth: number;        // 20-50% of viewport
  flowPanelPinned: boolean;

  // === ENTITY STATE ===
  currentEntity: Entity | null;
  entityLoading: boolean;
  entityError: string | null;

  relationships: Relationship[];
  sources: Source[];
  questions: ThinkingQuestion[];
  facets: Facet[];
  evidence: Evidence[];
  reframes: Reframe[];

  // === QUESTION STATE (Flow v2) ===
  flowQuestions: FlowQuestion[];
  currentQuestionId: string | null;
  parentQuestionId: string | null;

  // === JOURNEY STATE ===
  journeyId: string | null;
  journeySteps: JourneyStep[];
  journeyStartTime: number | null;
  currentStepTime: number | null;

  // === OVERLAY STATE ===
  entityOverlayEnabled: boolean;
  overlayEntities: OverlayEntity[];
  visibleEntityTypes: Set<string>;
  overlayLoading: boolean;

  // === SYNC STATE ===
  userId: string | null;
  syncStatus: 'idle' | 'syncing' | 'error';
  lastSyncTime: number | null;
  pendingSync: SyncItem[];
}

interface FlowActions {
  // Panel
  setFlowPanelOpen: (open: boolean) => void;
  setFlowPanelWidth: (width: number) => void;
  toggleFlowPanelPinned: () => void;

  // Entity
  setCurrentEntity: (entity: Entity | null) => void;
  fetchEntityDetails: (name: string) => Promise<void>;
  clearEntity: () => void;

  // Questions
  addFlowQuestion: (question: FlowQuestion) => void;
  removeFlowQuestion: (id: string) => void;
  setCurrentQuestion: (id: string | null) => void;
  updateQuestionStatus: (id: string, status: string) => void;

  // Journey
  startJourney: (bookId: string, contextId?: string) => void;
  addJourneyStep: (step: JourneyStep) => void;
  endJourney: () => Promise<void>;

  // Overlay
  setEntityOverlayEnabled: (enabled: boolean) => void;
  fetchEntitiesForBook: (calibreId: number) => Promise<void>;
  toggleEntityType: (type: string) => void;

  // Sync
  setUserId: (id: string) => void;
  syncToBackend: () => Promise<void>;
}
```

### 8.2 SiYuan Plugin State (Svelte Stores)

```typescript
// ForgeMode State
interface ForgeModeState {
  // Session
  sessionId: string | null;
  sessionActive: boolean;
  sessionMode: ThinkingMode;
  sessionTopic: string;

  // Template
  currentTemplate: ThinkingTemplate | null;
  currentSectionIndex: number;
  sectionResponses: Map<string, string>;

  // Conversation
  messages: Message[];
  isGenerating: boolean;

  // Question Engine
  lastQuestionClass: QuestionClass | null;
  questionClassesUsed: QuestionClass[];

  // Entities
  extractedEntities: Entity[];

  // Trail (for context mode)
  trailStack: TrailItem[];
  focusState: 'idle' | 'question' | 'entity' | 'facet';
}

// FlowMode State
interface FlowModeState {
  // Search
  searchQuery: string;
  searchResults: Entity[];

  // Focus
  currentEntity: Entity | null;
  focusState: 'idle' | 'entity' | 'facet';

  // Navigation
  trailStack: TrailItem[];
  standaloneTrailStack: TrailItem[];

  // Facets & Evidence
  facets: Facet[];
  evidence: Evidence[];
  showEvidence: boolean;

  // Context Mode
  contextBlockId: string | null;
  contextQuestions: Question[];
}
```

---

## 9. API Reference

### 9.1 Entity & Graph APIs

```
GET /graph/entity/{name}
─────────────────────────
Returns entity details with relationships, sources, questions.

Response:
{
  "name": "Dopamine",
  "type": "Concept",
  "description": "Neurotransmitter...",
  "relationships": [
    {"target": "ADHD", "type": "component_of"},
    {"target": "Reward System", "type": "part_of"}
  ],
  "sources": [
    {"book_id": "calibre:123", "title": "ADHD 2.0", "page": 67}
  ],
  "questions": [
    {"text": "How does dopamine affect focus?", "type": "Causal"}
  ]
}


GET /graph/entity/{name}/facets
───────────────────────────────
Returns or generates facet decomposition.

Query params:
  - force_refresh: boolean (default: false)

Response:
{
  "entity_name": "ADHD",
  "facets": [
    {"name": "Diagnosis", "type": "component", "exists_in_graph": true, "entity_id": "..."},
    {"name": "Treatment", "type": "component", "exists_in_graph": false}
  ],
  "cached": true,
  "generated_at": "2025-12-09T..."
}


GET /graph/entity/{name}/evidence
─────────────────────────────────
Returns evidence passages from indexed books.

Response:
{
  "entity_name": "Dopamine",
  "evidence": [
    {
      "source_id": "calibre:123",
      "source_title": "ADHD 2.0",
      "chunk_text": "Dopamine plays a crucial role...",
      "location": {"cfi": "/6/4...", "page": 67},
      "confidence": 0.85
    }
  ],
  "total_count": 12
}
```

### 9.2 Question & Context APIs

```
POST /questions/
────────────────
Create a new question.

Request:
{
  "context_id": "ctx_123",
  "text": "How does dopamine affect focus?",
  "source": "reader",
  "parent_question_id": null
}

Response:
{
  "id": "q_456",
  "context_id": "ctx_123",
  "text": "How does dopamine affect focus?",
  "status": "open",
  "source": "reader",
  "created_at": "2025-12-09T..."
}


GET /questions/?context_id={id}&source={source}&status={status}
───────────────────────────────────────────────────────────────
List questions with filters.


POST /questions/{id}/answers
────────────────────────────
Add an answer block to a question.

Request:
{
  "content": "Based on my reading, dopamine affects focus by...",
  "quality": "draft"
}


POST /context/
──────────────
Create a new context.

Request:
{
  "type": "feynman_problem",
  "title": "Understanding ADHD Time Perception",
  "key_questions": ["Why does time feel different?"],
  "core_concepts": ["time perception", "working memory"]
}
```

### 9.3 Question Engine API

```
POST /question-engine/detect-state
──────────────────────────────────
Detect user's cognitive/emotional state from messages.

Request:
{
  "messages": [
    {"role": "user", "content": "I'm confused about..."},
    {"role": "assistant", "content": "..."}
  ]
}

Response:
{
  "state": "stuck",
  "confidence": 0.82,
  "markers": ["confusion indicator", "repetition"]
}


POST /question-engine/generate-questions
────────────────────────────────────────
Generate thinking partner questions.

Request:
{
  "context": "Learning about dopamine",
  "state": "exploring",
  "approach": "Socratic",
  "recent_messages": [...]
}

Response:
{
  "questions": [
    {
      "text": "What evidence supports the dopamine hypothesis?",
      "class": "Schema-Probe",
      "cognitive_function": "Surfaces hidden structure"
    }
  ]
}


GET /question-engine/question-classes
─────────────────────────────────────
List all 9 question classes with descriptions.

Response:
{
  "classes": [
    {
      "name": "Schema-Probe",
      "description": "Surfaces hidden structure (lists, buckets, taxonomies)",
      "emoji": "🏗️",
      "maps_to_modes": ["Discovery", "Learning"]
    },
    {
      "name": "Causal",
      "description": "Pushes for mechanisms, prerequisites, sequences",
      "emoji": "⚡",
      "maps_to_modes": ["Dialogue", "Learning"]
    }
    // ... 7 more classes
  ]
}
```

---

## Appendix A: Component Quick Reference

### IES Reader Components

| Component | File | Purpose |
|-----------|------|---------|
| App | `App.tsx` | Main routing (Library ↔ Reader) |
| LibraryBrowser | `library/LibraryBrowser.tsx` | Calibre book grid |
| Reader | `Reader.tsx` | epub.js wrapper |
| FlowPanel | `flow/FlowPanel.tsx` | Side panel container |
| QuestionSelector | `flow/QuestionSelector.tsx` | Question dropdown |
| NotesSheet | `flow/NotesSheet.tsx` | Note capture UI |

### SiYuan Plugin Views

| View | File | Purpose |
|------|------|---------|
| Dashboard | `Dashboard.svelte` | Stats, suggestions |
| ForgeMode | `ForgeMode.svelte` | 5 thinking modes |
| FlowMode | `FlowMode.svelte` | Entity exploration |
| QuickCapture | `QuickCapture.svelte` | Fast capture |
| Inbox | `Inbox.svelte` | Capture queue |

### Backend Services

| Service | File | Purpose |
|---------|------|---------|
| GraphService | `graph_service.py` | Neo4j operations |
| QuestionService | `question_service.py` | Question CRUD |
| ContextCRUDService | `context_crud_service.py` | Context CRUD |
| CalibreService | `calibre_service.py` | Book catalog |
| ReframeService | `reframe_service.py` | LLM reframes |
| JourneyService | `journey_service.py` | Journey tracking |

---

## Appendix B: Development Commands

```bash
# Start infrastructure
docker compose up -d

# Backend (port 8081)
cd ies/backend
uv run uvicorn ies_backend.main:app --reload --port 8081

# IES Reader (port 5173)
cd ies/reader
pnpm dev

# SiYuan Plugin
cd .worktrees/siyuan/ies/plugin
pnpm dev

# Run backend tests
cd ies/backend
uv run pytest -v

# Check worktrees
git worktree list
```

---

*This document provides complete architecture and interaction maps for the IES system.*
