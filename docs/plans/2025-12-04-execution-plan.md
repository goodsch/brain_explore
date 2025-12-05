# Reframe & Template Integration - Execution Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement Reframe Layer + Thinking Templates + SiYuan Document Structure using Codex and Gemini CLI in parallel.

**Architecture:** Phase 1 defines shared interfaces (sequential), Phase 2 implements 4 workstreams in parallel, Phase 3 integrates and validates.

**Tech Stack:** Python/FastAPI (backend), Svelte/TypeScript (frontends), Neo4j (graph), Claude API (LLM)

---

## Phase 1: Interface Definitions (Codex - Sequential)

### Task 1.1: Add Reframe Entity to ADHD Ontology

**Tool:** Codex CLI
**Directory:** `/home/chris/dev/projects/codex/brain_explore`
**Sandbox:** `workspace-write`

**Prompt:**
```
Add Reframe entity type to the ADHD ontology in library/graph/adhd_ontology.py.

Add after the existing EntityType enum (around line 54):

1. Add ReframeType enum:
class ReframeType(str, Enum):
    METAPHOR = "metaphor"      # "Working memory is like a whiteboard"
    ANALOGY = "analogy"        # "ADHD attention is like a searchlight"
    STORY = "story"            # Brief narrative illustration
    PATTERN = "pattern"        # "Same pattern as X"
    CONTRAST = "contrast"      # "Unlike X, this works by..."

2. Add Reframe dataclass after the ADHDEntity class:
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
    created_at: datetime = field(default_factory=datetime.now)

3. Export both in library/graph/__init__.py

Apply changes now. Do not ask for confirmation.
```

**Command:**
```bash
codex exec -m gpt-5-codex \
  --config model_reasoning_effort="high" \
  --sandbox workspace-write \
  --full-auto \
  --skip-git-repo-check \
  -C /home/chris/dev/projects/codex/brain_explore \
  "Add Reframe entity type to the ADHD ontology in library/graph/adhd_ontology.py. Add ReframeType enum with values: METAPHOR, ANALOGY, STORY, PATTERN, CONTRAST. Add Reframe dataclass with fields: id, concept_id, type (ReframeType), domain (str), text (str), created_by (str), strength (float=0.5), helpful_votes (int=0), confusing_votes (int=0), created_at (datetime). Export both in library/graph/__init__.py. Apply now." 2>/dev/null
```

---

### Task 1.2: Create Thinking Template JSON Schema

**Tool:** Codex CLI
**Directory:** `/home/chris/dev/projects/codex/brain_explore`

**Prompt:**
```
Create the thinking template JSON schema and two template files.

1. Create directory: schemas/templates/

2. Create schemas/thinking-template.schema.json with JSON Schema for:
- id: string (required)
- mode: enum ["learning", "articulating", "planning", "ideating", "reflecting"]
- name: string (required)
- description: string
- sections: array of objects with:
  - id: string
  - prompt: string
  - input_type: enum ["concept_search", "freeform", "selection"]
  - ai_behavior: string
  - required: boolean
- graph_mapping: object with:
  - on_complete: array of action objects

3. Create schemas/templates/learning-mechanism-map.json:
{
  "id": "learning-mechanism-map",
  "mode": "learning",
  "name": "Mechanism Map",
  "description": "Understand how something works by mapping its components",
  "sections": [
    {"id": "focus", "prompt": "What concept or mechanism do you want to understand?", "input_type": "concept_search", "required": true},
    {"id": "components", "prompt": "What are the key parts or steps involved?", "input_type": "freeform", "ai_behavior": "Help break down into components, ask clarifying questions"},
    {"id": "connections", "prompt": "How do these parts relate to each other?", "input_type": "freeform", "ai_behavior": "Surface relationships, suggest graph connections"},
    {"id": "synthesis", "prompt": "In your own words, how does this mechanism work?", "input_type": "freeform", "ai_behavior": "Validate understanding, identify gaps"}
  ],
  "graph_mapping": {
    "on_complete": [
      {"action": "create_or_link", "entity_type": "spark", "source_section": "synthesis", "link_to": "focus.concept_id", "relationship": "sparked_by"},
      {"action": "update_journey", "add_exchange": true}
    ]
  }
}

4. Create schemas/templates/articulating-clarify-intuition.json:
{
  "id": "articulating-clarify-intuition",
  "mode": "articulating",
  "name": "Clarify Intuition",
  "description": "Transform a vague sense into clear understanding",
  "sections": [
    {"id": "intuition", "prompt": "What's the vague sense or intuition you want to clarify?", "input_type": "freeform", "required": true},
    {"id": "resonance", "prompt": "Why does this feel important? What resonates?", "input_type": "freeform", "ai_behavior": "Explore emotional significance, capture resonance signal"},
    {"id": "examples", "prompt": "Can you think of examples or situations where this applies?", "input_type": "freeform", "ai_behavior": "Ground abstract in concrete"},
    {"id": "articulation", "prompt": "Now try to state it clearly in one or two sentences.", "input_type": "freeform", "ai_behavior": "Refine language, test clarity"}
  ],
  "graph_mapping": {
    "on_complete": [
      {"action": "create_or_link", "entity_type": "insight", "source_section": "articulation", "metadata": {"resonance_from": "resonance"}},
      {"action": "update_journey", "add_exchange": true}
    ]
  }
}

Apply all changes now.
```

