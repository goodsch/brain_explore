#!/usr/bin/env python3
"""
Ingest books from Calibre library into Neo4j knowledge graph.

Pass 1 (Structure):
- Create Book nodes with calibre_id
- Extract text and chunk
- Extract entities via OpenAI
- Create MENTIONS relationships

Usage:
    python scripts/ingest_calibre.py                    # Process all books
    python scripts/ingest_calibre.py --id 42            # Process single book by calibre_id
    python scripts/ingest_calibre.py --test             # Test with one book
    python scripts/ingest_calibre.py --status           # Show processing stats
"""

import argparse
import json
import sqlite3
import sys
import textwrap
from pathlib import Path
from dataclasses import dataclass
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from openai import OpenAI

# Add library to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from library.ingest.extract import extract_document
from library.ingest.chunk import chunk_document
from library.graph.entities import EntityExtractor, deduplicate_entities
from library.graph.neo4j_client import KnowledgeGraph

console = Console()

# Configuration
CALIBRE_DB = Path("./calibre/library/metadata.db")
CALIBRE_LIBRARY = Path("./calibre/library")
PATTERN_TYPES = ["design", "narrative", "dynamic", "embodied", "identity", "mixed"]
PATTERN_CLASSIFIER_MODEL = "gpt-4o-mini"


@dataclass
class CalibreBook:
    """Book from Calibre library."""
    calibre_id: int
    title: str
    author: str
    path: str  # Full path to epub/pdf


@dataclass
class PatternClassification:
    """LLM-derived pattern type classification for a book."""
    pattern_type: str
    confidence: float
    rationale: str


PATTERN_PROMPT = """You classify books by the type of conceptual patterns they provide.

Return a JSON object:
{{
  "pattern_type": "design | narrative | dynamic | embodied | identity | mixed",
  "confidence": 0.0-1.0,
  "rationale": "one sentence on why"
}}

Pattern types:
- design: structural templates, pattern languages, system design guidance
- narrative: stories, reportage, case studies used to explain ideas
- dynamic: systems, timing, cycles, synchronization, feedback behavior
- embodied: sensorimotor/physical experience metaphors and body-based framing
- identity: self-concept, career/role identity, values and traits as patterns
- mixed: balanced blend of multiple categories or unclear dominant orientation

Use the metadata and text sample to decide. Prefer the dominant orientation a reader would use this book for.

Book:
- Title: {title}
- Author: {author}
- Metadata: {metadata}

Text sample (truncated):
\"\"\"{text_sample}\"\"\""""


