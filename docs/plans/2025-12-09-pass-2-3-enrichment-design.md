# Pass 2/3 Enrichment Pipeline Design

**Created:** 2025-12-09
**Status:** Design Complete

---

## Executive Summary

This document designs the Pass 2 (Relationship Extraction) and Pass 3 (LLM Enrichment) phases of the book ingestion pipeline. These passes transform extracted entities into a richly connected knowledge graph with causal relationships, reframes, mechanisms, and patterns.

### Current State

| Pass | Status | What It Does |
|------|--------|--------------|
| Pass 0 | Complete | Hardcover metadata enrichment (genres, descriptions, series) |
| Pass 1 | Complete | Entity extraction (concepts, theories, persons, patterns) + MENTIONS relationships |
| Pass 2 | Partial | ReframeMapper creates RESONATES_WITH/METAPHOR_FOR connections |
| Pass 3 | Not Started | Rich descriptions, reframes, mechanisms |

### Target State

- **Pass 2**: Extract causal relationships (CAUSES, ENABLES, PREVENTS) and structural relationships (COMPONENT_OF, CONTRASTS_WITH) between entities in the same book
- **Pass 3**: Generate reframes via existing ReframeService, extract mechanisms, add rich descriptions

---

## 1. Pass 2: Relationship Extraction

### 1.1 Current ReframeMapper Analysis

The existing `library/graph/reframe_mapper.py` implements a limited Pass 2:
- Only processes Pattern/StoryInsight/SchemaBreak entities
- Creates RESONATES_WITH/METAPHOR_FOR/ANALOGOUS_TO relationships
- Uses LLM to find cross-domain structural similarities

**Limitation**: Does not extract explicit causal relationships stated in the text.

### 1.2 Proposed Relationship Types

From `library/graph/adhd_ontology.py` (RelationshipType enum):

| Relationship | Description | Example |
|--------------|-------------|---------|
| `CAUSES` | X causes Y | "Dopamine deficiency causes attention issues" |
| `ENABLES` | X makes Y possible | "Working memory enables complex reasoning" |
| `PREVENTS` | X blocks Y | "Anxiety prevents focused attention" |
| `MODULATES` | X affects intensity of Y | "Sleep quality modulates executive function" |
| `COMPONENT_OF` | Part-whole | "Inhibition is component of executive function" |
| `SUPPORTS` | Evidence supports | "Study X supports theory Y" |
| `CONTRADICTS` | Evidence against | "Finding A contradicts model B" |
| `CONTRASTS_WITH` | Key difference | "ADHD contrasts with learned inattention" |
| `DEPENDS_ON` | Prerequisite | "Self-regulation depends on metacognition" |
| `OPERATIONALIZES` | Makes measurable | "BRIEF operationalizes executive function" |

### 1.3 Relationship Extraction Algorithm

**Input**: Book chunks with extracted entities from Pass 1

**Algorithm**:
1. For each chunk, identify pairs of entities both mentioned in that chunk
2. Send entity pairs + chunk context to LLM for relationship classification
3. Filter by confidence threshold (0.7)
4. Batch write relationships to Neo4j

**Chunk Co-occurrence Logic**:
```python
def find_entity_pairs_in_chunk(chunk_id: str, kg: KnowledgeGraph) -> list[tuple[str, str]]:
    """Find all pairs of entities that co-occur in the same chunk."""
    entities = kg.get_entities_for_chunk(chunk_id)
    pairs = []
    for i, e1 in enumerate(entities):
        for e2 in entities[i+1:]:
            pairs.append((e1, e2))
    return pairs
```

### 1.4 LLM Prompt Design for Relationship Extraction

