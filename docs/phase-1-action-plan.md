# Phase 1: Prove Core Hypothesis — Action Plan

**Status:** Just Started (Dec 2, 2025)
**Goal:** Use the system for therapy exploration, prove it works
**Timeline:** 7-10 days
**Success Criteria:** System captures exploration, extracts entities, creates concepts, adapts profile

---

## What We Have (Verified Dec 2)

✅ **Backend:** FastAPI service running on :8081
- Profile endpoint: Create and retrieve user profiles
- Session endpoint: Start sessions, capture exploration conversations
- Chat endpoint: Generate adaptive therapy questions
- Neo4j: Running with 48,987 entities
- Qdrant: Vector store ready for embeddings

✅ **Plugin:** Svelte-based SiYuan plugin
- Session management interface
- Message history display
- Profile creation workflow
- Builds successfully: `npm run build` → `dist/`

✅ **Infrastructure:** Docker-based architecture
- Neo4j: 5.x with APOC plugin
- Qdrant: Vector database for semantic search
- Both running and accessible

✅ **Proof of Concept:** First therapy session
- 5-turn exploration conversation
- Adaptive questions responding to content
- System demonstrates core capability

---

## Phase 1 Actions (7-10 Days)

### Week 1: Run Exploration Sessions

**Goal:** Capture 10 therapy exploration sessions (one per day)

Each session should:
1. Start with a genuine therapeutic question or topic
2. Continue for 5-10 turns of dialogue
3. Explore thinking patterns, worldview, therapeutic assumptions
4. Save session transcript to documentation
5. Note what emerged, what patterns appeared

**Example Topics for Sessions:**
1. How thinking patterns affect project completion (done)
2. The distinction between acceptance and resignation
3. What creates safety in dialogue
4. How curiosity differs from avoidance
5. What makes change feel possible
6. The relationship between structure and creativity
7. How to know when something is "good enough"
8. What resistance is trying to protect
9. The role of compassion in change
10. How to work with your own patterns

**Approach:**
- Sit down each morning with the plugin or use API directly
- Choose a topic you genuinely want to understand
- Have the conversation
- Let the system do the questioning
- Notice what it gets right and what it misses

---

### Week 2: Extract & Document Concepts

**Goal:** Create 20-30 therapeutic concepts from exploration sessions

**Process:**
1. Read through 10 session transcripts
2. For each meaningful concept that emerges:
   - Name it clearly (e.g., "Narrow Window of Awareness")
   - Define what it means
   - Note where it came from (which session)
   - Connect it to related concepts
   - Add clinical evidence/examples from sessions
3. Create concept documents in `therapy/Track_1_Human_Mind/`
4. Build explicit connections between concepts

**Expected Outcomes:**
- 20-30 concept documents
- Clear therapeutic worldview emerging
- Visible connections between concepts
- Foundation for Track 1 (Human Mind)

---

### Success Criteria for Phase 1

**System Proves It Works When:**

- [ ] Can run 10 complete therapy exploration sessions without errors
- [ ] Each session shows adaptive questioning (questions respond to content)
- [ ] Profile system captures patterns from conversation (thinking style changes)
- [ ] Can extract entities from session content
- [ ] Can create meaningful therapeutic concepts from sessions
- [ ] Concepts connect meaningfully to each other
- [ ] One complete feedback loop works:
  - Profile identifies pattern
  - Question targets that pattern
  - Session explores pattern
  - Profile updates from exploration
  - Next question builds on new understanding

**Personal Validation When:**

- [ ] Sessions feel genuinely therapeutic (not just chatbot)
- [ ] Learn something about yourself from the system
- [ ] Questions address your actual thinking (not generic)
- [ ] Concepts you create feel psychologically coherent
- [ ] Can articulate therapeutic worldview based on concepts

---

## Technical Checkpoints

### Before Each Session
```bash
# Verify backend is running
curl http://localhost:8081/health
# Should return: {"status":"healthy"}

# Check Docker services
docker compose ps
# Should show neo4j and qdrant both running
```

### Session Documentation
Each session should be documented:
```
docs/session-transcripts/session-001-DATE.md
- Topic: What was the main therapeutic question?
- Key Moments: Where did insight emerge?
- Patterns Noticed: What thinking patterns appeared?
- Concepts Extracted: What therapeutic ideas emerged?
- What Worked: What did the system do well?
- What Missed: Where did it not understand?
```

