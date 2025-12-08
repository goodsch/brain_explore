"""Books API router for Calibre library access.

Provides endpoints to list and get books from the Calibre library,
including ingestion queue management.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from ies_backend.schemas.calibre import Book
from ies_backend.services.calibre_service import CalibreService
from ies_backend.services.graph_service import GraphService


# Calibre library path - configurable via environment in production
# Use absolute path to project's calibre library
CALIBRE_LIBRARY_PATH = Path("/home/chris/dev/projects/codex/brain_explore/calibre/library")

# Ingestion queue storage (simple JSON file for now)
INGESTION_QUEUE_PATH = Path("/home/chris/dev/projects/codex/brain_explore/data/ingestion_queue.json")


def get_calibre_service() -> CalibreService:
    """Get CalibreService instance with configured library path."""
    return CalibreService(library_path=CALIBRE_LIBRARY_PATH)


class BooksListResponse(BaseModel):
    """Response for listing books."""

    books: list[Book]
    total: int


class IngestionQueueItem(BaseModel):
    """A book queued for ingestion."""

    calibre_id: int
    title: str
    author: str
    queued_at: datetime
    status: Literal["queued", "processing", "completed", "failed"]


class IngestionQueueResponse(BaseModel):
    """Response for ingestion queue listing."""

    items: list[IngestionQueueItem]
    total: int


class QueueIngestionResponse(BaseModel):
    """Response when queuing a book for ingestion."""

    calibre_id: int
    message: str
    queued_at: datetime


def _load_ingestion_queue() -> dict:
    """Load ingestion queue from JSON file."""
    if not INGESTION_QUEUE_PATH.exists():
        return {"items": {}}
    try:
        with open(INGESTION_QUEUE_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"items": {}}


def _save_ingestion_queue(queue: dict) -> None:
    """Save ingestion queue to JSON file."""
    INGESTION_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(INGESTION_QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2, default=str)


router = APIRouter()


@router.get("/books", response_model=BooksListResponse)
async def list_books(
    search: str | None = Query(default=None, description="Search by title or author"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum books to return"),
) -> BooksListResponse:
    """List books from the Calibre library.

    Returns books sorted by title. Optionally filter by search term.
    Books are enriched with entity counts from the knowledge graph.
    """
    service = get_calibre_service()
    books = service.list_books(search=search, limit=limit)

    # Get entity counts from Neo4j graph
    entity_counts = await GraphService.get_all_book_entity_counts()

    # Enrich books with entity counts
    enriched_books = []
    for book in books:
        entity_count = entity_counts.get(book.calibre_id, 0)
        enriched_book = Book(
            calibre_id=book.calibre_id,
            title=book.title,
            author=book.author,
            path=book.path,
            entity_count=entity_count,
            indexed=entity_count > 0,
        )
        enriched_books.append(enriched_book)

    return BooksListResponse(books=enriched_books, total=len(enriched_books))


@router.get("/books/ingestion-queue", response_model=IngestionQueueResponse)
async def get_ingestion_queue() -> IngestionQueueResponse:
    """Get the current ingestion queue status.

    Returns all books queued for ingestion with their current status.
    """
    queue = _load_ingestion_queue()

    # Handle both list format (current) and dict format (legacy)
    if isinstance(queue, list):
        raw_items = queue
    else:
        raw_items = list(queue.get("items", {}).values())

    items = [
        IngestionQueueItem(
            calibre_id=int(item["calibre_id"]),
            title=item["title"],
            author=item["author"],
            queued_at=datetime.fromisoformat(item["queued_at"]),
            status=item["status"],
        )
        for item in raw_items
    ]

    # Sort by queued_at descending (newest first)
    items.sort(key=lambda x: x.queued_at, reverse=True)

    return IngestionQueueResponse(items=items, total=len(items))


class ProcessQueueResponse(BaseModel):
    """Response for queue processing trigger."""

    message: str
    books_to_process: int
    status: Literal["started", "empty", "already_running"]


# Simple lock to prevent concurrent processing
_processing_lock = False


@router.post("/books/process-queue", response_model=ProcessQueueResponse)
async def process_queue() -> ProcessQueueResponse:
    """Trigger processing of queued books.

    This endpoint starts background processing of all queued books.
    Each book goes through:
    - Pass 1: Entity extraction
    - Pass 2: Relationship mapping

    Note: This is a fire-and-forget trigger. Check queue status for progress.
    """
    global _processing_lock

    if _processing_lock:
        return ProcessQueueResponse(
            message="Processing already in progress",
            books_to_process=0,
            status="already_running",
        )

    queue = _load_ingestion_queue()

    # Handle both formats
    if isinstance(queue, list):
        items = [item for item in queue if item.get("status") == "queued"]
    else:
        items = [
            item
            for item in queue.get("items", {}).values()
            if item.get("status") == "queued"
        ]

    if not items:
        return ProcessQueueResponse(
            message="No books queued for processing",
            books_to_process=0,
            status="empty",
        )

    # Start background processing
    import asyncio
    asyncio.create_task(_process_queue_background(items))

    return ProcessQueueResponse(
        message=f"Started processing {len(items)} books",
        books_to_process=len(items),
        status="started",
    )


@router.get("/books/{calibre_id}", response_model=Book)
async def get_book(calibre_id: int) -> Book:
    """Get a single book by its Calibre ID."""
    service = get_calibre_service()
    book = service.get_book(calibre_id=calibre_id)

    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with ID {calibre_id} not found")

    # Get entity count from Neo4j
    try:
        entities = await GraphService.get_entities_by_calibre_id(calibre_id)
        entity_count = len(entities)
    except Exception:
        entity_count = 0

    return Book(
        calibre_id=book.calibre_id,
        title=book.title,
        author=book.author,
        path=book.path,
        entity_count=entity_count,
        indexed=entity_count > 0,
    )


@router.get("/books/{calibre_id}/cover")
async def get_book_cover(calibre_id: int) -> FileResponse:
    """Get the cover image for a book.

    Returns the cover.jpg file from the book's folder.
    """
    service = get_calibre_service()
    cover_path = service.get_cover_path(calibre_id=calibre_id)

    if cover_path is None:
        raise HTTPException(status_code=404, detail=f"Cover not found for book {calibre_id}")

    return FileResponse(cover_path, media_type="image/jpeg")


@router.head("/books/{calibre_id}/file")
async def head_book_file(calibre_id: int) -> Response:
    """Get file metadata (HEAD request) for a book file.

    Returns Content-Length and Content-Type headers without the file body.
    Used by clients to determine file size before downloading.
    """
    service = get_calibre_service()
    file_path = service.get_book_file_path(calibre_id=calibre_id)

    if file_path is None:
        raise HTTPException(status_code=404, detail=f"Book file not found for book {calibre_id}")

    # Determine media type based on extension
    media_type = "application/epub+zip" if file_path.suffix.lower() == ".epub" else "application/pdf"
    file_size = file_path.stat().st_size

    return Response(
        content=None,
        headers={
            "Content-Length": str(file_size),
            "Content-Type": media_type,
        },
    )


@router.get("/books/{calibre_id}/file")
async def get_book_file(calibre_id: int) -> StreamingResponse:
    """Get the book file (epub or pdf) for a book.

    Returns the epub file if available, otherwise pdf.
    Served WITHOUT Content-Disposition header so epubjs can read it inline.
    """
    service = get_calibre_service()
    file_path = service.get_book_file_path(calibre_id=calibre_id)

    if file_path is None:
        raise HTTPException(status_code=404, detail=f"Book file not found for book {calibre_id}")

    # Determine media type based on extension
    media_type = "application/epub+zip" if file_path.suffix.lower() == ".epub" else "application/pdf"

    # Use StreamingResponse to avoid Content-Disposition header
    # which interferes with epubjs reading the file inline
    def file_iterator():
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):  # 64KB chunks
                yield chunk

    return StreamingResponse(
        file_iterator(),
        media_type=media_type,
        headers={"Content-Length": str(file_path.stat().st_size)},
    )


# === Ingestion Queue Endpoints ===


@router.post("/books/{calibre_id}/queue-ingest", response_model=QueueIngestionResponse)
async def queue_book_for_ingestion(calibre_id: int) -> QueueIngestionResponse:
    """Queue a book for entity extraction/ingestion.

    Adds the book to the ingestion queue for background processing.
    """
    service = get_calibre_service()
    book = service.get_book(calibre_id=calibre_id)

    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with ID {calibre_id} not found")

    # Load queue and add book
    queue = _load_ingestion_queue()
    now = datetime.utcnow()

    queue["items"][str(calibre_id)] = {
        "calibre_id": calibre_id,
        "title": book.title,
        "author": book.author,
        "queued_at": now.isoformat(),
        "status": "queued",
    }

    _save_ingestion_queue(queue)

    return QueueIngestionResponse(
        calibre_id=calibre_id,
        message=f"Book '{book.title}' queued for ingestion",
        queued_at=now,
    )


@router.delete("/books/{calibre_id}/queue-ingest")
async def remove_from_queue(calibre_id: int) -> dict:
    """Remove a book from the ingestion queue."""
    queue = _load_ingestion_queue()

    # Handle both list format (current) and dict format (legacy)
    if isinstance(queue, list):
        original_len = len(queue)
        queue = [item for item in queue if item["calibre_id"] != calibre_id]
        if len(queue) == original_len:
            raise HTTPException(status_code=404, detail=f"Book {calibre_id} not in queue")
        _save_ingestion_queue(queue)
    else:
        if str(calibre_id) not in queue.get("items", {}):
            raise HTTPException(status_code=404, detail=f"Book {calibre_id} not in queue")
        del queue["items"][str(calibre_id)]
        _save_ingestion_queue(queue)

    return {"message": f"Book {calibre_id} removed from queue"}


async def _process_queue_background(items: list[dict]) -> None:
    """Background task to process queued books."""
    global _processing_lock
    _processing_lock = True

    try:
        import subprocess
        import sys

        for item in items:
            calibre_id = item["calibre_id"]

            # Update status to processing
            _update_queue_item_status(calibre_id, "processing")

            try:
                # Run the daemon script for this specific book
                # Using subprocess to avoid import issues with library modules
                result = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        f"""
