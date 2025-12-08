# IES Flow, Reader & Journey v2 – Context & Question Integration

This document describes how Flow Mode, Reader, and Journey should behave now
that Contexts and Questions are first-class entities.

---

## 1. Flow Mode v2 – Context Cockpit

### 1.1 When a Context Note is Active

Trigger: user opens a Context Note in SiYuan and enables Flow Mode.

Flow Mode should:

1. Identify `context_id` and `context_type`:
   - from frontmatter or a metadata block in the note.
2. Parse the note for structured sections:
   - `## Key Questions`
   - `## Areas of Exploration`
   - `## Core Concepts`
3. Map each bullet item under these headings to:
   - a Question node (for Key Questions)
   - an "area" entity (for Areas of Exploration)
   - a Concept (for Core Concepts, via the KG)

### 1.2 Flow Mode UI

Suggested layout:

- **Top:** Context summary
  - title, type, status, short description
- **Middle:** Button panels
  - `Key Questions` – each as a clickable chip/button
  - `Areas of Exploration` – same
  - `Core Concepts` – optional shortcuts into the KG
- **Bottom:** Status & actions
  - new connections found
  - last extraction run time
  - buttons:
    - `Run Extraction for Context`
    - `Run Extraction for This Question/Area`
    - `Open Question/Journey Reader`

### 1.3 On Question/Area Click

When a user clicks a Question or Area button:

1. Flow sets:
   - `active_context_id`
   - `active_focus_id` (question or area)

2. Flow calls Extraction Engine:

```ts
runExtraction({
  context_id: active_context_id,
  focus_id: active_focus_id,
  profile: getExtractionProfile(context_id, focus_id)
})
```

3. Extraction Engine:
   - uses:
     - domain_filters
     - core_concepts & synonyms
     - relation_types
   - queries:
     - inverted index
     - embeddings
     - library
   - sends candidate segments to LLM
   - writes:
     - new/updated concepts & relations to KG
     - new subquestions/links to Question Graph
     - updates to context's linked_sources
   - logs a Journey entry representing the extraction run

4. Flow updates:
   - **Concept pane**:
     - relevant concepts around this focus
   - **Relation pane**:
     - edges (with evidence counts)
   - **Sources pane**:
     - list of relevant sources/sections
   - **Suggestions**:
     - newly proposed subquestions
     - possible clarifications to current Question text

Flow should mark what is “new since last run” to support incremental exploration.

---

## 2. Reader v2 – Question/Journey Reader

Reader now has two modes:

### 2.1 Normal Library Reader (unchanged)

- User picks a book / source.
- Reads linearly.
- Takes highlights/notes.
- Notes stored normally; can be linked to contexts/questions later.

### 2.2 Question/Journey Reader

Trigger: user chooses `Open Question/Journey Reader` from Flow or from a Context Note.

Parameters:
- `context_id` (required)
- `focus_id` (Question ID or Area ID; optional but recommended)

#### UI Layout

- **Left pane: Context navigation**
  - Context title & type
  - List of `Key Questions` (clickable)
  - List of `Areas of Exploration`
- **Center pane: Source view**
  - Current book/article section
  - Navigation within the source
- **Right pane: Journey & Notes**
  - Timeline of Journey entries scoped to:
    - `context_id`
    - optionally `focus_id`
  - Highlights/notes taken while reading
  - AI summaries / answer fragments

#### Behavior

1. On opening:
   - If `focus_id` is a Question:
     - use KG + indexes to suggest relevant passages across sources.
   - Present suggestions as a list:
     - source title, section name, short preview, reason for relevance.

2. When user chooses a suggested passage:
   - load that source/section into center pane
   - log Journey entry:
     - `classification`: ["reading_note"]
     - `source_links`: [source_id]

3. Notes & highlights:
   - are auto-tagged:
     - `context_id`
     - `focus_id` if set
   - optionally:
     - passed to Extraction Engine to refine KG and Question Graph
   - logged as Journey entries:
     - `classification`: ["reading_note", "highlight"]

4. Reader Assistant (AI):
   - can summarize current passage in terms of the active Question:
     - e.g., "Summarize how this passage relates to Q2"
   - can generate:
     - answer fragments
     - subquestions based on confusing or important parts

---

## 3. Journey v2 – Always-On Trace

Journey is the glue that keeps everything consistent.

### 3.1 What Creates Journey Entries?

