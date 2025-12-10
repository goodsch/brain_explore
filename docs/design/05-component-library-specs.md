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

## Accessibility Standards

All components must meet WCAG 2.1 Level AA compliance requirements. Accessibility is not optional - it's built into every component by default.

### Core Requirements

1. **Focus Visible** - All interactive elements must have visible focus indicators
   - Minimum: 2px outline with 4.5:1 contrast ratio
   - Style: Use design system focus ring (primary-500 with 2px offset)
   - Never remove focus styles without providing alternative

2. **Color Contrast**
   - Normal text: 4.5:1 minimum contrast ratio
   - Large text (18px+ or 14px+ bold): 3:1 minimum
   - Interactive elements: 3:1 for visual indicators
   - Test all color combinations, especially entity type colors

3. **Keyboard Navigation**
   - All functionality accessible via keyboard
   - Logical tab order following visual layout
   - Escape key closes modals/overlays
   - Arrow keys for navigation in lists/grids
   - Enter/Space for activation

4. **Screen Reader Support**
   - Meaningful labels for all interactive elements
   - State changes announced via aria-live
   - Form validation errors associated with inputs
   - Loading states announced
   - Dynamic content changes announced

5. **Motion Sensitivity**
   - Respect `prefers-reduced-motion` media query
   - Provide alternative to animations for essential info
   - Disable auto-playing animations when motion is reduced

### Common ARIA Patterns

Standard ARIA attributes for common component types:

| Element Type | Required ARIA Attributes | Notes |
|--------------|-------------------------|-------|
| Icon button | `aria-label="Action description"` | Must describe action, not icon |
| Expandable section | `aria-expanded="true/false"`, `aria-controls="id"` | Links button to controlled content |
| Search input | `aria-label="Search description"`, `role="searchbox"` | Describes what's being searched |
| Entity badge (clickable) | `aria-label="{type}: {name}"`, `role="button"` | Includes entity type and name |
| Entity badge (static) | `aria-label="{type}: {name}"`, `role="status"` | Non-interactive status indicator |
| Navigation | `role="navigation"`, `aria-label="Navigation type"` | Describes navigation purpose |
| Loading state | `aria-busy="true"`, `aria-live="polite"` | Announces loading to screen readers |
| Error message | `aria-live="assertive"`, `role="alert"` | Immediate announcement of errors |
| Tooltip | `aria-describedby="tooltip-id"` | Associates tooltip with trigger |
| Modal dialog | `role="dialog"`, `aria-modal="true"`, `aria-labelledby` | Focus trap required |
| Tab interface | `role="tablist"`, `role="tab"`, `aria-selected` | Full tab widget pattern |
| Combobox | `role="combobox"`, `aria-expanded`, `aria-controls` | For search with suggestions |

### Focus Management Patterns

**Focus Trap** (required for modals, dialogs, sheets):
```typescript
// On open:
1. Save currently focused element
2. Move focus to first focusable element in modal
3. Trap Tab/Shift+Tab within modal boundaries
4. Escape key closes and restores focus

// On close:
5. Return focus to saved element
```

**Focus Order** (for complex components):
```typescript
// Logical tab order:
1. Interactive header elements
2. Main content (left-to-right, top-to-bottom)
3. Action buttons (usually bottom-right)
4. Close/cancel actions (typically last)
```

### Keyboard Shortcuts Reference

Standard keyboard interactions by component type:

| Component Type | Keyboard Actions |
|----------------|-----------------|
| Button | Enter, Space |
| Link | Enter |
| Checkbox/Toggle | Space |
| Radio button | Arrow keys (between group), Space (select) |
| Dropdown | Enter/Space (open), Arrow keys (navigate), Enter (select), Escape (close) |
| Modal/Dialog | Escape (close) |
| Tabs | Arrow keys (navigate), Enter/Space (activate) |
| List/Grid | Arrow keys (navigate), Enter (select/activate) |
| Search | Escape (clear), Down arrow (show suggestions) |
| Graph canvas | Arrow keys (pan), +/- (zoom), Home (fit to view) |

### Screen Reader Announcements

Use `aria-live` regions for dynamic updates:

```typescript
// Polite (wait for pause in speech):
<div aria-live="polite" aria-atomic="true">
  Search found 12 results
</div>

// Assertive (interrupt immediately):
<div aria-live="assertive" role="alert">
  Error: Connection failed. Retrying...
</div>

// Status (for non-critical updates):
<div role="status" aria-live="polite">
  Synced 2 minutes ago
</div>
```