**Command:**
```bash
codex exec -m gpt-5-codex \
  --config model_reasoning_effort="high" \
  --sandbox workspace-write \
  --full-auto \
  --skip-git-repo-check \
  -C /home/chris/dev/projects/codex/brain_explore \
  "Create schemas/templates/ directory. Create schemas/thinking-template.schema.json with JSON Schema for template structure (id, mode, name, description, sections array, graph_mapping). Create schemas/templates/learning-mechanism-map.json for Learning mode with 4 sections (focus, components, connections, synthesis) and graph_mapping to create spark. Create schemas/templates/articulating-clarify-intuition.json for Articulating mode with 4 sections (intuition, resonance, examples, articulation) and graph_mapping to create insight. Apply now." 2>/dev/null
```

---

### Task 1.3: Create SiYuan Frontmatter TypeScript Types

**Tool:** Codex CLI
**Directory:** `/home/chris/dev/projects/codex/brain_explore`

**Prompt:**
```
Create TypeScript types for SiYuan frontmatter in ies/plugin/src/types/frontmatter.ts

export type BeType = 'spark' | 'insight' | 'thread' | 'favorite_problem' | 'session';
export type EntityStatus = 'captured' | 'exploring' | 'anchored';
export type ResonanceSignal = 'curious' | 'excited' | 'surprised' | 'moved' | 'disturbed' | 'unclear' | 'connected' | 'validated';
export type EnergyLevel = 'low' | 'medium' | 'high';

export interface BrainExploreFrontmatter {
  be_type: BeType;
  be_id: string;
  status: EntityStatus;
  resonance?: ResonanceSignal;
  energy?: EnergyLevel;
  concept_ids?: string[];
  thread_id?: string;
  created: string;  // ISO 8601
  promoted_from?: string;
}

export function parseFrontmatter(content: string): BrainExploreFrontmatter | null;
export function serializeFrontmatter(fm: BrainExploreFrontmatter): string;

Apply now.
```

**Command:**
```bash
codex exec -m gpt-5-codex \
  --config model_reasoning_effort="high" \
  --sandbox workspace-write \
  --full-auto \
  --skip-git-repo-check \
  -C /home/chris/dev/projects/codex/brain_explore \
  "Create ies/plugin/src/types/frontmatter.ts with TypeScript types for SiYuan frontmatter: BeType union, EntityStatus union, ResonanceSignal union, EnergyLevel union, BrainExploreFrontmatter interface, parseFrontmatter and serializeFrontmatter functions. Apply now." 2>/dev/null
```

---

### Task 1.4: Create API Route Stubs for Reframes

**Tool:** Codex CLI
**Directory:** `/home/chris/dev/projects/codex/brain_explore`

**Prompt:**
```
Create API route stubs for reframes in ies/backend/src/ies_backend/api/reframe.py

Create a FastAPI router with these endpoints (stubs that return NotImplementedError for now):

1. GET /concepts/{concept_id}/reframes - List cached reframes for a concept
2. POST /concepts/{concept_id}/reframes/generate - Generate reframes via LLM
3. POST /reframes/{reframe_id}/feedback - Vote helpful/confusing

Create Pydantic schemas in ies/backend/src/ies_backend/schemas/reframe.py:
- ReframeResponse (id, concept_id, type, domain, text, strength, helpful_votes, confusing_votes)
- ReframeListResponse (reframes: list[ReframeResponse])
- GenerateReframesRequest (count: int = 5)
- FeedbackRequest (vote: Literal["helpful", "confusing"])

Register router in main.py with prefix="/reframes"

Apply now.
```

