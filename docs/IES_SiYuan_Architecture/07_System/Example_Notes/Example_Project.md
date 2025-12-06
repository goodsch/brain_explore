# Example: Project – IES × SiYuan Integration

This example shows how a project can be structured and connected into the
rest of the system.

---

## Goals (Example)

- Implement the opinionated IES × SiYuan architecture.
- Make it trivial for future-Chris to explore, not configure.
- Allow AI assistants (via MCP or similar) to operate safely and predictably.

---

## Questions (Example)

- What is the simplest way to mirror these Markdown structures into SiYuan?
- How should block attributes be stored (tags, attributes, or external index)?
- Which health checks should run automatically vs. on-demand?

---

## Plan (Example)

- Phase 1: Mirror folder structure into SiYuan.
- Phase 2: Implement templates and attributes.
- Phase 3: Wire MCP tools and automations.
- Phase 4: Iterate based on real-world use.

---

## Status (Example)

- Architecture defined (this package).
- Next step:
  - Use MCP to create notebooks and templates in a live SiYuan instance.
- Risks:
  - Overcomplicating metadata.
  - Under-specifying AI behaviors.

---

## Logs (Example Snippets)

- `2025-12-05` — Generated initial Markdown package.
- `2025-12-06` — Mirrored notebooks into SiYuan via assistant.
- `2025-12-07` — Ran first Dialogue + Flow test using real captures.

---

## Decisions (Example)

- **D1: Markdown-first**
  - Status: Accepted
  - Rationale: Easier to version control and reason about.
  - Implication: Use Markdown as the primary spec, and treat SiYuan as a
    powerful front-end for it.
