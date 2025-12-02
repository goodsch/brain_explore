# Task Completion Checklist

## Before Ending Any Session

1. **Update progress file** (`progress-framework-project.md`)
   - What was accomplished
   - Current state
   - Next steps
   - Open questions

2. **Update SiYuan**
   - Session log in appropriate notebook
   - Active Work page if status changed
   - See `handoff.md` for full requirements

3. **Check for uncommitted work**
   - Not a git repo currently, but may change

## Code Changes

No strict linting/testing configured yet. When adding:
- Type hints for function signatures
- Docstrings for public functions
- Test with `pytest` if tests exist

## Infrastructure Changes

If modifying docker-compose.yml:
```bash
docker compose down
docker compose up -d
docker compose logs -f
```

## Documentation

Design documents go in `docs/plans/` with format:
`YYYY-MM-DD-{topic}.md`
