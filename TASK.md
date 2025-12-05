# SiYuan Plugin Worktree Task Briefing

**Branch:** `feature/siyuan-evolution`
**Phase:** 3 - SiYuan Plugin Evolution
**Focus:** Layer 3 - Processing Hub (Dashboard, Thinking, Capture)

---

## What This Worktree Is For

This worktree evolves the **SiYuan plugin** from its current state into a processing hub with three main features:

1. **Dashboard** - Central navigation for explorations, concepts, and capture queue
2. **Structured Thinking** - Evolution of current Forge mode with 5 thinking modes
3. **Quick Capture** - Phone-friendly thought capture with intelligent routing

---

## Current Plugin State

The existing plugin (`ies/plugin/`) has:
- Forge mode (basic structured dialogue)
- Flow mode (graph exploration with relationship display)
- Profile management basics
- Backend API integration

**What's Working:**
- Graph exploration UI
- Dialogue sessions
- Entity search
- Relationship visualization

---

## Goals

### Dashboard View
Central hub replacing scattered entry points:
- Recent explorations list
- Active concepts display
- Quick Capture queue status
- Entry points: Explore Concept, Structured Thinking, Read

### Structured Thinking Mode
Evolve Forge into 5 specialized modes:

| Mode | Purpose | AI Behavior |
|------|---------|-------------|
| Learning | Understand new concept | Socratic questioning |
| Articulating | Clarify vague intuition | Mirroring, precise language |
| Planning | Develop action strategy | Goal clarification |
| Ideating | Generate creative options | Divergent prompts |
| Self-Reflecting | Personal insight | Phenomenological questions |

**Interface:** Split view - conversation (left) + live note preview (right)

### Quick Capture Queue
- Accept unstructured text, voice notes, images, links
- AI extracts entities and suggests placements
- Route to existing notes, new concepts, or journeys

---

## Architecture Context

```
Layer 4: READEST              - Reading interface (separate worktree)
Layer 3: SIYUAN PLUGIN (THIS) - Processing hub
Layer 2: BACKEND              - API with new capture/journey endpoints
Layer 1: KNOWLEDGE GRAPH      - Neo4j with 50k+ entities
```

---

## Available Backend Endpoints

### Session API (existing)
- `POST /session` - Start structured thinking session
- `POST /session/{id}/message` - Send message in session

### Capture API (new - just created)
- `POST /capture/process` - Process captured content
  - Extracts entities
  - Suggests placements (existing note, new concept, journey)
  - Returns confidence scores

### Journey API (new - just created)
- `GET /journeys/user/{user_id}` - List journeys for dashboard

### Profile API (existing)
- `GET /profile/{user_id}` - Get user profile
- `PUT /profile/{user_id}` - Update profile

### Graph API (existing)
- `GET /graph/search?query={q}` - Search entities
- `GET /graph/entity/{id}` - Get entity details

---

## Key Components to Build/Evolve

