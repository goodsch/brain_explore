# Facet Schema Design (Phase 2B)

**Date:** 2025-12-08
**Status:** Implemented
**Version:** 1.0

---

## Overview

The facet system enables **categorical drilling** in Flow Mode: entity → facet → sub-entity exploration. Facets are thematic groupings of related concepts under a parent entity.

**Example:** ADHD entity has facets like "Diagnosis & Assessment", "Neurobiology", "Treatment & Strategies", each containing relevant sub-entities.

---

## Schema Design

### Neo4j Graph Structure

```
(:Entity {name: "ADHD"})
    -[:HAS_FACET]->
(:Facet {name: "Diagnosis", description: "...", order: 0, entity: "ADHD"})
    <-[:BELONGS_TO]-
(:Concept {name: "DSM-5 Criteria"})
```

**Node Types:**
- **Facet**: Categorical grouping node
  - Properties:
    - `name`: Facet name (e.g., "Diagnosis & Assessment")
    - `description`: Brief explanation of facet scope
    - `order`: Integer for display ordering (0 = first)
    - `entity`: Parent entity name (for scoping)

**Relationship Types:**
- **HAS_FACET**: Entity → Facet (one entity has many facets)
- **BELONGS_TO**: Concept → Facet (one concept can belong to multiple facets)

### Pydantic Schemas

```python
class FacetEntity(BaseModel):
    """An entity within a facet."""
    name: str
    type: str  # Node type (Concept, Researcher, etc.)
    relationship: str = "BELONGS_TO"

class Facet(BaseModel):
    """A thematic facet grouping."""
    name: str
    description: str | None = None
    entity_count: int = 0
    entities: list[FacetEntity] = []

class EntityFacetsResponse(BaseModel):
    """Response from /graph/entity/{name}/facets."""
    entity_name: str
    entity_type: str
    facets: list[Facet] = []
```

---

## API Endpoints

### GET /graph/entity/{name}/facets

Get facets for an entity.

**Request:**
```bash
GET /graph/entity/ADHD/facets
```

**Response:**
```json
{
  "entity_name": "ADHD",
  "entity_type": "Concept",
  "facets": [
    {
      "name": "Diagnosis & Assessment",
      "description": "Diagnostic criteria and assessment tools",
      "entity_count": 3,
      "entities": [
        {
          "name": "DSM-5 Criteria",
          "type": "Concept",
          "relationship": "BELONGS_TO"
        },
        {
          "name": "ADHD Rating Scale",
          "type": "Tool",
          "relationship": "BELONGS_TO"
        }
      ]
    },
    {
      "name": "Neurobiology",
      "description": "Brain mechanisms underlying ADHD",
      "entity_count": 2,
      "entities": [
        {
          "name": "Dopamine",
          "type": "Neurotransmitter",
          "relationship": "BELONGS_TO"
        },
        {
          "name": "Prefrontal Cortex",
          "type": "Brain Region",
          "relationship": "BELONGS_TO"
        }
      ]
    }
  ]
}
```

**Error Cases:**
- 404: Entity not found in knowledge graph
- 500: Database error

---

## Service Methods

### GraphService.get_entity_facets(entity_name: str)

Retrieve facets and their entities for a given entity.

**Returns:** Dict with entity info and facets, or None if not found.

**Cypher Query:**
```cypher
// Check entity exists
MATCH (e {name: $name})
RETURN e, labels(e) as labels

// Get facets and entities
MATCH (e {name: $name})-[:HAS_FACET]->(f:Facet)
OPTIONAL MATCH (concept)-[r:BELONGS_TO]->(f)
WHERE concept.name IS NOT NULL
RETURN f.name, f.description, f.order,
       collect({name: concept.name, type: labels(concept)[0], relationship: type(r)}) as entities
ORDER BY f.order
```

### GraphService.create_facet(entity_name, facet_name, description, order)

Create a new facet for an entity.

**Returns:** True if successful, False otherwise.

**Cypher Query:**
```cypher
MATCH (e {name: $entity_name})
MERGE (f:Facet {name: $facet_name, entity: $entity_name})
ON CREATE SET f.description = $description, f.order = $order
MERGE (e)-[:HAS_FACET]->(f)
RETURN f
```

### GraphService.add_entity_to_facet(facet_name, entity_name, concept_name)

