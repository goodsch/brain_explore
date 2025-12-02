# Handoff Process for brain_explore

This project uses SiYuan as a knowledge base. Handoffs MUST update both local files AND SiYuan.

## Required Updates

### 1. Local Progress File
Update `progress-framework-project.md` with:
- What was accomplished
- Current state (knowledge graph stats, extraction status)
- Next steps
- Open questions

### 2. SiYuan Session Log
Create or update session document at:
```
Framework Project notebook → /Sessions/YYYY-MM-DD-{topic}
```

Include:
- Focus and mode
- What was done
- Artifacts created (local + SiYuan)
- Next steps
- Open questions

### 3. SiYuan Active Work
Update the Active Work document:
```
Framework Project notebook → /Current State/Active Work
```

With current project status and priorities.

## SiYuan Connection Details

- **Host:** 192.168.86.60:6806
- **Notebooks:**
  - Framework Project (meta/planning)
  - Therapy Framework (content/exploration)

## Quick Reference

```bash
# Check SiYuan status
mcp__siyuan-mcp__check_siyuan_status

# List notebooks
mcp__siyuan-mcp__list_notebooks

# Query for documents
mcp__siyuan-mcp__sql_query with:
  SELECT id, content, hpath FROM blocks WHERE type = 'd' AND box = 'NOTEBOOK_ID'
```

## Notes

- This project is NOT a git repo — no commits needed
- Docker services (Neo4j, Qdrant) should be running for graph operations
- Check extraction status with `./scripts/check_progress.sh`
