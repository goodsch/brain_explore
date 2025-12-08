# Knowledge Graph

The Knowledge Graph is the network of Concepts, Theories, People, etc.
and their semantic relationships.

## Nodes

- Concept / Term / Theory / Person / Method (see `entities/04_concepts_and_entities.md`).

## Edges (examples)

- `related_to` (symmetric, high-level semantic relation)
- `part_of` / `has_part`
- `example_of` / `has_example`
- `supports` / `contradicts`
- `influences` / `is_influenced_by`
- `authored_by` (for works)
- `proposed_by` (for theories)

## Purpose

- Provide a semantic map of your knowledge domain(s).
- Support Flow Mode pivots: selecting a Concept and exploring related entities,
  questions, and sources.
- Enable cross-domain connections and analogies.

## Interaction with Question Graph

- Questions link to Concepts via `depends_on_concept`.
- Concept nodes list which Questions still depend on them.
- As Concepts become more richly defined, they can help answer multiple Questions.
