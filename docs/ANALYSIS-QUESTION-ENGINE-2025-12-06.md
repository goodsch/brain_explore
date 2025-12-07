# Backend Question Engine - Pressure Test Analysis

**Date:** 2025-12-06
**Component:** Backend Question Engine (Layer 2)
**Testing Method:** Four-Agent Critical Analysis

---

## Executive Summary

**Overall Grade: C+ (2.3/4.0)**

The Backend Question Engine demonstrates **strong technical architecture with research-backed templates**, but fails to deliver on core IES principles due to missing feedback loops and superficial frontend integration.

| Agent | Grade | Key Finding |
|-------|-------|-------------|
| Design Reviewer | B+ (87%) | Good patterns, critical service instantiation anti-pattern |
| Principle Evaluator | C- (2.0/4.0) | Infrastructure exists, feedback loops missing |
| Bug Hunter | C+ (75%) | 19 bugs (5 critical, 5 high, 6 medium, 3 low) |
| UX Analyst | C+ (76%) | Technically sound, UX-incomplete |

---

## What Works Well

### 1. Research-Backed Template Library
- **42 question templates** across 5 inquiry approaches
- Real academic citations (Paul & Elder, Gendlin, De Jong & Berg, Meadows)
- Directness variants (direct/balanced/gentle) with meaningfully different phrasings
- Templates include when-to-use guidance and source citations

