---
title: "IES AST SiYuan structure"
source: "https://chatgpt.com/c/69327091-fe40-8326-a6d7-124073d2e073"
author:
  - "[[ChatGPT]]"
published:
created: 2025-12-05
description: "ChatGPT is your AI chatbot for everyday use. Chat with the most advanced AI to explore ideas, solve problems, and learn faster."
tags:
  - "clippings"
---
Create an ideal IES AST driven SiYuan structure for developing projexts tailored to me

---

Cool, let’s just *decide* on a structure and you can tweak from there instead of endlessly iterating in your head.

Below is an **IES + AST–driven SiYuan structure** specifically tuned for:

- ADHD brain (low-friction entry, high-structure *after* capture)
- Your IES modes (Survey / Inquiry / Flow / Synthesis)
- Building / evolving projects like NeuroGarden, homelab stuff, therapy frameworks, etc.

---

## 1\. Top-level SiYuan layout

Use **one main notebook** for this:

**Notebook:**`🧭 IES – Projects`

Inside:

1. `00 – System`
	- `IES – Node Types & AST`
	- `IES – Modes & Prompts`
	- `Templates – Project`
	- `Templates – Session`
	- `Templates – Seed`
2. `10 – Seeds & Sparks`
	- `Inbox – Project Seeds`
	- Optional: `Inbox – Random Ideas`
3. `20 – Active Projects`
	- `Life – Family & Home`
	- `Biz – Practice & Money`
	- `Mind – Therapy Frameworks`
	- `Tech – Homelab & Automation`
	- `Meta – NeuroGarden / IES`
4. `30 – Knowledge & Concepts`
	- `Concepts – ADHD & EF`
	- `Concepts – Therapy Maps`
	- `Concepts – Automation & AI`
	- `Patterns – Project Patterns`
5. `90 – Archive`
	- `Archive – Completed Projects`
	- `Archive – Dropped / Parked`

This keeps:

- **Capture** = `10 – Seeds`
- **Doing / Building** = `20 – Active Projects`
- **Re-usable understanding** = `30 – Knowledge`

---

## 2\. Core AST: how a project is structured

Each **project is one main document** (with children docs as needed).  
Think of this as the **AST root**: everything else is typed sub-nodes.

**Project doc title pattern:**

`[PJT] <short-name> – <one-line purpose>`

Example:  
`[PJT] NeuroGarden – Executive Function Assistant`

### AST for a project (node types)

I’ll show it as a tree, and then how to encode it in SiYuan.

For your brain, **only a few sections are mandatory up front**:

1. Meta
2. Spark & Story (why you care)
3. First Tiny Step

Everything else can grow as you go.

---

## 3\. Node types & tags (AST in SiYuan)

Use **tags / attributes** to give each block a “type” and “mode”.

### Recommended types

Use tags like `#type/<X>`:

- `#type/project`
- `#type/goal`
- `#type/outcome`
- `#type/constraint`
- `#type/resource`
- `#type/hypothesis`
- `#type/question`
- `#type/insight`
- `#type/decision`
- `#type/task`
- `#type/experiment`
- `#type/evidence`
- `#type/session`
- `#type/retrospective`
- `#type/seed` (for anything pulled from Seeds)

### IES mode tags

These let you see *how* a block was produced:

- `#mode/survey` – scanning, listing, braindump, inventory
- `#mode/inquiry` – structured Q&A, probing, CBT-style “why / what else?”
- `#mode/flow` – exploring connections, mapping concepts, graph-style
- `#mode/synthesis` – summarizing, deciding, “what does this mean, so what, now what?”

So a single block might look like:

> “If NeuroGarden worked perfectly, what would feel different in my Mondays?”  
> `#type/question #mode/inquiry`

---

## 4\. Concrete project template (drop-in)

Create this as:  
`Templates – Project`

Then use “Insert Template” whenever you start a new project.

