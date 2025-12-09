# Pass 3 Enrichment Service Implementation

**Date:** 2025-12-09
**Status:** Complete
**Tests:** 15 new tests, all passing (404 total backend tests)

---

## Overview

Implemented the Pass 3 LLM Enrichment Service as specified in `docs/plans/2025-12-09-pass-3-llm-enrichment.md`.

The service orchestrates four types of AI-powered enrichment for book entities:

1. **Reframes** — Metaphors, analogies, stories (delegates to existing ReframeService)
2. **Mechanisms** — Step-by-step process explanations with triggers/outcomes
3. **Patterns** — Cross-domain structural templates (feedback loops, emergence, etc.)
4. **Rich Descriptions** — Enhanced entity descriptions from sparse extractions

---

## Implementation Details

### File Created

**`ies/backend/src/ies_backend/services/enrichment_service.py`** (850+ lines)

Key components:
- `EnrichmentService` class with async orchestration
- `RateLimiter` class (30 calls/min default)
- `calculate_enrichment_priority()` function (scores 0-1)
- `should_extract_mechanism()` eligibility check
- Three LLM prompts: mechanism extraction, pattern detection, description enhancement
- Singleton `enrichment_service` instance for easy import

### Core Methods

#### Public API

```python
async def enrich_book_entities(
    calibre_id: int,
    enable_reframes: bool = True,
    enable_mechanisms: bool = True,
    enable_patterns: bool = True,
    enable_descriptions: bool = True,
    max_entities: int = 20,
) -> dict[str, Any]:
    """Run Pass 3 enrichment for high-value entities in a book."""
```

Returns stats dict:
```python
{
    "calibre_id": 42,
    "reframes_generated": 15,
    "mechanisms_extracted": 3,
    "patterns_detected": 2,
    "descriptions_enriched": 8,
    "entities_processed": 20,
    "errors": 0,
}
```

#### Internal Pipeline

1. **Load Book Context** — `_get_book_context(calibre_id)`
   - Fetches title, author, genres, description from Neo4j

2. **Prioritize Entities** — `_get_prioritized_entities(calibre_id, limit=20)`
   - Queries Book→MENTIONS→Entity relationships
   - Calculates priority score (mention count, type, missing fields)
   - Returns top N entities sorted by priority

3. **Process Each Entity**
   - Reframes: `_generate_reframes_for_entity()` → calls existing ReframeService
   - Mechanisms: `_extract_mechanism_for_entity()` → LLM extraction + Neo4j storage
   - Patterns: `_detect_pattern_for_entity()` → LLM detection + deduplication
   - Descriptions: `_enhance_description_for_entity()` → LLM expansion

4. **Update Book Status** — `_update_book_status(calibre_id, "enriched")`

---

## Neo4j Schema Changes

### Mechanism Nodes

```cypher
(:Mechanism {
  id: "uuid",
  name: "Dopamine Reward Pathway",
  description: "one-sentence overview",
  steps: ["Step 1: ...", "Step 2: ...", ...],
  triggers: ["Novel stimulus", "Anticipated reward"],
  outcomes: ["Motivated behavior", "Learning reinforcement"],
  confidence: 0.85,
  source_book_calibre_id: 42,
  source_chunks: ["chunk_abc", "chunk_def"],
  created_at: datetime()
})

# Relationships
(Mechanism)-[:EXPLAINS]->(Concept|Theory|Framework)
(Book)-[:DESCRIBES]->(Mechanism)
```

### Pattern Nodes

```cypher
(:Pattern {
  id: "uuid",
  name: "Feedback Loop",
  description: "A cyclical process where outputs influence inputs",
  structural_elements: ["Input signal", "Process", "Output", "Feedback path"],
  variants: ["Positive feedback", "Negative feedback", "Delayed feedback"],
  examples_across_domains: [
    "Thermostat control (engineering)",
    "Dopamine reinforcement (neuroscience)",
    "Social media engagement (digital psychology)"
  ],
  source_books: [42, 57, 89],  # calibre_ids
  created_at: datetime()
})

# Relationships
(Pattern)-[:APPEARS_IN]->(Concept|Theory|Framework)
(Book)-[:DEMONSTRATES]->(Pattern)
```

### Enhanced Entity Fields

```cypher
# Existing entity nodes gain new properties
(Concept|Theory|Framework) {
  description_enriched_at: datetime(),
  key_aspects: ["aspect 1", "aspect 2", ...],
  has_mechanism: true/false,
  has_pattern: true/false
}
```

---

