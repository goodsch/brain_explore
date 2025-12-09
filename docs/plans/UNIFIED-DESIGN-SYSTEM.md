# IES Unified Design System

**Version:** 1.0.0
**Date:** 2025-12-05
**Aesthetic:** Contemplative Knowledge Space

---

## Design Philosophy

### Core Concept: The Reading Room

Imagine a personal library where natural light streams through tall windows, casting warm shadows on well-worn books. This is the IES aesthetic: **intellectual warmth** meeting **focused clarity**.

**Key Principles:**
1. **Quiet Confidence** — Design that supports thinking, not demands attention
2. **Warm Intellect** — Scholarly without being cold; inviting without being casual
3. **Deliberate Transitions** — Movement that guides, never startles
4. **Focused Hierarchy** — One thing matters at a time

### Design Language Summary

| Aspect | Approach |
|--------|----------|
| **Mood** | A quiet afternoon in a well-curated library |
| **Colors** | Warm paper tones, amber illumination, sage knowledge |
| **Typography** | Serif elegance for content, humanist sans for UI |
| **Interaction** | Gentle reveals, purposeful transitions |
| **Layout** | Generous breathing room, clear visual hierarchy |

---

## Typography System

### Font Stack

```css
/* Display / Headings — Scholarly elegance */
--ies-font-display: 'Crimson Pro', 'Palatino Linotype', 'Book Antiqua', Georgia, serif;

/* Body / Reading — Accessible legibility */
--ies-font-body: 'Nunito', 'Segoe UI', system-ui, -apple-system, sans-serif;

/* UI / Interface — Clean utility */
--ies-font-ui: 'Inter', 'SF Pro Text', system-ui, sans-serif;

/* Code / Mono — Technical precision */
--ies-font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
```

### Google Fonts Import

```css
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Nunito:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
```

### Type Scale

Based on a 1.25 (Major Third) scale, starting from 15px base:

| Token | Size | Line Height | Use |
|-------|------|-------------|-----|
| `--ies-text-xs` | 0.6875rem (11px) | 1.5 | Labels, captions |
| `--ies-text-sm` | 0.8125rem (13px) | 1.5 | Secondary text, metadata |
| `--ies-text-base` | 0.9375rem (15px) | 1.6 | Body text |
| `--ies-text-lg` | 1.125rem (18px) | 1.5 | Lead text, emphasis |
| `--ies-text-xl` | 1.375rem (22px) | 1.3 | Section headings |
| `--ies-text-2xl` | 1.75rem (28px) | 1.2 | Page headings |
| `--ies-text-3xl` | 2.25rem (36px) | 1.1 | Hero text |

---

## Color System

### Philosophy

Colors draw from **natural knowledge environments**: warm paper, amber lamplight, aged leather, living plants, and the quiet violet of dusk.

### Core Palette

#### Light Theme (Default)

```css
:root {
  /* === Background Layers (warm neutrals) === */
  --ies-bg-deep: #f8f6f3;        /* Aged paper base */
  --ies-bg-base: #fffef9;        /* Warm white */
  --ies-bg-elevated: #ffffff;    /* Pure white for focus */
  --ies-bg-overlay: rgba(255, 255, 255, 0.92);

  /* === Text Colors (warm grays) === */
  --ies-text-primary: #1a1816;   /* Near-black with warmth */
  --ies-text-secondary: #4a4641; /* Body text */
  --ies-text-muted: #7a756e;     /* De-emphasized */
  --ies-text-subtle: #a9a29a;    /* Hints, placeholders */

  /* === Borders === */
  --ies-border-subtle: rgba(26, 24, 22, 0.06);
  --ies-border-light: rgba(26, 24, 22, 0.10);
  --ies-border-medium: rgba(26, 24, 22, 0.15);
  --ies-border-strong: rgba(26, 24, 22, 0.25);

  /* === Accent: Amber/Gold (illumination, insight) === */
  --ies-accent: #c9872e;
  --ies-accent-rgb: 201, 135, 46;
  --ies-accent-50: #fdf8f0;
  --ies-accent-100: #fdf4e6;
  --ies-accent-200: #f5ddb8;
  --ies-accent-600: #c9872e;
  --ies-accent-700: #9a6820;
  --ies-accent-800: #7a5318;

  /* === Secondary: Sage/Teal (growth, knowledge) === */
  --ies-secondary: #5a8a7a;
  --ies-secondary-rgb: 90, 138, 122;
  --ies-secondary-50: #f0f7f5;
  --ies-secondary-100: #eef5f3;
  --ies-secondary-200: #c4ddd5;
  --ies-secondary-600: #5a8a7a;
  --ies-secondary-700: #466b5e;

  /* === Tertiary: Soft Violet (reflection, depth) === */
  --ies-tertiary: #8b7aa0;
  --ies-tertiary-rgb: 139, 122, 160;
  --ies-tertiary-50: #f5f3f8;
  --ies-tertiary-100: #f3f0f7;
  --ies-tertiary-200: #ddd6e8;
  --ies-tertiary-600: #8b7aa0;
  --ies-tertiary-700: #6b5a80;

  /* === Semantic === */
  --ies-success: #5a9a6a;
  --ies-success-bg: #f0f7f2;
  --ies-warning: #c99a40;
  --ies-warning-bg: #fdf8f0;
  --ies-error: #c45a5a;
  --ies-error-bg: #fdf2f2;
  --ies-info: #5a8aaa;
  --ies-info-bg: #f0f5f8;
}
```

