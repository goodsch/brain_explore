# IES Architecture Comparison: Proposed vs. Current Implementation

**Purpose:** Compare the new IES SiYuan Architecture Package against our current implementation to identify alignment, gaps, and improvement opportunities.
**Created:** December 5, 2025

---

## Executive Summary

The **IES SiYuan Architecture Package** proposes a comprehensive, AI-assistant-centric knowledge management system with rich block-level schemas and explicit data flows. Our **current implementation** is a four-layer system focused on reading-and-exploration integration with backend APIs.

**Key Finding:** The two architectures are **complementary, not competing**. The Architecture Package provides the **SiYuan document structure** we've been missing (Gap #1 in SYSTEM-DESIGN.md), while our implementation provides the **backend intelligence and cross-app integration** the Package assumes but doesn't define.

---

## Architecture Overview Comparison

### Proposed Architecture Package

```
IES × SiYuan Architecture Package
├── 00_Inbox/         → Ephemeral capture, raw input
├── 01_Seedlings/     → Atomic ideas, observations, questions
├── 02_Shaping/       → Dialogue-mode guided questioning
├── 03_Flow_Maps/     → Graph-like exploration and maps
├── 04_Concepts/      → Canonical concept pages (knowledge graph)
├── 05_Projects/      → Project structures, plans, decisions
├── 06_Archive/       → Retired/superseded material
└── 07_System/        → Templates, schemas, directives
```

**Philosophy:** Notes are primarily created/edited by AI assistant; human is the reader/explorer.

### Current Implementation

```
Four-Layer Architecture
├── Layer 4: Readest      → Reading Interface (book-centric exploration)
├── Layer 3: SiYuan       → Processing Hub (dashboard, ForgeMode, QuickCapture)
├── Layer 2: Backend      → APIs (graph, books, reframes, templates, personal, sessions)
└── Layer 1: Knowledge    → Neo4j domain graph + ADHD personal graph
```

**Philosophy:** Think WITH an AI partner who adapts to your cognitive patterns.

---

## Folder Structure Comparison

| Package Structure | Current Structure | Alignment |
|------------------|-------------------|-----------|
| `00_Inbox/` | `/Daily/` (in specs) | Partial - different naming |
| `01_Seedlings/` | Not implemented | **GAP** |
| `02_Shaping/` | `/Sessions/{mode}/` | Similar purpose |
| `03_Flow_Maps/` | `/Threads/` | Similar purpose |
| `04_Concepts/` | `/Concepts/` | **Aligned** |
| `05_Projects/` | Not in current spec | **GAP** |
| `06_Archive/` | Not in current spec | **GAP** |
| `07_System/` | N/A (in CLAUDE.md) | Different approach |

### Current SiYuan Structure (from siyuan-structure.ts)

```
/Daily/              → Zero-friction daily capture
/Insights/           → Promoted sparks
/Threads/            → Exploration paths
/Favorite Problems/  → Anchor questions
/Concepts/           → Formalized concepts
/Sessions/{mode}/    → Learning, Articulating, Planning, Ideating, Reflecting
```

---

## Block Schema Comparison

### Proposed Package: 7 Block Types

| Block Type | Purpose | Current Equivalent |
|------------|---------|-------------------|
| `seed-block` | Atomic idea | `spark` in ADHD ontology |
| `shaping-block` | Dialogue segment | Session transcript |
| `map-block` | Visual maps/diagrams | Not implemented |
| `concept-block` | Canonical concept | Domain entity |
| `decision-block` | Project decision | Not implemented |
| `log-entry-block` | Actions/events | Not implemented |
| Quick Capture | Raw input | `spark` with resonance |

### Current Implementation: Entity Types

**Domain Knowledge (from books):**
```
concept | framework | theory | mechanism | phenomenon |
pattern | distinction | person | book | assessment
```

**Personal Knowledge (ADHD ontology):**
```
spark | insight | thread | favorite_problem
```

### Key Differences

1. **Package has richer block semantics** - explicit `map-block`, `decision-block`, `log-entry-block`
2. **Current has richer personal metadata** - `resonance_signal`, `energy_level`, `exploration_visits`
3. **Package uses YAML frontmatter** - Current uses SiYuan block attributes
4. **Package assumes AI fills metadata** - Current collects from user interaction

---

## Quick Capture Comparison

### Package Quick Capture Schema

```yaml
quick_capture: true
capture_channel: phone|readest|web|voice|other
capture_source: ios_shortcut|readest|browser_extension|mcp_tool|manual
capture_time: ISO timestamp
capture_status: raw|classified|processed
auto_summary: string|null
auto_labels: []
linked_concepts: []
```

**Lifecycle:** `raw → classified → processed`

### Current Personal Graph Schema

```python
resonance_signal: curious|excited|surprised|moved|disturbed|unclear|connected|validated
energy_level: low|medium|high
status: captured|exploring|anchored
capture_context: string
exploration_visits: integer
```