### Testing Checklist

For every component, verify:

- [ ] Keyboard-only navigation works completely
- [ ] Focus indicator visible and high-contrast
- [ ] Screen reader announces all states/changes
- [ ] Color contrast meets WCAG AA standards
- [ ] Works with browser zoom up to 200%
- [ ] Respects prefers-reduced-motion
- [ ] ARIA attributes validated (no errors)
- [ ] Interactive elements have sufficient touch target size (44x44px minimum)

### Tools for Testing

- **Automated**: axe DevTools, Lighthouse, WAVE
- **Manual**: Keyboard-only navigation, screen reader (NVDA, JAWS, VoiceOver)
- **Color contrast**: WebAIM Contrast Checker, Chrome DevTools
- **Focus order**: Tab through interface, verify logical flow

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

- **Role:** `role="status"` for non-interactive badges, `role="button"` if interactive
- **ARIA Label:** `aria-label="{type} entity"` (e.g., "Concept entity", "Spark entity")
- **Tabindex:** `tabindex="0"` if interactive, not focusable if static
- **Keyboard Interactions:**
  - `Enter` or `Space`: Activate onClick handler (interactive only)
  - Focus indicator: 2px offset ring in primary-500
- **States:**
  - Hover: Announced as "button" by screen readers if interactive
  - Active: No additional announcement needed
  - Muted: Include "muted" or "inactive" in aria-label
- **Touch Target:** Minimum 44x44px for interactive badges (add padding if needed)
- **Color Contrast:** Verify entity type colors meet 4.5:1 ratio with background

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

- **Role:** `role="article"` for card container
- **ARIA Label:** `aria-labelledby="entity-name-{id}"` pointing to entity name element
- **ARIA Expanded:** `aria-expanded="true/false"` if expandable (on expand button)
- **ARIA Described By:** `aria-describedby="entity-desc-{id}"` for description
- **Keyboard Interactions:**
  - `Tab`: Focus on card (entire card is focusable container)
  - `Enter`: Open entity details / navigate to entity page
  - `Space`: Toggle expand/collapse description
  - `Shift+Tab`: Navigate backwards
- **Focus Management:**
  - Card container: focusable with `tabindex="0"`
  - Expand button (if present): separate focusable element
  - Focus indicator: 2px offset ring, primary-500
- **States:**
  - Selected: `aria-current="true"` and visible border
  - Expanded: `aria-expanded="true"` on expand button
  - Hover: No announcement needed (visual only)
- **Screen Reader:**
  - Announce: "Entity card: {name}, {type}, {connection count} connections"
  - If expandable: "Press Space to expand description"
  - Selected state: "Selected" appended to announcement
- **Touch Target:** Minimum 44px height for entire card

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

- **Role:** `role="button"` if interactive, `role="status"` if display-only
- **ARIA Label:** `aria-label="{class} question class"` (e.g., "Schema-Probe question class")
- **ARIA Pressed:** `aria-pressed="true"` if active/selected (when filtering by this class)
- **ARIA Describedby:** `aria-describedby="question-class-tooltip-{id}"` for class description
- **Keyboard Interactions:**
  - `Tab`: Focus badge (if interactive)
  - `Enter` or `Space`: Activate badge (filter by class, select question)
  - Focus indicator: 2px offset ring in primary-500
- **Tooltip:**
  - `role="tooltip"`
  - Contains question class description
  - Example: "Schema-Probe: Questions that examine mental frameworks and assumptions"
  - Appears on hover/focus (showTooltip prop)
  - Associated via `aria-describedby`
- **Icon (Emoji):**
  - `aria-hidden="true"` (decorative, class name in label)
  - Or include emoji meaning in aria-label for clarity
- **States:**
  - Default: Standard colors, not pressed
  - Active: `aria-pressed="true"`, border treatment, shadow
  - Hover: Tooltip appears, subtle scale (respect prefers-reduced-motion)
  - Label Hidden (icon-only): Full class name in `aria-label`
- **Screen Reader Announcements:**
  - Non-interactive: "{class} question class"
  - Interactive: "{class} question class, button"
  - Active: "{class} question class, selected"
  - Tooltip content read automatically when present
- **Color Contrast:**
  - Background color meets 4.5:1 with text
  - Border/icon meet 3:1 with background
  - Each question class color verified for accessibility