Add a concept to a facet.

**Returns:** True if successful, False otherwise.

**Cypher Query:**
```cypher
MATCH (f:Facet {name: $facet_name, entity: $entity_name})
MATCH (c {name: $concept_name})
MERGE (c)-[:BELONGS_TO]->(f)
RETURN f, c
```

---

## Facet Templates

Initial facets for key entities (from `flow-mode-evolution.md`):

### ADHD
1. **Diagnosis & Assessment** - Diagnostic criteria and assessment tools
2. **Symptoms & Presentation** - Observable symptoms and behavioral patterns
3. **Neurobiology** - Brain mechanisms and neuroscience
4. **Executive Function** - EF deficits and impact
5. **Time Perception** - Temporal processing differences
6. **Treatment & Strategies** - Interventions and management approaches

### Executive Function
1. **Components** - Core EF components (WM, inhibition, flexibility)
2. **Development** - EF development across lifespan
3. **Assessment** - EF measurement and evaluation
4. **Impairments** - EF deficits and disorders
5. **Interventions** - EF training and support

---

## Seeding Facets

Use the provided script to seed facets:

```bash
cd ies/backend
uv run python scripts/seed_facets.py
```

This creates facets for ADHD and Executive Function based on the templates above.

---

## Design Decisions

### Why Store Facets in Neo4j?

**Option A: Hardcoded templates** (simple, fast)
- Pro: No DB queries, instant response
- Con: Inflexible, can't evolve, no user customization

**Option B: Neo4j nodes** (chosen)
- Pro: Persistent, queryable, evolvable, supports future LLM generation
- Con: Requires DB queries, initial setup

**Option C: LLM-generated on demand** (future)
- Pro: Dynamic, context-aware
- Con: Slow, expensive, inconsistent

**Decision:** Start with B (Neo4j storage) with seed script for templates. Enables future evolution to C (LLM augmentation).

### Why BELONGS_TO Instead of CONTAINS?

- **BELONGS_TO** expresses concept → facet membership naturally
- Reads well: "DSM-5 Criteria BELONGS_TO Diagnosis facet"
- Allows concepts to belong to multiple facets (flexibility)

### Why Include `entity` Property on Facet?

- Scopes facets to entities (prevents collisions)
- Enables efficient querying: `MATCH (f:Facet {name: X, entity: Y})`
- Allows same facet name across entities (e.g., "Treatment" for ADHD and Depression)

---

## Testing

Comprehensive test coverage in `/tests/test_facets.py`:

- **get_entity_facets**: 5 tests (happy path, empty, null handling, not found, errors)
- **create_facet**: 4 tests (success, minimal params, errors, missing entity)
- **add_entity_to_facet**: 4 tests (success, errors, missing facet, missing concept)
- **Integration**: 1 test (create → populate → retrieve workflow)

Run tests:
```bash
uv run pytest tests/test_facets.py -v
```

---

## Frontend Integration

Flow Mode will use facets for categorical drilling:

1. **EntityFocus View**: Fetch facets via `/graph/entity/{name}/facets`
2. **Render Facet List**: Display facets as clickable cards
3. **FacetFocus View**: Click facet → show entities in that facet
4. **Navigate to Entity**: Click entity → navigate to EntityFocus for that entity

Trail progression:
```
Context → Question → Entity → Facet → Sub-Entity
```

---

## Future Enhancements

### Phase 3: LLM-Powered Facet Generation
- Analyze entity's related concepts
- Use LLM to generate thematic facets
- Store in Neo4j for caching

### Phase 4: User-Customizable Facets
- Users can create/edit facets
- Personal facet preferences per entity
- Merge with LLM-generated facets

### Phase 5: Cross-Entity Facets
- Facets that span multiple entities
- E.g., "Neuroscience" facet across ADHD, Depression, Anxiety
- Enables thematic exploration

---

## References

- Flow Mode Evolution Plan: `/docs/plans/flow-mode-evolution.md`
- Implementation: `/ies/backend/src/ies_backend/services/graph_service.py` (lines 411-571)
- Schema: `/ies/backend/src/ies_backend/schemas/graph.py` (lines 150-197)
- API: `/ies/backend/src/ies_backend/api/graph.py` (lines 258-304)
- Tests: `/ies/backend/tests/test_facets.py`
