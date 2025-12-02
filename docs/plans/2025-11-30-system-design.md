# System Design: Therapy Framework Exploration Platform

*Date: 2025-11-30*

## Overview

This document describes the complete system for building a structured understanding of Chris's therapeutic worldview through AI-assisted knowledge development.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    INTERFACE LAYER                       │
│  Happy App (mobile) ←→ Claude Code ←→ SiYuan + MCP      │
└─────────────────────────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Framework       │ │ Therapy         │ │ Auto-Generated  │
│ Project         │ │ Framework       │ │ Mind Maps       │
│ (Dashboard)     │ │ (Exploration)   │ │ (Visualization) │
└─────────────────┘ └─────────────────┘ └─────────────────┘
     SiYuan              SiYuan             Markmap
```

### Components

| Layer | Tool | Purpose |
|-------|------|---------|
| Interface | Happy app | Mobile-friendly Claude Code access |
| AI + Orchestration | Claude Code + MCP | Exploration sessions, SiYuan read/write |
| Dashboard | SiYuan: Framework Project | See shape, track progress, quick capture |
| Content | SiYuan: Therapy Framework | Build connected understanding |
| Visualization | Markmap (auto-generated) | Overview maps from link structure |

## SiYuan Notebook 1: Framework Project (Dashboard)

**Purpose:** See the overall shape — where you are, how pieces connect, what to pick up next.

### Structure

```
/Framework Project/
├── 🗺️ Project Map/
│   └── index.md          # Visual overview (embedded map or structured view)
│
├── 📍 Current State/
│   ├── active-work.md    # What's in progress right now
│   ├── blockers.md       # What's stuck and why
│   └── decisions-needed.md
│
├── 🧭 Navigation/
│   ├── tracks.md         # Track 1, 2, 3 overview with status
│   ├── milestones.md     # Key waypoints (past and future)
│   └── concept-index.md  # Auto-generated list of all concepts
│
├── 📥 Inbox/
│   └── quick-capture.md  # Dump ideas here, process later
│
├── 📋 Sessions/
│   └── YYYY-MM-DD-*.md   # Session logs
│
└── 🗄️ Archive/
    └── decisions/        # Past decisions with rationale
```

### Key Behaviors

- **Project Map** is the landing page — shows shape at a glance
- **Inbox** is for quick capture (dump ideas, process together periodically)
- **Sessions** creates continuity between work sessions
- **Current State** updates automatically at end of sessions

## SiYuan Notebook 2: Therapy Framework (Exploration)

**Purpose:** Build interconnected understanding through connecting + branching thinking.

### Structure

```
/Therapy Framework/
├── 1-Human Mind/           # Track 1: Why humans are the way they are
│   └── [concepts...]
│
├── 2-Change Process/       # Track 2: How therapy creates change
│   └── [concepts...]
│
├── 3-Method/               # Track 3: Your operational approach
│   └── [concepts...]
│
├── _Connections/           # Explicit relationship maps
│   ├── tensions.md         # Where ideas conflict or create productive tension
│   ├── foundations.md      # Core ideas that support many others
│   └── questions.md        # Open questions linking multiple concepts
│
└── _Inbox/                 # Raw captures before placing in tracks
```

### Linking System

1. **Every concept** gets bidirectional links to related concepts
2. **Block references** let you embed the same insight in multiple places
3. **Backlinks panel** shows "what links here" — reveals hidden connections
4. **Tags** for cross-cutting themes: `#mechanism`, `#tension`, `#grounded`, `#intuition`

### Concept Statuses

- `seed` — Initial capture, unexamined
- `developing` — Being explored, refined
- `solid` — Clear articulation, internally consistent
- `grounded` — Has research backing

### Exploration Workflow

```
Socratic session → Raw insight emerges → Capture in _Inbox
                                              ↓
                        Process: Place in Track, add links, tag status
                                              ↓
                        Over time: Links accumulate, clusters emerge
                                              ↓
                        Periodically: Review _Connections/, update maps
```

## Mind Map Generation

**Tool:** Markmap (https://markmap.js.org/)

**Why Markmap:**
- Generates interactive mind maps from markdown
- Runs in browser, no install needed
- Collapsible nodes, zoom/pan, clean aesthetic
- Free, open source

### Generation Pipeline

```
SiYuan links/structure
        ↓
   Export script
        ↓
   Markdown hierarchy
        ↓
   Markmap renders
        ↓
   Interactive visual map
```

### Map Types

1. **Full framework map** — All three tracks, high-level connections
2. **Track map** — Deep dive into one track's concepts
3. **Concept neighborhood** — One concept + everything it links to

### Generation Triggers

- On demand: `/generate-map` command
- At milestones: After completing a concept cluster
- Session end: Quick snapshot of what was touched

## Session Flow

```
1. Open Happy on phone
2. Start session: "Let's continue exploring [topic]"
3. Claude reads last session log, orients you
4. Socratic exploration happens
5. Insights captured to SiYuan via MCP
6. Session log written
7. Dashboard updated with current state
8. (Periodically) Generate fresh map to see new shape
```

## Implementation Plan

### Phase 1: Foundation (This Session)
- [x] Design complete system
- [ ] Create SiYuan notebooks with folder structure
- [ ] Migrate existing local content to SiYuan

### Phase 2: Automation (Next Session)
- [ ] Build Markmap generation script
- [ ] Update slash commands for new workflow
- [ ] Test full session flow

### Phase 3: Refinement (Ongoing)
- [ ] Iterate on dashboard views based on usage
- [ ] Refine concept template as patterns emerge
- [ ] Add map types as needed

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Happy for mobile | Solves input/output/session friction without custom development |
| SiYuan two notebooks | Separates meta (planning) from content (framework) |
| Markmap for visualization | Auto-generated, no manual drawing, browser-based |
| Dashboard over async forms | Simpler, more valuable for ADHD — see shape, not manage inbox |
| Connecting + branching model | Matches natural thinking style |

## Open Questions

- Exact Markmap script implementation (Python? Node?)
- Whether to embed maps in SiYuan or keep separate
- Backup/sync strategy for SiYuan data