### Entity Extraction Test
After 3-4 sessions, test entity extraction:
```bash
# Query Neo4j for entities extracted from sessions
# Check: Did system identify therapeutic concepts?
# Check: Are connections reasonable?
```

---

## Daily Workflow

**Each morning (15-20 minutes):**

1. **Start session**
   ```bash
   # Via plugin in SiYuan or direct API
   curl -X POST http://localhost:8081/session/start \
     -H "Content-Type: application/json" \
     -d '{"user_id": "chris"}'
   ```

2. **Choose a therapeutic topic**
   - Something genuine you want to understand
   - Related to thinking patterns, worldview, change
   - Different topic each day

3. **Have the conversation**
   - Let system ask the questions
   - Respond authentically
   - Notice what emerges
   - Continue for 5-10 exchanges

4. **Document the session**
   - Save transcript
   - Note key moments
   - Identify concepts that appeared
   - How did the system do?

5. **End of day: Log progress**
   - Update `docs/session-notes.md`
   - Commit if meaningful progress
   - Note what to focus on next

---

## What NOT To Do (Stay Disciplined)

❌ **Don't start coding features yet**
- Plugin works, backend works
- Everything needed already exists
- Focus on *using* the system, not building it

❌ **Don't try to optimize entity extraction**
- Test what exists first
- Only optimize after Phase 1 proves concept works
- Early optimization is premature

❌ **Don't add new endpoints or functionality**
- Session system works
- Chat system works
- Everything else can wait
- This is about exploration, not building

❌ **Don't try to make concepts "perfect"**
- Get them documented
- Connections will emerge naturally
- Perfection is the enemy of progress

❌ **Don't generalize from one session**
- You need patterns from 10 sessions
- Themes emerge from data, not assumptions
- Trust the process

---

## Metrics To Track

### Quantitative
- [ ] Sessions completed: __ / 10
- [ ] Concepts created: __ / 20
- [ ] Connections documented: __ / 30+
- [ ] Entity extractions working: Yes / No
- [ ] Profile updates working: Yes / No

### Qualitative
- Does dialogue feel therapeutic?
- Does system understand you?
- Do concepts feel psychologically real?
- Are connections meaningful?
- Can you articulate your therapeutic worldview?

---

## Decision Points During Phase 1

### If Entity Extraction Breaks
- Document the error
- Don't try to fix yet
- Note what should be different
- Continue with manual documentation

### If Profile Isn't Adapting
- Check that profile updates are being sent
- Manually validate profile changes
- Continue regardless - focus on concepts
- Fix profile adaptation in future phase

### If Dialogue Becomes Generic
- Change topics more dramatically
- Ask more specific therapeutic questions
- Note what triggers better responses
- Document what works for adjustment later

### If You Lose Interest
- This is a data point (what causes disengagement?)
- Change topics or approach
- Document why
- Continue with different angle

---

## Success Looks Like (End of Phase 1)

**In `docs/`:**
- `session-transcripts/` with 10 documented sessions
- `therapeutic-concepts/` with 20-30 concept files
- `phase-1-synthesis.md` articulating what you learned

**In Neo4j:**
- 20-30 new therapeutic concept nodes
- Connections between concepts visible
- Session data stored and queryable

**In your understanding:**
- Clear therapeutic worldview articulated
- Know which thinking patterns matter most
- Understand what creates change
- Can see connections between concepts

**In git history:**
- One commit per session
- Clear messages about what emerged
- Final commit: "Phase 1 complete - core hypothesis proven"

---

## Why This Approach Works

**The synthesis document showed:** Projects fail when configuration exceeds content.

**This action plan prevents that by:**
1. **Doing the actual work first** (therapy exploration)
2. **Using what exists** (no new features)
3. **Documenting as you go** (not retrospectively)
4. **Proving value each day** (measurable progress)
5. **Staying disciplined** (no scope creep)

You have everything you need. This phase is about *using* the system to prove the hypothesis works, not about building more infrastructure.

---

## Next Review

After 3 sessions: Checkpoint conversation
- Is dialogue working as expected?
- Are patterns emerging?
- Do concepts feel real?
- Adjust approach if needed

After 7 sessions: Mid-phase review
- Is entity extraction working?
- Can you articulate emerging worldview?
- Which topics are most valuable?
- Adjust final 3 sessions accordingly

After 10 sessions: Phase completion
- Did core hypothesis prove true?
- What worked better than expected?
- What needs improvement?
- Update Phase 2 plan based on learnings

---

**The work of Phase 1 is not building. It's exploring. It's proving that what you built actually works for what matters.**

Let's start.
