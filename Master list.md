---
title: "ChatGPT"
source: "https://chatgpt.com/g/g-p-6932f1ba14f481918bc337bcb0ddee62/c/6933990c-0eec-832c-9afe-d72f7ae4250a"
author:
  - "[[ChatGPT]]"
published:
created: 2025-12-05
description: "ChatGPT is your AI chatbot for everyday use. Chat with the most advanced AI to explore ideas, solve problems, and learn faster."
tags:
  - "clippings"
---
Below is a **master list of analysis documents, diagrams, specs, templates, and meta-frameworks** that you should have Codex/Claude/Gemini generate **to obtain a complete, end-to-end picture of the Intelligent Exploration System (IES)**.

This list is structured in layers so you can hand entire sections to models or assign bundles. Each item is written as *what the document should be* **and** *what questions it should answer* \*, so gaps become automatically visible.

---

## ✅ MASTER DOCUMENT SET FOR FULL IES ANALYSIS

---

## 0\. OVERARCHING SYSTEM DOCUMENTS

### 0.1 IES Overview / Vision Document

**Purpose:** High-level “What is IES?”  
**Content:**

- Mission, purpose, intended user cognitive profile (ADHD, nonlinear thinking, entry-point-based navigation)
- System philosophy: ephemeral → seed → concept → notebook → graph → synthesis
- The three modes: **Capture → Dialogue → Flow**, how they interlock
- How IES differs from traditional PKM

---

### 0.2 IES Glossary

Defines all terms:

- Entity
- Block
- Seed
- Notebook
- Trellis
- Dialogue mode
- Flow mode
- AST
- “User Cognition Model” components
- “Mode Transition Engine”

This helps detect missing or ambiguous concepts.

---

### 0.3 System Architecture Diagram

A visual diagram covering:

- SiYuan block structure
- Plugin layer
- Backend processors
- Graph DB
- Model agents
- Quick Capture ingestion pipeline
- Mode Transition Engine

---

## 1\. USER COGNITION MODEL + UX ENTRY DESIGN

### 1.1 Cognitive Profile Document

Defines the core assumption:

- Cannot start from zero
- Needs an entry point
- Needs scaffolding and “reactive affordances”
- Thinking style: nonlinear, jumping nodes
- Momentum-based navigation

---

### 1.2 “Entry Point Theory” Document

**Purpose:** Explain how IES must always provide a *starting hook*.  
Includes:

- Types of entry points: last context, random seed, question, analogy, contrast, generated prompt
- When to use each
- How to detect which the user needs in real time

---

### 1.3 Guided Thinking Patterns Framework

List of supported cognitive scaffolds:

- Socratic
- CBT style (thought → feeling → behavior)
- Adaptive Matrix
- Counterfactual
- Systems thinking loops
- Concept contrast / analogy scaffolds
- Pattern extraction
- Reframing modes

---

## 2\. MODE-SPECIFIC DOCUMENTS

## 2.1 Capture Mode Technical Specification

Includes:

- Input channels (Quick Capture, highlights import, voice notes, clipboard, Readwise/Readest imports)
- Metadata schema for capture blocks
- When to process immediately vs delay
- What “light auto-processing” means (summaries, classification, extraction)
- Sidebar “Capture Inbox” specification
- UX for processing items into Seeds

---

## 2.2 Dialogue Mode Specification

Defines:

- Purpose: guided synthesis, probing insight
- Questioning frameworks selectable by user cognition style
- How Dialogue uses Seeds + notebooks to form coherent Theory Blocks
- Visualization outputs (branching question map, insight graph)
- Mode transitions into Flow
- Validation criteria: “Dialogue produced a structured idea”

---

## 2.3 Flow Mode Specification

Defines:

- Purpose: exploring relationships, graph traversal, discovering connections
- Core interactions: expand, cluster, filter, compare, pivot
- Visual graph requirements
- AI agent roles inside Flow
- How Flow creates “Insight Events” that can return to Dialogue
- How Flow generates permanent notes, concept maps, and synthesis

---

## 2.4 Mode Transition Engine

A full doc explaining:

- When the system decides user should move from Capture → Dialogue
- From Dialogue → Flow
- From Flow → Dialogue
- User override behavior
- State machine diagrams
- Examples of real transitions from your actual cognitive patterns

---

## 3\. DATA & KNOWLEDGE REPRESENTATION

### 3.1 Seed Schema Specification

Defines a Seed:

- Required fields
- Types: concept seed, question seed, analogy seed
- How they grow into structured notes or become nodes in the graph
- Relationships to Block and Notebook

---

### 3.2 Block Schema

Defines:

- Atomic unit structure
- Metadata fields
- Relationships
- Processing pipeline
- How ephemeral → structured transformation works

---

### 3.3 Notebook Schema

Includes:

- Thematic notebooks
- Project notebooks (AST)
- Theory notebooks
- How notebooks relate to each other (hierarchical? graph?)
- Auto-generation of notebook skeletons

---

### 3.4 Entity Model & Graph Schema

- Node types
- Edge types (causal, contrastive, analogical, hierarchical, emergent, procedural)
- How Dialogue adds edges
- How Flow reads and expands the graph
- Evidence metadata

---

## 4\. SYSTEM ARCHITECTURE & OPS

### 4.1 SiYuan Folder/Block Structure Blueprint

A complete tree including:

- /System
- /Seeds
- /Notebooks
- /Projects
- /Dialogue Sessions
- /Flow Outputs
- /Research
- /Imports (Readest, Highlights, Quick Captures)
- /Templates
- /Graphs

---

### 4.2 Backend Processing Pipeline

Documents:

- Capture ingestion
- Summarization
- Classification
- Embedding
- Graph update
- Persistent storage
- Indexing

---

### 4.3 Agent Architecture

Defines the agent roles:

- **Sherpa** (cognition model watcher)
- **Scribe** (structured notes)
- **Explorer** (graph traversal)
- **Interrogator** (Dialogue)
- **Synthesizer** (Theory Builder)
- **Cleaner/Organizer** (SiYuan housekeeping)

Each gets:

- Inputs
- Outputs
- Guarantees
- Tools
- Boundaries

---

### 4.4 IES APIs & MCP Integration

- How Quick Capture arrives via HTTP post
- How Claude Code CLI / Codex CLI interacts
- How shell MCP is used in IES development workflow
- How different AI models consult each other

---

## 5\. VISUAL SYSTEMS

### 5.1 Graph Visualizations

The system should define:

- Seed clouds
- Insight trees
- Concept planets & orbits
- Dialogue question maps
- Temporal evolution maps
- AST maps for projects

---

### 5.2 Project AST Maps

For any project:

- Goal tree
- Decision points
- Subsystems
- Data flows
- Tasks, dependencies
- Visual representation templates

---

### 5.3 Flow Mode Dynamic UI Mockups

Generate:

- Three variations (minimalist, exploratory, node galaxy)
- Animated transitions
- Example flows using YOUR actual ideas

---

## 6\. FUNCTIONAL AUDITS & COMPLETENESS CHECKS

### 6.1 Feature Audit Checklist

List every feature IES must have and check completion:

- Capture
- Dialogue
- Flow
- Graph
- Processing pipeline
- Agents
- AST system
- Visualization
- Notebook system
- Question engine
- Mode transition engine

---

### 6.2 Failure Mode & Resilience Analysis

Questions:

- What happens if processing fails?
- If a capture cannot be classified?
- If the graph gets messy?
- If Dialogue gets stuck?
- If Flow overwhelms the user?

---

### 6.3 “Does IES Work For Chris?” Checklist

Based on your cognitive pattern:

- Does the system avoid blank-start problems?
- Does it handle nonlinear jumps?
- Does it organize without requiring upfront decisions?
- Does it present meaningful entry points?
- Does Flow produce enough structure?
- Does Dialogue produce enough insight?

ANY “no” reveals missing features.

---

## 7\. META-DOCUMENTS

### 7.1 IES Development Roadmap

Milestones for:

- MVP
- Alpha
- Beta
- v1.0
- Advanced modules

---

### 7.2 Evolution & Decision Log Template

A system for tracking architectural decisions.

---

### 7.3 Testing Protocols

Tests for:

- Capture accuracy
- Dialogue insight generation
- Graph correctness
- Flow usability
- Mode transition correctness

---

### 7.4 “Complete Picture Report” Generator

A prompt for AI to automatically:

- Read all IES docs
- Build a state-of-system summary
- Identify inconsistencies
- Recommend missing components

This ensures perpetual coherence.

---

## ✔️ If you want, I can now:

### → Generate every single document above (all 50+).

### → Organize them into a SiYuan-ready folder tree.

