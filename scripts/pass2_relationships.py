#!/usr/bin/env python3
"""
Pass 2: Relationship extraction for Calibre books.

Operates on books with status='entities_extracted'
Extracts CAUSES, PART_OF, CONTRASTS_WITH relationships
Updates status to 'relationships_mapped'

Usage:
    python scripts/pass2_relationships.py                 # All books
    python scripts/pass2_relationships.py --id 42         # Single book
    python scripts/pass2_relationships.py --limit 10      # Batch limit
    python scripts/pass2_relationships.py --status        # Show stats
    python scripts/pass2_relationships.py --dry-run       # Preview only
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

# Add library to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from library.graph.relationship_extractor import (
    RelationshipExtractor,
    deduplicate_relationships,
    validate_relationship
)
from library.graph.unified_client import UnifiedGraphClient
from library.ingest.chunk import Chunk

console = Console()


@dataclass
class CalibreBook:
    """Book from Calibre library."""
    calibre_id: int
    title: str
    author: str


def get_books_for_pass2(kg: UnifiedGraphClient, limit: int | None = None, calibre_id: int | None = None) -> list[CalibreBook]:
    """Get books ready for Pass 2 relationship extraction."""
    with kg.driver.session() as session:
        if calibre_id:
            # Single book by ID
            result = session.run("""
                MATCH (b:Book {calibre_id: $calibre_id})
                WHERE b.processing_status = 'entities_extracted'
                RETURN b.calibre_id as calibre_id, b.title as title, b.author as author
            """, calibre_id=calibre_id)
        else:
            # All books with entities_extracted status
            query = """
                MATCH (b:Book)
                WHERE b.processing_status = 'entities_extracted'
                RETURN b.calibre_id as calibre_id, b.title as title, b.author as author
                ORDER BY b.title
            """
            if limit:
                query += f" LIMIT {limit}"
            result = session.run(query)

        books = []
        for record in result:
            books.append(CalibreBook(
                calibre_id=record["calibre_id"],
                title=record["title"],
                author=record["author"] or "Unknown"
            ))

        return books


def get_entity_rich_chunks(
    kg: UnifiedGraphClient,
    book: CalibreBook,
    min_entities: int = 2
) -> list[tuple[Chunk, list[str]]]:
    """Get chunks that mention multiple entities.

    Args:
        kg: Knowledge graph client
        book: Book to get chunks for
        min_entities: Minimum number of entities required per chunk

    Returns:
        List of (Chunk, entity_names) tuples
    """
    with kg.driver.session() as session:
        result = session.run("""
            MATCH (b:Book {calibre_id: $calibre_id})<-[:FROM_BOOK]-(c:Chunk)
            MATCH (c)-[:MENTIONS]->(e)
            WITH c, collect(DISTINCT e.name) as entities
            WHERE size(entities) >= $min_entities
            RETURN c.id as chunk_id, c.content as content, entities
            ORDER BY size(entities) DESC
        """, calibre_id=book.calibre_id, min_entities=min_entities)

        chunks_with_entities = []
        for record in result:
            chunk = Chunk(
                id=record["chunk_id"],
                content=record["content"],
                token_count=0,  # Not needed for relationship extraction
                metadata={}
            )
            chunks_with_entities.append((chunk, record["entities"]))

        return chunks_with_entities


def get_valid_entities(kg: UnifiedGraphClient, book: CalibreBook) -> set[str]:
    """Get all valid entity names for a book.

    Args:
        kg: Knowledge graph client
        book: Book to get entities for

    Returns:
        Set of entity names (case-sensitive)
    """
    with kg.driver.session() as session:
        result = session.run("""
            MATCH (b:Book {calibre_id: $calibre_id})-[:MENTIONS]->(e)
            RETURN DISTINCT e.name as name
        """, calibre_id=book.calibre_id)

        return {record["name"] for record in result}


def pass2_single_book(
    book: CalibreBook,
    kg: UnifiedGraphClient,
    extractor: RelationshipExtractor,
    dry_run: bool = False
) -> dict:
    """Run Pass 2 relationship extraction on a single book.

    Args:
        book: Book to process
        kg: Knowledge graph client
        extractor: Relationship extractor
        dry_run: If True, preview only without writing to Neo4j

    Returns:
        Statistics dictionary
    """
    stats = {
        "calibre_id": book.calibre_id,
        "title": book.title,
        "chunks_processed": 0,
        "relationships_extracted": 0,
        "high_confidence": 0,  # confidence >= 0.8
        "relationships_stored": 0,
        "relationships_rejected": 0,
        "status": "success"
    }

    try:
        console.print(f"\n[bold blue]Processing:[/] {book.title[:60]}")
        console.print(f"  Calibre ID: {book.calibre_id}, Author: {book.author[:40]}")

        # Get entity-rich chunks
        with console.status("  Loading entity-rich chunks..."):
            chunks_with_entities = get_entity_rich_chunks(kg, book, min_entities=2)

        if not chunks_with_entities:
            console.print("  [yellow]No entity-rich chunks found, skipping[/]")
            stats["status"] = "no_chunks"
            return stats

        console.print(f"  Found: {len(chunks_with_entities)} entity-rich chunks")
        stats["chunks_processed"] = len(chunks_with_entities)

        # Get valid entities for validation
        valid_entities = get_valid_entities(kg, book)
        console.print(f"  Valid entities: {len(valid_entities)}")

        # Extract relationships
        all_relationships = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("  Extracting relationships...", total=len(chunks_with_entities))

            for result in extractor.extract_relationships_from_chunks(chunks_with_entities):
                all_relationships.extend(result.relationships)
                progress.advance(task)

        # Deduplicate relationships
        with console.status("  Deduplicating relationships..."):
            unique_relationships = deduplicate_relationships(all_relationships)

        stats["relationships_extracted"] = len(unique_relationships)
        console.print(f"  Extracted: {len(unique_relationships)} unique relationships")

        # Validate and store relationships
        if not dry_run:
            with console.status("  Validating and storing..."):
                for rel in unique_relationships:
                    # Validate
                    is_valid, reason = validate_relationship(rel, valid_entities)

                    if not is_valid:
                        console.print(f"  [yellow]Rejected:[/] {rel.source} -{rel.relation_type}-> {rel.target} ({reason})")
                        stats["relationships_rejected"] += 1
                        continue

                    # Count high confidence
                    if rel.confidence >= 0.8:
                        stats["high_confidence"] += 1

                    # Store in Neo4j
                    kg.add_typed_relationship(
                        source_name=rel.source,
                        target_name=rel.target,
                        relation_type=rel.relation_type,
                        evidence=rel.evidence,
                        confidence=rel.confidence,
                        source_book=book.calibre_id,
                        source_chunk=rel.chunk_id
                    )
                    stats["relationships_stored"] += 1

            # Update book status
            kg.update_book_status(book.calibre_id, "relationships_mapped")
            console.print(f"  [green]Stored {stats['relationships_stored']} relationships[/]")
            console.print(f"  [green]High confidence: {stats['high_confidence']}[/]")
        else:
            console.print(f"  [yellow]DRY RUN: Would store {len(unique_relationships)} relationships[/]")
            # Count high confidence for dry run
            stats["high_confidence"] = sum(1 for r in unique_relationships if r.confidence >= 0.8)

        console.print("  [green]Done![/]")

    except Exception as e:
        console.print(f"  [bold red]Error:[/] {e}")
        stats["status"] = f"error: {str(e)[:50]}"

    return stats


def show_status(kg: UnifiedGraphClient):
    """Show Pass 2 processing status."""
    with kg.driver.session() as session:
        # Books by status
        result = session.run("""
            MATCH (b:Book)
            WHERE b.processing_status IN ['entities_extracted', 'relationships_mapped', 'enriched']
            RETURN b.processing_status as status, count(b) as count
            ORDER BY
                CASE b.processing_status
                    WHEN 'entities_extracted' THEN 1
                    WHEN 'relationships_mapped' THEN 2
                    WHEN 'enriched' THEN 3
                END
        """)

        table = Table(title="Pass 2 Processing Status")
        table.add_column("Status", style="cyan")
        table.add_column("Count", justify="right")
        table.add_column("Description")

        status_descriptions = {
            "entities_extracted": "Ready for Pass 2",
            "relationships_mapped": "Pass 2 complete",
            "enriched": "Pass 3 complete"
        }

        total = 0
        for record in result:
            status = record["status"]
            count = record["count"]
            total += count
            table.add_row(
                status,
                str(count),
                status_descriptions.get(status, "")
            )

        table.add_row("[bold]Total[/]", f"[bold]{total}[/]", "")
        console.print(table)

        # Relationship statistics
        result = session.run("""
            MATCH ()-[r]-()
            WHERE r.extracted_by = 'pass2'
            WITH type(r) as rel_type, count(r) as count, avg(r.confidence) as avg_conf
            RETURN rel_type, count, avg_conf
            ORDER BY count DESC
        """)

        records = list(result)

        table = Table(title="Pass 2 Relationships")
        table.add_column("Type", style="cyan")
        table.add_column("Count", justify="right")
        table.add_column("Avg Confidence", justify="right")

        if records:
            for record in records:
                table.add_row(
                    record["rel_type"],
                    str(record["count"]),
                    f"{record['avg_conf']:.2f}"
                )
        else:
            console.print("\n[yellow]No Pass 2 relationships found yet[/]")

        if records:
            console.print(table)

        # Books with relationship stats (only if there are completed books)
        result = session.run("""
            MATCH (b:Book {processing_status: 'relationships_mapped'})
            OPTIONAL MATCH (b)-[:MENTIONS]->(e)
            WITH b, count(DISTINCT e) as entity_count
            OPTIONAL MATCH ()-[r]->()
            WHERE r.source_book = b.calibre_id AND r.extracted_by = 'pass2'
            WITH b, entity_count,
                 count(r) as relationship_count,
                 avg(r.confidence) as avg_confidence
            WHERE relationship_count > 0
            RETURN
                b.title,
                b.author,
                entity_count,
                relationship_count,
                round(avg_confidence * 100) as avg_confidence_pct,
                round(relationship_count * 1.0 / CASE WHEN entity_count > 0 THEN entity_count ELSE 1 END, 2) as rels_per_entity
            ORDER BY relationship_count DESC
            LIMIT 20
        """)

        book_records = list(result)

        if book_records:
            table = Table(title="Top Books by Relationships")
            table.add_column("Title", style="cyan", max_width=40)
            table.add_column("Author", max_width=20)
            table.add_column("Entities", justify="right")
            table.add_column("Rels", justify="right")
            table.add_column("Avg Conf %", justify="right")
            table.add_column("Rels/Entity", justify="right")

            for record in book_records:
                table.add_row(
                    record["title"][:40],
                    (record["author"] or "Unknown")[:20],
                    str(record["entity_count"]),
                    str(record["relationship_count"]),
                    str(record["avg_confidence_pct"]),
                    f"{record['rels_per_entity']:.2f}"
                )

            console.print(table)


def main():
    parser = argparse.ArgumentParser(description="Pass 2: Extract relationships from Calibre books")
    parser.add_argument("--id", type=int, help="Process single book by calibre_id")
    parser.add_argument("--limit", type=int, help="Limit number of books to process")
    parser.add_argument("--status", action="store_true", help="Show processing status")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to Neo4j")

    args = parser.parse_args()

    kg = UnifiedGraphClient()

    if args.status:
        show_status(kg)
        return

    # Get books ready for Pass 2
    if args.id:
        books = get_books_for_pass2(kg, calibre_id=args.id)
    else:
        books = get_books_for_pass2(kg, limit=args.limit)

    if not books:
        console.print("[yellow]No books ready for Pass 2 (need status='entities_extracted')[/]")
        return

    console.print(f"\n[bold green]Found {len(books)} books ready for Pass 2[/]\n")

    if args.dry_run:
        console.print("[bold yellow]DRY RUN MODE - No changes will be written to Neo4j[/]\n")

    # Initialize extractor
    extractor = RelationshipExtractor(model="gpt-4o-mini", confidence_threshold=0.5)

    # Process books
    results = []
    for book in books:
        result = pass2_single_book(book, kg, extractor, dry_run=args.dry_run)
        results.append(result)

    # Summary
    console.print("\n" + "=" * 60)
    console.print("[bold green]Pass 2 Complete[/]")

    success = sum(1 for r in results if r["status"] == "success")
    no_chunks = sum(1 for r in results if r["status"] == "no_chunks")
    errors = sum(1 for r in results if r["status"].startswith("error"))

    console.print(f"  Processed: {success} books")
    console.print(f"  No chunks: {no_chunks} books")
    console.print(f"  Errors: {errors} books")
    console.print(f"  Total relationships extracted: {sum(r['relationships_extracted'] for r in results)}")
    console.print(f"  Total relationships stored: {sum(r['relationships_stored'] for r in results)}")
    console.print(f"  High confidence (>=0.8): {sum(r['high_confidence'] for r in results)}")
    console.print(f"  Rejected: {sum(r['relationships_rejected'] for r in results)}")


if __name__ == "__main__":
    main()
