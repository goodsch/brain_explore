# Multi-Agent Orchestration System Design

**Date:** 2025-12-01
**Status:** Implemented
**Updated:** 2025-12-01 - Added 5 additional agents based on usage analysis
**Problem:** Stop hooks for documentation are brittle; context management is manual and error-prone

## Executive Summary

Replace reactive stop hooks with a proactive multi-agent orchestration system where specialized agents handle documentation, context management, and quality gates as first-class tasks rather than afterthoughts.

## Problems Being Solved

1. **Documentation gaps** - Stop hook fires too late, context is compressed, user is rushing
2. **Context management burden** - Manual loading of memories, progress files, project state
3. **Quality inconsistency** - No systematic review checkpoints
4. **Cognitive load** - User must remember to document, save context, request reviews

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SESSION START (Hook)                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Context Agent (Haiku) - Automatic context loading       │    │
│  │  • Reads .active-project                                │    │
│  │  • Loads relevant progress.md + CLAUDE.md               │    │
│  │  • Queries Serena memories + SiYuan                     │    │
│  │  • Loads backend context (if exploration)               │    │
│  │  → Outputs: Injected context summary                    │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    MAIN ORCHESTRATOR (Opus)                     │
│  • Receives user requests                                       │
│  • Decomposes into tasks                                        │
│  • Maintains TodoWrite state                                    │
│  • Routes to specialist agents                                  │
│  • Synthesizes results                                          │
│  • Triggers documentation at natural breakpoints                │
└─────────────────────────────────────────────────────────────────┘
         │         │         │         │         │         │
         ↓         ↓         ↓         ↓         ↓         ↓
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
    │Reviewer│ │Debugger│ │ Scribe │ │Session │ │Backend │ │Entity  │
    │(Sonnet)│ │(Sonnet)│ │(Haiku) │ │ Guide  │ │  Ops   │ │Manager │
    └────────┘ └────────┘ └────────┘ │(Sonnet)│ │(Haiku) │ │(Haiku) │
                                     └────────┘ └────────┘ └────────┘
```

## Agent Inventory

| Agent | Model | Purpose |
|-------|-------|---------|
| context-loader | Haiku | Load full context at session start |
| scribe | Haiku | Update documentation (progress.md, SiYuan, Serena) |
| reviewer | Sonnet | Code review before completion |
| debugger | Sonnet | Systematic debugging with root cause analysis |
| backend-ops | Haiku | Start services, health checks, infrastructure |
| entity-manager | Haiku | Query entities, create SiYuan pages |
| session-guide | Sonnet | Guide exploration sessions with Question Engine |
| project-switcher | Haiku | Switch projects with full context handoff |

## Agent Definitions

### 1. Context Agent (SessionStart)

**Purpose:** Automatically load relevant context at session start

**Trigger:** SessionStart hook (startup, resume, clear, compact)

**Model:** Haiku (fast, cheap)

**Responsibilities:**
- Read `.active-project` to determine current project
- Load `{project}/progress.md` for recent state
- Query Serena memories matching project
- Search episodic memory for recent related conversations
- Synthesize into compact context injection

**Output:** Structured context summary injected into session

```yaml
# .claude/agents/context-loader.md
---
name: context-loader
description: Loads project context at session start - progress files, memories, recent work
model: haiku
tools: Read, Glob, mcp__serena__list_memories, mcp__serena__read_memory, mcp__plugin_episodic-memory_episodic-memory__search
---

You are a context loader. Your job is to quickly gather relevant context for a new session.

Given the working directory, determine:
1. Which project is active (check .active-project or infer from path)
2. Load the project's progress.md
3. Check for relevant Serena memories
4. Search episodic memory for recent related conversations

Output a structured summary:
- Active project
- Recent work (from progress.md)
- Key decisions/context (from memories)
- Continuation points (from episodic memory)

