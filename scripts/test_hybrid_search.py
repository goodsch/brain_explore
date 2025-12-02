#!/usr/bin/env python3
"""
Test hybrid search with populated data.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from library.search.hybrid import HybridSearch
from library.graph.neo4j_client import KnowledgeGraph

console = Console()


def test_vector_search(searcher: HybridSearch, query: str, limit: int = 5):
    """Test pure vector search."""
    console.print(f"\n[bold cyan]Vector Search:[/] '{query}'")
    results = searcher.vector_search(query, limit=limit)

    for i, r in enumerate(results, 1):
        metadata = r.get("metadata") or {}
        source = Path(metadata.get("source_file", "unknown")).stem[:30]
        chapter = (metadata.get("chapter") or "")[:20]
        content_preview = r["content"][:150].replace("\n", " ")
        console.print(f"  {i}. [green]{r['score']:.3f}[/] | {source} | {chapter}")
        console.print(f"     {content_preview}...")

    return results


def test_graph_search(searcher: HybridSearch, concept: str):
    """Test knowledge graph search."""
    console.print(f"\n[bold cyan]Graph Search:[/] '{concept}'")

    try:
        result = searcher.graph_search(concept)

        if result.get("related", {}).get("nodes"):
            console.print("  Related concepts:")
            for node in result["related"]["nodes"][:5]:
                console.print(f"    - {node.get('name', 'unknown')}")

        if result.get("authors"):
            console.print("  Key authors:")
            for author in result["authors"][:5]:
                console.print(f"    - {author.get('author', 'unknown')}")

        return result
    except Exception as e:
        console.print(f"  [yellow]Graph search error: {e}[/]")
        return {}


def test_hybrid_search(searcher: HybridSearch, query: str, concepts: list[str]):
    """Test hybrid search combining vector + graph."""
    console.print(f"\n[bold cyan]Hybrid Search:[/] '{query}' + concepts {concepts}")

    results = searcher.hybrid_search(query, concepts=concepts, limit=5)

    for i, r in enumerate(results, 1):
        source = Path(r.source_file).stem[:30] if r.source_file else "unknown"
        console.print(f"  {i}. [green]{r.score:.3f}[/] | {source}")
        if r.related_concepts:
            console.print(f"     Concepts: {', '.join(r.related_concepts[:3])}")
        if r.supporting_authors:
            console.print(f"     Authors: {', '.join(r.supporting_authors[:3])}")
        content_preview = r.content[:100].replace("\n", " ")
        console.print(f"     {content_preview}...")

    return results


def show_graph_stats():
    """Show current graph statistics."""
    graph = KnowledgeGraph()
    stats = graph.get_stats()
    graph.close()

    console.print("\n[bold]Knowledge Graph Stats[/]")

    if stats["nodes"]:
        table = Table(title="Nodes")
        table.add_column("Type", style="cyan")
        table.add_column("Count", style="green")
        for label, count in sorted(stats["nodes"].items(), key=lambda x: -x[1]):
            table.add_row(label, str(count))
        console.print(table)

    if stats["relationships"]:
        table = Table(title="Relationships")
        table.add_column("Type", style="cyan")
        table.add_column("Count", style="green")
        for rel_type, count in sorted(stats["relationships"].items(), key=lambda x: -x[1]):
            table.add_row(rel_type, str(count))
        console.print(table)


def main():
    console.print(Panel.fit("[bold]Hybrid Search Verification[/]", border_style="blue"))

    # Show graph stats first
    show_graph_stats()

    # Initialize hybrid searcher
    console.print("\n[dim]Initializing search components...[/]")
    searcher = HybridSearch()

    # Test queries
    queries = [
        ("psychological flexibility and acceptance", ["psychological flexibility", "acceptance"]),
        ("emotion regulation strategies", ["emotion regulation"]),
        ("trauma treatment approaches", ["trauma", "PTSD"]),
        ("internal family systems parts", ["IFS", "parts"]),
        ("motivational interviewing techniques", ["motivation", "change talk"]),
    ]

    for query, concepts in queries:
        console.print(f"\n{'='*60}")

        # Vector search
        test_vector_search(searcher, query, limit=3)

        # Graph search for first concept
        if concepts:
            test_graph_search(searcher, concepts[0])

        # Hybrid search
        test_hybrid_search(searcher, query, concepts)

    console.print("\n[bold green]Verification complete![/]")


if __name__ == "__main__":
    main()
