"""SiYuan Note API client for creating and managing blocks."""

import logging
import os
from datetime import datetime
from typing import Any

import httpx


logger = logging.getLogger(__name__)


class SiYuanClient:
    """Async client for SiYuan Note API."""

    _base_url: str = os.getenv("SIYUAN_BASE_URL", "http://192.168.86.60:6806")
    _token: str = os.getenv("SIYUAN_TOKEN", "8ddw4vp2tokab94y.")

    @classmethod
    async def _request(cls, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make an authenticated request to SiYuan API."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{cls._base_url}/api/{endpoint}",
                json=data,
                headers={"Authorization": f"Token {cls._token}"},
            )
            response.raise_for_status()
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"SiYuan API error: {result.get('msg', 'Unknown error')}")
            return result.get("data", {})

    @classmethod
    async def list_notebooks(cls) -> list[dict[str, Any]]:
        """List all notebooks."""
        data = await cls._request("notebook/lsNotebooks", {})
        notebooks = data.get("notebooks", []) if isinstance(data, dict) else []
        return notebooks

    @classmethod
    async def find_notebook_by_name(cls, name: str) -> dict[str, Any] | None:
        """Find a notebook by name (case-insensitive partial match)."""
        notebooks = await cls.list_notebooks()
        name_lower = name.lower()
        for nb in notebooks:
            if name_lower in nb.get("name", "").lower():
                return nb
        return None

    @classmethod
    async def create_doc(
        cls,
        notebook_id: str,
        path: str,
        markdown: str,
    ) -> str:
        """Create a new document. Returns the document block ID."""
        data = await cls._request(
            "filetree/createDocWithMd",
            {"notebook": notebook_id, "path": path, "markdown": markdown},
        )
        # API returns ID as string directly
        if isinstance(data, str):
            return data
        return data.get("id", "") if isinstance(data, dict) else ""

    @classmethod
    async def append_block(
        cls,
        parent_id: str,
        markdown: str,
    ) -> str:
        """Append a block to a parent. Returns the new block ID."""
        data = await cls._request(
            "block/appendBlock",
            {"parentID": parent_id, "data": markdown, "dataType": "markdown"},
        )
        # Response is a list of operation results
        if isinstance(data, list) and data:
            ops = data[0].get("doOperations", [])
            if ops:
                return ops[0].get("id", "")
        return ""

    @classmethod
    async def get_doc_id_by_path(cls, notebook_id: str, path: str) -> str | None:
        """Get document ID by human-readable path."""
        try:
            data = await cls._request(
                "filetree/getIDsByHPath",
                {"notebook": notebook_id, "path": path},
            )
            ids = data if isinstance(data, list) else []
            return ids[0] if ids else None
        except Exception:
            return None

    @classmethod
    async def ensure_daily_doc(cls, notebook_id: str, date: datetime | None = None) -> str:
        """Ensure daily log document exists, return its ID."""
        date = date or datetime.now()
        path = f"/Daily/{date.strftime('%Y-%m-%d')}"
        title = date.strftime("%Y-%m-%d")

        # Check if doc exists
        doc_id = await cls.get_doc_id_by_path(notebook_id, path)
        if doc_id:
            return doc_id

        # Create it
        return await cls.create_doc(notebook_id, path, f"# {title}\n\n")

    @classmethod
    async def create_spark_block(
        cls,
        spark_id: str,
        title: str,
        content: str,
        source_id: str | None = None,
        source_name: str | None = None,
        resonance_signal: str = "curious",
        energy_level: str = "medium",
    ) -> str | None:
        """Create a spark block in SiYuan Daily log.

        Returns the block ID or None if creation fails.
        """
        try:
            # Find the IES or Personal notebook (must be open)
            notebooks = await cls.list_notebooks()
            open_notebooks = [nb for nb in notebooks if not nb.get("closed", True)]

            notebook = None
            # Priority: IES > Personal > any open notebook
            for name in ["IES", "Personal", "Intelligent Exploration"]:
                for nb in open_notebooks:
                    if name.lower() in nb.get("name", "").lower():
                        notebook = nb
                        break
                if notebook:
                    break

            # Fallback to first open notebook
            if not notebook and open_notebooks:
                notebook = open_notebooks[0]

            if not notebook:
                logger.warning("No SiYuan notebook found for spark creation")
                return None

            notebook_id = notebook["id"]

            # Ensure daily doc exists
            daily_doc_id = await cls.ensure_daily_doc(notebook_id)
            if not daily_doc_id:
                logger.warning("Could not ensure daily doc exists")
                return None

            # Build the spark markdown with frontmatter
            source_line = ""
            if source_id and source_name:
                source_line = f"\n\n*From: {source_name} (`{source_id}`)*"
            elif source_id:
                source_line = f"\n\n*Source: `{source_id}`*"

            markdown = f"""---
be_type: spark
be_id: {spark_id}
status: captured
resonance_signal: {resonance_signal}
energy_level: {energy_level}
source_type: conversation
source_id: {source_id or ''}
---

## {title}

{content}{source_line}

---
"""
            # Append to daily doc
            block_id = await cls.append_block(daily_doc_id, markdown)
            return block_id

        except Exception as e:
            logger.warning(f"Failed to create SiYuan spark block: {e}")
            return None
