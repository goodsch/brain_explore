<!-- MANUAL -->
# brain_explore — Intelligent Exploration System

*Domain-agnostic tool for structured thinking and knowledge exploration*

> **Ground Truth:** `docs/IES-SYSTEM-DESIGN.md`
>
> **Document Hierarchy:**
> 1. `docs/IES-SYSTEM-DESIGN.md` — WHY & HOW (cognitive architecture, operating model)
> 2. `docs/UNIFIED-PROJECT-SPEC-2025-12-09.md` — What's active vs archived
> 3. `docs/ARCHITECTURE-AND-INTERACTIONS.md` — Technical APIs and data flows
> 4. `docs/GAP-ANALYSIS-2025-12-09.md` — Implementation status
> 5. `docs/SIYUAN-FOLDER-STRUCTURE.md` — SiYuan notebook organization
>
> **TL;DR:** IES Reader is ACTIVE. Readest is ARCHIVED.

## Four-Layer System

| Layer | Component | Purpose |
|-------|-----------|---------|
| 1 | Knowledge Graph | 179 books → entities/relationships (Neo4j) |
| 2 | Backend APIs | FastAPI, 411 tests passing |
| 3 | SiYuan Plugin | Dashboard, 5 thinking modes, flow exploration |
| 4 | IES Reader | E-book reader with entity overlay and flow panel |

## Current Sprint (Dec 9, 2025)

**Phase 1 Design System: In Progress**