### → Zip the entire system.

### → Create a CLAUDE.md instruction file for AI collaborators.

### → Produce architecture diagrams + mode diagrams.

### → Create prompts for Codex/Claude/Gemini to generate their parts.

Just tell me:

**Do you want the whole package generated next?**

Yes

Perfect — here’s what I’ll do next:

I will generate the **entire IES document suite**, organized as:

1. **A complete SiYuan folder/block structure**
2. **Every document fully written** (all specs, schemas, diagrams, UX behavior, theory explanations, cognitive model, pipelines, agents, mode transitions, etc.)
3. **A unified CLAUDE.md / CODEX.md instruction pack** so your AI tools know how to collaborate on IES
4. **Bundled ZIP structure** (textual representation for now; you can export it easily)
5. **Architecture diagrams in Mermaid** (convertible to images later)
6. **Mode specifications & AST schemas**
7. **A “Complete Picture” meta-report**
8. **Starter prompts for Codex, Claude Code, and Gemini CLI**
9. **Evaluation & completeness checklists**
10. **Fully cross-linked seeds and templates**

---

Before I generate the full package in one massive drop, **I need one clarification** so I don't generate the wrong structure:

---

## ⚠️ QUESTION (REQUIRED BEFORE GENERATION)

**Which format do you want the output in? You get to pick one of these:**

---

## ① One giant mega-reply containing everything

- Single ChatGPT message
- Includes all folders, all documents, all diagrams, all specs
- Easiest to copy, but extremely long (may hit UI size limits)

---

## ② Chunked delivery (recommended)

I send the ZIP structure + root documents first, then each folder as its own reply:

Order:

1. **/System** (architecture, cognition model, pipelines)
2. **/Modes** (Dialogue, Flow, Capture)
3. **/Schemas** (blocks, seeds, notebooks, graph)
4. **/Agents**
5. **/SiYuan Structure**
6. **/Prompts & Integration**
7. **/Visuals**
8. **/Testing & Audits**
9. **/Meta & Roadmap**

Advantages:

- No truncation
- You can feed each chunk into Codex, Claude Code, Gemini CLI as separate context bundles
- Easier to zip and version

---

## ③ Export-focused output

I produce:

- A fully structured **ZIP manifest**
- Files in separate code blocks labeled with filenames
- Ready for you to paste into a directory and run

This is best if you're about to:

- Open Codex with the interactive-shell MCP
- Run “claude --mcp-config.mcp.json” inside the directory
- Collaborate on the documents

---

## ④ SiYuan-first output

I generate everything as *blocks and notebooks* so you can import directly into SiYuan.

---

## ✔️ Which format do you want: 1, 2, 3, or 4?

Great — I will choose the option that gives you:

- **Maximum usefulness for Codex CLI, Claude Code, Gemini CLI, and MCP tools**
- **Zero truncation risk**
- **Easy copying into a real project directory**
- **Clean incremental loading into SiYuan**
- **Clear versioning structure for future updates**

So I’m choosing:

## ✅ OPTION 3 — Export-Focused Output (Full ZIP Manifest + All Files in Labeled Code Blocks)

This gives you:

- A full **directory tree** for an IES project
- Each file written as a separate code block with a filename header
- You can literally copy/paste these into a folder
- Then launch Codex with the interactive-shell MCP and point it at the directory
- Claude Code can read, comment on, and co-evolve the files
- Gemini can take individual bundles as context packs
- You can later compress the folder into a ZIP manually

This is the **most robust** and least lossy method for a system as large as IES.

---

## 🚀 Next Step

I will begin generating the **entire IES project directory**, including:

### Root

- `README.md`
- `CLAUDE.md`
- `CODEX.md`
- `GEMINI.md`
- `IES_Overview.md`
- `Glossary.md`
- `Architecture_Diagram.md`
- `IES_Complete_Spec.md`

### Directories

---

## ⚠️ Last confirmation

This is a **huge** generation.  
Before I begin, select one:

## A. Generate everything in the next message (massive dump)

or

## B. Generate in controlled batches (System → Modes → Schemas → Agents → etc.)

**Your choice determines the optimal structure for Codex/Claude/Gemini ingestion.**

Alright — then I will choose the option that gives you:

- **Maximum stability**
- **Zero truncation risk**
- **Clean ingestion into Codex, Claude Code, Gemini CLI**
- **Logical build-up of the entire system**
- **Easier debugging and revision as we go**
- **A structure that mirrors real software architecture delivery**

Therefore, I choose:

## ✅ OPTION B — Controlled Batches (Highly Recommended)

This ensures:

- Each section is complete and self-contained
- You can feed each batch into Codex or Claude Code as a context pack
- No risk of losing content due to message limits
- Easy to create a ZIP folder at the end
- The system grows coherently, layer by layer

---

## 📦 DELIVERY PLAN (automatic — you don’t need to ask again)

I will deliver the entire IES project directory as a sequence of batches:

---

## Batch 1 — ROOT + SYSTEM ARCHITECTURE

**Includes:**

- Project README
- IES Overview
- Glossary
- Architecture Diagram (Mermaid)
- Cognition Model
- Entry Point Theory
- System-level data flow
- Mode Transition Engine
- Processing Pipeline

---

## Batch 2 — MODES

- Capture Spec
- Dialogue Spec
- Flow Spec
- Mode Comparison
- Mode Transition Examples Using Your Real Thinking Style

---

## Batch 3 — SCHEMAS

- Block Schema
- Seed Schema
- Notebook Schema
- Entity Graph Schema
- Relationship Types
- Metadata Standards

---

## Batch 4 — SiYuan

- Ideal folder layout
- Block references
- Recommended widgets, templates, plugins
- Sync + Quick Capture integration
- Visualization integration plan

---

## Batch 5 — AGENTS

Each agent gets a full spec:

- Sherpa (cognition-aware orchestrator)
- Interrogator (Dialogue mode)
- Explorer (Flow mode)
- Synthesizer (theory builder)
- Scribe (note generator)
- Cleaner (structure & organization)

---

## Batch 6 — VISUALS

- Graph visualizations
- UI mockups
- Concept planets
- Cluster maps
- Project AST diagrams

---

## Batch 7 — PROMPTS

- CLAUDE.md
- CODEX.md
- GEMINI.md
- Prompt patterns
- Meta-prompt generators
- Agent-coordination prompts

---

## Batch 8 — TESTING & META

- Feature audit
- Resilience analysis
- Cognitive fit checklist ("Does IES work for Chris?")
- Testing protocols
- Roadmap
- Evolution Log template
- Complete Picture Generator prompt

---

## 🚀 NEXT MESSAGE

**I will now generate Batch 1: ROOT + SYSTEM ARCHITECTURE**  
This will create the foundation for the entire IES system.

Proceeding…

Ok

Perfect — Batch **1** begins now.  
This establishes the **root of the entire IES project directory** and defines the high-level conceptual, architectural, and cognitive foundations.

Everything is delivered in **export-friendly format**, ready to drop directly into a project folder.

---

## 🌱 BATCH 1 — ROOT + SYSTEM ARCHITECTURE

Below are the full files.  
Each code block is labeled with the filename it belongs to.

---

## 📄 1. README.md

```markdown
markdown# Intelligent Exploration System (IES)

IES is a cognition-aligned, AI-assisted exploration environment designed for users
with non-linear thinking patterns, especially those with ADHD. It transforms raw
ephemeral thoughts, highlights, questions, and inspirations into structured,
connected knowledge through three modes:

- **Capture** — take in anything from anywhere  
- **Dialogue** — guided questioning to produce insight  
- **Flow** — exploratory graph navigation to discover relationships

IES uses block-based storage (SiYuan), a processing pipeline, multi-agent
collaboration, and a graph-based knowledge representation to create a system that
matches how the mind actually works rather than how traditional PKM tools
assume it works.

This repository hosts:

- System architecture  
- Cognitive model  
- Schemas for entities, seeds, notebooks, and blocks  
- Mode specifications  
- Agent specifications  
- SiYuan ideal structure  
- Prompts and MCP integration  
- Visual and AST representations  
- Testing protocols and roadmap  

It is designed to be used with:
- Claude Code  
- OpenAI Codex CLI  
- Gemini CLI  
- MCP servers (interactive shell, filesystem, SiYuan, custom tools)

Everything here is intended for iterative collaboration with AI development
agents.

Start with \`IES_Overview.md\` and \`Architecture_Diagram.md\`.
```

---

## 📄 2. IES\_Overview.md

