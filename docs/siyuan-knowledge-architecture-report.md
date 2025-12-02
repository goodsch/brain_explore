# SiYuan Knowledge Architecture Report

**Generated:** 2025-12-02
**Scope:** Analysis of three SiYuan notebooks and their relationship to the brain_explore codebase
**Purpose:** Understand what conceptual structures exist, identify gaps, and recommend improvements

---

## Executive Summary

The SiYuan notebooks represent **aspirational documentation** more than operational reality. They document a sophisticated vision (IES with profile-driven exploration, multi-modal questioning, chat-driven navigation) that is **partially implemented in code but not yet integrated into user workflow**. The gap between documentation and reality is significant:

- **IES Notebook:** Documents a complete system (Phases 1-4 marked complete) but Phase 5 (the user-facing plugin) is not started
- **Therapy Framework Notebook:** Contains 1 developing concept, scaffolding for 3 tracks, but minimal actual content
- **Framework Project Notebook:** Entirely planning-focused; no implementation of configuration system exists

The entity schema in SiYuan uses **lightweight custom attributes** (`custom-type`, `custom-status`, `custom-track`) but doesn't match the rigorous Pydantic schemas in the backend. The notebooks serve as **design documentation** rather than operational knowledge base.

---

## 1. Current Structure: Three Notebooks

### 1.1 Intelligent Exploration System (IES)

**Purpose:** Technical documentation for the generic exploration framework
**Documents:** 64 total (architecture, specs, mockups, dev logs, implementation phases, session examples)
**Status:** Production-ready backend (Phases 1-4 complete), plugin not started

#### Document Hierarchy

```
IES/
├── Overview (status dashboard, vision, quick links)
├── Architecture/
│   ├── System Overview (2-system model: theories ← knowledgebase)
│   ├── Data Flow
│   └── Multi-Agent Orchestration
├── Specs/
│   ├── README
│   ├── Profile System (6 dimensions, ADHD-focused)
│   ├── Entity System (light schema, materialization)
│   ├── Session Processing (extraction pipeline)
│   ├── Question Engine (8 approaches, state detection)
│   ├── API Reference
│   ├── SiYuan Formatting Reference
│   ├── Session Integration
│   └── Plugin Architecture (Develop/Explore/Synthesize modes)
├── Dev Log/
│   └── 2025-12-01 (daily work logs)
├── Implementation/
│   ├── Status (phase tracking)
│   ├── Backend Structure
│   ├── Commands
│   ├── Phases (detailed phase breakdown)
│   └── Phase 2 - Backend Core
├── Design/
│   └── UI Mockups
├── Mockups/
│   ├── Knowledgebase Approaches (3 options evaluated)
│   ├── Session Document Example
│   ├── Knowledge Hub
│   ├── Entity Pages (Narrow Window of Awareness example)
│   └── Integrated Theory (1-Human Mind)
└── Sessions/
    ├── chris/ (8 session documents from 2025-12-01/02)
    └── test/ (1 test document)
```

#### Key Concepts Documented

**Entities:**
- Personal entities: `idea`, `person`, `process`, `question`, `tension`
- Literature entities: `Concept`, `Theory`, `Researcher`, `Assessment` (49k in Neo4j)
- Light schema: `kind`, `domain`, `status` (not rigid types)
- Connections: `supports`, `tensions`, `develops`

**Profile System:**
- 6 dimensions: Processing, Attention, Communication, Executive, Sensory, Masking
- Research-grounded (Barkley, Beck, Big Five, Devon Price)
- Stored: Neo4j (full JSON) + SiYuan (human-readable page)

**Plugin Architecture (NOT IMPLEMENTED):**
- Three modes: Develop (Socratic), Explore (browse graph), Synthesize (build theories)
- Chat-driven navigation (not link clicking)
- Tool-calling architecture: SiYuan tools + Knowledge Graph tools + IES-specific tools
- Reference implementation: siyuan-plugin-copilot