- **Touch Target:** Minimum 44x44px if interactive (add padding if needed)
- **Label Hidden Mode:**
  - Icon must be at least 24px for recognizability
  - Full class name in `aria-label`
  - Tooltip essential for visual users

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

- **Role:** `role="navigation"` on container
- **ARIA Label:** `aria-label="Exploration history"` or `aria-label="Breadcrumb trail"`
- **List Structure:**
  - Use ordered list: `<ol>` with list items `<li>`
  - Semantic structure helps screen readers announce "item 1 of 5"
- **Current Item:**
  - `aria-current="page"` on current/active breadcrumb
  - Visual indicator (bold, different color) with sufficient contrast
- **Keyboard Interactions:**
  - `Tab`: Focus on first breadcrumb item
  - `Arrow Left/Right`: Navigate between breadcrumb items
  - `Enter`: Activate breadcrumb (navigate to that entity)
  - `Home`: Jump to first breadcrumb
  - `End`: Jump to last breadcrumb
- **Focus Management:**
  - Each breadcrumb item is focusable: `tabindex="0"`
  - Current item remains focusable
  - Focus indicator: 2px offset ring
- **Truncation:**
  - Ellipsis button: `aria-label="Show hidden items"`, `aria-expanded="false"`
  - When expanded: `aria-expanded="true"`
  - Tooltip shows full path: `aria-describedby="breadcrumb-tooltip-{id}"`
- **Screen Reader:**
  - Announce: "Navigation, exploration history"
  - Each item: "{entity name}, {entity type}"
  - Current item: "Current: {entity name}"
  - Truncation: "5 items total, 3 hidden"
- **Separators:**
  - Arrow separators are decorative: `aria-hidden="true"`
  - Or use CSS pseudo-elements (automatically hidden from screen readers)
- **Touch Target:** Minimum 44x44px for each breadcrumb item

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

- **Role:** `role="img"` or `role="region"` with label
- **ARIA Label:** `aria-label="Graph overview minimap, shows {nodeCount} entities"`
- **ARIA Roledescription:** `aria-roledescription="minimap navigation"`
- **ARIA Describedby:** `aria-describedby="minimap-instructions-{id}"` for usage instructions
- **Keyboard Interactions:**
  - `Tab`: Focus minimap viewport indicator
  - `Arrow Keys`: Pan main viewport (20px per press)
  - `+/-`: Zoom main viewport
  - `Enter`: Center main viewport on minimap focus point
  - `Escape`: Return focus to main graph
- **Viewport Indicator:**
  - Focusable element: `tabindex="0"`
  - `aria-label="Current viewport, use arrow keys to pan"`
  - Focus indicator: Distinct from viewport rectangle
  - Draggable with mouse: Visual feedback during drag
- **Focus Management:**
  - Minimap is independently focusable
  - Does not trap focus
  - Focus indicator visible on viewport rectangle
  - Focus returns to main graph when appropriate
- **Screen Reader Support:**
  - Viewport changes announced via `aria-live="polite"` in main canvas
  - "Viewport moved to {position}"
  - Node clusters: Described in instructions
- **Collapse/Expand:**
  - Toggle button: `aria-label="Collapse minimap"` or `aria-label="Expand minimap"`
  - `aria-expanded="true/false"` on toggle button
  - Collapsed: Only toggle button visible
  - Expanded: Full minimap shown
- **Instructions (Hidden but Accessible):**
  - "Use arrow keys to pan the main graph viewport"
  - "Drag the viewport rectangle to navigate"
  - "Click to jump to a location"
- **Touch Target:**
  - Viewport indicator: Minimum 44x44px for dragging
  - Collapse button: Minimum 44x44px
- **Color Contrast:**
  - Viewport rectangle: 3:1 contrast with minimap background
  - Node dots: Sufficient contrast for visibility
- **Alternative:**
  - Not essential for navigation (redundant with main graph controls)
  - Can be hidden without losing functionality
  - Primarily visual aid

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

- **Role:** `role="searchbox"` on input element
- **ARIA Label:** `aria-label="Search entities and content"` (or more specific: "Search {context}")
- **ARIA Described By:** `aria-describedby="search-error-{id}"` when error present
- **ARIA Busy:** `aria-busy="true"` when loading (announces "searching" to screen readers)
- **ARIA Invalid:** `aria-invalid="true"` when error state
- **Keyboard Interactions:**
  - Global shortcut (Cmd/Ctrl+K): Focus search input
  - `Escape`: Clear search input and close suggestions
  - `Down Arrow`: Navigate to first suggestion (if suggestions present)
  - `Enter`: Submit search / select highlighted suggestion
  - Tab: Exit search field normally
