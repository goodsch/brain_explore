# Multi-Layer Entity & Source Processing Pipeline

The pipeline has four conceptual layers:

- **Layer 0:** Ingestion & external metadata (cheap, API-based).
- **Layer 1:** Universal light processing & indexing (fast, broad coverage).
- **Layer 2:** Deeper relational & semantic processing (selective, scheduled).
- **Layer 3:** Flow-triggered, context-specific extraction (on-demand, focused).

The goal is to:

- Provide broad, low-cost structure for all sources.
- Build fast search primitives (word/phrase index).
- Concentrate heavy processing where it matters most:
  - around active Feynman Problems, Projects, Questions, and Concepts.
