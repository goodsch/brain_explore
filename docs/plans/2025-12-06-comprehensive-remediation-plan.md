# Comprehensive System Remediation Plan

**Date:** 2025-12-06
**Purpose:** Meta-analysis of all pressure test findings with multi-agent remediation strategy
**Goal:** Transform documented infrastructure into operational virtuous cycle

---

## Executive Meta-Analysis

### The Core Pattern

All 8 pressure-tested components reveal the **same fundamental problem**:

> **Infrastructure exists. Wiring is missing. Learning loops are broken.**

| Component | Has API | Frontend Calls It | Data Flows Back | System Learns |
|-----------|---------|-------------------|-----------------|---------------|
| Knowledge Graph | ✓ | Partial | No | No |
| Question Engine | ✓ | ✓ | No | No |
| Personal Graph | ✓ | Partial | No | No |
| Session Services | ✓ | ✓ | No | No |
| Journey Services | ✓ | No | No | No |
| Reframe/Template | ✓ | ✓ | No | No |
| Cross-App | ✓ | No | No | No |

### Aggregate Statistics

| Metric | Value |
|--------|-------|
| Total bugs identified | 135 |
| Critical bugs | 20 |
| High severity bugs | 38 |
| Components with 0% test coverage | 4 (Personal, Session, Journey, Cross-App) |
| Average grade | D+ (1.9/4.0) |
| Estimated remediation hours | 200+ |

---

## Root Cause Analysis

### Root Cause #1: Architectural Fragmentation

**THREE separate Neo4j client implementations:**

| Client | Location | Purpose | Schema |
|--------|----------|---------|--------|
| `KnowledgeGraph` | `library/graph/neo4j_client.py` | Domain entities | 4 types (collapses 14→4) |
| `ADHDKnowledgeGraph` | `library/graph/adhd_graph_client.py` | Personal entities | 8 types (unused) |
| `GraphService` | `backend/services/graph_service.py` | API queries | Mixed patterns |

**Impact:** Personal-domain bridge impossible. Virtuous cycle structurally blocked.

### Root Cause #2: Frontend-Backend Disconnect

**Critical wiring gaps:**

| Gap | Evidence |
|-----|----------|
| `endJourney()` never calls `saveJourney()` | Readest journeys trapped in localStorage |
| SiYuan never queries `/journeys` API | Journey history invisible |
| No E2E integration tests | Zero verification of communication |
| Fire-and-forget calls | Backend errors silently ignored |

### Root Cause #3: Stateless Backend Design

**No persistence layer:**

- Sessions stored in-memory (lost on restart)
- No Redis/persistent cache
- User context not maintained across requests
- Profile system exists but unused (user_id not passed)

### Root Cause #4: User Identity Fragmentation

| App | User ID | Format |
|-----|---------|--------|
| Backend | Hardcoded | `'chris'` |
| SiYuan | Hardcoded | `'chris'` |
| Readest | Supabase | UUID |

**Impact:** Cross-app correlation impossible. Profile system broken.

### Root Cause #5: Missing Feedback Loops

Every system collects data but nothing learns:

| System | Collects | Uses for Learning |
|--------|----------|-------------------|
| Question Engine | State detection | Never adapts based on responses |
| Reframe Service | Thumbs up/down | Never improves generation |
| Journey Tracking | Breadcrumbs | Never analyzed for patterns |
| Profile System | 6 dimensions | Never updated from sessions |

---

## Dependency Graph

```
                    ┌─────────────────────────────────────────┐
                    │     ROOT: Neo4j Client Unification      │
                    │   (Prerequisite for everything else)    │
                    └─────────────────┬───────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
│ User ID Unification │   │ Session Persistence │   │ Personal-Domain     │
│ (Backend Profile)   │   │ (Redis)             │   │ Graph Bridge        │
└─────────┬───────────┘   └─────────┬───────────┘   └─────────┬───────────┘
          │                         │                         │
          └─────────────────────────┼─────────────────────────┘
                                    ▼
                    ┌─────────────────────────────────────────┐
                    │     Frontend-Backend Wiring             │
                    │   (Readest & SiYuan → Backend APIs)     │
                    └─────────────────┬───────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
│ Cross-App Sync      │   │ Journey Visibility  │   │ Question Feedback   │
│ (State sharing)     │   │ (UI for history)    │   │ (Response analysis) │
└─────────────────────┘   └─────────────────────┘   └─────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │     Learning Loops                      │
                    │   (Profile updates, prompt adaptation)  │
                    └─────────────────────────────────────────┘
```