**Command:**
```bash
codex exec -m gpt-5-codex \
  --config model_reasoning_effort="high" \
  --sandbox workspace-write \
  --full-auto \
  --skip-git-repo-check \
  -C /home/chris/dev/projects/codex/brain_explore \
  "Create ies/backend/src/ies_backend/api/reframe.py with FastAPI router for: GET /concepts/{concept_id}/reframes, POST /concepts/{concept_id}/reframes/generate, POST /reframes/{reframe_id}/feedback. Create ies/backend/src/ies_backend/schemas/reframe.py with Pydantic models: ReframeResponse, ReframeListResponse, GenerateReframesRequest, FeedbackRequest. Register router in main.py. Stubs can raise NotImplementedError. Apply now." 2>/dev/null
```

---

## Phase 2: Parallel Implementation

After Phase 1 completes, run these 4 tasks in parallel (4 terminals):

### Task 2A: Backend Reframe Service (Codex)

**Terminal 1:**
```bash
codex exec -m gpt-5-codex \
  --config model_reasoning_effort="high" \
  --sandbox workspace-write \
  --full-auto \
  --skip-git-repo-check \
  -C /home/chris/dev/projects/codex/brain_explore/ies/backend \
  "Implement ReframeService in src/ies_backend/services/reframe_service.py.

Requirements:
1. ReframeService class with methods:
   - get_reframes(concept_id: str) -> list[Reframe] - Query Neo4j for cached reframes
   - generate_reframes(concept_id: str, count: int = 5) -> list[Reframe] - Use Claude API to generate, cache in Neo4j
   - record_feedback(reframe_id: str, vote: str) -> None - Update helpful/confusing votes, recalculate strength

2. Neo4j storage:
   - Create Reframe nodes with properties matching the Reframe dataclass
   - Link to Concept nodes with HAS_REFRAME relationship

3. LLM prompt for generation:
   - Input: concept name, definition, 2-3 related concepts
   - Output: Generate diverse reframes (metaphor, analogy, pattern, etc.)
   - Parse response into Reframe objects

4. Update api/reframe.py to use the service instead of stubs

5. Add tests in tests/test_reframe_service.py

Apply all changes now. Follow existing patterns in graph_service.py." 2>/dev/null
```

### Task 2B: Backend Template Engine (Codex)

**Terminal 2:**
```bash
codex exec -m gpt-5-codex \
  --config model_reasoning_effort="high" \
  --sandbox workspace-write \
  --full-auto \
  --skip-git-repo-check \
  -C /home/chris/dev/projects/codex/brain_explore/ies/backend \
  "Implement TemplateService in src/ies_backend/services/template_service.py.

Requirements:
1. TemplateService class with methods:
   - load_template(template_id: str) -> ThinkingTemplate - Load from schemas/templates/*.json
   - validate_template(template: dict) -> bool - Validate against JSON schema
   - execute_graph_mapping(template: ThinkingTemplate, session_data: dict) -> list[str] - Execute on_complete actions, return created entity IDs

2. ThinkingTemplate Pydantic model matching the JSON schema

3. Graph mapping executor:
   - 'create_or_link' action: Create spark/insight entity, link to concept
   - 'update_journey' action: Add exchange to active journey

4. Integration with SessionService:
   - When session completes, call execute_graph_mapping
   - Pass session transcript and section responses

5. Add tests in tests/test_template_service.py

Apply all changes now." 2>/dev/null
```

### Task 2C: SiYuan Plugin Document Structure (Gemini)

**Terminal 3:**
```bash
cd /home/chris/dev/projects/codex/brain_explore/.worktrees/siyuan && \
gemini "Use codebase_investigator to understand this SiYuan plugin codebase.

Then implement these changes:

1. Create src/utils/siyuan-structure.ts with functions:
   - ensureNotebookStructure() - Create /Daily/, /Insights/, /Threads/, /Favorite Problems/, /Sessions/ if missing
   - getDailyLogPath(date: Date) - Return path like /Daily/2025-12-04.md
   - createDailyEntry(content: string, frontmatter: BrainExploreFrontmatter) - Append to daily log
   - promoteToInsight(sparkId: string) - Move from daily to /Insights/, update status

2. Update src/views/QuickCapture.svelte:
   - On capture, call createDailyEntry with proper frontmatter
   - Show 'Promote to Insight' button for captured sparks

3. Create src/components/ReframesTab.svelte:
   - Fetch reframes from /concepts/{id}/reframes API
   - Display list with type badges (metaphor, analogy, etc.)
   - 'Generate' button if no reframes
   - Thumbs up/down for feedback

4. Add ReframesTab to FlowMode.svelte as new tab option

START IMPLEMENTING NOW. Do not ask for confirmation." --yolo -o text 2>&1
```

