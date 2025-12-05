# Entity Overlay Flow Mode Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enable auto-annotated entity highlighting in book text with type-based filtering, allowing users to see and interact with knowledge graph entities directly while reading.

**Architecture:** A content transformer injects styled `<span>` elements around known entity text in the epub HTML. The backend provides entities by book hash. The frontend manages filter state and handles entity clicks to show connections in the sidebar.

**Tech Stack:** FastAPI (backend), React/TypeScript (Readest), Neo4j (graph database), TailwindCSS/DaisyUI (styling)

---

## Overview

### Current Flow
1. User manually selects text
2. Frontend searches for matching entity
3. Sidebar shows entity details

### New Flow (Entity Overlay)
1. Book loads → fetch entities for this book from backend
2. Entity transformer wraps known entity names in styled spans
3. User sees entities highlighted by type (concept=blue, person=green, etc.)
4. User toggles which entity types are visible
5. User clicks entity → sidebar shows connections
6. No manual text selection required

---

## Task 1: Backend API - Get Entities by Book

**Files:**
- Create: `ies/backend/src/ies_backend/api/book_entities.py`
- Modify: `ies/backend/src/ies_backend/main.py:25-35` (add router)
- Modify: `ies/backend/src/ies_backend/services/graph_service.py` (add method)
- Create: `ies/backend/tests/test_book_entities.py`

### Step 1: Write the failing test

```python
# ies/backend/tests/test_book_entities.py
"""Tests for book entities API."""

import pytest
from unittest.mock import patch, AsyncMock


class TestGetBookEntities:
    """Tests for GET /graph/entities/by-book/{book_hash}."""

    @pytest.mark.asyncio
    async def test_returns_entities_for_valid_book(self):
        """Should return entities mentioned in the book."""
        from ies_backend.services.graph_service import GraphService

        mock_entities = [
            {"name": "Executive Function", "type": "Concept", "mention_count": 15},
            {"name": "Russell Barkley", "type": "Person", "mention_count": 8},
        ]

        with patch.object(
            GraphService,
            "get_entities_by_book",
            new_callable=AsyncMock,
            return_value=mock_entities
        ):
            result = await GraphService.get_entities_by_book("abc123hash")
            assert len(result) == 2
            assert result[0]["name"] == "Executive Function"
            assert result[0]["type"] == "Concept"

    @pytest.mark.asyncio
    async def test_returns_empty_for_unknown_book(self):
        """Should return empty list for book not in graph."""
        from ies_backend.services.graph_service import GraphService

        with patch.object(
            GraphService,
            "get_entities_by_book",
            new_callable=AsyncMock,
            return_value=[]
        ):
            result = await GraphService.get_entities_by_book("nonexistent")
            assert result == []

    @pytest.mark.asyncio
    async def test_filters_by_entity_type(self):
        """Should filter results by entity type when specified."""
        from ies_backend.services.graph_service import GraphService

        mock_entities = [
            {"name": "Executive Function", "type": "Concept", "mention_count": 15},
        ]

        with patch.object(
            GraphService,
            "get_entities_by_book",
            new_callable=AsyncMock,
            return_value=mock_entities
        ):
            result = await GraphService.get_entities_by_book("abc123", types=["Concept"])
            assert len(result) == 1
            assert result[0]["type"] == "Concept"
```

### Step 2: Run test to verify it fails

```bash
cd ies/backend && uv run pytest tests/test_book_entities.py -v
```

Expected: FAIL with "get_entities_by_book not found"

### Step 3: Add GraphService method