#### Dark Theme

```css
[data-theme="dark"], .dark, [data-theme-mode="dark"] {
  /* === Background Layers === */
  --ies-bg-deep: #0f0e0d;
  --ies-bg-base: #1c1a18;
  --ies-bg-elevated: #242220;
  --ies-bg-overlay: rgba(28, 26, 24, 0.95);

  /* === Text Colors === */
  --ies-text-primary: #f4f2ef;
  --ies-text-secondary: #c9c5bf;
  --ies-text-muted: #8a857e;
  --ies-text-subtle: #5a5650;

  /* === Borders === */
  --ies-border-subtle: rgba(244, 242, 239, 0.04);
  --ies-border-light: rgba(244, 242, 239, 0.08);
  --ies-border-medium: rgba(244, 242, 239, 0.12);
  --ies-border-strong: rgba(244, 242, 239, 0.20);

  /* === Accent (inverted for dark) === */
  --ies-accent-50: #2a2218;
  --ies-accent-100: #3a2a18;
  --ies-accent-200: #4a3a20;

  /* === Secondary (inverted) === */
  --ies-secondary-50: #1a2522;
  --ies-secondary-100: #202a28;
  --ies-secondary-200: #2a3a35;

  /* === Tertiary (inverted) === */
  --ies-tertiary-50: #252230;
  --ies-tertiary-100: #2a2535;
  --ies-tertiary-200: #3a3545;

  /* === Shadows (deeper for dark) === */
  --ies-shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.3);
  --ies-shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.35);
  --ies-shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  --ies-shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.5);
}
```

### Entity Type Colors

Unified across SiYuan and Readest:

| Entity Type | Color | Hex | Purpose |
|-------------|-------|-----|---------|
| **Concept** | Amber | `#c9872e` | Core ideas, definitions |
| **Person** | Sage | `#5a8a7a` | Authors, theorists, figures |
| **Theory** | Violet | `#8b7aa0` | Theoretical frameworks |
| **Framework** | Terracotta | `#b86e4a` | Practical methodologies |
| **Assessment** | Slate Blue | `#5a7a9a` | Tools, measures, tests |

```css
/* Entity Type System */
--ies-entity-concept: #c9872e;
--ies-entity-concept-bg: rgba(201, 135, 46, 0.10);
--ies-entity-concept-border: rgba(201, 135, 46, 0.25);

--ies-entity-person: #5a8a7a;
--ies-entity-person-bg: rgba(90, 138, 122, 0.10);
--ies-entity-person-border: rgba(90, 138, 122, 0.25);

--ies-entity-theory: #8b7aa0;
--ies-entity-theory-bg: rgba(139, 122, 160, 0.10);
--ies-entity-theory-border: rgba(139, 122, 160, 0.25);

--ies-entity-framework: #b86e4a;
--ies-entity-framework-bg: rgba(184, 110, 74, 0.10);
--ies-entity-framework-border: rgba(184, 110, 74, 0.25);

--ies-entity-assessment: #5a7a9a;
--ies-entity-assessment-bg: rgba(90, 122, 154, 0.10);
--ies-entity-assessment-border: rgba(90, 122, 154, 0.25);
```

### Question Class Colors

For thinking partner questions in ForgeMode and Flow:

| Class | Color | Use |
|-------|-------|-----|
| **Schema-Probe** | Blue `#4a90d9` | Structure questions |
| **Boundary** | Purple `#7b68ee` | Edge/limit questions |
| **Dimensional** | Teal `#20b2aa` | Spectrum questions |
| **Causal** | Amber `#c99a40` | Mechanism questions |
| **Counterfactual** | Orchid `#da70d6` | What-if questions |
| **Anchor** | Green `#3cb371` | Example questions |
| **Perspective-Shift** | Sienna `#cd853f` | Viewpoint questions |
| **Meta-Cognitive** | Slate `#778899` | Thinking pattern questions |
| **Reflective-Synthesis** | Steel Blue `#6495ed` | Integration questions |

