#!/usr/bin/env python3
"""Extract entities from a single book (for parallel execution)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from library.ingest.extract import extract_document
from library.ingest.chunk import chunk_document
from library.graph.entities import EntityExtractor, deduplicate_entities
from library.graph.neo4j_client import KnowledgeGraph


def extract_book(book_path: str):
    """Extract entities from one book."""
    path = Path(book_path)
    print(f"Processing: {path.name}")

    # Extract and chunk
    doc = extract_document(path)
    chunks = chunk_document(doc, max_tokens=512, overlap=50)
    print(f"  {len(chunks)} chunks")

    # Initialize
    extractor = EntityExtractor()
    graph = KnowledgeGraph()

    # Add book to graph
    graph.add_book(doc.title, doc.author, str(path))

    # Extract entities
    total_entities = 0
    total_relationships = 0

    for i, chunk in enumerate(chunks):
        if i % 50 == 0:
            print(f"  Chunk {i}/{len(chunks)}")

        try:
            result = extractor.extract_from_chunk(chunk)
            if result.entities or result.relationships:
                graph.add_extraction_result(result, str(path))
                total_entities += len(result.entities)
                total_relationships += len(result.relationships)
        except Exception as e:
            print(f"  Error on chunk {i}: {e}")

    graph.close()
    print(f"Done: {path.name} - {total_entities} entities, {total_relationships} relationships")
    return total_entities, total_relationships


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_single.py <book_path>")
        sys.exit(1)
    extract_book(sys.argv[1])