```python
# Add to ies/backend/src/ies_backend/services/graph_service.py

    @staticmethod
    async def get_entities_by_book(
        book_hash: str,
        types: list[str] | None = None,
        limit: int = 500
    ) -> list[dict]:
        """Get all entities mentioned in a book.

        Args:
            book_hash: The book's file hash (used as identifier)
            types: Optional list of entity types to filter by
            limit: Maximum entities to return

        Returns:
            List of entities with name, type, and mention_count
        """
        # Build type filter clause
        type_filter = ""
        if types:
            type_labels = " OR ".join([f"e:{t}" for t in types])
            type_filter = f"AND ({type_labels})"

        query = f"""
        MATCH (b:Book {{hash: $book_hash}})<-[:FROM_BOOK]-(c:Chunk)-[:MENTIONS]->(e)
        WHERE e.name IS NOT NULL {type_filter}
        WITH e, count(c) as mention_count
        RETURN DISTINCT e.name as name, labels(e)[0] as type, mention_count
        ORDER BY mention_count DESC
        LIMIT $limit
        """

        try:
            results = await Neo4jClient.execute_query(
                query, {"book_hash": book_hash, "limit": limit}
            )
            return [
                {
                    "name": r["name"],
                    "type": r["type"] or "Concept",
                    "mention_count": r["mention_count"],
                }
                for r in results
            ]
        except Exception:
            return []
```

### Step 4: Run test to verify it passes

```bash
cd ies/backend && uv run pytest tests/test_book_entities.py -v
```

Expected: PASS

### Step 5: Create API router

```python
# ies/backend/src/ies_backend/api/book_entities.py
"""Book entities API router for entity overlay feature.

Provides endpoint to get all entities mentioned in a specific book.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ies_backend.services.graph_service import GraphService


class BookEntity(BaseModel):
    """An entity mentioned in a book."""
    name: str
    type: str
    mention_count: int


class BookEntitiesResponse(BaseModel):
    """Response for book entities endpoint."""
    book_hash: str
    entities: list[BookEntity]
    total: int


router = APIRouter()


@router.get("/entities/by-book/{book_hash}", response_model=BookEntitiesResponse)
async def get_book_entities(
    book_hash: str,
    types: list[str] | None = Query(default=None, description="Filter by entity types"),
    limit: int = Query(default=500, ge=1, le=1000, description="Maximum entities"),
) -> BookEntitiesResponse:
    """Get all entities mentioned in a book.

    Use this to populate entity overlay highlighting in the reader.
    Returns entities sorted by mention frequency.
    """
    entities = await GraphService.get_entities_by_book(
        book_hash, types=types, limit=limit
    )

    return BookEntitiesResponse(
        book_hash=book_hash,
        entities=[BookEntity(**e) for e in entities],
        total=len(entities),
    )
```

### Step 6: Register router in main.py

```python
# Add import at top of ies/backend/src/ies_backend/main.py
from ies_backend.api.book_entities import router as book_entities_router

# Add in the router registration section (around line 30)
app.include_router(book_entities_router, prefix="/graph", tags=["graph"])
```

### Step 7: Run full test suite

```bash
cd ies/backend && uv run pytest -v
```

Expected: All tests pass

### Step 8: Commit

```bash
git add ies/backend/src/ies_backend/api/book_entities.py \
        ies/backend/src/ies_backend/services/graph_service.py \
        ies/backend/src/ies_backend/main.py \
        ies/backend/tests/test_book_entities.py
git commit -m "feat(backend): Add GET /graph/entities/by-book endpoint for entity overlay"
```

---

## Task 2: Frontend - Entity Transformer

**Files:**
- Create: `.worktrees/readest/readest/apps/readest-app/src/services/transformers/entity.ts`
- Modify: `.worktrees/readest/readest/apps/readest-app/src/services/transformers/index.ts`
- Modify: `.worktrees/readest/readest/apps/readest-app/src/services/transformers/types.ts`

### Step 1: Extend TransformContext type

