# Codebase Structure

```
brain_explore/
├── ies/                        # IES Framework project
│   ├── backend/                # FastAPI backend (was ies-backend/)
│   │   ├── src/ies_backend/
│   │   │   ├── api/
│   │   │   │   ├── profile.py           # Profile CRUD, capacity
│   │   │   │   ├── session.py           # Session processing, context
│   │   │   │   └── question_engine.py   # State detection, approach
│   │   │   ├── services/
│   │   │   │   ├── neo4j_client.py
│   │   │   │   ├── profile_service.py
│   │   │   │   ├── siyuan_client.py
│   │   │   │   ├── extraction_service.py
│   │   │   │   ├── session_context_service.py
│   │   │   │   ├── state_detection_service.py
│   │   │   │   ├── approach_selection_service.py
│   │   │   │   └── question_templates_service.py
│   │   │   └── schemas/
│   │   └── tests/
│   ├── CLAUDE.md               # IES-specific instructions
│   └── progress.md             # IES development progress
│
├── framework/                  # Framework Project (implementation)
│   ├── CLAUDE.md
│   └── progress.md
│
├── therapy/                    # Therapy Framework (content)
│   ├── CLAUDE.md
│   └── progress.md
│
├── library/                    # Shared: GraphRAG Python modules
│   ├── ingest/                 # Book processing
│   ├── graph/                  # Knowledge graph
│   ├── search/                 # Hybrid search
│   └── enrich/                 # Entity enrichment
│
├── scripts/                    # Shared: CLI scripts
├── books/                      # Shared: Source PDFs/EPUBs
├── docs/plans/                 # Design documents
├── archive/                    # Old/superseded files
│
├── .active-project             # Current project (ies|framework|therapy)
├── .claude/
│   ├── commands/               # Slash commands
│   ├── hooks/                  # SessionStart hook
│   └── settings.json           # Hook configuration
│
├── docker-compose.yml          # Neo4j + Qdrant
├── CLAUDE.md                   # Meta-level instructions
└── pyproject.toml
```

## Code Style
- Type hints encouraged
- Pydantic models for data structures
- Rich for CLI output
- No strict linting configured yet
