# Phase 1 Workflow: From Session to Formalized Concepts

**Purpose:** Complete reference for running Phase 1 therapy exploration sessions and extracting therapeutic concepts.

**Audience:** You, during Phase 1. This is your checklist and reference guide.

---

## The Complete Pipeline

```
Session Dialogue
    ↓
Session Transcript (auto-saved)
    ↓
Extraction Service (automated entity extraction)
    ↓
Interpret Extracted Entities
    ↓
Formalize into Concept Documents
    ↓
Document Connections Between Concepts
    ↓
Commit to git
```

Each step is detailed below.

---

## Step 1: Run a Therapy Exploration Session

### Before the session

```bash
# Verify backend is healthy
curl http://localhost:8081/health
# Should return: {"status":"healthy"}

# Check Docker services
docker compose ps
# Should show neo4j and qdrant running
```

### Run the session

```bash
# From project root
python scripts/run-session.py --topic "Your therapeutic question"

# The script will:
# 1. Create a session with your profile
# 2. Show your greeting and profile summary
# 3. Enter interactive conversation mode
# 4. Wait for your input (type your response)
# 5. Generate and display assistant response
# 6. Loop until you type "done"
# 7. Auto-save transcript to docs/session-transcripts/session-YYYYMMDD-HHMMSS.md
```

### What the session should feel like

- **Authentic dialogue** — You're genuinely exploring a therapeutic question, not testing the system
- **Adaptive responses** — The assistant's questions should build on what you said, not follow a script
- **Thinking partnership** — You should feel like you're thinking *with* the system, not talking *to* it
- **Natural pacing** — 5-10 exchanges is typical (20-30 minutes)

### After the session

The script auto-saves to:
```
docs/session-transcripts/session-20251202-143022.md
```

