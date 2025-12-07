# Architecture Decisions Log

Shared record of significant decisions made by any agent.

---

## 2025-12-07: Reframe Layer Entity Storage

**Decision:** Store Pattern/StoryInsight/DynamicPattern/SchemaBreak as Neo4j labels, not `type` property.

**Made by:** Claude (discovered during Pass 2/3 testing)

**Rationale:** Labels enable faster queries and proper graph semantics.

**Impact:** ReframeMapper and ReframeGenerator queries updated to use label-based filtering with CASE expressions.

---

## 2025-12-07: Cross-Agent Communication

**Decision:** File-based message queue in `.agents/` directory.

**Made by:** Claude

**Rationale:**
- Works across all three agent runtimes (Claude Code, Codex CLI, Gemini CLI)
- No external dependencies
- Human-readable and auditable
- Git-trackable for history

**Alternatives considered:**
- Redis pub/sub — requires running service, overkill
- Shared SQLite — file locking issues across agents
- API endpoints — requires backend changes

---

## Template for New Decisions

```markdown
## YYYY-MM-DD: Decision Title

**Decision:** What was decided.

**Made by:** Agent name

**Rationale:** Why this choice was made.

**Impact:** What changes as a result.
```
