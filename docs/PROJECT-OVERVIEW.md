# brain_explore: Comprehensive Project Overview

**Date:** December 2, 2025
**Status:** Phase 1 In Progress
**Version:** 1.0 (Synthesized from analysis findings)

---

## Executive Summary

**brain_explore** is a thinking partnership system—a domain-agnostic architecture that helps people explore complex knowledge domains with an AI that adapts to how they think.

The system works through three interconnected layers that form a thinking partnership:
1. **Layer 1: Knowledge Graph Creation** — Pre-processing pipeline that ingests domain materials into a rich knowledge graph (50k+ entities and relationships)
2. **Layer 2: Thinking Pattern Revelation & Dialogue** — Profile system that reveals how you think, with adaptive questioning tailored to your unique patterns
3. **Layer 3: Thinking Partnership Exploration** — Interactive interface where you explore knowledge with AI as a thinking partner, generating both deeper understanding AND novel conceptualizations

**Current State:** Layers 1 & 2 are built and functional. Layer 3 is deferred. Phase 1 validates that Layers 1 & 2 create genuine value through therapy domain exploration—proving that guided dialogue surfaces valuable concepts that can be extracted and formalized.

**Core Insight:** The system isn't about delivering knowledge or correcting thinking. It's about understanding how *this specific person* thinks, then thinking *with* them using domain knowledge as the medium—enabling them to generate novel insights and conceptualizations through their unique thinking style.

---

## The Vision: Three Interconnected Layers

### Layer 1: Knowledge Graph Creation (Pre-processing & Ingestion Pipeline)

**What it does:** Ingests domain materials (texts, research, frameworks, assessments) and creates a rich, interconnected knowledge graph with entities and relationships (50k+ entities in therapy domain).

**Why it matters:** The knowledge graph is the substrate for thinking partnership. It contains the domain's structure, connections, and implications. A richer, more connected graph enables deeper exploration and more novel conceptualizations.

**How it connects:** Layer 1 provides the raw material for Layers 2 & 3. Without it, there's nothing to think with.

**Status:** ✅ Fully functional. 50k therapy entities processed and indexed in Neo4j + Qdrant.

**Domain-Agnostic:** Can ingest any knowledge domain—scientific, legal, creative, organizational, etc.

---

### Layer 2: Thinking Pattern Revelation & Personalized Dialogue

**What it does:**
- Adaptive questioning reveals *how* you think (your patterns, assumptions, worldview, thinking style)
- Profile captures your unique approach and preferences
- Dialogue adapts to your thinking style—not generic prompts
- Creates insight through understanding your distinctive perspective

**Why it matters:** People think differently. Some need structure, others need freedom. Some think in hierarchies, others in webs. Some ask "why," others ask "what if." Generic dialogue treats everyone the same. Personalized dialogue works *with* how you actually think.

**How it connects:** This layer reveals patterns that inform Layer 3 exploration. Your thinking style becomes the lens through which you engage with the knowledge graph.

**Status:** ✅ Fully functional. Backend operational, dialogue system working, profile system capturing patterns.

---

### Layer 3: Thinking Partnership Exploration (Flow/Flo Interactive Interface)

**What it does:**
- Interactive knowledge exploration interface (reads texts/ebooks with overlaid knowledge graph connections)
- AI acts as a thinking partner—asking clarifying questions, surfacing unexpected connections, challenging assumptions
- System documents your exploration path and thinking process as breadcrumbs
- You extract and formalize your own insights from the thinking partnership

**The Dual Outcome:** Both deepens understanding of existing knowledge AND generates novel conceptualizations not explicitly in the original materials.

**Why it matters:** Reading and researching linearly limits what you discover. A thinking partner who understands how you think can guide you toward connections you wouldn't find alone, and through that process, you generate new frameworks and insights.

**How it connects:** Uses Layer 2 profile to personalize how it guides Layer 1 exploration. Your discovered concepts enrich the knowledge graph for future cycles.

**Status:** ⏳ Not yet built. Deferred to Phase 2+ (after Phase 1 validates Layers 1 & 2).

#### IES Question Engine + AST Mode (Phase 2c Preview)