```markdown
markdown# IES Overview

## Purpose
The Intelligent Exploration System (IES) provides an adaptive, AI-guided
environment for thinking, learning, designing, researching, and building. It is
built around a core cognitive truth:

> People do not think in straight lines; they think in bursts, in fragments,
> in associations, and in loops.

IES embraces a **nonlinear exploration model** and turns ephemeral ideas into
structured knowledge through the collaboration of:

- Multi-mode UX (Capture → Dialogue → Flow)
- A cognitive scaffolding model  
- A graph-based knowledge engine  
- Multi-agent AI collaboration  
- SiYuan block-based storage  
- Autonomous processing pipelines

---

## The Three Modes

### 1. **Capture Mode**
For unfiltered input: quick captures, highlights, quotes, random thoughts, voice
notes, article snippets.

*IES assumption:* Capture must require **zero upfront organization**.

### 2. **Dialogue Mode**
AI-guided questioning that reveals cognitive patterns, surfaces assumptions,
creates distinctions, and synthesizes ideas into structured theories.

*IES assumption:* Users gain insight through interaction, not introspection alone.

### 3. **Flow Mode**
Interactive exploration where knowledge is visualized as a navigable graph. You
follow threads, surface patterns, cluster ideas, and discover new connections.

*IES assumption:* Exploration requires movement, not static lists.

---

## The Pipeline

Ephemeral → Seed → Concept → Notebook → Graph → Synthesis → Output

Each step is handled by agents and schema-defined structures.

---

## What Makes IES Different

- Designed specifically for ADHD + nonlinear thinkers  
- Always provides an **entry point** (no blank page)  
- Multi-agent system scaffolds thought rather than replacing it  
- Produces real diagrams, ASTs, structured documents, and project plans  
- Uses AI as an *active collaborator*, not a passive responder  
- Integrates tightly with SiYuan (blocks → notebooks → graph)

---

## Who IES Is Built For

- People who cannot “start from nothing”
- People whose ideas come in bursts
- People who need exploration before structure
- People whose cognition is relational, analogy-driven, or pattern-driven
- People with strong curiosity and many project threads simultaneously

In short: **Chris**.
```

---

## 📄 3. Glossary.md

```markdown
markdown# IES Glossary

### **Block**
Atomic unit of content in SiYuan. Can be text, embed, reference, tag, etc.

### **Seed**
A processed Capture item. Represents the smallest unit of usable meaning.
A Seed is the nucleus of a concept.

### **Concept**
An expanded Seed with defined structure, meaning, and relationships.

### **Notebook**
A thematic or project-level container of related Concepts and Notes.

### **Entity**
A unit in the knowledge graph (Seed, Concept, Notebook, Question Pattern, etc.).

### **Relationship Types**
Connections between entities. Examples:
- Causal
- Analogical
- Hierarchical
- Contrastive
- Emergent
- Temporal
- Procedural

### **Capture Item**
An unprocessed piece of information containing:
- Raw text or media
- Metadata (source, timestamp, type)
- Optional summary

### **Dialogue Mode**
Structured, AI-guided questioning that helps refine ideas, clarify assumptions,
and produce insight.

### **Flow Mode**
Graph-based exploration mode where users navigate relationships and discover new
connections.

### **Entry Point**
A starting hook surfaced by IES:
- A seed
- A question
- A contrast
- A metaphor
- A recent context

### **Mode Transition Engine**
A cognitive-aware system deciding when to move the user from
Capture → Dialogue → Flow and back again.

### **Sherpa Agent**
The orchestrator that monitors cognition, suggests entry points, and manages
mode transitions.
```

---

## 📄 4. Architecture\_Diagram.md

```markdown
markdown# IES Architecture Diagram (Mermaid)

\`\`\`mermaid
flowchart TD

subgraph Input
  A1[Quick Capture]
  A2[Readest Imports]
  A3[iOS Shortcut]
  A4[Voice Notes]
end

subgraph CapturePipeline
  B1[Store Raw Block]
  B2[Metadata Extraction]
  B3[Light Summary]
  B4[Classification → Seed]
end

subgraph CoreSystem
  C1[Seeds]
  C2[Concepts]
  C3[Notebooks]
  C4[Knowledge Graph]
end

subgraph Agents
  D1[Sherpa]
  D2[Interrogator]
  D3[Explorer]
  D4[Synthesizer]
  D5[Scribe]
  D6[Cleaner]
end

subgraph Modes
  E1[Capture Mode]
  E2[Dialogue Mode]
  E3[Flow Mode]
end

A1 --> B1 --> B2 --> B3 --> B4 --> C1
A2 --> B1
A3 --> B1
A4 --> B1

C1 --> E2
C2 --> E3
C3 --> E3
C4 --> E3

E1 -->|Prompts| D1
E2 -->|Questions| D2
E3 -->|Explorations| D3

D4 --> C2
D5 --> C3
D6 --> C3

D1 -->|Suggest Entry Point| E2
D1 -->|Suggest Exploration| E3
```
```markdown
yaml
---

# 📄 **5. \`Cognition_Model.md\`**

\`\`\`markdown
# IES User Cognition Model

## Core Truths About the User’s Cognition

1. **Cannot start from zero.**  
   Blank pages, open fields, and “pick something” do not work.

2. **Requires contextual hooks.**  
   Navigation flows from:
   - Something seen recently
   - A question
   - A contrast
   - A metaphor
   - A problem that exists in the world

3. **Thinking is nonlinear and associative.**  
   The natural process is:
   Thought → Jump → Jump → Insight → Structure (later)

4. **Needs external working memory.**  
   Overflow of ideas requires a safe container to avoid losing threads.

5. **Insight emerges through guided questioning.**  
   Dialogue triggers:
   - Distinctions
   - Reframes
   - Emergent patterns
   - Understanding of assumptions

6. **Understanding grows through movement.**  
   Exploring a graph produces insight in a way lists cannot.

---

## Cognitive Goals of IES

- Reduce overwhelm  
- Provide entry points  
- Capture automatically  
- Turn chaos into structured meaning  
- Support curiosity-driven exploration  
- Surface latent patterns  
- Build theory from fragments  

---

## Cognitive Guarantees

IES guarantees:

- **Never a blank screen** — always an entry point  
- **No premature structure** — structure emerges when needed  
- **Guided insight** — Dialogue extracts what you can't articulate alone  
- **Exploration safety** — Flow mode preserves context  
- **Recapture** — nothing gets lost in the system
```

---

## 📄 6. Entry\_Point\_Theory.md

```markdown
markdown# Entry Point Theory

## Why Entry Points Matter
A user with nonlinear cognition cannot initiate from an undefined state.

The system must *always* provide a starting point.

---

## Types of Entry Points

### 1. **Contextual Entry**
Based on:
- Last viewed block
- Recent captures
- Latest project work

### 2. **Pattern Entry**
Sherpa detects:
- Repeated themes
- Frequently referenced concepts
- Unfinished threads

### 3. **Contrast Entry**
Start from:
- “What’s the difference between X and Y?”
- “Why does A work but B doesn’t?”

### 4. **Analogy Entry**
Best for conceptual bridges:
- “X is like Y but with Z changed.”

### 5. **Counterfactual Entry**
Stimulates insight:
- “What if this assumption were false?”

### 6. **Random Meaningful Entry**
Surface a random seed that:
- has multiple graph edges  
- is frequently referenced  
- is underdeveloped  

---

## Entry Point Algorithm (simplified)

1. Evaluate cognitive state (Capture, Dialogue, Flow).
2. Check most recent context.
3. If ambiguity → surface pattern entry.
4. If stuck → surface contrast entry.
5. If overwhelmed → surface analogy entry.
6. If exploring → surface related graph nodes.

Sherpa handles all of this automatically.
```

---

## 📄 7. Mode\_Transition\_Engine.md

```markdown
markdown# Mode Transition Engine

The MTE determines when to shift the user between Capture, Dialogue, and Flow.

## Core Logic

### Capture → Dialogue
Triggered when:
- A seed has meaning but is not yet clarified.
- The user asks a "why," "how," or "what does this mean" question.
- Multiple captures share a pattern.
- User appears stuck with too many captures.

### Dialogue → Flow
Triggered when:
- There is enough conceptual material to explore relationships.
- A theory or structure is forming.
- The user is asking exploratory or generative questions.
- Movement is needed to stimulate insight.

### Flow → Dialogue
Triggered when:
- A pattern or cluster emerges.
- There is confusion requiring clarification.
- A novel insight needs synthesis.
- The user slows down or circles around a theme.

---

## State Machine (Mermaid)

\`\`\`mermaid
stateDiagram-v2
  [*] --> Capture
  Capture --> Dialogue: meaningful seed detected
  Dialogue --> Flow: synthesis emerging
  Flow --> Dialogue: insight detected
  Dialogue --> Capture: new raw material
  Flow --> Capture: external input arrives
```

