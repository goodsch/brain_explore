# Readest Calibre Library View

**Date:** 2025-12-04
**Status:** Approved
**Phase:** 2c (Calibre Integration Phase 4)

## Overview

Add Calibre library browsing to Readest, enabling users to discover and open books directly from their Calibre catalog with entity overlay integration.

## User Flow

1. User clicks Import menu in library header
2. Selects "From Calibre Library" option
3. Modal opens showing Calibre book catalog
4. User searches or filters by "Has entities"
5. User clicks a book → opens immediately in reader
6. Book silently added to Readest library with `calibre_id`
7. Entity overlay works automatically (uses `calibre_id` for lookup)

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Integration approach | New source (like OPDS) | Least disruptive, works with existing library |
| Access point | Import menu item | Follows existing Readest UX patterns |
| Book display | Cover + title + entity badge | Guides users to knowledge-rich books |
| Selection behavior | Open directly, silent add | Reduces friction, user wants to read |
| Filtering | Search + "Has entities" toggle | Covers key use cases without complexity |

## UI Design

```
┌─────────────────────────────────────────────────────────┐
│  Calibre Library                                    ✕   │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────┐  ☑ Has entities only      │
│  │ 🔍 Search books...      │                           │
│  └─────────────────────────┘                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐               │
│  │      │  │      │  │      │  │      │               │
│  │ cover│  │ cover│  │ cover│  │ cover│               │
│  │      │  │      │  │      │  │      │               │
│  └──────┘  └──────┘  └──────┘  └──────┘               │
│  ADHD 2.0   Driven    Taking    Scattered             │
│  Hallowell  to Dis... Charge..  Minds                 │
│  ●142       ●89       ●203      Not indexed           │
│                                                         │
│  (... scrollable grid of books ...)                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Elements:**
- Header with title and close button
- Search input (debounced, 300ms)
- "Has entities only" checkbox filter
- Responsive grid of book cards (4 cols desktop, 2 cols mobile)
- Each card: cover image, title (truncated), author, entity badge
- Entity badge: green dot + count, or gray "Not indexed"
- Click anywhere on card → open book in reader

**Loading States:**
- Skeleton cards while fetching catalog
- Spinner on cover images until loaded
- "No books found" empty state for search

## Data Model

```typescript
interface CalibreDialogState {
  books: CalibreBook[];           // Full catalog from API
  filteredBooks: CalibreBook[];   // After search/filter applied
  entityCounts: Map<number, number>; // calibre_id → entity count
  searchQuery: string;
  hasEntitiesOnly: boolean;
  isLoading: boolean;
  error: string | null;
}

interface CalibreBook {
  calibre_id: number;
  title: string;
  author: string;
  path: string;                   // Calibre file path
}
```

## Data Flow

1. **On modal open:** Fetch full catalog (`GET /books?limit=500`)
2. **Entity counts:** Individual calls per visible book, cached in state
3. **Search:** Client-side filtering (catalog is ~179 books)
4. **Cover images:** Lazy-loaded as `<img src="/books/{id}/cover">`

**Opening a Book:**
1. User clicks book card
2. Create Readest `Book` object with `calibreId` field
3. Call `appService.importBook()` with Calibre file path
4. Navigate to reader with book hash
5. Modal closes automatically

## File Changes

### New Files

```
readest/apps/readest-app/src/app/library/components/
├── CalibreDialog.tsx        # Main modal component (~200 lines)
├── CalibreBookCard.tsx      # Individual book card (~80 lines)
└── CalibreSearchBar.tsx     # Search + filter controls (~50 lines)
```

### Modified Files

| File | Change |
|------|--------|
| `ImportMenu.tsx` | Add "From Calibre Library" menu item |
| `LibraryHeader.tsx` | Wire up Calibre dialog trigger |
| `page.tsx` (library) | Add dialog state and render |
| `@/types/book.ts` | Add `calibreId?: number` to Book interface |
| `flowModeStore.ts` | Use calibreId for entity fetching |

## Backend APIs (Already Built)

- `GET /books` — List all Calibre books
- `GET /books?search=query` — Search by title/author
- `GET /books/{calibre_id}/cover` — Fetch cover image
- `GET /graph/entities/by-calibre-id/{calibre_id}` — Entity count/lookup

## Implementation Order

1. Add `calibreId` to Book type
2. Create CalibreBookCard component
3. Create CalibreSearchBar component
4. Create CalibreDialog component
5. Wire into Import menu
6. Update flowModeStore for calibreId

## Success Criteria

- [ ] User can open Calibre browser from Import menu
- [ ] Books display with covers and entity count badges
- [ ] Search filters books by title/author
- [ ] "Has entities" filter shows only indexed books
- [ ] Clicking book opens it in reader
- [ ] Entity overlay works using calibreId
- [ ] Works on desktop and mobile layouts
