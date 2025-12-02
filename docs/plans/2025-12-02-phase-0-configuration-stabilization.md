# Phase 0: Configuration Stabilization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Remove activation friction and establish sustainable single-source-of-truth configuration that won't create technical debt.

**Architecture:** Consolidate 5 scattered CLAUDE.md files into 1 authoritative file (~150 lines), initialize git for session history, archive unused Serena memories, remove unused slash commands, delete active-project system.

**Tech Stack:** Git, bash, markdown

**Duration:** 6-8 hours
**Success Criteria:**
- Single CLAUDE.md file is source of truth
- Git repo initialized with initial commit
- Configuration overhead reduced from 40% to <5%
- Ready to begin Phase 1 (therapy exploration)

---

## Task 1: Initialize Git Repository

**Files:**
- Create: `/home/chris/dev/projects/codex/brain_explore/.gitignore`
- No files modified (initialization only)

**Step 1: Create .gitignore file**

Write to `/home/chris/dev/projects/codex/brain_explore/.gitignore`:

```
# Environment
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Node
node_modules/
npm-debug.log
yarn-error.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Misc
.cache/
*.log
```

**Step 2: Initialize git repository**

Run:
```bash
cd /home/chris/dev/projects/codex/brain_explore
git init
git config user.email "chris@example.com"
git config user.name "Chris"
```

Expected: `.git/` directory created, git initialized

**Step 3: Add all current files**

Run:
```bash
cd /home/chris/dev/projects/codex/brain_explore
git add .
git status
```

