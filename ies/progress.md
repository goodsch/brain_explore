# IES Progress

*Intelligent Exploration System — Backend API + SiYuan Plugin*

**Current Status:** Phase 5 COMPLETE ✅

| Component | Status | Notes |
|-----------|--------|-------|
| Backend | ✅ | 16 REST endpoints, 4,496 lines Python |
| Plugin | ✅ | iOS-capable, 14,092 lines TS/Svelte |
| Tests | ✅ | 61 unit tests passing |
| Documentation | 🟡 | Comprehensive, being cleaned up |

---

## Phase Completion Matrix

| Phase | Status | Description |
|-------|--------|-------------|
| 1. Profile Foundation | ✅ | 6-dimension cognitive profile, Neo4j persistence |
| 2. Backend Core | ✅ | Entity extraction, sessions, Neo4j storage |
| 3. Question Engine | ✅ | State detection, approach selection, 30 templates |
| 4. Session Integration | ✅ | Context loading, enhanced commands, E2E tested |
| 5. SiYuan Plugin | ✅ | Full chat UI with iOS support, E2E tested |
| 6. Generalization | 🔲 | Extract domain code, config system (Future) |

---

## Known Limitations (Honest Assessment)

**Current Therapy-Focus:**
- ✅ EntityDomain enum hardcodes "therapy"
- ✅ Extraction prompts reference therapy concepts
- ✅ DEFAULT_NOTEBOOK hardcoded in backend
- ✅ Plugin hardcodes USER_ID and BACKEND_HOST
- ✅ No configuration system for overrides

**Why This Is OK:**
- System works well for current use case (therapy)
- Clear path to generalization identified (Phase 6)
- Not blocking content development
- Configuration can be added incrementally

---

## Architecture & Key Decisions

### Backend (FastAPI)

**API Endpoints (16 total):**
```
Profile Management
  GET    /profile/{user_id}
  PATCH  /profile/{user_id}
  POST   /profile/{user_id}/dimensions

Session Management
  POST   /session/start
  POST   /session/chat-sync
  POST   /session/chat (SSE streaming)
  POST   /session/end
  GET    /session/context/{user_id}

Question Engine
  POST   /question-engine/detect-state
  POST   /question-engine/select-approach
  GET    /question-engine/templates
  POST   /question-engine/templates/search

Entity Management
  GET    /session/entities/{user_id}
  GET    /session/entities/{user_id}/{entity_name}
  GET    /session/entities/{user_id}/{entity_name}/page-data
```

**Services (14 total):**
- `profile_service.py` — User profile storage/retrieval
- `session_context_service.py` — Load context from Neo4j
- `session_document_service.py` — Create SiYuan docs
- `state_detection_service.py` — Analyze conversation state
- `approach_selection_service.py` — Choose therapeutic approach
- `extraction_service.py` — Claude API for entity extraction
- `entity_storage_service.py` — Persist to Neo4j
- `literature_linking_service.py` — Vector search Qdrant, create GROUNDED_IN edges
- `chat_service.py` — Claude integration for conversation
- `question_templates_service.py` — Template selection & rendering
- `neo4j_client.py` — Direct Neo4j operations
- `siyuan_client.py` — SiYuan API wrapper
- `siyuan_profile_service.py` — User profile in SiYuan

### Plugin (SiYuan)

**Architecture:**
- `index.ts` — Entry point, command registration
- `ies-sidebar-simple.svelte` — Main chat UI (130 lines, optimized for iOS)
- `ies-chat.ts` — Backend client with forwardProxy
- `ies-session.ts` — Svelte store for session state
- `defaultSettings.ts` — Plugin configuration

**iOS Support:**
- Uses `forwardProxy` API for cross-origin requests
- Hardcoded backend host (192.168.86.60) — iOS app proxies through different hostname
- Touch-friendly UI (44px+ buttons, 16px font)
- Non-streaming responses (avoids UI freezing)

### Question Engine

**8 States:** opening, exploring, probing, validating, integrating, clarifying, closing, follow_up

**5 Approaches:** socratic, metaphor_parable, narrative_reflection, structural_reframing, integration

