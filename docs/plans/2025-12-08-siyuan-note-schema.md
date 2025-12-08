# SiYuan Note Schema for AI Navigation

**Created:** 2025-12-08
**Purpose:** Define uniform note structure enabling AI to navigate, read, and edit notes in the IES system.

---

## Design Goals

1. **Collect and link ideas** → AI-assisted exploration → Synthesize to hard notes
2. **Uniform ontology** → AI can navigate/edit easily with predictable structure

---

## Note Types

| Type | Purpose | Location | Complexity |
|------|---------|----------|------------|
| `spark` | Raw capture, unprocessed resonance | `/Mind/Seedlings/*` | Minimal |
| `session` | AI-assisted thinking session | `/Mind/Sessions/` | Medium |
| `question` | Favorite problem (Feynman anchor) | `/Mind/Questions/` | Medium |
| `concept` | Refined domain knowledge | `/Mind/Concepts/` | Full |
| `theory` | Explanatory model | `/Mind/Theories Hub/` | Full |

---

## Lifecycle

```
CAPTURE              EXPLORE                SYNTHESIZE
────────────────────────────────────────────────────────
spark         →      session/question   →   concept/theory
status:captured      status:exploring       status:anchored
```

---

## Uniform Base Schema (All Notes)

Every note contains these elements in this order:

### 1. Header Block (Blockquote)
```markdown
> **Type:** {type} | **Status:** captured | exploring | anchored
```

### 2. Metadata Table
| Field | Value |
|-------|-------|
| Resonance | curious · excited · surprised · moved · disturbed · unclear |
| Energy | low · medium · high |
| Created | {date} |

### 3. Content Section
```markdown
## Content
{main idea or captured thought}
```

### 4. Links Section
```markdown
## Links
- Related: {block refs}
- Problems this addresses: {block refs to questions}
- Sources: {block refs to books/sessions}
```

### 5. Questions Section
```markdown
## Questions
{open threads for further exploration}
```

---

## Type-Specific Sections

### Spark (Minimal)
- `## Context` — What were you doing when this came up?

### Concept (Hard Note)
- `## Definition` — Clear, precise explanation
- `## Examples` — Concrete instances
- `## Distinctions` — What this is NOT

### Theory (Hard Note)
- `## Core Claim` — Central assertion
- `## Mechanisms` — How it works
- `## Evidence` — What supports this
- `## Contradictions` — What challenges this

### Question (Favorite Problem)
- `## The Question` — Clear statement
- `## Why This Matters` — Personal significance
- `## Current Thinking` — Working hypothesis
- `## Approaches Tried` — What's been explored

### Session
- `## Topic` — What was explored
- `## Entities Extracted` — Concepts discovered
- `## Next Steps` — Follow-up actions

---

## AI Navigation Patterns

### Finding Notes by Type
```sql
SELECT * FROM blocks
WHERE type = 'd'
AND hpath LIKE '%/Mind/Concepts/%'
```

### Finding Section Content
1. Get document ID from path
2. Query child blocks: `get_child_blocks(doc_id)`
3. Find `## {section}` heading
4. Read content blocks after heading until next `##`

### Updating Sections
1. Find the section heading block by content match
2. Find content blocks between this heading and next `---` or `##`
3. Use `update_block` to modify content

### Adding Links
Find `## Links` section, locate appropriate list item, append block ref:
```markdown
- Related: ((block-id)) [[Note Title]]
```

---

## Resonance Signals (ADHD-Optimized)

| Signal | Meaning | AI Use |
|--------|---------|--------|
| `curious` | Want to know more | Suggest exploration paths |
| `excited` | High energy, engaged | Good time for synthesis |
| `surprised` | Unexpected insight | Flag for connection-finding |
| `moved` | Emotional resonance | Preserve context carefully |
| `disturbed` | Conflicts with beliefs | Explore contradictions |
| `unclear` | Needs clarification | Prompt questions |

---

## Energy Levels (Mood-Based Access)

| Level | When to Surface | Content Complexity |
|-------|-----------------|-------------------|
| `low` | Tired, low motivation | Simple sparks, reviews |
| `medium` | Normal state | Exploration, connections |
| `high` | Energized, focused | Synthesis, hard notes |

---

## Status Lifecycle (Non-Judgmental)

| Status | Meaning | AI Behavior |
|--------|---------|-------------|
| `captured` | Just saved, unprocessed | Don't pressure to process |
| `exploring` | Actively being developed | Suggest connections, questions |
| `anchored` | Crystallized, stable | Reference in other contexts |

---

## Folder Structure

```
IES_example/
├── Life/
│   └── Daily Log          # Quick daily captures
├── Mind/
│   ├── Concepts/          # type: concept
│   ├── Maps/              # Visual connection maps
│   ├── Questions/         # type: question (favorite problems)
│   ├── Seedlings/         # type: spark (various subtypes)
│   │   ├── Contradictions
│   │   ├── Insights
│   │   ├── Observations
│   │   ├── Questions
│   │   └── What_Ifs
│   ├── Sessions/          # type: session
│   └── Theories Hub/      # type: theory
└── System/
    └── Templates/         # Note templates
```

---

## Template IDs (for programmatic use)

| Template | SiYuan Doc ID |
|----------|---------------|
| Spark | `20251208144643-t5zqg4y` |
| Concept | `20251208144643-k38gcfx` |
| Theory | `20251208144643-crnpsbg` |
| Question | `20251208144643-17ka1zy` |
| Session | `20251208144643-zupcksk` |

---

## Example: AI Reading a Concept Note

```python
# 1. Find concept by name
results = sql_query("""
    SELECT id, hpath FROM blocks
    WHERE type = 'd' AND content LIKE '%Executive Function%'
    AND hpath LIKE '%Concepts%'
""")

# 2. Get document content
doc = export_md_content(results[0]['id'])

# 3. Parse sections (all notes have same structure)
sections = parse_markdown_sections(doc['content'])

# 4. Access specific fields
definition = sections.get('Definition')
related = sections.get('Links')
questions = sections.get('Questions')
```

---

## Example: AI Creating a New Concept from Spark

```python
# 1. Read spark
spark = export_md_content(spark_id)

# 2. Create concept using template
new_doc = create_doc(
    notebook=notebook_id,
    path='/Mind/Concepts/New_Concept',
    markdown=concept_template.format(
        type='concept',
        status='exploring',
        content=spark['content'],
        definition='[AI generates from spark]',
        # ... other fields
    )
)

# 3. Link back to spark
update_links_section(new_doc, sources=[spark_id])
```

---

## Key Principles for AI

1. **All notes have same base sections** — Content, Links, Questions always exist
2. **Status is non-judgmental** — captured/exploring/anchored, not draft/incomplete
3. **Links are explicit** — Use SiYuan block refs `((id))` for traversable connections
4. **Resonance matters** — Emotional signals guide what to surface when
5. **Energy awareness** — Match content complexity to user's current energy
