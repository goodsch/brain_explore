# IES Context + Question Layer

This document defines the **Context Graph** and **Question Graph** that sit on top of
the existing IES architecture (SiYuan, knowledge graph, ingestion, Flow, Journey, etc.).

The goal is to:
- Anchor all AI behavior inside explicit **contexts** (Feynman problems, projects,
  theories, concept clusters, life areas).
- Represent **unknowns** as a structured **Question Graph** inside each context.
- Use these to drive **context-aware extraction**, Flow Mode, Reader, and Journey.
- Keep all of your existing IES architecture and modes intact, while giving AI a reliable
  answer to “where does this note go?”

This layer is **additive**: it should be integrated into existing IES components, not
replace them.

---

## 1. Core Concepts

### 1.1 Context

A **Context** is a structured "place" where attention lives for a while.

Examples:
- Feynman problem: "What is ADHD time perception?"
- Project: "IES Flow Mode v2"
- Theory: "Motivation & task initiation in ADHD"
- Concept cluster: "Executive Function components"
- Life area: "Therapy practice", "Parenting Cal"

Each Context:
- Has a **Context Note** in SiYuan (markdown-ish)
- Is represented as a node in the **Context Graph**
- Can have subcontexts
- Has an internal **Question Graph**
- Links into the global **Knowledge Graph**

#### Context Types

At minimum:

- `feynman_problem`
- `project`
- `theory`
- `concept_cluster`
- `life_area`

More types can be added later; the system should treat them generically.

#### Context Fields (conceptual)

```ts
Context {
  id: string
  type: "feynman_problem" | "project" | "theory" | "concept_cluster" | "life_area" | string
  title: string
  parent_context_id?: string
  status: "idea" | "active" | "paused" | "archived"

  key_questions: string[]          // Question IDs
  core_concepts: string[]          // Concept IDs in the KG
  linked_sources: string[]         // Source IDs in the Library
  artifacts: string[]              // Note IDs, diagrams, code, etc.

  created_at: string
  updated_at: string
}
```

Implementation detail:
- This can live in the existing IES metadata store (JSON/DB).
- The SiYuan Context Note is the human-readable representation; metadata can
  be written as frontmatter or a special block.

---

### 1.2 Question

**Question nodes** live inside a context and represent structured unknowns.

Examples:
- "How do ADHD brains subjectively experience time passing?"
- "What is the relationship between time blindness and working memory?"
- "What experimental paradigms are used to study ADHD time perception?"

Fields:

```ts
Question {
  id: string
  context_id: string
  parent_question_id?: string     // For subquestions / tree structure

  question_text: string
  status: "open" | "partial" | "answered" | "modeled"

  prerequisite_questions: string[]    // "To know this, you must know these"
  related_concepts: string[]          // Concept IDs in KG
  linked_sources: string[]            // Source IDs
  answers: AnswerBlock[]              // See below

  created_at: string
  updated_at: string
}
```

```ts
AnswerBlock {
  id: string
  question_id: string
  content: string          // markdown
  quality: "draft" | "good_enough" | "polished"
  created_at: string
  updated_at: string
}
```

Questions are:
- Created / refined via **Dialogue Mode**
- Used as anchors for **Flow Mode**, **Reader**, and **Synthesis**
- Targets for context-aware extraction

---

### 1.3 Knowledge Graph (existing)

The existing Knowledge Graph remains the shared backbone:

- `Concept` nodes (constructs, people, methods, etc.)
- `Relation` edges (component_of, causes, associated_with, explains, etc.)
- `Evidence` (source + snippet + location)

Context & Question nodes link into the KG:
- `core_concepts` (Context → Concept)
- `related_concepts` (Question → Concept)

---

### 1.4 Library & Indexes (existing + extended)

Library:
- Books, PDFs, notes, transcripts, etc.
- Each source:
  - metadata (title, author, topics, etc.)
  - structured text (chapters, sections, windows)

Indexes:
- **Inverted word index** over text segments
- **Embedding index** (optional) per segment

These are used to:
- Cheaply filter candidate segments for extraction, given a Context & Question.

---

### 1.5 Journey Log

Journey is the chronological trace of how you work inside contexts and questions.

Conceptually:

```ts
JourneyEntry {
  id: string
  timestamp: string

  context_id?: string
  focus_id?: string        // Question ID or "area of exploration" ID

  user_message?: string
  ai_message?: string

  classification: ("answer_fragment" | "new_question" | "clarification" |
                   "todo" | "meta_structure" | "reading_note" | "highlight")[]

  entity_links: string[]   // Concept IDs
  source_links: string[]   // Source IDs
}
```

Journey entries are:
- Created whenever:
  - you capture something
  - talk to the AI
  - click in Flow
  - read in Reader
  - run extraction or synthesis
- Used to:
  - update Context Notes
  - grow the Question Graph
  - enrich the KG

---

## 2. Context Notes in SiYuan

Contexts are primarily edited as ordinary SiYuan notes, with a **convention-based structure** that the plugin/agents read.

Example structure:

```markdown
# Feynman: What is ADHD time perception?

%% Optional: frontmatter / metadata block
- context_id:: C1
- context_type:: feynman_problem
- status:: active

## Summary / Intent
A brief description of what I'm trying to understand in this context.

## Key Questions
- [ ] Q1: How do ADHD brains subjectively experience time passing?
- [ ] Q2: What is the relationship between time blindness and working memory?
- [ ] Q3: How do time estimation and time reproduction differ in ADHD?

## Areas of Exploration
- A1: Clinical models (Barkley, delay aversion, etc.)
- A2: Experimental paradigms (time estimation tasks, discounting tasks)
- A3: Daily-life implications and therapy applications

## Core Concepts
- ADHD time perception
- time blindness
- temporal discounting
- prospective memory
- working memory
- executive function

## Current Best Understanding
(This section is updated by Synthesis Assistant)
```

The **Flow Mode plugin** and AI agents will:
- parse sections like `Key Questions`, `Areas of Exploration`, `Core Concepts`
- map list items to Question nodes and “areas” for the UI
- keep metadata (IDs, etc.) consistent between the note and the graph-level store

---

## 3. Context-Aware Extraction Profiles

Each Context can have a small **Extraction Profile** that tells the system:

> "When I’m working here, these are the concepts and relations I care about."

Conceptual shape:

```ts
ExtractionProfile {
  context_id: string
  // Optionally per-question overrides in a map
  question_overrides?: {
    [question_id: string]: QuestionExtractionProfile
  }

  // Defaults for this context:
  core_concepts: string[]           // e.g. ["ADHD time perception", "time blindness", ...]
  synonyms: Record<string, string[]>// concept -> list of synonyms/phrases
  relation_types: string[]          // e.g. ["component_of", "impacts", "associated_with"]
  domain_filters: string[]          // e.g. ["ADHD", "executive_function"]
}
```

```ts
QuestionExtractionProfile {
  core_concepts?: string[]
  synonyms?: Record<string, string[]>
  relation_types?: string[]
  domain_filters?: string[]
}
```

These profiles are what the **Extraction Engine** uses to build an extraction plan:
- Which sources to look at
- Which segments to fetch
- What to ask the LLM to extract

Profiles can live:
- as separate JSON/TOML files in the repo, or
- embedded as a fenced block in the Context Note

---

## 4. Hierarchical Source Processing (Levels)

To keep extraction efficient as the library grows, processing is layered:

### Level 0 – Ingestion & Metadata
- Extract text + structure for each source.
- Attach metadata (title, author, topics).
- Optionally call external APIs (Hardcover, etc.) for topics/themes.
- Store in Library.

### Level 1 – Full-Text Index
- Build an inverted index:
  - term → list of (source_id, segment_id, positions)
- Done once per source.

### Level 2 – Embeddings (optional but recommended)
- Compute embeddings for segments (chapter/section/windows).
- Build a vector index per domain or global.

### Level 3 – Context-Specific AI Extraction
Given `context_id` and optional `question_id` and its profile:

1. Filter sources by `domain_filters` or other tags.
2. Use Level 1 (inverted index) to find segments containing:
   - core concepts
   - synonyms
3. Use Level 2 (embeddings) to refine candidate segments.
4. Batch those segments and call LLM:
   - extract concepts & relationships
   - generate evidence snippets
   - suggest new subquestions
5. Write updates into:
   - Knowledge Graph (concepts + relations + evidence)
   - Question Graph (new questions)
   - Context metadata (linked sources)

Levels 0–2 are cheap and global; Level 3 is expensive and **only run for specific contexts/questions**.

---

## 5. Thinking Mode & Dynamic Source Acquisition