- **Clear Button:**
  - `aria-label="Clear search"`
  - `role="button"`
  - `tabindex="0"`
  - Visible only when input has value
- **Loading State:**
  - Spinner has `aria-hidden="true"` (decorative)
  - Loading announced via `aria-busy` and live region
- **Error State:**
  - Error message: `role="alert"` with `aria-live="assertive"`
  - Associated with input via `aria-describedby`
  - Red border with 3:1 contrast ratio
- **Suggestions (if present):**
  - Container: `role="listbox"`
  - Items: `role="option"`
  - Active item: `aria-selected="true"`
  - Input has `aria-controls="suggestions-list-{id}"`
  - Input has `aria-expanded="true"` when suggestions visible
- **Screen Reader Announcements:**
  - On search start: "Searching..."
  - On results: "Found {count} results"
  - On error: Error message
  - On clear: "Search cleared"
- **Touch Target:** Minimum 44px height for input and clear button

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

- **Role:** `role="group"` on container
- **ARIA Label:** `aria-label="Filter by entity type"` or `aria-label="Entity type filters"`
- **Each Pill:**
  - `role="checkbox"` (multi-select) or `role="radio"` (single-select)
  - `aria-checked="true/false"` for current state
  - `aria-label="{EntityType} filter"` (e.g., "Concept filter")
  - Checkmark icon: `aria-hidden="true"` (decorative, state conveyed by aria-checked)
- **Keyboard Interactions:**
  - `Tab`: Move to next pill
  - `Shift+Tab`: Move to previous pill
  - `Space`: Toggle pill on/off
  - `Enter`: Alternative toggle (also supported)
  - Arrow keys (optional): Navigate between pills within group
- **Focus Management:**
  - Each pill is independently focusable: `tabindex="0"`
  - Focus indicator: 2px offset ring in primary-500
  - High contrast against pill background
  - Disabled pills: `tabindex="-1"`, not focusable
- **States:**
  - Selected (ON): `aria-checked="true"`, visual checkmark, entity color background
  - Unselected (OFF): `aria-checked="false"`, gray background
  - Disabled: `aria-disabled="true"`, reduced opacity, cursor not-allowed
- **Screen Reader Announcements:**
  - On toggle: "Concept filter checked" or "Concept filter unchecked"
  - Group label read before first pill
  - State changes announced automatically via aria-checked
- **Multi-Select Context:**
  - If multiSelect=true: Use `role="checkbox"`
  - If multiSelect=false: Use `role="radiogroup"` on container, `role="radio"` on pills
  - Radio group: Only one pill selected at a time
- **Touch Target:** Minimum 44x44px for each pill (increase padding if needed)
- **Color Contrast:**
  - Selected state: Verify entity color meets 4.5:1 with white text
  - Unselected state: Gray background meets 4.5:1 with text
  - Focus indicator: 3:1 contrast with pill background

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

- **Role:** `role="status"` on container
- **ARIA Live:** `aria-live="polite"` for status change announcements
- **ARIA Atomic:** `aria-atomic="true"` (reads entire status on change)
- **ARIA Label:** `aria-label="Sync status: {status}"` with full context
  - Example: "Sync status: Synced 2 minutes ago"
  - Example: "Sync status: Syncing in progress"
  - Example: "Sync status: Error, last synced 5 minutes ago"
- **Status Text:**
  - Visible status text updates in sync with aria-label
  - Use same wording for consistency
  - Include timestamp in readable format ("2 minutes ago", not "2m")
- **Icon:**
  - `aria-hidden="true"` (decorative, status conveyed by text)
  - Or include icon meaning in aria-label if icon-only mode
- **Interactive Mode (Manual Sync Button):**
  - If clickable: `role="button"` on container or separate button
  - `aria-label="Trigger manual sync"`
  - `tabindex="0"`
  - `aria-disabled="true"` when syncing (prevent duplicate actions)
  - Keyboard: `Enter` or `Space` to activate
