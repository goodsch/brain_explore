# AI Assistant Directives for IES × SiYuan

These directives define how an AI assistant should create, edit, and move notes
within this architecture. They assume that **the AI is the primary author** and
the human is the primary reader / explorer.

They now explicitly incorporate the **Quick Capture layer**, where blocks are
captured with minimal friction and only lightly processed until you interact
with them.

---

## 1. Global Principles

1. **Atomicity**
   - 1 idea → 1 seed-block
   - 1 insight → 1 shaping-block
   - 1 concept → 1 canonical concept page
   - 1 decision → 1 decision-block
   - 1 capture event → 1 quick-capture block (with its own metadata)

2. **Reference, don’t duplicate**
   - Use block references wherever possible instead of copying text.
   - Prefer linking to Seedlings and Dialogue blocks rather than restating them.

3. **Always create an entry point**
   - Any substantial operation (dialogue session, map, synthesis) must end with:
     - A short “Entry Point Summary” section
     - Clear links to 2–5 key blocks or pages to visit next

4. **Mode-awareness**
   - Respect IES modes:
     - Capture → `00_Inbox`, quick-capture blocks
     - Dialogue → `02_Shaping`
     - Flow → `03_Flow_Maps`
     - Synthesis → `04_Concepts`, `05_Projects`
     - Archive → `06_Archive`

5. **Human-first readability**
   - Write for future-Chris: concise, clear, and context-rich.
   - Avoid generic psychoeducation unless explicitly requested.
   - Highlight what changed in Chris’s world-model.

---

## 2. Quick Capture Behavior

Quick captures are the **front door** of the system: blocks created with
minimal friction that may not have clear context yet.

### 2.1. Schema & Location

- Any block with `quick_capture: true` follows
  `/07_System/Quick_Capture_Schema.md`.
- It may live in:
  - `00_Inbox` daily quick-capture files
  - Book notes in `04_Concepts/Sources/Books`
  - Project notes
- The **sidebar queue** (plugin) is assumed to filter for:
  - `quick_capture: true`
  - `capture_status != processed`

### 2.2. Allowed Automatic Processing

When a new quick capture arrives (e.g., via HTTP POST):

- Initialize metadata:
  - `quick_capture: true`
  - `capture_channel`, `capture_source`, `capture_time`
  - `capture_status: raw`
- The AI **may** in background:
  - Compute a very short `auto_summary`
  - Suggest rough `auto_labels`
  - Set `linked_concepts` **only when trivially obvious**
    (e.g., capture literally says “Phenomenology:” and a concept with that ID exists)
  - Update `capture_status` from `raw` → `classified`

### 2.3. Prohibited Automatic Processing

The AI should **not** automatically:

- Move the block to another file or notebook.
- Split the capture into Seedlings.
- Attach it to a Project or Concept page in a structural way.

Those operations belong to **interactive processing**, when you select a capture
in the sidebar and choose what to do with it.

### 2.4. Interactive Processing Flow

When you trigger “Process this capture”:

- The AI:
  1. Reads the block and its metadata.
  2. Asks (or uses a default pattern) what you want:
     - Turn into one or more Seedlings
     - Attach to a Concept
     - Attach to a Project
     - Just summarize and mark done
  3. Performs the chosen actions:
     - Creates Seedlings in `01_Seedlings` as needed
     - Adds references on Concept / Project pages
  4. Updates:
     - `capture_status: processed`
     - `auto_summary`, `auto_labels`, `linked_concepts` if missing

---

## 3. Folder-Level Directives

### 00_Inbox

- Purpose: ephemeral capture, raw input, unsorted material.
- Typical structure:
  - Daily files: `QuickCapture_YYYY-MM-DD.md`
  - Each capture = one block with quick-capture metadata.
- Rules:
  - Do **not** perform heavy synthesis here.
  - Ensure each capture has:
    - `quick_capture: true`
    - `capture_channel`, `capture_source`, `capture_time`
    - `capture_status: raw | classified | processed`
  - Sidebar / tools should treat this as a primary quick-capture source, but
    remember that quick-capture blocks can also live elsewhere.

### 01_Seedlings

- Purpose: smallest meaningful units.
- Rules:
  - Each seed-block expresses exactly **one** idea, question, observation, or schema fragment.
  - Attach attributes:
    - `idea_type` (question, metaphor, schema, memory, etc.)
    - `domain` (ADHD, therapy, self, systems, etc.)
    - `confidence` (low/medium/high)
    - `clarity` (fuzzy/partial/clear)
  - Seedlings must be written so they make sense when read alone.
  - Seedlings may be **created from quick captures** during interactive processing,
    but should **not** be spawned automatically without an explicit action.

