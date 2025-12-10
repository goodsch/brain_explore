# Implementation Roadmap
## Design Package → Production: 12-Week Plan

**Document Status:** ACTIVE
**Created:** 2025-12-09
**Last Updated:** 2025-12-09
**Depends On:**
- `04-critical-evaluation.md` (30 issues identified)
- `05-flow-mode-blueprint.md` (Graph visualization redesign)
- `06-design-system-spec.md` (Unified tokens & components)

---

## Executive Summary

This roadmap translates the design package into actionable implementation phases over 12 weeks. The strategy prioritizes:

1. **Critical UX Blockers** - Issues marked P0 that break core workflows
2. **Foundation First** - Design system unification before component builds
3. **Flow Mode Transformation** - Graph visualization is the flagship feature
4. **Incremental Delivery** - Each phase ships working, testable improvements

**Total Estimated Effort:** 480 hours (~3 months for 1 full-time frontend dev)

---

## Priority Framework

### P0 - Critical (Broken/Misleading)
- Flow Mode has no graph visualization (blocked by stub implementation)
- Selection bar positioning breaks on scroll/resize
- Stub hooks not implemented (useLocalStorage, useNetworkStatus)
- Cross-app sync has no UI feedback

### P1 - High (Major UX Issues)
- Question CRUD incomplete (no edit/delete)
- No keyboard navigation for graph/questions
- Theme mismatch between SiYuan/Reader
- WCAG AA violations (contrast, ARIA labels)

### P2 - Medium (Quality of Life)
- Areas chips non-functional (dead UI)
- Mobile FAB discovery poor
- Progress indicators unclear (spinners without context)
- No empty state guidance

### P3 - Low (Polish)
- Optimistic UI updates missing
- Animation timing inconsistent
- Component documentation sparse
- No loading skeletons

---

## Phase 0: Quick Wins
**Timeline:** Week 1 (40 hours)
**Goal:** Fix critical blockers that can be solved with <4 hours effort each

### Objectives
- Unblock users from immediate pain points
- Build momentum with visible improvements
- De-risk Phase 1 by cleaning up technical debt

### Tasks

| Task | Effort | Priority | File(s) |
|------|--------|----------|---------|
| Fix selection bar bounds checking | S (2h) | P0 | `ies/reader/src/components/SelectionActions.tsx` |
| Add question delete button | S (3h) | P1 | `ies/plugin/src/components/QuestionsList.svelte` |
| Add question edit modal | M (4h) | P1 | `ies/plugin/src/components/QuestionEditModal.svelte` |
| Add ARIA labels to icon buttons | S (2h) | P1 | All components with `<button>` + icon |
| Add sync status indicator | S (3h) | P0 | `ies/reader/src/hooks/useSessionSync.ts` |
| Fix "Show All" button hiding | S (1h) | P1 | `ies/plugin/src/components/QuestionsList.svelte` |
| Add loading spinners with text | S (2h) | P2 | `flowStore.ts`, `FlowMode.svelte` |
| Fix entity name overflow | S (1h) | P2 | `EntityCard.svelte` (text-overflow) |
| Add error boundaries | M (4h) | P1 | Root components in both apps |
| Document keyboard shortcuts | S (2h) | P2 | New `docs/KEYBOARD-SHORTCUTS.md` |

**Success Criteria:**
- Selection bar stays in viewport on scroll
- Users can delete/edit questions from UI
- All icon buttons have `aria-label`
- Sync indicator shows "Synced" / "Syncing" / "Offline"
- Loading states have descriptive text

**Risks:**
- Selection bar fix may need epub.js patch (low probability)
- Question edit may require backend schema changes (validate first)

**Testing:**
- Manual: Test selection bar on mobile viewport (Chrome DevTools)
- Manual: Create/edit/delete question flow
- Automated: Add Playwright test for selection bar positioning
- Accessibility: Run axe-devtools on updated components

---

## Phase 1: Design System Foundation
**Timeline:** Week 2 (40 hours)
**Goal:** Establish single source of truth for design tokens and theming

### Objectives
- Eliminate theme mismatch between SiYuan plugin and IES Reader
- Fix WCAG AA contrast violations
- Enable prefers-reduced-motion support
- Create design token documentation

### Tasks

| Task | Effort | Priority | Deliverable |
|------|--------|----------|-------------|
| Create design tokens package | M (6h) | P1 | `ies/design-tokens/` package |
| Extract SiYuan theme variables | S (3h) | P1 | `tokens/colors.json` |
| Extract Reader theme variables | S (3h) | P1 | `tokens/colors.json` (merged) |
| Generate CSS custom properties | S (2h) | P1 | Build script outputs CSS |
| Apply tokens to SiYuan plugin | M (6h) | P1 | Replace hardcoded colors |
| Apply tokens to IES Reader | M (6h) | P1 | Replace hardcoded colors |
| Fix contrast ratio violations | S (3h) | P1 | Update token values for WCAG AA |
| Add reduced motion styles | S (2h) | P1 | `@media (prefers-reduced-motion)` |
| Document token usage | S (3h) | P2 | `design-tokens/README.md` |
| Setup Storybook | M (6h) | P2 | Initialize with theme docs |