### 5.1 Thinking Mode (unchanged behavior, new uses)

Thinking Mode remains a **free-form, exploratory space** where you:
- brainstorm
- journal
- riff with an AI thinking partner
- perform long-form reasoning without worrying about structure

This Context + Question layer does **not** change Thinking Mode’s behavior.

Instead, it provides **new ways to use its outputs**:

- After or during a Thinking session, the system can:
  - detect recurring themes, questions, or tentative models
  - propose:
    - "Promote this to a new Context?" (e.g., a Feynman problem or theory)
    - "Add these questions to an existing Context?"
  - create or update:
    - Context Notes
    - Question nodes
    - Extraction Profiles

Over time:
- raw, messy Thinking sessions crystallize into structured:
  - Feynman problems
  - projects
  - theories
  - question graphs

This allows the system to respect how your brain actually works (bottom-up, exploratory),
while still gradually building a navigable structure over it.

### 5.2 Dynamic Source Acquisition (books & academic papers)

IES already has (or will have) tools to:
- search for
- download
- ingest

**new books, articles, and academic papers** from external sources.

This layer integrates that capability by:

- Letting **Contexts** express information gaps:
  - via open questions
  - via missing concept links in the KG
  - via explicit user intent ("we need more sources on X")

- When a gap is detected, the system can:
  - perform targeted searches:
    - direct topic matches (e.g. "ADHD time perception clinical review")
    - conceptually related topics (e.g. "temporal discounting ADHD", "time perception in depression" for comparison)
  - prioritize diversity:
    - clinical reviews
    - experimental papers
    - theory pieces
    - practical guides

- Newly acquired sources are:
  - passed through the standard **Ingestion & Metadata** pipeline
  - indexed at Levels 1–2
  - made available for future **context-specific extractions**.

This closes the loop:
- Contexts and Questions reveal what you *don’t* have.
- Source acquisition tools fill those gaps on-demand.
- Hierarchical processing integrates new material efficiently.

---

## 6. Modes & How They Use Context + Questions (Overview)

See `IES_Flow_Reader_Journey_v2.md` for detailed behavior of Flow, Reader, and Journey.

High-level:

- **Capture Mode**
  - Ingests quick thoughts and questions.
  - Assigns them to Contexts and/or creates new Contexts/Questions.

- **Dialogue Mode**
  - Operates inside a chosen Context.
  - Builds the Question Graph and core concepts for that Context.

- **Flow Mode**
  - Treats the Context Note as a cockpit:
    - buttons for Key Questions, Areas of Exploration, Core Concepts
  - On click:
    - runs context-aware extraction
    - surfaces concepts, relations, sources

- **Reader Mode**
  - Has:
    - Normal Library mode (book-first)
    - Question/Journey mode (context + question first, then sources)

- **Journey Mode**
  - Logs everything as a chronological trace, always tagged with:
    - context_id
    - optional focus_id (question/area)

Thinking Mode:
- floats above all of this as a free-thinking space.
- its outputs can be turned into new Contexts and Questions as needed.

---

## 7. Integration Notes & Migration Strategy

This layer should be integrated into the existing IES architecture with minimal disruption:

1. **Add Context + Question schemas** to your existing metadata layer.
2. **Wrap existing modes** so they require or infer a `context_id`:
   - When a chat starts, either:
     - pick an existing Context, or
     - create a new one on the fly
3. **Add Context Notes convention** in SiYuan:
   - standard headings for Key Questions, Areas of Exploration, Core Concepts
4. **Update Flow Mode** to:
   - parse Context Note and render context-specific controls
   - trigger context-aware extraction runs (instead of generic entity exploration)
5. **Extend Reader** to:
   - add the Question/Journey mode with context/question left pane
   - auto-tag reading notes with context/question
6. **Wire in dynamic source acquisition tools**:
   - allow Contexts/Questions to request more sources
   - feed new sources into the hierarchical processing pipeline
7. **Keep existing Knowledge Graph + ingestion intact**:
   - just route extraction through the new context-aware pipeline
8. **Integrate Thinking Mode outputs**:
   - add affordances to promote themes/questions to Contexts/Questions.

This allows incremental adoption:
- start by creating a few Context Notes for existing "big things"
- make Flow Mode context-aware
- then gradually plug in:
  - Extraction Profiles
  - Reader Question/Journey view
  - dynamic source acquisition for high-value contexts.
