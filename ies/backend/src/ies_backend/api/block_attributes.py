"""Block Attributes API endpoints.

Provides REST API for querying and managing SiYuan block attributes.
"""

import logging

from fastapi import APIRouter, HTTPException, Query

from ..schemas.block_attribute import (
    BlockAttribute,
    BlockAttributeListResponse,
    BlockAttributeQuery,
    BlockAttributeStats,
    BlockAttributeUpdate,
    BlockAttributeUpdateResponse,
    BlockStatus,
    BlockType,
    EnergyLevel,
    ResonanceSignal,
)
from ..services.block_attribute_service import BlockAttributeService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/block-attributes", tags=["block-attributes"])
service = BlockAttributeService()


@router.get("/", response_model=BlockAttributeListResponse)
async def list_blocks(
    be_type: BlockType | None = Query(None, description="Filter by block type"),
    be_id: str | None = Query(None, description="Filter by backend entity ID"),
    status: BlockStatus | None = Query(None, description="Filter by status"),
    resonance: ResonanceSignal | None = Query(
        None, description="Filter by resonance signal"
    ),
    energy: EnergyLevel | None = Query(None, description="Filter by energy level"),
    context_id: str | None = Query(None, description="Filter by context ID"),
    notebook_id: str | None = Query(None, description="Filter by notebook ID"),
    limit: int = Query(50, ge=1, le=500, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Results offset"),
) -> BlockAttributeListResponse:
    """Query blocks by attributes.

    Returns list of SiYuan blocks matching the specified attribute filters.
    """
    query = BlockAttributeQuery(
        be_type=be_type,
        be_id=be_id,
        status=status,
        resonance=resonance,
        energy=energy,
        context_id=context_id,
        notebook_id=notebook_id,
        limit=limit,
        offset=offset,
    )

    blocks = await service.query_blocks(query)
    return BlockAttributeListResponse(blocks=blocks, total=len(blocks))


@router.get("/{block_id}", response_model=BlockAttribute)
async def get_block(block_id: str) -> BlockAttribute:
    """Get single block by ID.

    Args:
        block_id: SiYuan block ID

    Returns:
        BlockAttribute with all custom attributes

    Raises:
        HTTPException: 404 if block not found
    """
    block = await service.get_block_by_id(block_id)
    if not block:
        raise HTTPException(status_code=404, detail=f"Block {block_id} not found")
    return block


@router.get("/by-backend-id/{be_id}", response_model=BlockAttributeListResponse)
async def get_blocks_by_backend_id(be_id: str) -> BlockAttributeListResponse:
    """Get all SiYuan blocks linked to a backend entity.

    Args:
        be_id: Backend entity ID (e.g., spark_20251209_x7y8z9)

    Returns:
        List of blocks with matching be_id
    """
    blocks = await service.get_blocks_by_backend_id(be_id)
    return BlockAttributeListResponse(blocks=blocks, total=len(blocks))


@router.get("/by-type/{be_type}", response_model=BlockAttributeListResponse)
async def get_blocks_by_type(
    be_type: BlockType,
    limit: int = Query(50, ge=1, le=500),
) -> BlockAttributeListResponse:
    """Get blocks of a specific type.

    Args:
        be_type: Block type (spark, insight, concept, etc.)
        limit: Maximum results

    Returns:
        List of blocks of the specified type
    """
    blocks = await service.get_blocks_by_type(be_type, limit)
    return BlockAttributeListResponse(blocks=blocks, total=len(blocks))


@router.patch("/{block_id}", response_model=BlockAttributeUpdateResponse)
async def update_block_attributes(
    block_id: str, updates: BlockAttributeUpdate
) -> BlockAttributeUpdateResponse:
    """Update block attributes.

    Only non-None fields in the update request are applied.

    Args:
        block_id: SiYuan block ID
        updates: Attribute updates

    Returns:
        Update confirmation with list of updated fields

    Raises:
        HTTPException: 404 if block not found or update fails
    """
    # Check block exists
    existing = await service.get_block_by_id(block_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Block {block_id} not found")

    # Apply updates
    success = await service.update_block_attributes(block_id, updates)
    if not success:
        raise HTTPException(
            status_code=500, detail=f"Failed to update block {block_id}"
        )

    # Collect updated fields
    updated_fields = []
    if updates.be_type is not None:
        updated_fields.append("be_type")
    if updates.be_id is not None:
        updated_fields.append("be_id")
    if updates.status is not None:
        updated_fields.append("status")
    if updates.resonance is not None:
        updated_fields.append("resonance")
    if updates.energy is not None:
        updated_fields.append("energy")
    if updates.context_id is not None:
        updated_fields.append("context_id")
    if updates.source_id is not None:
        updated_fields.append("source_id")
    if updates.source_cfi is not None:
        updated_fields.append("source_cfi")

    return BlockAttributeUpdateResponse(
        block_id=block_id, updated_fields=updated_fields, success=True
    )


@router.get("/stats/summary", response_model=BlockAttributeStats)
async def get_stats() -> BlockAttributeStats:
    """Get statistics about block attributes in the system.

    Returns:
        Statistics including counts by type, status, resonance, energy
    """
    return await service.get_stats()
