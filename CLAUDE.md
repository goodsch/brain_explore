# brain_explore — Therapeutic Exploration System

*A three-layer system for exploring and developing therapeutic worldviews*

This workspace contains three related projects. Check `.active-project` or the SessionStart message to see which is active.

## Critical Reference: Five-Agent Analysis Documents

**Important:** Start here to understand the complete analysis and recommended path forward:

**Entry Point (Read in this order):**
1. **[docs/five-agent-synthesis.md](./docs/five-agent-synthesis.md)** — Integration of all five agent reports with clear vision, gaps, lessons, and phased path
2. **[docs/meta-analysis-master-report.md](./docs/meta-analysis-master-report.md)** — Comprehensive synthesis highlighting what worked, what went wrong, and recovery options
3. **[docs/timeline-analysis.md](./docs/timeline-analysis.md)** — How the project evolved in 3 days (Phase 1-5 breakdown)

**Detailed Agent Reports (Reference):**
- **[docs/true-vision-document.md](./docs/true-vision-document.md)** — Meta-cognitive exploration system vision extraction
- **[docs/siyuan-knowledge-architecture-report.md](./docs/siyuan-knowledge-architecture-report.md)** — Knowledge graph analysis (specs vs. reality)
- **[docs/synapse-autopsy-report.md](./docs/synapse-autopsy-report.md)** — Parallel project lessons and warnings
- **[docs/configuration-timeline-impact-report.md](./docs/configuration-timeline-impact-report.md)** — Configuration overhead quantified
- **[docs/reference-architecture-synthesis.md](./docs/reference-architecture-synthesis.md)** — Successful pattern analysis

**Planning Document:**
- **[docs/master-analysis-plan.md](./docs/master-analysis-plan.md)** — Framework that guided the five-agent analysis

These documents contain actionable findings about:
- Why the active-project feature creates activation friction (40% session overhead)
- How configuration overhead (2,500 lines) is limiting velocity
- What actually works (core IES, therapeutic focus)
- Clear phased path forward with success criteria (Phase 0-5)

## What This Is

```
IES (Intelligent Exploration System)
  - Backend API: Entity extraction, chat, Neo4j storage, literature linking
  - Plugin: SiYuan sidebar UI (iOS, Desktop, Web)
  - STATUS: Therapy-focused, production-ready
  - FUTURE: Generalization to other domains planned

Framework Project (Implementation Instance)
  - Configuration layer for this IES instance
  - User profiles, domain overrides, deployment settings
  - STATUS: Infrastructure in place, config system not yet implemented
  - PURPOSE: Bridge between generic IES and domain-specific Therapy

Therapy Framework (Content Layer)
  - Therapeutic worldview concepts and theories
  - Grounded in 63 therapy/psychology books
  - STATUS: Early development (Track 1 developing, Tracks 2-3 in progress)
  - PURPOSE: Develop articulate understanding of therapeutic approach
```

## Project Structure

```
brain_explore/
├── ies/                           # Intelligent Exploration System
│   ├── backend/                   # FastAPI backend (4,496 lines Python)
│   │   ├── src/ies_backend/       # API, services, schemas
│   │   └── tests/                 # 61 unit tests
│   ├── plugin/                    # SiYuan plugin (14,092 lines TS/Svelte)
│   ├── CLAUDE.md                  # IES project instructions
│   └── progress.md                # Development progress (detailed session logs)
│
├── framework/                     # Framework Project (Implementation Instance)
│   ├── CLAUDE.md                  # Framework project instructions
│   └── progress.md                # Implementation progress & roadmap
│
├── therapy/                       # Therapy Framework (Content Layer)
│   ├── CLAUDE.md                  # Content development instructions
│   └── progress.md                # Exploration progress & concepts
│
├── library/                       # Shared: GraphRAG modules (Python)
├── scripts/                       # Shared: CLI tools (document processing)
├── books/                         # Shared: 63 therapy/psychology books (PDF/EPUB)
├── docs/                          # Shared: Design docs, plans, setup guides
└── docker-compose.yml             # Shared: Neo4j + Qdrant infrastructure
```

## Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| **IES Backend** | ✅ Production | 16 API endpoints, tested and working |
| **IES Plugin** | ✅ Production | iOS-capable, works on Desktop/iPad/Web |
| **Framework Layer** | 🔲 Planned | Configuration system not yet implemented |
| **Therapy Content** | 🟡 Developing | Track 1 in progress, Tracks 2-3 seeds identified |
| **Setup & Config** | 🟡 Partial | Manual configuration required, not yet automated |

## Architecture: Current vs. Future

### Current State (Therapy-Focused)
- ✅ IES is optimized for therapy use
- ✅ EntityDomain enum contains "therapy"
- ✅ Extraction prompts reference therapy concepts
- ✅ Ready for exploration and content development

### Future State (Generic Framework)
- 🔲 Extract domain-specific code from IES
- 🔲 Implement Framework layer configuration system
- 🔲 Create architectural contracts (what implementations must provide)
- 🔲 Add API versioning and capability discovery
- Timeline: Post-therapy content development (Phase 6+)

## Quick Start

**First Time?** Start here:
1. See [README.md](./README.md) for setup instructions
2. Create `.env` from `.env.example`
3. Run `docker compose up -d`
4. Start backend: `cd ies/backend && uv run uvicorn ...`

**Continuing Work?** Check active project:
1. SessionStart message shows active project
2. Read `{project}/CLAUDE.md` for instructions
3. Read `{project}/progress.md` for current state
4. Do work, commit, update progress file

## Switching Projects

```bash
/switch-project ies        # Work on backend/plugin development
/switch-project framework  # Work on configuration & setup
/switch-project therapy    # Work on content development
```

The active project persists in `.active-project`.

## Shared Resources

| Resource | Purpose |
|----------|---------|
| `library/` | GraphRAG Python modules (in/search/graph operations) |
| `scripts/` | CLI tools (document ingestion, entity extraction) |
| `books/` | 63 therapy/psychology books (PDF/EPUB) |
| `docker-compose.yml` | Neo4j 5 + Qdrant infrastructure |
| `docs/plans/` | Architecture & design documents |
| `docs/setup.md` | Setup instructions (detailed) |
| `docs/structure.md` | Project structure reference |

## Infrastructure Quick Start

```bash
# Start Docker services (Neo4j + Qdrant)
docker compose up -d

# Verify Neo4j
curl http://localhost:7474

# Start IES Backend
cd ies/backend
cp ../.env.example .env
# Edit .env with your API keys
uv run uvicorn ies_backend.main:app --host 0.0.0.0 --port 8081

# Run tests
cd ies/backend && uv run pytest

# Build plugin
cd ies/plugin && npm install && npm run build
```

## SiYuan Integration

Three notebooks track different projects:
- **Intelligent Exploration System** — IES development (architecture, design, dev logs)
- **Framework Project** — Implementation work (configuration, deployment, testing)
- **Therapy Framework** — Content development (concepts, tracks, research)

## Development Process

### Making Changes
1. Identify which project you're working on
2. Make code changes
3. Run tests: `cd ies/backend && uv run pytest`
4. Commit: `git add . && git commit -m "..."`
5. **Update progress file** in `{project}/progress.md`

### Updating Documentation
- **Progress files** — Updated after each session
- **CLAUDE.md files** — Updated when scope changes
- **SiYuan notebooks** — Auto-updated by `/sync` command
- **Serena memories** — Use `/sc:save` at session end

## Project Analysis & Documentation

### Five-Agent Comprehensive Analysis Complete (Dec 2, 2025)

**Major Milestone:** Complete multi-agent analysis of brain_explore and parallel Synapse project with clear vision extraction, architecture assessment, and phased recovery path. **35,000+ words across 9 comprehensive analysis documents.**

#### Analysis Documents

**Five-Agent Team Reports:**

1. **`docs/true-vision-document.md`** (12,000+ words) — Vision Extraction Specialist
   - Extracted coherent meta-cognitive exploration system from 254+ sessions
   - Core insight: Help people understand how they think through three interconnected layers
   - Why projects keep expanding: User's thinking pattern (connecting concepts, seeing implications) is identical to capability being built
   - How architecture could channel this productively instead of creating scope creep

