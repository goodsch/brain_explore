# Wave 5 Specification: Quality - Test Coverage

**Date:** 2025-12-06
**Phase:** 3 - Remediation
**Target:** 80%+ test coverage on 4 critical services

---

## Objective

Add comprehensive test suites for the 4 services identified as having zero test coverage in the remediation plan:

1. **journey_service.py** - Journey tracking and synthesis
2. **chat_service.py** - Session management and AI chat
3. **personal_graph_service.py** - Personal knowledge sparks
4. **graph_service.py** - Domain knowledge graph queries

---

## Services Analysis

### 1. JourneyService (495 lines, 10 methods)

**Public Methods to Test:**
| Method | Description | Dependencies |
|--------|-------------|--------------|
| `create_journey()` | Create new journey with entry point | Neo4j |
| `get_journey()` | Retrieve journey by ID with steps/marks/exchanges | Neo4j |
| `list_journeys()` | List user's journeys with pagination | Neo4j |
| `update_journey()` | Add steps/marks/exchanges to journey | Neo4j |
| `delete_journey()` | Delete journey and related nodes | Neo4j |
| `generate_synthesis()` | AI-powered journey summary | Neo4j, Anthropic API |

**Private Methods (test via public API):**
- `_add_step()`, `_add_mark()`, `_add_exchange()`, `_get_anthropic_client()`

**Mocking Strategy:**
- Mock `neo4j_driver` for all database operations
- Mock `anthropic.Anthropic` for synthesis generation
- Use `pytest.fixture` for common journey data

### 2. ChatService (308 lines, 11 methods)

**Public Methods to Test:**
| Method | Description | Dependencies |
|--------|-------------|--------------|
| `start_session()` | Create new chat session with profile context | Neo4j, SessionStore, ProfileService |
| `chat_stream()` | Stream AI responses | Anthropic API, SessionStore |
| `get_session()` | Retrieve session by ID | SessionStore |
| `end_session()` | Close session | SessionStore |
| `list_sessions()` | List user's sessions | SessionStore |
| `resume_session()` | Resume existing session | SessionStore |

**Mocking Strategy:**
- Mock `session_store` (already tested separately)
- Mock `profile_service` (already tested separately)
- Mock `anthropic.Anthropic` for AI responses
- Mock `state_detection_service`, `approach_selection_service`

### 3. PersonalGraphService (342 lines, 9 methods)

**Public Methods to Test:**
| Method | Description | Dependencies |
|--------|-------------|--------------|
| `create_spark()` | Create personal spark node | Neo4j |
| `get_spark()` | Retrieve spark by ID | Neo4j |
| `visit_spark()` | Record visit, update visit count | Neo4j |
| `promote_to_insight()` | Upgrade spark to insight | Neo4j |
| `find_sparks_by_resonance()` | Query by resonance level | Neo4j |
| `find_sparks_by_energy()` | Query by energy level | Neo4j |
| `find_unvisited_sparks()` | Find sparks not recently visited | Neo4j |
| `get_stats()` | Get personal graph statistics | Neo4j |

**Mocking Strategy:**
- Mock `neo4j_driver` for all database operations
- Test schema creation via `_ensure_schema()` indirectly

### 4. GraphService (287 lines, 7 methods)

**Public Methods to Test:**
| Method | Description | Dependencies |
|--------|-------------|--------------|
| `find_related_concepts()` | Find entities related to a concept | Neo4j |
| `find_supporting_chunks()` | Find text chunks supporting entity | Neo4j |
| `get_stats()` | Get graph statistics | Neo4j |
| `search_concepts()` | Search entities by text | Neo4j |
| `get_most_connected()` | Get most connected entities | Neo4j |
| `get_entities_by_book()` | Get entities from a book | Neo4j |
| `get_entities_by_calibre_id()` | Get entities by Calibre ID | Neo4j |

**Mocking Strategy:**
- Mock `neo4j_driver` for all database operations

---

## Test Implementation Plan

### Phase 1: JourneyService Tests (Priority: High)
1. Test `create_journey()` - creates journey node with correct properties
2. Test `get_journey()` - retrieves journey with all related data
3. Test `list_journeys()` - pagination and filtering works
4. Test `update_journey()` - adding steps/marks/exchanges
5. Test `delete_journey()` - cleanup of related nodes
6. Test `generate_synthesis()` - AI generation and fallback

### Phase 2: ChatService Tests (Priority: High)
1. Test `start_session()` - creates session with profile context
2. Test `chat_stream()` - streaming responses work
3. Test `get_session()` / `end_session()` - basic CRUD
4. Test `list_sessions()` - user's sessions listed
5. Test `resume_session()` - session continuity

### Phase 3: PersonalGraphService Tests (Priority: Medium)
1. Test `create_spark()` - creates spark with properties
2. Test `get_spark()` - retrieves spark
3. Test `visit_spark()` - updates visit count
4. Test `promote_to_insight()` - status change and connections
5. Test finder methods - resonance, energy, unvisited queries
6. Test `get_stats()` - statistics calculation

### Phase 4: GraphService Tests (Priority: Medium)
1. Test `find_related_concepts()` - relationship traversal
2. Test `search_concepts()` - text search
3. Test `get_stats()` - graph metrics
4. Test entity retrieval by book/Calibre ID

---

## Success Criteria

- [ ] All 4 services have test files
- [ ] Each public method has at least 1 test
- [ ] Edge cases covered (empty results, not found, errors)
- [ ] Mocking properly isolates dependencies
- [ ] All tests pass: `uv run pytest` shows 150+ tests
- [ ] No regressions: existing 122 tests still pass

---

## Files to Create

```
ies/backend/tests/
├── test_journey_service.py    # NEW
├── test_chat_service.py       # NEW
├── test_personal_graph_service.py  # NEW
├── test_graph_service.py      # NEW
```

---

## TDD Note

Since we're adding tests to existing code:
1. Write test describing expected behavior
2. Run test - if it PASSES, code works correctly
3. If test FAILS, we found a bug to fix
4. Fix bug following RED-GREEN-REFACTOR cycle
