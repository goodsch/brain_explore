# Consolidated Architecture: Brain Explore System

**Date:** 2025-12-03
**Status:** Design Document
**Purpose:** Consolidate full system vision, dependencies, and phased implementation

---

## Executive Summary

Brain Explore is a **thinking partnership system** that helps users explore knowledge domains through AI-guided dialogue and graph-based navigation. This document consolidates the architecture after discovering dependency issues across parallel development efforts.

**Core Insight:** We built UI before designing the system. This document establishes the proper foundation.

---

## System Vision

### The Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION LAYER                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │    READEST      │  │  SIYUAN PLUGIN  │  │  QUICK CAPTURE  │         │
│  │  (Layer 4)      │  │   (Layer 3)     │  │   (Layer 3)     │         │
│  │  Reading +      │  │  Processing +   │  │  Mobile input   │         │
│  │  Flow mode      │  │  Thinking modes │  │  → queue        │         │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘         │
└───────────┼────────────────────┼────────────────────┼───────────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         BACKEND API LAYER                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ Graph API   │ │ Session API │ │ Journey API │ │ Capture API │       │
│  │ (Layer 1)   │ │ (Layer 2)   │ │ (Layer 3)   │ │ (Layer 3)   │       │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘       │
└─────────┼───────────────┼───────────────┼───────────────┼───────────────┘
          │               │               │               │
          ▼               ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA & INTELLIGENCE LAYER                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    KNOWLEDGE GRAPH (Neo4j)                       │   │
│  │    50k+ entities │ relationships │ source tracking │ journeys    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    CALIBRE (Source of Truth)                     │   │
│  │         Library management │ OPDS feed │ Ingestion trigger       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### Layer Definitions

| Layer | Purpose | Components | Status |
|-------|---------|------------|--------|
| **Layer 1** | Knowledge Graph | Neo4j, ingestion pipeline, entity extraction | ✅ Working (50k entities) |
| **Layer 2** | Thinking Partnership | Profile system, dialogue, adaptive questioning | ✅ Working (backend) |
| **Layer 3** | Processing Hub | SiYuan plugin, Quick Capture, journey tracking | ⚠️ UI built, backend gaps |
| **Layer 4** | Reading Interface | Readest Flow mode, text selection → graph | ⚠️ UI built, needs testing |
| **Foundation** | Source of Truth | Calibre library, OPDS, sync service | ❌ Not started |

---

## Dependency Graph

```
                         ┌─────────────────┐
                         │    CALIBRE      │
                         │ (Source of Truth)│
                         └────────┬────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │   OPDS   │ │  Sync    │ │  Source  │
              │   Feed   │ │ Service  │ │ Tracking │
              └────┬─────┘ └────┬─────┘ └────┬─────┘
                   │            │            │
                   ▼            ▼            ▼
              ┌──────────┐ ┌─────────────────────┐
              │ READEST  │ │   INGESTION         │
              │ Library  │ │   PIPELINE          │
              └────┬─────┘ └──────────┬──────────┘
                   │                  │
                   │                  ▼
                   │        ┌─────────────────────┐
                   │        │  KNOWLEDGE GRAPH    │
                   │        │  (Neo4j)            │
                   │        └──────────┬──────────┘
                   │                   │
                   ▼                   ▼
              ┌──────────────────────────────────┐
              │        FLOW MODE                 │
              │  (Readest panel + Graph queries) │
              └────────────────┬─────────────────┘
                               │
                               ▼
              ┌──────────────────────────────────┐
              │     SIYUAN PLUGIN                │
              │  Dashboard │ Structured Thinking │
              └────────────────┬─────────────────┘
                               │
                               ▼
              ┌──────────────────────────────────┐
              │     QUICK CAPTURE                │
              │  iOS Shortcut → Queue → Process  │
              └──────────────────────────────────┘
```

### Critical Path Analysis

**What can work NOW (no Calibre needed):**
1. Readest reads local epub files
2. Flow mode queries existing graph (50k entities from 63 books)
3. SiYuan Dashboard shows graph exploration
4. Journey tracking saves exploration paths

**What requires Calibre integration:**
1. New book ingestion → graph updates
2. Book removal → entity archival
3. Source links in Flow mode → open correct book
4. Library consistency (graph reflects available books)

---

## Current State vs Target State

### Readest Flow Mode

| Aspect | Current | Target |
|--------|---------|--------|
| Book source | Local files | Calibre OPDS |
| Entity lookup | ✅ Working | ✅ Working |
| Relationships | ✅ Working | ✅ Working |
| Source links | Shows book title | Opens book at passage |
| Journey save | Local storage | Backend + local fallback |

### SiYuan Structured Thinking

