# Intelligent Exploration System - Architecture

## Core Concept

The IES is an AI plugin for SiYuan that guides knowledge exploration through conversation, automatically extracting entities and connections, and building integrated understanding over time.

**Key insight:** The user never manages metadata. They just have conversations. The AI does entity extraction, connection discovery, and pattern recognition.

## The Exploration Loop

```
Sessions (Develop mode)
    │
    ├── creates ──► Entity Pages ◄──── Literature (from books)
    │                    │
    │                    ▼
    │              Knowledgebase (Neo4j + SiYuan)
    │                    │
    │                    │ (Explore mode)
    │                    ▼
    └── updates ──► Integrated Theories (Synthesize mode)
```

## Three Artifacts Per Session

1. **Session Document** - What happened (immutable record)
   - Topics explored, entities created, connections discovered
   - Research triggered, open questions
   - Links to transcript and entities

2. **Raw Transcript** - Full conversation preserved
   - AI processing notes attached
   - Provenance for quotes

3. **Entity Pages** - Updated/created from session
   - Core statement, evolution history
   - Connections to KB
   - Source quotes from sessions

## Plugin Modes

### Develop Mode (Socratic)
- AI guides with personalized questions
- Follows threads based on user response
- Identifies entities as they emerge in conversation
- Creates session document at end
- Updates entity pages and graph

### Explore Mode
- Browse knowledgebase (literature + personal)
- Clickable entities → creates page on demand
- Find connections, fill gaps
- Queue research

### Synthesize Mode
- Integrate learnings into Integrated Theory documents
- AI helps weave entities into coherent narrative
- Identifies gaps in the theory

## Knowledgebase: Annotation Layer

- Literature entities live in Neo4j (49k)
- SiYuan pages created ON DEMAND when accessed
- Personal entities always have pages
- Hub page shows: stats, recent, most connected, suggestions

## Ontology: Flexible Properties

Instead of rigid entity types, use block attributes:
- `custom-kind`: idea, person, process, artifact, etc.
- `custom-domain`: therapy, software, personal, etc.
- `custom-status`: seed, developing, solid
- Additional tags for enrichment

AI identifies and applies these during extraction - user doesn't manage.

## Session Flow

1. User starts session (or AI suggests based on gaps)
2. AI guides exploration with questions
3. Entities identified in real-time
4. AI: "Let me capture what emerged..." → generates session doc
5. Graph updated, entity pages updated
6. Hub refreshed with new stats/suggestions

## Implementation Status

### Phase 1: Profile Foundation ✅
- 6-dimension cognitive profile (processing, attention, communication, executive, sensory, masking)
- Neo4j persistence with async client
- SiYuan profile pages (human-readable)
- `/onboard-profile` command for conversational profile building
- `/check-in` command for session capacity check

### Phase 2: Backend Core ✅
- Entity extraction via Claude API (detailed prompt for kind/domain/status/connections)
- Session document generation → SiYuan (Key Insights, Entities, Open Questions, Quotes)
- Neo4j entity storage (create, update with status promotion, connections)
- API endpoints: POST /session/process, GET /session/entities/{user_id}

### Phase 3: Question Engine ✅
- State detection service (8 states, signal analysis, capacity override)
- Approach selection service (profile-aware, state-aware, with adaptations)
- Question templates (30 templates from therapy/coaching books)
- API endpoints: detect-state, select-approach, templates, generate-questions

### Phase 4: Session Integration ✅

**Hybrid Integration Approach:**
- Claude Code handles conversation naturally
- Backend called at key moments (start, state changes, end)
- Question Engine is a tool, not a controller

**Session Start — Context Loading:**
- Load profile + current capacity
- Load last 2-3 session summaries (continuity without overwhelm)
- Load active "developing" entities
- New endpoint: `GET /session/context/{user_id}` returns:
  - `profile_summary`: condensed for prompts
  - `capacity`: current 1-10 level
  - `recent_sessions`: last 2-3 with topic, entities, hanging_question (medium detail)
  - `active_entities`: developing/seed entities being worked on

**During Session — Judgment-Based:**
- No automatic polling (breaks flow)
- Claude calls Question Engine when sensing shift OR user says "I'm stuck"
- API available as tool, not mandatory

**Session End — Explicit + Suggestion:**
- Primary: `/end-session` command
- Secondary: Claude suggests at energy drop or 45+ min
- Minimal closure: trigger extraction, show summary, no required reflection

**Commands:**
- Enhanced `/explore-session` — loads context, profile-aware
- New `/end-session` — triggers extraction, shows summary

**Tested & Verified (2025-12-01):**
- All 16 API routes working on port 8081
- Context loading returns proper JSON structure
- Session metadata storage for continuity
