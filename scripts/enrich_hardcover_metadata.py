#!/usr/bin/env python3
"""
Pass 0: Enrich Calibre books with Hardcover metadata.

Searches Hardcover for each Calibre book and adds rich metadata:
- Description/summary
- Genre and subject tags
- Series information
- Community statistics

This metadata improves entity extraction quality by providing
context about the book's subject matter.

Usage:
    python scripts/enrich_hardcover_metadata.py                # Process all books
    python scripts/enrich_hardcover_metadata.py --id 42        # Process single book
    python scripts/enrich_hardcover_metadata.py --status       # Show enrichment stats
    python scripts/enrich_hardcover_metadata.py --limit 10     # Process N books
    python scripts/enrich_hardcover_metadata.py --test         # Test with one book
"""

import argparse
import asyncio
import os
import sqlite3
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "ies" / "backend" / "src"))

from library.graph.neo4j_client import KnowledgeGraph
from ies_backend.services.hardcover_service import HardcoverService, HardcoverBook

console = Console()

# Configuration
CALIBRE_DB = Path("./calibre/library/metadata.db")

# Set API token from environment or use provided token
DEFAULT_TOKEN = os.getenv("HARDCOVER_API_TOKEN")


def get_calibre_books(
    limit: int | None = None,
    calibre_id: int | None = None,
) -> list[dict]:
    """Get books from Calibre that need metadata enrichment."""
    conn = sqlite3.connect(CALIBRE_DB)
    conn.row_factory = sqlite3.Row

    if calibre_id:
        cursor = conn.execute(
            """
            SELECT b.id, b.title, b.path,
                   GROUP_CONCAT(a.name, ', ') as authors
            FROM books b
            LEFT JOIN books_authors_link bal ON b.id = bal.book
            LEFT JOIN authors a ON bal.author = a.id
            WHERE b.id = ?
            GROUP BY b.id
            """,
            (calibre_id,),
        )
    else:
        query = """
            SELECT b.id, b.title, b.path,
                   GROUP_CONCAT(a.name, ', ') as authors
            FROM books b
            LEFT JOIN books_authors_link bal ON b.id = bal.book
            LEFT JOIN authors a ON bal.author = a.id
            GROUP BY b.id
            ORDER BY b.title
        """
        if limit:
            query += f" LIMIT {limit}"
        cursor = conn.execute(query)

    books = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return books


def get_books_needing_enrichment(kg: KnowledgeGraph, limit: int | None = None) -> list[dict]:
    """Get Neo4j books without Hardcover metadata."""
    with kg.driver.session() as session:
        query = """
            MATCH (b:Book)
            WHERE b.calibre_id IS NOT NULL
              AND b.hardcover_id IS NULL
              AND NOT b.title STARTS WITH "ADHD Test"
            RETURN b.calibre_id as calibre_id, b.title as title, b.author as author
            ORDER BY b.title
        """
        if limit:
            query += f" LIMIT {limit}"

        result = session.run(query)
        return [dict(record) for record in result]


def update_book_metadata(kg: KnowledgeGraph, calibre_id: int, metadata: HardcoverBook) -> bool:
    """Update Neo4j book node with Hardcover metadata."""
    with kg.driver.session() as session:
        try:
            session.run(
                """
                MATCH (b:Book {calibre_id: $calibre_id})
                SET b.hardcover_id = $hardcover_id,
                    b.description = $description,
                    b.genres = $genres,
                    b.subjects = $subjects,
                    b.series_name = $series_name,
                    b.series_position = $series_position,
                    b.hardcover_rating = $rating,
                    b.hardcover_read_count = $read_count,
                    b.pages = $pages,
                    b.release_year = $release_year,
                    b.metadata_source = 'hardcover',
                    b.metadata_enriched_at = datetime()
                """,
                {
                    "calibre_id": calibre_id,
                    "hardcover_id": metadata.hardcover_id,
                    "description": metadata.description,
                    "genres": metadata.genres,
                    "subjects": metadata.subjects,
                    "series_name": metadata.series_name,
                    "series_position": metadata.series_position,
                    "rating": metadata.rating,
                    "read_count": metadata.users_read_count,
                    "pages": metadata.pages,
                    "release_year": metadata.release_year,
                },
            )
            return True
        except Exception as e:
            console.print(f"  [red]DB error: {e}[/]")
            return False


