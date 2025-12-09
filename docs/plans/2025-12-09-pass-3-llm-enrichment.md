# Pass 3 LLM Enrichment Pipeline Design

**Created:** 2025-12-09
**Status:** Design Complete
**Depends On:** Pass 1 (Entity Extraction) + Pass 2 (Relationship Extraction)

---

## Executive Summary

Pass 3 enriches extracted entities with AI-generated content that makes concepts more accessible, explains mechanisms, and connects ideas across domains. This pass transforms a sparse knowledge graph into a richly annotated exploration resource.

### Scope

Pass 3 performs four types of LLM-based enrichment:

1. **Reframes** — Metaphors, analogies, stories that make concepts accessible
2. **Mechanisms** — Step-by-step process descriptions (how things work)
3. **Patterns** — Recurring structural templates across domains
4. **Rich Descriptions** — Expanded explanations for sparse entities

### Integration Points

- **Existing API**: ReframeService already exists and works (`ies/backend/src/ies_backend/services/reframe_service.py`)
- **Ingestion Pipeline**: Integrates with `scripts/ingest_calibre.py` Pass 1 entity extraction
- **Status Lifecycle**: `entities_extracted → relationships_mapped → enriched`

---

## 1. Enrichment Architecture

### 1.1 System Components

```
┌──────────────────────────────────────────────────────┐
│             Pass 3 Enrichment Service                │
│                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │   Reframe    │  │  Mechanism   │  │  Pattern   │ │
│  │  Generator   │  │  Extractor   │  │  Detector  │ │
│  └──────────────┘  └──────────────┘  └────────────┘ │
│          │                 │                │        │
│          └─────────────────┴────────────────┘        │
│                         │                            │
│                    ┌────▼────┐                       │
│                    │Priority │                       │
│                    │Algorithm│                       │
│                    └────┬────┘                       │
└─────────────────────────┼──────────────────────────────┘
                          │
         ┌────────────────┴────────────────┐
         │                                  │
    ┌────▼─────┐                     ┌─────▼─────┐
    │  Neo4j   │                     │ Anthropic │
    │Knowledge │                     │   Claude  │
    │  Graph   │                     │  Sonnet 4 │
    └──────────┘                     └───────────┘
```

### 1.2 Priority Algorithm

Not all entities need enrichment. Prioritize by value:

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

# Enrichment strategy
entities_by_priority = sorted(entities, key=calculate_enrichment_priority, reverse=True)
top_20 = entities_by_priority[:20]  # Only enrich top concepts per book
```

**Rationale**: Enrichment is expensive (API costs + time). Focus on high-value entities.

---

## 2. Reframe Generation

### 2.1 Existing Implementation

**Service**: `ies/backend/src/ies_backend/services/reframe_service.py` (413 lines)

**Key Methods**:
- `generate_reframes(concept_id, count)` — Generates 1-10 reframes via Claude Sonnet 4
- `get_reframes(concept_id)` — Retrieves cached reframes from Neo4j
- `record_feedback(reframe_id, vote)` — Tracks helpful/confusing votes

**Reframe Types**:
- `metaphor` — X is like Y (cross-domain similarity)
- `analogy` — X:Y :: A:B (structural mapping)
- `story` — Narrative example embodying concept
- `pattern` — Recurring template or schema
- `contrast` — Key difference highlighting boundaries

**Neo4j Schema**:
```cypher
(:Reframe {
  id: "uuid",
  concept_id: "concept_123",
  type: "metaphor | analogy | story | pattern | contrast",
  domain: "therapy | personal | meta | system | practice",
  text: "Executive function is like a conductor...",
  strength: 0.85,  # 0-1 confidence score
  helpful_votes: 12,
  confusing_votes: 2,
  created_at: datetime()
})

(Concept)-[:HAS_REFRAME]->(Reframe)
```

### 2.2 LLM Prompt Strategy

**Current Prompt** (from `reframe_service.py` lines 26-48):

```python
REFRAME_PROMPT = """You are a wise therapeutic guide who specializes in reframing complex ideas.

Concept: {name}
Definition or summary: {definition}
Related concepts: {related}

Generate {count} distinct reframes that help someone understand or feel into this concept.
- Each reframe should pick a different strategy (metaphor, analogy, pattern, story, contrast).
- Keep them short (1-2 sentences) and concrete.
- Try to cover therapy, personal-life, and meta/system perspectives where helpful.

Respond ONLY with valid JSON matching:
{{
  "reframes": [
    {{
      "type": "metaphor | analogy | pattern | story | contrast",
      "domain": "therapy | personal | meta | system | practice",
      "text": "string",
      "strength": 0-1 number estimating clarity/impact
    }}
  ]
}}
"""
```

**Strengths**:
- Structured JSON output (easy parsing)
- Type diversity (forces different strategies)
- Domain coverage (therapy, personal, meta)
- Concreteness constraint (1-2 sentences)

**Enhancement for Ingestion Context**:

When calling during Pass 3, include book context:

```python
enhanced_prompt = REFRAME_PROMPT + """

**Book Context:**
This concept appears in: {book_title} by {book_author}
Book genre/domain: {book_genre}
Co-occurring concepts: {nearby_concepts}

Use this context to generate domain-appropriate reframes that connect to the book's perspective.
"""
```

### 2.3 Integration Strategy

**File**: `library/graph/enrichment_service.py` (new)

```python
from ies_backend.services.reframe_service import reframe_service

