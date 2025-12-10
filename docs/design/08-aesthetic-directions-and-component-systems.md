# Aesthetic Directions & Component System Options

**Document Version:** 1.0
**Date:** December 9, 2025
**Status:** Design Options for Review
**Context:** Extensions and alternatives to IES Design Language Guide v2

---

## Part 1: Aesthetic Direction Options

Six distinct aesthetic directions, each with complete design specifications. All options build upon the established IES foundation (dark-first, ADHD-friendly, entity-color-coded) while offering different visual personalities.

---

### Option A: "Obsidian Depths"

**Philosophy:** Deep, immersive knowledge cave. Minimal chrome, maximum content density. The interface disappears; knowledge emerges.

#### A.1 Color System

```css
/* Backgrounds — Ultra-deep, near-black with blue undertone */
--bg-void: #05070a;              /* Deepest layer */
--bg-primary: #0a0d12;           /* Main canvas */
--bg-secondary: #111621;         /* Elevated surfaces */
--bg-tertiary: #1a2030;          /* Nested elements */
--bg-hover: #222d40;             /* Hover states */
--bg-active: #2a3850;            /* Active states */

/* Text — High contrast, cool white */
--text-primary: #e8edf5;         /* Main text (AAA 14.2:1) */
--text-secondary: #8892a6;       /* Supporting text */
--text-muted: #5a6478;           /* Metadata */
--text-accent: #6db3f2;          /* Links, interactive text */

/* Entity Colors — Jewel tones, high saturation */
--entity-concept: #4a9eff;       /* Sapphire */
--entity-person: #2dd4a7;        /* Emerald */
--entity-theory: #a78bfa;        /* Amethyst */
--entity-framework: #fbbf24;     /* Topaz */
--entity-assessment: #f87171;    /* Ruby */
--entity-spark: #f472b6;         /* Pink tourmaline */
--entity-insight: #22d3ee;       /* Aquamarine */
--entity-thread: #a3e635;        /* Peridot */

/* Borders — Barely visible separation */
--border-subtle: rgba(100, 140, 200, 0.06);
--border-default: rgba(100, 140, 200, 0.12);
--border-focus: rgba(100, 140, 200, 0.25);
```

#### A.2 Typography

```css
/* Font Stack — Technical, precise */
--font-sans: 'IBM Plex Sans', 'SF Pro Text', system-ui, sans-serif;
--font-mono: 'IBM Plex Mono', 'SF Mono', monospace;
--font-display: 'IBM Plex Sans', sans-serif;

/* Scale — Tight, information-dense */
--text-xs: 0.6875rem;     /* 11px */
--text-sm: 0.8125rem;     /* 13px */
--text-base: 0.9375rem;   /* 15px */
--text-lg: 1.0625rem;     /* 17px */
--text-xl: 1.25rem;       /* 20px */
--text-2xl: 1.5rem;       /* 24px */
--text-3xl: 1.875rem;     /* 30px */

/* Weight — Functional hierarchy */
--font-light: 300;        /* De-emphasized */
--font-normal: 400;       /* Body */
--font-medium: 500;       /* UI labels */
--font-semibold: 600;     /* Headings */

/* Line Height — Compact but readable */
--leading-tight: 1.2;
--leading-normal: 1.45;
--leading-relaxed: 1.6;
```

#### A.3 Shape Language

**Principle:** Angular precision. Straight lines, sharp corners, technical aesthetic.

```css
--radius-none: 0;
--radius-sm: 2px;         /* Micro-rounding */
--radius-md: 4px;         /* Default */
--radius-lg: 6px;         /* Cards */
--radius-xl: 8px;         /* Modals */
--radius-full: 9999px;    /* Pills only */

/* Shapes are predominantly rectangular */
/* Circles reserved for avatars and status indicators */
/* Hexagons for entity nodes in graph */
```

#### A.4 Spacing Philosophy

**Principle:** Dense but organized. Grid-aligned, no wasted space.

```css
/* 4px base unit, tight scale */
--space-1: 0.25rem;       /* 4px — micro gap */
--space-2: 0.5rem;        /* 8px — tight */
--space-3: 0.75rem;       /* 12px — standard */
--space-4: 1rem;          /* 16px — comfortable */
--space-5: 1.25rem;       /* 20px — section */
--space-6: 1.5rem;        /* 24px — large section */
--space-8: 2rem;          /* 32px — page margin */

/* Component density */
--density-compact: 0.75;  /* 75% of default spacing */
--density-normal: 1;
--density-comfortable: 1.25;
```

#### A.5 Contrast Model

| Element | Foreground | Background | Ratio | Level |
|---------|------------|------------|-------|-------|
| Body text | #e8edf5 | #0a0d12 | 14.2:1 | AAA |
| Secondary | #8892a6 | #0a0d12 | 6.8:1 | AA |
| Muted | #5a6478 | #0a0d12 | 4.2:1 | AA (large) |
| Links | #6db3f2 | #0a0d12 | 7.1:1 | AA |
| Entity badge | #4a9eff | #111621 | 5.8:1 | AA |

#### A.6 Motion Style

**Principle:** Precise, mechanical. Quick entrances, instant feedback.

```css
--duration-instant: 50ms;
--duration-fast: 100ms;
--duration-base: 150ms;
--duration-slow: 250ms;

--ease-sharp: cubic-bezier(0.12, 0, 0.39, 0);     /* Quick stop */
--ease-snap: cubic-bezier(0.2, 0, 0, 1);          /* Snappy */
--ease-mechanical: steps(4, end);                  /* Stepped transitions */

/* Animation keywords: snap, slide, fade */
/* No bounce, no overshoot, no wobble */
```

#### A.7 Example Components

```
┌──────────────────────────────────────────────────┐
│ ENTITY BADGE (Obsidian style)                     │
├──────────────────────────────────────────────────┤
│ ┌────────────────┐                               │
│ │ ◆ Concept      │  Sharp corners, 2px radius    │
│ └────────────────┘  Solid entity color left edge │
│                     Monospace type option         │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ CARD (Obsidian style)                            │
├──────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────┐   │
│ │ ◆ Cognitive Load                            │   │
│ ├────────────────────────────────────────────┤   │
│ │ The amount of mental effort...              │   │
│ │ 12 connections · 2h ago                     │   │
│ └────────────────────────────────────────────┘   │
│ 4px radius, 1px border, no shadow                │
│ Header separated by horizontal rule              │
└──────────────────────────────────────────────────┘
```

---

