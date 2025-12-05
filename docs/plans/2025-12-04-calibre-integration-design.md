# Calibre Integration Design

**Date:** 2025-12-04
**Status:** Design Complete, Ready for Implementation

## Problem

Books exist in 3 places with different identifiers:
- Calibre: integer ID + optional ISBN
- Neo4j: file path as identifier
- Readest: metadata.identifier (UUID from epub)

Result: Entity overlay shows "0 entities" when identifiers don't match.

## Solution

**Calibre as single source of truth** with Calibre book ID as canonical identifier everywhere.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Calibre (Source of Truth)                    │
│  brain_explore/calibre/library/                                 │
│  ├── metadata.db (SQLite catalog)                               │
│  └── Author/Book folders (epub/pdf files)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Ingestion      │  │  IES Backend    │  │  Readest        │
│  Pipeline       │  │  (FastAPI)      │  │  (Tauri app)    │
│                 │  │                 │  │                 │
│  • Watch for    │  │  • Book catalog │  │  • Browse books │
│    new books    │  │    from Calibre │  │    via backend  │
│  • Extract      │  │  • Entity API   │  │  • Open files   │
│    entities     │  │    by calibre_id│  │    directly     │
│  • Store in     │  │                 │  │  • Entity       │
│    Neo4j        │  │                 │  │    overlay      │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Neo4j Knowledge Graph                        │
│  Book nodes with calibre_id property                            │
│  Entity nodes linked via MENTIONS relationships                 │
└─────────────────────────────────────────────────────────────────┘
```

## Docker Setup

Add to `docker-compose.yml`:

```yaml
calibre:
  image: crocodilestick/calibre-web-automated:latest
  container_name: brain_explore_calibre
  environment:
    - PUID=1000
    - PGID=1000
    - TZ=America/Chicago
  volumes:
    - ./calibre/config:/config
    - ./calibre/ingest:/cwa-book-ingest
    - ./calibre/library:/calibre-library
  ports:
    - 8084:8083
  restart: unless-stopped
```

## Multi-Pass Ingestion Pipeline

### Pass 1: Structure (sync)
- Create Book node with `calibre_id`
- Chunk text into paragraphs/sections
- Extract entities: Concept, Person, Theory, Framework
- Create MENTIONS relationships
- Status: `entities_extracted`

### Pass 2: Relationships (async)
- Causal: CAUSES, ENABLES, INHIBITS, LEADS_TO
- Component: PART_OF, OPERATIONALIZES
- Contrast: CONTRASTS_WITH, ALTERNATIVE_TO
- Status: `relationships_mapped`

### Pass 3: Enrichment (async, LLM)
- Generate Reframes for top concepts
- Extract mechanisms
- Identify patterns
- Status: `enriched`

### Status Lifecycle
```
pending → chunked → entities_extracted → relationships_mapped → enriched
```

## Backend API Changes

### New Endpoints

```
GET /books
GET /books?search=ADHD
GET /books/{calibre_id}
GET /books/{calibre_id}/cover
```

### Updated Endpoint

```
GET /graph/entities/by-book/{calibre_id}
```

Direct lookup by calibre_id instead of hash/title matching.

## Neo4j Schema Update

```cypher
(:Book {
  calibre_id: 42,           # Primary identifier
  title: "...",
  author: "...",
  path: "/calibre-library/Author/Title (42)/book.epub",
  processing_status: "enriched",
  has_entities: true
})
```

## Readest Integration

1. New Library view fetches `GET /books`
2. User selects book → opens directly from Calibre path
3. `calibre_id` stored in book state
4. Entity overlay calls `/graph/entities/by-book/{calibre_id}`

## Implementation Phases

### Phase 1: Infrastructure
- [ ] Add Calibre service to docker-compose.yml
- [ ] Create calibre/ directory structure
- [ ] Start container and verify
- [ ] Seed with 10 test books

### Phase 2: Backend APIs
- [ ] Add `/books` endpoint (queries metadata.db)
- [ ] Add `/books/{id}/cover` endpoint
- [ ] Update entity endpoint for calibre_id
- [ ] Add `calibre_id` to Neo4j Book schema

### Phase 3: Ingestion Pipeline
- [ ] Create ingestion worker script
- [ ] Implement metadata.db polling
- [ ] Integrate entity extraction (Pass 1)
- [ ] Test: drop book → entities in Neo4j

### Phase 4: Readest Library
- [ ] Add Library view component
- [ ] Fetch and display books
- [ ] Open with calibre_id in state
- [ ] Entity overlay uses calibre_id

### Phase 5: Enrichment
- [ ] Add Pass 2 (relationships)
- [ ] Add Pass 3 (reframes, mechanisms)
- [ ] Processing status indicators
- [ ] Re-process option for failed books

## Related

- **Phase 2c Reframe API**: Already implemented, will be used by Pass 3
- **resources+.md**: ChatGPT conversation on structured thinking and ingestion requirements
- **Serena memory**: `calibre-integration-design-dec4.md`