class EnrichmentService:
    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg
        self.reframe_service = reframe_service

    async def enrich_book_entities(self, calibre_id: int) -> dict:
        """Pass 3: Enrich entities for a book."""
        stats = {
            "reframes_generated": 0,
            "mechanisms_extracted": 0,
            "patterns_detected": 0,
            "descriptions_enriched": 0,
        }

        # Get entities for book, sorted by priority
        entities = self._get_prioritized_entities(calibre_id)

        for entity in entities[:20]:  # Top 20 only
            # Generate 3 reframes per high-value entity
            try:
                reframes = await self.reframe_service.generate_reframes(
                    concept_id=entity['id'],
                    count=3
                )
                stats['reframes_generated'] += len(reframes)
            except Exception as e:
                logger.error(f"Reframe generation failed for {entity['name']}: {e}")

        # Update book status
        self.kg.update_book_status(calibre_id, "enriched")

        return stats
```

### 2.4 Rate Limiting

**Claude Sonnet 4 Limits**:
- 1000 requests/minute (tier 2)
- ~$3 per million tokens

**Strategy**:
```python
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.call_times = []

    async def wait_if_needed(self):
        """Sleep if approaching rate limit."""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)

        # Remove old calls
        self.call_times = [t for t in self.call_times if t > minute_ago]

        if len(self.call_times) >= self.calls_per_minute:
            sleep_time = (self.call_times[0] - minute_ago).total_seconds()
            await asyncio.sleep(sleep_time)

        self.call_times.append(now)

# Usage
rate_limiter = RateLimiter(calls_per_minute=30)  # Conservative limit

async def generate_with_rate_limit(concept_id: str, count: int):
    await rate_limiter.wait_if_needed()
    return await reframe_service.generate_reframes(concept_id, count)
```

---

## 3. Mechanism Extraction

### 3.1 Definition

A **mechanism** explains the step-by-step process by which something works. Key components:
- **Steps**: Sequential actions or stages
- **Triggers**: What initiates the mechanism
- **Outcomes**: Effects or results
- **Components**: Parts involved

**Examples**:
- "Dopamine reward pathway" (neuroscience)
- "Feedback loop" (systems thinking)
- "Working memory encoding" (cognitive psychology)

### 3.2 Neo4j Schema

```cypher
(:Mechanism {
  id: "mech_uuid",
  name: "Dopamine Reward Pathway",
  description: "How dopamine signals reward and motivates behavior",
  steps: [
    "1. Novel stimulus detected by sensory cortex",
    "2. Ventral tegmental area releases dopamine",
    "3. Dopamine binds to receptors in nucleus accumbens",
    "4. Pleasure signal generated, behavior reinforced"
  ],
  triggers: ["Novel stimuli", "Anticipated reward", "Unexpected outcomes"],
  outcomes: ["Motivated behavior", "Learning reinforcement", "Habit formation"],
  source_book_calibre_id: 42,
  source_chunks: ["chunk_abc", "chunk_def"],
  confidence: 0.85,
  created_at: datetime()
})

