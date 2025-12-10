# Component Library Specifications

**Document Version:** 1.0
**Last Updated:** 2025-12-09
**Status:** Active

## Overview

This document defines reusable UI components for the IES system, covering both React (IES Reader) and Svelte (SiYuan Plugin) implementations. All components follow the design language defined in `04-design-language-guide.md` and use standardized design tokens.

### Design Principles

1. **Single Responsibility** - Each component has one clear purpose
2. **Composability** - Components can be combined to create complex UIs
3. **Consistency** - All components follow the design system
4. **Accessibility** - WCAG 2.1 AA compliance by default
5. **Mobile-First** - Responsive and touch-friendly
6. **Performance** - Optimized rendering and minimal re-renders

---

## Core Components

### 1. EntityBadge

**Purpose:** Display entity type with visual identifier (color + icon)

**Usage:** Entity labels, search results, entity cards, breadcrumbs

**Visual Specification:**

```
Sizes:
  sm: 18px height, 6px padding, 12px text, 14px icon
  md: 24px height, 8px padding, 14px text, 16px icon
  lg: 32px height, 10px padding, 16px text, 20px icon

Colors: See design tokens (entity type colors)
Border-radius: 4px
Font-weight: 500
```

**States:**

| State | Visual Treatment |
|-------|------------------|
| Default | Full opacity, solid color |
| Hover | 90% opacity (if interactive) |
| Active | Border: 2px solid, inset |
| Muted | 40% opacity, gray-500 background |

**Props/API:**

```typescript
interface EntityBadgeProps {
  entityType: EntityType; // Required
  size?: 'sm' | 'md' | 'lg'; // Default: 'md'
  interactive?: boolean; // Default: false
  muted?: boolean; // Default: false
  onClick?: () => void;
  className?: string;
}

type EntityType =
  | 'Concept' | 'Person' | 'Theory' | 'Framework' | 'Assessment'
  | 'Spark' | 'Insight' | 'Thread' | 'FavoriteProblem' | 'Reframe'
  | 'Pattern' | 'DynamicPattern' | 'StoryInsight' | 'SchemaBreak';
```

**Accessibility:**

- `role="status"` for non-interactive badges
- `role="button"` with `tabindex="0"` if interactive
- `aria-label="Entity type: {type}"`
- Keyboard: `Enter`/`Space` to activate if interactive

**Examples:**

```tsx
// React
<EntityBadge entityType="Concept" size="md" />
<EntityBadge
  entityType="Spark"
  interactive
  onClick={() => filterByType('Spark')}
/>

// Svelte
<EntityBadge entityType="Concept" size="md" />
<EntityBadge
  entityType="Spark"
  interactive
  on:click={() => filterByType('Spark')}
/>
```

**Visual Example:**

```
┌─────────────┐  ┌──────────────┐  ┌───────────────┐
│ 💡 Concept  │  │ ⚡ Spark     │  │ 🧵 Thread     │
└─────────────┘  └──────────────┘  └───────────────┘
   sm (18px)        md (24px)          lg (32px)
```

---

### 2. EntityCard

**Purpose:** Display entity information in a card format with expandable details

**Usage:** Search results, related entities, entity lists

**Visual Specification:**

```
Layout:
  - Header: EntityBadge + Name
  - Body: Description preview (2-3 lines)
  - Footer: Connection count + timestamp

Spacing:
  Padding: 16px
  Gap: 12px between sections
  Border-radius: 8px

Background: gray-50 (light mode) / gray-800 (dark mode)
Border: 1px solid gray-200 / gray-700
Min-height: 120px
```

**States:**

| State | Visual Treatment |
|-------|------------------|
| Default | Standard styling |
| Hover | Background → gray-100, cursor pointer, lift 2px |
| Expanded | Full description visible, chevron rotated |
| Selected | Border → primary-500 2px, shadow-md |

**Props/API:**

```typescript
interface EntityCardProps {
  entity: {
    id: string;
    name: string;
    type: EntityType;
    description: string;
    connectionCount?: number;
    lastVisited?: Date;
  };
  expanded?: boolean; // Default: false
  selected?: boolean; // Default: false
  onExpand?: () => void;
  onClick?: () => void;
  showFooter?: boolean; // Default: true
  maxDescriptionLines?: number; // Default: 3
}
```

**Accessibility:**

- `role="article"`
- `aria-expanded` if expandable
- `aria-label="Entity card: {name}"`
- Keyboard: `Enter` to navigate, `Space` to expand
- Focus visible outline

**Examples:**

```tsx
// React
<EntityCard
  entity={{
    id: "e1",
    name: "Cognitive Load",
    type: "Concept",
    description: "The amount of mental effort being used...",
    connectionCount: 12
  }}
  onClick={() => navigateToEntity("e1")}
/>

// Svelte
<EntityCard
  entity={{
    id: "e1",
    name: "Cognitive Load",
    type: "Concept",
    description: "The amount of mental effort being used...",
    connectionCount: 12
  }}
  on:click={() => navigateToEntity("e1")}
/>
```

**Visual Example:**

```
┌─────────────────────────────────────────┐
│ 💡 Concept    Cognitive Load            │
├─────────────────────────────────────────┤
│ The amount of mental effort being       │
│ used in working memory. High cognitive  │
│ load can impair...                      │
├─────────────────────────────────────────┤
│ 12 connections • Visited 2h ago         │
└─────────────────────────────────────────┘
```

---

