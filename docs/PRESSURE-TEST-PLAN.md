# Pressure Testing Plan: Full System Evaluation

**Created:** 2025-12-05
**Trigger:** SiYuan plugin analysis revealed catastrophic implementation-principle gap
**Goal:** Systematically validate ALL system components against core principles

## The Discovery

The SiYuan plugin critical analysis revealed:
- Infrastructure exists but doesn't deliver on principles
- Features built but not validated against user experience
- Documentation describes ideal state, not reality

**This pattern likely exists elsewhere in the system.**

---

## Testing Philosophy

### What We're Testing For

Not "does it work?" but:
1. **Does it deliver on core principles?**
2. **Does it create genuine thinking partnership?**
3. **Is the user experience aligned with ADHD-friendly design?**
4. **Does data flow support the virtuous cycle?**
5. **Are cross-component integrations real or theoretical?**

### Four-Agent Analysis Pattern

For each component, deploy four specialized agents:

| Agent | Focus | Questions |
|-------|-------|-----------|
| **Design Reviewer** | Consistency, patterns | Does it look/feel like one system? |
| **Principle Evaluator** | Core principle adherence | Does it DO what we SAY it does? |
| **Bug Hunter** | Technical issues | What breaks? What's fragile? |
| **UX Analyst** | User experience flows | Can users achieve their goals? |

---

## Component Testing Queue

### Priority 1: User-Facing Components (Week 1-2)

#### 1.1 Readest Integration (Layer 4)
**Status:** Built, not pressure-tested
**Risk:** Same pattern as SiYuan - infrastructure without principle delivery

**Test Focus:**
- Does entity overlay actually help reading comprehension?
- Does flow panel create thinking partnership or just display info?
- Is journey capture useful or noise?
- Does text selection → entity lookup feel natural?
- Cross-app continuity: Can you resume Readest journey in SiYuan?

**Files to Analyze:**
```
.worktrees/readest/readest/apps/readest-app/src/
├── app/reader/components/
│   ├── FlowPanel.tsx
│   ├── EntityTypeFilter.tsx
│   └── flowpanel/*.tsx
├── store/flowModeStore.ts
├── hooks/useFlowEntity.ts
└── services/flow/
    ├── graphClient.ts
    └── journeyStorage.ts
```

#### 1.2 Backend Question Engine (Layer 2)
**Status:** 85/85 tests passing
**Risk:** Tests verify API contracts, not principle delivery

**Test Focus:**
- Do generated questions actually guide cognition?
- Is state detection accurate in real sessions?
- Do question classes map meaningfully to thinking modes?
- Is profile adaptation noticeable or cosmetic?
- Are approach selections appropriate for user states?

**Files to Analyze:**
```
ies/backend/src/ies_backend/
├── api/question_engine.py
├── services/
│   ├── state_detection_service.py
│   ├── approach_selection_service.py
│   └── question_templates_service.py
└── schemas/question_engine.py
```

### Priority 2: Data Layer (Week 2-3)

#### 2.1 Knowledge Graph Structure (Layer 1)
**Status:** 291 entities, 338 relationships (10 books indexed)
**Risk:** Graph structure may not support exploration patterns

**Test Focus:**
- Does relationship structure support meaningful exploration?
- Are entity types useful or too granular/too coarse?
- Do relationship types enable interesting discoveries?
- Is entity extraction quality sufficient?
- Can users actually find what they're looking for?

**Files to Analyze:**
```
library/graph/
├── entities.py
├── neo4j_client.py
├── adhd_ontology.py
└── adhd_graph_client.py

scripts/
├── ingest_calibre.py
└── auto_ingest_daemon.py
```

#### 2.2 Personal Graph (ADHD Ontology)
**Status:** Schema defined, minimal real usage
**Risk:** Designed based on research but not validated with real captures

**Test Focus:**
- Is spark capture actually low-friction?
- Do resonance signals help retrieval?
- Does energy-based navigation work in practice?
- Is the lifecycle (captured → exploring → anchored) meaningful?
- Can users find past sparks when they need them?

**Files to Analyze:**
```
library/graph/
├── adhd_ontology.py
├── adhd_graph_client.py

ies/backend/src/ies_backend/
├── api/personal.py
└── services/personal_graph_service.py
```

### Priority 3: Backend Services (Week 3-4)

#### 3.1 Session & Dialogue Services ✅ COMPLETE (Dec 6)
**Status:** ✅ ANALYZED - UX Grade C+ (2.5/4.0) - See ANALYSIS-SESSION-DIALOGUE-2025-12-06.md
**Risk:** Endpoints work but don't create meaningful sessions

