# brain_explore Meta Configuration

Project-specific meta overrides and recommendations.

## Recommended for This Project

Since brain_explore involves therapy frameworks and introspective exploration:

```bash
# When doing therapy framework exploration
/meta preset multi-approach

# For long sessions
/meta preset adhd-friendly
```

## Project-Specific Presets

Consider creating:
- `therapy-exploration.md` — For when exploring therapy concepts with the user
- `framework-testing.md` — For when testing IES framework behavior

## Example Custom Overrides

```bash
# When the user seems stuck on introspection
/meta When the user struggles to answer, offer 3 reframings: concrete scenario, abstract pattern, and felt-sense/embodied

# When exploring new therapy concepts
/meta Connect new concepts to previously discussed ideas. Build a web of understanding.

# When testing framework features
/meta Be systematic. Test one thing at a time. Verify before moving on.
```

## Configuration Locations

| Scope | Location | Purpose |
|-------|----------|---------|
| Global presets | `~/.claude/meta/presets/` | Available everywhere |
| Project presets | `.claude/meta/presets/` | Project-specific (create if needed) |
| Active override | `~/.claude/meta/active-override.md` | Current session |

## See Also

- `~/.claude/meta/README.md` — Full system documentation
- `/meta help` — List available presets
