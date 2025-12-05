# Real Examples: The ADHD Ontology in Action

*Actual examples showing exactly how nodes and edges would look*

**Exported from SiYuan:** December 4, 2025
**Parent Document:** ADHD-Friendly Ontology Design

---

## Example 1: Capturing a Spark While Reading

You're reading Gabor Maté and this hits you:

> "We do not see things as they are, we see them as we are."

### What Gets Created

```mermaid
flowchart TD
    subgraph spark["SPARK NODE"]
        s1["<b>id:</b> spark_001<br/><b>type:</b> spark<br/><b>title:</b> 'We see as we are'<br/><b>content:</b> 'We do not see things as they are...'<br/><br/><b>resonance_signal:</b> surprised<br/><b>capture_context:</b> 'Reading Scattered Minds, ch.26'<br/><b>status:</b> captured<br/><b>energy_level:</b> medium<br/><b>exploration_visits:</b> 0"]
    end

    subgraph source["SOURCE"]
        src["<b>type:</b> person<br/><b>title:</b> Gabor Maté"]
    end

    subgraph problem["FAVORITE PROBLEM"]
        fp["<b>type:</b> favorite_problem<br/><b>title:</b> How do my past experiences<br/>shape what I can see now?"]
    end

    s1 -->|sparked_by| src
    s1 -->|addresses_problem| fp
```

### The Actual Data

```json
{
  "id": "spark_001",
  "type": "spark",
  "title": "We see as we are",
  "content": "We do not see things as they are, we see them as we are.",
  "resonance_signal": "surprised",
  "capture_context": "Reading Scattered Minds, ch.26 - section on implicit memory.",
  "status": "captured",
  "energy_level": "medium",
  "favorite_problems": ["fp_003"],
  "exploration_visits": 0,
  "created_at": "2024-12-04T10:30:00Z",
  "source_ref": "Scattered Minds, p.284"
}
```

---

## Example 2: A Spark Becomes an Insight

You return to that spark 3 times. Each time, you connect it to other things. Eventually you realize something:

### The Journey

```mermaid
flowchart LR
    subgraph day1["Day 1: Capture"]
        s1["Spark<br/>'We see as we are'<br/>visits: 0"]
    end

    subgraph day3["Day 3: First Return"]
        s2["Spark<br/>visits: 1"]
        c1["Concept<br/>'Implicit Memory'"]
        s2 -->|resonates_with| c1
    end

    subgraph day7["Day 7: Connection"]
        s3["Spark<br/>visits: 2"]
        c2["Concept<br/>'Narrow Window'"]
        s3 -->|resonates_with| c2
    end

    subgraph day10["Day 10: Insight Emerges"]
        s4["Spark<br/>visits: 3<br/>status: exploring"]
        i1["INSIGHT<br/>'My reactions aren't<br/>about now—they're<br/>implicit memory<br/>filtering what I see'"]
        s4 -->|led_to_discovery| i1
    end

    day1 --> day3 --> day7 --> day10
```

### The Insight Node

```json
{
  "id": "insight_007",
  "type": "insight",
  "title": "Reactions are implicit memory filtering",
  "content": "My strong reactions to criticism aren't about the present moment—they're implicit memories from childhood filtering what I can see.",
  "resonance_signal": "moved",
  "capture_context": "Journaling after therapy session. Connected the Maté quote to my own reactivity pattern.",
  "status": "exploring",
  "energy_level": "high",
  "favorite_problems": ["fp_003", "fp_001"],
  "exploration_visits": 0,
  "created_at": "2024-12-10T19:45:00Z"
}
```

---

## Example 3: Personal Growth Framework Concepts

From your Phase 1 work, here's how the 11 concepts would look:

