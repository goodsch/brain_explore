#!/usr/bin/env python3
"""
Enrich Chunk→Entity MENTIONS relationships for evidence retrieval.

Pass 2 (Evidence Linking):
- For books with entities_extracted status
- Create Chunk nodes with content and metadata
- Create Chunk-[:MENTIONS]->Entity relationships
- Create Chunk-[:FROM_BOOK]->Book relationships

This enables the evidence API to return actual text passages
rather than just book-level mentions.

Usage:
    python scripts/enrich_chunk_evidence.py                # Process all eligible books
    python scripts/enrich_chunk_evidence.py --id 42        # Process single book by calibre_id
    python scripts/enrich_chunk_evidence.py --status       # Show processing stats
    python scripts/enrich_chunk_evidence.py --limit 5      # Process N books
"""

import argparse
import re
import sqlite3
import sys
import uuid
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

# Add library to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from library.ingest.extract import extract_document
from library.ingest.chunk import chunk_document
from library.graph.neo4j_client import KnowledgeGraph

console = Console()

# Configuration
CALIBRE_DB = Path("./calibre/library/metadata.db")
CALIBRE_LIBRARY = Path("./calibre/library")


def get_books_for_enrichment(kg: KnowledgeGraph, limit: int | None = None, calibre_id: int | None = None) -> list[dict]:
    """Get books that have entities but no chunk evidence yet."""
    with kg.driver.session() as session:
        if calibre_id:
            # Single book
            result = session.run("""
                MATCH (b:Book {calibre_id: $calibre_id})
                WHERE b.processing_status = 'entities_extracted'
                RETURN b.calibre_id as calibre_id, b.title as title,
                       b.author as author, b.path as path
            """, calibre_id=calibre_id)
        else:
            # Books with entities but no chunks yet
            query = """
                MATCH (b:Book)
                WHERE b.processing_status = 'entities_extracted'
                  AND NOT exists { MATCH (c:Chunk)-[:FROM_BOOK]->(b) }
                RETURN b.calibre_id as calibre_id, b.title as title,
                       b.author as author, b.path as path
                ORDER BY b.title
            """
            if limit:
                query += f" LIMIT {limit}"
            result = session.run(query)

        return [dict(record) for record in result]


def get_book_entities(kg: KnowledgeGraph, calibre_id: int) -> list[str]:
    """Get entity names for a book."""
    with kg.driver.session() as session:
        result = session.run("""
            MATCH (b:Book {calibre_id: $calibre_id})-[:MENTIONS]->(e)
            RETURN e.name as name
        """, calibre_id=calibre_id)
        return [record["name"] for record in result]


def get_entity_search_terms(entity_name: str) -> list[str]:
    """Generate search terms for an entity (handles partial names, abbreviations)."""
    terms = [entity_name.lower()]

    # For multi-word names, add the last word (e.g., "Skinner" from "B. F. Skinner")
    words = entity_name.split()
    if len(words) > 1:
        # Add last name alone (for persons)
        last_word = words[-1].lower()
        if len(last_word) >= 4:  # Only if last word is substantial
            terms.append(last_word)

        # Also try without periods (B. F. Skinner → BF Skinner → Skinner)
        no_periods = entity_name.replace(".", "").lower()
        if no_periods != entity_name.lower():
            terms.append(no_periods)

    # For hyphenated terms, also search without hyphens
    if "-" in entity_name:
        terms.append(entity_name.replace("-", " ").lower())
        terms.append(entity_name.replace("-", "").lower())

    return list(set(terms))  # Dedupe


def entity_in_text(entity_name: str, text_lower: str) -> bool:
    """Check if entity appears in text with flexible matching."""
    search_terms = get_entity_search_terms(entity_name)

    for term in search_terms:
        # Use word boundary matching for short terms to avoid false positives
        if len(term) < 6:
            # Require word boundaries for short terms
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text_lower):
                return True
        else:
            # Substring match OK for longer terms
            if term in text_lower:
                return True

    return False


