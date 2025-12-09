# IES System Design — Conceptual Foundation

**Created:** 2025-12-09
**Status:** Ground Truth Document
**Purpose:** Define the cognitive architecture, operating model, and semantic foundations of IES

---

## Document Hierarchy

This document is the **conceptual foundation**. Other docs depend on it:

```
IES-SYSTEM-DESIGN.md          ← YOU ARE HERE (Ground Truth - WHY & HOW)
    │
    ├── UNIFIED-PROJECT-SPEC.md       (WHAT is active, migration status)
    ├── ARCHITECTURE-AND-INTERACTIONS.md  (Technical structure, APIs, data flows)
    └── GAP-ANALYSIS.md               (Implementation vs specification)
```

**Rule:** If any document conflicts with this one, this document wins.

---

## Table of Contents

1. [Why IES Exists](#1-why-ies-exists)
2. [The IES Operating Model](#2-the-ies-operating-model)
3. [Cognitive Architecture](#3-cognitive-architecture)
4. [Flow Mode: Master Definition](#4-flow-mode-master-definition)
5. [Entity Lifecycle & Knowledge Gradient](#5-entity-lifecycle--knowledge-gradient)
6. [Cross-Layer Identity Scheme](#6-cross-layer-identity-scheme)
7. [Context System](#7-context-system)
8. [Interaction Semantics](#8-interaction-semantics)
9. [Capture Pipeline](#9-capture-pipeline)
10. [Agent Orchestration](#10-agent-orchestration)
11. [Error States & Recovery](#11-error-states--recovery)
12. [System Boundaries & Safety](#12-system-boundaries--safety)
13. [Versioning & Invalidation](#13-versioning--invalidation)
14. [Cross-Layer Synchronization](#14-cross-layer-synchronization)
15. [Developer Experience Standards](#15-developer-experience-standards)

---

## 1. Why IES Exists

### The Problem

**ADHD brains work differently:**
- Interest-based activation, not importance-based
- Working memory limitations affect sustained attention
- Time perception distortions make planning unreliable
- Emotional dysregulation affects cognitive access
- Executive function deficits block task initiation

**Traditional knowledge management fails because:**
- Requires upfront categorization (cognitive load)
- Punishes exploration (forces linear progress)
- Loses context across sessions (working memory burden)
- Ignores emotional state (no resonance tracking)
- Treats capture as filing (shame-inducing backlog)

### The Solution

**IES is a thinking partner that:**
- Meets you where your attention is (context-aware)
- Captures without requiring categorization (friction-free)
- Remembers what you were thinking (journey tracking)
- Grows structure from exploration (emergent organization)
- Uses your curiosity as fuel (Flow Mode)

### The Core Loop

```
EXPLORE → CAPTURE → GROW → CONNECT → UNDERSTAND
   │          │        │        │          │
   │          │        │        │          └── Synthesis: answers emerge
   │          │        │        └── Relationships form between concepts
   │          │        └── Sparks become Insights become Concepts
   │          └── Highlights, notes, reactions captured with context
   └── Follow curiosity through books, entities, facets
```

**The virtuous cycle:** Each exploration feeds the graph, which enables better exploration.

---

## 2. The IES Operating Model

### How the System Behaves Over Time

**Session Start:**
1. User opens IES Reader or SiYuan plugin
2. System recalls last active Context (if any)
3. System shows recent journey entries
4. User can: continue where they left off, start fresh, or pick different Context

**During a Session:**
1. User explores (reads, clicks entities, follows facets)
2. System tracks journey (every meaningful action logged)
3. User captures (highlights, notes, questions)
4. System processes captures (entity extraction, context tagging)
5. Knowledge grows (graph enriched, connections form)

**Session End:**
1. System summarizes session progress
2. Pending captures queued for processing
3. Journey entry created for session
4. Context state persisted

### Mode Selection Logic

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MODE SELECTION DECISION TREE                     │
└─────────────────────────────────────────────────────────────────────┘

User Intent                          → Recommended Mode
─────────────────────────────────────────────────────────────────────
"I want to read this book"           → Reader Mode (Normal)
"I have a question to explore"       → Reader Mode (Question/Journey)
"I want to understand X"             → Flow Mode (start at entity X)
"I need to think through something"  → ForgeMode (select thinking template)
"I just had an idea"                 → Quick Capture
"I want to see my progress"          → Dashboard
"I want to process captures"         → Inbox Mode

Cognitive State                      → System Adjustment
─────────────────────────────────────────────────────────────────────
Low energy                           → Simpler UI, fewer options
High energy                          → Full exploration capabilities
Stuck/frustrated                     → Suggest mode change or break
In flow                              → Minimize interruptions
```

### Context Propagation Rules

1. **Explicit context:** User selects a Context (Feynman Problem, Project, etc.)
2. **Inferred context:** System detects from current note or book
3. **Inherited context:** Child actions inherit parent's context
4. **No context:** Captures go to Inbox for later processing

**Context persists until:**
- User explicitly changes it
- Session ends (reverts to "no context")
- Timeout after 4 hours of inactivity

---

## 3. Cognitive Architecture

### Mapping User Intention to System Behavior

```
┌─────────────────────────────────────────────────────────────────────┐
│                      COGNITIVE ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────┘

USER INTENTION          COGNITIVE OPERATION        SYSTEM MODE
───────────────────────────────────────────────────────────────────────
"What is this?"         Schema surfacing           Flow Mode (entity)
"How does X relate to   Relationship mapping       Flow Mode (facets)
 Y?"
"Why does X happen?"    Causal reasoning           Question exploration
"What do I think        Articulation               ForgeMode (Articulating)
 about this?"
"How should I           Planning                   ForgeMode (Planning)
 approach this?"
"What if...?"           Counterfactual thinking    ForgeMode (Ideating)
"What did I learn?"     Synthesis                  ForgeMode (Reflecting)
"I just noticed..."     Resonance capture          Quick Capture
```

### The Five Thinking Modes (ForgeMode)

| Mode | Cognitive Function | Template Purpose | Question Classes Used |
|------|-------------------|------------------|----------------------|
| **Learning** | Understanding mechanisms | Map how something works | Schema-Probe, Causal, Anchor |
| **Articulating** | Clarifying intuitions | Turn vague sense into words | Boundary, Dimensional, Meta-Cognitive |
| **Planning** | Structuring action | Create actionable plan | Dimensional, Causal, Counterfactual |
| **Ideating** | Generating possibilities | Explore creative options | Counterfactual, Perspective-Shift |
| **Reflecting** | Integrating experience | Extract lessons learned | Meta-Cognitive, Reflective-Synthesis |

### Nine Question Classes

| Class | Cognitive Function | When Used |
|-------|-------------------|-----------|
| **Schema-Probe** | Surfaces hidden structure | "What are the parts of this?" |
| **Boundary** | Clarifies edges/limits | "What is NOT included?" |
| **Dimensional** | Introduces spectra | "On a scale from X to Y..." |
| **Causal** | Pushes for mechanisms | "What causes this?" |
| **Counterfactual** | Exposes assumptions | "What if the opposite?" |
| **Anchor** | Grounds in concrete | "Give me a specific example" |
| **Perspective-Shift** | Changes viewpoint | "How would X see this?" |
| **Meta-Cognitive** | Checks thinking patterns | "How confident are you?" |
| **Reflective-Synthesis** | Ties threads together | "What's the main insight?" |

### Cognitive State Detection

The system monitors user behavior to detect cognitive states:

| State | Indicators | System Response |
|-------|-----------|-----------------|
| **Flowing** | Consistent engagement, quick actions | Minimize interruptions |
| **Stuck** | Repeated same query, long pauses | Offer reframe, suggest different angle |
| **Overwhelmed** | Rapid context switching, many open items | Suggest pause, simplify view |
| **Exploring** | Varied queries, breadth-first | Enable wandering, track trail |
| **Focusing** | Depth-first, same topic | Provide deeper resources |
| **Low energy** | Slow actions, short captures | Reduce complexity |

---

## 4. Flow Mode: Master Definition

### What Flow Mode IS

**Flow Mode is curiosity-driven exploration with memory.**

It enables:
- Following interest wherever it leads (facet traversal)
- Seeing connections (graph visualization)
- Accumulating evidence (passage collection)
- Asking questions (question generation)
- Never losing context (journey tracking)

### Flow Mode Principles

1. **Trail Always Visible:** User always sees where they came from
2. **One Click to Dive:** Any entity/facet/question is one click away
3. **Evidence Accumulates:** Relevant passages attach automatically
4. **Questions Emerge:** System suggests questions based on exploration
5. **No Dead Ends:** Every entity has facets, every facet leads somewhere
6. **Return is Free:** Can jump back to any point in trail

### Flow Mode Inputs

| Input | Required | Source |
|-------|----------|--------|
| Starting entity or question | Yes | User selection or text highlight |
| Context ID | Recommended | Active context or inferred |
| Book/source scope | Optional | Current book or all sources |

### Flow Mode Behavioral Guarantees

1. **Facets load within 2 seconds** (cached or generated)
2. **Evidence appears within 5 seconds** (indexed lookup)
3. **Trail persists for session** (survives page navigation)
4. **No data loss on crash** (journey logged incrementally)
5. **Works offline** (degraded mode with cached data)

### Flow State in Reader vs SiYuan

| Aspect | IES Reader | SiYuan Plugin |
|--------|------------|---------------|
| **Entry point** | Text selection, entity overlay click | Search, Context Note, direct navigation |
| **Panel location** | Right side panel | Left dock |
| **Evidence display** | Passages with "Jump to" | Passages with "Open in Reader" |
| **Trail persistence** | Session-based (flowStore) | Session + document-linked |
| **Capture target** | NotesSheet → SiYuan sync | Direct to SiYuan note |

---

## 5. Entity Lifecycle & Knowledge Gradient

### The Knowledge Gradient

Knowledge matures through stages. Each stage has different characteristics:

```
RAW TEXT                     (Source material)
    │
    ▼
HIGHLIGHT                    (Selected passage with location)
    │ + resonance signal
    ▼
SPARK                        (Raw resonance capture)
    │ + reflection
    ▼
INSIGHT                      (Processed meaning)
    │ + relationships
    ▼
CONCEPT                      (Named, defined entity)
    │ + evidence + relationships
    ▼
KNOWLEDGE GRAPH ENTITY       (Integrated into graph)
    │ + synthesis
    ▼
SYNTHESIS                    (Answer, theory, model)
```

### Stage Definitions

| Stage | What It Is | Required Fields | Where Stored |
|-------|-----------|-----------------|--------------|
| **Highlight** | Selected text with location | text, cfi, book_id | Reader (local) |
| **Spark** | Raw capture with emotional signal | content, resonance, energy | Neo4j (Personal Graph) |
| **Insight** | Reflected-upon spark | content, source_spark_id | Neo4j (Personal Graph) |
| **Concept** | Named entity with definition | name, type, description | Neo4j (Domain Graph) |
| **Entity** | Graph node with relationships | name, type, relationships | Neo4j (Domain Graph) |
| **Synthesis** | Answer or theory | content, question_id, evidence | SiYuan + Neo4j |

### Transitions Between Stages

| Transition | Trigger | Process |
|-----------|---------|---------|
| Text → Highlight | User selects + saves | CFI captured, stored locally |
| Highlight → Spark | Sync to backend | Add resonance/energy, create Spark node |
| Spark → Insight | User promotes | Reflect, add context, create Insight |
| Insight → Concept | Formalization | Name, define, add relationships |
| Concept → Entity | Graph integration | Merge with existing or create new |
| Entity → Synthesis | Answer generation | Combine evidence, create answer block |

### Entity Type Progression

```
PERSONAL ENTITIES (ADHD-friendly capture)
┌──────────────────────────────────────────────────────────────────┐
│  Spark → Insight → Thread → Favorite Problem                     │
│    │        │         │           │                              │
│    │        │         │           └── Stable anchor question     │
│    │        │         └── Connected exploration path             │
│    │        └── Processed meaning with source                    │
│    └── Raw resonance capture                                     │
└──────────────────────────────────────────────────────────────────┘

DOMAIN ENTITIES (Book-derived knowledge)
┌──────────────────────────────────────────────────────────────────┐
│  Book → Chunk → Concept → Theory → Framework                     │
│    │      │        │         │          │                        │
│    │      │        │         │          └── Organizing structure │
│    │      │        │         └── Explanatory model               │
│    │      │        └── Named idea with definition                │
│    │      └── Text segment with entities                         │
│    └── Source material                                           │
└──────────────────────────────────────────────────────────────────┘
```

---

## 6. Cross-Layer Identity Scheme

### ID Format Specification

All IDs follow a consistent format: `{type}_{source}_{unique}`

| Entity Type | ID Format | Example |
|-------------|-----------|---------|
| Book (Calibre) | `book_calibre_{calibre_id}` | `book_calibre_123` |
| Book (Neo4j) | `book_neo4j_{element_id}` | `book_neo4j_4:abc123` |
| Entity | `entity_{type}_{hash}` | `entity_concept_a1b2c3` |
| Spark | `spark_{timestamp}_{hash}` | `spark_20251209_x7y8z9` |
| Insight | `insight_{timestamp}_{hash}` | `insight_20251209_p3q4r5` |
| Context | `ctx_{type}_{hash}` | `ctx_feynman_m2n3o4` |
| Question | `q_{context}_{hash}` | `q_feynman_s5t6u7` |
| Journey | `journey_{date}_{session}` | `journey_20251209_001` |
| Session | `session_{mode}_{timestamp}` | `session_learning_20251209143000` |
| Highlight | `hl_{book}_{cfi_hash}` | `hl_calibre123_v8w9x0` |
| SiYuan Doc | `sy_{notebook}_{block_id}` | `sy_ies_20251209143000-abc123` |

### ID Propagation Rules

```
SOURCE                    DERIVED IDS                   STORAGE
───────────────────────────────────────────────────────────────────
Calibre book added   →   book_calibre_123           → Neo4j, Backend
                    →   Book Note sy_ies_*          → SiYuan

Highlight captured  →   hl_calibre123_*             → Reader (local)
                    →   spark_* (on sync)           → Neo4j
                    →   Block in Book Note          → SiYuan

Entity extracted    →   entity_concept_*            → Neo4j
                    →   Concept Note sy_ies_*       → SiYuan (if promoted)

Question created    →   q_feynman_*                 → Neo4j
                    →   Block in Context Note       → SiYuan
```

### Cross-Layer ID Mapping

| Layer | Stores | Maps To |
|-------|--------|---------|
| **Calibre** | calibre_id (integer) | Neo4j book node, Backend API |
| **Neo4j** | element_id (string) | Backend entities, SiYuan custom-id |
| **Backend** | UUID or hash | Frontend state, SiYuan block attributes |
| **SiYuan** | block_id (string) | Backend custom-id, Neo4j element_id |
| **Reader** | Local storage keys | Backend sync endpoints |

### Canonical Location Reference

For any passage in a book, the canonical reference is:

```json
{
  "book_id": "book_calibre_123",
  "cfi": "/6/4[chap03]!/4/2/1:0",
  "text_hash": "sha256:abc123...",
  "page_approx": 42
}
```

This allows:
- Jump-back from any app
- Deduplication of same passage
- Evidence linking across sources

---

## 7. Context System

### What is a Context?

A **Context** is a bounded space of attention. It answers: "What am I trying to understand?"

**Context Types:**

| Type | Purpose | Example |
|------|---------|---------|
| `feynman_problem` | Deep question to understand | "What is ADHD time perception?" |
| `project` | Concrete deliverable | "IES Flow Mode v2" |
| `theory` | Explanatory model | "Motivation & Task Initiation" |
| `concept_cluster` | Related concepts | "Executive Function Components" |
| `life_area` | Ongoing domain | "Therapy Practice" |

### Context Creation

**Explicit creation:** User creates Context Note with structure
**Implicit creation:** System detects repeated theme in captures
**Promotion:** Spark/Insight promoted to new Context

### Context Boundaries

A Context defines what is "in scope" for:
- **Questions:** Which questions belong to this context
- **Extraction:** What concepts/relations to look for
- **Sources:** Which books/papers are relevant
- **Journeys:** Which exploration sessions contribute

### Context Interaction Rules

1. **One active context at a time** per app
2. **Context can have parent** (nested contexts)
3. **Captures inherit active context** (or go to Inbox)
4. **Questions belong to exactly one context** (primary)
5. **Entities can relate to multiple contexts** (shared knowledge)

### Context Note Structure (SiYuan)

```markdown
# {Type}: {Title}

{: custom-type="{type}" custom-id="{context_id}" custom-status="{status}" }

## Summary / Intent
{What I'm trying to understand}

## Key Questions
- [ ] Q1: {question text}
- [ ] Q2: {question text}

## Areas of Exploration
- A1: {area description}
- A2: {area description}

## Core Concepts
- [[Concept: X]]
- [[Concept: Y]]

## Current Best Understanding
{Synthesis section - updated by AI}

## Evidence Pool
{Linked highlights and passages}

## Journey
{Auto-populated exploration history}
```

---

## 8. Interaction Semantics

### What Actions Mean

| Action | Semantic Meaning | System Effect |
|--------|-----------------|---------------|
| **Click entity** | "Show me more about X" | Load entity details, add to trail |
| **Click facet** | "Explore this aspect of X" | Navigate to facet entity or create |
| **Click question** | "This is what I want to know" | Set as active focus, filter evidence |
| **Highlight text** | "This is significant" | Create highlight, queue for processing |
| **Add note** | "This is what I think" | Create capture with context |
| **Click evidence** | "Show me the source" | Jump to passage in Reader |
| **Back button** | "Return to previous focus" | Pop trail stack |
| **Create concept** | "This deserves a name" | Formalize into graph entity |

### When System Creates Graph Entities

**Always create:**
- Book ingested from Calibre → Book node
- Entity extracted from text → Entity node (if new)
- Question created by user → Question node

**Create on promotion:**
- Spark promoted → Insight node
- Insight formalized → Concept node
- Concept with relationships → Full entity with edges

**Never auto-create:**
- Facets (suggested only, user confirms)
- Relationships (AI proposes, user approves above threshold)
- Synthesis (always requires user trigger)

### When Actions Create Journey Steps

| Action | Creates Journey Step | Step Type |
|--------|---------------------|-----------|
| Open book | Yes | `session_start` |
| Navigate to entity | Yes | `entity_focus` |
| Navigate to facet | Yes | `facet_explore` |
| Highlight text | Yes | `capture` |
| Add note | Yes | `capture` |
| Run extraction | Yes | `extraction` |
| Ask question | Yes | `question_ask` |
| Complete ForgeMode section | Yes | `template_section` |
| Click back | No | (navigation only) |
| Toggle UI element | No | (ui only) |

---

## 9. Capture Pipeline

### End-to-End Capture Flow

```
USER ACTION                    READER                BACKEND               SIYUAN
───────────────────────────────────────────────────────────────────────────────────

1. Select text            ┌──────────────┐
   in epub               │ Get CFI range │
                         └──────┬───────┘
                                │
2. Tap "Capture"          ┌─────▼─────────┐
   (or FAB on mobile)    │ Show NotesSheet│
                         └──────┬─────────┘
                                │
3. Add note,              ┌─────▼─────────┐
   select type           │ User input     │
                         └──────┬─────────┘
                                │
4. Save                   ┌─────▼─────────┐     ┌───────────────┐
                         │ POST /sync/    │────▶│ Validate      │
                         │ highlights     │     │ Create Spark  │
                         └──────┬─────────┘     └───────┬───────┘
                                │                       │
5. Confirm                ┌─────▼─────────┐            │
                         │ Show success   │            │
                         └────────────────┘            │
                                                       │
6. Process                                      ┌──────▼───────┐
   (async)                                     │ Entity extract│
                                               │ Context tag   │
                                               └───────┬───────┘
                                                       │
7. Sync to                                             │     ┌────────────────┐
   SiYuan                                              └────▶│ Find/Create    │
                                                             │ Book Note      │
                                                             │ Append block   │
                                                             └────────────────┘
```

### Required Capture Metadata

Every capture MUST include:

| Field | Required | Source |
|-------|----------|--------|
| `text` | Yes | Selected text |
| `book_id` | Yes | Calibre ID |
| `cfi` | Yes | epub.js CFI |
| `created_at` | Yes | Timestamp |
| `context_id` | If active | Current context |
| `note` | Optional | User annotation |
| `resonance` | Optional | Emotional signal |
| `energy` | Optional | Current energy level |

### Offline Behavior

When offline:
1. Captures stored in IndexedDB
2. Queue indicator shows pending count
3. On reconnect: sync queue processes in order
4. Conflicts: newer timestamp wins (user notified)

---

## 10. Agent Orchestration

### Agent Types and Responsibilities

| Agent | Trigger | Input | Output |
|-------|---------|-------|--------|
| **Intake** | New capture | Highlight/note | Entity refs, connections, classification |
| **Enrichment** | Flow activation | Entity + context | Facets, evidence, gaps |
| **Synthesis** | User request | Question + evidence | Answer block, summary |
| **Processing** | Queue check | Pending items | Processed items |

### Agent Execution Contract

Agents MUST:
1. **Be idempotent:** Same input → same output
2. **Be auditable:** Log all decisions with reasoning
3. **Respect confidence thresholds:** Only auto-approve above 0.8
4. **Create journey entries:** Document their actions
5. **Never delete user content:** Only annotate, link, or propose

Agents MUST NOT:
1. Modify original text
2. Delete captures or entities
3. Auto-approve below threshold
4. Execute without logging
5. Run without rate limits

### Processing Queue Schema

```json
{
  "id": "job_123",
  "type": "intake | enrichment | synthesis",
  "status": "pending | processing | needs_review | completed | failed",
  "priority": 1-10,
  "target": {
    "type": "highlight | spark | entity | question",
    "id": "target_id"
  },
  "context_id": "ctx_...",
  "created_at": "2025-12-09T...",
  "started_at": null,
  "completed_at": null,
  "proposed_actions": [],
  "approved_actions": [],
  "rejected_actions": [],
  "error": null
}
```

### Approval Workflow

```
AGENT PROPOSES ACTION
        │
        ▼
┌───────────────────┐
│ Confidence >= 0.8 │──── Yes ───▶ AUTO-APPROVE
└───────────────────┘                    │
        │ No                             │
        ▼                                ▼
┌───────────────────┐            ┌──────────────┐
│ Queue for Review  │            │ Execute      │
└───────────────────┘            │ Log result   │
        │                        └──────────────┘
        ▼
┌───────────────────┐
│ User approves?    │
└───────────────────┘
    │           │
   Yes          No
    │           │
    ▼           ▼
Execute     Archive
```

---

## 11. Error States & Recovery

### Error Categories

| Category | Example | User Message | Recovery |
|----------|---------|--------------|----------|
| **Network** | API unreachable | "Working offline" | Queue actions |
| **Extraction** | LLM timeout | "Couldn't analyze" | Retry button |
| **Empty result** | No facets found | "No facets yet" | Suggest alternatives |
| **Conflict** | Duplicate entity | "Similar exists" | Merge UI |
| **Sync failure** | SiYuan unreachable | "Saved locally" | Auto-retry |

### UI Uncertainty Communication

| Confidence | Display |
|------------|---------|
| 0.9-1.0 | Solid connection line |
| 0.7-0.9 | Dashed connection line |
| 0.5-0.7 | Dotted line + "?" badge |
| <0.5 | "Suggested" label, dimmed |

### Recovery Actions

| Error | Auto-Recovery | Manual Recovery |
|-------|--------------|-----------------|
| Network down | Queue, retry on reconnect | Force retry button |
| LLM failure | Retry 3x with backoff | Skip / use cached |
| Empty evidence | Show "not indexed" | Trigger ingestion |
| Sync conflict | Newer wins | Manual merge UI |
| Corrupted cache | Clear + rebuild | Clear cache button |

---

## 12. System Boundaries & Safety

### What Belongs in IES

**IN scope:**
- Book/paper reading and annotation
- Concept exploration and mapping
- Question-driven research
- Thinking sessions (ForgeMode)
- Knowledge graph growth
- Cross-app synchronization

**OUT of scope:**
- Task management (use external tool)
- Calendar/scheduling
- Email/communication
- File storage (use filesystem)
- Code development (use IDE)

### Automation Safety Rules

| Action | Automation Level | Why |
|--------|-----------------|-----|
| Create capture | Full auto | User initiated |
| Extract entities | Auto with logging | Reversible |
| Create relationships | Propose only | Needs validation |
| Delete anything | Never auto | Data loss risk |
| Modify user text | Never | Integrity |
| Create Context | Propose only | User decision |
| Answer questions | Propose only | Needs validation |

### Rate Limits

| Operation | Limit | Window |
|-----------|-------|--------|
| LLM calls | 60 | minute |
| Entity creation | 100 | minute |
| Batch extraction | 10 | minute |
| Sync operations | 30 | minute |

### Runaway Prevention

If system detects:
- >1000 entities created in 1 hour
- >100 failed operations in 10 minutes
- Loop pattern in agent behavior

**Action:** Pause all automation, alert user, require manual restart.

---

## 13. Versioning & Invalidation

### Cache TTLs

| Data Type | Cache Duration | Invalidation Trigger |
|-----------|---------------|---------------------|
| Facets | 24 hours | Entity updated, manual refresh |
| Evidence | 1 hour | New source indexed |
| Entity details | 4 hours | Entity modified |
| Book entities | 24 hours | Book re-indexed |
| Contexts | Session | User modification |
| Questions | Session | User modification |

### Schema Versioning

All persisted data includes `schema_version`:

```json
{
  "schema_version": "0.1.0",
  "data": { ... }
}
```

**Migration rule:** On load, check version. If older, run migrations before use.

### Graph Drift Prevention

1. **Entity merge on match:** Before creating, check for similar
2. **Relationship dedup:** Same source + target + type = update, not create
3. **Evidence dedup:** Same CFI + book = update, not create
4. **Periodic consistency check:** Background job validates references

---

## 14. Cross-Layer Synchronization

### Sync Architecture

```
                    ┌───────────────┐
                    │   BACKEND     │
                    │   (Neo4j)     │
                    └───────┬───────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
     ┌──────────┐    ┌──────────┐    ┌──────────┐
     │  READER  │    │  PLUGIN  │    │  SIYUAN  │
     │ (local)  │    │ (local)  │    │  (docs)  │
     └──────────┘    └──────────┘    └──────────┘
```

### Sync Protocol

1. **Reader → Backend:** On capture save, POST to /sync/highlights
2. **Backend → SiYuan:** After processing, create/update blocks via API
3. **SiYuan → Backend:** On note edit, webhook triggers sync
4. **Plugin ↔ Backend:** Real-time via API calls

### Conflict Resolution

| Conflict Type | Resolution |
|--------------|------------|
| Same entity, different data | Newer timestamp wins |
| Same highlight, different notes | Merge notes |
| Deleted in one, exists in other | Soft delete (archive) |
| Different parents | Keep both references |

### Sync Status States

| State | Meaning | UI |
|-------|---------|-----|
| `synced` | All data matches | Green check |
| `pending` | Local changes not pushed | Yellow dot |
| `syncing` | Transfer in progress | Spinner |
| `conflict` | Needs manual resolution | Red exclamation |
| `offline` | Cannot reach backend | Gray cloud |

---

## 15. Developer Experience Standards

### Local Development Workflow

```bash
# 1. Start infrastructure
docker compose up -d

# 2. Start backend
cd ies/backend && uv run uvicorn ies_backend.main:app --reload --port 8081

# 3. Start Reader (choose one)
cd ies/reader && pnpm dev                    # IES Reader
cd .worktrees/ies-reader && pnpm dev         # Worktree version

# 4. Start plugin (optional)
cd .worktrees/siyuan/ies/plugin && pnpm dev
```

### Worktree Rules

| Worktree | Branch | Purpose | Owner |
|----------|--------|---------|-------|
| `.` (root) | `master` | Backend, shared docs | All |
| `.worktrees/ies-reader/` | `feature/ies-reader-enhancement` | Reader development | Reader work |
| `.worktrees/siyuan/` | `feature/siyuan-evolution` | Plugin development | Plugin work |

**Rule:** Never work on features in master. Use worktrees.

### Test Requirements

| Component | Minimum Coverage | Test Type |
|-----------|-----------------|-----------|
| Backend services | 80% | Unit + integration |
| API endpoints | 100% | Integration |
| Reader components | 60% | Component + E2E |
| Plugin components | 60% | Component |

### Documentation Update Protocol

When changing:
- **API endpoints:** Update ARCHITECTURE-AND-INTERACTIONS.md
- **Schemas:** Update both code and ARCHITECTURE doc
- **System behavior:** Update this document (IES-SYSTEM-DESIGN.md)
- **Implementation status:** Update GAP-ANALYSIS.md
- **Active components:** Update UNIFIED-PROJECT-SPEC.md

---

## Appendix: Glossary

| Term | Definition |
|------|------------|
| **Context** | Bounded space of attention (Feynman problem, project, etc.) |
| **Entity** | Named concept in the knowledge graph |
| **Facet** | Sub-component or aspect of an entity |
| **Flow Mode** | Curiosity-driven exploration with memory |
| **ForgeMode** | Template-driven thinking sessions |
| **Journey** | Chronological trace of exploration |
| **Spark** | Raw resonance capture with emotional signal |
| **Insight** | Processed spark with reflection |
| **Trail** | Breadcrumb path through exploration |
| **CFI** | Canonical Fragment Identifier (epub location) |

---

*This document is the ground truth for IES system design. All other documents defer to it.*