Design work captured in `docs/IES question engine expansion.md` and `docs/IES AST SiYuan structure.md` now defines how Layer 3 evolves once reactivated:
- **Four thinking modes** — Discovery (schema surfacing), Dialogue (model building), Flow (associative exploration), and the new **AST (Assisted Structured Thinking)** mode that guides high-structure sessions inside SiYuan.
- **Nine question classes** — Schema-Probe, Boundary, Dimensional, Causal, Counterfactual, Anchor, Perspective-Shift, Meta-Cognitive, and Reflective-Synthesis. These serve as the taxonomy for the adaptive question engine so the system can intentionally shift inquiry style instead of relying on generic prompts.
- **Mode Transition Engine + Cognition Model** — Signals from the 6-dimension cognition profile (structure preference, pace, ambiguity tolerance, abstraction level, verification need, novelty preference) determine when to switch modes or rebalance question classes.

AST Mode effectively bridges ForgeMode templates with Flow exploration, ensuring that when Layer 3 resumes in Phase 2c it already has a well-defined structure for ADHD-friendly note capture and question tagging.

---

### Why These Three Form a Thinking Partnership

```
Layer 1 provides rich knowledge substrate
    ↓
Layer 2 reveals your unique thinking patterns
    ↓
Layer 3 uses patterns to guide exploration of Layer 1
    ↓
Thinking partnership generates new concepts
    ↓
You extract and formalize your discoveries
    ↓
Discoveries enrich Layer 1 for next cycle
    ↓ (cycle repeats at deeper level)
```

Each layer enables the others. None is complete alone. Together, they create a thinking partnership where you generate novel insights through guided exploration of rich knowledge.

---

## What's Actually Built

### ✅ FULLY WORKING

**IES Backend (FastAPI Server)**
- Session management: Start sessions, track conversations
- Chat endpoint: Accept user messages, generate therapeutic responses
- Profile system: Store and retrieve user profiles (thinking style, pace, structure preference)
- Database integration: Neo4j for knowledge graph, Qdrant for semantic search
- Health checks and error handling

**SiYuan Plugin**
- User interface for running sessions within SiYuan
- Session display and conversation history
- Profile creation workflow

**Knowledge Graph**
- 48,987 therapeutic and psychological entities in Neo4j
- Vector embeddings in Qdrant for semantic search
- Raw data loaded and indexed

**Therapeutic Dialogue**
- Claude-based question generation
- Context awareness: Remembers conversation history
- Adaptive responses: Questions change based on what you share
- Profile-aware: Greets you based on your profile

---

### ⚠️ PARTIALLY WORKING

**Profile System**
- Schema exists and works
- Can create profiles (detail-first thinker, adaptive pace, moderate structure need)
- Can retrieve profiles
- NOT validated: Does it actually update based on conversations? Does it accurately capture thinking style?

**Entity Extraction**
- Concept: Turn session conversations into structured therapeutic entities
- Status: Design exists, implementation not tested at scale
- Need to run real sessions to validate this works

---

### ❌ NOT BUILT (Deferred)

**Flow Mode Interface**
- Non-linear reading/navigation of knowledge graph
- Interactive PDF reading with concept linking
- Estimated effort: 40-60 hours
- Blocked by: Need proof that core dialogue works first

**Advanced Question Engine**
- 8 different inquiry approaches (Socratic, narrative, somatic, etc.)
- Adaptive selection based on thinking patterns
- Estimated effort: 20-30 hours
- Blocked by: Need profile validation first

**Advanced Pattern Recognition**
- Sophisticated observation of navigation and thinking patterns
- Automatic profile updates from conversation
- Behavioral insights extraction
- Estimated effort: High
- Blocked by: Need real usage data to know what matters

**Multi-Domain Framework**
- Generalization beyond therapy to other domains
- Configuration layer for different use cases
- Estimated effort: 60+ hours
- Blocked by: Need therapy use case proven valuable first

---

## The Current State: Why We're Here

### The Problem That Got Solved (Phase 0)

**Configuration was killing the project.** By Dec 1, 40% of development time was meta-work:
- Deciding which project was active
- Managing configuration across 7 files
- Syncing contradictory instructions
- Deciding what to work on

**The five-agent synthesis revealed:** Infrastructure was 96%, actual therapy exploration was 4%.

**The fix:** Ruthlessly simplified. Deleted the active-project system. Consolidated CLAUDE.md. Moved progress to git history. **Result:** Configuration overhead dropped from 40% to <5%.

### The Current Reality (Dec 2)

**What we know works:**
- IES backend is running and healthy
- Therapeutic dialogue generates coherent, adaptive responses
- One complete therapy session was conducted (Nov 29)
- System proved it can run end-to-end

