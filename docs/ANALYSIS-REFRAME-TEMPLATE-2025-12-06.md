# Reframe & Template Services - Pressure Test Analysis

**Date:** 2025-12-06
**Component:** Reframe & Template Services (Priority 3.3)
**Testing Pattern:** Four-Agent Critical Analysis

---

## Executive Summary

**Overall Grade: C (2.1/4.0)**

The Reframe & Template Services have **solid backend architecture** but suffer from **critical UX gaps** and a **missing feedback learning loop**. The documentation claims caching exists, but it doesn't. Features exist but are hidden behind technical barriers with minimal discoverability.

| Agent | Grade | Score | Key Finding |
|-------|-------|-------|-------------|
| Design Reviewer | B | 82% | Clean service layer, missing caching, inconsistent patterns |
| Principle Evaluator | C | 2.2/4.0 | Feedback collected but never used for learning |
| Bug Hunter | C+ | 2.3/4.0 | 15 bugs (1 critical), no rate limiting, cost runaway risk |
| UX Analyst | C- | 70% | 2 of 4 user stories achievable, features hidden |

**Critical Finding:** These are **content generators, not learning systems**. Feedback is collected but discarded. The "virtuous cycle" requires systems to improve over time — this is completely missing.

---

## Files Analyzed

**Backend:**
```
ies/backend/src/ies_backend/
├── api/
│   ├── reframe.py                    # Reframe API endpoints
│   └── template.py                   # Template API endpoints
├── services/
│   ├── reframe_service.py            # Claude integration, reframe generation
│   └── template_service.py           # Template loading, graph mapping
└── schemas/
    ├── reframe.py                    # Reframe models
    └── template.py                   # Template models
```

**Frontend:**
```
.worktrees/siyuan/ies/plugin/src/components/ReframesTab.svelte
.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/ReframesSection.tsx
.worktrees/siyuan/ies/plugin/src/views/ForgeMode.svelte (template usage)
```

---

## Principle Evaluation (C / 2.2/4.0)

### Thinking Partnership: 2/4

| Aspect | Status | Evidence |
|--------|--------|----------|
| Reframe generation works | Yes | Claude Sonnet 4 generates metaphors/analogies |
| Feedback loop exists | Yes | Thumbs up/down tracked in Neo4j |
| Feedback improves future | **No** | Votes stored but never queried for learning |
| Personalization | **No** | Same prompt for all users |

**Gap:** System doesn't learn. Feedback votes stored but never used to improve generation prompts or surface high-quality reframes.

### ADHD-Friendly Design: 3/4

| Aspect | Status | Evidence |
|--------|--------|----------|
| Low latency | Partial | Cached in Neo4j after generation |
| On-demand | Yes | Generate button, user controls |
| Natural UI | Yes | Tab placement, type grouping |
| Cognitive scaffolding | **No** | No hints, examples, or starters |

**Gap:** Templates add structure but don't reduce cognitive load. No activation energy reduction.

### Virtuous Cycle: 1/4

| Aspect | Status | Evidence |
|--------|--------|----------|
| Template graph mapping | Yes | Creates entities on session completion |
| Reframes enrich graph | **No** | Dead-end data, never referenced |
| Feedback → improvement | **No** | Votes collected, never analyzed |
| Cross-system integration | **No** | Reframes isolated from ForgeMode |

**Gap:** Only template graph mapping works. Everything else is disconnected.

### Domain Agnostic: 4/4

| Aspect | Status |
|--------|--------|
| Generic reframe prompts | Yes |
| Template schema universal | Yes |
| No hardcoded domain logic | Yes |

**This principle is fully delivered.**

---

## Design Issues (B / 82%)

### Strengths

1. **Clean Service Layer Separation** - API → Service → Schema properly enforced
2. **Proper Error Handling** - Exceptions converted to appropriate HTTP status codes
3. **Schema Quality** - Pydantic validation with field constraints
4. **LLM Integration** - Lazy initialization, dependency injection support

### Issues Found

| Issue | Severity | Location | Impact |
|-------|----------|----------|--------|
| No caching despite docs claiming it | High | `reframe_service.py:90-114` | Every request calls Claude API |
| Inconsistent singleton patterns | High | `reframe_service.py:335` vs `template.py:9` | Testing confusion |
| URL construction fragility | Medium | UI components | No typed API clients |
| Hardcoded LLM config | Medium | `reframe_service.py:99-102` | Can't tune model/temperature |
| Missing type hints | Low | `template_service.py` | Reduced IDE support |

---

## Bug Summary (C+ / 2.3/4.0)

### Bug Count by Severity

| Severity | Count | Key Issues |
|----------|-------|------------|
| Critical | 1 | No API key validation at startup |
| High | 3 | No rate limiting, no timeout, duplicate generation |
| Medium | 5 | Cypher injection (defense-in-depth), path traversal, case-sensitive validation |
| Low | 6 | Race condition, unbounded cache, missing logging |
| **Total** | **15** | |

### Critical Bug

**BUG-RT15: No API Key Validation on Startup**
- **Location:** `reframe_service.py:62`
- **Problem:** Application starts successfully even if `ANTHROPIC_API_KEY` missing. Error only on first request.
- **Impact:** Service appears healthy but fails at runtime. Health checks pass even though service is broken.

### High Severity Bugs