**Dependencies:**
- None (foundational work)

**Success Criteria:**
- Single `tokens/colors.json` used by both apps
- All text/background pairs meet WCAG AA (4.5:1 for normal text)
- Animations respect `prefers-reduced-motion: reduce`
- Storybook shows theme previews

**Risks:**
- SiYuan's CSS-in-JS may conflict with CSS custom properties (mitigation: use PostCSS plugin)
- Existing component styles may override tokens (mitigation: use `!important` sparingly, audit specificity)

**Testing:**
- Visual regression: Percy snapshots of key screens before/after
- Accessibility: Run axe-devtools on full app
- Manual: Toggle `prefers-reduced-motion` in browser DevTools

**Design Token Package Structure:**
```
ies/design-tokens/
├── tokens/
│   ├── colors.json          # Base color palette
│   ├── spacing.json         # 4px base scale
│   ├── typography.json      # Font sizes, weights
│   └── motion.json          # Duration, easing
├── build.js                 # Generate CSS/SCSS/JS
├── dist/
│   ├── tokens.css           # CSS custom properties
│   ├── tokens.scss          # SCSS variables
│   └── tokens.ts            # TS constants
└── README.md
```

---

## Phase 2: Flow Mode Core
**Timeline:** Weeks 3-4 (80 hours)
**Goal:** Replace stub graph view with interactive D3.js force-directed graph

### Objectives
- Implement core graph visualization from Flow Mode Blueprint
- Enable entity click navigation with smooth transitions
- Support basic pan/zoom interactions
- Maintain performance with 50+ nodes

### Tasks

| Task | Effort | Priority | Technical Notes |
|------|--------|----------|-----------------|
| Install D3.js dependencies | S (1h) | P0 | `d3`, `d3-force`, `@types/d3` |
| Create GraphCanvas component | L (12h) | P0 | SVG-based, hooks into flowStore |
| Implement force simulation | M (8h) | P0 | `d3.forceSimulation()` with link/charge |
| Add entity node rendering | M (6h) | P0 | Circle nodes with type colors |
| Add relationship edge rendering | M (6h) | P0 | Line paths with arrow markers |
| Implement radial focus layout | L (10h) | P0 | Selected entity at center, 2 levels |
| Add click navigation | M (4h) | P0 | Update flowStore → re-layout |
| Implement pan/zoom | M (6h) | P1 | `d3.zoom()` with constraints |
| Add zoom controls UI | S (3h) | P1 | +/- buttons, reset button |
| Optimize rendering performance | M (8h) | P1 | Canvas rendering for 100+ nodes |
| Add node labels | S (3h) | P1 | Text elements with overflow |
| Implement hover tooltips | S (3h) | P1 | Show entity type, description |
| Add loading state | S (2h) | P2 | Skeleton graph with pulse |
| Add empty state | S (2h) | P2 | "Select entity to explore" |
| Write unit tests | M (6h) | P1 | Test force layout calculations |

**Dependencies:**
- Phase 1 design tokens (for node colors)
- Backend `/graph` API working (already implemented)

**Success Criteria:**
- Graph displays with radial layout on entity selection
- Clicking node navigates to entity (updates flowStore)
- Pan/zoom works with mouse and trackpad
- Performance: 60fps with 50 nodes, 30fps with 100 nodes
- Tests cover force layout edge cases (empty graph, single node)

**Risks:**
- D3.js v7 breaking changes vs examples (mitigation: use official React examples)
- Performance degrades with >100 nodes (mitigation: implement canvas fallback in Phase 3)
- Force simulation doesn't stabilize (mitigation: tune force parameters, add timeout)

**Testing:**
- Unit: Test force layout with mock graph data
- Integration: Test entity click → API call → graph update
- Performance: Measure FPS with Chrome DevTools (target 60fps)
- Manual: Test on touch devices for pan/zoom

**Technical Implementation Details:**

### GraphCanvas Component Structure
```typescript
// ies/plugin/src/components/GraphCanvas.svelte
<script lang="ts">
  import * as d3 from 'd3';
  import { onMount, onDestroy } from 'svelte';
  import { flowStore } from '../stores/flowStore';

  // Props
  export let width = 800;
  export let height = 600;

  // D3 simulation
  let simulation: d3.Simulation<Node, Link>;
  let nodes: Node[] = [];
  let links: Link[] = [];

  // Lifecycle
  onMount(() => {
    initSimulation();
    flowStore.subscribe(updateGraph);
  });

  function initSimulation() {
    simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));
  }

  function updateGraph(state) {
    // Transform flowStore entities → D3 nodes/links
    // Apply radial layout for focused entity
    // Restart simulation
  }
</script>

<svg {width} {height}>
  <!-- Edges -->
  {#each links as link}
    <line
      x1={link.source.x} y1={link.source.y}
      x2={link.target.x} y2={link.target.y}
      stroke={tokens.colors.graph.edge}
    />
  {/each}

  <!-- Nodes -->
  {#each nodes as node}
    <circle
      cx={node.x} cy={node.y} r={20}
      fill={getNodeColor(node.type)}
      on:click={() => handleNodeClick(node)}
    />
  {/each}
</svg>
```

