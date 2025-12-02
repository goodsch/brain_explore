# Sync Documentation

Spawn the **scribe** agent to update documentation for the current session.

## Before spawning, gather this context:

1. **Active project**: Check `.active-project` or infer from current work
2. **Work summary**: Review what was accomplished this session
3. **Key decisions**: Any architectural or design choices made
4. **Next steps**: What should happen next
5. **Artifacts**: Files created/modified, commits made

## Then spawn the scribe agent:

```
Task(
  subagent_type: "scribe",
  description: "Update documentation for session",
  prompt: |
    Active project: {project}

    ## Work Summary
    {summary of what was accomplished}

    ## Key Decisions
    {decisions made and rationale}

    ## Next Steps
    {what should happen next}

    ## Artifacts
    {files changed, commits, etc.}

    Update progress.md and any relevant SiYuan notes.
)
```

## When to use /sync

- Before ending a session
- After completing a significant feature
- Before using /clear
- After a commit
- When you realize you should document something
