# IES Knowledge Pipeline - Complete Design

**Created:** 2025-12-08
**Purpose:** End-to-end pipeline for AI-assisted knowledge synthesis with SiYuan + IES Reader

---

## Design Principles

1. **Every block has identity** - Named blocks with attributes enable AI navigation
2. **Bidirectional trails** - From book → insights it sparked; From theory → evidence supporting it
3. **Progressive enrichment** - Raw captures → processed → synthesized → anchored
4. **Context awareness** - Always know which Feynman problem you're exploring
5. **Human in the loop** - AI proposes, human approves (with auto-approve thresholds)

---

## Note Type Hierarchy

```
📚 SOURCES/
├── Books/
│   ├── Stolen Focus.md (id: BOOK_STOLEN_FOCUS)
│   ├── Flow.md (id: BOOK_FLOW)
│   └── ...
├── Papers/
├── Articles/
└── Sources Hub.md (index)

🧩 PROBLEMS/ (Feynman Problems)
├── Why Can't I Start From Zero.md (id: PROBLEM_START_ZERO)
├── What Is ADHD Time Perception.md (id: PROBLEM_TIME_PERCEPTION)
└── Problems Hub.md (index)

🔶 THEORIES/
├── Entry Point Theory.md (id: THEORY_ENTRY_POINT)
├── Movement Creates Meaning.md (id: THEORY_MOVEMENT_MEANING)
└── Theories Hub.md (index)

💡 CONCEPTS/
├── Activation Energy.md (id: CONCEPT_ACTIVATION_ENERGY)
├── Context-Dependent Cognition.md (id: CONCEPT_CONTEXT_COGNITION)
└── Concepts Index.md

🌱 SPARKS/
├── 2025-12-08-attention-devotion.md (id: SPARK_20251208_001)
└── ... (minimal structure, promotion candidates)

💬 SESSIONS/
├── 2025-12-08-entry-point-exploration.md (id: SESSION_20251208_001)
└── ...
```

---

## Block Naming Convention

### Document-Level ID
```markdown
# 🔶 Theory: Entry Point Theory

{: custom-type="theory" custom-id="THEORY_ENTRY_POINT" custom-status="exploring" }
```

### Section-Level ID
```markdown
## Evidence
{: custom-section="evidence" custom-section-id="THEORY_ENTRY_POINT_EVIDENCE" }
```

### Block-Level ID (Highlights, Insights)
```markdown
> "Attention is the beginning of devotion." — Mary Oliver
{: custom-block-type="highlight" custom-id="HL_STOLEN_FOCUS_042" custom-source="calibre:123" custom-source-cfi="/6/4[chap01]!/4/2/1:0" custom-entity-refs="attention,devotion,entry-point" custom-resonance="moved" custom-energy="high" custom-processed="false" }
```

---

## SiYuan Custom Attributes Schema

### Document Attributes
| Attribute | Values | Purpose |
|-----------|--------|---------|
| `custom-type` | theory, concept, question, spark, book, session | Note classification |
| `custom-id` | THEORY_X, BOOK_X, etc. | Unique identifier for AI targeting |
| `custom-status` | draft, exploring, anchored | Lifecycle stage |
| `custom-context` | PROBLEM_X | Active Feynman problem (if any) |

### Section Attributes
| Attribute | Values | Purpose |
|-----------|--------|---------|
| `custom-section` | evidence, hypotheses, highlights, implications, crosslinks | Section type |
| `custom-section-id` | THEORY_X_EVIDENCE | Unique section identifier |

### Block Attributes (Highlights/Insights)
| Attribute | Values | Purpose |
|-----------|--------|---------|
| `custom-block-type` | highlight, insight, reaction, question | Block classification |
| `custom-id` | HL_X_001 | Unique highlight ID |
| `custom-source` | calibre:123 | Source reference |
| `custom-source-cfi` | /6/4[chap01]... | Jump-back location |
| `custom-entity-refs` | concept1,concept2 | Linked entities |
| `custom-resonance` | curious, excited, surprised, moved, disturbed | Emotional signal |
| `custom-energy` | low, medium, high | Capture energy level |
| `custom-processed` | true, false | Agent processing status |
| `custom-confidence` | 0.0-1.0 | AI confidence in connections |

