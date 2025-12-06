# IES Master Analysis Agent Plan

**Date:** 2025-12-05
**Purpose:** Systematically produce comprehensive IES documentation following Master list.md structure
**Approach:** Hybrid — verify existing docs against actual code, extend where reality differs

---

## Overview

This plan uses **dependency-ordered phases** with parallel agents within each phase to generate 28 markdown documents covering the complete IES system.

### Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Goal | Hybrid analysis | Use existing docs as reference, verify against code, extend gaps |
| Format | Markdown in git | Version controlled, developer-accessible |
| Structure | Follow Master list.md exactly | Clear mapping to original requirements |
| Execution | Dependency-ordered phases | Later docs reference earlier; reduces inconsistency |
| Output location | `docs/ies-master-analysis/{section}/` | Self-contained, mirrors Master list structure |

### Output Structure

```
docs/ies-master-analysis/
├── README.md                    # Index linking all documents
├── 0-system/
│   ├── 0.1-IES-Overview.md
│   ├── 0.2-Glossary.md
│   └── 0.3-Architecture-Diagram.md
├── 1-cognition/
│   ├── 1.1-Cognitive-Profile.md
│   ├── 1.2-Entry-Point-Theory.md
│   └── 1.3-Guided-Thinking-Patterns.md
├── 2-modes/
│   ├── 2.1-Capture-Spec.md
│   ├── 2.2-Dialogue-Spec.md
│   ├── 2.3-Flow-Spec.md
│   └── 2.4-Mode-Transition-Engine.md
├── 3-schemas/
│   ├── 3.1-Seed-Schema.md
│   ├── 3.2-Block-Schema.md
│   ├── 3.3-Notebook-Schema.md
│   └── 3.4-Entity-Graph-Schema.md
├── 4-architecture/
│   ├── 4.1-SiYuan-Structure.md
│   ├── 4.2-Backend-Pipeline.md
│   ├── 4.3-Agent-Architecture.md
│   └── 4.4-APIs-MCP-Integration.md
├── 5-visuals/
│   ├── 5.1-Graph-Visualizations.md
│   ├── 5.2-Project-AST-Maps.md
│   └── 5.3-Flow-Mode-UI.md
├── 6-audits/
│   ├── 6.1-Feature-Audit-Checklist.md
│   ├── 6.2-Failure-Modes.md
│   └── 6.3-Works-For-Chris-Checklist.md
└── 7-meta/
    ├── 7.1-Development-Roadmap.md
    ├── 7.2-Evolution-Decision-Log.md
    ├── 7.3-Testing-Protocols.md
    └── 7.4-Complete-Picture-Generator.md
```

---

## Phase 1: Foundation

**Purpose:** Establish baseline understanding that all other docs reference.

### Agent A: Overarching System Docs

**Analyzes:**
- `docs/PROJECT-OVERVIEW.md`
- `docs/SYSTEM-DESIGN.md`
- `CLAUDE.md`
- `docs/five-agent-synthesis.md`

**Produces:**

| File | Content |
|------|---------|
| `0-system/0.1-IES-Overview.md` | Mission, purpose, ADHD cognitive profile, system philosophy (ephemeral→seed→concept→notebook→graph→synthesis), three modes (Capture→Dialogue→Flow), how IES differs from traditional PKM |
| `0-system/0.2-Glossary.md` | All terms: Entity, Block, Seed, Notebook, Trellis, Dialogue mode, Flow mode, AST, User Cognition Model components, Mode Transition Engine |
| `0-system/0.3-Architecture-Diagram.md` | Mermaid diagrams covering: SiYuan block structure, plugin layer, backend processors, graph DB, model agents, Quick Capture ingestion pipeline, Mode Transition Engine |

### Agent B: Schema Docs

**Analyzes:**
- `ies/backend/src/ies_backend/schemas/`
- `.worktrees/siyuan/ies/plugin/src/types/blocks.ts`
- `docs/ARCHITECTURE-COMPARISON.md`
- `docs/IES_SiYuan_Architecture/`

**Produces:**

| File | Content |
|------|---------|
| `3-schemas/3.1-Seed-Schema.md` | Required fields, types (concept seed, question seed, analogy seed), how seeds grow into structured notes, relationships to Block and Notebook |
| `3-schemas/3.2-Block-Schema.md` | Atomic unit structure, metadata fields, relationships, processing pipeline, ephemeral→structured transformation |
| `3-schemas/3.3-Notebook-Schema.md` | Thematic/project/theory notebooks, how notebooks relate (hierarchical vs graph), auto-generation of notebook skeletons |
| `3-schemas/3.4-Entity-Graph-Schema.md` | Node types, edge types (causal, contrastive, analogical, hierarchical, emergent, procedural), how Dialogue adds edges, how Flow reads/expands graph, evidence metadata |