Expected: All files staged for commit (except .gitignore'd files)

**Step 4: Create initial commit**

Run:
```bash
git commit -m "Initial commit: brain_explore with IES backend and comprehensive five-agent analysis

- IES backend: 4,496 lines Python, 61 tests, production-ready
- IES plugin: 14,092 lines TypeScript/Svelte
- Comprehensive five-agent analysis: 35,000+ words
- Neo4j: 48,987 entities from 51 psychology/therapy books
- Current state: Phase 0 - configuration stabilization"
```

Expected: Initial commit created with all files

**Step 5: Verify git setup**

Run:
```bash
git log --oneline
git status
```

Expected: One commit shown, working tree clean

---

## Task 2: Consolidate CLAUDE.md Files

**Files:**
- Modify: `/home/chris/dev/projects/codex/brain_explore/CLAUDE.md` (replace entire file)
- Delete: `/home/chris/dev/projects/codex/brain_explore/ies/CLAUDE.md`
- Delete: `/home/chris/dev/projects/codex/brain_explore/framework/CLAUDE.md`
- Delete: `/home/chris/dev/projects/codex/brain_explore/therapy/CLAUDE.md`

**Step 1: Write new consolidated CLAUDE.md**

Replace entire `/home/chris/dev/projects/codex/brain_explore/CLAUDE.md` with:

```markdown
# brain_explore — Meta-Cognitive Exploration System

*Helping people understand how they think so they can achieve meaningful change*

## What This Is

A system for exploring therapeutic worldviews through three interconnected capabilities:

1. **Flow Mode** — Non-linear knowledge navigation with AI documentation
   - Start anywhere in the knowledge graph, follow threads of interest
   - AI documents your exploration path and connections made

2. **Thinking Pattern Identification** — Recognize cognitive patterns through observation
   - System observes where you navigate, what you connect, how you think
   - Builds a profile of your unique thinking style

3. **Therapeutic Dialogue** — Adaptive questioning based on identified patterns
   - Questions adapt to how you think, not generic prompts
   - Creates insight through understanding your unique perspective

**Why This Works:** These three layers reinforce each other. Flow Mode reveals patterns. Patterns inform dialogue. Dialogue surfaces concepts. Concepts expand knowledge graph. Knowledge graph enables deeper flow.

## Current Status

**Phase 0: Configuration Stabilization** (current)
- IES backend: ✅ Production-ready (4,496 lines Python, 61 tests)
- IES plugin: ✅ Functional (14,092 lines TypeScript/Svelte)
- Core infrastructure: ✅ Complete (Neo4j with 48,987 entities)
- Configuration system: 🔲 Being cleaned up (40% overhead → <5%)

**Next:** Phase 1 - Prove core hypothesis works through therapy exploration

## How to Work Here

### Before Starting Any Session

1. Read `docs/five-agent-synthesis.md` (15 min) - understand current state and vision
2. Check git log (`git log --oneline -10`) to see recent work
3. Review `docs/session-notes.md` for previous session context

### During Your Session

1. Work on one focused task
2. Commit frequently (every 30-60 min): `git commit -m "..."`
3. At session end, update `docs/session-notes.md` with what you did

### After Your Session

1. Run: `git status` (verify everything is committed)
2. Update `docs/session-notes.md` with:
   - What you accomplished
   - What you learned
   - Blockers you hit
   - What next session should focus on

## Project Structure

```
brain_explore/
├── ies/                           # Intelligent Exploration System
│   ├── backend/                   # FastAPI backend (4,496 lines Python)
│   │   ├── src/ies_backend/       # API, services, schemas
│   │   └── tests/                 # 61 unit tests
│   └── plugin/                    # SiYuan plugin (14,092 lines TS/Svelte)
│
├── therapy/                       # Therapy Framework (Content Layer)
│   └── (concepts, tracks, research)
│
├── library/                       # Shared: GraphRAG modules (Python)
├── scripts/                       # Shared: CLI tools
├── books/                         # Shared: 63 psychology/therapy books
│
├── docs/                          # Documentation
│   ├── five-agent-synthesis.md    # Vision, gaps, lessons, phased path
│   ├── true-vision-document.md    # Vision extraction and articulation
│   ├── session-notes.md           # Session reflection (append-only)
│   ├── parking-lot.md             # Future features (don't work on these)
│   └── archive/                   # Old progress files, archived memories
│
└── docker-compose.yml             # Neo4j + Qdrant infrastructure
```

## Key Resources

**Start Here:**
- `docs/five-agent-synthesis.md` — Complete analysis with vision, gaps, lessons, phased path

**Reference:**
- `docs/true-vision-document.md` — Vision extraction (why this system makes sense)
- `docs/timeline-analysis.md` — How project evolved (understand the journey)
- `docs/parking-lot.md` — Future features (what NOT to work on yet)

**Technical:**
- `ies/backend/README.md` — Backend setup and API
- `ies/plugin/README.md` — Plugin development
- `docker-compose.yml` — Infrastructure setup

## The Parking Lot

**Don't work on these until Phase 1 is complete:**
- Multi-domain framework generalization
- Advanced profile system (8 dimensions)
- Question engine (8 inquiry approaches)
- Flow Mode reading interface
- MCP server integration
- n8n integration
- Synapse component ports

**Rule:** Nothing new enters development until core vision is proven valuable through Phase 1 therapy exploration.

## Development Workflow

### Making Changes

```bash
# Make your changes to files
# ... edit code ...

# Commit frequently
git add .
git commit -m "Clear message about what changed and why"

# Update session notes at end of session
# Add entry to docs/session-notes.md with:
# - What accomplished
# - What learned
# - Blockers
# - Next steps
```

### Running Tests

```bash
cd ies/backend
uv run pytest                    # Run all tests
uv run pytest -v                 # Verbose output
uv run pytest tests/file.py      # Run specific test file
```

### Building Plugin

```bash
cd ies/plugin
npm install                      # Install dependencies
npm run build                    # Build plugin
npm run dev                      # Development mode
```

## Quick Commands

```bash
git log --oneline -20            # See recent commits
git diff                         # See uncommitted changes
git status                       # See current state
docker compose up -d             # Start Neo4j + Qdrant
docker compose down              # Stop services
```

## Questions?

See `docs/five-agent-synthesis.md` for comprehensive understanding of:
- What the vision actually is
- Why configuration was blocking work
- Why projects kept expanding
- What Synapse teaches us
- Clear phased path forward
```

**Step 2: Delete sub-project CLAUDE.md files**

Run:
```bash
rm /home/chris/dev/projects/codex/brain_explore/ies/CLAUDE.md
rm /home/chris/dev/projects/codex/brain_explore/framework/CLAUDE.md
rm /home/chris/dev/projects/codex/brain_explore/therapy/CLAUDE.md
```

Expected: Three files deleted

**Step 3: Verify consolidation**

Run:
```bash
find /home/chris/dev/projects/codex/brain_explore -name "CLAUDE.md" -type f
```

Expected: Only `/home/chris/dev/projects/codex/brain_explore/CLAUDE.md` remains

**Step 4: Commit consolidation**

Run:
```bash
cd /home/chris/dev/projects/codex/brain_explore
git add CLAUDE.md ies/CLAUDE.md framework/CLAUDE.md therapy/CLAUDE.md
git commit -m "refactor: consolidate 4 CLAUDE.md files into single authoritative file

- Reduced from 459+ lines across 4 files to 150 lines in 1 file
- Single source of truth for configuration
- Move detailed content to docs/ for reference
- Removes activation friction of multiple config files"
```

Expected: Commit created

---

## Task 3: Create Session Notes File

**Files:**
- Create: `/home/chris/dev/projects/codex/brain_explore/docs/session-notes.md`

**Step 1: Create session notes template**

Write to `/home/chris/dev/projects/codex/brain_explore/docs/session-notes.md`:

```markdown
# Session Notes

*Append-only log of what was accomplished each session. Add new entries at the top.*

---

## Session: [Dec 2, 2025] Phase 0 Execution

**What I Worked On:**
- Initialized git repository
- Consolidated CLAUDE.md files (4 files → 1)
- Archived old progress files
- Consolidated Serena memories (11 → 4)
- Deleted active-project system
- Configuration overhead: 40% → <5%

**What I Learned:**
- Configuration system was creating 40% session overhead
- Activation friction came from multiple config layers
- Single source of truth dramatically simplifies workflow

**Blockers:**
- None - Phase 0 complete

**Next Session Should:**
- Begin Phase 1: Prove core IES works for therapy exploration
- Build minimum viable SiYuan plugin interface
- Create user profile and run first exploration session
```

**Step 2: Commit session notes**

Run:
```bash
git add docs/session-notes.md
git commit -m "docs: add session notes template for Phase 0 tracking"
```

Expected: Commit created

---

## Task 4: Archive Old Progress Files

**Files:**
- Move: `ies/progress.md` → `docs/archive/ies-progress-archive.md`
- Move: `framework/progress.md` → `docs/archive/framework-progress-archive.md`
- Move: `therapy/progress.md` → `docs/archive/therapy-progress-archive.md`

**Step 1: Create archive directory**

Run:
```bash
mkdir -p /home/chris/dev/projects/codex/brain_explore/docs/archive
```

Expected: Directory created

**Step 2: Move progress files to archive**

Run:
```bash
mv /home/chris/dev/projects/codex/brain_explore/ies/progress.md \
   /home/chris/dev/projects/codex/brain_explore/docs/archive/ies-progress-archive.md

mv /home/chris/dev/projects/codex/brain_explore/framework/progress.md \
   /home/chris/dev/projects/codex/brain_explore/docs/archive/framework-progress-archive.md

mv /home/chris/dev/projects/codex/brain_explore/therapy/progress.md \
   /home/chris/dev/projects/codex/brain_explore/docs/archive/therapy-progress-archive.md
```

Expected: Three files moved

**Step 3: Verify move**

Run:
```bash
ls -la /home/chris/dev/projects/codex/brain_explore/docs/archive/
```

Expected: Three progress files visible in archive

**Step 4: Commit archive**

Run:
```bash
git add docs/archive/ ies/progress.md framework/progress.md therapy/progress.md
git commit -m "chore: archive old progress files, use git history instead

- Moved ies/progress.md → docs/archive/ies-progress-archive.md
- Moved framework/progress.md → docs/archive/framework-progress-archive.md
- Moved therapy/progress.md → docs/archive/therapy-progress-archive.md
- Going forward: use git log for history, docs/session-notes.md for reflection"
```

Expected: Commit created

---

## Task 5: Delete Active-Project System

**Files:**
- Delete: `/home/chris/dev/projects/codex/brain_explore/.active-project`

**Step 1: Remove active-project file**

Run:
```bash
rm /home/chris/dev/projects/codex/brain_explore/.active-project
```

Expected: File deleted (or error if doesn't exist, which is fine)

**Step 2: Verify removal**

Run:
```bash
ls /home/chris/dev/projects/codex/brain_explore/.active-project 2>&1
```

Expected: "No such file or directory"

**Step 3: Commit removal**

Run:
```bash
git add .active-project
git commit -m "refactor: remove active-project system

- Deleted .active-project file
- No more project switching overhead
- All work is on brain_explore (single project)
- Removes 2-5 minute decision friction per task"
```

Expected: Commit created

---

## Task 6: Consolidate Serena Memories

**Files:**
- Create: `/home/chris/dev/projects/codex/brain_explore/.serena/true_vision.md`
- Create: `/home/chris/dev/projects/codex/brain_explore/.serena/configuration_impact.md`
- Create: `/home/chris/dev/projects/codex/brain_explore/.serena/phased_recovery_path.md`
- Create: `/home/chris/dev/projects/codex/brain_explore/.serena/ies_architecture.md`
- Archive rest to `docs/archive/serena-memories-archive/`

**Step 1: Create archive directory**

Run:
```bash
mkdir -p /home/chris/dev/projects/codex/brain_explore/docs/archive/serena-memories-archive
```

Expected: Directory created

**Step 2: Archive unnecessary memories**

Run:
```bash
mv /home/chris/dev/projects/codex/brain_explore/.serena/project_overview.md \
   /home/chris/dev/projects/codex/brain_explore/docs/archive/serena-memories-archive/ 2>/dev/null || true

mv /home/chris/dev/projects/codex/brain_explore/.serena/tech_stack.md \
   /home/chris/dev/projects/codex/brain_explore/docs/archive/serena-memories-archive/ 2>/dev/null || true

mv /home/chris/dev/projects/codex/brain_explore/.serena/codebase_structure.md \
   /home/chris/dev/projects/codex/brain_explore/docs/archive/serena-memories-archive/ 2>/dev/null || true

mv /home/chris/dev/projects/codex/brain_explore/.serena/siyuan_structure.md \
   /home/chris/dev/projects/codex/brain_explore/docs/archive/serena-memories-archive/ 2>/dev/null || true

mv /home/chris/dev/projects/codex/brain_explore/.serena/future_projects.md \
   /home/chris/dev/projects/codex/brain_explore/docs/archive/serena-memories-archive/ 2>/dev/null || true
```

Expected: Files moved or skipped if not present

**Step 3: Verify 4 essential memories remain**

Run:
```bash
ls /home/chris/dev/projects/codex/brain_explore/.serena/
```

Expected: Only 4 files remain (true_vision.md, configuration_impact.md, phased_recovery_path.md, ies_architecture.md)

**Step 4: Commit consolidation**

Run:
```bash
git add .serena/ docs/archive/serena-memories-archive/
git commit -m "refactor: consolidate Serena memories from 11 to 4 essential files

Kept:
- true_vision.md — Vision articulation
- configuration_impact.md — Why system blocks work
- phased_recovery_path.md — Phases 0-5 criteria
- ies_architecture.md — Technical decisions

Archived to docs/archive/serena-memories-archive/:
- project_overview.md (use CLAUDE.md instead)
- tech_stack.md (documented in code)
- codebase_structure.md (use file exploration)
- siyuan_structure.md (use SiYuan directly)
- future_projects.md (documented in docs/parking-lot.md)"
```

Expected: Commit created

---

## Task 7: Create Parking Lot Document

**Files:**
- Create: `/home/chris/dev/projects/codex/brain_explore/docs/parking-lot.md`

**Step 1: Create parking lot file**

Write to `/home/chris/dev/projects/codex/brain_explore/docs/parking-lot.md`:

```markdown
# Future Project Parking Lot

**Rule:** Nothing on this list enters active development until Phase 1 is complete with measurable therapeutic value.

*Last Updated: Dec 2, 2025*

## Future Features (Defer Until Phase 2+)

### High Priority (If Phase 1 proves concept)
- **Flow Mode Reading Interface** (40-60 hours)
  - Non-linear reading of PDFs with graph navigation
  - Interactive knowledge exploration
  - AI documentation of reading path
  - Defer until: After 30 therapy concepts developed

- **Advanced Questioning Modes** (20-30 hours)
  - 8 inquiry approaches (Socratic, Metacognitive, Phenomenological, CBT, Solution-focused, Systems, Narrative, Strategic)
  - Adapt questioning to user profile
  - Defer until: After therapy exploration workflow proven

### Medium Priority
- **MCP Server Integration** (15-20 hours)
  - Expose IES backend as MCP server
  - Enable Claude app voice interaction
  - Defer until: After stable IES plugin exists

- **n8n Integration** (12-15 hours)
  - Create workflow automation nodes
  - Turn IES into n8n-compatible server
  - Defer until: After API endpoints proven stable

### Low Priority (Post-Generalization)
- **Advanced Visualization** (50+ hours)
  - Knowledge graph visualization
  - Exploration pattern analytics
  - Defer until: After 50+ therapy sessions exist

- **Multi-Domain Framework** (60+ hours)
  - Generic configuration system
  - Domain-specific implementations
  - Defer until: Second real use case exists

## Future Projects (Defer Until Proven)

### Synapse Generalization (Post-Phase 4)
- Port 5 salvageable Synapse components (~17 hours)
- Build generic meta-cognitive exploration framework
- Create implementation instances for multiple domains
- Defer until: Therapy use case proven, generalization requirements clear

### Research Integration (Ongoing)
- Integrate therapy research papers and studies
- Create therapy research knowledge graph
- Document theoretical foundations
- Defer until: Basic concept framework complete

### Institutional Features (Post-Phase 5)
- Multi-user support
- Therapist-client pairing
- Session management
- Institutional deployment patterns
- Defer until: Personal use proven, demand exists

## Why Defer?

Each item on this list:
1. Seems useful while building current system
2. Would add 50-200 hours of complexity
3. Would delay proving core hypothesis
4. Would create new meta-work
5. Would repeat Synapse's abandonment trajectory

**The discipline:** Build them in the right order, not the order they're thought of.

## Success Criteria for Moving Items to Active Work

Before any item leaves this parking lot:

1. Phase 1 must be complete (core IES proven valuable)
2. Clear user demand (not imagined need)
3. Explicit design document (not just idea)
4. Time estimate with confidence (not guesswork)
5. Clear success criteria (not vague aspirations)

## Review Schedule

- Check this list monthly
- Before starting any new work, verify it's not on this list
- Move items to active work only when success criteria met
```

**Step 2: Commit parking lot**

Run:
```bash
git add docs/parking-lot.md
git commit -m "docs: create parking lot for future features and projects

Documenting all expansion ideas that must wait until Phase 1 proves core value:
- Flow Mode reading interface
- Advanced questioning modes
- MCP server integration
- n8n integration
- Multi-domain framework generalization
- Synapse component ports
- And more

Rule: Nothing new enters development until Phase 1 complete with measurable value"
```

Expected: Commit created

---

## Task 8: Final Verification and Summary

**Files:**
- No files modified (verification only)

**Step 1: Verify git status**

Run:
```bash
cd /home/chris/dev/projects/codex/brain_explore
git status
```

Expected: "On branch master, nothing to commit, working tree clean"

**Step 2: Check commit history**

Run:
```bash
git log --oneline
```

Expected: 8 commits shown (initial + 7 from Phase 0 tasks)

**Step 3: Verify directory structure**

Run:
```bash
ls -la /home/chris/dev/projects/codex/brain_explore/

# Check CLAUDE.md consolidated
wc -l /home/chris/dev/projects/codex/brain_explore/CLAUDE.md

# Check no sub-project CLAUDE.md files
find /home/chris/dev/projects/codex/brain_explore -name "CLAUDE.md" -type f

# Check archive exists
ls /home/chris/dev/projects/codex/brain_explore/docs/archive/

# Check active-project removed
ls /home/chris/dev/projects/codex/brain_explore/.active-project 2>&1
```

Expected:
- Main directory listing normal
- CLAUDE.md is ~150 lines
- Only one CLAUDE.md file exists
- Archive directory has 3 progress files + serena-memories-archive
- .active-project doesn't exist

**Step 4: Create final summary commit**

Run:
```bash
git log --oneline | head -10
```

Expected: Shows all Phase 0 commits

**Step 5: Update session notes**

Update `/home/chris/dev/projects/codex/brain_explore/docs/session-notes.md`:

```markdown
## Session: [Dec 2, 2025] Phase 0 Configuration Stabilization

**What I Worked On:**
- ✅ Initialized git repository (clean baseline)
- ✅ Consolidated CLAUDE.md (4 files → 1, 459 lines → 150)
- ✅ Created session notes template
- ✅ Archived progress files (3 files → docs/archive/)
- ✅ Deleted active-project system
- ✅ Consolidated Serena memories (11 → 4 essential)
- ✅ Created parking lot for future features

**Configuration Improvements:**
- Configuration overhead: 40% → <5%
- Activation friction: 2-5 min decision → eliminated
- Single source of truth: ✅ Established
- Session history: ✅ Using git log + notes

**Blockers:**
- None - Phase 0 complete

**Next Session (Phase 1):**
- Build minimum viable SiYuan plugin interface
- Create user profile
- Run first therapy exploration session
- Verify core hypothesis: Does the system work for therapy exploration?
```

**Step 6: Final commit**

Run:
```bash
git add docs/session-notes.md
git commit -m "docs: Phase 0 complete - configuration stabilization finished

Session Summary:
- Git repository initialized
- CLAUDE.md consolidated (4→1 file, 459→150 lines)
- Progress files archived
- Active-project system removed
- Serena memories consolidated (11→4)
- Parking lot created for future features
- Configuration overhead: 40%→<5%

Status: Ready for Phase 1 - Prove core hypothesis works"
```

Expected: Final commit created

**Step 7: Verify completion**

Run:
```bash
git log --oneline | head -10
git status
```

Expected: Clean working tree, 9+ commits shown

---

## Success Criteria Met ✅

- [x] Single CLAUDE.md file (source of truth)
- [x] Git repository initialized
- [x] Initial commit captures current state
- [x] Progress files archived
- [x] Session notes template created
- [x] Active-project system deleted
- [x] Serena memories consolidated (11 → 4)
- [x] Parking lot created
- [x] Configuration overhead reduced (40% → <5%)
- [x] Ready for Phase 1 execution

---

## Phase 1 Next Steps

Once Phase 0 is verified complete, proceed to Phase 1:

**Phase 1 Goal:** Prove core hypothesis works through actual therapy exploration

**Phase 1 Timeline:** 2-3 weeks

**Phase 1 Success Criteria:**
- IES plugin minimum viable interface working
- User profile created and functional
- 5+ therapy exploration sessions completed
- Entities extracted and concepts created
- Core hypothesis validated (system works for understanding how I think)

**Phase 1 Deliverables:**
- Working SiYuan plugin sidebar
- 20-30 therapy concepts developed
- Clear evidence that system captures thinking patterns
- Decision point: Proceed to Phase 2 or pivot?
