"""Tests for BlockAttributeService."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from ies_backend.schemas.block_attribute import (
    BlockAttributeQuery,
    BlockAttributeUpdate,
    BlockStatus,
    BlockType,
    EnergyLevel,
    ResonanceSignal,
)
from ies_backend.services.block_attribute_service import BlockAttributeService


@pytest.fixture
def mock_siyuan():
    """Mock SiYuan client."""
    mock = MagicMock()
    mock._request = AsyncMock()
    return mock


@pytest.fixture
def service(mock_siyuan):
    """BlockAttributeService with mocked SiYuan client."""
    return BlockAttributeService(siyuan_client=mock_siyuan)


@pytest.mark.asyncio
async def test_query_blocks_by_type(service, mock_siyuan):
    """Test querying blocks by type."""
    # Mock SQL query response
    mock_siyuan._request.return_value = [
        {
            "id": "20251209143000-abc123",
            "box": "notebook123",
            "custom_be_type": "spark",
            "custom_be_id": "spark_20251209_x7y8z9",
            "custom_status": "captured",
            "custom_resonance": "surprised",
            "custom_energy": "medium",
            "custom_context": "ctx_feynman_m2n3o4",
            "custom_source": None,
            "custom_source_cfi": None,
            "created": 1702138200,
            "updated": 1702138200,
        }
    ]

    query = BlockAttributeQuery(be_type=BlockType.SPARK, limit=50)
    blocks = await service.query_blocks(query)

    assert len(blocks) == 1
    assert blocks[0].block_id == "20251209143000-abc123"
    assert blocks[0].be_type == BlockType.SPARK
    assert blocks[0].be_id == "spark_20251209_x7y8z9"
    assert blocks[0].status == BlockStatus.CAPTURED
    assert blocks[0].resonance == ResonanceSignal.SURPRISED
    assert blocks[0].energy == EnergyLevel.MEDIUM


@pytest.mark.asyncio
async def test_query_blocks_with_multiple_filters(service, mock_siyuan):
    """Test querying blocks with multiple filters."""
    mock_siyuan._request.return_value = []

    query = BlockAttributeQuery(
        be_type=BlockType.INSIGHT,
        status=BlockStatus.EXPLORING,
        resonance=ResonanceSignal.EXCITED,
        energy=EnergyLevel.HIGH,
        limit=100,
    )
    blocks = await service.query_blocks(query)

    # Verify SQL query was built with all filters
    call_args = mock_siyuan._request.call_args
    assert "custom_be_type = :be_type" in call_args[0][1]["stmt"]
    assert "custom_status = :status" in call_args[0][1]["stmt"]
    assert "custom_resonance = :resonance" in call_args[0][1]["stmt"]
    assert "custom_energy = :energy" in call_args[0][1]["stmt"]


@pytest.mark.asyncio
async def test_query_blocks_by_backend_id(service, mock_siyuan):
    """Test querying blocks by backend entity ID."""
    mock_siyuan._request.return_value = [
        {
            "id": "20251209143000-abc123",
            "box": "notebook123",
            "custom_be_type": "spark",
            "custom_be_id": "spark_20251209_x7y8z9",
            "custom_status": "captured",
            "custom_resonance": None,
            "custom_energy": None,
            "custom_context": None,
            "custom_source": None,
            "custom_source_cfi": None,
            "created": None,
            "updated": None,
        }
    ]

    query = BlockAttributeQuery(be_id="spark_20251209_x7y8z9", limit=100)
    blocks = await service.query_blocks(query)

    assert len(blocks) == 1
    assert blocks[0].be_id == "spark_20251209_x7y8z9"


@pytest.mark.asyncio
async def test_get_block_by_id(service, mock_siyuan):
    """Test getting single block by ID."""
    mock_siyuan._request.return_value = {
        "box": "notebook123",
        "custom-be_type": "concept",
        "custom-be_id": "concept_abc123",
        "custom-status": "anchored",
        "custom-resonance": "validated",
        "custom-energy": "medium",
        "custom-context": "ctx_project_xyz",
        "custom-source": "book_calibre_42",
        "custom-source-cfi": "/6/4[chap03]!/4/2/1:0",
        "created": 1702138200,
        "updated": 1702138200,
    }

    block = await service.get_block_by_id("20251209143000-abc123")

    assert block is not None
    assert block.block_id == "20251209143000-abc123"
    assert block.be_type == BlockType.CONCEPT
    assert block.status == BlockStatus.ANCHORED
    assert block.resonance == ResonanceSignal.VALIDATED
    assert block.energy == EnergyLevel.MEDIUM
    assert block.context_id == "ctx_project_xyz"
    assert block.source_id == "book_calibre_42"
    assert block.source_cfi == "/6/4[chap03]!/4/2/1:0"


@pytest.mark.asyncio
async def test_get_block_by_id_not_found(service, mock_siyuan):
    """Test getting block that doesn't exist."""
    mock_siyuan._request.return_value = None

    block = await service.get_block_by_id("nonexistent")

    assert block is None