```markdown
markdown# [PJT] {{Project Name}} – {{One-line purpose}}  #type/project

## 0. Meta
- **Status:** 🟢 Active / 🟡 Incubating / 🔴 On Hold
- **Domain:** {{Life / Biz / Mind / Tech / Meta}}
- **Created:** {{YYYY-MM-DD}}
- **Last Touched:** {{YYYY-MM-DD}}
- **Energy Fit Today:** {{💡 Thinky / 🛠 Build / 😴 Low-effort-only}}
- **Emotional Why (1–2 sentences):**  #type/insight #mode/synthesis

---

## 1. Spark & Story  #type/seed #mode/survey
- **Original spark / itch:**  
- **What made this feel important enough to write down?**  
- **What future “me” am I secretly trying to help?**

> Optional: paste in anything from \`Seeds & Sparks\` and tag it \`#linked-seed\`.

---

## 2. Problem Space  #mode/inquiry
### 2.1 What’s wrong / missing / confusing?  #type/problem
- Bullets of symptoms, frictions, questions.

### 2.2 Who/what is affected?  #type/stakeholder
- Me / Partner / Kids / Clients / Future-vs-Present self…

### 2.3 Hidden beliefs & assumptions  #type/assumption
- “I probably can’t ____ because ____.”
- “For this to ‘count’ it has to ____.”

---

## 3. Outcomes & Success  #mode/synthesis
### 3.1 North Star Outcome  #type/goal
- If this project quietly “worked,” life would look like:

### 3.2 Success Criteria  #type/outcome
- **Feel**: How will I feel/think differently?
- **Function**: What concrete things will be easier or automated?
- **Signals**: What would others notice?

### 3.3 Anti-goals / guardrails  #type/constraint
- “This project is *not* allowed to turn into…”
- “I am explicitly avoiding…”

---

## 4. Constraints & Resources  #mode/survey
### 4.1 Constraints  #type/constraint
- Time, money, tech, energy, executive function limits.

### 4.2 Resources  #type/resource
- Tools, existing systems (NeuroGarden, n8n, Homelab, etc.)
- Skills I already have.
- People I could ask.

---

## 5. Hypotheses & Approaches  #mode/flow
### 5.1 Main Hypotheses  #type/hypothesis
- H1:  
- H2:

### 5.2 Possible Approaches (branches)  #type/hypothesis
- A1 – “Quick-and-dirty MVP”
- A2 – “Nice architecture from day one”
- A3 – “Outsource / template”

> Link each approach to relevant concept notes in \`30 – Knowledge & Concepts\`.

---

## 6. Workstreams  #mode/synthesis
Each workstream is a **subtree** you can collapse.

### 6.1 Workstream 1 – {{Name}}  #type/workstream
- **Objective:**  #type/goal
- **Why this first (for ADHD brain):**  

#### 6.1.1 Milestones  #type/outcome
- M1 –
- M2 –

#### 6.1.2 Tasks  #type/task
- [ ] Copy tasks to Todoist and link back here  
- [ ] First tiny step that can be done in < 15 min

#### 6.1.3 Experiments  #type/experiment
- E1 – What I’m testing:
- Prediction:
- How I’ll know if it “worked”:

---

## 7. Knowledge & Research  #mode/flow
- Links to:
  - Obsidian notes
  - GitHub repos
  - Papers / books
  - Your ADHD / therapy frameworks

Use child docs if this section gets big:
- \`[PJT] {{Name}} – Research – Automation\`
- \`[PJT] {{Name}} – Research – Therapy\`

---

## 8. Decisions Log  #type/decision #mode/synthesis
Log as short, timestamped bullets:

- **2025-12-05** – Decided to start with “manual but structured” instead of full automation. Reason: need to feel it in my body first.
- **2025-12-10** – Dropped Approach A2, felt overwhelming.

---

## 9. Narrative Notes (IES Sessions)  #type/session
Link out to separate **session docs** (see Session Template below) or keep inline.

- **2025-12-05 – Session 01 (Inquiry)**  
  Key insight: …  
- **2025-12-07 – Session 02 (Flow)**  
  Mapped how this interacts with family / kids / time.

---

## 10. Retrospective  #type/retrospective #mode/synthesis
Fill this when you “close” a phase or whole project:

- What actually changed?
- What surprised me?
- What part of the AST felt most helpful / natural?
- What would Future Me want to know before starting something similar?
```

