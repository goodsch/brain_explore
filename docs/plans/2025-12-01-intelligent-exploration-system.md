# Intelligent Exploration System Design

*Date: 2025-12-01*
*Status: Design Phase*
*Last Updated: 2025-12-01 (Architecture Refinement)*

---

## Architecture Decisions (2025-12-01 Refinement)

### Two Connected Systems

The IES operates on two distinct but connected systems:

```
INTEGRATED THEORIES (The Output)
    │
    ├── 1-Human Mind (why humans are the way they are)
    ├── 2-Change Process (how therapy creates change)
    └── 3-Method (operational approach)
    │
    │ built from
    ▼
KNOWLEDGEBASE (The Raw Material)
    │
    ├── Personal Entities (from exploration sessions)
    └── Literature Entities (from books, 49k in Neo4j)
```

**Key Insight:** Entities are building blocks. Integrated Theories are the actual output — synthesized understanding built from entities.

### Three Document Types

| Type | Purpose | Lifecycle |
|------|---------|-----------|
| **Session documents** | Record of exploration | Created once, immutable |
| **Entity pages** | Individual concepts | Evolve over time, accumulate quotes |
| **Integrated Theories** | Synthesized understanding | **THE GOAL** |

### Three Plugin Modes

| Mode | Purpose | Flow |
|------|---------|------|
| **Develop** | Socratic questioning | AI guides → entities emerge → connected to KB |
| **Explore** | Browse knowledgebase | Find connections → fill gaps → research |
| **Synthesize** | Build theories | Integrate learnings → update theory docs |

### Knowledgebase Approach: Annotation Layer

- Literature entities live in Neo4j (49k)
- SiYuan pages created ON DEMAND when accessed
- No 49k page bloat — grows organically
- Hub page shows stats, recent activity, suggestions
- Clicking `[[entity]]` creates page if it doesn't exist

### User Experience: Zero Metadata Management

- User just has conversations
- AI identifies entities during conversation
- AI applies tags, makes connections
- AI generates session documents
- User reviews/approves, doesn't manage

### Flexible Entity Typing

Instead of rigid types (Concept, Theory, Researcher), use block attributes:
- `custom-kind`: idea, person, process, artifact, etc.
- `custom-domain`: therapy, software, personal, etc.
- `custom-status`: seed, developing, solid

Ontology emerges from use, not defined upfront.

---

## Overview

An AI-driven system for guided knowledge exploration that adapts to the user's cognitive patterns, captures insights as navigable entities, and builds a living knowledge graph that connects personal understanding with research literature.

**Core Philosophy:** Follow the thread naturally (ADHD-friendly), leave breadcrumbs (avoid getting lost), build connections (not just content).

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EXPLORATION LOOP                             │
│                                                                      │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│   │  ASSESS  │───▶│  GUIDE   │───▶│ CAPTURE  │───▶│  ENRICH  │──┐  │
│   │ (Profile)│    │(Explore) │    │(Extract) │    │(Connect) │  │  │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘  │  │
│        ▲                                                         │  │
│        └─────────────────────────────────────────────────────────┘  │
│                        continuous refinement                         │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        KNOWLEDGE LAYERS                              │
│                                                                      │
│   ┌─────────────────┐     ┌─────────────────┐     ┌──────────────┐ │
│   │  SiYuan Pages   │◀───▶│  Knowledge      │◀───▶│  Research    │ │
│   │  (Navigation)   │     │  Graph (Neo4j)  │     │  Queue       │ │
│   └─────────────────┘     └─────────────────┘     └──────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Assessment (Learner Profile)

### Purpose
Understand the user's brain and thinking patterns to create personalized exploration strategies.

### Profile Dimensions

#### 1. Cognitive Style
- **Processing mode**: Visual vs verbal, big picture vs detail-first
- **Association patterns**: Sequential vs branching/web-like
- **Abstraction preference**: Concrete examples vs theoretical frameworks
- **Learning rhythm**: Deep dive vs sampling, sustained vs bursts

#### 2. Content Gaps
- **Framework coverage**: Which tracks (Human Mind, Change Process, Method) are underdeveloped
- **Concept maturity**: Where are seeds vs solid ideas
- **Blind spots**: Unexamined assumptions, avoided topics
- **Integration gaps**: Ideas that exist but aren't connected

