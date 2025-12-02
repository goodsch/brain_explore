#!/usr/bin/env python3
"""
Ingest books from the library into the vector store.

Usage:
    python scripts/ingest_library.py                    # Process all books
    python scripts/ingest_library.py --file path/to.pdf # Process single file
    python scripts/ingest_library.py --test             # Test with one book
"""

import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add library to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from library.ingest.extract import extract_document, extract_all
from library.ingest.chunk import chunk_document
from library.ingest.embed import Embedder, VectorStore, embed_and_store

console = Console()

BOOKS_DIR = Path(__file__).parent.parent / "books"


def ingest_single_file(path: Path, embedder: Embedder, store: VectorStore) -> dict:
    """Ingest a single file and return stats."""
    console.print(f"\n[bold blue]Processing:[/] {path.name}")

    # Extract
    with console.status("Extracting text..."):
        doc = extract_document(path)
    console.print(f"  Extracted: {len(doc.sections)} sections")

    # Chunk
    with console.status("Chunking..."):
        chunks = chunk_document(doc, max_tokens=512, overlap=50)
    console.print(f"  Created: {len(chunks)} chunks")

    # Embed and store
    with console.status("Embedding and storing..."):
        count = embed_and_store(chunks, embedder, store)
    console.print(f"  Stored: {count} vectors")

    return {
        "file": path.name,
        "sections": len(doc.sections),
        "chunks": len(chunks),
        "vectors": count
    }


def ingest_directory(directory: Path, limit: int | None = None):
    """Ingest all books in directory."""
    files = list(directory.glob("*.pdf")) + list(directory.glob("*.epub"))

    if limit:
        files = files[:limit]

    console.print(f"\n[bold green]Found {len(files)} files to process[/]\n")

    embedder = Embedder()
    store = VectorStore()

    results = []
    errors = []

    for path in files:
        try:
            result = ingest_single_file(path, embedder, store)
            results.append(result)
        except Exception as e:
            console.print(f"[bold red]Error processing {path.name}:[/] {e}")
            errors.append({"file": path.name, "error": str(e)})

    # Summary
    console.print("\n" + "=" * 50)
    console.print("[bold green]Ingestion Complete[/]")
    console.print(f"  Processed: {len(results)} files")
    console.print(f"  Errors: {len(errors)} files")
    console.print(f"  Total chunks: {sum(r['chunks'] for r in results)}")

    # Vector store stats
    stats = store.get_stats()
    console.print(f"\n[bold]Vector Store:[/]")
    console.print(f"  Total vectors: {stats['vectors_count']}")
    console.print(f"  Status: {stats['status']}")

    return results, errors


def test_search(query: str):
    """Test search functionality."""
    console.print(f"\n[bold blue]Testing search:[/] '{query}'")

    embedder = Embedder()
    store = VectorStore()

    # Embed query
    query_embedding = embedder.embed_text(query)

    # Search
    results = store.search(query_embedding, limit=5)

    console.print(f"\nFound {len(results)} results:\n")
    for i, r in enumerate(results, 1):
        console.print(f"[bold]{i}. Score: {r['score']:.3f}[/]")
        console.print(f"   Source: {r['metadata'].get('source_file', 'unknown')}")
        console.print(f"   Chapter: {r['metadata'].get('chapter', 'N/A')}")
        console.print(f"   Content: {r['content'][:200]}...")
        console.print()


def main():
    parser = argparse.ArgumentParser(description="Ingest library into vector store")
    parser.add_argument("--file", type=Path, help="Process single file")
    parser.add_argument("--test", action="store_true", help="Test with first book only")
    parser.add_argument("--search", type=str, help="Test search with query")
    parser.add_argument("--stats", action="store_true", help="Show vector store stats")

    args = parser.parse_args()

    if args.stats:
        store = VectorStore()
        stats = store.get_stats()
        console.print(f"[bold]Vector Store Stats:[/]")
        for k, v in stats.items():
            console.print(f"  {k}: {v}")
        return

    if args.search:
        test_search(args.search)
        return

    if args.file:
        embedder = Embedder()
        store = VectorStore()
        ingest_single_file(args.file, embedder, store)
    elif args.test:
        ingest_directory(BOOKS_DIR, limit=1)
    else:
        ingest_directory(BOOKS_DIR)


if __name__ == "__main__":
    main()
