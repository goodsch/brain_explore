# Wave 4: Learning - Specification

**Date:** December 6, 2025
**Depends On:** Wave 3 (Visibility) - Complete
**Goal:** Make the system learn from user interactions

---

## Prerequisites (from Wave 3)

- FeedbackService with Neo4j persistence (complete)
- `get_effective_question_classes()` returns insight-generating question classes
- Profile system with `apply_observation()` method (stub with TODOs)
- ReframeService with `record_feedback()` method (stores but doesn't learn)
- Backend tests: 113/113 passing

---

## Task 4.1: Profile Updates from Session Patterns

**Current State:**
- `ProfileService.apply_observation()` exists but has TODOs:
  - "Only add if session showed deep engagement" - not implemented
  - "Track approach effectiveness for future question selection" - not implemented

**Requirements:**

1. **Session Engagement Metrics**
   - Calculate engagement score from session data:
     - Time spent per entity
     - Number of thinking partner exchanges
     - Questions that led to insight (feedback data)
     - Marks/saves during session
   - Threshold for "deep engagement" (e.g., >5min on entity, >3 exchanges)

2. **Hyperfocus Trigger Updates**
   - Add topics to `attention.hyperfocus_triggers` only when engagement score exceeds threshold
   - Weight by recency (recent sessions count more)
   - Cap triggers list (max 20, prune oldest/lowest-engagement)

3. **Approach Effectiveness Tracking**
   - Create new schema: `ApproachEffectiveness`
   - Track which question approaches led to insights for this user
   - Store per-user statistics: `{approach: "socratic", insight_rate: 0.45, sample_size: 20}`

**Files to Modify:**
- `ies/backend/src/ies_backend/services/profile_service.py` - Complete apply_observation
- `ies/backend/src/ies_backend/schemas/profile.py` - Add ApproachEffectiveness
- `ies/backend/tests/test_profile.py` - Add tests for learning behavior

**Acceptance Criteria:**
- [ ] apply_observation calculates engagement metrics
- [ ] High-engagement topics added to hyperfocus_triggers
- [ ] Approach effectiveness stored per user
- [ ] Tests verify learning behavior

---

## Task 4.2: Question Selection Optimization

**Current State:**
- `FeedbackService.get_effective_question_classes()` returns insight-generating classes
- `QuestionTemplatesService.generate_question_batch()` randomly selects from templates
- No integration between feedback data and question generation

**Requirements:**

1. **Weighted Question Selection**
   - Modify `generate_question_batch()` to accept optional user_id
   - Query effective question classes for this user
   - Weight template selection: higher probability for effective classes
   - Fallback to global effectiveness data if user has insufficient history

2. **User-Specific Effectiveness**
   - Add `get_user_effective_classes(user_id, min_sample=5)` to FeedbackService
   - Merge with global data when sample size insufficient
   - Return weighted probabilities, not just binary inclusion

3. **A/B Exploration**
   - Reserve 20% of questions for exploration (try less-used classes)
   - Track which classes need more samples for reliable statistics

**Files to Modify:**
- `ies/backend/src/ies_backend/services/feedback_service.py` - Add user-specific method
- `ies/backend/src/ies_backend/services/question_templates_service.py` - Weighted selection
- `ies/backend/src/ies_backend/api/question_engine.py` - Pass user_id to service
- `ies/backend/tests/test_feedback_service.py` - Add selection tests

**Acceptance Criteria:**
- [ ] Question selection weighted by effectiveness data
- [ ] User-specific preferences honored when data sufficient
- [ ] 20% exploration rate maintained
- [ ] Tests verify weighted selection behavior

---

## Task 4.3: Reframe Prompt Adaptation

**Current State:**
- `ReframeService.record_feedback()` stores thumbs up/down
- REFRAME_PROMPT is static string
- No learning from feedback

**Requirements:**

1. **Feedback Analysis**
   - Add `get_user_reframe_preferences(user_id)` method
   - Return: preferred types (metaphor > analogy), preferred domains (personal > meta)
   - Calculate from positive feedback distribution

2. **Prompt Customization**
   - Add user preferences to prompt context
   - Modify REFRAME_PROMPT to optionally emphasize preferred strategies
   - Example: "The user responds well to metaphors and personal-life examples"

3. **Avoid Negative Patterns**
   - Track which type/domain combinations received negative feedback
   - Reduce probability of those patterns for this user
   - Never completely exclude (preserve diversity)

**Files to Modify:**
- `ies/backend/src/ies_backend/services/reframe_service.py` - Add preference methods
- `ies/backend/tests/test_reframe_service.py` - Add preference tests

**Acceptance Criteria:**
- [ ] User reframe preferences extracted from feedback
- [ ] Prompt adapted to emphasize preferred strategies
- [ ] Negative patterns de-emphasized but not excluded
- [ ] Tests verify preference calculation

---

## Integration Points

### Session Flow (Profile Learning)
```
Session End → collect_engagement_metrics() → apply_observation()
                    ↓
             Calculate dwell time, exchanges, insights
                    ↓
             Update hyperfocus_triggers if threshold met
                    ↓
             Record approach effectiveness
```

### Question Flow (Selection Optimization)
```
generate_question_batch(user_id)
       ↓
   get_user_effective_classes(user_id)
       ↓
   Merge with global effectiveness
       ↓
   Apply weights to template selection
       ↓
   Reserve 20% for exploration
```

### Reframe Flow (Prompt Adaptation)
```
generate_reframes(user_id, concept)
       ↓
   get_user_reframe_preferences(user_id)
       ↓
   Build adapted prompt with preferences
       ↓
   Call LLM with customized prompt
```

---

## Agent Strategy

| Task | Agent Type | Approach |
|------|------------|----------|
| 4.1 Profile Learning | backend-developer | TDD with profile tests |
| 4.2 Question Selection | backend-developer | TDD with feedback/template tests |
| 4.3 Reframe Adaptation | backend-developer | TDD with reframe tests |
| Verification | critical-evaluator | Review all changes + run tests |

---

## Verification Commands

```bash
# Run all backend tests
cd ies/backend && uv run pytest

# Run specific test files
cd ies/backend && uv run pytest tests/test_profile.py -v
cd ies/backend && uv run pytest tests/test_feedback_service.py -v
cd ies/backend && uv run pytest tests/test_question_templates.py -v

# Check test count increased (baseline: 113)
cd ies/backend && uv run pytest --collect-only | grep "test session"
```

---

## Success Criteria

Wave 4 is complete when:
- [ ] Profile updates from session engagement patterns
- [ ] Question selection weighted by user effectiveness data
- [ ] Reframe prompts adapt to user preferences
- [ ] All tests pass (target: 120+ tests)
- [ ] Code reviewed by critical-evaluator agent
