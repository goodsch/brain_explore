# Future Serena Projects

As the Intelligent Exploration System develops, we'll create separate Serena projects for each component:

## Planned Projects

### 1. brain_explore (Current)
- **Path**: `/home/chris/dev/projects/codex/brain_explore`
- **Purpose**: GraphRAG library, entity extraction, knowledge processing
- **Languages**: Python

### 2. ies-plugin (Future)
- **Path**: TBD (likely `/home/chris/dev/projects/codex/ies-plugin`)
- **Purpose**: SiYuan plugin for AI-guided exploration
- **Languages**: TypeScript
- **Framework**: SiYuan Plugin API

### 3. ies-backend (EXISTS — inside brain_explore)
- **Path**: `/home/chris/dev/projects/codex/brain_explore/ies-backend`
- **Purpose**: FastAPI backend for IES
- **Languages**: Python
- **Framework**: FastAPI, Claude API
- **Status**: Phases 1-4 COMPLETE (Profile, Entities, Question Engine, Session Integration)

## Project Relationships

```
brain_explore (Knowledge Processing)
    │
    ├──► Provides: Neo4j graph, Qdrant vectors
    │
    ▼
ies-backend (API Layer)
    │
    ├──► Consumes: Neo4j, Qdrant, Claude API
    ├──► Provides: REST API for plugin
    │
    ▼
ies-plugin (SiYuan Interface)
    │
    ├──► Consumes: ies-backend API
    └──► Integrates: SiYuan UI
```

## When to Create New Projects

Create `ies-plugin` when:
- Starting SiYuan plugin development
- Need TypeScript-specific tooling

Create `ies-backend` when:
- Starting FastAPI backend development
- Need separate deployment/testing
