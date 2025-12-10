# IES Design Language Guide v2

**Philosophy:** Modern Information Space — Dark mode first, bold entity colors, fast purposeful motion, ADHD-friendly interactions

**Date:** December 9, 2025
**Version:** 2.0
**Status:** Unified standard for IES Reader and SiYuan Plugin

---

## Table of Contents

1. [Color System](#1-color-system)
2. [Typography](#2-typography)
3. [Spacing System](#3-spacing-system)
4. [Animation System](#4-animation-system)
5. [Interactive States](#5-interactive-states)
6. [Glass Morphism / Elevation](#6-glass-morphism--elevation)
7. [Entity Type Visual Language](#7-entity-type-visual-language)
8. [Question Class Visual Language](#8-question-class-visual-language)
9. [Dark Theme Specification](#9-dark-theme-specification)
10. [Implementation Guide](#10-implementation-guide)

---

## 1. Color System

### 1.1 Foundational Backgrounds

The IES dark theme uses near-black backgrounds with warm undertones for reduced eye strain during extended reading and exploration sessions.

```css
--bg-primary: #0f0f10;           /* Near black, warm undertone — main canvas */
--bg-secondary: #1a1a1c;         /* Elevated surfaces — cards, panels */
--bg-tertiary: #252528;          /* Nested elements — inputs, dropdowns */
--bg-hover: #2a2a2e;             /* Hover states */
--bg-active: #323236;            /* Active/pressed states */
```

**Usage:**
- `bg-primary` — Main application background, reading canvas
- `bg-secondary` — Flow panel, sidebar, modal backgrounds
- `bg-tertiary` — Card backgrounds, input fields
- `bg-hover` — Button/link hover states
- `bg-active` — Pressed buttons, active tabs

**Rationale:** Near-black (#0f0f10) instead of pure black (#000000) reduces eye strain and provides subtle depth. Warm undertone prevents the cold, harsh feel of pure black.

---

### 1.2 Text Hierarchy

Clear contrast ratios ensure readability on dark backgrounds while maintaining visual hierarchy.

```css
--text-primary: #f5f5f7;         /* Main text — WCAG AAA (>7:1 contrast) */
--text-secondary: #a1a1a6;       /* Secondary text — supporting content */
--text-muted: #6e6e73;           /* Muted text — hints, metadata */
--text-subtle: #48484a;          /* Subtle text — disabled, placeholders */
--text-inverse: #0f0f10;         /* Text on light backgrounds (rare) */
```

**Contrast Ratios:**
- Primary text on bg-primary: **13.2:1** (AAA)
- Secondary text on bg-primary: **6.1:1** (AA)
- Muted text on bg-primary: **3.8:1** (AA for large text)

**Usage:**
- `text-primary` — Body text, headings, primary UI labels
- `text-secondary` — Captions, secondary labels, timestamps
- `text-muted` — Placeholders, hints, metadata
- `text-subtle` — Disabled text, very low-priority content
- `text-inverse` — Text on entity color badges (rare)

---

### 1.3 Entity Type Colors

Bold, saturated colors ensure entity types are immediately distinguishable during reading and exploration. Not muted — visibility is critical for ADHD users.

```css
/* 5 Core Entity Types (Domain Knowledge) */
--entity-concept: #3b82f6;       /* Blue — ideas, principles */
--entity-person: #10b981;        /* Green — people, authors */
--entity-theory: #8b5cf6;        /* Purple — theories, models */
--entity-framework: #f59e0b;     /* Amber — frameworks, methods */
--entity-assessment: #ef4444;    /* Red — assessments, tools */

/* 3 Personal Entity Types (ADHD Ontology) */
--entity-spark: #ec4899;         /* Pink — raw insights, resonance */
--entity-insight: #06b6d4;       /* Cyan — processed understanding */
--entity-thread: #84cc16;        /* Lime — exploration paths */

/* Entity Backgrounds (15% opacity for badges, cards) */
--entity-concept-bg: rgba(59, 130, 246, 0.15);
--entity-person-bg: rgba(16, 185, 129, 0.15);
--entity-theory-bg: rgba(139, 92, 246, 0.15);
--entity-framework-bg: rgba(245, 158, 11, 0.15);
--entity-assessment-bg: rgba(239, 68, 68, 0.15);
--entity-spark-bg: rgba(236, 72, 153, 0.15);
--entity-insight-bg: rgba(6, 182, 212, 0.15);
--entity-thread-bg: rgba(132, 204, 22, 0.15);
```

**Color Rationale:**
- **Blue (Concept):** Traditional "information" color, abstract ideas
- **Green (Person):** Human association, growth, living entities
- **Purple (Theory):** Academic, scholarly, systematic thinking
- **Amber (Framework):** Structure, guidance, practical methods
- **Red (Assessment):** Tools, measurements, diagnostic
- **Pink (Spark):** Energy, excitement, raw resonance
- **Cyan (Insight):** Clarity, understanding, processed thought
- **Lime (Thread):** Connection, growth, ongoing exploration

**Accessibility:** All entity colors meet WCAG AA contrast (4.5:1) against dark backgrounds. Text overlays use 15% opacity backgrounds for legibility.

---

### 1.4 Question Class Colors

Nine cognitive function badges with distinct colors for Mode Transition Engine tracking and session analysis.

```css
/* 9 Question Classes (IES Question Engine) */
--q-schema: #3b82f6;             /* Blue — structure questions */
--q-schema-bg: rgba(59, 130, 246, 0.15);

--q-boundary: #8b5cf6;           /* Purple — edge/limit questions */
--q-boundary-bg: rgba(139, 92, 246, 0.15);

--q-dimensional: #14b8a6;        /* Teal — spectrum questions */
--q-dimensional-bg: rgba(20, 184, 166, 0.15);

--q-causal: #f59e0b;             /* Amber — mechanism questions */
--q-causal-bg: rgba(245, 158, 11, 0.15);

--q-counterfactual: #ec4899;     /* Pink — what-if questions */
--q-counterfactual-bg: rgba(236, 72, 153, 0.15);

--q-anchor: #10b981;             /* Green — concrete example questions */
--q-anchor-bg: rgba(16, 185, 129, 0.15);

--q-perspective: #f97316;        /* Orange — viewpoint change questions */
--q-perspective-bg: rgba(249, 115, 22, 0.15);

--q-meta: #6b7280;               /* Gray — thinking pattern questions */
--q-meta-bg: rgba(107, 114, 128, 0.15);

--q-synthesis: #6366f1;          /* Indigo — integration questions */
--q-synthesis-bg: rgba(99, 102, 241, 0.15);
```

**Usage:**
- Question badges in ForgeMode conversation
- Session document question class tags
- Mode Transition Engine visualization
- Cognitive coverage bars in session UI

**Rationale:** Question classes use overlapping but distinct colors from entity types. Similar hues indicate related cognitive functions (e.g., schema-probe blue aligns with concept blue for structural thinking).

---

### 1.5 Semantic Colors

Standard semantic colors for success, warning, error, and info states.

```css
--success: #10b981;              /* Green — confirmation, completion */
--success-bg: rgba(16, 185, 129, 0.15);

--warning: #f59e0b;              /* Amber — caution, attention needed */
--warning-bg: rgba(245, 158, 11, 0.15);

--error: #ef4444;                /* Red — errors, failures */
--error-bg: rgba(239, 68, 68, 0.15);

--info: #3b82f6;                 /* Blue — informational messages */
--info-bg: rgba(59, 130, 246, 0.15);
```

---

### 1.6 Energy Levels (ADHD Mood-Based Navigation)

Color-coded energy states for ADHD-friendly content filtering based on current cognitive capacity.

```css
--energy-low: #6b7280;           /* Cool gray — low energy, passive tasks */
--energy-low-bg: rgba(107, 114, 128, 0.15);

--energy-medium: #f59e0b;        /* Amber — moderate energy, active tasks */
--energy-medium-bg: rgba(245, 158, 11, 0.15);

--energy-high: #ef4444;          /* Red — high energy, demanding tasks */
--energy-high-bg: rgba(239, 68, 68, 0.15);
```

**Usage:**
- Personal graph API filters content by energy level
- Session UI indicates recommended energy state
- Dashboard suggestions grouped by energy requirement

---

### 1.7 Borders

Subtle borders using white with varying opacity for depth and separation.

```css
--border-subtle: rgba(255, 255, 255, 0.05);   /* Barely visible separation */
--border-default: rgba(255, 255, 255, 0.1);   /* Standard borders */
--border-focus: rgba(255, 255, 255, 0.2);     /* Focused elements */
--border-strong: rgba(255, 255, 255, 0.3);    /* Emphasized separation */
```

**Usage:**
- `border-subtle` — Nested card borders, dividers
- `border-default` — Input fields, buttons, cards
- `border-focus` — Focused inputs, active selections
- `border-strong` — Modal borders, emphasized containers

---

### 1.8 Gradients

Subtle gradients for active states, hover effects, and emphasis (used sparingly).

```css
--gradient-concept: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
--gradient-person: linear-gradient(135deg, #10b981 0%, #059669 100%);
--gradient-theory: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
--gradient-framework: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
--gradient-assessment: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
```

**Usage:** Active entity badges, hero sections, call-to-action buttons (minimal use to avoid visual noise).

---

## 2. Typography

### 2.1 Font Families

Three-tier font system balancing readability, personality, and technical precision.

```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-serif: 'Source Serif Pro', serif;
--font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
--font-system: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

**Usage:**
- `font-sans` (Inter) — UI text, labels, buttons, body text
- `font-serif` (Source Serif Pro) — **NOT CURRENTLY USED** (reserved for long-form reading if needed)
- `font-mono` (JetBrains Mono) — Code blocks, technical identifiers, file paths
- `font-system` — Fallback for performance-critical contexts

**Rationale:**
- **Inter:** Modern, highly legible at small sizes, excellent tracking/kerning for UI
- **JetBrains Mono:** Designed for code, excellent ligatures, high character distinction

---

### 2.2 Type Scale

Major Third (1.25 ratio) scale with 16px base for balanced hierarchy.

```css
--text-xs: 0.75rem;      /* 12px — Small labels, badges, timestamps */
--text-sm: 0.875rem;     /* 14px — Secondary text, captions, metadata */
--text-base: 1rem;       /* 16px — Body text (default) */
--text-lg: 1.125rem;     /* 18px — Large body, emphasized text */
--text-xl: 1.25rem;      /* 20px — Section headings */
--text-2xl: 1.5rem;      /* 24px — Card headings, panel titles */
--text-3xl: 1.875rem;    /* 30px — Page headings */
--text-4xl: 2.25rem;     /* 36px — Large headings, hero titles */
--text-5xl: 3rem;        /* 48px — Hero headings (rarely used) */
```

**Usage Examples:**
- `text-xs` — Entity badges, small timestamps, icon labels
- `text-sm` — Secondary UI text, metadata, captions
- `text-base` — Body text in reader, standard UI labels
- `text-lg` — Emphasized paragraphs, important labels
- `text-xl` — Section headings in Flow panel
- `text-2xl` — Entity names, panel titles
- `text-3xl` — Mode titles, page headings

---

### 2.3 Font Weights

Four weights providing clear hierarchy without excessive variation.

```css
--font-normal: 400;      /* Body text, standard UI labels */
--font-medium: 500;      /* Emphasized text, active states */
--font-semibold: 600;    /* Headings, important labels */
--font-bold: 700;        /* Hero text, strong emphasis (rarely used) */
```

**Usage:**
- `normal (400)` — Default for all body text and UI labels
- `medium (500)` — Active tabs, selected items, button text
- `semibold (600)` — Headings (h1-h3), entity names, panel titles
- `bold (700)` — Hero headings only (avoid in UI for accessibility)

---

### 2.4 Line Heights

Optimized for readability across UI labels and reading content.

```css
--leading-none: 1;           /* Icons, single-line labels */
--leading-tight: 1.25;       /* Headings, compact UI */
--leading-snug: 1.375;       /* Subheadings, button text */
--leading-normal: 1.5;       /* Standard UI text */
--leading-relaxed: 1.625;    /* Comfortable reading */
--leading-loose: 2;          /* Spacious reading (rare) */

/* Semantic line heights */
--leading-heading: 1.25;     /* All headings */
--leading-body: 1.6;         /* Body text in reader */
--leading-code: 1.5;         /* Code blocks, monospace text */
```

**Usage:**
- Headings: `leading-heading (1.25)`
- UI labels: `leading-normal (1.5)`
- Reading text: `leading-body (1.6)`
- Code: `leading-code (1.5)`

---

### 2.5 Letter Spacing

Subtle tracking adjustments for specific use cases.

```css
--tracking-tighter: -0.05em;     /* Large headings (36px+) */
--tracking-tight: -0.025em;      /* Headings (20-36px) */
--tracking-normal: 0;            /* Body text, UI labels (default) */
--tracking-wide: 0.025em;        /* Small caps, badge text */
--tracking-wider: 0.05em;        /* All-caps labels */
--tracking-widest: 0.1em;        /* Wide all-caps (rarely used) */
```

**Usage:**
- Default: `tracking-normal (0)` for all text
- Large headings (36px+): `tracking-tighter (-0.05em)` for visual balance
- All-caps labels: `tracking-wider (0.05em)` for legibility

---

## 3. Spacing System

### 3.1 Spacing Scale

4px base unit with linear scale for consistent rhythm and alignment.

```css
--space-0: 0;
--space-px: 1px;
--space-0-5: 0.125rem;   /* 2px */
--space-1: 0.25rem;      /* 4px */
--space-1-5: 0.375rem;   /* 6px */
--space-2: 0.5rem;       /* 8px */
--space-2-5: 0.625rem;   /* 10px */
--space-3: 0.75rem;      /* 12px */
--space-3-5: 0.875rem;   /* 14px */
--space-4: 1rem;         /* 16px */
--space-5: 1.25rem;      /* 20px */
--space-6: 1.5rem;       /* 24px */
--space-7: 1.75rem;      /* 28px */
--space-8: 2rem;         /* 32px */
--space-9: 2.25rem;      /* 36px */
--space-10: 2.5rem;      /* 40px */
--space-11: 2.75rem;     /* 44px */
--space-12: 3rem;        /* 48px */
--space-14: 3.5rem;      /* 56px */
--space-16: 4rem;        /* 64px */
--space-20: 5rem;        /* 80px */
--space-24: 6rem;        /* 96px */
--space-32: 8rem;        /* 128px */
```

**Rationale:** 4px base unit aligns with modern design systems (Tailwind, Material, Ant Design) and ensures pixel-perfect alignment on standard displays.

---

### 3.2 Semantic Spacing

Named tokens for common layout patterns.

```css
/* Inline spacing (horizontal gaps) */
--inline-xs: var(--space-1);    /* 4px — Tight inline gaps */
--inline-sm: var(--space-2);    /* 8px — Small gaps */
--inline-md: var(--space-3);    /* 12px — Default gaps */
--inline-lg: var(--space-4);    /* 16px — Larger gaps */
--inline-xl: var(--space-6);    /* 24px — Section gaps */

/* Stack spacing (vertical gaps) */
--stack-xs: var(--space-1);     /* 4px */
--stack-sm: var(--space-2);     /* 8px */
--stack-md: var(--space-4);     /* 16px */
--stack-lg: var(--space-6);     /* 24px */
--stack-xl: var(--space-8);     /* 32px */
--stack-2xl: var(--space-12);   /* 48px */

/* Padding (internal spacing) */
--pad-xs: var(--space-1);       /* 4px — Tight padding */
--pad-sm: var(--space-2);       /* 8px — Small padding */
--pad-md: var(--space-4);       /* 16px — Default padding */
--pad-lg: var(--space-6);       /* 24px — Generous padding */
--pad-xl: var(--space-8);       /* 32px — Large padding */
```

**Usage Examples:**
- Button padding: `padding: var(--pad-sm) var(--pad-md)` (8px vertical, 16px horizontal)
- Card padding: `padding: var(--pad-lg)` (24px all sides)
- Stack of items: `gap: var(--stack-md)` (16px between items)

---

### 3.3 Component-Specific Spacing

Predefined spacing for common UI components.

```css
--button-padding-x: var(--space-4);    /* 16px horizontal */
--button-padding-y: var(--space-2);    /* 8px vertical */
--input-padding-x: var(--space-3);     /* 12px */
--input-padding-y: var(--space-2);     /* 8px */
--card-padding: var(--space-4);        /* 16px */
--chip-padding-x: var(--space-3);      /* 12px */
--chip-padding-y: var(--space-1);      /* 4px */
```

---

### 3.4 Layout Spacing

Page-level spacing for consistent structure.

```css
--page-margin: var(--space-6);         /* 24px page margins */
--section-gap: var(--space-8);         /* 32px between sections */
--card-gap: var(--space-4);            /* 16px between cards */
```

---

### 3.5 Border Radius

Modern, subtle rounding for approachable UI without excessive roundness.

```css
--radius-none: 0;
--radius-sm: 4px;          /* Subtle rounding */
--radius-md: 8px;          /* Default cards, buttons */
--radius-lg: 12px;         /* Large cards, modals */
--radius-xl: 16px;         /* Extra large elements */
--radius-2xl: 24px;        /* Very rounded (rarely used) */
--radius-full: 9999px;     /* Pills, avatars, badges */

/* Semantic radius */
--radius-button: var(--radius-md);
--radius-input: var(--radius-md);
--radius-card: var(--radius-lg);
--radius-modal: var(--radius-xl);
--radius-chip: var(--radius-full);
--radius-badge: var(--radius-full);
```

**Usage:**
- Buttons: `border-radius: var(--radius-button)` (8px)
- Cards: `border-radius: var(--radius-card)` (12px)
- Entity badges: `border-radius: var(--radius-badge)` (full pill)

---

## 4. Animation System

### 4.1 Duration Tokens

Fast by default for responsiveness, longer for deliberate transitions.

```css
--duration-instant: 75ms;      /* Instant feedback (hover color change) */
--duration-fast: 150ms;        /* Quick interactions (buttons, toggles) */
--duration-base: 200ms;        /* Default animations (cards, panels) */
--duration-slow: 300ms;        /* Deliberate animations (modals, drawers) */
--duration-slower: 500ms;      /* Very slow (page transitions, rare) */
```

**Rationale:** Fast default (150ms) keeps UI snappy. ADHD users benefit from quick feedback without sluggish delays.

---

### 4.2 Easing Functions

Modern, snappy curves inspired by iOS/Linear/Arc.

```css
--ease-out: cubic-bezier(0, 0, 0.2, 1);       /* Quick start, smooth stop */
--ease-in: cubic-bezier(0.4, 0, 1, 1);        /* Smooth start, quick stop */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);  /* Smooth both ends */
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);  /* Subtle bounce (confirmations) */
--ease-linear: linear;                        /* Continuous animations (spinners) */
```

**Usage:**
- Default: `ease-out` for most transitions (feels responsive)
- Entrances: `ease-out` (quick appearance)
- Exits: `ease-in` (quick departure)
- Confirmations: `ease-spring` (subtle bounce on save/success)

---

### 4.3 Transition Presets

Common property combinations for convenience.

```css
--transition-fast: var(--duration-fast) var(--ease-out);
--transition-base: var(--duration-base) var(--ease-out);
--transition-slow: var(--duration-slow) var(--ease-out);
--transition-spring: var(--duration-base) var(--ease-spring);

/* Property-specific transitions */
--transition-colors: color var(--duration-fast) var(--ease-out),
                     background-color var(--duration-fast) var(--ease-out),
                     border-color var(--duration-fast) var(--ease-out);

--transition-transform: transform var(--duration-fast) var(--ease-out);
--transition-opacity: opacity var(--duration-fast) var(--ease-out);
--transition-shadow: box-shadow var(--duration-fast) var(--ease-out);
--transition-all: all var(--duration-fast) var(--ease-out);
```

**Usage:**
```css
.button {
  transition: var(--transition-colors);
}

.card {
  transition: var(--transition-transform), var(--transition-shadow);
}
```

---

### 4.4 Keyframe Animations

Predefined animations for common patterns.

```css
/* Fade in — Subtle entrance */
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide up — Content entrance from below */
@keyframes slide-up {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Scale in — Modal/popover entrance */
@keyframes scale-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

/* Pulse soft — ADHD-friendly attention (no aggressive flashing) */
@keyframes pulse-soft {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* Spin — Loading indicator */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Shake — Error/warning feedback */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-3px); }
  20%, 40%, 60%, 80% { transform: translateX(3px); }
}

/* Shimmer — Loading placeholder */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
```

**Usage:**
```css
.modal {
  animation: scale-in var(--duration-base) var(--ease-out) forwards;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}
```

---

### 4.5 ADHD-Friendly Animation Principles

**Guidelines:**
1. **Fast by default** — 150ms prevents sluggishness
2. **No aggressive flashing** — Use `pulse-soft`, not rapid blinks
3. **Subtle motion** — 8px slides, 0.95 scale (not 20px or 0.5)
4. **Purposeful only** — Animate state changes, not decoration
5. **Respect `prefers-reduced-motion`** — Essential for accessibility

```css
/* Reduced motion — Accessibility requirement */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 5. Interactive States

### 5.1 Button States

Five states providing clear feedback for all interactions.

```css
.button {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  transition: var(--transition-colors), var(--transition-shadow);
}

.button:hover {
  background: var(--bg-hover);
  border-color: var(--border-focus);
}

.button:focus {
  outline: 2px solid var(--border-focus);
  outline-offset: 2px;
}

.button:active {
  background: var(--bg-active);
  transform: translateY(1px);
}

.button:disabled {
  background: var(--bg-tertiary);
  color: var(--text-subtle);
  border-color: var(--border-subtle);
  cursor: not-allowed;
  opacity: 0.5;
}
```

---

### 5.2 Focus Ring Specification

Accessible focus indicators meeting WCAG 2.2 requirements.

```css
/* Focus ring standard */
:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 2px;
  border-radius: var(--radius-md);
}

/* Entity focus (type-specific) */
.entity-concept:focus-visible {
  outline-color: var(--entity-concept);
}
```

**Requirements:**
- 2px solid outline (visible on all backgrounds)
- 2px offset (separates from element border)
- Matches element border-radius for visual harmony

---

### 5.3 Touch Target Sizes

Minimum 44px for all interactive elements (WCAG 2.1 AA requirement).

```css
.button,
.link,
.input,
.chip {
  min-height: 44px;
  min-width: 44px;
  padding: var(--pad-sm) var(--pad-md);
}

/* Small badges can be 32px if not primary actions */
.entity-badge {
  min-height: 32px;
  padding: var(--pad-xs) var(--pad-sm);
}
```

---

### 5.4 Link States

Clear, accessible link styling for inline text links.

```css
.link {
  color: var(--entity-concept);
  text-decoration: none;
  transition: var(--transition-colors);
}

.link:hover {
  color: var(--text-primary);
  text-decoration: underline;
}

.link:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 2px;
}

.link:visited {
  color: var(--entity-theory);  /* Purple for visited links */
}
```

---

## 6. Glass Morphism / Elevation

### 6.1 Glass Effect

Floating panels with background blur for depth without heavy shadows.

```css
--glass-bg: rgba(26, 26, 28, 0.8);       /* 80% opaque bg-secondary */
--glass-blur: blur(12px);                /* Background blur */
--glass-border: 1px solid rgba(255, 255, 255, 0.1);
```

**Usage:**
```css
.flow-panel {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  border: var(--glass-border);
  border-radius: var(--radius-card);
}
```

**Rationale:** Glass effect provides visual depth without heavy shadows, which can feel oppressive on dark backgrounds. The blur creates separation from content beneath.

---

### 6.2 Shadow System

Subtle shadows for elevation hierarchy.

```css
--shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.1);
--shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.1);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
```

**Elevation Levels:**
1. **Base (no shadow)** — Inline elements, text
2. **xs** — Buttons, chips, small cards
3. **sm** — Input fields on focus, dropdowns
4. **md** — Floating cards, tooltips
5. **lg** — Modals, popovers, flow panel
6. **xl** — Full-screen overlays (rare)

**Usage:**
```css
.card {
  box-shadow: var(--shadow-md);
  transition: var(--transition-shadow);
}

.card:hover {
  box-shadow: var(--shadow-lg);
}
```

---

### 6.3 Z-Index Scale

Explicit layering to prevent z-index conflicts.

```css
--z-base: 0;          /* Default layer */
--z-dropdown: 50;     /* Dropdowns, tooltips */
--z-sticky: 100;      /* Sticky headers, tabs */
--z-overlay: 150;     /* Overlays, backdrops */
--z-modal: 200;       /* Modals, dialogs */
--z-popover: 250;     /* Popovers, toasts */
--z-tooltip: 300;     /* Tooltips (highest) */
```

---

## 7. Entity Type Visual Language

### 7.1 Entity Type Color + Shape System

Each entity type has a **color** (for inline highlights) and **optional icon** (for badges) to ensure distinguishability without color alone.

| Type | Color | Hex | Icon | Shape/Badge |
|------|-------|-----|------|-------------|
| Concept | Blue | #3b82f6 | 💡 | Rounded rectangle |
| Person | Green | #10b981 | 👤 | Circle |
| Theory | Purple | #8b5cf6 | 🔬 | Hexagon |
| Framework | Amber | #f59e0b | 📐 | Square |
| Assessment | Red | #ef4444 | 📊 | Diamond |
| Spark | Pink | #ec4899 | ✨ | Star burst |
| Insight | Cyan | #06b6d4 | 🔍 | Pentagon |
| Thread | Lime | #84cc16 | 🧵 | Wavy line |

**Implementation:**
```css
/* Inline entity highlights */
.entity-concept { color: var(--entity-concept); }
.entity-person { color: var(--entity-person); }
.entity-theory { color: var(--entity-theory); }

/* Entity badges */
.entity-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--chip-padding-y) var(--chip-padding-x);
  border-radius: var(--radius-badge);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}

.entity-badge.concept {
  background: var(--entity-concept-bg);
  color: var(--entity-concept);
  border: 1px solid var(--entity-concept);
}

.entity-badge.person {
  background: var(--entity-person-bg);
  color: var(--entity-person);
  border: 1px solid var(--entity-person);
}
```

---

### 7.2 Entity Hover States

Consistent hover behavior for inline entities and entity cards.

```css
/* Inline entity hover */
.entity-highlight {
  cursor: pointer;
  transition: var(--transition-colors);
  text-decoration: underline;
  text-decoration-color: transparent;
}

.entity-highlight:hover {
  text-decoration-color: currentColor;
  filter: brightness(1.2);
}

/* Entity card hover */
.entity-card {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  transition: var(--transition-colors), var(--transition-transform), var(--transition-shadow);
}

.entity-card:hover {
  background: var(--bg-hover);
  border-color: var(--border-focus);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}
```

---

### 7.3 Accessibility Without Color

For colorblind users or high-contrast modes, entity types are distinguishable by:

1. **Icons** — Emoji or SVG icons prefix entity names
2. **Shape** — Badge shapes differ (circle, square, hexagon)
3. **Text labels** — Type name displayed in badges ("Concept", "Person")
4. **Patterns** — Optional background patterns for high contrast mode

**Example:**
```html
<span class="entity-badge concept">
  <span class="entity-icon">💡</span>
  <span class="entity-name">Executive Function</span>
  <span class="entity-type-label">Concept</span>
</span>
```

---

## 8. Question Class Visual Language

### 8.1 Question Class Badges

Nine question classes displayed as emoji badges with type-specific colors.

```css
.question-class-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--chip-padding-y) var(--chip-padding-x);
  border-radius: var(--radius-badge);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}

.qc-schema {
  background: var(--q-schema-bg);
  color: var(--q-schema);
  border: 1px solid var(--q-schema);
}

.qc-boundary {
  background: var(--q-boundary-bg);
  color: var(--q-boundary);
  border: 1px solid var(--q-boundary);
}
```

**Badge Format:**
```
[Emoji] [Label]
```

Examples:
- 🏗️ Structure
- 🔲 Boundary
- 📐 Dimensional
- ⚡ Causal
- 🔮 What-If
- ⚓ Anchor
- 👁️ Perspective
- 🧠 Meta
- 🔗 Synthesis

---

### 8.2 Cognitive Coverage Visualization

Session UI displays cognitive coverage bars showing which question classes were used.

```css
.cognitive-coverage {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--pad-md);
  background: var(--bg-tertiary);
  border-radius: var(--radius-card);
}

.coverage-bar {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.coverage-label {
  min-width: 120px;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.coverage-track {
  flex: 1;
  height: 8px;
  background: var(--bg-primary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.coverage-fill {
  height: 100%;
  background: var(--q-schema);
  transition: width var(--duration-base) var(--ease-out);
}

.coverage-percent {
  min-width: 40px;
  text-align: right;
  font-size: var(--text-sm);
  color: var(--text-muted);
}
```

---

## 9. Dark Theme Specification

### 9.1 The Unified Dark Theme

**Critical Decision:** IES uses dark mode ONLY. No light mode option.

**Rationale:**
- Extended reading sessions require reduced eye strain
- Graph exploration involves prolonged screen time
- ADHD users benefit from consistent, predictable environment
- Dark backgrounds reduce visual noise and distraction

**Implementation:** All color tokens default to dark values. No theme toggle, no light mode CSS.

---

### 9.2 Background Layer Hierarchy

Five background levels creating depth without heavy shadows.

```css
/* Layer 1: Canvas */
--bg-primary: #0f0f10;           /* Main app background */

/* Layer 2: Surfaces */
--bg-secondary: #1a1a1c;         /* Panels, cards, sidebars */

/* Layer 3: Elements */
--bg-tertiary: #252528;          /* Inputs, nested cards */

/* Layer 4: Interactive */
--bg-hover: #2a2a2e;             /* Hover states */

/* Layer 5: Active */
--bg-active: #323236;            /* Active/pressed states */
```

**Usage:**
- Main reading canvas: `bg-primary`
- Flow panel background: `bg-secondary` or glass effect
- Cards within panel: `bg-tertiary`
- Button hover: `bg-hover`
- Button active: `bg-active`

---

### 9.3 Text on Dark Backgrounds

Five text levels ensuring readability at all hierarchy levels.

```css
--text-primary: #f5f5f7;         /* Main text — WCAG AAA (13.2:1) */
--text-secondary: #a1a1a6;       /* Supporting text — WCAG AA (6.1:1) */
--text-muted: #6e6e73;           /* Metadata — WCAG AA (3.8:1 large) */
--text-subtle: #48484a;          /* Disabled text */
--text-inverse: #0f0f10;         /* Text on light (rare) */
```

---

### 9.4 Resolving Reader/Panel Theme Conflict

**Problem (Pre-v2):** IES Reader had dark reading canvas but light Flow panel, creating jarring contrast.

**Solution:** Unified dark theme across all surfaces.

- Reading canvas: `bg-primary (#0f0f10)`
- Flow panel: `bg-secondary (#1a1a1c)` or glass effect
- Entity cards: `bg-tertiary (#252528)`
- All text: Light on dark

**No exceptions.** If a surface needs emphasis, use glass effect or shadow, not light background.

---

## 10. Implementation Guide

### 10.1 CSS Custom Properties

All design tokens implemented as CSS custom properties in `:root`.

**File Structure:**
```
ies/reader/src/styles/
├── design-system.css          # All tokens in one file

.worktrees/siyuan/ies/plugin/src/styles/design-system/
├── colors.css                 # Color tokens
├── typography.css             # Type scale, fonts
├── spacing.css                # Spacing, radius
└── animations.css             # Durations, easing, keyframes
```

**Usage:**
```css
/* Import design system */
@import './design-system.css';

/* Use tokens */
.my-component {
  background: var(--bg-secondary);
  color: var(--text-primary);
  padding: var(--pad-md);
  border-radius: var(--radius-card);
  transition: var(--transition-colors);
}
```

---

### 10.2 Component Styling Pattern

Consistent pattern for all UI components:

```css
.component {
  /* Layout */
  display: flex;
  flex-direction: column;
  gap: var(--stack-md);

  /* Spacing */
  padding: var(--pad-md);

  /* Appearance */
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-card);

  /* Elevation */
  box-shadow: var(--shadow-md);

  /* Transitions */
  transition: var(--transition-colors), var(--transition-shadow);
}

.component:hover {
  background: var(--bg-hover);
  border-color: var(--border-focus);
  box-shadow: var(--shadow-lg);
}
```

---

### 10.3 Utility Classes

Commonly used utilities for rapid development.

```css
/* Spacing */
.p-4 { padding: var(--space-4); }
.m-2 { margin: var(--space-2); }
.gap-4 { gap: var(--space-4); }

/* Text */
.text-primary { color: var(--text-primary); }
.text-secondary { color: var(--text-secondary); }
.text-lg { font-size: var(--text-lg); }
.font-semibold { font-weight: var(--font-semibold); }

/* Backgrounds */
.bg-primary { background: var(--bg-primary); }
.bg-secondary { background: var(--bg-secondary); }

/* Borders */
.border { border: 1px solid var(--border-default); }
.rounded-lg { border-radius: var(--radius-lg); }

/* Transitions */
.transition-colors { transition: var(--transition-colors); }
.transition-all { transition: var(--transition-all); }
```

---

### 10.4 Accessibility Checklist

Ensure all components meet these requirements:

- [ ] Focus indicators visible (2px outline, 2px offset)
- [ ] Touch targets minimum 44px (primary actions)
- [ ] Text contrast meets WCAG AA (4.5:1 normal, 3:1 large)
- [ ] Color not sole indicator (icons, labels, shapes)
- [ ] Motion respects `prefers-reduced-motion`
- [ ] Interactive states clear (hover, focus, active, disabled)
- [ ] Keyboard navigation functional (tab order, escape)

---

### 10.5 Design Token Reference Table

Quick reference for common combinations:

| Use Case | Background | Text | Border | Radius | Shadow |
|----------|------------|------|--------|--------|--------|
| Main canvas | bg-primary | text-primary | none | none | none |
| Panel | bg-secondary | text-primary | border-default | radius-card | shadow-lg |
| Card | bg-tertiary | text-primary | border-default | radius-lg | shadow-md |
| Button | bg-tertiary | text-primary | border-default | radius-button | shadow-xs |
| Input | bg-tertiary | text-primary | border-default | radius-input | none |
| Entity badge | entity-X-bg | entity-X | entity-X | radius-badge | none |
| Modal | bg-secondary | text-primary | border-default | radius-modal | shadow-xl |

---

## Appendix A: Token Migration Guide

### From Old System to v2

If migrating from an earlier design system, use this mapping:

| Old Token | New Token |
|-----------|-----------|
| `--bg-dark` | `--bg-primary` |
| `--bg-light` | `--bg-secondary` |
| `--text-main` | `--text-primary` |
| `--text-dim` | `--text-secondary` |
| `--spacing-sm` | `--space-2` (8px) |
| `--spacing-md` | `--space-4` (16px) |
| `--spacing-lg` | `--space-6` (24px) |
| `--font-body` | `--font-sans` |
| `--duration-normal` | `--duration-fast` (150ms) |

---

## Appendix B: Design Principles Summary

1. **Dark mode only** — No light theme, consistent environment
2. **Bold entity colors** — Not muted, visibility critical for ADHD
3. **Fast by default** — 150ms transitions, instant feedback
4. **Subtle motion** — 8px slides, no aggressive animations
5. **Clear hierarchy** — 5 background levels, 5 text levels
6. **4px base unit** — Consistent spacing rhythm
7. **Inter for UI** — Modern, legible sans-serif
8. **Accessibility first** — WCAG AA minimum, AAA where possible
9. **Glass over shadows** — Depth without oppressive shadows
10. **Purposeful only** — Every color, animation, space has reason

---

## Version History

- **v2.0** (Dec 9, 2025) — Unified design language for IES Reader + SiYuan Plugin
- **v1.0** (Dec 4, 2025) — Initial Reader design system (archived)

---

**End of Design Language Guide v2**