### Option B: "Warm Ember"

**Philosophy:** Cozy knowledge fireside. Warm undertones, soft edges, inviting surfaces. Reading feels like settling into a comfortable chair.

#### B.1 Color System

```css
/* Backgrounds — Warm browns and ochres */
--bg-primary: #100d0a;           /* Warm near-black */
--bg-secondary: #1a1612;         /* Warm elevated */
--bg-tertiary: #252018;          /* Nested warmth */
--bg-hover: #2e2720;             /* Warm hover */
--bg-active: #38302a;            /* Active warmth */

/* Text — Cream and warm whites */
--text-primary: #f5f2ed;         /* Warm white */
--text-secondary: #b8a894;       /* Warm secondary */
--text-muted: #7a6e5f;           /* Muted warmth */
--text-accent: #e8a855;          /* Amber accent */

/* Entity Colors — Sunset palette */
--entity-concept: #6ea8fe;       /* Sky blue */
--entity-person: #69d9a5;        /* Sage green */
--entity-theory: #b794f4;        /* Lavender */
--entity-framework: #ffc078;     /* Peach */
--entity-assessment: #ff8a8a;    /* Coral */
--entity-spark: #ff9ec4;         /* Rose */
--entity-insight: #78dce8;       /* Mint */
--entity-thread: #c5e478;        /* Chartreuse */

/* Borders — Warm golden tints */
--border-subtle: rgba(200, 160, 100, 0.06);
--border-default: rgba(200, 160, 100, 0.12);
--border-focus: rgba(232, 168, 85, 0.4);
```

#### B.2 Typography

```css
/* Font Stack — Humanist, readable */
--font-sans: 'Source Sans Pro', 'Segoe UI', system-ui, sans-serif;
--font-serif: 'Source Serif Pro', 'Georgia', serif;
--font-mono: 'Source Code Pro', monospace;

/* Scale — Comfortable reading */
--text-xs: 0.75rem;       /* 12px */
--text-sm: 0.875rem;      /* 14px */
--text-base: 1rem;        /* 16px */
--text-lg: 1.125rem;      /* 18px */
--text-xl: 1.3125rem;     /* 21px */
--text-2xl: 1.625rem;     /* 26px */
--text-3xl: 2rem;         /* 32px */

/* Weights — Gentle hierarchy */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;

/* Line heights — Generous */
--leading-normal: 1.5;
--leading-relaxed: 1.65;
--leading-loose: 1.8;
```

#### B.3 Shape Language

**Principle:** Soft, organic. Rounded corners, no sharp edges.

```css
--radius-sm: 6px;
--radius-md: 10px;
--radius-lg: 14px;
--radius-xl: 20px;
--radius-2xl: 28px;
--radius-full: 9999px;

/* All interactive elements use rounded corners */
/* Organic blob shapes for decorative elements */
/* Circles prominent in entity visualization */
```

#### B.4 Spacing Philosophy

**Principle:** Generous breathing room. Content doesn't feel cramped.

```css
/* 4px base, generous scale */
--space-1: 0.25rem;       /* 4px */
--space-2: 0.5rem;        /* 8px */
--space-3: 0.875rem;      /* 14px */
--space-4: 1.25rem;       /* 20px */
--space-5: 1.5rem;        /* 24px */
--space-6: 2rem;          /* 32px */
--space-8: 2.5rem;        /* 40px */
--space-10: 3rem;         /* 48px */

/* Padding multiplier for warmth */
--pad-cozy: 1.25;         /* 125% of default */
```

#### B.5 Contrast Model

| Element | Foreground | Background | Ratio | Level |
|---------|------------|------------|-------|-------|
| Body text | #f5f2ed | #100d0a | 13.8:1 | AAA |
| Secondary | #b8a894 | #100d0a | 7.2:1 | AA |
| Accent | #e8a855 | #100d0a | 8.5:1 | AAA |
| Links | #6ea8fe | #1a1612 | 6.2:1 | AA |

#### B.6 Motion Style

**Principle:** Gentle, organic. Soft entrances, eased transitions.

```css
--duration-fast: 180ms;
--duration-base: 280ms;
--duration-slow: 400ms;

--ease-gentle: cubic-bezier(0.4, 0, 0.2, 1);      /* Soft standard */
--ease-cozy: cubic-bezier(0.16, 1, 0.3, 1);      /* Gentle overshoot */
--ease-settle: cubic-bezier(0.22, 1, 0.36, 1);   /* Settling motion */

/* Animation keywords: float, drift, settle */
/* Subtle scale changes on hover (1.02-1.03) */
/* Soft glow on focus states */
```

#### B.7 Example Components

```
┌──────────────────────────────────────────────────┐
│ ENTITY BADGE (Warm Ember style)                  │
├──────────────────────────────────────────────────┤
│ ┌────────────────────┐                           │
│ │  ● Concept         │  Pill shape, generous pad │
│ └────────────────────┘  Soft glow on hover       │
│                         Warm entity color fill   │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ CARD (Warm Ember style)                          │
├──────────────────────────────────────────────────┤
│ ╭────────────────────────────────────────────╮   │
│ │  ● Cognitive Load                          │   │
│ │                                            │   │
│ │  The amount of mental effort being used... │   │
│ │                                            │   │
│ │  12 connections · 2h ago                   │   │
│ ╰────────────────────────────────────────────╯   │
│ 14px radius, soft shadow, no visible border      │
│ Generous internal padding (20px+)                │
└──────────────────────────────────────────────────┘
```

---

### Option C: "Neon Grid"

**Philosophy:** Cyberpunk knowledge matrix. High-contrast neon on black, grid-aligned, futuristic precision.

#### C.1 Color System

```css
/* Backgrounds — Pure black with subtle grid */
--bg-primary: #000000;           /* True black */
--bg-secondary: #0a0a0a;         /* Near black */
--bg-tertiary: #141414;          /* Grid visible */
--bg-hover: #1a1a1a;
--bg-active: #242424;
--bg-grid: rgba(255, 255, 255, 0.03);  /* Grid overlay */

/* Text — Electric whites and neons */
--text-primary: #ffffff;         /* Pure white */
--text-secondary: #888888;       /* Gray */
--text-muted: #555555;
--text-glow: #00ff88;            /* Matrix green glow */

/* Entity Colors — Neon spectrum */
--entity-concept: #00aaff;       /* Electric blue */
--entity-person: #00ff88;        /* Matrix green */
--entity-theory: #aa55ff;        /* Neon purple */
--entity-framework: #ffaa00;     /* Amber */
--entity-assessment: #ff5555;    /* Red */
--entity-spark: #ff55aa;         /* Hot pink */
--entity-insight: #00ffff;       /* Cyan */
--entity-thread: #aaff00;        /* Lime */

/* Glows — Neon glow effects */
--glow-concept: 0 0 20px rgba(0, 170, 255, 0.5);
--glow-person: 0 0 20px rgba(0, 255, 136, 0.5);
--glow-theory: 0 0 20px rgba(170, 85, 255, 0.5);

/* Borders — Neon accents */
--border-subtle: rgba(255, 255, 255, 0.05);
--border-default: rgba(255, 255, 255, 0.1);
--border-neon: 1px solid currentColor;
```