**What we don't know yet:**
- Does the dialogue system work across 10 different topics?
- Can we extract meaningful therapeutic concepts from sessions?
- Does the profile system actually capture and adapt to thinking patterns?
- Can we build a coherent therapeutic worldview from extracted concepts?

**This is what Phase 1 answers.**

---

## Phase 1: Prove the Core Hypothesis (7-10 Days)

### The Goal

**Prove that Layers 1 & 2 enable genuine thinking partnership that generates valuable concepts.**

Not validating dialogue alone. Not validating the knowledge graph. Validating the complete thinking partnership pipeline:
- Layer 2 dialogue reveals your thinking patterns
- That personalized dialogue guides meaningful exploration
- Exploration surfaces novel conceptualizations
- Those conceptualizations can be extracted, formalized, and documented
- The full loop creates genuine value

### The Work

**Run 10 therapy exploration sessions** where personalized dialogue guides thinking, and you extract concepts:
1. ✅ How thinking patterns affect project completion (Nov 29)
2. The distinction between acceptance and resignation
3. What creates safety in dialogue
4. How curiosity differs from avoidance
5. What makes change feel possible
6. The relationship between structure and creativity
7. How to know when something is "good enough"
8. What resistance is trying to protect
9. The role of compassion in change
10. How to work with your own patterns

**Extract and formalize 20-30 therapeutic concepts** from the sessions:
- Identify key insights and frameworks that emerge from dialogue
- Name each concept clearly (e.g., "Narrow Window of Awareness")
- Define what it means and why it matters
- Note where it came from (which session, what dialogue surfaced it)
- Document how your thinking patterns influenced what was discovered
- Show connections to other concepts and literature

**Document the extraction → formalization pipeline:**
- Show how dialogue-driven exploration surfaces concepts
- Demonstrate how your unique thinking patterns shaped what you discovered
- Create a coherent framework showing concept connections
- Articulate the emerging therapeutic worldview

### Success Criteria

**System proves thinking partnership works when:**
- ✅ Can run 10 complete sessions without errors
- ✅ Each session shows adaptive questioning (questions respond to your actual thinking)
- ✅ Profile system demonstrates it captured your thinking patterns
- ✅ Can extract meaningful, novel concepts from session content
- ✅ Concepts connect coherently and form a framework
- ✅ Evidence that your unique thinking patterns shaped what was discovered
- ✅ One complete feedback loop works: dialogue reveals pattern → guides exploration → surfaces concept → enriches understanding
- ✅ Validation that thinking partnership generates novel, valuable insights

**You know it works when:**
- ✅ Sessions feel like genuine thinking partnership (not chatbot Q&A)
- ✅ You discover frameworks and connections you didn't have before
- ✅ Questions address your actual thinking and build on your patterns
- ✅ Extracted concepts feel psychologically coherent and novel
- ✅ Can articulate therapeutic worldview based on discovered concepts
- ✅ Evidence that the system helped you think in new ways

---

## Phase 2: Build Understanding (Post-Phase 1)

**Only starts after Phase 1 proves the core hypothesis.**

### Goals
- Develop 50-100 therapeutic concepts (extending Track 1)
- Build explicit connections between concepts
- Integrate relevant research literature
- Extract and document thinking patterns from sessions

### Success Looks Like
- Track 1 (Human Mind) is coherent and substantially complete
- Can articulate a comprehensive therapeutic worldview
- System has identified 3-5 key thinking patterns
- Can point to specific concepts, connections, and literature supporting them

---

## Phase 3: Integrate Next Capability (Post-Phase 2)

**Choose one capability to add:**

**Option A: Flow Mode Reading**
- Implement interactive PDF reading with knowledge graph navigation
- Start with one therapy book, explore concepts non-linearly

**Option B: Advanced Dialogue**
- Implement 8 inquiry approaches
- Adapt questioning based on identified patterns

**Option C: Expanded Content**
- Continue developing Tracks 2-3 (Change Process, Method)

---

## What's NOT Being Done (The Parking Lot)

**These features are documented but explicitly deferred:**
- Multi-domain framework generalization
- Advanced profile system (8 dimensions)
- Advanced question engine (8 inquiry approaches)
- Flow Mode reading interface
- MCP server integration
- n8n integration
- Synapse component ports
- Advanced visualization and analytics

**Rule:** Nothing new enters development until Phase 1 proves core value.

