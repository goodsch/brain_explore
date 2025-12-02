# brain_explore

*A system for exploring and developing therapeutic worldviews using AI-guided conversations*

## What This Is

**brain_explore** is an AI-powered exploration tool built with three layers:

1. **IES** (Intelligent Exploration System) — Backend API + SiYuan plugin for guided conversations
2. **Framework Project** — Configuration & deployment for this therapy instance
3. **Therapy Framework** — The evolving therapeutic worldview we're developing

**Current Status:** IES backend + plugin are production-ready. Content development in progress.

## Quick Start

### Prerequisites

```bash
# Required tools
- uv (Python package manager)  # Install: curl -LsSf https://astral.sh/uv/install.sh | sh
- node 18+                      # Install: https://nodejs.org/
- docker & docker-compose       # Install: https://docs.docker.com/
- SiYuan (community or pro)     # Install: https://b3log.org/siyuan/
```

### Installation (5 minutes)

1. **Clone & enter project**
   ```bash
   cd brain_explore
   ```

2. **Start Docker services** (Neo4j + Qdrant)
   ```bash
   docker compose up -d
   # Verify: curl http://localhost:7474 should return Neo4j page
   ```

3. **Set up configuration**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys:
   #   - ANTHROPIC_API_KEY=sk-ant-...
   #   - OPENAI_API_KEY=sk-...
   #   - IES_SIYUAN_TOKEN=... (from SiYuan settings)
   ```

4. **Start backend**
   ```bash
   cd ies/backend
   uv run uvicorn ies_backend.main:app --host 0.0.0.0 --port 8081
   ```

5. **Build & enable plugin**
   ```bash
   cd ies/plugin
   npm install
   npm run build
   # Plugin appears in SiYuan settings → Plugins
   ```

### First Run

1. Open SiYuan sidebar
2. Click "Start Session" in IES plugin
3. Type a question (try: "What's most important for therapeutic change?")
4. End session → System extracts entities and creates SiYuan page

## Project Structure

```
brain_explore/
├── ies/                       # Intelligent Exploration System (tool layer)
│   ├── backend/               # FastAPI API (4,496 lines Python)
│   │   ├── src/ies_backend/   # API endpoints, services, schemas
│   │   └── tests/             # 61 unit tests
│   ├── plugin/                # SiYuan plugin (14,092 lines TS/Svelte)
│   ├── CLAUDE.md              # IES project instructions
│   └── progress.md            # Development progress & architecture
│
├── framework/                 # Framework Project (config layer)
│   ├── CLAUDE.md              # Framework instructions
│   ├── progress.md            # Implementation roadmap
│   └── config/                # Config files (to be created in Phase 6)
│
├── therapy/                   # Therapy Framework (content layer)
│   ├── CLAUDE.md              # Content development instructions
│   ├── progress.md            # Concept development progress
│   └── concepts/              # Individual concept explorations
│
├── library/                   # Shared GraphRAG modules
├── scripts/                   # Shared CLI tools
├── books/                     # 63 therapy/psychology books (PDF/EPUB)
├── docs/                      # Documentation & design plans
├── docker-compose.yml         # Infrastructure (Neo4j + Qdrant)
├── .env.example               # Configuration template
└── CLAUDE.md                  # Workspace overview
```

## Documentation

- **[CLAUDE.md](./CLAUDE.md)** — Workspace overview & quick reference
- **[ies/progress.md](./ies/progress.md)** — What's been built, architecture decisions
- **[framework/progress.md](./framework/progress.md)** — Configuration system roadmap
- **[therapy/progress.md](./therapy/progress.md)** — Concept development status
- **[docs/plans/](./docs/plans/)** — Architecture & design documents

## Development

### Making Code Changes

```bash
# 1. Make changes
# 2. Run tests
cd ies/backend && PYTHONPATH=src uv run pytest

# 3. Commit
git add . && git commit -m "Description of change"

# 4. Update progress file
# Edit {project}/progress.md with what you did
```

### Working on Content

```bash
# Use exploration sessions to develop concepts
/explore-session

# System handles:
# 1. Socratic dialogue with Claude
# 2. Entity extraction (automatic)
# 3. Storage in Neo4j
# 4. Literature linking (Qdrant search)
# 5. SiYuan document creation
```

### Common Commands

```bash
# Start everything
docker compose up -d
cd ies/backend && uv run uvicorn ies_backend.main:app --host 0.0.0.0 --port 8081