#### C.2 Typography

```css
/* Font Stack — Geometric, technical */
--font-sans: 'Space Grotesk', 'Orbitron', system-ui, sans-serif;
--font-mono: 'Space Mono', 'Fira Code', monospace;
--font-display: 'Orbitron', sans-serif;

/* Scale — Modular, technical */
--text-xs: 0.75rem;
--text-sm: 0.875rem;
--text-base: 1rem;
--text-lg: 1.125rem;
--text-xl: 1.25rem;
--text-2xl: 1.5rem;
--text-3xl: 2rem;

/* All caps option for headers */
--text-caps: uppercase;
--letter-spacing-caps: 0.1em;

/* Weights */
--font-normal: 400;
--font-medium: 500;
--font-bold: 700;
```

#### C.3 Shape Language

**Principle:** Geometric precision. Octagonal, hexagonal, grid-aligned.

```css
--radius-none: 0;
--radius-sm: 0;           /* Sharp by default */
--radius-md: 0;
--radius-chamfer: 4px;    /* Chamfered corners option */
--radius-hex: polygon();  /* Hexagonal clips */

/* CSS clip-paths for geometric shapes */
--clip-octagon: polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%);
--clip-hexagon: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
```

#### C.4 Spacing Philosophy

**Principle:** Grid-locked. Everything aligns to 8px grid.

```css
/* 8px base unit, strict grid */
--space-1: 0.5rem;        /* 8px */
--space-2: 1rem;          /* 16px */
--space-3: 1.5rem;        /* 24px */
--space-4: 2rem;          /* 32px */
--space-5: 2.5rem;        /* 40px */
--space-6: 3rem;          /* 48px */

/* All spacing must be multiples of 8px */
/* Grid visible as background pattern */
```

#### C.5 Contrast Model

| Element | Foreground | Background | Ratio | Level |
|---------|------------|------------|-------|-------|
| Body text | #ffffff | #000000 | 21:1 | AAA |
| Secondary | #888888 | #000000 | 5.3:1 | AA |
| Neon blue | #00aaff | #000000 | 8.6:1 | AAA |
| Neon green | #00ff88 | #000000 | 12.1:1 | AAA |

#### C.6 Motion Style

**Principle:** Digital, glitchy. Instant, with subtle digital artifacts.

```css
--duration-instant: 0ms;
--duration-fast: 80ms;
--duration-base: 120ms;
--duration-slow: 200ms;

--ease-digital: steps(1, end);                    /* Instant snap */
--ease-scan: cubic-bezier(0, 0, 0.2, 1);         /* Scanline feel */
--ease-glitch: cubic-bezier(0.6, -0.28, 0.74, 0.05);  /* Overshoot */

/* Animation keywords: scan, flicker, pulse */
/* Optional CRT scanline overlay */
/* Subtle glow pulse on active elements */
```

#### C.7 Example Components

```
┌──────────────────────────────────────────────────┐
│ ENTITY BADGE (Neon Grid style)                   │
├──────────────────────────────────────────────────┤
│ ┌─────────────────┐                              │
│ │▸ CONCEPT        │  Sharp edges, all caps       │
│ └─────────────────┘  Neon border glow on hover   │
│                      Geometric icon prefix       │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ CARD (Neon Grid style)                           │
├──────────────────────────────────────────────────┤
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓    │
│ ┃ ▸ COGNITIVE LOAD                         ┃    │
│ ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫    │
│ ┃ The amount of mental effort...           ┃    │
│ ┃                                          ┃    │
│ ┃ 12 ∙ 2H                                  ┃    │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛    │
│ Zero radius, 1px neon border, grid background   │
│ Data displayed in compact format                │
└──────────────────────────────────────────────────┘
```

---

### Option D: "Zen Paper"

**Philosophy:** Meditative simplicity. Paper-like texture, maximum whitespace, calligraphic elegance. Knowledge as haiku.

#### D.1 Color System

```css
/* Backgrounds — Ink-washed paper tones */
--bg-primary: #0e0e0e;           /* Sumi ink */
--bg-secondary: #161616;         /* Lighter ink wash */
--bg-tertiary: #1e1e1e;          /* Paper shadow */
--bg-hover: #262626;
--bg-active: #2e2e2e;

/* Text — Brush stroke blacks and grays */
--text-primary: #e6e6e6;         /* Rice paper white */
--text-secondary: #999999;       /* Diluted ink */
--text-muted: #666666;           /* Faded characters */
--text-accent: #c4a87c;          /* Gold leaf */

/* Entity Colors — Traditional ink colors */
--entity-concept: #7eb8da;       /* Ai (indigo) */
--entity-person: #8fbc8f;        /* Matcha */
--entity-theory: #b8a9c9;        /* Fuji (wisteria) */
--entity-framework: #d4a574;     /* Kitsune (fox) */
--entity-assessment: #cd5c5c;    /* Aka (red) */
--entity-spark: #e8a4b8;         /* Sakura */
--entity-insight: #8ecae6;       /* Sora (sky) */
--entity-thread: #adc178;        /* Wakaba (young leaf) */

/* Borders — Brushstroke quality */
--border-subtle: rgba(255, 255, 255, 0.03);
--border-default: rgba(255, 255, 255, 0.06);
--border-brush: 2px solid;       /* Calligraphic weight */
```

#### D.2 Typography

```css
/* Font Stack — Elegant, calligraphic feel */
--font-sans: 'Noto Sans', 'Hiragino Sans', system-ui, sans-serif;
--font-serif: 'Noto Serif', 'Hiragino Mincho', serif;
--font-mono: 'Noto Sans Mono', monospace;

/* Scale — Spacious, contemplative */
--text-xs: 0.75rem;
--text-sm: 0.875rem;
--text-base: 1.0625rem;    /* 17px — slightly larger base */
--text-lg: 1.25rem;
--text-xl: 1.5rem;
--text-2xl: 1.875rem;
--text-3xl: 2.5rem;

/* Weights — Minimal variation */
--font-normal: 400;
--font-medium: 500;

/* Line heights — Generous breathing */
--leading-normal: 1.6;
--leading-relaxed: 1.8;
--leading-loose: 2.0;
```

