# IES Reader Wave 1 Enhancement Design

**Created:** 2025-12-06
**Status:** APPROVED
**Scope:** Library integration + PWA + Design system + Responsive layout

---

## Executive Summary

Transform the IES Reader from a basic prototype into a polished, installable PWA with Calibre library integration and the IES design system. This is Wave 1 of a 3-wave enhancement plan.

**Wave Overview:**
- **Wave 1 (this week):** Library + PWA + Design system
- **Wave 2 (next week):** Interactive reading (question responses, notes, entity overlay)
- **Wave 3 (after):** Exploration/synthesis features

---

## Section 1: Calibre Library Integration

**The Problem:**
Currently, users can only read sample Gutenberg books or upload local files. The backend already has Calibre APIs (`GET /books`, `GET /books/{id}/file`, `GET /books/{id}/cover`) but the reader doesn't use them.

**The Solution:**

**New Component: `LibraryBrowser.tsx`**
- Grid view of book covers from Calibre library
- Search bar (uses `GET /books?search=query`)
- Filter by "indexed" status (books with entities extracted)
- Shows entity count badge on indexed books
- Clicking a book fetches the EPUB via `GET /books/{id}/file` and opens Reader

**Data Flow:**
```
App.tsx
├── LibraryBrowser (default view)
│   ├── SearchBar
│   ├── BookGrid
│   │   └── BookCard (cover, title, author, entity count)
│   └── Pagination or infinite scroll
└── Reader (when book selected)
```

**Key API Calls:**
- `GET /books` — List all books (paginated)
- `GET /books/{id}/cover` — Book cover image
- `GET /books/{id}/file` — EPUB file (stream or download)
- `GET /graph/entities/by-calibre-id/{id}` — Entity count for badge

**State Change:**
Replace `SAMPLE_BOOKS` constant with dynamic library fetch. Book selection passes `calibreId` to Reader so entity lookup knows which book context we're in.

---

## Section 2: PWA Configuration

**The Goal:**
Make the reader installable on any device, with offline reading capability.

**Implementation: `vite-plugin-pwa`**

```typescript
// vite.config.ts additions
import { VitePWA } from 'vite-plugin-pwa'

plugins: [
  react(),
  VitePWA({
    registerType: 'autoUpdate',
    manifest: {
      name: 'IES Reader',
      short_name: 'IES Reader',
      description: 'Read with knowledge graph integration',
      theme_color: '#1a1a2e',
      background_color: '#0f0f1a',
      display: 'standalone',
      icons: [/* 192x192, 512x512 PNGs */]
    },
    workbox: {
      runtimeCaching: [
        // Cache book files for offline reading
        { urlPattern: /\/books\/\d+\/file/, handler: 'CacheFirst' },
        // Cache covers
        { urlPattern: /\/books\/\d+\/cover/, handler: 'CacheFirst' },
        // Network-first for API calls
        { urlPattern: /\/api\//, handler: 'NetworkFirst' }
      ]
    }
  })
]
```

**Offline Strategy:**
- **Book files:** Cache-first (once downloaded, always available offline)
- **Covers:** Cache-first (static assets)
- **API calls:** Network-first with fallback to cached data
- **Existing offline queue:** Already handles journey saves when offline

**Install Prompt:**
Add a subtle "Install App" button in the header that appears when `beforeinstallprompt` event fires.

---

## Section 3: IES Design System Application

**The Goal:**
Transform the hackathon-prototype look into a cohesive, polished reading experience that matches the SiYuan plugin aesthetic.

**Design System Source:**
Use the existing `docs/plans/UNIFIED-DESIGN-SYSTEM.md` specification:
- "Contemplative Knowledge Space" aesthetic
- Warm paper tones (`#f8f6f3` base, `#fffef9` surface)
- Amber accent (`#d4a574`), sage secondary (`#7a9987`)
- Entity type colors: Blue/Concept, Green/Person, Purple/Theory, Orange/Framework

**Implementation: CSS Custom Properties**

Create `src/styles/design-system.css`:
```css
:root {
  /* Colors */
  --ies-bg-deep: #f8f6f3;
  --ies-bg-surface: #fffef9;
  --ies-accent: #d4a574;
  --ies-text-primary: #2d2d2d;

  /* Typography */
  --ies-font-display: 'Crimson Pro', serif;
  --ies-font-body: 'Nunito', sans-serif;
  --ies-font-ui: 'Inter', sans-serif;

  /* Spacing (8px base) */
  --ies-space-1: 0.5rem;
  --ies-space-2: 1rem;
  --ies-space-3: 1.5rem;

  /* Shadows */
  --ies-shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --ies-shadow-md: 0 4px 6px rgba(0,0,0,0.07);
}
```

