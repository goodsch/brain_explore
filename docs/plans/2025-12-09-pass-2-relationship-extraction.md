# Pass 2 Relationship Extraction Design

**Created:** 2025-12-09
**Status:** Design Document
**Purpose:** Define Pass 2 relationship extraction pipeline for IES book ingestion

---

## Executive Summary

**Problem:** Pass 1 extracts entities from books, but relationships between entities are captured during extraction but not systematically processed. Pass 2 will enhance relationship extraction with causal, component, and contrast relationships that are critical for knowledge graph navigation.

**Solution:** A targeted LLM-based relationship extraction pass that:
1. Operates on books with `processing_status='entities_extracted'`
2. Focuses on three relationship types: CAUSES, PART_OF, CONTRASTS_WITH
3. Uses sliding window approach over entity-rich chunks
4. Creates high-quality relationships with evidence attribution
5. Updates book status to `relationships_mapped`

**Impact:** Enables deeper exploration in Flow Mode by surfacing causal chains, component hierarchies, and conceptual contrasts.

---

## 1. Architecture Overview

### Pipeline Position

```
Calibre Book
    │
    ├─→ Pass 1 (Structure) ──────────── COMPLETE
    │   ├─ Create Book node
    │   ├─ Extract & chunk text
    │   ├─ Extract entities (OpenAI)
    │   ├─ Create MENTIONS relationships
    │   └─ Status: pending → entities_extracted
    │
    ├─→ Pass 2 (Relationships) ─────── THIS DESIGN
    │   ├─ Load entity-rich chunks
    │   ├─ Extract relationships (OpenAI)
    │   ├─ Create typed relationships
    │   ├─ Deduplicate & validate
    │   └─ Status: entities_extracted → relationships_mapped
    │
    └─→ Pass 3 (Enrichment) ─────────── FUTURE
        ├─ Generate reframes
        ├─ Extract mechanisms
        ├─ Add descriptions
        └─ Status: relationships_mapped → enriched
```

### Design Principles

1. **Targeted Extraction:** Only extract 3 relationship types, not all possible relationships
2. **Entity-Centric:** Focus on chunks that mention multiple entities
3. **Evidence-Based:** Every relationship must cite source text
4. **Incremental:** Can re-run on individual books without affecting others
5. **Observable:** Comprehensive logging and stats tracking

---

## 2. Relationship Types

### Core Types (Pass 2)

| Type | Direction | Semantics | Neo4j Label | Example |
|------|-----------|-----------|-------------|---------|
| **Causal** | A→B | A causes, enables, or produces B | `CAUSES` | Executive Function CAUSES Task Initiation |
| **Component** | A→B | A is a part/aspect/element of B | `PART_OF` | Working Memory PART_OF Executive Function |
| **Contrast** | A↔B | A differs from or contrasts with B | `CONTRASTS_WITH` | ADHD CONTRASTS_WITH Neurotypical |

### Rationale

**Why these three?**
- **CAUSES:** Essential for understanding mechanisms (Barkley: "EF deficits CAUSE attention issues")
- **PART_OF:** Critical for hierarchical navigation (Chunk theory: "Working memory is PART_OF executive function")
- **CONTRASTS_WITH:** Helps clarify boundaries and distinctions (DBT vs CBT, ADHD vs Autism)

**Why not others?**
- `SUPPORTS`/`CONTRADICTS` — Too subjective, better for evidence chunks (already in Pass 1)
- `DEVELOPS`/`CITES` — Author-specific, not concept relationships
- `OPERATIONALIZES` — Assessment-specific, handled separately

### Bidirectional Relationships

- `CAUSES`: Unidirectional (A causes B ≠ B causes A)
- `PART_OF`: Unidirectional (A is part of B ≠ B is part of A)
- `CONTRASTS_WITH`: Bidirectional (A contrasts B = B contrasts A) — create both directions

---

## 3. LLM Prompt Strategy

### Core Extraction Prompt