### Force Layout Parameters
Based on Blueprint specifications:
- **Link Distance:** 100px (adjusts based on zoom level)
- **Charge Strength:** -300 (repulsion between nodes)
- **Collision Radius:** 30px (prevents overlap)
- **Radial Focus:**
  - Level 0 (center): Selected entity
  - Level 1 (ring 1): Direct relationships (radius 120px)
  - Level 2 (ring 2): Second-degree (radius 240px)

---

## Phase 3: Flow Mode Enhancement
**Timeline:** Weeks 5-6 (80 hours)
**Goal:** Add minimap, semantic zoom, keyboard navigation, gesture polish

### Objectives
- Implement minimap for spatial orientation (Blueprint requirement)
- Add semantic zoom with 3 levels of detail
- Full keyboard navigation for accessibility
- Polish touch gestures for mobile

### Tasks

| Task | Effort | Priority | Technical Notes |
|------|--------|----------|-----------------|
| Create Minimap component | M (8h) | P1 | 150x150px, bottom-right corner |
| Implement minimap viewport | M (6h) | P1 | Draggable rectangle, synced zoom |
| Add semantic zoom levels | L (12h) | P1 | Full/Medium/Overview (Blueprint) |
| Implement keyboard navigation | M (8h) | P1 | Arrow keys, Tab, Enter, Escape |
| Add keyboard shortcuts help | S (3h) | P1 | `?` key shows modal |
| Polish pinch-to-zoom | M (6h) | P1 | Hammer.js for touch events |
| Add pan momentum | M (4h) | P2 | Deceleration after swipe |
| Optimize canvas rendering | L (10h) | P1 | Fallback for >100 nodes |
| Add node filtering UI | M (6h) | P2 | Filter by entity type |
| Implement search highlight | M (6h) | P2 | Highlight nodes matching search |
| Add edge bundling | L (10h) | P3 | D3 hierarchical edge bundling |
| Write integration tests | M (6h) | P1 | Test keyboard nav, zoom levels |

**Dependencies:**
- Phase 2 GraphCanvas component

**Success Criteria:**
- Minimap shows full graph, viewport rectangle updates on pan/zoom
- Semantic zoom hides labels at Overview, shows full details at Full
- All graph interactions work with keyboard (no mouse required)
- Pinch-to-zoom works on iOS/Android
- Canvas rendering maintains 30fps with 200+ nodes

**Risks:**
- Canvas rendering may require full rewrite (mitigation: progressive enhancement)
- Keyboard focus management conflicts with Svelte (mitigation: use `use:action` directives)
- Touch gestures interfere with scroll (mitigation: preventDefault selectively)

**Testing:**
- Manual: Test keyboard navigation with screen reader (NVDA/VoiceOver)
- Manual: Test touch gestures on real devices (iOS/Android)
- Performance: Measure rendering time with 500 nodes
- Integration: Playwright test for keyboard shortcuts

**Semantic Zoom Levels:**

| Level | Node Size | Label Display | Edge Display | Use Case |
|-------|-----------|---------------|--------------|----------|
| **Full** (1.0x) | 24px | All visible | All + arrows | Close-up detail |
| **Medium** (0.5x) | 16px | Hover only | All, no arrows | Navigation |
| **Overview** (0.25x) | 8px | None | Major only | Spatial overview |

**Keyboard Shortcuts:**

| Key | Action | Notes |
|-----|--------|-------|
| `Arrow Keys` | Navigate between nodes | Focus rings on nodes |
| `Tab` / `Shift+Tab` | Cycle through nodes | DOM order |
| `Enter` / `Space` | Select focused node | Updates flowStore |
| `Escape` | Clear selection | Return to overview |
| `+` / `-` | Zoom in/out | Also `Ctrl+Scroll` |
| `0` | Reset zoom | Fit all nodes |
| `?` | Show shortcuts | Modal overlay |
| `/` | Focus search | Filter nodes |

---

## Phase 4: Component Library
**Timeline:** Weeks 7-8 (80 hours)
**Goal:** Build reusable components from Design System Spec, document in Storybook

### Objectives
- Extract common patterns into shared components
- Document components with Storybook stories
- Enable design system adoption by future developers
- Fix component-level accessibility issues

### Tasks

| Task | Effort | Priority | Component(s) |
|------|--------|----------|--------------|
| Create EntityBadge component | S (3h) | P1 | Type icon + name, 5 variants |
| Create EntityCard component | M (6h) | P1 | Clickable card with metadata |
| Create QuestionClassBadge | S (2h) | P1 | 9 question types |
| Create BreadcrumbTrail component | M (4h) | P1 | Journey history with overflow |
| Create SearchInput component | S (3h) | P1 | With clear button, debounce |
| Create FilterPills component | M (4h) | P2 | Multi-select with clear all |
| Create ProgressRing component | S (2h) | P2 | SVG circular progress |
| Write Storybook stories | M (8h) | P1 | All components above |
| Document component props | M (6h) | P1 | JSDoc + Storybook docs |
| Add component tests | L (12h) | P1 | Jest + Testing Library |
| Extract shared utilities | M (6h) | P2 | Date formatting, string utils |
| Create component guidelines | M (6h) | P2 | When to use each component |
| Migrate existing code | L (16h) | P2 | Replace inline components |
| Setup Chromatic CI | S (2h) | P2 | Visual regression testing |

