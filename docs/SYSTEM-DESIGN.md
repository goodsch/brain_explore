# brain_explore: System Design

**Purpose:** Single source of truth for how the system works end-to-end.
**Rule:** Read this FULLY at session start. Check against it before building anything.
**Last Updated:** December 5, 2025

---

## 1. What This System Does

**One Sentence:** Help a person think WITH an AI partner who adapts to their unique cognitive patterns while exploring a rich knowledge domain.

**The Experience:**
1. You browse the Calibre library and open a book in Readest
2. Entity overlay highlights concepts, people, theories in the text
3. Click a highlighted term → Flow Panel shows connections
4. See what else discusses that concept, what it relates to
5. An AI asks you questions tailored to how YOU think
6. Your exploration path is captured as breadcrumbs
7. Over time, your sparks become insights, your patterns become visible
8. The cycle deepens both your understanding and the system's understanding of you

---

## 2. The Four Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4: READEST (Reading Interface)                           │
│  WHERE: You read books and explore concepts                     │
│  ───────────────────────────────────────────────────────────    │
│  • Calibre library browser (search, open books via backend API) │
│  • Entity overlay: inline highlighting with type-specific colors│
│  • Flow mode: split view (text + entity panel)                  │
│  • Click entity → relationships, sources, questions             │
│  • Breadcrumb journey captured automatically                    │
│  STATUS: MVP + Entity Overlay + Calibre Library (Dec 5)         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: SIYUAN PLUGIN (Processing Hub)                        │
│  WHERE: You process, think, and organize                        │
│  ───────────────────────────────────────────────────────────    │
│  • Dashboard: what to explore, recent journeys, capture queue   │
│  • ForgeMode: Template-driven structured thinking (5 modes)     │
│  • Flow Mode: graph exploration without books                   │
│  • Quick Capture: dump thoughts, auto-extract entities          │
│  • ReframesTab: view concept reframes (metaphors, analogies)    │
│  STATUS: MVP + Template Integration (Dec 5)                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: BACKEND (API Services)                                │
│  WHERE: All intelligence and data lives                         │
│  ───────────────────────────────────────────────────────────    │
│  • Graph API: search, explore, sources, suggestions             │
│  • Books API: Calibre catalog, covers, file serving (Dec 4)     │
│  • Entity API: by-book and by-calibre-id lookup                 │
│  • Reframe API: Claude-generated metaphors/analogies (Dec 4)    │
│  • Template API: thinking templates for ForgeMode (Dec 5)       │
│  • Personal API: ADHD-friendly spark/insight capture            │
│  • Session API: structured thinking dialogue                    │
│  • Journey API: breadcrumb capture and retrieval                │
│  STATUS: Production ready (85/85 tests)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: KNOWLEDGE GRAPH (Foundation)                          │
│  WHERE: Domain knowledge + personal knowledge live              │
│  ───────────────────────────────────────────────────────────    │
│  Domain Graph:                                                  │
│  • Calibre library: 179 books (single source of truth)          │
│  • Auto-ingestion daemon: books → entities automatically        │
│  • Current: 291 entities, 338 relationships (10 books indexed)  │
│  • Neo4j for graph queries, Qdrant for semantic search          │
│                                                                 │
│  Personal Graph (ADHD ontology):                                │
│  • spark, insight, thread, favorite_problem entities            │
│  • resonance_signal, energy_level metadata                      │
│  • sparked_by, led_to_discovery relationships                   │
│  STATUS: Operational + Auto-Ingestion Running                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Structures

### 3.1 Domain Knowledge (from books)

```
Entity Types: concept | framework | theory | mechanism | phenomenon |
              pattern | distinction | person | book | assessment

Relationships: MENTIONS | supports | contrasts_with | component_of | develops |
               cites | operationalizes | instance_of | related_to
```

**Source:** `library/graph/entities.py`, `library/graph/neo4j_client.py`

### 3.2 Personal Knowledge (ADHD-friendly)

```
Entity Types: spark | insight | thread | favorite_problem

Metadata:
  resonance_signal: curious | excited | surprised | moved | disturbed | unclear | connected | validated
  energy_level: low | medium | high
  status: captured | exploring | anchored
  capture_context: string (what you were doing when you captured it)
  exploration_visits: integer (how many times you've returned)

Relationships: sparked_by | led_to_discovery | addresses_problem |
               energy_toward | energy_away
```

