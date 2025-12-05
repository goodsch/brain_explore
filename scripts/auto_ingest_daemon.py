#!/usr/bin/env python3
"""
Automated Calibre book ingestion daemon.

Runs continuously in background:
1. Polls Calibre database every 5 minutes for new books
2. Processes unprocessed books automatically
3. Limits to 5 books per batch to avoid API overload
4. Logs all activity

Usage:
    python scripts/auto_ingest_daemon.py &  # Run in background
    python scripts/auto_ingest_daemon.py --once  # Run once and exit
"""

import argparse
import sqlite3
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

# Add library to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from library.graph.neo4j_client import KnowledgeGraph
from library.graph.entities import EntityExtractor

# Configuration
CALIBRE_DB = Path("./calibre/library/metadata.db")
CALIBRE_LIBRARY = Path("./calibre/library")
POLL_INTERVAL = 300  # 5 minutes
BATCH_SIZE = 5  # Process 5 books per batch
LOG_FILE = Path("logs/auto_ingest.log")

# Set up logging
LOG_FILE.parent.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class CalibreBook:
    """Book from Calibre library."""
    calibre_id: int
    title: str
    author: str
    path: str


def get_calibre_books(kg: KnowledgeGraph, limit: int = 10) -> list[CalibreBook]:
    """Get unprocessed books from Calibre database."""
    try:
        with sqlite3.connect(CALIBRE_DB) as conn:
            # Get books that don't exist in Neo4j or have no processing status
            query = """
                SELECT b.id, b.title, b.author_sort, b.path
                FROM books b
                ORDER BY b.title
                LIMIT ?
            """
            cursor = conn.execute(query, (limit * 3,))  # Get more to filter
            
            books = []
            for row in cursor.fetchall():
                book_id, title, author, book_path = row
                
                # Check if already processed
                if kg.book_exists(book_id):
                    continue
                
                # Find the actual file (epub preferred, then pdf)
                book_dir = CALIBRE_LIBRARY / book_path
                if not book_dir.exists():
                    continue
                    
                epub_files = list(book_dir.glob("*.epub"))
                pdf_files = list(book_dir.glob("*.pdf"))
                
                if epub_files:
                    file_path = str(epub_files[0])
                elif pdf_files:
                    file_path = str(pdf_files[0])
                else:
                    continue  # Skip if no readable format
                
                books.append(CalibreBook(
                    calibre_id=book_id,
                    title=title,
                    author=author or "Unknown",
                    path=file_path
                ))
                
                if len(books) >= limit:
                    break
            
            return books
            
    except Exception as e:
        logger.error(f"Failed to get Calibre books: {e}")
        return []


def process_single_book(kg: KnowledgeGraph, book: CalibreBook) -> bool:
    """Process a single book through the ingestion pipeline."""
    try:
        from library.ingest.extract import extract_document
        from library.ingest.chunk import chunk_document
        
        extractor = EntityExtractor()
        
        # Extract document text
        doc = extract_document(Path(book.path))
        
        # Chunk the document
        chunks = chunk_document(doc, max_tokens=512, overlap=50)
        
        # Limit chunks to avoid excessive API calls
        if len(chunks) > 50:
            chunks = chunks[:50]
            logger.warning(f"Limited {book.title} to 50 chunks (was {len(chunks)})")
        
        # Create book node
        kg.add_book(
            title=book.title,
            author=book.author,
            path=book.path,
            calibre_id=book.calibre_id,
            processing_status="chunked"
        )
        
        # Extract entities from chunks
        entities_found = 0
        for chunk in chunks:
            result = extractor.extract_from_chunk(chunk)
            
            for entity in result.entities:
                kg.add_entity(entity)
                entities_found += 1
                
                # Create MENTIONS relationship between book and entity
                with kg.driver.session() as session:
                    session.run("""
                        MATCH (b:Book {calibre_id: $calibre_id})
                        MATCH (e) WHERE e.name = $entity_name
                        MERGE (b)-[:MENTIONS]->(e)
                    """, calibre_id=book.calibre_id, entity_name=entity.name)
        
        # Update status
        kg.update_book_status(book.calibre_id, "entities_extracted")
        
        logger.info(f"Extracted {entities_found} entities from {book.title}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to process {book.title}: {e}")
        try:
            kg.update_book_status(book.calibre_id, "error")
        except:
            pass
        return False


def get_calibre_book_count():
    """Get total number of books in Calibre library."""
    try:
        with sqlite3.connect(CALIBRE_DB) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM books")
            return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Failed to get Calibre book count: {e}")
        return 0


def process_batch():
    """Process a batch of unprocessed books."""
    try:
        kg = KnowledgeGraph()
        unprocessed = get_calibre_books(kg, limit=BATCH_SIZE)
        
        if not unprocessed:
            logger.info("No unprocessed books found")
            return 0
            
        logger.info(f"Processing batch of {len(unprocessed)} books")
        
        processed_count = 0
        for book in unprocessed:
            try:
                logger.info(f"Processing: {book.title} by {book.author} (ID: {book.calibre_id})")
                if process_single_book(kg, book):
                    processed_count += 1
                    logger.info(f"Successfully processed book {book.calibre_id}")
                
                # Small delay between books to avoid API rate limits
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to process book {book.calibre_id}: {e}")
                continue
        
        logger.info(f"Batch complete: {processed_count}/{len(unprocessed)} books processed")
        return processed_count
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        return 0


def daemon_loop():
    """Main daemon loop."""
    logger.info("Starting auto-ingest daemon")
    logger.info(f"Polling every {POLL_INTERVAL} seconds, processing {BATCH_SIZE} books per batch")
    
    while True:
        try:
            start_time = datetime.now()
            
            # Check Calibre library size
            total_books = get_calibre_book_count()
            logger.info(f"Calibre library has {total_books} books")
            
            # Process a batch
            processed = process_batch()
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Batch completed in {duration:.1f}s")
            
            if processed > 0:
                logger.info(f"Processed {processed} books, waiting {POLL_INTERVAL}s for next batch")
            
            # Wait for next poll
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Daemon stopped by user")
            break
        except Exception as e:
            logger.error(f"Daemon error: {e}")
            logger.info(f"Retrying in {POLL_INTERVAL}s")
            time.sleep(POLL_INTERVAL)


def main():
    global BATCH_SIZE
    
    parser = argparse.ArgumentParser(description="Automated Calibre book ingestion")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help=f"Books per batch (default: {BATCH_SIZE})")
    
    args = parser.parse_args()
    BATCH_SIZE = args.batch_size
    
    if args.once:
        logger.info("Running single batch")
        processed = process_batch()
        logger.info(f"Single batch complete: {processed} books processed")
    else:
        daemon_loop()


if __name__ == "__main__":
    main()