**Question Engine (DESIGNED, NOT IMPLEMENTED):**
- 8 inquiry approaches (Socratic, Metacognitive, Phenomenological, CBT, Solution-focused, Systems, Narrative, Strategic)
- State detection → approach selection
- Profile-influenced phrasing

#### What's Actually Working

✅ **Backend (Phases 1-4 complete):**
- FastAPI on port 8081
- Profile CRUD endpoints
- Entity extraction (Claude API)
- Session processing pipeline
- Question generation (basic)
- Neo4j + Qdrant integration (49k nodes, 27k chunks)

❌ **Not Working:**
- SiYuan plugin (Phase 5 not started)
- Chat interface
- Entity page materialization
- Develop/Explore/Synthesize modes
- Multi-modal questioning
- Real-time session processing

#### Documentation vs. Reality Gap

**Documented as complete but not usable:**
- "Phases 1-4 Complete" → true for backend, but **no user interface exists**
- Plugin Architecture spec → **no code written**
- Entity materialization flow → **API endpoint doesn't exist** (`POST /entities/{name}/materialize`)
- Session Integration spec → **no SiYuan plugin to integrate with**

The IES notebook documents **the system as it should be**, not as it is. It's a **design document** that got marked "complete" when backend APIs were built, but the user-facing layer (plugin) was never started.

---

### 1.2 Therapy Framework

**Purpose:** Content layer for therapeutic worldview development
**Documents:** 14 total (3 track scaffolds, 1 developed concept, connection spaces, templates)
**Status:** Early-stage content development (1 concept "developing", rest scaffolding)

#### Document Hierarchy

```
Therapy Framework/
├── 1-Human Mind/
│   ├── README (track overview, key questions)
│   ├── Narrow Window of Awareness (ONLY developed concept)
│   └── consciousness (stub)
├── 2-Change Process/
│   └── README (track scaffold, no concepts)
├── 3-Method/
│   └── README (track scaffold, no concepts)
├── _Connections/
│   ├── Tensions
│   ├── Foundations
│   └── Open Questions
└── _Inbox/
    └── Unsorted
```

#### Entity Schema in Use

From custom attributes analysis:

```
custom-type: concept, session, transcript, integrated-theory, hub
custom-status: seed, developing, solid, complete
custom-track: 1-human-mind, 2-change-process, 3-method
custom-research-status: needs-research, in-progress, grounded
custom-kind: personal-concept
custom-domain: therapy
```

**Actual usage:**
- 3 concepts tagged with `custom-type: concept`
- 5 documents with `custom-status: developing`
- 2 with `custom-status: seed`
- 5 with `custom-track: 1-human-mind`

#### The One Developed Concept

**Narrow Window of Awareness** is the ONLY concept with substantive content:

**Structure:**
- Core statement (1 paragraph)
- Metadata table (status, track, created, research status)
- "Why I Believe This" (3 subsections: clinical experience, intuition, evidence)
- The Paradox (table comparing organism levels)
- Therapeutic Implications (5 numbered points)
- Open Questions (4 checklist items)
- Related Concepts (4 entities, all "seed" status)
- Research Queue (5 topics with priority ratings)

**Entity Linking Pattern:**
Related concepts use `siyuan://plugins/ies/materialize?entity=...` protocol links to unmaterialized entities. This is the **annotation layer approach** from the mockups—entities exist in graph but pages created on-demand.

**Problems:**
1. Protocol links won't work (no plugin handler registered)
2. Related concepts are listed but don't exist as Neo4j nodes
3. Research queue references literature but no Neo4j links created
4. Custom attributes used but no API to query/update them

#### Content Reality

- **1 concept developing:** Narrow Window of Awareness
- **3-4 concepts seeded:** Mentioned in "Related Concepts" but no pages exist
- **Tracks 2-3:** Empty scaffolding, no concepts identified
- **Connection spaces:** Empty (Tensions, Foundations, Open Questions)

