"""API endpoints for highlight synchronization to SiYuan."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..schemas.highlight import (
    BatchSyncResult,
    SyncStatusResponse,
    SyncResult,
)
from ..services.highlight_sync_service import HighlightSyncService
from ..services.highlight_service import HighlightService

router = APIRouter(prefix="/highlight-sync", tags=["highlight-sync"])


class SyncTriggerRequest(BaseModel):
    """Request to trigger highlight sync."""

    highlight_ids: list[str] | None = None  # Specific highlights, or None for all pending
    book_id: str | None = None  # Sync all highlights for a book


class SyncTriggerResponse(BaseModel):
    """Response after triggering highlight sync."""

    message: str
    total: int
    synced: int
    failed: int
    results: list[SyncResult]


@router.post("/trigger", response_model=SyncTriggerResponse)
async def trigger_highlight_sync(
    request: SyncTriggerRequest,
) -> SyncTriggerResponse:
    """Trigger highlight synchronization to SiYuan.

    Can sync:
    - Specific highlights by ID
    - All highlights for a book
    - All pending highlights (if no filters specified)

    Each highlight is synced with block attributes for cross-app integration.
    """
    results = []
    synced = 0
    failed = 0

    if request.book_id:
        # Sync all highlights for a book
        batch_result = await HighlightSyncService.sync_book_highlights(request.book_id)
        return SyncTriggerResponse(
            message=f"Synced highlights for book {request.book_id}",
            total=batch_result.total,
            synced=batch_result.synced,
            failed=batch_result.failed,
            results=batch_result.results,
        )

    elif request.highlight_ids:
        # Sync specific highlights
        for highlight_id in request.highlight_ids:
            highlight = await HighlightService.get_highlight(highlight_id)
            if not highlight:
                results.append(
                    SyncResult(
                        highlight_id=highlight_id,
                        success=False,
                        error="Highlight not found",
                    )
                )
                failed += 1
                continue

            result = await HighlightSyncService.sync_highlight(highlight)
            results.append(result)
            if result.success:
                synced += 1
            else:
                failed += 1

        return SyncTriggerResponse(
            message=f"Synced {synced} of {len(request.highlight_ids)} highlights",
            total=len(request.highlight_ids),
            synced=synced,
            failed=failed,
            results=results,
        )

    else:
        # Sync all pending highlights (across all books)
        from ..schemas.highlight import SyncStatus

        all_highlights = await HighlightService.list_highlights(limit=1000)
        pending = [
            h
            for h in all_highlights
            if h.sync_status in [SyncStatus.PENDING, SyncStatus.ERROR]
        ]

        for highlight in pending:
            result = await HighlightSyncService.sync_highlight(highlight)
            results.append(result)
            if result.success:
                synced += 1
            else:
                failed += 1

        return SyncTriggerResponse(
            message=f"Synced {synced} of {len(pending)} pending highlights",
            total=len(pending),
            synced=synced,
            failed=failed,
            results=results,
        )


@router.get("/status", response_model=SyncStatusResponse)
async def get_sync_status(
    book_id: str | None = Query(None, description="Filter by book (calibre ID)"),
) -> SyncStatusResponse:
    """Get highlight synchronization status summary.

    Returns counts by sync status:
    - synced: Successfully synced to SiYuan
    - pending: Not yet synced
    - error: Failed to sync
    - modified: Synced but modified since last sync

    Optionally filter by book_id.
    """
    return await HighlightSyncService.get_sync_status(book_id=book_id)


@router.post("/book/{book_id}", response_model=BatchSyncResult)
async def sync_book_highlights(book_id: str) -> BatchSyncResult:
    """Sync all pending highlights for a specific book.

    Creates the Book Note in SiYuan if it doesn't exist.
    Syncs all highlights with PENDING or ERROR status.
    Sets block attributes for cross-app integration.
    """
    return await HighlightSyncService.sync_book_highlights(book_id)


@router.post("/{highlight_id}", response_model=SyncResult)
async def sync_single_highlight(highlight_id: str) -> SyncResult:
    """Sync a single highlight to SiYuan.

    Creates the Book Note if it doesn't exist.
    Sets block attributes with IES metadata (be_type, be_id, source-cfi, etc).
    Updates highlight sync status.
    """
    highlight = await HighlightService.get_highlight(highlight_id)
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")

    return await HighlightSyncService.sync_highlight(highlight)