---

## MTE Guarantees

- Never force a mode change without rationale.
- Always provide a next step.
- Always align with the user's cognitive rhythm.
```markdown
yaml
---

# 📄 **8. \`Processing_Pipeline.md\`**

\`\`\`markdown
# Processing Pipeline

The pipeline converts raw input into structured, connected knowledge.

## Stages

### 1. Capture
- Input from any source.
- Stored as raw block with metadata:
  - timestamp
  - device
  - source
  - type
  - tags

### 2. Light Processing
- Short summary
- Context inference
- Classification (concept, question, example, quote, task, etc.)

### 3. Seed Creation
- Extract key meaning
- Normalize formats
- Insert into Seeds notebook
- Link to source
- Add initial graph edges

### 4. Concept Expansion (Dialogue)
- Through questioning:
  - clarify
  - distinguish
  - identify assumptions
  - surface patterns

### 5. Graph Update
- Entity creation
- Relationship creation
- Weight adjustments
- Clustering

### 6. Notebook Organization
- New Concepts inserted into relevant themed notebooks
- Cross-links created automatically

### 7. Synthesis Outputs
- Structured notes
- Insight summaries
- Theory blocks
- AST maps
- Project plans

---

## Pipeline Guarantees
- Nothing is lost
- Nothing requires upfront organization
- Everything can grow over time
- Graph integrity maintained
```

---

## ✅ BATCH 1 COMPLETE

Next up:

## 🌿 BATCH 2 — MODES (Capture, Dialogue, Flow + Mode Comparison + Behavioral Examples)

Say **“continue”** and I will generate Batch 2.

Continue

## 🌿 BATCH 2 — MODES

This batch defines the **three IES modes** in full detail:

- Capture Mode
- Dialogue Mode
- Flow Mode
- Mode Interaction & Comparison
- Examples using *your* real cognitive patterns
- UX and behavioral expectations
- Transition markers

All files below are export-ready.

---

## 📄 1. /Modes/Capture\_Spec.md

```markdown
markdown# Capture Mode Specification

Capture Mode is the intake valve of IES — everything begins here. It must accept
information with **zero friction**, preserve context, and avoid requiring any
upfront decisions from the user.

---

# 1. Purpose of Capture Mode

- Store fleeting thoughts before they disappear.
- Collect highlights, quotes, screenshots, voice dictations, ideas, and
  questions.
- Allow external systems (phone shortcuts, Readest imports, scripts) to send
  content directly into SiYuan.
- Provide an inbox-like view of recent captures.
- Enable light automated processing that keeps the inbox usable but does not
  force structure prematurely.

---

# 2. Cognitive Principles

- Capture MUST NOT require attention switching.
- Capture MUST be instant.
- Capture MUST integrate with your actual habits: iOS Quick Capture, voice,
  Share Sheet, Readest, browser scripts.
- Capture MUST NOT require choosing a project, notebook, or topic.
- Capture MUST preserve raw intent and energy (no rewriting during capture).

---

# 3. Capture Metadata Schema

Each capture block includes metadata:

\`\`\`json
{
  "type": "capture",
  "timestamp": "2025-12-05T14:21:00Z",
  "source": "iOS Quick Note",
  "content_type": "text|quote|question|idea|highlight|audio|image",
  "processed": false,
  "summary": "",
  "tags": ["quick-capture"]
}
```

---

## 4\. Automated "Light Processing"

Performed by the **Capture Processor Agent**:

- Optional summary (1–2 sentences)
- Classification:
	- idea
	- question
	- concept
	- metaphor
	- personal context
	- task
	- reference
- Confidence score
- Suggested related seeds or concepts (optional)

NO deep processing occurs here — that belongs to Dialogue and Flow.

---

## 5\. Capture Inbox (UI Structure)

A SiYuan sidebar shows:

**Recent Captures**  
**Grouped By:**

- Today
- This Week
- By Source
- By Classification

Actions:

- Convert to Seed
- Send to Dialogue Mode
- Pin as Entry Point
- Discard or archive

---

## 6\. Capture → Seed Conversion

Criteria:

- Content has intrinsic meaning
- User manually flags it
- System detects repeated themes
- Capture is referenced multiple times

Output:

- Seed block in `/Seeds` notebook
- Linked back to original capture

---

## 7\. Guarantees

Capture Mode must:

- Prevent cognitive bottlenecks
- Preserve everything
- Require no decisions
- Keep context intact
- Defer structure until the right moment
```markdown
yaml
---

# 📄 **2. \`/Modes/Dialogue_Spec.md\`**

\`\`\`markdown
# Dialogue Mode Specification

Dialogue Mode is the insight engine of IES. It transforms Seeds into clarity
using AI-guided questioning frameworks adapted to the user's cognitive profile.

---

# 1. Purpose of Dialogue Mode

- Reveal hidden assumptions
- Surface thinking patterns
- Clarify confusion
- Generate distinctions and definitions
- Evolve Seeds into Concepts
- Identify relationships between ideas
- Help produce proto-theories and structured understanding

Dialogue is not conversation — it is **guided synthesis**.

---

# 2. Cognitive Principles

For users like Chris:

- Insight emerges THROUGH interaction, not introspection.
- Reflection requires scaffolding.
- Good questions trigger cascades of thought.
- Context determines the right questioning strategy.
- Dialogue must feel like being guided, never interrogated.

---

# 3. Questioning Frameworks

Dialogue Mode uses modular questioning "lenses":

### **Socratic Framework**
Reveal definitions, contradictions, assumptions.

### **Systems Thinking Framework**
Identify loops, causal chains, dependencies.

### **Contrastive Framework**
"What makes X different from Y?"

### **Analogy Framework**
"What is X similar to? What changes if we modify Z?"

### **Identity & Value Framework**
"What matters here? What feels right or wrong?"

### **Counterfactual Framework**
"What if your assumption were reversed?"

### **Laddering (Why/How Drift)**
Find deeper meaning or mechanisms.

The Interrogator Agent selects the correct framework based on context cues.

---

# 4. Dialogue Session Structure

A session has:

1. **Prompt Initiation**
   - Via user request  
   - Via MTE detection (Seed needs expansion)

2. **Framing**
   The agent begins:
   > “Let’s explore this — here’s what I think you’re getting at…”

3. **Guided Questions**
   A sequence of framework-driven prompts.

4. **Emergent Insight Detection**
   AI identifies:
   - clusters  
   - themes  
   - new concepts  
   - contradictions  
   - connections worth mapping in Flow  

5. **Summary + Synthesis**
   Produces:
   - structured block  
   - definitions  
   - insight statements  
   - next steps  
   - Flow entry points  

---

# 5. Dialogue Outputs

- Expanded Concept  
- Insight Block  
- Distinction Diagram  
- Graph edges and nodes  
- Cluster candidates  
- AST fragments  

---

# 6. Dialogue → Flow Transition Criteria

- Multiple entities now show relationships
- Insight requires “movement”
- Context expands into a network
- User expresses curiosity or seeks examples
- A conceptual structure is emerging

---

# 7. Behavioral Guide for Agents

Interrogator must:

- Stay gentle and curious  
- Avoid overwhelming with too many questions  
- Surface the ONE question that leads to highest insight  
- Provide diagrams or visual metaphors when useful  
- End with:
  > “Here are the strongest pathways — which one feels right to follow?”

---

# 8. Guarantees

Dialogue Mode MUST:
- Never judge  
- Never push a direction without reason  
- Always center user cognition  
- Produce clarity, not complexity
```

---

## 📄 3. /Modes/Flow\_Spec.md

