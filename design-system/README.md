# IES Design System

**"Hybrid Contemplative"** - A unified design system for the Intelligent Exploration System

## Philosophy

Combines the best elements from multiple design approaches:

| Source | Contribution |
|--------|--------------|
| **Scholar's Library** | Warm paper tones, serif display typography, intellectual warmth |
| **Cupertino** | Layered shadows, smooth easing curves, tactile feedback |
| **Neurogarden** | ADHD-friendly patterns, energy levels, resonance signals |
| **Asri** | Spring animations, modern geometry, clean spacing |

## Quick Start

### 1. Include Google Fonts

```html
<link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;500;600&family=Nunito:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

### 2. Import the Design System

**CSS:**
```css
@import 'design-system/tokens/index.css';
```

**SCSS:**
```scss
@use 'design-system/tokens/index.css';
```

### 3. Use the Tokens

```css
.my-card {
  background: var(--ies-bg-elevated);
  border-radius: var(--ies-radius-card);
  box-shadow: var(--ies-shadow-card);
  padding: var(--ies-card-padding);
  transition: var(--ies-transition-all);
}

.my-card:hover {
  box-shadow: var(--ies-shadow-card-hover);
  transform: translateY(-2px);
}
```

## Token Files

| File | Contents |
|------|----------|
| `tokens/colors.css` | Color palette, entity types, question classes, energy levels |
| `tokens/typography.css` | Font families, size scale, weights, line heights |
| `tokens/spacing.css` | Spacing scale, border radius, container widths |
| `tokens/shadows.css` | Layered shadows, glows, dark theme variants |
| `tokens/animations.css` | Easing functions, durations, keyframes |
| `tokens/index.css` | Combined tokens + component patterns |

## Color System

### Backgrounds
```css
--ies-bg-deep: #f5f2ed;      /* Sidebars, wells */
--ies-bg-base: #faf8f5;      /* Main content */
--ies-bg-elevated: #ffffff;   /* Cards, modals */
--ies-bg-overlay: rgba(250, 248, 245, 0.95);
```

### Accent Colors
```css
--ies-accent: #c9872e;       /* Amber/gold - primary actions */
--ies-secondary: #5a8a7a;    /* Sage green - knowledge/growth */
--ies-tertiary: #8b7aa0;     /* Soft violet - reflection/depth */
```

### Entity Types
```css
--ies-entity-concept: #2563eb;    /* Blue */
--ies-entity-person: #059669;     /* Green */
--ies-entity-theory: #7c3aed;     /* Purple */
--ies-entity-framework: #ea580c;  /* Orange */
--ies-entity-assessment: #dc2626; /* Red */
```

### Question Classes (9 cognitive functions)
```css
--ies-q-schema: #4a90d9;          /* Structure */
--ies-q-boundary: #7b68ee;        /* Edges */
--ies-q-dimensional: #20b2aa;     /* Spectra */
--ies-q-causal: #d4874a;          /* Mechanisms */
--ies-q-counterfactual: #da70d6;  /* What-if */
--ies-q-anchor: #3cb371;          /* Concrete */
--ies-q-perspective: #cd853f;     /* Viewpoint */
--ies-q-meta: #778899;            /* Thinking */
--ies-q-synthesis: #6495ed;       /* Integration */
```

### Energy Levels (ADHD navigation)
```css
--ies-energy-low: #6b8e9f;
--ies-energy-medium: #c98b2f;
--ies-energy-high: #d94f5c;
```

## Typography

### Font Stack
```css
--ies-font-display: 'Crimson Pro', Georgia, serif;     /* Headings */
--ies-font-body: 'Nunito', -apple-system, sans-serif;  /* Body text */
--ies-font-mono: 'JetBrains Mono', monospace;          /* Code */
```

### Size Scale (Major Third 1.25 ratio)
```css
--ies-text-xs: 0.75rem;    /* 12px */
--ies-text-sm: 0.875rem;   /* 14px */
--ies-text-base: 1rem;     /* 16px */
--ies-text-lg: 1.125rem;   /* 18px */
--ies-text-xl: 1.25rem;    /* 20px */
--ies-text-2xl: 1.5rem;    /* 24px */
--ies-text-3xl: 1.875rem;  /* 30px */
--ies-text-4xl: 2.25rem;   /* 36px */
```

## Animation

### Easing (Cupertino signature)
```css
--ies-ease-cupertino: cubic-bezier(0.32, 0.72, 0, 1);  /* Default */
--ies-ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);  /* Bouncy */
```

### Durations
```css
--ies-duration-fast: 160ms;   /* Quick interactions */
--ies-duration-base: 320ms;   /* Default animations */
--ies-duration-slow: 640ms;   /* Deliberate motion */
```

### Presets
```css
--ies-transition-fast: 160ms cubic-bezier(0.32, 0.72, 0, 1);
--ies-transition-base: 320ms cubic-bezier(0.32, 0.72, 0, 1);
```

## Dark Theme

Apply dark theme with either:
- `[data-theme-mode="dark"]` attribute (SiYuan)
- `.dark` class (Readest/general)

```html
<div data-theme-mode="dark">...</div>
<!-- or -->
<div class="dark">...</div>
```

## Component Classes

Pre-built component patterns:

```css
.ies-card          /* Card container */
.ies-btn           /* Base button */
.ies-btn-primary   /* Primary action button */
.ies-btn-secondary /* Secondary button */
.ies-btn-outline   /* Ghost/outline button */
.ies-input         /* Text input */
.ies-chip          /* Badge/pill */
```

Entity type chips:
```css
.ies-entity-concept
.ies-entity-person
.ies-entity-theory
.ies-entity-framework
.ies-entity-assessment
```

Question class chips:
```css
.ies-q-schema
.ies-q-boundary
.ies-q-dimensional
.ies-q-causal
.ies-q-counterfactual
.ies-q-anchor
.ies-q-perspective
.ies-q-meta
.ies-q-synthesis
```

Energy level badges:
```css
.ies-energy-low
.ies-energy-medium
.ies-energy-high
```

## Accessibility

- Respects `prefers-reduced-motion` media query
- WCAG 2.1 AA contrast ratios maintained
- Clear visual hierarchy reduces cognitive load
- ADHD-friendly patterns (energy levels, resonance signals)

## Usage in Projects

### SiYuan Plugin (Svelte)
Import in `design-system.scss`:
```scss
@import 'path/to/design-system/tokens/index.css';
```

### Readest (React/Next.js)
Import in `globals.css`:
```css
@import 'path/to/design-system/tokens/index.css';
```

## Design Previews

Interactive previews of all design options are available in `/design-previews/`:
- `index.html` - Navigation hub
- `option-6-hybrid.html` - This design system (RECOMMENDED)
- `typography-options.html` - Font comparisons
- `color-alternatives.html` - Palette alternatives