```python
RELATIONSHIP_EXTRACTION_PROMPT = """Analyze this text and extract ONLY the following relationship types between entities:

ENTITY TYPES:
- Concept (core ideas, constructs)
- Theory (named theories/models)
- Framework (structured approaches)
- Person (authors, researchers)
- Assessment (instruments, scales)

RELATIONSHIP TYPES TO EXTRACT:

1) CAUSES (A→B): A causes, enables, produces, or leads to B
   - Causal mechanisms (e.g., "dopamine deficiency causes attention issues")
   - Prerequisites (e.g., "self-regulation requires executive function")
   - Temporal sequences (e.g., "shame blocks metabolization")

2) PART_OF (A→B): A is a component, aspect, module, or element of B
   - Hierarchical relationships (e.g., "working memory is part of executive function")
   - Taxonomic relationships (e.g., "ADHD is part of neurodevelopmental disorders")
   - Modular composition (e.g., "DBT includes mindfulness")

3) CONTRASTS_WITH (A↔B): A differs from, contrasts with, or is distinguished from B
   - Conceptual distinctions (e.g., "acceptance contrasts with resignation")
   - Comparison relationships (e.g., "ADHD differs from autism")
   - Theoretical opposites (e.g., "behaviorism contrasts with psychoanalysis")

INSTRUCTIONS:
- Only extract relationships that are EXPLICITLY stated or STRONGLY implied
- Include brief evidence quote (1-2 sentences) from the text
- If no clear relationships exist, return empty array
- Use exact entity names from the text
- Prefer precise relationships over vague connections

Return JSON in this exact format:
```json
{
  "relationships": [
    {
      "source": "exact entity name",
      "target": "exact entity name",
      "relation_type": "CAUSES | PART_OF | CONTRASTS_WITH",
      "evidence": "brief quote or paraphrase from text",
      "confidence": 0.0-1.0
    }
  ]
}
```

TEXT TO ANALYZE:
---
{chunk_text}
---

ENTITIES PRESENT:
{entity_list}

JSON output:"""
```

### Prompt Engineering Notes

**Why "ONLY these relationship types"?**
- Prevents LLM from inventing creative but unhelpful relationships
- Forces precision over quantity

**Why include entity list?**
- Grounds LLM attention on entities already extracted in Pass 1
- Reduces hallucination of entity names
- Enables validation (reject relationships with unknown entities)

**Why require evidence?**
- Prevents speculative relationships
- Enables trust/verification in UI
- Supports future relationship quality scoring

**Confidence Scoring:**
- 0.9-1.0: Explicit statement ("A causes B")
- 0.7-0.9: Strong implication with context
- 0.5-0.7: Weak implication, inferential
- Below 0.5: Reject (threshold for inclusion)

---

## 4. Implementation Architecture

### 4.1 Service Layer

**File:** `library/graph/relationship_extractor.py`

```python
@dataclass
class ExtractedRelationship:
    """A relationship extracted by LLM with evidence."""
    source: str           # Entity name
    target: str           # Entity name
    relation_type: str    # CAUSES | PART_OF | CONTRASTS_WITH
    evidence: str         # Text quote supporting relationship
    confidence: float     # 0.0-1.0
    chunk_id: str         # Source chunk for traceability

@dataclass
class RelationshipExtractionResult:
    """Result of relationship extraction for one chunk."""
    chunk_id: str
    relationships: list[ExtractedRelationship]
    entities_present: list[str]  # Entities that were in chunk

class RelationshipExtractor:
    """Extract typed relationships between entities using OpenAI."""

    def __init__(
        self,
        model: str = "gpt-4o",  # Use stronger model for relationships
        confidence_threshold: float = 0.5
    ):
        self.client = OpenAI()
        self.model = model
        self.confidence_threshold = confidence_threshold

    def extract_from_chunk(
        self,
        chunk: Chunk,
        entities: list[str]  # Entities present in this chunk
    ) -> RelationshipExtractionResult:
        """Extract relationships from a single chunk."""
        # Implementation: call OpenAI with prompt
        pass

    def extract_from_book(
        self,
        book: CalibreBook,
        kg: KnowledgeGraph,
        min_entities: int = 2  # Skip chunks with <2 entities
    ) -> dict:
        """Extract relationships from all entity-rich chunks in a book."""
        # Implementation: iterate chunks, filter by entity count
        pass
```

