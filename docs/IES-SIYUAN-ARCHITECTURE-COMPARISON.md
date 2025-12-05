# IES SiYuan Architecture Comparison

**Created:** 2025-12-05
**Purpose:** Compare current SiYuan plugin implementation with new IES Architecture Package

---

## Executive Summary

The new **IES SiYuan Architecture Package** introduces a comprehensive 7-layer folder structure with formal block schemas, a Quick Capture system with lifecycle management, and explicit AI behavior boundaries. This represents a significant evolution from the current implementation's simpler spark-based model.

**Key Shift:** From emotional resonance capture (sparks) to cognitive atomic units (seedlings) with structured processing workflows.

---

## Current Implementation

**Source:** `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts`

### Folder Structure (6 folders)

```
/Daily/                    # Daily log entries (sparks land here)
/Insights/                 # Promoted insights from sparks
/Threads/                  # Active exploration threads
/Favorite Problems/        # Anchor questions (Feynman-inspired)
/Concepts/                 # Formalized concepts
/Sessions/                 # AST session documents
  ├── Learning/
  ├── Articulating/
  ├── Planning/
  ├── Ideating/
  └── Reflecting/
```

### Block Types (3 types)

| Type | Purpose | Key Metadata |
|------|---------|--------------|
| `spark` | Raw resonance capture | `resonance_signal`, `energy_level`, `status` |
| `insight` | Promoted spark | `status: anchored` |
| `session` | ForgeMode thinking session | `mode`, `template_id`, `question_classes_used` |

### Features

- **Backend Integration:** `/personal/sparks` API for CRUD operations
- **Energy Levels:** low/medium/high for ADHD-friendly mood-based navigation
- **Resonance Signals:** 8 types (curious, excited, surprised, moved, disturbed, unclear, connected, validated)
- **Question Classes:** 9 types from Question Engine (schema_probe, boundary, causal, etc.)
- **Session Documents:** Full transcript with frontmatter, section responses, thinking dialogues

### Workflow

```
User captures thought
    ↓
createSparkWithBackend() → /Daily/{date}.md + Backend API
    ↓
promoteToInsight() → Move to /Insights/ + Update status
```

---

## New Architecture Package

**Source:** `IES_SiYuan_Architecture_Package_QuickCaptureUpdated/`

### Folder Structure (7 layers + subfolders)

```
/00_Inbox/                     # Ephemeral capture, raw input
    └── QuickCapture_YYYY-MM-DD.md

/01_Seedlings/                 # Atomic ideas (1 idea = 1 seed-block)
    ├── Observations/          # What I noticed
    ├── Questions/             # What I'm wondering
    ├── Contradictions/        # What doesn't fit
    ├── What_Ifs/              # Speculative ideas
    ├── Insights/              # Aha moments
    ├── Moments/               # Significant experiences
    └── Schemas/               # Mental model fragments

/02_Shaping/                   # Dialogue-mode guided questioning
    ├── Dialogue_Sessions/     # AI-guided exploration
    ├── Cognitive_Excavations/ # Deep dives into thinking
    ├── Internal_Models/       # Explicit mental models
    └── Mini_Syntheses/        # Small integration pieces

/03_Flow_Maps/                 # Non-linear exploration
    ├── Perspectives/          # Viewpoint maps
    ├── Concept_Maps/          # Relationship diagrams
    ├── Systems/               # System views
    ├── Schemas/               # Schema diagrams
    └── Timelines/             # Temporal views

/04_Concepts/                  # Canonical knowledge graph
    ├── IES/                   # System concepts
    ├── Emotion/               # Emotional concepts
    ├── Cognition/             # Cognitive concepts
    ├── ADHD/                  # ADHD-specific
    ├── Therapy/               # Therapeutic concepts
    ├── Self/                  # Self-understanding
    ├── Motivation/            # Motivation & drive
    ├── Other_People/          # Relationships
    ├── Environment/           # Context & setting
    ├── Tools/                 # Methods & tools
    └── Systems/               # Systems thinking

/05_Projects/                  # Active work structures
    └── {Project_Name}/
        ├── README.md          # Project overview
        ├── Goals.md           # What we're trying to achieve
        ├── Questions.md       # Open questions
        ├── Plan.md            # Action plan
        ├── Status.md          # Current state
        ├── Decisions.md       # Key decisions made
        ├── Research.md        # Background research
        ├── Maps.md            # Project-specific maps
        └── Logs.md            # Activity log

/06_Archive/                   # Retired/superseded material
    └── {archived items with reason + date}

/07_System/                    # Meta-layer (templates, schemas, directives)
    ├── Templates/
    ├── Example_Notes/
    ├── Block_Schemas.md
    ├── Quick_Capture_Schema.md
    ├── AI_Assistant_Directives.md
    ├── IES_SiYuan_Dataflow.md
    └── System_Architecture_Diagram.md
```