| Aspect | Current | Target |
|--------|---------|--------|
| 5 UI modes | ✅ Built | ✅ Built |
| Backend mode support | ❌ Ignored | Mode-specific system prompts |
| AI behavior | Generic IES | Mode-specific (Socratic, mirroring, etc.) |
| Output structure | Free-form | Mode-specific templates |
| Entity extraction | Generic | Mode-aware categorization |
| Session connections | None | Link to graph, to each other |

### Quick Capture

| Aspect | Current | Target |
|--------|---------|--------|
| iOS Shortcut | Design only | Built and documented |
| SiYuan queue | UI built | End-to-end working |
| AI processing | Stubbed | Entity extraction + routing |
| Routing | UI only | Creates notes, links to graph |

### Calibre Integration

| Aspect | Current | Target |
|--------|---------|--------|
| OPDS feed | Not connected | Readest consumes |
| Sync service | Not built | Watches library changes |
| Ingestion trigger | Manual | Automatic on new book |
| Source tracking | Not in graph | Every entity has source_book_id |
| Book removal | Not handled | Soft delete entities |

---

## Backend Gaps: Structured Thinking Modes

### Current Backend Behavior

The chat service (`chat_service.py`) has:
- Auto-detected approaches: socratic, solution_focused, phenomenological, narrative, integrative
- State detection based on recent messages
- Generic system prompt for all sessions

### Required Changes

**1. Mode-aware session start:**
```python
@router.post("/start")
async def start_session(request: SessionStartRequest):
    # NEW: Accept mode parameter
    mode = request.mode  # learning, articulating, planning, ideating, reflecting
    
    # Load mode-specific system prompt
    system_prompt = get_mode_prompt(mode)
    
    result = await chat_service.start_session(
        user_id=request.user_id,
        mode=mode,
        system_prompt=system_prompt
    )
```

**2. Mode-specific system prompts:**

| Mode | AI Persona | Technique | Output Focus |
|------|-----------|-----------|--------------|
| **Learning** | Socratic teacher | Open questions, assumption testing | Concept understanding |
| **Articulating** | Reflective mirror | Paraphrasing, precise language | Clear formulation |
| **Planning** | Strategic advisor | Goal clarification, obstacle mapping | Actionable steps |
| **Ideating** | Creative catalyst | Divergent prompts, wild ideas | Option generation |
| **Reflecting** | Phenomenological guide | Experience focus, felt sense | Personal insight |

**3. Mode-specific output schemas:**

```typescript
// Learning mode output
interface LearningOutput {
  concept: string;
  understanding: string;
  connections: string[];
  openQuestions: string[];
  misconceptionsChallenged: string[];
}

// Planning mode output
interface PlanningOutput {
  goal: string;
  obstacles: string[];
  steps: { action: string; milestone: string }[];
  resources: string[];
  firstAction: string;
}

// ... etc for each mode
```

---

## Phased Implementation Plan

### Phase 0: MVP Validation (Current)
**Goal:** Prove core value with existing infrastructure

- [ ] Test Readest Flow mode with existing 50k entities
- [ ] Verify entity lookup from text selection works
- [ ] Verify relationship navigation works
- [ ] Verify journey tracking saves correctly

**Success criteria:** User can read a book, select text, see related entities, explore connections.

### Phase 1: Backend Mode Support
**Goal:** Make Structured Thinking modes actually work

- [ ] Add `mode` parameter to session API
- [ ] Create detailed system prompts for each mode
- [ ] Pass mode to chat service
- [ ] Test each mode produces appropriate responses

**Success criteria:** Each mode feels distinctly different in conversation style.

### Phase 2: Output Structure
**Goal:** Sessions produce structured, usable artifacts

- [ ] Define output schema per mode
- [ ] Backend generates structured summary at session end
- [ ] SiYuan creates formatted notes from structure
- [ ] Link session entities to knowledge graph

**Success criteria:** Sessions produce reusable notes, not just transcripts.

### Phase 3: Calibre Integration
**Goal:** Calibre becomes source of truth

- [ ] Set up Calibre OPDS endpoint
- [ ] Connect Readest to OPDS
- [ ] Build sync service (detect library changes)
- [ ] Add source_book_id to graph schema
- [ ] Migrate existing entities (add source tracking)
- [ ] Implement soft delete on book removal

**Success criteria:** Add book to Calibre → appears in Readest → entities in graph. Remove book → entities archived.

### Phase 4: Quick Capture
**Goal:** Frictionless mobile capture

- [ ] Build iOS Shortcut
- [ ] Document setup process
- [ ] Test end-to-end: capture → queue → process → route
- [ ] Integrate with Calibre (captured book references resolve)

**Success criteria:** Capture thought on phone → appears in SiYuan queue → AI routes to correct location.