This is **early-stage exploration**, not a developed framework. The structure is ready for content, but content doesn't exist yet.

---

### 1.3 Framework Project

**Purpose:** Implementation instance layer (configuration, deployment, testing)
**Documents:** 27 total (project tracking, session logs, templates, architecture docs)
**Status:** Planning only; no configuration system implemented

#### Document Hierarchy

```
Framework Project/
├── Ideas Hub/
│   └── traversal mode (original IES concept notes)
├── Project Map (status dashboard, architecture diagram, progress tracking)
├── Current State/
│   ├── Active Work
│   ├── Decisions Needed
│   └── Blockers
├── Navigation/
│   ├── Tracks
│   ├── Milestones
│   └── Concept Index
├── Inbox/
│   └── Quick Capture
├── Sessions/ (8 session logs from 2025-11-30 to 2025-12-01)
├── Templates/
│   ├── Concept Template
│   └── Session Log Template
└── Architecture/
    ├── Linking Conventions
    ├── SQL Queries
    └── Intelligent Exploration System (mirrors IES notebook)
```

#### Purpose vs. Reality

**Documented purpose** (from CLAUDE.md):
> Framework Project — Implementation instance for this IES deployment. User profiles, domain overrides, deployment settings.

**Actual content:**
- Project management (tracking work, session logs)
- Session documentation (exploration conversations)
- Navigation aids (concept index, tracks, milestones)
- Templates for content creation

**What's MISSING:**
- No configuration system code
- No user profile storage (documented but not implemented)
- No domain-specific overrides
- No deployment settings

This notebook is a **project workspace** for tracking development work on the system itself, not a "framework implementation instance" as described in CLAUDE.md. The vision of it being a "configuration layer" is aspirational.

#### Observation: Meta-Level Documentation

The Framework Project notebook documents **the work of building the system**, not the system's configuration. It's where development sessions are logged, design ideas are captured, and progress is tracked. It's more like a **project journal** than a framework layer.

---

## 2. Entity Schema Analysis

### 2.1 Backend Schema (Pydantic)

From `ies/backend/src/ies_backend/schemas/entity.py`:

```python
# ENUMS
EntityKind: idea, person, process, question, tension
EntityDomain: therapy, personal, meta
EntityStatus: seed, developing, solid
ConnectionType: supports, tensions, develops

# MODELS
ExtractedEntity:
  - name: str
  - kind: EntityKind
  - domain: EntityDomain
  - status: EntityStatus
  - description: str
  - quotes: list[str]
  - connections: list[EntityConnection]

EntityPageData:
  - Core: name, kind, domain, status, description, quotes
  - Metadata: created_at, updated_at, session_ids
  - Connections: list[EntityConnection]
  - Literature: list[LiteratureLink]
```

**Profile Schema** (`profile.py`):
```python
UserProfile:
  - processing: ProcessingProfile (style, decision_style, habituation_speed, abstraction_preference)
  - attention: AttentionProfile (hyperfocus_triggers, distraction_vulnerabilities, current_capacity, recovery_patterns, optimal_session_length)
  - communication: CommunicationProfile (verbal_fluency, scripts_preference, directness_preference, pace, wait_time_needed)
  - executive: ExecutiveProfile (task_initiation, transition_cost, time_perception, structure_need, working_memory)
  - sensory: SensoryProfile (environment_preference, overwhelm_signals, regulation_tools)
  - masking: MaskingProfile (optional)
```

### 2.2 SiYuan Schema (Custom Attributes)

From SQL query of actual usage:

```
custom-type: concept, session, transcript, integrated-theory, hub
custom-status: seed, developing, solid, complete
custom-track: 1-human-mind, 2-change-process, 3-method
custom-research-status: needs-research, in-progress, grounded
custom-kind: personal-concept
custom-domain: therapy
custom-confidence: medium
custom-created: YYYY-MM-DD
custom-session: 2025-11-29-evening
custom-references: [[Entity Name]]
```

