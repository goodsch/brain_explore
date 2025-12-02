# Library Knowledge System Design

**Date:** 2024-11-30
**Status:** Approved
**Purpose:** Process and index the therapy framework library for efficient, accurate, and dynamic utilization during exploration sessions.

---

## Overview

A GraphRAG-based system that:
1. Deeply understands the library (books, assessments, papers)
2. Recognizes concepts in session notes
3. Enriches sessions with relevant library content and external research
4. Creates structured, linked notes in SiYuan for later exploration

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        KNOWLEDGE LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ Vector Store│    │ Knowledge   │    │ Source Documents    │  │
│  │ (chunks +   │◄──►│ Graph       │◄──►│ (books, papers,     │  │
│  │ embeddings) │    │ (entities,  │    │ assessments)        │  │
│  └─────────────┘    │ relations)  │    └─────────────────────┘  │
│                     └─────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ query/retrieve
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PROCESSING LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ Concept     │    │ Enrichment  │    │ Research Agent      │  │
│  │ Extractor   │───►│ Agent       │───►│ (arXiv, web)        │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ write enriched notes
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       WORKING MEMORY                            │
├─────────────────────────────────────────────────────────────────┤
│                         SiYuan                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Session  │  │ Concepts │  │ Evidence │  │ Explore  │        │
│  │ Notes    │  │          │  │ /Sources │  │ Queue    │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

**Flow:**
1. Library processed once → populates vector store + knowledge graph
2. Sessions happen → raw notes captured
3. Post-session: Concept extractor identifies key ideas → Enrichment agent queries knowledge layer → Research agent fills gaps → Results written to SiYuan
4. User tags items for exploration → next session pulls those + graph context

---

## Library Processing Pipeline

```
  PDF/EPUB
     │
     ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐
│ Extract  │───►│ Clean &  │───►│ Chunk    │───►│ Embed     │
│ Text     │    │ Structure│    │ (semantic│    │ (vectors) │
│          │    │          │    │ sections)│    │           │
└──────────┘    └──────────┘    └──────────┘    └───────────┘
                     │                               │
                     ▼                               ▼
              ┌──────────────┐              ┌──────────────┐
              │ Entity       │              │ Vector Store │
              │ Extraction   │              │ (Qdrant)     │
              └──────────────┘              └──────────────┘
                     │
                     ▼
              ┌──────────────┐
              │ Knowledge    │
              │ Graph        │
              │ (Neo4j)      │
              └──────────────┘
```

**Processing Stages:**

1. **Extract** - ebook-mcp for EPUBs, marker/pymupdf for PDFs → raw text with structure
2. **Clean & Structure** - Identify chapters, sections, headers; strip artifacts; preserve hierarchy
3. **Chunk** - Split semantically (respect section boundaries, keep context)
4. **Embed** - Generate vectors for each chunk
5. **Entity Extraction** - LLM identifies:
   - Authors (who wrote it, who they cite)
   - Concepts (emotion regulation, executive function, metacognition...)
   - Theories/Models (Gross's process model, Barkley's EF theory...)
   - Relationships (X supports Y, X contradicts Y, X operationalizes Y)

**Metadata per chunk:**
- Source book/paper
- Chapter/section
- Page number (if available)
- Extracted entities
- Embedding vector

---

## Session Enrichment Pipeline

```
  Session Transcript / Notes
              │
              ▼
     ┌─────────────────┐
     │ CONCEPT         │  Extracts: claims, questions, tensions, new terms
     │ EXTRACTOR       │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ ENRICHMENT      │  Queries knowledge layer for each concept
     │ AGENT           │  Finds: supporting passages, graph connections
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ RESEARCH        │  For gaps: searches arXiv, downloads papers
     │ AGENT           │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ NOTE GENERATOR  │  Creates: concept notes, evidence notes,
     │                 │  connection links, explore tags
     └────────┬────────┘
              │
              ▼
         SiYuan MCP
```

**Concept Extractor Output:**
```yaml
- concept: "emotion regulation as skill vs trait"
  type: tension
  confidence: high
  context: "discussion about whether DERS measures capacity or habit"
```

**Enrichment Agent Adds:**
```yaml
- concept: "emotion regulation as skill vs trait"
  library_support:
    - source: "Handbook of Emotion Regulation - Gross"
      chapter: 3
      summary: "Gross distinguishes process model (skill) from trait measures"
  graph_connections:
    - related_to: "executive function"
    - operationalized_by: "DERS", "ERQ"
    - theorized_by: "Gross process model"
```