# Run tests
cd ies/backend && PYTHONPATH=src uv run pytest

# Check backend
curl http://localhost:8081/docs

# Build plugin
cd ies/plugin && npm run build

# View logs
docker compose logs -f neo4j
docker compose logs -f qdrant
```

## Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Backend** | ✅ Production | 16 REST endpoints, all working |
| **Plugin** | ✅ Production | iOS-capable (works on iPad) |
| **Tests** | ✅ | 61 unit tests passing |
| **Config System** | 🔲 Planned | Phase 6 work |
| **Content** | 🟡 Developing | 1 concept done, 5 more identified |

### What Works Now

- ✅ Full end-to-end session flow (start → chat → extract → store)
- ✅ Entity extraction via Claude API
- ✅ Literature linking (entities linked to source books)
- ✅ iOS support (via forwardProxy API)
- ✅ SiYuan integration (concepts saved as documents)

### What's Next

**Phase 6 (Configuration):**
1. Extract hardcoded values to configuration files
2. Build user profile management
3. Create domain configuration system

**Phase 7+ (Content & Generalization):**
1. Develop more therapeutic concepts
2. Ground concepts in literature
3. Generalize IES for other domains

## Known Limitations

**Current Design Choices:**
- IES is currently therapy-specific (not generic yet)
- Some values hardcoded for chris + therapy use case
- Configuration system not implemented (Phase 6)
- Plugin requires manual settings (to be automated)

**Why This Is OK:**
- System works great for therapy use
- Clear roadmap to generalization
- Not blocking content development
- Configuration can be added incrementally

See [docs/plans/2025-12-02-documentation-cleanup-plan.md](./docs/plans/2025-12-02-documentation-cleanup-plan.md) for evolution plan.

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│          SiYuan (Frontend)                       │
│  ├─ Sidebar Plugin (IES Chat UI)               │
│  └─ Documents (Concepts, Session Logs)         │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│       IES Backend (Port 8081)                   │
│  ├─ Profile Service                            │
│  ├─ Session Management                         │
│  ├─ Entity Extraction (Claude API)            │
│  ├─ Literature Linking (Qdrant)               │
│  └─ Question Engine (State + Approach)        │
└────┬──────────┬──────────────┬─────────────────┘
     │          │              │
     ▼          ▼              ▼
  Neo4j      Qdrant      Claude API
 (Graph)   (Vectors)    (Entity Extraction)
```

## Key Metrics

| Metric | Value |
|--------|-------|
| **Backend Code** | 4,496 lines Python |
| **Plugin Code** | 14,092 lines TS/Svelte |
| **Unit Tests** | 61 passing |
| **API Endpoints** | 16 |
| **Question States** | 8 (opening, exploring, probing, etc.) |
| **Question Approaches** | 5 (socratic, metaphor, narrative, etc.) |
| **Question Templates** | 30 |
| **Books in Library** | 63 |
| **Neo4j Nodes** | 48,987 |
| **Qdrant Chunks** | 27,523 |

## Key Concepts

### Narrow Window of Awareness
Humans are aware enough to create meaning (our superpower) but not enough to see our own blind spots (our limitation). This paradox is both the source of suffering and capacity for growth.

### Hidden Function of Symptoms
Symptoms aren't problems to eliminate; they're solutions people are using. Anxiety protects, avoidance prevents hurt, drinking numbs pain. Therapy changes conditions so better options emerge.

### Conditions for Change
No pain is inherently unchangeable. Change is blocked not by unwillingness but by missing conditions. Therapy's job: shift conditions so change becomes the better option.

## Support

- **Issues?** Check `.env` configuration first
- **Tests failing?** Ensure Docker services are running: `docker compose ps`
- **Plugin not appearing?** Check SiYuan settings → Plugins → look for "IES Explorer"
- **Backend unreachable?** Verify port 8081 is accessible: `curl http://localhost:8081/docs`

## Next Steps

1. **Try an exploration session** — `/explore-session` in SiYuan
2. **Read progress files** — Understand what's been built
3. **Run tests** — Verify your setup works
4. **Review architecture** — Read `ies/progress.md` for technical details
5. **Contribute** — Content development or backend features

---

**Last Updated:** 2025-12-02
**Active Project:** ies (determined by `.active-project` file)
**Status:** Phase 5 Complete, Phase 6 Planned