### 4.2 Script Integration

**File:** `scripts/pass2_relationships.py` (new script)

```python
#!/usr/bin/env python3
"""
Pass 2: Relationship extraction for Calibre books.

Operates on books with status='entities_extracted'
Extracts CAUSES, PART_OF, CONTRASTS_WITH relationships
Updates status to 'relationships_mapped'

Usage:
    python scripts/pass2_relationships.py              # All books
    python scripts/pass2_relationships.py --id 42      # Single book
    python scripts/pass2_relationships.py --limit 10   # Batch limit
    python scripts/pass2_relationships.py --status     # Show stats
"""

def pass2_single_book(book: CalibreBook, kg: KnowledgeGraph) -> dict:
    """Run Pass 2 on a single book."""
    stats = {
        "calibre_id": book.calibre_id,
        "relationships_extracted": 0,
        "high_confidence": 0,  # confidence >= 0.8
        "chunks_processed": 0,
        "status": "success"
    }

    # Load chunks with entities
    # Extract relationships per chunk
    # Deduplicate relationships
    # Store in Neo4j
    # Update book status

    return stats
```

### 4.3 Auto-Daemon Integration

**File:** `scripts/auto_ingest_daemon.py` (enhancement)

```python
def process_single_book(kg: KnowledgeGraph, book: CalibreBook) -> bool:
    """Process a single book through all passes."""

    # Pass 1: Entities (existing code)
    # ... entity extraction ...
    kg.update_book_status(book.calibre_id, "entities_extracted")

    # Pass 2: Relationships (NEW)
    try:
        from scripts.pass2_relationships import pass2_single_book
        pass2_result = pass2_single_book(book, kg)
        logger.info(
            f"Pass 2 complete: {pass2_result['relationships_extracted']} "
            f"relationships ({pass2_result['high_confidence']} high confidence)"
        )
    except Exception as e:
        logger.warning(f"Pass 2 failed for {book.title}: {e}")
        # Don't fail whole ingestion if Pass 2 fails

    # Pass 3: Enrichment (FUTURE)
    # ...

    return True
```

---

## 5. Neo4j Schema Updates

### Relationship Properties

All Pass 2 relationships will have these properties:

```cypher
(:Entity)-[:CAUSES|PART_OF|CONTRASTS_WITH {
    evidence: "text quote",
    confidence: 0.0-1.0,
    extracted_by: "pass2",
    extracted_at: "2025-12-09T10:30:00Z",
    source_book: calibre_id,
    source_chunk: chunk_id
}]->(:Entity)
```

### Query Examples

**Find causal chains:**
```cypher
MATCH path = (a:Concept)-[:CAUSES*1..3]->(b:Concept)
WHERE a.name = "Executive Function Deficit"
RETURN path
```

**Find component hierarchies:**
```cypher
MATCH (child:Concept)-[:PART_OF]->(parent:Concept)
WHERE parent.name = "Executive Function"
RETURN child.name as component, parent.name as whole
ORDER BY child.name
```

**Find contrasting concepts:**
```cypher
MATCH (a:Concept)-[:CONTRASTS_WITH]-(b:Concept)
WHERE a.name CONTAINS "ADHD"
RETURN DISTINCT a.name, b.name, a.description
```

### Indexes

```cypher
-- Performance indexes for relationship traversal
CREATE INDEX relationship_confidence IF NOT EXISTS
FOR ()-[r:CAUSES]-() ON (r.confidence);

CREATE INDEX relationship_confidence_part IF NOT EXISTS
FOR ()-[r:PART_OF]-() ON (r.confidence);

CREATE INDEX relationship_confidence_contrast IF NOT EXISTS
FOR ()-[r:CONTRASTS_WITH]-() ON (r.confidence);
```

---

## 6. Deduplication & Validation

### Deduplication Strategy

**Problem:** Same relationship may be extracted from multiple chunks.