#### 3. Engagement Patterns
- **Interest triggers**: What topics/angles create energy
- **Dropout signals**: Signs of fatigue, overwhelm, or disengagement
- **Optimal session profile**: Length, time of day, warm-up needs
- **Momentum builders**: What creates productive flow states

### Assessment Process

**Initial Intake (Bootstrap)**
- 1-2 dedicated assessment sessions
- Mix of direct questions and exploratory conversation
- Output: Initial learner profile document

**Continuous Refinement**
- Every session updates profile signals
- Track: session length, topic switches, energy markers, completion patterns
- AI notes patterns: "User engages deeply with mechanism questions, loses energy on historical context"

### Profile Storage
- SiYuan document: `Framework Project/Learner Profile/`
- Structured attributes for querying
- Session-by-session observation log

---

## Phase 2: Guided Exploration

### Interaction Model
**AI-led, thread-following**: Claude asks purposeful questions, user responds, Claude follows the thread based on response — like a skilled therapist tracking what matters.

### Guidance Goals
For each concept/thread being explored:

1. **Clarify**: What exactly do you mean? Remove ambiguity.
2. **Round out**: What's missing? Fill gaps in the idea.
3. **Complete**: Where does this lead? Follow to natural conclusion.
4. **Connect**: How does this relate to X? Build bridges.

### Session Flow

```
1. ORIENT
   - Read learner profile
   - Check last session state
   - Review hanging questions/threads

2. FOCUS
   - AI proposes starting point based on profile + state
   - User confirms or redirects

3. EXPLORE (main loop)
   - AI asks one question
   - User responds
   - AI assesses: clarify more? round out? follow new thread?
   - AI asks next question
   - (repeat)

4. SENSE PAUSE
   - Energy dip detected → suggest capture point
   - Natural cliffhanger → note it, suggest pause
   - User signals done → wrap up

5. CAPTURE
   - AI summarizes what emerged
   - Confirms with user
   - Triggers extraction pipeline
```

### Question Types

| Type | Purpose | Example |
|------|---------|---------|
| Clarifying | Remove ambiguity | "When you say 'awareness,' do you mean conscious attention or something broader?" |
| Expanding | Fill gaps | "What happens when that breaks down?" |
| Connecting | Build bridges | "How does this relate to what you said earlier about meaning-making?" |
| Grounding | Add specificity | "Can you think of a specific client moment where this played out?" |
| Challenging | Test robustness | "What would someone who disagrees say about this?" |
| Synthesizing | Pull together | "So if I understand: X leads to Y because Z. Is that right?" |

### Pause Point Detection

Signals that suggest natural stopping points:
- Repeated short answers (energy dip)
- Circular responses (saturation)
- "I don't know" or uncertainty markers (edge reached)
- Strong insight moment (good cliffhanger)
- Explicit time/energy signals from user

---

## Phase 3: Capture & Extraction

### Entity Extraction Pipeline

```
Session transcript
       │
       ▼
┌──────────────┐
│ AI Analysis  │ ─── Identify entities mentioned/developed
└──────────────┘
       │
       ▼
┌──────────────┐
│ Entity       │ ─── Classify: Concept, Theory, Theme, Person, etc.
│ Classification│
└──────────────┘
       │
       ▼
┌──────────────┐
│ Relationship │ ─── Extract: supports, contradicts, develops, etc.
│ Extraction   │
└──────────────┘
       │
       ▼
┌──────────────┐
│ Graph Update │ ─── Add to Neo4j with session context
└──────────────┘
       │
       ▼
┌──────────────┐
│ SiYuan Page  │ ─── Create/update navigable document
│ Generation   │
└──────────────┘
```

### Entity Types

**Personal entities** (from exploration sessions):
- `PersonalConcept` — User's own ideas/framings
- `PersonalTheory` — User's explanatory models
- `Insight` — Specific realizations from sessions
- `OpenQuestion` — Unresolved questions worth tracking

**Literature entities** (from book extraction):
- `Concept` — Ideas from published sources
- `Theory` — Formal theoretical frameworks
- `Author` — People referenced
- `Assessment` — Measurement tools
- `Researcher` — Academic contributors

**Linking rule**: Personal entities connect TO literature entities but remain distinct. This allows:
- Seeing "my ideas" vs "the literature"
- Tracking how personal understanding relates to established knowledge
- Finding gaps where personal ideas lack research grounding

### Session Context Preservation

Each entity stores:
- Source session(s) where it emerged
- Exact quotes/context from discussion
- Evolution over time (if refined across sessions)
- User's confidence/certainty level