### 2.3 Schema Alignment Issues

| Dimension | Backend | SiYuan | Alignment |
|-----------|---------|--------|-----------|
| **Entity kinds** | 5 types (idea, person, process, question, tension) | Free text (`personal-concept`) | ❌ Mismatch |
| **Entity status** | 3 levels (seed, developing, solid) | 4 levels (+ complete) | ⚠️ Drift |
| **Domain** | 3 domains (therapy, personal, meta) | 1 used (therapy) | ✅ Subset |
| **Connections** | Strongly typed (supports, tensions, develops) | Free text in tables | ❌ No enforcement |
| **Research status** | Not in backend schema | 4 levels in SiYuan | ❌ SiYuan-only |

**Key Problem:** The backend has **rigorous Pydantic validation** but SiYuan uses **freeform custom attributes**. There's no enforcement of schema consistency. A document can have `custom-type: foobar` and the backend won't know.

**Missing:** Bidirectional sync mechanism. Backend creates Neo4j nodes, but SiYuan pages are manually created with potentially inconsistent attributes.

---

## 3. Gaps Between Documentation and Code

### 3.1 Documented But Not Implemented

| Feature | Documented In | Code Status |
|---------|--------------|-------------|
| **SiYuan Plugin** | IES/Specs/Plugin Architecture | ❌ Not started (Phase 5) |
| **Develop/Explore/Synthesize modes** | IES/Specs/Plugin Architecture | ❌ No code exists |
| **Entity materialization** | IES/Specs/Entity System | ❌ API endpoint missing |
| **Question Engine state detection** | IES/Specs/Question Engine | ❌ Designed, not built |
| **Multi-modal questioning** | IES/Specs/Question Engine | ❌ Only basic Socratic exists |
| **Session chat interface** | IES/Specs/Session Integration | ❌ No chat endpoint |
| **Profile-aware prompts** | IES/Specs/Profile System | ⚠️ Schema exists, usage unclear |
| **Configuration system** | Framework/Project Map | ❌ No code, pure planning |
| **Knowledge Hub UI** | IES/Mockups/Knowledge Hub | ❌ Mockup only |

### 3.2 Implemented But Not Documented

| Feature | Code Location | Documentation Status |
|---------|--------------|---------------------|
| **FastAPI backend** | `ies/backend/src/ies_backend/` | ✅ Documented in IES/Implementation |
| **Profile CRUD endpoints** | `ies/backend/src/ies_backend/api/profile.py` | ✅ Documented in IES/Specs/Profile System |
| **Entity extraction** | `ies/backend/src/ies_backend/services/extraction.py` | ✅ Documented in IES/Specs/Entity System |
| **Neo4j graph (49k nodes)** | Docker container | ✅ Documented in IES/Architecture |
| **Qdrant vectors (27k chunks)** | Docker container | ✅ Documented in IES/Architecture |
| **GraphRAG library** | `/library` (Python modules) | ⚠️ Code exists, minimal docs |

### 3.3 Documented vs. Usable

**Status labels are misleading:**

- **"Phases 1-4 Complete"** → True for backend APIs, but **system is not usable** without plugin
- **"Entity System ✅ Implemented"** → Extraction works, but **page materialization doesn't exist**
- **"Profile System ✅ Implemented"** → Schema exists, but **no evidence of actual usage in prompts**
- **"Question Engine 🔄 Designed"** → Honest status (not implemented)

The IES notebook treats **backend implementation** as **system completion**, but the user-facing interface (the plugin) is where the system becomes operational. Without Phase 5, the system is **technically complete but operationally unusable**.

---

## 4. How Notebooks Reflect Reality vs. Aspiration

### 4.1 IES Notebook: 70% Aspirational

**Reality:**
- Working FastAPI backend
- 16 API endpoints tested
- Entity extraction pipeline functional
- Neo4j + Qdrant operational

**Aspiration:**
- SiYuan plugin with chat sidebar
- Develop/Explore/Synthesize modes
- Chat-driven entity materialization
- Profile-aware questioning
- Multi-modal inquiry approaches

