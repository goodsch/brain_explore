"""Tests for highlight synchronization service."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from ies_backend.schemas.highlight import (
    Highlight,
    HighlightCreate,
    HighlightColor,
    SyncStatus,
    NoteType,
)
from ies_backend.services.highlight_sync_service import HighlightSyncService
from ies_backend.services.highlight_service import HighlightService, _highlights


@pytest.fixture(autouse=True)
def clear_storage():
    """Clear in-memory storage before each test."""
    _highlights.clear()
    from ies_backend.services.highlight_service import _book_highlights, _book_note_ids

    _book_highlights.clear()
    _book_note_ids.clear()


@pytest.mark.asyncio
async def test_sync_single_highlight():
    """Test syncing a single highlight to SiYuan."""
    # Create a highlight
    data = HighlightCreate(
        book_id="42",
        text="Test highlight text",
        cfi="/6/4[chap01]!/4/2/1:0",
        note="Test note",
        color=HighlightColor.YELLOW,
        chapter="Chapter 1",
    )
    highlight = await HighlightService.create_highlight(data)

    # Mock SiYuan client methods
    with (
        patch(
            "ies_backend.services.highlight_sync_service.SiYuanClient.find_book_note_by_calibre_id",
            new_callable=AsyncMock,
            return_value="doc_123",
        ),
        patch(
            "ies_backend.services.highlight_sync_service.SiYuanClient.append_highlight_to_book_note",
            new_callable=AsyncMock,
            return_value="block_456",
        ),
    ):
        # Sync the highlight
        result = await HighlightSyncService.sync_highlight(highlight)

        # Verify result
        assert result.success is True
        assert result.siyuan_block_id == "block_456"
        assert result.highlight_id == highlight.id
        assert result.error is None

        # Verify highlight was updated
        updated = _highlights[highlight.id]
        assert updated.siyuan_block_id == "block_456"
        assert updated.sync_status == SyncStatus.SYNCED
        assert updated.synced_at is not None
        assert updated.sync_error is None


@pytest.mark.asyncio
async def test_sync_creates_book_note():
    """Test that sync creates book note if it doesn't exist."""
    # Create a highlight
    data = HighlightCreate(
        book_id="42",
        text="Test highlight",
        cfi="/6/4[chap01]!/4/2/1:0",
    )
    highlight = await HighlightService.create_highlight(data)

    # Mock SiYuan client to simulate book note creation
    with (
        patch(
            "ies_backend.services.highlight_sync_service.SiYuanClient.find_book_note_by_calibre_id",
            new_callable=AsyncMock,
            return_value=None,  # Book note doesn't exist
        ),
        patch(
            "ies_backend.services.highlight_sync_service.SiYuanClient.create_book_note",
            new_callable=AsyncMock,
            return_value="new_doc_123",
        ),
        patch(
            "ies_backend.services.highlight_sync_service.SiYuanClient.append_highlight_to_book_note",
            new_callable=AsyncMock,
            return_value="block_456",
        ),
        patch(
            "ies_backend.services.highlight_sync_service.CalibreService.get_book",
            return_value=None,  # Simulate Calibre service failure
        ),
    ):
        # Sync the highlight
        result = await HighlightSyncService.sync_highlight(highlight)

        # Verify result
        assert result.success is True
        assert result.siyuan_block_id == "block_456"


@pytest.mark.asyncio
async def test_sync_sets_block_attributes():
    """Test that sync sets proper block attributes."""
    # Create a highlight with metadata
    data = HighlightCreate(
        book_id="42",
        text="Test highlight",
        cfi="/6/4[chap01]!/4/2/1:0",
        note="Important insight",
        context_id="ctx_123",
        question_id="q_456",
        note_type=NoteType.INSIGHT,
    )
    highlight = await HighlightService.create_highlight(data)

    # Mock SiYuan client
    append_mock = AsyncMock(return_value="block_789")

    with (
        patch(
            "ies_backend.services.highlight_sync_service.SiYuanClient.find_book_note_by_calibre_id",
            new_callable=AsyncMock,
            return_value="doc_123",
        ),
        patch(
            "ies_backend.services.highlight_sync_service.SiYuanClient.append_highlight_to_book_note",
            append_mock,
        ),
    ):
        # Sync the highlight
        await HighlightSyncService.sync_highlight(highlight)

        # Verify append_highlight_to_book_note was called with all metadata
        append_mock.assert_called_once()
        call_kwargs = append_mock.call_args.kwargs
        assert call_kwargs["highlight_id"] == highlight.id
        assert call_kwargs["context_id"] == "ctx_123"
        assert call_kwargs["question_id"] == "q_456"
        assert call_kwargs["note_type"] == "insight"
        assert call_kwargs["cfi"] == "/6/4[chap01]!/4/2/1:0"


@pytest.mark.asyncio
async def test_batch_sync():
    """Test batch syncing highlights for a book."""
    # Create multiple highlights
    for i in range(3):
        data = HighlightCreate(
            book_id="42",
            text=f"Highlight {i}",
            cfi=f"/6/4[chap01]!/4/2/{i}:0",
        )
        await HighlightService.create_highlight(data)

    # Mock SiYuan client
    with (
        patch(
            "ies_backend.services.highlight_sync_service.SiYuanClient.find_book_note_by_calibre_id",
            new_callable=AsyncMock,
            return_value="doc_123",
        ),
        patch(
            "ies_backend.services.highlight_sync_service.SiYuanClient.append_highlight_to_book_note",
            new_callable=AsyncMock,
            side_effect=["block_1", "block_2", "block_3"],
        ),
    ):
        # Batch sync
        result = await HighlightSyncService.sync_book_highlights("42")

        # Verify result
        assert result.total == 3
        assert result.synced == 3
        assert result.failed == 0
        assert len(result.results) == 3

        # Verify all highlights were synced
        for hl in _highlights.values():
            assert hl.sync_status == SyncStatus.SYNCED
            assert hl.siyuan_block_id is not None