### 3. QuestionClassBadge

**Purpose:** Display question class with emoji and color identifier

**Usage:** Question lists, active question display, question selector

**Visual Specification:**

```
Size: 28px height, 10px padding
Border-radius: 6px
Font-size: 14px
Font-weight: 500

Question Classes:
  Schema-Probe: 🔍 indigo-500
  Boundary: 🚧 amber-500
  Dimensional: 📊 blue-500
  Causal: 🔗 green-500
  Counterfactual: 🌀 purple-500
  Anchor: ⚓ cyan-500
  Perspective-Shift: 🔄 pink-500
  Meta-Cognitive: 🧠 violet-500
  Reflective-Synthesis: 💎 emerald-500
```

**States:**

| State | Visual Treatment |
|-------|------------------|
| Default | Emoji + label, colored background |
| Hover | Tooltip with class description, slight scale 1.05 |
| Active | Border 2px, shadow-sm |
| Label Hidden | Emoji only, 32px width |

**Props/API:**

```typescript
interface QuestionClassBadgeProps {
  questionClass: QuestionClass;
  showLabel?: boolean; // Default: true
  showTooltip?: boolean; // Default: true
  size?: 'sm' | 'md' | 'lg'; // Default: 'md'
  active?: boolean; // Default: false
  onClick?: () => void;
}

type QuestionClass =
  | 'Schema-Probe' | 'Boundary' | 'Dimensional'
  | 'Causal' | 'Counterfactual' | 'Anchor'
  | 'Perspective-Shift' | 'Meta-Cognitive' | 'Reflective-Synthesis';
```

**Accessibility:**

- `role="button"` if interactive
- `aria-label="Question class: {class}"`
- Tooltip with `aria-describedby`
- Keyboard: `Enter`/`Space` to activate

**Examples:**

```tsx
// React
<QuestionClassBadge questionClass="Schema-Probe" />
<QuestionClassBadge
  questionClass="Boundary"
  showLabel={false}
  onClick={() => filterByClass('Boundary')}
/>

// Svelte
<QuestionClassBadge questionClass="Schema-Probe" />
<QuestionClassBadge
  questionClass="Boundary"
  showLabel={false}
  on:click={() => filterByClass('Boundary')}
/>
```

**Visual Example:**

```
┌─────────────────────┐    ┌────┐
│ 🔍 Schema-Probe     │    │ 🚧 │
└─────────────────────┘    └────┘
   With label              Icon only
```

---

### 4. BreadcrumbTrail

**Purpose:** Display and navigate journey history as breadcrumb trail

**Usage:** Journey navigation, current context indicator

**Visual Specification:**

```
Layout:
  Horizontal scroll container
  Item + Separator + Item + ...

Item:
  Height: 32px
  Padding: 6px 12px
  Border-radius: 4px
  Font-size: 14px

Separator:
  Icon: → (right arrow)
  Color: gray-400
  Margin: 0 8px

Max visible items: 5 (truncate middle with "...")
```

**States:**

| State | Visual Treatment |
|-------|------------------|
| Default | gray-200 background |
| Hover | gray-300 background, cursor pointer |
| Current | primary-500 background, white text |
| Truncated | "..." with tooltip showing full path |

**Props/API:**

```typescript
interface BreadcrumbTrailProps {
  items: BreadcrumbItem[];
  maxVisible?: number; // Default: 5
  onNavigate: (itemId: string, index: number) => void;
  currentIndex?: number; // Default: last item
  className?: string;
}

interface BreadcrumbItem {
  id: string;
  label: string;
  entityType?: EntityType;
  timestamp?: Date;
}
```

**Accessibility:**

- `role="navigation"`
- `aria-label="Breadcrumb trail"`
- Each item has `aria-current="page"` if current
- Keyboard: Arrow keys to navigate, `Enter` to select
- Focus visible

**Examples:**

```tsx
// React
<BreadcrumbTrail
  items={[
    { id: "e1", label: "Cognitive Load", entityType: "Concept" },
    { id: "e2", label: "Working Memory", entityType: "Concept" },
    { id: "e3", label: "Miller's Law", entityType: "Theory" }
  ]}
  onNavigate={(id) => navigateToEntity(id)}
  currentIndex={2}
/>

// Svelte
<BreadcrumbTrail
  items={[
    { id: "e1", label: "Cognitive Load", entityType: "Concept" },
    { id: "e2", label: "Working Memory", entityType: "Concept" },
    { id: "e3", label: "Miller's Law", entityType: "Theory" }
  ]}
  on:navigate={({ detail: { id } }) => navigateToEntity(id)}
  currentIndex={2}
/>
```

**Visual Example:**

```
┌────────────────────────────────────────────────────┐
│ Cognitive Load → Working Memory → Miller's Law     │
└────────────────────────────────────────────────────┘

With truncation:
┌─────────────────────────────────────────────┐
│ Cognitive Load → ... → Miller's Law         │
└─────────────────────────────────────────────┘
```

---

### 5. Minimap

**Purpose:** Provide graph overview with current viewport indicator

**Usage:** Graph navigation, spatial context

**Visual Specification:**

```
Size: 200x150px (adjustable)
Position: Fixed corner (typically bottom-right)
Border: 1px solid gray-300
Border-radius: 8px
Background: white/alpha-90 (light mode), gray-800/alpha-90 (dark mode)
Shadow: shadow-lg

Node representation:
  - 4px circles colored by entity type
  - Clusters visible as color groups

Viewport indicator:
  - Rectangle outline 2px, primary-500
  - Draggable to pan main view
```

