# Missing Elements — Unified Project Spec

The UNIFIED PROJECT SPEC successfully resolves confusion about active codebases and worktrees.  
However, it omits several critical system definitions.

---

## 1. No Unified Operating Model

Although the architecture is described, the spec does NOT define:

- How the system behaves over time  
- How contexts propagate  
- How sessions start/end  
- How cognitive states affect mode transitions  
- The logic governing mode selection  
- The canonical “IES Loop” (Explore → Capture → Grow → Connect → Understand)

**Missing Deliverable:**  
An “Operating Manual for IES”.

---

## 2. No Narrative of the System’s Purpose

The spec describes architecture but not:

- Why IES exists  
- What cognitive problems it solves  
- How it supports ADHD workflows  
- Why Flow Mode is different from Reader Flow Mode  
- How the system supports exploration as a thinking modality

**Missing Deliverable:**  
A philosophy + intent document.

---

## 3. No Unified Definition of Flow Mode

The spec references:

- Reader FlowPanel  
- SiYuan FlowMode  
- Historical Readest Flow Mode  

But never defines:

- What Flow Mode *is*  
- Its principles  
- Its required inputs  
- Behavioral guarantees  
- How traversal works across layers  
- What a “Flow State” means for the system

**Missing Deliverable:**  
A master definition of Flow Mode.

---

## 4. No Systemwide Identity Scheme

The unified spec lacks:

- Entity IDs across layers  
- Context ID propagation rules  
- Journey ID ingestion and versioning  
- Session ID reuse across apps  
- Graph IDs vs SiYuan IDs mapping  
- Source location canonicalization for Calibre/Reader

**Missing Deliverable:**  
A consistent multi-layer identifier scheme.

---

## 5. No Definition of the Knowledge Gradient

Missing explanation of how knowledge matures:

- Raw text → Highlight  
- Highlight → Capture block  
- Capture → Spark  
- Spark → Insight  
- Insight → Concept  
- Concept → Knowledge Graph entity  
- Knowledge Graph → Synthesis

**Missing Deliverable:**  
A multi-stage maturity model for knowledge.

---

## 6. No Definition of System Boundaries

The document does not specify:

- What belongs in IES and what does NOT  
- Rules for adding new integrations  
- Rules for extending the knowledge graph  
- What agents are allowed to do  
- What levels of automation are safe  
- How to prevent runaway or destructive automation

**Missing Deliverable:**  
A boundary & safety specification.

---

## 7. Missing Developer Experience Layer

The spec omits:

- Local dev workflows  
- Generator tools  
- Test harness guidelines  
- Agent development guidelines  
- Worktree rules for Claude/Codex/Gemini  
- Documentation update protocol

**Missing Deliverable:**  
A DX (Developer Experience) standard.

---

## 8. Missing “Ground Truth” Document

There is no file that:

- Defines source of truth for architecture  
- Defines schema canonicalization  
- Ensures spec drift doesn’t occur  
- Helps agents determine “what is real”  

This is critical because IES is complex and distributed.

**Missing Deliverable:**  
A single “Ground Truth” specification.

---

## Summary of Missing Areas

1. The IES Operating Model  
2. Philosophy & purpose  
3. Master Flow Mode definition  
4. Cross-layer ID scheme  
5. Knowledge maturity gradient  
6. System boundaries & safety rules  
7. Developer experience specification  
8. Ground truth specification