**Ratio:** ~30% built, 70% designed but not implemented.

The IES notebook is a **comprehensive design specification** that treats design completion as implementation completion. It's excellent documentation for **what to build**, but conflates "specified" with "done."

### 4.2 Therapy Framework Notebook: 95% Aspirational

**Reality:**
- 1 concept with substantive content ("Narrow Window of Awareness")
- 3 track scaffolds (READMEs with questions)
- Templates for content creation

**Aspiration:**
- Integrated theory across 3 tracks
- Dozens of concepts per track
- Rich connection mapping (Tensions, Foundations, Open Questions)
- Research-grounded concepts
- Synthesized understanding of therapeutic worldview

**Ratio:** ~5% developed content, 95% scaffolding and vision.

This notebook is **early-stage exploration**. The structure is ready (tracks, connection spaces, templates) but content hasn't been created yet. The vision is clear, execution just started.

### 4.3 Framework Project Notebook: 100% Meta (Not Framework)

**Reality:**
- Project tracking (active work, blockers, decisions)
- Session logs (development conversations)
- Design idea capture
- Progress monitoring

**Aspiration (from CLAUDE.md):**
- Configuration system for IES instances
- User profile storage
- Domain-specific overrides
- Deployment settings

**Ratio:** 0% configuration layer, 100% project journal.

This notebook serves a **different purpose** than documented. It's not a "framework implementation instance"—it's a **meta-workspace for managing the project itself**. The configuration layer vision exists only in CLAUDE.md, not in the notebook or code.

---

## 5. Knowledge Graph Structure Serving the Vision

### 5.1 Current Graph Structure (Neo4j)

**Entity Types:**
- Literature: `Concept`, `Theory`, `Researcher`, `Assessment` (49k nodes from 51 books)
- Personal: Not yet in graph (extraction works, storage unclear)

**Relationships:**
- Literature relationships exist (concept → theory, theory → researcher)
- Personal entity relationships documented but not observed in graph

