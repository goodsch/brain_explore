# Missing Elements — Architecture & Interactions Spec

This document outlines what the Architecture & Interactions specification fails to define, even though it provides a very complete structural overview.

---

## 1. No Definition of the Cognitive Layer

The spec describes *interfaces* and *layers* but never describes:

- How the system supports thinking  
- How “Flow,” “Context,” “Session,” or “Journey” map to cognitive operations  
- How question classes or cognitive states connect to UI/UX  
- How the 5 Thinking Modes actually relate to exploration

**Missing Deliverable:**  
A cognitive architecture tying user intention → mode → UI → data flow.

---

## 2. No Entity Lifecycle Model

The document lists entity types and API endpoints but does **not** specify:

- How a highlight becomes a Spark  
- How a Spark becomes an Insight  
- How an Insight becomes a Concept  
- How a Concept becomes a Graph entity  
- How these transitions appear across Reader, Plugin, Backend, and SiYuan

**Missing Deliverable:**  
A canonical entity lifecycle diagram & rules.

---

## 3. No Capture Pipeline

Although the UI shows NotesSheet and QuickCapture, the spec does NOT define:

- How captures flow to SiYuan  
- What metadata all captures must include  
- How Reader → Plugin → Backend sync works  
- Error handling, conflict resolution, offline behavior

**Missing Deliverable:**  
A defined “Capture → Process → Store” pipeline.

---

## 4. No Unified Context System

The spec shows Context APIs and some UI usage but does NOT explain:

- How a Context is created during real usage  
- How a Context interacts with FlowMode or Reading Mode  
- How multiple apps share Context identity  
- How Context boundaries affect available questions or extraction

**Missing Deliverable:**  
A cross-application Context model.

---

## 5. No Interaction Semantics

The spec shows interaction *flows* but not the *meaning* of interactions:

- What does clicking a facet *mean*?  
- What is the semantic difference between evidence, relationships, facets?  
- When does the system create new graph entities vs reuse existing ones?  
- When does navigation create a Journey step?

**Missing Deliverable:**  
Interaction semantics = rules that define meaning, not visuals.

---

## 6. No Agent Integration Layer

ARCHITECTURE-AND-INTERACTIONS.md does NOT define:

- Intake, Synthesis, or Processing agents  
- Message queues  
- Automatic enrichment  
- Job lifecycle  
- Agent → API execution contract  
- What actions an agent is allowed to perform on user data

**Missing Deliverable:**  
A complete agent orchestration layer.

---

## 7. No Versioning or Invalidation Model

Missing definitions:

- How cached facets get refreshed  
- How outdated evidence is replaced  
- How schema changes are detected  
- How you avoid graph drift across updates

**Missing Deliverable:**  
A versioning protocol.

---

## 8. Missing Error States & Recovery

The spec does not describe:

- What happens when extraction fails  
- What happens when a facet returns no entities  
- How the system handles empty evidence or contradictory evidence  
- How UI conveys uncertainty or incomplete knowledge

**Missing Deliverable:**  
A UX error model.

---

## 9. No Cross-Layer Synchronization Specification

Missing:

- A unified timestamp or ID system  
- Deterministic mapping for Reader ↔ Plugin ↔ Backend  
- Sync rules for conflicts and merges  
- How journeys unify across layers

**Missing Deliverable:**  
A cross-layer sync protocol.

---

## Summary of Missing Areas

1. Cognitive architecture  
2. Entity lifecycle  
3. Capture→Process pipeline  
4. Context semantics  
5. Interaction semantics  
6. Agent orchestration  
7. Versioning/invalidation  
8. Error & uncertainty model  
9. Cross-layer synchronization