2. **`docs/siyuan-knowledge-architecture-report.md`** (4,800+ words) — SiYuan Knowledge Graph Analyst
   - Deep analysis of three SiYuan notebooks: IES (2,379 blocks), Framework, Therapy
   - Gap between aspirational and actual: IES specs 96% complete, plugin not started
   - Neo4j data reality: 48,987 entities loaded but only ~1 actively used for exploration
   - Therapy Framework: has structure (Tracks 1-3) but only 1-2 concepts developed; zero Track 2-3 content
   - Infrastructure/content ratio: 96% infrastructure work, 4% actual therapeutic exploration
   - Missing layer: Profile system specified but never instantiated, question engine specified but unimplemented

3. **`docs/synapse-autopsy-report.md`** (2,900+ words) — Synapse Project Archaeologist
   - Analysis of parallel project (abandoned Oct 2024 after 1 month development)
   - Architectural parallels: Both combine knowledge graphs + document processing + reading interface
   - Root cause of abandonment: Same pattern now emerging in brain_explore
   - Critical warning: brain_explore is at Oct 3 of Synapse's trajectory
   - Five salvageable components identified (~17 hours total effort to port)
   - Key lesson: Meta-system building replaced user value focus
   - Both projects share: same vision (meta-cognitive exploration), same failure mode (scope expansion)

4. **`docs/configuration-timeline-impact-report.md`** (9,500+ words) — Configuration Impact Auditor
   - Timeline of configuration inflation over 72 hours (Nov 29 - Dec 2)
   - Seven phases mapped: clean baseline → active-project system → meta-override escape hatch
   - Configuration quantified: 2,500 lines managing 20,000 lines code (1:8 ratio) within 72 hours
   - Core contradiction identified: System warns "keep it simple" while being over-engineered
   - Eight-layer hierarchy: Global CLAUDE.md → project CLAUDE.md → progress files → active-project system → Serena memories → slash commands → feature specs → meta-overrides
   - Impact assessment: 40% of session time spent on configuration maintenance
   - Activation friction: 2-5 minutes decision overhead per task ("which project am I?")
   - ROI analysis: 12-16 hours to simplify, 219 hours/year savings
   - ADHD-hostile design: Creates decision paralysis at initiation despite being built for ADHD user

5. **`docs/reference-architecture-synthesis.md`** (3,500+ words) — Reference Architecture Synthesizer
   - Analysis of successful reference projects (Agentic AI Systems, Claude Code Infrastructure)
   - Five proven patterns extracted:
     1. Minimize configuration (successful projects: <200 lines CLAUDE.md)
     2. Progressive disclosure (500-line rule enforced, deep dives in separate resources)
     3. Auto-activation via hooks (not manual switching)
     4. Single source of truth (not 8 configuration layers)
     5. Fixed decision points (config decided once, not per-session)
   - brain_explore violates all five patterns
   - Recommendation: Immediate kill of premature Framework layer abstraction
   - Consolidate to single CLAUDE.md, eliminate active-project switching

**Master Synthesis Documents:**

6. **`docs/five-agent-synthesis.md`** (7,000+ words) — Integration of all five agent reports
   - True vision articulated: Meta-cognitive exploration system (Flow Mode + Pattern ID + Dialogue)
   - Knowledge architecture gap: Specs vs. implementation vs. actual use
   - Synapse lessons: Why parallel project failed, how to avoid same fate
   - Configuration impact quantified: 40% session overhead from 2,500 config lines
   - Reference patterns: What successful projects do differently
   - Clear phased path forward with success criteria
   - Future project parking lot (defer all until core proven)

7. **`docs/master-analysis-plan.md`** (5,000+ words) — Framework that guided five-agent dispatch
   - Five specialized agent roles with independent analysis targets
   - Five clarification questions that led to analysis
   - Expected deliverables and three-wave analysis timeline

