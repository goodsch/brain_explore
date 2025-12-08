# Flow Mode Graph Interaction – Full UX & Behavior Spec

This file contains the complete storyboarded UX specification for the adaptive Flow Mode UI with contextual graph traversal, entity/facet expansion, and journey mapping.

---

## 1. Flow Mode Layout (High-Level)

Flow Mode consists of three vertical UI zones:

### Left Panel – Context & Trail
- Context title, type, status
- Key Questions (buttons)
- Areas of Exploration (buttons)
- Trail (breadcrumbs showing graph navigation path)

### Center Panel – Focus View
Changes dynamically based on what the user is exploring:
- Question Focus
- Entity Focus
- Facet Focus
- Graph Slice View

### Right Panel – Journey & Notes
- Chronological trace of every interaction
- Notes, pinned items, structural updates

---

## 2. State 1 – Entering Flow from a Context Note

Triggered when user opens a Context Note and activates Flow Mode.

Left:
- Show Context, Key Questions, Areas

Center:
- “Pick a Question” prompt

Right:
- Journey shows: “Flow started in Context”

---

## 3. State 2 – Question Focus

When user clicks a Question (e.g., Q1).

Left:
- Highlight selected Question
- Trail: Context → Question

Center:
- Question text
- Search results (keyword-based MVP)
- Entities in Focus: basic extraction from snippets

Right:
- Journey entry: “Selected Question Q1”

---

## 4. State 3 – Entity Focus

When user clicks an entity (e.g., ADHD).

Left:
- Trail: Context → Question → Entity

Center:
- Entity summary (from KG or LLM)
- Facets for Entity:
  - Diagnosis
  - Symptoms
  - Physiology
  - Time-related phenomena
  - Executive Function profile
  - Treatment

Right:
- Journey entry: “Focused Entity: ADHD”

---

## 5. State 4 – Facet Focus

When user clicks a facet (e.g., “Physiology / Neurobiology”).

Left:
- Trail: Context → Question → Entity → Facet

Center:
- Facet summary
- Graph Slice View:
  - Core node (e.g., ADHD)
  - First-level related physiology concepts:
    - dopamine
    - prefrontal cortex
    - striatum
    - neural circuitry
  - Indicate new vs existing KG nodes
- Evidence snippets

Right:
- Journey entry:
  - type: facet_expansion
  - data: extracted nodes/relations

---

## 6. State 5 – Traversing the Graph

Clicking a sub-entity (e.g., “Temporal discounting”) moves into:

Left Trail:
- Context → Question → Entity → Facet → Entity

Center:
- Entity Focus for new node
- Facets for new entity

Right:
- Journey entry: entity_focus

This enables **incremental KG growth**:
- Minimal extraction
- Local-only expansion
- No overwhelming global graph

---

## 7. Trail vs Journey

### Trail = local navigation
- Represents the path through concepts/facets in the current exploration
- Clickable breadcrumbs

### Journey = chronological history
- Every interaction logged
- Can replay or filter by context/question

---

## 8. ADHD-Friendly Constraints
- Only show small graph slices (1-hop neighbors)
- Highlight new nodes/edges
- Always show “Back to Question”
- Provide quick actions:
  - “Pin as Key Concept”
  - “Promote to Key Question”

---

## 9. Implementation Checklist

- Parse Context Note → Questions, Areas, Concepts
- Build UI containers for:
  - Question Focus
  - Entity Focus
  - Facet Focus
  - Graph Slice View
- Create facet templates for common entities (ADHD, EF, Time Perception)
- Implement expandFacet(context, entity, facet)
- Maintain Trail stack
- Log Journey entries for:
  - question_select
  - entity_focus
  - facet_expansion
  - graph_traverse
- Keep KG updates incremental and local

---

This document captures the complete envisioned UX for contextual graph exploration in Flow Mode.