---

## Phase 4: Enrichment & Connection

### Automatic Enrichment (Post-Session)

**1. Graph Connection Discovery**
```
For each new/updated entity:
  - Query Neo4j for related entities (shared themes, author overlap, etc.)
  - Identify 1st-degree connections
  - Surface unexpected connections (different domains, same pattern)
  - Add connection metadata to SiYuan page
```

**2. Framework Integration**
```
For each PersonalConcept:
  - Determine Track placement (Human Mind / Change Process / Method)
  - Identify which framework gaps it fills
  - Note tensions with existing concepts
  - Flag open questions it raises
```

**3. Literature Grounding Check**
```
For concepts marked for grounding:
  - Search vector store for related chunks
  - Identify supporting/contradicting sources
  - Generate "what the literature says" summary
  - Note where personal framing differs from literature
```

### On-Demand Research Queue

**Trigger**: User clicks "Research This" on entity page

**Process**:
1. Entity added to research queue
2. AI performs:
   - Vector search of local library
   - ArXiv search for academic papers
   - Deep research if needed (web search, synthesis)
3. Results:
   - Relevant book chapters identified
   - Papers downloaded and summarized
   - Key supporting/contradicting evidence extracted
4. Entity page updated with research findings

### Research Queue Management

- Queue visible in SiYuan dashboard
- Priority levels: urgent / normal / someday
- Batch processing during non-session time
- Results review as part of session start

---

## SiYuan Structure

### New Notebook: Connected Knowledge Base

```
/Connected Knowledge Base/
├── _Index/
│   ├── All Entities.md          # Auto-generated master list
│   ├── By Type.md               # Grouped by entity type
│   ├── By Track.md              # Grouped by framework track
│   └── Recent.md                # Recently touched entities
│
├── Concepts/
│   └── [Entity pages...]
│
├── Theories/
│   └── [Entity pages...]
│
├── Themes/
│   └── [Entity pages...]
│
├── People/
│   └── [Entity pages...]
│
├── Open Questions/
│   └── [Entity pages...]
│
└── _Navigation/
    ├── Breadcrumbs.md           # Current exploration trail
    ├── Session Paths.md         # Past exploration journeys
    └── Suggested Next.md        # AI-recommended explorations
```

### Entity Page Template

```markdown
# {Entity Name}

**Type:** {Concept | Theory | Theme | Person | Open Question}
**Track:** {Human Mind | Change Process | Method | Cross-cutting}
**Status:** {seed | developing | solid | grounded}
**Created:** {date} | **Updated:** {date}

---

## Summary
{AI-generated summary of the entity, updated as understanding evolves}

## From Your Exploration
{Quotes and context from sessions where this emerged}

> "{exact quote}" — Session {date}

## Connections

### First-Degree (Direct)
{{query: connections where source = this}}

| Entity | Relationship | Context |
|--------|--------------|---------|
| [[Related Concept]] | supports | "Because X leads to Y" |
| [[Another Theory]] | tensions with | "Differs on mechanism" |

### From Literature
| Source | Relationship | Key Quote |
|--------|--------------|-----------|
| {Book/Paper} | supports | "..." |

## Research Status
- [ ] Local library searched
- [ ] ArXiv searched
- [ ] Deep research completed

[🔬 Queue for Research]

## Open Questions
- {Questions this raises}

## Session History
- {date}: First emerged in discussion of X
- {date}: Refined connection to Y
```

### Breadcrumb System

**Purpose**: Track exploration path to avoid getting lost

**Implementation**:
- `_Navigation/Breadcrumbs.md` shows current trail
- Each entity page shows "You came here from: [[X]]"
- "Back" links to retrace steps
- Session paths saved for review ("How did I get to this insight?")

---

## New Commands

### `/explore-session`
Existing command — general Socratic exploration of therapeutic worldview.

### `/explore-topic <entity>` (NEW)
AI-aided connection crawl starting from a specific entity.

```
Flow:
1. Load entity page
2. AI summarizes entity + shows connections
3. User picks a connection to explore
4. AI asks questions about the relationship
5. New insights captured
6. Breadcrumbs updated
7. Repeat or return
```

### `/research-queue` (NEW)
Manage and process research queue.

```
Options:
- View queue
- Process next item
- Batch process all
- Review completed research
```

### `/profile-review` (NEW)
Review and update learner profile.

