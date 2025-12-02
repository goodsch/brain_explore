# Documentation Cleanup Plan

**Date:** 2025-12-02
**Objective:** Get all documentation accurate, organized, and aligned with actual project state

---

## Current Issues (from Audit)

### Architecture Honesty
- 🔴 IES claims to be "generic" but contains therapy-specific code
- 🔴 Framework Project has zero code (only CLAUDE.md + progress.md)
- 🔴 Therapy Framework is exploration-stage, not production-ready
- ⚠️ Documentation overstates completion ("READY FOR USE")

### Configuration
- 🔴 Hardcoded values in plugin (USER_ID, BACKEND_HOST)
- 🔴 Hardcoded notebook ID in backend
- 🔴 No .env.example or configuration documentation
- 🔴 No way to override IES defaults from Framework layer

### Documentation
- 🔴 Root README.md doesn't exist
- 🔴 Setup instructions scattered across files
- ⚠️ Progress files claim "READY" but are incomplete
- ⚠️ Conflation of dev tooling (agents) with product architecture

### Alignment
- ⚠️ What's actually built ≠ what's documented
- ⚠️ Three-layer architecture is aspirational, not real
- ⚠️ Each project's role is unclear

---

## Decision: Architectural Direction

**CHOSEN:** Path C - Hybrid Approach (Honest + Aspirational)

**What This Means:**
1. **Ship as therapy-focused:** IES is currently therapy-specific, document it that way
2. **Document the vision:** Note that generalization is future work
3. **Add structure:** Create clear interfaces even if not currently used
4. **Roadmap it:** Backlog items for generalization work

**Why This Works:**
- ✅ Honest about current state
- ✅ Still aspirational about future
- ✅ Less immediate work than full generalization
- ✅ Foundation for future Path A work
- ✅ Unblocks shipping and using the system now

---

## Cleanup Tasks

### Phase 1: Update CLAUDE.md Files (Define Roles)

#### Task 1.1: Root CLAUDE.md (Workspace Overview)
- [ ] Rename "IES (Generic Framework)" → "IES (Therapeutic Exploration)"
- [ ] Update three-layer description: "Current: therapy-focused; Future: generic"
- [ ] Add "Architecture Evolution" section with future vision
- [ ] Add "Known Limitations" section (domain-specific code, etc.)
- [ ] Keep: Project switching, quick start, shared resources
- [ ] Add: Prerequisites section (uv, node, docker, etc.)