**States:**

| State | Visual Treatment |
|-------|------------------|
| Default | Semi-transparent, compact |
| Hover | Full opacity, expand slightly |
| Dragging | Viewport indicator follows cursor |
| Collapsed | Show only expand button |

**Props/API:**

```typescript
interface MinimapProps {
  nodes: MinimapNode[];
  viewport: ViewportBounds;
  onViewportChange: (bounds: ViewportBounds) => void;
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  collapsible?: boolean; // Default: true
  collapsed?: boolean;
}

interface MinimapNode {
  id: string;
  x: number;
  y: number;
  type: EntityType;
}

interface ViewportBounds {
  x: number;
  y: number;
  width: number;
  height: number;
}
```

**Accessibility:**

- `role="img"`
- `aria-label="Graph minimap"`
- Keyboard: Arrow keys to pan viewport
- Focus visible on viewport indicator
- `aria-describedby` for instructions

**Examples:**

```tsx
// React
<Minimap
  nodes={graphNodes}
  viewport={{ x: 0, y: 0, width: 800, height: 600 }}
  onViewportChange={(bounds) => panGraphTo(bounds)}
  position="bottom-right"
/>

// Svelte
<Minimap
  nodes={graphNodes}
  viewport={{ x: 0, y: 0, width: 800, height: 600 }}
  on:viewportChange={({ detail: bounds }) => panGraphTo(bounds)}
  position="bottom-right"
/>
```

**Visual Example:**

```
┌──────────────────────┐
│  •  • •              │
│    •   •  •          │
│  •  •    ┌────┐      │
│      •   │    │ •    │
│  •    •  └────┘  •   │
│    •     •      •    │
└──────────────────────┘
  Viewport indicator (rectangle)
  Nodes (colored dots)
```

---

### 6. SearchInput

**Purpose:** Text input for entity/content search with debouncing

**Usage:** Global search, entity lookup, filtering

**Visual Specification:**

```
Height: 40px
Padding: 10px 40px 10px 12px (room for icons)
Border: 1px solid gray-300
Border-radius: 8px
Font-size: 14px

Icons:
  - Search icon: 20px, gray-400, left side
  - Clear button: 20px, gray-500, right side (when value present)
  - Loading spinner: 20px, primary-500, right side (when loading)

Keyboard hint: "Cmd+K" or "Ctrl+K" (gray-400, right side)
```

**States:**

| State | Visual Treatment |
|-------|------------------|
| Default | Border gray-300, placeholder visible |
| Focus | Border primary-500 2px, shadow-sm, outline ring |
| Filled | Clear button visible |
| Loading | Spinner replaces clear button |
| Error | Border red-500, error message below |
| Disabled | Background gray-100, cursor not-allowed |

**Props/API:**

```typescript
interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string; // Default: "Search..."
  debounceMs?: number; // Default: 300
  loading?: boolean; // Default: false
  error?: string;
  disabled?: boolean;
  keyboardShortcut?: string; // Default: "Cmd+K"
  onFocus?: () => void;
  onBlur?: () => void;
  className?: string;
}
```

**Accessibility:**

- `role="searchbox"`
- `aria-label="Search entities and content"`
- `aria-describedby` for error messages
- `aria-busy="true"` when loading
- Keyboard shortcut registered globally
- Clear button: `aria-label="Clear search"`

**Examples:**

```tsx
// React
<SearchInput
  value={searchQuery}
  onChange={setSearchQuery}
  placeholder="Search entities..."
  loading={isSearching}
  keyboardShortcut="Cmd+K"
/>

// Svelte
<SearchInput
  value={searchQuery}
  on:change={({ detail }) => setSearchQuery(detail)}
  placeholder="Search entities..."
  loading={isSearching}
  keyboardShortcut="Cmd+K"
/>
```

**Visual Example:**

```
┌───────────────────────────────────────┐
│ 🔍 cognitive load            Cmd+K  × │
└───────────────────────────────────────┘
   Icon    Input value         Shortcut Clear
```

---

### 7. FilterPills

**Purpose:** Multi-select entity type filters with visual feedback

**Usage:** Filter entity lists, search refinement

**Visual Specification:**

```
Layout:
  Horizontal wrap container
  Gap: 8px between pills

Pill:
  Height: 32px
  Padding: 8px 12px
  Border-radius: 16px (fully rounded)
  Font-size: 14px
  Font-weight: 500
  Transition: all 200ms ease
```

**States:**

| State | Visual Treatment |
|-------|------------------|
| OFF | Background gray-200, text gray-700 |
| ON | Background entity-color, text white, checkmark |
| Hover | Scale 1.05, cursor pointer |
| Disabled | Opacity 50%, cursor not-allowed |

**Props/API:**

```typescript
interface FilterPillsProps {
  entityTypes: EntityType[];
  selectedTypes: EntityType[];
  onToggle: (type: EntityType) => void;
  multiSelect?: boolean; // Default: true
  showIcons?: boolean; // Default: true
  disabled?: boolean;
  className?: string;
}
```

**Accessibility:**

- `role="group"`
- `aria-label="Entity type filters"`
- Each pill: `role="checkbox"`, `aria-checked`
- Keyboard: `Tab` to navigate, `Space` to toggle
- Focus visible ring

**Examples:**