**Test Focus:**
- Does session state persist correctly?
- Is dialogue context maintained appropriately?
- Do sessions feel like conversations or transactions?
- Is extraction from sessions accurate?
- Can sessions be meaningfully resumed?

**Files to Analyze:**
```
ies/backend/src/ies_backend/
├── api/session.py
├── services/
│   ├── session_service.py
│   └── extraction_service.py
└── schemas/session.py
```

#### 3.2 Journey & Breadcrumb Services ✅ COMPLETE (Dec 6)
**Status:** ✅ ANALYZED - Design Grade B+ (87%) - See ANALYSIS-JOURNEY-2025-12-06.md
**Risk:** Three parallel breadcrumb systems with unclear boundaries

**Test Focus:**
- Is journey tracking overhead worth it?
- Can users actually resume and benefit?
- Do breadcrumbs help reflection or just accumulate?
- Is cross-session continuity real?
- What happens to old journeys?

**Files to Analyze:**
```
ies/backend/src/ies_backend/
├── api/journey.py
├── services/journey_service.py
└── schemas/journey.py
```

**Key Findings:**
- Strong API design consistency (95%)
- Three parallel breadcrumb systems (Journey, Thinking, Flow) with unclear integration
- Missing thinking-to-journey promotion
- No journey tests
- Incomplete SiYuan integration

#### 3.3 Reframe & Template Services
**Status:** Recently added, minimal usage
**Risk:** Features exist but don't integrate into workflow

**Test Focus:**
- Do reframes actually help understanding?
- Are templates guiding or constraining?
- Is Claude reframe generation quality sufficient?
- Do templates map meaningfully to modes?
- Is caching strategy effective?

**Files to Analyze:**
```
ies/backend/src/ies_backend/
├── api/reframe.py
├── api/template.py
├── services/
│   ├── reframe_service.py
│   └── template_service.py
└── schemas/
    ├── reframe.py
    └── template.py
```

### Priority 4: Integration Points (Week 4)

#### 4.1 Readest ↔ Backend Integration
- Does entity overlay use live graph data?
- Is journey sync reliable?
- What happens when backend is down?

#### 4.2 SiYuan ↔ Backend Integration
- Is forwardProxy pattern reliable?
- Are session documents correctly linked to backend?
- Does spark promotion work end-to-end?

#### 4.3 SiYuan ↔ Readest Integration
- Can exploration state transfer between apps?
- Is there any cross-app awareness?
- Can you continue a journey started in Readest?

#### 4.4 Calibre ↔ Ingestion Pipeline
- Is auto-ingestion daemon reliable?
- Does entity extraction quality vary by book type?
- Are Book-Entity relationships useful?

---

## Testing Execution Protocol

### For Each Component:

**Step 1: Spawn Four Agents**
```
Task: Design Reviewer - [component] design consistency
Task: Principle Evaluator - [component] core principles
Task: Bug Hunter - [component] bugs and edge cases
Task: UX Analyst - [component] user experience flows
```

**Step 2: Synthesize Findings**
- Create `docs/ANALYSIS-[component]-[date].md`
- Grade against principles (A-F)
- Identify critical vs. high vs. medium issues
- Document root causes

**Step 3: Create Remediation Plan**
- Prioritize by principle impact
- Estimate effort
- Identify dependencies
- Add to tracking

**Step 4: Execute Fixes**
- Work through priority order
- Validate each fix against principles
- Update documentation

**Step 5: Re-Test**
- Verify fixes actually work
- Check for regression
- Confirm principle alignment

---

## Success Criteria

After full pressure testing, the system should demonstrate:

### Thinking Partnership (Core Principle #1)
- [ ] Questions invite response and reflection
- [ ] System adapts based on user responses
- [ ] Dialogue feels like conversation, not transaction
- [ ] User generates insights they couldn't alone

### ADHD-Friendly Design (Core Principle #2)
- [ ] Capture is genuinely low-friction (<10 seconds)
- [ ] Energy/resonance retrieval works in practice
- [ ] System adapts to user's current state
- [ ] Progress is visible and encouraging

### Question Classes Active (Core Principle #3)
- [ ] Classes guide, not just decorate
- [ ] Users notice different question types
- [ ] Mode transitions feel natural
- [ ] Cognitive patterns become visible

### Virtuous Cycle Complete (Core Principle #4)
- [ ] Dialogue → Patterns (profiles updated)
- [ ] Patterns → Exploration (guidance personalized)
- [ ] Exploration → Concepts (extraction works)
- [ ] Concepts → Enrichment (graph grows)

