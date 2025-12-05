# brain_explore System Design Visual

*Visual diagrams of the complete system architecture*

**Exported from SiYuan:** December 4, 2025

---

## Four-Layer Architecture

```mermaid
flowchart TB
    subgraph L4["Layer 4: READEST - Reading Interface"]
        R1[Linear Reading]
        R2[Flow Mode]
        R3[Entity Panel]
        R4[Breadcrumb Capture]
        R1 -->|toggle| R2
        R2 --> R3
        R2 --> R4
    end

    subgraph L3["Layer 3: SIYUAN - Processing Hub"]
        S1[Dashboard]
        S2[Structured Thinking]
        S3[Flow Exploration]
        S4[Quick Capture]
        S1 --> S2
        S1 --> S3
        S1 --> S4
    end

    subgraph L2["Layer 2: BACKEND - API Services"]
        B1[Graph API]
        B2[Session API]
        B3[Journey API]
        B4[Capture API]
        B5[Question Engine]
        B6[Profile Service]
    end

    subgraph L1["Layer 1: KNOWLEDGE GRAPH"]
        G1[(Neo4j<br/>50k entities)]
        G2[(Qdrant<br/>Vectors)]
        G3[(Personal Graph<br/>ADHD Ontology)]
    end

    L4 -->|REST API| L2
    L3 -->|REST API| L2
    L2 --> L1
```

---

## Data Flow: Reading to Insight

```mermaid
flowchart LR
    subgraph User["User Actions"]
        A1[Read book]
        A2[Highlight passage]
        A3[Explore concept]
        A4[Answer questions]
        A5[Articulate insight]
    end

    subgraph System["System Processing"]
        S1[Entity extraction]
        S2[Graph lookup]
        S3[Relationship retrieval]
        S4[Question generation]
        S5[Journey capture]
    end

    subgraph Storage["Knowledge Storage"]
        D1[(Domain Graph)]
        D2[(Personal Graph)]
        D3[(User Profile)]
    end

    A1 --> A2 --> S1
    S1 --> S2 --> D1
    S2 --> S3 --> A3
    A3 --> S4
    D3 --> S4
    S4 --> A4 --> A5
    A5 --> D2
    A3 --> S5 --> D2
```

---

## Entity Types

```mermaid
flowchart TB
    subgraph Domain["Domain Knowledge (from books)"]
        C[concept]
        F[framework]
        T[theory]
        M[mechanism]
        PH[phenomenon]
        PA[pattern]
        D[distinction]
        PE[person]
    end

    subgraph Personal["Personal Knowledge (ADHD-friendly)"]
        SP[spark]
        IN[insight]
        TH[thread]
        FP[favorite_problem]
    end

    SP -->|"promoted to"| IN
    SP -->|"sparked_by"| Domain
    IN -->|"addresses"| FP
    TH -->|"contains"| SP
    TH -->|"contains"| IN
```

---

## Spark Lifecycle

```mermaid
stateDiagram-v2
    [*] --> captured: Quick capture
    captured --> exploring: Start working with it
    exploring --> anchored: Fully integrated
    exploring --> captured: Set aside
    anchored --> exploring: Revisit

    note right of captured
        Just captured, not processed
        Has: resonance_signal, capture_context
    end note

    note right of exploring
        Actively developing
        Has: exploration_visits, last_visited
    end note

    note right of anchored
        Part of understanding
        Connected to other concepts
    end note
```

---

## User Workflows

### Reading Flow

```mermaid
sequenceDiagram
    participant U as User
    participant R as Readest
    participant B as Backend
    participant G as Graph

    U->>R: Open book
    U->>R: Highlight passage
    U->>R: Toggle Flow mode
    R->>B: Extract entities from highlight
    B->>G: Query relationships
    G-->>B: Related concepts, sources
    B-->>R: Entity panel data
    R-->>U: Show connections + questions
    U->>R: Click related concept
    R->>B: Save breadcrumb
    B->>G: Store journey step
```

### Quick Capture Flow

```mermaid
sequenceDiagram
    participant U as User
    participant S as SiYuan
    participant B as Backend
    participant G as Graph

    U->>S: Dump thought
    S->>B: POST /capture/process
    B->>B: Extract entities
    B->>G: Find related concepts
    G-->>B: Matches
    B-->>S: Suggested placements
    S-->>U: Show options
    U->>S: Confirm placement
    S->>B: Create spark
    B->>G: Store in personal graph
```

---

## Integration Status

```mermaid
flowchart TB
    subgraph Connected["Connected"]
        C1[Readest to Graph API]
        C2[SiYuan to Backend APIs]
        C3[Backend to Neo4j]
        C4[Backend to Qdrant]
    end

    subgraph Partial["Partial"]
        P1[Journey capture]
        P2[Question engine]
        P3[Profile usage]
    end

    subgraph Missing["Not Connected"]
        M1[Personal Graph to UI]
        M2[Quick Capture destination]
        M3[Readest to SiYuan sync]
        M4[Book library browser]
        M5[SiYuan note structure]
    end

    Connected --> Partial
    Partial --> Missing
```

---

## The Virtuous Cycle

```mermaid
flowchart TB
    A[Read something] --> B[Resonates - Spark]
    B --> C[Connect to domain concept]
    C --> D[Explore relationships]
    D --> E[AI asks personalized question]
    E --> F[Articulate insight]
    F --> G[Insight enriches personal graph]
    G --> H[Profile learns your patterns]
    H --> I[Better suggestions next time]
    I --> A

    style A fill:#e1f5fe
    style F fill:#c8e6c9
    style H fill:#fff3e0
```

---

## Critical Gaps

|Gap|What's Missing|Impact|
|---|--------------|------|
|Gap 1|SiYuan Structure|Can't capture - no destination|
|Gap 2|Personal Graph Integration|Can't personalize|
|Gap 3|Book Library Access|Can't start reading from system|
|Gap 4|Journey to Value loop|Data captured but unused|
|Gap 5|Cross-App Sync|Fragmented experience|

---

*Source: SiYuan note "System Design Visual"*
