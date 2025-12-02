#!/bin/bash
# SessionStart hook: Load active project context
# Runs on: startup, resume, clear, compact

PROJECT_DIR="$CLAUDE_PROJECT_DIR"
ACTIVE_FILE="$PROJECT_DIR/.active-project"

# Default to ies if no active project set
if [[ -f "$ACTIVE_FILE" ]]; then
    ACTIVE_PROJECT=$(cat "$ACTIVE_FILE" | tr -d '[:space:]')
else
    ACTIVE_PROJECT="ies"
fi

# Validate project
case "$ACTIVE_PROJECT" in
    ies|framework|therapy)
        ;;
    *)
        ACTIVE_PROJECT="ies"
        ;;
esac

# Get progress file path and extract recent context
PROGRESS_FILE="$PROJECT_DIR/$ACTIVE_PROJECT/progress.md"
RECENT_WORK=""

if [[ -f "$PROGRESS_FILE" ]]; then
    # Get last session header and first few lines
    RECENT_WORK=$(head -50 "$PROGRESS_FILE" | grep -A5 "^## " | head -10 | tr '\n' ' ' | sed 's/  */ /g')
fi

# Project-specific notebook IDs
case "$ACTIVE_PROJECT" in
    ies)
        PROJECT_DESC="IES Framework Development"
        NOTEBOOK_ID="20251201113102-ctr4bco"
        ;;
    framework)
        PROJECT_DESC="Framework Project"
        NOTEBOOK_ID="20251130004638-unaugyc"
        ;;
    therapy)
        PROJECT_DESC="Therapy Framework"
        NOTEBOOK_ID="20251130004638-cm5m9g8"
        ;;
esac

# Output context
cat << EOF
{
  "additionalContext": "## Multi-Agent Orchestration Active\\n\\n**Project:** $ACTIVE_PROJECT ($PROJECT_DESC)\\n**SiYuan Notebook:** $NOTEBOOK_ID\\n\\n### Available Agents\\n| Agent | Model | Use For |\\n|-------|-------|---------|\\n| context-loader | Haiku | Load full context at session start |\\n| scribe | Haiku | Update docs after work (progress, SiYuan, Serena) |\\n| reviewer | Sonnet | Code review before completion |\\n| debugger | Sonnet | Systematic debugging with root cause analysis |\\n| backend-ops | Haiku | Start services, health checks |\\n| entity-manager | Haiku | Query entities, create SiYuan pages |\\n| session-guide | Sonnet | Guide exploration sessions |\\n| project-switcher | Haiku | Switch projects with context handoff |\\n\\n### Commands\\n- **/sync**: Spawn scribe to document session\\n- **/switch-project**: Change active project\\n- **/explore-session**: Start exploration (therapy)\\n- **/end-session**: End and extract entities\\n\\n### Recent Work\\n$RECENT_WORK\\n\\n### Workflow\\n1. Spawn **context-loader** for deep context (or read progress.md)\\n2. Use specialized agents for tasks\\n3. Spawn **scribe** after significant work or before /clear"
}
EOF

exit 0