### Domain Agnostic (Core Principle #5)
- [ ] No hardcoded domain assumptions
- [ ] Works with any knowledge domain
- [ ] Configuration, not code changes

### Design Cohesion (Quality Criterion)
- [ ] Single design system used everywhere
- [ ] Consistent interaction patterns
- [ ] Dark/light themes work uniformly

---

## Tracking

### Current Status

| Component | Status | Analysis Date | Grade | Remediation |
|-----------|--------|---------------|-------|-------------|
| SiYuan Plugin | **COMPLETE** | 2025-12-05 | C→B+ | ✅ All critical items fixed |
| Readest Integration | **PARTIAL** | 2025-12-05 | D+→B- | 4/15 bugs fixed, ALL Core UX features VERIFIED working (overlay default-off), design system pending |
| Question Engine | **COMPLETE** | 2025-12-06 | C+ | 19 bugs found, remediation plan created |
| Knowledge Graph | **COMPLETE** | 2025-12-06 | D+ | 23 bugs found (5 critical), THREE Neo4j clients need unification |
| Personal Graph | **COMPLETE** | 2025-12-06 | C+ | 14 bugs (1 critical: zero tests), ADHD design 4.0/4.0, virtuous cycle broken |
| Session Services | **COMPLETE** | 2025-12-06 | D+ | 23 bugs (5 critical), 0% test coverage, no auth/persistence |
| Journey Services | **COMPLETE** | 2025-12-06 | C- | 23 bugs, THREE parallel systems, write-only (no UI access) |
| Reframe/Template | **COMPLETE** | 2025-12-06 | C | 15 bugs, no caching, feedback collected but never used |
| Cross-App Integration | **COMPLETE** | 2025-12-06 | D- | 18 bugs (3 critical), backend API exists but NEVER USED by frontends |

### SiYuan Remediation Complete (Dec 5)

Verified via code audit:
- ✅ Phase 1.1: Questions Interactive (`handleQuestionResponse()` dialogue loop)
- ✅ Phase 1.2: Question Classes Active (`QUESTION_CLASS_HINTS` cognitive guidance)
- ✅ Phase 1.3: Domain Agnostic (configurable notebook preferences)
- ✅ Phase 1.4: Backend Health Check (Dashboard status indicator)
- ✅ Phase 2.2: Concept Extraction Flow (`ConceptExtractor.svelte`)
- ✅ Phase 2.3: Energy Navigation (Dashboard energy/resonance filters)
- DEFERRED: Phase 2.1 Mode-Specific UI (single panel works well)

### Readest Bugs Status

| Bug | Severity | Status | Note |
|-----|----------|--------|------|
| BUG-R01 | Critical | ⚠️ OPEN | Event listeners in FoliateViewer (foliate-js complexity) |
| BUG-R02 | Critical | ✅ FIXED | Trie-based entity matching in entity.ts |
| BUG-R03 | High | ✅ FIXED | AbortController in flowModeStore |
| BUG-R04 | High | ✅ FIXED | Mount tracking in useFlowEntity |
| BUG-R05 | High | ⚠️ OPEN | Singleton config refresh |
| BUG-R06-15 | Med/Low | ⚠️ OPEN | Various UX and edge cases |

**Remaining Readest Work:**
- ✅ Entity highlights clickable (VERIFIED Dec 5) — Full chain implemented: entity.ts creates spans → iframeEventHandlers.ts dispatches events → useEntityClick.ts opens Flow panel. Overlay defaults to disabled; enable via EntityTypeFilter toggle.
- ✅ Question response input (VERIFIED Dec 5) — QuestionsSection.tsx: expandable questions, textarea input, Cmd+Enter shortcut, journey tracking via addThinkingPartnerExchange, bookmark feature
- ✅ Journey breadcrumbs visible (VERIFIED Dec 5) — JourneyBreadcrumb.tsx: step navigation, dwell time display, +N overflow, notes counter, rendered in FlowPanel.tsx line 163
- Design system integration (IES tokens → Readest)

### Question Engine Analysis Complete (Dec 6)

**Four-Agent Analysis Results:**
- Design Reviewer: B+ (87%) — Good patterns, service instantiation anti-pattern
- Principle Evaluator: C- (2.0/4.0) — Infrastructure exists, feedback loops missing
- Bug Hunter: C+ (75%) — 19 bugs (5 critical, 5 high, 6 medium, 3 low)
- UX Analyst: C+ (76%) — Technically sound, UX-incomplete