```tsx
// React
<FilterPills
  entityTypes={['Concept', 'Theory', 'Person']}
  selectedTypes={['Concept']}
  onToggle={(type) => toggleFilter(type)}
  showIcons
/>

// Svelte
<FilterPills
  entityTypes={['Concept', 'Theory', 'Person']}
  selectedTypes={['Concept']}
  on:toggle={({ detail: type }) => toggleFilter(type)}
  showIcons
/>
```

**Visual Example:**

```
┌──────────────────────────────────────────────────┐
│ ✓ 💡 Concept   🎓 Theory   👤 Person   ⚡ Spark  │
└──────────────────────────────────────────────────┘
   Selected      Unselected   Unselected Unselected
   (blue bg)     (gray bg)    (gray bg)  (gray bg)
```

---

### 8. SyncStatusIndicator

**Purpose:** Display cross-app session sync status

**Usage:** Status bar, header, sync monitoring

**Visual Specification:**

```
Size: Compact (icon + text) or icon-only
Icon size: 16px
Font-size: 12px
Padding: 4px 8px
Border-radius: 4px

Status indicators:
  Synced: ✓ green-500
  Syncing: ↻ blue-500 (animated spin)
  Error: ✕ red-500
  Offline: ⊘ gray-400
```

**States:**

| State | Visual Treatment |
|-------|------------------|
| Synced | Green checkmark, "Synced" text |
| Syncing | Spinning icon, "Syncing..." text |
| Error | Red X, error message in tooltip |
| Offline | Gray icon, "Offline" text |

**Props/API:**

```typescript
interface SyncStatusIndicatorProps {
  status: 'synced' | 'syncing' | 'error' | 'offline';
  lastSyncTime?: Date;
  errorMessage?: string;
  compact?: boolean; // Default: false (show text)
  showTooltip?: boolean; // Default: true
  onClick?: () => void; // Manual sync trigger
}
```

**Accessibility:**

- `role="status"`
- `aria-live="polite"` for status changes
- `aria-label` with full status description
- Tooltip with `aria-describedby`
- Keyboard: `Enter` to trigger manual sync if interactive

**Examples:**

```tsx
// React
<SyncStatusIndicator
  status="synced"
  lastSyncTime={new Date()}
  onClick={() => triggerManualSync()}
/>

// Svelte
<SyncStatusIndicator
  status="synced"
  lastSyncTime={new Date()}
  on:click={() => triggerManualSync()}
/>
```

**Visual Example:**

```
Expanded:
┌──────────────────┐
│ ✓ Synced • 2m ago│
└──────────────────┘

Compact:
┌────┐
│ ✓  │ (with tooltip)
└────┘
```

---

### 9. SelectionBar

**Purpose:** Floating action bar for text selection actions

**Usage:** E-book reader text selection

**Visual Specification:**

```
Size: Auto width based on actions, 40px height
Position: Absolute, 8px above/below selection
Background: gray-900 (dark) with shadow-xl
Border-radius: 8px
Padding: 6px

Actions:
  Each action: 32px button, white icon, 4px gap
  Icons: 20px size
  Hover: gray-700 background
```

**States:**

| State | Visual Treatment |
|-------|------------------|
| Hidden | Opacity 0, pointer-events none |
| Visible | Fade in 200ms, positioned near selection |
| Above selection | Arrow pointing down |
| Below selection | Arrow pointing up (if no space above) |

**Props/API:**

```typescript
interface SelectionBarProps {
  visible: boolean;
  position: { x: number; y: number };
  selectedText: string;
  actions: SelectionAction[];
  onAction: (action: string) => void;
  preferPosition?: 'above' | 'below' | 'auto'; // Default: 'auto'
}

interface SelectionAction {
  id: string;
  icon: string; // Icon name or component
  label: string;
  shortcut?: string;
}
```

**Accessibility:**

- `role="toolbar"`
- `aria-label="Text selection actions"`
- Each action button: `aria-label` with action name
- Keyboard: `Tab` to navigate actions, `Enter` to execute
- Focus trap when visible
- `Escape` to dismiss

**Examples:**

```tsx
// React
<SelectionBar
  visible={hasSelection}
  position={{ x: 100, y: 200 }}
  selectedText="cognitive load"
  actions={[
    { id: 'lookup', icon: 'search', label: 'Look up' },
    { id: 'note', icon: 'edit', label: 'Note' },
    { id: 'highlight', icon: 'marker', label: 'Highlight' }
  ]}
  onAction={(action) => handleSelectionAction(action)}
/>

// Svelte
<SelectionBar
  visible={hasSelection}
  position={{ x: 100, y: 200 }}
  selectedText="cognitive load"
  actions={[
    { id: 'lookup', icon: 'search', label: 'Look up' },
    { id: 'note', icon: 'edit', label: 'Note' },
    { id: 'highlight', icon: 'marker', label: 'Highlight' }
  ]}
  on:action={({ detail: action }) => handleSelectionAction(action)}
/>
```

**Visual Example:**

```
        ▼
┌──────────────────────┐
│  🔍   📝   🖍️        │
└──────────────────────┘
   Look  Note  Highlight
    up
```

---

### 10. BottomSheet

**Purpose:** Mobile drawer/modal with drag interaction

**Usage:** Mobile FlowPanel, entity details, filters

**Visual Specification:**