- **States:**
  - Synced: Green checkmark, "Synced {time} ago"
  - Syncing: Animated spinner, "Syncing in progress"
  - Error: Red X, "Sync failed: {error message}"
  - Offline: Gray icon, "Offline, sync unavailable"
- **Screen Reader Announcements:**
  - Synced: "Sync complete" (automatically via aria-live)
  - Syncing: "Syncing started" on start, no continuous announcements
  - Error: "Sync error: {error message}" (assertive via role="alert")
  - Offline: "Connection lost, sync unavailable"
- **Error State:**
  - Error message: Full text in tooltip
  - `role="alert"` for error announcements (higher priority)
  - `aria-describedby="sync-error-{id}"` pointing to detailed error
- **Tooltip:**
  - `role="tooltip"`
  - `id="sync-status-tooltip-{id}"`
  - Associated via `aria-describedby`
  - Shows: Last sync time, next sync time, sync status details
  - Visible on hover/focus
- **Animation:**
  - Spinner: Respects `prefers-reduced-motion`
  - If motion reduced: Use static icon or gentle pulse
  - Continuous spin only during active syncing
- **Compact Mode:**
  - Icon-only: Full status in `aria-label`
  - Tooltip always available for detailed info
  - Ensure icon is large enough (minimum 16px, prefer 20px)
- **Touch Target:** Minimum 44x44px if interactive

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

- **Role:** `role="toolbar"` on container
- **ARIA Label:** `aria-label="Text selection actions"`
- **ARIA Orientation:** `aria-orientation="horizontal"`
- **Action Buttons:**
  - Each button: `aria-label="{Action name}: {selected text snippet}"` (e.g., "Look up: cognitive load")
  - Icon-only buttons must have text labels
  - Minimum 44x44px touch target (critical for mobile)
- **Keyboard Interactions:**
  - `Tab`: Focus first action button
  - `Arrow Left/Right`: Navigate between action buttons
  - `Enter` or `Space`: Execute action
  - `Escape`: Dismiss selection bar and clear selection
  - `Shift+Tab`: Navigate backwards
- **Focus Management:**
  - On appear: Auto-focus first action button
  - Focus trap: Keep focus within toolbar
  - On dismiss: Return focus to reading content
  - Focus indicator: High contrast ring (white or primary color on dark background)
- **Positioning:**
  - Use `aria-describedby` to associate with selected text
  - Avoid covering selected text (position above/below)
  - Ensure adequate contrast with background (dark bar on light content)
- **Screen Reader Announcements:**
  - On appear: "Text selection toolbar, {actionCount} actions available"
  - Selected text: Read by screen reader automatically (text selection)
  - Action result: Announce via `aria-live="polite"` region
    - "Added highlight"
    - "Note created"
    - "Lookup for cognitive load"
- **Animation:**
  - Respect `prefers-reduced-motion`
  - Fade-in: 200ms or instant if motion reduced
  - Smooth position adjustment as selection changes
- **Mobile Considerations:**
  - Larger touch targets (48x48px minimum)
  - Position to avoid keyboard overlap
  - Consider bottom position on mobile
- **Visibility:**
  - `aria-hidden="true"` when not visible
  - Remove from tab order when hidden
  - Use `display: none` or `visibility: hidden` (not just opacity)

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

- **Role:** `role="dialog"` when half/full, `role="region"` when collapsed
- **ARIA Modal:** `aria-modal="true"` when full screen (traps focus)
- **ARIA Label:** `aria-labelledby="sheet-title-{id}"` or `aria-label="Entity details sheet"`
- **ARIA Hidden:** `aria-hidden="true"` when fully closed (not just collapsed)
- **Drag Handle:**
  - `role="slider"` or `role="separator"`
  - `aria-label="Drag to resize sheet"`
  - `aria-orientation="vertical"`
  - `aria-valuenow="{currentState}"` (0=collapsed, 1=half, 2=full)
  - `aria-valuetext="{stateLabel}"` ("Collapsed", "Half screen", "Full screen")
  - `tabindex="0"` (keyboard accessible)
- **Keyboard Interactions:**
  - `Escape`: Collapse sheet (or close if already collapsed)
  - `Arrow Up/Down` on handle: Change sheet state
  - `Tab`: Navigate content (trapped when full screen)
  - `Shift+Tab`: Navigate backwards
- **Focus Management:**
  - Collapsed: No focus trap, handle is focusable
  - Half: No focus trap, content remains accessible
  - Full: Focus trap enabled, Escape to exit
  - On expand: Focus moves to first interactive element or sheet title
  - On collapse: Focus returns to trigger element or handle
  - Save and restore focus appropriately
