# Develop Mode MVP Design

*Date: 2025-12-01*
*Status: Design Complete, Ready for Implementation*

---

## Overview

The Develop Mode MVP is the core exploration loop of the Intelligent Exploration System (IES). It enables Socratic questioning that adapts to the user's cognitive profile, captures insights as entities, and builds a knowledge graph connecting personal understanding with research literature.

**Key Insight:** The conversation engine itself is the core of IES, not just a passthrough to extraction. Conversations must be correctly focused, structured, and guided based on how the user's brain works.

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CLAUDE CODE                                      │
│                                                                      │
│  /explore-session                                                    │
│       ↓                                                              │
│  Profile-informed Socratic conversation                              │
│       ↓                                                              │
│  /end-session                                                        │
│       ↓                                                              │
│  Transcript captured → sent to backend                               │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                                │
│                                                                      │
│  1. Receive transcript                                               │
│  2. Extract entities (Claude API)                                    │
│  3. Classify: kind, domain, status                                   │
│  4. Identify connections between entities                            │
│  5. Generate structured session document                             │
│  6. Create/update entity pages                                       │
│       ↓                                                              │
│  Write to SiYuan (via API)                                           │
│  Write to Neo4j (entity graph)                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. Profile System

### Purpose

Understand the user's brain and thinking patterns to create personalized exploration strategies. The profile shapes how conversations are approached—not just what topics are discussed.

### Profile Dimensions

```
1. Processing Style
   - Detail-first ←→ Pattern-first
   - Deliberative ←→ Intuitive
   - Habituation speed (how quickly "new" becomes "familiar")

2. Attention & Energy
   - Hyperfocus triggers (what topics/contexts unlock flow)
   - Distraction vulnerabilities
   - Current capacity (daily/session check-in)
   - Recovery patterns (what restores energy)

3. Communication Preferences
   - Verbal fluency level
   - Scripts vs spontaneity preference
   - Directness preference
   - Pace (fast exchange vs slow reflection)

4. Executive Functioning
   - Task initiation patterns
   - Transition costs
   - Time perception
   - Structure needs (rigid ←→ flexible)

5. Sensory Context
   - Environment preferences (quiet/stimulating)
   - Overwhelm signals
   - Regulation tools that help

6. Masking Awareness (optional/advanced)
   - What traits feel unsafe to show
   - Energy cost of different contexts
```

### Onboarding Approach

**Not a formal assessment battery** — that's clinical. Instead:

1. **Conversational intake** (2-3 sessions) — AI asks questions drawn from assessment frameworks, but conversationally
2. **Observation-based refinement** — System notes patterns during regular sessions
3. **User self-report** — "Today I'm at 60% capacity" type check-ins
4. **Explicit profile review** — Periodic "does this still feel accurate?"

### Research Foundation

Profile dimensions drawn from:
- Barkley ADHD/Executive Function scales (19 assessments in Neo4j)
- Devon Price's "Unmasking Autism" (masking, contextual functioning)
- Beck instruments (mood/anxiety baseline)
- Big Five personality model (cognitive style)

---

## 2. Question Design Engine

### Purpose

Dynamically select questioning approaches based on user state, content type, and profile—not just default Socratic questioning.

### Inquiry Approaches (from resources)

| Approach | When to Use |
|----------|-------------|
| **Socratic** | Stuck in loops, need clarity |
| **Metacognitive** | Need clarity, reflection on thinking |
| **Phenomenological / Focusing** | Emotion-heavy, body-based knowing |
| **CBT** | Stuck in loops, testing beliefs |
| **Solution-focused** | Overwhelmed, need forward motion |
| **Systems thinking** | Unclear purpose, meaning-making |
| **Design thinking** | Unclear purpose, problem reframing |
| **Narrative** | Emotion-heavy, meaning-making |
| **Strategic** | Planning, decision-making |
| **Somatic** | Overwhelmed, grounding needed |

### Selection Logic

