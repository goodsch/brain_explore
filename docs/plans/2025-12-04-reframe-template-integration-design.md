# Reframe & Template Integration Design

**Created:** 2025-12-04
**Status:** Approved for implementation

---

## Summary

Integrate two new capabilities from the ChatGPT design document:
1. **Reframe Layer** - Makes concepts human/accessible via metaphors and analogies
2. **Thinking Template Schema** - Formalizes how structured thinking sessions produce graph updates

Plus formalize the **SiYuan Document Structure** for personal knowledge artifacts.

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Scope | Both Reframes + Templates | Full value, parallel work makes it feasible |
| Execution | Hybrid (interfaces first, then parallel) | Coordination where needed, speed where safe |
| SiYuan structure | Daily logs + promoted items | ADHD-friendly: capture fast, organize later |
| Source of truth | Backend API canonical | Clean separation: Backend owns, Neo4j stores, SiYuan displays |
| Reframe generation | Hybrid (on-demand + cache + background for popular) | Balance cost and UX |
| Template scope | 2 templates (Learning + Articulating) | Validates pattern without over-investing |

---

## 1. Reframe Layer

### Entity Type

```python
class ReframeType(str, Enum):
    METAPHOR = "metaphor"      # "Working memory is like a whiteboard"
    ANALOGY = "analogy"        # "ADHD attention is like a searchlight"
    STORY = "story"            # Brief narrative illustration
    PATTERN = "pattern"        # "Same pattern as X"
    CONTRAST = "contrast"      # "Unlike X, this works by..."

@dataclass
class Reframe:
    id: str
    concept_id: str           # Links to domain concept
    type: ReframeType
    domain: str               # Source domain: "relationships", "sports", "cooking"
    text: str                 # The actual reframe content
    created_by: str           # "user" | "ai"
    strength: float = 0.5     # Quality score (updated by feedback)
    helpful_votes: int = 0
    confusing_votes: int = 0
    created_at: datetime
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/concepts/{id}/reframes` | GET | List cached reframes |
| `/concepts/{id}/reframes/generate` | POST | Generate via LLM (if not cached) |
| `/reframes/{id}/feedback` | POST | Vote helpful/confusing |

### LLM Strategy

- Input: concept name, definition, 2-3 related concepts
- Output: 3-5 reframes across different types/domains
- Cache permanently in Neo4j (Reframe nodes linked to Concept)
- Background generation for concepts with >5 visits

### UI Integration

- New "Reframes" tab in Flow panel (both SiYuan and Readest)
- Shows cached reframes immediately
- "Generate" button if empty
- Thumbs up/down for feedback voting

---

## 2. Thinking Template Schema

### JSON Schema Structure

```json
{
  "id": "learning-mechanism-map",
  "mode": "learning",
  "name": "Mechanism Map",
  "description": "Understand how something works by mapping its components",

  "sections": [
    {
      "id": "focus",
      "prompt": "What concept or mechanism do you want to understand?",
      "input_type": "concept_search",
      "required": true
    },
    {
      "id": "components",
      "prompt": "What are the key parts or steps involved?",
      "input_type": "freeform",
      "ai_behavior": "Help break down into components, ask clarifying questions"
    },
    {
      "id": "connections",
      "prompt": "How do these parts relate to each other?",
      "input_type": "freeform",
      "ai_behavior": "Surface relationships, suggest graph connections"
    },
    {
      "id": "synthesis",
      "prompt": "In your own words, how does this mechanism work?",
      "input_type": "freeform",
      "ai_behavior": "Validate understanding, identify gaps"
    }
  ],

  "graph_mapping": {
    "on_complete": [
      {
        "action": "create_or_link",
        "entity_type": "spark",
        "source_section": "synthesis",
        "link_to": "focus.concept_id",
        "relationship": "sparked_by"
      },
      {
        "action": "update_journey",
        "add_exchange": true
      }
    ]
  }
}
```

### Templates to Build

