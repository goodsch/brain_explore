# brain_explore Project Overview (Updated 2025-12-02)

## Executive Summary

**brain_explore** is a three-layer system for exploring and developing therapeutic worldviews using AI-guided conversations.

**Status:** IES backend + plugin production-ready. Content development in progress.

**Architecture:** Honest & Aspirational (Path C) — Current therapy-focused, future generalization planned.

---

## Three Layers

### Layer 1: IES (Intelligent Exploration System)
**What:** Backend API + SiYuan plugin for guided conversations
**Status:** ✅ Phase 5 Complete
**Details:**
- Backend: 4,496 lines Python (FastAPI)
- Plugin: 14,092 lines TS/Svelte (iOS-capable)
- 16 REST endpoints
- 61 unit tests passing
- Entity extraction via Claude API
- Literature linking via Qdrant vector search

**Current Limitations:**
- Domain-specific (therapy hardcoded)
- Values hardcoded for chris + therapy
- No configuration system yet
- These are Phase 6 work items, not blockers

### Layer 2: Framework Project
**What:** Configuration & deployment for this implementation instance
**Status:** 🔲 Planned (infrastructure ready, config system not implemented)
**Details:**
- Uses: IES Backend + IES Plugin
- Bridges: Generic IES ↔ Domain-specific Therapy
- Purpose: Configures IES for specific use case
- Will contain: User profiles, domain config, deployment settings

**Currently Missing:**
- User profile configuration system
- Domain configuration files
- Deployment configuration
- Plugin settings management

**Timeline:** Phase 6 (next work)

### Layer 3: Therapy Framework
**What:** The evolving therapeutic worldview we're developing
**Status:** 🟡 Concept development in progress
**Details:**
- 3 tracks: Human Mind, Change Process, Method
- 1 concept developed (Narrow Window of Awareness)
- 5 concept seeds identified
- Grounded in 63 therapy/psychology books
- Using IES system for exploration & documentation

**Current Concepts:**
- ✅ Narrow Window of Awareness (developing)
- 🌱 Meaning-Making as Solution (seed)
- 🌱 Unique Personhood (seed)
- 🌱 Foundational Understanding (seed)
- 🌱 Hidden Function of Symptoms (seed)
- 🌱 Conditions for Change (seed)

---

## Architecture Evolution

### Current State (Therapy-Focused Monolith)
```
chris + therapy → IES Backend (hardcoded) + IES Plugin
```

**Why This Is OK:**
- System works excellently for this use case
- Not blocking content development
- Clear path to generalization
- Configuration can be added incrementally

### Target State (Configurable)
```
Framework Config ─┐
                  ├─ IES Backend (reads config) + Plugin (reads settings)
Therapy Content ─┘
```

### Ultimate Vision (Generic)
```
Config Layer A ─┐
                ├─ Generic IES Backend
Config Layer B ─┘
```

---

## Technical Stack

**Backend:**
- Python 3.10+
- FastAPI 0.109+
- Neo4j 5.15+ (graph database)
- Qdrant (vector database)
- Anthropic API (entity extraction)
- OpenAI API (embeddings)

**Plugin:**
- TypeScript 5.1+
- Svelte 4.2+
- Vite 5.2+
- SiYuan 1.1.5+

**Infrastructure:**
- Docker + docker-compose
- Neo4j container
- Qdrant container
- Port 8081 (backend)
- Port 7687 (Neo4j)
- Port 6333 (Qdrant)

---

## Knowledge Base

- **63 Books:** Therapy, psychology, neuroscience
- **Neo4j Nodes:** 48,987
- **Qdrant Chunks:** 27,523
- **Embeddings:** OpenAI text-embedding-3-small

---

## Development Workflow

### Code Changes
1. Make changes
2. Run tests: `cd ies/backend && PYTHONPATH=src uv run pytest`
3. Commit: `git commit -m "..."`
4. Update progress file: `{project}/progress.md`

### Content Development
1. Run exploration session: `/explore-session`
2. Socratic dialogue with Claude
3. System auto-extracts entities
4. Auto-stores in Neo4j
5. Auto-links to literature
6. Auto-creates SiYuan documents

---

## Current Focus

**Why Documentation Cleanup Was Done:**
- Clarify honest vs aspirational claims
- Remove misleading "READY" claims
- Identify what actually needs to be built
- Create actionable roadmaps
- Remove conflation of dev tooling with product

**Key Insight:**
This is OK — therapy-focused monolith is fine for current work. Generalization is incremental future work, not blocker.

---

## Quick Reference

| Item | Details |
|------|---------|
| **Backend Start** | `cd ies/backend && uv run uvicorn ies_backend.main:app --host 0.0.0.0 --port 8081` |
| **Tests** | `cd ies/backend && PYTHONPATH=src uv run pytest` |
| **Plugin Build** | `cd ies/plugin && npm install && npm run build` |
| **Docker** | `docker compose up -d` |
| **Neo4j UI** | http://localhost:7474 (neo4j / brainexplore) |
| **Qdrant UI** | http://localhost:6333/dashboard |
| **Backend Docs** | http://localhost:8081/docs |
| **Active Project** | See `.active-project` file |

---

## Documentation Locations

- **Workspace Overview:** `./CLAUDE.md`
- **IES Architecture:** `./ies/progress.md` & `./ies/CLAUDE.md`
- **Framework Roadmap:** `./framework/progress.md` & `./framework/CLAUDE.md`
- **Content Development:** `./therapy/progress.md` & `./therapy/CLAUDE.md`
- **Setup Guide:** `./README.md` & `.env.example`
- **Cleanup Plan:** `./docs/plans/2025-12-02-documentation-cleanup-plan.md`
- **Cleanup Details:** This memory file

---

## Last Updated

2025-12-02 — Documentation cleanup & clarification session
