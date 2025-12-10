# IES Design Tokens v2.0

**Single source of truth for IES design system colors, spacing, typography, and motion.**

Dark theme first, ADHD-friendly, entity-driven visual language.

## Installation

```bash
cd ies/design-tokens
npm install
npm run build
```

## Usage

### In CSS/SCSS

```css
@import '@ies/design-tokens/dist/tokens.css';

.card {
  background: var(--color-bg-secondary);
  padding: var(--space-4);
  border-radius: var(--radius-card);
  color: var(--color-text-primary);
}

.entity-concept {
  color: var(--color-entity-concept);
  background: var(--color-entity-concept-bg);
}
```

### In TypeScript/JavaScript

```typescript
import { tokens } from '@ies/design-tokens';

const entityColor = tokens.color.entity.concept; // "#3b82f6"
const spacing = tokens.space[4]; // "1rem"
const duration = tokens.duration.fast; // "150ms"
```

### In React/Styled Components

```tsx
import { tokens } from '@ies/design-tokens';

const Card = styled.div`
  background: ${tokens.color.bg.secondary};
  padding: ${tokens.space[4]};
  border-radius: ${tokens.radius.card};
  transition: all ${tokens.duration.fast} ${tokens.easing.out};
`;
```

## Token Structure

### Colors (`color`)

- **Backgrounds** (`bg`) - 5 levels (primary, secondary, tertiary, hover, active)
- **Text** (`text`) - 5 levels (primary, secondary, muted, subtle, inverse)
- **Entity Types** (`entity`) - 8 types with background variants
  - `concept` (blue), `person` (green), `theory` (purple), `framework` (amber)
  - `assessment` (red), `spark` (pink), `insight` (cyan), `thread` (lime)
- **Question Classes** (`question`) - 9 types with background variants
- **Semantic** (`semantic`) - success, warning, error, info
- **Energy Levels** (`energy`) - low, medium, high (ADHD mood-based)
- **Borders** (`border`) - subtle, default, focus, strong
- **Glass Effect** (`glass.bg`) - Glassmorphic panel background

### Spacing (`space`)

4px base unit, 0 through 32 (0px → 128px)

**Semantic spacing:**
- `space-1` (4px) - Tight gaps
- `space-2` (8px) - Small gaps
- `space-4` (16px) - Default gaps
- `space-6` (24px) - Section gaps
- `space-8` (32px) - Large gaps

**Border Radius** (`radius`):
- `sm` (4px), `md` (8px), `lg` (12px), `xl` (16px), `full` (9999px)
- Semantic: `button`, `input`, `card`, `modal`, `chip`, `badge`

**Breakpoints** (`breakpoint`):
- `sm` (480px), `md` (768px), `lg` (1024px), `xl` (1280px), `2xl` (1536px)

### Typography (`font`)

- **Families** (`family`) - sans (Inter), serif (Source Serif Pro), mono (JetBrains Mono)
- **Sizes** (`size`) - xs (12px) through 5xl (48px), Major Third scale (1.25 ratio)
- **Weights** (`weight`) - normal (400), medium (500), semibold (600), bold (700)
- **Line Heights** (`lineHeight`) - none (1) through loose (2), semantic (heading, body, code)
- **Letter Spacing** (`letterSpacing`) - tighter through widest

### Motion (`duration`, `easing`)

- **Durations** - instant (75ms), fast (150ms), base (200ms), slow (300ms), slower (500ms)
- **Easings** - out, in, in-out, spring, linear
- **Shadows** (`shadow`) - xs through xl
- **Z-Index** (`zIndex`) - base (0) through tooltip (300)

## Design Principles

1. **Dark mode only** - No light theme, consistent environment
2. **Bold entity colors** - Not muted, visibility critical for ADHD
3. **Fast by default** - 150ms transitions, instant feedback
4. **Subtle motion** - 8px slides, no aggressive animations
5. **4px base unit** - Consistent spacing rhythm
6. **WCAG AA minimum** - AAA where possible (primary text)

## Build Scripts

```bash
npm run build       # Build all formats (CSS, SCSS, JS, TS)
npm run watch       # Watch for changes and rebuild
npm run clean       # Clean dist folder
```

## Output Files

```
dist/
├── tokens.css      # CSS custom properties (--color-bg-primary)
├── tokens.scss     # SCSS variables ($color-bg-primary)
├── tokens.js       # JavaScript ES6 module
└── tokens.ts       # TypeScript with type exports
```

## Integration

### IES Reader (React + Vite)

```tsx
// vite.config.ts
import { defineConfig } from 'vite';

export default defineConfig({
  resolve: {
    alias: {
      '@ies/design-tokens': '/ies/design-tokens/dist/tokens.ts'
    }
  }
});

// In components
import { tokens } from '@ies/design-tokens';
```

### SiYuan Plugin (Svelte)

```svelte
<script>
import '@ies/design-tokens/dist/tokens.css';
</script>

<style>
.panel {
  background: var(--color-bg-secondary);
  padding: var(--space-4);
}
</style>
```

### Backend (Python/FastAPI)

Design tokens can be used in Jinja2 templates or exported as JSON for client responses.

```python
import json

with open('ies/design-tokens/tokens/colors.json') as f:
    colors = json.load(f)['color']

# Use in API response
@app.get("/api/theme")
def get_theme():
    return {"colors": colors}
```

## Development Workflow

1. **Edit tokens** - Modify JSON files in `tokens/`
2. **Build** - Run `npm run build`
3. **Import** - Updated tokens available in `dist/`
4. **Commit** - Commit both source tokens and built files

## Migration Guide

### From Hardcoded Values

**Before:**
```css
.card {
  background: #1a1a1c;
  padding: 16px;
  border-radius: 12px;
}
```

**After:**
```css
@import '@ies/design-tokens/dist/tokens.css';

.card {
  background: var(--color-bg-secondary);
  padding: var(--space-4);
  border-radius: var(--radius-card);
}
```

### From TypeScript Constants

**Before:**
```typescript
const COLORS = {
  bgPrimary: '#0f0f10',
  entityConcept: '#3b82f6',
};
```

**After:**
```typescript
import { tokens } from '@ies/design-tokens';

const bgPrimary = tokens.color.bg.primary;
const entityConcept = tokens.color.entity.concept;
```

## Type Safety

TypeScript users get full autocomplete for token paths:

```typescript
import { tokens, type EntityType, type Spacing } from '@ies/design-tokens';

// Autocomplete for entity types
const entityType: EntityType = 'concept'; // ✓
const color = tokens.color.entity[entityType]; // "#3b82f6"

// Autocomplete for spacing
const spacing: Spacing = '4'; // ✓
const paddingValue = tokens.space[spacing]; // "1rem"
```

## Documentation

- **Full Design System**: `/docs/design/04-design-language-guide.md`
- **Entity Colors**: See `tokens/colors.json` → `color.entity`
- **Question Classes**: See `tokens/colors.json` → `color.question`
- **ADHD Features**: Energy levels, fast motion, bold colors

## Version History

- **v2.0.0** (Dec 9, 2025) - Unified design language for IES Reader + SiYuan Plugin
- **v1.0.0** (Dec 4, 2025) - Initial Reader design system (archived)

## License

MIT