**Source:** `library/graph/adhd_ontology.py`, `library/graph/adhd_graph_client.py`

### 3.3 Reframe (makes concepts accessible)

```
Types: metaphor | analogy | story | pattern | contrast

Fields:
  concept_id: string (linked concept)
  type: ReframeType
  content: string (the reframe text)
  helpful_votes: integer
  confusing_votes: integer
  generated_by: string (model name)
```

**Source:** `ies/backend/src/ies_backend/api/reframe.py`

### 3.4 Thinking Template (ForgeMode structure)

```
Template Schema:
  id: string (e.g., "learning-mechanism-map")
  mode: learning | articulating | planning | ideating | reflecting
  title: string
  description: string
  sections: Array<Section>
  graph_mapping: GraphMapping rules

Section:
  id: string
  prompt: string (AI asks this)
  input_type: concept_search | freeform | selection
  ai_behavior: string
  required: boolean
```

**Source:** `schemas/thinking-template.schema.json`, `ies/backend/src/ies_backend/api/template.py`

### 3.5 User Profile (6 dimensions)

```typescript
{
  structure_preference: 0-1,    // open ↔ scaffolded
  pace: 0-1,                    // slow/deep ↔ fast/broad
  ambiguity_tolerance: 0-1,     // needs closure ↔ sits with uncertainty
  abstraction_level: 0-1,       // concrete ↔ abstract
  verification_need: 0-1,       // intuitive ↔ evidence-based
  novelty_preference: 0-1       // familiar ↔ surprising
}
```

### 3.6 Journey (exploration path)

```typescript
{
  id: string,
  user_id: string,
  started_at: timestamp,
  ended_at: timestamp,
  entry_point: { type: 'book' | 'search' | 'dashboard', reference: string },
  path: Array<{
    entity_id: string,
    timestamp: timestamp,
    dwell_time_seconds: number,
    source_passage?: string
  }>,
  marks: Array<{
    type: 'highlight' | 'annotation' | 'question',
    entity_id: string,
    content: string
  }>
}
```

---

## 4. User Workflows

### 4.1 Reading Flow (Layer 4 → Layer 2 → Layer 1)

```
1. Open Readest → Import Menu → "From Calibre Library"
2. Browse/search books → click to open
3. Entity overlay highlights concepts in text (color-coded by type)
4. Click highlighted term → Flow Panel opens
5. Entity panel shows:
   - Definition and related concepts
   - Relationships grouped by type
   - Other sources discussing it
   - Thinking partner question
6. Click related concept → navigate there
7. Journey captured automatically
8. End session → journey saved
```

### 4.2 Structured Thinking Flow (Layer 3 → Layer 2)

```
1. Open SiYuan plugin dashboard
2. Select "Start Thinking" → choose mode:
   - Learning: understand new concept (template: mechanism-map)
   - Articulating: clarify vague intuition (template: clarify-intuition)
   - Planning: develop action strategy
   - Ideating: generate creative options
   - Reflecting: personal insight
3. ForgeMode loads template from backend API
4. AI asks section-by-section questions
5. Live note preview shows emerging structure
6. Save note → entities extracted → linked to graph
```

### 4.3 Quick Capture Flow (anywhere → Layer 3 → Layer 2)

```
1. Capture thought (text, voice, photo, link)
2. AI extracts entities and themes
3. Suggests placements:
   - Append to existing note
   - Create new concept
   - Link to journey
4. Confirm or adjust
5. Routed to destination with links
```

### 4.4 Exploration Flow (Layer 3 → Layer 1)

```
1. Search or browse from dashboard
2. Select entity → see relationships grouped by type
3. Click "Reframes" tab → see metaphors/analogies
4. Click relationship → navigate to connected entity
5. Ask thinking partner for questions at any point
6. Journey captured as you explore
```

---

## 5. Integration Points (What's Connected)

### Currently Connected ✅
| From | To | How |
|------|-----|-----|
| Readest | Calibre Library | `/books` API serves catalog + files |
| Readest | Entity Overlay | `/graph/entities/by-calibre-id` |
| Readest | Flow Panel | `/graph/explore`, `/graph/sources` |
| SiYuan Plugin | Backend APIs | All endpoints via forwardProxy |
| SiYuan ForgeMode | Template API | `/templates/{id}` |
| Backend | Neo4j | graph_service.py |
| Backend | Qdrant | Semantic search |
| Backend | Calibre DB | calibre_service.py |
| Ingestion Daemon | Neo4j | auto_ingest_daemon.py |