@pytest.mark.asyncio
async def test_get_blocks_by_backend_id(service, mock_siyuan):
    """Test getting all blocks linked to a backend entity."""
    mock_siyuan._request.return_value = [
        {
            "id": "block1",
            "box": "notebook123",
            "custom_be_type": "spark",
            "custom_be_id": "spark_123",
            "custom_status": "captured",
            "custom_resonance": None,
            "custom_energy": None,
            "custom_context": None,
            "custom_source": None,
            "custom_source_cfi": None,
            "created": None,
            "updated": None,
        },
        {
            "id": "block2",
            "box": "notebook123",
            "custom_be_type": "insight",
            "custom_be_id": "spark_123",  # Same backend ID
            "custom_status": "anchored",
            "custom_resonance": None,
            "custom_energy": None,
            "custom_context": None,
            "custom_source": None,
            "custom_source_cfi": None,
            "created": None,
            "updated": None,
        },
    ]

    blocks = await service.get_blocks_by_backend_id("spark_123")

    assert len(blocks) == 2
    assert all(b.be_id == "spark_123" for b in blocks)


@pytest.mark.asyncio
async def test_get_blocks_by_type(service, mock_siyuan):
    """Test getting blocks of a specific type."""
    mock_siyuan._request.return_value = [
        {
            "id": "block1",
            "box": "notebook123",
            "custom_be_type": "question",
            "custom_be_id": "q_123",
            "custom_status": None,
            "custom_resonance": None,
            "custom_energy": None,
            "custom_context": "ctx_project",
            "custom_source": None,
            "custom_source_cfi": None,
            "created": None,
            "updated": None,
        }
    ]

    blocks = await service.get_blocks_by_type(BlockType.QUESTION, limit=10)

    assert len(blocks) == 1
    assert blocks[0].be_type == BlockType.QUESTION
    assert blocks[0].context_id == "ctx_project"


@pytest.mark.asyncio
async def test_update_block_attributes(service, mock_siyuan):
    """Test updating block attributes."""
    mock_siyuan._request.return_value = {}  # setBlockAttrs returns empty on success

    updates = BlockAttributeUpdate(
        status=BlockStatus.EXPLORING,
        resonance=ResonanceSignal.CURIOUS,
        energy=EnergyLevel.HIGH,
        context_id="ctx_new_context",
    )

    success = await service.update_block_attributes("block123", updates)

    assert success is True

    # Verify attrs were set with custom- prefix
    call_args = mock_siyuan._request.call_args
    attrs = call_args[0][1]["attrs"]
    assert attrs["custom-status"] == "exploring"
    assert attrs["custom-resonance"] == "curious"
    assert attrs["custom-energy"] == "high"
    assert attrs["custom-context"] == "ctx_new_context"


@pytest.mark.asyncio
async def test_update_block_attributes_partial(service, mock_siyuan):
    """Test updating only some attributes."""
    mock_siyuan._request.return_value = {}

    updates = BlockAttributeUpdate(status=BlockStatus.ANCHORED)

    success = await service.update_block_attributes("block123", updates)

    assert success is True

    # Only status should be in attrs
    call_args = mock_siyuan._request.call_args
    attrs = call_args[0][1]["attrs"]
    assert "custom-status" in attrs
    assert "custom-resonance" not in attrs
    assert "custom-energy" not in attrs


@pytest.mark.asyncio
async def test_get_stats(service, mock_siyuan):
    """Test getting block attribute statistics."""
    mock_siyuan._request.return_value = [
        {
            "custom_be_type": "spark",
            "custom_status": "captured",
            "custom_resonance": "curious",
            "custom_energy": "medium",
            "custom_be_id": "spark_1",
        },
        {
            "custom_be_type": "spark",
            "custom_status": "captured",
            "custom_resonance": "excited",
            "custom_energy": "high",
            "custom_be_id": "spark_2",
        },
        {
            "custom_be_type": "insight",
            "custom_status": "anchored",
            "custom_resonance": "validated",
            "custom_energy": "medium",
            "custom_be_id": "insight_1",
        },
        {
            "custom_be_type": "concept",
            "custom_status": "anchored",
            "custom_resonance": None,
            "custom_energy": None,
            "custom_be_id": None,  # No backend link
        },
    ]

    stats = await service.get_stats()

    assert stats.total_blocks == 4
    assert stats.blocks_by_type["spark"] == 2
    assert stats.blocks_by_type["insight"] == 1
    assert stats.blocks_by_type["concept"] == 1
    assert stats.blocks_by_status["captured"] == 2
    assert stats.blocks_by_status["anchored"] == 2
    assert stats.blocks_by_resonance["curious"] == 1
    assert stats.blocks_by_resonance["excited"] == 1
    assert stats.blocks_by_resonance["validated"] == 1
    assert stats.blocks_by_energy["medium"] == 2
    assert stats.blocks_by_energy["high"] == 1
    assert stats.blocks_with_backend_link == 3
    assert stats.blocks_without_backend_link == 1


@pytest.mark.asyncio
async def test_query_blocks_handles_errors(service, mock_siyuan):
    """Test that query_blocks handles SiYuan errors gracefully."""
    mock_siyuan._request.side_effect = Exception("SiYuan API error")

    query = BlockAttributeQuery(be_type=BlockType.SPARK)
    blocks = await service.query_blocks(query)

    assert blocks == []


@pytest.mark.asyncio
async def test_get_block_handles_errors(service, mock_siyuan):
    """Test that get_block_by_id handles errors gracefully."""
    mock_siyuan._request.side_effect = Exception("SiYuan API error")

    block = await service.get_block_by_id("block123")

    assert block is None
