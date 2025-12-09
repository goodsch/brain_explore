"""API endpoints for reader highlights."""

from fastapi import APIRouter, HTTPException, Query

from ..schemas.highlight import (
    Highlight,
    HighlightCreate,
    HighlightUpdate,
    HighlightResponse,
    HighlightListResponse,
    HighlightBatchCreate,
    HighlightBatchResponse,
)
from ..services.highlight_service import HighlightService

router = APIRouter(prefix="/highlights", tags=["highlights"])


@router.post("", response_model=HighlightResponse)
async def create_highlight(data: HighlightCreate) -> HighlightResponse:
    """Create a new highlight.

    Creates a highlight from reader selection with CFI location.
    Highlight can be linked to a context/question for exploration tracking.
    """
    highlight = await HighlightService.create_highlight(data)
    return HighlightResponse(
        highlight=highlight,
        message="Highlight created",
        siyuan_synced=False,
    )


@router.get("/{highlight_id}", response_model=Highlight)
async def get_highlight(highlight_id: str) -> Highlight:
    """Get a highlight by ID."""
    highlight = await HighlightService.get_highlight(highlight_id)
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return highlight


@router.patch("/{highlight_id}", response_model=HighlightResponse)
async def update_highlight(
    highlight_id: str, data: HighlightUpdate
) -> HighlightResponse:
    """Update a highlight's note, color, or context."""
    highlight = await HighlightService.update_highlight(highlight_id, data)
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return HighlightResponse(
        highlight=highlight,
        message="Highlight updated",
        siyuan_synced=False,
    )


@router.delete("/{highlight_id}")
async def delete_highlight(highlight_id: str) -> dict:
    """Delete a highlight."""
    deleted = await HighlightService.delete_highlight(highlight_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return {"message": "Highlight deleted", "id": highlight_id}


@router.get("", response_model=HighlightListResponse)
async def list_highlights(
    book_id: str | None = Query(None, description="Filter by book (calibre ID)"),
    context_id: str | None = Query(None, description="Filter by context"),
    limit: int = Query(100, ge=1, le=500, description="Maximum results"),
) -> HighlightListResponse:
    """List highlights with optional filtering.

    Filter by book_id to get all highlights for a specific book.
    Filter by context_id to get highlights related to a specific exploration context.
    """
    highlights = await HighlightService.list_highlights(
        book_id=book_id,
        context_id=context_id,
        limit=limit,
    )
    return HighlightListResponse(
        highlights=highlights,
        total=len(highlights),
        book_id=book_id,
    )


@router.post("/sync", response_model=HighlightBatchResponse)
async def sync_highlights(data: HighlightBatchCreate) -> HighlightBatchResponse:
    """Sync multiple highlights from a book.

    Use this endpoint to batch sync highlights from the reader.
    Existing highlights (matched by CFI) will be updated.
    New highlights will be created.

    This is the primary endpoint for Reader -> Backend highlight sync.
    """
    result = await HighlightService.batch_sync(data)
    return HighlightBatchResponse(
        created=result["created"],
        updated=result["updated"],
        errors=result["errors"],
        message=f"Synced {result['created'] + result['updated']} highlights",
    )


@router.get("/book/{book_id}", response_model=HighlightListResponse)
async def get_book_highlights(
    book_id: str,
    limit: int = Query(100, ge=1, le=500),
) -> HighlightListResponse:
    """Get all highlights for a specific book.

    Convenience endpoint for fetching highlights by book.
    Returns highlights sorted by creation time (newest first).
    """
    highlights = await HighlightService.list_highlights(
        book_id=book_id,
        limit=limit,
    )
    return HighlightListResponse(
        highlights=highlights,
        total=len(highlights),
        book_id=book_id,
    )


@router.get("/unprocessed", response_model=list[Highlight])
async def get_unprocessed_highlights(
    limit: int = Query(50, ge=1, le=200),
) -> list[Highlight]:
    """Get highlights pending entity extraction.

    Used by background processing to find highlights that need
    entity extraction for evidence linking.
    """
    return await HighlightService.get_unprocessed_highlights(limit=limit)


@router.post("/{highlight_id}/process")
async def mark_highlight_processed(
    highlight_id: str,
    entity_refs: list[str],
) -> dict:
    """Mark a highlight as processed with extracted entities.

    Called after entity extraction to update highlight with found entities.
    """
    highlight = await HighlightService.mark_processed(highlight_id, entity_refs)
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return {
        "message": "Highlight processed",
        "id": highlight_id,
        "entity_count": len(entity_refs),
    }


@router.post("/{highlight_id}/sync-siyuan")
async def sync_highlight_to_siyuan(highlight_id: str) -> dict:
    """Sync a highlight to SiYuan Book Note.

    Creates the Book Note if it doesn't exist (auto-creation).
    Appends the highlight to the Book Note's Highlights section.

    Returns the SiYuan block ID if successful.
    """
    highlight = await HighlightService.get_highlight(highlight_id)
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")

    block_id = await HighlightService.sync_highlight_to_siyuan(highlight)
    if not block_id:
        raise HTTPException(
            status_code=500,
            detail="Failed to sync to SiYuan. Check SiYuan connection.",
        )

    return {
        "message": "Highlight synced to SiYuan",
        "id": highlight_id,
        "siyuan_block_id": block_id,
    }


@router.post("/book/{book_id}/sync-siyuan")
async def sync_book_highlights_to_siyuan(book_id: str) -> dict:
    """Sync all highlights for a book to SiYuan.

    Creates the Book Note if it doesn't exist.
    Syncs all un-synced highlights for this book.
    """
    highlights = await HighlightService.list_highlights(book_id=book_id)

    # Filter to un-synced highlights
    unsynced = [h for h in highlights if not h.siyuan_block_id]

    synced = 0
    errors = []

    for h in unsynced:
        try:
            block_id = await HighlightService.sync_highlight_to_siyuan(h)
            if block_id:
                synced += 1
        except Exception as e:
            errors.append(f"Failed to sync {h.id}: {str(e)[:50]}")

    return {
        "message": f"Synced {synced} highlights to SiYuan",
        "book_id": book_id,
        "synced": synced,
        "already_synced": len(highlights) - len(unsynced),
        "errors": errors,
    }
