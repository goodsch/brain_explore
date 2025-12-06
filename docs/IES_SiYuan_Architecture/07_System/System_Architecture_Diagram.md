# System Architecture Diagram (Mermaid)

```mermaid
graph TD
    subgraph Capture
        A[External Inputs<br/>Shortcuts, MCP, Voice, Apps]
        B[00_Inbox]
    end

    subgraph Seeds
        C[01_Seedlings]
    end

    subgraph Shaping
        D[02_Shaping<br/>Dialogue Sessions]
    end

    subgraph Flow
        E[03_Flow_Maps<br/>Concept Maps, Schemas, Timelines]
    end

    subgraph Knowledge
        F[04_Concepts<br/>Canonical Pages]
    end

    subgraph Doing
        G[05_Projects<br/>Structured Workspaces]
    end

    subgraph Archive
        H[06_Archive]
    end

    subgraph Meta
        I[07_System<br/>Schemas, Templates, Directives]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H

    C --> F
    C --> G
    D --> F
    D --> G
    E --> G

    I --> B
    I --> C
    I --> D
    I --> E
    I --> F
    I --> G
    I --> H
```

This diagram expresses the **logical architecture** of the IES × SiYuan system:

- `07_System` influences how all other layers behave.
- Data flows mostly left-to-right (Capture → Archive) but with flexible
  shortcuts based on context.
