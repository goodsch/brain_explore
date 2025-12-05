# IES Explorer UI Overview

This document introduces the **IES Explorer** plugin UI so a UI/UX designer can understand its structure, states, and interaction expectations before sketching or refreshing visual treatments. The plugin lives inside SiYuan but renders a self-contained single-page experience built with Svelte/Vite; it runs either in the custom dock (sidebar) or in a standalone tab (`src/index.ts`:1-80).

## Entry points & layout

- **Primary containers**: the plugin registers two hosts in `src/index.ts:1-80`: a dock at the bottom-right and a tab that both mount the root `Dashboard` component. Designers should plan for a 100% height container with vertical stacking, so dashboards, chat views, and graphs can fill the full dock or tab area.
- **Thematic anchor**: the UI borrows SiYuan’s `b3` theme classes and `var(--b3-*)` tokens for colors, borders, shadows, and typography (`src/index.scss`:1-60). Matching these tokens keeps the plugin visually cohesive with the surrounding app while still allowing custom gradients or highlights.

## Dashboard (landing hub)

Filling the root container is `src/views/Dashboard.svelte:1-220`, which orchestrates:

- A header with the plugin title and version badge.
- A **stat row** (Entities / Relationships / Books) that shows aggregate counts from `/graph/stats`. Use a centered, card-like layout with bold numeric values (statistic highlight) and smaller uppercase labels.
- **Mode buttons** (Forge vs Flow). These pill cards have icon, title, and short descriptor, plus hover states that shift border colors to reinforce their interactivity. Each mode fills equal horizontal space (`src/views/Dashboard.svelte:80-180`).
- **Suggestions section**: chips grouped into “Most Connected” and “Novel Concepts”. Chips invoke Flow mode when clicked. Designers should treat them as chip-style filters with hover and focused states (`src/views/Dashboard.svelte:180-240`).
- Loading / error states: the dashboard shows a centered loading text or a retry block with a button when the data requests fail (`src/views/Dashboard.svelte:40-90`).

## Forge mode (Socratic dialogue)

Forge is the AI-guided chat interface (`src/views/ForgeMode.svelte:1-220`). Key UI patterns:

- Top navigation bar: back button, mode title (“Forge”), and an “Active” badge shown whenever a session is live.
- **Control strip** (`src/components/SessionControls.svelte:1-200`): shows the Start/End buttons, status indicators (idle, starting, active, ending, error), session timer, capacity indicator, and extraction summary. Buttons use SiYuan’s `.b3-button` styles and change color in different states.
- **Message surface**: scrollable list where assistant/user messages stack vertically; user bubbles are indented, and assistant bubbles use neutral cards. When no messages yet, a welcome note motivates starting a session.
- **Input area**: textarea plus send button, disabled during loading. Enter without Shift sends; Shift+Enter keeps writing. Input sits below the message list with a top border and consistent padding.
- **Feedback**: `showMessage` toasts appear on backend errors (e.g., start/chat/end failures), but the UI itself also switches to error messages inside the control strip so the user can retry.

The session is backed by `src/stores/ies-session.ts:1-80`, so designers should respect five states (idle, starting, active, ending, ended/error) when proposing animations or microcopy.

## Flow mode (graph exploration)

Flow (`src/views/FlowMode.svelte:1-200`) lets users navigate knowledge concepts:

- Header: back button, title, and “Clear” action once a path is active.
- Search bar + button at the top, with small loading state (button label toggles to `...` while searching).
- **Search results list**: each entry shows name + type badge; type affects a subtle left border color (theory/researcher/concept).
- **Centered concept**: when a topic is active, a highlighted chip sits in the middle with connected groups below.
- **Grouped relationships**: cards grouped by relationship type display direction arrows, labels, and a wrapped collection of buttons for neighboring nodes (the buttons adopt subtle accent borders per type). Clicking any node navigates to it and adds it to the exploration path.
- **Exploration path breadcrumbs**: horizontal row of steps with arrows; clicking a previous step re-centers the view.
- **Thinking Partner**: a call-to-action button triggers `/graph/thinking-partner` and renders a highlighted question card beneath it.

## Shared Messaging UI & Input (sidebar)

The plugin also exposes a docked sidebar version of the Forge chat, defined in `src/ies-sidebar.svelte:1-220`. Key UX notes:

- **Session controls** sit at the top via `<SessionControls>` and mimic Forge’s states.
- **Message area**: auto-scrolls when messages are appended; includes placeholder illustration/text before the first session. User/assistant avatars are simple circle icons with color-coded backgrounds.
- **Streaming indicator**: while response streaming occurs, the newest assistant bubble shows a blinking cursor (`▊`); designers can mirror this with a subtle animated caret.
- **Input textarea** auto-resizes up to 150px and has disabled styling when the session isn’t active; send/stop buttons toggle depending on whether there is an ongoing stream. Keyboard handling specifically treats Enter (submit) vs Shift+Enter (newline).
- **Responsive tweaks**: mobile detection increases spacing, font sizes, and button dimensions; `@media (pointer: coarse)` styles enlarge tappable areas, and very small screens shrink avatar sizes. Designers should account for docked mobile width (~300px) vs desktop.

## Backend integration cues

The experience relies on a FastAPI backend (`ies-chat.ts:1-160`) running at `http://<host>:8081`. Designers should expect these calls:

1. `GET /graph/stats` & `/graph/suggestions` (dashboard metrics + chips)
2. `GET /graph/search` (Flow search)
3. `GET /graph/explore/<concept>` (neighbors + relationships)
4. `POST /graph/thinking-partner` (reflective question)
5. `POST /session/start`, `/session/chat`, `/session/end` (Forge chat lifecycle)

Avoid creating interactions that rely on instant backend responses—there is already retry UI for load failures, and Send buttons are disabled during streaming. The `chat` call streams SSE chunks, so the UI should show a streaming cue until `onComplete` fires.

## Design guidance

- Use existing SiYuan variables (`var(--b3-theme-*)`, `var(--b3-border-color)`) for colors so the plugin inherits the current theme (light/dark). Custom accents (for modes, badges, chips) should still be legible on both themes.
- Keep the layout vertically stacked with clear separation between controls, content, and inputs; maximum width in dock/tab is ~420px, so avoid sprawling grids.
- Prioritize clarity of state (idle/loading/active/error) through microcopy + color while keeping animations subtle. Both Forge and Flow lean on button-driven actions, so emphasize affordances (raised buttons, hover outlines).
- For Flow, think of concept cards as node cards with directional group headings; allow them to wrap gracefully on narrow widths and keep path breadcrumbs touch-friendly.

If you need mock data or want to prototype interactions, the existing Svelte components can be run in `npm run dev` and rely on `vite`’s HMR, but no additional assets are required: everything compiles down to the single `Dashboard` entry.