```typescript
// Add to .worktrees/readest/readest/apps/readest-app/src/services/transformers/types.ts

export type EntityOverlay = {
  name: string;
  type: string; // Concept, Person, Theory, Assessment
  mentionCount: number;
};

export type TransformContext = {
  bookKey: string;
  viewSettings: ViewSettings;
  userLocale: string;
  primaryLanguage?: string;
  width?: number;
  height?: number;
  content: string;
  transformers: string[];
  reversePunctuationTransform?: boolean;
  // New: entity overlay data
  entityOverlay?: {
    enabled: boolean;
    entities: EntityOverlay[];
    visibleTypes: string[];
  };
};
```

### Step 2: Create entity transformer

```typescript
// .worktrees/readest/readest/apps/readest-app/src/services/transformers/entity.ts
/**
 * Entity transformer for overlay flow mode.
 *
 * Wraps known entity names in styled <span> elements for highlighting
 * and interaction in the reader view.
 */

import type { Transformer, TransformContext, EntityOverlay } from './types';

const ENTITY_TYPE_CLASSES: Record<string, string> = {
  Concept: 'entity-concept',
  Person: 'entity-person',
  Theory: 'entity-theory',
  Framework: 'entity-framework',
  Assessment: 'entity-assessment',
  Model: 'entity-theory',
  Researcher: 'entity-person',
};

/**
 * Escape special regex characters in entity name.
 */
function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Build regex pattern for entity matching.
 * Matches whole words only, case-insensitive.
 */
function buildEntityPattern(entities: EntityOverlay[]): RegExp | null {
  if (entities.length === 0) return null;

  // Sort by length descending to match longer phrases first
  const sorted = [...entities].sort((a, b) => b.name.length - a.name.length);

  const patterns = sorted.map(e => escapeRegex(e.name));
  // Word boundary matching, case-insensitive
  return new RegExp(`\\b(${patterns.join('|')})\\b`, 'gi');
}

/**
 * Create entity name to data lookup map.
 */
function buildEntityMap(entities: EntityOverlay[]): Map<string, EntityOverlay> {
  const map = new Map<string, EntityOverlay>();
  for (const entity of entities) {
    map.set(entity.name.toLowerCase(), entity);
  }
  return map;
}

/**
 * Transform HTML content to wrap entity mentions in styled spans.
 */
export const entityTransformer: Transformer = {
  name: 'entity',

  transform: async (ctx: TransformContext): Promise<string> => {
    const { entityOverlay, content } = ctx;

    // Skip if not enabled or no entities
    if (!entityOverlay?.enabled || !entityOverlay.entities?.length) {
      return content;
    }

    // Filter to visible types only
    const visibleEntities = entityOverlay.entities.filter(
      e => entityOverlay.visibleTypes.includes(e.type)
    );

    if (visibleEntities.length === 0) {
      return content;
    }

    const pattern = buildEntityPattern(visibleEntities);
    if (!pattern) return content;

    const entityMap = buildEntityMap(visibleEntities);

    // Parse HTML and process text nodes only (avoid matching in tags/attributes)
    // Simple approach: split on HTML tags, process text parts
    const parts = content.split(/(<[^>]+>)/);

    const transformed = parts.map(part => {
      // Skip HTML tags
      if (part.startsWith('<')) return part;

      // Replace entity mentions in text
      return part.replace(pattern, (match) => {
        const entity = entityMap.get(match.toLowerCase());
        if (!entity) return match;

        const typeClass = ENTITY_TYPE_CLASSES[entity.type] || 'entity-default';

        return `<span class="entity-link ${typeClass}" data-entity-name="${entity.name}" data-entity-type="${entity.type}">${match}</span>`;
      });
    });

    return transformed.join('');
  },
};
```

### Step 3: Register transformer

```typescript
// Add to .worktrees/readest/readest/apps/readest-app/src/services/transformers/index.ts

import { entityTransformer } from './entity';

export const availableTransformers: Transformer[] = [
  punctuationTransformer,
  footnoteTransformer,
  languageTransformer,
  styleTransformer,
  whitespaceTransformer,
  sanitizerTransformer,
  simpleccTransformer,
  entityTransformer, // Add entity transformer
];
```