def create_chunk_evidence(kg: KnowledgeGraph, calibre_id: int, chunks: list, entity_names: set[str]) -> dict:
    """Create Chunk nodes and link to entities found in them."""
    stats = {"chunks_created": 0, "mentions_created": 0}

    with kg.driver.session() as session:
        for i, chunk in enumerate(chunks):
            chunk_id = f"chunk_{calibre_id}_{i}"
            # Get text content from chunk - different chunk types have different attributes
            if hasattr(chunk, 'content'):
                content = chunk.content
            elif hasattr(chunk, 'text'):
                content = chunk.text
            else:
                content = str(chunk)  # Last resort fallback
            content_lower = content.lower()

            # Find which entities are mentioned in this chunk
            mentioned_entities = []
            for entity_name in entity_names:
                if entity_in_text(entity_name, content_lower):
                    mentioned_entities.append(entity_name)

            if not mentioned_entities:
                continue  # Skip chunks with no entity mentions

            # Create chunk node
            chapter = getattr(chunk, 'chapter', None) or getattr(chunk, 'source', None)

            session.run("""
                MERGE (c:Chunk {chunk_id: $chunk_id})
                SET c.content = $content,
                    c.chapter = $chapter,
                    c.created_at = datetime()
                WITH c
                MATCH (b:Book {calibre_id: $calibre_id})
                MERGE (c)-[:FROM_BOOK]->(b)
            """, chunk_id=chunk_id, content=content[:2000], chapter=chapter, calibre_id=calibre_id)

            stats["chunks_created"] += 1

            # Link chunk to entities
            for entity_name in mentioned_entities:
                session.run("""
                    MATCH (c:Chunk {chunk_id: $chunk_id})
                    MATCH (e) WHERE e.name = $entity_name
                    MERGE (c)-[:MENTIONS]->(e)
                """, chunk_id=chunk_id, entity_name=entity_name)
                stats["mentions_created"] += 1

    return stats


def enrich_book(kg: KnowledgeGraph, book: dict) -> dict:
    """Enrich a single book with chunk evidence."""
    calibre_id = book["calibre_id"]
    title = book["title"]
    path = book.get("path")

    stats = {
        "calibre_id": calibre_id,
        "title": title,
        "chunks_created": 0,
        "mentions_created": 0,
        "status": "success"
    }

    try:
        console.print(f"\n[bold blue]Enriching:[/] {title[:60]}")

        # Get existing entities for this book
        entity_names = set(get_book_entities(kg, calibre_id))
        if not entity_names:
            console.print("  [yellow]No entities found, skipping[/]")
            stats["status"] = "no_entities"
            return stats

        console.print(f"  Found {len(entity_names)} entities to link")

        # Find the book file
        if not path:
            # Look up from Calibre DB
            conn = sqlite3.connect(CALIBRE_DB)
            cursor = conn.execute(
                "SELECT path FROM books WHERE id = ?",
                (calibre_id,)
            )
            row = cursor.fetchone()
            conn.close()
            if not row:
                console.print("  [red]Book not found in Calibre[/]")
                stats["status"] = "not_found"
                return stats
            book_dir = CALIBRE_LIBRARY / row[0]
        else:
            book_dir = Path(path).parent

        # Find epub/pdf
        epub_files = list(book_dir.glob("*.epub")) if book_dir.exists() else []
        pdf_files = list(book_dir.glob("*.pdf")) if book_dir.exists() else []

        if epub_files:
            file_path = epub_files[0]
        elif pdf_files:
            file_path = pdf_files[0]
        else:
            console.print(f"  [red]No readable file found in {book_dir}[/]")
            stats["status"] = "no_file"
            return stats

        # Extract and chunk
        with console.status("  Extracting text..."):
            doc = extract_document(file_path)

        if not doc.sections:
            console.print("  [yellow]No sections found[/]")
            stats["status"] = "empty"
            return stats

        with console.status("  Chunking text..."):
            chunks = chunk_document(doc, max_tokens=512, overlap=50)

        console.print(f"  Created {len(chunks)} chunks")

        # Limit chunks to avoid massive graphs
        if len(chunks) > 100:
            console.print(f"  [yellow]Limiting to first 100 chunks (of {len(chunks)})[/]")
            chunks = chunks[:100]

        # Create chunk evidence
        with console.status("  Creating chunk evidence..."):
            chunk_stats = create_chunk_evidence(kg, calibre_id, chunks, entity_names)

        stats["chunks_created"] = chunk_stats["chunks_created"]
        stats["mentions_created"] = chunk_stats["mentions_created"]

        # Update book status
        with kg.driver.session() as session:
            session.run("""
                MATCH (b:Book {calibre_id: $calibre_id})
                SET b.processing_status = 'chunk_evidence_added',
                    b.chunk_count = $chunk_count
            """, calibre_id=calibre_id, chunk_count=stats["chunks_created"])

        console.print(f"  [green]Created {stats['chunks_created']} chunks with {stats['mentions_created']} entity mentions[/]")

    except Exception as e:
        console.print(f"  [bold red]Error:[/] {e}")
        stats["status"] = f"error: {str(e)[:50]}"

    return stats