---

## Spacing System

### Base Unit

All spacing derived from 4px base unit:

```css
--ies-space-0: 0;
--ies-space-1: 0.25rem;  /* 4px */
--ies-space-2: 0.5rem;   /* 8px */
--ies-space-3: 0.75rem;  /* 12px */
--ies-space-4: 1rem;     /* 16px */
--ies-space-5: 1.25rem;  /* 20px */
--ies-space-6: 1.5rem;   /* 24px */
--ies-space-8: 2rem;     /* 32px */
--ies-space-10: 2.5rem;  /* 40px */
--ies-space-12: 3rem;    /* 48px */
--ies-space-16: 4rem;    /* 64px */
--ies-space-20: 5rem;    /* 80px */
```

### Component Spacing Guidelines

| Component | Padding | Gap |
|-----------|---------|-----|
| Card | `--ies-space-4` to `--ies-space-6` | — |
| Button | `--ies-space-2` vertical, `--ies-space-4` horizontal | — |
| Form Input | `--ies-space-3` | — |
| List Items | — | `--ies-space-2` to `--ies-space-3` |
| Sections | — | `--ies-space-6` to `--ies-space-8` |

---

## Border Radius

```css
--ies-radius-none: 0;
--ies-radius-sm: 6px;      /* Buttons, inputs, small chips */
--ies-radius-md: 10px;     /* Cards, panels */
--ies-radius-lg: 16px;     /* Modals, large containers */
--ies-radius-xl: 24px;     /* Hero elements */
--ies-radius-full: 9999px; /* Pills, avatars */
```

---

## Shadows

Layered shadows for natural depth:

```css
/* Light Theme */
--ies-shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.04);
--ies-shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04);
--ies-shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.04);
--ies-shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12), 0 4px 8px rgba(0, 0, 0, 0.06);
--ies-shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.15), 0 8px 16px rgba(0, 0, 0, 0.08);

/* Glow (for focus/accent states) */
--ies-shadow-glow: 0 0 20px rgba(var(--ies-accent-rgb), 0.15);
--ies-shadow-glow-strong: 0 0 30px rgba(var(--ies-accent-rgb), 0.25);
```

---

## Animation System

### Timing Functions

```css
--ies-ease-out: cubic-bezier(0.16, 1, 0.3, 1);     /* Smooth deceleration */
--ies-ease-in: cubic-bezier(0.4, 0, 1, 1);         /* Subtle acceleration */
--ies-ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);   /* Balanced */
--ies-ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1); /* Playful spring */
```

### Duration Scale

```css
--ies-duration-instant: 100ms;   /* Micro-interactions */
--ies-duration-fast: 150ms;      /* Quick state changes */
--ies-duration-normal: 200ms;    /* Default transitions */
--ies-duration-slow: 300ms;      /* Deliberate reveals */
--ies-duration-slower: 400ms;    /* Emphasis transitions */
--ies-duration-slowest: 500ms;   /* Dramatic effects */
```

### Standard Transitions

```css
--ies-transition-fast: 150ms var(--ies-ease-out);
--ies-transition-normal: 200ms var(--ies-ease-out);
--ies-transition-slow: 300ms var(--ies-ease-out);
--ies-transition-bounce: 400ms var(--ies-ease-bounce);
```

### Animation Keyframes

```css
@keyframes ies-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes ies-slide-up {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes ies-scale-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes ies-pulse-soft {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

@keyframes ies-shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Stagger utility for lists */
@keyframes ies-stagger-in {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### Motion Accessibility

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Component Primitives

### Buttons

```css
.ies-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--ies-space-2);
  padding: var(--ies-space-2) var(--ies-space-4);
  font-family: var(--ies-font-ui);
  font-size: var(--ies-text-sm);
  font-weight: 600;
  line-height: 1.4;
  color: var(--ies-text-primary);
  background: var(--ies-bg-elevated);
  border: 1px solid var(--ies-border-medium);
  border-radius: var(--ies-radius-sm);
  cursor: pointer;
  transition: all var(--ies-transition-fast);
  user-select: none;
}

.ies-btn:hover:not(:disabled) {
  background: var(--ies-bg-base);
  border-color: var(--ies-accent);
  box-shadow: var(--ies-shadow-sm);
}