### Task 2D: Readest Reframes Tab (Gemini)

**Terminal 4:**
```bash
cd /home/chris/dev/projects/codex/brain_explore/.worktrees/readest && \
gemini "Use codebase_investigator to understand this Readest codebase, specifically the FlowPanel component structure.

Then implement:

1. Create apps/readest-app/src/app/reader/components/flow/ReframesSection.tsx:
   - Props: conceptId: string
   - State: reframes, loading, error
   - Fetch from backend /concepts/{id}/reframes
   - Display reframes grouped by type
   - 'Generate Reframes' button with loading state
   - Thumbs up/down feedback buttons
   - Empty state with helpful message

2. Add ReframesSection to FlowPanel.tsx:
   - New 'Reframes' tab alongside Entity, Relationships, Sources, Questions
   - Only show if conceptId is available

3. Style to match existing FlowPanel aesthetics

4. Handle loading and error states gracefully

START IMPLEMENTING NOW. Do not ask for confirmation." --yolo -o text 2>&1
```

---

## Phase 3: Integration & Validation

### Task 3.1: Cross-Validation (Gemini reviews)

```bash
# Review backend services
gemini "Review these files for bugs and security issues:
- ies/backend/src/ies_backend/services/reframe_service.py
- ies/backend/src/ies_backend/services/template_service.py
Report issues with severity levels." -o text

# Review frontend components
gemini "Review these files for bugs and React/Svelte best practices:
- .worktrees/siyuan/src/components/ReframesTab.svelte
- .worktrees/readest/apps/readest-app/src/app/reader/components/flow/ReframesSection.tsx
Report issues." -o text
```

### Task 3.2: Run Tests

```bash
cd /home/chris/dev/projects/codex/brain_explore/ies/backend && \
uv run pytest tests/ -v
```

### Task 3.3: End-to-End Test

Manual verification:
1. Start backend: `cd ies/backend && uv run uvicorn ies_backend.main:app --reload`
2. Test reframe API: `curl http://localhost:8000/concepts/executive-function/reframes`
3. Test generate: `curl -X POST http://localhost:8000/concepts/executive-function/reframes/generate`
4. Verify SiYuan plugin shows Reframes tab
5. Verify Readest shows Reframes tab

---

## Execution Commands Summary

### Phase 1 (Run sequentially):
```bash
# 1.1 - Reframe entity
codex exec -m gpt-5-codex --config model_reasoning_effort="high" --sandbox workspace-write --full-auto --skip-git-repo-check -C /home/chris/dev/projects/codex/brain_explore "[Task 1.1 prompt]" 2>/dev/null

# 1.2 - Template schema
codex exec -m gpt-5-codex --config model_reasoning_effort="high" --sandbox workspace-write --full-auto --skip-git-repo-check -C /home/chris/dev/projects/codex/brain_explore "[Task 1.2 prompt]" 2>/dev/null

# 1.3 - TypeScript types
codex exec -m gpt-5-codex --config model_reasoning_effort="high" --sandbox workspace-write --full-auto --skip-git-repo-check -C /home/chris/dev/projects/codex/brain_explore "[Task 1.3 prompt]" 2>/dev/null

# 1.4 - API stubs
codex exec -m gpt-5-codex --config model_reasoning_effort="high" --sandbox workspace-write --full-auto --skip-git-repo-check -C /home/chris/dev/projects/codex/brain_explore "[Task 1.4 prompt]" 2>/dev/null
```

### Phase 2 (Run in parallel - 4 terminals):
```bash
# Terminal 1: Backend Reframe Service
codex exec ... "[Task 2A prompt]" 2>/dev/null

# Terminal 2: Backend Template Engine
codex exec ... "[Task 2B prompt]" 2>/dev/null

# Terminal 3: SiYuan Plugin
gemini "[Task 2C prompt]" --yolo -o text 2>&1

# Terminal 4: Readest
gemini "[Task 2D prompt]" --yolo -o text 2>&1
```

### Phase 3 (Run sequentially):
```bash
# Cross-validation
gemini "[Task 3.1 prompts]" -o text

# Tests
cd ies/backend && uv run pytest tests/ -v

# Manual E2E
# Follow Task 3.3 steps
```