### Execution Order (Blockers First)

**Wave 1: Foundation (Must complete before anything else)**
1. Neo4j client unification → Single `GraphClient` class
2. User ID unification → Backend profile system as source of truth
3. Session persistence → Redis for session state

**Wave 2: Wiring (Depends on Wave 1)**
4. Frontend-backend integration → Wire Readest/SiYuan to existing APIs
5. Personal-domain graph bridge → Create `SPARKED_BY` relationships
6. Security hardening → Auth, rate limiting, input validation

**Wave 3: Visibility (Depends on Wave 2)**
7. Journey UI → History view, synthesis display
8. Question feedback capture → Response analysis endpoint
9. Cross-app sync → State sharing mechanism

**Wave 4: Learning (Depends on Wave 3)**
10. Profile updates from sessions
11. Reframe prompt adaptation from votes
12. Question class selection from state

**Wave 5: Quality (Parallel with Wave 4)**
13. Test suites for all services
14. E2E integration tests
15. Documentation updates

---

## Multi-Agent Execution Strategy

### Agent Specializations

| Agent Type | Focus | Tools | Parallel? |
|------------|-------|-------|-----------|
| `backend-developer` | Neo4j unification, Redis, APIs | All backend tools | Wave 1 |
| `fullstack-developer` | Frontend-backend wiring | All tools | Wave 2-3 |
| `system-architect` | Cross-app sync design | Planning tools | Wave 2 |
| `critical-evaluator` | Verify each wave | Review tools | After each wave |
| `Explore` | Codebase investigation | Search tools | As needed |

### Scratch Document Strategy

For effective cross-agent communication, each wave produces:

1. **`/docs/scratch/wave-N-spec.md`** — Input specification for wave agents
2. **`/docs/scratch/wave-N-decisions.md`** — Decisions made during implementation
3. **`/docs/scratch/wave-N-blockers.md`** — Issues requiring escalation
4. **`/docs/scratch/wave-N-complete.md`** — Completion verification checklist

### Wave 1 Execution Plan

**Agent:** `backend-developer`

**Task 1.1: Neo4j Client Unification (8 hours)**
```
Prompt for agent:
"Create a unified GraphClient that replaces KnowledgeGraph, ADHDKnowledgeGraph,
and GraphService. Requirements:
- Single connection pool with proper lifecycle
- Support ALL 14 entity types (no type collapse)
- Parameterized queries (fix Cypher injection)
- Personal-domain graph in SAME client
- Backward compatible with existing code
- Write tests for each method

Files to modify:
- Create: library/graph/unified_client.py
- Update: All services to import from unified client
- Delete: After migration complete

Output: /docs/scratch/wave-1-task-1-complete.md"
```

**Task 1.2: User ID Unification (4 hours)**
```
Prompt for agent:
"Unify user identity to backend profile system. Requirements:
- Profile service is source of truth for user identity
- Generate UUID for new users, allow external ID mapping
- Update Readest graphClient to use profile ID (not Supabase UUID)
- Update SiYuan to fetch user ID from profile
- Update all backend services to accept user_id parameter

Files to modify:
- ies/backend/src/ies_backend/services/profile_service.py
- .worktrees/readest/...flowModeStore.ts
- .worktrees/siyuan/.../siyuan-structure.ts

Output: /docs/scratch/wave-1-task-2-complete.md"
```

**Task 1.3: Session Persistence (6 hours)**
```
Prompt for agent:
"Add Redis-backed session persistence. Requirements:
- Replace in-memory session store with Redis
- Session state survives server restarts
- Add session listing/resumption endpoints
- 24-hour TTL with extension on activity
- Proper cleanup on session end

Files to modify:
- ies/backend/src/ies_backend/services/chat_service.py
- Add: ies/backend/src/ies_backend/services/session_store.py
- docker-compose.yml (add Redis service)

Output: /docs/scratch/wave-1-task-3-complete.md"
```

### Wave 2 Execution Plan

**Agents:** `fullstack-developer` (×2 parallel), `system-architect`

