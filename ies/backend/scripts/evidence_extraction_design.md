# Evidence Extraction Pipeline Design

**Status:** Design Phase
**Author:** Backend Developer Agent
**Date:** December 8, 2025
**Target:** IES Backend Layer 2

---

## Executive Summary

Design for a batch processing pipeline that extracts text chunks from Qdrant vector store and creates MENTIONS relationships to global entities in Neo4j. This populates the evidence layer needed for the `get_entity_evidence()` endpoint in Flow Mode.

**Current State:**
- Qdrant: 38,893 text chunks with embeddings
- Neo4j: 10 Chunk nodes, ~1,400 Book→Entity MENTIONS
- Neo4j: ~300 global entities (Concept, Theory, Researcher, etc.)
- User-specific GROUNDED_IN relationships working via LiteratureLinkingService

**Goal State:**
- Neo4j: All 38,893 chunks as Chunk nodes
- Chunk→Entity MENTIONS relationships (global, not user-specific)
- Support incremental updates as new chunks are added
- Enable rich evidence display in Flow Mode

---

## 1. Architecture Overview

### 1.1 Pipeline Components

```
┌─────────────────────────────────────────────────────────────┐
│  QDRANT VECTOR STORE                                        │
│  - 38,893 text chunks                                       │
│  - Embeddings (1536-dim)                                    │
│  - Payload: chunk_id, content, source_file, chapter, etc.   │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│  EXTRACTION SERVICE                                         │
│  ─────────────────────────────────────────────────────────  │
│  1. Batch processor (scroll through Qdrant)                 │
│  2. Entity matcher (semantic search for each chunk)         │
│  3. Neo4j writer (create Chunk nodes + MENTIONS rels)       │
│  4. Progress tracker (idempotent, resumable)                │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│  NEO4J KNOWLEDGE GRAPH                                      │
│  - Chunk nodes (id, content, source_file, chapter, etc.)    │
│  - Entity nodes (Concept, Theory, Researcher, etc.)         │
│  - Chunk→Entity MENTIONS (score, created_at)                │
│  - Chunk→Book FROM_BOOK (link to source)                    │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

1. **Fetch Phase**: Retrieve chunks from Qdrant in batches
2. **Match Phase**: For each chunk, find relevant entities via vector search
3. **Write Phase**: Create Chunk nodes and MENTIONS relationships in Neo4j
4. **Track Phase**: Record progress for resumability

---

## 2. Implementation Strategy

### 2.1 Reuse Existing Patterns

**LiteratureLinkingService provides foundation:**
- Qdrant connection and query patterns
- OpenAI embedding generation
- Score threshold filtering (0.45)
- Neo4j Chunk node creation pattern

**Key differences from LiteratureLinkingService:**
1. **Direction**: Entity → Chunks (user-specific) vs. Chunk → Entities (global)
2. **Relationship**: GROUNDED_IN (personal) vs. MENTIONS (global)
3. **Scale**: On-demand (session time) vs. Batch (all chunks)
4. **Query**: Search chunks for entity vs. Search entities for chunk

### 2.2 Entity Matching Strategy

**Option A: Embed chunk, search entity names** (RECOMMENDED)
- Generate embedding for chunk content
- Search against pre-embedded entity names/descriptions
- Filter by similarity threshold (0.45)
- Create MENTIONS for top matches

**Option B: NER-style extraction**
- Use LLM to extract entity names from chunk text
- Match extracted names to graph entities
- Higher precision, higher cost, slower

**Recommendation:** Start with Option A (semantic search), evaluate precision/recall, fall back to Option B if needed.

### 2.3 Batch Processing Design

```python
class EvidenceExtractionService:
    """Extract chunks from Qdrant and link to entities in Neo4j."""

    BATCH_SIZE = 100  # Process 100 chunks at a time
    ENTITY_LIMIT = 5  # Max entities per chunk
    SCORE_THRESHOLD = 0.45  # Minimum similarity score

    async def extract_all_evidence(
        self,
        resume_from: str | None = None,
        max_chunks: int | None = None,
    ) -> dict:
        """
        Main extraction pipeline.

        Args:
            resume_from: chunk_id to resume from (for interrupted runs)
            max_chunks: Process at most this many chunks (for testing)

        Returns:
            Stats dict with counts and progress
        """