**Dependencies:**
- Phase 1 design tokens package

**Success Criteria:**
- 7 reusable components documented in Storybook
- All components have unit tests (>80% coverage)
- Existing code migrated to use shared components
- Chromatic catches visual regressions in CI

**Risks:**
- Svelte/React component duplication (mitigation: use Web Components for cross-framework)
- Over-abstraction slows iteration (mitigation: extract after 3rd usage, not 2nd)

**Testing:**
- Unit: Test component props and events (Jest)
- Visual: Storybook snapshots with Chromatic
- Accessibility: Axe addon in Storybook
- Integration: Test component usage in real views

**Component Specifications:**

### EntityBadge
```typescript
// Props
interface EntityBadgeProps {
  type: EntityType;        // Concept | Person | Theory | etc.
  name: string;            // Entity name
  size?: 'sm' | 'md' | 'lg'; // Default 'md'
  clickable?: boolean;     // Show hover state
  onClick?: () => void;    // Click handler
}

// Visual
- Icon (lucide-react, 14px @ md)
- Name (truncated with tooltip)
- Type color from design tokens
- Hover: 8% lighter background
- Size variants: sm=20px, md=24px, lg=32px height
```

### EntityCard
```typescript
// Props
interface EntityCardProps {
  entity: Entity;          // Full entity object
  showDescription?: boolean; // Default true
  showMetadata?: boolean;  // Default true
  onClick?: () => void;    // Navigation handler
}

// Visual
- Header: EntityBadge + edit button
- Body: Description (3 lines max)
- Footer: Source book + relationship count
- Hover: Elevation shadow
- Focus: 2px outline (keyboard)
```

### BreadcrumbTrail
```typescript
// Props
interface BreadcrumbTrailProps {
  trail: JourneyTrailItem[]; // From journey API
  maxVisible?: number;       // Default 5
  onItemClick?: (item: JourneyTrailItem) => void;
}

// Visual
- Horizontal scroll on overflow
- Separator: "/" (muted color)
- Current item: Bold, no hover
- Past items: Clickable, hover underline
- Overflow: "..." button shows dropdown
```

**Storybook Organization:**
```
Components/
├── Data Display/
│   ├── EntityBadge
│   └── EntityCard
├── Navigation/
│   ├── BreadcrumbTrail
│   └── FilterPills
├── Inputs/
│   └── SearchInput
└── Feedback/
    └── ProgressRing

Pages/
├── FlowMode (composite)
└── ForgeMode (composite)
```

---

## Phase 5: Mobile & Polish
**Timeline:** Weeks 9-10 (80 hours)
**Goal:** Fix mobile-specific issues, improve discoverability, empty states

### Objectives
- Implement draggable bottom sheet for mobile Flow Panel
- Fix touch target sizes (<44px violations)
- Improve FAB discoverability with onboarding
- Add contextual empty states with next actions

### Tasks

| Task | Effort | Priority | Impact |
|------|--------|----------|--------|
| Create BottomSheet component | L (10h) | P1 | Replaces sidebar on mobile |
| Add drag handle indicator | S (2h) | P1 | Visual affordance |
| Implement snap points | M (6h) | P1 | Collapsed/Half/Full |
| Fix touch target sizes | M (6h) | P1 | Audit all buttons/links |
| Add FAB onboarding tooltip | S (3h) | P2 | Show on first visit |
| Create EmptyState component | M (4h) | P2 | Illustration + CTA |
| Add "No questions" empty state | S (2h) | P2 | "Add your first question" |
| Add "No entities" empty state | S (2h) | P2 | "Select text to extract" |
| Add "No graph data" empty state | S (2h) | P2 | "Explore entities to build" |
| Improve mobile graph gestures | M (8h) | P1 | Pinch, pan, double-tap |
| Add haptic feedback | S (3h) | P2 | iOS/Android vibration |
| Polish loading skeletons | M (6h) | P2 | Replace spinners |
| Add optimistic UI updates | L (10h) | P2 | Instant feedback for CRUD |
| Mobile testing on real devices | L (12h) | P1 | iOS 16+, Android 12+ |
| Write mobile-specific tests | M (6h) | P1 | Playwright mobile viewport |

**Dependencies:**
- Phase 2 graph implementation (for mobile gestures)
- Phase 4 component library (for EmptyState)

**Success Criteria:**
- Bottom sheet works on iOS/Android with smooth animations
- All touch targets ≥44x44px (WCAG 2.5.5)
- First-time users see FAB tooltip
- Empty states provide clear next action
- Mobile gestures feel native (not web-like)

