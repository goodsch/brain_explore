"""Book entities API router for entity overlay feature.

Provides endpoint to get all entities mentioned in a specific book.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ies_backend.services.graph_service import GraphService


class BookEntity(BaseModel):
    """An entity mentioned in a book."""
    name: str
    type: str
    mention_count: int


class BookEntitiesResponse(BaseModel):
    """Response for book entities endpoint."""
    book_hash: str
    entities: list[BookEntity]
    total: int


router = APIRouter()


@router.get("/entities/by-book/{book_hash}", response_model=BookEntitiesResponse)
async def get_book_entities(
    book_hash: str,
    title: str | None = Query(default=None, description="Book title for fallback matching"),
    types: list[str] | None = Query(default=None, description="Filter by entity types"),
    limit: int = Query(default=500, ge=1, le=1000, description="Maximum entities"),
) -> BookEntitiesResponse:
    """Get all entities mentioned in a book.

    Use this to populate entity overlay highlighting in the reader.
    Returns entities sorted by mention frequency.
    Tries matching by hash first, then falls back to title if provided.
    """
    entities = await GraphService.get_entities_by_book(
        book_hash, title=title, types=types, limit=limit
    )

    return BookEntitiesResponse(
        book_hash=book_hash,
        entities=[BookEntity(**e) for e in entities],
        total=len(entities),
    )