**Access Pattern:**
- Vector search via Qdrant (27k chunks)
- Graph queries via Neo4j (Cypher)
- No SiYuan integration (plugin doesn't exist)

### 5.2 Intended Graph Structure (From Specs)

**Two-Layer Model:**

```
┌─────────────────────────────────────────────────────────────┐
│                    INTEGRATED THEORIES                       │
│                    (What you're building)                    │
│                                                              │
│   Track 1: Human Mind                                        │
│   Track 2: Change Process                                    │
│   Track 3: Method                                            │
│                                                              │
│                         ↑ built from ↓                       │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                      KNOWLEDGEBASE                           │
│                                                              │
│   Personal Entities  ←→  Literature Entities                │
│   (from sessions)        (from books, 49k)                  │
└─────────────────────────────────────────────────────────────┘
```

**Connection Pattern:**
- Personal concepts link TO literature (grounding)
- Literature links BACK to personal (context)
- Integrated theories synthesize across both

**Reality Check:**
This is a beautiful vision, but **personal entities aren't in the graph yet**. The extraction pipeline works, but graph storage/linking is unclear. The "two-layer model" is aspirational.

### 5.3 Flow Mode + Self-Understanding Vision

From the design docs, the ultimate vision:

> **Flow Mode:** ADHD-friendly exploration that preserves momentum, provides clear entry points, avoids blank-page paralysis, and enables thread-following without getting lost.

> **Self-Understanding:** Articulate therapeutic worldview by exploring personal concepts, grounding them in literature, identifying tensions, and building integrated theories.

**How Graph Structure Should Support This:**

1. **Flow Mode Requirements:**
   - Recent context loading (what was I exploring?)
   - Hanging threads (where did I leave off?)
   - Entry points (what can I explore now?)
   - Breadcrumbs (how did I get here?)

2. **Self-Understanding Requirements:**
   - Personal concept maturity tracking (seed → developing → solid)
   - Literature grounding (which books support this idea?)
   - Contradiction detection (what tensions exist?)
   - Theory synthesis (how do concepts integrate?)

**Current Graph Support:** ❌ **Inadequate**

- No "recent sessions" query
- No "hanging threads" tracking
- No "entry points" discovery
- Personal concepts not stored in graph
- No tension detection
- No theory synthesis

**Missing Graph Entities to Support Vision:**

| Entity Type | Purpose | Status |
|-------------|---------|--------|
| **Session** | Track exploration history | ❌ Not in graph |
| **Thread** | Capture ongoing inquiries | ❌ Not designed |
| **Entry Point** | Surfaced exploration opportunities | ❌ Not designed |
| **Tension** | Contradictions between concepts | ⚠️ Designed (entity kind) but no detection |
| **Integrated Theory** | Synthesized understanding | ⚠️ Designed as doc type, not graph node |
| **Research Queue** | Concepts needing grounding | ⚠️ In SiYuan tables, not graph |

---

## 6. Recommendations

### 6.1 Immediate: Align Expectations with Reality

**Problem:** Documentation claims "Phases 1-4 Complete" but system is unusable without plugin.

**Recommendation:** Update status labels to reflect operational reality:

```
Phase 1: Profile Foundation        ✅ Backend Complete, 🔲 No UI
Phase 2: Backend Core              ✅ APIs Complete, 🔲 No Integration
Phase 3: Question Engine           ⚠️ Basic Only, 🔲 Multi-modal Not Built
Phase 4: Session Integration       ⚠️ Backend Only, 🔲 Plugin Missing
Phase 5: SiYuan Plugin             🔲 Not Started ← BLOCKER FOR USABILITY
```

**Impact:** Sets honest expectations; focuses development on Phase 5 as critical path.

### 6.2 Short-term: Entity Schema Enforcement

**Problem:** Backend has rigid Pydantic schemas, SiYuan uses freeform custom attributes, no sync mechanism.

**Recommendation:** Implement schema validation for SiYuan entity pages:

1. **Backend API:** `POST /validate/entity-page` endpoint
   - Accepts SiYuan block attributes
   - Validates against EntityKind/Status/Domain enums
   - Returns errors if schema violated

2. **SiYuan Integration:** Pre-save hook in future plugin
   - Validates custom attributes before save
   - Prevents `custom-type: foobar` mistakes
   - Enforces consistency with Neo4j schema

3. **Migration:** Audit existing pages, fix schema drift
   - Change `custom-status: complete` → `solid` (backend only has 3 levels)
   - Change `custom-kind: personal-concept` → `custom-kind: idea` (match backend enum)

**Impact:** Ensures graph/SiYuan consistency, prevents data quality degradation.

### 6.3 Medium-term: Personal Entity Storage

**Problem:** Extraction works, but personal entities not observed in Neo4j. Graph is all literature.

**Recommendation:** Verify and document personal entity storage:

1. **Audit:** Query Neo4j for personal entities
   ```cypher
   MATCH (n) WHERE n.domain = 'personal' RETURN count(n)
   ```

2. **If missing:** Implement personal entity storage in extraction pipeline
   - Create nodes with `domain: personal`
   - Store quotes, connections, session_ids
   - Link to literature entities

3. **Document:** Update IES/Specs/Entity System with:
   - Cypher queries for personal entities
   - Example personal → literature links
   - Session → entity relationships

**Impact:** Makes the "two-layer model" operational, enables personal concept tracking.

### 6.4 Medium-term: Session Context in Graph

**Problem:** Flow Mode requires "recent sessions" and "hanging threads" but graph doesn't store sessions.

**Recommendation:** Add Session nodes to Neo4j:

```cypher
CREATE (s:Session {
  id: "2025-12-01-narrow-window",
  user_id: "chris",
  date: "2025-12-01",
  topic: "Narrow Window Emergence",
  hanging_question: "How distinguish necessary vs unnecessary pain?"
})

// Link to explored entities
CREATE (s)-[:EXPLORED {context: "Initial articulation"}]->(e:Entity {name: "Narrow Window of Awareness"})

// Link to extracted entities
CREATE (s)-[:CREATED]->(e2:Entity {name: "Meaning as Solution"})
```

**Schema:**
```python
Session:
  - id: str (unique identifier)
  - user_id: str
  - date: str
  - topic: str
  - duration_minutes: int
  - entities_explored: list[str] (via relationships)
  - entities_created: list[str] (via relationships)
  - hanging_question: str (optional)
  - mode: str (develop, explore, synthesize)
```

**Impact:** Enables "where did I leave off?" queries, supports Flow Mode entry points.

### 6.5 Long-term: Tension Detection

**Problem:** Framework needs to identify contradictions but no mechanism exists.

**Recommendation:** Implement contradiction detection:

1. **Entity Extraction:** When creating connections, identify "tensions" relationships
   - Already in schema: `ConnectionType.TENSIONS`
   - Prompt Claude to identify contradictions during extraction

2. **Graph Query:** Find tension subgraphs
   ```cypher
   MATCH (a:Entity)-[r:TENSIONS]->(b:Entity)
   RETURN a.name, b.name, r.context
   ```

3. **SiYuan Page:** Auto-generate "Tensions" section showing conflicting concepts
   - "Narrow Window supports meaning-making but tensions with Efficiency vs Experience"
   - Surface in _Connections/Tensions notebook

**Impact:** Supports self-understanding by highlighting unresolved contradictions.

### 6.6 Long-term: Research Queue as Graph Entities

**Problem:** Research queue exists as SiYuan table cells, not queryable/prioritizable.

**Recommendation:** Create ResearchItem nodes:

```cypher
CREATE (r:ResearchItem {
  topic: "Predictive processing (Friston, Clark, Seth)",
  reason: "Mechanism for meaning-making",
  priority: "high",
  concept: "Narrow Window of Awareness",
  status: "queued"
})

CREATE (e:Entity {name: "Narrow Window of Awareness"})-[:NEEDS_RESEARCH]->(r)
```

**Impact:** Enables priority sorting, tracks research progress, links findings back to concepts.

### 6.7 Structural: Framework Project Clarity

**Problem:** Notebook serves as project journal but documented as "configuration layer."

**Recommendation:** Rename or clarify purpose:

**Option A:** Rename to "Development Log" or "Project Journal"
- Acknowledge it's a meta-workspace
- Remove references to "configuration system" in CLAUDE.md
- Update docs/structure.md to reflect actual purpose

**Option B:** Create actual Framework configuration layer
- Implement user profile storage (SiYuan page + Neo4j sync)
- Implement domain overrides (therapy-specific extraction prompts)
- Implement deployment settings (environment configs)
- Move project tracking to separate notebook

**Recommendation:** Choose Option A. The notebook is useful as-is. Don't force it into a role it doesn't serve.

---

## 7. Knowledge Graph Structure to Support Vision

### 7.1 Missing Entity Types

To fully support Flow Mode + Self-Understanding:

| Entity Type | Purpose | Relationships |
|-------------|---------|---------------|
| **Session** | Track exploration history | EXPLORED(Entity), CREATED(Entity), FOLLOWED(Thread) |
| **Thread** | Ongoing inquiry | BRANCHES_FROM(Thread), RESOLVES_TO(Entity), BLOCKED_BY(Question) |
| **Question** | Open inquiry | ASKED_IN(Session), RELATES_TO(Entity), ANSWERED_BY(Entity) |
| **IntegratedTheory** | Synthesized understanding | SYNTHESIZES(Entity), DEVELOPS_FROM(Theory), TRACKS(Track) |
| **Track** | Organizational structure | CONTAINS(Entity), PART_OF(IntegratedTheory) |
| **ResearchItem** | Grounding need | GROUNDS(Entity), REFERENCES(Book), STATUS(queued/in-progress/done) |

### 7.2 Critical Relationships

**For Flow Mode:**
```cypher
// Where did I leave off?
MATCH (u:User)-[:LAST_SESSION]->(s:Session)-[:HANGING_QUESTION]->(q:Question)
RETURN s, q

// What can I explore now?
MATCH (e:Entity {status: 'developing'})-[:NEEDS_RESEARCH]->(r:ResearchItem {status: 'queued'})
RETURN e, r ORDER BY r.priority DESC

// How did I get here?
MATCH path = (start:Entity)-[:DEVELOPS*1..3]->(current:Entity)
RETURN path
```

**For Self-Understanding:**
```cypher
// What tensions exist?
MATCH (a:Entity)-[:TENSIONS]->(b:Entity)
WHERE a.domain = 'personal' OR b.domain = 'personal'
RETURN a, b

// What needs grounding?
MATCH (e:Entity {domain: 'personal'})-[:SUPPORTED_BY]->(lit:Concept)
WITH e, count(lit) as support_count
WHERE support_count < 3
RETURN e.name, support_count

// What's ready to synthesize?
MATCH (e:Entity {status: 'solid', track: '1-human-mind'})
RETURN e.name, e.description
```

### 7.3 Schema Extensions Needed

**Current Entity Schema:**
```python
ExtractedEntity:
  - name, kind, domain, status
  - description, quotes
  - connections
```

**Extended Entity Schema:**
```python
ExtractedEntity:
  # Existing
  - name, kind, domain, status
  - description, quotes
  - connections

  # NEW: Context tracking
  - session_ids: list[str]  # Where discussed
  - created_in: str         # Originating session
  - last_updated: str       # Most recent mention

  # NEW: Development tracking
  - confidence: int         # 1-10 how certain
  - research_items: list[ResearchItem]  # What needs investigation
  - questions: list[str]    # Hanging questions

  # NEW: Integration tracking
  - track: str              # Which framework track
  - theory_id: str          # If part of integrated theory
  - synthesis_ready: bool   # Enough connections to synthesize?
```

---

## 8. Conclusion

The SiYuan notebooks represent **sophisticated design thinking** but reveal a **large implementation gap**:

### Current State
- **IES Notebook:** Comprehensive design spec, 30% implemented (backend only)
- **Therapy Framework:** Early-stage scaffolding, 5% content developed
- **Framework Project:** Project journal, 0% configuration layer

### Key Findings

1. **Backend vs. Frontend Gap:** Phases 1-4 "complete" but system unusable without plugin (Phase 5)

2. **Schema Drift:** Backend has rigid Pydantic schemas, SiYuan uses freeform custom attributes, no sync

3. **Personal Entities Missing:** Graph is 100% literature, personal concepts not stored/linked

4. **Flow Mode Unsupported:** No session tracking, hanging threads, or entry point discovery in graph

5. **Documentation Aspiration:** Notebooks document the system as it should be, not as it is

### Priority Actions

**P0 (Blocking):** Build Phase 5 plugin to make system usable
**P1 (Quality):** Implement entity schema validation and sync
**P2 (Flow Mode):** Add Session nodes to graph for context tracking
**P3 (Self-Understanding):** Store personal entities in graph with literature links
**P4 (Content):** Develop Track 1 concepts beyond single example

### The Notebooks' True Value

The SiYuan notebooks are **excellent design documentation** that:
- Articulate a clear vision for the system
- Specify entity schemas and relationships
- Mock up user interactions
- Track development progress

They should be valued as **design artifacts**, not operational knowledge base. The real work is translating these specifications into working code (Phase 5 plugin) and developing content (Therapy Framework concepts).

The vision is sound. The gap is execution.

---

**Appendices**

- [A] SQL queries used for analysis
- [B] Custom attribute usage breakdown
- [C] Neo4j schema (if accessible)
- [D] Backend API endpoint inventory
