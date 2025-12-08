# Entity: Project

A Project is the execution/building side of the system. Where a Feynman Problem
is about deep understanding, a Project is about producing tangible outcomes.

## Purpose

- Represent concrete work streams (apps, presentations, experiments).
- Consume Questions and Concepts as inputs for design and implementation.
- Provide an action-oriented complement to Feynman Problems.

## Examples

- "Build IES Flow Mode v1 for SiYuan."
- "Create a parent workshop on ADHD time perception."

## Recommended Fields

- `id`
- `title`
- `goal`: overall purpose / target outcome
- `description`
- `deliverables`: list of expected outputs
- `linked_feynman_problem_ids`
- `key_question_ids`: subset of Question Graph nodes central to this project
- `timeline`: free-form or structured milestone info
- `status`: e.g., `idea` | `planned` | `in_progress` | `paused` | `done`
- `created_at`, `updated_at`

## Behavior

- Projects pull from the Question Graph:
  - They select specific questions to resolve in service of an outcome.
- Flow Mode can surface project-relevant questions and concepts when a
  Project note is the focus entity.