```
States:
  Collapsed: 60px visible (handle + peek content)
  Half: 50vh visible
  Full: 100vh - 60px (safe area)

Handle:
  Width: 40px, height: 4px
  Border-radius: 2px
  Background: gray-400
  Centered, 8px from top

Background: white (light mode), gray-900 (dark mode)
Border-radius: 16px 16px 0 0
Shadow: shadow-2xl
Transition: transform 300ms ease-out
```

**States:**

| State | Visual Treatment |
|-------|------------------|
| Collapsed | Only handle + title visible |
| Half | 50% viewport height |
| Full | Nearly full screen |
| Dragging | Follow touch/mouse Y position |
| Animating | Smooth snap to nearest state |

**Props/API:**

```typescript
interface BottomSheetProps {
  open: boolean;
  initialState?: 'collapsed' | 'half' | 'full'; // Default: 'collapsed'
  onStateChange?: (state: BottomSheetState) => void;
  onClose?: () => void;
  disableDrag?: boolean; // Default: false
  children: React.ReactNode;
  title?: string;
  showHandle?: boolean; // Default: true
}

type BottomSheetState = 'collapsed' | 'half' | 'full';
```

**Accessibility:**

- `role="dialog"`
- `aria-modal="true"` when full
- `aria-label` with sheet purpose
- Drag handle: `aria-label="Drag to resize"`
- Keyboard: `Escape` to collapse/close
- Focus trap when full

**Examples:**

```tsx
// React
<BottomSheet
  open={isOpen}
  initialState="half"
  onStateChange={(state) => setSheetState(state)}
  onClose={() => setIsOpen(false)}
  title="Entity Details"
>
  <EntityDetailsContent />
</BottomSheet>

// Svelte
<BottomSheet
  open={isOpen}
  initialState="half"
  on:stateChange={({ detail: state }) => setSheetState(state)}
  on:close={() => setIsOpen(false)}
  title="Entity Details"
>
  <EntityDetailsContent />
</BottomSheet>
```

**Visual Example:**

```
Collapsed:
┌──────────────────────────┐
│         ────             │ ← Handle
│  Entity Details          │
└──────────────────────────┘

Half:
┌──────────────────────────┐
│         ────             │
│  Entity Details          │
│                          │
│  [Content visible]       │
│                          │
│                          │
└──────────────────────────┘

Full: (Nearly entire screen)
```

---

## Graph Components

### 11. GraphNode

**Purpose:** Visual representation of entity in graph visualization

**Usage:** Flow Mode graph, entity relationship visualization

**Visual Specification:**

```
Default size: 48px diameter circle
Size variants:
  - By importance: 32px - 64px
  - By connection count: 40px - 80px

Border: 2px solid, color by entity type
Background: white (light mode), gray-800 (dark mode)
Label: Max 20 chars, truncated with ellipsis
Label position: Below node, 4px gap
Font-size: 12px
```

**States:**

| State | Visual Treatment |
|-------|------------------|
| Default | Standard size, type color border |
| Hover | Scale 1.1, shadow-md, tooltip with full name |
| Selected | Border 3px, shadow-lg, label bold |
| Active | Pulse animation, glow effect |
| Muted | Opacity 30%, gray border |

**Props/API:**

```typescript
interface GraphNodeProps {
  entity: {
    id: string;
    name: string;
    type: EntityType;
    connectionCount?: number;
    importance?: number; // 0-1
  };
  position: { x: number; y: number };
  size?: number; // Override default size
  selected?: boolean;
  muted?: boolean;
  onClick?: () => void;
  onDoubleClick?: () => void;
  onHover?: (hover: boolean) => void;
}
```

**Accessibility:**

- `role="button"`
- `aria-label="Entity: {name} ({type})"`
- `aria-pressed="true"` if selected
- Keyboard: `Enter` to select, `Space` to expand
- Focus visible ring

**Examples:**

```tsx
// React
<GraphNode
  entity={{
    id: "e1",
    name: "Cognitive Load",
    type: "Concept",
    connectionCount: 12
  }}
  position={{ x: 100, y: 200 }}
  selected={selectedId === "e1"}
  onClick={() => selectEntity("e1")}
/>

// Svelte
<GraphNode
  entity={{
    id: "e1",
    name: "Cognitive Load",
    type: "Concept",
    connectionCount: 12
  }}
  position={{ x: 100, y: 200 }}
  selected={selectedId === "e1"}
  on:click={() => selectEntity("e1")}
/>
```

**Visual Example:**

```
Default:
    ┌─────┐
    │     │ ← Circle with type-color border
    │ 💡  │
    │     │
    └─────┘
  Cognitive Load

Selected:
    ┌─────┐
    │░░░░░│ ← Thicker border, shadow
    │░💡░░│
    │░░░░░│
    └─────┘
  Cognitive Load (bold)
```

---

### 12. GraphEdge

**Purpose:** Visual connection between entities in graph

**Usage:** Relationship visualization, connection strength

**Visual Specification:**

```
Line:
  Width: 1-3px (by relationship strength)
  Color: gray-400 default, type-specific color if typed relationship
  Style: Solid (strong) or dashed (weak)

Arrow:
  Size: 8px
  Direction: Optional (for directed relationships)

Label:
  Font-size: 11px
  Background: white/alpha-90
  Padding: 2px 6px
  Border-radius: 3px
  Position: Middle of line
```

**States:**

| State | Visual Treatment |
|-------|------------------|
| Default | Gray line, subtle |
| Hover | Thicker line, darker color, label visible |
| Selected | Primary color, label always visible |
| Highlighted | Animated dash, attention color |

**Props/API:**