#### D.3 Shape Language

**Principle:** Minimal, asymmetric. Few shapes, meaningful placement.

```css
--radius-none: 0;
--radius-sm: 2px;
--radius-md: 4px;
--radius-lg: 8px;

/* Asymmetric rounding option */
--radius-paper: 0 8px 0 8px;     /* Top-right, bottom-left */

/* Shapes are subtle, mostly rectangular */
/* Single accent stroke/line for emphasis */
/* Negative space as design element */
```

#### D.4 Spacing Philosophy

**Principle:** Ma (negative space). Generous whitespace, asymmetric balance.

```css
/* 8px base, expansive scale */
--space-1: 0.5rem;        /* 8px */
--space-2: 1rem;          /* 16px */
--space-3: 1.5rem;        /* 24px */
--space-4: 2rem;          /* 32px */
--space-6: 3rem;          /* 48px */
--space-8: 4rem;          /* 64px */
--space-12: 6rem;         /* 96px */

/* Asymmetric padding */
--pad-zen-x: var(--space-6);
--pad-zen-y: var(--space-4);
```

#### D.5 Contrast Model

| Element | Foreground | Background | Ratio | Level |
|---------|------------|------------|-------|-------|
| Body text | #e6e6e6 | #0e0e0e | 12.6:1 | AAA |
| Secondary | #999999 | #0e0e0e | 6.5:1 | AA |
| Accent | #c4a87c | #0e0e0e | 7.8:1 | AA |

#### D.6 Motion Style

**Principle:** Deliberate, zen. Slow, intentional, meditative.

```css
--duration-slow: 400ms;
--duration-base: 300ms;
--duration-deliberate: 600ms;

--ease-zen: cubic-bezier(0.33, 0, 0.2, 1);        /* Gentle */
--ease-breath: cubic-bezier(0.4, 0, 0.6, 1);     /* In-out breath */
--ease-flow: cubic-bezier(0.16, 1, 0.3, 1);      /* Water-like */

/* Animation keywords: appear, fade, flow */
/* Minimal motion, purposeful transitions */
/* Subtle ink-spreading effects */
```

#### D.7 Example Components

```
┌──────────────────────────────────────────────────┐
│ ENTITY BADGE (Zen Paper style)                   │
├──────────────────────────────────────────────────┤
│                                                  │
│     Concept                                      │
│     ─────                                        │
│                                                  │
│ Minimal: text + underline only                   │
│ Entity color as subtle text tint                 │
│ No background, no border, no chrome              │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ CARD (Zen Paper style)                           │
├──────────────────────────────────────────────────┤
│                                                  │
│                                                  │
│     Cognitive Load                               │
│     ─────────                                    │
│                                                  │
│     The amount of mental effort                  │
│     being used in working memory.                │
│                                                  │
│     12 · 2h                                      │
│                                                  │
│                                                  │
│ No visible card boundary                         │
│ Content floats in space with generous margin     │
│ Single horizontal rule as separator              │
└──────────────────────────────────────────────────┘
```

---

### Option E: "Glass Prism"

**Philosophy:** Light-refracting surfaces. Glassmorphism evolved — translucent layers, spectral highlights, depth through blur.

#### E.1 Color System

```css
/* Backgrounds — Translucent layers */
--bg-primary: #0a0a0c;
--bg-secondary: rgba(20, 20, 24, 0.8);    /* Glass base */
--bg-tertiary: rgba(30, 30, 36, 0.7);
--bg-hover: rgba(40, 40, 48, 0.8);
--bg-active: rgba(50, 50, 60, 0.85);

/* Glass effects */
--glass-tint: rgba(255, 255, 255, 0.05);
--glass-blur: blur(16px);
--glass-saturate: saturate(180%);
--glass-border: 1px solid rgba(255, 255, 255, 0.08);

/* Text */
--text-primary: #f8f8fc;
--text-secondary: #a0a0b0;
--text-muted: #606070;
--text-spectral: linear-gradient(90deg, #ff6b6b, #4ecdc4);

/* Entity Colors — Spectral, prismatic */
--entity-concept: #60a5fa;
--entity-person: #34d399;
--entity-theory: #a78bfa;
--entity-framework: #fbbf24;
--entity-assessment: #f87171;
--entity-spark: #f472b6;
--entity-insight: #22d3ee;
--entity-thread: #a3e635;

/* Prismatic highlights */
--prism-gradient: linear-gradient(135deg,
  rgba(96, 165, 250, 0.1),
  rgba(167, 139, 250, 0.1),
  rgba(244, 114, 182, 0.1)
);
```

#### E.2 Typography

```css
/* Font Stack — Clean, modern */
--font-sans: 'Inter', system-ui, sans-serif;
--font-mono: 'JetBrains Mono', monospace;

/* Scale — Balanced */
--text-xs: 0.75rem;
--text-sm: 0.875rem;
--text-base: 1rem;
--text-lg: 1.125rem;
--text-xl: 1.25rem;
--text-2xl: 1.5rem;
--text-3xl: 1.875rem;

/* Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;

/* Line heights */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
```

#### E.3 Shape Language

**Principle:** Soft geometry. Rounded rectangles, frosted surfaces.

```css
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;
--radius-xl: 20px;
--radius-2xl: 28px;
--radius-full: 9999px;

/* Glass panel styling */
.glass-panel {
  background: var(--bg-secondary);
  backdrop-filter: var(--glass-blur) var(--glass-saturate);
  border: var(--glass-border);
  border-radius: var(--radius-lg);
}
```

#### E.4 Spacing Philosophy

**Principle:** Layered depth. Space creates visual layers.

```css
/* 4px base */
--space-1: 0.25rem;
--space-2: 0.5rem;
--space-3: 0.75rem;
--space-4: 1rem;
--space-5: 1.25rem;
--space-6: 1.5rem;
--space-8: 2rem;

/* Layer spacing (z-axis feeling) */
--layer-gap: var(--space-4);
--layer-pad: var(--space-5);
```

#### E.5 Contrast Model

