"""Service for managing reader highlights."""

import uuid
from datetime import datetime
import logging

from ..schemas.highlight import (
    Highlight,
    HighlightCreate,
    HighlightUpdate,
    HighlightBatchCreate,
)
from .siyuan_client import SiYuanClient
from .calibre_service import CalibreService

logger = logging.getLogger(__name__)

# In-memory storage (MVP - will migrate to PostgreSQL/Neo4j later)
_highlights: dict[str, Highlight] = {}
_book_highlights: dict[str, list[str]] = {}  # book_id -> highlight_ids
_book_note_ids: dict[str, str] = {}  # book_id -> siyuan_doc_id (cache)


class HighlightService:
    """Manages reader highlights with storage and entity extraction."""

    @staticmethod
    async def create_highlight(data: HighlightCreate) -> Highlight:
        """Create a new highlight.

        Args:
            data: Highlight creation data

        Returns:
            Created highlight with ID
        """
        highlight_id = f"hl_{uuid.uuid4().hex[:12]}"

        highlight = Highlight(
            id=highlight_id,
            book_id=data.book_id,
            text=data.text,
            cfi=data.cfi,
            note=data.note,
            color=data.color,
            context_id=data.context_id,
            chapter=data.chapter,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Store highlight
        _highlights[highlight_id] = highlight

        # Index by book
        if data.book_id not in _book_highlights:
            _book_highlights[data.book_id] = []
        _book_highlights[data.book_id].append(highlight_id)

        logger.info(f"Created highlight {highlight_id} for book {data.book_id}")

        return highlight

    @staticmethod
    async def get_highlight(highlight_id: str) -> Highlight | None:
        """Get a highlight by ID."""
        return _highlights.get(highlight_id)

    @staticmethod
    async def update_highlight(
        highlight_id: str, data: HighlightUpdate
    ) -> Highlight | None:
        """Update a highlight.

        Args:
            highlight_id: Highlight to update
            data: Update data

        Returns:
            Updated highlight or None if not found
        """
        highlight = _highlights.get(highlight_id)
        if not highlight:
            return None

        # Apply updates
        update_dict = data.model_dump(exclude_none=True)
        for key, value in update_dict.items():
            setattr(highlight, key, value)
        highlight.updated_at = datetime.utcnow()

        _highlights[highlight_id] = highlight
        return highlight

    @staticmethod
    async def delete_highlight(highlight_id: str) -> bool:
        """Delete a highlight.

        Args:
            highlight_id: Highlight to delete

        Returns:
            True if deleted, False if not found
        """
        highlight = _highlights.pop(highlight_id, None)
        if not highlight:
            return False

        # Remove from book index
        if highlight.book_id in _book_highlights:
            _book_highlights[highlight.book_id] = [
                hid
                for hid in _book_highlights[highlight.book_id]
                if hid != highlight_id
            ]

        return True

    @staticmethod
    async def list_highlights(
        book_id: str | None = None,
        context_id: str | None = None,
        limit: int = 100,
    ) -> list[Highlight]:
        """List highlights with optional filtering.

        Args:
            book_id: Filter by book
            context_id: Filter by context
            limit: Maximum results

        Returns:
            List of highlights
        """
        if book_id:
            highlight_ids = _book_highlights.get(book_id, [])
            highlights = [
                _highlights[hid] for hid in highlight_ids if hid in _highlights
            ]
        else:
            highlights = list(_highlights.values())

        # Apply context filter
        if context_id:
            highlights = [h for h in highlights if h.context_id == context_id]

        # Sort by creation time (newest first) and limit
        highlights.sort(key=lambda h: h.created_at, reverse=True)
        return highlights[:limit]

    @staticmethod
    async def batch_sync(data: HighlightBatchCreate) -> dict:
        """Sync multiple highlights from a book.

        Args:
            data: Batch of highlights to sync

        Returns:
            Dict with created/updated counts
        """
        created = 0
        updated = 0
        errors = []

        # Get existing highlights for this book (keyed by CFI for deduplication)
        existing_by_cfi = {}
        for hid in _book_highlights.get(data.book_id, []):
            h = _highlights.get(hid)
            if h:
                existing_by_cfi[h.cfi] = h

        for hl_data in data.highlights:
            try:
                # Check if highlight already exists (by CFI)
                existing = existing_by_cfi.get(hl_data.cfi)
                if existing:
                    # Update existing
                    update_data = HighlightUpdate(
                        note=hl_data.note,
                        color=hl_data.color,
                        context_id=hl_data.context_id,
                    )
                    await HighlightService.update_highlight(existing.id, update_data)
                    updated += 1
                else:
                    # Create new
                    await HighlightService.create_highlight(hl_data)
                    created += 1
            except Exception as e:
                errors.append(f"Error syncing highlight: {str(e)[:50]}")
                logger.error(f"Error syncing highlight: {e}")

        logger.info(
            f"Batch sync for book {data.book_id}: created={created}, updated={updated}"
        )

        return {
            "created": created,
            "updated": updated,
            "errors": errors,
        }

    @staticmethod
    async def mark_processed(
        highlight_id: str, entity_refs: list[str]
    ) -> Highlight | None:
        """Mark a highlight as processed with extracted entities.

        Args:
            highlight_id: Highlight to update
            entity_refs: List of entity names found in the highlight

        Returns:
            Updated highlight or None if not found
        """
        highlight = _highlights.get(highlight_id)
        if not highlight:
            return None

        highlight.processed = True
        highlight.entity_refs = entity_refs
        highlight.updated_at = datetime.utcnow()

        _highlights[highlight_id] = highlight
        return highlight

    @staticmethod
    async def get_unprocessed_highlights(limit: int = 50) -> list[Highlight]:
        """Get highlights that haven't been processed for entity extraction.

        Args:
            limit: Maximum highlights to return

        Returns:
            List of unprocessed highlights
        """
        unprocessed = [h for h in _highlights.values() if not h.processed]
        unprocessed.sort(key=lambda h: h.created_at)
        return unprocessed[:limit]

    @staticmethod
    async def sync_highlight_to_siyuan(highlight: Highlight) -> str | None:
        """Sync a highlight to SiYuan Book Note.

        Creates the Book Note if it doesn't exist (auto-creation).
        Appends the highlight to the Book Note's Highlights section.

        Args:
            highlight: Highlight to sync

        Returns:
            SiYuan block ID or None if sync failed
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
                except Exception as e:
                    logger.warning(f"Failed to get book info for {book_id}: {e}")
                    # Fallback: create with minimal info
                    doc_id = await SiYuanClient.create_book_note(
                        calibre_id=book_id,
                        title=f"Book {book_id}",
                        author="Unknown",
                    )

            if not doc_id:
                logger.warning(f"Could not create/find book note for {book_id}")
                return None

            # Cache the book note ID
            _book_note_ids[book_id] = doc_id

            # Append highlight to book note
            block_id = await SiYuanClient.append_highlight_to_book_note(
                doc_id=doc_id,
                highlight_text=highlight.text,
                note=highlight.note,
                chapter=highlight.chapter,
                cfi=highlight.cfi,
            )

            if block_id:
                # Update highlight with SiYuan block ID
                highlight.siyuan_block_id = block_id
                _highlights[highlight.id] = highlight
                logger.info(f"Synced highlight {highlight.id} to SiYuan block {block_id}")

            return block_id

        except Exception as e:
            logger.warning(f"Failed to sync highlight to SiYuan: {e}")
            return None

    @staticmethod
    async def sync_to_siyuan(highlight_id: str) -> bool:
        """Sync a specific highlight to SiYuan.

        Args:
            highlight_id: ID of highlight to sync

        Returns:
            True if synced successfully
        """
        highlight = _highlights.get(highlight_id)
        if not highlight:
            return False

        block_id = await HighlightService.sync_highlight_to_siyuan(highlight)
        return block_id is not None