**Why:** Two failed projects (Synapse abandoned Oct 6) and one nearly-failed project (brain_explore Dec 1) followed the same pattern: "While building X, I see how Y would be useful, so I add Y, which makes me think Z would help..." Configuration explodes. Original goal gets deferred. Project abandons.

This time: Finish Phase 1 before adding anything.

---

## Architecture Overview

### System Components

```
User (in SiYuan or direct API)
    ↓
IES Backend (FastAPI, :8081)
    ├─ Session Manager (start/retrieve sessions)
    ├─ Profile Manager (create/update profiles)
    ├─ Chat Endpoint (receive message → generate response)
    └─ Integration Layer
        ├─ Neo4j (Knowledge graph: 48,987 entities)
        ├─ Qdrant (Vector search: semantic similarity)
        └─ Claude API (Response generation)

SiYuan Plugin (Optional UI)
    └─ Connects to IES Backend
```

### Data Flow: A Therapy Session

```
1. User creates profile
   → Profile stored in backend
   → System retrieves profile context

2. User starts session
   → Session ID created
   → Greeting generated based on profile
   → Conversation history initialized

3. User sends message
   → Message added to history
   → Relevant concepts queried from Neo4j (semantic search)
   → Profile context retrieved
   → Claude generates adaptive response
   → Response sent to user

4. Profile updates (future enhancement)
   → System analyzes conversation
   → Updates profile based on patterns
   → Next session uses refined profile
```

---

## Technical Details

### Backend Stack
- **Framework:** FastAPI (Python)
- **Database:** Neo4j 5.x (graph database)
- **Vector Store:** Qdrant (semantic search)
- **LLM:** Claude API (response generation)
- **Testing:** 61 unit tests (54 passing)

### Plugin Stack
- **Framework:** Svelte + TypeScript
- **Target:** SiYuan note-taking app
- **Build:** npm (webpack)
- **Status:** Builds successfully, connects to backend

### Infrastructure
- **Hosting:** Docker Compose (local dev)
- **Services:** Neo4j, Qdrant both running
- **Port:** Backend on :8081

---

## Key Insights from Analysis

### Why Configuration Was Blocking Work

Over 72 hours (Nov 29 - Dec 2), configuration grew from 0% to 40% overhead:
- Active-project system (created but never used)
- Meta-override escape hatches (needed to bypass own rigidity)
- 37 configuration files requiring sync
- 1:6 configuration-to-code ratio (should be 1:100+)

**Root cause:** While building, each new idea seemed useful, so it got added to the project instead of deferred.

**Solution:** Ruthless simplification. Delete the meta-layer. Trust the phased plan.

---

### Why Synapse Was Abandoned (The Precedent)

**Timeline:**
- Sept 11-30: Core development (APIs, graph model, extraction)
- Oct 1-3: Feature expansion (multi-source ingestion, graph explorer)
- Oct 3-6: Complexity explosion (54 agent types, 15-layer pipeline, ABSOLUTE RULES)
- Oct 6+: Momentum stops → project abandoned

**Pattern:** Each feature seemed necessary. Configuration exploded. System became harder to activate. Easier to stop than continue.

**Lesson:** brain_explore was following the same path on Dec 1. Phase 1 breaks the pattern by deferring all features.

---

### The Irony (and the Point)

You're building a system to help people understand their thinking patterns **while your own thinking patterns were creating scope expansion.**

**The solution:** Don't fight how you think. Channel it. Modular architecture where new ideas become "future capabilities" instead of "current project additions."

When Phase 1 is done, you'll have proven the core works. Then Phases 2-4 can pull in capabilities as needed, without bloating Phase 1.

---

## Workflows

### Running a Therapy Session

```bash
# Terminal 1: Ensure backend is running
cd ies/backend
PYTHONPATH=./src python -m uvicorn ies_backend.main:app --host 0.0.0.0 --port 8081

# Terminal 2: Run a session
python scripts/run-session.py --topic "Your therapeutic question"

# The script will:
# 1. Create a session
# 2. Show your profile and greeting
# 3. Enter interactive conversation mode
# 4. Save transcript when you type 'done'
```

### Documenting Progress

```bash
# After each session
git add docs/session-transcripts/
git commit -m "docs: session N - topic"

# At end of day/week
# Update docs/session-notes.md with reflections
```

### Extracting Concepts

**Process:**
1. Read session transcript
2. Identify key therapeutic ideas that emerged
3. Create concept document in `therapy/Track_1_Human_Mind/`
4. Document connections to other concepts
5. Commit

