# IES Design System v2 — Modern Information Space

**Date:** 2025-12-06
**Status:** Design Complete
**Replaces:** UNIFIED-DESIGN-SYSTEM.md ("Contemplative Knowledge Space")

## Philosophy

**Previous:** "Contemplative Knowledge Space" — warm, vintage, reading room aesthetic
**New:** "Modern Information Space" — sleek, alive, information-dense

Inspired by:
- **Linear** — Dark, minimal, surgical precision
- **Raycast** — Floating panels, blur effects, keyboard-elegant
- **Arc** — Bold colors, rounded, playful-premium

## Color System

### Dark Mode (Default)

```css
:root {
  /* Base */
  --bg-primary: #0f0f10;      /* Near black, warm undertone */
  --bg-secondary: #1a1a1c;    /* Elevated surfaces */
  --bg-tertiary: #252528;     /* Cards, panels */
  --bg-hover: #2a2a2e;        /* Hover states */

  /* Text */
  --text-primary: #f5f5f5;    /* Primary content */
  --text-secondary: #a0a0a5;  /* Secondary, labels */
  --text-muted: #6b6b70;      /* Disabled, hints */

  /* Borders */
  --border-subtle: #2a2a2e;   /* Dividers */
  --border-default: #3a3a3e;  /* Input borders */
  --border-focus: #5a5a60;    /* Focus states */
}
```

### Light Mode (Optional)

```css
:root.light {
  --bg-primary: #fafafa;
  --bg-secondary: #f0f0f2;
  --bg-tertiary: #ffffff;
  --bg-hover: #e8e8ea;

  --text-primary: #1a1a1c;
  --text-secondary: #6b6b70;
  --text-muted: #a0a0a5;

  --border-subtle: #e0e0e2;
  --border-default: #d0d0d2;
  --border-focus: #b0b0b5;
}
```

### Entity Colors (The Accent System)

No single accent color. Entity types provide visual interest:

```css
:root {
  /* Entity Type Colors — Bold, not muted */
  --entity-concept: #3b82f6;      /* Blue */
  --entity-person: #10b981;       /* Green */
  --entity-theory: #8b5cf6;       /* Purple */
  --entity-framework: #f59e0b;    /* Amber */
  --entity-assessment: #ef4444;   /* Red */
  --entity-spark: #ec4899;        /* Pink */
  --entity-insight: #06b6d4;      /* Cyan */
  --entity-thread: #84cc16;       /* Lime */

  /* Gradients for active states */
  --gradient-concept: linear-gradient(135deg, #3b82f6, #1d4ed8);
  --gradient-person: linear-gradient(135deg, #10b981, #059669);
  --gradient-theory: linear-gradient(135deg, #8b5cf6, #6d28d9);
  --gradient-framework: linear-gradient(135deg, #f59e0b, #d97706);
  --gradient-assessment: linear-gradient(135deg, #ef4444, #dc2626);
}
```

### Semantic Colors

```css
:root {
  --success: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;
  --info: #3b82f6;
}
```

## Typography

Sans-serif primary. No serifs.

```css
:root {
  /* Font Families */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Font Sizes */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 2rem;      /* 32px */

  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

### Usage

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Body | --font-sans | --text-base | normal |
| Headings | --font-sans | --text-xl+ | semibold |
| Labels | --font-sans | --text-sm | medium |
| Metadata | --font-mono | --text-xs | normal |
| Entity IDs | --font-mono | --text-sm | normal |
| Code | --font-mono | --text-sm | normal |

## Spacing

8px base unit.

```css
:root {
  --space-0: 0;
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
}
```

## Borders & Radius

Rounded corners on interactive elements.

```css
:root {
  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;

  /* Border Width */
  --border-thin: 1px;
  --border-medium: 2px;
}
```

## Shadows & Depth

Subtle shadows for floating panels.

```css
:root {
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.6);

  /* Glass effect for floating panels */
  --glass-bg: rgba(26, 26, 28, 0.8);
  --glass-blur: blur(12px);
  --glass-border: 1px solid rgba(255, 255, 255, 0.1);
}
```

## Animations

Smooth, fast transitions.

```css
:root {
  /* Durations */
  --duration-instant: 100ms;
  --duration-fast: 150ms;
  --duration-base: 200ms;
  --duration-slow: 300ms;

  /* Easings */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

## Components

### Buttons

```css
.btn {
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-primary {
  background: var(--gradient-concept);
  color: white;
  border: none;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: var(--border-thin) solid var(--border-default);
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: none;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
```

### Cards

```css
.card {
  background: var(--bg-tertiary);
  border: var(--border-thin) solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}

.card-hover:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
}
```

### Floating Panels (Glass Effect)

```css
.panel-floating {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  border: var(--glass-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
}
```

### Entity Badges

```css
.entity-badge {
  font-family: var(--font-sans);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-full);
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
}

.entity-badge[data-type="concept"] {
  background: rgba(59, 130, 246, 0.15);
  color: var(--entity-concept);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.entity-badge[data-type="person"] {
  background: rgba(16, 185, 129, 0.15);
  color: var(--entity-person);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

/* ... similar for other entity types */
```

### Inputs

```css
.input {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  padding: var(--space-2) var(--space-3);
  background: var(--bg-secondary);
  border: var(--border-thin) solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  transition: border-color var(--duration-fast) var(--ease-out);
}

.input:focus {
  outline: none;
  border-color: var(--entity-concept);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.input::placeholder {
  color: var(--text-muted);
}
```

### Keyboard Shortcuts

```css
.kbd {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  padding: var(--space-1) var(--space-2);
  background: var(--bg-secondary);
  border: var(--border-thin) solid var(--border-default);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
}
```

## Layout Patterns

### Information Dense

- Tight spacing (--space-2 to --space-4 between elements)
- Multiple columns where appropriate
- Collapsible sections
- No wasted whitespace

### Mobile Full-Screen App

```css
.app-container {
  min-height: 100vh;
  min-height: 100dvh; /* Dynamic viewport height */
  background: var(--bg-primary);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
}

.app-header {
  position: sticky;
  top: 0;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  border-bottom: var(--glass-border);
  padding: var(--space-3) var(--space-4);
  z-index: 100;
}

.app-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
}
```

## Migration Notes

### What Changes

| Old | New |
|-----|-----|
| Warm paper tones (#f8f6f3) | Dark primary (#0f0f10) |
| Crimson Pro serif | Inter sans-serif |
| Amber accent (#d4a574) | Entity colors as accents |
| Soft, calm aesthetic | Bold, alive aesthetic |
| Reading room philosophy | Information space philosophy |

### Entity Colors (Unchanged)

The entity type colors remain similar but are now bolder/more saturated:
- Concept: Blue (slightly brighter)
- Person: Green (slightly brighter)
- Theory: Purple (unchanged)
- Framework: Amber/Orange (unchanged)
- Assessment: Red (unchanged)

## Success Criteria

- [ ] Dark mode is default across SiYuan plugin and IES Reader
- [ ] No serif fonts in UI (content may still use them)
- [ ] Entity colors provide visual interest throughout
- [ ] Floating panels use glass effect
- [ ] Transitions are smooth and fast
- [ ] Feels modern, not vintage
- [ ] Information-dense, no wasted space
