# Entity: Question

Questions are the atomic units of the Question Graph / Lack-of-Knowledge Graph.

## Purpose

- Explicitly represent what is not yet known (or only partially known).
- Anchor reading, thinking, and extraction efforts.
- Act as stepping stones in learning pathways.

## Examples

- "What is 'time blindness' in ADHD?"
- "Which brain systems are involved in time estimation?"
- "What are the core UI elements needed in Flow Mode?"

## Recommended Fields

- `id`
- `text`: full question text
- `type`: e.g., `why` | `how` | `what` | `compare` | `strategy` | `definition`
- `parent_question_ids`: questions that this question helps to answer
- `child_question_ids`: prerequisite questions ("to know this, you must know…")
- `related_concept_ids`: concepts/terms involved
- `linked_source_fragments`: references to chunks that help answer this question
- `status`: e.g., `unknown` | `partial` | `answered` | `obsolete`
- `confidence`: numeric score reflecting confidence in the current answer
- `explanation_block_id`: optional link to a block/note with your own Feynman-style explanation
- `created_at`, `updated_at`

## Behavior

- New Questions are generated from:
  - Feynman Problems
  - Projects
  - Flow interaction ("What else do I need to know?")
- Questions may be:
  - Filled with evidence and explanations over time.
  - Marked answered when the explanation is clear, simple, and robust.