```

---

## 3. Neo4j Schema and Queries

### 3.1 Chunk Node Schema

```cypher
(:Chunk {
    id: str,              # Unique chunk identifier (from Qdrant)
    chunk_id: str,        # Same as id (for compatibility with LiteratureLinkingService)
    content: str,         # Full text content (truncated to 2000 chars for storage)
    source_file: str,     # Path to source book/document
    chapter: str?,        # Chapter/section identifier
    section_title: str?,  # Section title if available
    page_start: int?,     # Starting page number
    page_end: int?,       # Ending page number
    token_count: int?,    # Token count from Qdrant
    created_at: datetime, # When chunk was added to Neo4j
    indexed_at: datetime  # When chunk was indexed for MENTIONS
})
```

### 3.2 Create Chunk with MENTIONS

```cypher
// Create or update Chunk node
MERGE (c:Chunk {id: $chunk_id})
ON CREATE SET
    c.chunk_id = $chunk_id,
    c.content = $content,
    c.source_file = $source_file,
    c.chapter = $chapter,
    c.section_title = $section_title,
    c.page_start = $page_start,
    c.page_end = $page_end,
    c.token_count = $token_count,
    c.created_at = $now
ON MATCH SET
    c.indexed_at = $now

// Link to source book (if Book node exists)
WITH c
OPTIONAL MATCH (b:Book)
WHERE b.path CONTAINS $source_file
    OR $source_file CONTAINS b.path
FOREACH (_ IN CASE WHEN b IS NOT NULL THEN [1] ELSE [] END |
    MERGE (c)-[:FROM_BOOK]->(b)
)

// Create MENTIONS relationships to entities
WITH c
UNWIND $entities AS entity
MATCH (e {name: entity.name})
MERGE (c)-[r:MENTIONS]->(e)
ON CREATE SET
    r.score = entity.score,
    r.created_at = $now
ON MATCH SET
    r.score = CASE WHEN r.score < entity.score THEN entity.score ELSE r.score END

RETURN c.id, count(DISTINCT e) as entities_linked
```

### 3.3 Progress Tracking Query

```cypher
// Store extraction progress
MERGE (p:ExtractionProgress {id: 'evidence_extraction'})
SET
    p.last_chunk_id = $last_chunk_id,
    p.chunks_processed = $chunks_processed,
    p.relationships_created = $relationships_created,
    p.updated_at = $now
RETURN p
```

### 3.4 Resume Query

```cypher
// Get last processed chunk
MATCH (p:ExtractionProgress {id: 'evidence_extraction'})
RETURN p.last_chunk_id as last_chunk_id,
       p.chunks_processed as chunks_processed