# Relationships
(Mechanism)-[:EXPLAINS]->(Concept)
(Mechanism)-[:COMPONENT_OF]->(Theory)
(Book)-[:DESCRIBES]->(Mechanism)
```

### 3.3 Extraction Prompt

```python
MECHANISM_EXTRACTION_PROMPT = """Analyze this concept and extract a mechanistic explanation of how it works.

**Concept:** {concept_name}
**Type:** {concept_type}
**Current Description:** {concept_description}

**Context from book "{book_title}":**
{context_chunks}

**Instructions:**
1. Determine if this concept involves a process or mechanism (does it describe HOW something works?)
2. If yes, break down the mechanism into clear sequential steps
3. Identify triggers/inputs that initiate the mechanism
4. Identify outcomes/effects of the mechanism
5. Keep explanations ADHD-friendly:
   - Use short, concrete steps (3-7 steps ideal)
   - Avoid jargon where possible
   - Make progression clear and logical

**Return JSON:**
{{
  "has_mechanism": true/false,
  "mechanism": {{
    "name": "descriptive name for the mechanism",
    "description": "one-sentence overview",
    "steps": [
      "Step 1: [action/stage]",
      "Step 2: [action/stage]",
      ...
    ],
    "triggers": ["trigger 1", "trigger 2", ...],
    "outcomes": ["outcome 1", "outcome 2", ...],
    "confidence": 0.0-1.0
  }}
}}

If has_mechanism is false, set mechanism to null.
"""
```

### 3.4 Extraction Algorithm

```python
class MechanismExtractor:
    def __init__(self, kg: KnowledgeGraph, model: str = "claude-sonnet-4-20250514"):
        self.kg = kg
        self.client = Anthropic()
        self.model = model

    async def extract_mechanism(self, entity: dict, book_context: dict) -> dict | None:
        """Extract mechanism explanation for an entity."""

        # Get relevant chunks mentioning this entity
        chunks = self._get_entity_chunks(
            entity_name=entity['name'],
            calibre_id=book_context['calibre_id'],
            limit=5
        )

        context_text = "\n\n---\n\n".join([c['content'] for c in chunks])

        prompt = MECHANISM_EXTRACTION_PROMPT.format(
            concept_name=entity['name'],
            concept_type=entity.get('type', 'Unknown'),
            concept_description=entity.get('description', 'No description available'),
            book_title=book_context['title'],
            context_chunks=context_text[:3000]  # Limit token usage
        )

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        result = self._parse_mechanism_response(response.content[0].text)

        if result and result['has_mechanism'] and result['mechanism']['confidence'] >= 0.7:
            # Store in Neo4j
            mechanism_id = await self._create_mechanism_node(
                mechanism_data=result['mechanism'],
                entity_id=entity['id'],
                book_calibre_id=book_context['calibre_id'],
                source_chunks=[c['id'] for c in chunks]
            )
            return {"mechanism_id": mechanism_id, "name": result['mechanism']['name']}

        return None

    async def _create_mechanism_node(self, mechanism_data: dict, entity_id: str,
                                      book_calibre_id: int, source_chunks: list[str]) -> str:
        """Create Mechanism node and relationships."""
        mechanism_id = str(uuid.uuid4())

        query = """
        MATCH (e) WHERE e.id = $entity_id OR e.name = $entity_id
        MATCH (b:Book {calibre_id: $calibre_id})
        CREATE (m:Mechanism {
          id: $mechanism_id,
          name: $name,
          description: $description,
          steps: $steps,
          triggers: $triggers,
          outcomes: $outcomes,
          confidence: $confidence,
          source_book_calibre_id: $calibre_id,
          source_chunks: $source_chunks,
          created_at: datetime()
        })
        MERGE (m)-[:EXPLAINS]->(e)
        MERGE (b)-[:DESCRIBES]->(m)
        RETURN m
        """

        await Neo4jClient.execute_write(query, {
            "mechanism_id": mechanism_id,
            "entity_id": entity_id,
            "calibre_id": book_calibre_id,
            "name": mechanism_data['name'],
            "description": mechanism_data['description'],
            "steps": mechanism_data['steps'],
            "triggers": mechanism_data['triggers'],
            "outcomes": mechanism_data['outcomes'],
            "confidence": mechanism_data['confidence'],
            "source_chunks": source_chunks
        })

        return mechanism_id
```

### 3.5 When to Extract Mechanisms

Not all concepts have mechanisms. Target these entity types:

| Entity Type | Extract Mechanism? | Rationale |
|-------------|-------------------|-----------|
| Concept | ✅ Yes | Often describe processes |
| Theory | ✅ Yes | Usually have explanatory mechanisms |
| Framework | ✅ Yes | Operational frameworks have steps |
| Assessment | ❌ No | Tools, not processes |
| Person | ❌ No | People don't have mechanisms |
| Pattern | ⚠️ Maybe | If pattern describes a dynamic process |

**Filter**:
```python
MECHANISM_ELIGIBLE_TYPES = {'Concept', 'Theory', 'Framework', 'DynamicPattern'}

def should_extract_mechanism(entity: dict) -> bool:
    """Determine if entity is eligible for mechanism extraction."""
    if entity.get('type') not in MECHANISM_ELIGIBLE_TYPES:
        return False

    # Skip if already has mechanism
    if entity.get('has_mechanism', False):
        return False

    # Require minimum description length
    desc = entity.get('description', '')
    if len(desc) < 30:
        return False

    return True
```

---

## 4. Pattern Detection

### 4.1 Definition

A **pattern** is a recurring structural template that appears across multiple domains. Patterns are meta-level abstractions.

**Examples**:
- "Feedback Loop" (appears in systems, biology, psychology)
- "Tipping Point" (appears in physics, social dynamics, ecosystems)
- "Oscillation" (appears in electronics, emotions, markets)
- "Emergence" (appears in complexity science, consciousness, organizations)

### 4.2 Neo4j Schema

```cypher
(:Pattern {
  id: "pattern_uuid",
  name: "Feedback Loop",
  description: "A cyclical process where outputs influence inputs",
  structural_elements: [
    "Input signal",
    "Process/transformation",
    "Output signal",
    "Feedback path (positive or negative)"
  ],
  variants: [
    "Positive feedback (amplifying)",
    "Negative feedback (stabilizing)",
    "Delayed feedback (oscillating)"
  ],
  examples_across_domains: [
    "Thermostat control system (engineering)",
    "Dopamine reinforcement (neuroscience)",
    "Social media engagement (digital psychology)"
  ],
  source_books: [42, 57, 89],  # calibre_ids where pattern appears
  created_at: datetime()
})

