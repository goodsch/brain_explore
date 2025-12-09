# Brain Explore / Intelligent Exploration System (IES) - Development Status

**Current Date:** December 8, 2025
**Phase:** Phase 2c (Evidence & Enrichment) - ~75% Complete

## 1. Project Overview
The Intelligent Exploration System (IES) is a four-layer system for AI-partnered knowledge exploration, designed to help users think with an AI partner that adapts to their cognitive style.
- **Layer 1: Knowledge Graph** (Neo4j + Qdrant) - Ingests 179+ books, extracts entities (~300 chunks currently).
- **Layer 2: Backend APIs** (FastAPI) - Graph, Session, Journey, Profile services.
- **Layer 3: SiYuan Plugin** - "Inbox" (formerly Capture), Flow Mode, Forge Mode.
- **Layer 4: IES Reader** (Readest fork) - E-book reader with entity overlay.

## 2. Recent Accomplishments (Dec 7 - Dec 8)

### Documentation & Context Optimization (Dec 7)
*   **Streamlined CLAUDE.md**: Reduced from 1757 to ~119 lines to save context tokens. Detailed history moved to `docs/CHANGELOG.md`.
*   **Serena Memory Cleanup**: Consolidated 8 memories into 4 active ones (`ies_architecture`, `true_vision`, `books-to-download`, `configuration_impact`).

### Backend Infrastructure (Dec 7)
*   **Connection Fixes**: Backend now binds to `0.0.0.0` (was localhost) to allow Docker container access.
*   **IES MCP Server**: Created a stateless MCP wrapper around the backend to enable voice-driven ForgeMode sessions via Claude Desktop/Mobile.
*   **Source Tools**: Integrated Anna's Archive and Arxiv search/download tools into the IES MCP server.
*   **Conversation Pipeline**: Implemented `ConversationParser` and `ConversationService` to ingest external AI chat exports (Claude/ChatGPT) into the graph.

### Frontend / UI (Dec 7)
*   **Theme Fixes**: Fixed "IES Modern" SiYuan theme issues (file permissions 600->644, `theme.json` format).
*   **Plugin Refactor**: Renamed "Quick Capture" to "Inbox" throughout the UI.
*   **New Features**: Designed "Quick Plan" (one-shot planning) and "Transcript Upload" for the SiYuan plugin.
*   **Design System**: Established "IES Design System v2" (Modern Information Space: dark mode default, entity colors as accents).

### Sprint 2: Evidence (Dec 8)
*   **Backend Evidence Endpoint**: Implemented `GET /graph/entity/{name}/evidence` returning both high-confidence chunks and book-level mentions.
*   **Graph Service**: Added `get_entity_evidence()` method and `EvidencePassage` schema.
*   **Testing**: Added 6 new tests for evidence functionality (Total: 215 passing tests).
*   **Research**: Downloaded "Wave 3" books (Cognitive Architecture & Metacognition) and papers.
*   **Reader Integration (In Progress)**:
    *   Added `EvidencePassage` to `flowModeStore.ts`.
    *   Added `getEntityEvidence()` to `graphClient.ts`.
    *   Created `EvidenceSection.tsx` component.
    *   *Pending*: Wire up evidence fetching in `useFlowEntity` hook and render in `FlowPanel`.

## 3. Current Status

### Backend (`ies/backend`)
*   **Status**: Healthy, running on port 8081.
*   **Key Components**: 
    *   `ConversationService` (New): Fully wired for chat imports.
    *   `GraphService`: Enhanced with Evidence support.
*   **Data**: ~1400 Book mentions, but only ~10 actual text chunks extracted. Needs batch extraction job.

### SiYuan Plugin (`.worktrees/siyuan`)
*   **Status**: Installed and working.
*   **UI**: "Inbox" rename complete. "IES Modern" theme fixed.
*   **Pending**: Implementation of "Quick Plan" and "Transcript Upload" UIs.

### IES Reader (`.worktrees/readest`)
*   **Status**: Running on port 5173. Proxy configured for `/conversations`.
*   **In Progress**: Integration of Evidence panel into Flow Mode.

## 4. Immediate To-Do List (Sprint 2 Continuation)

1.  **Complete Reader Evidence Integration**:
    *   Update `useFlowEntity` hook to fetch evidence.
    *   Add `EvidenceSection` to `FlowPanel.tsx` render loop.
    *   Verify "Open in Reader" functionality for evidence snippets.

2.  **Build Chunk Extraction Pipeline**:
    *   Design/Implement batch job to populate `Chunk` nodes from existing Books (currently sparse).
    *   Create `MENTIONS` relationships between Chunks and Entities in Neo4j.

3.  **SiYuan Plugin Features**:
    *   Implement "Quick Plan" modal and backend integration.
    *   Implement "Transcript Upload" UI (Drag & drop markdown files).

4.  **Verify Ingestion Queue**:
    *   Test the refactored `books.py` queue endpoints.

## 5. Operational Notes
*   **Context**: Use `docs/CHANGELOG.md` for history and `mcp__serena__read_memory` for architecture details. Keep `CLAUDE.md` minimal.
*   **Docker**: SiYuan runs in Docker (`brain_explore_siyuan`). Plugins live in `data/siyuan/workspace/data/plugins/`. Themes in `conf/appearance/themes/`.
*   **Permissions**: Watch out for file permissions when copying to Docker volumes (ensure 644 for files).
*   **Ports**: 
    *   Backend: 8081
    *   Reader: 5173
    *   SiYuan: 6806
    *   Qdrant: 6333
    *   Neo4j: 7474/7687
