# Master Plan: Multi-Agent Analysis of Brain Dump & Project Recovery

**Date:** 2025-12-02
**Objective:** Create a systematic analysis of the brain dump, interconnected projects (brain_explore + Synapse), and configuration system to identify the core vision and create a focused recovery path.

**Overall Goal:** Extract the ephemeral vision that keeps emerging across projects, understand why projects bloat, and design a lean, focused architecture that serves the actual goals.

---

## Part 1: Understanding the Core Vision

### What I'm Hearing (Meta-Pattern Analysis)

From your brain dump, there's a consistent thread across all your projects:

**The Core Question You're Trying to Answer:**
> How can I help people understand *how they think* and *how they see the world* so they can achieve meaningful change?

**Three Manifestations:**

1. **Flow Mode** — Non-linear reading through knowledge graphs with AI documentation
   - Problem it solves: Linear reading doesn't match how people naturally make connections
   - Goal: "Flow through connections while AI documents your learning"

2. **Self-Understanding Layer** — Accessible identification of thinking patterns
   - Problem it solves: People don't recognize their own unique thinking/worldviews
   - Goal: "Find novel ways to identify thinking patterns, then approach from there"

3. **Therapeutic Conversation System** — Right questions + understanding patterns
   - Problem it solves: You need to understand how they think to ask effective questions
   - Goal: "Identify aspects of how they think/process so you can ask better questions"

**The Pattern:** You're building a *meta-cognitive exploration system* that combines knowledge navigation + thinking pattern identification + therapeutic dialogue.

**Why Projects Get Bloated:**
Your description is key: *"The way my brain works is to connect concepts... I'll see something we're implementing that gives ideas or makes it seem like it'd be useful to do other things."*

This isn't a weakness—it's your superpower. But without architecture that channels it, you get bloat. Each new connection gets added to the current project instead of being a separate module you can pull in later.

---

## Part 2: The Interconnected Projects

### brain_explore (Current)

**Status:** Production-ready infrastructure (IES backend + SiYuan plugin) + bloated configuration system

**What's Working:**
- Backend API (4,496 lines, 61 tests, fully functional)
- SiYuan plugin (14,092 lines TypeScript/Svelte)
- Neo4j + Qdrant infrastructure
- Entity extraction + graph model for therapy concepts

**What's Broken:**
- 96% infrastructure, 4% actual usage (tool-building before tool-using)
- Configuration system is ADHD-hostile despite being built for ADHD user
- Three-layer framework abstraction (IES → Framework → Therapy) exists only in docs
- Never actually explored therapy worldview using the tool

**Your Ideas for This Project:**
1. MCP server integration (connect to Claude app for voice)
2. n8n integration (alternative MCP implementation)
3. Flow Mode reading capabilities (non-linear knowledge navigation)
4. Self-understanding identification layer (how do they think/process?)
5. Advanced therapeutic conversation modes

---

### Synapse (Abandoned/Parallel)

**Status:** Similar goals, different implementation (needs analysis)

**Your Mention:** "I don't know if we ever got their book"

**Question:** Does Synapse contain:
- Flow Mode concept further developed?
- Different approaches to the same goals?
- Literature/book integration code?
- Session history showing why it was abandoned?

---

## Part 3: Agent Analysis Plan

I'm proposing a **team of 5 specialized agents** working in parallel on independent investigations:

### Team Composition & Assignments

**Agent 1: Vision Extraction Specialist**
- **Task:** Deep analysis of all session history (@claude-prompts/) + brain dump
- **Goal:** Extract the core vision that keeps emerging
- **Deliverable:** "True Vision Document" - what you're actually trying to build (not what you said you'd build)
- **Key Questions:**
  - What appears in multiple projects?
  - What keeps pulling your focus?
  - What does "helping someone understand how they think" actually mean architecturally?
  - How do Flow Mode, self-understanding, and therapeutic dialogue interconnect?

**Agent 2: SiYuan Knowledge Graph Analyst**
- **Task:** Deep dive into all three SiYuan notebooks (IES, Framework, Therapy)
- **Goal:** Understand what concepts/structures you've been documenting
- **Deliverable:** "Knowledge Architecture Report"
  - Current entity schema
  - Therapeutic concepts being captured
  - Gaps between documentation and code
  - How notebooks reflect the real project vs. aspirational project