| Template ID | Mode | Purpose | Graph Output |
|-------------|------|---------|--------------|
| `learning-mechanism-map` | Learning | Understand how X works | Spark linked to focus concept |
| `articulating-clarify-intuition` | Articulating | Formalize a vague sense | Insight with resonance signal |

### SessionService Integration

1. Load template by ID when session starts
2. Template drives section flow and AI prompts
3. On session complete, execute `graph_mapping` operations
4. Create appropriate entities in personal graph

---

## 3. SiYuan Document Structure

### Folder Hierarchy

```
/brain_explore/                    # SiYuan notebook
├── /Daily/                        # Low-friction capture (ADHD-friendly)
│   ├── 2025-12-04.md             # Today's sparks, notes, captures
│   └── ...
├── /Insights/                     # Promoted from Daily (stable)
├── /Threads/                      # Exploration paths
├── /Favorite Problems/            # Feynman-style anchor questions
└── /Sessions/                     # Structured thinking session logs
```

### Frontmatter Standard

```yaml
---
be_type: spark | insight | thread | favorite_problem | session
be_id: "spark_abc123"              # Backend canonical ID
status: captured | exploring | anchored
resonance: curious | excited | surprised | moved | disturbed
energy: low | medium | high
concept_ids: ["concept_123"]       # Linked domain concepts
thread_id: "thread_xyz"            # If part of exploration
created: 2025-12-04T10:30:00Z
promoted_from: "Daily/2025-12-04"  # For insights promoted from daily
---
```

### Quick Capture Flow

1. User opens Quick Capture in SiYuan
2. Types thought, clicks "Capture"
3. Backend extracts entities, assigns `be_id`
4. Creates block in today's Daily log with frontmatter
5. User can later promote to Insight

### Promotion Flow

1. User marks spark as "worth keeping"
2. Plugin creates new doc in /Insights/ with same `be_id`
3. Updates backend status: `captured` → `anchored`
4. Original daily entry gets link to promoted insight

---

## 4. Implementation Plan

### Phase 1: Define Interfaces (Sequential)

Single agent defines shared schemas:
- Reframe dataclass in `adhd_ontology.py`
- Thinking template JSON schema
- SiYuan frontmatter spec (TypeScript types)
- API route signatures (OpenAPI stubs)

### Phase 2: Parallel Implementation (4 Agents)

**Agent A: Backend - Reframe Service**
- `services/reframe_service.py`
- Neo4j storage for Reframe nodes
- LLM generation with caching
- API endpoints
- Tests

**Agent B: Backend - Template Engine**
- `services/template_service.py`
- Load/validate templates
- `graph_mapping` executor
- SessionService integration
- 2 template JSON files + tests

**Agent C: SiYuan Plugin - Document Structure**
- Create notebook structure
- Frontmatter utilities
- Quick Capture → Daily routing
- Promotion flow
- Reframes tab in FlowMode

**Agent D: Readest - Reframes Tab**
- `ReframesSection.tsx` component
- API integration
- Feedback voting UI
- Loading/empty states

### Phase 3: Integration (Sequential)

- Wire all components together
- End-to-end testing
- Documentation updates

---

## File Boundaries (No Conflicts)

| Agent | Files |
|-------|-------|
| A | `ies/backend/src/ies_backend/services/reframe_service.py`, `routers/reframe.py` |
| B | `ies/backend/src/ies_backend/services/template_service.py`, `schemas/templates/*.json` |
| C | `.worktrees/siyuan/` (isolated worktree) |
| D | `.worktrees/readest/` (isolated worktree) |

---

## Success Criteria

1. User can view reframes for any concept in Flow panel
2. "Generate" creates 3-5 reframes via LLM, cached for future
3. Feedback voting updates reframe strength
4. Learning session creates spark linked to focus concept
5. Articulating session creates insight with resonance
6. Quick Capture creates entry in Daily log with frontmatter
7. User can promote spark to insight (moves to /Insights/)