```
Shows:
- Current profile summary
- Recent pattern observations
- Suggested profile updates
- Option to manually adjust
```

---

## Interface Layer: SiYuan Plugin

### Vision

Rather than external tools (Claude Code CLI, Happy app), the primary interface is a **SiYuan plugin** that embeds the AI directly into the knowledge environment. This keeps context tight and enables seamless note creation.

**Reference**: [siyuan-plugin-copilot](https://github.com/Achuan-2/siyuan-plugin-copilot)

### Plugin Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SiYuan Interface                          │
│  ┌─────────────────────┐     ┌───────────────────────────────┐ │
│  │    Document View    │     │      AI Sidebar Panel         │ │
│  │                     │     │  ┌─────────────────────────┐  │ │
│  │  [Entity Page]      │◀───▶│  │  Mode: explore-topic    │  │ │
│  │  - Summary          │     │  ├─────────────────────────┤  │ │
│  │  - Connections      │     │  │  Chat Interface         │  │ │
│  │  - Research Status  │     │  │  > User message         │  │ │
│  │                     │     │  │  < AI response          │  │ │
│  │  [Action Buttons]   │     │  │  > ...                  │  │ │
│  │  🔬 Research        │     │  ├─────────────────────────┤  │ │
│  │  🔗 Find Connections│     │  │  [Context Panel]        │  │ │
│  │  📖 Jump to Source  │     │  │  - Current entity       │  │ │
│  │                     │     │  │  - 1st-degree links     │  │ │
│  └─────────────────────┘     │  │  - Track: Human Mind    │  │ │
│                              │  └─────────────────────────┘  │ │
│                              └───────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │     Backend Services       │
                    │  - Neo4j (graph queries)   │
                    │  - Qdrant (vector search)  │
                    │  - LLM API (Claude)        │
                    │  - Ebook MCP (sources)     │
                    └───────────────────────────┘
```

### Plugin Modes

Each mode has its own system prompt, context loading, and behavior:

#### Mode 1: `explore-session`
**Purpose**: Open-ended Socratic exploration of therapeutic worldview
**Context loaded**:
- Learner profile
- Current track focus (if any)
- Recent session summaries
- Hanging questions

**Behavior**: AI-led questioning, follows threads, captures to inbox

#### Mode 2: `explore-topic`
**Purpose**: AI-aided connection crawl starting from current entity
**Context loaded**:
- Current entity page content
- First-level graph connections
- Related literature chunks (vector search)
- Track context

**Behavior**:
- Summarizes current entity
- Shows connection options
- User picks direction
- AI explores the relationship
- Breadcrumbs updated automatically

#### Mode 3: `research-mode`
**Purpose**: Deep dive into literature for current topic
**Context loaded**:
- Current entity
- Full graph neighborhood (2-3 degrees)
- All related book chunks
- ArXiv search results

**Behavior**:
- AI synthesizes what literature says
- Surfaces agreements/tensions with user's framing
- Can jump to source pages in ebooks
- Updates entity page with findings

#### Mode 4: `capture-mode`
**Purpose**: Quick structured capture of ideas
**Context loaded**:
- Minimal — just track structure
- Entity templates

**Behavior**:
- User dumps thoughts
- AI structures into entity format
- Suggests track placement
- Creates draft pages

### Note-Specific Context

When viewing any entity page, the sidebar automatically loads:

```typescript
interface PageContext {
  entity: {
    name: string;
    type: EntityType;
    track: Track;
    status: Status;
    content: string;
  };
  connections: {
    direct: Connection[];      // 1st-degree from graph
    suggested: Connection[];   // AI-inferred from content
  };
  literature: {
    supporting: Chunk[];       // Vector search results
    contradicting: Chunk[];
  };
  sessionHistory: SessionRef[];  // Past discussions of this entity
}
```

### Action Buttons

Entity pages include quick-action buttons:

| Button | Action |
|--------|--------|
| 🔬 Research | Queue for deep research / trigger immediate research |
| 🔗 Connections | Show full graph neighborhood, suggest new links |
| 📖 Source | Jump to relevant book passage (via ebook-mcp) |
| ✏️ Refine | Open explore-topic mode focused on this entity |
| 🌿 Branch | Create new entity branching from this one |

### Ebook Integration

**Reference**: [siyuan-sireader](https://github.com/mm-o/siyuan-sireader)

When exploring a topic:
- AI can reference specific book passages
- User can jump to that passage in the reader
- Highlights/annotations flow back into entity pages
- Citations automatically tracked

```
User exploring "Emotional Regulation"
    │
    ▼
AI: "Gross describes this in Chapter 3 of Handbook of Emotion Regulation..."
    │
    ▼
[📖 Jump to Source] → Opens reader at that chapter
    │
    ▼
User highlights passage → Highlight appears on entity page
```

### Persistent Memory Per Track

Each track maintains its own memory context:

```
/Framework Project/Memory/
├── Track 1 - Human Mind/
│   ├── key-concepts.md      # Core concepts established
│   ├── open-threads.md      # Unfinished explorations
│   └── session-summaries/   # Per-session learnings
├── Track 2 - Change Process/
│   └── ...
└── Track 3 - Method/
    └── ...
```

When entering a track, the AI loads:
- Key concepts established so far
- Open threads/questions
- Recent session work in this track
- Relevant learner profile sections

### Plugin Technical Stack

```
Frontend (SiYuan Plugin):
- TypeScript
- SiYuan Plugin API
- Custom sidebar panel

Backend Services:
- FastAPI server (Python)
- Neo4j driver
- Qdrant client
- Claude API (Anthropic SDK)
- Ebook-MCP integration

Communication:
- REST API between plugin and backend
- WebSocket for streaming responses
- SiYuan API for document operations
```

---

## Bidirectional Sync

### Graph → Sessions
When new entities are added to the graph (from book extraction):
1. Check existing session notes for mentions
2. If found, create links back to sessions
3. Surface in "Related to your exploration" section

### Sessions → Graph
When entities emerge in exploration:
1. Check if similar entity exists in graph
2. If yes: link personal entity to literature entity
3. If no: create as PersonalConcept, flag for research

### Deduplication Strategy

```
New entity mentioned: "emotion regulation"
    │
    ▼
Search graph for similar:
- Exact match? → Link
- Fuzzy match (>0.85 similarity)? → Prompt user: "Is this the same as 'Emotional Regulation' from Gross?"
- No match? → Create new PersonalConcept
```

---

## Implementation Phases

### Phase A: Foundation (Entity System)
- [ ] Define entity schema for Neo4j (PersonalConcept, Insight, etc.)
- [ ] Create SiYuan entity page template with dynamic connections
- [ ] Build entity extraction from session transcripts
- [ ] Implement basic SiYuan page generation
- [ ] Set up Connected Knowledge Base notebook structure

### Phase B: Backend Services
- [ ] FastAPI server skeleton
- [ ] Neo4j query layer (connections, neighborhoods)
- [ ] Qdrant search integration
- [ ] Claude API integration with streaming
- [ ] Context assembly logic (per-mode)

### Phase C: SiYuan Plugin (MVP)
- [ ] Plugin scaffold (TypeScript, SiYuan API)
- [ ] Sidebar panel UI
- [ ] Mode switcher (explore-session, explore-topic)
- [ ] Chat interface with streaming
- [ ] Basic entity page detection and context loading

### Phase D: Guided Exploration
- [ ] Implement learner profile structure
- [ ] Build initial assessment session flow
- [ ] Create guided questioning engine (system prompts per mode)
- [ ] Implement pause point detection
- [ ] Build session capture pipeline

### Phase E: Enrichment & Integration
- [ ] Automatic graph connection discovery
- [ ] Research queue system
- [ ] Ebook integration (jump to source)
- [ ] Bidirectional sync (graph ↔ sessions)
- [ ] Breadcrumb/navigation system

### Phase F: Polish
- [ ] Action buttons on entity pages
- [ ] Deduplication prompts
- [ ] Visualization (Markmap)
- [ ] Track-specific memory persistence
- [ ] Performance optimization

---

## Open Design Questions

1. **Entity deduplication**: How to handle when same concept emerges in different sessions with different names?

2. **Connection strength**: Should connections have weights? How to determine?

3. **Profile privacy**: Learner profile contains personal cognitive patterns — storage/access considerations?

4. **Session transcript storage**: Full transcripts vs. extracted highlights only?

5. **Conflict resolution**: When personal insight contradicts literature, how to represent?

---

## Success Metrics

- **Exploration depth**: Average connections per entity
- **Framework coverage**: % of tracks with solid concepts
- **Research grounding**: % of concepts with literature connections
- **Engagement**: Session length trends, return frequency
- **Navigation utility**: Breadcrumb usage, connection clicks
- **Insight emergence**: New entities per session over time