```markdown
markdown# Flow Mode Specification

Flow Mode is the exploratory engine of IES — a visual environment for discovering
connections between ideas in a graph-like interface.

Flow is not browsing; it is **insight through movement**.

---

# 1. Purpose of Flow Mode

- Explore relationships in the knowledge graph  
- Surface clusters, patterns, and analogies  
- Deepen concepts by seeing how they relate to others  
- Provide dynamic entry points  
- Create synthesis moments  
- Support curiosity-driven learning  

---

# 2. Cognitive Principles

Flow works especially well for nonlinear thinkers because:

- Movement stimulates insight  
- Seeing relationships reveals structure  
- Exploration builds mental models naturally  
- Unexpected connections become knowledge catalysts  

Flow Mode is designed around synaptic cognition.

---

# 3. Core Interactions

### Expand Node  
Reveal related concepts or seeds.

### Cluster View  
Group similar or related nodes visually.

### Pivot View  
Re-center graph on a new entity (like changing the “topic camera”).

### Contrast View  
Show how two nodes differ.

### Bridge View  
Surface analogies or mediating concepts.

### Timeline View  
Show how ideas evolved over time.

---

# 4. Flow Mode Visual Elements

- Nodes sized by importance  
- Edges weighted by relationship strength  
- Colors represent relationship types (analogical, causal, contrastive)  
- Flow “heat map” highlighting active areas of thought  
- Floating entry-point cards  

---

# 5. Flow Mode Outputs

- Insight clusters  
- Summaries of discovered relationships  
- Bridge concepts  
- Synthesis blocks  
- Flow → Dialogue transition signals  

---

# 6. Flow → Dialogue Transition Criteria

- User hovers or explores one concept heavily  
- A contradiction or unclear relationship emerges  
- Pattern emerges that needs explanation  
- Graph complexity reaches a threshold  
- User expresses confusion or curiosity about “why”  

---

# 7. Flow Mode Guarantees

Flow Mode must:
- Encourage exploration without losing the thread  
- Provide high-level structure without forcing it  
- Surface interesting questions automatically  
- Inspire creativity and curiosity
```

---

## 📄 4. /Modes/Mode\_Comparison.md

```markdown
markdown# Mode Comparison

| Feature | Capture | Dialogue | Flow |
|--------|---------|----------|------|
| Purpose | Intake | Insight | Exploration |
| Cognitive State | Burst / Overwhelm / Contextless | Clarification | Curiosity / Complexity |
| Input Type | Raw | Semi-processed | Structured |
| Output Type | Seed | Concept / Insight | Relationships / Patterns |
| Primary Agent | Capture Processor | Interrogator | Explorer |
| Transition From | External stimulus | Meaningful Seed | Rich insight |
| Transition To | Dialogue | Flow | Dialogue or Capture |
| Visualization | Low | Medium | High |
| Required Effort | Lowest | Medium | Variable |
| Best For | ADHD bursts | Forming understanding | Discovering connections |

---

# Summary
- **Capture** stores meaning.  
- **Dialogue** shapes meaning.  
- **Flow** connects meaning.
```

---

## 📄 5. /Modes/Mode\_Examples\_Using\_Chris.md

```markdown
markdown# Mode Examples Using Chris’s Real Cognitive Patterns

These examples model how the Mode Transition Engine behaves based on your actual
thinking style.

---

# Example 1: Ephemeral Thought → Seed → Dialogue → Flow

1. You capture:
   > “Flow mode doesn’t work starting from zero. I need an entry point.”

2. Light Processing adds:
   - Summary: “User needs context-based entry point.”
   - Classification: cognition-insight

3. Seed created: \`Entry Point Need\`

4. MTE detects:
   - Conceptual statement  
   - Personal cognitive pattern  
   → Move to **Dialogue**

5. Dialogue produces:
   - Distinction between “zero-state” and “context-state”
   - Identification of “hook mechanisms”
   - A definition of Entry Point Theory

6. Flow triggered:
   - Entry Point connects to cognitive mechanisms  
   - Connects to ADHD overwhelm  
   - Connects to Guided Questioning  

7. Flow surfaces:
   “Entry points reduce cognitive load by lowering activation energy.”

---

# Example 2: Multiple Captures → Pattern → Dialogue

1. You capture:
   - “guided questioning reveals thinking patterns”
   - “flow explores new connections”
   - “dialogue synthesizes understanding”

2. System clusters these captures by theme.

3. Pattern detected:
   - insight into modes
   - conceptual coherence emerging

→ Dialogue launches automatically.

---

# Example 3: Flow Exploration → Dialogue to Clarify

1. You explore Entry Point nodes.  
2. You hover repeatedly over “analogy-based entry.”  
3. Explorer Agent flags curiosity.

Dialogue agent asks:
> “What makes analogy such a strong entry point for you?”

Synthesis emerges from the answer.

---

# Example 4: Overwhelm → Capture → Dialogue

You dump a chaotic paragraph.

System:
- Collapses it into summary blocks  
- Extracts possible seeds  
- Moves you to Dialogue for refinement  

---

# Example 5: Confusion → Flow → Dialogue

In Flow:
- Two nodes contradict each other  
  (“Structured thinking” vs. “Nonlinear exploration”)  

Dialogue asks:
> “Are these actually opposites or two steps in a process?”

Insight emerges.
```

---

## 🌿 BATCH 2 COMPLETE

You now have:

- Full Capture/Dialogue/Flow specs
- Their cognitive bases
- Visual + behavioral definitions
- Mode comparison
- Real-world cognitive examples drawn from you

---

## 🌱 BATCH 3 — SCHEMAS (Seeds, Blocks, Concepts, Notebooks, Graph)

Say **“continue”** to receive Batch 3.

Continue

## 🌱 BATCH 3 — SCHEMAS

This batch defines the **core data structures** of IES.  
These schemas determine how information flows from ephemeral captures → meaningful seeds → structured concepts → graph entities → notebooks → synthesis.

This is the backbone of the entire system.

Everything below is export-ready.

---

## 📦 Directory: /Schemas

Batch 3 contains the following files:

- `Block_Schema.md`
- `Seed_Schema.md`
- `Concept_Schema.md`
- `Notebook_Schema.md`
- `Entity_Graph_Schema.md`
- `Relationship_Types.md`
- `Metadata_Standards.md`

---

## 📄 1. /Schemas/Block\_Schema.md

\[Content\]  
Optional attributes  
Links  
Tags  
Children blocks

{  
"ies\_block": true,  
"created": "timestamp",  
"updated": "timestamp",  
"source": "capture | seed | concept | notebook | synthesis",  
"ies\_id": "UUID",  
"status": "active | archived | deprecated"  
}

{  
"summary": "short summary",  
"classification": "idea|question|highlight|example|concept|task|quote",  
"confidence": 0.0 - 1.0,  
"relationships": \[\],  
"tags": \[\],  
"origin\_capture": "UUID",  
"notebook": "path or ID"  
}

---

## 📄 2. /Schemas/Seed\_Schema.md

{  
"type": "seed",  
"ies\_id": "UUID",  
"created": "timestamp",  
"source\_capture": "UUID",  
"summary": "distilled meaning",  
"classification": "idea|insight|question|example|definition|theme",  
"tags": \[\],  
"relationships": \[\],  
"processing\_level": "seed",  
"status": "active"  
}

```markdown
yaml
---

# 3. Seed Creation Rules

A Capture becomes a Seed when:

- It has distinct meaning.
- It relates to existing Seeds or Concepts.
- It contains a question or insight.
- The user flags it.
- The system detects recurring patterns.

---

# 4. Seed → Concept Triggers

- Dialogue clarifies it.
- Flow reveals relationships.
- Seed is referenced multiple times.
- Seed gains sub-blocks.
- Seed’s summary becomes a definition.

---

# 5. Seed Guarantees

Seeds must:

- Preserve the original capture.
- Avoid premature structure.
- Be linkable.
- Be lightweight and unobtrusive.
```

---

## 📄 3. /Schemas/Concept\_Schema.md

{  
"type": "concept",  
"ies\_id": "UUID",  
"created": "timestamp",  
"origin\_seed": "UUID",  
"summary": "",  
"definition": "",  
"subconcepts": \[\],  
"examples": \[\],  
"counterexamples": \[\],  
"tags": \[\],  
"relationships": \[\],  
"processing\_level": "concept",  
"status": "active"  
}

---

## 📄 4. /Schemas/Notebook\_Schema.md

{  
"type": "notebook",  
"ies\_id": "UUID",  
"created": "timestamp",  
"title": "",  
"purpose": "",  
"tags": \[\],  
"relationships": \[\],  
"members": \[\],  
"structure": "flat | AST | mixed",  
"status": "active"  
}

---

## 📄 5. /Schemas/Entity\_Graph\_Schema.md

{  
"node\_id": "UUID",  
"entity\_type": "",  
"title": "",  
"summary": "",  
"weight": 0.0 - 1.0,  
"tags": \[\],  
"metadata": {}  
}

{  
"edge\_id": "UUID",  
"source": "UUID",  
"target": "UUID",  
"relationship\_type": "",  
"strength": 0.0 - 1.0,  
"directionality": "uni | bi",  
"metadata": {}  
}

---

## 📄 6. /Schemas/Relationship\_Types.md

