# Repository Guidelines

## IES SiYuan Architecture Expert Context

When discussing the IES SiYuan Architecture Package (`IES_SiYuan_Architecture_Package_QuickCaptureUpdated/`), you have expertise in:

### Package 7-Layer Structure
- `00_Inbox/` — Quick Capture with status lifecycle (raw → classified → processed)
- `01_Seedlings/` — Atomic ideas (7 types: Questions, Observations, Moments, Schemas, Contradictions, What_Ifs, Insights)
- `02_Shaping/` — Dialogue-mode guided questioning
- `03_Flow_Maps/` — Graph-like exploration (Perspectives, Concept_Maps, Systems, Timelines)
- `04_Concepts/` — Canonical concept pages (11 domain folders)
- `05_Projects/` — Active work structures (8-page template)
- `06_Archive/` — Retired/superseded material
- `07_System/` — Templates, schemas, directives

### Key Package Documents
- `07_System/AI_Assistant_Directives.md` — AI behavior rules
- `07_System/Block_Schemas.md` — 6 block types (seed, shaping, map, concept, decision, log_entry)
- `07_System/Quick_Capture_Schema.md` — Capture lifecycle
- `07_System/IES_SiYuan_Dataflow.md` — Information flow

### Design Decisions Already Made
- **Merged folder structure** (9 folders): Daily, Seedlings/{7 types}, Sessions/{5 modes}, Flow_Maps, Concepts, Insights, Favorite_Problems, Projects, Archive
- **Dual Insights folders:** Seedlings/Insights (raw) vs /Insights/ (promoted)
- **Both YAML frontmatter AND SiYuan attributes** (synced)
- **Two status fields:** `capture_status` (AI: raw/classified/processed) and `status` (user: captured/exploring/anchored)

### ADHD-Friendly Requirements to Preserve
- resonance_signal: 8 emotional retrieval cues
- energy_level: 3 levels for mood-based navigation
- exploration_visits: recency tracking
- Backend linking: be_id, be_type for Neo4j sync

### Key Implementation Files
- `.worktrees/siyuan/ies/plugin/src/utils/siyuan-structure.ts` — Folder structure
- `.worktrees/siyuan/ies/plugin/src/views/ForgeMode.svelte` — Session creation
- `library/graph/adhd_ontology.py` — ADHD entity types
- `docs/ARCHITECTURE-COMPARISON.md` — Full comparison analysis

---

## Project Structure & Module Organization
- `ies/backend/`: FastAPI service for entity extraction and knowledge storage; source in `src/ies_backend`, tests in `tests`.
- `ies/plugin/`: SiYuan plugin (Svelte/TypeScript) for running sessions; built with Vite.
- `library/`: Shared GraphRAG-style utilities reused across layers.
- `scripts/`: CLI helpers and maintenance scripts.
- `docs/`, `framework/`, `therapy/`, `books/`, `data/`: Planning docs, configuration, content, reference texts, and datasets. Secrets live in `.env` (copy from `.env.example`).
- Infrastructure: `docker-compose.yml` spins up Neo4j + Qdrant; logs via `docker compose logs -f neo4j|qdrant`.

## Build, Test, and Development Commands
- Bootstrap services: `docker compose up -d` (Neo4j, Qdrant).
- Backend dev server: `cd ies/backend && uv run uvicorn ies_backend.main:app --host 0.0.0.0 --port 8081`.
- Backend tests: `cd ies/backend && PYTHONPATH=src uv run pytest` (async-friendly; keeps imports resolved).
- Lint/type check: `cd ies/backend && uv run ruff check . && uv run mypy src` (line length 100, strict typing).
- Plugin build: `cd ies/plugin && npm install && npm run build`; watch mode: `npm run dev`.
- Plugin packaging helpers: `npm run make-link` (dev symlink) and `npm run make_dev_copy` (copy into SiYuan sandbox).

## Coding Style & Naming Conventions
- Python (backend/library): PEP 8 with ruff enforced; 4-space indents; snake_case for functions/vars, PascalCase for classes; prefer typed dataclasses/Pydantic models; keep public API in `ies_backend` small and documented.
- TypeScript/Svelte (plugin): ES module syntax; camelCase for vars/functions, PascalCase for components; keep UI state in stores/modules instead of globals; co-locate component styles.
- Keep configs/env-specific values in `.env`, not in source. Avoid committing book or session data excerpts.

## Testing Guidelines
- Tests live in `ies/backend/tests`; name files `test_*.py` and mirror module paths (e.g., `tests/services/test_entities.py`).
- Add unit tests for new endpoints/services and async handlers; use pytest markers instead of custom runners.
- For plugin changes, add minimal interaction coverage where possible (unit-level helpers) and manually verify in SiYuan after `npm run dev`.
- Aim for steady coverage; prefer small, deterministic fixtures and test doubles over live API hits.

## Commit & Pull Request Guidelines
- Follow existing prefixes: `fix:`, `docs:`, `chore:`, `feat:`; keep messages imperative and scoped (e.g., `fix: handle empty book nodes`).
- PRs should describe the behavior change, test steps (`pytest`, `ruff`, `mypy`, `npm run build`), and note any config/env updates. Link issues/tasks; include screenshots or console output for plugin UI changes.
- Keep changeset focused; update relevant `progress.md` files when touching framework/therapy workstreams.