**Critical Findings:**
1. **Questions Not Used for Dialogue** — Backend generates questions but no feedback loop analyzes responses
2. **Nine Question Classes Decorative** — Classes assigned post-hoc via round-robin, not used for selection
3. **Service Instantiation Anti-Pattern** — API creates new instances instead of importing singletons
4. **Profile System Unused** — 6-dimensional profiles exist but ForgeMode doesn't pass user_id
5. **Missing UX Convenience** — No single `/question/next` endpoint for simple integration

**Bug Summary:**
| Severity | Count | Key Issues |
|----------|-------|------------|
| Critical | 5 | Race condition in service init, null pointer in template selection, silent JSON parsing failures |
| High | 5 | Template adaptation swallows KeyError, exploration markers use substring match |
| Medium | 6 | Profile loading failures, fallback approach duplicates, magic number thresholds |
| Low | 3 | Template library rebuilt on instantiation, mixed quote styles |

**Remediation Plan (20 hours total):**
- Phase 1 (3 hours): Fix service patterns, input validation, template edge cases
- Phase 2 (5 hours): Add `/question/next` endpoint, word boundary fixes
- Phase 3 (18 hours): Response analysis endpoint, functional question classes, feedback API
- Phase 4 (14 hours): Profile inference, session context preservation

**See:** `docs/ANALYSIS-QUESTION-ENGINE-2025-12-06.md` for complete analysis

### Knowledge Graph Analysis Complete (Dec 6)

**Four-Agent Analysis Results:**
- Design Reviewer: D+ (68%) — THREE disconnected Neo4j clients, schema collapses 14→4 types
- Principle Evaluator: C- (2.1/4.0) — Personal-Domain bridge missing, ADHD features decorative
- Bug Hunter: D+ (1.8/4.0) — 23 bugs (5 critical, 8 high, 7 medium, 3 low)
- UX Analyst: C (2.3/4.0) — No fulltext search, no discovery queries, features unused

**Critical Findings:**
1. **THREE Disconnected Neo4j Clients** — `KnowledgeGraph`, `ADHDKnowledgeGraph`, `GraphService` operate independently with different schemas
2. **Schema Collapses 14→4 Types** — Only Researcher/Concept/Theory/Assessment survive; all others become "Concept"
3. **Personal-Domain Bridge Missing** — Sparks cannot connect to book concepts, breaking virtuous cycle
4. **Cypher Injection Vulnerability** — F-string label interpolation allows query manipulation
5. **Ingestion Discards 70-90% Content** — 50-chunk limit means most book content never indexed

**Bug Summary:**
| Severity | Count | Key Issues |
|----------|-------|------------|
| Critical | 5 | Cypher injection, driver leaks, hardcoded credentials, content discard, fragmented architecture |
| High | 8 | Dead migration code, therapy-hardcoded prompts, JSON parsing failures, SQLite locking, race conditions |
| Medium | 7 | Missing fulltext index, ADHD features not in API, thread operations unused, no pagination |
| Low | 3 | Redundant constraints, magic numbers, inconsistent datetime handling |

**Remediation Plan (22 hours total):**
- Phase 1 (4 hours): Critical security fixes (Cypher injection, credentials, driver leaks)
- Phase 2 (8 hours): Unify Neo4j clients, restore full type system, bridge personal-domain graphs
- Phase 3 (6 hours): Expose ADHD features in API, add fulltext search, fix ingestion coverage
- Phase 4 (4 hours): Make extraction domain-agnostic, validate with non-therapy content

**See:** `docs/ANALYSIS-KNOWLEDGE-GRAPH-2025-12-06.md` for complete analysis

### Personal Graph Analysis Complete (Dec 6)

**Four-Agent Analysis Results:**
- Design Reviewer: C+ (78%) — Complete library layer bypass, schema field inconsistency
- Principle Evaluator: B+ (3.3/4.0) — ADHD-Friendly 4.0/4.0 perfect, Virtuous Cycle 2.0/4.0 broken
- Bug Hunter: D (1.7/4.0) — 14 bugs (1 critical: zero test coverage)
- UX Analyst: C (2.0/4.0) — Capture friction 600ms+, endpoint proliferation

**Critical Findings:**
1. **Zero Test Coverage** — `pytest -k personal` selects 0 of 94 tests (CRITICAL)
2. **Library Layer Bypass** — Service imports `Neo4jClient` directly, ignores `ADHDKnowledgeGraph`
3. **Virtuous Cycle Broken** — `source_id`/`concept_ids` are write-only properties, no graph relationships
4. **Missing Endpoints** — Thread and FavoriteProblem entities have zero API endpoints
5. **Schema Field Inconsistency** — `visit_count` (backend) vs `exploration_visits` (library)

