# Quick Add: AI Chat Import, Additional Sources, and Prompt-to-Create

Date: 2025-12-07  
Owner: Codex  
Purpose: Unify Quick Add across chats, web/arXiv/YouTube sources, and prompt-based creation (ADHD-friendly plans, sparks), with clean storage and export.

## Goals
- Single Quick Add pipeline for chats (Claude/ChatGPT/text/URL), web/arXiv/YouTube, and freeform prompt-to-create.
- Persist as ConversationSession (chat) or SourceDocument (content) with entity links.
- Optional quick-create of plans/checklists/sparks from a short prompt.
- Reader/EPUB outputs for all stored items.

## Current State
- Chats: conversation import + reader/EPUB implemented; entities linked.
- Sources: basic import + reader/EPUB implemented; simple fetch (no readability/transcript parsing yet).
- Prompt-to-create: not implemented (placeholder).

## Plan

### 1) Source Expansion & Fetching
- Add MCP-backed fetchers:
  - arXiv: fetch metadata + abstract; attempt PDF text if allowed.
  - YouTube: fetch transcript; fallback to caption APIs.
  - Web: readability extractor to strip boilerplate.
- Normalize to `SourceDocument` with content text, metadata (title, uri, author/channel, published_at), `entity_count`.
- Dedup by URI hash; size caps and chunking for very long inputs.

### 2) Quick Add API Surface
- Unify entrypoints:
  - `POST /conversations/import` (chat) — already present.
  - `POST /sources/import` (web/arXiv/YouTube/text/file) — present, extend with fetchers.
  - `POST /quick-add/prompt` — new: build plan/checklist/spark from a short prompt.
- Payload examples:
  - Chat: `{source: claude|chatgpt|text|url, content, topic?, extract_entities?, create_sparks?}`
  - Source: `{source_type: web|arxiv|youtube|text|file, content (url or text), title?, extract_entities?}`
  - Prompt: `{intent: [plan|checklist|spark|summary], content, duration?, due?, link_source_id?}`

### 3) Prompt-to-Create (ADHD-Friendly)
- Service: `PlanBuilderService`:
  - Outputs: timeboxed steps, micro-start, friction reducers, optional checklist with due/durations.
  - Spark creation: concise insight with tags, linked to source/conversation.
  - Entity linking: reuse ExtractionService on prompt or linked source to add `MENTIONS`.
- Storage: `Plan`/`Spark` nodes with `DERIVES_FROM` edge to ConversationSession/SourceDocument and `MENTIONS` to entities.

### 4) Rendering/Export
- Reader/EPUB already wired; extend to include appendices:
  - Entities appendix when available.
  - Sparks/plans appendix when linked.
- Optional theme toggle for reader view (light/dark).

### 5) Data Model
- `ConversationSession`: id, source, topic/title, imported_at, turn_count, entity_count, transcript, `MENTIONS`.
- `SourceDocument`: id, source_type, title, uri, imported_at, entity_count, content, `MENTIONS`.
- `Plan`/`Spark`: nodes with `DERIVES_FROM` (ConversationSession|SourceDocument), optional `MENTIONS`.

### 6) Testing
- Parser/fetch tests: Claude/ChatGPT exports; arXiv/YouTube/web fixtures.
- Quick Add prompt tests: plan/spark shape, links created, entity mentions recorded.
- Reader/EPUB: presence of title/meta and appendices in outputs.

### 7) Non-Goals (this pass)
- No UI work here; focus on API/services.
- No heavy PDF OCR; only text extraction where available.
- No new embeddings/literature linking changes.

## Sequence
1) Implement MCP-backed fetchers and readability/transcript parsing in SourceService.
2) Add PlanBuilderService + `/quick-add/prompt` to create plans/sparks with links.
3) Extend rendering to add entities/sparks appendices; add reader theme toggle.
4) Expand tests to cover new fetchers and prompt output.***