```
RELATIONSHIP_EXTRACTION_PROMPT = """Analyze the relationship between two entities within this text context.

**Entity A:** {entity_a_name} ({entity_a_type})
Description: {entity_a_description}

**Entity B:** {entity_b_name} ({entity_b_type})
Description: {entity_b_description}

**Text Context:**
{chunk_text}

**Instructions:**
1. Determine if there is an explicit or strongly implied relationship between Entity A and Entity B in this text
2. If a relationship exists, classify it using ONLY these types:
   - CAUSES: A directly causes or produces B
   - ENABLES: A makes B possible or facilitates B
   - PREVENTS: A blocks or inhibits B
   - MODULATES: A affects the intensity or degree of B
   - COMPONENT_OF: A is a part or component of B
   - SUPPORTS: A provides evidence for B
   - CONTRADICTS: A provides evidence against B
   - CONTRASTS_WITH: A and B are different in an important way
   - DEPENDS_ON: A requires or depends on B
   - OPERATIONALIZES: A measures or makes B concrete

3. If no clear relationship exists, return null

**Return JSON:**
{
  "relationship": {
    "type": "CAUSES | ENABLES | PREVENTS | ... | null",
    "direction": "A_TO_B | B_TO_A | BIDIRECTIONAL",
    "confidence": 0.0-1.0,
    "evidence": "brief quote or paraphrase from text"
  }
}
"""
```

### 1.5 Neo4j Schema for Relationships with Evidence

```cypher
CREATE (a)-[r:CAUSES {
  evidence: "quote from source text",
  confidence: 0.85,
  source_chunk_id: "chunk_abc123",
  source_book_calibre_id: 42,
  created_by: "pass2_relationship_extractor",
  created_at: datetime()
}]->(b)
```

### 1.6 Implementation: RelationshipExtractor Service

**File**: `library/graph/relationship_extractor.py`

```python
RELATIONSHIP_TYPES = [
    "CAUSES", "ENABLES", "PREVENTS", "MODULATES",
    "COMPONENT_OF", "SUPPORTS", "CONTRADICTS",
    "CONTRASTS_WITH", "DEPENDS_ON", "OPERATIONALIZES"
]

CONFIDENCE_THRESHOLD = 0.7
MAX_ENTITY_PAIRS_PER_CHUNK = 10  # Limit API calls

class RelationshipExtractor:
    def __init__(self, kg: KnowledgeGraph, model: str = "gpt-4o-mini"):
        self.kg = kg
        self.client = OpenAI()
        self.model = model

    def get_chunk_entities(self, chunk_id: str) -> list[dict]:
        """Get entities mentioned in a specific chunk."""
        # Query: MATCH (c:Chunk {id: $id})-[:MENTIONS]->(e) RETURN e

    def extract_relationships_for_chunk(self, chunk_id: str, chunk_text: str) -> list[dict]:
        """Extract relationships between entity pairs in a chunk."""
        entities = self.get_chunk_entities(chunk_id)
        pairs = self._generate_pairs(entities)[:MAX_ENTITY_PAIRS_PER_CHUNK]

        relationships = []
        for e1, e2 in pairs:
            result = self._classify_relationship(e1, e2, chunk_text)
            if result and result['confidence'] >= CONFIDENCE_THRESHOLD:
                relationships.append(result)

        return relationships

    def process_book(self, calibre_id: int) -> dict:
        """Run Pass 2 relationship extraction for a book."""
        chunks = self._get_book_chunks(calibre_id)
        total_relationships = 0

        for chunk in chunks:
            rels = self.extract_relationships_for_chunk(chunk['id'], chunk['content'])
            for rel in rels:
                self._create_relationship(rel)
                total_relationships += 1

        self.kg.update_book_status(calibre_id, "relationships_mapped")

        return {"chunks_processed": len(chunks), "relationships_created": total_relationships}
```

---

## 2. Pass 3: LLM Enrichment

### 2.1 Enrichment Types

| Enrichment | Source | Purpose |
|------------|--------|---------|
| **Reframes** | Existing ReframeService | Make concepts accessible via metaphors/analogies |
| **Mechanisms** | New extraction | Explain how things work (process descriptions) |
| **Rich Descriptions** | LLM generation | Expand terse entity descriptions |
| **Patterns** | New extraction | Identify recurring structures |

### 2.2 Integration with Existing ReframeService

The `ies/backend/src/ies_backend/services/reframe_service.py` already provides:
- `generate_reframes(concept_id, count)` - Generates reframes via Claude
- `get_reframes(concept_id)` - Retrieves cached reframes
- `record_feedback(reframe_id, vote)` - Tracks helpful/confusing votes
- Neo4j storage with `HAS_REFRAME` relationships

**Pass 3 Strategy**: For each high-value concept (frequent mentions, central to book), call `generate_reframes()` with count=3.

### 2.3 Mechanism Extraction