**Lifecycle:** `captured → exploring → anchored`

### Alignment Assessment

| Feature | Package | Current | Winner |
|---------|---------|---------|--------|
| Capture channels | Explicit enum | Implicit | Package |
| Status lifecycle | 3 stages | 3 stages | Tie |
| Auto-processing | AI summarizes/labels | Entity extraction | Package broader |
| Emotional metadata | None | 8 resonance signals | **Current** |
| Energy-based navigation | None | 3 energy levels | **Current** |
| Visit tracking | None | `exploration_visits` | **Current** |
| AI behavior boundaries | Explicit | Implicit | Package |

---

## Data Flow Comparison

### Package Flow (Linear with branches)

```
Capture → 00_Inbox → 01_Seedlings → 02_Shaping → 03_Flow_Maps → 04_Concepts → 05_Projects → 06_Archive
                          ↓              ↓             ↓              ↓
                      04_Concepts    04_Concepts   05_Projects    05_Projects
```

### Current Flow (Four-layer with feedback)

```
Layer 4 (Readest)           Layer 3 (SiYuan)
      ↓                           ↓
      └──────── Layer 2 (Backend APIs) ────────┘
                      ↓
              Layer 1 (Neo4j + Personal Graph)
                      ↓
              Feedback to Layers 3/4
```

### Key Difference

**Package:** Content moves through folders with AI transformation
**Current:** Content flows between apps via APIs with graph enrichment

---

## Thinking Modes Comparison

### Package Modes (5)

| Mode | Folder | Purpose |
|------|--------|---------|
| Capture | 00_Inbox | Raw input |
| Dialogue | 02_Shaping | Guided questioning |
| Flow | 03_Flow_Maps | Non-linear exploration |
| Synthesis | 04_Concepts, 05_Projects | Consolidation |
| Archive | 06_Archive | Retirement |

### Current Modes (5 in ForgeMode)

| Mode | Template | Purpose |
|------|----------|---------|
| Learning | mechanism-map | Understand new concept |
| Articulating | clarify-intuition | Clarify vague thoughts |
| Planning | (planned) | Develop action strategy |
| Ideating | (planned) | Generate creative options |
| Reflecting | (planned) | Personal insight |

### Current Modes (4 in AST specification)

| Mode | Purpose |
|------|---------|
| Discovery | Schema surfacing (fast capture) |
| Dialogue | Model building |
| Flow | Associative browsing |
| AST | Structured templates |

### Alignment

- Both have ~5 modes
- Package modes are **location-based** (which folder)
- Current modes are **behavior-based** (AI questioning style)
- Current has richer **question class taxonomy** (9 classes)

---

## Question Engine Comparison

### Package Approach

No explicit question engine. Questions emerge from AI directives:
- Challenge/reframe in Shaping
- Entry point summaries in all sessions
- Next-step suggestions

### Current Approach

**9 Question Classes:**
1. Schema-Probe (hidden structure)
2. Boundary (edges/limits)
3. Dimensional (spectra/coordinates)
4. Causal (mechanisms)
5. Counterfactual (what-if)
6. Anchor (concrete instances)
7. Perspective-Shift (viewpoint changes)
8. Meta-Cognitive (thinking patterns)
9. Reflective-Synthesis (integration)

**Mode Transition Engine:** Watches interaction patterns, proposes mode switches.

### Assessment

**Current implementation is significantly richer** in question generation and cognitive scaffolding.

---

## AI Behavior Directives

### Package Explicit Rules

1. **Atomicity** - 1 idea → 1 block
2. **Reference, don't duplicate** - Use block references
3. **Always create entry points** - Summary + next links
4. **Mode-awareness** - Respect folder locations
5. **Human-first readability** - Write for future-Chris

### Package Prohibited Actions (for Quick Capture)

- Don't move blocks automatically
- Don't split into Seedlings automatically
- Don't attach to Projects/Concepts without interaction

### Current Approach

Less explicit. AI behavior defined in:
- Template AI behavior specifications
- Question Engine approach selection
- Session API orchestration

### Recommendation

**Adopt Package's explicit directive model** - clearer boundaries prevent AI overreach.

---

## What Package Has That We Need

### 1. Seedlings Folder Structure

**Gap:** We don't have a place for atomic ideas that aren't yet insights.

**Package provides:**
```
01_Seedlings/
├── Questions/
├── Insights/
├── Observations/
├── Moments/
├── Schemas/
├── Contradictions/
└── What_Ifs/
```

**Recommendation:** Add `01_Seedlings/` subfolder structure to current `/Daily/` or create separate seedling space.

### 2. Decision and Log Block Types

**Gap:** No explicit tracking for decisions made or events logged.

**Package provides:**
- `decision-block` with status (pending/accepted/rejected/revisited)
- `log-entry-block` for actions and events

**Recommendation:** Add these block types to session output.

### 3. Explicit Archive Strategy

**Gap:** No defined retirement process.