import sys
sys.path.insert(0, '/home/chris/dev/projects/codex/brain_explore')
from scripts.auto_ingest_daemon import process_single_book, CalibreBook
from library.graph.neo4j_client import KnowledgeGraph

kg = KnowledgeGraph()

# Get book info from Calibre
import sqlite3
from pathlib import Path

CALIBRE_DB = Path('/home/chris/dev/projects/codex/brain_explore/calibre/library/metadata.db')
CALIBRE_LIBRARY = Path('/home/chris/dev/projects/codex/brain_explore/calibre/library')

with sqlite3.connect(CALIBRE_DB) as conn:
    cursor = conn.execute(
        "SELECT id, title, author_sort, path FROM books WHERE id = ?",
        ({calibre_id},)
    )
    row = cursor.fetchone()
    if row:
        book_id, title, author, book_path = row
        book_dir = CALIBRE_LIBRARY / book_path
        epub_files = list(book_dir.glob("*.epub"))
        pdf_files = list(book_dir.glob("*.pdf"))

        if epub_files:
            file_path = str(epub_files[0])
        elif pdf_files:
            file_path = str(pdf_files[0])
        else:
            print("No readable file found")
            sys.exit(1)

        book = CalibreBook(
            calibre_id=book_id,
            title=title,
            author=author or "Unknown",
            path=file_path
        )

        if process_single_book(kg, book):
            print("SUCCESS")
        else:
            print("FAILED")
    else:
        print("Book not found in Calibre")
        sys.exit(1)
""",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout per book
                )

                if "SUCCESS" in result.stdout:
                    _update_queue_item_status(calibre_id, "completed")
                else:
                    _update_queue_item_status(calibre_id, "failed")
                    print(f"Processing failed for {calibre_id}: {result.stderr}")

            except subprocess.TimeoutExpired:
                _update_queue_item_status(calibre_id, "failed")
                print(f"Timeout processing book {calibre_id}")
            except Exception as e:
                _update_queue_item_status(calibre_id, "failed")
                print(f"Error processing book {calibre_id}: {e}")

    finally:
        _processing_lock = False


def _update_queue_item_status(calibre_id: int, status: str) -> None:
    """Update the status of a queue item."""
    queue = _load_ingestion_queue()

    if isinstance(queue, list):
        for item in queue:
            if item["calibre_id"] == calibre_id:
                item["status"] = status
                break
    else:
        if str(calibre_id) in queue.get("items", {}):
            queue["items"][str(calibre_id)]["status"] = status

    _save_ingestion_queue(queue)
