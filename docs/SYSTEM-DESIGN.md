# brain_explore: System Design

**Purpose:** Single source of truth for how the system works end-to-end.
**Rule:** Read this FULLY at session start. Check against it before building anything.

---

## 1. What This System Does

**One Sentence:** Help a person think WITH an AI partner who adapts to their unique cognitive patterns while exploring a rich knowledge domain.

**The Experience:**
1. You read a book and highlight something that resonates
2. That highlight connects to a concept in the knowledge graph
3. You see what else discusses that concept, what it relates to
4. An AI asks you questions tailored to how YOU think
5. Your exploration path is captured as breadcrumbs
6. Over time, your sparks become insights, your patterns become visible
7. The cycle deepens both your understanding and the system's understanding of you

---

## 2. The Four Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4: READEST (Reading Interface)                           │
│  WHERE: You read books and explore concepts                     │
│  ───────────────────────────────────────────────────────────    │
│  • Linear reading with highlight/annotate                       │
│  • Flow mode: split view (text + entity panel)                  │
│  • Text selection → entity lookup → relationship browse         │
│  • Breadcrumb journey captured automatically                    │
│  STATUS: MVP built, needs integration                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: SIYUAN PLUGIN (Processing Hub)                        │
│  WHERE: You process, think, and organize                        │
│  ───────────────────────────────────────────────────────────    │
│  • Dashboard: what to explore, recent journeys, capture queue   │
│  • Structured Thinking: 5 modes with AI dialogue                │
│  • Flow Mode: graph exploration without books                   │
│  • Quick Capture: dump thoughts, auto-extract entities          │
│  STATUS: MVP built, needs integration                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: BACKEND (API Services)                                │
│  WHERE: All intelligence and data lives                         │
│  ───────────────────────────────────────────────────────────    │
│  • Graph API: search, explore, sources, suggestions             │
│  • Session API: structured thinking dialogue                    │
│  • Journey API: breadcrumb capture and retrieval                │
│  • Capture API: content → entity extraction                     │
│  • Question Engine: thinking partner questions                  │
│  • Profile Service: cognitive profile (6 dimensions)            │
│  STATUS: Production ready (54/61 tests)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: KNOWLEDGE GRAPH (Foundation)                          │
│  WHERE: Domain knowledge + personal knowledge live              │
│  ───────────────────────────────────────────────────────────    │
│  Domain Graph:                                                  │
│  • 50k entities from 63 therapy/psychology books                │
│  • 125k relationships (supports, contrasts, develops, etc.)     │
│  • Neo4j for graph queries, Qdrant for semantic search          │
│                                                                 │
│  Personal Graph (NEW - ADHD ontology):                          │
│  • spark, insight, thread, favorite_problem entities            │
│  • resonance_signal, energy_level metadata                      │
│  • sparked_by, led_to_discovery relationships                   │
│  STATUS: Domain graph operational, personal graph schema built  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Structures

### 3.1 Domain Knowledge (from books)

```
Entity Types: concept | framework | theory | mechanism | phenomenon |
              pattern | distinction | person | book | assessment

Relationships: supports | contrasts_with | component_of | develops |
               cites | operationalizes | instance_of | related_to
```

**Source:** `library/graph/entities.py`, `library/graph/neo4j_client.py`

### 3.2 Personal Knowledge (ADHD-friendly)

```
Entity Types: spark | insight | thread | favorite_problem

Metadata:
  resonance_signal: curious | excited | surprised | moved | disturbed | unclear
  energy_level: low | medium | high
  status: captured | exploring | anchored
  capture_context: string (what you were doing when you captured it)
  exploration_visits: integer (how many times you've returned)

Relationships: sparked_by | led_to_discovery | addresses_problem |
               energy_toward | energy_away
```

**Source:** `library/graph/adhd_ontology.py`, `library/graph/adhd_graph_client.py`

### 3.3 User Profile (6 dimensions)

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

### 3.4 Journey (exploration path)

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
1. Open book in Readest
2. Read, highlight passage that resonates
3. Toggle Flow mode (split panel appears)
4. Entity panel shows:
   - What concept this relates to
   - Other sources discussing it
   - Related concepts
   - Thinking partner question
5. Click related concept → navigate there
6. Journey captured automatically
7. End session → journey saved → available in SiYuan dashboard
```

### 4.2 Structured Thinking Flow (Layer 3 → Layer 2)

```
1. Open SiYuan plugin dashboard
2. Select "Start Thinking" → choose mode:
   - Learning: understand new concept
   - Articulating: clarify vague intuition
   - Planning: develop action strategy
   - Ideating: generate creative options
   - Reflecting: personal insight
