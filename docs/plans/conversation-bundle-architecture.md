# Conversation Bundle Architecture

*Design document for structured conversation processing in IES*

**Source:** ChatGPT design conversation (2025-12-07)
**Status:** Proposed
**Created:** 2025-12-08

---

## Executive Summary

Transform conversations from flat transcript storage into rich, structured "Conversation Bundles" that automatically extract insights, generate notes, and enrich the knowledge graph. This enables Flow Mode to surface the "good stuff" from thinking sessions.

---

## Problem Statement

Current state:
- Conversations are exported as flat markdown
- Insights require manual extraction (sparks)
- Flow Mode shows entities but not thinking evolution
- No temporal view of concept understanding
- "Good stuff" gets buried in transcripts

Desired state:
- Conversations automatically parsed into structured messages
- "Moments" (insights, decisions, reframes) extracted automatically
- Notes generated for concepts discussed
- Flow Mode shows journey of understanding over time
- One-click access to highlights from any conversation

---

## Architecture Overview

### Conversation Bundle Model

A Conversation Bundle contains five layers:

```
┌─────────────────────────────────────────────────────────┐
│                   Conversation Bundle                    │
├─────────────────────────────────────────────────────────┤
│  1. Raw Transcript    │ Full conversation, per-message  │
│                       │ metadata (speaker, mode, time)  │
├───────────────────────┼─────────────────────────────────┤
│  2. Moments Layer     │ Extracted insights, decisions,  │
│                       │ reframes, questions, hypotheses │
├───────────────────────┼─────────────────────────────────┤
│  3. Derived Artifacts │ Auto-generated notes: Concept,  │
│                       │ Synthesis, Personal, Design     │
├───────────────────────┼─────────────────────────────────┤
│  4. Graph Links       │ Entities created/modified,      │
│                       │ edges added, evidence refs      │
├───────────────────────┼─────────────────────────────────┤
│  5. Journey Updates   │ Timeline entries, evolution     │
│                       │ narrative, cross-domain links   │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
Conversation Export (ChatGPT/Claude)
         │
         ▼
┌─────────────────┐
│  Parse Service  │ → Structured messages with metadata
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Moment Extractor│ → Insights, decisions, reframes, questions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Note Generator  │ → Concept, Synthesis, Personal notes
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Graph Enricher  │ → Neo4j entities, relationships
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Journey Updater │ → Timeline entries, evolution narrative
└─────────────────┘
```

---

## Schema Definitions

### ConversationBundle (Neo4j Node)

```cypher
(:ConversationBundle {
  id: "conv_2025-12-07_ies_entry_point_cognition",
  title: "Designing Flow Mode Around Entry Points",
  created_at: datetime(),
  source_platform: "chatgpt",
  conversation_kind: ["design", "introspection"],
  is_key_conversation: true,
  project: "IES",
  modes_touched: ["Flow", "Dialogue", "Thinking"]
})
```

### Message (Neo4j Node)

```cypher
(:Message {
  id: "m1",
  bundle_id: "conv_2025-12-07_...",
  author: "user",  // or "assistant"
  timestamp: datetime(),
  content: "Flow doesn't start from zero...",
  mode: "introspection",  // design, planning, troubleshooting
  siyuan_block_id: "20251207221512-abc123"
})
```

### Moment (Neo4j Node)

```cypher
(:Moment {
  id: "moment_1",
  bundle_id: "conv_2025-12-07_...",
  kind: "insight",  // decision, reframe, question, hypothesis, contradiction
  title: "Flow cannot start from zero",
  summary: "User realizes they cannot initiate thinking from blank state",
  importance: 0.92,
  siyuan_block_id: "20251207221600-def456"
})

// Relationships
(:Moment)-[:EXTRACTED_FROM]->(:Message)
(:Moment)-[:REFERENCES]->(:Entity)
(:Moment)-[:SUPPORTS]->(:Requirement)
```

### Moment Types Taxonomy

| Kind | Description | Maps to Entity |
|------|-------------|----------------|
| insight | New understanding or realization | Insight |
| decision | Design or implementation choice | (new: Decision) |
| reframe | Alternative perspective on concept | Reframe |
| question | Open inquiry to explore | FavoriteProblem |
| hypothesis | Testable proposition | Thread |
| contradiction | Tension between ideas | SchemaBreak |
| definition | Clarification of term/concept | Concept |
| metaphor | Illustrative comparison | Reframe |

### DerivedArtifact (Neo4j Node)