---

## 5\. Seed & Session templates (IES-powered)

### Seed template (for 10 – Seeds & Sparks)

### Session template (for focused IES runs)

Use child docs under a project, e.g.  
`[PJT] NeuroGarden – S01 – Inquiry – 2025-12-05`

```markdown
markdown# [SESSION] {{Project}} – S{{NN}} – {{Mode}} – {{Date}}  #type/session

- **IES Mode:** #mode/survey / #mode/inquiry / #mode/flow / #mode/synthesis
- **Energy level coming in:** 1–5
- **Time box:** {{30–60 min}}

## 1. Focus Question
What am I trying to understand / decide / design right now?

## 2. Question-Answer Chain  #mode/inquiry
Q1:  
A1:  

Q2:  
A2:  

(Let the AI / IES guide with follow-ups. Each Q is \`#type/question\`, each A → potential \`#type/insight\`.)

## 3. Emergent Insights  #type/insight #mode/synthesis
- Insight 1:
- Insight 2:

## 4. Concrete Updates to Project AST
- [ ] Update **Problem Space** with…
- [ ] Update **Workstreams** with…
- [ ] Add **Decisions Log** entry:
  - 2025-12-05 – …

## 5. Next Tiny Step  #type/task
- “When I leave this session, the next 10–15 min move is: ___”
```

---

## 6\. How this is “AST-driven” in practice

In SiYuan terms:

- **Headings = AST levels**  
	H1 = project, H2 = major sections, H3/H4 = node types (tasks, hypotheses, etc).
- **Tags = node types + modes**  
	This lets you:
	- Search: `#type/decision AND #mode/synthesis`
	- Filter all `#type/question` across projects to feed IES Inquiry.
- **Child docs = reusable subtrees**  
	For big projects: each workstream or research theme can be its own doc with the same AST pattern.

---

## 7\. If you want a super-minimal version to actually start today

When you open SiYuan to start a new project, only fill:

1. `Spark & Story`
2. `North Star Outcome`
3. `First Tiny Step task` (and push to Todoist)

Everything else is allowed to grow later, via session docs.

---

If you’d like, next step I can:

- Take **one real project** (e.g. “NeuroGarden – Exec Function Assistant”)
- Fill in this template with you, so you have a concrete, lived example instead of a generic skeleton.

---

Make sure to include ways of visualizing aspects of projects as often as possible

---

Absolutely — for **your brain**, *visualization isn’t optional,* it’s a **core cognitive scaffold**.  
So here is the **revised, visualization-heavy IES + AST-driven SiYuan project system**, where nearly every major section includes an explicit *visual layer* you can generate manually *or* automatically using your IES agent.

This is the first version optimized for **constant visual anchors**: maps, graphs, flows, tables, progress bars, timelines, block diagrams, and conceptual metaphors.

---

## 🌐 IDEAL VISUAL-FIRST IES + AST PROJECT SYSTEM (FOR SIYUAN)

Below is the **improved structure**, annotated with where and how visualization should happen.

---

## 0 — System Foundations (Visual Mode Enabled)

This folder stays the same **plus**:

### IES – Visual Methods

A lookup sheet of visualization options you can invoke from anywhere:

- **Graphs:** mind map, concept map, dependency graph
- **Flows:** process diagram, pipeline map
- **Structures:** AST tree, hierarchical outline
- **Timelines:** roadmap, milestone chart
- **Matrices:** 2x2 comparisons, decision matrix
- **Embodied visuals:** “energy map,” “friction heat map,” “attention budget diagram”
- **Narrative visuals:** storyboards, user journeys, interaction loops
- **System visuals:** architecture diagram, data flow, component map

