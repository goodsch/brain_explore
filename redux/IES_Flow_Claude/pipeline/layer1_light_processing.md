# Layer 1 – Universal Light Processing & Indexing

Layer 1 runs for **all** sources. It is designed to be:

- Fast
- Shallow
- Sufficient to support initial exploration and Flow queries

## Operations

1. **Chunking**
   - Split sources into manageable units (e.g., paragraphs/sections).
   - Maintain mapping: `chunk_id -> (source_id, location, text)`.

2. **Global Summary & Themes**
   - Generate a high-level summary per source.
   - Extract themes / categories / topics.
   - Optionally map to a shared taxonomy (ADHD, UX, cognition, etc.).

3. **Light Entity Extraction**
   - NER-style pass to extract:
     - People, methods, institutions.
     - Abstract concepts, key terms.
   - Normalize to canonical Concept/Person/Theory nodes when possible.
   - Create new entities with low-confidence flags when needed.

4. **Word / Phrase Index**
   - Build a full-text index:
     - tokens/phrases → list of (source_id, chunk_id, positions).
   - Consider:
     - simple word index,
     - phrase index,
     - normalized term index.

## Outputs

- Basic Concept/Person/Theory nodes connected to sources.
- Fast search capabilities for words & phrases.
- Thematic labels on sources to guide further processing.