.ies-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.ies-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Primary variant */
.ies-btn--primary {
  background: var(--ies-accent);
  border-color: var(--ies-accent);
  color: white;
}

.ies-btn--primary:hover:not(:disabled) {
  background: var(--ies-accent-700);
  border-color: var(--ies-accent-700);
}

/* Ghost variant */
.ies-btn--ghost {
  background: transparent;
  border-color: transparent;
}

.ies-btn--ghost:hover:not(:disabled) {
  background: var(--ies-bg-base);
}

/* Icon-only */
.ies-btn--icon {
  padding: var(--ies-space-2);
}
```

### Cards

```css
.ies-card {
  background: var(--ies-bg-elevated);
  border: 1px solid var(--ies-border-subtle);
  border-radius: var(--ies-radius-md);
  box-shadow: var(--ies-shadow-sm);
  transition: all var(--ies-transition-normal);
}

.ies-card:hover {
  box-shadow: var(--ies-shadow-md);
  border-color: var(--ies-border-light);
}

/* Interactive card */
.ies-card--interactive {
  cursor: pointer;
}

.ies-card--interactive:hover {
  transform: translateY(-2px);
}

.ies-card--interactive:active {
  transform: translateY(0);
  box-shadow: var(--ies-shadow-sm);
}

/* Accent border variants */
.ies-card--accent {
  border-left: 3px solid var(--ies-accent);
}

.ies-card--secondary {
  border-left: 3px solid var(--ies-secondary);
}
```

### Chips / Pills

```css
.ies-chip {
  display: inline-flex;
  align-items: center;
  gap: var(--ies-space-1);
  padding: var(--ies-space-1) var(--ies-space-3);
  font-family: var(--ies-font-ui);
  font-size: var(--ies-text-sm);
  font-weight: 500;
  background: var(--ies-bg-base);
  border: 1px solid var(--ies-border-light);
  border-radius: var(--ies-radius-full);
  transition: all var(--ies-transition-fast);
  cursor: pointer;
}

.ies-chip:hover {
  background: var(--ies-accent-100);
  border-color: var(--ies-accent-200);
}

/* Entity type chips */
.ies-chip--concept {
  background: var(--ies-entity-concept-bg);
  border-color: var(--ies-entity-concept-border);
  color: var(--ies-entity-concept);
}

.ies-chip--person {
  background: var(--ies-entity-person-bg);
  border-color: var(--ies-entity-person-border);
  color: var(--ies-entity-person);
}

.ies-chip--theory {
  background: var(--ies-entity-theory-bg);
  border-color: var(--ies-entity-theory-border);
  color: var(--ies-entity-theory);
}

.ies-chip--framework {
  background: var(--ies-entity-framework-bg);
  border-color: var(--ies-entity-framework-border);
  color: var(--ies-entity-framework);
}

.ies-chip--assessment {
  background: var(--ies-entity-assessment-bg);
  border-color: var(--ies-entity-assessment-border);
  color: var(--ies-entity-assessment);
}
```

### Inputs

```css
.ies-input {
  width: 100%;
  padding: var(--ies-space-3) var(--ies-space-4);
  font-family: var(--ies-font-body);
  font-size: var(--ies-text-base);
  color: var(--ies-text-primary);
  background: var(--ies-bg-elevated);
  border: 1px solid var(--ies-border-light);
  border-radius: var(--ies-radius-sm);
  transition: all var(--ies-transition-fast);
}

.ies-input::placeholder {
  color: var(--ies-text-subtle);
}

.ies-input:focus {
  outline: none;
  border-color: var(--ies-accent);
  box-shadow: 0 0 0 3px var(--ies-accent-100);
}

.ies-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Textarea */
.ies-textarea {
  min-height: 100px;
  resize: vertical;
  line-height: 1.5;
}
```

---

## Entity Overlay Styles

For inline entity highlighting in reading content:

```css
.ies-entity {
  cursor: pointer;
  border-radius: 3px;
  padding: 1px 3px;
  margin: 0 -1px;
  transition: all var(--ies-transition-fast);
  position: relative;
}

.ies-entity::after {
  content: '';
  position: absolute;
  left: 2px;
  right: 2px;
  bottom: 0;
  height: 2px;
  border-radius: 1px;
  opacity: 0.6;
  transition: opacity var(--ies-transition-fast);
}

.ies-entity:hover::after {
  opacity: 1;
}

