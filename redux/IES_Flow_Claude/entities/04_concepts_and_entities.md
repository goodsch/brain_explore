# Entities: Concepts, Terms, Theories, People

These are semantic anchors in the Knowledge Graph.

## Purpose

- Represent stable ideas and entities that occur across sources.
- Tie Questions and Sources together via shared meaning.
- Provide handles for Flow Mode to pivot on.

## Types

- Concept (e.g., "time perception", "executive function")
- Term (e.g., "temporal discounting")
- Theory/Model (e.g., "Multiple time scales model of ADHD")
- Person (e.g., "Russell Barkley")
- Method/Technique (e.g., "Feynman technique")

## Recommended Fields

- `id`
- `name`
- `type`: `concept` | `term` | `theory` | `person` | `method` | …
- `definition`: your current best explanation in your own words
- `aliases`: list of synonyms / alternate spellings
- `related_entity_ids`: edges in the Knowledge Graph
- `related_question_ids`: questions that depend on or involve this entity
- `source_mentions`: references to source chunks where this entity appears
- `importance`: heuristic centrality / priority
- `created_at`, `updated_at`

## Behavior

- Created from:
  - Entity extraction from sources.
  - AI decomposition of Problems/Questions/Projects.
  - Manual creation via Flow Mode chat.
- As your understanding improves, `definition` is updated and new relations
  between concepts are added.
