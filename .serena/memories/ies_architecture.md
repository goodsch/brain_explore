# IES Architecture — Current State (Dec 7, 2025)

## Four-Layer System

| Layer | Component | Status | Key Files |
|-------|-----------|--------|-----------|
| 1 | Knowledge Graph | Production | `library/graph/unified_client.py` (1,476 lines) |
| 2 | Backend APIs | 185 tests passing | `ies/backend/src/ies_backend/` |
| 3 | SiYuan Plugin | Remediation complete | `.worktrees/siyuan/ies/plugin/` |
| 4 | Readest | Wave 2 complete, Wave 3 in progress | `.worktrees/readest/` |

## Backend API Routes (Layer 2)

| Route | Purpose |
|-------|---------|
| `/graph` | Entity search, exploration, relationships |
| `/session` | Thinking sessions, ForgeMode |
| `/journeys` | Breadcrumb tracking, synthesis |
| `/profile` | User profiles, login |
| `/books` | Calibre catalog, covers, file serving |
| `/templates` | Thinking mode templates |
| `/reframes` | Concept metaphors/analogies |
| `/personal` | Sparks, insights, ADHD-friendly capture |
| `/flow` | Flow session lifecycle |
| `/inbox` | Quick capture processing |

## Key Services

- **UnifiedGraphClient** — Single Neo4j connection pool, 14 entity types preserved
- **SessionStore** — Redis-backed sessions, 24-hour TTL
- **FlowOrientationService** — Exploration strand generation
- **InboxService** — AI entity extraction from captures
- **FeedbackService** — Question response tracking

## Entity Types (14 total)

Domain: Concept, Person, Theory, Framework, Assessment
Personal: Spark, Insight, Thread, FavoriteProblem, Reframe
Patterns: Pattern, DynamicPattern, StoryInsight, SchemaBreak

## SiYuan Plugin Structure

9-folder hierarchy:
- `/Daily/` — Quick captures
- `/Seedlings/` — Atomic ideas (7 subcategories)
- `/Sessions/` — Mode-specific thinking (5 modes)
- `/Flow_Maps/` — Visual exploration
- `/Concepts/` — Canonical concepts
- `/Insights/` — Promoted insights
- `/Favorite_Problems/` — Anchor questions
- `/Projects/` — Active work
- `/Archive/` — Retired material

## IES Reader Features

- Calibre library browser with search/filter
- PWA with offline support
- Entity overlay (inline highlighting)
- Flow panel (relationships, sources, questions)
- Interactive questions with Cmd+Enter response
- Journey breadcrumbs (visible navigation trail)
- Notes capture with entity context

## Docker Services

```yaml
brain_explore_neo4j     # 7474, 7687
brain_explore_qdrant    # 6333, 6334
brain_explore_redis     # 6379
brain_explore_calibre   # 8083
brain_explore_siyuan    # 6806
```

## Integration Points

- Calibre → Neo4j: `calibre_id` as universal book identifier
- Backend → Redis: Session state persistence
- SiYuan ↔ Backend: forwardProxy from Docker
- Readest ↔ Backend: Direct HTTP (localhost:8081)