```typescript
interface GraphEdgeProps {
  from: string; // Node ID
  to: string; // Node ID
  relationship?: {
    type: string;
    label: string;
    strength?: number; // 0-1
    directed?: boolean;
  };
  selected?: boolean;
  highlighted?: boolean;
  onHover?: (hover: boolean) => void;
  onClick?: () => void;
}
```

**Accessibility:**

- `role="img"`
- `aria-label="Connection from {source} to {target}"`
- Not keyboard focusable (navigate via nodes)
- Tooltip with relationship details on hover

**Examples:**

```tsx
// React
<GraphEdge
  from="e1"
  to="e2"
  relationship={{
    type: "relates_to",
    label: "influences",
    strength: 0.8,
    directed: true
  }}
  selected={selectedEdge === "e1-e2"}
  onClick={() => selectEdge("e1-e2")}
/>

// Svelte
<GraphEdge
  from="e1"
  to="e2"
  relationship={{
    type: "relates_to",
    label: "influences",
    strength: 0.8,
    directed: true
  }}
  selected={selectedEdge === "e1-e2"}
  on:click={() => selectEdge("e1-e2")}
/>
```

**Visual Example:**

```
Default:
  Node A ───────────────── Node B

With arrow (directed):
  Node A ─────────────────→ Node B

With label:
  Node A ─────[influences]─────→ Node B

Hover:
  Node A ═════[influences]═════→ Node B
         ↑ Thicker line
```

---

### 13. GraphCanvas

**Purpose:** Container for graph visualization with pan/zoom/gestures

**Usage:** Main graph view container

**Visual Specification:**

```
Size: Fill parent container
Background: gray-50 (light mode), gray-900 (dark mode)
Grid (optional): 1px dotted gray-300, 50px spacing

Controls overlay:
  Position: Top-right, 16px gap
  Buttons: Zoom in, Zoom out, Fit to view, Reset
  Size: 32px, gray-800 background, white icons

Zoom range: 0.1x - 3x
Pan: Unlimited (with bounds indicator)
```

**States:**

| State | Visual Treatment |
|-------|------------------|
| Default | Standard view |
| Panning | Cursor: grabbing, momentum scroll |
| Zooming | Scale transform, smooth transition |
| Loading | Skeleton nodes, loading indicator |
| Empty | "No entities" message, centered |

**Props/API:**

```typescript
interface GraphCanvasProps {
  nodes: GraphNodeData[];
  edges: GraphEdgeData[];
  initialZoom?: number; // Default: 1
  minZoom?: number; // Default: 0.1
  maxZoom?: number; // Default: 3
  showGrid?: boolean; // Default: true
  showControls?: boolean; // Default: true
  fitOnLoad?: boolean; // Default: true
  onNodeClick?: (nodeId: string) => void;
  onEdgeClick?: (edgeId: string) => void;
  onViewportChange?: (viewport: Viewport) => void;
}

interface GraphNodeData {
  id: string;
  entity: Entity;
  x?: number; // Auto-layout if not provided
  y?: number;
}

interface GraphEdgeData {
  id: string;
  from: string;
  to: string;
  relationship?: Relationship;
}

interface Viewport {
  x: number;
  y: number;
  zoom: number;
}
```

**Accessibility:**

- `role="application"`
- `aria-label="Entity relationship graph"`
- Keyboard: Arrow keys to pan, +/- to zoom, Home to fit
- Focus management for nodes
- Screen reader announcements for viewport changes

**Examples:**

```tsx
// React
<GraphCanvas
  nodes={entityNodes}
  edges={relationships}
  initialZoom={1}
  showGrid
  showControls
  onNodeClick={(id) => selectEntity(id)}
  onViewportChange={(vp) => saveViewport(vp)}
/>

// Svelte
<GraphCanvas
  nodes={entityNodes}
  edges={relationships}
  initialZoom={1}
  showGrid
  showControls
  on:nodeClick={({ detail: id }) => selectEntity(id)}
  on:viewportChange={({ detail: vp }) => saveViewport(vp)}
/>
```

**Visual Example:**

```
┌──────────────────────────────────┐ ┌─────┐
│  •     •                         │ │  +  │ Zoom in
│     •       •    •               │ │  -  │ Zoom out
│  •       •           •           │ │  ⊡  │ Fit view
│       •        •        •        │ │  ↻  │ Reset
│  •  •     •        •      •      │ └─────┘
│        •      •        •         │   Controls
└──────────────────────────────────┘
   Grid background, nodes, edges
```

---

## Layout Components

### 14. FlowPanel

**Purpose:** Sidebar/drawer container for exploration panel

**Usage:** IES Reader side panel, SiYuan entity browser

**Visual Specification:**

```
Desktop:
  Width: 400px default (resizable 300-600px)
  Position: Right side (or left, configurable)
  Border: 1px solid gray-200
  Resize handle: 4px drag area, hover cursor: col-resize

Mobile:
  Use BottomSheet component instead

Header:
  Height: 56px
  Title + close button
  Background: gray-50
  Border-bottom: 1px solid gray-200

Content:
  Scrollable
  Padding: 16px
  Background: white
```

**States:**

| State | Visual Treatment |
|-------|------------------|
| Expanded | Full width, content visible |
| Collapsed | 0px width, hidden |
| Resizing | Show resize indicator, cursor: col-resize |
| Animating | Smooth transition 300ms |

**Props/API:**

