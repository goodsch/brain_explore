# Flow Mode Overview

Flow Mode is an alternative way to traverse the knowledge graph that is:
- **Question-first** and **concept-first** rather than note-first.
- **Visual and conversational**, showing relationships and prompting exploration.
- **Tightly integrated** with the entity & source processing pipeline.

## Core Ideas

1. The **currently open note** in SiYuan defines the **focus entity**:
   - FeynmanProblem, Project, Question, Concept, etc.
2. Flow Mode centers the UI around this focus entity and:
   - Displays first-level relationships (sub-concepts, sub-questions, etc.).
   - Presents a mini knowledge graph in the sidebar.
   - Offers contextual chat with an AI that can create/update entities & notes.
3. Flow Mode triggers **context-specific extraction** from sources to deepen
   the area around the current focus.

See `flow_mode_interactions.md` for detailed interaction patterns.
