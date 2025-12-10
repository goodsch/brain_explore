# IES Reader Storybook

Storybook configuration for the IES Reader component library.

## Overview

This Storybook instance showcases components from the IES Design System v2, including:
- Interactive UI components
- Error handling boundaries
- Design system tokens and patterns

## Configuration

### Addons

- **@storybook/addon-a11y** - Accessibility testing and validation
- **@storybook/addon-docs** - Automatic documentation generation
- **@storybook/addon-interactions** - Component interaction testing
- **@chromatic-com/storybook** - Visual regression testing
- **@storybook/addon-vitest** - Vitest integration

### Theme

Default theme is set to **dark mode** matching the IES Design System v2:
- Background: `#0f0f10` (--bg-primary)
- Text: `#f5f5f5` (--text-primary)
- Glassmorphic UI elements

### Viewports

Pre-configured responsive viewports:
- **Mobile**: 375x667px
- **Tablet**: 768x1024px
- **Desktop**: 1440x900px (default)
- **Desktop Wide**: 1920x1080px

## Usage

### Development

```bash
# Start Storybook dev server on port 6006
pnpm storybook
```

### Build

```bash
# Build static Storybook for deployment
pnpm build-storybook
```

The output will be in `storybook-static/` directory.

## Creating Stories

### Basic Story Structure

```tsx
import type { Meta, StoryObj } from '@storybook/react';
import { YourComponent } from './YourComponent';

const meta = {
  title: 'Components/YourComponent',
  component: YourComponent,
  parameters: {
    layout: 'centered', // or 'fullscreen', 'padded'
  },
  tags: ['autodocs'],
  argTypes: {
    // Define controls for component props
  },
} satisfies Meta<typeof YourComponent>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    // Default prop values
  },
};
```

### With Interactions

```tsx
import { fn } from '@storybook/test';

export const WithClick: Story = {
  args: {
    onClick: fn(),
  },
};
```

## Design System Integration

All stories automatically load the IES Design System CSS via `preview.ts`:
- `/src/index.css` (global styles)
- `/src/styles/design-system.css` (CSS custom properties)

Components use CSS custom properties from the design system:
- `var(--bg-primary)`, `var(--bg-secondary)`, etc.
- `var(--text-primary)`, `var(--text-secondary)`, etc.
- `var(--space-*)` for spacing
- `var(--radius-*)` for border radius
- `var(--glass-*)` for glassmorphic effects

## Accessibility Testing

The a11y addon runs automatically on all stories. Check the "Accessibility" tab in Storybook to view:
- WCAG violations
- Color contrast issues
- Keyboard navigation problems
- ARIA attribute validation

## File Structure

```
.storybook/
├── main.ts              # Storybook configuration
├── preview.ts           # Global decorators and parameters
├── vitest.setup.ts      # Vitest integration setup
└── README.md            # This file

src/
└── components/
    ├── Button.tsx
    ├── Button.css
    ├── Button.stories.tsx
    ├── ErrorBoundary.tsx
    ├── ErrorBoundary.css
    └── ErrorBoundary.stories.tsx
```

## Resources

- [Storybook Documentation](https://storybook.js.org/docs)
- [IES Design System Documentation](../docs/design/)
- [Accessibility Guidelines](https://storybook.js.org/docs/writing-tests/accessibility-testing)
