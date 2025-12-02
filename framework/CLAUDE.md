# Framework Project

**Scope:** Implementation of IES for therapy worldview exploration

This is the first implementation instance of IES. Work here is about configuring IES for this specific use case and testing features.

## What This Is

```
IES (generic framework)
    │
    └──► Framework Project (THIS — implementation for chris + therapy)
              │
              └──► Therapy Framework (the content being developed)
```

## Quick Start

```bash
# Ensure backend is running
cd ../ies/backend && IES_NEO4J_PASSWORD=brainexplore uv run uvicorn ies_backend.main:app --host 0.0.0.0 --port 8081

# Start Docker services
docker compose up -d
```

## Commands

| Command | Purpose |
|---------|---------|
| `/framework-session` | Meta work — testing/configuring the system |
| `/explore-session` | Content work — exploring therapeutic worldview |
| `/end-session` | Close session, trigger entity extraction |
| `/onboard-profile` | Build user profile conversationally |
| `/check-in` | Session capacity check-in |

## Configuration

**User:** chris
**Domain:** Therapeutic worldview
**Knowledge substrate:** 51 therapy books (48,987 nodes in Neo4j)

## SiYuan Notebook

Framework Project notebook:
- `/Project Map` — Dashboard
- `/Current State/` — Active work, blockers
- `/Sessions/` — Session logs
- `/Templates/` — Concept, session templates

## What Belongs Here

✅ User profile configuration
✅ Session logs from testing IES
✅ Implementation-specific adjustments
✅ Integration between IES and Therapy Framework

❌ Generic IES development (→ ies/)
❌ Actual therapy content (→ therapy/)
