# brain_explore Project Visualizations

*Visual representations of architecture, progress, and roadmap*

**Exported from SiYuan:** December 4, 2025

---

## 1. Four-Layer Architecture

```mermaid
flowchart TB
    subgraph L4["Layer 4: READEST"]
        R1[E-book Reader]
        R2[Flow Mode Toggle]
        R3[Entity Panel]
        R4[Breadcrumb Capture]
    end

    subgraph L3["Layer 3: SIYUAN PLUGIN"]
        S1[Dashboard Hub]
        S2[5 Thinking Modes]
        S3[Flow Exploration]
        S4[Quick Capture]
    end

    subgraph L2["Layer 2: BACKEND APIs"]
        B1[Graph API]
        B2[Session API]
        B3[Journey API]
        B4[Capture API]
        B5[Question Engine]
    end

    subgraph L1["Layer 1: KNOWLEDGE GRAPH"]
        K1[(Neo4j<br/>50k entities)]
        K2[(Qdrant<br/>Vectors)]
        K3[(Personal Graph<br/>ADHD Ontology)]
    end

    L4 --> L2
    L3 --> L2
    L2 --> L1

    style L4 fill:#e1f5fe
    style L3 fill:#f3e5f5
    style L2 fill:#fff3e0
    style L1 fill:#e8f5e9
```

---

## 2. Phase Progress Timeline

```mermaid
gantt
    title brain_explore Development Phases
    dateFormat  YYYY-MM-DD
    section Phase 0
    Config Stabilization     :done, p0, 2025-12-01, 1d
    section Phase 1
    10 Validation Sessions   :done, p1a, 2025-12-02, 1d
    11 Concepts Extracted    :done, p1b, 2025-12-02, 1d
    section Phase 2a
    CLI Validation (5 tests) :done, p2a, 2025-12-02, 1d
    section Phase 2b
    Backend Graph APIs       :done, p2b1, 2025-12-02, 1d
    SiYuan Plugin MVP        :done, p2b2, 2025-12-02, 1d
    Readest Integration      :done, p2b3, 2025-12-03, 1d
    ADHD Ontology           :done, p2b4, 2025-12-04, 1d
    section Phase 2c
    User Testing             :active, p2c, 2025-12-04, 7d
    section Phase 3
    Domain Generalization    :p3, 2025-12-15, 14d
```

---

## 3. Thinking Partnership Cycle

```mermaid
flowchart LR
    subgraph Input
        A[User Reading<br/>Layer 4]
        B[User Exploring<br/>Layer 3]
    end

    subgraph Processing
        C[Thinking Partner<br/>Questions]
        D[Pattern<br/>Recognition]
    end

    subgraph Output
        E[Breadcrumb<br/>Journeys]
        F[Novel<br/>Concepts]
    end

    subgraph Enrichment
        G[Knowledge Graph<br/>Layer 1]
    end

    A --> C
    B --> C
    C --> D
    D --> E
    D --> F
    F --> G
    G --> A
    G --> B

    style Input fill:#bbdefb
    style Processing fill:#fff9c4
    style Output fill:#c8e6c9
    style Enrichment fill:#ffccbc
```

---

## 4. Component Status Dashboard

|Layer|Component|Status|Progress|
|-----|---------|------|--------|
|4|Readest Flow Mode|Complete|100%|
|4|Entity Panel|Complete|100%|
|4|Journey Capture|Complete|100%|
|3|Dashboard|Complete|100%|
|3|5 Thinking Modes|Complete|100%|
|3|Flow Exploration|Complete|100%|
|3|Quick Capture|Complete|100%|
|2|Graph API|Complete|100%|
|2|Journey API|Complete|100%|
|2|Session API|Complete|100%|
|2|Personal Graph API|**Missing**|0%|
|2|Tests|Partial|89%|
|1|Neo4j Graph|Complete|100%|
|1|Qdrant Vectors|Complete|100%|
|1|ADHD Ontology|Complete|100%|

---

## 5. Worktree Organization

```mermaid
flowchart TB
    subgraph Master["master branch"]
        M1[Backend APIs]
        M2[Shared Docs]
        M3[Library Code]
        M4[ADHD Ontology]
    end

    subgraph Readest[".worktrees/readest"]
        R1[Layer 4 Code]
        R2[Flow Mode]
        R3[TASK.md]
    end

    subgraph SiYuan[".worktrees/siyuan"]
        S1[Layer 3 Code]
        S2[Plugin Views]
        S3[TASK.md]
    end

    Master -.-> Readest
    Master -.-> SiYuan

    style Master fill:#e3f2fd
    style Readest fill:#fce4ec
    style SiYuan fill:#f3e5f5
```

---

## 6. API Endpoint Map

```mermaid
flowchart LR
    subgraph Client["Clients"]
        C1[Readest]
        C2[SiYuan Plugin]
        C3[CLI Tools]
    end

    subgraph Backend["Backend :8081"]
        subgraph Graph["/graph"]
            G1[/stats]
            G2[/search]
            G3[/explore]
            G4[/sources]
            G5[/suggestions]
            G6[/thinking-partner]
        end

        subgraph Journey["/journeys"]
            J1[POST /]
            J2[GET /id]
            J3[GET /user/id]
        end

        subgraph Capture["/capture"]
            CP1[POST /process]
        end

        subgraph Session["/session"]
            S1[POST /]
            S2[POST /id/message]
            S3[GET /context/id]
        end

        subgraph Personal["/personal - NEEDED"]
            P1[/sparks]
            P2[/insights]
            P3[/threads]
            P4[/favorite-problems]
        end
    end

    C1 --> Graph
    C1 --> Journey
    C2 --> Graph
    C2 --> Journey
    C2 --> Capture
    C2 --> Session
    C3 --> Graph
```

---

## 7. Data Flow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant R as Readest/SiYuan
    participant B as Backend
    participant G as Neo4j Graph
    participant Q as Qdrant

    U->>R: Select text / Search concept
    R->>B: GET /graph/search
    B->>Q: Semantic search
    Q-->>B: Matching entities
    B->>G: Get relationships
    G-->>B: Entity + relations
    B-->>R: Entity data
    R-->>U: Display entity panel

    U->>R: Navigate to related concept
    R->>B: GET /graph/explore/{id}
    B->>G: Query neighborhood
    G-->>B: Related entities
    B-->>R: Grouped relationships
    R-->>U: Update display

    U->>R: End session
    R->>B: POST /journeys
    B->>G: Store breadcrumbs
    B-->>R: Journey saved
    R-->>U: Confirmation
```

---

## 8. Knowledge Graph Statistics

|Metric|Value|
|------|-----|
|**Total Entities**|50,000+|
|**Relationships**|125,000+|
|**Books Ingested**|63|
|**Relationship Types**|supports, contrasts, develops, component_of, cites, authored_by|
|**Entity Types**|Concept, Theory, Researcher, Assessment, Book, Chapter|
|**User Concepts**|11 (personal growth framework — active application)|
|**ADHD Entity Types**|spark, insight, thread, favorite_problem|

---

*Source: SiYuan note "Project Visualizations"*