**Component Restyling:**
- **LibraryBrowser:** Card grid with warm backgrounds, subtle shadows, cover images
- **Reader toolbar:** Refined with proper spacing, icon consistency
- **FlowPanel:** Match SiYuan plugin styling (section headers, relationship badges, question cards)

**Dark Mode:**
Add `[data-theme="dark"]` overrides with inverted palette.

---

## Section 4: Responsive Layout

**The Goal:**
Work seamlessly on phone, tablet, and desktop without feeling cramped or wasteful.

**Breakpoint Strategy:**
```css
/* Mobile-first breakpoints */
--ies-bp-sm: 640px;   /* Large phones */
--ies-bp-md: 768px;   /* Tablets */
--ies-bp-lg: 1024px;  /* Desktop */
--ies-bp-xl: 1280px;  /* Wide desktop */
```

**Layout Behavior by Device:**

| Screen | Library | Reader | Flow Panel |
|--------|---------|--------|------------|
| Phone (<640px) | Single column, large touch targets | Full width, Flow as bottom sheet | Slides up from bottom |
| Tablet (768-1024px) | 2-3 column grid | Full width, Flow as side drawer | 350px slide-in drawer |
| Desktop (>1024px) | 4-5 column grid | Centered max-width, Flow pinned | 400px persistent panel |

**Key Patterns:**

- **Flow Panel on mobile:** Bottom sheet (like iOS share sheet) instead of side panel — better for one-handed use
- **Touch targets:** Minimum 44px for all interactive elements
- **Swipe gestures:** Swipe right to open Flow, swipe left to close
- **Reader width:** Max 720px content width on desktop for comfortable reading

**Implementation:**
Use CSS Grid + Container Queries where possible. Zustand store tracks viewport size for conditional rendering (bottom sheet vs side panel).

---

## Section 5: File Structure & Implementation Plan

**New/Modified Files:**

```
ies/reader/src/
├── styles/
│   └── design-system.css          # NEW: CSS custom properties
├── components/
│   ├── library/
│   │   ├── LibraryBrowser.tsx     # NEW: Main library grid
│   │   ├── BookCard.tsx           # NEW: Cover + metadata card
│   │   ├── SearchBar.tsx          # NEW: Search input
│   │   └── LibraryBrowser.css     # NEW: Library styles
│   ├── Reader.tsx                 # MODIFY: Accept calibreId, restyle
│   ├── Reader.css                 # MODIFY: Design system tokens
│   └── flow/
│       ├── FlowPanel.tsx          # MODIFY: Restyle, responsive
│       └── FlowPanel.css          # MODIFY: Design system tokens
├── App.tsx                        # MODIFY: Route between Library/Reader
├── App.css                        # MODIFY: Design system tokens
└── index.css                      # MODIFY: Import design-system.css
vite.config.ts                     # MODIFY: Add vite-plugin-pwa
public/
├── icons/                         # NEW: PWA icons (192, 512)
└── manifest additions via plugin
```

**Implementation Order:**

1. **Design system first** — Create CSS file, import globally, verify tokens work
2. **PWA config** — Add plugin, generate manifest, test install prompt
3. **LibraryBrowser** — Build component, wire to backend APIs
4. **Restyle existing** — Apply tokens to Reader, FlowPanel, App
5. **Responsive** — Add breakpoints, bottom sheet for mobile Flow
6. **Polish** — Loading states, error handling, transitions

---

## Dependencies to Add

```json
{
  "devDependencies": {
    "vite-plugin-pwa": "^0.17.0"
  }
}
```

Fonts (via Google Fonts or self-hosted):
- Crimson Pro (display)
- Nunito (body)
- Inter (UI)

---

## Success Criteria

- [ ] Can browse Calibre library and open any book
- [ ] App installable as PWA on iOS, Android, desktop
- [ ] Offline reading works for previously opened books
- [ ] UI matches IES design system aesthetic
- [ ] Works well on phone, tablet, and desktop
- [ ] Flow panel adapts to screen size (bottom sheet on mobile)

---

## Future Waves (Out of Scope)

**Wave 2: Interactive Reading**
- Question response capture
- Entity overlay highlighting
- Reading notes/annotations
- Journey breadcrumb visualization

**Wave 3: Exploration/Synthesis**
- Spark-based initiation
- Multi-phase exploration (orientation → branching → deepening → synthesis)
- Synthesis artifact generation
- Visual views (map, timeline)
