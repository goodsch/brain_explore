# Phase 2 Plan: Layer 3 (Flow/Flo Interface)

**Status:** READY TO START
**Date:** December 2, 2025
**Prerequisite:** Phase 1 Complete ✅

---

## What Phase 1 Proved

1. **Layers 1 & 2 work flawlessly** — Knowledge graph + adaptive dialogue create genuine value
2. **Personalized dialogue surfaces novel concepts** — 11 therapeutic insights extracted from 10 sessions
3. **Complete pipeline validated** — Session → Transcript → Extraction → Formalization → Connection
4. **Core hypothesis confirmed** — Thinking partnership generates insights the person didn't have before
5. **A coherent therapeutic framework emerged** — From "Narrow Window" to "Window as Condition for Depth"

---

## What Layer 3 Is

**Flow/Flo Interface:** Interactive knowledge exploration where users engage with domain materials (books, PDFs, research) while an AI thinking partner guides the exploration based on their profile and the knowledge graph.

### Core Capabilities

1. **Non-linear reading** — Navigate knowledge graph connections instead of linear book chapters
2. **AI thinking partner** — Asks clarifying questions, surfaces unexpected connections, challenges assumptions
3. **Exploration breadcrumbs** — System documents the user's path and thinking process
4. **Insight extraction** — User generates and formalizes their own discoveries

### What It's NOT

- Not a chatbot (Layer 2 already handles dialogue)
- Not a search engine (Layer 1 already handles knowledge graph queries)
- Not a reading app (SiYuan already handles document management)

---

## Design Principles (from Phase 1 Learning)

### 1. Build on What Works

Phase 1 proved the dialogue system creates value. Layer 3 should:
- Use the same dialogue engine (IES backend)
- Use the same profile system
- Add visual navigation on top, not replace the core

### 2. Start with One Use Case

Don't build everything. Pick one:
- **Option A:** Non-linear PDF reading with graph navigation
- **Option B:** Concept exploration starting from a question
- **Option C:** Session replay with knowledge graph overlay

Recommended: **Option B** — Closest to what Phase 1 proved valuable

### 3. Minimal Viable Interface

Layer 3 is an interface, not new infrastructure:
- Backend: Already built (IES)
- Knowledge graph: Already populated (50k entities)
- Profile system: Already working

What's needed: A UI that exposes these capabilities for exploration (not just dialogue)

---

## Architecture Options

### Option 1: Extend SiYuan Plugin

**Approach:** Add exploration panels to existing plugin
**Pros:** Reuses existing codebase; integrated with notes
**Cons:** Plugin complexity already high (14k lines TS/Svelte)
**Estimate:** 30-40 hours

### Option 2: Standalone Web App

**Approach:** New React/Vue app connecting to IES backend
**Pros:** Clean slate; modern tooling; easier to iterate
**Cons:** Separate from note-taking context; new deployment
**Estimate:** 40-50 hours

### Option 3: Terminal/CLI Exploration

**Approach:** Rich terminal UI (blessed, ink, or similar)
**Pros:** Fast to build; matches current workflow; no UI framework
**Cons:** Limited visualization; text-only
**Estimate:** 15-20 hours

**Recommendation:** Start with Option 3, upgrade to Option 2 after validation

---

## Proposed Scope (MVP)

### Phase 2a: CLI Exploration Tool (15-20 hours)

Build a terminal-based exploration interface that:
1. Takes a starting question/concept
2. Queries knowledge graph for related entities
3. Displays connections and navigation options
4. Allows drilling into concepts
5. Surfaces thinking partner questions at decision points
6. Saves exploration path to markdown file

**Success criteria:**
- Can explore one concept to depth 3
- AI asks useful clarifying questions
- Path is documented and replayable
- User reports value from the exploration

### Phase 2b: Visual Interface (30-40 hours, if 2a proves value)

Upgrade to web or plugin interface:
1. Graph visualization of concept relationships
2. Click-to-navigate exploration
3. Split-pane: concept detail + graph view
4. Session history and path replay
5. Integration with SiYuan for note capture

---

## Open Design Questions

### 1. How does exploration differ from dialogue?

In Layer 2 (dialogue): User drives the conversation; AI responds adaptively
In Layer 3 (exploration): User navigates knowledge; AI surfaces connections and questions

**Question:** When does the AI speak vs. when does it just show connections?

### 2. What's the unit of exploration?

- A concept (from the 50k entities)?
- A passage (from the books)?
- A question (from the user)?
- A session (like Phase 1)?

**Question:** What does the user actually want to explore?

### 3. How does profile inform exploration?

Phase 1 proved profile-aware dialogue works. How does profile affect navigation?
- Different paths based on thinking style?
- Different questions based on preferences?
- Different depth based on engagement patterns?

**Question:** What does personalized exploration look like?

---

## Next Steps

### Immediate (This Week)

1. **Decide on initial scope** — CLI (Option 3) or web (Option 2)?
2. **Define one use case** — What specific exploration would Layer 3 enable?
3. **Sketch the interaction** — What does a 5-minute exploration session look like?

### Before Building

1. **Review IES backend API** — What endpoints exist? What's missing for exploration?
2. **Review knowledge graph structure** — How do entities connect? What's navigable?
3. **Identify Phase 1 concepts as test case** — Can we build Layer 3 navigation for the 11 therapeutic concepts?

### First Implementation

1. **CLI exploration tool** — Navigate knowledge graph from command line
2. **Thinking partner integration** — AI questions at decision points
3. **Path documentation** — Save exploration as markdown
4. **Validation session** — Run 3-5 explorations, assess value

---

## Success Criteria (Phase 2)

**Quantitative:**
- [ ] CLI tool can navigate knowledge graph
- [ ] 5 exploration sessions completed
- [ ] Each session generates at least 1 new insight
- [ ] Path documentation is reusable

**Qualitative:**
- [ ] Exploration feels different from dialogue (more agency, less conversation)
- [ ] Knowledge graph connections surface unexpected relationships
- [ ] AI questions enhance rather than interrupt exploration
- [ ] User would use this again (vs. just reading/chatting)

---

## Parking Lot (Not Phase 2)

These are explicitly deferred:
- Advanced visualization (graph rendering, analytics)
- Multi-user support
- Domain generalization (applying to non-therapy domains)
- Full PDF reading integration
- MCP server integration
- n8n workflow automation

**Rule:** Phase 2 proves Layer 3 creates value. Phase 3+ adds capabilities.

---

## Timeline Estimate

- **Phase 2a (CLI):** 15-20 hours → Validate concept
- **Phase 2b (Visual):** 30-40 hours → If 2a proves value
- **Buffer:** 10-15 hours for unexpected complexity

**Total Phase 2:** 55-75 hours over 2-3 weeks

---

**Document Status:** Draft for review
**Author:** Claude Code
**Last Updated:** December 2, 2025