**Task 2.1: Readest-Backend Wiring (Parallel A)**
```
Prompt for fullstack-developer:
"Wire Readest Flow panel to backend APIs. Requirements:
- endJourney() must call saveJourney()
- Add retry queue for failed backend calls
- Show sync status indicator in UI
- Journey history fetched from backend (not localStorage)
- Entity click → backend entity fetch

Files to modify:
- .worktrees/readest/.../flowModeStore.ts
- .worktrees/readest/.../graphClient.ts
- .worktrees/readest/.../journeyStorage.ts

Output: /docs/scratch/wave-2-task-1-complete.md"
```

**Task 2.2: SiYuan-Backend Wiring (Parallel B)**
```
Prompt for fullstack-developer:
"Wire SiYuan plugin to backend Journey API. Requirements:
- FlowMode exploration → backend journey recording
- Dashboard shows journey history from backend
- ForgeMode session → backend session API
- callBackendApi() returns errors instead of null

Files to modify:
- .worktrees/siyuan/.../FlowMode.svelte
- .worktrees/siyuan/.../Dashboard.svelte
- .worktrees/siyuan/.../siyuan-structure.ts

Output: /docs/scratch/wave-2-task-2-complete.md"
```

**Task 2.3: Cross-App Sync Design (Architect)**
```
Prompt for system-architect:
"Design cross-app sync mechanism. Deliverables:
- Sync protocol specification
- Conflict resolution strategy
- Offline queue design
- Event notification system (polling vs WebSocket vs SSE)
- Security considerations

Output: /docs/plans/cross-app-sync-design.md"
```

### Wave 3-5 Execution Plans

(Similar structure with specific prompts for each task)

---

## Skills Integration Protocol

### Mandatory Skills (MUST Use)

These skills are **required** for all implementation work. Not optional. Not "nice to have."

| Skill | When to Use | Enforcement |
|-------|-------------|-------------|
| `superpowers:verification-before-completion` | Before ANY claim of "done", "fixed", "passing" | Iron Law: Evidence THEN claim |
| `superpowers:test-driven-development` | ALL code changes | RED-GREEN-REFACTOR cycle |
| `superpowers:systematic-debugging` | Any bug or unexpected behavior | 4-phase investigation first |
| `superpowers:requesting-code-review` | After completing each task | Dispatch code-reviewer agent |

### Wave-Specific Skill Usage

**Wave 1: Foundation**
```
Skills Required:
1. superpowers:brainstorming → BEFORE designing unified GraphClient
2. superpowers:writing-plans → Create bite-sized implementation tasks
3. superpowers:test-driven-development → Write tests FIRST for each method
4. skill-codex → Heavy Neo4j unification implementation
5. superpowers:verification-before-completion → Run all tests BEFORE claiming done
6. superpowers:requesting-code-review → Review unified client before Wave 2
```

**Wave 2: Wiring (Parallel Tasks)**
```
Skills Required:
1. superpowers:dispatching-parallel-agents → Spawn 2 fullstack agents
2. superpowers:brainstorming → Design sync protocol (architect agent)
3. gemini-cli → Parallel code generation for Readest/SiYuan wiring
4. superpowers:test-driven-development → Write integration tests FIRST
5. superpowers:verification-before-completion → Verify E2E before claiming done
```

**Wave 3-4: Visibility & Learning**
```
Skills Required:
1. superpowers:writing-plans → Detailed UI implementation specs
2. superpowers:test-driven-development → Component tests FIRST
3. superpowers:requesting-code-review → Review each feature
4. gemini-cli → Cross-validate implementations with Google Search grounding
```

**Wave 5: Quality**
```
Skills Required:
1. superpowers:dispatching-parallel-agents → 3 agents for test suites
2. superpowers:verification-before-completion → 80%+ coverage verified
3. superpowers:requesting-code-review → Full codebase review
```

### Codex Skill Usage

Use `skill-codex` for **heavy implementation tasks** (>50 lines of new code):

```
Codex Execution Protocol:
1. Model Selection:
   - o3: Complex architectural changes (Neo4j unification)
   - o4-mini: Standard implementation (API wiring)

2. Sandbox Mode:
   - full-auto: For well-specified tasks with tests
   - suggest: When design decisions needed

3. Integration:
   - Always pass existing tests as validation
   - Generate scratch document with decisions made
   - Request code review after completion
```