**Solution:** Merge relationships with same (source, target, relation_type) triple:

```python
def deduplicate_relationships(
    relationships: list[ExtractedRelationship]
) -> list[ExtractedRelationship]:
    """Merge duplicate relationships, keeping highest confidence."""

    seen = {}  # (source, target, type) → relationship

    for rel in relationships:
        key = (rel.source, rel.target, rel.relation_type)

        if key not in seen:
            seen[key] = rel
        else:
            # Keep relationship with higher confidence
            if rel.confidence > seen[key].confidence:
                # Merge evidence
                seen[key].evidence = f"{seen[key].evidence}; {rel.evidence}"
                seen[key].confidence = rel.confidence

    return list(seen.values())
```

### Validation Rules

1. **Entity Existence:** Both source and target must exist in Neo4j (reject unknown entities)
2. **Confidence Threshold:** Reject relationships with confidence < 0.5
3. **Self-Loops:** Reject relationships where source == target
4. **Type Consistency:** Verify relation_type is one of CAUSES/PART_OF/CONTRASTS_WITH
5. **Evidence Required:** Reject relationships without evidence text

**Implementation:**

```python
def validate_relationship(
    rel: ExtractedRelationship,
    kg: KnowledgeGraph
) -> tuple[bool, str]:
    """Validate relationship, return (is_valid, reason)."""

    # Check confidence
    if rel.confidence < 0.5:
        return False, "confidence too low"

    # Check self-loop
    if rel.source == rel.target:
        return False, "self-loop"

    # Check type
    if rel.relation_type not in ["CAUSES", "PART_OF", "CONTRASTS_WITH"]:
        return False, "invalid type"

    # Check entities exist
    if not kg.entity_exists(rel.source):
        return False, f"source entity not found: {rel.source}"
    if not kg.entity_exists(rel.target):
        return False, f"target entity not found: {rel.target}"

    # Check evidence
    if not rel.evidence or len(rel.evidence) < 10:
        return False, "insufficient evidence"

    return True, "valid"
```

---

## 7. Integration with Existing Pipeline

### Status Lifecycle

```
pending
  │
  ├─→ chunked (after text extraction)
  │
  ├─→ entities_extracted (Pass 1 complete)
  │       │
  │       ├─→ relationships_mapped (Pass 2 complete) ← NEW
  │       │       │
  │       │       └─→ enriched (Pass 3 complete) [FUTURE]
  │       │
  │       └─→ error (any pass fails)
  │
  └─→ empty (no text found)
```

### KnowledgeGraph Client Updates

**File:** `library/graph/unified_client.py`

```python
class UnifiedGraphClient:
    # ... existing methods ...

    def add_typed_relationship(
        self,
        source_name: str,
        target_name: str,
        relation_type: str,  # CAUSES | PART_OF | CONTRASTS_WITH
        evidence: str,
        confidence: float,
        source_book: Optional[int] = None,
        source_chunk: Optional[str] = None
    ):
        """Add a Pass 2 relationship with metadata."""
        now = datetime.now().isoformat()

        with self.driver.session() as session:
            # For CONTRASTS_WITH, create bidirectional relationship
            if relation_type == "CONTRASTS_WITH":
                session.run(f"""
                    MATCH (a) WHERE a.name = $source
                    MATCH (b) WHERE b.name = $target
                    MERGE (a)-[r1:CONTRASTS_WITH]->(b)
                    MERGE (a)<-[r2:CONTRASTS_WITH]-(b)
                    SET r1.evidence = $evidence,
                        r1.confidence = $confidence,
                        r1.extracted_by = 'pass2',
                        r1.extracted_at = $now,
                        r1.source_book = $book,
                        r1.source_chunk = $chunk,
                        r2.evidence = $evidence,
                        r2.confidence = $confidence,
                        r2.extracted_by = 'pass2',
                        r2.extracted_at = $now,
                        r2.source_book = $book,
                        r2.source_chunk = $chunk
                """, source=source_name, target=target_name,
                     evidence=evidence, confidence=confidence,
                     now=now, book=source_book, chunk=source_chunk)
            else:
                # Unidirectional (CAUSES, PART_OF)
                session.run(f"""
                    MATCH (a) WHERE a.name = $source
                    MATCH (b) WHERE b.name = $target
                    MERGE (a)-[r:{relation_type}]->(b)
                    SET r.evidence = $evidence,
                        r.confidence = $confidence,
                        r.extracted_by = 'pass2',
                        r.extracted_at = $now,
                        r.source_book = $book,
                        r.source_chunk = $chunk
                """, source=source_name, target=target_name,
                     evidence=evidence, confidence=confidence,
                     now=now, book=source_book, chunk=source_chunk)

    def entity_exists(self, name: str) -> bool:
        """Check if entity exists in graph."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e) WHERE e.name = $name
                RETURN count(e) > 0 as exists
            """, name=name)
            record = result.single()
            return record["exists"] if record else False
```

