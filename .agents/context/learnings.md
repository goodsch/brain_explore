# Shared Learnings

Patterns and insights discovered during development that other agents should know.

---

## Neo4j Patterns

### Label vs Property for Entity Types
Neo4j labels (`:Pattern`, `:StoryInsight`) are faster to query than property-based filtering (`WHERE e.type = 'pattern'`). Use labels for categorical types.

### CASE Expressions for Type Mapping
When entities are stored with labels but you need a string type field:
```cypher
RETURN CASE
  WHEN e:Pattern THEN 'pattern'
  WHEN e:StoryInsight THEN 'story_insight'
END AS type
```

---

## Testing Patterns

### Mock OpenAI Client
```python
with patch("module.OpenAI") as mock_openai:
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps({...})
    instance.client.chat.completions.create.return_value = mock_response
```

### Mock Neo4j Session
```python
mock_session = MagicMock()
mock_kg.driver.session.return_value.__enter__.return_value = mock_session
mock_session.run.return_value = [{"name": "Test", "type": "concept"}]
```

---

## Project Conventions

### Commit Message Prefixes
- `feat:` — New feature
- `fix:` — Bug fix
- `test:` — Tests only
- `docs:` — Documentation
- `refactor:` — Code restructure without behavior change

### Worktree Discipline
- Master branch = backend only
- Feature work = always in worktrees
- Check `git status` before any edits

---

## Add New Learnings

When you discover something useful, add it here so other agents benefit.