### Block Schemas (6 types)

#### 1. `seed-block` — Atomic idea unit

```yaml
block_type: seed
idea_type: <question|insight|observation|moment|schema|contradiction|what_if|other>
domain: <ADHD|Therapy|Self|Systems|Cognition|Emotion|...>
source: <inbox|dialogue|project|external>
clarity: <fuzzy|partial|clear>
confidence: <low|medium|high>
created_at: <ISO timestamp>
last_touched_at: <ISO timestamp>
related_concepts: []
tags: []
```

#### 2. `shaping-block` — Dialogue segment

```yaml
block_type: shaping
session_id: <uuid-or-date-based-id>
speaker: <chris|ai>
phase: <exploration|challenge|synthesis|meta>
related_seedlings: []
created_at: <ISO timestamp>
last_touched_at: <ISO timestamp>
```

#### 3. `map-block` — Visual representation

```yaml
block_type: map
map_type: <concept_cluster|timeline|system|schema|perspective|other>
focus: <primary concept or question>
related_concepts: []
related_seedlings: []
entry_points: []
created_at: <ISO timestamp>
last_touched_at: <ISO timestamp>
```

#### 4. `concept-block` — Canonical definition

```yaml
block_type: concept
concept_id: <slug>
concept_name: <Name>
domain: <Cognition|Emotion|Motivation|Self|...>
status: <active|draft|deprecated>
created_at: <ISO timestamp>
last_touched_at: <ISO timestamp>
version: 1
```

#### 5. `decision-block` — Project decision

```yaml
block_type: decision
project_id: <project name or ID>
status: <pending|accepted|rejected|revisited>
rationale: <short summary>
created_at: <ISO timestamp>
decided_at: <ISO timestamp>
related_maps: []
related_concepts: []
```

#### 6. `log-entry-block` — Activity record

```yaml
block_type: log_entry
context: <project|system|personal>
project_id: <optional>
timestamp: <ISO timestamp>
summary: <what happened>
related_blocks: []
```

### Quick Capture System

**The defining new feature** — blocks captured with minimal friction that may not have clear context yet.

#### Schema

```yaml
# Core fields (required)
quick_capture: true
capture_channel: <phone|readest|web|voice|other>
capture_source: <ios_shortcut|readest|browser_extension|mcp_tool|manual|other>
capture_time: <ISO timestamp>
capture_status: <raw|classified|processed>

# AI-populated fields (optional)
auto_summary: <string|null>
auto_labels: []
linked_concepts: []

# Book/highlight captures (optional)
book_title: <string>
book_author: <string>
location: <page/chapter>
highlight_id: <string>
entities: []
```

#### Status Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                     CAPTURE STATUS LIFECYCLE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   RAW                CLASSIFIED              PROCESSED          │
│    │                     │                       │              │
│    │  AI background      │  User interactive    │              │
│    │  processing         │  decision            │              │
│    ▼                     ▼                       ▼              │
│  ┌───┐   auto_summary  ┌───┐   Create seeds   ┌───┐           │
│  │ R │ ───────────────▶│ C │ ────────────────▶│ P │           │
│  │ A │   auto_labels   │ L │   Link concepts  │ R │           │
│  │ W │   linked_       │ A │   Attach to      │ O │           │
│  └───┘   concepts      │ S │   projects       │ C │           │
│                        │ S │                  │ E │           │
│  Just landed,          └───┘                  │ S │           │
│  no AI work                                   │ S │           │
│                        AI has safely          │ E │           │
│                        added metadata         │ D │           │
│                                               └───┘           │
│                                                                 │
│                                               User decided      │
│                                               what to do        │
└─────────────────────────────────────────────────────────────────┘
```

#### AI Behavior Boundaries

| Action | Allowed Automatically | Requires Interactive Command |
|--------|----------------------|------------------------------|
| Add `auto_summary` | ✅ | |
| Add `auto_labels` | ✅ | |
| Add `linked_concepts` (when obvious) | ✅ | |
| Move `raw` → `classified` | ✅ | |
| Move block to new file | | ✅ |
| Split into Seedlings | | ✅ |
| Attach to Project | | ✅ |
| Attach to Concept page | | ✅ |
| Mark as `processed` | | ✅ |

### Templates

#### Seedling Template

```markdown
# TEMPLATE: Seedling