---

## 1 — Seeds & Sparks (Visualization = Shape the Idea)

Template updated:

### Visualization prompts added:

After the raw thought dump, include:

**“Visual Snapshots” section**

- What shape is this idea? (circle, tree, knot, constellation, machine, ecosystem…)
- Quick sketch (ASCII or hand-drawn upload)
- Concept map auto-generated by IES
- 2x2 “Value vs Effort” placement

This gives your brain **visual traction** on ideas before they solidify.

---

## 2 — Project Template (Updated With Visualization Blocks Everywhere)

Below is the **fully upgraded template**, with mandatory visual sections.

---

## PROJECT TEMPLATE (VISUAL-FIRST, IES–AST)

```markdown
markdown# [PJT] {{Project Name}} – {{Purpose}}  #type/project

## 0. Meta
- **Status:** 🟢 / 🟡 / 🔴  
- **Domain:** {{Life/Biz/Mind/Tech/Meta}}  
- **Visual Index:**  
  - 📍 Concept Map  
  - 🕸 Dependency Graph  
  - 🔄 Workflow Diagram  
  - 📅 Timeline  
  - 🔥 Friction Heat Map  
  - ⚡️ Energy Map  

---
## 1. Spark & Story  #type/seed #mode/survey

### 1.1 Origin Spark
Raw bullets…

### 1.2 Emotional Snapshot  
What does this FEEL like visually? (storm, lighthouse, tangled headphones…)

### 1.3 Visualizations (pick 1–3)
- ✨ **Concept map** of initial idea  
- 🧠 **Mental model sketch** (IES can auto-generate)  
- 📈 **Value vs. Complexity 2x2**  
- 🔮 **“Future State Image”** — one screenshot from the ideal outcome

---

## 2. Problem Space  #mode/inquiry

### 2.1 Frictions & Symptoms
Bullets…

### 2.2 Visualizations
- 🔥 **Friction Heat Map**  
  (Red = constant pain, yellow = noticeable but tolerable, green = fine)  
- 🧩 **Problem Topology Map**  
  Show how problems cluster (executive function, emotional friction, technical bottlenecks).

### 2.3 Assumptions
List…

### Visualization
- 🪞 **Assumption Web**  
  (Visually shows which beliefs constrain which choices.)

---

## 3. Outcomes & Success  #mode/synthesis

### 3.1 North Star Outcome  
Paragraph…

### Visualization
- ⭐️ **North Star Diagram**  
  - Core outcome in center  
  - Surrounding “rings” of supporting changes  
- 🎯 **Definition-of-Done Radar Chart**  
  Axes: Feeling, Function, Reliability, Automation, Simplicity, Joy.

### 3.2 Success Criteria  
List…

### 3.3 Anti-goals  
List…

---

## 4. Constraints & Resources  #mode/survey

### Constraints
List…

### Resources
List…

### Visualization
- ⚖️ **Constraint/Resource Balance Table**  
- 🧱 **Barrier Map** (like obstacles on a path)  
- 🌿 **Resource Garden Map** (everything available laid out as “plants” with roles)

---

## 5. Hypotheses & Approaches  #mode/flow

### Hypotheses  
List…

### Approaches  
List…

### Visualization
- 🔀 **Branching Decision Tree**  
- 🔬 **Hypothesis Validation Table**  
- ✨ **Scenario Storyboards** for each possible approach

---

## 6. Workstreams  #mode/synthesis

### For each workstream:

#### 6.x Workstream – {{Name}}  #type/workstream
- Objective  
- Why this matters now  

##### Visualization
- 🔄 **Workstream Flow Diagram**  
- 📅 **Mini Roadmap**  
- 📊 **Progress Bar** or “stacked phase” visual  
- 🕸 **Dependency Graph** of tasks

##### Milestones
List…

##### Tasks
List…

##### Experiments
List…

---

## 7. Knowledge & Research  #mode/flow

### Visualization Options
- 🧠 **Knowledge Constellation Map**  
  (Links between concepts you already have)  
- 📚 **Source Dashboard**  
  Table view with: Source → Insight → Relevance → Node in AST  
- 🧬 **Concept Integration Diagram**  
  (Shows how this project fits into your broader thinking frameworks)

---

## 8. Decisions Log  #mode/synthesis

### Visualization
- 🗺️ **Decision Timeline**  
- ♟ **Decision Impact Map**  
  (Highlights which decisions shaped later constraints or successes.)

---

## 9. IES Sessions (Narrative Notes)  #type/session

### Visualization included inside each session:
- 🗂 **Question Flow Tree**  
- 💡 **Insight Clusters**  
- 🔁 **Before/After mental state diagram**

Session template updated further below.

---

## 10. Retrospective  #type/retrospective

### Visualization
- 🎥 **Story of the Project (Storyboard)**  
- 📈 **Outcome Radar (Before vs After)**  
- 🔗 **Causal Map: Why this project worked or didn’t**
```

