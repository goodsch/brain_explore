# Integrated Reading & Knowledge System Design

**Date**: 2025-12-03
**Status**: Design Complete
**Supersedes**: Phase 2b plugin-only approach

---

## Executive Summary

This design expands the brain_explore system from a three-layer architecture to a four-layer architecture by integrating **Readest** (an open-source e-book reader) as the primary reading interface. The key insight driving this design is:

> "Instead of reading one book, you're reading a concept."

Flow mode surfaces all sources discussing the current entity, transforming reading from linear consumption into conceptual exploration.

---

## 1. Architecture Overview

### 1.1 Four-Layer Model

```
Layer 4: READEST          - Reading + Flow exploration
Layer 3: SIYUAN PLUGIN    - Processing hub (Dashboard, Thinking, Capture)
Layer 2: BACKEND          - API, dialogue, profile, entity services
Layer 1: KNOWLEDGE GRAPH  - Neo4j entities + relationships + user concepts
```

### 1.2 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           READEST (Layer 4)                             │
│  ┌─────────────────────────┐    ┌─────────────────────────────────────┐ │
│  │     Linear Mode         │    │           Flow Mode                 │ │
│  │  ┌─────────────────┐    │    │  ┌───────────┐  ┌─────────────────┐ │ │
│  │  │                 │    │    │  │  Source   │  │  Entity Panel   │ │ │
│  │  │  Traditional    │    │    │  │  Panel    │  │  ┌───────────┐  │ │ │
│  │  │  e-book reading │    │◄──►│  │           │  │  │Definition │  │ │ │
│  │  │                 │    │    │  │  Current  │  │  ├───────────┤  │ │ │
│  │  │  - Highlight    │    │    │  │  passage  │  │  │Relations  │  │ │ │
│  │  │  - Annotate     │    │    │  │  or book  │  │  ├───────────┤  │ │ │
│  │  │  - Bookmark     │    │    │  │  section  │  │  │Sources    │  │ │ │
│  │  │                 │    │    │  │           │  │  ├───────────┤  │ │ │
│  │  └─────────────────┘    │    │  │           │  │  │Questions  │  │ │ │
│  │         │               │    │  │           │  │  └───────────┘  │ │ │
│  │         ▼               │    │  └───────────┘  └─────────────────┘ │ │
│  │  [Toggle Flow Mode]     │    │         │                           │ │
│  └─────────────────────────┘    └─────────┼───────────────────────────┘ │
│                                           │                             │
│                    ┌──────────────────────┴────────────────────┐        │
│                    │  Breadcrumb Journey                       │        │
│                    │  - Path: entity1 → entity2 → entity3      │        │
│                    │  - Marks: highlights, annotations         │        │
│                    │  - Context: questions asked, time spent   │        │
│                    └──────────────────────┬────────────────────┘        │
└───────────────────────────────────────────┼─────────────────────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    │                                               │
                    ▼                                               ▼
┌─────────────────────────────────────┐  ┌────────────────────────────────┐
│      SIYUAN PLUGIN (Layer 3)        │  │      BACKEND (Layer 2)         │
│  ┌─────────────┐ ┌───────────────┐  │  │  ┌────────────────────────┐    │
│  │  Dashboard  │ │  Structured   │  │  │  │  Graph API             │    │
│  │  - Recent   │ │  Thinking     │  │  │  │  - Entity search       │    │
│  │  - Concepts │ │  ┌──────────┐ │  │  │  │  - Neighborhood        │    │
│  │  - Journeys │ │  │Conversa- │ │  │  │  │  - Sources             │    │
│  │  - Profile  │ │  │tion      │ │  │  │  └────────────────────────┘    │
│  └─────────────┘ │  ├──────────┤ │  │  │  ┌────────────────────────┐    │
│  ┌─────────────┐ │  │Live Note │ │  │  │  │  Profile Service       │    │
│  │Quick Capture│ │  │Preview   │ │  │  │  │  - Cognition model     │    │
│  │  - Queue    │ │  └──────────┘ │  │  │  │  - Preferences         │    │
│  │  - Process  │ │  Modes:       │  │  │  │  - History             │    │
│  │  - Route    │ │  - Learning   │  │  │  └────────────────────────┘    │
│  └─────────────┘ │  - Articulate │  │  │  ┌────────────────────────┐    │
│                  │  - Planning   │  │  │  │  Session Service       │    │
│                  │  - Ideating   │  │  │  │  - Dialogue            │    │
│                  │  - Reflect    │  │  │  │  - Extraction          │    │
│                  └───────────────┘  │  │  └────────────────────────┘    │
└─────────────────────────────────────┘  │  ┌────────────────────────┐    │
                    │                    │  │  Readest Sync          │    │
                    │                    │  │  - Highlights          │    │
                    │                    │  │  - Journeys            │    │
                    │                    │  │  - Annotations         │    │
                    │                    │  └────────────────────────┘    │
                    │                    └────────────────────────────────┘
                    │                                   │
                    └───────────────────┬───────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      KNOWLEDGE GRAPH (Layer 1)                          │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                        NEO4J + QDRANT                           │   │