### 2. Comprehensive State Detection
- 8 user states: FLOWING, STUCK, OVERWHELMED, EXPLORING, PROCESSING, UNCERTAIN, EMOTIONAL, TIRED
- Word boundary matching prevents false positives ("workflow" doesn't match "flow")
- Repetition detection using Jaccard similarity (35% threshold)
- Priority-ordered classification with confidence scores

### 3. Profile Adaptation Logic
- 6-dimensional user profile (Attention, Processing, Communication, Executive, Sensory, Working Memory)
- Profile dimensions influence approach selection and question adaptation
- Tests prove adaptation works (directness/pacing/abstraction adapt correctly)

### 4. Well-Structured Schemas
- 9 question classes with clear cognitive functions
- Comprehensive enums prevent magic strings
- Rich metadata constants with mappings

---

## Critical Findings

### Finding 1: Questions Generated But Not Used for Dialogue (CRITICAL)

**The Problem:** Backend generates sophisticated questions, but there's no feedback loop.

**Evidence:**
- ForgeMode calls `/generate-questions`, gets question back
- No endpoint analyzes user's RESPONSE to that question
- System can't learn which questions worked or confused users
- Question classes are assigned post-hoc via round-robin, not used for selection

**Impact:**
- Questions feel generic, not personally attuned
- No learning loop to improve over time
- Principle 1 (Thinking Partnership) partially undelivered

**Root Cause:** Backend is stateless; questions are ephemeral transactions, not part of conversation.

### Finding 2: Nine Question Classes Are Decorative (HIGH)

**The Problem:** Question classes exist but aren't used for selection.

**Current Flow:**
1. Detect state → Select approach (Socratic, etc.)
2. Get templates by approach
3. **AFTER selection**, assign class via `i % len(approach_classes)`

**What Should Happen:**
1. Detect state → Determine NEEDED question classes
2. Filter questions BY class based on cognitive need
3. Select from filtered set

**Example Gap:**
- User state: STUCK (needs ANCHOR or META_COGNITIVE to ground/reflect)
- Approach: SOCRATIC (classes: SCHEMA_PROBE, BOUNDARY, CAUSAL)
- User gets abstract Schema-Probe when they need concrete Anchor

### Finding 3: Service Instantiation Anti-Pattern (HIGH)

**Location:** `api/question_engine.py` lines 24-28

```python
# Creates NEW instances (WRONG)
state_detection_service = StateDetectionService()
```

But services define singletons at bottom of their modules. API layer ignores singletons.

**Impact:**
- Duplicate service instances
- State not shared between API and direct service usage
- Inconsistent with other backend APIs

### Finding 4: Profile System Exists But Isn't Used (MEDIUM)

**Evidence:**
- Sophisticated 6-dimensional profile schema exists
- Profile adaptation logic works (tests prove it)
- BUT: No profile creation flow in frontend
- ForgeMode doesn't pass `user_id` to Question Engine
- Profile adaptation is theoretical, not realized

### Finding 5: Missing UX Convenience (MEDIUM)

**Problem:** API optimized for flexibility, not usability.

**Current:**
```
Frontend must: POST /detect-state → POST /select-approach → POST /generate-questions
```

**Needed:**
```
Single call: POST /question/next → Returns ONE question with explanation
```

---

## Bug Summary (19 Total)

### Critical (5)
| ID | Description | File |
|----|-------------|------|
| BUG-QE-01 | Race condition in module-level service initialization | api/question_engine.py:24-28 |
| BUG-QE-02 | Null pointer exception in template selection (empty categories) | api/question_engine.py:245-256 |
| BUG-QE-03 | Silent JSON parsing failures in ProfileService | services/profile_service.py:243-264 |
| BUG-QE-04 | Empty string messages not validated | services/state_detection_service.py:100-117 |
| BUG-QE-05 | Type inconsistency in certainty_language (int | None) | schemas/question_engine.py:135 |

### High (5)
| ID | Description | File |
|----|-------------|------|
| BUG-QE-06 | Template adaptation swallows KeyError silently | services/question_templates_service.py:509-515 |
| BUG-QE-07 | get_categories_for_approach() returns empty for None | services/question_templates_service.py:604-616 |
| BUG-QE-08 | Multi-word marker regex doesn't handle word boundaries | services/state_detection_service.py:71-75 |
| BUG-QE-09 | Exploration markers use substring match, not word boundary | services/state_detection_service.py:96 |
| BUG-QE-10 | Capacity check mutates confidence but doesn't re-classify state | services/state_detection_service.py:218-226 |

### Medium (6)
| ID | Description |
|----|-------------|
| BUG-QE-11 | Profile loading failure silently returns None |
| BUG-QE-12 | Fallback approaches can include selected approach |
| BUG-QE-13 | session_duration_minutes not passed in /generate-questions |
| BUG-QE-14 | Repetition detection has magic number threshold |
| BUG-QE-15 | Empty recent_messages not validated in API layer |
| BUG-QE-16 | Abstraction level classification returns "mixed" for no patterns |

### Low (3)
| ID | Description |
|----|-------------|
| BUG-QE-17 | Template library built on every service instantiation |
| BUG-QE-18 | Uncertainty check uses fragile `or 5` pattern |
| BUG-QE-19 | Marker lists use mixed quote styles |

---

## Principle Alignment Scores

| Principle | Score | Status |
|-----------|-------|--------|
| **Thinking Partnership** | C (2.0/4.0) | Infrastructure exists, dialogue loop missing |
| **ADHD-Friendly Design** | D+ (1.5/4.0) | Research-backed intent, minimal execution |
| **Nine Question Classes** | B- (2.8/4.0) | Schema complete, integration superficial |
| **Profile Adaptation** | C- (1.8/4.0) | Logic works, no learning loop |

---

## Remediation Plan

### Phase 1: Critical Fixes (Immediate)

1. **Fix Service Instantiation Pattern**
   - Import singletons from service modules instead of creating new instances
   - File: `api/question_engine.py` lines 24-28
   - Effort: 30 minutes

2. **Move Request Models to Schemas**
   - Move `DetectStateRequest`, `SelectApproachRequest`, `GenerateQuestionsRequest` to `schemas/question_engine.py`
   - Effort: 30 minutes

3. **Add Input Validation**
   - Add `min_length=1` to `recent_messages` field
   - Add null checks for profile loading
   - Effort: 1 hour

4. **Fix Template Selection Edge Cases**
   - Return 404 when no templates can be selected
   - Log KeyError when placeholders missing
   - Effort: 1 hour

### Phase 2: UX Improvements (High Priority)

5. **Add `/question/next` Convenience Endpoint**
   - Single call returns ONE best question with explanation
   - Combines state detection + approach selection + question generation
   - Include `explain_to_user` field with human-friendly reasoning
   - Effort: 4 hours

6. **Add `session_duration_minutes` to GenerateQuestionsRequest**
   - Enable fatigue detection in all endpoints
   - Effort: 30 minutes

7. **Add Exploration Markers Word Boundary Fix**
   - Use `_match_marker()` instead of substring match
   - Effort: 30 minutes

### Phase 3: Feedback Loop (Important)

8. **Add Response Analysis Endpoint**
   - `POST /question/{question_id}/response`
   - Analyze user's answer to inform next question selection
   - Track which question classes user engages with vs ignores
   - Effort: 8 hours

9. **Make Question Classes Selection Criteria**
   - Add state → needed classes mapping
   - Filter questions BY class before selection
   - Remove round-robin assignment
   - Effort: 6 hours

10. **Add Question Feedback API**
    - `POST /questions/{question_id}/feedback`
    - Track helpful/confusing/too_direct ratings
    - Effort: 4 hours

### Phase 4: Profile Integration (Deferred)

11. **Profile Inference from Conversation**
    - Endpoint: `POST /profile/infer`
    - Detect preferences from natural language patterns
    - Effort: 8 hours

12. **Session Context Preservation**
    - Store detected state, approach, questions in session
    - Avoid re-detecting state every message
    - Effort: 6 hours

---

## Success Criteria After Remediation

- [ ] All critical bugs fixed (BUG-QE-01 through BUG-QE-05)
- [ ] Service instantiation follows singleton pattern
- [ ] `/question/next` endpoint available for simple integration
- [ ] Input validation prevents empty/malformed requests
- [ ] Question classes used for selection, not just tagging
- [ ] User response analyzed to inform next question
- [ ] Frontend can use Question Engine with single API call

---

## Comparison with Other Analyzed Components

| Component | Overall Grade | Principle Delivery | Bug Count |
|-----------|---------------|-------------------|-----------|
| SiYuan Plugin | B+ (fixed) | Good after remediation | 7 fixed |
| Readest Integration | B- (fixed) | Good after remediation | 5 fixed |
| **Question Engine** | C+ | Mediocre | 19 found |

**Observation:** Question Engine has the most bugs and lowest principle delivery of analyzed components. However, its bugs are less user-facing (backend-only) and its architecture is sound.

---

## Conclusion

The Backend Question Engine is **well-architected but incomplete**. It has:
- Excellent domain modeling (states, approaches, classes)
- Research-backed template library
- Comprehensive test coverage for happy paths

But lacks:
- Dialogue loop (questions → responses → learning)
- Functional question class integration
- UX convenience for frontends
- Profile system actually being used

**Path to A-grade:**
1. Fix service patterns and critical bugs (1-2 hours)
2. Add `/question/next` convenience endpoint (4 hours)
3. Make question classes functional selection criteria (6 hours)
4. Add response analysis feedback loop (8 hours)

Total estimated effort: **20 hours** to transform from C+ to B+/A-.

---

## Files Analyzed

```
ies/backend/src/ies_backend/
├── api/question_engine.py (401 lines)
├── services/
│   ├── state_detection_service.py (359 lines)
│   ├── approach_selection_service.py (265 lines)
│   └── question_templates_service.py (634 lines)
├── schemas/question_engine.py (252 lines)
└── tests/test_question_engine.py (705 lines)
```

**Total: 2,616 lines analyzed**

---

*Analysis completed 2025-12-06 using four-agent critical evaluation pattern.*