### Dashboard.svelte (new)
```
┌─────────────────────────────────────────────────────────────────┐
│  DASHBOARD                                          [Profile]   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Recent         │  │  Active         │  │  Quick          │ │
│  │  Explorations   │  │  Concepts       │  │  Capture Queue  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  [Explore Concept]  [Structured Thinking]  [Read]        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### StructuredThinking.svelte (evolve from Forge)
- Mode selector (Learning, Articulating, Planning, Ideating, Reflecting)
- Split view: conversation + live note preview
- Mode-specific AI prompting
- Note auto-generation from conversation

### QuickCapture.svelte (new)
- Input field for text/voice/link
- Processing status display
- Placement suggestions with confidence
- One-click routing to destination

---

## Current Status

**Commit:** `242ae72` - Concept Extraction Flow (Virtuous Cycle) complete

**Phase:** Layer 3 Processing Hub IMPLEMENTED + REMEDIATION COMPLETE

### Critical Analysis Remediation (Dec 5)

A four-agent pressure test (CRITICAL-ANALYSIS-2025-12-05.md) identified gaps between documented principles and implementation. **Remediation audit complete - most items already fixed:**

| Phase | Item | Status |
|-------|------|--------|
| 1.1 | Make Questions Interactive | ✅ COMPLETE - `handleQuestionResponse()` creates full dialogue loop |
| 1.2 | Activate Question Classes | ✅ COMPLETE - `QUESTION_CLASS_HINTS` provides cognitive guidance |
| 1.3 | Remove Domain Hardcoding | ✅ COMPLETE - Configurable notebook preferences |
| 1.4 | Add Backend Health Check | ✅ COMPLETE - Dashboard shows connection status |
| 2.1 | Mode-Specific UI | DEFERRED - Single unified panel works well |
| 2.2 | Concept Extraction Flow | ✅ COMPLETE - `ConceptExtractor.svelte` with graph formalization |
| 2.3 | Energy-Based Navigation | ✅ COMPLETE - Dashboard energy/resonance filters |
| 3.x | Design Consolidation | OPTIONAL - CSS already comprehensive |
| 4.x | Minor Bug Fixes | ✅ VERIFIED - Error handling patterns correct |

**Key Implementations Verified:**
- `ForgeMode.svelte` lines 993-1075: Full question-response dialogue loop
- `ForgeMode.svelte` lines 1290-1360: Question hints, response starters, history
- `Dashboard.svelte` lines 267-271: Energy/resonance filter endpoints
- `QuickCapture.svelte` lines 149-239: Proper try/catch/finally error handling
- `siyuan-structure.ts` lines 218-248: Notebook validation with meaningful errors

---

## Deliverables Checklist

### Dashboard (Complete)
- [x] Dashboard component with navigation (v0.3.0)
- [x] Recent explorations list (from journeys API)
- [x] Knowledge graph statistics display
- [x] Entry point buttons for three modes

### Structured Thinking (Complete)
- [x] Structured Thinking mode selector (ForgeMode.svelte)
- [x] 5 thinking modes implemented (Learning, Articulating, Planning, Ideating, Reflecting)
- [x] Mode-specific AI behaviors configured
- [x] Backend session API integration
- [ ] Split view for Structured Thinking (conversation + note preview) - DEFERRED (works with single view)

### Quick Capture (Complete)
- [x] Quick Capture input and queue (QuickCapture.svelte)
- [x] Integrate capture processing API
- [x] Placement suggestion UI
- [x] Entity extraction display

### Graph Exploration (Complete)
- [x] FlowMode with entity search and navigation
- [x] Grouped relationship display by type
- [x] Thinking partner questions integration
- [x] Journey breadcrumb tracking

### Profile Management (Existing)
- [x] Profile management basics (already present from earlier work)

---

## Next Steps

SiYuan plugin Phase 3 is **COMPLETE** with remediation verified. The plugin now delivers on core principles:

- ✅ Thinking partnership (interactive questions with dialogue loop)
- ✅ Question class guidance (cognitive hints, response starters)
- ✅ ADHD-friendly navigation (energy/resonance filters)
- ✅ Virtuous cycle (concept extraction → graph formalization)

**Recommended next actions:**

1. **Readest Pressure Test** - Apply same four-agent analysis to Layer 4 (per PRESSURE-TEST-PLAN.md)
2. **End-to-End Testing** - Test complete flow: Reading → Capture → Thinking → Concept Extraction → Graph
3. **User Testing** - Get feedback on the complete four-layer system
4. **iOS Shortcut Setup** - Configure Quick Capture shortcut (see `docs/plans/2025-12-03-quick-capture-design.md`)

**Deferred:**
- Split view for Structured Thinking (single panel works well)
- Mode-specific UI differentiation (unified design is clean)

---

## File Structure

```
ies/plugin/src/
├── components/
│   ├── Dashboard.svelte        # New - central hub
│   ├── StructuredThinking.svelte  # Evolve from ForgeSession
│   ├── QuickCapture.svelte     # New - capture queue
│   ├── ProfileManager.svelte   # New/enhanced
│   └── (existing components)
├── stores/
│   └── modeContext.ts          # Cross-component state
└── api/
    └── (existing API clients)
```

---

## Design Document Reference

Full design details: `docs/plans/2025-12-03-integrated-reading-knowledge-system.md`

Key sections:
- Section 3: SiYuan Plugin Evolution (Layer 3)
- Section 3.1: Dashboard View
- Section 3.2: Structured Thinking Mode
- Section 3.3: Quick Capture Queue
- Section 7.2: SiYuan Plugin ↔ Backend API contracts

---

## Development Commands

```bash
cd ies/plugin
npm install                # Install dependencies
npm run dev                # Development mode with hot reload
npm run build              # Production build
```

---

## Backend Health Check

Before starting, verify backend is running:
```bash
curl http://localhost:8081/health
# Should return: {"status": "healthy"}
```

---

## Integration Notes

- This worktree focuses on the SiYuan plugin only
- Readest work happens in `.worktrees/readest`
- Backend is on main branch - pull updates as needed
- Bidirectional sync with Readest is Phase 4 (later)
- Current Forge mode should be preserved as base for Structured Thinking