**Wave 1 Codex Tasks:**
```bash
# Neo4j Unification (use o3 for complexity)
codex exec --model o3 --sandbox full-auto \
  "Create unified GraphClient in library/graph/unified_client.py that:
   - Replaces KnowledgeGraph, ADHDKnowledgeGraph, GraphService
   - Supports all 14 entity types (no collapse)
   - Uses parameterized queries (fix injection)
   - Passes all existing tests
   Write output to /docs/scratch/wave-1-task-1-complete.md"

# Redis Session Store (use o4-mini)
codex exec --model o4-mini --sandbox full-auto \
  "Add Redis-backed session persistence to ies/backend:
   - Create services/session_store.py
   - Update chat_service.py to use Redis
   - Add Redis to docker-compose.yml
   - 24-hour TTL with extension
   Write output to /docs/scratch/wave-1-task-3-complete.md"
```

### Gemini CLI Usage

Use `gemini-cli` for **parallel operations** and **cross-validation**:

```
Gemini Integration Protocol:
1. Parallel Code Generation:
   - Launch Gemini for Readest wiring while Claude handles SiYuan
   - Each generates implementation independently
   - Claude reviews and integrates both

2. Google Search Grounding:
   - Use for best practices research (e.g., "Neo4j connection pooling patterns")
   - Verify library usage against current docs

3. Cross-Validation:
   - Generate solution with Gemini, compare to Claude solution
   - Use differences to identify edge cases
```

**Example Parallel Execution:**
```bash
# Terminal 1: Claude handles SiYuan wiring
# Terminal 2: Gemini handles Readest wiring
gemini -p "Wire Readest flowModeStore to backend Journey API. Requirements:
  - endJourney() calls saveJourney() with retry
  - Journey history from backend, not localStorage
  - Add sync status indicator
  Output TypeScript implementation."
```

### Verification Protocol (Iron Law)

**NEVER claim completion without evidence.**

```
Before ANY "done" claim:
1. Run verification command(s)
2. Capture actual output
3. Confirm output matches expectation
4. ONLY THEN state completion

Verification Commands by Wave:
- Wave 1: `cd ies/backend && uv run pytest` (must show 94+ tests passing)
- Wave 2: `curl -X POST http://localhost:8081/journeys` (must return 200/201)
- Wave 3: Manual UI verification with screenshots
- Wave 4: Profile update verification with before/after
- Wave 5: `uv run pytest --cov` (must show 80%+)
```

### Test-Driven Development Protocol

**ALL code changes follow RED-GREEN-REFACTOR:**

```
TDD Cycle (Non-Negotiable):
1. RED: Write test that fails
   - Test describes expected behavior
   - Run test, confirm it fails
   - Commit failing test

2. GREEN: Write minimal code to pass
   - Only what's needed to pass test
   - No extra features
   - Run test, confirm it passes

3. REFACTOR: Improve without changing behavior
   - Clean up code
   - All tests still pass
   - Commit refactored code
```

**TDD for Each Wave Task:**
```
Wave 1 Example (GraphClient):
1. Write test: test_unified_client_creates_entity_preserving_type()
2. Run: pytest test_unified_client.py → FAIL
3. Implement: unified_client.py with type preservation
4. Run: pytest test_unified_client.py → PASS
5. Refactor: Extract common patterns
6. Run: pytest → ALL PASS
7. Commit: "Add unified GraphClient with type preservation"
```

### Parallel Agent Dispatch

Use `superpowers:dispatching-parallel-agents` for **3+ independent tasks**:

```
Wave 2 Parallel Dispatch:
1. Agent A: Readest-backend wiring (fullstack-developer)
2. Agent B: SiYuan-backend wiring (fullstack-developer)
3. Agent C: Cross-app sync design (system-architect)

Coordination:
- Each agent writes to /docs/scratch/wave-2-task-N-*.md
- Main orchestrator reads scratch docs for integration
- critical-evaluator reviews after all complete
```

**Dispatch Command Pattern:**
```
Task tool with run_in_background: true
- Launch Agent A for Readest
- Launch Agent B for SiYuan
- Launch Agent C for sync design
- Continue monitoring with AgentOutputTool
- Integrate results when all complete
```

### Code Review Protocol

After EACH task completion:

```
Code Review Checklist:
1. Use superpowers:requesting-code-review skill
2. Dispatch critical-evaluator agent with:
   - Files changed
   - Tests added
   - Requirements satisfied
