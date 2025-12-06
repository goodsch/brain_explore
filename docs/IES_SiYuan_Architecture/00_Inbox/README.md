# 00 Inbox

Ephemeral capture: raw, unprocessed, unsorted notes.

This folder is the primary landing zone for **generic quick captures** that
arrive via HTTP POST, iOS Shortcuts, MCP tools, or manual entry.

Recommended usage:

- Create one file per day, e.g. `QuickCapture_YYYY-MM-DD.md`.
- Each quick capture is a single block with **quick_capture metadata** in
  a small YAML header (see `/07_System/Quick_Capture_Schema.md`).
- Captures are *not* heavily processed or moved automatically.
- Instead, they appear in a **sidebar queue** (plugin) that filters for
  `quick_capture: true` and `capture_status != processed`.

Your AI assistant is allowed to:

- Add light classification (`auto_summary`, `auto_labels`, `linked_concepts`)
- Update `capture_status` from `raw` → `classified`
- Leave all heavy processing (splitting into Seedlings, linking to Projects,
  updating Concepts) to **interactive sessions** you initiate.
