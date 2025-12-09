# IES Architecture — Implementation Reference

> **Ground Truth:** `docs/IES-SYSTEM-DESIGN.md`
> **API Details:** `docs/ARCHITECTURE-AND-INTERACTIONS.md`

## Backend API Routes

| Route | Purpose |
|-------|---------|
| `/context` | Context CRUD, parsing, search |
| `/questions` | Question CRUD, `GET /{id}/relevant-passages` |
| `/graph` | Entity search, facets, relationships |
| `/session-state` | Cross-app sync (needs Redis migration) |
| `/highlights` | Highlight CRUD + SiYuan sync |
| `/highlight-sync` | Batch sync to SiYuan |
| `/visits` | "What's new" tracking |
| `/journey-timeline` | Exploration history |
| `/extraction` | Context-aware entity extraction |
| `/books` | Calibre catalog, covers, files |
| `/reframes` | Concept metaphors/analogies |
| `/templates` | Thinking mode templates |
| `/block-attributes` | SiYuan block metadata |

## Key Services

| Service | Lines | Purpose |
|---------|-------|---------|
| `ExtractionEngine` | 600 | Context-aware extraction |
| `SessionStateService` | 289 | Cross-app state (in-memory) |
| `HighlightSyncService` | 225 | Reader → SiYuan sync |
| `JourneyTimelineService` | 369 | Exploration aggregation |
| `PassageRankingService` | 269 | Question-driven passages |

## Entity Types (14)

**Domain:** Concept, Person, Theory, Framework, Assessment
**Personal:** Spark, Insight, Thread, FavoriteProblem, Reframe
**Patterns:** Pattern, DynamicPattern, StoryInsight, SchemaBreak

## Question Engine (9 Classes)

1. Schema-Probe — Structure surfacing
2. Boundary — Edge clarification
3. Dimensional — Spectrum positioning
4. Causal — Mechanism exploration
5. Counterfactual — What-if analysis
6. Anchor — Concrete grounding
7. Perspective-Shift — Viewpoint change
8. Meta-Cognitive — Thinking patterns
9. Reflective-Synthesis — Integration

## IES Reader Key Files

| File | Purpose |
|------|---------|
| `Reader.tsx` | epub.js wrapper, selection handling |
| `FlowPanel.tsx` | Entity exploration UI |
| `flowStore.ts` | Zustand state (entities, questions, sync) |
| `useSessionSync.ts` | Backend state sync (5s/30s polling) |
| `useReadingPosition.ts` | CFI-based position tracking |

## SiYuan Plugin Key Files

| File | Purpose |
|------|---------|
| `FlowMode.svelte` | Graph exploration (113KB) |
| `ForgeMode.svelte` | Structured thinking (110KB) |
| `ContextSyncService.ts` | Backend polling for sync |

## Docker Services

```
brain_explore_neo4j     # 7474, 7687
brain_explore_redis     # 6379
brain_explore_qdrant    # 6333
brain_explore_calibre   # 8083
brain_explore_siyuan    # 6806
```