- **Touch Gestures:**
  - Swipe up: Expand sheet
  - Swipe down: Collapse sheet
  - Ensure touch target for handle is 44px tall minimum
- **Screen Reader Announcements:**
  - State change: "Sheet expanded to {state}" via `aria-live="polite"`
  - Opening: "Dialog opened" (if modal)
  - Closing: "Dialog closed"
  - Use status region for non-modal announcements
- **Content:**
  - Scrollable content: `aria-label="Sheet content"` on scroll container
  - Overflow: Ensure scrollable region is keyboard accessible
  - Long content: Virtual scrolling for performance
- **Backdrop (when full):**
  - Semi-transparent overlay behind sheet
  - Click to collapse (if not modal)
  - `aria-hidden="true"` (decorative)
- **Animation:**
  - Respect `prefers-reduced-motion`
  - Instant snap if motion reduced
  - Otherwise smooth 300ms ease-out
- **Mobile Optimization:**
  - Handles touch gestures with appropriate thresholds
  - Momentum scrolling within content
  - Safe area insets respected (notch, home indicator)

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

- **Role:** `role="button"` (interactive node)
- **ARIA Label:** `aria-label="{name}, {type}, {connectionCount} connections"`
  - Example: "Cognitive Load, Concept, 12 connections"
- **ARIA Pressed:** `aria-pressed="true"` if selected/active
- **ARIA Describedby:** `aria-describedby="node-tooltip-{id}"` for extended info
- **Keyboard Interactions:**
  - `Tab`: Navigate to next node
  - `Shift+Tab`: Navigate to previous node
  - `Enter`: Select node (primary action)
  - `Space`: Expand/show node connections
  - `Escape`: Deselect node
  - Arrow keys: Handled by parent GraphCanvas for viewport navigation
- **Focus Management:**
  - Each node: `tabindex="0"` or managed by canvas
  - Focus indicator: 3px ring offset from node circle
  - High contrast: primary-500 or white (depending on background)
  - Selected node: Additional visual treatment (thicker border)
- **States:**
  - Default: `aria-pressed="false"`
  - Selected: `aria-pressed="true"`, announced as "selected"
  - Active: Additional pulse animation (respect prefers-reduced-motion)
  - Muted: `aria-disabled="true"`, reduced opacity, not interactive
  - Hover: Tooltip appears (via aria-describedby)
- **Screen Reader Announcements:**
  - On selection: "{name} selected, {type} entity"
  - On expansion: "Showing {count} related entities"
  - On deselection: "{name} deselected"
- **Node Label:**
  - Text label below node is decorative (already in aria-label)
  - Use `aria-hidden="true"` on label if node has aria-label
  - Or make label the accessible name source
- **Tooltip:**
  - Appears on hover/focus
  - `role="tooltip"`
  - `id` referenced by node's `aria-describedby`
  - Contains full name if truncated, description, connection count
- **Touch Target:**
  - Minimum 44x44px for interactive area (expand beyond visual circle if needed)
  - Use padding/transparent hit area for small nodes
- **Color Contrast:**
  - Border color meets 3:1 with background
  - Text label meets 4.5:1 with background
  - Focus indicator meets 3:1 with node and background
- **Animation:**
  - Respect `prefers-reduced-motion`
  - Disable pulse/glow animations if motion reduced
  - Maintain state indication without animation

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

- **Role:** `role="img"` (represents visual connection)
- **ARIA Label:** `aria-label="Connection from {source} to {target}"`
  - If relationship typed: `aria-label="{source} {relationship} {target}"`
  - Example: "Cognitive Load influences Working Memory"
  - Directed: Include direction in label
- **ARIA Describedby:** `aria-describedby="edge-tooltip-{id}"` for detailed relationship info
- **Keyboard Navigation:**
  - Edges are not directly keyboard focusable
  - Navigate via connected nodes (Tab to nodes)
  - Relationship info announced when node is selected
  - Alternative: List view of relationships for keyboard users
- **Hover/Focus:**
  - Hover triggers tooltip with relationship details
  - When connected node is focused, related edges can be highlighted
  - Screen reader announces relationships when node is selected
- **Tooltip:**
  - `role="tooltip"`
  - Contains: Relationship type, strength, description
  - Example: "influences (strength: 0.8) - Cognitive Load affects the capacity of Working Memory"
  - Appears on edge hover or when either node is focused