**Research Agent Adds:**
```yaml
- concept: "metacognitive awareness precedes change"
  gaps_found: "No direct library support"
  arxiv_results:
    - paper: "Metacognition in Psychotherapy: A Review"
      relevance: "Directly addresses sequencing question"
      action: "downloaded for review"
```

---

## SiYuan Integration & Tagging

**Note Structure:**
```
/Therapy Framework/
├── 1-Human Mind/
│   ├── Emotion Regulation/
│   │   ├── emotion-regulation.md        ← Concept note
│   │   ├── gross-process-model.md       ← Theory note
│   │   └── evidence/
│   │       ├── gross-ch3-summary.md
│   │       └── barkley-ef-er-link.md
├── _Evidence/
│   ├── books/
│   └── papers/
├── _Explore/                            ← Tagged for conversation
└── _Sessions/
```

**Tagging via SiYuan Attributes:**
```yaml
custom-attrs:
  explore: true
  explore-mode: "deep"    # deep | question | challenge | connect
  explore-prompt: "How does this fit with Barkley's model?"
  confidence: "low"
  evidence-strength: "moderate"
  last-enriched: "2024-11-30"
```

**Explore Modes:**
- `deep` - Tell me everything the library knows about this
- `question` - I have a specific question about this
- `challenge` - Stress test this idea
- `connect` - How does this relate to X?

**Session Start Query:**
```sql
SELECT * FROM blocks
WHERE custom-attrs.explore = true
ORDER BY custom-attrs.confidence ASC
```

---

## Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Vector Store | Qdrant (Docker) | Fast, good filtering, free |
| Knowledge Graph | Neo4j (Docker) | Industry standard, visualization |
| Embeddings | OpenAI ada-002 or nomic-embed-text | Cost vs privacy trade-off |
| LLM (processing) | Claude API | Best at entity extraction |
| LLM (enrichment) | Claude via Claude Code | Already integrated |
| Document Processing | marker (PDFs), ebooklib (EPUBs) | Quality extraction |
| Orchestration | Python + Claude Code | Existing workflow |
| Storage | SiYuan (MCP) | Already chosen |

**Docker Compose:**
```yaml
services:
  qdrant:
    image: qdrant/qdrant
    ports: ["6333:6333"]
    volumes: ["./data/qdrant:/qdrant/storage"]

  neo4j:
    image: neo4j:5
    ports: ["7474:7474", "7687:7687"]
    volumes: ["./data/neo4j:/data"]
    environment:
      NEO4J_AUTH: neo4j/password
```

**Package Structure:**
```
brain_explore/
├── library/
│   ├── ingest/
│   │   ├── extract.py
│   │   ├── chunk.py
│   │   └── embed.py
│   ├── graph/
│   │   ├── entities.py
│   │   ├── relations.py
│   │   └── neo4j_client.py
│   ├── search/
│   │   ├── vector.py
│   │   ├── graph.py
│   │   └── hybrid.py
│   └── enrich/
│       ├── extractor.py
│       ├── enricher.py
│       ├── researcher.py
│       └── writer.py
├── scripts/
│   ├── ingest_library.py
│   └── enrich_session.py
└── docker-compose.yml
```

**MCP Integration:**
```
mcp__library__search(query, mode="hybrid")
mcp__library__enrich_concept(concept, context)
mcp__library__find_gaps(concepts[])
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- Set up Docker (Qdrant + Neo4j)
- Build ingestion pipeline (extract → chunk → embed)
- Process 10 core books as proof of concept
- Basic vector search working

### Phase 2: Knowledge Graph (Week 2)
- Entity extraction prompts
- Relationship extraction
- Populate Neo4j from library
- Hybrid search (vector + graph)

### Phase 3: Enrichment Pipeline (Week 3)
- Concept extractor for session notes
- Enrichment agent (matches to library)
- Research agent (arXiv integration)
- SiYuan note writer

### Phase 4: Integration (Week 4)
- MCP server wrapping the library
- Tagging system in SiYuan
- Session start query (pull tagged items)
- End-to-end test with real session

### Phase 5: Refinement (Ongoing)
- Tune chunking/extraction quality
- Add remaining books
- Improve graph relationships
- Build explore queue dashboard

---

## Immediate Next Steps

1. Fix SiYuan API token (current blocker)
2. Set up Docker compose with Qdrant + Neo4j
3. Build basic ingestion for one book as test
4. Validate vector search works

---

## Open Questions

- Embeddings: OpenAI (better quality, cost) vs local nomic-embed (free, private)?
- Graph visualization: Neo4j browser sufficient or need custom UI?
- Session capture: Manual paste or automated from Claude Code transcript?