async def enrich_book(
    service: HardcoverService,
    kg: KnowledgeGraph,
    calibre_id: int,
    title: str,
    author: str | None,
) -> dict:
    """Enrich a single book with Hardcover metadata."""
    stats = {
        "calibre_id": calibre_id,
        "title": title,
        "status": "not_found",
        "hardcover_id": None,
        "genres": 0,
    }

    try:
        console.print(f"\n[bold blue]Searching:[/] {title[:60]}")
        if author:
            console.print(f"  Author: {author}")

        # Search Hardcover
        metadata = await service.search_and_match(title, author)

        if not metadata:
            console.print("  [yellow]No match found[/]")
            return stats

        console.print(f"  [green]Found:[/] {metadata.title} (ID: {metadata.hardcover_id})")

        if metadata.genres:
            console.print(f"  Genres: {', '.join(metadata.genres[:5])}")
        if metadata.description:
            console.print(f"  Description: {metadata.description[:100]}...")

        # Update Neo4j
        if update_book_metadata(kg, calibre_id, metadata):
            stats["status"] = "enriched"
            stats["hardcover_id"] = metadata.hardcover_id
            stats["genres"] = len(metadata.genres or [])
            console.print("  [green]✓ Metadata saved to Neo4j[/]")
        else:
            stats["status"] = "db_error"

    except Exception as e:
        console.print(f"  [bold red]Error:[/] {e}")
        stats["status"] = f"error: {str(e)[:30]}"

    return stats


async def show_status(kg: KnowledgeGraph):
    """Show Hardcover enrichment status."""
    with kg.driver.session() as session:
        # Books with/without Hardcover metadata
        result = session.run("""
            MATCH (b:Book)
            WHERE b.calibre_id IS NOT NULL
            RETURN
                count(CASE WHEN b.hardcover_id IS NOT NULL THEN 1 END) as enriched,
                count(CASE WHEN b.hardcover_id IS NULL THEN 1 END) as pending,
                count(b) as total
        """)
        record = result.single()

        table = Table(title="Hardcover Enrichment Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", justify="right")

        table.add_row("Total books with calibre_id", str(record["total"]))
        table.add_row("Enriched with Hardcover", str(record["enriched"]))
        table.add_row("Pending enrichment", str(record["pending"]))

        console.print(table)

        # Sample enriched books
        result = session.run("""
            MATCH (b:Book)
            WHERE b.hardcover_id IS NOT NULL
            RETURN b.title as title, b.hardcover_id as hc_id,
                   size(b.genres) as genres, b.hardcover_rating as rating
            LIMIT 5
        """)

        console.print("\n[bold]Sample Enriched Books:[/]")
        for record in result:
            genres = record["genres"] or 0
            rating = record["rating"] or "N/A"
            console.print(f"  [cyan]{record['title'][:40]}[/] - {genres} genres, rating: {rating}")


async def main():
    parser = argparse.ArgumentParser(description="Enrich books with Hardcover metadata")
    parser.add_argument("--id", type=int, help="Process single book by calibre_id")
    parser.add_argument("--status", action="store_true", help="Show enrichment stats")
    parser.add_argument("--limit", type=int, help="Limit number of books")
    parser.add_argument("--test", action="store_true", help="Test with one book")
    parser.add_argument("--token", type=str, help="Hardcover API token (or set HARDCOVER_API_TOKEN)")
    args = parser.parse_args()

    # Get token
    token = args.token or DEFAULT_TOKEN
    if not token and not args.status:
        console.print("[bold red]Error:[/] No API token provided")
        console.print("Set HARDCOVER_API_TOKEN environment variable or use --token")
        return

    kg = KnowledgeGraph()

    if args.status:
        await show_status(kg)
        return

    service = HardcoverService(api_token=token)

    # Determine what to process
    if args.test:
        args.limit = 1

    if args.id:
        # Single book from Calibre
        books = get_calibre_books(calibre_id=args.id)
    else:
        # Books from Neo4j needing enrichment
        books = get_books_needing_enrichment(kg, limit=args.limit)

        # If no Neo4j books, fall back to Calibre
        if not books:
            console.print("[yellow]No Neo4j books need enrichment. Checking Calibre...[/]")
            calibre_books = get_calibre_books(limit=args.limit)
            books = [
                {"calibre_id": b["id"], "title": b["title"], "author": b["authors"]}
                for b in calibre_books
            ]

    if not books:
        console.print("[yellow]No books found to enrich[/]")
        return

    console.print(f"[bold]Found {len(books)} books to enrich[/]")

    # Process books
    all_stats = []
    for book in books:
        stats = await enrich_book(
            service=service,
            kg=kg,
            calibre_id=book.get("calibre_id") or book.get("id"),
            title=book["title"],
            author=book.get("author") or book.get("authors"),
        )
        all_stats.append(stats)

        # Rate limit: ~1 request per second to stay under 60/min
        await asyncio.sleep(1.0)

    # Summary
    console.print("\n" + "=" * 60)
    table = Table(title="Enrichment Summary")
    table.add_column("Title", max_width=35)
    table.add_column("Hardcover ID", justify="right")
    table.add_column("Genres", justify="right")
    table.add_column("Status", style="cyan")

    enriched = 0
    for s in all_stats:
        table.add_row(
            s["title"][:35],
            str(s["hardcover_id"] or "-"),
            str(s["genres"]),
            s["status"],
        )
        if s["status"] == "enriched":
            enriched += 1

    console.print(table)
    console.print(f"\n[bold]Enriched {enriched}/{len(all_stats)} books[/]")


if __name__ == "__main__":
    asyncio.run(main())