Open the file. It contains:
- Your profile summary
- Session greeting
- Full conversation (alternating You/Assistant)
- Blank Reflection section (you'll fill this in later)

---

## Step 2: Extract Entities Using the Backend Service

The IES backend has an **ExtractionService** that automatically extracts entities from transcripts.

### What it extracts

**Entity Types:**
- **idea** — A concept, belief, or insight that emerged
- **person** — A theorist, author, or figure referenced
- **process** — A method, technique, or way of doing something
- **question** — An open question or inquiry
- **tension** — A conflict, paradox, or unresolved opposition

**Entity Domains:**
- **therapy** — Related to therapeutic approach, theory, or practice
- **personal** — Related to your personal experience or context
- **meta** — About the exploration process itself

**Entity Status:**
- **seed** — First mention, rough idea, needs more exploration
- **developing** — Has been explored some, taking shape
- **solid** — Well-developed, clearly articulated

**Entity Connections:**
- **supports** — This entity strengthens/supports another
- **tensions** — This entity is in tension with another
- **develops** — This entity develops/extends another

### Run extraction on your transcript

```bash
# Using the backend API (requires backend running on :8081)

SESSION_ID="your-session-id"  # From session output
TRANSCRIPT_FILE="docs/session-transcripts/session-20251202-143022.md"

# Extract entities (API endpoint)
curl -X POST http://localhost:8081/session/extract \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"transcript\": \"$(cat $TRANSCRIPT_FILE)\"}"

# Returns JSON with:
# - entities: [list of extracted entities with connections]
# - session_summary: {key_insights, open_questions, threads_explored}
```

### Example extraction output

```json
{
  "entities": [
    {
      "name": "Narrow Window of Awareness",
      "kind": "idea",
      "domain": "therapy",
      "status": "solid",
      "description": "Humans perceive through limited senses and pattern-matching, creating meaning from incomplete data...",
      "quotes": [
        "We're aware enough to create meaning but not aware enough to see our blind spots",
        "Our limitation is our gift"
      ],
      "connections": [
        {"to": "Meaning-Making", "relationship": "supports"},
        {"to": "Paradox of Efficiency", "relationship": "develops"}
      ]
    },
    {
      "name": "Meaning-Making as Solution",
      "kind": "idea",
      "domain": "therapy",
      "status": "developing",
      "description": "The act of creating meaning, even false meaning, is adaptive and necessary...",
      "quotes": ["Better than walking into walls"],
      "connections": [
        {"to": "Narrow Window of Awareness", "relationship": "develops"}
      ]
    }
  ],
  "session_summary": {
    "key_insights": [
      "Understanding human limitation is foundational to therapy",
      "Meaning-making is not a bug, it's the system working as designed"
    ],
    "open_questions": [
      "How do we distinguish necessary vs unnecessary pain?",
      "Where does neurodivergence fit in this framework?"
    ],
    "threads_explored": [
      "The paradox of efficiency in human perception",
      "How therapy can work within limitations rather than against them"
    ]
  }
}
```

---

## Step 3: Interpret the Extracted Entities

The extraction service identifies entities automatically, but **you decide which ones are worth formalizing into concept documents.**

### Decision criteria

**Extract to a concept document if:**
- ✅ The entity represents a core insight (not a tangential mention)
- ✅ You can articulate why it matters therapeutically
- ✅ It connects to other concepts or research
- ✅ You could explain it to someone else
- ✅ It emerged from your authentic thinking, not prompted

**Skip if:**
- ❌ It's a first mention (seed status) without development
- ❌ It's a person/reference without your own insight
- ❌ It's metadata about the process, not the content
- ❌ You can't articulate why it's important yet

### Example from Nov 29 session

**Extracted:**
- Narrow Window of Awareness (solid) → **formalize**
- Meaning-Making as Solution (developing) → **consider for next session**
- Paradox of Efficiency (seed) → **skip for now**
- Therapy Isn't About "More Correct" (solid) → **formalize**

---

## Step 4: Formalize Concepts into Documents

Take extracted entities and create polished concept documents.

### Concept document structure

**Filename:** `therapy/Track_1_Human_Mind/NN-concept-name.md`

```markdown
# Concept Name

## Definition
[1-3 sentences defining what this concept means]

## The Core Insight
[What makes this insight valuable? Why does it matter?]

## Clinical Application
[How does this apply to therapy?]

### The Therapeutic Stance
[What approach does this suggest for working with clients?]

## Where This Emerges
**Session:** [Session number and date]
**Topic:** [What question was being explored]

**Key dialogue that surfaced this:**
- Turn 3: User says X, Assistant asks Y, User realizes Z
- Turn 5: This connection made the insight click

## Related Concepts
- **Concept A** (connection type) — How it relates
- **Concept B** (connection type) — How it relates

## Research Connections
- **Theory/Author** — Relevant research or frameworks
- **Empirical finding** — Research evidence

## Open Questions
1. [Question 1 this concept raises]
2. [Question 2]

## Evidence from Sessions
- **Session 1:** Where this showed up
- **Session 2:** How it developed

---

**Status:** [seed | developing | solid]
**Last Updated:** [Date]
**Thinking Patterns That Influenced This:** [How did your thinking style shape this discovery?]
```

### Example: Narrow Window of Awareness (from Nov 29)

See: `therapy/Track_1_Human_Mind/01-narrow-window-of-awareness.md`

This is your template. Use it for all concept documents.

### Tips for formalizing

1. **Use exact quotes** from the session that led to the insight
2. **Show the dialogue path** — How did the assistant's question lead to your realization?
3. **Link to related concepts** even if they don't exist yet (placeholder)
4. **Be precise** about therapeutic implications, don't stay abstract
5. **Document your thinking pattern** — How did your unique way of thinking shape this insight?

---

## Step 5: Document Connections Between Concepts

After extracting 3-4 concepts, create a **Concept Map** showing how they relate.

### Relationship types

- **develops** — Concept A extends or develops Concept B
- **tensions** — Concept A contradicts or creates tension with Concept B
- **supports** — Concept A provides foundation for Concept B
- **contrasts** — Concept A shows difference with Concept B
- **instantiates** — Concept A is a specific example of Concept B

### Create a concept map file

**Filename:** `therapy/Track_1_Human_Mind/CONNECTIONS.md`

```markdown
# Track 1 Concept Connections

## Foundational Concepts

**Narrow Window of Awareness** (1)
- develops → Meaning-Making as Solution (2)
- develops → Unnecessary Pain (TBD)
- supports → Unique Personhood (TBD)

**Meaning-Making as Solution** (2)
- develops from → Narrow Window of Awareness (1)
- supports → Therapy Isn't About "More Correct" (3)

**Therapy Isn't About "More Correct"** (3)
- supports from → Meaning-Making as Solution (2)
- instantiates → Working Within Limitations (TBD)

## Visual Structure

```
Narrow Window of Awareness
  ├── Meaning-Making (adaptive response to limitation)
  │    └── Therapy works within framework, not against it
  └── Unique Personhood (each person's window is singular)
```

## Research Grounding

- Predictive Processing (Barrett, Clark) → Narrow Window
- Existentialism (Sartre) → Accepting limitation
- Phenomenology (Heidegger) → How consciousness shapes perception
```

---

## Step 6: Commit to Git

After each concept or batch of concepts:

```bash
# Add the session transcript
git add docs/session-transcripts/session-20251202-143022.md

# Add concept documents
git add therapy/Track_1_Human_Mind/NN-concept-name.md

# Update connections if changed
git add therapy/Track_1_Human_Mind/CONNECTIONS.md

# Commit with clear message
git commit -m "docs: session N - extracted concepts (Concept Name, Related Concept)

- Concept Name: [brief description]
- Related Concept: [brief description]
- Key insight: [what you learned]"
```

---

## Complete Workflow Checklist

Use this checklist for each session:

### Before Session
- [ ] Backend healthy: `curl http://localhost:8081/health`
- [ ] Docker services running: `docker compose ps`
- [ ] Have a genuine therapeutic question ready

### During Session
- [ ] Run: `python scripts/run-session.py --topic "..."`
- [ ] Engage authentically (5-10 exchanges)
- [ ] Type "done" when complete
- [ ] Verify transcript saved: `ls -la docs/session-transcripts/`

### After Session
- [ ] Run extraction on transcript (via API)
- [ ] Review extracted entities
- [ ] Decide which to formalize (solid or developing, not seed)
- [ ] Create concept documents (therapy/Track_1_Human_Mind/)
- [ ] Update CONNECTIONS.md
- [ ] Document how your thinking patterns influenced discoveries
- [ ] Commit: `git add ... && git commit -m "..."`

### Progress Tracking
After each session, update progress:
- Sessions completed: X/10
- Concepts formalized: Y/20-30
- New connections identified: Z

---

## What Success Looks Like

### After Session 1 (Nov 29) — Already Done
- 1 session transcript
- 1 concept formalized (Narrow Window of Awareness)
- 1 connection documented (to Meaning-Making, Unnecessary Pain)

### After Session 5
- 5 session transcripts
- 8-10 concepts formalized
- Clear patterns emerging (which ideas are foundational, which are developing)
- Therapeutic worldview starting to cohere

### After Session 10 (Phase 1 Complete)
- 10 session transcripts
- 20-30 concepts formalized
- Comprehensive CONNECTIONS.md showing concept map
- Clear therapeutic worldview articulated
- Evidence that personalized dialogue shaped what was discovered
- Ready to move to Phase 2 (Flow/Flo interface)

---

## Troubleshooting

### Backend won't respond to extraction request

```bash
# Check backend is running
curl http://localhost:8081/health

# If not running, start it:
cd ies/backend
PYTHONPATH=./src python -m uvicorn ies_backend.main:app --host 0.0.0.0 --port 8081
```

### Extraction returned entities I don't recognize

This means the extraction service is picking up concepts that weren't meaningful to you. That's okay—just don't formalize them. The system is learning what matters.

### Session felt generic, not like thinking partnership

This usually means:
- The topic was too abstract (try more specific, personal questions)
- Your responses were too brief (give the system more to work with)
- Your profile needs updating (it's basing questions on old assumptions)

Try again with a different topic.

### Can't decide if a concept is "solid" enough to formalize

**Ask yourself:**
- Could I explain this to another therapist?
- Does it change how I think about therapy?
- Can I point to the dialogue that surfaced it?

If yes to all three, it's solid enough.

---

## Key Principles for Phase 1

1. **Authentic exploration first** — Run genuine sessions, not tests
2. **Let the extraction service help** — Use its output to guide what you formalize
3. **Formalize deliberately** — Not every extracted entity needs a concept document
4. **Document your thinking** — Show how your unique patterns shaped discoveries
5. **Build connections gradually** — Patterns will emerge across 10 sessions
6. **Commit frequently** — After each session at minimum

---

## Next Steps After Phase 1

Once 10 sessions complete and 20-30 concepts are formalized:

1. **Review the therapeutic worldview** — What's the coherent framework that emerged?
2. **Identify key patterns** — Which concepts are foundational? Which are still developing?
3. **Plan Phase 2** — Layer 3 (Flow/Flo) with this knowledge foundation
4. **Extract thinking patterns** — Document how your unique thinking shaped discoveries

---

**Ready to run Session 2?**

Choose a topic from the Phase 1 plan and run:
```bash
python scripts/run-session.py --topic "Your question here"
```

The extraction, formalization, and connection-building will happen naturally as you go.

---

*Last Updated: December 2, 2025*
*Reference: docs/phase-1-action-plan.md, docs/PROJECT-OVERVIEW.md, CLAUDE.md*
