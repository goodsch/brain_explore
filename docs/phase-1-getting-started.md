# Phase 1 - Getting Started

## Right Now: Everything You Need is Ready

✅ Backend running on :8081
✅ Plugin built and ready
✅ Neo4j + Qdrant running
✅ Chris profile created
✅ First session successfully completed
✅ Action plan documented
✅ Session runner script created

---

## Start Your First Session (Today)

### Option 1: Quick Start (Recommended)

```bash
# Terminal 1: Ensure backend is running
cd ies/backend
PYTHONPATH=./src python -m uvicorn ies_backend.main:app --host 0.0.0.0 --port 8081

# Terminal 2: Run a session (interactive mode)
python scripts/run-session.py

# Or with a starting topic:
python scripts/run-session.py --topic "How do I know when I'm avoiding something vs. when I'm intuiting I should move on?"
```

The script will:
1. Start a session with the backend
2. Display your profile and greeting
3. Let you have a conversation
4. Save the transcript when you're done (type "done")

### Option 2: Direct API (If you prefer)

```bash
# Start session
curl -X POST http://localhost:8081/session/start \
  -H "Content-Type: application/json" \
  -d '{"user_id": "chris"}'

# Chat
curl -X POST http://localhost:8081/session/chat-sync \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "YOUR_SESSION_ID",
    "message": "Your message here",
    "messages": []
  }'
```

### Option 3: SiYuan Plugin

1. Open SiYuan
2. Go to Plugins → Install from Marketplace → Search "IES"
3. Enable the plugin
4. Open the IES Explorer sidebar
5. Click "Start Session"
6. Type messages and press enter

---

## Your Phase 1 Daily Workflow

Each morning (15-20 minutes):

1. **Choose a topic** - Something about thinking patterns, worldview, or change
2. **Run a session** - Use the script or direct API
3. **Have the conversation** - Let the system ask questions
4. **Note reflections** - What emerged? What was surprising?
5. **End the session** - Type "done"
6. **File is auto-saved** - Check `docs/session-transcripts/`

---

## Topics for Your 10 Sessions

Use these or create your own:

1. ✅ **How thinking patterns affect project completion** (Already done)
2. **The distinction between acceptance and resignation**
   - When is "letting go" actually wisdom vs. avoidance?
   - What's the internal shift between fighting and accepting?

3. **What creates safety in dialogue**
   - What makes it safe to be vulnerable?
   - When do you trust someone vs. protect yourself?

4. **How curiosity differs from avoidance**
   - When are you exploring vs. escaping?
   - What does genuine interest feel like?

5. **What makes change feel possible**
   - When do you believe change is real?
   - What's different about moments of real shift?

6. **The relationship between structure and creativity**
   - Do you need constraints to be creative?
   - What gets stifled by too much structure?

7. **How to know when something is "good enough"**
   - What's the difference between completion and perfectionism?
   - How do you recognize adequate?

8. **What resistance is trying to protect**
   - When you resist something, what are you preserving?
   - What would you lose if you didn't resist?

9. **The role of compassion in change**
   - How does self-compassion change how you relate to patterns?
   - What happens when you stop fighting yourself?

10. **How to work with your own patterns** (or something that emerges from the first 9)

---

## After Each Session: Document

The script auto-creates markdown files in `docs/session-transcripts/`. Open each file and add:

```markdown
## Reflection

### Key Moments
- What surprised you?
- Where did real insight emerge?

### Patterns Noticed
- What recurring themes appeared?
- What about yourself did you learn?

### Concepts That Emerged
- What new ideas or framings came up?
- How might you name what you discovered?

### What Worked Well
- What did the system do right?
- Where did it understand you well?

### What Could Be Better
- Where did it miss?
- What would be more helpful?
```

This reflection becomes data for the next phase.

---

## Success Looks Like

After Session 1-3:
- ✅ System works end-to-end
- ✅ Questions feel appropriate to you
- ✅ Dialogue feels like actual exploration

After Session 4-7:
- ✅ Patterns in your thinking emerge clearly
- ✅ System adapts to your style
- ✅ Concepts starting to form

After Session 10:
- ✅ 20-30 concepts documented
- ✅ Therapeutic worldview articulated
- ✅ Clear direction for Phase 2

---

## If Something Goes Wrong

### Backend won't start
```bash
# Check if port 8081 is in use
lsof -i :8081

# Kill the process
kill -9 <PID>

# Try again
PYTHONPATH=./src python -m uvicorn ies_backend.main:app --host 0.0.0.0 --port 8081
```

### Can't connect to backend
```bash
# Check health
curl http://localhost:8081/health

# If it fails, backend isn't running (see above)
```

### Session transcripts not saving
```bash
# Check directory exists
ls -la docs/session-transcripts/

# Create if missing
mkdir -p docs/session-transcripts/
```

### Chat returns empty response
- Sometimes Claude takes a moment
- Check backend logs for errors
- Try a simpler message

---

## Keep Track

**Commit after each session:**
```bash
git add docs/session-transcripts/
git commit -m "docs: session 1 - topic name"
```

**Update session notes:**
Edit `docs/session-notes.md` when Phase 1 feels like it's progressing.

---

## The Rule: Use What Exists

**Don't:**
- Add new backend endpoints
- Modify the chat system
- Create new components
- Optimize anything

**Do:**
- Run sessions
- Document what happens
- Let patterns emerge from data
- Trust the process

---

## Questions?

See:
- `docs/phase-1-action-plan.md` — Full Phase 1 plan
- `docs/five-agent-synthesis.md` — Why this approach
- CLAUDE.md — Project overview

---

**You're ready. Start session 2 tomorrow.**