---

## Phase 2: Core

**Purpose:** Define the cognitive model and operational modes that make IES unique.

### Agent C: User Cognition + UX Docs

**Analyzes:**
- `.interleaved-thinking/final-answer.md`
- `docs/siyuan-exports/06-adhd-friendly-ontology-design.md`
- `docs/siyuan-exports/07-adhd-ontology-real-examples.md`
- `.worktrees/siyuan/ies/plugin/src/views/ForgeMode.svelte`

**Produces:**

| File | Content |
|------|---------|
| `1-cognition/1.1-Cognitive-Profile.md` | Core assumptions: cannot start from zero, requires contextual hooks, nonlinear/associative thinking, needs external working memory, insight through guided questioning, understanding through movement |
| `1-cognition/1.2-Entry-Point-Theory.md` | Entry point types (contextual, pattern, contrast, analogy, counterfactual, random meaningful), when to use each, how to detect which user needs in real time |
| `1-cognition/1.3-Guided-Thinking-Patterns.md` | Supported cognitive scaffolds: Socratic, CBT-style (thought→feeling→behavior), Adaptive Matrix, Counterfactual, Systems thinking loops, Concept contrast/analogy, Pattern extraction, Reframing modes |

### Agent D: Mode Specs

**Analyzes:**
- `.worktrees/siyuan/ies/plugin/src/views/ForgeMode.svelte`
- `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/`
- `ies/backend/src/ies_backend/api/session.py`
- `ies/backend/src/ies_backend/services/capture_service.py`
- `ies/backend/src/ies_backend/services/thinking_service.py`
- `ies/backend/src/ies_backend/services/flow_session_service.py`
- `docs/IES_SiYuan_Architecture/`

**Produces:**

| File | Content |
|------|---------|
| `2-modes/2.1-Capture-Spec.md` | Input channels (Quick Capture, highlights, voice, clipboard, Readest imports), metadata schema, when to process immediately vs delay, light auto-processing, Capture Inbox sidebar spec, UX for processing items into Seeds |
| `2-modes/2.2-Dialogue-Spec.md` | Purpose (guided synthesis), questioning frameworks by user cognition style, how Dialogue uses Seeds + notebooks to form Theory Blocks, visualization outputs, mode transitions into Flow, validation criteria |
| `2-modes/2.3-Flow-Spec.md` | Purpose (exploring relationships), core interactions (expand, cluster, filter, compare, pivot), visual graph requirements, AI agent roles inside Flow, Insight Events that return to Dialogue, permanent notes/concept maps/synthesis generation |
| `2-modes/2.4-Mode-Transition-Engine.md` | When system moves Capture→Dialogue, Dialogue→Flow, Flow→Dialogue, user override behavior, state machine diagrams, real transition examples from Chris's cognitive patterns |

---

## Phase 3: Technical

**Purpose:** Document implementation details — SiYuan structure, backend services, agents, visual systems.

### Agent E: Architecture/Ops Docs

**Analyzes:**
- `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts`
- `.worktrees/siyuan/ies/plugin/src/types/blocks.ts`
- `ies/backend/src/ies_backend/api/` (all routers)
- `ies/backend/src/ies_backend/services/` (all services)
- `docker-compose.yml`
- `docs/plans/` design documents

**Produces:**

| File | Content |
|------|---------|
| `4-architecture/4.1-SiYuan-Structure.md` | Complete folder tree (/System, /Seeds, /Notebooks, /Projects, /Dialogue_Sessions, /Flow_Outputs, /Research, /Imports, /Templates, /Graphs), block types, frontmatter standards, Quick Capture flow |
| `4-architecture/4.2-Backend-Pipeline.md` | Capture ingestion, summarization, classification, embedding, graph update, persistent storage, indexing — based on actual implementation |
| `4-architecture/4.3-Agent-Architecture.md` | Six agents (Sherpa, Scribe, Explorer, Interrogator, Synthesizer, Cleaner) each with: inputs, outputs, guarantees, tools, boundaries |
| `4-architecture/4.4-APIs-MCP-Integration.md` | All backend API endpoints (Quick Capture HTTP post, Claude Code CLI interaction, shell MCP usage, multi-model consultation patterns) |

### Agent F: Visual Systems Docs

**Analyzes:**
- `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/`
- `.worktrees/siyuan/ies/plugin/src/views/FlowMode.svelte`
- `docs/plans/UNIFIED-DESIGN-SYSTEM.md`
- Existing mermaid diagrams in docs

**Produces:**