---

## 8. Performance Considerations

### Chunking Strategy

**Problem:** Books have 50+ chunks, extracting relationships from all is expensive.

**Solution:** Filter to entity-rich chunks only.

```python
def get_entity_rich_chunks(
    book: CalibreBook,
    kg: KnowledgeGraph,
    min_entities: int = 2
) -> list[tuple[Chunk, list[str]]]:
    """Get chunks that mention multiple entities."""

    # Query Neo4j for chunks belonging to this book
    with kg.driver.session() as session:
        result = session.run("""
            MATCH (b:Book {calibre_id: $calibre_id})<-[:FROM_BOOK]-(c:Chunk)
            MATCH (c)-[:MENTIONS]->(e)
            WITH c, collect(DISTINCT e.name) as entities
            WHERE size(entities) >= $min_entities
            RETURN c.id as chunk_id, c.content as content, entities
            ORDER BY size(entities) DESC
        """, calibre_id=book.calibre_id, min_entities=min_entities)

        return [(Chunk(id=r["chunk_id"], content=r["content"]), r["entities"])
                for r in result]
```

**Expected Impact:**
- Average book: 50 chunks → ~15 entity-rich chunks (70% reduction)
- Cost per book: $0.15-0.30 (GPT-4o-mini)
- Processing time: 2-3 minutes per book

### API Rate Limiting

```python
class RelationshipExtractor:
    def __init__(self, ...):
        self.rate_limiter = RateLimiter(max_calls=50, period=60)  # 50/min

    def extract_from_chunk(self, ...):
        self.rate_limiter.wait_if_needed()
        # ... call OpenAI ...
```

### Batch Processing

```python
def process_batch(limit: int = 5):
    """Process multiple books in batch with rate limiting."""
    kg = KnowledgeGraph()
    books = get_books_for_pass2(kg, limit=limit)

    for i, book in enumerate(books):
        logger.info(f"Processing book {i+1}/{len(books)}: {book.title}")

        try:
            pass2_single_book(book, kg)
            time.sleep(2)  # 2s between books
        except Exception as e:
            logger.error(f"Failed: {e}")
            continue
```

---

## 9. Success Metrics

### Quantitative Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Relationships per book | 20-50 | Track in stats |
| High confidence (>0.8) | >60% | Filter in query |
| Entity coverage | >80% entities in at least 1 relationship | Query Neo4j |
| Processing time | <3 min per book | Log timestamps |
| API cost | <$0.30 per book | Track tokens |

### Qualitative Metrics

1. **Relationship Precision:** Manual review of 20 random relationships per book type
2. **Evidence Quality:** Check that evidence text supports claimed relationship
3. **Flow Mode Value:** Do relationships enable useful exploration paths?

### Validation Query

```cypher
// Show Pass 2 statistics
MATCH (b:Book {processing_status: 'relationships_mapped'})
OPTIONAL MATCH (b)<-[:FROM_BOOK]-(c:Chunk)-[:MENTIONS]->(e)
WITH b, count(DISTINCT e) as entity_count
MATCH ()-[r]-()
WHERE r.source_book = b.calibre_id
  AND r.extracted_by = 'pass2'
WITH b, entity_count,
     count(r) as relationship_count,
     avg(r.confidence) as avg_confidence
RETURN
    b.title,
    b.author,
    entity_count,
    relationship_count,
    round(avg_confidence * 100) as avg_confidence_pct,
    round(relationship_count * 1.0 / entity_count, 2) as rels_per_entity
ORDER BY relationship_count DESC
LIMIT 20
```