| Element | Foreground | Background | Ratio | Level |
|---------|------------|------------|-------|-------|
| Body text | #f8f8fc | #0a0a0c | 15.1:1 | AAA |
| On glass | #f8f8fc | rgba(20,20,24,0.8) | ~12:1 | AAA |
| Secondary | #a0a0b0 | #0a0a0c | 6.3:1 | AA |

#### E.6 Motion Style

**Principle:** Fluid, layered. Depth-aware transitions.

```css
--duration-fast: 150ms;
--duration-base: 250ms;
--duration-slow: 350ms;

--ease-glass: cubic-bezier(0.4, 0, 0.2, 1);
--ease-layer: cubic-bezier(0.16, 1, 0.3, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);

/* Animation keywords: float, layer, blur */
/* Parallax-like depth effects */
/* Blur transitions on focus */
```

#### E.7 Example Components

```
┌──────────────────────────────────────────────────┐
│ ENTITY BADGE (Glass Prism style)                 │
├──────────────────────────────────────────────────┤
│ ╭─────────────────────╮                          │
│ │ ● Concept           │  Glass background        │
│ ╰─────────────────────╯  Backdrop blur visible   │
│                          Subtle prismatic border │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ CARD (Glass Prism style)                         │
├──────────────────────────────────────────────────┤
│ ╭──────────────────────────────────────────────╮ │
│ │ ● Cognitive Load                             │ │
│ │                                              │ │
│ │ The amount of mental effort being used       │ │
│ │ in working memory. High cognitive load...    │ │
│ │                                              │ │
│ │ 12 connections · 2h ago                      │ │
│ ╰──────────────────────────────────────────────╯ │
│ Frosted glass background with 16px blur          │
│ Subtle white border, soft shadow                 │
│ Prismatic accent gradient on hover               │
└──────────────────────────────────────────────────┘
```

---

### Option F: "Current IES Enhanced"

**Philosophy:** Evolution, not revolution. The existing IES design system refined with improved consistency and polish.

#### F.1 Color System

```css
/* Identical to Design Language Guide v2, with additions */
--bg-primary: #0f0f10;
--bg-secondary: #1a1a1c;
--bg-tertiary: #252528;
--bg-hover: #2a2a2e;
--bg-active: #323236;

/* Text */
--text-primary: #f5f5f7;
--text-secondary: #a1a1a6;
--text-muted: #6e6e73;
--text-subtle: #48484a;

/* Entity Colors (existing) */
--entity-concept: #3b82f6;
--entity-person: #10b981;
--entity-theory: #8b5cf6;
--entity-framework: #f59e0b;
--entity-assessment: #ef4444;
--entity-spark: #ec4899;
--entity-insight: #06b6d4;
--entity-thread: #84cc16;

/* NEW: Enhanced semantic states */
--focus-ring: rgba(59, 130, 246, 0.5);  /* Blue focus ring */
--selection-bg: rgba(59, 130, 246, 0.2); /* Selection highlight */
```

#### F.2 Typography

```css
/* Existing system with refinements */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Refined scale (Major Third 1.25) */
--text-xs: 0.75rem;
--text-sm: 0.875rem;
--text-base: 1rem;
--text-lg: 1.125rem;
--text-xl: 1.25rem;
--text-2xl: 1.5rem;
--text-3xl: 1.875rem;
--text-4xl: 2.25rem;

/* Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* Line heights */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
```

#### F.3 Shape Language

**Principle:** Modern, consistent. Current system standardized.

```css
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-xl: 16px;
--radius-2xl: 24px;
--radius-full: 9999px;

/* Component-specific (existing) */
--radius-button: var(--radius-md);
--radius-input: var(--radius-md);
--radius-card: var(--radius-lg);
--radius-modal: var(--radius-xl);
--radius-badge: var(--radius-full);
```

#### F.4 Spacing Philosophy

**Principle:** 4px grid, existing scale refined.

```css
/* Existing scale */
--space-0: 0;
--space-1: 0.25rem;    /* 4px */
--space-2: 0.5rem;     /* 8px */
--space-3: 0.75rem;    /* 12px */
--space-4: 1rem;       /* 16px */
--space-5: 1.25rem;    /* 20px */
--space-6: 1.5rem;     /* 24px */
--space-8: 2rem;       /* 32px */
--space-10: 2.5rem;    /* 40px */
--space-12: 3rem;      /* 48px */

/* Component spacing (existing) */
--button-padding-x: var(--space-4);
--button-padding-y: var(--space-2);
--card-padding: var(--space-4);
```

#### F.5 Contrast Model

| Element | Foreground | Background | Ratio | Level |
|---------|------------|------------|-------|-------|
| Body text | #f5f5f7 | #0f0f10 | 13.2:1 | AAA |
| Secondary | #a1a1a6 | #0f0f10 | 6.1:1 | AA |
| Muted | #6e6e73 | #0f0f10 | 3.8:1 | AA (lg) |
| Entity blue | #3b82f6 | #0f0f10 | 5.5:1 | AA |

#### F.6 Motion Style

**Principle:** Fast, purposeful. ADHD-friendly timing.

```css
--duration-instant: 75ms;
--duration-fast: 150ms;
--duration-base: 200ms;
--duration-slow: 300ms;

--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);

/* Existing keyframes maintained */
/* @keyframes fade-in, slide-up, scale-in, etc. */
```

#### F.7 Example Components

```
Identical to current 05-component-library-specs.md
with improved state consistency and accessibility
```

---

## Part 2: Component System Options

Six component system architectures with distinct organizational philosophies, naming conventions, and interaction patterns.

---

### System 1: "Atomic Design Extended"

**Philosophy:** Atoms → Molecules → Organisms → Templates → Pages. Extended with Tokens and Behaviors.

#### 1.1 Naming Convention

```
Pattern: [Level][Category][Name][Variant?][State?]

Levels:
  01- Tokens (design variables)
  02- Atoms (indivisible elements)
  03- Molecules (simple combinations)
  04- Organisms (complex sections)
  05- Templates (page structures)
  06- Pages (final implementations)

Examples:
  02-atom-button-primary
  02-atom-button-primary-hover
  03-molecule-search-input
  03-molecule-entity-badge-sm
  04-organism-entity-card-expanded
  04-organism-flow-panel-collapsed
  05-template-reader-layout
  06-page-flow-mode
```

#### 1.2 Responsive Rules

