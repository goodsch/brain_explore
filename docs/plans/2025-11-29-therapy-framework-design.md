# Therapy Framework Project Design

**Date:** 2025-11-29
**Status:** Approved
**Owner:** Chris

## Executive Summary

This project builds a structured understanding of Chris's therapeutic worldview through an AI-assisted knowledge development system. The approach uses parallel tracks: immediate work with existing tools while building an engaging custom interface.

## Goals

### Primary Goal
**Self-understanding** — Build a structured way to articulate and examine own therapeutic worldview and clinical instincts.

### Secondary Goals (Serve the Primary)
- Living knowledge base (externalized, navigable, searchable, growable)
- Repeatable process for examining thinking
- Documents and internalized clarity as outcomes

### What This Is NOT
- Not primarily a client-facing method (though may become one)
- Not primarily a research database (though grounded in research)
- Not primarily a marketing tool (though clarity enables marketing)

## Core Problem

**Blockers being addressed:**
1. Too many ideas, no structure (primary)
2. No process for systematically examining own thinking
3. Never synthesized a full picture

**Current state:**
- Working blend: Existentialism + CBT/REBT + Humanistic + Evolutionary lens
- Gaps: Neurodivergence, nervous system, real-world systems, how change actually happens — not integrated holistically

## Design Decisions

### Decision 1: Three Content Tracks
| Track | Focus | Examples |
|-------|-------|----------|
| 1 - Human Mind | Why humans are the way they are | Threat response, adaptation, identity |
| 2 - Change Process | How therapy creates change | Stages, mechanisms, what moves the needle |
| 3 - Method | Operational approach | Session scaffolds, templates, tools |

### Decision 2: Two Development Tracks
| Track | Purpose | Timeline |
|-------|---------|----------|
| Track 1: Start Now | Begin actual thinking work with existing tools | This week |
| Track 2: Build Interface | Create engaging custom interface | 2-4 weeks parallel |

### Decision 3: Two SiYuan Notebooks
| Notebook | Purpose | Contents |
|----------|---------|----------|
| Framework Project | Meta/planning | Dashboard, decisions, sessions, backlog |
| Therapy Framework | Actual content | Concepts across three tracks |

### Decision 4: Multi-Modal Working Style
- Research integration, structured prompts, visual mapping rotate as lead
- Variety aids insight — not one rigid process
- Structure for re-entry/starting; emergence for actual work

### Decision 5: AI Plays Four Roles Equally
1. Questioning partner (surfaces thinking)
2. Research assistant (finds and connects from sources)
3. Organizer (structures into knowledge base)
4. Re-entry guide (context restoration, next steps)

## Architecture

### MCP Tools Stack

```
┌─────────────────────────────────────────────┐
│              AI (Claude)                    │
│   Questioning + Research + Organization     │
├──────────┬──────────┬──────────┬────────────┤
│  annas   │ ebook-   │ siyuan-  │  (future)  │
│   MCP    │   mcp    │   mcp    │  visual    │
└──────────┴──────────┴──────────┴────────────┘
     │           │          │
     ▼           ▼          ▼
  Anna's     EPUB/PDF    SiYuan
  Archive    Library     Knowledge Base
```

### Research Pipeline

```
Topic/Question
     │
     ▼
annas.search(query) ──→ Find relevant books
     │
     ▼
annas.download(id) ──→ Acquire books
     │
     ▼
ebook-mcp.get_toc() ──→ Understand structure
ebook-mcp.get_chapter_markdown() ──→ Extract content
     │
     ▼
AI Synthesis ──→ Meta-analysis
  • Extract key claims
  • Find agreements
  • Identify tensions
  • Note gaps
     │
     ▼
siyuan-mcp.createConcept() ──→ Store with evidence chain
```

### AI Facilitation Modes

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Socratic** | Vague intuition | One question at a time, mirror, surface assumptions |
| **Structured Prompts** | Defining something specific | Template questions, fill as answered, flag gaps |
| **Research** | Grounding in literature | Full pipeline (discovery → synthesis → storage) |
| **Challenge** | Stress-testing an idea | Devil's advocate, contradictions, edge cases |

