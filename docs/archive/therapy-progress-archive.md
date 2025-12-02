# Therapy Framework Progress

*Exploring and articulating therapeutic worldview*

**Current Status:** Concept development in progress

| Track | Status | Progress |
|-------|--------|----------|
| 1-Human Mind | 🟡 Developing | 1 concept developed, 2 seeds |
| 2-Change Process | 🟡 Starting | 1 concept seed identified |
| 3-Method | 🔲 Not Started | — |

---

## Overview

Three tracks articulating therapeutic worldview:

**Track 1: Human Mind**
- Why humans are the way they are
- Why they struggle
- What they're doing about it

**Track 2: Change Process**
- How therapy creates change
- What conditions enable transformation
- Hidden functions of symptoms

**Track 3: Method**
- Operational approach (to be defined)
- What we actually do in sessions
- How we maintain this worldview

---

## Concept Status

### Track 1: Human Mind

#### ✅ Developing: Narrow Window of Awareness
- **Status:** Actively developing (furthest along)
- **Description:** Humans aware enough to create meaning, not enough to see blind spots
- **Key Insight:** Limitation is both suffering source AND capacity for meaning
- **Grounding:** Needs literature linkage to predictive processing, consciousness research
- **SiYuan:** `/1-Human Mind/Narrow Window of Awareness`

#### 🌱 Seed: Meaning-Making as Solution
- **Status:** Identified, not captured
- **Description:** The fact that we make meaning isn't the problem; unnecessary suffering is
- **Key Insight:** We need to reduce unnecessary pain, not change people
- **Next:** Develop through exploration sessions

#### 🌱 Seed: Unique Personhood
- **Status:** Identified, not captured
- **Description:** Each person's experience is singular; universal techniques miss the person
- **Next:** Ground in existential psychology

#### 🌱 Seed: Foundational Understanding
- **Status:** Identified, emerging as Track 1→2 bridge
- **Description:** Baseline beliefs a person needs before techniques can work
- **Key Insight:** Not a fixed list, varies per person
- **Next:** Develop with "Hanging Question"

### Track 2: Change Process

#### 🌱 Seed: Hidden Function of Symptoms
- **Status:** Identified, not captured
- **Description:** Anxiety as protection, drinking as survival, avoidance as coping
- **Key Insight:** Symptoms aren't problems to eliminate; they're solutions people are using
- **Next:** Ground in trauma-informed & solution-focused therapy

#### 🌱 Seed: Conditions for Change
- **Status:** Identified, not captured
- **Description:** Not "addressable vs unavoidable" but "conditions present vs not yet present"
- **Key Insight:** No pain is inherently unchangeable; change is blocked by missing conditions
- **Next:** Develop through exploration of what "conditions" actually are

### Track 3: Method

#### 🔲 Not Started
- **Status:** Empty (to be developed)
- **What It Needs:** Operational approach, session structure, therapeutic presence
- **When:** After Tracks 1-2 solidified

---

## Hanging Questions

### Primary Question
> "How do you identify what foundations are missing for a particular person? Is it intuitive, or is there a process?"

**Context:** Shared foundation must exist before techniques work, but missing pieces vary per person

**Follow-up Questions:**
- What are the invisible basics people lack? (What emotions are, uniqueness, etc.)
- How do you assess what's missing?
- Is it observable patterns or embodied intuition?

---

## Development Process

### How to Develop Concepts

Use `/explore-session` to explore ideas. System handles:
1. Session chat with Claude (Socratic dialogue)
2. Entity extraction (Claude API)
3. Auto-storage in Neo4j
4. Literature linking (Qdrant search)
5. SiYuan document creation

### Key Tools

- **Exploration Session:** `/explore-session` — Main development tool
- **Literature Grounding:** Entities auto-linked to 63 therapy books
- **SiYuan Storage:** Concepts automatically saved to `/Therapy Framework` notebook
- **Neo4j Graph:** Relationships tracked for concept connections

---

## Research Queue

Topics to ground concepts (ordered by relevance):

1. **Predictive Processing** (Friston, Clark, Seth)
   - Link: Narrow Window → Predictive processing model

2. **Existential Psychology** (Yalom, Frankl)
   - Link: Unique Personhood → Existential freedom & meaning

3. **Solution-Focused Therapy** (Berg, de Shazer)
   - Link: Hidden Function → Solutions people are using

4. **Trauma-Informed Approach** (van der Kolk, Bessel)
   - Link: Hidden Function → Survival strategies

5. **Terror Management Theory** (Greenberg, Pyszczynski)
   - Link: Narrow Window → Meaning-making & existential fear

6. **Buddhist Psychology** (First arrow vs second arrow)
   - Link: Foundations → Acceptance of unavoidable suffering

---

## Session Log

### 2025-12-01: Foundations Before Techniques

**Focus:** Hanging question — addressable vs unavoidable pain