### 02_Shaping

- Purpose: guided questioning, internal model shaping, and cognitive excavation.
- Rules:
  - Preserve the questioning chain:
    - Mark AI vs. human turns clearly.
    - Use headings for phases of exploration.
  - At the end of each session, output:
    - Key insights
    - What changed in thinking
    - New or updated Seedlings
    - References to any processed quick captures used
  - Do **not** promote new concepts directly from here; instead:
    - Create or update Seedlings
    - Propose concept updates in a dedicated section

### 03_Flow_Maps

- Purpose: non-linear exploration and mapping.
- Rules:
  - Use visual structures (Mermaid, tables, lists, nested headings).
  - Represent:
    - Concept clusters
    - Schema diagrams
    - Timelines
    - System views
  - Always:
    - Include a “How to read this map” section.
    - Provide 2–4 recommended next places to jump to.

### 04_Concepts

- Purpose: canonical knowledge graph.
- Rules:
  - One concept per file.
  - Structure each concept page with:
    - Definition (how Chris currently understands it)
    - Core properties / dimensions
    - Related concepts
    - Examples from Chris’s life/clients/projects
    - Common confusions / pitfalls
    - Links to relevant Seedlings, Shaping, Flow Maps, Projects, and if relevant,
      **source highlights / quick captures**.
  - When updating:
    - Add a short changelog section (what changed and why).
    - Maintain backward compatibility in links and references.

### 05_Projects

- Purpose: active things being built.
- Rules:
  - Every project must have:
    - Goals
    - Questions
    - Plan
    - Status
    - Logs
  - Any task-like item should:
    - Link to a corresponding entry in the external task manager (Todoist, etc.), if applicable.
  - Every project edit must end with:
    - A “Next actionable step” section.
    - Status update (if relevant).
  - Quick captures **inside project files** should follow the same quick-capture schema,
    allowing them to show up in the global queue while still living in their contextual home.

### 06_Archive

- Purpose: long-term reference, not active editing.
- Rules:
  - Only AI moves content here.
  - Mark archived items with:
    - `archived_on`
    - `reason` (superseded, completed, deprecated, etc.)

### 07_System

- Purpose: meta-layer and system definition.
- Rules:
  - Human edits here are allowed and expected.
  - AI should:
    - Respect any changes Chris makes to schemas and directives.
    - Treat this as the source of truth for structure.
    - Summarize major changes when this folder is edited.

---

## 4. Interaction-Level Behaviors

Whenever the AI:

1. **Receives a quick capture (Capture mode)**
   - Create or update a block with quick-capture metadata.
   - Optionally compute `auto_summary`, `auto_labels`, and trivially obvious `linked_concepts`.
   - Update `capture_status` from `raw` → `classified` as appropriate.

2. **Processes a capture interactively**
   - Follow the Quick Capture flow (Section 2.4).
   - Ensure the result is:
     - Visible (Seedlings, Concept links, Project notes).
     - Traceable (links back to the original capture).

3. **Runs a Dialogue session (Shaping)**
   - Start from Seedlings and/or processed captures.
   - End with:
     - Updated/new Seedlings
     - Proposed concept updates
     - Candidate Flow Maps to create or adjust

4. **Builds or updates a Flow Map**
   - Always center it on one or a small number of focal concepts or questions.
   - Use references to Seedlings, Concepts, and processed captures, not raw duplicated text.

5. **Updates a Concept page**
   - Identify which Seedlings / Shaping notes / captures support the update.
   - Note what changed in understanding explicitly.

6. **Touches a Project**
   - Ensure the project still has:
     - Clear goals
     - Clear next actions
     - Up-to-date status

---

## 5. Safety Valves and Health Checks

- Periodically:
  - Scan for quick captures stuck in `raw` or `classified` for a long time and:
    - Offer a short summary of themes.
    - Suggest either bulk-marking some as processed or scheduling a processing session.
  - Scan for orphan Seedlings (no references) and:
    - Suggest merging, promoting, or archiving them.
  - Scan for stale concepts (no updates despite adjacent changes) and:
    - Suggest a review session.
  - Scan for Flow Maps with outdated links or missing explanations.

Your AI assistant can implement automated “health check” runs as background jobs
or scheduled commands that report back to you with suggested maintenance actions.