---

## Book Note Template

```markdown
# 📚 {Book Title}

{: custom-type="book" custom-id="BOOK_X" custom-status="reading" }

---

## Metadata
| Field | Value |
|-------|-------|
| Author | {author} |
| Year | {year} |
| Calibre ID | {id} |
| Status | not-started / reading / completed / processing |
| Started | {date} |
| Finished | {date} |

---

## Core Thesis
{: custom-section="thesis" custom-section-id="BOOK_X_THESIS" }

{What is this book fundamentally arguing?}

---

## Key Concepts Extracted
{: custom-section="concepts" custom-section-id="BOOK_X_CONCEPTS" }

- [[Concept: X]]
- [[Concept: Y]]

---

## Highlights
{: custom-section="highlights" custom-section-id="BOOK_X_HIGHLIGHTS" }

> "{highlight text}"
{: custom-block-type="highlight" custom-id="HL_X_001" custom-source-cfi="..." custom-entity-refs="..." custom-processed="false" }

**My reaction:** {initial thought}

---

## Connections to My Thinking
{: custom-section="connections" custom-section-id="BOOK_X_CONNECTIONS" }

- Relates to [[Theory: Entry Point Theory]] because...
- Challenges [[Feynman Problem: X]] by...

---

## Processing Queue
{: custom-section="queue" custom-section-id="BOOK_X_QUEUE" }

Highlights awaiting agent processing:
{{query blocks where ial contains 'custom-source="calibre:X"' and ial contains 'custom-processed="false"'}}
```

---

## Highlight Capture Pipeline

### Step 1: Reader Capture
```json
{
  "id": "HL_STOLEN_FOCUS_042",
  "book_id": "calibre:123",
  "book_title": "Stolen Focus",
  "cfi": "/6/4[chap01]!/4/2/1:0",
  "text": "Attention is the beginning of devotion.",
  "note": "This connects to Entry Point Theory - attention as the entry point",
  "created": "2025-12-08T14:30:00Z",
  "context_id": "PROBLEM_START_ZERO",
  "energy": "high",
  "resonance": "moved"
}
```

### Step 2: Sync to SiYuan
1. Find or create Book Note for "Stolen Focus"
2. Append highlight block to `## Highlights` section
3. Set `custom-processed="false"`
4. Add to processing queue

### Step 3: Agent Processing
Intake Agent analyzes:
- Entity extraction: ["attention", "devotion"]
- Relationship detection: Mentions "beginning" → activation concept?
- Context matching: User was in PROBLEM_START_ZERO context

Proposes:
```json
{
  "proposed_actions": [
    {"action": "add_entity_ref", "entity": "CONCEPT_ATTENTION", "confidence": 0.95},
    {"action": "add_entity_ref", "entity": "CONCEPT_ENTRY_POINT", "confidence": 0.75},
    {"action": "link_to_section", "target": "THEORY_ENTRY_POINT_EVIDENCE", "confidence": 0.70}
  ]
}
```

### Step 4: Approval & Linking
- Actions above threshold (0.8) auto-approved
- Others queued for human review
- On approval: Update highlight attributes, add to target Evidence section

### Step 5: Bidirectional Trail
**In Book Note:**
> "Attention is the beginning of devotion."
> → Linked to: [[Theory: Entry Point Theory]]

**In Theory Note (Evidence section):**
> From [[📚 Stolen Focus]]: "Attention is the beginning of devotion."
> {: custom-source="BOOK_STOLEN_FOCUS" custom-highlight-ref="HL_STOLEN_FOCUS_042" }

---

## Agent Types

### 1. Intake Agent
**Trigger:** New highlight, spark, or session
**Tasks:**
- Extract entities (concepts, people, theories)
- Detect resonance signals
- Propose initial connections
- Set processing status

### 2. Enrichment Agent
**Trigger:** Flow Mode activation, scheduled batch, or manual request
**Tasks:**
- Gather all evidence for a theory/problem
- Identify gaps: "No evidence about emotional entry points"
- Propose synthesis drafts
- Suggest sources from library