## SiYuan Structure

### Notebook 1: Framework Project (Meta)

```
/Framework Project/
├── Dashboard/              # Current status, what's next
├── Decisions/              # Key choices (with rationale)
├── Architecture/           # System design, MCP configs
├── Sessions/               # Work session logs
├── Backlog/                # Ideas, enhancements, future
└── References/             # Links to tools, docs
```

### Notebook 2: Therapy Framework (Content)

```
/Therapy Framework/
├── 1-Human Mind/           # Track 1 concepts
├── 2-Change Process/       # Track 2 concepts
├── 3-Method/               # Track 3 concepts
├── _Inbox/                 # Quick capture
└── _Maps/                  # Visual diagrams
```

### Templates

**Concept:**
- Name
- Track (1, 2, or 3)
- Status (seed / developing / solid)
- Core statement (1-3 sentences)
- Why I believe this
- Open questions
- Links to related concepts

**Session Log:**
- Date
- Starting question/focus
- Key insights surfaced
- Concepts created/updated
- Where to pick up next

## Session Protocol

1. **Re-entry** (2 min): Read last session log, orient
2. **Focus**: Set intention — what question/area today?
3. **Work**: AI-assisted exploration
4. **Capture** (10 min): Update SiYuan, write session log

## ADHD Accommodations

| Challenge | Solution |
|-----------|----------|
| Starting is hard | Clear entry points, never blank page |
| Sustaining is hard | Context preservation, session logs |
| Overwhelm | Manageable chunks, one question at a time |
| Engagement | Visual feedback, varied interaction, progress sense |

## Implementation Plan

### Track 1: Start Working (This Week)

**Day 1-2: Setup**
- [ ] Create `.mcp.json` with annas, ebook-mcp, siyuan-mcp
- [ ] Enable siyuan-mcp, verify connection
- [ ] Create SiYuan notebooks and folder structure
- [ ] Create Concept and Session Log templates

**Day 3+: Begin Work**
- [ ] First session: Pick ONE foundational question
- [ ] Use research process to ground in literature
- [ ] Capture first concepts
- [ ] Write session log

### Track 2: Build Interface (Parallel)

**Week 1:** Basic web UI + SiYuan read/write
**Week 2:** Visual map panel
**Week 3:** Mode switcher, progress dashboard
**Week 4+:** Iterate based on use

## Configuration

### MCP Servers

```json
{
  "mcpServers": {
    "annas": {
      "command": "/home/chris/.local/bin/annas",
      "args": ["mcp"],
      "env": {
        "ANNAS_DOWNLOAD_PATH": "/home/chris/dev/projects/claude/neurogarden/reference/books",
        "ANNAS_SECRET_KEY": "9xh5HWgKwUEARCwhgKyMWbPNAc4tm"
      }
    },
    "ebook-mcp": {
      "command": "uv",
      "args": ["--directory", "/home/chris/dev/mcp_servers/ebook-mcp/src/ebook_mcp", "run", "main.py"]
    },
    "siyuan-mcp": {
      "command": "npx",
      "args": ["siyuan-mcp@latest"],
      "env": {
        "SIYUAN_HOST": "192.168.86.60",
        "SIYUAN_PORT": "6806",
        "SIYUAN_TOKEN": "8ddw4vp2tokab94y"
      }
    }
  }
}
```

## Success Criteria

**6-month vision:**
1. Living knowledge base with 50+ interconnected concepts
2. Clear articulation of therapeutic worldview
3. Evidence trails for major principles
4. Repeatable process that feels natural
5. Visual map showing framework structure

## Open Questions

1. Which visual mapping library for the interface? (React Flow, D3, Mermaid)
2. How to handle conflicting evidence in principles?
3. When is a concept "solid" vs "developing"?
4. How to integrate client case examples without privacy issues?

---

*Design validated through brainstorming session 2025-11-29*
