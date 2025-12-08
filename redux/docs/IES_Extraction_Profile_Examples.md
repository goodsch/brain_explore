# IES Extraction Profiles – Examples

This document provides example Extraction Profiles for common Context types.

The profiles are used by the **Extraction Engine** to decide:
- which concepts to focus on
- which relations to extract
- which sources/domains to prioritize

Profiles can be stored as JSON, YAML, or embedded blocks in Context Notes.

---

## Example 1: Feynman Problem – ADHD Time Perception

Context:
- id: `ctx_feynman_adhd_time`
- type: `feynman_problem`
- title: "What is ADHD time perception?"

```jsonc
{
  "context_id": "ctx_feynman_adhd_time",
  "core_concepts": [
    "ADHD time perception",
    "time blindness",
    "temporal discounting",
    "time estimation",
    "time reproduction",
    "prospective memory"
  ],
  "synonyms": {
    "time blindness": ["time-blindness", "time blind", "time-blind"],
    "temporal discounting": ["delay discounting", "delay aversion"],
    "time estimation": ["time estimation tasks", "subjective time estimation"]
  },
  "relation_types": [
    "component_of",
    "impacts",
    "associated_with",
    "explains",
    "contradicted_by"
  ],
  "domain_filters": [
    "ADHD",
    "executive_function",
    "time_perception"
  ],
  "question_overrides": {
    "q_adhd_time_relationship_wm": {
      "core_concepts": [
        "time blindness",
        "working memory",
        "time estimation"
      ],
      "relation_types": [
        "impacts",
        "associated_with",
        "mediates"
      ]
    }
  }
}
```

---

## Example 2: Concept Cluster – Executive Function Components

Context:
- id: `ctx_concept_ef_components`
- type: `concept_cluster`
- title: "Executive Function components"

```jsonc
{
  "context_id": "ctx_concept_ef_components",
  "core_concepts": [
    "executive function",
    "working memory",
    "inhibition",
    "cognitive flexibility",
    "planning",
    "self-monitoring"
  ],
  "relation_types": [
    "component_of",
    "is_a",
    "required_for",
    "impacts"
  ],
  "domain_filters": [
    "ADHD",
    "executive_function"
  ]
}
```

---

## Example 3: Theory – Motivation & Task Initiation in ADHD

Context:
- id: `ctx_theory_motivation_task_init`
- type: `theory`
- title: "Motivation & task initiation in ADHD"

```jsonc
{
  "context_id": "ctx_theory_motivation_task_init",
  "core_concepts": [
    "task initiation",
    "activation energy",
    "reward sensitivity",
    "dopamine",
    "interest-based nervous system",
    "threat-based motivation",
    "reward prediction error"
  ],
  "relation_types": [
    "explains",
    "relies_on",
    "contradicted_by",
    "supported_by"
  ],
  "domain_filters": [
    "ADHD",
    "motivation",
    "neurobiology"
  ]
}
```

---

## Example 4: Project – IES Flow Mode v2

Context:
- id: `ctx_project_flow_mode_v2`
- type: `project`
- title: "IES Flow Mode v2"

Here the Extraction Profile is less about scientific constructs and more about
design/implementation concepts. It can still be useful to anchor source analysis
(e.g., docs, blog posts, research on PKM / knowledge graphs) to this project.

```jsonc
{
  "context_id": "ctx_project_flow_mode_v2",
  "core_concepts": [
    "Flow Mode",
    "context graph",
    "question graph",
    "knowledge graph",
    "context-aware extraction",
    "ADHD-friendly exploration"
  ],
  "relation_types": [
    "inspired_by",
    "implements",
    "extends",
    "similar_to"
  ],
  "domain_filters": [
    "knowledge_management",
    "pkm",
    "knowledge_graphs",
    "ai_assistants"
  ]
}
```

---

## How Dev/AI Tools Can Use These

- Given a Context Note being edited:
  - generate an initial Extraction Profile based on headings and content
- Given a stored profile:
  - refine it as you work (e.g., add new concepts, synonyms, relations)
- When Flow Mode or Reader calls the Extraction Engine:
  - pass `context_id`, optional `question_id`, and profile
  - let the engine:
    - build candidate segment sets from Library + Indexes
    - send batched segments to LLM with a prompt that references the profile