**Example:** From Nov 29 session, extracted "Narrow Window of Awareness" concept documenting how human perception creates both meaning and suffering.

---

## Success Metrics

### Quantitative (Phase 1)
- [ ] 10 sessions completed
- [ ] 20-30 concepts documented
- [ ] Concepts connected (relationship map)
- [ ] Entity extraction validated
- [ ] Profile updates working

### Qualitative (Phase 1)
- Sessions feel therapeutic (not chatbot-like)?
- System understands how you think?
- Concepts feel psychologically real?
- Can articulate therapeutic worldview?

### Timeline
- **Target:** 7-10 days to complete Phase 1
- **Current progress:** 1/10 sessions, 1/30 concepts, 0 days elapsed
- **Next session:** Topic #2 (Acceptance vs. Resignation)

---

## Known Limitations & Open Questions

### What We Don't Know Yet

1. **Scale:** Does the system work across 10 topics, or does it plateau?
2. **Concept Quality:** Will extracted concepts be psychologically coherent?
3. **Profile Adaptation:** Does the profile system actually capture and update thinking patterns?
4. **Entity Extraction:** Can we reliably extract therapeutic concepts from sessions?
5. **Feedback Loops:** Can we demonstrate that profile updates lead to better questions?

### What We're Betting On

- That 10 sessions will reveal patterns (not 30)
- That 20-30 concepts will feel sufficient to articulate a worldview (not 100)
- That the dialogue system is already good enough (no tweaking needed)
- That manual concept extraction will work (before automation)

### What Could Break Phase 1

- Dialogue becomes generic after a few sessions
- Concepts don't connect meaningfully
- Profile system doesn't actually change between sessions
- Entity extraction fails or produces garbage

**If any of these happen:** Document it, adjust Phase 2 plan accordingly. The goal is learning, not proving we were right.

---

## Decision Log

### Dec 2, 2025: Phase 0 Completion → Phase 1 Start
- **Decision:** Delete active-project system, consolidate CLAUDE.md, initialize git
- **Rationale:** Configuration overhead was 40%, blocking actual work
- **Result:** Overhead dropped to <5%, ready to do real work

### Dec 2, 2025: Focus on Therapy Dialogue, Not Flow Mode
- **Decision:** Phase 1 validates dialogue layer only, defer Flow Mode to Phase 2+
- **Rationale:** Three layers needed for full vision, but only dialogue is functional enough to validate
- **Result:** Shorter Phase 1 timeline, faster validation

### Dec 2, 2025: Manual Concept Extraction, Not Automated
- **Decision:** Use human reading + writing concept documents, not automated entity extraction
- **Rationale:** Want to validate quality first, automate after
- **Result:** Phase 1 generates 20-30 high-quality concepts

---

## Getting Started (Right Now)

### For Understanding the Project
1. Read this document (you're doing it)
2. Read `docs/five-agent-synthesis.md` (comprehensive analysis)
3. Skim `CLAUDE.md` (quick reference)

### For Running Sessions
1. Ensure backend is running: `curl http://localhost:8081/health`
2. Run a session: `python scripts/run-session.py --topic "your question"`
3. Document afterward: Edit transcript, add reflections
4. Commit: `git add docs/session-transcripts/; git commit -m "..."`

### For Extracting Concepts
1. Read completed session transcripts
2. Identify key therapeutic ideas
3. Create concept document in `therapy/Track_1_Human_Mind/`
4. Document connections
5. Commit

---

## Resources

**For Understanding Why:**
- `docs/five-agent-synthesis.md` — Complete analysis of vision, gaps, configuration problems, phased path

**For Getting Started:**
- `docs/phase-1-getting-started.md` — Quick start guide
- `scripts/run-session.py` — Session runner script
- `docs/phase-1-action-plan.md` — Daily workflow and topics

**For Reference:**
- `CLAUDE.md` — Project quick reference
- `docs/parking-lot.md` — Features explicitly deferred
- `docs/session-notes.md` — Reflection log (append-only)

**For Technical Details:**
- `ies/backend/README.md` — Backend setup
- `ies/plugin/` — Plugin source
- `docker-compose.yml` — Infrastructure

---

## Questions?

This document synthesizes findings from the analysis phase. It's the single source of truth for "what is brain_explore and where are we."

If something is unclear, it means the document needs improvement. Feedback welcome.

---

**End of Project Overview**

*Last Updated: December 2, 2025*
*Synthesized from: Five-Agent Analysis, Phase 1 Plan, Vision Documents*
