
  Worktree Basics

  Each worktree = separate directory = separate branch

  /home/chris/dev/projects/codex/brain_explore/           → master
  /home/chris/dev/projects/codex/brain_explore/.worktrees/readest/  → feature/readest-integration
  /home/chris/dev/projects/codex/brain_explore/.worktrees/siyuan/   → feature/siyuan-evolution

  You don't switch branches - you switch directories.

  Starting Claude Code Sessions

  | To work on...           | Start session from...                                            |
  |-------------------------|------------------------------------------------------------------|
  | Phase 1 (API contracts) | /home/chris/dev/projects/codex/brain_explore/                    |
  | Phase 2 (Readest)       | /home/chris/dev/projects/codex/brain_explore/.worktrees/readest/ |
  | Phase 3 (SiYuan)        | /home/chris/dev/projects/codex/brain_explore/.worktrees/siyuan/  |

  # Example: Start session for Readest work
  cd /home/chris/dev/projects/codex/brain_explore/.worktrees/readest
  claude

  # Example: Start session for SiYuan work  
  cd /home/chris/dev/projects/codex/brain_explore/.worktrees/siyuan
  claude

  How to Know Where You Are

  # Shows current branch AND worktree path
  git worktree list

  # Quick check - which branch am I on?
  git branch --show-current

  # What's my working directory?
  pwd

  Common Pitfalls to Avoid

  | Pitfall                                | How to Avoid                               |
  |----------------------------------------|--------------------------------------------|
  | Editing files in wrong worktree        | Check pwd before starting work             |
  | Committing to wrong branch             | git branch --show-current before commit    |
  | Running git checkout                   | Don't - use cd to switch worktrees instead |
  | Confusion about which session is which | Keep separate terminal windows labeled     |

  Parallel Sessions Pattern

  Terminal 1 (main)           Terminal 2 (readest)        Terminal 3 (siyuan)
  ─────────────────           ────────────────────        ───────────────────
  cd brain_explore/           cd .worktrees/readest/      cd .worktrees/siyuan/
  claude                      claude                      claude
  → Phase 1 work              → Phase 2 work              → Phase 3 work

  When Ready to Merge

  # From main directory
  cd /home/chris/dev/projects/codex/brain_explore

  # Merge readest work
  git merge feature/readest-integration

  # Merge siyuan work (may have CLAUDE.md conflict - that's OK)
  git merge feature/siyuan-evolution

  # Resolve any conflicts, commit

  Cleanup (After Merge)

  # Remove worktrees when done
  git worktree remove .worktrees/readest
  git worktree remove .worktrees/siyuan

  # Delete branches if no longer needed
  git branch -d feature/readest-integration
  git branch -d feature/siyuan-evolution

  ---
  Key mental model: Think of worktrees as 3 separate project folders that happen to share git history. Each Claude session lives in one
  folder.


# Worktree Quick Reference

## Active Worktrees

| Directory | Branch | Purpose |
|-----------|--------|---------|
| `/home/chris/dev/projects/codex/brain_explore/` | `master` | Phase 1: API contracts |
| `.worktrees/readest/` | `feature/readest-integration` | Phase 2: Readest MVP |
| `.worktrees/siyuan/` | `feature/siyuan-evolution` | Phase 3: SiYuan plugin |

## Quick Commands

```bash
# Where am I?
pwd && git branch --show-current

# List all worktrees
git worktree list

# Start Claude session for specific phase
cd /home/chris/dev/projects/codex/brain_explore              # Phase 1
cd /home/chris/dev/projects/codex/brain_explore/.worktrees/readest  # Phase 2
cd /home/chris/dev/projects/codex/brain_explore/.worktrees/siyuan   # Phase 3
```

## Rules

1. **Don't `git checkout`** - change directories instead
2. **Check `pwd` before editing** - make sure you're in the right worktree
3. **Each terminal = one worktree** - don't mix
4. **Commit often** - each worktree has independent commits

## Merging (When Done)

```bash
# From main directory only
cd /home/chris/dev/projects/codex/brain_explore

git merge feature/readest-integration
git merge feature/siyuan-evolution
# Resolve CLAUDE.md conflicts by combining both updates
```

## Cleanup

```bash
git worktree remove .worktrees/readest
git worktree remove .worktrees/siyuan
git branch -d feature/readest-integration
git branch -d feature/siyuan-evolution
```
