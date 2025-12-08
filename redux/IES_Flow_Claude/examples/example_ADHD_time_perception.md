# Example: ADHD Time Perception

This example illustrates how the entities, graphs, Flow Mode, and pipeline
would work together for the Feynman Problem:

> "Why does ADHD distort the perception of time?"

## 1. Feynman Problem

- `title`: "ADHD Time Perception"
- `description`: Understand why time feels different with ADHD, including
  time blindness, temporal discounting, and difficulty estimating durations.
- `importance`: 5
- `root_question_ids`: [Q1, Q2, Q3, ...]
- `seed_concept_ids`: [C_ADHD, C_Time_Perception, C_Temporal_Discounting, ...]

## 2. Root Questions (Question Graph)

Example questions:

- Q1: "What is 'time blindness' in ADHD?"
- Q2: "Which brain systems are involved in time estimation?"
- Q3: "How does dopamine influence time perception and reward?"
- Q4: "What is temporal discounting and how is it different in ADHD?"

Relationships:

- Q1 requires Q2 and Q3.
- Q4 depends_on_concept C_Temporal_Discounting and C_ADHD.

## 3. Concepts (Knowledge Graph)

- C_ADHD: Concept "ADHD"
- C_Time_Perception: Concept "time perception"
- C_Temporal_Discounting: Concept "temporal discounting"
- C_Dopamine: Concept "dopamine"

Edges (examples):

- C_Time_Perception related_to C_ADHD
- C_Temporal_Discounting related_to C_Time_Perception
- C_Dopamine influences C_Time_Perception

## 4. Flow Mode Interaction

When the "ADHD Time Perception" note is opened:

1. Focus entity = FeynmanProblem FP_ADHD_Time_Perception.
2. Flow Mode generates/loads first-level components:
   - "Time blindness"
   - "Temporal discounting"
   - "Prospective vs retrospective timing"
   - "Dopamine & reward circuitry"
3. Sidebar shows a mini graph with ADHD Time Perception at the center and
   these sub-entities around it.
4. The user clicks "Temporal discounting":
   - Focus entity changes to that Concept.
   - Flow Mode fetches relevant chunks via the word index.
   - Layer 3 runs contextual extraction to pull out definitions, mechanisms,
     and ADHD-related differences.
   - A structured summary is inserted into the note and the Knowledge Graph
     is updated.

## 5. Pipeline Involvement

- Layer 0: Barkley, Hallowell, and other ADHD books are ingested with metadata.
- Layer 1: They are chunked, summarized, and indexed; basic ADHD/time entities
  are extracted.
- Layer 2: Priority given to chunks mentioning time, time perception,
  discounting, reward; relational extraction builds claims and relations.
- Layer 3: When the user focuses on ADHD Time Perception in Flow, targeted
  extraction sharpens the definitions and evidence specifically for this area.

This shows how the whole system behaves around a single rich Feynman Problem.
