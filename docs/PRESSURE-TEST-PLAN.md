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

#### 3.1 Session & Dialogue Services
**Status:** API endpoints exist
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

#### 3.2 Journey & Breadcrumb Services
**Status:** API endpoints exist
**Risk:** Journeys captured but not useful

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
| Readest Integration | **PARTIAL** | 2025-12-05 | D+ | 4/15 bugs fixed, UX pending |
| Question Engine | Pending | - | - | - |
| Knowledge Graph | Pending | - | - | - |
| Personal Graph | Pending | - | - | - |
| Session Services | Pending | - | - | - |
| Journey Services | Pending | - | - | - |
| Reframe Services | Pending | - | - | - |
| Template Services | Pending | - | - | - |
| Cross-App Integration | Pending | - | - | - |

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
- Core UX: Entity highlights clickable, question response input, journey breadcrumbs visible
- Design system integration (IES tokens → Readest)

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