@pytest.mark.asyncio
async def test_sync_error_handling():
    """Test that sync errors are properly handled."""
    # Create a highlight
    data = HighlightCreate(
        book_id="42",
        text="Test highlight",
        cfi="/6/4[chap01]!/4/2/1:0",
    )
    highlight = await HighlightService.create_highlight(data)

    # Mock SiYuan client to raise an error
    with (
        patch(
            "ies_backend.services.highlight_sync_service.SiYuanClient.find_book_note_by_calibre_id",
            new_callable=AsyncMock,
            side_effect=Exception("SiYuan connection error"),
        ),
    ):
        # Sync the highlight
        result = await HighlightSyncService.sync_highlight(highlight)

        # Verify error handling
        assert result.success is False
        assert result.siyuan_block_id is None
        assert "SiYuan connection error" in result.error

        # Verify highlight was marked as error
        updated = _highlights[highlight.id]
        assert updated.sync_status == SyncStatus.ERROR
        assert updated.sync_error is not None
        assert updated.siyuan_block_id is None


@pytest.mark.asyncio
async def test_get_sync_status():
    """Test getting sync status summary."""
    # Create highlights with different sync statuses
    for i in range(5):
        data = HighlightCreate(
            book_id="42",
            text=f"Highlight {i}",
            cfi=f"/6/4[chap01]!/4/2/{i}:0",
        )
        hl = await HighlightService.create_highlight(data)

        # Set different sync statuses
        if i < 2:
            hl.sync_status = SyncStatus.SYNCED
        elif i < 4:
            hl.sync_status = SyncStatus.PENDING
        else:
            hl.sync_status = SyncStatus.ERROR

        _highlights[hl.id] = hl

    # Get sync status
    status = await HighlightSyncService.get_sync_status(book_id="42")

    # Verify counts
    assert status.total_highlights == 5
    assert status.synced == 2
    assert status.pending == 2
    assert status.error == 1
    assert status.modified == 0
    assert status.book_id == "42"


@pytest.mark.asyncio
async def test_batch_sync_retries_errors():
    """Test that batch sync retries highlights with error status."""
    # Create a highlight with error status
    data = HighlightCreate(
        book_id="42",
        text="Test highlight",
        cfi="/6/4[chap01]!/4/2/1:0",
    )
    hl = await HighlightService.create_highlight(data)
    hl.sync_status = SyncStatus.ERROR
    hl.sync_error = "Previous error"
    _highlights[hl.id] = hl

    # Mock SiYuan client for successful retry
    with (
        patch(
            "ies_backend.services.highlight_sync_service.SiYuanClient.find_book_note_by_calibre_id",
            new_callable=AsyncMock,
            return_value="doc_123",
        ),
        patch(
            "ies_backend.services.highlight_sync_service.SiYuanClient.append_highlight_to_book_note",
            new_callable=AsyncMock,
            return_value="block_456",
        ),
    ):
        # Batch sync
        result = await HighlightSyncService.sync_book_highlights("42")

        # Verify retry was successful
        assert result.synced == 1
        assert result.failed == 0

        # Verify highlight was updated
        updated = _highlights[hl.id]
        assert updated.sync_status == SyncStatus.SYNCED
        assert updated.sync_error is None


@pytest.mark.asyncio
async def test_sync_status_filter_by_book():
    """Test that sync status can be filtered by book."""
    # Create highlights for different books
    for book_id in ["42", "43"]:
        for i in range(2):
            data = HighlightCreate(
                book_id=book_id,
                text=f"Highlight {i}",
                cfi=f"/6/4[chap01]!/4/2/{i}:0",
            )
            await HighlightService.create_highlight(data)

    # Get sync status for specific book
    status = await HighlightSyncService.get_sync_status(book_id="42")

    # Verify only book 42 highlights are counted
    assert status.total_highlights == 2
    assert status.book_id == "42"


@pytest.mark.asyncio
async def test_sync_preserves_existing_block_id():
    """Test that sync doesn't overwrite existing block ID on retry."""
    # Create a highlight
    data = HighlightCreate(
        book_id="42",
        text="Test highlight",
        cfi="/6/4[chap01]!/4/2/1:0",
    )
    hl = await HighlightService.create_highlight(data)

    # Manually set as already synced
    hl.sync_status = SyncStatus.SYNCED
    hl.siyuan_block_id = "existing_block_123"
    _highlights[hl.id] = hl

    # Mock SiYuan client
    with (
        patch(
            "ies_backend.services.highlight_sync_service.SiYuanClient.find_book_note_by_calibre_id",
            new_callable=AsyncMock,
            return_value="doc_123",
        ),
        patch(
            "ies_backend.services.highlight_sync_service.SiYuanClient.append_highlight_to_book_note",
            new_callable=AsyncMock,
            return_value="new_block_456",
        ),
    ):
        # Batch sync should skip already synced highlights
        result = await HighlightSyncService.sync_book_highlights("42")

        # Verify no highlights were synced (already synced)
        assert result.synced == 0
        assert result.total == 0

        # Verify original block ID is preserved
        assert _highlights[hl.id].siyuan_block_id == "existing_block_123"