3. Address all feedback before proceeding
4. Document review outcome in scratch doc
```

### Skill Invocation Reminders

**At start of EVERY implementation session:**
```
1. ☐ Check: Which skills apply to this task?
2. ☐ Invoke: Skill tool for each applicable skill
3. ☐ Announce: "Using [skill] for [purpose]"
4. ☐ Follow: Skill instructions exactly
5. ☐ Create: TodoWrite items for skill checklists
```

**Common Rationalizations to Reject:**
- "This is simple, no need for TDD" → WRONG. Use TDD.
- "I'll verify later" → WRONG. Verify NOW.
- "Skills are overkill for this" → WRONG. Use skills.
- "I already know the pattern" → WRONG. Read current skill version.

---

## CLAUDE.md Revamp Specification

### Current Problems

1. **Too long** — 800+ lines, most historical context
2. **Conflicting information** — Some sections outdated
3. **No PM authority** — Unclear decision-making protocol
4. **Context overload** — Every session loads all history

### New Structure

```markdown
# brain_explore — Intelligent Exploration System

## What This Is (10 lines)
[Brief system description]

## Current State (20 lines)
- Phase: 2c Integration → 3 Remediation
- Overall health: [Single grade]
- Critical blockers: [3-5 items]
- Next wave: [Current wave number]

## Project Manager Protocol (15 lines)
Claude acts as PM. Determines all next steps without asking.
- Check /docs/plans/ for current execution plan
- Check /docs/scratch/ for wave status
- Use TodoWrite for all task tracking
- Use specialized agents per wave specification

## Active Work (30 lines)
### Current Wave: [N]
- Task list with status
- Blockers
- Completion criteria

## Architecture (40 lines)
[Simplified 4-layer diagram]
[Key files per layer]

## Commands (20 lines)
[Essential commands only]

## Archived Context
See: /docs/archive/CLAUDE-historical.md
```

### Total: ~150 lines (vs current 800+)

### Complete New CLAUDE.md Content

```markdown
<!-- MANUAL -->
# brain_explore — Intelligent Exploration System

A four-layer thinking partnership tool: Knowledge Graph → Backend APIs → SiYuan Plugin → Readest Reader

## Current State

**Phase:** 3 - Remediation
**Health:** D+ (1.9/4.0) — 135 bugs identified across 8 components
**Current Wave:** 1 - Foundation (Neo4j unification, User ID, Session persistence)

### Critical Blockers
1. THREE Neo4j clients with schema drift
2. User ID fragmented (backend='chris', Readest=UUID)
3. Sessions lost on restart (in-memory only)
4. Frontend-backend wiring incomplete (journeys never saved)
5. Zero test coverage on 4 critical services

### Active Plan
See: `docs/plans/2025-12-06-comprehensive-remediation-plan.md`

---

## Project Manager Protocol

**Claude acts as PM.** Determine all next steps autonomously. Don't ask what to work on — identify optimal action and proceed.

### Decision Framework
1. Check `/docs/scratch/` for current wave status
2. Check `/docs/plans/` for execution strategy
3. Use TodoWrite for ALL task tracking
4. Use specialized agents per wave specification
5. Create scratch documents for cross-agent communication

### Agent Usage
| Wave | Agent Type | Purpose |
|------|------------|---------|
| 1 | `backend-developer` | Neo4j, Redis, APIs |
| 2-3 | `fullstack-developer` | Frontend-backend wiring |
| 2 | `system-architect` | Cross-app sync design |
| All | `critical-evaluator` | Wave verification |

### Scratch Document Protocol
Each wave produces:
- `wave-N-spec.md` — Input specification
- `wave-N-decisions.md` — Decisions during implementation
- `wave-N-blockers.md` — Issues for escalation
- `wave-N-complete.md` — Completion verification

---

## Architecture

```
Layer 1: Knowledge Graph (Neo4j + Qdrant)
├── library/graph/          # Graph clients (UNIFY THESE)
├── calibre/                # Book catalog (179 books)
└── scripts/ingest*.py      # Ingestion pipeline

Layer 2: Backend APIs (FastAPI)
├── ies/backend/src/ies_backend/api/     # 6 routers
├── ies/backend/src/ies_backend/services/ # Business logic
└── ies/backend/tests/                   # 94 tests

Layer 3: SiYuan Plugin (Svelte)
└── .worktrees/siyuan/ies/plugin/src/
    ├── views/              # ForgeMode, FlowMode, Dashboard
    └── utils/              # Backend integration

Layer 4: Readest (React/Next.js)
└── .worktrees/readest/readest/apps/readest-app/src/
    ├── store/              # flowModeStore (WIRE TO BACKEND)
    └── services/flow/      # graphClient, journeyStorage
```

