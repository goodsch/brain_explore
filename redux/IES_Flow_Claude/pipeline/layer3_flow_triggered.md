# Layer 3 – Flow-Triggered Context-Specific Extraction

Layer 3 activates during Flow Mode interactions.

## Context

- A **focus entity** is active (Question, Concept, Problem, Project).
- Flow Mode knows:
  - The focus entity and its neighbors.
  - Related sources/chunks discovered in Layer 1 and Layer 2.

## Operations

1. **Identify Gaps**
   - Detect questions with little/no evidence.
   - Identify concepts with weak definitions or sparse relations.

2. **Targeted Corpus Search**
   - Use the word/phrase index to fetch candidate chunks relevant to:
     - the focus entity,
     - its immediate sub-entities,
     - its child questions.

3. **Contextual Extraction**
   - Run focused extraction on these candidate chunks to find:
     - definitions,
     - claims,
     - mechanisms,
     - comparisons,
     - directly relevant answers or partial answers.

4. **Graph & Note Updates**
   - Add new relations and claims to the Knowledge Graph.
   - Link them to relevant Questions and Concepts.
   - Offer to:
     - insert structured summaries and snippets into the current note,
     - create new Questions or Concepts where appropriate.

5. **Processing Status Updates**
   - Mark chunks/entities as partially deep-processed for certain contexts.
   - Avoid redundant heavy processing on frequently revisited regions.

## Outputs

- Just-in-time deepening of the graph around the focus entity.
- Notes enriched with contextually relevant structure and evidence.
