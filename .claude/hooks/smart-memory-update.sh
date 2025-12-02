#!/bin/bash
# Smart Memory Update Hook
# Only triggers memory-updater if files in docs/ were actually modified in this turn

# Check if any files in docs/ were created or modified in this session
MODIFIED_FILES=$(find "$CLAUDE_PROJECT_DIR/docs" -type f -newer /tmp/session_start_time 2>/dev/null | wc -l)

if [ "$MODIFIED_FILES" -gt 0 ]; then
  echo "Files modified detected. Memory update needed."
  exit 0
else
  echo "No file modifications detected. Skipping memory update."
  exit 0
fi