**Package provides:**
- `06_Archive/` folder
- Explicit `archived_on`, `reason` metadata
- AI-only moves to archive

**Recommendation:** Add archive folder and archival workflow.

### 4. AI Behavior Boundaries

**Gap:** Our AI behavior is implicit in code.

**Package provides:**
- Explicit "may do" and "may not do" lists
- Background vs interactive processing distinction
- Health check protocols

**Recommendation:** Document explicit AI boundaries in SiYuan plugin.

---

## What We Have That Package Needs

### 1. Backend API Layer

**Package assumes:** MCP or similar for AI operations
**We provide:** Complete REST API with 85/85 tests

### 2. Book/Reading Integration

**Package assumes:** External capture from Readest
**We provide:** Full Calibre integration, entity overlay, Flow panel

### 3. ADHD-Friendly Personal Graph

**Package has:** Generic capture status
**We provide:** Resonance signals, energy levels, visit tracking

### 4. Question Engine

**Package has:** Implicit AI questioning
**We provide:** 9 question classes, mode transition engine, profile-adapted questions

### 5. Cross-App Integration

**Package is:** SiYuan-only
**We provide:** Readest ↔ SiYuan (designed, partially implemented)

---

## Integration Recommendations

### 1. Adopt Package Folder Structure (with modifications)

```
PROPOSED MERGED STRUCTURE:
├── Daily/              → Quick captures (Package's 00_Inbox)
├── Seedlings/          → From Package (new)
│   ├── Questions/
│   ├── Observations/
│   ├── Moments/
│   ├── Schemas/
│   └── What_Ifs/
├── Sessions/           → Current (Package's 02_Shaping)
│   ├── Learning/
│   ├── Articulating/
│   ├── Planning/
│   ├── Ideating/
│   └── Reflecting/
├── Flow_Maps/          → Package's 03_Flow_Maps (rename from Threads)
├── Concepts/           → Both agree
├── Insights/           → Current (elevated Seedlings)
├── Favorite_Problems/  → Current (ADHD anchor points)
├── Projects/           → Package's 05_Projects (new)
└── Archive/            → Package's 06_Archive (new)
```

### 2. Adopt Package Block Schemas (with ADHD extensions)

```yaml
# Merged seed-block schema
block_type: seed
idea_type: question|insight|observation|moment|schema|contradiction|what_if

# Package fields
domain: string
clarity: fuzzy|partial|clear
confidence: low|medium|high

# ADHD extensions (current)
resonance_signal: curious|excited|surprised|moved|disturbed|unclear|connected|validated
energy_level: low|medium|high
exploration_visits: integer
```

### 3. Adopt Package Quick Capture Schema (with backend linkage)

```yaml
# Package fields
quick_capture: true
capture_channel: phone|readest|web|voice|other
capture_source: ios_shortcut|readest|browser_extension|mcp_tool|manual
capture_time: ISO timestamp
capture_status: raw|classified|processed

# Current backend linkage
be_id: string         # Backend entity ID
be_type: spark|insight
linked_concepts: []   # From knowledge graph
```

### 4. Adopt Package AI Directives

Document in SiYuan plugin:
- What AI may do automatically
- What requires user interaction
- Health check protocols

### 5. Keep Current Backend + Question Engine

Package assumes external AI - we provide it via:
- Backend APIs (graph, reframes, templates, personal)
- Question Engine (9 classes)
- Mode Transition Engine

---

## Implementation Priority

### Phase 1: Document Structure (Addresses Gap #1)

1. Create `Seedlings/` folder structure
2. Create `Projects/` folder structure
3. Create `Archive/` folder structure
4. Update `createSessionDocument()` to use new paths

### Phase 2: Block Schema Merge

1. Update block attributes to include Package fields
2. Add ADHD extensions to Package schema
3. Update ForgeMode to generate merged schema

### Phase 3: Quick Capture Enhancement

1. Implement capture_channel detection
2. Add auto_summary and auto_labels via backend
3. Implement explicit processed/classified states
4. Add AI behavior boundary enforcement

### Phase 4: Archive and Health Checks

1. Implement archive workflow
2. Add health check periodic scans
3. Surface orphan/stale content alerts

---

## Conclusion

The IES SiYuan Architecture Package provides an excellent **document-level structure** that complements our **infrastructure-level implementation**. Merging them creates:

1. **Clear folder hierarchy** for where content lives
2. **Rich block semantics** for what content means
3. **Explicit AI boundaries** for how AI behaves
4. **Backend integration** for cross-app intelligence
5. **ADHD-friendly metadata** for emotional and energy-based navigation

**Recommended next step:** Implement Phase 1 (Document Structure) to address the critical Gap #1 identified in SYSTEM-DESIGN.md.

---

*Document created: December 5, 2025*
*Source materials: IES_SiYuan_Architecture_Package_QuickCaptureUpdated, docs/SYSTEM-DESIGN.md*