### 3. Synthesis Agent
**Trigger:** Explicit user request
**Tasks:**
- Pull relevant sections across notes
- Generate coherent narrative
- Create new hard notes from accumulated evidence
- Update all crosslinks bidirectionally

---

## Processing Queue Schema

```json
{
  "id": "job_123",
  "type": "intake | enrichment | synthesis",
  "status": "pending | processing | needs_review | completed | failed",
  "target": {
    "block_id": "HL_STOLEN_FOCUS_042",
    "note_id": "BOOK_STOLEN_FOCUS"
  },
  "context_id": "PROBLEM_START_ZERO",
  "created": "2025-12-08T14:35:00Z",
  "proposed_actions": [...],
  "auto_approve_threshold": 0.8,
  "approved_actions": [...],
  "rejected_actions": [...],
  "completed_at": null,
  "journey_entry_id": "journey_456"
}
```

---

## AI Query Examples

```sql
-- Find all unprocessed highlights
SELECT * FROM blocks WHERE
  ial LIKE '%custom-block-type="highlight"%'
  AND ial LIKE '%custom-processed="false"%'

-- Find all evidence for Entry Point Theory
SELECT * FROM blocks WHERE
  ial LIKE '%custom-section-id="THEORY_ENTRY_POINT_EVIDENCE"%'

-- Find highlights with high confidence entity connections
SELECT * FROM blocks WHERE
  ial LIKE '%custom-block-type="highlight"%'
  AND ial LIKE '%custom-confidence%'
  -- Parse and filter confidence > 0.8

-- Find all captures related to a Feynman problem
SELECT * FROM blocks WHERE
  ial LIKE '%custom-context="PROBLEM_START_ZERO"%'

-- Find books with unprocessed highlights
SELECT DISTINCT doc_id FROM blocks WHERE
  ial LIKE '%custom-type="book"%'
  AND id IN (
    SELECT parent_id FROM blocks WHERE
      ial LIKE '%custom-processed="false"%'
  )
```

---

## Implementation Layers

### Layer 1: SiYuan Schema (FIRST)
- [ ] Book Note template with all sections
- [ ] Theory template (12 sections with IDs)
- [ ] Feynman Problem template (12 sections with IDs)
- [ ] Concept template
- [ ] Spark template (minimal)
- [ ] Session template
- [ ] Hub pages (Theories, Sources, Problems)
- [ ] Attribute schema documentation

### Layer 2: Reader → SiYuan Sync (SECOND)
- [ ] Highlight export API from Readest
- [ ] Book Note auto-creation service
- [ ] Highlight → SiYuan block with attributes
- [ ] CFI preservation for jump-back
- [ ] Context awareness (active problem tracking)

### Layer 3: Backend Services (THIRD)
- [x] Context service (enhance with attribute support)
- [x] Journey service
- [ ] Highlight sync service
- [ ] Processing queue service
- [ ] Agent orchestration service

### Layer 4: Agent Pipeline (FOURTH)
- [ ] Intake agent implementation
- [ ] Enrichment agent implementation
- [ ] Synthesis agent implementation
- [ ] Approval workflow (auto vs manual)
- [ ] Confidence calibration

### Layer 5: Flow Mode Integration (FIFTH)
- [ ] Evidence pool visualization
- [ ] Cross-book passage discovery
- [ ] Enrichment request UI
- [ ] Processing queue visibility
- [ ] Trail tracking

---

## Success Criteria

1. **Capture:** Highlight in Reader → appears in SiYuan Book Note within 30 seconds
2. **Process:** New highlight → Intake agent proposes connections within 1 minute
3. **Navigate:** AI can find all evidence for any theory with single query
4. **Synthesize:** Agent can draft new theory section from 10+ highlights
5. **Trace:** Every insight traceable back to source passage with one click

---

## Open Questions

1. **Attribute syntax:** SiYuan IAL vs frontmatter vs custom blocks?
2. **Sync frequency:** Real-time vs batch for Reader → SiYuan?
3. **Auto-approve defaults:** What confidence threshold feels safe?
4. **Entity extraction model:** Use existing KG entities or extract new?
5. **Conflict resolution:** What if highlight connects to multiple theories?