#### Task 1.2: ies/CLAUDE.md (IES Framework)
- [ ] Update scope: "Therapeutic Exploration System (TES)" or keep as "IES with therapy focus"
- [ ] Add "Current Limitations" section
- [ ] Add "Configuration Required" subsection (what can't be overridden yet)
- [ ] Move agent discussion to "Development Assistance"
- [ ] Add "Future Generalization" vision

#### Task 1.3: framework/CLAUDE.md (Implementation Instance)
- [ ] Update scope: "TES Implementation for Therapy Worldview"
- [ ] Add "Current Structure" explaining why there's no code (not yet implemented)
- [ ] Add "Configuration System" section (future work)
- [ ] Keep: Quick start, commands, components
- [ ] Add clear expectations: "This layer will contain user profiles, domain overrides, etc."

#### Task 1.4: therapy/CLAUDE.md (Content Exploration)
- [ ] Keep: Three-track structure, quick start, hanging question
- [ ] Update "Current Status": Note that Track 1 is developing, others are seeds
- [ ] Add "Development Workflow": How to use `/explore-session`
- [ ] Add "Research Grounding": How to ground concepts in source material

---

### Phase 2: Reorganize Progress Files (Clarity & Honesty)

#### Task 2.1: ies/progress.md
Current: 7,400+ lines, comprehensive but scattered

New structure:
```markdown
# IES Progress

*Therapeutic exploration framework for SiYuan*

---

## Current Status

Phase 5 COMPLETE ✅

| Component | Status | Notes |
|---|---|---|
| Backend | ✅ Production | 16 endpoints, entity extraction, literature linking |
| Plugin | ✅ Production | iOS-capable, tested iOS + Desktop |
| Tests | ✅ | 61 unit tests passing |

---

## Known Limitations & Future Work

### Current Limitations (Therapy-Specific)
- [x] EntityDomain enum hardcodes THERAPY
- [x] DEFAULT_NOTEBOOK hardcoded (needs config)
- [x] Plugin hardcodes USER_ID and BACKEND_HOST
- [ ] No versioning or capability discovery

### Future Work (Path to Generalization)
- [ ] Extract domain enum to configuration
- [ ] Make notebook ID configurable
- [ ] Plugin configuration system
- [ ] API versioning and capability discovery

---

## Session Log

[Keep recent sessions, archive old ones]

---

## Backlog

### Phase 6 Features
- [ ] Action buttons for common operations
- [ ] Entity relationship visualization
- [ ] Session export to PDF

### Configuration System
- [ ] Plugin settings panel
- [ ] Backend URL configuration
- [ ] Domain enum overrides

### Generalization
- [ ] Remove THERAPY enum
- [ ] Configuration contracts
- [ ] Framework interface specifications
```

#### Task 2.2: framework/progress.md
Current: 5.5KB, good structure but misleading status

New structure:
```markdown
# Framework Project Progress

*Implementation instance of IES for therapy worldview*

---

## Current Status

⚠️ CONFIGURATION LAYER NOT YET IMPLEMENTED

| Layer | Status | Purpose |
|---|---|---|
| IES Backend | ✅ Using | Handles entity extraction, chat, storage |
| IES Plugin | ✅ Using | SiYuan sidebar interface |
| User Config | 🔲 Planned | User profiles, domain overrides |
| Domain Config | 🔲 Planned | Therapy-specific settings |

---

## What We're Using

Backend is running on port 8081. Plugin connects and handles:
- Session chat
- Entity extraction
- SiYuan page creation

---

## What's Next

### Immediate (Next Phase)
1. Extract hardcoded values to configuration
2. Create config system for user overrides
3. Implement user profile management

### Future
1. Domain-specific prompt templates
2. Custom extraction rules
3. Deployment to different environments

---

## Session Log

[Track implementation sessions, not usage sessions]
```

#### Task 2.3: therapy/progress.md
Current: 3.6KB, good structure, honest status

Keep mostly as-is, but clarify:
```markdown
# Therapy Framework Progress

*Exploring and articulating therapeutic worldview*

---

## Current Status

🟡 CONCEPT DEVELOPMENT IN PROGRESS

| Track | Status | Concepts |
|---|---|---|
| 1-Human Mind | Developing | 1 developed, 2 seeds |
| 2-Change Process | Starting | 1 seed identified |
| 3-Method | Not started | — |

---

## Development Process

Use `/explore-session` to develop concepts. Session output is automatically:
1. Entity-extracted via Claude API
2. Stored in Neo4j
3. Linked to source literature
4. Accessible via SiYuan

---

## Session Log

[Keep exploration sessions only, organize by track]
```

---

### Phase 3: Create Setup & Configuration

#### Task 3.1: Root README.md
```markdown
# brain_explore

*Therapeutic exploration framework for worldview development*

## What This Is

A three-layer system for exploring ideas deeply:
- **IES Backend** — Entity extraction, chat, literature linking
- **Plugin** — SiYuan integration (iPad, Desktop, Web)
- **Therapy Content** — Evolving concepts about therapeutic worldview

## Quick Start

### Prerequisites
```bash
- uv (Python package manager)
- node 18+ (for plugin build)
- docker & docker-compose
- SiYuan (community or pro)
- Anthropic API key
```

### Setup
```bash
1. Clone and cd into project
2. `docker compose up -d`  # Start Neo4j, Qdrant
3. Copy .env.example to .env and fill in values
4. cd ies/backend && uv run uvicorn ies_backend.main:app --host 0.0.0.0 --port 8081
5. cd ../plugin && npm install && npm run build
6. Enable plugin in SiYuan settings
```

## Documentation

- [Setup Guide](docs/setup.md)
- [Architecture](docs/architecture.md)
- [API Reference](ies/backend/README.md)
- [Development](docs/development.md)

## Project Structure

See [docs/structure.md](docs/structure.md) for detailed layout.
```

#### Task 3.2: .env.example
```bash
# IES Backend Configuration

## Neo4j (Graph Database)
IES_NEO4J_HOST=localhost
IES_NEO4J_PORT=7687
IES_NEO4J_USER=neo4j
IES_NEO4J_PASSWORD=brainexplore

## Claude API (Entity Extraction)
ANTHROPIC_API_KEY=sk-...
IES_ANTHROPIC_API_KEY=  # Optional: overrides ANTHROPIC_API_KEY

## OpenAI API (Embeddings for Literature Linking)
OPENAI_API_KEY=sk-...

## SiYuan Integration
IES_SIYUAN_HOST=localhost
IES_SIYUAN_PORT=6806
IES_SIYUAN_TOKEN=4we79so0hs4dmtlm
IES_SIYUAN_DEFAULT_NOTEBOOK=20251201113102-ctr4bco

## Backend Service
IES_BACKEND_HOST=0.0.0.0
IES_BACKEND_PORT=8081

## User & Domain (Framework Layer)
IES_USER_ID=chris
IES_DOMAIN=therapy

## Feature Flags
IES_ENABLE_STREAMING=false  # Currently uses non-streaming for iOS
IES_LITERATURE_LINKING_THRESHOLD=0.45
```

#### Task 3.3: docs/setup.md
Detailed step-by-step setup with troubleshooting

#### Task 3.4: docs/structure.md
Tree view of project structure

---

### Phase 4: Update SiYuan Documentation

#### Task 4.1: Update IES Notebook
- Add section: "Known Limitations"
- Add section: "Future Generalization Path"
- Archive old dev logs

#### Task 4.2: Update Framework Project Notebook
- Add note: "Configuration layer not yet implemented"
- Add backlog for config work
- Clean up inactive sections

#### Task 4.3: Update Therapy Framework Notebook
- Organize concepts by track status (developing, seeds)
- Add research queue with links to source books
- Create index of all seed concepts

---

### Phase 5: Update Serena Memories

Regenerate memories with accurate information:
- [ ] `project_overview.md` — Update with Path C (honest + aspirational)
- [ ] `ies_architecture.md` — Add "Known Limitations"
- [ ] `future_projects.md` — Add generalization roadmap
- [ ] Create new: `configuration_system.md` (what needs to be added)

---

## Implementation Order

**Session 1 (Today):**
1. Update root CLAUDE.md (15 min)
2. Create .env.example (10 min)
3. Update ies/progress.md to honest status (30 min)
4. Update framework/progress.md with clear next steps (20 min)
5. Update therapy/progress.md with status clarity (10 min)

**Session 2 (Next):**
1. Create root README.md (30 min)
2. Create docs/setup.md (45 min)
3. Create docs/structure.md (20 min)
4. Update CLAUDE.md files (45 min)

**Session 3:**
1. Update SiYuan notebooks (1 hour)
2. Update Serena memories (30 min)
3. Final verification pass (30 min)

---

## Success Criteria

✅ **Done when:**
- [ ] Root CLAUDE.md updated with honest architecture
- [ ] Each project CLAUDE.md updated with clear scope
- [ ] Progress files removed misleading "READY" claims
- [ ] .env.example documents all configuration
- [ ] Root README.md provides clear quick start
- [ ] Setup instructions are complete and tested
- [ ] Documentation matches actual implementation
- [ ] Roadmap clear: "Current therapy-specific, future generic"
- [ ] All updated to Serena memories

---

## Notes

- **Honesty over aspiration:** If something isn't done, say so
- **Clear roadmap:** Document path to generalization even if not done yet
- **Actionable progress:** Progress files should have next concrete steps
- **Tested setup:** Follow your own setup instructions to verify they work