---

## Essential Commands

```bash
# Services
docker compose up -d              # Start Neo4j, Qdrant, SiYuan
cd ies/backend && uv run uvicorn ies_backend.main:app --reload --port 8081

# Testing
cd ies/backend && uv run pytest   # Backend tests (94)
cd .worktrees/siyuan/ies/plugin && pnpm build  # SiYuan plugin
cd .worktrees/readest/readest/apps/readest-app && pnpm dev  # Readest

# Git
git status && git log --oneline -5  # Check state
```

---

## Key Documents

| Purpose | Location |
|---------|----------|
| Remediation plan | `docs/plans/2025-12-06-comprehensive-remediation-plan.md` |
| Pressure test results | `docs/PRESSURE-TEST-PLAN.md` |
| System design | `docs/SYSTEM-DESIGN.md` |
| Archived history | `docs/archive/CLAUDE-historical-2025-12-06.md` |

---

## Wave Status

### Wave 1: Foundation (Current)
- [ ] Neo4j client unification
- [ ] User ID unification
- [ ] Session persistence (Redis)

### Wave 2: Wiring
- [ ] Readest-backend integration
- [ ] SiYuan-backend integration
- [ ] Cross-app sync design

### Wave 3-5: (After Wave 2)
See remediation plan for details.

<!-- END MANUAL -->
```

---

## Success Criteria

### Wave 1 Complete When:
- [ ] Single `GraphClient` handles all Neo4j operations
- [ ] All entity types preserved (no 14→4 collapse)
- [ ] Profile service provides unified user identity
- [ ] Sessions persist across server restarts
- [ ] All existing tests still pass

### Wave 2 Complete When:
- [ ] Readest journeys save to backend
- [ ] SiYuan displays backend journey history
- [ ] Backend errors surface in frontends (no silent failures)
- [ ] Cross-app sync design approved

### Wave 3 Complete When:
- [ ] Journey history UI in both apps
- [ ] Question responses captured and stored
- [ ] Cross-app sync implemented (per design)

### Wave 4 Complete When:
- [ ] Profile updates from session patterns
- [ ] Reframe generation improves from feedback
- [ ] Question selection uses response history

### Wave 5 Complete When:
- [ ] 80%+ test coverage on all services
- [ ] E2E tests for critical user flows
- [ ] CLAUDE.md revamped and operational

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Neo4j migration breaks existing data | Medium | High | Create migration script, backup before |
| Redis adds complexity | Low | Medium | Use managed Redis if self-hosted fails |
| Cross-app sync conflicts | Medium | Medium | Start with last-write-wins, improve later |
| Agent coordination overhead | Medium | Low | Clear scratch document protocol |
| Scope creep | High | High | Strict wave boundaries, defer enhancements |

---

## Timeline Estimate

| Wave | Duration | Parallelism | Total Hours |
|------|----------|-------------|-------------|
| Wave 1 | 3-4 days | Sequential | 18h |
| Wave 2 | 2-3 days | 2× parallel | 16h |
| Wave 3 | 2-3 days | 2× parallel | 16h |
| Wave 4 | 3-4 days | Sequential | 20h |
| Wave 5 | 2-3 days | 3× parallel | 20h |
| **Total** | **12-17 days** | | **~90h** |

Note: Assumes focused execution with agent support. Real time depends on blockers discovered.

---

## Immediate Next Steps

1. **Create scratch document directory:** `/docs/scratch/`
2. **Archive current CLAUDE.md:** `/docs/archive/CLAUDE-historical-2025-12-06.md`
3. **Write new CLAUDE.md:** Per specification above
4. **Begin Wave 1:** Neo4j client unification

---

## Appendix: Component Bug Summary

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| Knowledge Graph | 5 | 8 | 7 | 3 | 23 |
| Question Engine | 5 | 5 | 6 | 3 | 19 |
| Personal Graph | 1 | 2 | 6 | 5 | 14 |
| Session Services | 5 | 12 | 6 | 0 | 23 |
| Journey Services | 5 | 8 | 7 | 3 | 23 |
| Reframe/Template | 1 | 3 | 5 | 6 | 15 |
| Cross-App | 3 | 6 | 5 | 4 | 18 |
| **Total** | **25** | **44** | **42** | **24** | **135** |
