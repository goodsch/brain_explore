#!/usr/bin/env python3
"""
Extract entities from ingested books and populate the knowledge graph.

Usage:
    python scripts/extract_entities.py --file path/to.pdf    # Process single file
    python scripts/extract_entities.py --test                 # Test with sample chunks
    python scripts/extract_entities.py --stats               # Show graph stats
"""

import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent.parent))

from library.ingest.extract import extract_document
from library.ingest.chunk import chunk_document
from library.graph.entities import EntityExtractor, deduplicate_entities
from library.graph.neo4j_client import KnowledgeGraph

console = Console()
BOOKS_DIR = Path(__file__).parent.parent / "books"


def extract_from_file(path: Path, sample_size: int = None):
    """Extract entities from a single file."""
    console.print(f"\n[bold blue]Processing:[/] {path.name}")

    # Extract and chunk
    with console.status("Extracting text..."):
        doc = extract_document(path)

    with console.status("Chunking..."):
        chunks = chunk_document(doc, max_tokens=512, overlap=50)

    if sample_size:
        chunks = chunks[:sample_size]
        console.print(f"  Using sample of {sample_size} chunks")

    console.print(f"  Processing {len(chunks)} chunks")

    # Initialize
    extractor = EntityExtractor()
    graph = KnowledgeGraph()

    # Add book to graph
    graph.add_book(doc.title, doc.author, str(path))

    # Extract entities
    all_results = []
    total_entities = 0
    total_relationships = 0

    for i, chunk in enumerate(chunks):
        console.print(f"  Extracting from chunk {i+1}/{len(chunks)}...", end="\r")

        try:
            result = extractor.extract_from_chunk(chunk)

            if result.entities or result.relationships:
                all_results.append(result)
                graph.add_extraction_result(result, str(path))
                total_entities += len(result.entities)
                total_relationships += len(result.relationships)

        except Exception as e:
            console.print(f"\n  [red]Error on chunk {i+1}:[/] {e}")

    console.print(f"\n  Extracted: {total_entities} entities, {total_relationships} relationships")

    # Deduplicate and show summary
    entities = deduplicate_entities(all_results)

    # Group by type
    by_type = {}
    for entity in entities.values():
        by_type.setdefault(entity.type, []).append(entity)

    console.print("\n[bold]Entities by type:[/]")
    for entity_type, ents in sorted(by_type.items()):
        console.print(f"  {entity_type}: {len(ents)}")
        for e in ents[:5]:
            console.print(f"    - {e.name}")
        if len(ents) > 5:
            console.print(f"    ... and {len(ents) - 5} more")

    graph.close()
    return all_results


def show_stats():
    """Show knowledge graph statistics."""
    graph = KnowledgeGraph()
    stats = graph.get_stats()
    graph.close()

    console.print("\n[bold]Knowledge Graph Statistics[/]\n")

    if stats["nodes"]:
        table = Table(title="Nodes")
        table.add_column("Type", style="cyan")
        table.add_column("Count", style="green")
        for label, count in stats["nodes"].items():
            table.add_row(label, str(count))
        console.print(table)

    if stats["relationships"]:
        table = Table(title="Relationships")
        table.add_column("Type", style="cyan")
        table.add_column("Count", style="green")
        for rel_type, count in stats["relationships"].items():
            table.add_row(rel_type, str(count))
        console.print(table)

    if not stats["nodes"] and not stats["relationships"]:
        console.print("[yellow]Graph is empty. Run extraction first.[/]")


def test_extraction():
    """Test extraction with a few chunks."""
    # Find first book
    books = list(BOOKS_DIR.glob("*.pdf")) + list(BOOKS_DIR.glob("*.epub"))
    if not books:
        console.print("[red]No books found in books/[/]")
        return

    path = books[0]
    console.print(f"[bold]Testing with:[/] {path.name}")

    # Extract with small sample
    extract_from_file(path, sample_size=5)


def main():
    parser = argparse.ArgumentParser(description="Extract entities to knowledge graph")
    parser.add_argument("--file", type=Path, help="Process single file")
    parser.add_argument("--test", action="store_true", help="Test with 5 chunks")
    parser.add_argument("--stats", action="store_true", help="Show graph stats")
    parser.add_argument("--sample", type=int, help="Number of chunks to sample")

    args = parser.parse_args()

    if args.stats:
        show_stats()
    elif args.test:
        test_extraction()
    elif args.file:
        extract_from_file(args.file, sample_size=args.sample)
    else:
        console.print("Use --test, --file, or --stats")
        console.print("Example: python scripts/extract_entities.py --test")


if __name__ == "__main__":
    main()
