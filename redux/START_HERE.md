# START HERE – IES Context + Question Layer Pack

This zip contains a **self-contained spec bundle** for the new Context + Question layer
for IES. It is designed so you can drop it into your project repo and point Claude Code
(or any other assistant) at it as a starting knowledge base.

The goal of this layer is to:
- Make **contexts** (Feynman problems, projects, theories, concept clusters, life areas)
  first-class objects.
- Represent **unknowns** as a structured **Question Graph** inside each context.
- Drive **context-aware extraction**, Flow Mode, Reader, and Journey.
- Keep all of your existing IES architecture and modes intact, while giving AI a reliable
  answer to “where does this note go?”

> **Important:** This does *not* replace or break Thinking Mode.
> - Thinking Mode still works as-is for free-form, exploratory sessions.
> - The *outputs* of a Thinking session can now be promoted into:
>   - new Contexts (e.g. a new Feynman problem or theory)
>   - new Questions inside existing Contexts
> - Over time, this lets raw Thinking sessions crystallize into structured,
>   traversable problems and models.

> **Important capability:** The system can **download new books and academic papers**
> using specialized tools.
> - When a context exposes a new topic or gap, the system can:
>   - search for and download relevant books, papers, and articles
>   - bias towards a variety of source types:
>     - directly on-topic sources
>     - adjacent/related sources offering alternative angles
> - These become part of the Library and are processed via the **hierarchical
>   source processing pipeline** defined in this bundle.

---

## Files & Structure

- `START_HERE.md` ← **you are here**
- `docs/`
  - `IES_Context_and_Question_Layer.md`
    - Master spec for:
      - Context Graph
      - Question Graph
      - Knowledge Graph integration
      - Library + Indexes
      - Journey Log
    - Defines Context Notes in SiYuan and Extraction Profiles.
    - Includes notes on:
      - Thinking Mode integration
      - Dynamic acquisition of new sources (books/papers).
  - `IES_Extraction_Profile_Examples.md`
    - Concrete JSON-style examples of Extraction Profiles for:
      - a Feynman problem (ADHD time perception)
      - a Concept cluster (Executive Function components)
      - a Theory (Motivation & task initiation in ADHD)
      - a Project (IES Flow Mode v2)
    - These are templates for what the Extraction Engine expects.
  - `IES_Flow_Reader_Journey_v2.md`
    - Behavioral spec for:
      - Flow Mode v2 as a **Context Cockpit**
      - Reader v2 with **Question/Journey** mode
      - Journey v2 as an always-on trace
    - Describes how user actions (clicks, reading, notes) turn into:
      - context-aware extraction jobs
      - updates to Context/Question/KG
      - Journey entries.
  - `IES_Integration_Checklist.md`
    - Practical checklist for integrating this layer into the existing IES codebase.
    - Intended as a “task list” for Claude Code to work from:
      - add types
      - wire SiYuan plugin behavior
      - extend Flow + Reader
      - hook in Extraction Engine and Journey.

---

## Recommended Ingestion Order for Claude / Tools

1. **Read `IES_Context_and_Question_Layer.md` first**
   - Understand the data model and how it sits on top of existing IES pieces.

2. Then **skim `IES_Flow_Reader_Journey_v2.md`**
   - Get a feel for how the UI/UX and mode behaviors change under the new model.

3. Then **review `IES_Extraction_Profile_Examples.md`**
   - Internalize the structure and purpose of Extraction Profiles.
   - Use these as examples when generating profiles for new Contexts.

4. Finally, **use `IES_Integration_Checklist.md` as a working TODO**
   - This is the main “implementation driver” doc:
   - Claude Code (or another dev assistant) can follow it step by step
     to integrate the new layer into the existing IES codebase.

---

## How This Fits with Existing IES Modes

- **Thinking Mode**
  - Unchanged functionally.
  - New: Thinking sessions can be used to:
    - identify emergent Feynman problems, projects, and theories
    - auto-generate or refine Context Notes and Question Graphs.
  - Implementation idea:
    - add a small “promote to Context/Question” helper that:
      - scans Thinking logs for promising recurring themes/questions
      - offers to turn them into Contexts or Questions.

- **Capture / Dialogue / Flow / Reader / Journey**
  - All are extended, not replaced.
  - Each mode now:
    - operates **inside a Context**, and often a **Question**
    - writes updates to:
      - Context Graph
      - Question Graph
      - Knowledge Graph
      - Journey Log

- **Source Acquisition**
  - Existing / future “book & paper download” tools become:
    - part of the **Ingestion & Metadata** pipeline.
  - New behavior:
    - when you are inside a Context and a gap is identified:
      - system can propose:
        - “Fetch and ingest more sources on X”
      - use topic + related-topic search to diversify:
        - direct matches
        - conceptually adjacent perspectives.

---

## Next Steps

For integration work:

- Use `IES_Integration_Checklist.md` as the immediate working document.
- As you adapt the codebase:
  - you can annotate these docs with implementation notes
  - or generate new `docs/IES_*` files (e.g., for specific services).

If you want to evolve or extend the design, the **recommended extension points** are:
- adding new `context_type` values
- defining richer `relation_types` in the Knowledge Graph
- expanding the hierarchical processing logic in the Extraction Engine
- adding new Reader/Flow affordances for ADHD-friendly navigation.