def show_status(kg: KnowledgeGraph):
    """Show chunk evidence status."""
    with kg.driver.session() as session:
        # Books by status
        result = session.run("""
            MATCH (b:Book)
            RETURN b.processing_status as status, count(b) as count
            ORDER BY count DESC
        """)

        table = Table(title="Book Processing Status")
        table.add_column("Status", style="cyan")
        table.add_column("Count", justify="right")

        for record in result:
            status = record["status"] or "legacy"
            table.add_row(status, str(record["count"]))

        console.print(table)

        # Chunk stats
        result = session.run("""
            MATCH (c:Chunk)
            OPTIONAL MATCH (c)-[:MENTIONS]->(e)
            WITH count(DISTINCT c) as chunks, count(DISTINCT e) as entities_linked
            RETURN chunks, entities_linked
        """)
        record = result.single()

        if record:
            console.print(f"\n[bold]Chunk Evidence:[/]")
            console.print(f"  Total chunks: {record['chunks']}")
            console.print(f"  Unique entities with chunk evidence: {record['entities_linked']}")

        # Sample evidence
        result = session.run("""
            MATCH (c:Chunk)-[:MENTIONS]->(e)
            MATCH (c)-[:FROM_BOOK]->(b:Book)
            RETURN e.name as entity, b.title as book,
                   substring(c.content, 0, 100) as excerpt
            LIMIT 3
        """)

        console.print(f"\n[bold]Sample Evidence:[/]")
        for record in result:
            console.print(f"  [cyan]{record['entity']}[/] in '{record['book'][:30]}...'")
            console.print(f"    \"{record['excerpt']}...\"")


def main():
    parser = argparse.ArgumentParser(description="Enrich chunk evidence for entities")
    parser.add_argument("--id", type=int, help="Process single book by calibre_id")
    parser.add_argument("--status", action="store_true", help="Show processing stats")
    parser.add_argument("--limit", type=int, help="Limit number of books to process")
    args = parser.parse_args()

    kg = KnowledgeGraph()

    if args.status:
        show_status(kg)
        return

    # Get books to process
    books = get_books_for_enrichment(kg, limit=args.limit, calibre_id=args.id)

    if not books:
        console.print("[yellow]No books found for enrichment[/]")
        console.print("Books need processing_status='entities_extracted' and no existing chunks")
        return

    console.print(f"[bold]Found {len(books)} books to enrich[/]")

    # Process books
    all_stats = []
    for book in books:
        stats = enrich_book(kg, book)
        all_stats.append(stats)

    # Summary
    console.print("\n" + "=" * 60)
    table = Table(title="Enrichment Summary")
    table.add_column("Title", max_width=40)
    table.add_column("Chunks", justify="right")
    table.add_column("Mentions", justify="right")
    table.add_column("Status", style="cyan")

    total_chunks = 0
    total_mentions = 0
    for s in all_stats:
        table.add_row(
            s["title"][:40],
            str(s["chunks_created"]),
            str(s["mentions_created"]),
            s["status"]
        )
        total_chunks += s["chunks_created"]
        total_mentions += s["mentions_created"]

    table.add_row(
        "[bold]Total[/]",
        f"[bold]{total_chunks}[/]",
        f"[bold]{total_mentions}[/]",
        ""
    )
    console.print(table)


if __name__ == "__main__":
    main()