✅ Completed (Phase 2c - 100%):
- Cross-app session sync (IES Reader ↔ SiYuan)
- Pass 2/3 enrichment pipeline (relationships + LLM)
- Extraction Engine with UI integration
- All 5 thinking templates
- Highlight sync with block attributes
- P1/P2 Reader integration (What's New, Timeline)
- Redis migration for session persistence
- Centralized journey event logging (JourneyLogger)
- Journey continuity API (`/session-state/continue`)
- Journey pattern analysis (entity clustering, path detection, recommendations)

✅ Completed (Phase 1 - Design System Foundation):
- Design tokens package with 158 tokens (colors, spacing, typography, motion)
- Storybook v8.5 with a11y addon
- Accessibility: prefers-reduced-motion support (CSS + React hook)
- WCAG contrast fixes in SiYuan plugin

**Next:** Component library in Storybook + visual regression testing

## Quick Start

```bash
# Infrastructure
docker compose up -d

# Backend (port 8081)
cd ies/backend && uv run uvicorn ies_backend.main:app --reload --port 8081

# IES Reader (port 5173)
cd ies/reader && pnpm dev

# SiYuan Plugin (in worktree)
cd .worktrees/siyuan/ies/plugin && pnpm dev
```

## Project Structure

```
brain_explore/
├── ies/backend/          # FastAPI (Layer 2)
├── ies/design-tokens/    # Design tokens package (Style Dictionary)
├── ies/reader/           # IES Reader (Layer 4)
├── library/graph/        # Neo4j client, entity extraction
├── .worktrees/siyuan/    # SiYuan plugin (Layer 3)
└── docs/                 # Documentation
```

## Key Commands

```bash
# Tests
cd ies/backend && uv run pytest

# Docker
docker compose up -d      # Start
docker compose ps         # Status

# Git
git log --oneline -10     # Recent commits
```

## Worktrees

| Location | Branch | Purpose |
|----------|--------|---------|
| `.` (root) | `master` | Backend APIs only |
| `.worktrees/siyuan/` | `feature/siyuan-evolution` | SiYuan plugin |
| `.worktrees/ies-reader/` | `feature/ies-reader-enhancement` | IES Reader |

**Archived:** `.worktrees/readest/` — DO NOT USE

## Critical Constraints

**DO NOT:**
- Work on features in master branch (use worktrees)
- Skip tests before committing
- Reference Readest in new code (use IES Reader)

**ALWAYS:**
- Check git status before starting
- Run tests after changes
- Use Serena symbolic tools for code exploration
- Check ground truth docs for architecture questions

## On-Demand Resources

For detailed implementation info, use these resources instead of expecting everything here:

| Need | Resource |
|------|----------|
| API endpoints | `docs/ARCHITECTURE-AND-INTERACTIONS.md` |
| Implementation status | `docs/GAP-ANALYSIS-2025-12-09.md` (100% complete, Phase 2c done) |
| **SiYuan folder structure** | `docs/SIYUAN-FOLDER-STRUCTURE.md` (10 top folders, seedlings/sessions hierarchy) |
| **User Journey Analysis** | `docs/USER-JOURNEY-ANALYSIS-2025-12-09.md` (67 issues: 18 critical, 24 high) |
| **Cross-App Journey Analysis** | `docs/CROSS-APP-JOURNEY-ANALYSIS-2025-12-09.md` (5 journey scenarios, state transfer matrix) |
| **UX/UI Design Package** | `docs/design/00-design-package-index.md` (323KB, 8 complete docs) |
| **Design Playground** | `docs/design/interactive-design-playground.html` (6 themes, live component preview) |
| **Aesthetic Options** | `docs/design/08-aesthetic-directions-and-component-systems.md` (53KB, 6 themes + 4 component systems) |
| **UX Issues** | `docs/UX-CRITIQUE-2025-12-09.md` (30 issues, severity-rated) |
| **Flow Mode Redesign** | `docs/design/06-flow-mode-blueprint.md` (Graph viz specification) |
| **Design System** | `docs/design/04-design-language-guide.md` (Colors, typography, motion) |
| **Implementation Plan** | `docs/design/07-implementation-roadmap.md` (12-week roadmap, 480h) |
| **Accessibility (Reduced Motion)** | `docs/ACCESSIBILITY-REDUCED-MOTION.md` (prefers-reduced-motion implementation guide) |
| **WCAG Contrast Audit** | `docs/WCAG-CONTRAST-AUDIT-2025-12-09.md` (Dec 9 audit, 100% WCAG AA compliance) |
| Calibre integration | `docs/plans/2025-12-04-calibre-integration-design.md` |
| Pass 2/3 pipeline | `docs/plans/2025-12-09-pass-2-relationship-extraction.md` |
| Session sync design | `docs/plans/2025-12-09-context-sync-design.md` |
| Changelog | `docs/CHANGELOG.md` |

## Serena Memories

Query on-demand with `mcp__serena__read_memory`:

| Memory | Content |
|--------|---------|
| `project-status-dec9` | Current status, document hierarchy |
| `ies_architecture` | Technical implementation details |
| `deprecated-readest` | Warning about archived Readest |

## Working Style

Claude acts as project manager. Identify optimal next action and proceed — don't ask what to work on. User will redirect if needed.
<!-- END MANUAL -->

<!-- AUTO-MANAGED: build-commands -->
## Build Commands

| Component | Command |
|-----------|---------|
| Backend | `cd ies/backend && uv run uvicorn ies_backend.main:app --reload --port 8081` |
| Backend Tests | `cd ies/backend && uv run pytest` |
| IES Reader | `cd ies/reader && pnpm dev` |
| Storybook | `cd ies/reader && pnpm storybook` (port 6006) |
| Design Tokens | `cd ies/design-tokens && npm run build` |
| Docker | `docker compose up -d` |
| SiYuan Plugin | `cd .worktrees/siyuan/ies/plugin && pnpm dev` |
<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: architecture -->
## Architecture Quick Reference

> **Full details:** See `docs/ARCHITECTURE-AND-INTERACTIONS.md`

**Backend API Routes** (registered in `main.py`):

| Route | Purpose |
|-------|---------|
| `/context` | Context CRUD, parsing, search |
| `/questions` | Question CRUD, relevant passages |
| `/graph` | Entity search, facets, relationships |
| `/session-state` | Cross-app sync (IES Reader ↔ SiYuan) with journey continuity |
| `/highlights` | Highlight CRUD with SiYuan sync |
| `/visits` | "What's new" tracking |
| `/journey-timeline` | Exploration history |
| `/journey-patterns` | Pattern analysis, entity clustering, recommendations |
| `/extraction` | Context-aware entity extraction |
| `/books` | Calibre catalog, covers, files |
| `/reframes` | Concept metaphors/analogies |
| `/templates` | Thinking mode templates |

**Session State API** (`/session-state`) — Redis-backed cross-app continuity:
- `GET /{user_id}` — Get current session state (404 if no active session)
- `PATCH /{user_id}` — Update state (partial updates, creates if missing)
- `POST /{user_id}/heartbeat` — Keepalive (updates last_activity_at)
- `GET /{user_id}/history` — State change history (limit param, newest first)
- `DELETE /{user_id}` — Clear session (records session_ended event)
- `GET /{user_id}/continue` — Journey continuity data with deep links
- `GET /{user_id}/is-active` — Check if session active (within 30min timeout)

**Key Services:**
- `SessionStateService` — Cross-app state sync with Redis persistence (Redis backend, 24h TTL, 30min session timeout)
  - Journey trail tracking (max 50 items, most recent first)
  - Reading position sync (CFI-based for EPUB precision)
  - Context/Question state management
  - Heartbeat mechanism for session keepalive
  - Change type detection (context_opened, question_selected, book_opened, reading_progress, entity_visited)
- `RedisClient` — Async Redis singleton with connection pooling
- `JourneyLogger` — Centralized event logging to Neo4j timeline
- `ExtractionEngine` — Context-aware entity extraction (600 lines)
- `HighlightSyncService` — Reader → SiYuan sync with journey logging
- `PassageRankingService` — Question-driven reading
- `JourneyTimelineService` — Aggregates ContextJourneyEntry + BreadcrumbJourney
- `JourneyPatternService` — Pattern analysis (entity clustering, frequent entities, common paths, recommendations)

**Entity Types (14):**
- Domain: Concept, Person, Theory, Framework, Assessment
- Personal: Spark, Insight, Thread, FavoriteProblem, Reframe
- Patterns: Pattern, DynamicPattern, StoryInsight, SchemaBreak

**Question Engine (9 classes):**
Schema-Probe, Boundary, Dimensional, Causal, Counterfactual, Anchor, Perspective-Shift, Meta-Cognitive, Reflective-Synthesis

**Session State Schema:**
- Core state: `active_context_id`, `active_question_id`, `current_book` (ReadingPosition)
- Journey continuity: `current_entity_id`, `current_entity_name`, `journey_trail[]`, `last_app_source`
- Timestamps: `last_activity_at`, `created_at`, `updated_at`
- History tracking: Change types (context_opened, question_selected, book_opened, reading_progress, entity_visited)

**Journey Trail Item:**
- Entity: `entity_id`, `entity_name`, `entity_type`
- Source: `source_app` (reader | siyuan), `timestamp`, `source_context`
- Engagement: `dwell_seconds` (time spent on entity)

**Design Tokens** (`ies/design-tokens/`) — Single source of truth for IES design system:
- **Package**: `@ies/design-tokens` v2.0.0
  - 158 tokens: colors (entity/question types, semantic, glass), spacing (4px base), typography (Inter/Source Serif/JetBrains Mono), motion (durations/easings)
  - Build tool: Style Dictionary 4.0.1
  - Outputs: CSS variables, SCSS, TypeScript/JavaScript
  - Command: `npm run build` → `dist/tokens.{css,scss,js,ts}`
- **Token Categories**:
  - Colors: 5-level backgrounds, 5-level text, 8 entity types + bg variants, 9 question classes + bg variants, semantic (success/warning/error/info), energy levels (ADHD mood-based), borders, glass effect
  - Spacing: 0-32 scale (0px-128px), semantic radius (button/input/card/modal/chip/badge), breakpoints (sm/md/lg/xl/2xl)
  - Typography: Font families (sans/serif/mono), sizes (xs-5xl, Major Third 1.25 ratio), weights (400-700), line heights, letter spacing
  - Motion: Durations (instant 75ms → slower 500ms), easings (out/in/in-out/spring/linear), shadows (xs-xl), z-index layers (0-300)
- **WCAG Compliance**: All text colors meet WCAG AA minimum (4.5:1 normal, 3.0:1 large)
  - Primary text: 17.60:1 (AAA)
  - Secondary text: 7.45:1 (AA)
  - Muted text: 4.74:1 (AA, was 3.78:1 - fixed Dec 9)
  - Subtle text: 3.52:1 (large text only)
- **Accessibility**: Comprehensive `prefers-reduced-motion` support
  - All animations/transitions reduced to 0.01ms when user prefers reduced motion
  - Scroll behavior auto (disables smooth scrolling)
  - Animation iteration count limited to 1
- **Integration**: Import `@ies/design-tokens` in React/Svelte, use CSS vars or TypeScript constants
- **Test HTML**: `ies/design-tokens/test.html` - Live token preview with all colors, spacing, typography, motion

**IES Reader Components** (`ies/reader/src/`):
- `Reader.tsx` — epub.js wrapper with selection handling, sync status indicator
  - Visual sync indicator with 4 states (idle/synced/syncing/error)
  - Icons: CheckCircle2 (synced/idle), RefreshCcw (syncing), CloudOff (error)
  - Toolbar integration with glassmorphic design
- `Reader.css` — IES Design System v2 styling (dark theme, glassmorphism)
  - Sync indicator animations (spin keyframe for syncing state)
  - Flow toggle button with active state styling
  - Mobile-responsive breakpoints (480px, 768px)
- `styles/motion.css` — Accessibility-first motion system
  - `prefers-reduced-motion: reduce` — Disables all animations/transitions (0.01ms)
  - `prefers-reduced-motion: no-preference` — Smooth scrolling, default transitions (150ms fast)
  - Utility classes: `.no-motion` (force disable), `.force-motion` (override)
- `hooks/useReducedMotion.ts` — React hook for motion preference detection
  - Returns boolean: true if user prefers reduced motion
  - SSR-safe, listens for preference changes via `matchMedia`
  - Use: Conditionally apply animations or adjust durations
- `ErrorBoundary.tsx` — React error boundary component with graceful fallback UI
  - Catches component errors using `getDerivedStateFromError()` and `componentDidCatch()`
  - Displays error details (message, component stack) with expand/collapse
  - Reset functionality via `handleReset()` to recover from errors
  - Integrated in `App.tsx` wrapping Reader component
  - Styling in `ErrorBoundary.css` with glassmorphic error card design
- `.storybook/` — Storybook v8.5 configuration
  - Addons: a11y (accessibility testing), vitest (unit tests), docs (auto-docs), interactions (interaction testing), chromatic (visual regression)
  - Framework: React + Vite
  - Stories: `**/*.stories.tsx` (Button, ErrorBoundary)
  - Dark theme default: bg #0f0f10, text #f5f5f5
  - Viewports: Mobile (375px), Tablet (768px), Desktop (1440px, default), Desktop Wide (1920px)
  - Port: 6006
  - Command: `pnpm storybook`
- `components/Button.tsx` — Design system button component with variants
  - Variants: primary, secondary, success, warning, danger
  - Sizes: small, medium, large
  - States: default, hover, active, disabled
  - Full accessibility: ARIA labels, keyboard navigation
  - Story: `Button.stories.tsx` with all variants and interaction tests
- `FlowPanel.tsx` — Entity exploration panel
- `useSessionSync` — Backend state sync hook (5s active / 30s background polling, 3s write debounce)
  - Syncs context_id, question_id from flowStore → backend
  - Polls journey_trail from backend (read-only, SiYuan writes)
  - Adds entity visits via `addEntityVisit()` with dwell tracking
  - Sets sync status: idle → syncing → synced/error (via flowStore.setSyncStatus)
- `useReadingPosition` — CFI-based position tracking
- `flowStore.ts` — Zustand state management with journey trail + sync status
  - State: journeyTrail (JourneyTrailItem[]), lastAppSource (AppSource), syncStatus, syncError
  - Actions: setJourneyTrail(), setLastAppSource(), setSyncStatus()

**SiYuan Plugin** (`.worktrees/siyuan/ies/plugin/src/`):
- `FlowMode.svelte` — Graph exploration (113KB)
- `ForgeMode.svelte` — Structured thinking (110KB)
- `FlowModeWithErrorHandling.svelte` — Error boundary wrapper for FlowMode
  - Catches runtime errors (ErrorEvent, PromiseRejectionEvent)
  - Displays graceful error UI via ErrorDisplay component
  - Component re-mount on retry using `{#key componentKey}` pattern
- `ForgeModeWithErrorHandling.svelte` — Error boundary wrapper for ForgeMode
  - Same error handling pattern as FlowModeWithErrorHandling
- `ErrorDisplay.svelte` — Reusable error UI component for Svelte
  - Props: error, message, showDetails, showRetry
  - Alert circle icon, error message, expandable stack trace
  - Retry button dispatches 'retry' event
  - Styled with SiYuan theme variables (b3-theme-error, b3-spacing-*)
- `styles/design-system/colors.css` — WCAG AA compliant color system (Dec 9, 2025 update)
  - Entity colors: WCAG AA minimum (4.5:1), AAA for primary text (17.60:1)
  - Question class colors with accessible backgrounds
  - Semantic colors (success/warning/error/info)
  - Fixed contrast violations: text-muted (#6e6e73 → #7e7e85, 3.78:1 → 4.74:1)
  - text-subtle: #6a6a70 (3.52:1, large text only)
- `styles/design-system/animations.css` — Motion system with accessibility support
  - Durations: instant (75ms) → slower (500ms)
  - Easings: out, in, in-out, spring, linear
  - Transition presets: fast, base, slow, spring
  - Keyframe animations: fade-in, fade-out, slide-up, slide-down, scale-in
  - `prefers-reduced-motion: reduce` — All animations/transitions reduced to 0.01ms
  - Scroll behavior: auto (disables smooth scrolling for reduced motion)
  - Animation iteration count: limited to 1 for reduced motion
- `QuestionEditModal.svelte` — Question text and context link editor
  - Multi-select for linked contexts
  - Uses forwardProxy pattern for backend API calls
- `UserQuestionsPanel.svelte` — User questions management panel
  - CRUD operations for questions with delete confirmation
- `ContextSyncService.ts` — Bidirectional session sync (5s visible / 30s hidden polling)
  - Pushes local context/question changes to backend
  - Pulls remote changes and updates local state (last-write-wins)
  - Journey continuity: current_entity_id, journey_trail, last_app_source
  - Visibility-based polling (faster when visible, slower when hidden)
<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: conventions -->
<!-- Reserved for future use -->
<!-- END AUTO-MANAGED -->