```typescript
interface FlowPanelProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  position?: 'left' | 'right'; // Default: 'right'
  defaultWidth?: number; // Default: 400
  minWidth?: number; // Default: 300
  maxWidth?: number; // Default: 600
  resizable?: boolean; // Default: true
  collapsible?: boolean; // Default: true
  children: React.ReactNode;
  header?: React.ReactNode; // Custom header
  footer?: React.ReactNode; // Custom footer
}
```

**Accessibility:**

- `role="complementary"`
- `aria-label="Exploration panel"`
- `aria-expanded` state
- Keyboard: `Escape` to close
- Focus trap when open
- Resize handle: `aria-label="Resize panel"`

**Examples:**

```tsx
// React
<FlowPanel
  open={isPanelOpen}
  onClose={() => setPanelOpen(false)}
  title="Entity Details"
  position="right"
  resizable
>
  <EntityExplorationContent />
</FlowPanel>

// Svelte
<FlowPanel
  open={isPanelOpen}
  on:close={() => setPanelOpen(false)}
  title="Entity Details"
  position="right"
  resizable
>
  <EntityExplorationContent />
</FlowPanel>
```

**Visual Example:**

```
Desktop:
┌────────────────────┬─┬──────────────┐
│                    │ │  ╔═══════════╗│
│   Main Content     │ │  ║ Entity    ║│ ← FlowPanel
│                    │ │  ║ Details   ║│
│                    │ │  ║           ║│
│                    │ │  ║  [content]║│
└────────────────────┴─┴──╚═══════════╝┘
                      ↑ Resize handle

Mobile: (Uses BottomSheet)
```

---

### 15. TabBar

**Purpose:** Mode switching navigation with icons and labels

**Usage:** SiYuan thinking mode selector, view switcher

**Visual Specification:**

```
Layout:
  Horizontal tabs
  Fixed at top or bottom
  Equal width tabs or auto-sized

Tab:
  Height: 48px
  Padding: 12px 20px
  Icon: 20px, above label
  Label: 12px, below icon
  Gap: 4px between icon and label

Active indicator:
  Bottom border: 3px solid primary-500
  Or: Background highlight

Border-bottom: 1px solid gray-200 (on bar)
```

**States:**

| State | Visual Treatment |
|-------|------------------|
| Default | Gray icon + label |
| Hover | Icon + label darker, background gray-50 |
| Active | Primary color, active indicator |
| Disabled | Opacity 40%, cursor not-allowed |

**Props/API:**

```typescript
interface TabBarProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  position?: 'top' | 'bottom'; // Default: 'top'
  indicatorStyle?: 'border' | 'background'; // Default: 'border'
  orientation?: 'horizontal' | 'vertical'; // Default: 'horizontal'
  className?: string;
}

interface Tab {
  id: string;
  label: string;
  icon: string | React.ReactNode;
  disabled?: boolean;
  badge?: number; // Notification count
  shortcut?: string; // Keyboard shortcut
}
```

**Accessibility:**

- `role="tablist"`
- Each tab: `role="tab"`, `aria-selected`
- Keyboard: Arrow keys to navigate, `Enter`/`Space` to select
- `aria-controls` pointing to tab panel
- Focus visible ring
- Shortcuts registered globally

**Examples:**

```tsx
// React
<TabBar
  tabs={[
    { id: 'flow', label: 'Flow', icon: '🌊' },
    { id: 'forge', label: 'Forge', icon: '🔨' },
    { id: 'focus', label: 'Focus', icon: '🎯' },
    { id: 'weave', label: 'Weave', icon: '🧵' },
    { id: 'frame', label: 'Frame', icon: '🖼️' }
  ]}
  activeTab={currentMode}
  onTabChange={(id) => switchMode(id)}
/>

// Svelte
<TabBar
  tabs={[
    { id: 'flow', label: 'Flow', icon: '🌊' },
    { id: 'forge', label: 'Forge', icon: '🔨' },
    { id: 'focus', label: 'Focus', icon: '🎯' },
    { id: 'weave', label: 'Weave', icon: '🧵' },
    { id: 'frame', label: 'Frame', icon: '🖼️' }
  ]}
  activeTab={currentMode}
  on:tabChange={({ detail: id }) => switchMode(id)}
/>
```

**Visual Example:**

```
┌────────┬────────┬────────┬────────┬────────┐
│   🌊   │   🔨   │   🎯   │   🧵   │   🖼️   │
│  Flow  │ Forge  │ Focus  │ Weave  │ Frame  │
└────────┴────────┴────────┴────────┴────────┘
    ███ ← Active indicator (bottom border)
```

---

## Component Composition Examples

### Example 1: Entity Search Interface

```tsx
<div className="entity-search">
  <SearchInput
    value={query}
    onChange={setQuery}
    placeholder="Search entities..."
    loading={isSearching}
  />

  <FilterPills
    entityTypes={allEntityTypes}
    selectedTypes={filters}
    onToggle={toggleFilter}
    showIcons
  />

  <div className="results">
    {results.map(entity => (
      <EntityCard
        key={entity.id}
        entity={entity}
        onClick={() => navigateToEntity(entity.id)}
      />
    ))}
  </div>
</div>
```

### Example 2: Graph Exploration View