| File | Content |
|------|---------|
| `5-visuals/5.1-Graph-Visualizations.md` | Seed clouds, insight trees, concept planets/orbits, dialogue question maps, temporal evolution maps, AST maps for projects |
| `5-visuals/5.2-Project-AST-Maps.md` | Goal tree, decision points, subsystems, data flows, tasks/dependencies, visual representation templates |
| `5-visuals/5.3-Flow-Mode-UI.md` | Three variations (minimalist, exploratory, node galaxy), animated transitions, examples using actual IES ideas |

---

## Phase 4: Validation

**Purpose:** Audit completeness, identify gaps, produce meta-documents for ongoing evolution.

**Note:** These agents read ALL Phase 1-3 outputs plus additional sources.

### Agent G: Audits/Checks Docs

**Analyzes:**
- All Phase 1-3 outputs
- Actual codebase state
- `docs/CRITICAL-ANALYSIS-2025-12-05.md`
- `docs/ANALYSIS-READEST-2025-12-05.md`
- `docs/PRESSURE-TEST-PLAN.md`

**Produces:**

| File | Content |
|------|---------|
| `6-audits/6.1-Feature-Audit-Checklist.md` | Every IES feature with completion status: Capture, Dialogue, Flow, Graph, Processing pipeline, Agents, AST system, Visualization, Notebook system, Question engine, Mode transition engine |
| `6-audits/6.2-Failure-Modes.md` | What happens if: processing fails, capture unclassifiable, graph gets messy, Dialogue gets stuck, Flow overwhelms user — with mitigations |
| `6-audits/6.3-Works-For-Chris-Checklist.md` | Validates against cognitive profile: avoids blank-start? handles nonlinear jumps? organizes without upfront decisions? presents entry points? Flow produces structure? Dialogue produces insight? |

### Agent H: Meta-Docs

**Analyzes:**
- All Phase 1-3 outputs
- `docs/COMPREHENSIVE-PROJECT-STATUS.md`
- `docs/STATUS-DASHBOARD.md`
- Git history

**Produces:**

| File | Content |
|------|---------|
| `7-meta/7.1-Development-Roadmap.md` | Milestones for MVP, Alpha, Beta, v1.0, Advanced modules — based on actual current state |
| `7-meta/7.2-Evolution-Decision-Log.md` | Template for tracking architectural decisions with rationale |
| `7-meta/7.3-Testing-Protocols.md` | Tests for: capture accuracy, dialogue insight generation, graph correctness, flow usability, mode transition correctness |
| `7-meta/7.4-Complete-Picture-Generator.md` | Prompt template for AI to: read all IES docs, build state summary, identify inconsistencies, recommend missing components |

---

## Execution Mechanics

### Phase Sequencing

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: Foundation (parallel)                               │
│   Agent A (System) ──┬──► Wait for both                     │
│   Agent B (Schemas) ─┘                                       │
├─────────────────────────────────────────────────────────────┤
│ PHASE 2: Core (parallel)                                     │
│   Agent C (Cognition) ──┬──► Wait for both                  │
│   Agent D (Modes) ──────┘                                    │
├─────────────────────────────────────────────────────────────┤
│ PHASE 3: Technical (parallel)                                │
│   Agent E (Architecture) ──┬──► Wait for both               │
│   Agent F (Visuals) ───────┘                                 │
├─────────────────────────────────────────────────────────────┤
│ PHASE 4: Validation (parallel)                               │
│   Agent G (Audits) ──┬──► Wait for both                     │
│   Agent H (Meta) ────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

### Agent Configuration

Each agent uses:
- `Task` tool with `subagent_type="Explore"` for analysis or `subagent_type="general-purpose"` for generation
- Specific file paths to analyze
- Output file paths to write
- Reference to Master list.md section requirements
- Instructions to verify claims against actual code

### Quality Gates

After each phase:
1. Verify all expected output files exist
2. Spot-check content for reasonable depth
3. Re-run failed agents before proceeding
4. Optional: User review before next phase

### Deliverables

- 28 markdown documents in `docs/ies-master-analysis/`
- Index file `docs/ies-master-analysis/README.md` linking all documents
- Git commit with clear message after each phase

---

## Document Requirements

Each document should:

1. **Start with purpose** — What question does this document answer?
2. **Reference actual code** — Include file paths and line numbers where relevant
3. **Use Mermaid diagrams** — For architecture, flows, state machines
4. **Include examples** — Real examples from the IES codebase, not hypotheticals
5. **Note gaps explicitly** — If something is designed but not implemented, say so
6. **Cross-reference** — Link to related documents in the analysis set

---

## Success Criteria

The analysis is complete when:

- [ ] All 28 documents exist with substantive content
- [ ] Each document cites actual code/config, not just conceptual descriptions
- [ ] Mermaid diagrams render correctly
- [ ] Cross-references between documents are valid
- [ ] Feature Audit (6.1) accurately reflects implementation state
- [ ] "Works for Chris" checklist (6.3) has no false positives
- [ ] README.md provides clear navigation to all documents