Be concise. This context will be injected into the main session.
```

### 2. Scribe Agent (Documentation)

**Purpose:** Update documentation at natural breakpoints

**Triggers:**
- After commits
- After feature completion
- After significant debugging sessions
- Before context clears
- On explicit `/sync` command

**Model:** Haiku (cheap, can run frequently)

**Responsibilities:**
- Update project progress.md with session work
- Create/update SiYuan notes for significant findings
- Write Serena memories for architectural decisions
- Summarize context before compaction

**Output:** Updated documentation files

```yaml
# .claude/agents/scribe.md
---
name: scribe
description: Updates documentation - progress files, SiYuan notes, Serena memories. Spawn after commits, feature completion, or before context clears.
model: haiku
tools: Read, Write, Edit, mcp__siyuan-mcp__*, mcp__serena__write_memory
---

You are a documentation scribe. Given a summary of work done, update the appropriate documentation:

## Input (provided by orchestrator)
- Active project (ies/framework/therapy)
- Work summary (what was accomplished)
- Key decisions made
- Next steps identified

## Actions

### 1. Progress File
Update `{project}/progress.md`:
- Add dated entry with work summary
- Note any blockers or decisions
- List next steps

### 2. SiYuan (if significant)
For architectural decisions or discoveries:
- Create/update note in appropriate notebook
- Link to related concepts

### 3. Serena Memory (if architectural)
For decisions that affect future sessions:
- Write memory with clear name
- Include rationale and alternatives considered

Be concise. Documentation should be scannable.
```

### 3. Reviewer Agent (Quality Gate)

**Purpose:** Review code changes before completion

**Triggers:**
- After implementation tasks
- Before merging branches
- On explicit `/review` command

**Model:** Sonnet (needs reasoning capability)

**Responsibilities:**
- Review changes against requirements/plan
- Check for obvious bugs
- Verify test coverage
- Assess production readiness

**Output:** Structured review with severity-rated issues

```yaml
# .claude/agents/reviewer.md
---
name: reviewer
description: Reviews code changes for quality, security, and requirements compliance. Use after implementation tasks or before merges.
model: sonnet
tools: Read, Grep, Glob, Bash
---

You are a code reviewer. Review the provided changes for production readiness.

## Input (provided by orchestrator)
- What was implemented
- Requirements or plan reference
- Git range to review (base..head)

## Review Process

1. Read the requirements/plan
2. Review changed files
3. Check for:
   - Requirements compliance
   - Obvious bugs
   - Security issues
   - Test coverage
   - Code style consistency

## Output Format

### Strengths
[Specific positives with file:line references]

### Issues

#### Critical (Must Fix)
[Blocking issues]

#### Important (Should Fix)
[Significant issues]

#### Minor (Nice to Have)
[Polish items]

### Assessment
**Ready to merge:** Yes / No / With fixes
**Reasoning:** [1-2 sentences]
```

### 4. Coder Agent (Implementation)

**Purpose:** Focused implementation of specific tasks

**Triggers:**
- When orchestrator decomposes work
- For parallelizable implementation tasks

**Model:** Sonnet (primary coding model)

**Responsibilities:**
- Implement specific, bounded tasks
- Write tests
- Follow existing patterns
- Report back with summary

```yaml
# .claude/agents/coder.md
---
name: coder
description: Implements specific coding tasks. Give it a bounded task with clear requirements.
model: sonnet
tools: Read, Write, Edit, Bash, Grep, Glob
---

You are an implementation specialist. Complete the assigned task following existing patterns.

## Input (provided by orchestrator)
- Task description
- Relevant files/context
- Constraints

## Process

1. Understand the task fully
2. Read relevant existing code
3. Implement following existing patterns
4. Write/update tests
5. Verify implementation works

## Output

Report back with:
- What you implemented
- Files changed
- Test results
- Any issues encountered
```

## Orchestration Patterns

### Pattern 1: Session Lifecycle

```
SessionStart Hook
       ↓
Context Agent (Haiku)
  • Load .active-project
  • Load progress.md
  • Query memories
       ↓
Context Injected → Main Session Begins
       ↓
[... work happens ...]
       ↓
Natural Breakpoint (commit, feature done, etc.)
       ↓
Scribe Agent (Haiku)
  • Update progress.md
  • Update SiYuan
  • Write memories
       ↓
Continue or End Session
```

### Pattern 2: Implementation Flow

```
User Request
     ↓
