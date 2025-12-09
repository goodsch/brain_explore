"""Block Attribute Service for querying SiYuan blocks by attributes.

This service enables the backend to:
- Query SiYuan blocks by be_type, status, resonance, energy
- Link SiYuan blocks to backend entities via be_id
- Track ADHD-friendly navigation metadata
- Support cross-app synchronization
"""

import logging
from typing import Any

from ..schemas.block_attribute import (
    BlockAttribute,
    BlockAttributeQuery,
    BlockAttributeStats,
    BlockAttributeUpdate,
    BlockType,
)
from .siyuan_client import SiYuanClient


logger = logging.getLogger(__name__)


class BlockAttributeService:
    """Service for managing SiYuan block attributes."""

    def __init__(self, siyuan_client: SiYuanClient | None = None):
        """Initialize with optional SiYuan client (for testing)."""
        self.siyuan = siyuan_client or SiYuanClient

    async def query_blocks(self, query: BlockAttributeQuery) -> list[BlockAttribute]:
        """Query blocks by attributes.

        Uses SiYuan SQL API to search blocks with custom attributes.

        Args:
            query: Query parameters (type, status, resonance, energy, etc.)

        Returns:
            List of blocks matching the query
        """
        # Build SQL query for SiYuan
        conditions = []
        params = {}

        if query.be_type:
            conditions.append("custom_be_type = :be_type")
            params["be_type"] = query.be_type.value

        if query.be_id:
            conditions.append("custom_be_id = :be_id")
            params["be_id"] = query.be_id

        if query.status:
            conditions.append("custom_status = :status")
            params["status"] = query.status.value

        if query.resonance:
            conditions.append("custom_resonance = :resonance")
            params["resonance"] = query.resonance.value

        if query.energy:
            conditions.append("custom_energy = :energy")
            params["energy"] = query.energy.value

        if query.context_id:
            conditions.append("custom_context = :context_id")
            params["context_id"] = query.context_id

        if query.notebook_id:
            conditions.append("box = :notebook_id")
            params["notebook_id"] = query.notebook_id

        # Build WHERE clause
        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Execute SQL query via SiYuan API
        try:
            sql = f"""
                SELECT id, box, custom_be_type, custom_be_id, custom_status,
                       custom_resonance, custom_energy, custom_context,
                       custom_source, custom_source_cfi, created, updated
                FROM blocks
                WHERE {where_clause}
                LIMIT {query.limit} OFFSET {query.offset}
            """

            result = await self.siyuan._request("query/sql", {"stmt": sql})
            rows = result if isinstance(result, list) else []

            # Map rows to BlockAttribute objects
            blocks = []
            for row in rows:
                try:
                    blocks.append(self._row_to_block_attribute(row))
                except Exception as e:
                    logger.warning(f"Failed to parse block row: {e}")
                    continue

            return blocks

        except Exception as e:
            logger.error(f"Failed to query blocks: {e}")
            return []

    async def get_block_by_id(self, block_id: str) -> BlockAttribute | None:
        """Get single block by ID.

        Args:
            block_id: SiYuan block ID

        Returns:
            BlockAttribute or None if not found
        """
        try:
            # Use SiYuan getBlockAttrs API
            result = await self.siyuan._request("attr/getBlockAttrs", {"id": block_id})

            if not result:
                return None

            # Parse attributes
            return BlockAttribute(
                block_id=block_id,
                notebook_id=result.get("box"),
                be_type=self._parse_enum(result.get("custom-be_type"), BlockType),
                be_id=result.get("custom-be_id"),
                status=result.get("custom-status"),
                resonance=result.get("custom-resonance"),
                energy=result.get("custom-energy"),
                context_id=result.get("custom-context"),
                source_id=result.get("custom-source"),
                source_cfi=result.get("custom-source-cfi"),
                created_at=self._parse_timestamp(result.get("created")),
                updated_at=self._parse_timestamp(result.get("updated")),
            )

        except Exception as e:
            logger.error(f"Failed to get block {block_id}: {e}")
            return None

    async def get_blocks_by_backend_id(self, be_id: str) -> list[BlockAttribute]:
        """Get all SiYuan blocks linked to a backend entity.

        Args:
            be_id: Backend entity ID (e.g., spark_20251209_x7y8z9)

        Returns:
            List of blocks with matching be_id
        """
        query = BlockAttributeQuery(be_id=be_id, limit=100)
        return await self.query_blocks(query)

    async def get_blocks_by_type(
        self, be_type: BlockType, limit: int = 50
    ) -> list[BlockAttribute]:
        """Get blocks of a specific type.

        Args:
            be_type: Block type (spark, insight, concept, etc.)
            limit: Maximum number of results

        Returns:
            List of blocks of the specified type
        """
        query = BlockAttributeQuery(be_type=be_type, limit=limit)
        return await self.query_blocks(query)

    async def update_block_attributes(
        self, block_id: str, updates: BlockAttributeUpdate
    ) -> bool:
        """Update block attributes.

        Args:
            block_id: SiYuan block ID
            updates: Attribute updates (only non-None fields are updated)

        Returns:
            True if successful
        """
        try:
            # Build attrs dict with custom- prefix
            attrs: dict[str, str] = {}

            if updates.be_type is not None:
                attrs["custom-be_type"] = updates.be_type.value
            if updates.be_id is not None:
                attrs["custom-be_id"] = updates.be_id
            if updates.status is not None:
                attrs["custom-status"] = updates.status.value
            if updates.resonance is not None:
                attrs["custom-resonance"] = updates.resonance.value
            if updates.energy is not None:
                attrs["custom-energy"] = updates.energy.value
            if updates.context_id is not None:
                attrs["custom-context"] = updates.context_id
            if updates.source_id is not None:
                attrs["custom-source"] = updates.source_id
            if updates.source_cfi is not None:
                attrs["custom-source-cfi"] = updates.source_cfi

            if not attrs:
                return True  # Nothing to update

            # Use SiYuan setBlockAttrs API
            await self.siyuan._request(
                "attr/setBlockAttrs", {"id": block_id, "attrs": attrs}
            )
            return True

        except Exception as e:
            logger.error(f"Failed to update block {block_id}: {e}")
            return False

    async def get_stats(self) -> BlockAttributeStats:
        """Get statistics about block attributes in the system.

        Returns:
            BlockAttributeStats with counts by type, status, etc.
        """
        try:
            # Query all blocks with any custom attributes
            sql = """
                SELECT custom_be_type, custom_status, custom_resonance, custom_energy,
                       custom_be_id
                FROM blocks
                WHERE custom_be_type IS NOT NULL OR custom_be_id IS NOT NULL
            """
            result = await self.siyuan._request("query/sql", {"stmt": sql})
            rows = result if isinstance(result, list) else []

            # Count statistics
            blocks_by_type: dict[str, int] = {}
            blocks_by_status: dict[str, int] = {}
            blocks_by_resonance: dict[str, int] = {}
            blocks_by_energy: dict[str, int] = {}
            blocks_with_backend_link = 0
            blocks_without_backend_link = 0

            for row in rows:
                # Type counts
                be_type = row.get("custom_be_type")
                if be_type:
                    blocks_by_type[be_type] = blocks_by_type.get(be_type, 0) + 1

                # Status counts
                status = row.get("custom_status")
                if status:
                    blocks_by_status[status] = blocks_by_status.get(status, 0) + 1

                # Resonance counts
                resonance = row.get("custom_resonance")
                if resonance:
                    blocks_by_resonance[resonance] = (
                        blocks_by_resonance.get(resonance, 0) + 1
                    )

                # Energy counts
                energy = row.get("custom_energy")
                if energy:
                    blocks_by_energy[energy] = blocks_by_energy.get(energy, 0) + 1

                # Backend link counts
                be_id = row.get("custom_be_id")
                if be_id:
                    blocks_with_backend_link += 1
                else:
                    blocks_without_backend_link += 1

            return BlockAttributeStats(
                total_blocks=len(rows),
                blocks_by_type=blocks_by_type,
                blocks_by_status=blocks_by_status,
                blocks_by_resonance=blocks_by_resonance,
                blocks_by_energy=blocks_by_energy,
                blocks_with_backend_link=blocks_with_backend_link,
                blocks_without_backend_link=blocks_without_backend_link,
            )

        except Exception as e:
            logger.error(f"Failed to get block stats: {e}")
            return BlockAttributeStats(
                total_blocks=0,
                blocks_with_backend_link=0,
                blocks_without_backend_link=0,
            )

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def _row_to_block_attribute(self, row: dict[str, Any]) -> BlockAttribute:
        """Convert SQL row to BlockAttribute object."""
        return BlockAttribute(
            block_id=row.get("id", ""),
            notebook_id=row.get("box"),
            be_type=self._parse_enum(row.get("custom_be_type"), BlockType),
            be_id=row.get("custom_be_id"),
            status=row.get("custom_status"),
            resonance=row.get("custom_resonance"),
            energy=row.get("custom_energy"),
            context_id=row.get("custom_context"),
            source_id=row.get("custom_source"),
            source_cfi=row.get("custom_source_cfi"),
            created_at=self._parse_timestamp(row.get("created")),
            updated_at=self._parse_timestamp(row.get("updated")),
        )

    def _parse_enum(self, value: Any, enum_class: type) -> Any:
        """Safely parse enum value."""
        if value is None:
            return None
        try:
            return enum_class(value)
        except (ValueError, KeyError):
            return None

    def _parse_timestamp(self, value: Any) -> Any:
        """Safely parse timestamp value."""
        if value is None:
            return None
        try:
            # SiYuan timestamps are in Unix epoch format (seconds)
            from datetime import datetime

            if isinstance(value, (int, float)):
                return datetime.fromtimestamp(value)
            return None
        except Exception:
            return None