### Step 4: Add entity CSS styles

```css
/* Add to appropriate CSS file or inject via transformer */
/* These styles will be injected into the epub iframe */

.entity-link {
  cursor: pointer;
  border-bottom: 2px dotted;
  border-radius: 2px;
  padding: 0 2px;
  transition: all 0.2s ease;
}

.entity-link:hover {
  border-bottom-style: solid;
  background-color: rgba(37, 99, 235, 0.1);
}

.entity-concept {
  color: #2563eb;
  border-color: #93c5fd;
}

.entity-person {
  color: #16a34a;
  border-color: #86efac;
}

.entity-theory,
.entity-framework {
  color: #9333ea;
  border-color: #c4b5fd;
}

.entity-assessment {
  color: #ea580c;
  border-color: #fdba74;
}

.entity-default {
  color: #6b7280;
  border-color: #d1d5db;
}
```

### Step 5: Commit

```bash
cd .worktrees/readest
git add readest/apps/readest-app/src/services/transformers/entity.ts \
        readest/apps/readest-app/src/services/transformers/index.ts \
        readest/apps/readest-app/src/services/transformers/types.ts
git commit -m "feat(readest): Add entity transformer for overlay flow mode"
```

---

## Task 3: Flow Mode Store - Entity Overlay State

**Files:**
- Modify: `.worktrees/readest/readest/apps/readest-app/src/store/flowModeStore.ts`

### Step 1: Add entity overlay state

```typescript
// Add to flowModeStore.ts interface and store

// New types
export type EntityType = 'Concept' | 'Person' | 'Theory' | 'Framework' | 'Assessment';

export interface BookEntityOverlay {
  name: string;
  type: EntityType;
  mentionCount: number;
}

// Add to FlowModeState interface
interface FlowModeState {
  // ... existing fields ...

  // Entity overlay state
  entityOverlayEnabled: boolean;
  bookEntities: BookEntityOverlay[];
  visibleEntityTypes: EntityType[];
  isLoadingBookEntities: boolean;

  // Entity overlay actions
  setEntityOverlayEnabled: (enabled: boolean) => void;
  setBookEntities: (entities: BookEntityOverlay[]) => void;
  toggleEntityType: (type: EntityType) => void;
  setVisibleEntityTypes: (types: EntityType[]) => void;
  fetchBookEntities: (bookHash: string) => Promise<void>;
}

// Add to store implementation
export const useFlowModeStore = create<FlowModeState>((set, get) => ({
  // ... existing state ...

  // Entity overlay defaults
  entityOverlayEnabled: false,
  bookEntities: [],
  visibleEntityTypes: ['Concept', 'Person', 'Theory', 'Framework', 'Assessment'],
  isLoadingBookEntities: false,

  setEntityOverlayEnabled: (enabled) => set({ entityOverlayEnabled: enabled }),

  setBookEntities: (entities) => set({ bookEntities: entities }),

  toggleEntityType: (type) => {
    const current = get().visibleEntityTypes;
    const updated = current.includes(type)
      ? current.filter(t => t !== type)
      : [...current, type];
    set({ visibleEntityTypes: updated });
  },

  setVisibleEntityTypes: (types) => set({ visibleEntityTypes: types }),

  fetchBookEntities: async (bookHash) => {
    set({ isLoadingBookEntities: true });
    try {
      const apiBase = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
        ? `http://${window.location.hostname}:8081`
        : 'http://localhost:8081';

      const response = await fetch(`${apiBase}/graph/entities/by-book/${bookHash}`);
      if (!response.ok) throw new Error('Failed to fetch entities');

      const data = await response.json();
      set({
        bookEntities: data.entities,
        isLoadingBookEntities: false,
      });
    } catch (error) {
      console.error('Failed to fetch book entities:', error);
      set({ bookEntities: [], isLoadingBookEntities: false });
    }
  },
}));
```

### Step 2: Commit

```bash
cd .worktrees/readest
git add readest/apps/readest-app/src/store/flowModeStore.ts
git commit -m "feat(readest): Add entity overlay state to flowModeStore"
```

---

## Task 4: Entity Type Filter Controls

**Files:**
- Create: `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/EntityTypeFilter.tsx`
- Modify: `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/Header.tsx`

### Step 1: Create EntityTypeFilter component

```tsx
// .worktrees/readest/readest/apps/readest-app/src/app/reader/components/flowpanel/EntityTypeFilter.tsx
import React from 'react';
import clsx from 'clsx';