---

## Integration Points

### Readest ↔ Backend

| Endpoint | Purpose | Status |
|----------|---------|--------|
| `GET /graph/search?q=` | Entity lookup from selected text | ✅ Working |
| `GET /graph/entity/{id}` | Entity details | ✅ Working |
| `GET /graph/explore/{id}` | Related entities | ✅ Working |
| `GET /graph/sources/{id}` | Source passages | ✅ Working |
| `POST /journeys` | Save exploration journey | ✅ Working |
| `GET /question-engine/question` | Thinking partner questions | ✅ Working |

### SiYuan ↔ Backend

| Endpoint | Purpose | Status |
|----------|---------|--------|
| `POST /session/start` | Start thinking session | ⚠️ Ignores mode |
| `POST /session/chat-sync` | Send message | ⚠️ Ignores mode |
| `POST /session/end` | End and extract | ✅ Working |
| `GET /journeys/user/{id}` | List user journeys | ✅ Working |
| `POST /capture/process` | Process captured content | ✅ Working |

### Calibre ↔ System (Future)

| Integration | Purpose | Status |
|-------------|---------|--------|
| OPDS → Readest | Book library | ❌ Not built |
| Library → Sync Service | Change detection | ❌ Not built |
| Sync → Ingestion | Trigger processing | ❌ Not built |
| Graph ← Source tracking | Entity provenance | ❌ Not built |

---

## Open Questions

1. **Graph migration:** How to add source_book_id to existing 50k entities? (Need to map book titles to Calibre IDs)

2. **Offline handling:** If Calibre is offline, should Readest cache books locally? Should graph queries still work?

3. **Multi-user:** Current system assumes single user (chris). How does this scale?

4. **Mode switching:** Can user switch modes mid-session? Or must they end and restart?

5. **Session linking:** How do sessions relate to each other? Parent-child? Tags? Graph edges?

---

## Appendix: System Prompt Templates (Draft)

### Learning Mode

```
You are a Socratic guide helping the user deeply understand a concept.

YOUR APPROACH:
- Ask open-ended questions that reveal assumptions
- Build understanding through guided discovery
- Never lecture - help them discover through questions
- Challenge oversimplifications gently
- Connect new understanding to what they already know

RESPONSE PATTERN:
1. Acknowledge what they said
2. Reflect back your understanding
3. Ask ONE probing question that deepens exploration

Keep responses concise (2-4 sentences + question).
```

### Articulating Mode

```
You are a reflective mirror helping the user crystallize vague thoughts.

YOUR APPROACH:
- Listen for the essence of what they're trying to say
- Reflect back in clearer, more precise language
- Ask "Is this what you mean?" to test your understanding
- Help them find the exact words for fuzzy feelings
- Don't add your own interpretation - amplify theirs

RESPONSE PATTERN:
1. Paraphrase what you heard
2. Offer a more precise formulation
3. Ask if that captures it, or what's missing

Keep responses concise. The goal is clarity, not expansion.
```

### Planning Mode

```
You are a strategic thinking partner helping the user develop an action plan.

YOUR APPROACH:
- Clarify the goal before jumping to solutions
- Surface obstacles and constraints
- Break big goals into concrete next steps
- Ensure every step is actionable
- Identify the very first action they can take

RESPONSE PATTERN:
1. Confirm understanding of the goal
2. Explore one obstacle or consideration
3. Ask what would move them forward

Stay practical. Plans should be doable, not ideal.
```

### Ideating Mode

```
You are a creative catalyst helping the user generate options.

YOUR APPROACH:
- Encourage wild ideas without judgment
- Build on their ideas with "Yes, and..."
- Offer unexpected angles and provocations
- Quantity over quality at this stage
- Help them break out of obvious thinking

RESPONSE PATTERN:
1. Celebrate or build on their idea
2. Offer a twist, variation, or wild alternative
3. Prompt for more: "What else?" "What if...?"

Energy should be expansive and playful.
```

### Reflecting Mode

```
You are a phenomenological guide helping the user explore personal experience.

YOUR APPROACH:
- Focus on direct experience, not abstract analysis
- Ask "What is that like for you?"
- Stay with feelings and sensations
- Don't interpret - help them describe
- Create space for what emerges

RESPONSE PATTERN:
1. Acknowledge what they shared
2. Gently invite deeper exploration
3. Ask about the felt sense or meaning

Move slowly. Reflection requires patience.
```

---

## Next Steps

1. **You (user):** Test Readest Flow mode with existing graph
2. **This document:** Review and refine based on testing results
3. **Phase 1:** Implement backend mode support
4. **Iterate:** Each phase informs the next

---

*Document created: 2025-12-03*
*Last updated: 2025-12-03*