# Relationships
(Pattern)-[:APPEARS_IN]->(Concept)
(Pattern)-[:ANALOGOUS_TO]->(Pattern)
(Book)-[:DEMONSTRATES]->(Pattern)
```

### 4.3 Extraction Prompt

```python
PATTERN_DETECTION_PROMPT = """Analyze this concept to determine if it represents a recurring structural pattern.

**Concept:** {concept_name}
**Type:** {concept_type}
**Description:** {concept_description}

**Context from book:**
{context_chunks}

**Instructions:**
A pattern is a structural template that can appear across multiple domains. Examples:
- Feedback Loop (control systems, neuroscience, economics)
- Tipping Point (phase transitions, social movements, ecosystems)
- Emergence (complexity science, consciousness, culture)
- Oscillation (electrical circuits, mood cycles, market swings)

1. Determine if this concept describes a structural pattern (not just a domain-specific idea)
2. If yes, identify:
   - Core structural elements (what are the key components?)
   - Variants (how does the pattern manifest differently?)
   - Cross-domain examples (where else does this pattern appear?)

**Return JSON:**
{{
  "is_pattern": true/false,
  "pattern": {{
    "name": "pattern name",
    "description": "structural description (domain-agnostic)",
    "structural_elements": ["element 1", "element 2", ...],
    "variants": ["variant 1", "variant 2", ...],
    "examples_across_domains": [
      "domain 1: example",
      "domain 2: example",
      ...
    ],
    "confidence": 0.0-1.0
  }}
}}

If is_pattern is false, set pattern to null.
"""
```

### 4.4 Pattern Detection Algorithm

```python
class PatternDetector:
    def __init__(self, kg: KnowledgeGraph, model: str = "claude-sonnet-4-20250514"):
        self.kg = kg
        self.client = Anthropic()
        self.model = model

    async def detect_pattern(self, entity: dict, book_context: dict) -> dict | None:
        """Detect if entity represents a structural pattern."""

        # Only check high-level concepts
        if entity.get('type') not in {'Concept', 'Theory', 'Framework', 'DynamicPattern'}:
            return None

        # Get context
        chunks = self._get_entity_chunks(
            entity_name=entity['name'],
            calibre_id=book_context['calibre_id'],
            limit=3
        )

        context_text = "\n\n---\n\n".join([c['content'] for c in chunks])

        prompt = PATTERN_DETECTION_PROMPT.format(
            concept_name=entity['name'],
            concept_type=entity.get('type', 'Unknown'),
            concept_description=entity.get('description', 'No description'),
            context_chunks=context_text[:2000]
        )

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        result = self._parse_pattern_response(response.content[0].text)

        if result and result['is_pattern'] and result['pattern']['confidence'] >= 0.75:
            # Create Pattern node if new, or link existing pattern
            pattern_id = await self._create_or_link_pattern(
                pattern_data=result['pattern'],
                entity_id=entity['id'],
                book_calibre_id=book_context['calibre_id']
            )
            return {"pattern_id": pattern_id, "name": result['pattern']['name']}

        return None

    async def _create_or_link_pattern(self, pattern_data: dict, entity_id: str,
                                       book_calibre_id: int) -> str:
        """Create new Pattern node or link to existing one."""

        # Check if pattern already exists (by name similarity)
        existing = await self._find_similar_pattern(pattern_data['name'])

        if existing:
            # Link entity to existing pattern
            pattern_id = existing['id']
            await self._link_entity_to_pattern(entity_id, pattern_id, book_calibre_id)
        else:
            # Create new Pattern node
            pattern_id = str(uuid.uuid4())

            query = """
            MATCH (e) WHERE e.id = $entity_id OR e.name = $entity_id
            MATCH (b:Book {calibre_id: $calibre_id})
            CREATE (p:Pattern {
              id: $pattern_id,
              name: $name,
              description: $description,
              structural_elements: $structural_elements,
              variants: $variants,
              examples_across_domains: $examples,
              source_books: [$calibre_id],
              created_at: datetime()
            })
            MERGE (p)-[:APPEARS_IN]->(e)
            MERGE (b)-[:DEMONSTRATES]->(p)
            RETURN p
            """

            await Neo4jClient.execute_write(query, {
                "pattern_id": pattern_id,
                "entity_id": entity_id,
                "calibre_id": book_calibre_id,
                "name": pattern_data['name'],
                "description": pattern_data['description'],
                "structural_elements": pattern_data['structural_elements'],
                "variants": pattern_data['variants'],
                "examples": pattern_data['examples_across_domains']
            })

        return pattern_id
```

### 4.5 Pattern Consolidation

Over time, multiple books may describe the same pattern with different names. Consolidate:

```python
async def consolidate_patterns(self):
    """Find and merge duplicate patterns."""
    query = """
    MATCH (p1:Pattern), (p2:Pattern)
    WHERE id(p1) < id(p2)
      AND (p1.name = p2.name OR p1.name IN p2.aliases OR p2.name IN p1.aliases)
    RETURN p1, p2
    """

    duplicates = await Neo4jClient.execute_query(query)

    for record in duplicates:
        # Merge p2 into p1
        await self._merge_patterns(record['p1'], record['p2'])