- Capture events (quick captures, voice notes)
- Dialogue interactions
- Flow button clicks + extraction runs
- Reader sessions (opening suggested passages, highlights, notes)
- Synthesis events (creating/updating answer blocks, context summaries)
- Thinking Mode sessions (if tagged with a context, or promoted later)

### 3.2 Minimal Data to Record

Every JourneyEntry should have at least:

- `timestamp`
- `context_id` (if known)
- optional `focus_id` (Question/Area ID)
- data about the event:
  - messages, actions, note content, etc.
- optional classification tags:
  - `answer_fragment`, `new_question`, `reframe`, `todo`, `reading_note`, `highlight`, `meta_structure`
- optional `entity_links` and `source_links`

### 3.3 Using Journey Data

- To **update structure**:
  - detect `new_question` entries and create Question nodes
  - detect `meta_structure` events to update Context Notes
- To **support replay**:
  - filter Journey by `context_id` (and optionally `focus_id`)
  - get a narrative of how understanding evolved
- To **aid AI agents**:
  - use recent Journey entries as context:
    - "What have we been doing in this context the last N sessions?"
    - "What are the last 5 open questions not yet answered?"

---

## 4. Interaction Flow Examples

### 4.1 Flow-based Exploration Example

Scenario: Context `ctx_feynman_adhd_time`, Question `q_adhd_time_relationship_wm`.

1. User opens the Context Note and enables Flow.
2. Flow parses Key Questions and displays Q2 as a button.
3. User clicks Q2.
4. Flow sets `active_context_id = ctx_feynman_adhd_time`, `active_focus_id = q_adhd_time_relationship_wm`.
5. Flow calls `runExtraction(...)`.
6. Extraction Engine:
   - finds relevant segments in ADHD/EF sources.
   - calls LLM to extract relations between time blindness and working memory.
   - writes new edges + evidence to KG.
   - adds suggested subquestions to the Question Graph.
   - logs a Journey entry describing this extraction.
7. Flow reloads its panels:
   - shows concepts and relations around time blindness and working memory.
   - lists key sources and snippets.
8. User can:
   - click into Reader to examine those sources, or
   - ask the AI to synthesize an answer fragment.

### 4.2 Question-Driven Reading Example

1. From Flow, user clicks "Open Question/Journey Reader" for Q2.
2. Reader opens in Question/Journey mode:
   - left pane: context + questions
   - center: empty (no source chosen yet)
   - right: Journey entries so far for Q2
3. Reader proposes a list of relevant passages across sources.
4. User chooses one; center pane loads that passage.
5. User highlights a key paragraph and adds a note.
6. System:
   - tags note with `context_id` and `focus_id`
   - logs a Journey entry (`classification`: ["reading_note", "highlight"])
   - optionally updates KG if new relations are detected.
7. Later, user asks:
   - "Summarize everything we have on Q2 so far."
   - Synthesis Assistant pulls:
     - KG relations
     - evidence snippets
     - reading notes
     - dialogue fragments
   - Generates an AnswerBlock attached to Q2.

---

## 5. Integration with Existing IES Components

This v2 behavior should be integrated without major rewrites:

1. **SiYuan Plugin**:
   - Add helpers to:
     - detect when a Context Note is active
     - parse headings for context structure
     - surface Flow + Reader UI panels

2. **Backend**:
   - Extend metadata store with Context, Question, Journey schemas.
   - Plug Extraction Engine into Flow/Reader calls using new profiles.

3. **AI Prompts**:
   - Update system prompts for:
     - Dialogue: "You are operating inside Context X..."
     - Flow: "You are helping navigate questions within Context X..."
     - Reader: "You are helping read sources to answer Question Y..."
   - Ensure `context_id` and optional `question_id` are always part of AI context.

4. **Thinking Mode Integration**:
   - Optionally:
     - tag a Thinking session with a `context_id`
     - mine Thinking logs for emergent questions/themes
     - provide a "promote to Context/Question" action.

5. **Dynamic Source Acquisition Integration**:
   - When extraction or Reader reveals topic gaps:
     - trigger a search/download pipeline to fetch new books/papers.
   - After ingestion:
     - new sources go through Level 0–2 processing.
     - become available for future context-aware extractions.

6. **Migration**:
   - Start by creating a small number of Context Notes for existing "big things":
     - e.g., IES, ADHD & EF, Homelab, Therapy Practice.
   - Gradually:
     - extract Key Questions
     - wire Flow Mode to them
     - add Extraction Profiles
     - extend Reader Question/Journey mode.