**30 Question Templates:** Grounded in therapy literature, profile-aware selection

---

## Testing

**Unit Tests (61 collected):**
```
test_profile.py
  - Profile retrieval
  - Profile updates
  - Dimension updates

test_session_context.py
  - Context loading from Neo4j
  - Profile integration
  - Fallback handling

test_question_engine.py
  - State detection
  - Approach selection
  - Template retrieval
```

**Test Execution:**
```bash
cd ies/backend
PYTHONPATH=src uv run pytest
```

**Missing (High Priority):**
- [ ] E2E session flow (start → chat → extract → store)
- [ ] Neo4j integration tests (actual database operations)
- [ ] Plugin API contract tests
- [ ] Plugin-backend integration tests

---

## Session Log (Recent)

### 2025-12-01: Multi-Agent Orchestration System

**Accomplished:**
- Designed 8-agent orchestration system for development
- Created agents: context-loader, scribe, reviewer, debugger, backend-ops, entity-manager, session-guide, project-switcher
- Updated SessionStart hook with agent inventory
- Moved discussion from product architecture to "Development Assistance"

**Key Decision:** Agents are Claude Code helpers, not runtime system features

---

### 2025-12-01: Phase 5 Complete - Plugin Fully Working

**Accomplished:**
- Full SiYuan plugin with Socratic dialogue interface
- iOS support via forwardProxy API
- Desktop support (Docker SiYuan)
- E2E tested on iPad + Desktop
- v0.1.4 - Production ready

**What Changed:**
- Rewrote component for iOS compatibility (removed complex stores)
- Added forwardProxy integration (iOS-specific networking)
- Touch-friendly UI (44px buttons, 16px font)
- Hardcoded backend host (192.168.86.60)

---

## Next Steps (Phase 6)

### High Priority (Blocking)
1. **Integration Tests** — E2E coverage for session flow
2. **Configuration System** — Extract hardcoded values
3. **Documentation** — Setup guides, API reference

### Medium Priority
1. **Action Buttons** — Common operations (start, end, etc.)
2. **Entity Visualization** — Relationship graphs
3. **Session Export** — PDF generation

### Future (Post-Generalization)
1. **Remove domain-specific code** — Make truly generic
2. **API Versioning** — Capability discovery
3. **Plugin Settings** — Backend URL configuration
4. **Streaming Responses** — Enable when iOS support better

---

## Resources

- **Backend:** `/home/chris/dev/projects/codex/brain_explore/ies/backend/`
- **Plugin:** `/home/chris/dev/projects/codex/brain_explore/ies/plugin/`
- **Design Docs:** `/home/chris/dev/projects/codex/brain_explore/docs/plans/`
- **SiYuan Notebook:** "Intelligent Exploration System"

---

## Key Metrics

- **Backend Code:** 4,496 lines Python
- **Plugin Code:** 14,092 lines TS/Svelte
- **Unit Tests:** 61 passing
- **API Endpoints:** 16
- **Services:** 14
- **Question States:** 8
- **Question Approaches:** 5
- **Question Templates:** 30
- **Neo4j Nodes:** 48,987 (from 63 books)
- **Qdrant Chunks:** 27,523
- **API Response Time:** <1s (non-streaming JSON)

---

## Development Commands

```bash
# Start backend
cd ies/backend && IES_NEO4J_PASSWORD=brainexplore uv run uvicorn ies_backend.main:app --host 0.0.0.0 --port 8081

# Run tests
cd ies/backend && PYTHONPATH=src uv run pytest

# Build plugin
cd ies/plugin && npm install && npm run build

# Start Docker services
docker compose up -d

# Check backend health
curl http://localhost:8081/docs
```

---

## Architecture Evolution

**Current (Therapy-Focused):**
- ✅ Domain-specific code in IES
- ✅ Hardcoded values for chris + therapy
- ✅ Works great for current use case

**Future (Generic Framework):**
- 🔲 Extract domain code to Framework layer
- 🔲 Create configuration system
- 🔲 Define interface contracts
- 🔲 Support multiple implementations
- 🔲 API versioning

This is intentional and planned. See `/docs/plans/2025-12-02-documentation-cleanup-plan.md` for details.
