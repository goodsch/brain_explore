#!/usr/bin/env python3
"""
Backfill evidence chunks from books for Sprint 2.

This script:
1. Gets all entities from the knowledge graph
2. For each entity, searches for mentions in ingested book text
3. Creates Chunk nodes with content and MENTIONS relationships

Usage:
    uv run python scripts/backfill_evidence.py --limit 50
    uv run python scripts/backfill_evidence.py --entity "ADHD"
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Iterator

from neo4j import GraphDatabase
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from library.ingest.extract import extract_document
from library.ingest.chunk import chunk_document

console = Console()

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "brainexplore"
BOOKS_DIR = Path("calibre/library")


def get_entities(driver, limit: int | None = None) -> list[dict]:
    """Get entities from the graph."""
    query = """
    MATCH (e)
    WHERE e.name IS NOT NULL
    AND (e:Concept OR e:Person OR e:Theory OR e:Framework OR e:Term)
    RETURN DISTINCT e.name as name, labels(e)[0] as type
    ORDER BY e.name
    """
    if limit:
        query += f" LIMIT {limit}"

    with driver.session() as session:
        result = session.run(query)
        return [{"name": r["name"], "type": r["type"]} for r in result]


def get_books(driver) -> list[dict]:
    """Get all books with their paths from the graph."""
    query = """
    MATCH (b:Book)
    WHERE b.path IS NOT NULL
    RETURN b.title as title, b.author as author, b.path as path, b.calibre_id as calibre_id
    """
    with driver.session() as session:
        result = session.run(query)
        return [dict(r) for r in result]


def find_mentions_in_text(text: str, entity_name: str, context_chars: int = 300) -> list[dict]:
    """Find mentions of an entity in text and extract context."""
    mentions = []
    # Case-insensitive search for the entity name
    pattern = re.compile(re.escape(entity_name), re.IGNORECASE)

    for match in pattern.finditer(text):
        start = max(0, match.start() - context_chars)
        end = min(len(text), match.end() + context_chars)

        # Expand to sentence boundaries if possible
        context = text[start:end]

        # Clean up partial sentences at start
        if start > 0:
            first_sentence_end = context.find('. ')
            if first_sentence_end > 0 and first_sentence_end < len(context) // 3:
                context = context[first_sentence_end + 2:]

        # Clean up partial sentences at end
        if end < len(text):
            last_sentence_end = context.rfind('. ')
            if last_sentence_end > len(context) * 2 // 3:
                context = context[:last_sentence_end + 1]

        mentions.append({
            "text": context.strip(),
            "position": match.start(),
        })

    return mentions


def create_evidence_chunk(
    driver,
    entity_name: str,
    book_path: str,
    book_title: str,
    book_author: str | None,
    chunk_text: str,
    chunk_index: int,
    chapter: str | None = None,
) -> bool:
    """Create a Chunk node and MENTIONS relationship."""
    chunk_id = f"evidence_{entity_name}_{hash(chunk_text) % 10000}_{chunk_index}"

    query = """
    // Create or update chunk
    MERGE (c:Chunk {chunk_id: $chunk_id})
    SET c.content = $content,
        c.source_file = $book_path,
        c.chapter = $chapter,
        c.created_at = datetime()

    // Link to book
    WITH c
    MATCH (b:Book {path: $book_path})
    MERGE (c)-[:FROM_BOOK]->(b)

    // Link to entity
    WITH c
    MATCH (e) WHERE e.name = $entity_name
    MERGE (c)-[:MENTIONS]->(e)

    RETURN c.chunk_id as id
    """

    try:
        with driver.session() as session:
            result = session.run(
                query,
                chunk_id=chunk_id,
                content=chunk_text[:2000],  # Limit chunk size
                book_path=book_path,
                chapter=chapter,
                entity_name=entity_name,
            )
            return bool(result.single())
    except Exception as e:
        console.print(f"[red]Error creating chunk: {e}[/red]")
        return False


def process_entity(driver, entity: dict, books: list[dict], max_chunks_per_book: int = 3) -> int:
    """Find and create evidence chunks for an entity."""
    chunks_created = 0
    entity_name = entity["name"]

    for book in books:
        book_path = book["path"]

        # Skip if book file doesn't exist
        if not Path(book_path).exists():
            continue

        try:
            # Extract document
            doc = extract_document(Path(book_path))
            full_text = "\n\n".join(s.content for s in doc.sections)

            # Find mentions
            mentions = find_mentions_in_text(full_text, entity_name)

            if not mentions:
                continue

            # Create chunks for top mentions (limit per book)
            for i, mention in enumerate(mentions[:max_chunks_per_book]):
                if create_evidence_chunk(
                    driver=driver,
                    entity_name=entity_name,
                    book_path=book_path,
                    book_title=book.get("title", "Unknown"),
                    book_author=book.get("author"),
                    chunk_text=mention["text"],
                    chunk_index=i,
                ):
                    chunks_created += 1

        except Exception as e:
            console.print(f"[yellow]Warning: Could not process {book_path}: {e}[/yellow]")
            continue

    return chunks_created


def main():
    parser = argparse.ArgumentParser(description="Backfill evidence chunks from books")
    parser.add_argument("--limit", type=int, help="Limit number of entities to process")
    parser.add_argument("--entity", type=str, help="Process single entity by name")
    parser.add_argument("--dry-run", action="store_true", help="Don't create chunks, just show what would be done")
    args = parser.parse_args()

    console.print("[bold blue]Sprint 2: Evidence Backfill[/bold blue]")
    console.print("Connecting to Neo4j...")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    try:
        # Get entities
        if args.entity:
            entities = [{"name": args.entity, "type": "Unknown"}]
        else:
            entities = get_entities(driver, args.limit)

        console.print(f"Found {len(entities)} entities to process")

        # Get books
        books = get_books(driver)
        console.print(f"Found {len(books)} books to search")

        if args.dry_run:
            console.print("[yellow]Dry run mode - no chunks will be created[/yellow]")
            return

        # Process entities
        total_chunks = 0
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing entities...", total=len(entities))

            for entity in entities:
                progress.update(task, description=f"Processing: {entity['name'][:30]}...")
                chunks = process_entity(driver, entity, books)
                total_chunks += chunks
                progress.advance(task)

        console.print(f"\n[bold green]Done![/bold green] Created {total_chunks} evidence chunks")

        # Show stats
        with driver.session() as session:
            result = session.run("""
                MATCH (c:Chunk)-[m:MENTIONS]->(e)
                RETURN count(DISTINCT c) as chunks, count(m) as mentions, count(DISTINCT e) as entities
            """)
            stats = result.single()
            console.print(f"Total chunks: {stats['chunks']}")
            console.print(f"Total MENTIONS relationships: {stats['mentions']}")
            console.print(f"Entities with evidence: {stats['entities']}")

    finally:
        driver.close()


if __name__ == "__main__":
    main()