---

## 10. Implementation Tasks

### Phase 1: Core Service (4-6 hours)

- [ ] Create `library/graph/relationship_extractor.py`
  - [ ] Define `ExtractedRelationship`, `RelationshipExtractionResult` dataclasses
  - [ ] Implement `RelationshipExtractor` class
  - [ ] Write extraction prompt
  - [ ] Implement `extract_from_chunk()` with OpenAI integration
  - [ ] Implement `extract_from_book()` with entity filtering
  - [ ] Add deduplication logic
  - [ ] Add validation logic

### Phase 2: Script & CLI (2-3 hours)

- [ ] Create `scripts/pass2_relationships.py`
  - [ ] Implement `pass2_single_book()` orchestration
  - [ ] Add CLI argument parsing (--id, --limit, --status)
  - [ ] Add progress tracking with Rich
  - [ ] Add stats summary output
  - [ ] Add error handling and logging

### Phase 3: Integration (2-3 hours)

- [ ] Update `library/graph/unified_client.py`
  - [ ] Add `add_typed_relationship()` method
  - [ ] Add `entity_exists()` method
  - [ ] Add bidirectional CONTRASTS_WITH logic
  - [ ] Add relationship property updates

- [ ] Update `scripts/auto_ingest_daemon.py`
  - [ ] Add Pass 2 call after Pass 1
  - [ ] Add error handling for Pass 2 failures
  - [ ] Update logging

### Phase 4: Testing & Validation (3-4 hours)

- [ ] Create `ies/backend/tests/test_relationship_extractor.py`
  - [ ] Mock OpenAI responses
  - [ ] Test extraction logic
  - [ ] Test deduplication
  - [ ] Test validation rules

- [ ] Manual validation
  - [ ] Run on 3 test books
  - [ ] Review extracted relationships for precision
  - [ ] Check evidence quality
  - [ ] Verify Neo4j storage

### Phase 5: Documentation & Monitoring (1-2 hours)

- [ ] Update `docs/GAP-ANALYSIS-2025-12-09.md`
  - [ ] Mark Pass 2 as complete
  - [ ] Update implementation percentage

- [ ] Update `CLAUDE.md`
  - [ ] Add Pass 2 to architecture section
  - [ ] Document relationship types

- [ ] Add monitoring queries
  - [ ] Relationship count by type
  - [ ] Average confidence by book
  - [ ] Entity coverage metrics

**Total Estimated Time:** 12-18 hours

---

## 11. Risks & Mitigations

### Risk 1: Low Relationship Precision

**Risk:** LLM extracts spurious relationships not supported by text.

**Mitigation:**
- Require evidence quotes in prompt
- Use confidence threshold (0.5)
- Manual review of sample relationships
- Add negative examples to prompt if needed

### Risk 2: Entity Name Mismatch

**Risk:** LLM uses different entity name than Pass 1 extracted (e.g., "EF" vs "Executive Function").

**Mitigation:**
- Pass entity list to prompt explicitly
- Validation rejects relationships with unknown entities
- Entity aliasing in Neo4j (future enhancement)

### Risk 3: High API Costs

**Risk:** Processing 179 books at $0.30/book = $53.70 total.

**Mitigation:**
- Filter to entity-rich chunks (70% cost reduction)
- Use GPT-4o-mini for first pass, GPT-4o only if needed
- Batch processing with rate limiting
- Cost monitoring and alerts

### Risk 4: Relationship Duplication

**Risk:** Same relationship extracted from multiple chunks creates Neo4j duplicates.

**Mitigation:**
- Deduplication in extraction pipeline
- Neo4j MERGE (not CREATE) for relationships
- Track source_chunk for debugging

---