- **Visual Only:**
  - Edge is primarily visual representation
  - Full relationship information provided through:
    - Node announcements (lists connected entities)
    - Tooltip on hover
    - Alternative list view of relationships
- **Screen Reader Support:**
  - When node is selected, announce: "{name} connected to {count} entities"
  - List connected entities in FlowPanel or details view
  - Provide "View relationships" button for text-based navigation
- **Arrow/Direction:**
  - Directional relationships: Include direction in aria-label
  - "Cognitive Load influences Working Memory" (not bidirectional)
  - Non-directed: "Connected to" or "Related to"
- **Label on Edge:**
  - Relationship label text: `aria-hidden="true"` (already in edge aria-label)
  - Or make label the primary accessible name source
- **Color Coding:**
  - If edges use color for relationship types:
    - Don't rely solely on color (include label/icon)
    - Ensure sufficient contrast (3:1 minimum)
    - Pattern/dash style as additional indicator
- **Alternative Access:**
  - Provide "Relationships" list in entity detail panel
  - Keyboard-accessible list of all connections
  - "View as list" toggle for non-visual users
  - List includes all relationship info without requiring graph interaction

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

- **Role:** `role="application"` (tells screen readers this uses custom keyboard interactions)
- **ARIA Label:** `aria-label="Entity relationship graph, {nodeCount} entities, {edgeCount} connections"`
- **ARIA Roledescription:** `aria-roledescription="interactive graph visualization"`
- **Keyboard Interactions (Graph Navigation):**
  - `Arrow Keys`: Pan viewport (20px per press, hold for continuous)
  - `+` or `=`: Zoom in
  - `-`: Zoom out
  - `0`: Reset to 100% zoom
  - `Home`: Fit all nodes in view
  - `F`: Alternative fit-to-view shortcut
  - `Tab`: Navigate between graph nodes (logical order)
  - `Enter` on node: Select/activate node
  - `Space` on node: Expand node connections
  - `Escape`: Clear selection
  - `Ctrl/Cmd + F`: Focus search (if present)
- **Focus Management:**
  - Canvas container: `tabindex="0"` (receives focus for arrow key navigation)
  - Individual nodes: `tabindex="0"` or managed via `aria-activedescendant`
  - Zoom controls: Standard button focus
  - Active node highlighted with visible focus ring
- **Screen Reader Support:**
  - Viewport changes: Announced via `aria-live="polite"` region
    - "Zoomed in to {zoom}%"
    - "Panned to {position}"
    - "Fit to view, showing all {count} entities"
  - Node selection: "Selected {entityName}, {entityType}"
  - Loading: `aria-busy="true"` with "Loading graph" announcement
  - Empty state: "No entities to display"
- **Graph Controls:**
  - Zoom in button: `aria-label="Zoom in"`, keyboard shortcut displayed
  - Zoom out button: `aria-label="Zoom out"`
  - Fit view button: `aria-label="Fit all entities in view"`
  - Reset button: `aria-label="Reset graph view"`
  - All buttons: minimum 44x44px touch target
- **Alternative Access:**
  - Provide text-based entity list as alternative navigation method
  - "View as list" toggle for non-visual access
  - Keyboard-only users can navigate via Tab through nodes
- **Grid Background:**
  - Decorative only: `aria-hidden="true"`
  - Or use CSS background (not in DOM)
- **Animation:**
  - Respect `prefers-reduced-motion`
  - Disable pan/zoom animations if motion reduced
  - Instant transitions instead of smooth
- **Instructions:**
  - Provide keyboard shortcuts help: `aria-describedby="graph-instructions-{id}"`
  - Instructions region: Hidden but accessible
  - Keyboard shortcut: `?` to show instructions modal

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

- **Role:** `role="complementary"` (or `role="region"` with label)
- **ARIA Label:** `aria-label="Entity exploration panel"` or `aria-labelledby="panel-title-{id}"`
- **ARIA Hidden:** `aria-hidden="true"` when collapsed (removes from accessibility tree)
- **ARIA Expanded:** `aria-expanded="true/false"` on toggle button
- **Keyboard Interactions:**
  - `Escape`: Close panel and return focus to trigger element
  - `Tab`: Navigate through panel contents (trapped when open)
  - `Shift+Tab`: Navigate backwards (trapped within panel)
  - Panel toggle button: `Enter` or `Space` to open/close