```

---

## 5. Rich Description Enhancement

### 5.1 Purpose

Some entities have terse descriptions extracted during Pass 1. Enhance them with:
- Expanded explanations
- Context from book
- Accessible language

**Target**: Entities with description < 50 characters

### 5.2 Enhancement Prompt

```python
DESCRIPTION_ENHANCEMENT_PROMPT = """Expand the description of this concept using context from the book.

**Concept:** {concept_name}
**Type:** {concept_type}
**Current Description:** {current_description}

**Context from book "{book_title}":**
{context_chunks}

**Instructions:**
1. Preserve the core meaning of the current description
2. Expand to 2-3 sentences (100-150 words)
3. Make it accessible to non-experts
4. Include key aspects: what it is, why it matters, how it relates to other concepts
5. Use concrete examples where possible

**Return JSON:**
{{
  "enhanced_description": "expanded description here",
  "key_aspects": ["aspect 1", "aspect 2", ...],
  "confidence": 0.0-1.0
}}
"""
```

### 5.3 Implementation

```python
class DescriptionEnhancer:
    def __init__(self, kg: KnowledgeGraph, model: str = "claude-sonnet-4-20250514"):
        self.kg = kg
        self.client = Anthropic()
        self.model = model

    async def enhance_description(self, entity: dict, book_context: dict) -> bool:
        """Enhance entity description with richer content."""

        current_desc = entity.get('description', '')

        # Only enhance if description is too short
        if len(current_desc) >= 50:
            return False

        # Get context chunks
        chunks = self._get_entity_chunks(
            entity_name=entity['name'],
            calibre_id=book_context['calibre_id'],
            limit=3
        )

        if not chunks:
            return False

        context_text = "\n\n---\n\n".join([c['content'] for c in chunks])

        prompt = DESCRIPTION_ENHANCEMENT_PROMPT.format(
            concept_name=entity['name'],
            concept_type=entity.get('type', 'Unknown'),
            current_description=current_desc or "No description available",
            book_title=book_context['title'],
            context_chunks=context_text[:2000]
        )

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )

        result = self._parse_enhancement_response(response.content[0].text)

        if result and result['confidence'] >= 0.7:
            # Update entity description
            await self._update_entity_description(
                entity_id=entity['id'],
                description=result['enhanced_description'],
                key_aspects=result['key_aspects']
            )
            return True

        return False

    async def _update_entity_description(self, entity_id: str, description: str,
                                          key_aspects: list[str]) -> None:
        """Update entity description in Neo4j."""
        query = """
        MATCH (e) WHERE e.id = $entity_id OR e.name = $entity_id
        SET e.description = $description,
            e.key_aspects = $key_aspects,
            e.description_enriched_at = datetime()
        """

        await Neo4jClient.execute_write(query, {
            "entity_id": entity_id,
            "description": description,
            "key_aspects": key_aspects
        })
```

---

## 6. Orchestration: EnrichmentService

### 6.1 Service Architecture

**File**: `library/graph/enrichment_service.py` (new, ~300 lines)

```python
import asyncio
import logging
from typing import Any

from anthropic import Anthropic

from ies_backend.services.reframe_service import reframe_service
from library.graph.unified_client import UnifiedGraphClient

logger = logging.getLogger(__name__)