### Partially Connected ⚠️
| From | To | Status |
|------|-----|-----|
| Readest | Personal Graph | API exists, UI not wired |
| SiYuan | Personal Graph | API exists, UI not wired |
| Quick Capture | Destinations | Entity extraction works, routing partial |
| Journeys | Graph enrichment | Captured but not analyzed |

### NOT Connected Yet ❌
| From | To | Gap |
|------|-----|-----|
| Readest | SiYuan | No sync between them |
| Journey patterns | Suggestions | Patterns not used for personalization |

---

## 6. Backend API Reference

### Graph API
```
GET  /graph/stats                    # Knowledge graph statistics
GET  /graph/search?q={query}         # Entity search
GET  /graph/explore/{entity_id}      # Neighborhood exploration
GET  /graph/sources/{entity_id}      # Book references
GET  /graph/suggestions              # Dashboard topics
POST /graph/thinking-partner         # AI questions for entity
```

### Books API (Calibre)
```
GET  /books                          # List all books from Calibre
GET  /books?search={query}           # Search by title/author
GET  /books/{calibre_id}             # Get single book
GET  /books/{calibre_id}/cover       # Fetch cover image
HEAD /books/{calibre_id}/file        # File metadata (size, type)
GET  /books/{calibre_id}/file        # Serve epub/pdf file
```

### Entity API
```
GET  /graph/entities/by-book/{hash}       # Entities by book hash
GET  /graph/entities/by-calibre-id/{id}   # Entities by Calibre ID
```

### Reframe API
```
GET  /concepts/{id}/reframes              # Get cached reframes
POST /concepts/{id}/reframes/generate     # Generate via Claude
POST /reframes/{id}/feedback              # Vote helpful/confusing
```

### Template API
```
GET  /templates/{template_id}             # Get thinking template
```

### Personal Graph API
```
POST /personal/sparks                     # Create spark
GET  /personal/sparks/{id}                # Get spark
POST /personal/sparks/{id}/visit          # Record visit
POST /personal/sparks/{id}/promote        # Promote to insight
GET  /personal/sparks/by-resonance/{sig}  # Find by emotional state
GET  /personal/sparks/by-energy/{level}   # Find by energy level
GET  /personal/stats                      # Personal graph stats
```

### Journey API
```
POST   /journeys                     # Save breadcrumb journey
GET    /journeys/{id}                # Retrieve journey
GET    /journeys/user/{user_id}      # List user's journeys
PATCH  /journeys/{id}                # Update journey
DELETE /journeys/{id}                # Delete journey
```

### Session API
```
POST /session                        # Start structured thinking session
POST /session/{id}/message           # Send message in session
GET  /session/context/{user_id}      # Load session context
```

---

## 7. Current Graph Statistics

```json
{
  "entities": 291,
  "relationships": 338,
  "books": 10,
  "node_counts": {
    "Concept": 134,
    "Researcher": 118,
    "Theory": 22,
    "Book": 10,
    "Assessment": 7
  },
  "relationship_counts": {
    "MENTIONS": 324,
    "COMPONENT_OF": 4,
    "SUPPORTS": 4,
    "DEVELOPS": 3,
    "CONTRADICTS": 2,
    "CITES": 1
  }
}
```

**Auto-ingestion status:** 10/179 Calibre books indexed. Daemon running (5-minute polls).

---

## 8. What's Actually Built vs. What's Designed