```

---

## 4. Implementation Steps

### Phase 1: Core Service (1-2 hours)

**File:** `/ies/backend/src/ies_backend/services/evidence_extraction_service.py`

1. Create `EvidenceExtractionService` class
2. Implement Qdrant scroll/pagination logic
3. Implement entity matching via semantic search
4. Implement Neo4j Chunk creation with MENTIONS
5. Add progress tracking and resumability

### Phase 2: Entity Embedding Cache (30 min)

**Challenge:** We need to search "which entities match this chunk?"
- Can't search Qdrant for entity names (entities aren't in Qdrant)
- Solution: Pre-compute embeddings for all entity names/descriptions

**Options:**
1. Embed on-the-fly: For each chunk, embed all ~300 entity names, compute cosine similarity
2. Use Qdrant collection: Create separate `entities` collection with entity embeddings
3. Use in-memory cache: Pre-embed entities at service startup, cache in memory

**Recommendation:** Option 2 (Qdrant collection) for scalability and persistence.

### Phase 3: CLI Script (30 min)

**File:** `/ies/backend/scripts/extract_evidence.py`

```python
#!/usr/bin/env python3
"""
Extract evidence from Qdrant chunks and link to Neo4j entities.

Usage:
    # Full extraction
    uv run python scripts/extract_evidence.py

    # Resume from last checkpoint
    uv run python scripts/extract_evidence.py --resume

    # Test with first 100 chunks
    uv run python scripts/extract_evidence.py --limit 100

    # Force re-index (delete existing MENTIONS)
    uv run python scripts/extract_evidence.py --force
"""
```

### Phase 4: Testing (1 hour)

**File:** `/ies/backend/tests/test_evidence_extraction.py`

Tests:
1. Chunk node creation with all properties
2. MENTIONS relationship creation with scores
3. FROM_BOOK relationship to source books
4. Progress tracking and resumability
5. Idempotency (re-running doesn't duplicate)
6. Score threshold filtering

### Phase 5: Monitoring & Validation (30 min)

1. Add logging for progress (chunks/sec, entities found)
2. Add validation query to check results
3. Add health check endpoint for extraction status

---

## 5. Entity Embedding Collection Design

### 5.1 Create Entities Collection in Qdrant

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(host="localhost", port=6333)

client.create_collection(
    collection_name="brain_explore_entities",
    vectors_config=VectorParams(
        size=1536,  # text-embedding-3-small
        distance=Distance.COSINE,
    ),
)
```

### 5.2 Populate Entities Collection

```python
async def index_entities_to_qdrant():
    """
    Pre-compute embeddings for all entities in Neo4j.
    Stores in Qdrant for efficient chunk→entity matching.
    """
    # Get all entities from Neo4j
    query = """
    MATCH (e)
    WHERE e.name IS NOT NULL
        AND labels(e)[0] IN [
            'Concept', 'Theory', 'Researcher', 'Person',
            'Framework', 'Assessment', 'Method', 'Mechanism'
        ]
    RETURN e.name as name,
           labels(e)[0] as type,
           e.description as description
    """

    entities = await Neo4jClient.execute_query(query, {})

    # Generate embeddings
    for entity in entities:
        # Combine name + description for richer embedding
        text = f"{entity['name']}: {entity.get('description', '')}"
        embedding = embed_text(text)

        # Store in Qdrant
        qdrant.upsert(
            collection_name="brain_explore_entities",
            points=[{
                "id": entity['name'],
                "vector": embedding,
                "payload": {
                    "name": entity['name'],
                    "type": entity['type'],
                    "description": entity.get('description'),
                },
            }],
        )
```

### 5.3 Entity Matching for Chunk

```python
def find_entities_for_chunk(chunk_text: str) -> list[dict]:
    """
    Find entities that should be mentioned by this chunk.

    Args:
        chunk_text: Text content of the chunk

    Returns:
        List of {name, type, score} dicts for matching entities
    """
    # Embed chunk
    chunk_embedding = embed_text(chunk_text)

    # Search entities collection
    results = qdrant.query_points(
        collection_name="brain_explore_entities",
        query=chunk_embedding,
        limit=10,  # Get top 10 candidates
        score_threshold=0.45,  # Minimum similarity
    )

    # Return entity matches
    return [
        {
            "name": r.payload["name"],
            "type": r.payload["type"],
            "score": r.score,
        }
        for r in results.points
        if r.score >= SCORE_THRESHOLD
    ][:ENTITY_LIMIT]  # Top 5
```

---

## 6. Performance Considerations

### 6.1 Batch Size Tuning

- **Too small** (< 50): Overhead from network round-trips
- **Too large** (> 500): Memory pressure, slow failure recovery
- **Recommended:** 100-200 chunks per batch

### 6.2 Rate Limiting

- OpenAI API: 3,500 requests/min (text-embedding-3-small)
- At 100 chunks/batch with 1 embedding call each: ~1.7 batches/sec = 102/min
- Safe margin: Process ~50 chunks/min = 2,000 chunks/hour
- Full 38,893 chunks: ~20 hours (acceptable for initial run)

**Optimization:** Batch embedding calls (up to 2,048 inputs per request)

