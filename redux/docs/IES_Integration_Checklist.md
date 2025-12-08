# IES Context + Question Layer – Integration Checklist

This file is intended as a **working TODO** for integrating the Context + Question
layer into the existing IES codebase. It is written to be friendly to dev assistants
like Claude Code.

---

## 1. Add Docs to the Repo

- [ ] Add this folder to the repo:
  - `IES_Context_Question_Layer/`
    - `START_HERE.md`
    - `docs/IES_Context_and_Question_Layer.md`
    - `docs/IES_Extraction_Profile_Examples.md`
    - `docs/IES_Flow_Reader_Journey_v2.md`
    - `docs/IES_Integration_Checklist.md`

- [ ] Link to these docs from any existing high-level IES architecture doc
  (e.g., `docs/IES_Architecture.md`).

---

## 2. Define Core Types / Schemas

In whatever language/store you use (TS, Python, DB schemas, etc.):

- [ ] Define `Context` type/interface with fields:
  - `id`, `type`, `title`, `parent_context_id?`, `status`
  - `key_questions`, `core_concepts`, `linked_sources`, `artifacts`
  - `created_at`, `updated_at`

- [ ] Define `Question` type/interface with fields:
  - `id`, `context_id`, `parent_question_id?`
  - `question_text`, `status`
  - `prerequisite_questions`, `related_concepts`, `linked_sources`
  - `answers[]`
  - timestamps

- [ ] Define `AnswerBlock` type/interface.

- [ ] Define `JourneyEntry` type/interface.

- [ ] Define `ExtractionProfile` and `QuestionExtractionProfile` types/interfaces.

- [ ] Add persistence:
  - JSON files, DB tables, or re-use existing metadata store.

---

## 3. SiYuan Context Note Conventions

- [ ] Decide how to store `context_id` and `context_type` in a Context Note:
  - frontmatter / YAML
  - a dedicated metadata block at top of note
  - or specific SiYuan attributes

- [ ] Implement a parser that:
  - given a Context Note document:
    - reads `## Key Questions` section
    - reads `## Areas of Exploration` section
    - reads `## Core Concepts` section
  - maps each bullet item to:
    - a Question (for Key Questions)
    - an "area" entity
    - a Concept (for Core Concepts, mapped to KG IDs where possible)

- [ ] Add logic to:
  - create new Question nodes for items that don't yet have IDs
  - store back references (IDs) in the note if desired (optional, but helpful).

---

## 4. Flow Mode v2

- [ ] Make Flow Mode require an active `context_id`:
  - When enabled, it should:
    - detect if current note is a Context Note
    - if not, offer to:
      - choose a context
      - or create a new Context from the current note.

- [ ] Implement Flow UI panels:
  - Context summary
  - Key Questions as buttons
  - Areas of Exploration as buttons
  - Core Concepts as concept shortcuts

- [ ] On Question/Area button click:
  - set `active_context_id`, `active_focus_id`
  - call Extraction Engine:

```ts
runExtraction({
  context_id: active_context_id,
  focus_id: active_focus_id,
  profile: getExtractionProfile(context_id, focus_id)
})
```

- [ ] After extraction, update Flow panels:
  - show concepts, relations, sources, suggested subquestions.
  - highlight “new since last run”.

---

## 5. Extraction Engine – Context Integration

- [ ] Implement `runExtraction({ context_id, focus_id, profile })`:

  High-level steps:
  1. Use `profile.domain_filters` to filter sources from Library.
  2. Use inverted index to find segments containing:
     - `profile.core_concepts`
     - `profile.synonyms` (concept → list of phrases).
  3. Optionally use embedding index to refine candidate segments.
  4. Batch segments and send to LLM with:
     - context + question description
     - profile (concepts, relation_types).
  5. Parse LLM response into:
     - new/confirmed Concept nodes
     - Relation edges (with relation types)
     - Evidence snippets
     - suggested new subquestions/questions.
  6. Write changes to:
     - Knowledge Graph (concepts, relations, evidence)
     - Question Graph (new questions/links)
     - Context metadata (linked_sources).
  7. Write a JourneyEntry describing:
     - context_id, focus_id
     - sources touched
     - counts of new concepts/relations/questions.

