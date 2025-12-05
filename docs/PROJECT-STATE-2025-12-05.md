# Project State — 2025-12-05

Scope: repository root (`master` worktree) only; no assumptions about remote or external services.

## Repository Snapshot
- Branch: `master`, ahead of origin by 32 commits.
- Dirty tree: modified `CLAUDE.md`; untracked `IES Chat/` note folder (`Hypothetical questions for introspection*.md`, `IES question engine expansion.md`, `Intelligent Exploration System.md`).
- Worktrees: `.worktrees/readest` (`feature/readest-integration`), `.worktrees/siyuan` (`feature/siyuan-evolution`).

## Code & Artifacts Observed
- Backend: `ies/backend/` (FastAPI; `src/ies_backend` APIs/services/schemas/models; tests in `ies/backend/tests`). README is minimal and out of sync with root instructions.
- Plugin: `ies/plugin/` (Svelte/TypeScript; built with Vite). Not inspected in this pass.
- Library: Python package via root `pyproject.toml` (`qdrant-client`, `neo4j`, `openai`, etc.).
- Infra: `docker-compose.yml` for Neo4j + Qdrant; `.env.example` present.
- Root JS: minimal `package.json` with `@waldzellai/clear-thought-onepointfive` only.
- Content: therapy concepts under `therapy/Track_1_Human_Mind/` (11 concept docs + `CONNECTIONS.md`).

## Documentation Reality Check
- Root `README.md`: comprehensive quick start + status table; claims backend/plugin production-ready and tests passing.
- Root `CLAUDE.md`: expanded narrative; Phase 2c focus (reframes/templates); notes worktrees and status claims (all four layers built).
- `docs/COMPREHENSIVE-PROJECT-STATUS.md` (2025-12-03): asserts Phase 2b complete, all layers working, 17 unpushed commits; aligns with README claims.
- `CLEANUP_SUMMARY.md` (2025-12-02): documents doc overhaul; states `ies/framework/therapy progress.md` condensed—but **no progress.md files are currently present anywhere**.
- `TASK.md` at root is a SiYuan plugin briefing (Phase 3, `feature/siyuan-evolution`), conflicting with `CLAUDE.md` note that master has no TASK.
- `docs/WORKTREE-GUIDE.md`: instructions on worktree usage (master/readest/siyuan).
- Pending doc updates flagged in cleanup summary: `ies/CLAUDE.md`, `framework/CLAUDE.md`, `therapy/CLAUDE.md` still to align messaging.

## Testing & Health (Not Run Here)
- No tests or builds executed in this pass. Docs claim 61 backend tests (54 passing) and production-ready backend/plugin; current state unverified.
- Service health (Neo4j/Qdrant/backend) not checked.

## Risks / Inconsistencies
- Status claims unverified (production-ready, test pass counts).
- Missing `progress.md` files despite references; may break workflows or status hooks.
- Root `TASK.md` location may mislead contributors given worktree model.
- Backend README divergence from root instructions (uv vs pip, endpoints listed).
- Untracked `IES Chat/` notes and modified `CLAUDE.md` need intentional handling before commit.

## Suggested Next Actions
1) Decide what to do with `IES Chat/` notes and the `CLAUDE.md` modification; commit or stash intentionally.
2) Recreate/restore `ies/framework/therapy` `progress.md` files referenced in docs, or update docs to remove stale references.
3) Align per-project `CLAUDE.md` files (ies/framework/therapy) with the cleanup summary guidance.
4) Clarify `TASK.md` placement: move into the SiYuan worktree or replace with a master-scoped task doc.
5) Validate code health: run backend tests (`cd ies/backend && PYTHONPATH=src uv run pytest`) and, if relevant, build the plugin (`cd ies/plugin && npm run build`); record results.
6) Confirm infrastructure works end-to-end (docker compose up, backend health, plugin ↔ backend connectivity) before asserting production-ready status.
