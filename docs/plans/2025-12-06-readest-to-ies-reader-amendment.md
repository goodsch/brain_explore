# Plan Amendment: Readest → IES Reader Switch

**Date:** 2025-12-06
**Amends:** `2025-12-06-comprehensive-remediation-plan.md`
**Decision:** Replace Readest integration with custom IES Reader

---

## Rationale

### Problems with Readest
1. **Tauri + Next.js complexity** — Heavy build system, frequent breaks
2. **Monorepo structure** — Changes require navigating `.worktrees/readest/readest/apps/readest-app/`
3. **Upstream conflicts** — Our modifications conflict with upstream updates
4. **Supabase dependency** — User ID tied to external auth system
5. **Feature bloat** — We only use 10% of Readest's functionality

### Benefits of IES Reader
1. **Simple stack** — Vite + React + TypeScript (same as SiYuan plugin)
2. **Full control** — No upstream to fight
3. **Direct paths** — `ies/reader/src/` vs deeply nested worktree
4. **No external auth** — User ID from our profile service
5. **Minimal footprint** — ~10 files, ~500 lines of code

---

## Architecture Update

### Before (Readest)
```
Layer 4: Readest (React/Next.js + Tauri)
└── .worktrees/readest/readest/apps/readest-app/src/
    ├── store/flowModeStore.ts           # 407 lines, Zustand
    ├── services/flow/graphClient.ts     # Backend integration
    └── services/flow/journeyStorage.ts  # localStorage (broken)
```

### After (IES Reader)
```
Layer 4: IES Reader (React + Vite)
└── ies/reader/src/
    ├── store/flowStore.ts               # Zustand state management
    ├── services/graphClient.ts          # Backend API client
    ├── hooks/useEntityLookup.ts         # Entity search logic
    └── components/
        ├── Reader.tsx                   # EPUB reader + toolbar
        └── flow/FlowPanel.tsx           # Entity display sidebar
```

---

## Wave 2 Updates

### Task 2.1: ~~Readest-Backend Wiring~~ → IES Reader-Backend Wiring

**Original prompt:**
```
Wire Readest Flow panel to backend APIs.
Files: .worktrees/readest/.../flowModeStore.ts, graphClient.ts, journeyStorage.ts
```

**Updated prompt:**
```
Wire IES Reader to backend APIs. Requirements:

1. User Authentication
   - Add login flow to App.tsx (call /profile/login on startup)
   - Store user_id in flowStore
   - Pass user_id to all backend calls

2. Entity Lookup (already implemented, needs real endpoints)
   - graphClient.searchEntities() → GET /graph/search?q={text}
   - graphClient.exploreEntity() → GET /graph/explore/{id}
   - graphClient.getEntity() → GET /graph/entity/{id}

3. Journey Persistence
   - flowStore.endJourney() → graphClient.saveJourney()
   - Add retry queue for failed saves
   - Fetch journey history on FlowPanel open

4. Thinking Partner Questions
   - graphClient.getThinkingPartnerQuestions() → POST /question-engine/questions

5. Sync Status
   - Add sync indicator to FlowPanel header
   - Show pending/synced/error states

Files to modify:
- ies/reader/src/services/graphClient.ts (update endpoints)
- ies/reader/src/store/flowStore.ts (add user_id, retry queue)
- ies/reader/src/components/flow/FlowPanel.tsx (sync indicator)
- ies/reader/src/App.tsx (login flow)

Output: /docs/scratch/wave-2-task-1-complete.md
```

### Task 2.2: SiYuan-Backend Wiring (Unchanged)
No changes needed — SiYuan plugin remains as specified.

### Task 2.3: Cross-App Sync Design (Simplified)

**Original scope:**
- Readest ↔ SiYuan ↔ Backend sync
- Supabase UUID mapping

**Updated scope:**
- IES Reader ↔ SiYuan ↔ Backend sync
- Unified user_id from profile service (simpler)
- No Supabase mapping needed

---

## Backend API Requirements

