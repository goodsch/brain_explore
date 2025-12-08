# Layer 2 – Deeper Relational & Semantic Processing

Layer 2 is **selective** and more expensive. It focuses on:

- Extracting structure inside arguments.
- Building relationships between concepts.
- Identifying claims, evidence, mechanisms, and comparisons.

## Prioritization

Sources/chunks are prioritized based on:

- Relevance to active entities:
  - Feynman Problems, Projects, Questions, Concepts currently in focus.
- Frequency/centrality of entities:
  - High-use concepts get deeper processing first.
- Explicit user preferences:
  - e.g., "focus deep processing on ADHD time perception".

## Operations

1. **Relational Extraction per Chunk**
   - Extract:
     - Definitions ("X is...")
     - Claims ("X causes/affects Y")
     - Mechanisms (process descriptions)
     - Comparisons (X vs Y)
     - Examples / case studies
     - Conditions / limitations
   - Turn into structured records, e.g.:
     - `definition(concept, text, source_chunk)`
     - `relation(concept_A, relation_type, concept_B, evidence_chunk)`
     - `claim(subject, predicate, object, strength, sources[])`

2. **Question Alignment**
   - Map chunks/relations to existing Questions.
   - Attach evidence to questions as `answer_evidence`.
   - Update question `status` as evidence accumulates.

3. **Background Scheduling**
   - Maintain a priority queue of chunks/entities.
   - Continuously process items in the background as resources allow.

## Outputs

- A richer Knowledge Graph with relational edges and claims.
- Questions linked to evidence and moving toward "answered".