### 6.3 Neo4j Write Performance

- Use `UNWIND` for batch relationship creation
- Write 100 chunks + relationships in single transaction
- Expected throughput: ~1,000 chunks/min

### 6.4 Parallelization

**Phase 1:** Single-threaded pipeline
**Phase 2:** If needed, partition by source_file or chunk_id prefix

---

## 7. Incremental Update Strategy

### 7.1 Detecting New Chunks

```python
async def get_unindexed_chunks() -> list[str]:
    """
    Find chunks in Qdrant that haven't been indexed to Neo4j yet.

    Returns:
        List of chunk_ids not yet in Neo4j
    """
    # Get all chunk_ids from Neo4j
    neo4j_chunks = await Neo4jClient.execute_query(
        "MATCH (c:Chunk) RETURN c.id as id",
        {}
    )
    neo4j_chunk_ids = {r['id'] for r in neo4j_chunks}

    # Get all chunk_ids from Qdrant (expensive, cache this)
    qdrant_chunks = qdrant.scroll(
        collection_name="brain_explore_library",
        with_payload=["chunk_id"],
        with_vectors=False,
        limit=10000,
    )

    # Return difference
    qdrant_chunk_ids = {p.payload['chunk_id'] for p in qdrant_chunks[0]}
    return list(qdrant_chunk_ids - neo4j_chunk_ids)
```

### 7.2 Scheduled Updates

**Option A:** Cron job (daily at 3am)
```bash
0 3 * * * cd /path/to/ies/backend && uv run python scripts/extract_evidence.py --incremental
```

**Option B:** On-demand via API endpoint
```python
@router.post("/admin/extract-evidence")
async def trigger_evidence_extraction():
    """Admin endpoint to trigger evidence extraction."""
    # Run in background task
    background_tasks.add_task(
        EvidenceExtractionService().extract_all_evidence
    )
    return {"status": "started"}
```

---

## 8. Validation and Quality Checks

### 8.1 Post-Extraction Validation

```cypher
// Check: Every Chunk should have at least one MENTIONS
MATCH (c:Chunk)
WHERE NOT (c)-[:MENTIONS]->()
RETURN count(c) as orphaned_chunks

// Check: Distribution of MENTIONS per chunk
MATCH (c:Chunk)-[r:MENTIONS]->()
WITH c, count(r) as mention_count
RETURN mention_count, count(c) as chunk_count
ORDER BY mention_count

// Check: Top entities by chunk mentions
MATCH (c:Chunk)-[:MENTIONS]->(e)
WITH e, count(c) as chunk_count
RETURN e.name, labels(e)[0] as type, chunk_count
ORDER BY chunk_count DESC
LIMIT 20
```

### 8.2 Quality Metrics

Track during extraction:
- **Coverage:** % of chunks with at least 1 MENTIONS
- **Density:** Average MENTIONS per chunk
- **Precision:** Manual spot-check of 50 random Chunk→Entity links
- **Score distribution:** Histogram of similarity scores

Target thresholds:
- Coverage: > 80% (some chunks may be too generic)
- Density: 2-4 entities per chunk (based on MAX_LINKS_PER_ENTITY)
- Precision: > 70% (human-judged correctness)

---

## 9. Error Handling and Recovery

### 9.1 Failure Scenarios

1. **Qdrant connection lost**
   - Retry with exponential backoff
   - Resume from last checkpoint

2. **Neo4j transaction timeout**
   - Reduce batch size
   - Retry failed batch

3. **OpenAI rate limit**
   - Sleep and retry with backoff
   - Track rate limit headers

4. **Entity not found in Neo4j**
   - Log warning, skip MENTIONS creation
   - Don't fail entire batch

### 9.2 Idempotency Guarantees

- `MERGE` on Chunk ensures no duplicates
- `MERGE` on MENTIONS ensures no duplicate relationships
- `ON MATCH SET` updates scores if better match found
- Progress tracking allows resuming from checkpoint

---

## 10. Testing Strategy

### 10.1 Unit Tests

