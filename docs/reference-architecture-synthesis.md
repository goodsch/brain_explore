# Reference Architecture Synthesis Report

**Analysis Date:** 2025-12-02
**Scope:** Three reference projects analyzed for architectural patterns and lessons for brain_explore
**Mode:** Pattern extraction and application recommendations

---

## Executive Summary

After analyzing three production-grade Claude Code reference projects, clear patterns emerge for managing complexity, preventing configuration drift, and building sustainable systems. The most striking finding: **successful projects minimize configuration overhead** while **maximizing focused domain work**.

**Key Insight:** The best projects don't try to be everything. They pick ONE thing, do it exceptionally well, and provide clear patterns others can adapt.

**For brain_explore:** The path forward is consolidation, not expansion. The reference projects show that splitting attention across three conceptual layers (IES/Framework/Therapy) creates more problems than it solves.

---

## 1. Reference Projects Analyzed

### 1.1 Agentic AI Systems

**Repository:** https://github.com/ThibautMelen/agentic-ai-systems
**Purpose:** Educational documentation of agentic patterns
**Scale:** 49 markdown files, comprehensive workflows/agents/implementation guide
**Key Strength:** Crystal-clear taxonomy and decision trees

**What This Project Does Well:**
- **Single responsibility:** Pure documentation/education, no code to maintain
- **Hierarchical organization:** Foundations → Workflows → Agents → Implementation → Guides
- **Decision support:** Flowcharts for "which pattern should I use?"
- **Visual standards:** Consistent emojis, color schemes, Mermaid diagrams
- **Progressive disclosure:** High-level README → detailed sub-docs → reference materials
- **No configuration drift:** It's all markdown, no settings.json or hooks to maintain

**Configuration Approach:**
- Zero runtime configuration
- One README as entry point
- Everything else is reference material indexed from README
- Navigation is via hyperlinks, not slash commands or context switching

**Lessons for brain_explore:**
1. **Taxonomy serves discovery, not workflow:** The clean Baseline→Chaining→Routing→Parallel→Orchestrator→Evaluator progression is pedagogical, not operational
2. **Visual consistency reduces cognitive load:** Predictable emoji system (🏎️=baseline, ⛓️=chaining, etc.) creates instant recognition
3. **Decision trees > taxonomies:** "Quick Decision" flowchart gets you to the right pattern faster than browsing categories
4. **Reference, don't repeat:** Glossary defines terms once, everything links to it

### 1.2 Claude Code Infrastructure Showcase

**Repository:** https://github.com/ericbuess/claude-code-infrastructure-showcase
**Purpose:** Production-tested skills/hooks/agents from 6 months real use
**Scale:** 5 skills (49 total files), 6 hooks, 10 agents, 3 commands
**Key Strength:** Progressive disclosure via modular skills

**What This Project Does Well:**
- **500-line rule rigorously enforced:** Main SKILL.md <500 lines, resources/ for deep dives
- **Auto-activation that works:** skill-rules.json + two essential hooks
- **Tech stack awareness:** Frontend/backend skills explicitly state requirements (React+MUI, Express+Prisma)
- **Integration-first documentation:** CLAUDE_INTEGRATION_GUIDE.md teaches AI how to customize for users
- **Production-validated:** Everything extracted from real 50K+ line codebase

**Configuration Approach:**
```
.claude/
├── skills/
│   ├── skill-name/
│   │   ├── SKILL.md              # <500 lines, high-level
│   │   └── resources/            # Deep dives as needed
│   │       ├── topic-1.md
│   │       └── topic-2.md
│   └── skill-rules.json          # Single source of truth for triggers
├── hooks/
│   ├── skill-activation-prompt.* # Essential: auto-suggest skills
│   └── post-tool-use-tracker.sh  # Essential: track file changes
└── settings.json                 # Minimal: just hook references
```

**Critical Pattern - Two Essential Hooks:**
1. **UserPromptSubmit** (skill-activation-prompt): Suggests skills before Claude sees prompt
2. **PostToolUse** (post-tool-use-tracker): Tracks file changes for context

Everything else is optional. The system works with just these two + skill-rules.json.

**Lessons for brain_explore:**
1. **Progressive disclosure prevents bloat:** 500-line limit forces focus, resources/ for depth
2. **Auto-activation via rules, not proliferating commands:** One skill-rules.json beats 20 slash commands
3. **Tech stack explicit in every skill:** Frontend skill says "Requires React+MUI v7" upfront
4. **Customization happens at integration, not runtime:** Path patterns configured once when copying skill
5. **Essential vs Optional clearly marked:** Start with 2 hooks, add more only if needed

### 1.3 Claude Code Docs

**Repository:** https://github.com/ericbuess/claude-code-docs
**Purpose:** Local mirror of official docs with auto-update
**Scale:** ~20 doc files, auto-sync from Anthropic
**Key Strength:** Single-purpose utility with zero maintenance