**Definition**: A mechanism explains the step-by-step process by which something works.

**Schema**:
```python
(:Mechanism {
  id: "mech_uuid",
  name: "Dopamine Reward Pathway",
  description: "How dopamine signals reward and motivates behavior",
  steps: ["Stimulus triggers...", "Dopamine released...", "Receptor binding..."],
  triggers: ["Novel stimuli", "Anticipated reward"],
  outcomes: ["Motivation", "Learning reinforcement"],
  source_book_calibre_id: 42
})

# Relationships
(Mechanism)-[:EXPLAINS]->(Concept)
(Mechanism)-[:COMPONENT_OF]->(Theory)
```

### 2.4 LLM Prompt for Mechanism Extraction

```
MECHANISM_EXTRACTION_PROMPT = """Analyze this concept and extract a mechanistic explanation of how it works.

**Concept:** {concept_name}
**Type:** {concept_type}
**Description:** {concept_description}

**Context from book:**
{context_chunks}

**Instructions:**
1. If this concept involves a process or mechanism, describe the steps
2. Identify triggers/inputs that initiate the mechanism
3. Identify outcomes/effects of the mechanism
4. Keep explanations concrete and ADHD-friendly (short steps, clear progression)

**Return JSON:**
{
  "has_mechanism": true/false,
  "mechanism": {
    "name": "descriptive name for the mechanism",
    "steps": ["step 1", "step 2", ...],
    "triggers": ["trigger 1", ...],
    "outcomes": ["outcome 1", ...],
    "confidence": 0.0-1.0
  }
}
"""
```

### 2.5 Enrichment Priority Algorithm

Not all entities need enrichment. Prioritize by:

```python
def calculate_enrichment_priority(entity: dict) -> float:
    """Calculate priority score for entity enrichment (0-1)."""
    score = 0.0

    # High mention count = high value
    mentions = entity.get('mention_count', 0)
    score += min(mentions / 50, 0.3)  # Max 0.3 from mentions

    # Central entity types get priority
    priority_types = {'Concept', 'Theory', 'Framework', 'Mechanism'}
    if entity.get('type') in priority_types:
        score += 0.2

    # Missing description = needs enrichment
    if not entity.get('description') or len(entity.get('description', '')) < 50:
        score += 0.3

    # No reframes yet
    if not entity.get('has_reframes', False):
        score += 0.2

    return min(score, 1.0)
```

---

## 3. Implementation Plan

### 3.1 Functions to Add to `ingest_calibre.py`

```python
def run_pass2_relationships(book: CalibreBook, kg: KnowledgeGraph) -> dict:
    """Pass 2: Extract relationships between entities."""
    from library.graph.relationship_extractor import RelationshipExtractor

    extractor = RelationshipExtractor(kg)
    return extractor.process_book(book.calibre_id)


def run_pass3_enrichment(book: CalibreBook, kg: KnowledgeGraph) -> dict:
    """Pass 3: Enrich entities with reframes, mechanisms, descriptions."""
    from library.graph.enrichment_service import EnrichmentService

    enricher = EnrichmentService(kg)
    return enricher.enrich_book_entities(book.calibre_id)


def ingest_book_full(book: CalibreBook, kg: KnowledgeGraph, ...) -> dict:
    """Run all passes: 0 (metadata) -> 1 (entities) -> 2 (relationships) -> 3 (enrichment)."""
    stats = {}

    # Pass 1: Entity extraction (existing)
    stats['pass1'] = ingest_book(book, kg, extractor, classifier)

    if stats['pass1']['status'] == 'success':
        # Pass 2: Relationship extraction
        stats['pass2'] = run_pass2_relationships(book, kg)

        # Pass 3: Enrichment (expensive, run selectively)
        if args.enrich:
            stats['pass3'] = run_pass3_enrichment(book, kg)

    return stats
```

### 3.2 Status Transitions

```
pending                    # Book node created
    ↓ (Pass 1: chunking + entity extraction)
entities_extracted        # Entities created, MENTIONS relationships added
    ↓ (Pass 2: relationship extraction)
relationships_mapped      # CAUSES/ENABLES/etc relationships added
    ↓ (Pass 3: LLM enrichment)
enriched                  # Reframes, mechanisms, rich descriptions added
```

### 3.3 CLI Flags