8. **`docs/timeline-analysis.md`** — Project evolution across five phases (Nov 29-Dec 2)
   - Phase 1: Clear Personal Vision (focused, achievable)
   - Phase 2: Scope Expansion (introducing complexity)
   - Phase 3: Framework Abstraction (premature generalization)
   - Phase 4: Configuration Complexity (meta-system expansion)
   - Phase 5: Current State (reality check)

9. **`docs/meta-analysis-master-report.md`** — Comprehensive synthesis with three recovery options
   - What worked well: Core IES, technology choices, therapeutic focus
   - Where things went wrong: Tool-building before tool-using
   - Configuration contradictions and ADHD-hostile design
   - Three recovery paths with trade-offs analysis

#### Core Vision: Meta-Cognitive Exploration System

From analysis of 254+ sessions and design history:

**Unified Vision:** Help people understand *how they think* and *how they see the world* so they can achieve meaningful change.

**Three Interconnected Layers:**
1. **Flow Mode** — Non-linear knowledge navigation with AI documentation of exploration paths
   - Problem: Linear reading doesn't match natural thinking; jumps between related concepts
   - Solution: Start anywhere in knowledge graph, follow threads of interest, let AI document
   - Why it works: People learn fastest following own curiosity, not predetermined sequence

2. **Thinking Pattern Identification** — Recognize unique cognitive patterns through observation
   - Problem: People don't recognize their own thinking patterns and worldviews
   - Solution: Observe navigation patterns, concept interest, question styles; build profile
   - Why it works: You can't change patterns you don't recognize

3. **Therapeutic Dialogue** — Adaptive questioning based on identified patterns
   - Problem: Generic questions don't work; they ignore how this person actually thinks
   - Solution: Ask questions adapted to their patterns, current state, area of exploration
   - Why it works: Right question in right way creates insight; wrong question creates resistance

**Why This Vision Is Coherent:** These three don't just coexist—they're mutually reinforcing. Flow Mode reveals patterns. Patterns inform dialogue. Dialogue surfaces concepts. Concepts expand knowledge graph. Knowledge graph enables deeper flow. Each layer makes others more effective.

#### Analysis Status: Ready for Phase 0-1 Execution

**What the Five-Agent Analysis Found:**
- Core vision is coherent and compelling (meta-cognitive exploration is not a flawed idea)
- Technical foundation is solid (IES backend and plugin work well)
- Therapy-focused configuration is appropriate (not premature generalization)
- Configuration system is broken (40% session overhead, ADHD-hostile design)
- Content development barely started (1-2 concepts vs. full framework needed)
- Project at critical trajectory point (same path as abandoned Synapse project)

**Immediate Blockers to Fix (Phase 0):**
1. Simplify configuration (eliminate active-project switching, consolidate CLAUDE.md)
2. Clarify single source of truth (too many configuration layers)
3. Establish clear focus (stop building meta-systems, start using them)
4. Estimate: 12-16 hours, ROI: 219 hours/year savings

**Phase 1 Validation (After Phase 0):**
- Activate core IES with real therapeutic exploration
- Develop Therapy Framework Track 1 concepts
- Gather user feedback on exploration value
- Success = proceed to Phase 2-3 expansion
- Failure = core vision flawed or execution wrong, needs pivot

**Status:** Analysis complete and documented. Ready to begin Phase 0. Execute immediately before expanding further.

#### Key Quantified Findings

| Metric | Finding | Impact |
|--------|---------|--------|
| **Configuration Overhead** | 2,500 lines managing 20,000 lines code | 40% session time on meta-work |
| **Work Distribution** | 96% infrastructure, 4% therapeutic content | Goal displacement from Day 1 |
| **Activation Friction** | 2-5 minutes decision overhead per task | ADHD-hostile despite design intent |
| **Neo4j Utilization** | 48,987 entities loaded, ~1 active | Massive infrastructure, zero usage |
| **Content Development** | 1-2 therapy concepts, zero Track 2-3 | Exploration barely started |
| **Synapse Timeline** | Oct 3 trajectory before abandonment | brain_explore now at same point |
| **Simplification ROI** | 12-16 hours to fix, 219 hours/year saved | High-impact quick win |

#### Phased Path Forward (Phases 0-5)