**Positive Finding:**
- **ADHD-Friendly Design: 4.0/4.0** — 8 resonance signals, 3 energy levels, non-judgmental lifecycle all properly implemented

**Bug Summary:**
| Severity | Count | Key Issues |
|----------|-------|------------|
| Critical | 1 | Zero test coverage |
| High | 2 | Whitespace validation bypass, promote race condition |
| Medium | 6 | No driver shutdown, silent exceptions, DoS via unbounded limit |
| Low | 5 | Missing CRUD endpoints, datetime fallback |

**Remediation Plan (14 hours total):**
- Phase 1 (4 hours): Create test suite, fix whitespace validation, fix race condition
- Phase 2 (4 hours): Add graph relationships for concept_ids, integrate with library layer
- Phase 3 (3 hours): Add Thread/FavoriteProblem endpoints, spark update/delete
- Phase 4 (3 hours): Unified query endpoint, state transitions, limit bounds

**See:** `docs/ANALYSIS-PERSONAL-GRAPH-2025-12-06.md` for complete analysis

### Cross-App Integration Analysis Complete (Dec 6)

**Four-Agent Analysis Results:**
- Design Reviewer: C- (2.0/4.0) — Apps operate in parallel, not collaboration; no sync layer
- Principle Evaluator: F (0.5/4.0) — Backend Journey API complete but NEVER USED
- Bug Hunter: D+ (1.8/4.0) — 18 bugs (3 critical, 6 high, 5 medium, 4 low)
- UX Analyst: D (1.2/4.0) — 1 of 4 user stories achievable, apps are islands

**Critical Findings:**
1. **Journey API Never Called** — `endJourney()` returns journey but never calls `saveJourney()` to persist
2. **User ID Mismatch** — Backend/SiYuan use 'chris', Readest uses Supabase UUID
3. **No Sync Service Exists** — Three parallel data stores with zero synchronization
4. **Fire-and-Forget Calls** — Backend calls have no retry, errors silently dropped
5. **Zero Integration Tests** — No E2E tests verify cross-app communication

**Smoking Gun (flowModeStore.ts):**
```typescript
endJourney: () => {
  // ... calculates journey ...
  return completedJourney;  // NEVER CALLS saveJourney()!
},
```

**Bug Summary:**
| Severity | Count | Key Issues |
|----------|-------|------------|
| Critical | 3 | Journey data loss, user ID mismatch, no sync |
| High | 6 | Fire-and-forget, no retry, no conflict resolution |
| Medium | 5 | Missing error handling, no offline support |
| Low | 4 | Logging gaps, documentation drift |

**Remediation Plan (38 hours total):**
- Phase 1 (6 hours): Wire up existing APIs, call saveJourney(), unify user ID
- Phase 2 (8 hours): SiYuan Journey integration, display journey history
- Phase 3 (12 hours): Design and implement sync service with offline queue
- Phase 4 (6 hours): Cross-app deep links (SiYuan↔Readest)
- Phase 5 (6 hours): E2E integration tests

**The Core Problem:**
System built bottom-up (backend → frontends) but user journey integration never wired. The "virtuous cycle" is a documentation artifact, not operational reality.

**See:** `docs/ANALYSIS-CROSS-APP-INTEGRATION-2025-12-06.md` for complete analysis

### Issue Tracking

After each analysis, issues should be:
1. Documented in analysis file
2. Added to GitHub issues (if using)
3. Prioritized in remediation plan
4. Tracked to completion

---

## Timeline

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | SiYuan Plugin Remediation | Critical fixes complete |
| 2 | Readest Analysis + SiYuan continuation | Readest analysis doc |
| 3 | Backend Services Analysis | Service analysis docs |
| 4 | Integration Analysis + Bug Fixes | Integration analysis doc |
| 5 | Remediation Sprint | High-priority fixes |
| 6 | Re-testing | Verification of fixes |

---

## Lessons to Apply

From SiYuan analysis:

1. **Don't assume infrastructure = delivery** - APIs existing ≠ principles working
2. **Test user experience, not just code** - Technical tests miss UX gaps
3. **Validate against principles explicitly** - Each component must prove alignment
4. **Documentation must match reality** - Update or flag discrepancies
5. **Design systems must be enforced** - Having ≠ using
6. **Pressure test continuously** - Not just at major milestones

---

## Next Action

**Immediate:** Complete SiYuan plugin remediation (Week 1)
**Then:** Begin Readest pressure testing (Week 2)
**Ongoing:** Update this plan as findings emerge