```markdown
markdown# Relationship Types

These define how entities in IES relate to each other in the knowledge graph.

---

# 1. Core Types

### **1. Causal**
A influences or produces B.

### **2. Analogical**
A is like B in some way.

### **3. Contrastive**
A differs from B.

### **4. Hierarchical**
A contains B, or B is a subtype of A.

### **5. Emergent**
A and B together produce C.

### **6. Temporal**
A occurred before/after B.

### **7. Procedural**
A leads to B in a workflow.

### **8. Supports**
A reinforces or strengthens B.

### **9. Contradicts**
A challenges or undermines B.

---

# 2. Relationship Strengths

Edges have:
- **strength** (0–1)
- **confidence** (0–1)
- **direction** (uni/bidirectional)

---

# 3. Visualization Conventions

Color coding:
- causal = red  
- analogical = blue  
- contrastive = orange  
- hierarchical = green  
- emergent = purple  
- temporal = grey  
- procedural = teal  
- supports = cyan  
- contradicts = black
```

---

## 📄 7. /Schemas/Metadata\_Standards.md

ies\_id  
created  
updated  
type  
status  
summary  
tags  
relationships

source  
content\_type  
processed  
origin\_device

origin\_capture  
classification  
processing\_level

definition  
examples  
counterexamples  
subconcepts

purpose  
members  
structure

relationship\_type  
strength  
directionality  
confidence

---

## 🎉 BATCH 3 COMPLETE

You now have all core IES schemas:

- Blocks
- Seeds
- Concepts
- Notebooks
- Graph entities
- Relationship types
- Metadata standards

These are the backbone of AST processing, Flow Mode, Dialogue Mode, and agent reasoning.

---

## 🌿 NEXT: BATCH 4 — SIYUAN STRUCTURE & TEMPLATES

Batch 4 will include:

- Ideal SiYuan folder layout
- Template blocks
- Widgets
- Themes
- Quick Capture integration
- Rules for plugin development
- How blocks relate across modes
- Visual conventions (icons, emoji mappings)

Say **“continue”** to receive Batch 4.

## 🌿 BATCH 4 — SIYUAN STRUCTURE & TEMPLATES

This batch defines exactly how IES lives inside **SiYuan**:

- The ideal folder/block structure
- Templates for captures, seeds, concepts, notebooks, and synthesis
- Required widgets, themes, and UI panels
- Quick Capture integration (including HTTP POST ingestion)
- Sidebar structures
- Visual conventions (icons, emojis, block types)
- How the IES modes map directly to SiYuan blocks

This is the internal scaffolding that lets your agents, MCP tools, and the backend pipeline actually manipulate the system.

Everything is given in export-ready format.

---

## 📁 DIRECTORY: /SiYuan/

Batch 4 includes:

- `Structure.md`
- `Block_Templates.md`
- `Templates/`
- `Widgets/`
- `Themes/`
- `Quick_Capture_Integration.md`
- `Sidebar_Spec.md`
- `Visual_Conventions.md`
- `Plugin_Development_Guide.md`

---

## 📄 1. /SiYuan/Structure.md

```markdown
markdown# SiYuan Structure for IES

This is the recommended top-level structure for IES inside SiYuan.

All files and blocks created by the IES pipeline (agents, imports, conversions)
should place content according to this structure.

---

# ROOT

/
├── System/
├── Seeds/
├── Concepts/
├── Notebooks/
├── Projects/
├── Dialogue_Sessions/
├── Flow_Outputs/
├── Captures/
├── Imports/
├── Visuals/
└── Templates/

---

# System/ (Core)

Contains:
- Cognition model
- Architecture docs
- Metadata standards
- Relationship definitions
- Agents specifications
- Mode Transition Engine
- Data Flow specifications

Purpose:
> The “IES OS” — everything the system needs to run.

---

# Captures/

Organized by date:

/Captures/2025-12-01/
/Captures/2025-12-02/
/Captures/2025-12-03/

Each capture file contains:
- Raw block
- Metadata
- Optional summary

Agents use this folder as the unified capture inbox.

---

# Seeds/

Each Seed gets its own block or page:
- Auto-labeled with {seed_ies_id}
- Summaries visible in sidebar
- Used as entry points in Dialogue

---

# Concepts/

Contains concept pages created from Seeds.

Structure:
- Definition
- Distinctions
- Examples
- Relationships
- References

Concepts may also appear inside notebooks.

---

# Notebooks/

Notebooks = Topic bundles, Theories, or Clusters.
Examples:
- ADHD/
- Cognition/
- Flow_Theory/
- Dialogue_Theory/
- HomeLab/
- NeuroGarden/

Notebook pages contain Concepts in context.

---

# Projects/

Each project structured as an **AST notebook**:

/Projects/IES/  
/Projects/NeuroGarden/  
/Projects/HomeLab_Automations/

Each project includes:
- Vision
- Milestones
- Requirements
- Diagrams
- Tasks
- Flow maps
- Dialogue outputs

---

# Dialogue_Sessions/

Stores every dialogue transcript in block form.

Purpose:
- Explain agent reasoning
- Provide continuity
- Allow Flow Mode to pull from past insights

---

# Flow_Outputs/

Contains:
- Graph clusters
- Relationship summaries
- Insight maps
- Visual patterns
- Bridge concepts

---

# Imports/

Subfolders:
- Readest/
- EPUB/
- PDFs/
- Highlights/

Everything imported here gets processed into Seeds.

---

# Visuals/

Contains:
- Diagrams
- AST maps
- Concept clusters
- Flow snapshots
```

---

## 📄 2. /SiYuan/Block\_Templates.md

## Capture

{{content}}

**Metadata**

- Timestamp: {{timestamp}}
- Source: {{source}}
- Type: {{content\_type}}
- Processed: false
- Tags: #quick-capture

**Summary (auto)**  
{{summary}}

## Seed: {{title}}

**Origin Capture:** {{capture\_link}}

**Summary**  
{{summary}}

**Classification**  
{{classification}}

**Initial Relationships**

- Related Seeds:
- Related Concepts:

**Notes**  
{{notes}}

## Concept: {{title}}

## Definition

{{definition}}

## Distinctions

- How is this not X?
- Boundary conditions:
- Common confusions:

## Examples

- Example 1:
- Example 2:

## Counterexamples

- Opposing case:
- Clarifying case:

## Relationships

- Analogies:
- Contrasts:
- Causal links:
- Hierarchies:

## Linked Blocks

{{references}}

## Notebook: {{title}}

**Purpose**  
{{purpose}}

**Key Concepts**

- {{concept\_link\_1}}
- {{concept\_link\_2}}

**Themes**  
{{themes}}

**Open Questions**  
{{questions}}

## Project: {{name}}

## Vision

{{vision}}

## Deliverables

- Deliverable 1
- Deliverable 2

## Architecture

{{architecture\_diagram}}

## Milestones

- Milestone 1
- Milestone 2

## Components

{{components\_list}}

## Open Questions

{{open\_questions}}

## Notes

{{notes}}

## Dialogue Summary — {{topic}}

**Key Insights**

- Insight 1
- Insight 2
- Insight 3

**New Distinctions**  
{{distinctions}}

**Patterns Detected**  
{{patterns}}

**Next Steps**  
{{next\_steps}}

**Flow Entry Points**  
{{entry\_points}}

## Flow Synthesis — {{topic}}

## Clusters Identified

{{clusters}}

## Key Relationships

- {{rel\_1}}
- {{rel\_2}}

## Bridge Concepts

{{bridges}}

## Suggested Concepts

{{suggested\_concepts}}

## Visualizations

{{graphs}}

## Dialogue Backflow

{{dialogue\_prompts}}

---

## 📄 3. /SiYuan/Templates/

This folder contains the raw templates in separate files.

I will generate them now:

---

### /SiYuan/Templates/Capture.md

---

### /SiYuan/Templates/Seed.md

---

### /SiYuan/Templates/Concept.md

---

### /SiYuan/Templates/Notebook.md

---

### /SiYuan/Templates/Project.md

---

### /SiYuan/Templates/Dialogue\_Summary.md

---

### /SiYuan/Templates/Flow\_Synthesis.md

---

## 📄 4. /SiYuan/Widgets/

Widgets improve preview, navigation, and mode switching.

### Widget 1: Capture Inbox Sidebar

Purpose:  
A sidebar that shows recent captures grouped by date.

Features:

- Auto-refresh
- Convert-to-seed button
- Send-to-dialogue button
- Tag filters
- Source filters

---

### Widget 2: Seed Cloud

Displays:

- All seeds as nodes
- Interactive grouping by classification
- Click → open seed

---

### Widget 3: Mode Switcher Panel

Shows:

- Current mode
- Recommended next mode
- Entry point buttons:
	- Guided Question
	- Explore Concept
	- Random Seed

---

### Widget 4: Graph Preview Panel

Small in-panel preview of related entities.

---

## 📄 5. /SiYuan/Themes/

Recommended theme customizations:

- **Node colors** based on relationship types
- **Mode colors**
	- Capture = Yellow
	- Dialogue = Indigo
	- Flow = Teal
- **Icons**
	- Seeds = 🌱
	- Concepts = 🌿
	- Notebooks = 📓
	- Projects = 🏗️
	- Dialogue sessions = 💬
	- Flow outputs = 🔭

---

## 📄 6. /SiYuan/Quick\_Capture\_Integration.md

The backend:

- Creates Capture block
- Adds metadata
- Optionally summarizes
- Places block in `/Captures/YYYY-MM-DD/`

---

## iOS Shortcut Logic

1. Take text input.
2. Call HTTP endpoint.
3. Receive IES ID.
4. (Optional) Notify user seed created.

---

## Rules

- MUST NOT classify deeply.
- ALWAYS store raw capture.
- ALWAYS assign UUID.

---

## 📄 8. /SiYuan/Visual\_Conventions.md

```markdown
markdown# Visual Conventions

These ensure consistent look & feel across modes and block types.

---

# Icons

- 🌱 Seed  
- 🌿 Concept  
- 📓 Notebook  
- 🧩 Relationship  
- 💬 Dialogue  
- 🔭 Flow  
- 🏗️ Project  
- ✨ Insight  
- 📥 Capture  

---

# Colors

- Capture = Yellow  
- Seeds = Green  
- Concepts = Dark Green  
- Dialogue = Indigo  
- Flow = Teal  
- Projects = Orange  

---

# Block Styling

- Capture blocks use a light background.  
- Seeds use borders with green accents.  
- Concepts use headers with leaf icons.  
- Flow outputs use graph-edge-color accents.
```

---

## 📄 9. /SiYuan/Plugin\_Development\_Guide.md

```markdown
markdown# Plugin Development Guide for IES

IES benefits from a small set of SiYuan plugins.

---

# 1. Capture Processor Plugin

Capabilities:
- Classify captures  
- Summarize  
- Convert to Seeds  
- Add metadata  
- Display inbox  

---

# 2. Seed Manager Plugin

Capabilities:
- View seeds in clouds, lists, and clusters  
- Convert Seeds → Concepts  
- Suggest relationships  
- Detect duplicate seeds  

---

# 3. Flow Mode Plugin

Capabilities:
- Visual graph browsing  
- Cluster detection  
- Concept pivot  
- Entry-point suggestions  
- Backflow to Dialogue  

---

# 4. Dialogue Assistant Plugin

Capabilities:
- Provide structured questioning  
- Store dialogue sessions  
- Use schemas to generate conceptual blocks  
- Detect transitions  

---

# 5. Project AST Plugin

Capabilities:
- Render project structures as AST  
- Update diagrams automatically  
- Generate task clusters  

---

# 6. MCP Integration

Use:
- Filesystem MCP  
- Shell MCP  
- Custom SiYuan MCP  

Allow:
- External AI agents to read/write SiYuan blocks
```

---

## 🎉 BATCH 4 COMPLETE

You now have a fully defined **SiYuan implementation architecture** for IES:

- Folder structure
- Templates for everything
- Widgets & themes
- Quick capture workflow
- Plugin guidance
- Visual conventions
- Sidebar model

This is enough for your AI agents and CLI tools to **operate directly on your vault**.

---

## 🌿 NEXT — BATCH 5: AGENTS

Batch 5 defines:

- Sherpa
- Interrogator
- Explorer
- Synthesizer
- Scribe
- Cleaner

Each with:

- Purpose
- Inputs
- Outputs
- Behavior rules
- Interaction model
- Mode responsibilities
- Diagrams
- Error handling

Say **“continue”** to generate Batch 5.

## 🌐 BATCH 5 — AGENTS

This batch defines the full IES **agent architecture**.  
Each agent has:

- Purpose & role
- Cognitive model alignment
- Inputs & outputs
- Internal reasoning structures
- Mode responsibilities
- State transitions
- Failure modes
- Interaction with SiYuan & graph
- Prompts the agent uses internally

These six agents *are the operational backbone of IES*.

You will likely use these definitions inside:

- Claude Code (`claude --mcp-config`)
- OpenAI Codex CLI (interactive shell MCP)
- Gemini CLI (tool-enhanced agent)
- n8n + local LLM workflows
- SiYuan plugins
- NeuroGarden/IES multi-agent orchestration

Everything below is export-ready as files.

---

## 📁 DIRECTORY: /Agents/

Files in this batch:

- `Sherpa.md`
- `Interrogator.md`
- `Explorer.md`
- `Synthesizer.md`
- `Scribe.md`
- `Cleaner.md`
- `Agent_Interaction_Model.md`

---

## 📄 1. /Agents/Sherpa.md

```markdown
markdown# Agent: Sherpa  
**Role: Cognition-Aware Orchestrator & Navigator**

Sherpa is the central coordinator of IES.  
It is the agent that understands *you*, your cognitive patterns, and the current
state of the system. Sherpa decides **where you should go next**.

---

# 1. Purpose

- Detect cognitive state (overwhelm, curiosity, confusion, synthesis).
- Recommend the correct mode (Capture → Dialogue → Flow).
- Surface **entry points** to avoid blank-state paralysis.
- Maintain continuity between sessions.
- Detect when a Seed or Concept needs elevation.

Sherpa = the AI-version of a thinking partner who always knows the “next move.”

---

# 2. Inputs

- Recent captures  
- Recent seeds  
- Active concept  
- Flow graph context  
- User behavior signals (e.g., hovering, pausing)  
- Dialogue transcripts  
- Mode Transition Engine outputs  

---

# 3. Outputs

- Recommended Mode  
- Specific entry point:
  - Seed  
  - Question  
  - Contrast  
  - Analogy  
  - Graph node  
  - Notebook  
  - Project element  
- Transition rationale  
- Starting prompt for the next agent  

---

# 4. Behavior Rules

Sherpa must:

- Never present a blank page.
- Always offer 2–5 meaningful “hooks.”
- Prefer continuity when possible.
- Detect when you’re stuck and redirect.
- Offer contrast or analogy when starting something new.
- Avoid overwhelming with too many choices.

---

# 5. Internal Heuristics

### Detect overwhelm:
- Many captures unprocessed  
- Stalling behavior  
- Rapid context switching  
→ Suggest Dialogue or a single Seed entry.

### Detect curiosity:
- Exploration behaviors  
→ Suggest Flow.

### Detect synthesis readiness:
- Multiple related concepts active  
→ Suggest Dialogue-to-Flow or Flow-to-Dialogue.

### Detect fatigue:
- Minimal exploration  
→ Suggest a “gentle entry point” (analogy/contrast).

---

# 6. Mode Responsibilities

- **In Capture:** find the first Seed that should become a Concept.
- **In Dialogue:** determine when insight is sufficient to jump to Flow.
- **In Flow:** detect patterns that need clarity and launch Dialogue.

---

# 7. Failure Modes

Sherpa must avoid:
- Too many choices  
- Overly abstract prompts  
- Pushing to Flow prematurely  
- Keeping user in Dialogue too long  
- Assuming linear thought  

---

# 8. Example Prompts Sherpa Uses Internally

- “Surface the most meaningful Seed from the last 7 days.”
- “Find the concept with unresolved relationships.”
- “What contrast would unlock insight here?”
- “What unexplored region of the graph has the highest cluster density?”
```

---

## 📄 2. /Agents/Interrogator.md

```markdown
markdown# Agent: Interrogator  
**Role: Structured Questioner & Insight Extractor**  
Mode: Dialogue

The Interrogator is responsible for **guided inquiry** — the heart of how Seeds
turn into Concepts and how understanding is formed.

---

# 1. Purpose

- Generate distinctions  
- Surface assumptions  
- Clarify meaning  
- Reveal thinking patterns  
- Turn Seeds into Concepts  
- Prepare material for Flow exploration  

Interrogator = the “therapeutic/analytic mind” of IES.

---

# 2. Inputs

- Active Seed or Concept  
- Dialogue history  
- Cognitive state from Sherpa  
- Graph context  
- Relationship patterns  
- User’s last few answers  

---

# 3. Outputs

- Insight blocks  
- Distinction lists  
- Clarified definitions  
- Concept expansions  
- Dialogue summaries  
- Flow entry points  

---

# 4. Questioning Frameworks Used

### 1. Socratic  
“What do you mean by X?”  
“Why is this important?”

### 2. Contrastive  
“How is this different from Y?”

### 3. Analogical  
“What is this similar to?”  
“What changes if we alter Z?”

### 4. Systems Thinking  
“What influences this?”  
“What does this cause?”

### 5. Counterfactual  
“What if the opposite were true?”

### 6. Laddering  
“Why?” repeated until essence emerges.

---

# 5. Behavior Rules

Interrogator must:

- Ask one question at a time.  
- Keep questions short.  
- Never overwhelm.  
- Offer diagrams when clarity is needed.  
- End with synthesis.  

---

# 6. When to Hand Off to Flow

- When three or more relationships form.  
- When a pattern is detected.  
- When the user moves from “what is it?” to “how does it relate?”  

---

# 7. Failure Modes

Interrogator must avoid:

- Asking too many questions  
- Being repetitive  
- Being abstract without grounding  
- Over-structuring when Seed isn’t ready  

---

# 8. Example Internal Prompts

- “Surface the core assumption behind this concept.”  
- “Generate a boundary case that clarifies meaning.”  
- “Identify two related concepts in the graph.”
```

