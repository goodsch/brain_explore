# Reframe Layer Ingestion Methodology

**Created:** 2025-12-07
**Status:** IN PROGRESS
**Scope:** Multi-pass enrichment pipeline for ADHD-friendly knowledge graph

---

## Implementation Status

| Step | Description | Status |
|------|-------------|--------|
| Step 1 | Structural & Thematic Extraction | ✅ Complete (`library/graph/entities.py`) |
| Step 2 | Cross-Domain Mapping ("ADHD Leap") | ❌ Not started |
| Step 3 | Generative Reframe Creation | ❌ Not started |
| Step 4 | Classification by Pattern Type | ❌ Not started |

**Pass 1 complete:** 9 entity types + 11 relationship types in extraction prompt.
**Passes 2-3 pending:** Resonance check and generative reframe creation.

---

## Overview

Based on the system design discussions provided, here is the methodology for the "Reframe Layer" ingestion pipeline. This methodology is designed to move beyond dry semantic extraction and instead capture the "cross-domain conceptual reframing" characteristic of creative or ADHD cognition.
1. The Core Objective: "Human-Flavored" Nodes
Standard knowledge graphs extract explicit relationships (A is a type of B). To mimic an intelligent human with ADHD, this methodology extracts implicit structural similarities (A feels like B because they share the same dynamic tension).
This requires a new fundamental unit in your graph: the Reframe Node.
The Data Model
Instead of just linking a concept to a definition, every major concept acts as a hub for multiple Reframe nodes:
 * Type: Metaphor, Analogy, Story, Pattern, Contrast.
 * Domain: The source domain (e.g., "Physics," "Jazz," "Gardening").
 * Text: The narrative explanation (e.g., "This concept acts like a thermostat for emotional regulation").
 * Source: Where this reframe came from (Book, Podcast, Generated).
2. Ingestion Methodology: The 4-Step Pipeline
This process applies to books, documents, and even narrative media (podcasts/video).
Step 1: Structural & Thematic Extraction
Do not just summarize the content. The ingestion agent must parse the text to identify "Conceptual Shapes".
 * For Non-Fiction (Pattern Libraries):
   * Extract Pattern nodes: Reusable schemas (e.g., "Feedback Loops," "Tragedy of the Commons").
   * Extract DynamicPattern nodes: Temporal structures like "Oscillation" or "Emergence".
 * For Fiction/Narrative (Concept Engines):
   * Segment the text into FictionUnit or StoryInsight nodes (e.g., a specific vignette from Invisible Cities or a segment from Radiolab).
   * Extract Core Metaphors and Schema Breaks (moments where an intuitive model fails).
Step 2: Cross-Domain Mapping (The "ADHD Leap")
Once a unit is extracted, the system must perform a "resonance check" against existing nodes in the graph to find non-obvious connections.
 * The Prompt: "Which existing concepts in the graph does this story/pattern resonate with?".
 * The Output: A relationship edge labeled [:METAPHOR_FOR] or [:ANALOGOUS_TO].
   * Example: Mapping a biological concept (Mycelial Networks) to a sociological concept (Community Support Structures).
Step 3: Generative Reframe Creation
If the source text does not explicitly contain a metaphor, the system generates one using the extracted structural pattern.
 * Input: A dense technical concept (e.g., "Working Memory Load").
 * Action: The system queries a StoryInsight or FictionUnit that shares the same structure (e.g., "The Backwards Bicycle Experiment").
 * Generation: "Your struggle with Working Memory is like the Backwards Bicycle: your internal model keeps snapping back to the old path".
 * Result: A new Reframe node linked to the concept.
Step 4: Classification by Pattern Type
To ensure the graph doesn't become a messy pile of associations, every source is classified by the kind of conceptual patterns it provides:
| Pattern Type | Source Examples | Use Case |
|---|---|---|
| Design/Structural | A Pattern Language | Reusable templates for problem-solving. |
| Narrative | Radiolab, This American Life | Explaining concepts through emotional arcs. |
| Dynamic | Sync, Complexity | Explaining timing, cycles, and synchronization. |
| Embodied | The Body Has a Mind of Its Own | Grounding abstract ideas in physical sensation. |
| Identity | Refuse to Choose! | Reframing personal traits and behaviors. |
3. Example: Ingesting "The Backwards Bicycle"
Here is how an "intelligent human" ingestion looks for a specific YouTube video or document about the Backwards Bicycle experiment.
 * Ingest & Segment: Identify the video as an Experiment node.
 * Extract Features:
   * Phenomena: Neuroplasticity, unlearning.
   * Schema Break: "Knowledge does not equal understanding."
 * Map to Graph:
   * Create Edge: (:Experiment {name:"Backwards Bicycle"})-[:DEMONSTRATES]->(:Concept {name:"Neuroplasticity"})
   * Create Edge: (:Experiment)-[:EMBODIES]->(:SchemaBreak {name:"Prediction Error"})
 * Generate Reframe:
   * Prompt: "Create a reframe for 'Habit Relapse' using the Backwards Bicycle."
   * Output: "Relapsing isn't failure; it's the handlebars snapping back. You are rewriting a neural pathway, not just making a choice."

---

## Implementation Plan

### Pass 2: Cross-Domain Mapping

**Location:** New service `library/graph/reframe_mapper.py` or extension of `scripts/auto_ingest_daemon.py`

**Algorithm:**
1. After Pass 1 extraction, collect all new entities of type: pattern, dynamic_pattern, story_insight, schema_break
2. Query existing graph for concepts without reframes: `MATCH (c:Concept) WHERE NOT (c)<-[:METAPHOR_FOR]-(:Reframe) RETURN c`
3. For each new pattern/story, prompt LLM: "Which of these concepts does [pattern] resonate with structurally?"
4. Create RESONATES_WITH or METAPHOR_FOR edges where confidence > 0.7

**Integration Point:** Run after `auto_ingest_daemon.py` completes Pass 1 on each book.

### Pass 3: Generative Reframe Creation

**Location:** Extension of existing `ReframeService` in `ies/backend/src/ies_backend/services/reframe_service.py`

**Algorithm:**
1. Identify "dense" concepts (high in-degree, low reframe count)
2. Query for StoryInsights or Patterns that share structural tags (e.g., "feedback", "threshold", "oscillation")
3. Generate reframe using template: "Concept X is like [Story/Pattern Y] because both involve [structural similarity]"
4. Store as Reframe node with `source: "Generated"`

**Trigger:** Background job or on-demand via API when user explores a concept lacking accessible reframes.

### Pass 4: Pattern Type Classification

**Location:** Book metadata enrichment in `scripts/ingest_calibre.py`

**Schema Addition:**
```python
# Add to Book node properties
pattern_type: Literal["design", "narrative", "dynamic", "embodied", "identity", "mixed"]
```

**Classification:** LLM prompt during ingestion or manual curation for high-value sources.

---

## Success Criteria

- [ ] Pass 2 creates cross-domain connections for 50%+ of extracted patterns/stories
- [ ] Pass 3 generates reframes for concepts with 0 existing reframes
- [ ] Graph exploration surfaces non-obvious connections (ADHD "resonance")
- [ ] Pattern type classification enables filtered exploration by learning style