class PatternTypeClassifier:
    """LLM helper to assign pattern_type to books."""

    def __init__(self, client: OpenAI | None = None, model: str = PATTERN_CLASSIFIER_MODEL):
        self.client = client or OpenAI()
        self.model = model

    def classify(self, title: str, author: str, metadata: str | None, text_sample: str | None) -> PatternClassification | None:
        """Return pattern classification or None on failure."""
        sample = (text_sample or "").strip()
        if not sample:
            sample = "No text available; rely on metadata only."

        prompt = PATTERN_PROMPT.format(
            title=title or "Unknown title",
            author=author or "Unknown author",
            metadata=metadata or "No additional metadata",
            text_sample=sample
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            pattern_type = (data.get("pattern_type") or "").strip().lower()

            if pattern_type not in PATTERN_TYPES:
                return None

            confidence = float(data.get("confidence", 0))
            rationale = str(data.get("rationale", "")).strip()
            return PatternClassification(pattern_type=pattern_type, confidence=confidence, rationale=rationale)
        except Exception as e:
            console.print(f"  [yellow]Pattern classification skipped:[/] {e}")
            return None


def _summarize_text_for_classification(text: str, max_chars: int = 2000) -> str:
    """Prepare a concise text sample for pattern classification."""
    clean_text = " ".join(text.split())
    if len(clean_text) <= max_chars:
        return clean_text
    return textwrap.shorten(clean_text, width=max_chars, placeholder="...")


def get_calibre_books(limit: int | None = None, calibre_id: int | None = None) -> list[CalibreBook]:
    """Get books from Calibre database."""
    conn = sqlite3.connect(CALIBRE_DB)

    if calibre_id:
        query = """
            SELECT b.id, b.title, b.author_sort, b.path
            FROM books b
            WHERE b.id = ?
        """
        cursor = conn.execute(query, (calibre_id,))
    else:
        query = """
            SELECT b.id, b.title, b.author_sort, b.path
            FROM books b
            ORDER BY b.title
        """
        if limit:
            query += f" LIMIT {limit}"
        cursor = conn.execute(query)

    books = []
    for row in cursor.fetchall():
        book_id, title, author, book_path = row

        # Find the actual file (epub preferred, then pdf)
        book_dir = CALIBRE_LIBRARY / book_path
        epub_files = list(book_dir.glob("*.epub"))
        pdf_files = list(book_dir.glob("*.pdf"))

        if epub_files:
            file_path = epub_files[0]
        elif pdf_files:
            file_path = pdf_files[0]
        else:
            continue  # Skip if no readable format

        books.append(CalibreBook(
            calibre_id=book_id,
            title=title,
            author=author or "Unknown",
            path=str(file_path)
        ))

    conn.close()
    return books


def ingest_book(book: CalibreBook, kg: KnowledgeGraph, extractor: EntityExtractor, classifier: PatternTypeClassifier | None = None) -> dict:
    """Ingest a single book - extract entities and store in Neo4j."""
    stats = {
        "calibre_id": book.calibre_id,
        "title": book.title,
        "sections": 0,
        "chunks": 0,
        "entities": 0,
        "relationships": 0,
        "status": "success",
        "pattern_type": None
    }

    try:
        # Check if already processed
        if kg.book_exists(book.calibre_id):
            console.print(f"  [yellow]Skipping (already exists):[/] {book.title[:50]}")
            stats["status"] = "skipped"
            return stats

        path = Path(book.path)
        console.print(f"\n[bold blue]Processing:[/] {book.title[:60]}")
        console.print(f"  Calibre ID: {book.calibre_id}, Author: {book.author[:40]}")

        # Create book node (status: pending)
        kg.add_book(
            title=book.title,
            author=book.author,
            path=book.path,
            calibre_id=book.calibre_id,
            processing_status="pending"
        )

        # Extract text
        with console.status("  Extracting text..."):
            doc = extract_document(path)
        stats["sections"] = len(doc.sections)
        console.print(f"  Extracted: {len(doc.sections)} sections")

        # Classify pattern type using a short text sample
        if classifier and doc.sections:
            sample_text = _summarize_text_for_classification(doc.full_text)
            classification = classifier.classify(
                title=doc.title or book.title,
                author=doc.author or book.author,
                metadata=f"Calibre path: {book.path}",
                text_sample=sample_text
            )
            if classification:
                stats["pattern_type"] = classification.pattern_type
                kg.update_book_pattern_type(
                    calibre_id=book.calibre_id,
                    pattern_type=classification.pattern_type,
                    confidence=classification.confidence,
                    rationale=classification.rationale
                )
                console.print(f"  Pattern type: [green]{classification.pattern_type}[/] (conf {classification.confidence:.2f})")
            else:
                console.print("  [yellow]Pattern type: unavailable[/]")

        if not doc.sections:
            console.print("  [yellow]No sections found, skipping[/]")
            kg.update_book_status(book.calibre_id, "empty")
            stats["status"] = "empty"
            return stats

        # Chunk
        with console.status("  Chunking text..."):
            chunks = chunk_document(doc, max_tokens=512, overlap=50)
        stats["chunks"] = len(chunks)
        console.print(f"  Created: {len(chunks)} chunks")

        # Limit chunks to avoid excessive API calls (first 50 for now)
        if len(chunks) > 50:
            console.print(f"  [yellow]Limiting to first 50 chunks (of {len(chunks)})[/]")
            chunks = chunks[:50]

        # Extract entities
        extraction_results = []
        all_relationships = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("  Extracting entities...", total=len(chunks))

            for result in extractor.extract_from_chunks(chunks):
                extraction_results.append(result)
                all_relationships.extend(result.relationships)
                progress.advance(task)

        # Deduplicate entities (returns dict of name -> Entity)
        unique_entities_dict = deduplicate_entities(extraction_results)
        unique_entities = list(unique_entities_dict.values())
        stats["entities"] = len(unique_entities)
        stats["relationships"] = len(all_relationships)

        console.print(f"  Found: {len(unique_entities)} unique entities, {len(all_relationships)} relationships")

        # Store in Neo4j
        with console.status("  Storing in Neo4j..."):
            for entity in unique_entities:
                kg.add_entity(entity)

            for rel in all_relationships:
                kg.add_relationship(rel)

            # Create MENTIONS relationships (book -> entity)
            for entity in unique_entities:
                # Link book directly to entity
                with kg.driver.session() as session:
                    session.run("""
                        MATCH (b:Book {calibre_id: $calibre_id})
                        MATCH (e) WHERE e.name = $entity_name
                        MERGE (b)-[:MENTIONS]->(e)
                    """, calibre_id=book.calibre_id, entity_name=entity.name)

        # Update status
        kg.update_book_status(book.calibre_id, "entities_extracted")
        console.print("  [green]Done![/]")

    except Exception as e:
        console.print(f"  [bold red]Error:[/] {e}")
        stats["status"] = f"error: {str(e)[:50]}"
        try:
            kg.update_book_status(book.calibre_id, "error")
        except:
            pass

    return stats


def show_status(kg: KnowledgeGraph):
    """Show ingestion status."""
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

        total = 0
        for record in result:
            status = record["status"] or "legacy"
            count = record["count"]
            total += count
            table.add_row(status, str(count))

        table.add_row("[bold]Total[/]", f"[bold]{total}[/]")
        console.print(table)

        # Entity counts
        result = session.run("""
            MATCH (b:Book {processing_status: 'entities_extracted'})-[:MENTIONS]->(e)
            RETURN labels(e)[0] as type, count(DISTINCT e) as count
            ORDER BY count DESC
        """)

        table = Table(title="Entities from Calibre Books")
        table.add_column("Type", style="cyan")
        table.add_column("Count", justify="right")

        for record in result:
            table.add_row(record["type"], str(record["count"]))

        console.print(table)

        # Pattern type classification counts
        result = session.run("""
            MATCH (b:Book)
            WHERE b.pattern_type IS NOT NULL
            RETURN b.pattern_type AS pattern_type, count(b) AS count
            ORDER BY count DESC
        """)

        pattern_table = Table(title="Pattern Type Coverage")
        pattern_table.add_column("Pattern Type", style="cyan")
        pattern_table.add_column("Count", justify="right")

        has_rows = False
        for record in result:
            has_rows = True
            pattern_table.add_row(record["pattern_type"], str(record["count"]))

        if has_rows:
            console.print(pattern_table)


def main():
    parser = argparse.ArgumentParser(description="Ingest Calibre books into Neo4j")
    parser.add_argument("--id", type=int, help="Process single book by calibre_id")
    parser.add_argument("--test", action="store_true", help="Test with one book only")
    parser.add_argument("--limit", type=int, help="Limit number of books to process")
    parser.add_argument("--status", action="store_true", help="Show processing status")

    args = parser.parse_args()

    kg = KnowledgeGraph()

    if args.status:
        show_status(kg)
        kg.close()
        return

    # Get books
    if args.id:
        books = get_calibre_books(calibre_id=args.id)
    elif args.test:
        books = get_calibre_books(limit=1)
    else:
        books = get_calibre_books(limit=args.limit)

    if not books:
        console.print("[yellow]No books found to process[/]")
        kg.close()
        return

    console.print(f"\n[bold green]Found {len(books)} books to process[/]\n")

    # Initialize extractor
    extractor = EntityExtractor()
    classifier = PatternTypeClassifier()

    # Process books
    results = []
    for book in books:
        result = ingest_book(book, kg, extractor, classifier)
        results.append(result)

    # Summary
    console.print("\n" + "=" * 60)
    console.print("[bold green]Ingestion Complete[/]")

    success = sum(1 for r in results if r["status"] == "success")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    errors = sum(1 for r in results if r["status"].startswith("error"))
    classified = sum(1 for r in results if r.get("pattern_type"))

    console.print(f"  Processed: {success} books")
    console.print(f"  Skipped: {skipped} books")
    console.print(f"  Errors: {errors} books")
    console.print(f"  Pattern types classified: {classified}")
    console.print(f"  Total entities: {sum(r['entities'] for r in results)}")
    console.print(f"  Total relationships: {sum(r['relationships'] for r in results)}")

    kg.close()


if __name__ == "__main__":
    main()