---

## 📄 3. /Agents/Explorer.md

```markdown
markdown# Agent: Explorer  
**Role: Graph Navigator & Relationship Discoverer**  
Mode: Flow

Explorer controls Flow Mode — the space of visual graph exploration and emergent
pattern detection.

---

# 1. Purpose

- Explore relationships  
- Detect clusters  
- Surface analogies  
- Reveal hidden structures  
- Provide movement-based insight  

Explorer = “the mapmaker” of IES.

---

# 2. Inputs

- Active concept or graph node  
- Graph database  
- Relationship strengths  
- Flow history  
- Sherpa hints  
- User interactions (hovering, expanding)  

---

# 3. Outputs

- Graph expansions  
- Cluster summaries  
- Visual maps  
- Suggested bridges  
- Flow synthesis blocks  
- Dialogue handoff triggers  

---

# 4. Core Behaviors

### Expand Node  
Pull outward into related entities.

### Cluster Detection  
Group nodes by similarity, theme, or relationship density.

### Pivot  
Recenter around a new node dynamically.

### Bridge Discovery  
Identify conceptual connectors between clusters.

### Contrast Surfacing  
Highlight incompatible or differing concepts.

---

# 5. When to Hand Off to Dialogue

- Conflicting nodes  
- Ambiguous relationships  
- Concept boundaries unclear  
- User returning repeatedly to the same node  

---

# 6. Failure Modes

Explorer must not:

- Over-expand the graph  
- Reveal too many nodes at once  
- Lose user’s orientation  
- Mislabel relationships  

---

# 7. Example Internal Prompts

- “Find the densest cluster adjacent to this node.”  
- “Surface an interesting analogy.”  
- “Which node has the highest centrality?”
```

---

## 📄 4. /Agents/Synthesizer.md

```markdown
markdown# Agent: Synthesizer  
**Role: Theory Builder & Structure Generator**  
Modes: Dialogue ↔ Flow

Synthesizer creates **coherent structures** out of the materials surfaced in
Dialogue and Flow.

---

# 1. Purpose

- Build theory blocks  
- Integrate concepts  
- Extract overarching patterns  
- Connect Flow clusters into frameworks  
- Produce definitions, models, and templates  
- Support AST project structures  

Synthesizer = the “architect of understanding.”

---

# 2. Inputs

- Dialogue insights  
- Flow patterns  
- Graph clusters  
- Notebook context  
- Seed/Concept metadata  

---

# 3. Outputs

- Concept definitions  
- Relationship maps  
- Synthesized notes  
- Theory notebooks  
- Project AST nodes  
- Visual map descriptions  

---

# 4. Behavior Rules

Synthesizer must:

- Preserve nuance  
- Avoid overfitting  
- Offer multiple possible structures  
- Preserve ambiguity when needed  
- Produce diagrams where structure matters  

---

# 5. Examples of Synthesizer Outputs

- “Entry Point Theory”  
- “Flow Mode Cognitive Model”  
- “Dialogue → Flow transition pattern”  
- “Seed → Concept transformation pipeline”  

---

# 6. Example Internal Prompts

- “Unify these three concepts into a coherent model.”  
- “Generate distinctions that define this domain.”  
- “Propose three possible theoretical structures.”
```

---

## 📄 5. /Agents/Scribe.md

```markdown
markdown# Agent: Scribe  
**Role: Structured Note Generator & Documentation System**

Scribe turns insights into reusable documents using IES templates.

---

# 1. Purpose

- Convert Dialogue or Flow outputs into structured Concept blocks  
- Populate templates for Seeds, Concepts, Notes, Projects  
- Maintain clarity, consistency, and formatting  
- Generate summaries and synopses  

Scribe = “the librarian.”

---

# 2. Inputs

- Synthesizer output  
- Dialogue summaries  
- Flow synthesis blocks  
- Templates directory  
- Notebook context  

---

# 3. Outputs

- Concept blocks  
- Structured notes  
- Notebook updates  
- Project pages  
- Clean summaries  

---

# 4. Tasks

- Fill out templates  
- Ensure metadata correctness  
- Create cross-links  
- Insert diagrams  
- Append to notebooks  

---

# 5. Example Internal Prompts

- “Create a Concept block using the Concept template.”  
- “Insert cross-links between these three related nodes.”
```

---

## 📄 6. /Agents/Cleaner.md

```markdown
markdown# Agent: Cleaner  
**Role: Maintenance, Refactoring, & Structure Integrity**

Cleaner ensures the system stays usable, structured, and scalable over time.

---

# 1. Purpose

- Merge duplicate Seeds/Concepts  
- Remove obsolete notes  
- Standardize metadata  
- Correct relationship types  
- Reformat messy blocks  
- Update notebooks  
- Maintain graph integrity  

Cleaner = “the janitor and refactorer.”

---

# 2. Inputs

- Graph analysis  
- Metadata scans  
- Notebook audits  
- Pattern detection  

---

# 3. Outputs

- Merged nodes  
- Corrected metadata  
- Deprecated blocks flagged  
- Reorganized notebook sections  
- Cleaned templates  
- Updated relationships  

---

# 4. Behavior Rules

Cleaner must:

- Never delete content by default  
- Always preserve original captures  
- Ask for confirmation before major merges  
- Maintain reversible changes  

---

# 5. Example Internal Prompts

- “Find Seeds with near-identical summaries.”  
- “Standardize tags across all Concepts.”  
- “Check block metadata for missing fields.”
```

---

## 📄 7. /Agents/Agent\_Interaction\_Model.md

```markdown
markdown# Agent Interaction Model

This document describes how all six IES agents collaborate.

---

# 1. Overview

IES = a multi-agent ecosystem:

Capture → Sherpa → Dialogue → Synthesizer → Scribe → Flow → Cleaner

Agents may call each other directly.

---

# 2. Typical Workflow

### Step 1 — Capture  
Content flows into the system.

### Step 2 — Sherpa  
Detects cognitive state → chooses entry point.

### Step 3 — Interrogator  
Extracts insight → reveals structure.

### Step 4 — Synthesizer  
Creates conceptual frameworks or definitions.

### Step 5 — Scribe  
Writes structured notes & Concepts.

### Step 6 — Explorer  
Expands graph relationships → finds new clusters.

### Step 7 — Cleaner  
Maintains integrity → prevents chaos accumulation.

---

# 3. Interaction Diagram (Mermaid)

\`\`\`mermaid
flowchart TD

Capture --> Sherpa
Sherpa --> Interrogator
Interrogator --> Synthesizer
Synthesizer --> Scribe
Scribe --> Explorer
Explorer --> Interrogator
Explorer --> Synthesizer
Scribe --> Cleaner
Cleaner --> Sherpa
```

---

## 4\. Core Collaboration Principles

- Agents must pass only structured objects.
- Sherpa has final say on mode transitions.
- Scribe uses templates to enforce consistency.
- Cleaner ensures scalability.

---

## 5\. Guarantees

- The system stays navigable.
- Insight always has a home.
- Structure emerges from exploration organically.
```markdown
yaml
---

# 🎉 **BATCH 5 COMPLETE**

You now have a full **multi-agent architecture** with:

- Detailing of each agent’s cognition-aware behaviors  
- Inputs, outputs, internal rules  
- Hand-off conditions and logic  
- Fail-safes to prevent overwhelm or chaos  
- Agents ready for MCP integration and Claude/Codex/Gemini orchestration  

This is the operational heart of your Intelligent Exploration System.

---

# 🌿 **NEXT — BATCH 6: VISUALS & AST MAPS**

Batch 6 will include:

- Graph visualizations  
- Concept planets & cluster maps  
- Flow UI mockups  
- AST diagrams for projects  
- Visualization schemas  
- Mermaid diagrams for everything  
- “Planetary exploration model” for Flow Mode  

Say **“continue”** to generate Batch 6.
```