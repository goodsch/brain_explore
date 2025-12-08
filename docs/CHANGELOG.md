# IES Changelog

This file contains detailed development history. For current status, see CLAUDE.md.

## December 2025

### Dec 8 - Context Layer MVP + Navigation Foundation + Entity Enrichment
- **Phase 2A: Entity Details Endpoint** — Rich entity data for EntityFocus view
  - `GET /graph/entity/{name}` - Returns entity type, description, related concepts, source books
  - `EntityDetailsResponse` schema with `RelatedEntity` and `SourceBook` types
  - `GraphService.get_entity_details()` queries KG for comprehensive entity data
  - 4 new tests (195 total passing)
- **IES Reader Enhancement** — CFI-aware note capture
  - Note capture now includes CFI range for location context
  - Source Serif Pro font for cleaner reading experience
  - Google Fonts preconnect for faster loading
- **Flow Mode Navigation Foundation (Phase 1)** — Graph traversal with trail tracking
  - Navigation state machine: `FocusState` = 'idle' | 'question' | 'entity' | 'facet'
  - Trail component (breadcrumbs): Context → Question → Entity with click-to-navigate
  - EntityFocus view: entity name, type, description, clickable neighbors, source books
  - Functions: `navigateToEntity()`, `navigateBack()`, `pushTrail()`, `popTrail()`
  - Core Concepts and search results now navigate to entity focus view
  - Sections hide when in entity focus for clean UI
  - Full CSS styling for trail and entity focus components
  - Commit: `58f1c94` (SiYuan), `c63c007` (master)
- **Context Layer Implementation** — Question-driven exploration for Flow Mode
  - Backend: `/context` API with parse, save, search, journey endpoints
  - Types: Context, Question, ContextJourneyEntry schemas
  - Parser: Detects Context Notes from `## Key Questions`, `## Areas of Exploration`, `## Core Concepts` sections
  - Search: Keyword-based entity search using context concepts + question terms
- **Flow Mode Enhancement** — Context Panel UI
  - New `contextBlockId` prop for Context Note detection
  - Key Questions as clickable buttons with search integration
  - Areas of Exploration and Core Concepts display
  - Search results panel with entity navigation
- **Spec Docs** — `redux/` folder with Context + Question Layer specification
  - `IES_Context_and_Question_Layer.md` — Master spec
  - `IES_Flow_Reader_Journey_v2.md` — Behavioral specs
  - `IES_Extraction_Profile_Examples.md` — JSON templates
  - `IES_Integration_Checklist.md` — Implementation roadmap
- **Evolution Plan** — `docs/plans/flow-mode-evolution.md` with 5-phase roadmap
- **Flow Mode Standalone Navigation (Phase 2)** — Search results → entity exploration
  - Fixed plugin → backend connection: `forwardProxy` pattern for Docker CORS bypass
  - Standalone entity panel: click search result → view entity details (type, description, facets, related, sources)
  - Standalone facet panel: click facet → view entities in that facet with back navigation
  - Search results visibility: only shown in `idle` state, hidden during entity/facet view
  - Full navigation flow: search → entity → facet → back to entity → back to search
  - Version indicator (v0.4.0) added for deployment verification

### Dec 7 - IES Reader Wave 2 & Wave 3, MCP Server
- **IES Modern Theme** — Dark-mode-first SiYuan theme (IES Design System v2)
- **IES Reader Wave 2** — Interactive reading features (questions, breadcrumbs, notes capture)
- **IES Reader Wave 3** — Mobile optimization, ingestion queue UI, text selection bar (COMPLETE)
- **IES MCP Server** — Voice-driven ForgeMode sessions via Claude Desktop
- **Conversation Service** — Parse Claude exports, extract insights, store in Neo4j

### Dec 6 - 5-Wave Remediation Sprint Complete
- **Wave 1 (Foundation):** UnifiedGraphClient (1,476 lines), Redis session store, user ID system
- **Wave 2 (Wiring):** Cross-app sync design, journey persistence from both apps
- **Wave 3 (Visibility):** Journey synthesis API, question feedback service
- **Wave 4 (Learning):** Profile learning from sessions, question selection from feedback
- **Wave 5 (Quality):** 63 new tests, 185 total tests passing, 78% coverage
- **IES Reader Wave 1** — Calibre library browser, PWA, IES design system

### Dec 5 - SiYuan & Readest Remediation
- SiYuan plugin remediation complete (interactive questions, cognitive guidance)
- Readest remediation complete (entity click-to-flow, journey breadcrumbs)
- Architecture merge: IES SiYuan Architecture Package + current implementation
- Flow Mode backend implementation (capture → thinking → flow pipeline)

### Dec 4 - Calibre Integration & Entity Overlay
- Calibre integration Phase 2-3 complete (backend APIs, ingestion pipeline)
- Entity overlay feature complete (inline highlighting in Readest)
- Template API and Reframe API complete

### Dec 3 - Phase 2c Planning
- Integration gaps analysis
- Reframe + Template integration design
- ADHD-friendly ontology research

## Status Summary

- **Phase 0:** Configuration stabilization ✅
- **Phase 1:** Core hypothesis validated (11 concepts extracted) ✅
- **Phase 2a:** CLI exploration tool validated ✅
- **Phase 2b:** Visual interfaces (Readest + SiYuan MVP) ✅
- **Phase 2c:** Integration features (~75% complete)
  - Context Layer MVP ✅ (Dec 8)

## Phase 1 Results

10 validation sessions completed. Personal growth framework emerged:
1. Narrow Window of Awareness
2. Acceptance vs. Resignation
3. Grief as Acceptance
4. Metabolization of Difficulty
5. Shame as Non-Acceptance
6. Authentic Presence
7. Nervous System Configurations
8. Capacity and Nervous System Access
9. Superpower in Weakness
10. Window as Condition for Depth

See `/therapy/Track_1_Human_Mind/` for extracted concepts.