3. AI asks mode-appropriate questions
4. Live note preview shows emerging structure
5. Save note → entities extracted → linked to graph
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
3. Click relationship → navigate to connected entity
4. Ask thinking partner for questions at any point
5. Journey captured as you explore
```

---

## 5. Integration Points (What's Connected vs. Not)

### Currently Connected ✅
| From | To | How |
|------|-----|-----|
| Readest | Backend Graph API | REST calls for entity/explore |
| SiYuan Plugin | Backend APIs | All endpoints work |
| Backend | Neo4j (domain) | graph_service.py |
| Backend | Qdrant | Semantic search |

### NOT Connected Yet ❌
| From | To | Gap |
|------|-----|-----|
| Readest | Personal Graph | ADHD ontology not wired |
| SiYuan | Personal Graph | ADHD ontology not wired |
| Quick Capture | Anywhere | No destination defined |
| Readest | SiYuan | No sync between them |
| Books library | Graph | 63 books ingested but not navigable from UI |
| Journeys | Graph enrichment | Captured but not used |

---

## 6. SiYuan Structure (NOT YET DEFINED)

**This is a major gap.** We have:
- A plugin that can create/read blocks
- An ADHD ontology with entity types

We DON'T have:
- Where sparks go (which notebook? which document structure?)
- How favorite_problems are represented
- How threads are stored
- How personal graph relates to SiYuan documents
- Note types and templates

**Needs Design:**
```
/brain_explore/                    # Notebook
├── /Sparks/                       # Quick captures
│   └── YYYY-MM-DD.md              # Daily spark log? Or individual files?
├── /Insights/                     # Promoted sparks
├── /Threads/                      # Exploration journeys
├── /Favorite Problems/            # Navigation anchors
├── /Concepts/                     # Domain concepts I'm developing
└── /Journeys/                     # Reading session captures
```

---

## 7. Data Flow Diagram

```
                    ┌──────────────────┐
                    │   USER ACTION    │
                    └────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Read in Readest │ │Think in SiYuan  │ │ Capture thought │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│                    BACKEND APIs                          │
│  Graph API  │  Session API  │  Journey API  │ Capture   │
└─────────────────────────────────────────────────────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│                   KNOWLEDGE GRAPH                        │
│         Domain Graph (Neo4j)  +  Personal Graph          │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                   USER PROFILE                           │
│         Cognitive dimensions + exploration patterns      │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              THINKING PARTNER QUESTIONS                  │
│         Personalized based on profile + context          │
└─────────────────────────────────────────────────────────┘
```

---

## 8. What's Actually Built vs. What's Designed

| Component | Designed | Built | Integrated | Usable |
|-----------|----------|-------|------------|--------|
| Neo4j domain graph | ✅ | ✅ | ✅ | ✅ |
| Backend Graph API | ✅ | ✅ | ✅ | ✅ |
| Backend Session API | ✅ | ✅ | ✅ | ✅ |
| Backend Journey API | ✅ | ✅ | ⚠️ | ❌ |
| Backend Capture API | ✅ | ✅ | ⚠️ | ❌ |
| Question Engine | ✅ | ✅ | ✅ | ⚠️ |
| Profile Service | ✅ | ✅ | ⚠️ | ❌ |
| ADHD Personal Graph | ✅ | ✅ | ❌ | ❌ |
| Readest Flow Mode | ✅ | ✅ | ⚠️ | ⚠️ |
| SiYuan Dashboard | ✅ | ✅ | ⚠️ | ⚠️ |
| SiYuan Thinking Modes | ✅ | ✅ | ⚠️ | ⚠️ |
| Quick Capture | ✅ | ⚠️ | ❌ | ❌ |
| SiYuan structure | ❌ | ❌ | ❌ | ❌ |
| Book navigation | ❌ | ❌ | ❌ | ❌ |
| Cross-app sync | ✅ | ❌ | ❌ | ❌ |

**Legend:** ✅ Done | ⚠️ Partial | ❌ Not done

---

## 9. Critical Gaps (Blocking Real Usage)

### Gap 1: SiYuan Structure
**Problem:** No defined place for sparks, insights, threads to go
**Impact:** Can't use Quick Capture, can't store personal knowledge
**To Resolve:** Design notebook/document structure, implement templates

### Gap 2: Personal Graph Integration
**Problem:** ADHD ontology built but not connected to any UI
**Impact:** Can't capture with resonance signals, can't navigate by energy
**To Resolve:** Wire ADHDKnowledgeGraph to backend APIs, expose in frontends

### Gap 3: Book Library Access
**Problem:** 63 books ingested but no way to browse/open them from UI
**Impact:** Can't start reading flow from within the system
**To Resolve:** Add book browser to SiYuan/Readest, link to graph entities

### Gap 4: Journey → Value Loop
**Problem:** Journeys captured but never used
**Impact:** Exploration data doesn't improve suggestions or enrich graph
**To Resolve:** Design journey processing pipeline

### Gap 5: Cross-App Continuity
**Problem:** Readest and SiYuan don't share state
**Impact:** Can't resume exploration across apps
**To Resolve:** Shared journey storage, sync mechanism

---

## 10. The Virtuous Cycle (Goal State)

```
You read a book
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
curl http://localhost:8081/health
curl http://localhost:8081/graph/stats
```

### Work in Worktrees
```bash
cd .worktrees/readest    # Layer 4
cd .worktrees/siyuan     # Layer 3
cd .                     # Layer 2 / shared
```

### Key Files
```
docs/SYSTEM-DESIGN.md              # This file (source of truth)
library/graph/adhd_ontology.py     # Personal knowledge schema
library/graph/adhd_graph_client.py # Personal knowledge operations
ies/backend/src/ies_backend/       # All backend services
```

---

*Last Updated: December 4, 2025*
*Rule: Update this doc when system design changes. This is the canonical reference.*