```scss
// Breakpoint tokens
$breakpoints: (
  'xs': 320px,    // Mobile small
  'sm': 480px,    // Mobile large
  'md': 768px,    // Tablet
  'lg': 1024px,   // Desktop
  'xl': 1280px,   // Wide desktop
  '2xl': 1536px   // Ultra-wide
);

// Responsive mixin
@mixin respond($breakpoint) {
  @media (min-width: map-get($breakpoints, $breakpoint)) {
    @content;
  }
}

// Component responsive pattern
.entity-card {
  padding: var(--space-3);           // Mobile default

  @include respond('md') {
    padding: var(--space-4);         // Tablet+
  }

  @include respond('lg') {
    padding: var(--space-5);         // Desktop+
  }
}

// Layout shifts
.flow-panel {
  // Mobile: Bottom sheet
  position: fixed;
  bottom: 0;
  width: 100%;

  @include respond('md') {
    // Tablet+: Side panel
    position: relative;
    width: 400px;
    bottom: auto;
  }
}
```

#### 1.3 State Logic

```typescript
// State machine approach
type ComponentState =
  | 'idle'
  | 'hover'
  | 'focus'
  | 'active'
  | 'disabled'
  | 'loading'
  | 'error'
  | 'success';

interface StatefulComponent<T> {
  state: ComponentState;
  data: T;
  transition(event: string): void;
}

// State transitions defined per component
const buttonStateMachine = {
  idle: {
    HOVER: 'hover',
    FOCUS: 'focus',
    CLICK: 'active',
    DISABLE: 'disabled'
  },
  hover: {
    LEAVE: 'idle',
    CLICK: 'active',
    FOCUS: 'focus'
  },
  active: {
    RELEASE: 'hover',
    COMPLETE: 'success',
    FAIL: 'error'
  },
  // ... etc
};

// CSS state classes
.atom-button {
  &[data-state="idle"] { /* default styles */ }
  &[data-state="hover"] { background: var(--bg-hover); }
  &[data-state="focus"] { outline: 2px solid var(--focus-ring); }
  &[data-state="active"] { transform: translateY(1px); }
  &[data-state="disabled"] { opacity: 0.5; cursor: not-allowed; }
  &[data-state="loading"] { /* spinner styles */ }
}
```

---

### System 2: "BEM-Extended"

**Philosophy:** Block__Element--Modifier extended with Namespaces and Utilities.

#### 2.1 Naming Convention

```css
Pattern: [namespace]-[block]__[element]--[modifier]

Namespaces:
  c-  Components (reusable UI)
  l-  Layout (structural)
  u-  Utility (single-purpose)
  t-  Theme (theming)
  js- JavaScript hooks
  is- State classes

Examples:
  c-entity-badge
  c-entity-badge__icon
  c-entity-badge__label
  c-entity-badge--sm
  c-entity-badge--concept
  c-entity-badge.is-active

  l-flow-panel
  l-flow-panel__header
  l-flow-panel__content
  l-flow-panel--collapsed

  u-mt-4        (margin-top: 1rem)
  u-text-muted
  u-hidden-sm   (hidden on small screens)

  t-dark
  t-entity-concept

  js-toggle-panel
  js-entity-lookup

  is-loading
  is-expanded
  is-selected
```

#### 2.2 Responsive Rules

```css
/* Responsive modifier pattern */
.c-entity-card {
  padding: 12px;
}

.c-entity-card--compact {
  padding: 8px;
}

/* Breakpoint-specific modifiers */
@media (min-width: 768px) {
  .c-entity-card--md\:expanded {
    padding: 20px;
  }
}

/* Utility responsive variants */
.u-hidden { display: none; }
.u-hidden-sm { @media (max-width: 479px) { display: none; } }
.u-hidden-md { @media (max-width: 767px) { display: none; } }
.u-show-md { @media (min-width: 768px) { display: block; } }

/* Layout responsive shifts */
.l-flow-panel {
  /* Mobile */
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  max-height: 70vh;
}

@media (min-width: 768px) {
  .l-flow-panel {
    position: static;
    max-height: none;
    width: 400px;
  }
}
```

#### 2.3 State Logic

```css
/* State classes using is- prefix */
.c-button {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  cursor: pointer;
}

.c-button.is-hover,
.c-button:hover {
  background: var(--bg-hover);
}

.c-button.is-focus,
.c-button:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}

.c-button.is-active,
.c-button:active {
  transform: translateY(1px);
  background: var(--bg-active);
}

.c-button.is-disabled,
.c-button[disabled] {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.c-button.is-loading {
  color: transparent;
  position: relative;
}

.c-button.is-loading::after {
  content: '';
  /* spinner styles */
}

/* JavaScript toggles state classes */
button.addEventListener('click', () => {
  button.classList.add('is-loading');
});
```

---

### System 3: "Tailwind-Native"

**Philosophy:** Utility-first with component extraction. Design tokens as Tailwind config.

#### 3.1 Naming Convention

```jsx
// No custom class names — composition of utilities
// Component files named by purpose

// EntityBadge.tsx
<span className={cn(
  // Base styles
  "inline-flex items-center gap-1",
  "px-3 py-1 rounded-full",
  "text-xs font-medium",
  "transition-colors duration-150",

  // Entity type variants
  entityTypeStyles[type],

  // Size variants
  sizeStyles[size],

  // State variants
  interactive && "cursor-pointer hover:opacity-90",
  selected && "ring-2 ring-offset-2",
  disabled && "opacity-50 cursor-not-allowed"
)}>
  <EntityIcon type={type} className="w-4 h-4" />
  <span>{label}</span>
</span>

// Extracted component classes (rare)
// In tailwind.config.js
module.exports = {
  theme: {
    extend: {
      // Design tokens become Tailwind theme
      colors: {
        'bg-primary': '#0f0f10',
        'entity-concept': '#3b82f6',
        // ... etc
      }
    }
  },
  plugins: [
    // Component plugin for rare extractions
    plugin(({ addComponents }) => {
      addComponents({
        '.entity-badge-base': {
          '@apply inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium': {}
        }
      })
    })
  ]
}
```

#### 3.2 Responsive Rules

```jsx
// Tailwind responsive prefixes
<div className={cn(
  // Mobile first
  "p-3 text-sm",

  // Tablet (md:)
  "md:p-4 md:text-base",

  // Desktop (lg:)
  "lg:p-6 lg:text-lg",

  // Layout shifts
  "fixed bottom-0 inset-x-0",       // Mobile: bottom sheet
  "md:static md:w-96",              // Tablet+: side panel

  // Visibility
  "hidden md:block",                // Hide on mobile
  "md:hidden"                       // Show only on mobile
)}>

// Container queries (Tailwind v3.3+)
<div className="@container">
  <div className="@md:flex @md:gap-4">
    {/* Responds to container width, not viewport */}
  </div>
</div>
```