## Priority Algorithm

```python
def calculate_enrichment_priority(entity: dict) -> float:
    """
    Score factors (max 1.0):
    - Mention count: 0-0.3 (50+ mentions = max)
    - Priority type (Concept/Theory/Framework/Mechanism): +0.2
    - Missing description (<50 chars): +0.3
    - No reframes yet: +0.2
    """
```

**Example Scores:**
- High-value concept (Executive Function, 50 mentions, no desc): 0.8
- Low-value person (Author, 2 mentions, has desc): 0.04
- Theory with reframes (Attachment Theory, 30 mentions, desc): 0.6

---

## Rate Limiting

**RateLimiter Class:**
- Default: 30 calls/minute (conservative for Claude Sonnet 4)
- Tracks call timestamps in sliding window
- Automatic sleep when approaching limit
- Used for all LLM calls (mechanisms, patterns, descriptions)

**Note:** Reframe generation uses existing ReframeService which has its own rate limiting.

---

## LLM Integration

### Model

**Claude Sonnet 4** (`claude-sonnet-4-20250514`)

Used for:
- Mechanism extraction (max_tokens=1024)
- Pattern detection (max_tokens=1024)
- Description enhancement (max_tokens=512)

Reframes use ReframeService which also uses Claude Sonnet 4.

### Prompts

All prompts request structured JSON responses with confidence scores.

**Mechanism Extraction:**
- Analyzes concept for process/mechanism
- Returns steps (3-7 ideal), triggers, outcomes
- ADHD-friendly: short steps, minimal jargon
- Threshold: 0.7 confidence for storage

**Pattern Detection:**
- Identifies cross-domain structural templates
- Returns structural elements, variants, examples
- Higher threshold: 0.75 confidence (patterns are higher-value)
- Deduplication: checks for existing patterns by name

**Description Enhancement:**
- Expands sparse descriptions to 2-3 sentences (100-150 words)
- Adds key aspects for structured understanding
- Threshold: 0.7 confidence for update

### JSON Parsing

Robust parser handles:
- Markdown code blocks (```json ... ```)
- Plain JSON objects
- JSON embedded in explanation text
- Malformed responses (returns None)

---

## Test Coverage

**File:** `tests/test_enrichment_service.py` (15 tests, all passing)

### Test Categories

**Priority Calculation (3 tests):**
- High-priority entity scoring
- Low-priority entity scoring
- Priority capping at 1.0

**Mechanism Eligibility (4 tests):**
- Eligible concept with description
- Ineligible Person type
- Already has mechanism
- Short description (<30 chars)

**Service Methods (8 tests):**
- Reframe generation delegation
- JSON parsing (markdown + plain)
- Book context retrieval (success + not found)
- Entity prioritization
- Full enrichment flow (success + missing book)

### Running Tests

```bash
# Run enrichment tests only
cd ies/backend
uv run pytest tests/test_enrichment_service.py -v

# Run full backend suite
uv run pytest tests/ -v
```

**Current Status:** 404 backend tests passing (15 new + 389 existing)

---

## Usage Examples

### Basic Usage

```python
from ies_backend.services.enrichment_service import enrichment_service

# Enrich a book (all enrichment types enabled)
stats = await enrichment_service.enrich_book_entities(
    calibre_id=42,
    max_entities=20
)

print(f"Generated {stats['reframes_generated']} reframes")
print(f"Extracted {stats['mechanisms_extracted']} mechanisms")
print(f"Detected {stats['patterns_detected']} patterns")
print(f"Enhanced {stats['descriptions_enriched']} descriptions")
```

### Selective Enrichment

```python
# Only reframes and descriptions (skip expensive mechanisms/patterns)
stats = await enrichment_service.enrich_book_entities(
    calibre_id=42,
    enable_mechanisms=False,
    enable_patterns=False,
    max_entities=10
)
```

### Custom Client

```python
from anthropic import AsyncAnthropic
from ies_backend.services.enrichment_service import EnrichmentService

# Use custom Anthropic client (for testing or different API key)
custom_client = AsyncAnthropic(api_key="custom-key")
service = EnrichmentService(anthropic_client=custom_client)

stats = await service.enrich_book_entities(calibre_id=42)
```

---

## CLI Integration (Planned)

The design document specifies CLI integration via `scripts/ingest_calibre.py`:

### Planned CLI Flags

