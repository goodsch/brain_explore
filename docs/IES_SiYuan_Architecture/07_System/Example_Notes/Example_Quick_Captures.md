# Example: Quick Captures

These examples show how quick-capture metadata can be attached to blocks
in different contexts.

---

## 1. Phone Quick Capture in 00_Inbox

```markdown
## qc-2025-12-05-001

```yaml
quick_capture: true
capture_channel: phone
capture_source: ios_shortcut
capture_time: 2025-12-05T11:02:33-05:00
capture_status: raw
auto_summary: null
auto_labels: []
linked_concepts: []
```

I keep thinking about phenomenology in terms of “what actually shows up in experience”
vs “what I think I should be feeling.”
```

After light background processing, the AI might update to:

```yaml
quick_capture: true
capture_channel: phone
capture_source: ios_shortcut
capture_time: 2025-12-05T11:02:33-05:00
capture_status: classified
auto_summary: "Reflection on phenomenology as focus on 'what shows up' vs 'what should be felt'."
auto_labels: ["phenomenology", "self", "experience"]
linked_concepts: ["phenomenology"]
```

---

## 2. Readest Highlight Quick Capture in a Book Note

```markdown
### highlight-readest-abc-123

```yaml
block_type: source_highlight
quick_capture: true
capture_channel: readest
capture_source: readest
capture_time: 2025-12-05T11:05:12-05:00
capture_status: raw
book_title: "Ideas Pertaining to a Pure Phenomenology and to a Phenomenological Philosophy"
book_author: "Edmund Husserl"
location: "Chapter 2, §15"
highlight_id: "readest-abc-123"
entities: ["phenomenology", "intentionality", "consciousness"]
auto_summary: null
auto_labels: []
linked_concepts: []
```

> Phenomenology is not a theory about the world, but a method of carefully describing
> the structures of experience as they are given.
```

After background classification:

```yaml
capture_status: classified
auto_summary: "Defines phenomenology as a method for describing structures of experience."
auto_labels: ["phenomenology", "methodology", "experience"]
linked_concepts: ["phenomenology"]
```

And after an interactive processing session, if you decide to promote it:

- A `seed-block` is created in `01_Seedlings/Schemas`.
- The original highlight stays where it is, but:
  - `capture_status: processed`
  - Gains a link to the new seed.

---

These examples are meant as a reference for how your MCP / AI assistant
should shape and evolve quick-capture blocks over time.
