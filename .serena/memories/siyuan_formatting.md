# SiYuan Formatting Reference

## Links and References

| Type | Syntax | Example |
|------|--------|---------|
| Block reference | `((block-id))` | `((20251129161040-gxolw02))` |
| Block ref with anchor | `((block-id "text"))` | `((20251129161040-gxolw02 "Hub page"))` |
| Block embed | `!((block-id))` | `!((20251129161040-gxolw02))` |

**Important:** SiYuan does NOT use `[[Page Name]]` wiki-style links. All references require the target block's ID.

## Tags

| Type | Syntax | Example |
|------|--------|---------|
| Simple tag | `#TagName#` | `#concept#` |
| Hierarchical tag | `#Parent/Child#` | `#therapy/technique#` |

**Important:** Tags require BOTH opening and closing `#`. Unlike most systems, `#tag` alone won't work.

## Block Attributes (Kramdown IAL)

Attributes appear after blocks in `{: }` syntax:

```markdown
Some paragraph text
{: id="20251129161040-abc123" updated="20251129161040" custom-key="value"}
```

### Common Attributes
- `id` — Block ID (auto-generated)
- `updated` — Timestamp
- `title` — Document title (for doc blocks)
- `type` — Block type
- Custom attributes: `custom-myattr="value"`

## Via MCP API

### Creating content with links
1. First find/create target block to get its ID
2. Use `((id))` syntax in markdown content

### Setting attributes
Use `set_block_attrs` tool after creating the block:
```
id: "block-id"
attrs: { "custom-status": "draft", "custom-priority": "high" }
```

### Creating tags in content
Include `#TagName#` directly in the markdown when using `insert_block`, `append_block`, etc.

## What NOT to Do

| Wrong | Right |
|-------|-------|
| `[[Page Name]]` | `((block-id))` |
| `#tag` | `#tag#` |
| `@mention` | Not supported |
| Front matter YAML | Use block attributes |

## Database Queries for Finding IDs

Find document by title:
```sql
SELECT id FROM blocks WHERE type = 'd' AND content = 'Document Title'
```

Find blocks with specific tag:
```sql
SELECT * FROM blocks WHERE tag LIKE '%tagname%'
```