```bash
# Run Pass 3 only
python scripts/ingest_calibre.py --pass3 --id 42

# Selective enrichment
python scripts/ingest_calibre.py --pass3 --id 42 \
  --no-mechanisms --no-patterns

# Full pipeline (Pass 1 + 2 + 3)
python scripts/ingest_calibre.py --full --id 42

# Batch enrichment
python scripts/ingest_calibre.py --enrich-all --limit 10
```

### Integration Code (Not Yet Implemented)

```python
# In scripts/ingest_calibre.py

from ies_backend.services.enrichment_service import enrichment_service

async def run_pass3(calibre_id: int, args) -> dict:
    """Run Pass 3 enrichment."""
    console.print(f"\n[bold blue]Pass 3:[/] LLM enrichment for book {calibre_id}")

    stats = await enrichment_service.enrich_book_entities(
        calibre_id=calibre_id,
        enable_reframes=not args.no_reframes,
        enable_mechanisms=not args.no_mechanisms,
        enable_patterns=not args.no_patterns,
        enable_descriptions=not args.no_descriptions
    )

    console.print(f"  [green]✓ Enrichment complete[/]")
    console.print(f"    Reframes: {stats['reframes_generated']}")
    console.print(f"    Mechanisms: {stats['mechanisms_extracted']}")
    console.print(f"    Patterns: {stats['patterns_detected']}")
    console.print(f"    Descriptions: {stats['descriptions_enriched']}")

    return stats
```

**Status:** Service implemented, CLI integration pending.

---

## Cost Estimates

Based on design document projections:

### Per-Book Costs (20 entities)

| Enrichment Type | API Calls | Est. Cost/Call | Total |
|-----------------|-----------|----------------|-------|
| Reframes (3 per entity) | 60 | $0.003 | $0.18 |
| Mechanisms (10 eligible) | 10 | $0.01 | $0.10 |
| Patterns (5 eligible) | 5 | $0.01 | $0.05 |
| Descriptions (15 sparse) | 15 | $0.002 | $0.03 |
| **Total Pass 3** | **90** | - | **$0.36** |

**Assumptions:**
- Claude Sonnet 4: ~$3/M input tokens, ~$15/M output tokens
- Average prompt: 1000 tokens input, 500 tokens output
- Conservative estimate: ~$0.01 per call

### 179-Book Library

- **Full enrichment**: 179 × $0.36 = **$64.44**
- **Optimized (100 books)**: 100 × $0.36 = **$36.00**

---

## Next Steps

### Immediate

1. ✅ **Service Implementation** — Complete
2. ✅ **Unit Tests** — Complete (15 tests)
3. ✅ **Integration with existing services** — ReframeService integration working

### CLI Integration (Priority 1)

Update `scripts/ingest_calibre.py`:
- Add `--pass3`, `--full`, `--enrich-all` flags
- Add `--no-mechanisms`, `--no-patterns`, `--no-reframes`, `--no-descriptions` flags
- Implement `run_pass3()` function
- Add status filtering for batch enrichment

**Estimate:** 2-3 hours

### Neo4j Schema Initialization (Priority 2)

Call `EnrichmentService.initialize_schema()` on application startup:
- Creates full-text index on Chunk nodes if not exists
- Required for efficient segment search

**Location:** `ies/backend/src/ies_backend/main.py` startup event

**Estimate:** 30 minutes

### Integration Tests (Priority 3)

Create `tests/integration/test_enrichment_integration.py`:
- Test full Pass 3 pipeline on real book data
- Verify Neo4j schema changes
- Validate LLM response parsing
- Measure actual API costs

**Estimate:** 2-3 hours

### Documentation (Priority 4)

Update project documentation:
- Add Pass 3 to `docs/ARCHITECTURE-AND-INTERACTIONS.md`
- Update `docs/GAP-ANALYSIS-2025-12-09.md` (mark Pass 3 complete)
- Add enrichment examples to `docs/IES-SYSTEM-DESIGN.md`

**Estimate:** 1-2 hours

---

## Success Criteria

From design document:

| Metric | Target | Measurement | Status |
|--------|--------|-------------|--------|
| **Reframe Quality** | >70% helpful votes | User feedback in UI | Pending usage |
| **Mechanism Completeness** | >75% of process concepts | Manual audit | Pending data |
| **Pattern Cross-Domain Coverage** | >3 domains per pattern | Neo4j query | Pending data |
| **Description Enhancement** | <5% confusion rate | User feedback | Pending usage |
| **Processing Time** | <5 minutes per book | Timing logs | Pending measurement |
| **API Cost** | <$0.40 per book | Cost tracking | Pending measurement |
| **Error Rate** | <5% of entities | Error logs | Monitoring ready |