#### 3.3 State Logic

```jsx
// State via Tailwind modifiers
<button className={cn(
  // Base
  "bg-bg-tertiary text-text-primary",

  // Hover
  "hover:bg-bg-hover",

  // Focus
  "focus-visible:outline-2 focus-visible:outline-focus-ring",

  // Active
  "active:translate-y-px active:bg-bg-active",

  // Disabled
  "disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none",

  // Group states (parent hover affects child)
  "group-hover:opacity-100",

  // Peer states (sibling state affects element)
  "peer-invalid:border-red-500",

  // Data attributes for JS-controlled state
  "data-[loading=true]:text-transparent",
  "data-[selected=true]:ring-2"
)}>

// State management via data attributes
<button
  data-loading={isLoading}
  data-selected={isSelected}
  className="..."
>
```

---

### System 4: "CSS Modules + Design Tokens"

**Philosophy:** Scoped styles with shared tokens. Maximum encapsulation, clear contracts.

#### 4.1 Naming Convention

```
File structure:
components/
  EntityBadge/
    EntityBadge.tsx
    EntityBadge.module.css
    EntityBadge.types.ts
    EntityBadge.test.tsx
    index.ts

CSS class naming (within modules):
  - camelCase for class names
  - Descriptive, no abbreviations
  - Modifiers as separate classes

EntityBadge.module.css:
  .badge { }
  .badgeSmall { }
  .badgeMedium { }
  .badgeLarge { }
  .icon { }
  .label { }
  .interactive { }
  .selected { }
  .disabled { }
  .conceptType { }
  .personType { }

Usage in component:
  import styles from './EntityBadge.module.css';

  <span className={cn(
    styles.badge,
    styles[`${size}Size`],
    styles[`${type}Type`],
    interactive && styles.interactive,
    selected && styles.selected
  )}>
```

#### 4.2 Responsive Rules

```css
/* EntityBadge.module.css */

/* Design tokens imported globally */
@import '../../styles/tokens.css';

.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);

  /* Mobile-first responsive */
  @media (min-width: 768px) {
    padding: var(--space-2) var(--space-4);
    font-size: var(--text-sm);
  }
}

/* Container query support */
@container (min-width: 400px) {
  .badge {
    gap: var(--space-2);
  }
}

/* Responsive utility classes in separate file */
/* responsive.module.css */
.hiddenMobile {
  @media (max-width: 767px) {
    display: none;
  }
}

.hiddenDesktop {
  @media (min-width: 768px) {
    display: none;
  }
}
```

#### 4.3 State Logic

```css
/* EntityBadge.module.css */

.badge {
  transition: var(--transition-colors);
}

/* Hover state */
.interactive:hover {
  background: var(--bg-hover);
  cursor: pointer;
}

/* Focus state */
.badge:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}

/* Active state */
.interactive:active {
  transform: translateY(1px);
}

/* Selected state (data attribute) */
.badge[data-selected="true"] {
  ring: 2px solid var(--border-focus);
}

/* Disabled state */
.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

/* Loading state */
.loading {
  color: transparent;
  position: relative;
}

.loading::after {
  content: '';
  position: absolute;
  /* spinner animation */
}
```

```typescript
// EntityBadge.tsx
interface EntityBadgeProps {
  state?: 'idle' | 'hover' | 'focus' | 'active' | 'disabled' | 'loading';
}

// State managed via props + data attributes
<span
  className={cn(styles.badge, state === 'disabled' && styles.disabled)}
  data-selected={selected}
  data-loading={loading}
>
```

---

### System 5: "Compound Components"

**Philosophy:** Related components share context. Parent orchestrates, children render.

#### 5.1 Naming Convention

```typescript
// Compound component pattern
// Parent + dot notation children

EntityCard.tsx exports:
  EntityCard (parent/container)
  EntityCard.Header
  EntityCard.Body
  EntityCard.Footer
  EntityCard.Badge
  EntityCard.Actions

Usage:
<EntityCard entity={entity} selected={isSelected}>
  <EntityCard.Header>
    <EntityCard.Badge />
    <EntityCard.Actions />
  </EntityCard.Header>
  <EntityCard.Body maxLines={3} />
  <EntityCard.Footer showConnections showTimestamp />
</EntityCard>

File naming:
  EntityCard/
    EntityCard.tsx        // Parent + exports
    EntityCardContext.tsx // Shared context
    Header.tsx
    Body.tsx
    Footer.tsx
    Badge.tsx
    Actions.tsx
    index.ts

CSS:
  .entityCard { }
  .entityCard-header { }
  .entityCard-body { }
  .entityCard-footer { }
  .entityCard-badge { }
  .entityCard-actions { }
```

#### 5.2 Responsive Rules

```typescript
// Responsive behavior defined at parent level
<EntityCard
  entity={entity}
  layout={useResponsive({
    base: 'compact',      // Mobile
    md: 'standard',       // Tablet
    lg: 'expanded'        // Desktop
  })}
>
  <EntityCard.Header />
  <EntityCard.Body />
  {/* Footer only on tablet+ */}
  <Show when={isAboveMd}>
    <EntityCard.Footer />
  </Show>
</EntityCard>

// Context provides responsive info to children
const EntityCardContext = createContext({
  layout: 'standard',
  isMobile: false,
  isExpanded: false
});

// Children read context for responsive rendering
function Body({ maxLines }) {
  const { layout, isMobile } = useEntityCardContext();
  const lines = isMobile ? 2 : maxLines;
  // ...
}
```

#### 5.3 State Logic

```typescript
// State managed at parent, distributed via context
interface EntityCardState {
  isHovered: boolean;
  isFocused: boolean;
  isSelected: boolean;
  isExpanded: boolean;
  isLoading: boolean;
}

const EntityCardContext = createContext<{
  state: EntityCardState;
  dispatch: (action: EntityCardAction) => void;
}>();

// Parent manages state machine
function EntityCard({ children, entity }) {
  const [state, dispatch] = useReducer(entityCardReducer, initialState);

  return (
    <EntityCardContext.Provider value={{ state, dispatch, entity }}>
      <div
        className={cn(styles.card, state.isSelected && styles.selected)}
        onMouseEnter={() => dispatch({ type: 'HOVER_START' })}
        onMouseLeave={() => dispatch({ type: 'HOVER_END' })}
      >
        {children}
      </div>
    </EntityCardContext.Provider>
  );
}

// Children respond to state
function Header() {
  const { state, entity } = useEntityCardContext();
  return (
    <div className={cn(
      styles.header,
      state.isHovered && styles.headerHovered
    )}>
      {entity.name}
    </div>
  );
}
```