**What This Project Does Well:**
- **One command, many uses:** `/docs` for everything (list, read, check sync, what's new)
- **Auto-update via single PreToolUse hook:** Checks GitHub before reading docs
- **Fixed installation location:** ~/.claude-code-docs (no "where should I put this?")
- **Platform-aware installer:** Detects macOS/Linux, checks dependencies, migrates old versions
- **Uninstall script included:** Complete removal, no orphaned files

**Configuration Approach:**
```
~/.claude-code-docs/           # Fixed location
├── docs/                      # Auto-synced markdown files
├── claude-docs-helper.sh      # All logic in one script
└── uninstall.sh              # Clean removal

~/.claude/
├── commands/docs.md          # Single command: Execute helper script
└── settings.json             # Single hook: PreToolUse Read → git pull
```

**The Installer Pattern:**
```bash
# Smart detection of old installations
find_existing_installations() {
    # Checks command file, settings.json hooks
    # Deduplicates paths
    # Returns list
}

# Safe migration
if old_install_exists; then
    fresh_install_at_new_location
    cleanup_old_safely
fi
```

**Lessons for brain_explore:**
1. **Fixed paths eliminate decisions:** ~/.claude-code-docs, not "where should I install?"
2. **One script handles everything:** No TypeScript + bash + JSON + markdown sprawl
3. **Migration built into installer:** Detects old versions, upgrades cleanly
4. **Uninstall is first-class:** Easy to remove when done
5. **Single command with flags:** `/docs -t hooks` beats `/docs-check` + `/docs-read hooks`

---

## 2. How Successful Projects Handle Complexity

### 2.1 The 500-Line Rule (Progressive Disclosure)

**Pattern:** Keep main files under 500 lines, use references for depth

**From Infrastructure Showcase:**
```
backend-dev-guidelines/
├── SKILL.md                    # 302 lines - overview + navigation
└── resources/
    ├── architecture-overview.md
    ├── routing-patterns.md
    ├── controller-patterns.md
    ├── service-patterns.md
    ├── repository-patterns.md
    ├── async-and-errors.md
    ├── validation.md
    ├── configuration.md
    ├── dependency-injection.md
    ├── testing-strategies.md
    ├── database-patterns.md
    └── complete-examples.md
```

**How it works:**
1. SKILL.md provides conceptual overview and quick reference
2. Resources are loaded only when needed ("see resources/routing-patterns.md for details")
3. Each resource <500 lines, focused on one topic
4. Table of contents in resources >100 lines

**Contrast with brain_explore:**
- Root CLAUDE.md: 246 lines
- Three sub-project CLAUDE.md: 56+59+61 = 176 lines
- Three progress files: 261+226+305 = 792 lines
- **Total:** 1,214 lines of configuration prose

**None** of these follow progressive disclosure. All are loaded eagerly.

### 2.2 Single Source of Truth Pattern

**Pattern:** One canonical file per concern, everything references it

**Infrastructure Showcase - skill-rules.json:**
```json
{
  "version": "1.0",
  "skills": {
    "skill-name": {
      "type": "domain|guardrail",
      "enforcement": "suggest|block",
      "priority": "high|medium|low",
      "promptTriggers": { ... },
      "fileTriggers": { ... }
    }
  }
}
```

All trigger logic in ONE file. Hooks read this, nothing duplicated.

**Contrast with brain_explore:**
- `.active-project` file (which project?)
- Root CLAUDE.md (what are the projects?)
- Sub-project CLAUDE.md files (what is each project?)
- progress.md files (what's the status?)
- Serena memories (what's the architecture?)

Same information in 5+ places. Synchronization nightmare.

### 2.3 Fixed Paths Eliminate Decisions

**Pattern:** Convention over configuration for locations

**Claude Code Docs:**
- Installation: Always `~/.claude-code-docs`
- Command: Always `.claude/commands/docs.md`
- Hook: Always PreToolUse → helper script

No "where should this go?" questions. No path variables. Just conventions.

**Agentic AI Systems:**
- Entry point: Always `README.md`
- Workflows: Always `workflows/`
- Implementation: Always `implementation/`

**Contrast with brain_explore:**
- "Which progress file should I update?"
- "Is this IES work or Framework work?"
- "Do I need to switch projects first?"
- "Should this be in Serena memory or CLAUDE.md?"

Every decision adds friction.

### 2.4 Minimal Configuration Surface Area

**Infrastructure Showcase - Essential Hooks:**
```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/skill-activation-prompt.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "Edit|MultiEdit|Write",
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-tracker.sh"
      }]
    }]
  }
}
```

That's it. Two hooks. System works. Optional hooks clearly marked as "customize if needed."

**Contrast with brain_explore:**
- 11 Serena memory files
- 4 CLAUDE.md files
- 3 progress files
- Multiple slash commands (/switch-project, /sc:load, /sc:save, /catchup, /handoff)
- Template files (mostly empty)

---

## 3. Configuration Patterns That Work

### 3.1 Hook-Based Auto-Activation

**How it works:**

```typescript
// skill-activation-prompt.ts (UserPromptSubmit hook)
const rules = JSON.parse(fs.readFileSync('skill-rules.json'));
const userPrompt = input.prompt;
const currentFiles = input.file_context || [];

for (const [skillName, config] of Object.entries(rules.skills)) {
  // Check keyword triggers
  const hasKeyword = config.promptTriggers.keywords.some(kw =>
    userPrompt.toLowerCase().includes(kw.toLowerCase())
  );

  // Check file path triggers
  const hasFileMatch = currentFiles.some(file =>
    config.fileTriggers.pathPatterns.some(pattern =>
      minimatch(file, pattern)
    )
  );

  if (hasKeyword || hasFileMatch) {
    suggestSkill(skillName);
  }
}
```

**Why this works:**
- Skills activate automatically based on context
- No manual "/use-skill backend-dev-guidelines" needed
- Configuration (skill-rules.json) separate from activation logic
- User just works, system suggests relevant skills

**Application to brain_explore:**

Instead of:
```
/switch-project ies
/sc:load
# ... now I can work on IES
```

Could be:
```
# User edits ies/backend/src/ies_backend/api/session.py
# → Hook detects Python + "backend" path
# → Suggests "ies-backend" skill automatically
# → Loads relevant context on demand
```

### 3.2 Path Pattern Configuration

**Infrastructure Showcase approach:**

```json
{
  "backend-dev-guidelines": {
    "fileTriggers": {
      "pathPatterns": [
        "blog-api/src/**/*.ts",
        "auth-service/src/**/*.ts",
        "backend/**/*.ts"
      ]
    }
  }
}
```

**CLAUDE_INTEGRATION_GUIDE.md teaches customization:**

> When integrating this skill:
> 1. Ask user about their project structure
> 2. Update pathPatterns to match their layout
> 3. Monorepo: ["packages/api/**/*.ts", "apps/backend/**/*.ts"]
> 4. Single app: ["src/**/*.ts", "backend/**/*.ts"]

**Key insight:** Configuration happens once at integration time, not every session.

**Application to brain_explore:**

Instead of three CLAUDE.md files determining "which project," use path patterns:

```json
{
  "ies-backend": {
    "fileTriggers": {
      "pathPatterns": ["ies/backend/**/*.py"]
    }
  },
  "ies-plugin": {
    "fileTriggers": {
      "pathPatterns": ["ies/plugin/**/*.{ts,tsx,svelte}"]
    }
  },
  "therapy-content": {
    "fileTriggers": {
      "pathPatterns": ["therapy/**/*.md"]
    }
  }
}
```

Skills activate based on what you're editing, not which "project" you declared active.

### 3.3 Command Design Patterns

**Good: Claude Code Docs**
```
/docs                  # List topics
/docs hooks            # Read specific topic
/docs -t              # Check sync status
/docs -t hooks        # Check sync, then read
/docs what's new      # Show recent changes
```

One command, multiple uses via arguments/flags.

**Bad: Hypothetical Over-Engineered**
```
/docs-list
/docs-read hooks
/docs-check-sync
/docs-sync-and-read hooks
/docs-show-changes
```

Five commands for five operations.

**Application to brain_explore:**

Current:
```
/switch-project ies
/switch-project framework
/switch-project therapy
/sc:load
/sc:save
/catchup
/handoff
```

Better:
```
/work                 # Smart session start (loads context based on current directory)
/work done           # Smart session end (saves context, offers handoff)
/work status         # What's been happening lately?
```

### 3.4 Installation and Migration Patterns

**Claude Code Docs installer:**

```bash
# 1. Detect old installations from configs
find_existing_installations() {
    # Parse ~/.claude/commands/docs.md for paths
    # Parse ~/.claude/settings.json for hook paths
    # Return deduplicated list
}

# 2. Migrate safely
if [[ -d "$INSTALL_DIR" ]]; then
    safe_git_update "$INSTALL_DIR"
else
    if [[ ${#existing_installs[@]} -gt 0 ]]; then
        migrate_installation "${existing_installs[0]}"
    else
        fresh_install
    fi
fi

# 3. Update configs to point to new location
update_command_file
update_hooks
cleanup_old_installations
```

**Key principles:**
1. Detect existing installations automatically
2. Migrate without losing work
3. Fixed target location (no "where do you want this?")
4. Clean up old installations safely
5. Idempotent (run multiple times safely)

---

## 4. Integration Patterns for MCP

### 4.1 MCP Server Pattern (Observed but not deeply documented)

From brain_explore's current setup:
- Serena MCP provides symbolic code navigation
- SiYuan MCP provides notebook operations
- Tavily/Arxiv MCPs provide research capabilities

**Best practice from reference projects:**
Skills reference MCP capabilities without hardcoding them.

**From Infrastructure Showcase - backend-dev-guidelines:**
```markdown
## Database Operations

Use the database service pattern:
- PrismaService wraps Prisma client
- Repositories extend PrismaService
- Services use repositories, never Prisma directly

Example: [See resources/repository-patterns.md]
```

The skill teaches patterns that work WITH tools (Prisma), not specific tool invocations.

### 4.2 MCP Tool Discovery Pattern

**None of the reference projects demonstrate this** because they're focused on Claude Code infrastructure, not MCP integration.

**Opportunity for brain_explore:**
Be the reference implementation for "how to integrate MCP servers into a complex project."

**Potential pattern:**
```json
// .claude/mcp-capabilities.json
{
  "serena": {
    "provides": ["code_navigation", "symbol_search", "refactoring"],
    "when": "working on Python/TypeScript code"
  },
  "siyuan": {
    "provides": ["note_storage", "block_operations", "entity_linking"],
    "when": "working on knowledge graph or content"
  }
}
```

Skill-rules.json could reference MCP capabilities, auto-suggesting skills that need those tools.

### 4.3 API Versioning Pattern

**From agentic-ai-systems (architectural documentation):**

Agents should:
1. Discover capabilities via introspection
2. Handle missing features gracefully
3. Version their contracts explicitly

**Application to brain_explore IES:**

```python
# ies/backend/src/ies_backend/schemas/api_version.py
class APICapabilities(BaseModel):
    version: str = "1.0.0"
    features: List[str] = [
        "profile_management",
        "session_tracking",
        "question_generation",
        "entity_extraction",
        "literature_linking"
    ]

@router.get("/api/capabilities")
async def get_capabilities() -> APICapabilities:
    """Clients query this to discover what's available."""
    return APICapabilities()
```

Framework layer queries this to know what IES can do, rather than assuming.

---

## 5. Anti-Patterns to Avoid

### 5.1 Configuration Proliferation

**Anti-pattern seen in brain_explore:**
```
.active-project              # Which project?
CLAUDE.md (root)            # What are the projects?
ies/CLAUDE.md               # What is IES?
framework/CLAUDE.md         # What is Framework?
therapy/CLAUDE.md           # What is Therapy?
ies/progress.md             # IES status
framework/progress.md       # Framework status
therapy/progress.md         # Therapy status
```

Same information, 8 files, constant sync burden.

**Good pattern from Infrastructure Showcase:**
```
skill-rules.json            # Triggers
SKILL.md                    # Content
resources/*.md              # Deep dives
```

Clear separation: triggers vs content vs details.

### 5.2 Taxonomy as Workflow

**Anti-pattern:**
Forcing work into predefined categories that don't match task granularity.

brain_explore's three-layer system:
- IES (generic framework)
- Framework (implementation instance)
- Therapy (content)

**Problem:** Real tasks cut across layers:
- "Add literature linking" touches all three
- "Fix iOS bug" is categorized as IES but needs Framework context
- "Develop concept" is Therapy but needs IES understanding

**Good pattern from Agentic AI Systems:**
Taxonomy for *discovery* (finding the right pattern), not workflow enforcement.

Their flowchart:
```
Task → Destructive? → Complex? → Predictable steps? → [Pattern choice]
```

Gets you to the right pattern without forcing you to "be in" that category.

### 5.3 Premature Generalization

**Anti-pattern from brain_explore:**
Building "Framework" layer before having a second implementation to justify it.

Current state:
- IES: Production-ready, therapy-focused
- Framework: Empty shell, config system not implemented
- Therapy: 4% of intended content

**YAGNI violation:** "You Aren't Gonna Need It"

**Good pattern from Infrastructure Showcase:**
Build for ONE real use case (their microservices app), then extract patterns others can adapt.

> "These aren't theoretical examples - they're extracted from 50,000+ lines of TypeScript"

### 5.4 Template Sprawl

**Anti-pattern from brain_explore:**
Empty template files that document features that don't exist:
- `.claude/templates/catchup.md` - entirely commented out
- `.claude/templates/handoff.md` - three options, no guidance
- `.claude/templates/exit-rules.md` - empty

**Good pattern:**
Templates are *examples*, not scaffolding. Infrastructure Showcase README:

```markdown
### Quick Start: Creating a New Skill

**Template:**
```markdown
---
name: my-new-skill
description: Brief description...
---

# My New Skill
## Purpose
## When to Use
## Key Information
```

Inline example, copy-paste ready, no separate template file to maintain.

### 5.5 Manual Context Loading

**Anti-pattern:**
Requiring "/sc:load" at session start to bulk-load Serena memories.

**Contradicts brain_explore's own global CLAUDE.md:**
> "Query when context is needed, don't bulk-load. Preserves context window for actual work."

**Good pattern from Infrastructure Showcase:**
Auto-activation via hooks. Context loads based on what you're doing, not manual commands.

---

## 6. Specific Recommendations for brain_explore

### 6.1 Consolidate Configuration

**Current state:** 422 lines across 4 CLAUDE.md files + 792 lines across 3 progress files

**Recommendation:** ONE CLAUDE.md, skill-based context

```
brain_explore/
├── CLAUDE.md                           # ~100 lines max
├── .claude/
│   ├── skills/
│   │   ├── ies-backend/
│   │   │   ├── SKILL.md               # IES backend development
│   │   │   └── resources/
│   │   │       ├── api-patterns.md
│   │   │       └── testing-guide.md
│   │   ├── ies-plugin/
│   │   │   └── SKILL.md               # SiYuan plugin development
│   │   ├── therapy-exploration/
│   │   │   └── SKILL.md               # Content development
│   │   └── skill-rules.json           # Triggers
│   └── hooks/
│       ├── skill-activation.sh
│       └── context-tracker.sh
└── .work/
    └── session-notes.md               # Replaces 3 progress files
```

**Migration:**
1. Extract IES patterns from ies/CLAUDE.md → skills/ies-backend/SKILL.md
2. Extract Therapy approach from therapy/CLAUDE.md → skills/therapy-exploration/SKILL.md
3. Framework layer: Delete. It's premature.
4. Progress files: Consolidate into single session-notes.md
5. skill-rules.json defines when each skill activates

### 6.2 Implement Auto-Activation

**Current:** Manual project switching and memory loading

**Recommendation:** Hook-based activation like Infrastructure Showcase

```bash
# .claude/hooks/skill-activation.sh
# Reads skill-rules.json
# Checks user prompt + current file paths
# Suggests relevant skills automatically

# Example triggers:
# Editing ies/backend/src/ies_backend/api/*.py
#   → Suggests "ies-backend" skill
# Editing therapy/**/*.md
#   → Suggests "therapy-exploration" skill
# Prompt contains "entity extraction" or "session flow"
#   → Suggests "ies-backend" skill
```

### 6.3 Apply Progressive Disclosure

**Current:** Bulk-loading via /sc:load

**Recommendation:** Lazy loading via references

```markdown
# skills/ies-backend/SKILL.md

## Architecture

IES uses a three-tier architecture:
- API layer: FastAPI endpoints
- Service layer: Business logic
- Storage layer: Neo4j + Qdrant

For detailed API patterns, see [resources/api-patterns.md]
For testing strategies, see [resources/testing-guide.md]
```

Claude loads main SKILL.md (~300 lines), then resources only when needed.

### 6.4 Eliminate Active-Project System

**Current:** `.active-project` file + /switch-project command

**Recommendation:** Path-based skill activation

Work on what you want. Skills activate based on file paths and prompt content.

No "which project am I in?" question. No switching. Just edit files.

### 6.5 Consolidate Progress Tracking

**Current:** Three progress.md files (792 total lines)

**Recommendation:** Single session-notes.md with date-based entries

```markdown
# Session Notes

## 2025-12-02 - Entity Linking Implementation

**Context:** Adding literature linking to entity extraction

**Progress:**
- Implemented literature_service.py
- Added API endpoint /api/entities/{id}/link-literature
- Tests passing

**Next:**
- Frontend UI for link management
- Update SiYuan plugin to display links

## 2025-12-01 - Question Engine Refinement

**Context:** Improving question generation quality
...
```

Append-only log. No need to maintain three separate files in sync.

### 6.6 MCP Integration as Reference Implementation

**Opportunity:** None of the reference projects show MCP integration

**Recommendation:** brain_explore could be the reference for MCP-heavy projects

```
.claude/
├── mcp-servers.json              # Which servers are available
├── skills/
│   └── ies-backend/
│       └── SKILL.md
│           → "Uses Serena MCP for code navigation"
│           → "Uses SiYuan MCP for note storage"
└── hooks/
    └── mcp-capability-check.sh   # Verifies required servers
```

**Pattern to demonstrate:**
- How to document MCP dependencies in skills
- How to gracefully handle missing MCP servers
- How to version MCP tool usage

### 6.7 Apply 500-Line Rule

**Current:**
- No SKILL.md file exceeds 500 lines (doesn't exist yet)
- But CLAUDE.md files don't follow progressive disclosure

**Recommendation:**
```
skills/ies-backend/
├── SKILL.md                      # <500 lines
│   - Quick reference for common operations
│   - Links to resources for deep dives
└── resources/
    ├── api-design-patterns.md    # <500 lines
    ├── testing-strategies.md     # <500 lines
    ├── neo4j-operations.md       # <500 lines
    └── plugin-communication.md   # <500 lines
```

Each file focused, digestible, discoverable via main SKILL.md.

---

## 7. Concrete Examples from Reference Projects

### 7.1 Skill Structure (Infrastructure Showcase)

**From skill-developer/SKILL.md:**

```markdown
---
name: skill-developer
description: Create and manage Claude Code skills following Anthropic best practices...
---

# Skill Developer Guide

## Purpose
Comprehensive guide for creating skills with auto-activation

## When to Use This Skill
Automatically activates when you mention:
- Creating or adding skills
- Modifying skill triggers
- Understanding skill activation

## System Overview
[Brief explanation of hook architecture]

## Quick Start: Creating a New Skill
[Step-by-step with code examples]

## Resource Files
- [SKILL_RULES_REFERENCE.md](resources/...) - Complete schema
- [TRIGGER_TYPES.md](resources/...) - Trigger patterns
- [HOOK_MECHANISMS.md](resources/...) - How hooks work
```

**Note:** 426 lines total. Under 500-line limit. 7 resource files for depth.

### 7.2 Agent Structure (Infrastructure Showcase)

**From code-architecture-reviewer.md:**

```yaml
---
name: code-architecture-reviewer
description: |
  Use when you need to review recently written code for adherence to
  best practices, architectural consistency, and system integration.

  Examples:
  - "I've added a new API endpoint to the form service"
  - "I've finished implementing the WorkflowStepCard component"

model: sonnet
color: blue
---

You are an expert software engineer specializing in code review...

When reviewing code, you will:

1. **Analyze Implementation Quality**
   - Verify TypeScript strict mode
   - Check error handling
   [...]

2. **Question Design Decisions**
   - Challenge non-standard implementations
   [...]

8. **Return to Parent Process**
   - Save review to ./dev/active/[task]/[task]-code-review.md
   - Inform parent: "Code review saved to: ..."
   - Wait for explicit approval before fixes
```

**Note:**
- YAML frontmatter with clear description
- Examples in description show when to use
- Explicit "return to parent" protocol
- Saves output to predictable location

### 7.3 Hook Configuration (Infrastructure Showcase)

**From .claude/hooks/skill-activation-prompt.ts:**

```typescript
interface SkillRule {
  type: 'domain' | 'guardrail';
  enforcement: 'suggest' | 'block';
  priority: 'high' | 'medium' | 'low';
  promptTriggers?: {
    keywords?: string[];
    intentPatterns?: string[];
  };
  fileTriggers?: {
    pathPatterns?: string[];
    contentPatterns?: string[];
  };
}

// Read skill-rules.json once
const skillRules = JSON.parse(
  fs.readFileSync('.claude/skills/skill-rules.json', 'utf-8')
);

// Check each skill
for (const [skillName, rule] of Object.entries(skillRules.skills)) {
  if (shouldActivate(rule, userPrompt, currentFiles)) {
    console.log(`\n📚 Suggested Skill: ${skillName}`);
    console.log(`   Reason: ${getActivationReason(rule)}`);
  }
}
```

**Note:**
- Single source of truth (skill-rules.json)
- Clean separation: logic vs configuration
- Activation reason shown to user

### 7.4 Command Pattern (Claude Code Docs)

**From .claude/commands/docs.md:**

```markdown
Execute the Claude Code Docs helper script

Usage:
- /docs - List all available topics
- /docs <topic> - Read specific documentation
- /docs -t - Check sync status
- /docs -t <topic> - Check freshness then read
- /docs whats new - Show recent changes

Examples of expected output:
[Shows exactly what user will see]

Execute: ~/.claude-code-docs/claude-docs-helper.sh "$ARGUMENTS"
```

**Note:**
- One command, multiple uses
- Shows expected output (sets expectations)
- All logic in external script (testable, maintainable)

---

## 8. How to Structure for Flow Mode, Self-Understanding, Therapeutic Dialogue

### 8.1 The Vision (from Meta-Analysis)

brain_explore aims to combine three capabilities:
1. **Flow Mode** - Non-linear navigation through knowledge graphs
2. **Self-Understanding** - Help users recognize their thinking patterns
3. **Therapeutic Dialogue** - Context-aware questioning based on patterns

**Current problem:** Project is 96% infrastructure, 4% content

**Reference project lesson:** Build for ONE use case first, then extract patterns

### 8.2 Flow Mode Architecture

**What Flow Mode needs:**
- Entity-to-entity navigation (exists: Neo4j graph)
- Literature backing (exists: 63 books ingested)
- AI-generated summaries (exists: entity extraction)
- Mobile-friendly UI (exists: SiYuan plugin)

**What Flow Mode does NOT need:**
- Framework layer (premature)
- Project switching system (wrong abstraction)
- Three separate CLAUDE.md files (overhead)

**Recommended structure:**

```
brain_explore/
├── backend/                    # Renamed from ies/backend
│   ├── src/
│   │   ├── api/               # Session, entities, questions
│   │   ├── services/          # Graph ops, question engine
│   │   └── flows/             # NEW: Flow Mode specific
│   │       ├── navigation.py  # Entity graph traversal
│   │       └── summary.py     # AI summarization
│   └── tests/
├── plugin/                     # Renamed from ies/plugin
│   └── src/
│       └── flows/             # Flow Mode UI
├── content/                    # Renamed from therapy/
│   └── concepts/              # The actual therapeutic content
├── .claude/
│   ├── skills/
│   │   ├── backend-dev/
│   │   ├── plugin-dev/
│   │   └── content-dev/
│   └── hooks/
└── CLAUDE.md                   # Single config file
```

**Flow Mode skill:**

```markdown
---
name: flow-mode-dev
description: Flow Mode navigation and visualization
---

# Flow Mode Development

## Purpose
Non-linear navigation through knowledge graphs with AI summaries

## Architecture
- Backend: Graph traversal (Neo4j)
- Plugin: Interactive visualization (SiYuan)
- Content: Therapeutic concepts (entities)

## Common Operations
- Add new entity type
- Improve navigation algorithms
- Enhance summary generation

See [resources/navigation-patterns.md] for graph traversal details
See [resources/visualization.md] for UI patterns
```

### 8.3 Self-Understanding Architecture

**What Self-Understanding needs:**
- Pattern recognition (needs: NLP analysis of user writing)
- Thinking style categorization (needs: psychological models)
- Reflection prompts (needs: question generation)

**Current state:** Concept exists, not implemented

**Recommended approach:**

Don't build as separate layer. It's a *feature* of Flow Mode.

```python
# backend/src/services/pattern_recognition.py

class ThinkingPatternRecognizer:
    """Analyzes user's exploration patterns to identify thinking styles."""

    def analyze_session(self, session_id: str) -> ThinkingProfile:
        """
        Looks at:
        - Which entities user explores
        - How they navigate (linear vs branching)
        - Questions they ask
        - Concepts they relate

        Returns profile: analytical, intuitive, systematic, etc.
        """
        pass
```

**Integration with Flow Mode:**
As user navigates graph, backend tracks patterns → Surfaces insights in plugin UI

**Skill structure:**

```markdown
# skills/self-understanding/SKILL.md

## Pattern Recognition
User's navigation patterns reveal thinking style

## Implementation
- Track navigation in session log
- Analyze path patterns (linear, branching, circular)
- Identify concept affinity (abstract vs concrete)
- Generate reflection prompts

See [resources/pattern-taxonomy.md] for thinking style categories
See [resources/analysis-algorithms.md] for detection methods
```

### 8.4 Therapeutic Dialogue Architecture

**What Therapeutic Dialogue needs:**
- User profile (exists: profile_service)
- Question generation (exists: question_engine)
- Context-awareness (exists: session tracking)
- Therapeutic models (needs: content development)

**Current state:** Infrastructure complete, content 4% done

**Recommended focus:**

Stop building infrastructure. Develop content.

```
content/
├── tracks/
│   ├── 01-human-mind/
│   │   ├── concepts/
│   │   │   ├── attachment-theory.md
│   │   │   ├── cognitive-distortions.md
│   │   │   └── defense-mechanisms.md
│   │   └── questions/
│   │       └── attachment-exploration.md
│   ├── 02-therapeutic-change/
│   └── 03-integration/
└── models/
    ├── person-centered.md
    ├── cognitive-behavioral.md
    └── psychodynamic.md
```

**Content development skill:**

```markdown
# skills/content-dev/SKILL.md

## Purpose
Develop therapeutic worldview concepts grounded in literature

## Process
1. Identify concept from reading
2. Extract key ideas
3. Connect to knowledge graph
4. Generate exploration questions
5. Link to therapeutic models

## Resources
- [Book processing workflow](resources/literature-workflow.md)
- [Concept template](resources/concept-template.md)
- [Question design](resources/question-patterns.md)
```

**Key insight from reference projects:**

Infrastructure Showcase spent 6 months building tools, THEN documented patterns.
Agentic AI Systems documented patterns from Anthropic research.
Claude Code Docs mirrors official docs.

brain_explore has 96% of infrastructure done. **Time to shift to content.**

### 8.5 Integration Pattern

**How Flow Mode + Self-Understanding + Therapeutic Dialogue work together:**

```
User starts session
    ↓
Backend activates profile
    ↓
User navigates entities (Flow Mode)
    ↓
Backend tracks navigation patterns (Self-Understanding)
    ↓
Backend generates reflection questions based on patterns (Therapeutic Dialogue)
    ↓
Plugin displays questions in context
    ↓
User responds
    ↓
Backend refines profile
    ↓
Next session: Better questions, more relevant navigation
```

**This is ONE system, not three projects.**

**Recommended skill organization:**

```
.claude/skills/
├── backend-api/          # General backend development
├── plugin-ui/            # SiYuan plugin development
├── flow-navigation/      # Flow Mode features
├── pattern-recognition/  # Self-Understanding features
├── question-design/      # Therapeutic Dialogue features
└── content-development/  # Writing therapeutic concepts
```

Path-based activation means working on flow navigation code → flow-navigation skill loads.

---

## 9. Summary of Lessons

### 9.1 Configuration Management

**Do:**
- ✅ Single CLAUDE.md <200 lines
- ✅ Skill-rules.json for triggers
- ✅ Progressive disclosure (main skill + resources)
- ✅ Fixed paths (conventions over configuration)
- ✅ Auto-activation via hooks

**Don't:**
- ❌ Multiple CLAUDE.md files fighting for authority
- ❌ Manual context loading commands
- ❌ Empty template files
- ❌ Configuration that duplicates information
- ❌ Project switching systems for single-repo work

### 9.2 Skill Design

**Do:**
- ✅ Keep main SKILL.md <500 lines
- ✅ Use resources/ for deep dives
- ✅ Explicit tech stack requirements
- ✅ Examples in YAML frontmatter description
- ✅ Clear "When to use" section

**Don't:**
- ❌ Monolithic skills >1000 lines
- ❌ Assuming user's tech stack matches yours
- ❌ Vague trigger descriptions
- ❌ Skills that try to cover everything
- ❌ Duplicating content across skills

### 9.3 Hook Architecture

**Do:**
- ✅ Two essential hooks (UserPromptSubmit, PostToolUse)
- ✅ Read configuration from JSON
- ✅ Provide clear activation reasons
- ✅ Mark optional hooks clearly
- ✅ Test hooks independently

**Don't:**
- ❌ Hardcode trigger logic in hook scripts
- ❌ Block workflow unless absolutely necessary
- ❌ Hooks that duplicate slash command functionality
- ❌ Complex hook dependencies
- ❌ Hooks without clear purpose

### 9.4 Agent Design

**Do:**
- ✅ Clear role definition in YAML frontmatter
- ✅ Examples showing when to invoke
- ✅ Explicit "return to parent" protocol
- ✅ Predictable output locations
- ✅ Wait for approval before making changes

**Don't:**
- ❌ Agents that auto-fix without asking
- ❌ Vague agent descriptions
- ❌ Agents that try to do everything
- ❌ Output saved in random locations
- ❌ No protocol for returning control

### 9.5 Project Organization

**Do:**
- ✅ Single purpose per component
- ✅ Clear navigation from README
- ✅ Progressive disclosure of complexity
- ✅ Visual consistency (emojis, color schemes)
- ✅ Decision trees for "which pattern?"

**Don't:**
- ❌ Organizational taxonomy as workflow
- ❌ Splitting before you have 2+ use cases
- ❌ Configuration per sub-project
- ❌ Manual switching between "modes"
- ❌ Premature generalization

---

## 10. Action Plan for brain_explore

### Phase 1: Consolidation (1-2 hours)

1. **Merge CLAUDE.md files**
   - Extract useful bits from sub-project CLAUDE.md
   - Single root CLAUDE.md ~150 lines
   - Delete ies/framework/therapy CLAUDE.md files

2. **Consolidate progress tracking**
   - Create .work/session-notes.md
   - Append-only log format
   - Archive old progress files

3. **Remove Framework layer**
   - It's empty and premature
   - Move any useful docs to main docs/
   - Delete framework/ directory

4. **Simplify directory structure**
   - ies/backend → backend/
   - ies/plugin → plugin/
   - therapy/ → content/

### Phase 2: Skill Creation (2-3 hours)

1. **Create skill structure**
   ```
   .claude/skills/
   ├── backend-dev/SKILL.md
   ├── plugin-dev/SKILL.md
   ├── content-dev/SKILL.md
   └── skill-rules.json
   ```

2. **Populate skills from existing docs**
   - backend-dev from ies/CLAUDE.md + Serena memories
   - plugin-dev from SiYuan integration notes
   - content-dev from therapy/CLAUDE.md

3. **Create skill-rules.json**
   ```json
   {
     "backend-dev": {
       "fileTriggers": {
         "pathPatterns": ["backend/**/*.py"]
       }
     },
     "plugin-dev": {
       "fileTriggers": {
         "pathPatterns": ["plugin/**/*.{ts,tsx,svelte}"]
       }
     },
     "content-dev": {
       "fileTriggers": {
         "pathPatterns": ["content/**/*.md"]
       }
     }
   }
   ```

### Phase 3: Hook Implementation (1-2 hours)

1. **Adapt skill-activation hook from Infrastructure Showcase**
   - Copy skill-activation-prompt.sh/.ts
   - Point at brain_explore skill-rules.json
   - Test activation

2. **Add post-tool-use tracker**
   - Copy post-tool-use-tracker.sh
   - Tracks edited files for context

3. **Update settings.json**
   - Two hooks only
   - Remove manual loading commands

### Phase 4: Content Focus (Ongoing)

1. **Stop infrastructure work**
   - Backend is production-ready
   - Plugin exists and works
   - No more "framework" development

2. **Start content development**
   - Work in content/ directory
   - content-dev skill auto-activates
   - Build therapeutic concepts

3. **Use system while building**
   - Flow Mode works now
   - Generate real sessions
   - Iterate on question quality based on use

### Phase 5: Reference Implementation (Future)

Once content is substantial:

1. **Document MCP integration patterns**
   - How IES uses Serena, SiYuan, Tavily MCPs
   - Become reference for MCP-heavy projects

2. **Extract reusable patterns**
   - THEN create framework layer
   - After proving with second use case
   - Not before

---

## 11. Conclusion

The reference projects reveal a consistent pattern: **successful Claude Code projects minimize configuration overhead and maximize focused work.**

**Key takeaway:** brain_explore's three-layer system (IES/Framework/Therapy) creates more problems than it solves. The infrastructure is 96% complete but configuration overhead is preventing content development.

**Recommendation:** Consolidate to single-layer system with skill-based specialization. Stop building infrastructure. Start developing content.

**The path forward:**
1. Merge configuration (4 CLAUDE.md → 1)
2. Implement auto-activation (no manual switching)
3. Apply progressive disclosure (skills + resources)
4. Focus on content (therapeutic concepts)
5. Use the system (real sessions, real insights)

Once you have substantial content AND a second use case, THEN extract framework patterns. Not before.

**brain_explore can be a reference implementation for:**
- MCP-heavy projects (Serena, SiYuan, Tavily integration)
- Knowledge graph exploration systems
- AI-guided content development workflows

But only after proving the patterns work for the first use case (therapeutic worldview exploration).

---

**End of Report**