Orchestrator Analyzes
     ↓
TodoWrite (plan tasks)
     ↓
For each task:
  ├─> Coder Agent (implement)
  ├─> Reviewer Agent (review)
  ├─> Fix if needed
  └─> Mark complete
     ↓
All tasks done
     ↓
Scribe Agent (document)
     ↓
Report to user
```

### Pattern 3: Context Management

```
Context Getting Large (>40k tokens)
     ↓
Scribe Agent (summarize current state)
  • Write progress.md update
  • Write Serena memory if needed
     ↓
/clear (or auto-compact)
     ↓
Context Agent (reload essentials)
     ↓
Continue with fresh context
```

## Triggers and Automation

### Hook-Based Triggers

```jsonc
// .claude/settings.json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "startup|resume",
      "hooks": [{
        "type": "command",
        "command": ".claude/hooks/spawn-context-agent.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": ".claude/hooks/check-commit.sh"
        // If commit detected, signal to spawn Scribe
      }]
    }]
  }
}
```

### Instruction-Based Triggers (CLAUDE.md)

```markdown
## Automatic Documentation

After completing any of the following, spawn the Scribe agent:
- Git commits
- Feature implementation
- Significant debugging session
- Before using /clear

The Scribe agent will update progress.md and relevant documentation.
```

### Explicit Commands

```markdown
# .claude/commands/sync.md
Spawn the Scribe agent to update documentation for the current session.

Provide context:
- Active project
- Summary of work done this session
- Key decisions made
- Next steps
```

## File Structure

```
.claude/
├── agents/
│   ├── context-loader.md    # Session start context
│   ├── scribe.md            # Documentation updates
│   ├── reviewer.md          # Code review
│   └── coder.md             # Implementation
├── commands/
│   ├── sync.md              # Trigger Scribe manually
│   └── review.md            # Trigger Reviewer manually
├── hooks/
│   ├── spawn-context-agent.sh
│   └── check-commit.sh
└── settings.json
```

## Context Communication

Agents communicate through:

1. **Structured prompts** - Orchestrator fills templates with context
2. **File handoffs** - Write to known locations, other agents read
3. **Return values** - Structured output returned to orchestrator

Example orchestrator → scribe handoff:

```markdown
## Session Summary for Scribe

**Project:** ies
**Date:** 2025-12-01

### Work Completed
- Implemented multi-agent orchestration design
- Created agent definitions for context-loader, scribe, reviewer, coder
- Wrote design document

### Key Decisions
- Haiku for cheap/frequent agents (context, scribe)
- Sonnet for reasoning agents (reviewer, coder)
- Hook + instruction hybrid for triggers

### Next Steps
- Implement the agent files
- Test context loading flow
- Integrate with existing SessionStart hook
```

## Migration Path

### Phase 1: Add Agents (No Breaking Changes)
1. Create `.claude/agents/` directory
2. Add agent definitions
3. Add `/sync` command
4. Test manual invocation

### Phase 2: Integrate Hooks
1. Update SessionStart to spawn Context Agent
2. Remove Stop hook (documentation guardian)
3. Add PostToolUse hook for commit detection

### Phase 3: Refine Instructions
1. Update CLAUDE.md with orchestration patterns
2. Add triggers for automatic Scribe spawning
3. Tune based on real usage

## Success Metrics

- **Documentation coverage:** Progress files updated after every significant session
- **Context load time:** <5 seconds to load relevant context
- **Cognitive load:** User doesn't need to remember to document
- **Quality:** Code reviewed before completion

## Open Questions

1. **PreCompact hook:** Should Scribe auto-spawn before compaction?
2. **SiYuan integration depth:** How much should auto-sync to notes?
3. **Parallel vs. sequential:** When to parallelize agents?
4. **Cost:** How often can Haiku agents run before cost matters?

## References

- [Claude Code Subagents Docs](https://code.claude.com/docs/en/sub-agents)
- [Superpowers Plugin Patterns](https://github.com/superpowers-marketplace)
- [ThibautMelen/agentic-ai-systems](https://github.com/ThibautMelen/agentic-ai-systems)