Clear recovery path with detailed success criteria in [five-agent-synthesis.md](./docs/five-agent-synthesis.md):

| Phase | Focus | Duration | Success Criteria |
|-------|-------|----------|------------------|
| **Phase 0** | Stabilize | 2-3 days | Simplify config, consolidate CLAUDE.md, eliminate active-project switching |
| **Phase 1** | Prove | 2-3 weeks | Core IES activated, therapy content developed, measurable exploration value |
| **Phase 2-3** | Expand | 4-6 weeks | Scale therapeutic content, develop Therapy Framework tracks, multi-user testing |
| **Phase 4-5** | Generalize | 8+ weeks | Framework abstraction, multi-domain support (if Phase 1 proves value) |

**Currently At:** Phase 0 (configuration stabilization needed)
**Critical Decision Point:** Phase 1 completion proves or disproves entire approach. Success = proceed to Phase 2-3. Failure = core vision was flawed, pivot or abandon.

**Recommendation from Analysis:** Begin Phase 0 immediately (12-16 hour investment, 219 hour/year ROI).

#### Future Project Parking Lot

All expansion ideas deferred until core vision proven:
- Multi-domain framework generalization
- Advanced profile system (currently just schema)
- Question engine with 8 questioning approaches
- Synapse component ports (17 hours identified)
- Therapeutic modality specializations
- Institutional deployment patterns

**Rule:** Nothing new enters active development until phases 0-1 complete with measurable therapeutic value.

#### Analysis Team & Deliverables Summary

**Five Specialized Agents with Independent Analysis:**

1. **Vision Extraction Specialist** → [true-vision-document.md](./docs/true-vision-document.md)
   - Identified meta-cognitive exploration system (Flow Mode + Pattern ID + Dialogue)
   - Recognized user's thinking pattern identical to system being built
   - Proposed architectural channeling instead of scope containment

2. **SiYuan Knowledge Graph Analyst** → [siyuan-knowledge-architecture-report.md](./docs/siyuan-knowledge-architecture-report.md)
   - Mapped aspirational specs vs. actual implementation vs. active usage
   - Quantified infrastructure/content ratio (96% vs. 4%)
   - Identified missing profile system and question engine layers

3. **Synapse Project Archaeologist** → [synapse-autopsy-report.md](./docs/synapse-autopsy-report.md)
   - Analyzed parallel abandoned project for pattern recognition
   - Identified brain_explore at identical failure trajectory point
   - Found 5 salvageable components and root cause lessons

4. **Configuration Impact Auditor** → [configuration-timeline-impact-report.md](./docs/configuration-timeline-impact-report.md)
   - Mapped 72-hour configuration inflation timeline
   - Quantified 2,500 lines managing 20,000 (1:8 ratio)
   - Calculated 40% session overhead and 219 hour/year ROI for fix

5. **Reference Architecture Synthesizer** → [reference-architecture-synthesis.md](./docs/reference-architecture-synthesis.md)
   - Analyzed 5 successful reference projects
   - Extracted 5 proven architectural patterns
   - Identified all 5 patterns violated by current design

**Master Synthesis Documents:**

- **[five-agent-synthesis.md](./docs/five-agent-synthesis.md)** — Integration of all findings with phased path
- **[meta-analysis-master-report.md](./docs/meta-analysis-master-report.md)** — What worked, what failed, recovery options
- **[master-analysis-plan.md](./docs/master-analysis-plan.md)** — Analysis framework and methodology

### Serena Memory System

Memories stored in `.serena/` (updated based on analysis):
- `project_overview.md` — Three-layer architecture overview
- `ies_architecture.md` — IES technical design
- `true_vision.md` — Meta-cognitive exploration system articulation
- `configuration_impact.md` — Why current system is blocking work
- `synapse_lessons.md` — Why parallel project failed, how to avoid fate
- `phased_recovery_path.md` — Phases 0-5 with success criteria
- `tech_stack.md` — Dependencies and versions
- `codebase_structure.md` — File organization
- `siyuan_structure.md` — Notebook layout

Use `/sc:load` at session start to load full context.