**What Shifted:**
- Question transformed: Not "addressable vs unavoidable" but "conditions for change present vs not yet present"
- No pain is inherently unchangeable
- "Unwillingness" is rational calculation (cost/benefit)
- Symptoms serve hidden functions (protection, survival)

**Key Insight:**
> "Therapy's job: shift conditions so change becomes the better option"

**Emerging Concept:** "Foundational Understanding"
- The baseline beliefs a person needs before techniques work
- Not fixed list, varies per person
- Example: Some people don't know emotions are normal, others don't know they're unique

**Entities Identified:**
- Foundational Understanding (new concept, Track 1→2 bridge)
- Hidden Function of Symptoms (seed for Track 2)
- Conditions for Change (reframe of original question)

---

### 2025-12-01: Project Restructure

**Accomplished:**
- Therapy Framework isolated as content layer
- Clear separation from IES (tool) and Framework Project (config)
- Progress file focused on content development

---

### 2025-11-29: First Exploration

**Focus:** "What is the single most important thing you believe about why humans struggle?"

**Key Insights:**
1. **Narrow Window of Awareness** — Aware enough to create meaning, not enough to see blind spots
2. **Meaning-Making is a Solution** — Not the problem itself
3. **The Paradox** — Our limitation is both suffering source AND capacity for meaning
4. **Therapy's Goal** — Reduce unnecessary pain, not make people "correct"

**Entities Created:**
- Narrow Window of Awareness (fully developed)
- Meaning-Making as Solution (identified)
- Unique Personhood (identified)

---

## Next Session Priorities

### High Priority

1. **Develop Hanging Question**
   - [ ] Run `/explore-session` focused on "How do you identify missing foundations?"
   - [ ] Document process (intuitive, patterns, structured?)
   - [ ] Identify sub-skills therapists use

2. **Ground Narrow Window**
   - [ ] Research predictive processing literature
   - [ ] Link to consciousness studies
   - [ ] Identify specific sources in therapy books

3. **Develop Hidden Function**
   - [ ] Explore symptom as protection/survival
   - [ ] Document examples (anxiety, avoidance, etc.)
   - [ ] Link to trauma-informed therapy literature

### Medium Priority

1. **Capture Seeds**
   - [ ] Meaning-Making: Develop through exploration
   - [ ] Unique Personhood: Ground in existential psychology
   - [ ] Foundational Understanding: Define what "foundations" means

2. **Track 2 Development**
   - [ ] Start with Hidden Function
   - [ ] Then Conditions for Change
   - [ ] Then integration with Track 1

3. **Build Connections**
   - [ ] Map how concepts relate to each other
   - [ ] Identify tensions and paradoxes
   - [ ] Create concept web in SiYuan

---

## Resources

- **Notebook:** `/Therapy Framework` in SiYuan
- **Exploration Tool:** `/explore-session` command
- **Literature Base:** 63 therapy/psychology books (Neo4j + Qdrant)
- **Storage:** Neo4j for concepts, SiYuan for development, Qdrant for grounding

---

## Key Metrics

- **Concepts Developed:** 1 (Narrow Window of Awareness)
- **Concept Seeds:** 5 identified
- **Hanging Questions:** 1 primary + 3 follow-ups
- **Track 3 Status:** 0% (not started)
- **Literature Linked:** Each concept auto-linked to source books
- **Session Time:** ~4 hours exploration (2025-11-29, 2025-12-01)

---

## Development Guidelines

### Concept Development Stages

```
Seed (identified, not captured)
  ↓
Developing (in active exploration)
  ↓
Grounded (linked to literature)
  ↓
Complete (with examples, relationships, implications)
```

### What Makes a Concept "Complete"
- ✅ Clear description (1 paragraph max)
- ✅ Key insight (1-2 sentences)
- ✅ Literature grounding (2-3 specific sources)
- ✅ Examples (2-3 concrete cases)
- ✅ Relationships (how it connects to other concepts)

### Using Exploration Sessions

1. **Choose topic:** Which hanging question or seed to develop
2. **Set intention:** What you want to understand about it
3. **Explore:** Socratic dialogue with Claude
4. **Extract:** System auto-extracts entities
5. **Ground:** Auto-linked to literature
6. **Integrate:** Add relationships to SiYuan

---

## Notes

**Why Three Tracks?**
- Track 1 (Human Mind) is foundation
- Track 2 (Change Process) is how we work with that understanding
- Track 3 (Method) is operational/technical
- Together they articulate complete therapeutic worldview

**Why Build It Incrementally?**
- One concept fully developed > multiple shallow seeds
- Literature grounding prevents hallucination
- Exploration process refines thinking
- SiYuan storage creates searchable knowledge base

**Timeline Expectations:**
- Current pace: ~1 concept per 1-2 hours exploration
- Target: Complete Track 1 (1 developed + 2 more) by end of Phase 5
- Tracks 2-3: Ongoing development alongside IES plugin work
