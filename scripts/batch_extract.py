#!/usr/bin/env python3
"""
Batch extract entities from remaining books.

Usage:
    python scripts/batch_extract.py              # Process all remaining
    python scripts/batch_extract.py --priority   # Process priority books first
    python scripts/batch_extract.py --list       # List remaining books
"""

import argparse
import sys
from pathlib import Path
from rich.console import Console

sys.path.insert(0, str(Path(__file__).parent.parent))

from library.graph.neo4j_client import KnowledgeGraph
from scripts.extract_entities import extract_from_file

console = Console()
BOOKS_DIR = Path(__file__).parent.parent / "books"

# Priority books for therapy framework (most relevant first)
PRIORITY_BOOKS = [
    "Behave - Robert Sapolsky",
    "Being You - Anil Seth",
    "Surfing Uncertainty - Andy Clark",
    "Self-Compassion - Kristin Neff",
    "Atlas of the Heart - Brene Brown",
    "The Denial of Death - Ernest Becker",
    "Maps of Meaning - Jordan Peterson",
    "Thinking in Systems - Donella Meadows",
    "The Extended Mind - Annie Murphy Paul",
    "Handbook of Psychotherapy Integration",
    "Highly Sensitive Person - Elaine Aron",
    "Metaphors We Live By - Lakoff",
    "Humble Inquiry",
    "Character Strengths",
    "Experiential Learning",
    "Executive Functions - Russell Barkley",
]


def get_processed_titles():
    """Get titles already in the graph."""
    graph = KnowledgeGraph()
    with graph.driver.session() as session:
        result = session.run("MATCH (b:Book) RETURN b.title as title")
        titles = {r["title"].lower() for r in result}
    graph.close()
    return titles


def get_remaining_books():
    """Get books not yet processed."""
    processed = get_processed_titles()
    all_books = list(BOOKS_DIR.glob("*.pdf")) + list(BOOKS_DIR.glob("*.epub"))

    remaining = []
    for book in all_books:
        # Check if book title (from filename) matches any processed title
        name = book.stem.lower()
        is_processed = any(
            name.split(" - ")[0] in title or title in name
            for title in processed
        )
        if not is_processed:
            remaining.append(book)

    return remaining


def batch_extract(priority_only=False, limit=None):
    """Extract entities from remaining books."""
    remaining = get_remaining_books()
    console.print(f"\n[bold]Found {len(remaining)} books to process[/]\n")

    if priority_only:
        # Reorder by priority
        def priority_key(path):
            name = path.stem.lower()
            for i, p in enumerate(PRIORITY_BOOKS):
                if p.lower() in name:
                    return i
            return 999
        remaining.sort(key=priority_key)
        # Only process priority books
        remaining = [b for b in remaining if priority_key(b) < 999]
        console.print(f"[yellow]Processing {len(remaining)} priority books[/]\n")

    if limit:
        remaining = remaining[:limit]

    for i, book in enumerate(remaining, 1):
        console.print(f"\n[bold cyan]===== Book {i}/{len(remaining)} =====[/]")
        try:
            extract_from_file(book)
        except Exception as e:
            console.print(f"[red]Failed: {e}[/]")
            continue

    console.print("\n[bold green]Batch extraction complete![/]")


def list_remaining():
    """List books not yet processed."""
    remaining = get_remaining_books()
    console.print(f"\n[bold]Remaining books ({len(remaining)}):[/]\n")
    for book in sorted(remaining, key=lambda p: p.stem):
        console.print(f"  - {book.name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--priority", action="store_true", help="Priority books only")
    parser.add_argument("--list", action="store_true", help="List remaining books")
    parser.add_argument("--limit", type=int, help="Max books to process")

    args = parser.parse_args()

    if args.list:
        list_remaining()
    else:
        batch_extract(priority_only=args.priority, limit=args.limit)


if __name__ == "__main__":
    main()
