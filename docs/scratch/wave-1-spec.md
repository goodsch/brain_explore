# Wave 1 Specification: Neo4j Client Unification

**Date:** 2025-12-06
**Status:** In Progress
**Owner:** Claude (PM)

---

## Design Decisions (Finalized)

### 1. Architecture: Single Unified Class

**Decision:** Create single `UnifiedGraphClient` class combining all three existing clients.

**Rationale:**
- Personal-domain bridge requires atomic transactions across current client boundaries
- SPARKED_BY relationships between sparks and entities need single transaction context
- Composition would reintroduce coordination problems we're fixing

### 2. Entity Types: Preserve All 14

**Decision:** Support all entity types without collapse.

| Category | Types |
|----------|-------|
| Domain | Concept, Person, Theory, Framework, Assessment |
| Personal | Spark, Insight, Thread, FavoriteProblem |
| Enrichment | Reframe, Pattern, Mechanism, Method |
| Content | Book, Chunk |

**Implementation:** `ALLOWED_TYPES` set with validation, parameterized queries.

### 3. Connection Pool: Singleton with Lazy Init

**Decision:** Module-level singleton driver with lazy initialization.

```python
_driver: Driver | None = None

def get_driver() -> Driver:
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
            max_connection_lifetime=3600,
            max_connection_pool_size=50
        )
    return _driver
```

### 4. Migration: Backwards-Compatible Aliases

**Decision:** Create unified client alongside existing, provide aliases.

```python
# In neo4j_client.py (temporary)
from .unified_client import UnifiedGraphClient
KnowledgeGraph = UnifiedGraphClient  # Alias
```

### 5. Personal-Domain Bridge: New Methods

**Decision:** Add integration methods:

| Method | Purpose |
|--------|---------|
| `link_spark_to_entity(spark_id, entity_name)` | Create SPARKED_BY relationship |
| `find_sparks_for_entity(entity_name)` | Get user sparks for domain concept |
| `find_entities_for_spark(spark_id)` | Get domain concepts from spark |
| `enrich_entity_from_sparks(entity_name)` | Update entity with user insights |

---

## Implementation Tasks

### Task 1.1: Create UnifiedGraphClient (TDD)

**File:** `library/graph/unified_client.py`

**Test First:**
```python
# tests/test_unified_client.py
def test_add_entity_preserves_type():
    """Entity type should not collapse to generic Concept"""
    client = UnifiedGraphClient()
    client.add_entity("Test Framework", "Framework", {...})
    result = client.get_entity("Test Framework")
    assert result["type"] == "Framework"  # NOT "Concept"
```

**Methods to Include:**
- All 16 from KnowledgeGraph
- All 24 from ADHDKnowledgeGraph
- All 7 from GraphService
- 4 new bridge methods

### Task 1.2: Fix Cypher Injection

**Current Problem (neo4j_client.py:50):**
```python
# VULNERABLE
query = f"MERGE (e:{entity_type} {{name: $name}})"
```

**Fix:**
```python
ALLOWED_TYPES = {"Concept", "Person", "Theory", "Framework", ...}

def add_entity(self, name: str, entity_type: str, ...):
    if entity_type not in ALLOWED_TYPES:
        raise ValueError(f"Invalid entity type: {entity_type}")
    # Now safe to use in query
```

### Task 1.3: Migrate Backend Services

**Files to Update:**
- `ies/backend/src/ies_backend/services/graph_service.py` → import from unified_client
- `ies/backend/src/ies_backend/services/personal_service.py` → import from unified_client
- `scripts/ingest_calibre.py` → import from unified_client

### Task 1.4: Add Backwards Compatibility

**File:** `library/graph/neo4j_client.py`
```python
import warnings
from .unified_client import UnifiedGraphClient

def __getattr__(name):
    if name == "KnowledgeGraph":
        warnings.warn("KnowledgeGraph is deprecated, use UnifiedGraphClient", DeprecationWarning)
        return UnifiedGraphClient
    raise AttributeError(f"module has no attribute {name}")
```

---

## Verification Criteria

- [ ] All 94 existing backend tests pass
- [ ] Entity types preserved (no 14→4 collapse)
- [ ] Cypher injection vulnerability fixed
- [ ] Single connection pool (verify with `SHOW CONNECTIONS`)
- [ ] Personal-domain bridge methods work (SPARKED_BY relationships created)
- [ ] No import errors in any service

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `library/graph/unified_client.py` | CREATE |
| `library/graph/neo4j_client.py` | UPDATE (add deprecation alias) |
| `library/graph/adhd_graph_client.py` | UPDATE (add deprecation alias) |
| `ies/backend/.../graph_service.py` | UPDATE (change import) |
| `tests/test_unified_client.py` | CREATE |

---

## Blocked By

Nothing - this is the foundation task.

## Blocks

- Wave 1 Task 1.2 (User ID Unification)
- Wave 1 Task 1.3 (Session Persistence)
- All Wave 2+ tasks
