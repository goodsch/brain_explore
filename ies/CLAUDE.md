# IES (Intelligent Exploration System)

**Scope:** Generic AI-guided exploration framework for SiYuan

This is the reusable framework layer. Work here is about building features that any implementation can use.

## Current Phase

Phase 4 COMPLETE. Next: Phase 5 (SiYuan Plugin)

## Quick Start

```bash
# Start backend
cd backend && IES_NEO4J_PASSWORD=brainexplore uv run uvicorn ies_backend.main:app --host 0.0.0.0 --port 8081

# Run tests
cd backend && uv run pytest
```

## Structure

```
ies/
├── backend/           # FastAPI backend (Phases 1-4 complete)
│   ├── src/ies_backend/
│   │   ├── api/       # Profile, session, question-engine endpoints
│   │   ├── services/  # Business logic
│   │   └── schemas/   # Pydantic models
│   └── tests/
├── plugin/            # SiYuan plugin (future - Phase 5)
├── CLAUDE.md          # This file
└── progress.md        # IES development progress
```

## Key Decisions

- **Port 8081** (8000 occupied by Portainer)
- **Hybrid integration:** Claude Code handles conversation, backend called at key moments
- **Question Engine:** 8 states, 5 approaches, profile-aware adaptations

## Documentation

- **SiYuan:** IES notebook (specs, mockups, architecture)
- **Design docs:** `../docs/plans/2025-12-01-*.md`

## What Belongs Here

✅ Backend features, API endpoints, schemas
✅ Plugin development
✅ Generic specs that apply to any implementation
✅ Framework-level architecture decisions

❌ User-specific configuration (→ framework/)
❌ Content exploration (→ therapy/)
❌ Session logs from using the system (→ framework/)