```python
class TestEvidenceExtraction:
    async def test_chunk_node_creation(self):
        """Test Chunk node is created with all properties."""

    async def test_mentions_relationship_creation(self):
        """Test MENTIONS relationships are created with scores."""

    async def test_from_book_relationship(self):
        """Test FROM_BOOK links chunk to source book."""

    async def test_progress_tracking(self):
        """Test progress is saved and can be resumed."""

    async def test_idempotency(self):
        """Test re-running doesn't create duplicates."""

    async def test_score_filtering(self):
        """Test only high-confidence matches are kept."""
```

### 10.2 Integration Tests

```python
class TestEvidenceExtractionIntegration:
    async def test_end_to_end_small_batch(self):
        """Test extraction of 10 chunks end-to-end."""

    async def test_resume_from_checkpoint(self):
        """Test extraction resumes from saved progress."""

    async def test_entity_embedding_cache(self):
        """Test entity embeddings are generated correctly."""
```

### 10.3 Manual Validation

1. Extract 100 chunks
2. Manually inspect 10 random Chunk→Entity MENTIONS
3. Check precision: Are the entities actually mentioned in the chunk?
4. Check recall: Sample 5 chunks, identify entities manually, compare

---

## 11. Monitoring and Observability

### 11.1 Logging

```python
import logging

logger = logging.getLogger(__name__)

# Progress logging
logger.info(f"Processing batch {batch_num}/{total_batches}")
logger.info(f"Chunks processed: {chunks_processed}/{total_chunks} ({progress_pct:.1f}%)")
logger.info(f"Entities linked: {relationships_created}")
logger.info(f"Processing rate: {chunks_per_sec:.2f} chunks/sec")

# Error logging
logger.warning(f"No entities found for chunk {chunk_id}")
logger.error(f"Failed to create MENTIONS for chunk {chunk_id}: {error}")
```

### 11.2 Metrics

Track in-memory, expose via `/admin/extraction-status`:
```json
{
  "status": "running" | "completed" | "failed",
  "chunks_processed": 1234,
  "total_chunks": 38893,
  "progress_percent": 3.17,
  "relationships_created": 4567,
  "avg_entities_per_chunk": 3.7,
  "chunks_per_second": 45.2,
  "estimated_completion": "2025-12-08T15:30:00Z",
  "errors": 12,
  "last_error": "Qdrant timeout at chunk xyz"
}
```

---

## 12. Future Enhancements

### 12.1 Phase 2: Bi-directional Search

Currently planned: Chunk → Entities (semantic search)

Future: Also support Entity → Chunks (inverse index)
- Pre-compute which chunks mention each entity
- Store as inverted index in Redis or Neo4j
- Enables instant retrieval for `get_entity_evidence()`

### 12.2 Phase 3: Contextual Embeddings

Current: Embed entire chunk as single vector

Future: Generate multiple embeddings per chunk
- Sentence-level embeddings
- Paragraph-level embeddings
- Enables finer-grained evidence retrieval

### 12.3 Phase 4: LLM-based Extraction

Current: Semantic search (fast, lower precision)

Future: Hybrid approach
- Semantic search for candidates (top 20)
- LLM verification for precision (top 5)
- Extract specific quotes/snippets where entity is mentioned

---

## 13. Dependencies

### Required Packages

Already in project:
- `qdrant-client` (Qdrant vector store)
- `openai` (embeddings)
- `neo4j` (graph database)
- `fastapi` (async framework)
- `pydantic` (schemas)

No new dependencies needed.

### Infrastructure

Already running:
- Qdrant: `localhost:6333`
- Neo4j: `localhost:7687`
- OpenAI API key in environment

---

## 14. Timeline Estimate

| Phase | Task | Estimate |
|-------|------|----------|
| 1 | Core service implementation | 2 hours |
| 2 | Entity embedding collection setup | 1 hour |
| 3 | CLI script | 30 min |
| 4 | Unit tests | 1 hour |
| 5 | Integration tests | 1 hour |
| 6 | Initial extraction run | 20 hours (background) |
| 7 | Validation and tuning | 2 hours |
| **Total** | **Development time** | **7.5 hours** |