### Endpoints IES Reader Needs

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/profile/login` | POST | Get/create user profile | ✅ Exists |
| `/graph/search` | GET | Search entities by text | ✅ Exists |
| `/graph/explore/{id}` | GET | Get entity + relationships | ✅ Exists |
| `/graph/entity/{id}` | GET | Get single entity | ✅ Exists |
| `/question-engine/questions` | POST | Generate thinking partner Qs | ✅ Exists |
| `/journeys` | POST | Save completed journey | ⚠️ Verify |
| `/journeys` | GET | List user's journeys | ⚠️ Verify |
| `/journeys/{id}` | GET | Get journey details | ⚠️ Verify |

### Endpoints to Verify/Implement

Before Wave 2 implementation, verify these endpoints work:

```bash
# Test journey save
curl -X POST http://localhost:8081/journeys \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "entry_point": "Book Title", "path": []}'

# Test journey list
curl http://localhost:8081/journeys?user_id=test

# Test journey detail
curl http://localhost:8081/journeys/{id}
```

---

## IES Reader Feature Roadmap

### MVP (Wave 2)
- [x] EPUB reading with text selection
- [x] Flow Panel with entity display
- [x] Journey tracking (in-memory)
- [ ] Backend entity lookup (wire real endpoints)
- [ ] Backend journey persistence
- [ ] User authentication flow
- [ ] Sync status indicator

### Post-MVP (Wave 3+)
- [ ] Journey history UI
- [ ] Offline queue with sync
- [ ] Bookmarks
- [ ] Annotations
- [ ] Reading progress sync
- [ ] Library management (Calibre integration)

### Future (Nice to Have)
- [ ] PWA for mobile
- [ ] Electron wrapper for desktop
- [ ] KOReader plugin for e-ink devices

---

## Files to Delete (After Migration Verified)

Once IES Reader is fully wired and tested, these Readest-related files become obsolete:

```
.worktrees/readest/                    # Entire worktree
docs/ANALYSIS-*-READEST-*.md          # Readest-specific analyses
```

**Do not delete until:**
1. IES Reader passes all Wave 2 acceptance criteria
2. Journey save/load verified end-to-end
3. At least 2 weeks of usage without issues

---

## Updated Success Criteria

### Wave 2 Complete When:

**Original:**
- [ ] Readest journeys save to backend
- [ ] SiYuan displays backend journey history
- [ ] Backend errors surface in frontends

**Updated:**
- [ ] IES Reader journeys save to backend
- [ ] IES Reader fetches journey history from backend
- [ ] SiYuan displays backend journey history
- [ ] Both apps use user_id from profile service
- [ ] Sync status visible in both UIs
- [ ] Backend errors surface with retry option

---

## Implementation Order

1. **Verify backend endpoints** — Test journey CRUD before frontend work
2. **Add user auth to IES Reader** — Login flow, store user_id
3. **Wire graphClient to real endpoints** — Replace stubs
4. **Add journey persistence** — Save on endJourney()
5. **Add journey history fetch** — Load on FlowPanel open
6. **Add sync status indicator** — Visual feedback
7. **Test end-to-end** — Full flow from text selection to journey save

---

## CLAUDE.md Updates Required

Update the following sections in `/home/chris/dev/projects/codex/brain_explore/CLAUDE.md`:

1. **Architecture section** — Replace Readest with IES Reader
2. **Essential Commands** — Add `cd ies/reader && npm run dev`
3. **Wave 2 description** — Update task descriptions
4. **IES Reader section** — Already added, verify accuracy

---

## Appendix: Comparison Matrix

| Aspect | Readest | IES Reader |
|--------|---------|------------|
| Build time | ~30s | ~3s |
| Dependencies | 200+ | 15 |
| Lines of code | 10,000+ | 500 |
| Platforms | Desktop (Tauri) | Web (any browser) |
| User ID | Supabase UUID | Profile service |
| Control | Limited (upstream) | Full |
| Format support | EPUB only | EPUB only |
| Flow Mode | Partial | Complete |
| Journey save | Broken | Pending |
| Maintenance | High | Low |
