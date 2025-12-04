# IES Explorer Visual & Interaction Overview

## Dashboard Hub
- **Branding:** Top header with concentric logo, label “IES Explorer” and version badge (`v0.3.1` in code).  
- **Status row:** Stats bar shows totals for entities, relationships, sources inside elevated pill cards with accent text and divider lines, gracefully handled loading/error dialogs.  
- **Mode cards:** Three big buttons for Think (structured dialogue), Explore (knowledge navigation), Capture (quick notes). Each card has a subtle glow, icon, hover lift, and descriptive subtitle.  
- **Recents & queues:** Recent exploration cards show step counts, timestamps, and resume journeys into Flow. Capture queue chips and concept suggestion chips (Most Connected & Novel Concepts) act as entry points as well.  
- **Transitions:** Dashboard fades in with translate/opacity animation when data loads.

## Flow Mode (Graph Exploration)
- **Header & controls:** Back button, “Flow” title, and inline “Clear” action when a journey exists.  
- **Search:** Text input with embedded search icon, inline clear button, and “Explore” CTA that handles async loading (spinner) and strikes out when no query.  
- **Search results:** Vertical list of concept cards with type-colored indicators, animated entry, and type badge.  
- **Core panel:** Once a concept is selected, central badge states `Exploring {concept}` with pulsing glow, connection count, and tabs for “Connections” and “Reframes.”  
- **Connections view:** Grouped relationship sections show relational direction (→/←), counts, and chips for each connected node (hover accent, type color). Clicking a chip loads that node and extends the path trail.  
- **Path trail:** Breadcrumb pills show exploration history; selecting a step rewinds position.  
- **Thinking Partner:** Button requests AI question; busy state text “Contemplating...” replaced by card with icon + generated question.
- **Reframes component:** Lists metaphors/analogies with type badges, timestamp, and up/down feedback buttons; “Generate Reframe” button requests new items.

## Forge Mode (Structured Thinking)
- **Setup state:** Mode selection cards for Learning, Articulating, Planning, Ideating, Reflecting, each with emoji icon and descriptive text. Topic textarea plus a primary “Start {mode} Session” button that only enables when text is entered.  
- **Active session:** Conversation pane shows chat bubbles; user messages and assistant responses alternate with simple styling. Input textarea supports Enter-to-send (no shift) and two buttons (Send/End).  
- **Note preview:** Toggleable markdown summary pane displays key insights derived from assistant replies, rendered live beside the conversation when a session is active.  
- **Statuses:** Starting spinner text, error banner with retry action, and notifications when ending a session (entity extraction count).  
- **Accent tokens:** Uses SiYuan theme variables (`--b3-theme-*`) for consistent colors and backgrounds.

## Quick Capture
- **Header:** Back button plus title “Quick Capture.”  
- **Input phase:** Toggle between Text and Link capture types, textarea placeholder updates, “Process” button triggers AI extraction with busy label and disables when empty. Errors display in an inline alert.  
- **Results phase:** Shows AI summary, list of extracted entities (graph match badges with checkmarks), suggested tags, and “Route To” cards ranking placement destinations by confidence. Each card shows icon, target name, action, and confidence percentage. Selecting one toasts the routing info and resets capture.  
- **Assistance copy:** Footer text explains the routing action of the AI.

## Theming & Motion
- **Typography:** Combines serif (`Crimson Pro`) for titles with sans system UI (`Nunito`) for body text, plus JetBrains Mono for version badges.  
- **Color palette:** Light tokens (sepia base, warm accent, muted secondary/tertiary) with a dedicated dark-theme override toggle via `[data-theme-mode="dark"]`.  
- **Micro-interactions:** Hover lifts, glows, slide/fade animations, rotating spinners, and pulsing concept centers script subtle lifelike motion.  
- **Visual language:** Rounded cards, chip grids, subtle borders/shadows, and accent-themed badges keep the experience cohesive across views.