```mermaid
flowchart TD
    subgraph core["CORE FRAMEWORK"]
        nw["Narrow Window<br/><i>Universal constraint -> meaning</i><br/>status: anchored"]
    end

    subgraph process["PROCESS"]
        avr["Acceptance vs Resignation<br/><i>Aliveness, not form</i>"]
        met["Metabolization<br/><i>Pain -> capacity</i>"]
        shame["Shame as Non-Acceptance<br/><i>Blocker to metabolization</i>"]
    end

    subgraph mechanism["MECHANISM"]
        ns["Nervous System Configs<br/><i>3 states</i>"]
        gate["NS as Gatekeeper<br/><i>Capacity when accessed</i>"]
    end

    subgraph outcome["OUTCOME"]
        pres["Authentic Presence<br/><i>Result of shame work</i>"]
        super["Superpower in Weakness<br/><i>Trauma -> strength</i>"]
    end

    nw -->|enables| avr
    avr -->|requires| met
    shame -->|inhibits| met
    met -->|requires| ns
    ns -->|implements| gate
    met -->|produces| pres
    pres -->|enables| super
```

---

## Example 4: Favorite Problems as Navigation Anchors

```mermaid
flowchart TD
    subgraph problems["YOUR FAVORITE PROBLEMS"]
        fp1["<b>FP1:</b> How do I leverage<br/>my unique brain?"]
        fp2["<b>FP2:</b> What makes constraint<br/>generative vs limiting?"]
        fp3["<b>FP3:</b> How do past experiences<br/>shape what I can see?"]
    end

    subgraph connected["Connected Knowledge"]
        s1["Spark: Maté quote"]
        s2["Spark: Barkley on EF"]
        c1["Narrow Window"]
        c2["Interest-based NS"]
        i1["Insight: Reactions = memory"]
        t1["Thread: ADHD as difference"]
    end

    s1 -->|addresses| fp3
    s2 -->|addresses| fp1
    c1 -->|addresses| fp2
    c2 -->|addresses| fp1
    i1 -->|addresses| fp3
    i1 -->|addresses| fp1
    t1 -->|addresses| fp1

    style fp1 fill:#ff6b6b
    style fp2 fill:#4ecdc4
    style fp3 fill:#ffe66d
```

### Navigation: "Show me everything about FP1"

Query: `MATCH (n)-[:addresses_problem]->(fp {id: "fp1"}) RETURN n`

Returns:
- Spark: Barkley on EF
- Concept: Interest-based nervous system
- Insight: Reactions = memory
- Thread: ADHD as difference

**Every path leads somewhere.** No dead ends.

---

## Example 5: A Thread (Exploration Journey)

```mermaid
flowchart LR
    subgraph thread["THREAD: Understanding My Reactivity"]
        direction TB
        t["<b>thread_004</b><br/>status: exploring<br/>visits: 5"]
    end

    subgraph journey["The Journey"]
        direction LR
        step1["1. Sparked by<br/>therapy session"]
        step2["2. Read Maté<br/>on implicit memory"]
        step3["3. Connected to<br/>Narrow Window"]
        step4["4. Insight about<br/>my reactions"]
        step5["5. Applied in<br/>conversation"]

        step1 --> step2 --> step3 --> step4 --> step5
    end
```

### Thread Node

```json
{
  "id": "thread_004",
  "type": "thread",
  "title": "Understanding My Reactivity",
  "content": "A journey from noticing my strong reactions to criticism, through Maté's implicit memory work, to realizing my reactions are survival echoes.",
  "status": "exploring",
  "breadcrumbs": [
    {"node_id": "spark_therapy_001", "note": "Noticed pattern"},
    {"node_id": "spark_001", "note": "Maté resonated"},
    {"node_id": "concept_implicit_memory", "note": "This explains it"},
    {"node_id": "concept_narrow_window", "note": "Connected!"},
    {"node_id": "insight_007", "note": "Aha moment"}
  ],
  "exploration_visits": 5,
  "last_visited": "2024-12-10T19:50:00Z"
}
```

---

## Navigation Scenarios

### "I have low energy, show me something familiar"

Query: `energy_level = low AND exploration_visits > 3`

### "What sparked my thinking about shame?"

Query: `MATCH path = (n)-[:sparked_by|led_to*]->(shame_concept) RETURN path`

### "Continue where I left off"

Query: `ORDER BY last_visited DESC LIMIT 5`

### "Surprise me with something I haven't seen"

Query: `exploration_visits = 0 AND resonance_signal IN ['curious', 'surprised']`

---

This is what your knowledge graph would actually look like—a living map of your thinking, with multiple paths in and no dead ends.

---

*Source: SiYuan note "ADHD-Friendly Ontology Design/Real Examples"*
