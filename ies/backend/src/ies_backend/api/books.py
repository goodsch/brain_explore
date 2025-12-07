"""Books API router for Calibre library access.

Provides endpoints to list and get books from the Calibre library,
including ingestion queue management.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from ies_backend.schemas.calibre import Book
from ies_backend.services.calibre_service import CalibreService


# Calibre library path - configurable via environment in production
# Use absolute path to project's calibre library
CALIBRE_LIBRARY_PATH = Path("/home/chris/dev/projects/codex/brain_explore/calibre/library")

# Ingestion queue file - stores books queued for processing
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
    status: str  # 'queued', 'processing', 'completed', 'failed'


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
    """
    service = get_calibre_service()
    books = service.list_books(search=search, limit=limit)

    return BooksListResponse(books=books, total=len(books))


@router.get("/books/{calibre_id}", response_model=Book)
async def get_book(calibre_id: int) -> Book:
    """Get a single book by its Calibre ID."""
    service = get_calibre_service()
    book = service.get_book(calibre_id=calibre_id)

    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with ID {calibre_id} not found")

    return book


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


@router.get("/books/ingestion-queue", response_model=IngestionQueueResponse)
async def get_ingestion_queue() -> IngestionQueueResponse:
    """Get the current ingestion queue status.

    Returns all books queued for ingestion with their current status.
    """
    queue = _load_ingestion_queue()

    items = [
        IngestionQueueItem(
            calibre_id=int(item["calibre_id"]),
            title=item["title"],
            author=item["author"],
            queued_at=datetime.fromisoformat(item["queued_at"]),
            status=item["status"],
        )
        for item in queue.get("items", {}).values()
    ]

    # Sort by queued_at descending (newest first)
    items.sort(key=lambda x: x.queued_at, reverse=True)

    return IngestionQueueResponse(items=items, total=len(items))


@router.delete("/books/{calibre_id}/queue-ingest")
async def remove_from_queue(calibre_id: int) -> dict:
    """Remove a book from the ingestion queue."""
    queue = _load_ingestion_queue()

    if str(calibre_id) not in queue.get("items", {}):
        raise HTTPException(status_code=404, detail=f"Book {calibre_id} not in queue")

    del queue["items"][str(calibre_id)]
    _save_ingestion_queue(queue)

    return {"message": f"Book {calibre_id} removed from queue"}
