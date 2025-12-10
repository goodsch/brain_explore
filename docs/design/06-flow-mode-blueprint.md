# Flow Mode Interaction Blueprint

**Version:** 1.0
**Date:** 2025-12-09
**Status:** Design Specification

---

## Executive Summary

This document specifies a complete redesign of Flow Mode's interaction model, transitioning from card-based lists to a spatial graph interface. The design synthesizes best practices from 9 leading knowledge graph tools while introducing novel "movement through knowledge" patterns optimized for cognitive flow states.

**Core Innovation:** Radial focus navigation with semantic zoom and persistent spatial memory, enabling intuitive exploration of 200+ entity graphs at 60fps.

**Critical Problem Solved:** Current Flow Mode has NO graph visualization—only card lists. Users cannot see relationships spatially, breaking the cognitive model of "exploring a knowledge landscape."

---

## 1. Core Visual Structure

### 1.1 Radial Focus View (TheBrain-Inspired)

**Layout Algorithm:**
```
Center: Active entity (selected)
Ring 1 (r=200px): 1-hop related entities (6-12 nodes max)
Ring 2 (r=400px): 2-hop related entities (20-30 nodes max)
```

**Directional Semantics:**
- **Above (12 o'clock):** Causes, prerequisites, parent categories
- **Below (6 o'clock):** Effects, consequences, child categories
- **Left/Right (3/9 o'clock):** Related concepts, lateral connections
- **Diagonals:** Mixed relationships

**Visual Encoding:**
- Node size: Importance score (16px-48px diameter)
- Node color: Entity type (14 types, consistent palette)
- Edge thickness: Relationship strength (1px-4px)
- Edge style: Relationship type (solid, dashed, dotted)

**Example State:**
```
Active: "Cognitive Load Theory"
├─ Above: "Working Memory" (cause)
├─ Below: "Multimedia Learning" (effect)
├─ Left: "Schema Theory" (related)
└─ Right: "Attention Management" (related)
```

### 1.2 Always-Visible Minimap (Kinopio-Inspired)

**Position:** Bottom-right corner, 180x120px
**Appearance:**
- Semi-transparent background (rgba(0,0,0,0.8))
- Entity clusters as colored dots
- Viewport as highlighted rectangle
- Zoom level indicator

**Interactions:**
- Click: Jump to location
- Drag: Pan main canvas
- Scroll: Zoom main canvas

**Performance:**
- Simplified rendering (no labels, fixed LOD)
- Update on viewport change only (debounced 100ms)

### 1.3 Three-Layer Semantic Zoom

**Layer 1: Overview (Zoom 0.2-0.5)**
```
┌─────────────────────────────┐
│   [Cluster]   [Cluster]     │
│      10          8          │
│                             │
│   [Cluster]   [Cluster]     │
│      15          12         │
└─────────────────────────────┘
```
- Show entity type clusters
- Display count per cluster
- No individual labels
- Force-directed layout

**Layer 2: Navigation (Zoom 0.5-1.5)**
```
┌─────────────────────────────┐
│  Working Memory ─── Schema  │
│       │              │      │
│   Cognitive ─── Attention   │
│    Load           Mgmt      │
└─────────────────────────────┘
```
- Show entity labels
- Show relationship lines
- Show entity type icons
- Radial focus active

**Layer 3: Detail (Zoom 1.5-3.0)**
```
┌─────────────────────────────┐
│  Working Memory             │
│  ┌─────────────────────┐    │
│  │ Limited capacity... │    │
│  │ 7±2 chunks...       │    │
│  └─────────────────────┘    │
│       │                     │
│   Cognitive Load Theory     │
└─────────────────────────────┘
```
- Show content previews
- Show facets as badges
- Show source indicators
- Show relationship labels

---

## 2. Navigation Interactions

### 2.1 Gesture-First Navigation

**Touch/Trackpad Gestures:**
```typescript
// Pinch Zoom → Semantic Zoom
if (pinchDelta < -50) {
  // Zoom out: Navigate → Overview
  transitionToZoomLevel('overview', 500)
} else if (pinchDelta > 50) {
  // Zoom in: Navigate → Detail
  transitionToZoomLevel('detail', 500)
}

// Two-Finger Pan → Canvas Pan
canvas.translate(deltaX, deltaY)
clampToGraphBounds() // Prevent scrolling to empty space

// Hover → Preview
if (hoverDuration > 300ms) {
  showTooltip(entity)
  highlightConnections(entity, 1) // 1-hop highlight
}
```

**Mouse Interactions:**
- **Single-click:** Select entity → Update radial view (500ms animated)
- **Double-click:** Expand entity → Open detail panel
- **Right-click:** Context menu (Pin, Hide, Explore, Add to Journey)
- **Drag node:** Pin entity position (persists to local storage)
- **Drag canvas:** Pan viewport
- **Scroll:** Zoom (with semantic zoom transitions)

**Spatial Memory:**
- Pinned positions saved per user
- Unpinned entities use force-directed layout
- Pinned entities act as anchors for force simulation

### 2.2 Keyboard Shortcuts

**Primary Navigation:**
```
Arrow Keys    Navigate to adjacent entities (by direction)
Enter         Select entity / Expand detail
Escape        Navigate back (pop journey trail)
Space         Toggle detail panel
```

**View Modes:**
```
G             Switch to Graph view (default)
L             Switch to List view (filterable)
T             Switch to Timeline view (temporal)
M             Toggle Minimap visibility
F             Toggle fullscreen
```

**Quick Actions:**
```
/             Open search (fuzzy entity search)
P             Open pins/bookmarks panel
?             Show keyboard shortcuts overlay
Cmd+Z         Undo (navigate back)
Cmd+Shift+Z   Redo (navigate forward)
```

**Filters:**
```
1-9           Toggle entity type filter (by number)
Shift+1-9     Isolate single entity type
A             Show all types
D             Set depth filter (1-hop, 2-hop, 3-hop)
```

### 2.3 Multi-Modal Navigation

**Graph View (Default):**
- Radial focus + force-directed layout
- Visual spatial reasoning
- Optimized for exploration

**List View (Filterable):**
```
┌─────────────────────────────────────┐
│ 📊 Entity Type Filters              │
├─────────────────────────────────────┤
│ □ Concept (45)                      │
│ ☑ Theory (12)                       │
│ ☑ Framework (8)                     │
│ □ Person (23)                       │
│ □ Spark (156)                       │
├─────────────────────────────────────┤
│ Search: [cognitive____________]     │
├─────────────────────────────────────┤
│ ⚡ Cognitive Load Theory            │
│    Related: 8 entities              │
│                                     │
│ 📖 Cognitive Apprenticeship         │
│    Related: 6 entities              │
└─────────────────────────────────────┘
```

**Timeline View (Temporal):**
```
┌─────────────────────────────────────┐
│ Dec 8, 2:34 PM                      │
│ ├─ Opened "Cognitive Load Theory"  │
│ └─ Explored "Working Memory"        │
│                                     │
│ Dec 8, 2:15 PM                      │
│ ├─ Created Spark: "Attention..."   │
│ └─ Linked to "Multimedia Learning" │
└─────────────────────────────────────┘
```

**Search (Direct Access):**
- Fuzzy search across entity names
- Type-ahead suggestions
- Recent entities priority
- Keyboard-first (Cmd+K style)

**Pins/Bookmarks:**
- Starred entities for quick access
- Organized by entity type
- Drag to reorder
- Persistent across sessions

---

## 3. Spatial Memory Features

### 3.1 Position Persistence

**Storage Schema:**
```typescript
interface PinnedPosition {
  entityId: string
  x: number
  y: number
  isPinned: boolean
  pinnedAt: string
}

// Local Storage: flow_mode_positions_v1
{
  "user_123": {
    "entity_456": { x: 200, y: 300, isPinned: true, pinnedAt: "2025-12-09T..." },
    "entity_789": { x: -100, y: 150, isPinned: true, pinnedAt: "2025-12-09T..." }
  }
}
```

**Pin Interactions:**
- Right-click → "Pin Position"
- Drag pinned entity → Update position
- Unpinned entities use force-directed layout
- Pinned entities excluded from force simulation

### 3.2 Directional Consistency

**Causal Relationships Always Vertical:**
```
  [Cause/Parent]
        │
        ↓
  [Effect/Child]
```

**Lateral Relationships Always Horizontal:**
```
[Related] ←──→ [Related]
```

**Mixed Relationships Use Diagonals:**
```
  [Parent]
      ╲
       ↘
  [Sibling]
```

### 3.3 Breadcrumb Trail Visualization

**Position:** Top-left, below header
**Appearance:**
```
Home > Cognitive Science > Working Memory > Current Entity
  ↑         ↑                  ↑               ↑
 Click    Click              Click         (active)
```

**Spatial Highlight:**
- Hover breadcrumb → Highlight entity in graph
- Click breadcrumb → Animate to that entity (500ms)

### 3.4 Canvas Boundaries

**Constraint Strategy:**
- Calculate graph bounding box
- Add 200px padding on all sides
- Clamp pan offset to padded bounds
- Prevent scrolling to empty space

**Offscreen Indicators:**
```
┌─────────────────────────────────────┐
│         ↑ 3 entities                │
│                                     │
│   [Visible Entities]                │
│                                     │
│ ← 5  [Current View]        2 →      │
│                                     │
│         ↓ 4 entities                │
└─────────────────────────────────────┘
```

### 3.5 Return to Origin

**Button:** Floating action button (bottom-left)
**Action:** Animate to first entity in journey (home position)
**Shortcut:** `H` key

---

## 4. Animation & Physics

### 4.1 Entity Selection Transition

**Duration:** 500ms
**Easing:** Spring (stiffness=100, damping=20)

```typescript
// Selection Flow:
1. User clicks entity
2. Current entity scales down to 0.8x (100ms)
3. Camera pans to new entity (400ms)
4. New entity scales up to 1.2x, then 1.0x (100ms)
5. Related entities fade in radially (200ms)
```

**Visual Feedback:**
```
t=0ms:     [Old Entity] (scale: 1.0)
t=100ms:   [Old Entity] (scale: 0.8, opacity: 0.6)
t=300ms:   Camera panning... [New Entity] approaching center
t=500ms:   [New Entity] (scale: 1.2, opacity: 1.0)
t=600ms:   [New Entity] (scale: 1.0) ← Final state
```

### 4.2 Relationship Reveal Animation

**Trigger:** Entity selection or filter change
**Sequence:**
```typescript
1. Hide old connections (fade out 100ms)
2. Compute new layout (force simulation)
3. Fade in new nodes (200ms, stagger 20ms each)
4. Draw connection lines (spring physics, 300ms)
```

**Spring Physics Parameters:**
```typescript
{
  charge: -200,        // Node repulsion
  linkDistance: 150,   // Preferred edge length
  collisionRadius: 30, // Prevent overlap
  alphaDecay: 0.02     // Simulation speed
}
```

### 4.3 Layout Morphing

**Use Case:** Switching between view modes
**Strategy:** Morph, not replace

```typescript
// Graph → List transition:
1. Fade out edges (100ms)
2. Tween node positions to list layout (400ms, ease-in-out)
3. Fade in list UI (200ms)

// Preserve relative positions:
// - Top entities stay at top
// - Bottom entities stay at bottom
// - Left/right collapsed to center
```

### 4.4 Hover States

**Entity Hover:**
```css
transform: scale(1.1);
box-shadow: 0 4px 12px rgba(0,0,0,0.3);
transition: all 150ms ease-out;
```

**Connection Highlight:**
- 1-hop edges: opacity 1.0, width +1px
- 2-hop edges: opacity 0.3
- Other edges: opacity 0.1

### 4.5 Force-Directed Layout

**D3-Force Configuration:**
```typescript
simulation
  .force('charge', d3.forceManyBody().strength(-200))
  .force('link', d3.forceLink().distance(150))
  .force('collision', d3.forceCollide().radius(30))
  .force('center', d3.forceCenter(width/2, height/2))
  .force('radial', d3.forceRadial(200, activeX, activeY)) // Radial focus
  .alphaDecay(0.02)
  .velocityDecay(0.3)
```

**Pinned Entity Handling:**
```typescript
// Exclude pinned entities from force simulation
node.fx = isPinned ? pinnedX : null
node.fy = isPinned ? pinnedY : null
```

---

## 5. Information Architecture

### 5.1 Layout Specification

```
┌──────────────────────────────────────────────────────────────────┐
│ [IES Logo] Breadcrumbs > Trail > Current    [Search] [User] [?] │ 60px
├──────────────────────────────────────────────────────────────────┤
│ Filters: [All] [Concept] [Theory] [Spark]   Depth: [2-hop ▼]   │ 48px
│ Mode: [● Graph] [ List] [ Timeline]         [ Return Home 🏠]   │
├──────────────────────────────────────────────────────────────────┤
│  ┌────────┐                                                     │
│  │ Mini-  │   ╔════════════════════════════════════╗            │
│  │ map    │   ║                                    ║            │
│  │        │   ║     [Related]    [Related]         ║            │
│  │ [□]    │   ║          ╲          ╱              ║            │
│  │        │   ║           [Active]                 ║  Main      │
│  └────────┘   ║          ╱          ╲              ║  Canvas    │
│  180x120px    ║     [Related]    [Related]         ║            │
│               ║                                    ║            │
│               ╚════════════════════════════════════╝            │
│                                                                  │
│  [Return 🏠]                                    [+ New Entity]  │ FAB
├──────────────────────────────────────────────────────────────────┤
│ Detail Panel (collapsible, 300px height)                        │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ [▼ Cognitive Load Theory]              [Pin] [Hide] [Edit]  ││
│ │ ─────────────────────────────────────────────────────────────││
│ │ Tabs: [Description] [Facets] [Relationships] [Sources]      ││
│ │                                                              ││
│ │ Working memory has limited capacity for processing...       ││
│ │                                                              ││
│ │ Facets: #education #cognitive-science #design-principles    ││
│ │ Sources: Book: "E-Learning and the Science of Instruction"  ││
│ └──────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
```

### 5.2 Component Hierarchy

```
FlowModeGraph (root)
├─ Header
│  ├─ Breadcrumbs
│  ├─ SearchBar
│  └─ UserMenu
├─ Toolbar
│  ├─ EntityTypeFilters
│  ├─ DepthFilter
│  ├─ ViewModeTabs
│  └─ ReturnHomeButton
├─ GraphCanvas
│  ├─ SVGLayer (edges)
│  ├─ EntityNodes (HTML overlay)
│  └─ Minimap
├─ DetailPanel
│  ├─ EntityHeader
│  ├─ TabBar
│  └─ ContentArea
└─ FloatingActionButtons
   ├─ ReturnHomeButton
   └─ CreateEntityButton
```

### 5.3 Responsive Breakpoints

**Desktop (>1024px):**
- Full layout as shown above
- Detail panel 300px height (collapsible)
- Minimap 180x120px

**Tablet (768px-1024px):**
- Minimap 120x80px
- Detail panel slides from bottom (sheet style)
- Toolbar wraps to 2 rows

**Mobile (<768px):**
- Graph view only (no minimap)
- Detail panel fullscreen modal
- Bottom sheet for filters
- Gesture-first navigation

---

## 6. State Management

### 6.1 Global State Schema

```typescript
interface FlowModeState {
  // Active Selection
  activeEntityId: string | null
  activeEntity: Entity | null

  // Journey Tracking
  journeyTrail: JourneyTrailItem[] // Max 50, newest first
  currentJourneyIndex: number // For undo/redo navigation

  // Spatial Memory
  pinnedEntities: Record<string, PinnedPosition>

  // Filter State
  filterState: {
    entityTypes: Set<EntityType> // Which types are visible
    depth: 1 | 2 | 3 // Hop distance from active entity
    facets: string[] // Facet filters
    searchQuery: string
  }

  // View Configuration
  viewMode: 'graph' | 'list' | 'timeline'
  zoomLevel: 'overview' | 'navigation' | 'detail'

  // Camera State
  camera: {
    x: number // Pan offset X
    y: number // Pan offset Y
    scale: number // Zoom scale (0.2-3.0)
  }

  // Graph Data
  visibleEntities: Entity[] // Filtered by depth + type
  visibleRelationships: Relationship[]

  // UI State
  detailPanelOpen: boolean
  minimapVisible: boolean
  isLoading: boolean
}
```

### 6.2 Zustand Store Actions

```typescript
interface FlowModeActions {
  // Navigation
  selectEntity: (entityId: string) => void
  navigateBack: () => void
  navigateForward: () => void
  returnToHome: () => void

  // Filters
  toggleEntityType: (type: EntityType) => void
  setDepth: (depth: 1 | 2 | 3) => void
  setSearchQuery: (query: string) => void

  // View
  setViewMode: (mode: ViewMode) => void
  setZoomLevel: (level: ZoomLevel) => void
  panCamera: (deltaX: number, deltaY: number) => void
  zoomCamera: (scale: number) => void

  // Spatial Memory
  pinEntity: (entityId: string, x: number, y: number) => void
  unpinEntity: (entityId: string) => void

  // Data Loading
  loadEntitiesInRadius: (entityId: string, depth: number) => Promise<void>
  refreshGraph: () => Promise<void>
}
```

### 6.3 Session Sync Integration

**Sync Strategy:**
```typescript
// Write to backend every 3 seconds (debounced)
useEffect(() => {
  const syncState = debounce(() => {
    patchSessionState({
      current_entity_id: activeEntityId,
      current_entity_name: activeEntity?.name,
      journey_trail: journeyTrail.slice(0, 10), // Last 10 items only
      last_app_source: 'siyuan'
    })
  }, 3000)

  syncState()
}, [activeEntityId, journeyTrail])

// Poll from backend every 5 seconds (read-only for remote changes)
useInterval(() => {
  const remoteState = await getSessionState()
  if (remoteState.last_app_source === 'reader') {
    // Reader made a change, update local state
    setJourneyTrail(remoteState.journey_trail)
  }
}, 5000)
```

---

## 7. Performance Considerations

### 7.1 Entity Limiting

**Default Configuration:**
```typescript
const PERFORMANCE_LIMITS = {
  maxVisibleEntities: 200,
  defaultDepth: 2,
  maxDepth: 3,
  forceSimulationTicks: 300,
  debounceMs: 100
}
```

**Depth Filtering:**
```
1-hop: Active + 1st-degree neighbors (10-20 entities)
2-hop: Active + 1st + 2nd-degree neighbors (50-100 entities)
3-hop: Active + 1st + 2nd + 3rd-degree neighbors (150-200 entities)
```

**User Warning:**
```
If entity count > 200:
┌────────────────────────────────────┐
│ ⚠️ Large Graph Detected            │
├────────────────────────────────────┤
│ This view has 347 entities.        │
│ Performance may be reduced.        │
│                                    │
│ [Reduce to 2-hop] [Filter Types]  │
└────────────────────────────────────┘
```

### 7.2 Lazy Loading Strategy

**On Entity Selection:**
```typescript
async function selectEntity(entityId: string) {
  // 1. Update active entity immediately (cached)
  setActiveEntity(cachedEntities.get(entityId))

  // 2. Load 1-hop neighbors (fast)
  const oneHop = await fetchRelatedEntities(entityId, 1)
  setVisibleEntities([activeEntity, ...oneHop])

  // 3. Load 2-hop neighbors (background)
  const twoHop = await fetchRelatedEntities(entityId, 2)
  setVisibleEntities([activeEntity, ...oneHop, ...twoHop])
}
```

**Caching Strategy:**
```typescript
// LRU Cache for entities (max 500)
const entityCache = new LRU<string, Entity>(500)

// Prefetch on hover (300ms delay)
onEntityHover((entityId) => {
  setTimeout(() => {
    if (!entityCache.has(entityId)) {
      fetchEntity(entityId).then(e => entityCache.set(entityId, e))
    }
  }, 300)
})
```

### 7.3 Level-of-Detail Rendering

**Zoom-Based LOD:**
```typescript
function getEntityLOD(zoomLevel: number, entitySize: number): LOD {
  if (zoomLevel < 0.5) {
    return 'dot' // Just a colored circle
  } else if (zoomLevel < 1.0) {
    return 'icon' // Icon + label
  } else {
    return 'full' // Icon + label + facets
  }
}
```

**Rendering Optimization:**
```typescript
// Only render entities in viewport + 200px margin
const visibleEntities = entities.filter(entity => {
  const isInViewport = isRectInViewport(
    entity.x - 50,
    entity.y - 50,
    100,
    100,
    camera,
    200 // margin
  )
  return isInViewport
})
```

### 7.4 Target Performance

**Metrics:**
- 60fps animation (16.67ms per frame)
- <100ms interaction latency (click to visual response)
- <500ms entity selection transition
- <1s graph layout computation (200 entities)

**Monitoring:**
```typescript
// Performance monitoring
const metrics = {
  fps: measureFPS(),
  entityCount: visibleEntities.length,
  renderTime: measureRenderTime(),
  layoutTime: measureLayoutTime()
}

if (metrics.fps < 30 || metrics.renderTime > 50) {
  console.warn('Performance degraded', metrics)
  // Suggest reducing depth or entity count
}
```

### 7.5 WebGL Rendering Decision

**Criteria for WebGL:**
```
IF entity_count > 500 OR fps < 30:
  Use WebGL renderer (Pixi.js or Three.js)
ELSE:
  Use SVG + HTML (simpler, more flexible)
```

**Recommended Libraries:**
- **Pixi.js:** 2D WebGL renderer, good for 1000+ entities
- **Three.js:** 3D renderer (overkill for 2D graph)
- **react-force-graph:** D3 + Three.js integration

**Phase 1 Implementation:**
- Start with SVG + HTML (simpler)
- Add WebGL renderer if performance issues arise

---

## 8. Technology Recommendations

### 8.1 Core Libraries

**Graph Layout:**
```json
{
  "d3-force": "^3.0.0",           // Force-directed layout
  "d3-zoom": "^3.0.0",            // Pan/zoom behavior
  "d3-selection": "^3.0.0",       // DOM manipulation
  "d3-interpolate": "^3.0.0"      // Animation tweening
}
```

**React Integration:**
```json
{
  "@react-sigma/core": "^4.0.0",  // (Alternative: Pre-built graph)
  "react-force-graph": "^1.43.0", // (Alternative: D3 wrapper)
  "react-use-gesture": "^9.1.3",  // Gesture handling
  "framer-motion": "^10.16.4"     // UI animations (already used)
}
```

**State Management:**
```json
{
  "zustand": "^4.4.7"             // Already used in project
}
```

### 8.2 Implementation Approaches

**Option A: D3 + Custom React Components (Recommended)**
- **Pros:** Full control, matches existing patterns, lightweight
- **Cons:** More implementation work
- **Complexity:** Medium

**Option B: react-force-graph**
- **Pros:** Battle-tested, WebGL support, less code
- **Cons:** Less flexibility, harder to customize
- **Complexity:** Low

**Option C: @react-sigma/core**
- **Pros:** Mature, good performance, React-first
- **Cons:** Opinionated API, learning curve
- **Complexity:** Medium

**Recommendation:** Start with **Option A** for maximum control and consistency with existing codebase.

### 8.3 File Structure

```
ies/plugin/src/components/flow-mode/
├─ FlowModeGraph.svelte           # Root component
├─ graph/
│  ├─ GraphCanvas.svelte          # SVG + HTML graph
│  ├─ EntityNode.svelte           # Single entity node
│  ├─ RelationshipEdge.svelte     # Connection line
│  ├─ Minimap.svelte              # Overview map
│  └─ useForceLayout.ts           # D3 force simulation hook
├─ toolbar/
│  ├─ EntityTypeFilters.svelte
│  ├─ DepthFilter.svelte
│  ├─ ViewModeTabs.svelte
│  └─ SearchBar.svelte
├─ detail/
│  ├─ DetailPanel.svelte
│  ├─ EntityDescription.svelte
│  ├─ FacetsList.svelte
│  └─ RelationshipsList.svelte
├─ stores/
│  ├─ flowGraphStore.ts           # Zustand store
│  └─ spatialMemoryStore.ts       # Pinned positions
└─ utils/
   ├─ graphLayout.ts              # Layout algorithms
   ├─ animations.ts               # Spring physics
   └─ performance.ts              # FPS monitoring
```

---

## 9. Wireframes

### 9.1 Default Radial View (Desktop)

```
┌────────────────────────────────────────────────────────────────┐
│ IES > Cognitive Science > Working Memory      [Search] [User]  │
├────────────────────────────────────────────────────────────────┤
│ [All] [Concept] [Theory] [Spark]  Depth: [● 2-hop] [ 3-hop]   │
│ Mode: [● Graph] [ List] [ Timeline]                            │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│              Schema Theory                                      │
│                   ●                                             │
│                    \                                            │
│                     \                                           │
│     Working Memory ──●── Cognitive Load Theory                 │
│            ●            /        (ACTIVE)                       │
│             \          /                                        │
│              \        /                                         │
│               ●──────●                                          │
│          Attention   Multimedia                                │
│                      Learning                                   │
│                                                                 │
│  ┌──────┐                                                      │
│  │ ┌─┐  │                                          [Return 🏠] │
│  │ │■│  │← Minimap                                             │
│  │ └─┘  │                                                      │
│  └──────┘                                                      │
├────────────────────────────────────────────────────────────────┤
│ ▼ Cognitive Load Theory              [Pin] [Hide] [Edit]      │
│ ───────────────────────────────────────────────────────────────│
│ [Description] [Facets] [Relationships] [Sources] [Questions]   │
│                                                                 │
│ Working memory has limited capacity for processing new         │
│ information. When cognitive load exceeds capacity...           │
│                                                                 │
│ Facets: #education #cognitive-science #instructional-design    │
└────────────────────────────────────────────────────────────────┘
```

### 9.2 Zoomed Out Overview

```
┌────────────────────────────────────────────────────────────────┐
│ IES > All Entities                            [Search] [User]  │
├────────────────────────────────────────────────────────────────┤
│ [All] [Concept] [Theory]  Zoom: [● Overview] [ Navigation]    │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│     ┌─────────┐                 ┌─────────┐                    │
│     │ Theory  │                 │ Concept │                    │
│     │   12    │                 │   45    │                    │
│     └─────────┘                 └─────────┘                    │
│                                                                 │
│                   ┌─────────┐                                  │
│                   │  Spark  │                                  │
│                   │   156   │                                  │
│                   └─────────┘                                  │
│                                                                 │
│     ┌─────────┐                 ┌─────────┐                    │
│     │Framework│                 │ Person  │                    │
│     │    8    │                 │   23    │                    │
│     └─────────┘                 └─────────┘                    │
│                                                                 │
│  ┌──────┐                                                      │
│  │ ■    │← Minimap shows full graph                           │
│  └──────┘                                           [Zoom In]  │
└────────────────────────────────────────────────────────────────┘
```

### 9.3 Zoomed In Detail View

```
┌────────────────────────────────────────────────────────────────┐
│ IES > Cognitive Science > Cognitive Load Theory   [Back] [Pin] │
├────────────────────────────────────────────────────────────────┤
│ Zoom: [ Overview] [ Navigation] [● Detail]          [Zoom Out] │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────────────────────────────────┐                │
│   │ Working Memory                           │                │
│   │ ┌──────────────────────────────────────┐ │                │
│   │ │ Limited capacity (7±2 chunks)        │ │                │
│   │ │ Duration: 15-30 seconds              │ │                │
│   │ └──────────────────────────────────────┘ │                │
│   │ #cognitive-science #memory               │                │
│   │ Sources: Baddeley (1992), Miller (1956) │                │
│   └──────────────────────────────────────────┘                │
│                      │                                         │
│                      │ "Causes"                                │
│                      ↓                                         │
│   ┌──────────────────────────────────────────┐                │
│   │ ★ Cognitive Load Theory                  │                │
│   │ ┌──────────────────────────────────────┐ │                │
│   │ │ Instructional design framework...    │ │                │
│   │ │ Three types: intrinsic, extraneous,  │ │                │
│   │ │ germane cognitive load               │ │                │
│   │ └──────────────────────────────────────┘ │                │
│   │ #education #design-principles            │                │
│   │ Sources: Sweller (1988, 1994, 2011)     │                │
│   └──────────────────────────────────────────┘                │
│                      │                                         │
│                      │ "Influences"                            │
│                      ↓                                         │
│   ┌──────────────────────────────────────────┐                │
│   │ Multimedia Learning                      │                │
│   │ ┌──────────────────────────────────────┐ │                │
│   │ │ Dual-channel processing...           │ │                │
│   │ └──────────────────────────────────────┘ │                │
│   └──────────────────────────────────────────┘                │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 9.4 Mobile Layout (Bottom Sheet)

```
┌────────────────────────────┐
│ IES  [≡] [Search] [User]   │
├────────────────────────────┤
│                            │
│        Schema              │
│          ●                 │
│           \                │
│            \               │
│  Working ───●── Cognitive  │
│  Memory         Load       │
│                (ACTIVE)    │
│             /              │
│            /               │
│           ●                │
│      Attention             │
│                            │
│ (Pinch to zoom)            │
│ (Swipe up for detail)      │
│                            │
├────────────────────────────┤
│ ═══  Swipe up ═══          │ ← Handle
├────────────────────────────┤
│ Cognitive Load Theory      │
│ ──────────────────────────│
│ Working memory has...      │
│                            │
│ [Description] [Related]    │
│ [Sources] [Questions]      │
└────────────────────────────┘
```

### 9.5 List View Fallback

```
┌────────────────────────────────────────────────────────────────┐
│ IES > Cognitive Science                       [Search] [User]  │
├────────────────────────────────────────────────────────────────┤
│ [All] [Concept] [Theory] [Spark]                               │
│ Mode: [ Graph] [● List] [ Timeline]                            │
├────────────────────────────────────────────────────────────────┤
│ Search: [cognitive________________]         Sort: [Name ▼]     │
├────────────────────────────────────────────────────────────────┤
│ ☑ Theory (12)                                                  │
│   ├─ ⚡ Cognitive Load Theory                                  │
│   │   Related: Working Memory, Schema Theory (+6 more)         │
│   │   Sources: Sweller (1988, 1994, 2011)                      │
│   │                                                             │
│   ├─ ⚡ Cognitive Apprenticeship                               │
│   │   Related: Situated Learning, Scaffolding (+4 more)        │
│   │                                                             │
│   └─ ⚡ Constructivism                                          │
│       Related: Piaget, Schema Theory (+8 more)                 │
│                                                                 │
│ ☑ Concept (45)                                                 │
│   ├─ 📖 Working Memory                                         │
│   │   Related: Cognitive Load Theory, Attention (+3 more)      │
│   │                                                             │
│   ├─ 📖 Schema Theory                                          │
│   │   Related: Cognitive Load Theory, Constructivism (+5 more) │
│   │                                                             │
│   └─ ...                                                        │
│                                                                 │
│ [Load More...]                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 10. Comparison to Current State

### 10.1 Current Implementation (As-Is)

**File:** `.worktrees/siyuan/ies/plugin/src/components/FlowMode.svelte` (113KB)

**Visual Structure:**
```
┌────────────────────────────────────────┐
│ Entity: [Cognitive Load Theory  ▼]    │ ← Dropdown only
├────────────────────────────────────────┤
│ Related Entities:                      │
│ ┌────────────────────────────────────┐ │
│ │ □ Working Memory                   │ │
│ │   Type: Concept                    │ │
│ │   Relationship: Causes             │ │
│ │                                    │ │
│ │ □ Schema Theory                    │ │
│ │   Type: Theory                     │ │
│ │   Relationship: Related            │ │
│ │                                    │ │
│ │ □ Multimedia Learning              │ │
│ │   Type: Concept                    │ │
│ │   Relationship: Influences         │ │
│ └────────────────────────────────────┘ │
│                                        │
│ (Scrollable list, no spatial layout)  │
└────────────────────────────────────────┘
```

**Problems:**
1. **No graph visualization** — Just a list of cards
2. **No spatial relationships** — Can't see how entities relate spatially
3. **No navigation flow** — Must use dropdown to select entities
4. **No breadcrumb trail** — Can't see exploration path
5. **No minimap** — Can't see global context
6. **No zoom** — Single level of detail
7. **No animations** — Instant updates, jarring transitions
8. **Limited filtering** — Basic entity type checkboxes
9. **No spatial memory** — Can't pin entities or return to previous positions

### 10.2 Proposed Implementation (To-Be)

**Visual Structure:**
```
┌────────────────────────────────────────────────────────────────┐
│ Breadcrumbs > Trail > Current            [Search] [Filters]    │
├────────────────────────────────────────────────────────────────┤
│                  Radial Focus Graph                            │
│                                                                 │
│              Working Memory                                     │
│                   ●                                             │
│                    \                                            │
│                     \                                           │
│        Schema ──────●────── Cognitive Load Theory              │
│        Theory              (ACTIVE, centered)                   │
│                           /                                     │
│                          /                                      │
│                         ●                                       │
│                  Multimedia Learning                            │
│                                                                 │
│  [Minimap]                                     [Return Home]   │
└────────────────────────────────────────────────────────────────┘
```

**Improvements:**
1. ✅ **Spatial graph visualization** — See all entities and relationships
2. ✅ **Radial focus layout** — Active entity centered, related in rings
3. ✅ **Animated navigation** — Smooth transitions between entities
4. ✅ **Breadcrumb trail** — Visual history of exploration path
5. ✅ **Minimap** — Global context always visible
6. ✅ **Semantic zoom** — Three levels (overview, navigation, detail)
7. ✅ **Spring physics** — Natural movement and layout
8. ✅ **Advanced filtering** — Type, depth, facets, search
9. ✅ **Spatial memory** — Pin entities, return to home

### 10.3 Migration Strategy

**Phase 1: Core Graph (Week 1-2)**
- Implement GraphCanvas with D3-force
- Add EntityNode and RelationshipEdge components
- Add basic pan/zoom
- Wire to existing FlowMode data

**Phase 2: Radial Focus (Week 3)**
- Add radial layout algorithm
- Implement entity selection transitions
- Add breadcrumb trail
- Integrate with session sync

**Phase 3: Polish (Week 4)**
- Add minimap
- Add semantic zoom
- Add animations and spring physics
- Add spatial memory (pinning)

**Phase 4: Optimization (Week 5)**
- Performance monitoring
- Lazy loading
- Level-of-detail rendering
- WebGL fallback if needed

**Backward Compatibility:**
- Keep existing FlowMode as "List View" fallback
- Add view mode toggle (Graph | List | Timeline)
- Preserve all existing API contracts

---

## 11. Open Questions & Design Decisions

### 11.1 Unresolved Questions

**Q1: Should we use WebGL from the start or optimize SVG first?**
- **Recommendation:** Start with SVG + HTML for simplicity, add WebGL only if performance degrades.

**Q2: How do we handle entity types with no spatial semantics (e.g., Spark)?**
- **Recommendation:** Use force-directed layout for non-causal relationships, reserve directional semantics for causal/hierarchical relationships only.

**Q3: Should minimap be toggleable or always visible?**
- **Recommendation:** Always visible by default, add toggle for power users (M key).

**Q4: How do we prevent graph layout from "jumping" when filters change?**
- **Recommendation:** Use morphing transitions (tween positions) instead of re-layout from scratch.

**Q5: Should we support 3D graph visualization?**
- **Recommendation:** No. 2D is sufficient and less cognitively demanding. 3D adds complexity without clear benefit.

### 11.2 Design Principles

**Principle 1: Spatial Consistency**
> Once a user learns where an entity is, it should stay there unless explicitly moved.

**Principle 2: Progressive Disclosure**
> Show overview first, reveal details on demand. Never overwhelm with information.

**Principle 3: Smooth Transitions**
> Every state change should be animated. Instant updates break spatial memory.

**Principle 4: Minimal Friction**
> Most actions should require one click/gesture. Common actions should have keyboard shortcuts.

**Principle 5: Always Show Context**
> User should always know: Where am I? Where did I come from? Where can I go?

---

## 12. Success Metrics

### 12.1 Usability Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Time to find related entity | <5 seconds | User testing: "Find all effects of Cognitive Load Theory" |
| Navigation errors (dead ends) | <10% | Analytics: % of navigations leading to back button |
| Session duration | >5 minutes | Analytics: Average time in Flow Mode |
| Return usage | >30% | Analytics: % of sessions using Return Home button |

### 12.2 Performance Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Frame rate | 60fps | Performance monitoring |
| Entity selection latency | <100ms | Click → visual response |
| Layout computation | <1s (200 entities) | Time to settle force simulation |
| Render time | <16ms per frame | requestAnimationFrame profiling |

### 12.3 Adoption Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Flow Mode usage | >50% of sessions | Analytics: % sessions using Flow vs Forge |
| Graph view preference | >80% | Analytics: Graph vs List view time |
| Entity depth explored | >2 hops | Analytics: Average journey trail length |
| Pinned entities | >5 per user | Analytics: Average pinned entity count |

---

## 13. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up D3-force + React integration
- [ ] Implement GraphCanvas component
- [ ] Add EntityNode and RelationshipEdge rendering
- [ ] Wire to existing FlowMode API
- [ ] Add basic pan/zoom

**Deliverable:** Basic graph visualization with pan/zoom

### Phase 2: Radial Focus (Week 3)
- [ ] Implement radial layout algorithm
- [ ] Add entity selection transitions (500ms spring)
- [ ] Add breadcrumb trail component
- [ ] Integrate with session sync API
- [ ] Add "Return Home" button

**Deliverable:** Radial focus navigation with breadcrumbs

### Phase 3: Advanced Features (Week 4)
- [ ] Add minimap component
- [ ] Implement semantic zoom (3 levels)
- [ ] Add animation system (spring physics)
- [ ] Add spatial memory (pinning)
- [ ] Add view mode tabs (Graph | List | Timeline)

**Deliverable:** Full-featured spatial graph

### Phase 4: Polish & Optimization (Week 5)
- [ ] Add keyboard shortcuts
- [ ] Implement performance monitoring
- [ ] Add lazy loading and LOD rendering
- [ ] Mobile responsive layout
- [ ] User onboarding tutorial

**Deliverable:** Production-ready Flow Mode 2.0

---

## 14. References & Inspiration

### 14.1 Competitive Analysis Sources

| Tool | Key Innovation | Implemented |
|------|----------------|-------------|
| **TheBrain** | Radial focus view, directional semantics | ✅ Core concept |
| **Kinopio** | Infinite canvas, always-visible minimap | ✅ Minimap |
| **Heptabase** | Pinned positions, spatial memory | ✅ Pinning |
| **Roam Research** | Bidirectional links, breadcrumbs | ✅ Breadcrumbs |
| **Obsidian** | Graph view, zoom levels | ✅ Semantic zoom |
| **Scapple** | Freeform positioning, minimal UI | ✅ Aesthetic |
| **Logseq** | Outline + graph duality | ✅ List view |
| **Muse** | Spatial canvas, gesture-first | ✅ Gestures |
| **Kosmik** | Infinite canvas, mixed media | ✅ Pan/zoom |

### 14.2 Technical References

- **D3.js Force Layout:** https://d3js.org/d3-force
- **React Use Gesture:** https://use-gesture.netlify.app/
- **Framer Motion:** https://www.framer.com/motion/
- **Graph Visualization Techniques:** "Graph Drawing" by Battista et al.
- **Spatial Memory Research:** "The Image of the City" by Kevin Lynch

### 14.3 Design Resources

- **Gestalt Principles:** For entity clustering and visual grouping
- **Fitts's Law:** For touch target sizing and spacing
- **Animation Principles:** For natural-feeling transitions
- **Color Theory:** For entity type differentiation

---

## Appendix A: Entity Type Visual Encoding

| Entity Type | Icon | Color | Examples |
|-------------|------|-------|----------|
| Concept | 📖 | Blue (#3B82F6) | Working Memory, Attention |
| Theory | ⚡ | Purple (#8B5CF6) | Cognitive Load Theory |
| Framework | 🏗️ | Indigo (#6366F1) | ADDIE Model |
| Person | 👤 | Green (#10B981) | John Sweller |
| Assessment | 📊 | Cyan (#06B6D4) | Quiz, Test |
| Spark | ✨ | Yellow (#F59E0B) | User insights |
| Insight | 💡 | Orange (#F97316) | Discoveries |
| Thread | 🧵 | Pink (#EC4899) | Inquiry threads |
| FavoriteProblem | ❤️ | Red (#EF4444) | Core questions |
| Reframe | 🔄 | Teal (#14B8A6) | Analogies |
| Pattern | 🔍 | Slate (#64748B) | Recurring patterns |
| DynamicPattern | 📈 | Emerald (#059669) | Evolving patterns |
| StoryInsight | 📚 | Amber (#D97706) | Narrative insights |
| SchemaBreak | ⚠️ | Rose (#E11D48) | Paradigm shifts |

---

## Appendix B: Keyboard Shortcuts Reference

**Navigation:**
- `Arrow Keys` — Navigate to adjacent entities
- `Enter` — Select entity / Expand detail
- `Escape` — Navigate back
- `Space` — Toggle detail panel
- `H` — Return to home

**Views:**
- `G` — Graph view
- `L` — List view
- `T` — Timeline view
- `M` — Toggle minimap
- `F` — Fullscreen

**Actions:**
- `/` — Search
- `P` — Pins/bookmarks
- `?` — Help overlay
- `Cmd+Z` — Undo navigation
- `Cmd+Shift+Z` — Redo navigation

**Filters:**
- `1-9` — Toggle entity type
- `Shift+1-9` — Isolate type
- `A` — Show all types
- `D` — Depth filter

---

## Appendix C: Animation Timing Reference

| Transition | Duration | Easing | Notes |
|------------|----------|--------|-------|
| Entity selection | 500ms | Spring (100, 20) | Pan + zoom to center |
| Relationship reveal | 300ms | Spring physics | Lines fade in with force |
| Layout morph | 400ms | ease-in-out | Preserve relative positions |
| Hover state | 150ms | ease-out | Scale + shadow |
| Zoom level change | 300ms | ease-in-out | Semantic zoom transition |
| Detail panel slide | 200ms | ease-out | Bottom sheet appearance |
| Minimap update | 100ms | ease-out | Debounced viewport update |

---

**Document Status:** ✅ Ready for Implementation
**Next Steps:** Phase 1 implementation planning
**Owner:** IES Development Team
**Last Updated:** 2025-12-09