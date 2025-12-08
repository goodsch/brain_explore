# Entity: FeynmanProblem

A Feynman Problem is a personally meaningful, deep “I want to really understand this” item.

## Purpose

- Anchor long-term, high-value understanding goals.
- Tie together Questions, Concepts, Projects, and Sources.
- Drive prioritization of deeper processing in the pipeline.

## Examples

- "Why does ADHD distort the perception of time?"
- "How should a Flow Mode UI really work for my brain?"

## Recommended Fields

- `id`: unique identifier
- `title`: short human-readable label
- `description`: free-form explanation of what this problem means to you
- `importance`: priority or weight (e.g., 1–5)
- `status`: e.g., `exploring` | `learning` | `explaining` | `mastered`
- `linked_project_ids`: projects that implement work related to this problem
- `root_question_ids`: key starting questions in the Question Graph
- `seed_concept_ids`: initial concepts that appear central
- `contexts`: domains / lenses (e.g., clinical, UX, self-management)
- `created_at`, `updated_at`: timestamps

## Behavior

- On creation, AI should:
  - Generate candidate root questions.
  - Suggest key concepts/entities.
  - Seed the Question Graph around this problem.
- Over time, the status moves from "exploring" toward "mastered" as the
  linked Questions become answered with high confidence.