**Risks:**
- Bottom sheet conflicts with scroll (mitigation: use react-spring with scroll lock)
- Haptic API not supported on all devices (mitigation: progressive enhancement)
- Optimistic UI creates race conditions (mitigation: rollback on error)

**Testing:**
- Manual: Test on iPhone SE (small screen), iPad (tablet)
- Manual: Test on Android devices (Samsung, Pixel)
- Automated: Playwright with mobile viewport emulation
- Performance: Measure scroll jank with Chrome DevTools

**Bottom Sheet Specifications:**

### Snap Points
| State | Height | Use Case | Gesture |
|-------|--------|----------|---------|
| **Collapsed** | 64px | Peek at content | Swipe up |
| **Half** | 50vh | Read content | Swipe up/down |
| **Full** | 90vh | Maximize panel | Swipe up |

### Interaction States
- **Drag Handle:** 32x4px rounded rectangle, 8px from top
- **Overlay:** 60% black when expanded (tapping dismisses)
- **Momentum:** Continues scrolling after release (deceleration curve)
- **Bounce:** Subtle spring animation at snap points

**Empty State Guidelines:**

Each empty state follows this pattern:
1. **Icon/Illustration** (48px, muted color)
2. **Headline** (16px semibold, 1-2 words)
3. **Description** (14px regular, 1-2 sentences)
4. **Primary Action** (Button, clear CTA)
5. **Secondary Action** (Link, optional)

Examples:
- **No Questions:** "Start Exploring" → "Add your first question to guide your reading"
- **No Entities:** "Highlight to Extract" → "Select text in a book to discover entities"
- **No Graph Data:** "Build Your Graph" → "Explore entities to see their connections"

---

## Phase 6: AI & Discovery
**Timeline:** Weeks 11-12 (80 hours)
**Goal:** Implement AI-powered features from Blueprint (bridge entities, pattern recommendations)

### Objectives
- Add bridge entity suggestions to connect disparate clusters
- Implement pattern-based exploration recommendations
- Add natural language search for entities/questions
- Enable smart filtering (e.g., "show only theories from 2020s books")

### Tasks

| Task | Effort | Priority | Technical Notes |
|------|--------|----------|-----------------|
| Design bridge suggestion API | M (6h) | P2 | Backend: graph algorithm |
| Implement Jaccard similarity | M (4h) | P2 | Find entities bridging clusters |
| Add "Suggested Bridges" panel | M (6h) | P2 | Shows 3-5 bridge entities |
| Design pattern recommendation API | M (6h) | P2 | Backend: pattern matching |
| Implement pattern detector | L (10h) | P2 | Identify exploration patterns |
| Add "Try This Next" panel | M (6h) | P2 | Contextual suggestions |
| Add natural language search | L (12h) | P2 | Backend: OpenAI embeddings |
| Implement semantic search UI | M (6h) | P2 | Search bar with NLP hint |
| Add smart filter parser | L (10h) | P3 | Parse "theories from 2020s" |
| Add filter suggestions | M (4h) | P3 | Auto-complete for filters |
| Implement usage analytics | M (6h) | P3 | Track feature adoption |
| Add A/B test framework | M (6h) | P3 | Test recommendation variants |
| Write AI feature docs | M (4h) | P2 | Explain how suggestions work |
| User testing session | M (4h) | P2 | 5 users, moderated |

**Dependencies:**
- Phase 2 graph implementation (for cluster detection)
- Phase 3 minimap (to show suggested bridges visually)
- Backend: OpenAI API key configured

**Success Criteria:**
- Bridge suggestions connect ≥2 clusters in 80% of graphs
- Pattern recommendations are relevant (user acceptance >50%)
- Natural language search returns relevant results (precision >0.7)
- Smart filters parse correctly (accuracy >90%)

**Risks:**
- AI suggestions feel intrusive (mitigation: make dismissible, learn from feedback)
- OpenAI API costs escalate (mitigation: cache embeddings, rate limit)
- Pattern detection has false positives (mitigation: require ≥3 occurrences)

**Testing:**
- Unit: Test Jaccard similarity calculations
- Integration: Test full suggestion pipeline (mock OpenAI)
- User testing: Measure relevance with real users
- Performance: Measure latency of NLP search (<500ms target)

**Bridge Entity Detection Algorithm:**

### Jaccard Similarity Approach
```python
# Pseudocode for backend implementation
def find_bridge_entities(graph, cluster_a, cluster_b):
    """Find entities that connect two clusters."""
    # Get entities in each cluster
    entities_a = set(graph.get_cluster_entities(cluster_a))
    entities_b = set(graph.get_cluster_entities(cluster_b))

    # Find candidates: entities connected to both clusters
    candidates = []
    for entity in graph.all_entities:
        connections_to_a = entity.relationships & entities_a
        connections_to_b = entity.relationships & entities_b

        if len(connections_to_a) > 0 and len(connections_to_b) > 0:
            # Jaccard similarity score
            intersection = connections_to_a & connections_to_b
            union = connections_to_a | connections_to_b
            score = len(intersection) / len(union)
            candidates.append((entity, score))

    # Return top 5 by score
    return sorted(candidates, key=lambda x: x[1], reverse=True)[:5]
```