```cypher
(:DerivedArtifact {
  id: "artifact_1",
  bundle_id: "conv_2025-12-07_...",
  artifact_type: "requirement",  // insight, theory, question
  title: "Flow Mode requires non-zero entry",
  body_md: "Flow Mode SHALL always start from...",
  status: "proposed",  // draft, accepted, implemented
  siyuan_doc_id: "20251207230000-ghi789"
})

(:DerivedArtifact)-[:DERIVED_FROM]->(:Moment)
(:DerivedArtifact)-[:ABOUT]->(:Entity)
```

### Full JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ConversationBundle",
  "type": "object",
  "required": ["id", "title", "created_at", "messages"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^conv_\\d{4}-\\d{2}-\\d{2}_"
    },
    "title": { "type": "string" },
    "created_at": { "type": "string", "format": "date-time" },
    "tags": {
      "type": "array",
      "items": { "type": "string" }
    },
    "meta": {
      "type": "object",
      "properties": {
        "conversation_kind": {
          "type": "array",
          "items": {
            "enum": ["design", "introspection", "planning", "troubleshooting", "exploration", "synthesis"]
          }
        },
        "is_key_conversation": { "type": "boolean" },
        "project": { "type": "string" },
        "modes_touched": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "participants": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "role": { "enum": ["user", "assistant"] },
          "label": { "type": "string" }
        }
      }
    },
    "messages": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "author_id", "content"],
        "properties": {
          "id": { "type": "string" },
          "author_id": { "type": "string" },
          "timestamp": { "type": "string", "format": "date-time" },
          "content": { "type": "string" },
          "tags": { "type": "array", "items": { "type": "string" } },
          "mode": {
            "enum": ["design", "introspection", "planning", "troubleshooting", "exploration"]
          },
          "source": {
            "type": "object",
            "properties": {
              "platform": { "type": "string" },
              "thread_id": { "type": "string" },
              "message_index": { "type": "integer" }
            }
          }
        }
      }
    },
    "moments": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "kind", "title", "message_ids"],
        "properties": {
          "id": { "type": "string" },
          "kind": {
            "enum": ["insight", "decision", "reframe", "question", "hypothesis", "contradiction", "definition", "metaphor"]
          },
          "title": { "type": "string" },
          "summary": { "type": "string" },
          "message_ids": {
            "type": "array",
            "items": { "type": "string" }
          },
          "tags": { "type": "array", "items": { "type": "string" } },
          "linked_concepts": {
            "type": "array",
            "items": { "type": "string" }
          },
          "importance": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          }
        }
      }
    },
    "derived_artifacts": {
      "type": "object",
      "properties": {
        "insights": { "type": "array" },
        "requirements": { "type": "array" },
        "questions": { "type": "array" },
        "theories": { "type": "array" }
      }
    },
    "graph_links": {
      "type": "object",
      "properties": {
        "concepts_created_or_modified": {
          "type": "array",
          "items": { "type": "string" }
        },
        "edges_added": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "from": { "type": "string" },
              "to": { "type": "string" },
              "relation": { "type": "string" },
              "evidence": {
                "type": "array",
                "items": { "type": "string" }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## SiYuan Integration

### Note Templates

#### Conversation Transcript Note

**Path:** `/Sessions/Conversations/YYYY-MM-DD - {title}.md`

```markdown
---
type: conversation_transcript
bundle_id: conv_2025-12-07_ies_entry_point_cognition
platform: chatgpt
conversation_kind: [design, introspection]
---

# {title}

## Metadata
- **Date:** 2025-12-07
- **Participants:** Chris, IES Agent
- **Key Concepts:** [[Entry Point Cognition]], [[Flow Mode]], [[World Schema]]

## Transcript

### User (22:15:12)
{ial: mode="introspection" moment_refs="moment_1"}

Flow doesn't start from zero because I can't start from zero...

### Assistant (22:15:45)

I understand - you're describing...
```

#### Moments Note

**Path:** `/Sessions/Conversations/YYYY-MM-DD - Moments.md`

```markdown
---
type: conversation_moments
bundle_id: conv_2025-12-07_ies_entry_point_cognition
---

# Moments - {date} {title}

## Insights

- **Flow cannot start from zero** {: importance="0.92"}
  - Kind: insight
  - Links: [[Entry Point Cognition]], [[Flow Mode]]
  - Source: ((transcript-block-id))
  - Summary: User realizes they cannot initiate thinking from blank state

## Design Decisions

- **Flow Mode must always offer anchors** {: importance="0.87"}
  - Kind: decision
  - Links: [[Flow Mode]], [[Mode Transition Engine]]
  - Source: ((transcript-block-id-2))

## Questions

- **What kinds of entry points feel most natural?**
  - Origin: user
  - Links: [[Entry Point Cognition]]
```

#### Concept Note (Auto-Generated)

**Path:** `/Concepts/{domain}/{concept-name}.md`

```markdown
---
type: concept
domain: ADHD
status: evolving
aliases: ["ADHD outcomes", "long-term impacts of ADHD"]
---

# {concept name}

## Definition
{auto-generated from moments + existing definitions}

## Key Points
- {bullet from insight moment}
- {bullet from insight moment}

## Factors
- **Internal:** {extracted factors}
- **External:** {extracted factors}
- **Systemic:** {extracted factors}

## Evidence & Sources
- ((moment-block-id)) - insight from conversation {date}
- ((book-block-id)) - {book title}

## Related Concepts
- [[concept-1]]
- [[concept-2]]

## Open Questions
- {extracted question moments}
```

---

## UI Specifications

### Conversation Dashboard

New view in SiYuan plugin for browsing conversation bundles.

#### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ ◀ Back    Designing Flow Mode Around Entry Points    ⭐ Pin     │
│ Dec 7, 2025 · Design · Introspection · IES                      │
├────────────────────────────────┬────────────────────────────────┤
│                                │  Overview │ Moments │ Graph    │
│  TRANSCRIPT                    ├────────────────────────────────┤
│                                │                                │
│  [User] 22:15                  │  Summary                       │
│  Flow doesn't start from       │  - Entry points needed for     │
│  zero because I can't start    │    Flow Mode initiation        │
│  from zero... ▌ insight        │  - World schema concept        │
│                                │    introduced                  │
│  [Assistant] 22:15             │                                │
│  I understand - you're         │  Key Concepts                  │
│  describing an initiation      │  ┌──────────────────────────┐  │
│  problem...                    │  │ Entry Point Cognition    │  │
│                                │  │ Flow Mode v2             │  │
│  [User] 22:18                  │  │ World Schema             │  │
│  Yes, and the world schema     │  └──────────────────────────┘  │
│  thing is about... ▌ reframe   │                                │
│                                │  Stats                         │
│                                │  4 insights · 2 decisions      │
│                                │  3 questions · 1 theory        │
│                                │                                │
│                                │  [Show Only Good Stuff]        │
└────────────────────────────────┴────────────────────────────────┘
```

#### Tabs

1. **Overview** - Summary, key concepts, stats
2. **Moments** - Grouped by type (insights, decisions, questions)
3. **Artifacts** - Generated requirements, theories
4. **Graph** - Mini-graph of concepts from this conversation

### Flow Mode Journey Tabs

Enhance existing Flow Mode with temporal views:

```
┌─────────────────────────────────────────────────────────────────┐
│  life outcomes with ADHD                                        │
│  A concept evolving across your research & conversations        │
├─────────────────────────────────────────────────────────────────┤
│  Timeline │ Evolution │ Highlights │ Cross-Domain │ Connections │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TIMELINE                                                       │
│                                                                 │
│  Dec 01 ─●─ "Self-worth mediates outcomes"          [insight]   │
│            └─ from: Design conversation about...                │
│                                                                 │
│  Dec 03 ─●─ "Negative outcomes aren't inherent"     [reframe]   │
│            └─ from: Reading notes on...                         │
│                                                                 │
│  Dec 04 ─●─ "Interplay of factors is systemic"      [theory]    │
│            └─ from: Synthesis session...                        │
│                                                                 │
│  Dec 07 ─●─ "Entry Point Cognition influences..."   [insight]   │
│            └─ from: IES design conversation                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### "Just the Good Stuff" View

Condensed view accessible from any conversation:

```
┌─────────────────────────────────────────────────────────────────┐
│  ✨ Highlights from: Designing Flow Mode (Dec 7)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INSIGHTS                                                       │
│  • Flow cannot start from zero - needs entry points    ↩︎       │
│  • World schema shapes how we interpret information    ↩︎       │
│                                                                 │
│  DECISIONS                                                      │
│  • Flow Mode must always offer anchors                 ↩︎       │
│  • Entry points: recent thought, seed, question, entity ↩︎      │
│                                                                 │
│  NEW THEORIES                                                   │
│  • Entry Point Cognition Model (draft)                 →        │
│  • World-Experience Schema (draft)                     →        │
│                                                                 │
│  OPEN QUESTIONS                                                 │
│  • What entry points feel most natural?                ↩︎       │
│  • How does world-schema relate to dev theories?       ↩︎       │
│                                                                 │
│  ↩︎ = jump to source   → = open note                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Conversation Ingest Pipeline (Backend)

**Goal:** Parse conversation exports into structured bundles

| Task | Effort | Dependencies |
|------|--------|--------------|
| 1.1 ChatGPT markdown parser | 2-3 hrs | Existing conversation_parser.py |
| 1.2 Claude export parser | 2-3 hrs | None |
| 1.3 ConversationBundle Neo4j model | 2 hrs | None |
| 1.4 Message node creation | 1 hr | 1.3 |
| 1.5 API endpoint: POST /conversations/ingest | 2 hrs | 1.1-1.4 |

**Builds on:** Existing `ies/backend/src/ies_backend/services/conversation_service.py`

### Phase 2: Moment Extraction Service

**Goal:** Extract moments from parsed conversations

| Task | Effort | Dependencies |
|------|--------|--------------|
| 2.1 Moment extraction prompt engineering | 3-4 hrs | None |
| 2.2 MomentExtractor service class | 2 hrs | 2.1 |
| 2.3 Moment Neo4j model + relationships | 2 hrs | Phase 1 |
| 2.4 Confidence scoring system | 2 hrs | 2.2 |
| 2.5 Human review queue (optional) | 3 hrs | 2.4 |
| 2.6 API endpoint: POST /conversations/{id}/extract-moments | 2 hrs | 2.1-2.4 |

### Phase 3: Auto-Note Generation

**Goal:** Generate SiYuan notes from bundles

| Task | Effort | Dependencies |
|------|--------|--------------|
| 3.1 Note template system | 2 hrs | None |
| 3.2 Transcript note generator | 2 hrs | 3.1 |
| 3.3 Moments note generator | 2 hrs | 3.1 |
| 3.4 Concept note updater | 3 hrs | 3.1 |
| 3.5 SiYuan API integration | 2 hrs | 3.2-3.4 |
| 3.6 Backlink injection | 2 hrs | 3.5 |

### Phase 4: UI Evolution (SiYuan Plugin)

**Goal:** Surface conversation bundles in Flow Mode

| Task | Effort | Dependencies |
|------|--------|--------------|
| 4.1 Conversation Dashboard component | 4-5 hrs | Phase 1-3 |
| 4.2 Moments tab in dashboard | 2 hrs | 4.1 |
| 4.3 "Good Stuff" condensed view | 2 hrs | 4.1 |
| 4.4 Journey Timeline tab in Flow Mode | 3 hrs | Phase 2 |
| 4.5 Evolution narrative view | 3 hrs | 4.4 |
| 4.6 Cross-domain map visualization | 4 hrs | 4.4 |

---

## Gap Analysis vs. Current System

### Backend API Coverage

| Proposed Feature | Current Support | Gap |
|------------------|-----------------|-----|
| Conversation parsing | `conversation_parser.py` exists | Extend for full metadata |
| Bundle storage | `/conversations` endpoint | Need full bundle model |
| Moment extraction | InboxService extracts entities | Need moment-specific extraction |
| Note generation | None | New service required |
| Journey timeline | `/journeys` tracks breadcrumbs | Need temporal concept view |

### Entity Type Mapping

| Proposed Moment | Existing Entity | Action Needed |
|----------------|-----------------|---------------|
| insight | Insight ✓ | Direct mapping |
| decision | — | Add Decision entity type |
| reframe | Reframe ✓ | Direct mapping |
| question | FavoriteProblem (partial) | Extend or add Question type |
| hypothesis | Thread (partial) | Extend or add Hypothesis type |
| contradiction | SchemaBreak ✓ | Direct mapping |

### SiYuan Plugin Impact

New components needed:
- ConversationDashboard.svelte
- MomentsPanel.svelte
- JourneyTimeline.svelte
- CondensedView.svelte

Modifications to existing:
- FlowMode.svelte (add Journey tabs)
- EntityCard.svelte (add conversation links)

---

## Open Questions

1. **Extraction accuracy** — LLM moment extraction may hallucinate. Implement confidence thresholds? Human review queue?

2. **Note sprawl control** — Auto-generating 4+ notes per conversation could overwhelm. What triggers note generation vs. just storing moments?

3. **Existing sparks migration** — Current `/personal/sparks` endpoint stores conversation insights. Migrate to moments or keep both?

4. **Processing triggers** — Auto-process on upload? Manual trigger? Background daemon?

5. **Cross-platform sync** — If notes are generated in SiYuan, how do Readest and IES Reader access them?

---

## Success Criteria

1. **Parse → Store:** Any ChatGPT/Claude export can be ingested as a bundle in <5 seconds
2. **Extract:** Moments extracted with >80% precision (validated on 10 test conversations)
3. **Surface:** Flow Mode shows conversation-sourced insights alongside book-sourced insights
4. **Navigate:** User can go from Flow Mode entity → relevant conversation → exact message in <3 clicks
5. **Temporal:** Journey timeline shows concept evolution across multiple conversations

---

## References

- Source conversation: `ChatGPT.md` (2025-12-07)
- True Vision document: `docs/true-vision-document.md`
- Current architecture: Serena memory `ies_architecture`
- Existing conversation service: `ies/backend/src/ies_backend/services/conversation_service.py`
