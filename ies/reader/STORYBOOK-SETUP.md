# Storybook Setup for IES Reader

## Installation Summary

Storybook 10.1.5 has been successfully configured for the IES Reader project.

## Configuration Files

### Main Configuration (.storybook/main.ts)
- Framework: `@storybook/react-vite`
- Stories location: `../src/**/*.stories.@(js|jsx|mjs|ts|tsx)`
- Autodocs enabled

### Addons Installed
1. **@storybook/addon-a11y** (v10.1.5) - Accessibility testing
2. **@storybook/addon-docs** (v10.1.5) - Documentation generation
3. **@storybook/addon-interactions** (v8.6.14) - Component interaction testing
4. **@storybook/addon-vitest** (v10.1.5) - Vitest integration
5. **@chromatic-com/storybook** (v4.1.3) - Visual regression testing

### Preview Configuration (.storybook/preview.ts)
- Global CSS: Imports `../src/index.css` (includes design system)
- Default theme: Dark mode (`#0f0f10`)
- Viewports: Mobile (375px), Tablet (768px), Desktop (1440px), Desktop Wide (1920px)
- Accessibility testing: Set to 'todo' mode

## Components with Stories

### 1. Button Component
Location: `/home/chris/dev/projects/codex/brain_explore/ies/reader/src/components/Button.tsx`

**Features:**
- 4 variants: primary, secondary, ghost, danger
- 3 sizes: sm, md, lg
- Loading state with spinner
- Disabled state
- Full TypeScript support

**Stories:**
- Primary, Secondary, Ghost, Danger
- Small, Medium, Large
- Loading, Disabled
- AllVariants, AllSizes showcase

### 2. ErrorBoundary Component
Location: `/home/chris/dev/projects/codex/brain_explore/ies/reader/src/components/ErrorBoundary.tsx`

**Features:**
- React error boundary implementation
- Graceful fallback UI
- Error details display (collapsible)
- Reset mechanism
- Custom error messages

**Stories:**
- Default (interactive error trigger)
- CustomMessage
- ErrorState (visual testing)
- NestedBoundaries

## Running Storybook

### Development Server
```bash
cd /home/chris/dev/projects/codex/brain_explore/ies/reader
pnpm storybook
```

Access at: http://localhost:6006/

### Build Static Storybook
```bash
pnpm build-storybook
```

**Note:** The static build currently fails during the service worker generation step due to a vite-plugin-pwa compatibility issue with large Storybook manager files (3.15 MB exceeds 2 MB default limit). This is a known issue and doesn't affect:
- Development mode (works perfectly)
- Component stories (all functional)
- Accessibility testing
- Documentation generation

The vite.config.ts has been updated to set `maximumFileSizeToCacheInBytes: 4MB`, but this setting doesn't apply to the Storybook manager build. A workaround would be to disable PWA specifically for Storybook builds or accept that static builds will only be used for the dev server.

## Design System Integration

All components automatically load the IES Design System v2 CSS variables:

### Colors
- `--bg-primary`, `--bg-secondary`, `--bg-tertiary` - Background colors
- `--text-primary`, `--text-secondary`, `--text-tertiary` - Text colors
- `--accent`, `--accent-hover` - Accent colors
- `--error`, `--error-bg`, `--error-fg` - Error states
- Entity colors (concept, person, theory, etc.)

### Spacing
- `--space-1` through `--space-6` - Consistent spacing scale

### Other Tokens
- `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-full` - Border radius
- `--glass-bg`, `--glass-blur`, `--glass-border` - Glassmorphic effects
- `--duration-fast`, `--ease-out` - Animation timings

## Next Steps

1. **Add more component stories:**
   - FlowPanel
   - Reader controls
   - Entity cards
   - Modal dialogs

2. **Set up Chromatic for visual regression testing:**
   ```bash
   npx chromatic --project-token=<token>
   ```

3. **Enable interaction testing:**
   Add interaction tests to existing stories using `@storybook/test`

4. **Create MDX documentation:**
   Write design system documentation pages in `.mdx` format

5. **Fix static build issue:**
   - Either disable PWA for Storybook builds
   - Or configure separate build pipeline
   - Or accept dev-only Storybook workflow

## Known Issues

1. **Version Mismatch Warning:**
   - `@storybook/addon-interactions@8.6.14` vs Storybook 10.1.5
   - `@storybook/test@8.6.14` vs Storybook 10.1.5
   - These packages don't have 10.x versions yet but work with minor warnings

2. **Static Build Fails:**
   - PWA service worker generation fails due to large manager file
   - Development mode unaffected
   - Workaround: Use `pnpm storybook` for development/demo

3. **Addon Order Warning:**
   - Missing `@storybook/addon-actions` or `@storybook/addon-essentials`
   - Non-blocking, interactions still work

## File Structure

```
/home/chris/dev/projects/codex/brain_explore/ies/reader/
├── .storybook/
│   ├── main.ts              # Storybook configuration
│   ├── preview.ts           # Global decorators and parameters
│   ├── vitest.setup.ts      # Vitest integration
│   └── README.md            # Storybook documentation
├── src/
│   ├── components/
│   │   ├── Button.tsx
│   │   ├── Button.css
│   │   ├── Button.stories.tsx
│   │   ├── ErrorBoundary.tsx
│   │   ├── ErrorBoundary.css
│   │   └── ErrorBoundary.stories.tsx
│   ├── styles/
│   │   └── design-system.css
│   └── index.css            # Global styles (imported in preview.ts)
└── package.json             # Scripts: storybook, build-storybook
```

## Resources

- [Storybook Documentation](https://storybook.js.org/docs)
- [Storybook React-Vite](https://storybook.js.org/docs/get-started/frameworks/react-vite)
- [Accessibility Testing](https://storybook.js.org/docs/writing-tests/accessibility-testing)
- [Interaction Testing](https://storybook.js.org/docs/writing-tests/interaction-testing)