### UI Implementation
- **Trigger:** Show suggestions when graph has ≥2 disconnected clusters
- **Panel:** Docked to right side, dismissible
- **Card:** Entity badge + "Connects X and Y" + relevance score
- **Action:** Clicking adds entity to graph at midpoint between clusters

**Pattern Recommendation Examples:**

| Pattern | Detection | Recommendation |
|---------|-----------|----------------|
| **Theory Hopping** | User visits 3+ Theory entities in <5min | "Explore Frameworks that apply these theories" |
| **Person Focus** | User visits same Person 3+ times | "See Concepts influenced by [Person]" |
| **Era Exploration** | User filters by date range | "Compare with similar ideas from [other era]" |
| **Concept Clustering** | User visits related Concepts | "These form a Theme. Create one?" |
| **Dead End** | User backtracks 2+ times | "Bridge to [nearby entity] to continue" |

**Natural Language Search:**

### Query Types
- **Entity name:** "Carl Jung" → Exact match
- **Concept:** "attachment theory" → Semantic search
- **Question:** "why do people procrastinate?" → Question generation
- **Filter:** "theories from neuroscience books" → Smart filter

### Backend Pipeline
1. Parse query with spaCy (entity recognition)
2. Generate embedding with OpenAI `text-embedding-3-small`
3. Vector search in Neo4j (cosine similarity)
4. Rerank by graph centrality (PageRank)
5. Return top 10 results with snippets

---

## Cross-Cutting Concerns

### Testing Strategy

| Phase | Unit Tests | Integration Tests | E2E Tests | Manual Testing |
|-------|------------|-------------------|-----------|----------------|
| 0 | Component tests | Selection bar positioning | Full CRUD flow | Mobile devices |
| 1 | Token generator | Theme applied correctly | Visual regression | Contrast checker |
| 2 | Force layout logic | Graph updates on nav | Entity click flow | Performance profiling |
| 3 | Keyboard handlers | Minimap sync | Zoom levels work | Touch gestures |
| 4 | Component props | Component integration | Storybook snapshots | Accessibility audit |
| 5 | Bottom sheet logic | Sheet + scroll | Mobile workflows | Real device testing |
| 6 | AI algorithms | API integration | NLP search flow | User testing |

**Test Coverage Targets:**
- Unit tests: ≥80% coverage
- Integration tests: All critical paths (auth, CRUD, navigation)
- E2E tests: Happy path + 3 error scenarios per feature
- Manual tests: Weekly on iOS/Android/Desktop

**Automated Testing Tools:**
- Unit: Jest + Testing Library
- Integration: Playwright
- Visual: Chromatic (Storybook snapshots)
- Accessibility: axe-devtools, Pa11y CI
- Performance: Lighthouse CI

### Design Review Checkpoints

| Phase | Checkpoint | Attendees | Artifacts |
|-------|------------|-----------|-----------|
| 0 | Quick wins demo | PM, Designer | Screen recordings |
| 1 | Design tokens review | Designer, Frontend lead | Storybook theme docs |
| 2 | Graph interaction demo | PM, Designer, Users (2) | Interactive prototype |
| 3 | Minimap UX review | Designer, Users (3) | Usability test report |
| 4 | Component library review | Designer, Frontend team | Storybook published |
| 5 | Mobile UX review | PM, Designer, Users (5) | Device testing report |
| 6 | AI features review | PM, Designer, Data scientist | A/B test plan |

**Review Criteria:**
- Matches Design System Spec visually
- Meets accessibility standards (WCAG AA)
- Works on target devices (iOS 16+, Android 12+, Chrome 100+)
- Performance acceptable (Core Web Vitals)

### Performance Budgets

| Metric | Target | Current | Measurement |
|--------|--------|---------|-------------|
| **First Contentful Paint** | <1.5s | TBD | Lighthouse |
| **Largest Contentful Paint** | <2.5s | TBD | Lighthouse |
| **Time to Interactive** | <3.5s | TBD | Lighthouse |
| **Cumulative Layout Shift** | <0.1 | TBD | Lighthouse |
| **Graph Render (50 nodes)** | <500ms | TBD | Chrome DevTools |
| **Graph Render (200 nodes)** | <2s | TBD | Chrome DevTools |
| **Search API Response** | <300ms | TBD | Backend logs |
| **Bundle Size (Reader)** | <500KB | TBD | Webpack analyzer |
| **Bundle Size (Plugin)** | <800KB | TBD | Rollup analyzer |

**Optimization Strategies:**
- Code splitting by route (React.lazy)
- Tree shaking unused D3 modules
- Image optimization (WebP, lazy loading)
- Canvas rendering for large graphs (Phase 3)
- API response caching (React Query)

### Accessibility Compliance

**WCAG 2.1 Level AA Requirements:**

