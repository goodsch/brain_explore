# Quick Capture Schema

Quick captures are **blocks**, not whole notes. They can live almost anywhere
(00_Inbox, book notes, project notes), but what makes them "quick captures"
is their metadata.

This schema describes the common fields that should be added to any
quick-captured block.

---

## 1. Core Fields

```yaml
quick_capture: true                # marks this block as part of the quick-capture queue
capture_channel: <phone|readest|web|voice|other>
capture_source: <ios_shortcut|readest|browser_extension|mcp_tool|manual|other>
capture_time: <ISO timestamp>      # when it was captured
capture_status: <raw|classified|processed>
auto_summary: <string|null>        # optional short summary
auto_labels: []                    # optional list of rough tags / topics
linked_concepts: []                # optional list of concept ids/names
```

### `capture_status` lifecycle

- `raw` — just landed. No AI work has been done.
- `classified` — AI has safely added a `auto_summary`, `auto_labels`,
  and maybe `linked_concepts` when trivially obvious (e.g., exact concept name match).
- `processed` — you (with AI) have **interactively** decided what to do with it
  (e.g., created Seedlings, linked to Projects/Concepts, or decided it's done).

The sidebar plugin should typically show everything where:

- `quick_capture: true`
- `capture_status != processed`

---

## 2. Additional Fields for Book / Highlight Captures

For sources like Readest or other reading tools, the following fields can also be present:

```yaml
book_title: <string>
book_author: <string>
location: <page or chapter info>
highlight_id: <source-specific id>
entities: []   # optional list of entities from the capture source (topics, people, concepts)
```

These blocks usually live in per-book notes under something like:

- `04_Concepts/Sources/Books/<Author - Title>.md`

---

## 3. Interaction with Other Schemas

Quick-capture metadata can be **combined** with other block schemas:

- A `source_highlight` block can also be a quick capture:
  ```yaml
  block_type: source_highlight
  quick_capture: true
  ...
  ```

- A block might later become tightly linked to a concept, project, or seed,
  but it **does not stop** being a quick capture until you decide it’s processed.

This gives you:

- A **global queue** (via `quick_capture: true`)
- Fine-grained workflows (via `capture_status` and other schemas)
- Location-based context (Inbox vs book vs project)

---

## 4. AI Behavior Boundaries

Your AI assistant should **respect these boundaries**:

- It may:
  - Add `auto_summary`, `auto_labels`, and `linked_concepts` when obvious.
  - Move `capture_status` from `raw` → `classified`.

- It should **not**:
  - Move the block to a new file or notebook without an interactive command.
  - Split the block into Seedlings automatically unless you explicitly request
    processing for that capture.
  - Attach it to Projects or Concept pages in a hidden way; such moves should be
    visible and traceable.

All heavier transformations belong to **explicit “Process this capture”** flows
you trigger in the sidebar or via commands.