```
DETECT STATE
    ↓
├─ Overwhelmed? → Solution-focused, Somatic
├─ Stuck in loops? → Socratic, CBT
├─ Unclear purpose? → Design thinking, Systems
├─ Emotion-heavy? → Phenomenological, Narrative
├─ Need clarity? → Metacognitive, Socratic
├─ Planning mode? → Strategic inquiry
└─ Meaning-making? → Narrative, Systems
    ↓
SELECT APPROACH → APPLY TOOLS/TEMPLATES
```

### MVP Scope

Start with 4-5 core approaches:
1. **Socratic** — core default
2. **Solution-focused** — when overwhelmed
3. **Phenomenological/Focusing** — when emotional or stuck in head
4. **Systems thinking** — when seeing connections matters
5. **Metacognitive** — when reflection on process helps

### Resource Library

Books available for question templates:
- Socratic: Asking the Right Questions, Thinker's Guide to Socratic Questioning
- Metacognitive: Make It Stick, Metacognition (Dunlosky)
- Focusing: Focusing (Gendlin)
- CBT: Mind Over Mood, Feeling Good
- Solution-focused: Interviewing for Solutions
- Systems: Thinking in Systems, The Fifth Discipline
- Strategic: Superforecasting, Good Strategy Bad Strategy, Sources of Power
- Narrative: Maps of Meaning, Narrative Means to Therapeutic Ends

---

## 3. Session Flow

### Lifecycle

```
1. SESSION START
   ├── Load user profile
   ├── Check current capacity ("How are you feeling? 1-10")
   ├── Load recent session context (last topics, open threads)
   └── AI proposes starting point based on profile + state

2. EXPLORATION LOOP
   ┌─────────────────────────────────────────────────────────┐
   │  DETECT STATE                                           │
   │  ├── Energy level (from responses, length, tone)        │
   │  ├── Cognitive state (overwhelmed, stuck, flowing)      │
   │  └── Content type (abstract, emotional, concrete)       │
   │                        ↓                                │
   │  SELECT APPROACH (from question engine)                 │
   │                        ↓                                │
   │  ASK QUESTION (adapted to profile)                      │
   │  ├── Pacing (fast/slow per profile)                     │
   │  ├── Abstraction level (concrete/theoretical)           │
   │  └── Directness (blunt/gentle)                          │
   │                        ↓                                │
   │  PROCESS RESPONSE                                       │
   │  ├── Note entities emerging                             │
   │  ├── Track thread (what we're exploring)                │
   │  └── Update state detection                             │
   └─────────────────────────────────────────────────────────┘
                    ↓ (repeat until pause signal)

3. SESSION END
   ├── Detect pause signal (energy dip, explicit, natural end)
   ├── AI summarizes session
   ├── User confirms/edits summary
   └── Trigger backend extraction

4. POST-SESSION (Backend)
   ├── Extract entities from transcript
   ├── Create structured session document in SiYuan
   ├── Create/update entity pages
   ├── Update Neo4j graph
   └── Update profile (patterns observed)
```

### Profile Influence Points

| Profile Dimension | How It Affects Session |
|-------------------|------------------------|
| Processing style | Question sequence, abstraction level |
| Attention patterns | Topic steering, depth vs breadth |
| Current capacity | Session length, complexity |
| Communication preference | Question phrasing, wait time |
| Sensory/energy context | Pause frequency, break suggestions |

---

## 4. Entity System

### Light Schema

```
kind: idea | person | process | question | tension
domain: therapy | personal | meta
status: seed | developing | solid
```

Connections and tags do the rest of the work. Ontology emerges from use, not defined upfront.

### Extraction Schema (Claude prompt output)

```json
{
  "entities": [
    {
      "name": "string",
      "kind": "idea | person | process | question | tension",
      "domain": "therapy | personal | meta",
      "status": "seed | developing | solid",
      "description": "string",
      "quotes": ["exact quotes from transcript"],
      "connections": [
        {"to": "entity_name", "relationship": "supports | tensions | develops"}
      ]
    }
  ],
  "session_summary": {
    "key_insights": ["string"],
    "open_questions": ["string"],
    "threads_explored": ["string"]
  }
}
```