## 12. Future Enhancements

### Short-Term (Phase 2 Extensions)

1. **Relationship Strength:** Add `strength` property (1-5 scale) for relationship importance
2. **Temporal Relationships:** Add `PRECEDES`, `FOLLOWS` for developmental sequences
3. **Negative Relationships:** Add `PREVENTS`, `INHIBITS` for negative causation
4. **Entity Aliases:** Handle entity name variations (abbreviations, synonyms)

### Long-Term (Pass 3+)

1. **Relationship Enrichment:** Add descriptions to relationships (not just evidence)
2. **Cross-Book Relationships:** Find relationships mentioned in multiple books
3. **Relationship Confidence Updates:** Adjust confidence based on multi-book evidence
4. **Relationship Versioning:** Track relationship changes over time

---

## 13. Appendix: Example Output

### Sample Input (Chunk)

```
Executive function includes several component processes: working memory,
cognitive flexibility, and inhibitory control. Research by Barkley (1997)
shows that deficits in these executive function components cause significant
difficulties with self-regulation in individuals with ADHD. This contrasts
with neurotypical development where executive functions develop more uniformly.
```

### Expected Extraction

```json
{
  "relationships": [
    {
      "source": "Working Memory",
      "target": "Executive Function",
      "relation_type": "PART_OF",
      "evidence": "Executive function includes several component processes: working memory, cognitive flexibility, and inhibitory control.",
      "confidence": 0.95
    },
    {
      "source": "Cognitive Flexibility",
      "target": "Executive Function",
      "relation_type": "PART_OF",
      "evidence": "Executive function includes several component processes: working memory, cognitive flexibility, and inhibitory control.",
      "confidence": 0.95
    },
    {
      "source": "Inhibitory Control",
      "target": "Executive Function",
      "relation_type": "PART_OF",
      "evidence": "Executive function includes several component processes: working memory, cognitive flexibility, and inhibitory control.",
      "confidence": 0.95
    },
    {
      "source": "Executive Function Deficit",
      "target": "Self-Regulation Difficulty",
      "relation_type": "CAUSES",
      "evidence": "deficits in these executive function components cause significant difficulties with self-regulation",
      "confidence": 0.90
    },
    {
      "source": "ADHD",
      "target": "Neurotypical Development",
      "relation_type": "CONTRASTS_WITH",
      "evidence": "This contrasts with neurotypical development where executive functions develop more uniformly.",
      "confidence": 0.85
    }
  ]
}
```

### Neo4j Result

```cypher
// Created relationships
(Working Memory)-[:PART_OF {confidence: 0.95, evidence: "..."}]->(Executive Function)
(Cognitive Flexibility)-[:PART_OF {confidence: 0.95, evidence: "..."}]->(Executive Function)
(Inhibitory Control)-[:PART_OF {confidence: 0.95, evidence: "..."}]->(Executive Function)
(Executive Function Deficit)-[:CAUSES {confidence: 0.90, evidence: "..."}]->(Self-Regulation Difficulty)
(ADHD)<-[:CONTRASTS_WITH {confidence: 0.85, evidence: "..."}]->(Neurotypical Development)
```

---

## 14. References

**Existing Code Patterns:**
- `library/graph/entities.py` — Entity extraction with OpenAI (Pass 1 reference)
- `scripts/ingest_calibre.py` — Book processing pipeline (integration point)
- `library/graph/unified_client.py` — Neo4j client operations
- `ies/backend/src/ies_backend/schemas/concept.py` — RelationshipType enum (COMPONENT_OF, CAUSES, ENABLES)

**Redux Specifications:**
- `docs/GAP-ANALYSIS-2025-12-09.md` — Pass 2 requirements (CAUSES, PART_OF, CONTRASTS_WITH)
- `docs/IES-SYSTEM-DESIGN.md` — Knowledge graph semantics

**Design Decisions:**
- Three relationship types chosen for maximum navigation value
- Entity-rich chunk filtering for cost efficiency
- Confidence scoring for quality control
- Bidirectional CONTRASTS_WITH for symmetric relationships
