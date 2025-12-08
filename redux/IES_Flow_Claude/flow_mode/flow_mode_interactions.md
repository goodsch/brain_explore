# Flow Mode: User Interaction & Auto-Processing

## 1. Focus Entity Determination

- The plugin inspects the open note's metadata/frontmatter to determine:
  - Is this a FeynmanProblem / Project / Question / Concept / other?
  - What is its `entity_id`?
- That entity becomes the **focus entity** for Flow Mode.

## 2. Auto-Processing When a Focus Entity Is Opened

### First-Time Focus

On first open:

1. Resolve or create the entity record from the note.
2. AI generates **first-level relationships**:
   - Components / facets (e.g., for ADHD: Diagnosis, Symptoms, Time Perception, Executive Function, etc.).
3. For each facet:
   - If noun-like → create/attach a Concept.
   - If a question → create a Question node.
4. Link them as neighbors and **kick off entity extraction** from the corpus
   for these sub-entities.

### Subsequent Focus

On subsequent opens:

- Flow Mode reuses the existing graph structure.
- Provides a "Refresh / Expand" action to:
  - Re-run extraction with new sources.
  - Ask AI to propose additional sub-entities given updated knowledge.

## 3. Visual Micro Knowledge Graph

In the Flow sidebar:

- Center node: the focus entity.
- Surrounding nodes: first-level neighbors (questions, concepts, problems, projects).
- Each node is a clickable chip with type and status badges.

Interactions:

- Clicking a chip changes the focus entity in the Flow panel.
- Optionally, user can also "Open note" for that entity to switch the main editor.
- This creates a **visual thinking space** for navigating ideas.

## 4. Special Blocks in the Main Note

Flow Mode can manage structured blocks in the note:

- **Components / Facets**
- **Open Questions**
- **Key Sources & Snippets**
- **Current Understanding** (Feynman-style explanation)

These blocks:

- Stay linked to graph entities.
- Are updated by AI when structure or understanding changes.

## 5. Contextual AI Chat

The Flow chat is always bound to the current focus entity and includes:

- The entity's metadata and neighbors.
- Representative snippets from relevant sources.
- The current note content or selection.

The AI can, conversationally:

- Create new Questions or Concepts.
- Add edges between entities.
- Refine definitions and explanations.
- Restructure the note into a more coherent format.
- Propose learning pathways and reading queues.

All creations/edits from chat are persisted into the graph and notes, not kept
only in the chat transcript.