Initial extraction runs in background overnight, doesn't block development.

---

## 15. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenAI rate limits | Slow extraction | Batch embeddings, implement backoff |
| Low match precision | Poor evidence quality | Start with 0.45 threshold, tune up if needed |
| Neo4j memory pressure | Slow writes | Batch writes, monitor memory |
| Qdrant scroll timeout | Extraction fails | Implement checkpointing, resume logic |
| Entity embeddings too generic | Low match quality | Include descriptions in embedding text |

---

## 16. Success Criteria

1. **Completeness:** All 38,893 Qdrant chunks are Chunk nodes in Neo4j
2. **Connectivity:** > 80% of chunks have at least 1 MENTIONS relationship
3. **Quality:** Manual validation shows > 70% precision
4. **Performance:** Extraction completes in < 24 hours
5. **Resumability:** Can resume from checkpoint after interruption
6. **Idempotency:** Re-running doesn't create duplicates
7. **Evidence API:** `get_entity_evidence()` returns rich results for test entities

---

## 17. Next Steps After Design Approval

1. Review this design document with team
2. Confirm entity embedding strategy (Qdrant collection vs. in-memory)
3. Decide on initial score threshold (0.45 recommended)
4. Implement Phase 1 (core service)
5. Run pilot extraction on 100 chunks
6. Validate precision/recall
7. Tune threshold and proceed with full extraction

---

## Appendix A: Example Evidence Retrieval

### Before Pipeline

```cypher
// Query for "ADHD" evidence
MATCH (c:Chunk)-[:MENTIONS]->(e {name: "ADHD"})
RETURN count(c)
// Result: 0 (no Chunk→Entity MENTIONS exist yet)
```

### After Pipeline

```cypher
// Query for "ADHD" evidence
MATCH (c:Chunk)-[:MENTIONS]->(e {name: "ADHD"})
OPTIONAL MATCH (c)-[:FROM_BOOK]->(b:Book)
RETURN c.content, c.source_file, c.chapter, b.title, count(*) OVER () as total
LIMIT 5
// Result: 50+ evidence passages from multiple books
```

API response:
```json
{
  "entity_name": "ADHD",
  "evidence": [
    {
      "id": "ADHD_20:index_split_000.html:30",
      "text": "The cutting-edge work of a neuroscientist...",
      "source_title": "ADHD 2.0",
      "source_author": "Edward M. Hallowell",
      "location": {"chapter": "20"},
      "confidence": 0.87,
      "source_type": "chunk"
    }
  ],
  "total_count": 52,
  "sources_searched": 8
}
```

---

## Appendix B: Neo4j Queries for Monitoring

### Extraction Progress

```cypher
// Current extraction status
MATCH (p:ExtractionProgress {id: 'evidence_extraction'})
RETURN p.chunks_processed as processed,
       p.relationships_created as relationships,
       p.last_chunk_id as last_chunk,
       p.updated_at as last_update
```

### Chunk Coverage by Book

```cypher
// Which books have chunks indexed?
MATCH (b:Book)
OPTIONAL MATCH (c:Chunk)-[:FROM_BOOK]->(b)
WITH b, count(c) as chunk_count
RETURN b.title, b.author, chunk_count
ORDER BY chunk_count DESC
```

### Top Entities by Evidence Count

```cypher
// Which entities have the most evidence?
MATCH (c:Chunk)-[:MENTIONS]->(e)
WITH e, count(c) as evidence_count
RETURN e.name, labels(e)[0] as type, evidence_count
ORDER BY evidence_count DESC
LIMIT 20
```

### Quality Check: Low-Score Relationships

```cypher
// Find low-confidence MENTIONS relationships
MATCH (c:Chunk)-[r:MENTIONS]->(e)
WHERE r.score < 0.50
RETURN c.chunk_id, e.name, r.score, c.content
ORDER BY r.score
LIMIT 10
```

---

**End of Design Document**
