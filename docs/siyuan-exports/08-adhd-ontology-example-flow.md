# Example: How a Spark Becomes Knowledge

> A practical walkthrough of the ADHD-friendly ontology in action

**Exported from SiYuan:** December 4, 2025
**Parent Document:** ADHD-Friendly Ontology Design

---

## The Scenario

You're reading about ADHD and come across this quote:

> "ADHD is not a problem of knowing what to do; it is a problem of doing what you know." — Russell Barkley

Something about this **resonates**. You don't know exactly why yet, but it matters.

---

## Step 1: Capture the Spark

```mermaid
flowchart LR
    quote["Quote in book"] --> capture{"Resonates!"}
    capture --> spark["SPARK<br/><br/>resonance: surprised<br/>context: Reading Barkley<br/>status: captured"]
```

**What gets saved:**

|Field|Value|
|-----|-----|
|type|`spark`|
|content|"ADHD is not a problem of knowing..."|
|resonance_signal|`surprised`|
|capture_context|"Reading Executive Functions, ch.3"|
|status|`captured`|
|favorite_problems|`["How do I leverage my unique brain?"]`|

**Key:** No classification required. Just save it.

---

## Step 2: Return and Explore

Later, you return to this spark. Maybe through:

- Your favorite problem ("How do I leverage my unique brain?")
- Recent captures
- Searching for "ADHD"
- Serendipitous discovery

```mermaid
flowchart TB
    spark["Spark"] --> explore["Exploring"]

    explore --> connect1["Connect to: Executive Function"]
    explore --> connect2["Connect to: Implementation Gap"]
    explore --> connect3["Discover: Rosier's work"]

    connect3 --> new_spark["New Spark<br/>Interest-based motivation"]

    spark -.->|sparked_by| original["Barkley book"]
    new_spark -.->|led_to_discovery| spark
```

**Status changes:** `captured` -> `exploring`
**Visits:** 1 -> 2 -> 3...

---

## Step 3: Connections Emerge

As you explore, relationships form:

```mermaid
flowchart TD
    subgraph journey["Your Learning Journey"]
        spark1["Barkley quote<br/>(the knowing-doing gap)"]
        spark2["Rosier insight<br/>(interest-based motivation)"]
        spark3["Maté on shame<br/>(implicit memory)"]
    end

    subgraph concepts["Emerging Concepts"]
        c1["Implementation Gap<br/>status: exploring"]
        c2["Interest-Based Nervous System<br/>status: anchored"]
    end

    spark1 -->|led_to_discovery| spark2
    spark2 -->|led_to_discovery| spark3

    spark1 -->|resonates_with| c1
    spark2 -->|component_of| c2
    spark3 -->|resonates_with| c1

    c1 -.->|addresses_problem| fp["How do I leverage my unique brain?"]
    c2 -.->|addresses_problem| fp
```

---

## Step 4: Crystallization (Optional)

Some explorations become anchored insights:

```mermaid
stateDiagram-v2
    direction LR

    spark: Spark
    exploring: Exploring
    insight: Insight
    anchored: Anchored

    spark --> exploring: Return to it
    exploring --> exploring: Keep exploring
    exploring --> insight: Personal realization
    insight --> anchored: Integrated into thinking

    note right of anchored
        "I now understand that my struggle
        isn't laziness—it's an interest gap.
        I need to make things interesting,
        not just important."
    end note
```

**The insight that emerged:**

> My struggle isn't laziness—it's an interest gap. Importance doesn't motivate me; interest does. I need to make things interesting, not just important.

---

## The Navigation Experience

```mermaid
flowchart TD
    subgraph entry["Entry Points (Multiple!)"]
        e1["Favorite Problem"]
        e2["Recent Activity"]
        e3["Energy Level"]
        e4["Search"]
        e5["Serendipity"]
    end

    subgraph content["Your Knowledge"]
        sparks["Sparks"]
        insights["Insights"]
        concepts["Concepts"]
        threads["Threads"]
    end

    e1 --> content
    e2 --> content
    e3 --> content
    e4 --> content
    e5 --> content

    sparks <-->|connections| insights
    insights <-->|connections| concepts
    concepts <-->|connections| threads
```

**No "right" way in.** Every path is valid.

---

## What Makes This ADHD-Friendly

|Traditional PKM|This System|
|---------------|-----------|
|"Where should I file this?"|Just capture it as a spark|
|"Is this important enough?"|Did it resonate? That's enough|
|"I never finish anything"|`exploring` is a valid permanent state|
|"I can't find anything"|Multiple entry points, no wrong way|
|"I forgot why I saved this"|`capture_context` preserves the moment|
|"I feel behind"|`exploration_visits` shows you've been here|

---

## Try It Now

1. **Capture a spark** — Something that resonated recently
2. **Tag a favorite problem** — What persistent question does it relate to?
3. **Note the resonance** — curious? surprised? moved?
4. **Save the context** — What were you doing when this struck you?

No need to organize. No need to classify. Just capture the spark. The connections will emerge as you explore.

---

*Source: SiYuan note "ADHD-Friendly Ontology Design/Example Flow"*