### Session Document Structure

Structured sections (not chronological transcript):
- **Key Insights** — What emerged
- **Entities Discussed** — With status and connections
- **Open Questions** — Unresolved threads
- **Key Quotes** — Important moments
- **Context** — Enough to remember what you were thinking

Raw transcript stored separately if needed.

---

## 5. Backend Architecture

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| API Framework | FastAPI | Async, streaming support |
| Graph Database | Neo4j | Entities, relations, profile queries |
| Vector Store | Qdrant | Semantic search (existing) |
| Document Store | SiYuan | Human-readable pages |
| LLM | Claude API | Entity extraction, summaries |

### Endpoints

```
POST /session/process
├── Input: transcript, user_id
├── Extract entities (Claude API)
├── Generate session document
├── Create/update entity pages (SiYuan API)
├── Update graph (Neo4j)
└── Output: session_doc_id, entities_created, entities_updated

GET /profile/{user_id}
└── Return current profile

PATCH /profile/{user_id}
└── Update profile dimensions

POST /profile/{user_id}/observe
├── Input: session patterns (length, topics, energy signals)
└── Update profile based on observations

GET /context/{user_id}
├── Recent sessions
├── Open threads
├── Suggested starting points
└── Current profile summary

GET /entity/{entity_id}
└── Entity details + connections from graph

POST /entity/search
├── Input: query, filters
└── Hybrid search (Neo4j + Qdrant)
```

### Data Flow

```
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
    │   Neo4j     │          │   Qdrant    │          │   SiYuan    │
    │  (Graph)    │          │  (Vectors)  │          │   (Docs)    │
    │             │          │             │          │             │
    │ - Entities  │          │ - Chunks    │          │ - Sessions  │
    │ - Relations │          │ - Semantic  │          │ - Entities  │
    │ - Profile   │          │   search    │          │ - Profile   │
    └─────────────┘          └─────────────┘          └─────────────┘
```

---

## 6. Implementation Phases

### Phase 1: Profile Foundation
- [ ] Design profile schema (Neo4j + SiYuan)
- [ ] Build conversational onboarding flow (Claude Code command)
- [ ] Create profile CRUD endpoints
- [ ] Implement capacity check-in

### Phase 2: Backend Core
- [ ] FastAPI project setup
- [ ] Entity extraction endpoint (Claude API)
- [ ] Session document generation
- [ ] SiYuan page creation/update
- [ ] Neo4j entity/relation storage

### Phase 3: Question Engine
- [ ] State detection logic
- [ ] Approach selection rules
- [ ] Question templates (from books)
- [ ] Profile-adapted phrasing

### Phase 4: Session Integration
- [ ] `/explore-session` command (enhanced)
- [ ] `/end-session` command (triggers backend)
- [ ] Context loading at session start
- [ ] Profile observation after sessions

### Phase 5: Polish
- [ ] Profile review command
- [ ] Entity page templates
- [ ] Session document templates
- [ ] Error handling and edge cases

---

## Open Questions (for implementation)

1. **Profile storage format** — JSON in SiYuan block attributes? Separate Neo4j nodes?
2. **Session transcript format** — How to capture Claude Code conversation for backend?
3. **Capacity check-in UX** — Inline question vs explicit command?
4. **Approach switching** — How often to re-evaluate state during session?

---

## Dependencies

### Existing Infrastructure
- Neo4j: 48,987 nodes, 121,299+ relationships
- Qdrant: 27,523 semantic chunks
- SiYuan: Connected via siyuan-mcp
- Docker Compose: `docker compose up -d`

### New Components Needed
- FastAPI backend service (`ies-backend` project)
- Enhanced Claude Code commands
- Profile schema and storage

---

## Success Criteria

MVP is complete when:
1. User can complete onboarding to create initial profile
2. `/explore-session` loads profile and adapts questioning
3. `/end-session` triggers backend extraction
4. Session documents appear in SiYuan with structured format
5. Entities are created/updated in Neo4j and SiYuan
6. Profile updates based on session observations