/* Type variants */
.ies-entity--concept {
  background: var(--ies-entity-concept-bg);
}
.ies-entity--concept::after {
  background: linear-gradient(90deg, var(--ies-entity-concept), #d4a853);
}
.ies-entity--concept:hover {
  background: rgba(201, 135, 46, 0.18);
}

.ies-entity--person {
  background: var(--ies-entity-person-bg);
}
.ies-entity--person::after {
  background: linear-gradient(90deg, var(--ies-entity-person), #7aaa9a);
}
.ies-entity--person:hover {
  background: rgba(90, 138, 122, 0.18);
}

.ies-entity--theory {
  background: var(--ies-entity-theory-bg);
}
.ies-entity--theory::after {
  background: linear-gradient(90deg, var(--ies-entity-theory), #ab9ac0);
}
.ies-entity--theory:hover {
  background: rgba(139, 122, 160, 0.18);
}

.ies-entity--framework {
  background: var(--ies-entity-framework-bg);
}
.ies-entity--framework::after {
  background: linear-gradient(90deg, var(--ies-entity-framework), #d88e6a);
}
.ies-entity--framework:hover {
  background: rgba(184, 110, 74, 0.18);
}

.ies-entity--assessment {
  background: var(--ies-entity-assessment-bg);
}
.ies-entity--assessment::after {
  background: linear-gradient(90deg, var(--ies-entity-assessment), #7a9aba);
}
.ies-entity--assessment:hover {
  background: rgba(90, 122, 154, 0.18);
}
```

---

## Utility Classes

### Animation Utilities

```css
.ies-fade-in {
  animation: ies-fade-in var(--ies-duration-normal) var(--ies-ease-out);
}

.ies-slide-up {
  animation: ies-slide-up var(--ies-duration-slow) var(--ies-ease-out);
}

.ies-scale-in {
  animation: ies-scale-in var(--ies-duration-normal) var(--ies-ease-out);
}

.ies-loading {
  animation: ies-pulse-soft 1.5s ease-in-out infinite;
}

.ies-shimmer {
  background: linear-gradient(
    90deg,
    var(--ies-bg-base) 0%,
    var(--ies-bg-elevated) 50%,
    var(--ies-bg-base) 100%
  );
  background-size: 200% 100%;
  animation: ies-shimmer 1.5s ease-in-out infinite;
}

/* Stagger children */
.ies-stagger > * {
  animation: ies-stagger-in var(--ies-duration-slow) var(--ies-ease-out) backwards;
}
.ies-stagger > *:nth-child(1) { animation-delay: 0ms; }
.ies-stagger > *:nth-child(2) { animation-delay: 50ms; }
.ies-stagger > *:nth-child(3) { animation-delay: 100ms; }
.ies-stagger > *:nth-child(4) { animation-delay: 150ms; }
.ies-stagger > *:nth-child(5) { animation-delay: 200ms; }
.ies-stagger > *:nth-child(6) { animation-delay: 250ms; }
.ies-stagger > *:nth-child(7) { animation-delay: 300ms; }
.ies-stagger > *:nth-child(8) { animation-delay: 350ms; }
```

### Scrollbar Styling

```css
.ies-scrollable {
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--ies-border-medium) transparent;
}

.ies-scrollable::-webkit-scrollbar {
  width: 6px;
}

.ies-scrollable::-webkit-scrollbar-track {
  background: transparent;
}

.ies-scrollable::-webkit-scrollbar-thumb {
  background: var(--ies-border-medium);
  border-radius: 3px;
}

.ies-scrollable::-webkit-scrollbar-thumb:hover {
  background: var(--ies-text-subtle);
}
```

### Focus Visible

```css
.ies-focus-ring:focus-visible {
  outline: 2px solid var(--ies-accent);
  outline-offset: 2px;
}
```

---

## Implementation Guide

### SiYuan Plugin (Svelte)

1. **Import the design system** in `index.scss`:
   ```scss
   @import './styles/design-system.scss';
   ```

2. **Replace local CSS variables** with `--ies-*` tokens

3. **Apply `.ies-root`** to the plugin container for base styles

4. **Use design system classes** instead of inline styles

### Readest (React/Tailwind)

1. **Create `ies-tokens.css`** with all CSS custom properties

2. **Import in `globals.css`**:
   ```css
   @import './ies-tokens.css';
   ```

3. **Replace hardcoded colors** in TypeScript with CSS variable references

4. **Create Tailwind plugin** for IES color tokens (optional)

---

## Accessibility Checklist

- [ ] All text meets WCAG AA contrast (4.5:1 minimum)
- [ ] Focus states visible for keyboard navigation
- [ ] Animations respect `prefers-reduced-motion`
- [ ] Form inputs have visible labels
- [ ] Interactive elements have hover/focus feedback
- [ ] Error states use more than just color

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-05 | Initial unified design system |