| Criterion | Target | Verification |
|-----------|--------|--------------|
| **1.4.3 Contrast** | 4.5:1 (text), 3:1 (UI) | axe-devtools |
| **1.4.10 Reflow** | No horizontal scroll @ 320px | Manual testing |
| **1.4.11 Non-text Contrast** | 3:1 for UI components | Manual testing |
| **2.1.1 Keyboard** | All functions keyboard accessible | Manual testing |
| **2.1.2 No Keyboard Trap** | Focus can move freely | Manual testing |
| **2.4.3 Focus Order** | Logical focus order | Manual testing |
| **2.4.7 Focus Visible** | Focus indicator visible | Manual testing |
| **2.5.5 Target Size** | ≥44x44px touch targets | Manual testing |
| **4.1.2 Name, Role, Value** | All controls labeled | axe-devtools |

**Testing Schedule:**
- Phase 0-1: Automated axe scans on each PR
- Phase 2-3: Manual keyboard testing weekly
- Phase 4-5: Screen reader testing (NVDA, VoiceOver)
- Phase 6: Full WCAG audit with Pa11y CI

---

## Resource Allocation

### Team Composition
- **Frontend Developer (1 FTE):** Primary implementer
- **Designer (0.3 FTE):** Review checkpoints, component specs
- **Backend Developer (0.2 FTE):** AI features API, performance optimization
- **PM (0.1 FTE):** Weekly progress reviews, user testing coordination

**Total Effort:** 480 hours (12 weeks × 40 hours)

### Allocation by Phase

| Phase | Frontend | Designer | Backend | PM | Total |
|-------|----------|----------|---------|----|----|
| 0 | 40h | 2h | 0h | 2h | 44h |
| 1 | 40h | 8h | 0h | 4h | 52h |
| 2 | 80h | 8h | 4h | 4h | 96h |
| 3 | 80h | 4h | 0h | 4h | 88h |
| 4 | 80h | 12h | 0h | 4h | 96h |
| 5 | 80h | 8h | 0h | 8h | 96h |
| 6 | 80h | 4h | 20h | 4h | 108h |
| **Total** | **480h** | **46h** | **24h** | **30h** | **580h** |

### Skill Requirements

**Frontend Developer:**
- Expert: TypeScript, React, Svelte
- Proficient: D3.js, Canvas API, Web Components
- Familiar: Accessibility (WCAG), Performance optimization

**Designer:**
- Expert: Design systems, component design
- Proficient: Usability testing, accessibility
- Familiar: Figma, Storybook

**Backend Developer:**
- Expert: Python, FastAPI
- Proficient: Neo4j, graph algorithms
- Familiar: OpenAI API, embeddings

---

## Risk Management

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| D3.js performance degrades with large graphs | Medium | High | Implement canvas fallback (Phase 3) |
| React/Svelte component duplication | High | Medium | Use Web Components for shared code |
| OpenAI API costs exceed budget | Low | High | Cache embeddings, rate limit requests |
| Mobile gestures conflict with browser defaults | Medium | Medium | Use preventDefault selectively, test extensively |
| Design token changes break existing styles | Low | Medium | Visual regression testing with Chromatic |
| Keyboard navigation conflicts with screen readers | Low | High | Test with NVDA and VoiceOver early |

### Process Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep extends timeline | High | High | Freeze scope after Phase 0, defer new features to backlog |
| Designer availability impacts Phase 4 | Medium | Medium | Front-load design reviews in Phases 1-2 |
| User testing recruitment delays Phase 6 | Medium | Low | Recruit testers in Phase 4, compensate appropriately |
| Dependency on backend team for AI APIs | Low | Medium | Mock APIs for frontend development, integrate in Phase 6 |

### Mitigation Strategies

**Scope Management:**
- **Freeze Scope:** After Phase 0 quick wins, defer all new requests to "Phase 7: Backlog"
- **Time Boxes:** Each task has max hours; if exceeded, reassess or defer
- **Weekly Reviews:** PM checks progress vs plan, adjusts next week's tasks

**Technical Debt:**
- **Refactor Budget:** 10% of each phase for refactoring/cleanup
- **Code Review:** All PRs reviewed by second developer
- **Documentation:** Update docs in same PR as code changes

**Quality Gates:**
- **No Merge Without Tests:** ≥80% coverage for new code
- **No Merge With Accessibility Violations:** axe-devtools must pass
- **No Merge With Performance Regressions:** Lighthouse score must not decrease

---

## Success Metrics

### User-Facing Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| **Graph Interaction Rate** | 0% (no graph) | 60% of sessions | Analytics |
| **Question Creation Rate** | Low (10/month) | 50/month | Database query |
| **Mobile Usage** | Unknown | 30% of sessions | Analytics |
| **Session Duration** | TBD | +20% | Analytics |
| **Feature Discovery (FAB)** | TBD | 80% of new users | Onboarding tracking |
| **Cross-App Sync Usage** | TBD | 40% of sessions | Session state API logs |

### Technical Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| **Test Coverage** | ~60% | ≥80% | Jest coverage report |
| **Accessibility Score** | Unknown | 100% (axe) | axe-devtools |
| **Lighthouse Performance** | Unknown | ≥90 | Lighthouse CI |
| **Bundle Size** | Unknown | <500KB (Reader) | Webpack analyzer |
| **Graph Render Time (50 nodes)** | N/A | <500ms | Chrome DevTools |
| **API Response Time (p95)** | ~200ms | <300ms | Backend logs |

