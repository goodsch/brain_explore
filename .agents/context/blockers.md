# Current Blockers

Track blockers that may affect multiple agents or need cross-agent resolution.

---

## Active Blockers

*None currently*

---

## Resolved Blockers

### 2025-12-07: Pass 2/3 found no source entities

**Reported by:** Claude
**Resolved by:** Claude
**Resolution:** Queries were using `e.type` property but entities stored as labels. Fixed query to use label-based filtering.

---

## Template

```markdown
### YYYY-MM-DD: Blocker Title

**Reported by:** Agent
**Blocking:** What work is blocked
**Details:** Description of the issue
**Needs:** What's required to unblock
```