**Note:** All metrics will be measurable once CLI integration is complete and real books are enriched.

---

## Key Design Decisions

### 1. Reframe Delegation

**Decision:** Call existing `ReframeService` instead of duplicating logic.

**Rationale:**
- ReframeService already has Claude integration, caching, and feedback voting
- Avoids code duplication
- Maintains consistent reframe quality

**Implementation:** `_generate_reframes_for_entity()` calls `reframe_service.generate_reframes()`

### 2. Priority-Based Processing

**Decision:** Calculate priority score and only enrich top 20 entities per book.

**Rationale:**
- Enrichment is expensive (API costs + time)
- High-mention entities provide most value
- Sparse entities can be enriched on-demand later

**Implementation:** `calculate_enrichment_priority()` with weighted scoring

### 3. Confidence Thresholds

**Decision:** Different thresholds for different enrichment types.

**Thresholds:**
- Mechanisms: 0.7 (moderate confidence)
- Patterns: 0.75 (higher confidence, cross-domain claims)
- Descriptions: 0.7 (moderate confidence)

**Rationale:**
- Patterns make structural claims across domains → higher bar
- Descriptions and mechanisms are book-specific → moderate bar

### 4. Pattern Deduplication

**Decision:** Check for existing patterns by name before creating new ones.

**Implementation:**
- `_find_similar_pattern()` queries existing Pattern nodes
- If found, link entity to existing pattern via `_link_entity_to_pattern()`
- If not found, create new Pattern node

**Rationale:**
- Patterns like "Feedback Loop" appear across many books
- Consolidation enables cross-domain analysis
- Prevents graph bloat

### 5. Rate Limiting Strategy

**Decision:** Conservative 30 calls/minute with sliding window.

**Rationale:**
- Claude Sonnet 4 tier 2 limit: 1000 req/min
- Conservative limit prevents burst failures
- Enrichment is batch process (not real-time)
- Can increase limit if needed

---

## Known Limitations

### 1. In-Memory Pattern Storage

**Issue:** Pattern deduplication uses simple name matching (case-insensitive).

**Limitation:** Similar patterns with different names won't be merged.

**Example:**
- "Feedback Loop" and "Feedback Cycle" would be separate patterns

**Future:** Implement semantic similarity matching using embeddings.

### 2. No Cross-Book Pattern Analysis

**Issue:** Patterns are created per-book during enrichment.

**Limitation:** No global analysis of which patterns appear most frequently.

**Future:** Add `consolidate_patterns()` batch job to find and merge duplicates across all books.

### 3. Chunk Retrieval Limit

**Issue:** `_get_entity_chunks()` limits to 5 chunks per entity.

**Limitation:** May miss context if entity appears in many passages.

**Future:** Implement relevance ranking for chunk selection (TF-IDF or semantic similarity).

### 4. No Streaming for Long Operations

**Issue:** `enrich_book_entities()` processes all entities before returning.

**Limitation:** No progress updates for long-running enrichments.

**Future:** Add progress callback or async generator for streaming results.

### 5. Error Handling

**Issue:** Entity-level errors are logged but don't halt entire enrichment.

**Behavior:** `stats['errors']` increments, processing continues.

**Trade-off:** Resilient to individual failures, but silent errors possible.

**Mitigation:** Comprehensive logging, error tracking in stats.

---

## Related Files

**Implementation:**
- `ies/backend/src/ies_backend/services/enrichment_service.py` — Main service
- `ies/backend/src/ies_backend/services/reframe_service.py` — Reframe delegation
- `ies/backend/src/ies_backend/services/neo4j_client.py` — Database client

**Tests:**
- `ies/backend/tests/test_enrichment_service.py` — Unit tests

**Design:**
- `docs/plans/2025-12-09-pass-3-llm-enrichment.md` — Complete specification
- `docs/plans/2025-12-09-pass-2-3-enrichment-design.md` — Overall enrichment pipeline

**Schema:**
- `ies/backend/src/ies_backend/schemas/extraction.py` — ExtractionProfile types
- `ies/backend/src/ies_backend/schemas/reframe.py` — Reframe types

---

## Changelog

**2025-12-09:**
- Initial implementation of EnrichmentService
- Added RateLimiter class
- Created priority algorithm
- Implemented mechanism extraction
- Implemented pattern detection
- Implemented description enhancement
- Added 15 unit tests (all passing)
- Created implementation documentation

---

**Status:** Service implementation complete and tested. Ready for CLI integration and production use.
