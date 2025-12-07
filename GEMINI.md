# GEMINI — Gemini CLI Operating Guide

This repo is stewarded by Claude; Gemini should follow these rules for parallel work.

## Cross-Agent Communication

**CHECK INBOX ON SESSION START:**
```bash
python scripts/agent_comm.py inbox --agent gemini
```

**Post updates/questions:**
```bash
python scripts/agent_comm.py post --from gemini --to claude --type update --subject "Task complete" --body "Details..."
```

**Update your status:**
```bash
python scripts/agent_comm.py status --agent gemini --task "Working on X" --status active
```

**Shared context:** `.agents/context/` contains decisions, blockers, and learnings.

---

## Gemini's Strengths

Use Gemini for:
- **Web research** — Google Search integration for current docs/practices
- **Codebase analysis** — `codebase_investigator` for architecture understanding
- **Parallel exploration** — Can run searches while other agents work
- **Second opinions** — Code review from different perspective

## Current Assignment

**IES Reader development** in `.worktrees/ies-reader/`

Branch: `feature/ies-reader`

## Current Phase (Dec 7, 2025)

**Phase 2c: ~75% complete**

| Component | Status |
|-----------|--------|
| IES Reader Wave 1 | ✅ Complete (library, PWA, design system) |
| IES Reader Wave 2 | ✅ Complete (interactive features) |
| IES Reader Wave 3 | 🔄 In progress (mobile optimization) |

## Worktrees

**Use worktrees, not master:**

| Worktree | Branch | Purpose |
|----------|--------|---------|
| `.worktrees/ies-reader/` | `feature/ies-reader` | **Your primary workspace** |
| `.worktrees/siyuan/` | `feature/siyuan-evolution` | SiYuan plugin |
| `.worktrees/readest/` | `feature/readest-integration` | Readest fork |

## Quick Commands

```bash
# IES Reader dev
cd .worktrees/ies-reader/ies/reader && pnpm dev

# Check status
python scripts/agent_comm.py status --show

# Post completion update
python scripts/agent_comm.py post --from gemini --to claude --type handoff \
  --subject "Wave 3 Section X complete" \
  --body "Implemented mobile nav. Ready for review."
```

## Key Documentation

| Resource | Purpose |
|----------|---------|
| `CLAUDE.md` | Full project instructions |
| `docs/plans/2025-12-07-ies-reader-wave3-design.md` | IES Reader Wave 3 spec |
| `.agents/context/decisions.md` | Architecture decisions |
| `.agents/context/learnings.md` | Shared patterns |

## Guardrails

- **DO NOT** work on master branch
- **DO NOT** commit secrets or book files
- **DO** update status when starting/completing work
- **DO** post handoff messages when completing tasks
- **DO** check `.agents/context/blockers.md` for known issues

## Communication Protocol

When you complete work or need help:

1. **Handoff:** Post message with `--type handoff` summarizing what's done
2. **Blocked:** Post message with `--type blocker` describing the issue
3. **Question:** Post message with `--type question` for decisions needing input

**Claude checks the queue regularly and will respond or coordinate.**

## IES Reader Wave 3 Tasks

From the design doc:

1. **Section 1:** Mobile navigation (hide arrows, FAB for notes)
2. **Section 2:** Touch targets and gestures ✅
3. **Section 3:** Responsive layout refinements
4. **Section 4:** Performance optimization for mobile

Pick up where previous work left off. Check git log for recent changes.
