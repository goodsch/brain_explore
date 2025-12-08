# Reader View & EPUB Beautification Plan

Date: 2025-12-07  
Owner: Codex  
Scope: Improve presentation of conversations and source documents in reader view (HTML) and EPUB exports, without adding new fetchers/cleaners.

## Goals
- Polish on-page reader styling (conversations + sources).
- Produce richer EPUBs with chapters, TOC, and appendices (entities/sparks/plans).
- Keep dependencies minimal (stdlib zip for EPUB).

## Plan

### 1) Design & CSS
- Shared CSS (inline for HTML, embedded for EPUB):
  - Body: serif stack (e.g., "Source Serif Pro", Georgia), 70–75ch max-width, 1.6 line-height.
  - Headings: humanist sans (e.g., "Inter", system fallback), consistent margins.
  - Role badges: small-caps, color-coded (user/assistant/system), rounded pills.
  - Blocks: padded “cards” for turns; gentle dividers; improved blockquote and code/pre styles.
  - Links: subtle underline on hover; readable colors.
  - Optional `.theme-dark` variant for reader view.

### 2) Reader View Enhancements
- Group consecutive turns per role (already done) with clearer separation.
- Metadata bar: title/topic, source type, original link, imported timestamp; optional sticky top bar.
- Add light/dark toggle (JS-free small script toggling `.theme-dark`).
- Sources: basic paragraph wrapping on blank lines; preserve headings when present (light heuristic).

### 3) EPUB Structure
- Files:
  - `content.opf` (metadata), `nav.xhtml` (TOC).
  - Chapters:
    1. Intro: title, source, uri, imported_at.
    2. Body: main content (turns or paragraphs) with inline role badges.
    3. Entities appendix (if available): name, type, description when present.
    4. Sparks/plans appendix (optional, if linked/available).
- Embed same base CSS (no external fonts; fallback stacks).
- Add anchors for turns/sections to allow TOC entries (e.g., first N turns).

### 4) Data Wiring
- Conversations: use stored transcript/turns; append entities list if extraction exists.
- Sources: use stored content; append entities list if extraction exists.
- Sparks/plans: placeholder—append if relations exposed; otherwise skip.

### 5) API
- Reuse existing routes: `/conversations/{id}/read|/epub`, `/sources/{id}/read|/epub`.
- Optional reader query param for theme (default light) if desired.

### 6) Testing
- Reader HTML contains title, meta, role badges.
- EPUB zip includes required files (mimetype, container.xml, content.opf, nav.xhtml, chapters).
- Entities appendix present when extraction exists.
- Avoid snapshots; assert key substrings.

### 7) Non-goals (this pass)
- No new readability extraction or YouTube transcript parsing improvements.
- No asset embedding beyond CSS.
- No new dependencies.

## Next Steps
1) Implement CSS/template upgrades for reader view.
2) Implement EPUB chaptering + entities appendix.
3) Add sparks/plans appendix once data is exposed.