- **Focus Management (Critical):**
  - On open: Move focus to first focusable element (usually close button or first interactive element)
  - Focus trap: Tab cycles within panel boundaries
  - Save previous focus: Return to it on close
  - First focusable: Close button or panel title
  - Last focusable: Last action button in panel
- **Resize Handle:**
  - `role="separator"`
  - `aria-label="Resize exploration panel"`
  - `aria-orientation="vertical"`
  - `aria-valuenow="{currentWidth}"`
  - `aria-valuemin="{minWidth}"`
  - `aria-valuemax="{maxWidth}"`
  - Keyboard: `Arrow Left/Right` to resize (10px increments)
  - Screen reader: Announce width changes "Panel width {width} pixels"
- **Close Button:**
  - `aria-label="Close exploration panel"`
  - Visible and first in focus order
  - Icon button needs text label
- **Screen Reader Announcements:**
  - On open: "Exploration panel opened"
  - On close: "Exploration panel closed"
  - Use `aria-live="polite"` region for panel status
- **Mobile Considerations:**
  - On mobile, use BottomSheet instead (different focus trap behavior)
  - Ensure touch target sizes meet 44x44px minimum
- **Animation:**
  - Respect `prefers-reduced-motion`
  - Instant open/close if motion reduced
  - Otherwise smooth 300ms transition
- **Touch Target:** Close button minimum 44x44px

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

- **Role:** `role="tablist"` on container
- **ARIA Label:** `aria-label="Thinking mode selector"` or `aria-label="View switcher"`
- **ARIA Orientation:** `aria-orientation="horizontal"` (or "vertical" if vertical tabs)
- **Each Tab:**
  - `role="tab"`
  - `aria-selected="true"` for active tab, `"false"` for others
  - `aria-controls="tabpanel-{id}"` pointing to associated panel
  - `aria-label="{TabName} mode"` (e.g., "Flow mode")
  - `tabindex="0"` for active tab, `"-1"` for inactive tabs
- **Tab Panel:**
  - `role="tabpanel"`
  - `id="tabpanel-{id}"` (referenced by tab's aria-controls)
  - `aria-labelledby="tab-{id}"` (references controlling tab)
  - `tabindex="0"` (focusable for keyboard scrolling)
- **Keyboard Interactions:**
  - `Tab`: Enter/exit tab list (focus active tab)
  - `Arrow Left`: Navigate to previous tab (circular)
  - `Arrow Right`: Navigate to next tab (circular)
  - `Home`: Jump to first tab
  - `End`: Jump to last tab
  - `Enter` or `Space`: Activate focused tab (switch mode)
  - Shortcuts (if defined): e.g., `Ctrl+1` for first tab
- **Focus Management:**
  - Roving tabindex: Only active tab is in tab order
  - Arrow keys move focus between tabs
  - Entering tab list focuses active tab
  - Focus indicator: 2px offset ring
  - Clear visual distinction for focused vs active tab
- **States:**
  - Active: `aria-selected="true"`, visual indicator (border/background)
  - Inactive: `aria-selected="false"`, muted appearance
  - Disabled: `aria-disabled="true"`, `tabindex="-1"`, cannot be selected
  - Hover: Visual feedback (not announced)
- **Screen Reader Announcements:**
  - On tab focus: "{TabName}, tab, {position} of {total}"
  - Active tab: "Selected" appended
  - On activation: "{TabName} tab selected"
  - Tab panel content announced when panel gains focus
- **Badge (Notification Count):**
  - Visual badge only: Include count in aria-label
  - Example: `aria-label="Forge mode, 3 notifications"`
  - Or use `aria-describedby` pointing to badge
- **Keyboard Shortcuts:**
  - Display shortcut hints visually (e.g., "⌘1")
  - Register globally (not just when tab list focused)
  - Document in instructions or help
- **Touch Target:**
  - Minimum 44x44px for each tab
  - Adequate spacing between tabs for touch accuracy
- **Color Contrast:**
  - Active indicator meets 3:1 with background
  - Text meets 4.5:1 in all states
  - Disabled tabs meet 3:1 minimum (can be lower opacity)
- **Icon + Text:**
  - Icon: `aria-hidden="true"` (decorative, meaning in label)
  - Text: Provides accessible name
  - If icon-only: Must have text label (visible or aria-label)

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