│   │                                                                 │   │
│   │   Entities (50k+)           Relationships (125k+)               │   │
│   │   - Concepts                - supports                          │   │
│   │   - Theories                - contrasts_with                    │   │
│   │   - Researchers             - component_of                      │   │
│   │   - Assessments             - develops                          │   │
│   │   - Books                   - cites                             │   │
│   │   - Chapters                - authored_by                       │   │
│   │                                                                 │   │
│   │   User Layer                                                    │   │
│   │   - Formalized concepts (from exploration)                      │   │
│   │   - Breadcrumb journeys (exploration paths)                     │   │
│   │   - Annotations & highlights (cross-referenced)                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Readest Integration (Layer 4)

### 2.1 Technology Stack

- **Framework**: Tauri (Rust backend + web frontend)
- **UI**: TypeScript + Svelte
- **Rendering**: foliate-js (EPUB, PDF, etc.)
- **Source**: https://github.com/readest/readest (MIT license)

### 2.2 Linear Mode (Existing + Extensions)

Standard e-book reading with enhancements:

| Feature | Description |
|---------|-------------|
| Reading | Page-by-page or scroll, font controls, themes |
| Highlights | Color-coded, synced to SiYuan |
| Annotations | Margin notes, linked to graph entities |
| Flow Toggle | Button/gesture to enter Flow mode on selection |

### 2.3 Flow Mode (New)

Split-panel view for conceptual exploration:

**Source Panel (Left)**
- Current passage or chapter
- Entity mentions highlighted/linked
- Can switch to any source discussing current entity

**Entity Panel (Right)**
- **Definition**: Canonical summary from graph
- **Relationships**: Grouped by type (supports, contrasts, etc.)
- **Other Sources**: Books/chapters discussing this entity
- **Thinking Partner**: AI-generated questions based on profile

### 2.4 Breadcrumb Journey Capture

Every Flow session captures:

```typescript
interface BreadcrumbJourney {
  id: string;
  started_at: string;
  ended_at: string;
  entry_point: {
    type: 'book' | 'search' | 'dashboard';
    reference: string;  // book_id or search_query
  };
  path: Array<{
    entity_id: string;
    entity_name: string;
    timestamp: string;
    source_passage?: string;
    dwell_time_seconds: number;
  }>;
  marks: Array<{
    type: 'highlight' | 'annotation' | 'question';
    entity_id: string;
    content: string;
    timestamp: string;
  }>;
  thinking_partner_exchanges: Array<{
    question: string;
    response?: string;
    timestamp: string;
  }>;
}
```

---

## 3. SiYuan Plugin Evolution (Layer 3)

### 3.1 Dashboard View

Central hub replacing current entry points:

```
┌─────────────────────────────────────────────────────────────────┐
│  DASHBOARD                                          [Profile ⚙]│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Recent         │  │  Active         │  │  Quick          │ │
│  │  Explorations   │  │  Concepts       │  │  Capture        │ │
│  │  ────────────── │  │  ────────────── │  │  Queue          │ │
│  │  • Journey 1    │  │  • Concept A    │  │  ────────────── │ │
│  │  • Journey 2    │  │  • Concept B    │  │  • 3 items      │ │
│  │  • Session 1    │  │  • Framework X  │  │    pending      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Start New...                                             │  │
│  │  [🔍 Explore Concept]  [💭 Structured Thinking]  [📚 Read]│  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Structured Thinking Mode

Replaces and expands "Forge" mode with five use cases:

| Mode | Purpose | AI Behavior |
|------|---------|-------------|
| **Learning** | Understand new concept/domain | Socratic questioning, connection surfacing |
| **Articulating** | Clarify vague intuition | Mirroring, precise language prompts |
| **Planning** | Develop action strategy | Goal clarification, obstacle identification |
| **Ideating** | Generate creative options | Divergent prompts, combination suggestions |
| **Self-Reflecting** | Personal insight | Phenomenological questions, pattern recognition |

**Interface**: Split view with conversation (left) and live note preview (right)

```
┌─────────────────────────────────────────────────────────────────┐
│  STRUCTURED THINKING: Learning about "Acceptance"               │
├────────────────────────────────┬────────────────────────────────┤
│  Conversation                  │  Note Preview                  │
│  ──────────────────────────    │  ────────────────────────────  │
│  AI: What draws you to this    │  # Acceptance                  │
│  concept?                      │                                │
│                                │  ## Initial Understanding      │
│  You: I've been thinking       │  - Distinct from resignation   │
│  about the difference between  │  - Involves active engagement  │
│  acceptance and resignation... │                                │
│                                │  ## Questions                  │
│  AI: That's a rich             │  - How does acceptance relate  │
│  distinction. What feels       │    to grief?                   │
│  different in your body when   │                                │
│  you imagine each?             │  ## Connections                │
│                                │  - [[Narrow Window]]           │
│  [Your response...]            │  - [[Metabolization]]          │
│                                │                                │
├────────────────────────────────┴────────────────────────────────┤
│  [Mode: Learning ▼]  [Save Note]  [Link to Graph]  [End Session]│
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Quick Capture Queue

Phone-friendly thought capture with intelligent processing:

**Capture Methods:**
- Text dump (unstructured thoughts)
- Voice note (transcribed)
- Photo (OCR'd if text)
- Link (fetched and summarized)

**Processing Pipeline:**
1. AI extracts structure and entities
2. Suggests placement (existing note, new note, concept link)
3. User confirms or adjusts
4. Routed to appropriate location with links

### 3.4 Profile Management

**Onboarding Wizard** (first use):
- Short vignettes with preference choices
- Direct questions about working style
- Initial profile generation

**Profile Dashboard**:
- View current dimension values
- Adjust preferences manually
- See how profile affects suggestions

---

## 4. User Cognition Model

### 4.1 Eight Dimensions

```typescript
interface UserCognitionProfile {
  user_id: string;
  created_at: string;
  last_updated: string;

  dimensions: {
    structure_preference: number;     // 0 (open) → 1 (scaffolded)
    pace: number;                     // 0 (slow/deep) → 1 (fast/broad)
    ambiguity_tolerance: number;      // 0 (needs closure) → 1 (sits with uncertainty)
    novelty_preference: number;       // 0 (familiar) → 1 (surprising)
    abstraction_level: number;        // 0 (concrete) → 1 (abstract)
    social_orientation: number;       // 0 (individual) → 1 (relational)
    temporal_focus: number;           // 0 (present) → 1 (future/past)
    verification_need: number;        // 0 (intuitive) → 1 (evidence-based)
  };

  primary_reasoning_styles: Array<
    'narrative' | 'analytical' | 'systems' |
    'relational' | 'somatic' | 'metacognitive'
  >;

  preferred_question_modes: Array<
    'socratic' | 'reflective' | 'solution_focused' |
    'phenomenological' | 'strategic'
  >;

  exploration_patterns: {
    typical_depth: number;            // Average entity hops per journey
    breadth_vs_depth: number;         // 0 (depth-first) → 1 (breadth-first)
    return_frequency: number;         // How often revisits concepts
  };
}
```

### 4.2 How Profile Drives System

| Component | Profile Usage |
|-----------|---------------|
| **Readest Flow** | Question complexity, relationship grouping, source suggestions |
| **Structured Thinking** | Question style, pacing, abstraction level |
| **Quick Capture** | Routing suggestions, link density |
| **Dashboard** | Concept recommendations, journey suggestions |

---

## 5. Canonical Concept Schema

Cross-system object bridging all layers:

```typescript
interface Concept {
  // Identity
  id: string;                         // UUID
  name: string;                       // Display name
  canonical_name: string;             // Normalized for matching

  // Content
  summary: string;                    // 1-3 sentence definition
  type: 'concept' | 'theory' | 'framework' |
        'phenomenon' | 'person' | 'assessment';

  // Cross-system links
  graph_node_id: string;              // Neo4j node ID
  siyuan_note_id?: string;            // SiYuan document ID
  siyuan_block_ids: string[];         // Source blocks

  // Relationships
  relationships: Array<{
    type: 'supports' | 'contrasts_with' | 'component_of' |
          'develops' | 'is_example_of' | 'operationalizes';
    target_id: string;
    confidence: number;
    source_blocks?: string[];
  }>;

  // Sources
  book_references: Array<{
    book_id: string;
    chapter?: string;
    page_range?: string;
    passage_ids: string[];
  }>;

  // Metadata
  created_at: string;
  last_updated: string;
  created_by: 'ingestion' | 'extraction' | 'user';
  status: 'draft' | 'stable' | 'deprecated';
  version: number;
  tags: string[];
}
```

---

## 6. Data Flows

### 6.1 Reading → Knowledge (Bottom-up)

```
User highlights passage in Readest
         │
         ▼
┌─────────────────────────────┐
│ Extract entities from text  │
│ (NER + graph matching)      │
└──────────────┬──────────────┘
               │
         ┌─────┴─────┐
         ▼           ▼
┌─────────────┐ ┌─────────────┐
│Create SiYuan│ │Link to graph│
│block        │ │entities     │
└──────┬──────┘ └──────┬──────┘
       │               │
       └───────┬───────┘
               ▼
┌─────────────────────────────┐
│ Update concept sources      │
│ Track user engagement       │
└─────────────────────────────┘
```

### 6.2 Knowledge → Reading (Top-down)

```
User searches "acceptance" in Dashboard
         │
         ▼
┌─────────────────────────────┐
│ Graph query: find entity    │
│ + relationships + sources   │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Open in Readest Flow mode   │
│ - First source as default   │
│ - Entity panel populated    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ User explores, system       │
│ captures breadcrumb journey │
└─────────────────────────────┘
```

### 6.3 Quick Capture → Placement

```
User dumps thought on phone
         │
         ▼
┌─────────────────────────────┐
│ AI processing:              │
│ - Extract entities          │
│ - Identify themes           │
│ - Match to existing notes   │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Suggest placements:         │
│ - Append to note X (85%)    │
│ - Create new concept (10%)  │
│ - Link to journey Y (5%)    │
└──────────────┬──────────────┘
               │
         User confirms
               │
               ▼
┌─────────────────────────────┐
│ Route to destination        │
│ Create bidirectional links  │
└─────────────────────────────┘
```

---

## 7. API Contracts

### 7.1 Readest ↔ Backend

**Entity Lookup**
```
GET /api/v1/graph/entity/{id}
Response: {
  entity: Concept,
  relationships: Relationship[],
  sources: BookReference[]
}
```

**Neighborhood Exploration**
```
GET /api/v1/graph/explore/{entity_id}?depth=1&limit=20
Response: {
  center: Concept,
  neighbors: Array<{
    entity: Concept,
    relationship: string,
    distance: number
  }>
}
```

**Thinking Partner Question**
```
POST /api/v1/thinking-partner/question
Body: {
  entity_id: string,
  context: {
    current_passage?: string,
    recent_path: string[],
    user_profile_id: string
  }
}
Response: {
  questions: Array<{
    text: string,
    type: 'clarifying' | 'connecting' | 'challenging',
    related_entities?: string[]
  }>
}
```

**Save Journey**
```
POST /api/v1/journeys
Body: BreadcrumbJourney
Response: { id: string, siyuan_note_id: string }
```

### 7.2 SiYuan Plugin ↔ Backend

**Structured Thinking Session**
```
POST /api/v1/session
Body: {
  mode: 'learning' | 'articulating' | 'planning' | 'ideating' | 'reflecting',
  topic: string,
  user_profile_id: string,
  initial_context?: {
    related_concepts: string[],
    source_journey_id?: string
  }
}
Response: { session_id: string }

POST /api/v1/session/{id}/message
Body: { content: string }
Response: {
  response: string,
  extracted_entities: string[],
  suggested_note_updates: Array<{
    block_id: string,
    content: string,
    action: 'append' | 'replace' | 'link'
  }>
}
```

**Quick Capture Processing**
```
POST /api/v1/capture/process
Body: {
  content: string,
  type: 'text' | 'voice' | 'image' | 'link',
  context?: { current_note_id?: string }
}
Response: {
  extracted_entities: string[],
  suggested_placements: Array<{
    target_type: 'note' | 'concept' | 'journey',
    target_id: string,
    confidence: number,
    preview: string
  }>
}
```

---

## 8. Implementation Phases

### Phase 1: Foundation (2 weeks)

**Goals:**
- Finalize API contracts
- Set up Readest development environment
- Audit backend for needed extensions

**Deliverables:**
- [ ] API specification document (OpenAPI)
- [ ] Readest fork with development setup
- [ ] Backend endpoint stubs
- [ ] Integration test framework

### Phase 2: Readest MVP (3 weeks)

**Goals:**
- Flow mode toggle and basic split view
- Entity panel with graph queries
- Breadcrumb capture (no sync yet)

**Deliverables:**
- [ ] Flow mode UI in Readest
- [ ] Entity panel component
- [ ] Graph API integration
- [ ] Local journey storage

### Phase 3: SiYuan Evolution (3 weeks)

**Goals:**
- Dashboard view
- Structured Thinking mode
- Quick Capture queue

**Deliverables:**
- [ ] Dashboard component
- [ ] Structured Thinking with live preview
- [ ] Quick Capture processing pipeline
- [ ] Profile management UI

### Phase 4: Integration (2 weeks)

**Goals:**
- Bidirectional sync
- Journey processing
- End-to-end testing

**Deliverables:**
- [ ] Readest ↔ SiYuan sync
- [ ] Journey → Graph enrichment
- [ ] Profile-driven suggestions
- [ ] User acceptance testing

---

## 9. Success Criteria

### Functional
- [ ] Can start from empty system and grow from any entry point
- [ ] Flow mode surfaces 3+ sources per entity
- [ ] Breadcrumb journeys saved and retrievable
- [ ] Quick Capture routes correctly 80%+ of time
- [ ] Profile affects question style noticeably

### Performance
- [ ] Entity lookup < 200ms
- [ ] Flow mode transition < 500ms
- [ ] Journey save < 1s
- [ ] Capture processing < 5s

### User Experience
- [ ] "Reading a concept" feels natural
- [ ] Mode transitions are smooth
- [ ] ADHD rabbit holes captured, not lost
- [ ] Profile onboarding takes < 5 minutes

---

## 10. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Readest fork maintenance burden | Contribute upstream where possible; minimize divergence |
| Graph query performance at scale | Index optimization; caching layer; pagination |
| Profile accuracy | Continuous learning from behavior; manual override |
| Sync conflicts | Last-write-wins with merge UI for conflicts |
| Scope creep | Strict phase gates; parking lot discipline |

---

## Appendix A: Migration from check/docs

| Original Document | New Location | Changes |
|------------------|--------------|---------|
| user-cognition-model.md | Section 4 | Expanded to 8 dimensions |
| modes-spec.md | Section 3.2 | Explore→Structured Thinking (5 modes) |
| mode-transition-engine.md | Section 6 | Cross-system state; richer breadcrumbs |
| schemas.md | Section 5 | Canonical Concept enhanced |
| analysis.md | Throughout | All gaps addressed in design |

---

## Appendix B: File Structure (Proposed)

```
brain_explore/
├── readest/                       # Forked/extended Readest
│   ├── apps/readest-app/          # Tauri application
│   └── packages/
│       ├── readest-core/          # Core reading functionality
│       └── flow-mode/             # New: Flow mode components
│
├── ies/
│   ├── backend/
│   │   └── src/ies_backend/
│   │       ├── api/
│   │       │   ├── graph.py       # Extended for Readest
│   │       │   ├── readest.py     # New: Readest sync endpoints
│   │       │   └── capture.py     # New: Quick Capture processing
│   │       └── services/
│   │           ├── thinking_partner.py  # New
│   │           └── journey.py     # New
│   │
│   └── plugin/
│       └── src/
│           ├── components/
│           │   ├── Dashboard.svelte        # New
│           │   ├── StructuredThinking.svelte  # Evolved from Forge
│           │   ├── QuickCapture.svelte     # New
│           │   └── ProfileManager.svelte   # New
│           └── stores/
│               └── modeContext.ts  # Cross-system state
```