---

## 3 — Updated Session Template (Visualized Thinking)

```markdown
markdown# [SESSION] {{Project}} – S{{NN}} – {{Mode}} – {{Date}}

## 1. Focus Question
(What we’re trying to answer)

## 2. Q→A Chain  #mode/inquiry
IES-guided.

### Visualization
- Create a **Socratic Tree**:  
  Q1 → Q1a → Q1b → A1 etc.

## 3. Emergent Insights  #mode/synthesis
List…

### Visualization
- Cluster insights into **three conceptual buckets**.
- Show **strength & certainty meter** for each.

## 4. AST Updates  
List specific nodes to update…

### Visualization
- “Before/After” AST diff
- Highlight where the new insight inserts into the tree

## 5. Next Tiny Step  
A single task…

### Visualization
- Represent next step as a **spotlight on a path**.
```

---

## 4 — Dedicated Visualization Shortcuts (Super Useful for ADHD)

Inside your “System” folder add:

### IES – Visualization Shortcuts

Each block is a button-like command (or snippet) you can paste inside a project:

- `/mindmap` → Convert bullets into a mind map
- `/constellation` → Convert linked notes into “stars”
- `/timeline` → Generate a timeline from milestones
- `/flow` → Generate a block diagram of chosen workstream
- `/heatmap` → Convert friction list into heat map
- `/garden` → Resource garden diagram
- `/radar` → Create radar chart for outcomes

These can be implemented using SiYuan plugins or by having your IES agent generate diagrams as Mermaid, Graphviz, or ASCII.

---

## 5 — If you want a visual dashboard for each project

Add at the top of each project:

This becomes the **control panel** for your ADHD brain.

---

## 6 — Optional: Visual Metaphor Layer

This is *especially* good for grounding your thinking.

Each project has a **metaphor**:

- Garden
- Machine
- Journey
- Ecosystem
- Story
- Constellation
- City
- River
- Operating system

Then you map project elements to metaphor elements visually:

Example (Garden):

- Workstreams = “beds”
- Tasks = “seeds”
- Dependencies = “roots”
- Resources = “sunlight/water/nutrients”
- Constraints = “weeds/shade”

This works *shockingly well* for memory, emotional resonance, and motivation.

---

## 7 — If you want, I can now generate:

🌱 A **full downloadable template ZIP**  
🗺 A **visual guidebook PDF** explaining each visualization  
📐 A **Mermaid-based diagram library**  
🧠 A **SiYuan plugin spec** for automatic visualization generation  
🎨 Or a **theme** optimized for your visual workflow (project dashboards, color-coded AST, custom icons)

Just tell me which you want next.