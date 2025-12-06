# Block Schemas for IES × SiYuan

These schemas describe the main *logical* block types used in this architecture.
In SiYuan, these can map to:

- Custom attributes
- Data attributes
- Block templates
- Naming conventions and tags

You can adapt the exact storage mechanism, but the *shape* and *fields*
should remain consistent.

---

## 0. Quick-Capture Metadata (Common Layer)

Any block can additionally carry **quick-capture** metadata (see
`/07_System/Quick_Capture_Schema.md` for full details):

```yaml
quick_capture: true|false
capture_channel: <phone|readest|web|voice|other>
capture_source: <ios_shortcut|readest|browser_extension|mcp_tool|manual|other>
capture_time: <ISO timestamp>
capture_status: <raw|classified|processed>
auto_summary: <string|null>
auto_labels: []
linked_concepts: []
```

For reading tools (Readest, etc.) you may also see:

```yaml
book_title: <string>
book_author: <string>
location: <page/chapter>
highlight_id: <string>
entities: []
```

This metadata does **not** replace block types below; it *augments* them so
that a block can be both, e.g., a `source_highlight` and a quick capture.

---

## 1. `seed-block`

**Purpose:** Represent a single atomic idea, question, observation, or schema fragment.

**Constraints:**
- Exactly one idea per block.
- Must be readable in isolation.

**Suggested fields / attributes:**

- `block_type`: `"seed"`
- `idea_type`: `"question" | "insight" | "observation" | "moment" | "schema" | "contradiction" | "what_if" | "other"`
- `domain`: arbitrary string (`"ADHD"`, `"Therapy"`, `"Systems"`, `"Self"`, etc.)
- `source`: `"inbox" | "dialogue" | "project" | "external" | ...`
- `clarity`: `"fuzzy" | "partial" | "clear"`
- `confidence`: `"low" | "medium" | "high"`
- `created_at`: ISO timestamp
- `last_touched_at`: ISO timestamp
- `related_concepts`: list of concept IDs or names
- `tags`: free-form list

You may also attach quick-capture fields when a seed originated
directly from a quick capture.

---

## 2. `shaping-block` (Dialogue / Shaping)

**Purpose:** Capture segments of a Dialogue session where understanding is shaped.

**Suggested fields:**

- `block_type`: `"shaping"`
- `session_id`: stable ID for a dialogue session
- `speaker`: `"chris" | "ai"`
- `phase`: `"exploration" | "challenge" | "synthesis" | "meta"`
- `related_seedlings`: list of seed IDs or links
- `created_at`
- `last_touched_at`

---

## 3. `map-block`

**Purpose:** Represent a map (concept map, schema, timeline, system view).

**Characteristics:**
- Usually contains structured content like:
  - Mermaid diagrams
  - Nested lists
  - Tables
  - Mindmap-like structures

**Suggested fields:**

- `block_type`: `"map"`
- `map_type`: `"concept_cluster" | "timeline" | "system" | "schema" | "perspective" | "other"`
- `focus`: ID or name of focal concept/question
- `related_concepts`: list
- `related_seedlings`: list
- `entry_points`: list of recommended starting nodes
- `created_at`
- `last_touched_at`

---

## 4. `concept-block`

**Purpose:** Represent the canonical definition and understanding of a concept.

Usually implemented as the main body of a concept page in `04_Concepts`.

**Suggested fields:**

- `block_type`: `"concept"`
- `concept_id`: stable identifier (slug)
- `concept_name`: human-readable name
- `domain`
- `status`: `"active" | "draft" | "deprecated"`
- `created_at`
- `last_touched_at`
- `version`: integer or semantic version string

---

## 5. `decision-block`

**Purpose:** Represent a single decision in a project.

**Suggested fields:**

- `block_type`: `"decision"`
- `project_id`: project name or ID
- `status`: `"pending" | "accepted" | "rejected" | "revisited"`
- `rationale`: short string summary
- `created_at`
- `decided_at` (optional)
- `related_maps`: list of map IDs/links
- `related_concepts`: list

---

## 6. `log-entry-block`

**Purpose:** Track actions or events in a project or general daily log.

**Suggested fields:**

- `block_type`: `"log_entry"`
- `context`: `"project" | "system" | "personal" | ...`
- `project_id` (optional)
- `timestamp`
- `summary`
- `related_blocks`: list

---

## 7. Daily Landing Page Structures

Daily / session landing pages are composed of multiple blocks, but you may also
define a higher-level “page schema” for them (see Template files).

---

You can extend these schemas as needed (e.g., add `energy_level`, `mood`, etc.),
but keep the **core types stable** so that all automations and MCP tools can rely
on them.