> One atomic idea, question, observation, or schema fragment.

## Seed

Write the atomic idea here in a single short paragraph or bullet.

- It should stand alone.
- Avoid mixing multiple ideas.
```

#### Concept Page Template

```markdown
# TEMPLATE: Concept Page

## 1. Working Definition
How Chris currently understands this concept.

## 2. Core Dimensions / Properties
- Dimension 1:
- Dimension 2:

## 3. How This Shows Up
- In Chris's life:
- In clients:
- In systems:

## 4. Related Concepts
- Closely related:
- Often confused with:
- Depends on:
- Influences:

## 5. Examples & Vignettes

## 6. Common Pitfalls / Misunderstandings

## 7. Links & References
- Seedlings:
- Dialogue sessions:
- Flow Maps:
- Projects:

## 8. Changelog
- `YYYY-MM-DD` — summary of change.
```

#### Dialogue Session Template

```markdown
# TEMPLATE: Dialogue Session

## 1. Context / Setup
- What are we exploring?
- Which Seedlings or concepts prompted this?

## 2. Exploration Phase
(Alternate AI/human turns)

## 3. Challenge / Reframe Phase
- Alternative framings
- Mark turning points explicitly

## 4. Synthesis Phase
- What changed in understanding
- New or updated Seedlings

## 5. Next Steps
- Concept pages to update/create
- Flow Maps to build/revise
- Project implications
```

#### Flow Map Template

```markdown
# TEMPLATE: Flow Map

## 1. How to Read This Map
Explain in 2–4 sentences.

## 2. Diagram
(Mermaid or visual format)

## 3. Key Nodes
- **Node A:** summary + links
- **Node B:** summary + links

## 4. Entry Points
- Start at [Node A] if you are interested in …
- Start at [Node B] if you are curious about …

## 5. References
- Seedlings:
- Dialogue sessions:
- Concept pages:
- Projects:
```

---

## Comparison Matrix

| Aspect | Current Implementation | New Architecture |
|--------|------------------------|------------------|
| **Primary metaphor** | Sparks → Insights (emotional) | Captures → Seedlings → Concepts (cognitive) |
| **Capture location** | `/Daily/` log | `/00_Inbox/` queue |
| **Atomic unit** | Spark (energy + resonance) | Seed-block (clarity + confidence) |
| **Processing model** | Backend-first (API calls) | SiYuan-first with AI classification |
| **Folder structure** | Flat (6 folders) | Hierarchical (7 layers + subfolders) |
| **Block types** | 3 informal | 6 formal schemas |
| **Quick Capture** | Implicit (sparks) | Explicit system with lifecycle |
| **Capture status** | `captured → anchored` | `raw → classified → processed` |
| **Dialogue sessions** | `/Sessions/{mode}/` | `/02_Shaping/Dialogue_Sessions/` |
| **Visual maps** | Not structured | `/03_Flow_Maps/` with 5 types |
| **Projects** | Not implemented | Full 8-page structure |
| **Archive** | Not implemented | `/06_Archive/` with reasons |
| **Templates** | JSON backend templates | Markdown in `/07_System/Templates/` |
| **AI boundaries** | Implicit | Explicit allowed/prohibited actions |
| **Domain taxonomy** | Via backend | 11 concept domains in folder structure |

---

## Data Flow Comparison

### Current Flow

```
External Input (Readest, manual)
    ↓
createSparkWithBackend()
    ↓
