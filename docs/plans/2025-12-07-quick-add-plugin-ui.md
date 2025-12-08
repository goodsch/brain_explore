# Quick Add Plugin UI Integration Plan

Date: 2025-12-07  
Owner: Codex  
Scope: Surface Quick Add prompt-to-create, chat/source imports, and reader/EPUB entry points in the plugin/reader UI.

## Goals
- Single “Quick Add” UI for chats, URLs (web/YouTube/arXiv), plain text, and prompt-based Plan/Checklist/Spark creation.
- Show generated artifacts (plan/checklist/spark) inline; expose reader/EPUB links for imports.
- Pass context (source_id) when invoked from reader selections/books.

## UX Outline
- Entry points: 
  - Sidebar/FAB “Quick Add”
  - Reader capture drawer tab “Quick Add”
- Form fields:
  - Source type dropdown: Chat | URL/Web | YouTube | arXiv | Text | Prompt
  - Textarea: paste content or prompt
  - Intent pills (for Prompt): Plan, Checklist, Spark (multi-select), optional Due/Duration
  - Toggle: Run extraction (default on)
  - Context: hidden `source_id` when launched from a book/selection
- Actions:
  - For Prompt: POST `/quick-add/prompt`
  - For Chat: POST `/conversations/import`
  - For Source: POST `/sources/import`
- Results panel:
  - Plan card: micro-start, timeboxed steps, friction reducers, done criteria, total time
  - Checklist card: items with checkboxes
  - Spark chip: one-liner + tags
  - Entities: pill list; clicking opens graph/entity overlay
  - Links: “Reader view” and “Download EPUB” (conversations/sources)

## API Contracts (already implemented)
- `/quick-add/prompt` → BuildPlanResponse {plan?, checklist?, spark?, extraction}
- `/conversations/import` → ConversationImportResponse {session, extraction}
- `/sources/import` → SourceImportResponse {document, extraction}
- Reader/EPUB: `/conversations/{id}/read|/epub`, `/sources/{id}/read|/epub`

## UI Components
- QuickAddForm: source selector, textarea, intent pills, toggles, submit
- ResultCards:
  - PlanCard (micro-start + steps)
  - ChecklistCard (items)
  - SparkChip
  - EntitiesList (clickable)
  - LinkBar (reader/EPUB)
- State: loading/error banners; fallback hint when LLM unavailable

## Data Flow
- On submit:
  - Determine route (prompt vs import)
  - POST with context (source_id if available)
  - Render results; store last response for copy/export
- Entity clicks: open graph client/entity overlay
- Theme: respect app theme; allow local toggle for preview (switch data-theme attr)

## Error/Latency Handling
- Show spinner; timeout fallback to local plan/checklist messaging (already in service)
- Display error banner with retry; keep typed content intact

## Next Steps
1) Build QuickAddForm + ResultCards in plugin/reader UI.
2) Wire API calls to existing endpoints; add context passing from reader selection.
3) Add reader/EPUB links in result cards.
4) Add minimal tests/storybook knobs (if present) for rendering states.