| Component | Designed | Built | Integrated | Usable |
|-----------|----------|-------|------------|--------|
| Neo4j domain graph | ✅ | ✅ | ✅ | ✅ |
| Calibre integration | ✅ | ✅ | ✅ | ✅ |
| Auto-ingestion daemon | ✅ | ✅ | ✅ | ✅ |
| Backend Graph API | ✅ | ✅ | ✅ | ✅ |
| Backend Books API | ✅ | ✅ | ✅ | ✅ |
| Backend Reframe API | ✅ | ✅ | ✅ | ✅ |
| Backend Template API | ✅ | ✅ | ✅ | ✅ |
| Backend Personal API | ✅ | ✅ | ⚠️ | ⚠️ |
| Backend Session API | ✅ | ✅ | ✅ | ✅ |
| Backend Journey API | ✅ | ✅ | ⚠️ | ⚠️ |
| Question Engine | ✅ | ✅ | ✅ | ⚠️ |
| ADHD Personal Graph | ✅ | ✅ | ⚠️ | ❌ |
| Readest Flow Mode | ✅ | ✅ | ✅ | ✅ |
| Readest Entity Overlay | ✅ | ✅ | ✅ | ✅ |
| Readest Calibre Browser | ✅ | ✅ | ✅ | ✅ |
| SiYuan Dashboard | ✅ | ✅ | ✅ | ⚠️ |
| SiYuan ForgeMode | ✅ | ✅ | ✅ | ⚠️ |
| SiYuan ReframesTab | ✅ | ✅ | ✅ | ⚠️ |
| Quick Capture | ✅ | ⚠️ | ⚠️ | ❌ |
| SiYuan structure | ⚠️ | ❌ | ❌ | ❌ |
| Cross-app sync | ✅ | ❌ | ❌ | ❌ |

**Legend:** ✅ Done | ⚠️ Partial | ❌ Not done

---

## 9. Critical Gaps (Blocking Full Usage)

### Gap 1: SiYuan Document Structure ⚠️
**Problem:** No defined place for sparks, insights, threads to go
**Impact:** Can't use Quick Capture destinations, can't store personal knowledge in SiYuan
**Status:** Design exists in `docs/plans/2025-12-04-reframe-template-integration-design.md`
**To Resolve:** Implement folder structure utils, document templates

### Gap 2: Personal Graph UI Integration ⚠️
**Problem:** ADHD ontology API built but not connected to UI
**Impact:** Can't capture with resonance signals in UI, can't navigate by energy
**To Resolve:** Wire Personal API to SiYuan Quick Capture and Readest capture

### Gap 3: Journey → Value Loop ❌
**Problem:** Journeys captured but never analyzed
**Impact:** Exploration data doesn't improve suggestions or enrich graph
**To Resolve:** Design journey processing pipeline

### Gap 4: Cross-App Continuity ❌
**Problem:** Readest and SiYuan don't share state
**Impact:** Can't resume exploration across apps
**To Resolve:** Shared journey storage, sync mechanism

---

## 10. The Virtuous Cycle (Goal State)

```
You browse Calibre library
    ↓
Open book in Readest → entities highlighted
    ↓
Click entity → see connections, reframes
    ↓
Something resonates → capture as spark
    ↓
Spark links to domain concept
    ↓
You explore related concepts in Flow mode
    ↓
AI asks questions tailored to YOUR thinking style
    ↓
You articulate insight → promoted from spark
    ↓
Insight enriches personal graph
    ↓
Next session, system knows:
  - What resonates with you
  - How you think
  - What questions help you
    ↓
Better suggestions, better questions
    ↓
Deeper exploration, richer insights
    ↓ (cycle continues)
```

---

## 11. Session Start Checklist

Before building anything, verify:

- [ ] Which layer am I working in? (1/2/3/4)
- [ ] Does this connect to other layers? How?
- [ ] Is the integration point defined in this doc?
- [ ] If not, should I be designing the integration first?
- [ ] Does this address a Gap from Section 9?
- [ ] Will this be usable end-to-end, or just another disconnected piece?

---

## 12. Quick Reference

### Start Infrastructure
```bash
docker compose up -d
cd ies/backend && uv run uvicorn ies_backend.main:app --port 8081
```

### Test Backend
```bash
cd ies/backend && uv run pytest              # 85/85 tests
curl http://localhost:8081/health
curl http://localhost:8081/graph/stats
```

### Check Ingestion
```bash
python scripts/check_ingestion.py            # View status table
python scripts/auto_ingest_daemon.py &       # Start daemon
```

### Work in Worktrees
```bash
cd .worktrees/readest    # Layer 4
cd .worktrees/siyuan     # Layer 3
cd .                     # Layer 2 / shared
```

### Key Files
```
docs/SYSTEM-DESIGN.md                    # This file (source of truth)
docs/COMPREHENSIVE-PROJECT-STATUS.md     # Complete project status
library/graph/adhd_ontology.py           # Personal knowledge schema
library/graph/adhd_graph_client.py       # Personal knowledge operations
ies/backend/src/ies_backend/             # All backend services
scripts/auto_ingest_daemon.py            # Book ingestion daemon
```

---

*Last Updated: December 5, 2025*
*Rule: Update this doc when system design changes. This is the canonical reference.*
