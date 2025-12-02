# Project: Therapy Framework (brain_explore)

## Purpose
Build a structured understanding of Chris's therapeutic worldview through AI-assisted knowledge development.

## Current State (2025-11-30)

### Status: GRAPHRAG LIBRARY SYSTEM OPERATIONAL

**Two systems now running:**

1. **SiYuan Knowledge Base** — For exploration and concept development
2. **GraphRAG Library System** — For querying 50 therapy books

### GraphRAG System

**Vector Store (Qdrant):** 27,523 chunks from 51 books
**Knowledge Graph (Neo4j):** 48,987 nodes, 121,299+ relationships

| Books with Entity Extraction | Entities | Relationships |
|------------------------------|----------|---------------|
| ACT (Hayes) | 59 | 36 |
| Emotion Regulation (Gross) | 151 | 16 |
| IFS (Schwartz) | 187 | 107 |
| Motivational Interviewing | 89 | 64 |
| Existential Psychotherapy (Yalom) | 132 | 67 |
| Body Keeps the Score (van der Kolk) | 75 | 53 |
| Developing Mind (Siegel) | 121 | 51 |
| Thinking Fast and Slow (Kahneman) | 73 | 50 |

**To use:**
```bash
docker compose up -d                        # Start services
python scripts/test_hybrid_search.py        # Test searches
python scripts/extract_entities.py --stats  # View graph stats
```

### SiYuan System

**Operational** — Two notebooks ready for exploration:
- Framework Project: Dashboard, templates, architecture docs
- Therapy Framework: 3 tracks, connections, first concept

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     brain_explore System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐     ┌──────────────────────────────────┐  │
│  │  SiYuan         │     │  GraphRAG Library                │  │
│  │  (Knowledge     │     │  ┌────────────┐  ┌────────────┐  │  │
│  │   Base)         │     │  │ Qdrant     │  │ Neo4j      │  │  │
│  │                 │     │  │ (Vectors)  │  │ (Graph)    │  │  │
│  │  - Exploration  │     │  │ 27K chunks │  │ 897 nodes  │  │  │
│  │  - Concepts     │     │  └────────────┘  └────────────┘  │  │
│  │  - Sessions     │     │                                  │  │
│  └─────────────────┘     │  Hybrid Search: vector + graph   │  │
│                          └──────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Claude Code + MCP                                       │   │
│  │  - siyuan-mcp (read/write knowledge base)               │   │
│  │  - ebook-mcp (read books)                               │   │
│  │  - arxiv (research papers)                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start Commands

| Command | Purpose |
|---------|---------|
| `/framework-session` | Build the system (meta work) |
| `/explore-session` | Explore therapeutic worldview (content) |

## Key Files

| Path | Purpose |
|------|---------|
| `CLAUDE.md` | Full project guidance for AI |
| `AGENTS.md` | This file — quick state snapshot |
| `progress-framework-project.md` | Framework/system progress |
| `progress-therapy-framework.md` | Exploration/content progress |
| `library/` | Python modules for GraphRAG |
| `scripts/` | CLI tools (ingest, extract, search) |
| `docker-compose.yml` | Qdrant + Neo4j containers |

## Next Steps

1. **Expand entity extraction** — Process remaining 42 books
2. **Session enrichment pipeline** — Post-session AI processing
3. **SiYuan integration** — Write GraphRAG discoveries to knowledge base
4. **Interactive interface** — CLI or web for library exploration
