"""Books API router for Calibre library access.

Provides endpoints to list and get books from the Calibre library.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ies_backend.schemas.calibre import Book
from ies_backend.services.calibre_service import CalibreService


# Calibre library path - configurable via environment in production
# Use absolute path to project's calibre library
CALIBRE_LIBRARY_PATH = Path("/home/chris/dev/projects/codex/brain_explore/calibre/library")


def get_calibre_service() -> CalibreService:
    """Get CalibreService instance with configured library path."""
    return CalibreService(library_path=CALIBRE_LIBRARY_PATH)


class BooksListResponse(BaseModel):
    """Response for listing books."""

    books: list[Book]
    total: int


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
            "Content-Disposition": f'attachment; filename="{file_path.name}"',
        },
    )


@router.get("/books/{calibre_id}/file")
async def get_book_file(calibre_id: int) -> FileResponse:
    """Get the book file (epub or pdf) for a book.

    Returns the epub file if available, otherwise pdf.
    The file is served with Content-Disposition header for download.
    """
    service = get_calibre_service()
    file_path = service.get_book_file_path(calibre_id=calibre_id)

    if file_path is None:
        raise HTTPException(status_code=404, detail=f"Book file not found for book {calibre_id}")

    # Determine media type based on extension
    media_type = "application/epub+zip" if file_path.suffix.lower() == ".epub" else "application/pdf"

    return FileResponse(
        file_path,
        media_type=media_type,
        filename=file_path.name,
    )