import { useTranslation } from '@/hooks/useTranslation';
import { EntityType, useFlowModeStore } from '@/store/flowModeStore';

const ENTITY_TYPE_CONFIG: Record<EntityType, { label: string; color: string; bgColor: string }> = {
  Concept: { label: 'Concepts', color: 'text-blue-600', bgColor: 'bg-blue-100' },
  Person: { label: 'People', color: 'text-green-600', bgColor: 'bg-green-100' },
  Theory: { label: 'Theories', color: 'text-purple-600', bgColor: 'bg-purple-100' },
  Framework: { label: 'Frameworks', color: 'text-purple-600', bgColor: 'bg-purple-100' },
  Assessment: { label: 'Assessments', color: 'text-orange-600', bgColor: 'bg-orange-100' },
};

const EntityTypeFilter: React.FC = () => {
  const _ = useTranslation();
  const {
    entityOverlayEnabled,
    visibleEntityTypes,
    toggleEntityType,
    setEntityOverlayEnabled,
    bookEntities,
  } = useFlowModeStore();

  // Count entities by type
  const typeCounts = React.useMemo(() => {
    const counts: Record<string, number> = {};
    for (const entity of bookEntities) {
      counts[entity.type] = (counts[entity.type] || 0) + 1;
    }
    return counts;
  }, [bookEntities]);

  return (
    <div className="space-y-3">
      {/* Master toggle */}
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">{_('Entity Overlay')}</span>
        <input
          type="checkbox"
          className="toggle toggle-primary toggle-sm"
          checked={entityOverlayEnabled}
          onChange={(e) => setEntityOverlayEnabled(e.target.checked)}
        />
      </div>

      {/* Type filters */}
      {entityOverlayEnabled && (
        <div className="flex flex-wrap gap-2">
          {(Object.keys(ENTITY_TYPE_CONFIG) as EntityType[]).map((type) => {
            const config = ENTITY_TYPE_CONFIG[type];
            const isActive = visibleEntityTypes.includes(type);
            const count = typeCounts[type] || 0;

            return (
              <button
                key={type}
                onClick={() => toggleEntityType(type)}
                className={clsx(
                  'flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium transition-all',
                  isActive
                    ? `${config.bgColor} ${config.color}`
                    : 'bg-base-200 text-base-content/50'
                )}
              >
                <span>{config.label}</span>
                {count > 0 && (
                  <span className={clsx(
                    'rounded-full px-1.5 text-xs',
                    isActive ? 'bg-white/50' : 'bg-base-300'
                  )}>
                    {count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default EntityTypeFilter;
```

### Step 2: Add filter to FlowPanel header

```tsx
// Modify Header.tsx to include EntityTypeFilter
// Add import
import EntityTypeFilter from './EntityTypeFilter';

// Add in the header content, below the title/controls
<div className="border-t border-base-300 pt-3 mt-3">
  <EntityTypeFilter />
</div>
```

### Step 3: Commit

```bash
cd .worktrees/readest
git add readest/apps/readest-app/src/app/reader/components/flowpanel/EntityTypeFilter.tsx \
        readest/apps/readest-app/src/app/reader/components/flowpanel/Header.tsx
git commit -m "feat(readest): Add entity type filter controls to flow panel"
```

---

## Task 5: Wire Up Entity Overlay to FoliateViewer

**Files:**
- Modify: `.worktrees/readest/readest/apps/readest-app/src/app/reader/components/FoliateViewer.tsx`

### Step 1: Fetch entities on book load

```typescript
// In FoliateViewer.tsx, add:

import { useFlowModeStore } from '@/store/flowModeStore';

// Inside component, add:
const {
  entityOverlayEnabled,
  bookEntities,
  visibleEntityTypes,
  fetchBookEntities,
} = useFlowModeStore();

// Add effect to fetch entities when book loads
useEffect(() => {
  // Fetch entities using book hash (derived from bookKey or file hash)
  const bookHash = bookKey; // Or extract actual file hash
  fetchBookEntities(bookHash);
}, [bookKey, fetchBookEntities]);
```

### Step 2: Pass entity overlay to transform context

```typescript
// In the getDocTransformHandler function, modify the TransformContext:

const ctx: TransformContext = {
  bookKey,
  viewSettings,
  width,
  height,
  primaryLanguage: bookData.book?.primaryLanguage,
  userLocale: getLocale(),
  content: data,
  transformers: [
    'style',
    'punctuation',
    'footnote',
    'whitespace',
    'language',
    'sanitizer',
    'entity', // Add entity transformer
  ],
  // Add entity overlay data
  entityOverlay: {
    enabled: entityOverlayEnabled,
    entities: bookEntities,
    visibleTypes: visibleEntityTypes,
  },
};
```

### Step 3: Add click handler for entity spans

```typescript
// Add to iframe event handling (in useFoliateEvents or similar)

// Listen for clicks on entity-link spans
const handleEntityClick = (event: Event) => {
  const target = event.target as HTMLElement;
  if (target.classList.contains('entity-link')) {
    const entityName = target.dataset.entityName;
    const entityType = target.dataset.entityType;
    if (entityName) {
      // Open flow panel with this entity
      setFlowModeActive(true);
      // Fetch entity details
      fetchEntityDetails(entityName);
    }
  }
};

// Register on document load in iframe
```

### Step 4: Commit

```bash
cd .worktrees/readest
git add readest/apps/readest-app/src/app/reader/components/FoliateViewer.tsx
git commit -m "feat(readest): Wire entity overlay to FoliateViewer transform pipeline"
```

---

## Task 6: Integration Testing

### Step 1: Start backend

```bash
cd ies/backend && uv run uvicorn ies_backend.main:app --reload --port 8081
```

### Step 2: Start Readest

```bash
cd .worktrees/readest/readest && pnpm dev-web
```

### Step 3: Test flow

1. Open a book that has been ingested to the knowledge graph
2. Toggle "Entity Overlay" in flow panel
3. Verify entities appear highlighted in text
4. Click entity type filters to show/hide types
5. Click an entity in text
6. Verify sidebar shows entity connections

### Step 4: Final commit

```bash
git add -A
git commit -m "feat: Complete entity overlay flow mode implementation"
```

---

## Success Criteria

1. **Backend API works**: `GET /graph/entities/by-book/{hash}` returns entities
2. **Entities highlighted**: Book text shows colored underlines for entities
3. **Filter works**: Toggling type buttons shows/hides entity categories
4. **Click interaction**: Clicking entity opens sidebar with connections
5. **Performance**: No noticeable lag when loading/rendering entities
6. **Styling matches**: Entity colors match synapse design mockups

---

## Notes

### Book Hash
The book hash used to query entities must match what's stored in Neo4j. This is typically the MD5 hash of the epub file. Verify the hash format matches between Readest's bookKey and the graph database.

### Performance Considerations
- Entity regex matching happens on each page render
- Consider caching transformed content
- For books with 500+ entities, may need virtualization

### Future Enhancements
- Hover cards showing entity preview (like synapse mockup)
- Entity density heatmap in progress bar
- Entity-based navigation ("jump to next mention of X")
