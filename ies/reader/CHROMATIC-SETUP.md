# Chromatic Visual Regression Testing Setup

## Overview

Chromatic provides visual regression testing for Storybook components. It captures snapshots of every story and compares them against baselines to detect visual changes.

## Prerequisites

- Storybook configured and running (already done)
- `@chromatic-com/storybook` addon installed (already done)
- Chromatic account and project token

## Setup Steps

### 1. Create Chromatic Account

1. Go to [chromatic.com](https://www.chromatic.com/)
2. Sign in with GitHub
3. Create a new project linked to `goodsch/brain_explore`
4. Copy the project token

### 2. Add Project Token

Store the token as a GitHub secret for CI:

```bash
# GitHub Settings → Secrets → Actions
# Add: CHROMATIC_PROJECT_TOKEN = <your-token>
```

For local testing:
```bash
export CHROMATIC_PROJECT_TOKEN=<your-token>
```

### 3. Run Chromatic Locally

```bash
cd ies/reader
npx chromatic --project-token=$CHROMATIC_PROJECT_TOKEN
```

### 4. GitHub Actions Workflow

Create `.github/workflows/chromatic.yml`:

```yaml
name: Chromatic

on:
  push:
    branches: [master]
    paths:
      - 'ies/reader/**'
  pull_request:
    branches: [master]
    paths:
      - 'ies/reader/**'

jobs:
  chromatic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for Chromatic to detect changes

      - uses: pnpm/action-setup@v2
        with:
          version: 9

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
          cache-dependency-path: 'ies/reader/pnpm-lock.yaml'

      - name: Install dependencies
        working-directory: ies/reader
        run: pnpm install

      - name: Run Chromatic
        uses: chromaui/action@latest
        with:
          projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
          workingDir: ies/reader
          buildScriptName: build-storybook
          exitZeroOnChanges: true  # Don't fail on visual changes (review in UI)
```

## Usage

### Accepting Changes

1. Push changes that modify component visuals
2. Chromatic detects visual diffs
3. Review changes in Chromatic UI
4. Accept or reject changes
5. Accepted changes become the new baseline

### TurboSnap (Recommended)

TurboSnap only snapshots stories affected by code changes:

```yaml
- name: Run Chromatic
  uses: chromaui/action@latest
  with:
    projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
    workingDir: ies/reader
    onlyChanged: true  # Enable TurboSnap
```

### Skip Chromatic for Non-Visual Changes

Add `[skip chromatic]` to commit message to skip visual testing:

```bash
git commit -m "docs: update README [skip chromatic]"
```

## Configuration

### Storybook Addon Config

The `@chromatic-com/storybook` addon is already configured in `.storybook/main.ts`.

### Story-Level Configuration

Disable Chromatic for specific stories:

```tsx
export const AnimatedComponent: Story = {
  parameters: {
    chromatic: { disableSnapshot: true },
  },
};
```

Capture at specific viewport:

```tsx
export const ResponsiveComponent: Story = {
  parameters: {
    chromatic: { viewports: [375, 768, 1440] },
  },
};
```

### Animation Handling

Chromatic waits for animations to complete. For infinite animations:

```tsx
export const LoadingSpinner: Story = {
  parameters: {
    chromatic: { pauseAnimationAtEnd: true },
  },
};
```

## Troubleshooting

### Build Fails

The static Storybook build has a known PWA issue. Chromatic may need:

```yaml
- name: Build Storybook without PWA
  working-directory: ies/reader
  run: VITE_PWA_ENABLED=false pnpm build-storybook
```

### Large Snapshots

If snapshot uploads are slow, consider:
- Using TurboSnap (`onlyChanged: true`)
- Disabling snapshots for complex/animated stories
- Reducing viewport count

## Cost Considerations

- Free tier: 5,000 snapshots/month
- TurboSnap reduces snapshot count significantly
- Consider disabling for draft PRs

## Resources

- [Chromatic Documentation](https://www.chromatic.com/docs/)
- [Storybook Visual Testing](https://storybook.js.org/docs/writing-tests/visual-testing)
- [TurboSnap](https://www.chromatic.com/docs/turbosnap)