| ID | Issue | Impact |
|----|-------|--------|
| BUG-RT04 | No rate limiting on generate endpoint | Cost runaway: 100k requests = $300+ |
| BUG-RT03 | No timeout on Claude API calls | 600-second default timeout exhausts async loop |
| BUG-RT08 | Duplicate reframe generation | Clicking "Generate" 3x creates 15 reframes |

### Test Coverage

**Current:** 6 tests, ~40% code path coverage

**Missing:**
- Error path tests (API failures, timeouts, malformed responses)
- Security tests (injection attempts, path traversal)
- Concurrency tests (race conditions)
- Cache behavior tests
- Integration tests with real Neo4j

---

## UX Analysis (C- / 70%)

### User Story Achievement: 2 of 4

| Story | Status | Issue |
|-------|--------|-------|
| Understand difficult concept | Partial | Reframes hidden in collapsed accordion |
| Start structured session | Fails | No UI to browse templates, magic strings required |
| Provide feedback | Works | Thumbs up/down functional |
| Complete template session | Partial | No progress indicator, graph mapping invisible |

### UX Checklist: 2 of 7

- [x] Multiple reframe types available
- [x] Feedback mechanism exists
- [ ] **Reframes load quickly** - No caching, regenerates every request
- [ ] **Templates discoverable** - Hidden behind hardcoded mode mapping
- [ ] **Template sections have clear purpose** - Prompts buried in backend
- [ ] **Session output useful** - Concepts created silently
- [ ] **UI integration seamless** - Hidden in tabs/panels

### Critical Friction Points

1. **Template Discoverability = Zero**
   - Only 2 of 5 modes have templates
   - No indication when template unavailable
   - Must know magic `templateId` strings

2. **Reframe Generation Hidden**
   - Collapsed accordion below other content
   - Must scroll past entity details
   - No auto-generation on entity load

3. **Template Progress Invisible**
   - No "Step X of Y" indicator
   - No breadcrumb showing completed sections
   - `showProgress` default = `false`

4. **Graph Mapping = Black Box**
   - Concepts created silently
   - User has no idea session formalized their thinking
   - Virtuous cycle invisible

---

## Remediation Plan

### Phase 1: Critical Fixes (6 hours)

| Task | Priority | Est. |
|------|----------|------|
| Add API key validation at startup | P1 | 0.5h |
| Add rate limiting (10/min per user) | P1 | 1h |
| Add Claude API timeout (30 seconds) | P1 | 0.5h |
| Check existing reframes before generating | P1 | 1h |
| Add structured logging | P2 | 1h |
| Standardize singleton pattern | P2 | 2h |

### Phase 2: Caching & Performance (4 hours)

| Task | Priority | Est. |
|------|----------|------|
| Implement proper reframe caching | P1 | 2h |
| Add cache TTL and invalidation | P2 | 1h |
| Create typed API clients for frontend | P2 | 1h |

### Phase 3: UX Improvements (8 hours)

| Task | Priority | Est. |
|------|----------|------|
| Auto-generate 2-3 reframes on entity load | P1 | 2h |
| Show template structure before starting | P1 | 2h |
| Display graph mapping results after session | P1 | 1h |
| Add progress indicator to templates | P2 | 1h |
| Build template browser modal | P2 | 2h |

### Phase 4: Feedback Learning (6 hours)

| Task | Priority | Est. |
|------|----------|------|
| Query high-rated reframes for similar concepts | P2 | 2h |
| Modify generation prompt with examples | P2 | 2h |
| Add recommendation endpoint | P3 | 2h |

### Phase 5: Testing (4 hours)

| Task | Priority | Est. |
|------|----------|------|
| Error path tests | P1 | 1.5h |
| Security tests | P2 | 1h |
| Integration tests | P2 | 1.5h |

**Total Estimated Effort: 28 hours**

---

## The Core Problem

**These systems don't learn.**

Reframes and templates are static generators:
- Feedback collected but discarded
- No prompt adaptation based on success patterns
- No retrieval of high-quality reframes for similar concepts
- Templates are pure structure with no AI partnership

**What Good Looks Like:**
- Generation prompt adapts based on vote history
- High-rated reframes surfaced automatically
- Templates adjust scaffolding based on user patterns
- Personal graph insights inform generation

**Current Reality:**
- Static prompt regardless of history
- Feedback never queried
- Each system operates in isolation
- No improvement over time

---

## Impact Summary

### What Works

- Claude Sonnet 4 generates useful metaphors/analogies
- 5 reframe types provide variety
- Feedback collection (thumbs up/down)
- Template JSON schema well-designed
- Template graph mapping creates entities
- Domain-agnostic design (4/4)

### What's Broken

- No caching despite documentation claiming it
- Cost runaway risk (no rate limiting)
- Feedback never used for learning
- Templates hidden behind magic strings
- No progress indicators
- Graph mapping results invisible to user
- 60% of thinking modes have no templates

### Production Readiness

**Not recommended** without addressing:
1. Rate limiting (cost protection)
2. API key validation (startup safety)
3. Claude API timeout (reliability)
4. Basic caching (performance)

---

## Success Criteria

After remediation:

- [ ] Reframes cached, not regenerated on every request
- [ ] Rate limiting prevents cost runaway
- [ ] High-quality reframes surface first (sorted by votes)
- [ ] Templates discoverable via browser UI
- [ ] Progress indicator shows "Step X of Y"
- [ ] Graph mapping results shown to user
- [ ] 80%+ test coverage
- [ ] All critical/high bugs resolved
