"""Service for syncing highlights to SiYuan with block attributes."""

import logging
from datetime import datetime

from ..schemas.highlight import (
    Highlight,
    SyncResult,
    BatchSyncResult,
    SyncStatusResponse,
    SyncStatus,
)
from .siyuan_client import SiYuanClient
from .calibre_service import CalibreService
from .journey_logger import JourneyLogger

logger = logging.getLogger(__name__)

# In-memory storage references (shared with highlight_service)
from .highlight_service import _highlights, _book_note_ids


class HighlightSyncService:
    """Manages highlight synchronization to SiYuan with block attributes."""

    @staticmethod
    async def sync_highlight(highlight: Highlight) -> SyncResult:
        """Sync a single highlight to SiYuan with block attributes.

        Args:
            highlight: Highlight to sync

        Returns:
            SyncResult with success status and details
        """
        try:
            book_id = highlight.book_id

            # Check cache for existing book note
            doc_id = _book_note_ids.get(book_id)

            if not doc_id:
                # Try to find existing book note
                doc_id = await SiYuanClient.find_book_note_by_calibre_id(book_id)

            if not doc_id:
                # Need to create book note - fetch book info from Calibre
                try:
                    calibre = CalibreService()
                    book = calibre.get_book(int(book_id))
                    if book:
                        doc_id = await SiYuanClient.create_book_note(
                            calibre_id=book_id,
                            title=book.title,
                            author=book.author,
                        )
                    else:
                        # Fallback: create with minimal info
                        doc_id = await SiYuanClient.create_book_note(
                            calibre_id=book_id,
                            title=highlight.book_title or f"Book {book_id}",
                            author=highlight.book_author or "Unknown",
                        )
                except Exception as e:
                    logger.warning(f"Failed to get book info for {book_id}: {e}")
                    # Fallback: create with minimal info
                    doc_id = await SiYuanClient.create_book_note(
                        calibre_id=book_id,
                        title=highlight.book_title or f"Book {book_id}",
                        author=highlight.book_author or "Unknown",
                    )

            if not doc_id:
                error_msg = f"Could not create/find book note for {book_id}"
                logger.warning(error_msg)

                # Update highlight with error status
                highlight.sync_status = SyncStatus.ERROR
                highlight.sync_error = error_msg
                _highlights[highlight.id] = highlight

                return SyncResult(
                    highlight_id=highlight.id,
                    success=False,
                    error=error_msg,
                )

            # Cache the book note ID
            _book_note_ids[book_id] = doc_id

            # Append highlight to book note with full metadata
            block_id = await SiYuanClient.append_highlight_to_book_note(
                doc_id=doc_id,
                highlight_text=highlight.text,
                note=highlight.note,
                chapter=highlight.chapter,
                cfi=highlight.cfi,
                highlight_id=highlight.id,
                context_id=highlight.context_id,
                question_id=highlight.question_id,
                note_type=highlight.note_type.value if highlight.note_type else None,
            )

            if not block_id:
                error_msg = "Failed to create SiYuan block"
                logger.warning(f"{error_msg} for highlight {highlight.id}")

                # Update highlight with error status
                highlight.sync_status = SyncStatus.ERROR
                highlight.sync_error = error_msg
                _highlights[highlight.id] = highlight

                return SyncResult(
                    highlight_id=highlight.id,
                    success=False,
                    error=error_msg,
                )

            # Update highlight with sync success
            highlight.siyuan_block_id = block_id
            highlight.sync_status = SyncStatus.SYNCED
            highlight.sync_error = None
            highlight.synced_at = datetime.utcnow()
            _highlights[highlight.id] = highlight

            logger.info(
                f"Synced highlight {highlight.id} to SiYuan block {block_id}"
            )

            # Log to journey if context is available
            if highlight.context_id:
                await JourneyLogger.log_highlight_created(
                    context_id=highlight.context_id,
                    highlight_text=highlight.text,
                    book_id=book_id,
                    question_id=highlight.question_id,
                )

            return SyncResult(
                highlight_id=highlight.id,
                success=True,
                siyuan_block_id=block_id,
            )

        except Exception as e:
            error_msg = f"Sync failed: {str(e)}"
            logger.warning(f"Failed to sync highlight {highlight.id}: {e}")

            # Update highlight with error status
            highlight.sync_status = SyncStatus.ERROR
            highlight.sync_error = error_msg
            _highlights[highlight.id] = highlight

            return SyncResult(
                highlight_id=highlight.id,
                success=False,
                error=error_msg,
            )

    @staticmethod
    async def sync_book_highlights(book_id: str) -> BatchSyncResult:
        """Batch sync all pending highlights for a book.

        Args:
            book_id: Calibre book ID

        Returns:
            BatchSyncResult with sync statistics
        """
        from .highlight_service import HighlightService

        # Get all highlights for this book
        highlights = await HighlightService.list_highlights(book_id=book_id, limit=500)

        # Filter to pending or error highlights (retry errors)
        to_sync = [
            h
            for h in highlights
            if h.sync_status in [SyncStatus.PENDING, SyncStatus.ERROR]
        ]

        results = []
        synced = 0
        failed = 0

        for highlight in to_sync:
            result = await HighlightSyncService.sync_highlight(highlight)
            results.append(result)

            if result.success:
                synced += 1
            else:
                failed += 1

        logger.info(
            f"Batch sync for book {book_id}: {synced} synced, {failed} failed"
        )

        return BatchSyncResult(
            book_id=book_id,
            total=len(to_sync),
            synced=synced,
            failed=failed,
            results=results,
        )

    @staticmethod
    async def get_sync_status(book_id: str | None = None) -> SyncStatusResponse:
        """Get sync status summary.

        Args:
            book_id: Optional filter by book

        Returns:
            SyncStatusResponse with status counts
        """
        from .highlight_service import HighlightService

        # Get highlights (filtered by book if specified)
        highlights = await HighlightService.list_highlights(book_id=book_id, limit=1000)

        # Count by sync status
        synced = sum(1 for h in highlights if h.sync_status == SyncStatus.SYNCED)
        pending = sum(1 for h in highlights if h.sync_status == SyncStatus.PENDING)
        error = sum(1 for h in highlights if h.sync_status == SyncStatus.ERROR)
        modified = sum(1 for h in highlights if h.sync_status == SyncStatus.MODIFIED)

        return SyncStatusResponse(
            total_highlights=len(highlights),
            synced=synced,
            pending=pending,
            error=error,
            modified=modified,
            book_id=book_id,
        )