```bash
# Existing
python scripts/ingest_calibre.py --id 42     # Process single book (Pass 1)
python scripts/ingest_calibre.py --status    # Show stats

# New flags
python scripts/ingest_calibre.py --pass2 --id 42     # Run Pass 2 only on book 42
python scripts/ingest_calibre.py --pass3 --id 42     # Run Pass 3 only on book 42
python scripts/ingest_calibre.py --full --id 42      # Run all passes
python scripts/ingest_calibre.py --enrich-all        # Run Pass 3 on all eligible books
```

### 3.4 Rate Limiting and Cost Estimation

**Pass 2 Costs** (gpt-4o-mini):
- ~10 entity pairs per chunk (average)
- ~50 chunks per book
- ~500 API calls per book
- Cost: ~$0.05 per book

**Pass 3 Costs** (claude-sonnet-4):
- Reframes: ~5 per book @ $0.003 each = $0.015/book
- Mechanisms: ~3 per book @ $0.01 each = $0.03/book
- Descriptions: ~20 per book @ $0.002 each = $0.04/book
- Total Pass 3: ~$0.085/book

**Rate Limiting Strategy**:
```python
import asyncio

RATE_LIMIT_DELAY = 1.0  # 1 second between API calls
MAX_CONCURRENT_CALLS = 5

async def rate_limited_call(func, *args):
    """Wrapper to rate-limit API calls."""
    await asyncio.sleep(RATE_LIMIT_DELAY)
    return await func(*args)
```

---

## 4. Priority Order

### Phase 1: Pass 2 Foundation (High Value, Medium Effort)

1. **Create `relationship_extractor.py`** service
2. **Add chunk-entity query** method to UnifiedGraphClient
3. **Implement relationship extraction prompt** with confidence filtering
4. **Update `ingest_calibre.py`** with `--pass2` flag
5. **Update status transitions** in book processing

**Why first**: Relationships between entities are the core value of a knowledge graph. Without CAUSES/ENABLES, entities are just a list.

### Phase 2: Pass 3 Reframes (High Value, Low Effort)

1. **Create enrichment service** that calls existing ReframeService
2. **Implement priority algorithm** to select entities for enrichment
3. **Add `--pass3` flag** to CLI
4. **Batch processing** with rate limiting

**Why second**: ReframeService already exists and works. Just need to call it during ingestion.

### Phase 3: Pass 3 Mechanisms (Medium Value, Medium Effort)

1. **Design Mechanism schema** and Neo4j model
2. **Implement mechanism extraction prompt**
3. **Add EXPLAINS relationship** creation
4. **Integrate into enrichment service**

**Why third**: Mechanisms add explanatory power but require more complex extraction.

### Phase 4: Rich Descriptions (Low Value, Low Effort)

1. **Implement description enrichment prompt**
2. **Add to enrichment service** as optional step
3. **Only run for entities with missing/short descriptions**

**Why last**: Nice to have, but entities function without rich descriptions.

---

## 5. Files to Create/Modify

### New Files

| File | Purpose | Lines (est.) |
|------|---------|--------------|
| `library/graph/relationship_extractor.py` | Pass 2 relationship extraction | ~300 |
| `library/graph/enrichment_service.py` | Pass 3 orchestration | ~250 |
| `ies/backend/tests/test_relationship_extractor.py` | Unit tests | ~200 |
| `ies/backend/tests/test_enrichment_service.py` | Unit tests | ~150 |

### Modified Files

| File | Changes |
|------|---------|
| `scripts/ingest_calibre.py` | Add `--pass2`, `--pass3`, `--full` flags |
| `scripts/auto_ingest_daemon.py` | Optionally enable Pass 2/3 in batch processing |
| `library/graph/unified_client.py` | Add `get_entities_for_chunk()`, `get_chunks_for_book()` methods |
| `docs/GAP-ANALYSIS-2025-12-09.md` | Update Pass 2/3 status |

---

## 6. Success Criteria

| Metric | Target |
|--------|--------|
| Pass 2 relationship accuracy | >80% precision (manual review of 50 samples) |
| Pass 3 reframe quality | >70% helpful votes (user feedback) |
| Processing time | <5 minutes per book for Pass 2+3 |
| API cost | <$0.15 per book total |
| Test coverage | >80% for new services |
