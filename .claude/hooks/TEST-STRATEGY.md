# Hook Test Strategy

## Hooks Under Test

### 1. SessionStart Hook (`session-context.sh`)
**Type:** Command
**Trigger:** startup, resume
**Purpose:** Inject documentation protocol reminder with last session date

### 2. Stop Hook (prompt-based)
**Type:** Prompt
**Trigger:** Session exit
**Purpose:** Block exit if significant work done without documentation updates

---

## Test Cases

### SessionStart Hook

| Test | Steps | Expected Result |
|------|-------|-----------------|
| **Fresh start** | `claude` (new session) | See "SessionStart:Callback hook success" + additionalContext injected |
| **Resume** | `/clear` then continue | Hook fires again on resume |
| **Context visible** | Ask "what documentation protocol is active?" | Claude knows about progress file, Serena memories, SiYuan |
| **Last date shown** | Check injected context | Shows date from most recent `## Session:` header |

**Manual verification:**
```bash
# Test hook output directly
CLAUDE_PROJECT_DIR="/home/chris/dev/projects/codex/brain_explore" \
  bash .claude/hooks/session-context.sh
```

Expected output:
```json
{
  "additionalContext": "DOCUMENTATION PROTOCOL ACTIVE: ... Last progress update: 2025-12-01 ..."
}
```

---

### Stop Hook

| Test | Steps | Expected Result |
|------|-------|-----------------|
| **Trivial session** | Start session, ask simple question, `/exit` | `{"ok": true}` - exits cleanly |
| **Significant work, docs updated** | Do real work, update progress file, `/exit` | `{"ok": true}` - exits cleanly |
| **Significant work, NO docs** | Make architecture decision, discuss design, `/exit` WITHOUT updating docs | `{"ok": false, "reason": "..."}` - blocked with reason |
| **JSON format** | Any exit | No schema validation errors |

**Scenarios that SHOULD block:**
- Architecture decisions made, no memory update
- New concepts established, no progress file update
- Mockups created in SiYuan, no mention in progress

**Scenarios that SHOULD pass:**
- Quick Q&A session
- Debugging/testing hooks (like this session)
- Already updated progress file during session

---

## Quick Test Sequence

### Test 1: Basic Hook Firing
```
1. Start new session: `claude`
2. Look for: "SessionStart:Callback hook success"
3. Ask: "What documentation should I update in this project?"
4. Verify Claude knows: progress file, Serena memories, SiYuan
5. Exit: `/exit`
6. Verify: Clean exit (no schema errors)
```

### Test 2: Stop Hook Blocking
```
1. Start session
2. Have substantive conversation about architecture
3. Make decisions without documenting
4. Exit: `/exit`
5. Verify: Hook blocks with reason explaining what needs documenting
6. Update documentation as suggested
7. Exit again
8. Verify: Clean exit
```

### Test 3: Stop Hook Passing
```
1. Start session
2. Do significant work
3. Update progress-framework-project.md
4. Exit: `/exit`
5. Verify: Clean exit (hook sees the Edit/Write calls)
```

---

## Known Issues / Edge Cases

- [ ] Stop hook prompt model might still output markdown wrapper around JSON
- [ ] Very short sessions might be misjudged as "significant"
- [ ] Hook can't see MCP tool calls? (need to verify)

---

## Debugging

**If SessionStart fails:**
```bash
# Check script is executable
ls -la .claude/hooks/session-context.sh

# Test with env var
CLAUDE_PROJECT_DIR="$(pwd)" bash .claude/hooks/session-context.sh

# Check JSON validity
CLAUDE_PROJECT_DIR="$(pwd)" bash .claude/hooks/session-context.sh | jq .
```

**If Stop hook fails schema validation:**
- The prompt model is outputting non-JSON
- Check for markdown code blocks, explanatory text
- Make prompt more emphatic about JSON-only output

**If Stop hook blocks incorrectly:**
- Review the prompt logic
- Consider adding more "pass" conditions
- Check if it can see tool usage in conversation
