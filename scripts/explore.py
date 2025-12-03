#!/usr/bin/env python3
"""
CLI Knowledge Graph Exploration Tool (Layer 3 MVP)

Navigate the 50k therapy entity knowledge graph interactively.
Saves exploration path as markdown breadcrumbs.

Usage:
    python scripts/explore.py "acceptance"
    python scripts/explore.py --concept "grief"
    python scripts/explore.py --interactive
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Add library to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from library.graph.neo4j_client import KnowledgeGraph
from library.search.hybrid import HybridSearch

# Rich terminal formatting (optional, degrades gracefully)
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


class ExplorationSession:
    """Tracks exploration path and provides navigation."""

    def __init__(self, output_dir: str = "docs/explorations"):
        self.kg = KnowledgeGraph()
        self.search = HybridSearch()
        self.path = []  # List of (concept, depth, timestamp)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d-%H%M%S")

    def explore(self, concept: str, depth: int = 2) -> dict:
        """Explore a concept and its connections."""
        # Record in path
        self.path.append({
            "concept": concept,
            "depth": depth,
            "timestamp": datetime.now().isoformat()
        })

        # Get related concepts from graph
        related = self.kg.find_related_concepts(concept, depth=depth)

        # Get supporting text chunks
        chunks = self.kg.find_supporting_chunks(concept, limit=3)

        return {
            "concept": concept,
            "related": related,
            "sources": chunks,
            "path_length": len(self.path)
        }

    def search_concepts(self, query: str, limit: int = 10) -> list:
        """Search for concepts matching a query."""
        results = self.search.hybrid_search(query, limit=limit)
        return results

    def explain(self, concept: str) -> str:
        """Get an explanation of a concept with sources."""
        return self.search.explain_concept(concept)

    def get_stats(self) -> dict:
        """Get knowledge graph statistics."""
        return self.kg.get_stats()

    def save_path(self) -> Path:
        """Save exploration path as markdown."""
        filename = f"exploration-{self.session_id}.md"
        filepath = self.output_dir / filename

        content = [
            f"# Exploration Session {self.session_id}",
            "",
            f"**Started:** {self.path[0]['timestamp'] if self.path else 'N/A'}",
            f"**Concepts explored:** {len(self.path)}",
            "",
            "## Exploration Path",
            ""
        ]

        for i, step in enumerate(self.path, 1):
            content.append(f"{i}. **{step['concept']}** (depth {step['depth']})")

        content.extend([
            "",
            "## Concepts Visited",
            ""
        ])

        for step in self.path:
            content.append(f"### {step['concept']}")
            content.append(f"*Explored at {step['timestamp']}*")
            content.append("")

        filepath.write_text("\n".join(content))
        return filepath

    def close(self):
        """Clean up resources."""
        self.kg.close()


def print_result(result: dict):
    """Display exploration result."""
    related = result.get('related', {})
    nodes = related.get('nodes', []) if isinstance(related, dict) else []
    relationships = related.get('relationships', []) if isinstance(related, dict) else []

    if RICH_AVAILABLE:
        console.print(Panel(f"[bold]{result['concept']}[/bold]",
                           subtitle=f"Path depth: {result['path_length']}"))

        if nodes:
            table = Table(title="Related Concepts")
            table.add_column("Concept", style="cyan")
            table.add_column("Type", style="green")

            for node in nodes[:15]:
                name = node.get('name', 'Unknown')
                labels = ", ".join(node.get('labels', node.keys()))
                table.add_row(name, labels)
            console.print(table)

        if relationships:
            console.print("\n[bold]Relationships:[/bold]")
            for rel in relationships[:10]:
                console.print(f"  {rel.get('start', '?')} --[{rel.get('type', '?')}]--> {rel.get('end', '?')}")

        if result.get('sources'):
            console.print("\n[bold]Source Passages:[/bold]")
            for i, chunk in enumerate(result['sources'][:3], 1):
                text = chunk.get('text', chunk.get('content', ''))[:200]
                console.print(f"  {i}. {text}...")
    else:
        print(f"\n=== {result['concept']} ===")
        print(f"Path depth: {result['path_length']}")

        if nodes:
            print(f"\nRelated Concepts ({len(nodes)} found):")
            for node in nodes[:15]:
                name = node.get('name', 'Unknown')
                print(f"  - {name}")

        if relationships:
            print(f"\nRelationships ({len(relationships)} found):")
            for rel in relationships[:10]:
                print(f"  {rel.get('start', '?')} --[{rel.get('type', '?')}]--> {rel.get('end', '?')}")

        if result.get('sources'):
            print("\nSource Passages:")
            for i, chunk in enumerate(result['sources'][:3], 1):
                text = chunk.get('text', chunk.get('content', ''))[:200]
                print(f"  {i}. {text}...")


def interactive_mode(session: ExplorationSession):
    """Run interactive exploration loop."""
    print("\n=== Knowledge Graph Explorer ===")
    print("Commands: explore <concept>, search <query>, explain <concept>, stats, path, save, quit")
    print()

    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not cmd:
            continue

        parts = cmd.split(maxsplit=1)
        action = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if action in ("quit", "exit", "q"):
            break
        elif action == "explore" and arg:
            result = session.explore(arg)
            print_result(result)
        elif action == "search" and arg:
            results = session.search_concepts(arg)
            print(f"\nSearch results for '{arg}':")
            for i, r in enumerate(results[:10], 1):
                # SearchResult is a dataclass with content, score, related_concepts
                concepts = ", ".join(r.related_concepts[:3]) if r.related_concepts else "N/A"
                print(f"  {i}. {r.content[:80]}... (concepts: {concepts})")
        elif action == "explain" and arg:
            explanation = session.explain(arg)
            print(f"\n{explanation}")
        elif action == "stats":
            stats = session.get_stats()
            print(f"\nKnowledge Graph Stats:")
            for k, v in stats.items():
                print(f"  {k}: {v}")
        elif action == "path":
            print(f"\nExploration path ({len(session.path)} steps):")
            for i, step in enumerate(session.path, 1):
                print(f"  {i}. {step['concept']}")
        elif action == "save":
            filepath = session.save_path()
            print(f"\nSaved to {filepath}")
        else:
            print("Unknown command. Try: explore <concept>, search <query>, explain <concept>, stats, path, save, quit")

    # Save on exit
    if session.path:
        filepath = session.save_path()
        print(f"\nExploration saved to {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Explore the therapy knowledge graph")
    parser.add_argument("concept", nargs="?", help="Concept to explore")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--depth", "-d", type=int, default=2, help="Exploration depth")
    parser.add_argument("--search", "-s", help="Search for concepts")
    args = parser.parse_args()

    session = ExplorationSession()

    try:
        if args.interactive:
            interactive_mode(session)
        elif args.search:
            results = session.search_concepts(args.search)
            print(f"\nSearch results for '{args.search}':")
            for i, r in enumerate(results[:10], 1):
                concepts = ", ".join(r.related_concepts[:3]) if r.related_concepts else "N/A"
                print(f"  {i}. {r.content[:80]}... (concepts: {concepts})")
        elif args.concept:
            result = session.explore(args.concept, depth=args.depth)
            print_result(result)
            filepath = session.save_path()
            print(f"\nExploration saved to {filepath}")
        else:
            # Default to interactive mode
            interactive_mode(session)
    finally:
        session.close()


if __name__ == "__main__":
    main()