class EnrichmentService:
    """Orchestrates Pass 3 LLM enrichment for book entities."""

    def __init__(self, kg: UnifiedGraphClient):
        self.kg = kg
        self.reframe_service = reframe_service
        self.mechanism_extractor = MechanismExtractor(kg)
        self.pattern_detector = PatternDetector(kg)
        self.description_enhancer = DescriptionEnhancer(kg)
        self.rate_limiter = RateLimiter(calls_per_minute=30)

    async def enrich_book_entities(self, calibre_id: int,
                                     enable_reframes: bool = True,
                                     enable_mechanisms: bool = True,
                                     enable_patterns: bool = True,
                                     enable_descriptions: bool = True) -> dict:
        """
        Run Pass 3 enrichment for all high-value entities in a book.

        Args:
            calibre_id: Book ID from Calibre
            enable_reframes: Generate reframes (default True)
            enable_mechanisms: Extract mechanisms (default True)
            enable_patterns: Detect patterns (default True)
            enable_descriptions: Enhance descriptions (default True)

        Returns:
            Statistics dict with counts of enrichments
        """
        logger.info(f"Starting Pass 3 enrichment for book {calibre_id}")

        stats = {
            "calibre_id": calibre_id,
            "reframes_generated": 0,
            "mechanisms_extracted": 0,
            "patterns_detected": 0,
            "descriptions_enriched": 0,
            "entities_processed": 0,
            "errors": 0,
        }

        # Load book context
        book_context = self._get_book_context(calibre_id)
        if not book_context:
            logger.error(f"Book {calibre_id} not found in graph")
            return stats

        # Get prioritized entities
        entities = self._get_prioritized_entities(calibre_id, limit=20)
        logger.info(f"Enriching {len(entities)} high-priority entities")

        # Process each entity
        for entity in entities:
            stats['entities_processed'] += 1
            logger.info(f"Enriching entity: {entity['name']} ({entity['type']})")

            try:
                # 1. Reframes (cheapest, always useful)
                if enable_reframes and not entity.get('has_reframes'):
                    reframe_count = await self._generate_reframes_for_entity(
                        entity, book_context
                    )
                    stats['reframes_generated'] += reframe_count

                # 2. Mechanisms (expensive, selective)
                if enable_mechanisms and should_extract_mechanism(entity):
                    if await self._extract_mechanism_for_entity(entity, book_context):
                        stats['mechanisms_extracted'] += 1

                # 3. Patterns (expensive, high value)
                if enable_patterns and entity['type'] in PATTERN_ELIGIBLE_TYPES:
                    if await self._detect_pattern_for_entity(entity, book_context):
                        stats['patterns_detected'] += 1

                # 4. Descriptions (cheap, fill gaps)
                if enable_descriptions and len(entity.get('description', '')) < 50:
                    if await self._enhance_description_for_entity(entity, book_context):
                        stats['descriptions_enriched'] += 1

            except Exception as e:
                logger.error(f"Enrichment failed for {entity['name']}: {e}")
                stats['errors'] += 1
                continue

        # Update book status
        self.kg.update_book_status(calibre_id, "enriched")

        logger.info(f"Pass 3 complete: {stats}")
        return stats

    async def _generate_reframes_for_entity(self, entity: dict,
                                             book_context: dict) -> int:
        """Generate reframes for entity using existing ReframeService."""
        await self.rate_limiter.wait_if_needed()

        try:
            reframes = await self.reframe_service.generate_reframes(
                concept_id=entity['id'],
                count=3
            )
            return len(reframes)
        except Exception as e:
            logger.error(f"Reframe generation failed: {e}")
            return 0

    async def _extract_mechanism_for_entity(self, entity: dict,
                                             book_context: dict) -> bool:
        """Extract mechanism explanation for entity."""
        await self.rate_limiter.wait_if_needed()

        result = await self.mechanism_extractor.extract_mechanism(entity, book_context)
        return result is not None

    async def _detect_pattern_for_entity(self, entity: dict,
                                          book_context: dict) -> bool:
        """Detect if entity represents a structural pattern."""
        await self.rate_limiter.wait_if_needed()

        result = await self.pattern_detector.detect_pattern(entity, book_context)
        return result is not None

    async def _enhance_description_for_entity(self, entity: dict,
                                                book_context: dict) -> bool:
        """Enhance terse entity description."""
        await self.rate_limiter.wait_if_needed()

        return await self.description_enhancer.enhance_description(entity, book_context)

    def _get_book_context(self, calibre_id: int) -> dict | None:
        """Load book metadata for context."""
        with self.kg.driver.session() as session:
            result = session.run(
                """
                MATCH (b:Book {calibre_id: $calibre_id})
                RETURN b.title as title, b.author as author,
                       b.genres as genres, b.description as description
                """,
                {"calibre_id": calibre_id}
            )
            record = result.single()
            if not record:
                return None

            return {
                "calibre_id": calibre_id,
                "title": record['title'],
                "author": record['author'],
                "genres": record.get('genres', []),
                "description": record.get('description', '')
            }

    def _get_prioritized_entities(self, calibre_id: int, limit: int = 20) -> list[dict]:
        """Get high-value entities for enrichment."""
        with self.kg.driver.session() as session:
            result = session.run(
                """
                MATCH (b:Book {calibre_id: $calibre_id})-[:MENTIONS]->(e)
                WITH e, count(*) as mention_count
                RETURN e.id as id, e.name as name, e.type as type,
                       e.description as description, mention_count,
                       exists((e)-[:HAS_REFRAME]->()) as has_reframes,
                       exists((e)<-[:EXPLAINS]-()) as has_mechanism
                ORDER BY mention_count DESC
                LIMIT $limit
                """,
                {"calibre_id": calibre_id, "limit": limit}
            )

            entities = []
            for record in result:
                entity = dict(record)
                entity['priority'] = calculate_enrichment_priority(entity)
                entities.append(entity)

            # Sort by calculated priority
            entities.sort(key=lambda e: e['priority'], reverse=True)
            return entities
```

---

## 7. CLI Integration

### 7.1 Updated ingest_calibre.py

**New flags**:

```bash
# Run Pass 3 only on specific book
python scripts/ingest_calibre.py --pass3 --id 42

# Run Pass 3 with selective enrichments
python scripts/ingest_calibre.py --pass3 --id 42 --no-mechanisms --no-patterns

# Run full pipeline (Pass 1 + Pass 2 + Pass 3)
python scripts/ingest_calibre.py --full --id 42

# Batch enrichment on all books with status "relationships_mapped"
python scripts/ingest_calibre.py --enrich-all --limit 10
```

### 7.2 Code Changes

**File**: `scripts/ingest_calibre.py`

```python
# Add imports
from library.graph.enrichment_service import EnrichmentService

# Add CLI arguments
parser.add_argument("--pass3", action="store_true",
                    help="Run Pass 3 enrichment only")
parser.add_argument("--full", action="store_true",
                    help="Run all passes (1+2+3)")
parser.add_argument("--enrich-all", action="store_true",
                    help="Run Pass 3 on all books with status 'relationships_mapped'")