- [ ] Add prompts/templates for the extraction LLM calls that:
  - reference the ExtractionProfile
  - produce structured JSON output for concepts/relations/evidence/questions.

---

## 6. Reader v2 – Question/Journey Mode

- [ ] Extend Reader to support two modes:
  - Normal Library Reader (existing behavior)
  - Question/Journey Reader

- [ ] For Question/Journey Reader:
  - require `context_id`
  - optionally `focus_id`

- [ ] Implement left pane:
  - show Context title/type
  - show Key Questions
  - show Areas of Exploration

- [ ] Integrate with KG + indexes:
  - when a Question is active:
    - propose a ranked list of relevant passages across sources.

- [ ] Notes & highlights:
  - auto-tag with `context_id` and `focus_id` (if set)
  - store as JourneyEntry (`classification`: ["reading_note", "highlight"])
  - optional path:
    - pass notes/highlights to Extraction Engine for incremental refinement.

---

## 7. Journey v2

- [ ] Ensure Journey logging is implemented for:
  - Capture events
  - Dialogue interactions
  - Flow button clicks + Extraction runs
  - Reader sessions
  - Synthesis events
  - (optionally) Thinking Mode sessions

- [ ] Add simple query/filter helpers:
  - `getJourneyForContext(context_id)`
  - `getJourneyForFocus(context_id, focus_id)`
  - `getRecentJourneyEntries(context_id, n)`

- [ ] Consider a UI:
  - timeline view per Context
  - filter by classification (questions, answers, todos, notes, etc.).

---

## 8. Thinking Mode Integration

- [ ] Leave core Thinking Mode behavior unchanged.

- [ ] Add optional integration points:
  - allow tagging a Thinking session with a `context_id`
  - periodically scan Thinking logs for:
    - repeated questions
    - emerging models/theories
  - provide a “promote” action:
    - promote to new Context
    - promote to Question(s) under an existing Context

- [ ] Hook this into AI assistants:
  - a Thinking transcript can be passed to:
    - a “schema builder” that proposes:
      - candidate Contexts
      - candidate Questions.

---

## 9. Dynamic Source Acquisition Integration

- [ ] If not already present, formalize a small API for:
  - `searchSources(query, typeFilters)`
  - `downloadSource(source_handle)`
  - `ingestSource(file_or_url)` (plugs into Level 0 Ingestion & Metadata)

- [ ] Wire Contexts/Questions into this:
  - when a Context/Question is under-sourced:
    - propose:
      - "Fetch more sources about X?"
  - use:
    - direct topic searches (e.g., "ADHD time perception review")
    - related topic searches (e.g., "temporal discounting ADHD", "time perception disorders")

- [ ] After download:
  - run new sources through:
    - Level 0 (ingestion, metadata)
    - Level 1 (inverted index)
    - Level 2 (embeddings)
  - mark them as available for future extractions.

---

## 10. First End-to-End Test Scenario

Use this as a validation script:

1. Create Context:
   - Feynman: "What is ADHD time perception?"
2. Use Dialogue Mode to:
   - define 3–5 Key Questions
   - define 2–3 Areas of Exploration
   - identify core concepts.
3. Open Flow Mode on this Context:
   - click a Question
   - run Extraction with a basic profile.
4. Confirm:
   - KG updated with relevant concepts/relations
   - Question Graph updated (maybe new subquestions)
   - Journey entry logged.
5. Open Reader in Question/Journey mode:
   - choose the same Question
   - open one suggested passage and take notes.
6. Ask Synthesis Assistant:
   - "Draft a short explanation answering this Question."
7. Confirm:
   - an AnswerBlock is created and attached to the Question
   - Context Note's "Current Best Understanding" section can be updated.

Once this scenario works end-to-end, the new layer is effectively integrated.