### Quality Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| **Bugs Reported** | N/A | <5/week | GitHub issues |
| **Bugs Resolved (p50)** | N/A | <3 days | GitHub metrics |
| **Design Consistency** | Low | High (Storybook) | Manual audit |
| **User Satisfaction (CSAT)** | Unknown | ≥4.5/5 | User survey |

### Phase-Specific Success Criteria

**Phase 0:**
- [ ] All P0 issues resolved
- [ ] All ARIA labels added
- [ ] Selection bar positioning works on mobile

**Phase 1:**
- [ ] Design tokens used by both apps
- [ ] All contrast violations fixed
- [ ] Reduced motion support implemented

**Phase 2:**
- [ ] Graph displays with radial layout
- [ ] Entity click navigation works
- [ ] 60fps performance with 50 nodes

**Phase 3:**
- [ ] Minimap implemented and synced
- [ ] Keyboard navigation works for all graph actions
- [ ] Canvas rendering maintains 30fps with 200 nodes

**Phase 4:**
- [ ] 7 components in Storybook
- [ ] ≥80% test coverage on components
- [ ] Chromatic catches visual regressions

**Phase 5:**
- [ ] Bottom sheet works on iOS/Android
- [ ] All touch targets ≥44x44px
- [ ] Empty states provide clear CTAs

**Phase 6:**
- [ ] Bridge suggestions connect clusters
- [ ] Natural language search works
- [ ] User acceptance >50% for recommendations

---

## Post-Implementation

### Phase 7: Backlog (Deferred Features)

Features identified but deferred to stay on timeline:

| Feature | Reason Deferred | Estimated Effort |
|---------|----------------|------------------|
| Edge bundling (hierarchical) | Low priority, complex | 10h |
| Graph layout animations | Polish, not critical | 8h |
| Export graph as image | Nice-to-have | 6h |
| Collaborative graph editing | Complex, requires real-time sync | 40h |
| Custom entity types | Low usage, high complexity | 20h |
| Graph query language | Power user feature | 30h |
| Mobile app (native) | Long-term vision | 200h+ |

**Prioritization Criteria for Backlog:**
- User demand (feature requests, usage data)
- Strategic value (differentiators, retention)
- Technical feasibility (dependencies, complexity)

### Maintenance Plan

**Ongoing Activities:**
- Weekly bug triage (PM + Frontend)
- Monthly accessibility audits (axe-devtools)
- Quarterly performance reviews (Lighthouse)
- Bi-annual user testing (5 users)

**Update Cadence:**
- Design tokens: As needed, versioned (semver)
- Storybook: Updated with each component change
- Documentation: Updated in same PR as code
- Dependencies: Monthly security updates (Dependabot)

### Knowledge Transfer

**Documentation Deliverables:**
- Component library guide (Storybook)
- Graph implementation deep dive (architecture doc)
- Design token usage guide (README)
- Testing strategy (TESTING.md)
- Accessibility guide (A11Y.md)

**Handoff Sessions:**
- Week 6: Component library demo (Frontend team)
- Week 8: Mobile UX patterns (Designer + Frontend)
- Week 12: AI features architecture (Backend + Frontend)

---

## Appendix

### Glossary

| Term | Definition |
|------|------------|
| **Bridge Entity** | Entity that connects two otherwise disconnected graph clusters |
| **Semantic Zoom** | Zoom levels that change level of detail, not just scale |
| **Radial Layout** | Graph layout with selected entity at center, relationships in rings |
| **Design Token** | Named design decision (color, spacing) in shareable format |
| **Jaccard Similarity** | Measure of overlap between two sets (used for bridge detection) |
| **CFI** | EPUB Canonical Fragment Identifier (precise reading position) |
| **Journey Trail** | History of entities visited across Reader and SiYuan |

### References

- **Critical Evaluation:** `04-critical-evaluation.md` (30 UX issues)
- **Flow Mode Blueprint:** `05-flow-mode-blueprint.md` (Graph visualization spec)
- **Design System Spec:** `06-design-system-spec.md` (Tokens & components)
- **Architecture Doc:** `../ARCHITECTURE-AND-INTERACTIONS.md` (API routes)
- **Gap Analysis:** `../GAP-ANALYSIS-2025-12-09.md` (Implementation status)

### Tools & Libraries

| Tool | Purpose | Version |
|------|---------|---------|
| D3.js | Graph visualization | v7.8+ |
| React | IES Reader UI | v18.2+ |
| Svelte | SiYuan plugin UI | v4.2+ |
| Storybook | Component documentation | v7.6+ |
| Jest | Unit testing | v29.7+ |
| Playwright | E2E testing | v1.40+ |
| Chromatic | Visual regression | Latest |
| axe-devtools | Accessibility testing | Latest |

---

**Document Status:** ACTIVE
**Next Review:** 2025-12-16 (after Phase 0 completion)
**Maintained By:** Frontend Lead
**Approved By:** PM, Designer, Architect
