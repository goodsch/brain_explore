# Question Graph (Lack-of-Knowledge Graph)

The Question Graph explicitly represents your unknowns and partially knowns.

## Nodes

- `Question` entities (see `entities/03_questions.md`).

## Edges

- `requires`:
  - Q2 must be understood to answer Q1.
  - Direction: `Q1 --requires--> Q2`.
- `helps_answer`:
  - Q2 contributes partial information toward answering Q1.
- `depends_on_concept`:
  - Q uses Concept C.
  - Link: `Question --depends_on_concept--> Concept`.

## Purpose

- Provide a structured view of what you don't yet know.
- Drive learning pathways and Flow Mode navigation.
- Inform pipeline prioritization (deep processing around active questions).

## Dynamics

- As you learn and explain, Question statuses evolve:
  - `unknown` → `partial` → `answered`.
- "To know this, you must know this" relationships are modeled directly via
  `requires` edges.
- New questions are spawned as gaps are revealed during study and Flow
  interaction.