┌─────────────────────────────┐
│  Backend API + SiYuan Block │
│  /Daily/{date}.md           │
└─────────────────────────────┘
    ↓
promoteToInsight()
    ↓
┌─────────────────────────────┐
│  /Insights/                 │
│  status: anchored           │
└─────────────────────────────┘
```

### New Architecture Flow

```
External Input (Shortcuts, MCP, Voice, Apps)
    ↓
┌──────────────────┐
│  00_Inbox        │  quick_capture: true, capture_status: raw
└────────┬─────────┘
         │ AI background processing
         ▼
┌──────────────────┐
│  00_Inbox        │  capture_status: classified
│  (auto_summary,  │  (auto_labels, linked_concepts)
│   auto_labels)   │
└────────┬─────────┘
         │ Interactive "Process this capture"
         ▼
┌──────────────────┐     ┌──────────────────┐
│  01_Seedlings    │────▶│  02_Shaping      │
│  (atomic ideas)  │     │  (dialogue)      │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         ▼                        ▼
┌──────────────────┐     ┌──────────────────┐
│  03_Flow_Maps    │────▶│  04_Concepts     │
│  (visual maps)   │     │  (canonical)     │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         ▼                        ▼
┌──────────────────┐     ┌──────────────────┐
│  05_Projects     │────▶│  06_Archive      │
│  (active work)   │     │  (retired)       │
└──────────────────┘     └──────────────────┘
         ▲
         │
┌──────────────────┐
│  07_System       │  (Templates, Schemas, Directives)
│  influences all  │
└──────────────────┘
```

---

## Migration Considerations

### What to Preserve

1. **Energy + Resonance metadata** — Valuable ADHD-friendly features not in new architecture
2. **Backend API integration** — `/personal/sparks` for cross-device sync
3. **Question Engine integration** — 9 question classes for thinking partner
4. **Session document format** — Frontmatter, transcript, thinking dialogues

### What to Add

1. **Quick Capture system** — Status lifecycle, AI boundaries, sidebar queue
2. **Seedling types** — 7 subtypes beyond just "spark"
3. **Formal block schemas** — 6 types with consistent fields
4. **Project structure** — 8-page template for active work
5. **Flow Maps** — Structured visual exploration
6. **Archive system** — Retirement with reasons

### Hybrid Approach (Recommended)

Merge the best of both:

```
/00_Inbox/                 # NEW: Quick captures with status lifecycle
/01_Seedlings/             # NEW: Replaces /Daily/ for atomic ideas
    ├── Observations/
    ├── Questions/
    ├── Insights/          # Merge with current /Insights/
    └── ...
/02_Shaping/               # NEW: Replaces /Sessions/
    └── Dialogue_Sessions/
/03_Flow_Maps/             # NEW: Structured exploration
/04_Concepts/              # KEEP: Add domain subfolders
/05_Projects/              # NEW: Full structure
/06_Archive/               # NEW: Retirement system
/07_System/                # NEW: Templates and schemas

# PRESERVE from current:
- Energy levels (low/medium/high)
- Resonance signals (8 types)
- Backend API integration
- Question Engine (9 classes)
```

---

## Implementation Priority

### Phase 1: Foundation
1. Update `STRUCTURE_FOLDERS` to 7-layer architecture
2. Add Quick Capture schema to block types
3. Implement `capture_status` lifecycle

### Phase 2: UI Components
4. Create Quick Capture Queue sidebar component
5. Add "Process this capture" workflow
6. Implement Seedling type selection

### Phase 3: Templates
7. Port Markdown templates to SiYuan
8. Create Concept Page structure
9. Add Flow Map templates

### Phase 4: Integration
10. Connect Quick Capture to existing backend APIs
11. Add AI classification service
12. Implement health checks and maintenance scans

---

## References

- **Current Implementation:** `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts`
- **New Architecture:** `IES_SiYuan_Architecture_Package_QuickCaptureUpdated/`
- **Block Schemas:** `07_System/Block_Schemas.md`
- **Quick Capture Schema:** `07_System/Quick_Capture_Schema.md`
- **AI Directives:** `07_System/AI_Assistant_Directives.md`
- **Data Flow:** `07_System/IES_SiYuan_Dataflow.md`