```tsx
<div className="graph-view">
  <GraphCanvas
    nodes={entities}
    edges={relationships}
    onNodeClick={selectEntity}
    showGrid
    showControls
  />

  <Minimap
    nodes={entities}
    viewport={currentViewport}
    onViewportChange={panTo}
    position="bottom-right"
  />

  <FlowPanel
    open={selectedEntity !== null}
    onClose={() => setSelectedEntity(null)}
    title="Entity Details"
  >
    <EntityCard entity={selectedEntity} expanded />
    <BreadcrumbTrail
      items={journeyTrail}
      onNavigate={navigateToEntity}
    />
  </FlowPanel>
</div>
```

### Example 3: Reader Integration

```tsx
<div className="reader-view">
  <ReaderContent onSelect={handleSelection} />

  <SelectionBar
    visible={hasSelection}
    position={selectionPosition}
    selectedText={selectedText}
    actions={[
      { id: 'lookup', icon: 'search', label: 'Look up' },
      { id: 'highlight', icon: 'marker', label: 'Highlight' }
    ]}
    onAction={handleSelectionAction}
  />

  <BottomSheet
    open={showEntityPanel}
    initialState="half"
    title="Entity Details"
  >
    <EntityCard entity={currentEntity} expanded />
  </BottomSheet>

  <SyncStatusIndicator
    status={syncStatus}
    lastSyncTime={lastSync}
  />
</div>
```

---

## Implementation Notes

### React Implementation

```typescript
// Shared types
export type EntityType = 'Concept' | 'Person' | 'Theory' | /* ... */;
export type QuestionClass = 'Schema-Probe' | 'Boundary' | /* ... */;

// Component library structure
components/
  core/
    EntityBadge.tsx
    EntityCard.tsx
    QuestionClassBadge.tsx
    SearchInput.tsx
    FilterPills.tsx
    SyncStatusIndicator.tsx
  graph/
    GraphNode.tsx
    GraphEdge.tsx
    GraphCanvas.tsx
  layout/
    FlowPanel.tsx
    TabBar.tsx
    BottomSheet.tsx
  navigation/
    BreadcrumbTrail.tsx
    Minimap.tsx
  reader/
    SelectionBar.tsx
  index.ts  // Barrel exports
```

### Svelte Implementation

```typescript
// Component library structure
components/
  core/
    EntityBadge.svelte
    EntityCard.svelte
    QuestionClassBadge.svelte
    SearchInput.svelte
    FilterPills.svelte
    SyncStatusIndicator.svelte
  graph/
    GraphNode.svelte
    GraphEdge.svelte
    GraphCanvas.svelte
  layout/
    FlowPanel.svelte
    TabBar.svelte
    BottomSheet.svelte
  navigation/
    BreadcrumbTrail.svelte
    Minimap.svelte
  index.ts  // Component exports
```

### Shared Utilities

```typescript
// Design tokens
export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '24px',
  '2xl': '32px'
};

export const colors = {
  // Entity type colors
  concept: { light: '#3B82F6', dark: '#60A5FA' },
  person: { light: '#8B5CF6', dark: '#A78BFA' },
  // ... all entity types
};

// Accessibility helpers
export function getEntityTypeLabel(type: EntityType): string {
  const labels = {
    'Concept': 'Concept entity',
    'Person': 'Person entity',
    // ... all types
  };
  return labels[type] || type;
}

export function getQuestionClassDescription(qClass: QuestionClass): string {
  const descriptions = {
    'Schema-Probe': 'Questions that examine mental frameworks',
    'Boundary': 'Questions that test edge cases and limits',
    // ... all classes
  };
  return descriptions[qClass] || qClass;
}
```

---

## Performance Optimization

### Virtualization

Components that render large lists should use virtualization:

- **EntityCard lists** - Use `react-window` or `@tanstack/react-virtual`
- **Graph nodes** - Cull off-screen nodes
- **Journey trails** - Limit visible items with truncation

### Memoization

```typescript
// React
const EntityCard = React.memo(({ entity, onClick }) => {
  // Component implementation
}, (prevProps, nextProps) => {
  return prevProps.entity.id === nextProps.entity.id &&
         prevProps.selected === nextProps.selected;
});

// Svelte (automatic with stores)
```

### Debouncing/Throttling

- **SearchInput** - Debounce onChange (300ms default)
- **Pan/zoom** - Throttle viewport updates (16ms / 60fps)
- **Resize** - Throttle resize handlers (100ms)

---

## Testing Guidelines

### Component Tests

Each component should have:

1. **Snapshot tests** - Visual regression
2. **Interaction tests** - Click, hover, keyboard
3. **Accessibility tests** - ARIA, keyboard navigation
4. **State tests** - All state variations

Example:

```typescript
describe('EntityBadge', () => {
  it('renders with correct entity type', () => {
    render(<EntityBadge entityType="Concept" />);
    expect(screen.getByText('Concept')).toBeInTheDocument();
  });

  it('handles click when interactive', () => {
    const onClick = jest.fn();
    render(<EntityBadge entityType="Concept" interactive onClick={onClick} />);
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalled();
  });

  it('is keyboard accessible', () => {
    const onClick = jest.fn();
    render(<EntityBadge entityType="Concept" interactive onClick={onClick} />);
    const badge = screen.getByRole('button');
    fireEvent.keyDown(badge, { key: 'Enter' });
    expect(onClick).toHaveBeenCalled();
  });
});
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-09 | Initial component library specification |

---

## References

- Design Language Guide: `04-design-language-guide.md`
- Architecture Document: `ARCHITECTURE-AND-INTERACTIONS.md`
- IES System Design: `IES-SYSTEM-DESIGN.md`
