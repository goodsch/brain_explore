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