---

### System 6: "Headless + Styled Variants"

**Philosophy:** Behavior separate from styling. Headless logic + variant-based styling.

#### 6.1 Naming Convention

```typescript
// Two-layer system:
// 1. Headless hooks (behavior)
// 2. Styled components (presentation)

// Headless layer
hooks/
  useEntityBadge.ts      // Returns props, state, handlers
  useEntityCard.ts
  useFlowPanel.ts
  useSearchInput.ts

// Styled layer
components/
  EntityBadge.tsx        // Uses hook + applies variants
  EntityBadge.variants.ts // CVA variant definitions

// Variant naming (CVA pattern)
const badgeVariants = cva(
  // Base classes
  "inline-flex items-center gap-1 rounded-full font-medium transition-colors",
  {
    variants: {
      size: {
        sm: "px-2 py-0.5 text-xs",
        md: "px-3 py-1 text-sm",
        lg: "px-4 py-1.5 text-base"
      },
      entityType: {
        concept: "bg-entity-concept/15 text-entity-concept border-entity-concept",
        person: "bg-entity-person/15 text-entity-person border-entity-person",
        // ... etc
      },
      intent: {
        default: "border border-current",
        subtle: "border-transparent",
        strong: "bg-current text-white"
      }
    },
    defaultVariants: {
      size: "md",
      intent: "default"
    }
  }
);
```

#### 6.2 Responsive Rules

```typescript
// Responsive variants in CVA
const cardVariants = cva("rounded-lg border transition-all", {
  variants: {
    layout: {
      compact: "p-3 gap-2",
      standard: "p-4 gap-3",
      expanded: "p-6 gap-4"
    }
  },
  // Compound variants for responsive behavior
  compoundVariants: [
    {
      layout: "standard",
      className: "md:p-5 md:gap-4"  // Override at breakpoint
    }
  ]
});

// Responsive hook provides layout variant
function useResponsiveLayout() {
  const [layout, setLayout] = useState<'compact' | 'standard' | 'expanded'>('compact');

  useEffect(() => {
    const mq = window.matchMedia('(min-width: 768px)');
    setLayout(mq.matches ? 'standard' : 'compact');
    // ... listener
  }, []);

  return layout;
}

// Usage
function EntityCard({ entity }) {
  const layout = useResponsiveLayout();
  return (
    <div className={cardVariants({ layout })}>
      {/* content */}
    </div>
  );
}
```

#### 6.3 State Logic

```typescript
// Headless hook manages all state
function useEntityBadge(props: EntityBadgeProps) {
  const [state, setState] = useState<BadgeState>('idle');

  const handlers = {
    onMouseEnter: () => setState('hover'),
    onMouseLeave: () => setState('idle'),
    onFocus: () => setState('focus'),
    onBlur: () => setState('idle'),
    onClick: () => {
      if (props.disabled) return;
      setState('active');
      props.onClick?.();
      setTimeout(() => setState('idle'), 150);
    }
  };

  const stateProps = {
    'data-state': state,
    'aria-disabled': props.disabled,
    'aria-pressed': props.selected,
    tabIndex: props.interactive ? 0 : -1
  };

  return { state, handlers, stateProps };
}

// Styled component applies state to variants
function EntityBadge(props: EntityBadgeProps) {
  const { state, handlers, stateProps } = useEntityBadge(props);

  return (
    <span
      className={badgeVariants({
        size: props.size,
        entityType: props.type,
        // State-based variant
        state: state  // 'idle' | 'hover' | 'focus' | 'active' | 'disabled'
      })}
      {...handlers}
      {...stateProps}
    >
      <EntityIcon type={props.type} />
      {props.label}
    </span>
  );
}

// CVA state variants
const badgeVariants = cva("...", {
  variants: {
    state: {
      idle: "",
      hover: "bg-opacity-80",
      focus: "ring-2 ring-offset-2",
      active: "scale-95",
      disabled: "opacity-50 cursor-not-allowed"
    }
  }
});
```

---

## Comparison Matrix

### Aesthetic Directions

| Aspect | A: Obsidian | B: Warm Ember | C: Neon Grid | D: Zen Paper | E: Glass Prism | F: Current+ |
|--------|-------------|---------------|--------------|--------------|----------------|-------------|
| **Mood** | Technical | Cozy | Cyberpunk | Meditative | Modern | Familiar |
| **Density** | High | Low | Medium | Very Low | Medium | Medium |
| **Color Temp** | Cool | Warm | Neutral | Neutral | Cool | Warm-neutral |
| **Corners** | Sharp | Soft | None | Minimal | Rounded | Medium |
| **Animation** | Snappy | Gentle | Digital | Deliberate | Fluid | Fast |
| **Best For** | Power users | Extended reading | Technical users | Focus sessions | Visual appeal | Broad audience |

### Component Systems

| Aspect | 1: Atomic | 2: BEM-Ext | 3: Tailwind | 4: CSS Modules | 5: Compound | 6: Headless |
|--------|-----------|------------|-------------|----------------|-------------|-------------|
| **Learning Curve** | Medium | Low | Low | Low | High | High |
| **Scalability** | High | Medium | High | High | High | Very High |
| **Encapsulation** | Medium | Low | Low | High | Medium | High |
| **Flexibility** | Medium | Medium | High | Medium | High | Very High |
| **Team Size** | Large | Any | Any | Medium | Medium | Large |
| **Reusability** | High | Medium | High | High | Very High | Very High |

---

## Recommended Combinations

### For IES Project

**Aesthetic:** Option F (Current IES Enhanced) or Option E (Glass Prism)
- F maintains continuity, E adds visual sophistication

**Component System:** System 6 (Headless + Styled Variants) or System 4 (CSS Modules)
- System 6 for maximum flexibility and testing
- System 4 for simpler, scoped approach

### Migration Path

If choosing new direction:

1. **Phase 1:** Implement design tokens from chosen aesthetic
2. **Phase 2:** Migrate 5 core components to new system
3. **Phase 3:** Roll out to remaining components
4. **Phase 4:** Deprecate old system

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-09 | Initial aesthetic directions and component systems |

---

**End of Document**