parser.add_argument("--no-reframes", action="store_true",
                    help="Skip reframe generation")
parser.add_argument("--no-mechanisms", action="store_true",
                    help="Skip mechanism extraction")
parser.add_argument("--no-patterns", action="store_true",
                    help="Skip pattern detection")
parser.add_argument("--no-descriptions", action="store_true",
                    help="Skip description enhancement")

# Add Pass 3 execution logic
async def run_pass3(calibre_id: int, args) -> dict:
    """Run Pass 3 enrichment."""
    console.print(f"\n[bold blue]Pass 3:[/] LLM enrichment for book {calibre_id}")

    kg = KnowledgeGraph()
    enricher = EnrichmentService(kg)

    stats = await enricher.enrich_book_entities(
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

# Main execution
if args.pass3:
    if args.id:
        await run_pass3(args.id, args)
    else:
        console.print("[red]Error:[/] --pass3 requires --id")
elif args.enrich_all:
    # Find books with status "relationships_mapped"
    books = get_books_ready_for_enrichment(limit=args.limit)
    console.print(f"[bold]Enriching {len(books)} books[/]")

    for book in books:
        await run_pass3(book['calibre_id'], args)
        await asyncio.sleep(2)  # Rate limiting
```

---

## 8. Cost Analysis

### 8.1 Per-Book Costs

| Enrichment Type | API Calls | Cost/Call | Total/Book |
|-----------------|-----------|-----------|------------|
| Reframes (3 per entity, 20 entities) | 60 | $0.003 | $0.18 |
| Mechanisms (10 entities) | 10 | $0.01 | $0.10 |
| Patterns (5 entities) | 5 | $0.01 | $0.05 |
| Descriptions (15 entities) | 15 | $0.002 | $0.03 |
| **Total Pass 3** | **90** | - | **$0.36** |

**Assumptions**:
- Claude Sonnet 4: ~$3 per million input tokens, ~$15 per million output tokens
- Average prompt: 1000 tokens input, 500 tokens output
- Cost per call: ~$0.01

### 8.2 179-Book Library Estimate

- Total books: 179
- Pass 3 cost per book: $0.36
- **Total cost**: 179 × $0.36 = **$64.44**

**Optimization**: Run Pass 3 only on high-value books (100 books) → $36

---

## 9. Testing Strategy

### 9.1 Unit Tests

**File**: `ies/backend/tests/test_enrichment_service.py`

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from library.graph.enrichment_service import EnrichmentService

@pytest.mark.asyncio
async def test_reframe_generation():
    """Test reframe generation for entity."""
    kg = MagicMock()
    service = EnrichmentService(kg)

    entity = {
        "id": "concept_123",
        "name": "Executive Function",
        "type": "Concept",
        "description": "Cognitive control processes"
    }

    book_context = {
        "calibre_id": 42,
        "title": "ADHD 2.0",
        "author": "Barkley"
    }

    with patch.object(service.reframe_service, 'generate_reframes',
                     return_value=[{"id": "r1"}, {"id": "r2"}]):
        count = await service._generate_reframes_for_entity(entity, book_context)

    assert count == 2

@pytest.mark.asyncio
async def test_mechanism_extraction():
    """Test mechanism extraction for processual concept."""
    kg = MagicMock()
    service = EnrichmentService(kg)

    entity = {
        "id": "concept_dopamine",
        "name": "Dopamine Reward Pathway",
        "type": "Concept",
        "description": "How dopamine signals reward"
    }

    with patch.object(service.mechanism_extractor, 'extract_mechanism',
                     return_value={"mechanism_id": "mech_123"}):
        result = await service._extract_mechanism_for_entity(entity, {})

    assert result is True

@pytest.mark.asyncio
async def test_priority_calculation():
    """Test entity priority scoring."""
    from library.graph.enrichment_service import calculate_enrichment_priority

    entity = {
        "type": "Concept",
        "mention_count": 50,
        "description": "Short desc",
        "has_reframes": False
    }

    priority = calculate_enrichment_priority(entity)

    # Should score high: priority type + high mentions + needs description + no reframes
    assert priority >= 0.8
```

### 9.2 Integration Tests

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_pass3_enrichment(test_book_calibre_id):
    """Test complete Pass 3 pipeline on test book."""
    kg = KnowledgeGraph()
    service = EnrichmentService(kg)

    stats = await service.enrich_book_entities(
        calibre_id=test_book_calibre_id,
        enable_reframes=True,
        enable_mechanisms=True,
        enable_patterns=True,
        enable_descriptions=True
    )

    assert stats['entities_processed'] > 0
    assert stats['reframes_generated'] > 0
    assert stats['errors'] == 0

    # Verify book status updated
    book_status = kg.get_book_status(test_book_calibre_id)
    assert book_status == "enriched"
```

---

## 10. Implementation Tasks

### Priority 1: Reframes (High Value, Low Effort)

- [ ] Create `EnrichmentService` with reframe orchestration
- [ ] Add priority algorithm for entity selection
- [ ] Integrate with existing `ReframeService`
- [ ] Add `--pass3` flag to `ingest_calibre.py`
- [ ] Write unit tests for reframe generation
- [ ] Test on 5 books, measure quality

**Estimate**: 4 hours

### Priority 2: Mechanisms (Medium Value, Medium Effort)

- [ ] Design `Mechanism` Neo4j schema
- [ ] Create `MechanismExtractor` class
- [ ] Implement mechanism extraction prompt
- [ ] Add `_create_mechanism_node()` with EXPLAINS relationship
- [ ] Write unit tests for mechanism extraction
- [ ] Test on 3 books with process-heavy concepts

**Estimate**: 6 hours

### Priority 3: Rich Descriptions (Medium Value, Low Effort)

- [ ] Create `DescriptionEnhancer` class
- [ ] Implement description enhancement prompt
- [ ] Add description update logic in Neo4j
- [ ] Integrate into `EnrichmentService`
- [ ] Write unit tests

**Estimate**: 3 hours

### Priority 4: Patterns (High Value, High Effort)

- [ ] Design `Pattern` Neo4j schema
- [ ] Create `PatternDetector` class
- [ ] Implement pattern detection prompt
- [ ] Add pattern consolidation logic (merge duplicates)
- [ ] Add APPEARS_IN relationship creation
- [ ] Write unit tests
- [ ] Test on 5 books, validate cross-domain patterns

**Estimate**: 8 hours

---

## 11. Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Reframe Quality** | >70% helpful votes | User feedback in UI |
| **Mechanism Completeness** | >75% of process concepts have mechanisms | Manual audit of 50 samples |
| **Pattern Cross-Domain Coverage** | >3 domains per pattern | Neo4j query |
| **Description Enhancement** | <5% confusion rate | User feedback |
| **Processing Time** | <5 minutes per book | Timing logs |
| **API Cost** | <$0.40 per book | Cost tracking |
| **Error Rate** | <5% of entities | Error logs |

---

## 12. Future Enhancements

### 12.1 Adaptive Enrichment

Use feedback to adjust enrichment strategy:

```python
def get_enrichment_strategy(book_context: dict) -> dict:
    """Tailor enrichment based on book genre."""
    genre = book_context.get('genres', [])[0] if book_context.get('genres') else 'general'

    if genre == 'neuroscience':
        return {
            'enable_mechanisms': True,
            'enable_patterns': False,
            'reframe_count': 5  # More analogies for dense content
        }
    elif genre == 'self-help':
        return {
            'enable_mechanisms': False,
            'enable_patterns': True,
            'reframe_count': 3
        }
    else:
        return {
            'enable_mechanisms': True,
            'enable_patterns': True,
            'reframe_count': 3
        }
```

### 12.2 Cross-Book Pattern Mining

After enriching multiple books, mine for shared patterns:

```cypher
MATCH (p:Pattern)<-[:DEMONSTRATES]-(b:Book)
WITH p, count(DISTINCT b) as book_count
WHERE book_count >= 3
RETURN p.name, book_count, collect(b.title)
ORDER BY book_count DESC
```

### 12.3 Mechanism Chains

Link mechanisms that build on each other:

```cypher
MATCH (m1:Mechanism)-[:EXPLAINS]->(c:Concept)<-[:DEPENDS_ON]-(m2:Mechanism)
MERGE (m2)-[:BUILDS_ON]->(m1)
```

---

## 13. Appendix: Example Enrichment

### Book: "ADHD 2.0" by Edward Hallowell

**Entity**: Executive Function (Concept)

**Pass 1 Output**:
- Name: "Executive Function"
- Type: Concept
- Description: "Cognitive control processes"
- Mention Count: 47

**Pass 3 Enrichment**:

**Reframes Generated**:
1. **Metaphor**: "Executive function is like a conductor orchestrating an orchestra — it coordinates timing, suppresses distractions, and keeps all sections playing in harmony."
2. **Analogy**: "Just as a thermostat regulates temperature by monitoring and adjusting, executive function monitors your actions and adjusts behavior to meet goals."
3. **Story**: "Think of a project manager juggling deadlines, team communication, and budget constraints — that's your executive function managing daily life."

**Mechanism Extracted**:
- Name: "Executive Function Regulation Cycle"
- Steps:
  1. "Goal setting: Prefrontal cortex defines target behavior"
  2. "Working memory: Holds goal and context active"
  3. "Inhibition: Suppresses competing impulses"
  4. "Monitoring: Evaluates progress toward goal"
  5. "Adjustment: Updates behavior based on feedback"
- Triggers: ["Novel task", "Competing demands", "Time pressure"]
- Outcomes: ["Goal achievement", "Impulse control", "Flexible problem-solving"]

**Pattern Detected**: None (concept is domain-specific, not a structural pattern)

**Description Enhanced**:
"Executive function refers to the set of cognitive control processes that enable us to plan, organize, inhibit impulses, and flexibly switch between tasks. These processes are primarily mediated by the prefrontal cortex and include working memory, cognitive flexibility, and inhibitory control. Executive function is crucial for managing daily life, from completing multi-step tasks to regulating emotional responses. In ADHD, executive function deficits manifest as difficulty sustaining attention, poor time management, and impulsive decision-making."

---

**End of Document**