**Agent 3: Synapse Project Archaeologist**
- **Task:** Analyze `/home/chris/dev/projects/claude/synapse` (if it exists)
- **Goal:** Understand what was tried, why it was abandoned, what insights remain
- **Deliverable:** "Synapse Autopsy Report"
  - Core vision in Synapse
  - How it differs from brain_explore
  - What code/ideas are reusable
  - Why it was abandoned (blockers? pivoted?)
  - Flow Mode development level

**Agent 4: Configuration Impact Auditor** (supplementary to existing critique)
- **Task:** Map exactly how configuration bloat cascaded across sessions
- **Goal:** Understand when configuration system became the primary work
- **Deliverable:** "Configuration Timeline"
  - When was active-project introduced?
  - What problems did it create immediately vs. over time?
  - How did 4 CLAUDE.md files emerge?
  - Session velocity impact (session length + focus ratio over time)

**Agent 5: Reference Architecture Synthesizer**
- **Task:** Analyze @ccref repos + reference projects for patterns
- **Goal:** Understand what configuration/architecture patterns work for multi-faceted projects
- **Deliverable:** "Synthesis Report"
  - How do successful projects structure multi-concept work?
  - MCP patterns that could serve IES
  - Integration patterns (n8n, voice, etc.)
  - Configuration anti-patterns to avoid

---

## Part 4: Follow-Up Questions Before Dispatch

Before I send these agents to work, I need clarifications:

**Question 1: Synapse Location**
The Synapse project you mention — where is it? I see references in the working directories:
- `/home/chris/dev/projects/claude/synapse` (from CLAUDE.md)?
- Or elsewhere?

**Question 2: SiYuan Notebooks Access**
You mentioned "Create a team of specialized agents to perform in depth meta analysis of the SiYuan notebooks."

Are the notebooks:
- Exportable to markdown files that agents can read?
- Accessible via SiYuan API/MCP tools?
- Or should agents focus on the session history that references them?

**Question 3: The "Book" You Mention**
"With the synapse project, I don't know if we ever got their book."

Are you referring to:
- A specific book that was supposed to be integrated?
- A foundational text for understanding your vision?
- Or something else?

**Question 4: Priority of New Features vs. Recovery**
The ideas you mentioned (MCP server, n8n, Flow Mode, self-understanding layer):

Should agents:
- **A)** Analyze how these *should* be integrated once core system is healthy
- **B)** Analyze whether any of these are actually MVPs that unblock the rest
- **C)** Focus analysis only on recovery, defer feature analysis

**Question 5: Scope of "Brain Dump" Analysis**
You want agents to understand "what I'm trying to accomplish" across projects.

Should analysis:
- **A)** Be limited to what's documented (session history, code)
- **B)** Include interpretation of implicit goals (inferring from patterns)
- **C)** Both

---

## Part 5: Proposed Analysis Timeline

**If you answer the clarification questions, I would dispatch agents in this sequence:**

### Wave 1 (Parallel - Independent)
- Agent 1: Vision Extraction (reads all session history)
- Agent 3: Synapse Archaeologist (analyzes parallel project)
- Agent 5: Reference Architecture (analyzes @ccref)

### Wave 2 (After Wave 1 completes)
- Agent 2: SiYuan Analyst (uses Vision Extraction findings to focus analysis)
- Agent 4: Configuration Auditor (uses Vision Extraction to identify key inflection points)

### Wave 3 (Integration)
- Synthesize all reports
- Identify core vision + validation of interconnected concepts
- Create "True State Document" of what you're actually building
- Design recovery path based on real goals (not aspirational configuration)

---

## Part 6: Expected Deliverables

After all agents complete:

1. **True Vision Document** — The actual problem you're solving (extracted from implicit patterns)
2. **Knowledge Architecture Report** — What the system should actually store/track
3. **Synapse Autopsy** — Ideas/code worth salvaging, lessons from why it was abandoned
4. **Configuration Timeline** — How/when meta-work eclipsed actual work
5. **Synthesis Report** — Proven patterns from reference projects
6. **Master Integration Plan** — How these five insights compose into recovery strategy

Then we move to **Design Phase**:
- Design the lean core architecture for your actual goals
- Design the expansion points where Flow Mode, self-understanding, MCP integration fit
- Create implementation plan with sequencing

---

## Next Step: Your Response

Please answer the five clarification questions above, and I'll dispatch the agent team immediately.

**Expected timeline:**
- Agent analysis: 30-45 minutes (all teams running parallel)
- Synthesis: 15-20 minutes
- Then we move to design phase with full clarity on what you're building

Sound good?
