"""SiYuan client for knowledge base operations."""

from typing import Any

import httpx

from ies_backend.config import settings


class SiYuanClient:
    """Client for SiYuan API interactions."""

    @classmethod
    def _get_base_url(cls) -> str:
        """Get the SiYuan API base URL."""
        return f"http://{settings.siyuan_host}:{settings.siyuan_port}"

    @classmethod
    def _get_headers(cls) -> dict[str, str]:
        """Get request headers with auth token."""
        return {
            "Authorization": f"Token {settings.siyuan_token}",
            "Content-Type": "application/json",
        }

    @classmethod
    async def _request(
        cls, endpoint: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make a request to the SiYuan API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{cls._get_base_url()}/api{endpoint}",
                headers=cls._get_headers(),
                json=data or {},
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"SiYuan API error: {result.get('msg')}")
            return result.get("data", {})

    @classmethod
    async def create_doc(
        cls, notebook: str, path: str, markdown: str
    ) -> dict[str, Any]:
        """Create a new document in SiYuan.

        Args:
            notebook: Notebook ID
            path: Document path (e.g., "/Profiles/chris")
            markdown: Markdown content

        Returns:
            Document info including ID
        """
        return await cls._request(
            "/filetree/createDocWithMd",
            {"notebook": notebook, "path": path, "markdown": markdown},
        )

    @classmethod
    async def update_block(cls, block_id: str, markdown: str) -> dict[str, Any]:
        """Update a block's content.

        Args:
            block_id: Block ID to update
            markdown: New markdown content
        """
        return await cls._request(
            "/block/updateBlock",
            {"id": block_id, "data": markdown, "dataType": "markdown"},
        )

    @classmethod
    async def get_block_kramdown(cls, block_id: str) -> str:
        """Get a block's kramdown source."""
        result = await cls._request("/block/getBlockKramdown", {"id": block_id})
        return result.get("kramdown", "")

    @classmethod
    async def sql_query(cls, sql: str) -> list[dict[str, Any]]:
        """Execute a SQL query against SiYuan's database.

        Args:
            sql: SQL query string

        Returns:
            List of matching records
        """
        result = await cls._request("/query/sql", {"stmt": sql})
        return result if isinstance(result, list) else []

    @classmethod
    async def find_doc_by_path(
        cls, notebook: str, path: str
    ) -> dict[str, Any] | None:
        """Find a document by its human-readable path.

        Args:
            notebook: Notebook ID
            path: Human-readable path (e.g., "/Profiles/chris")

        Returns:
            Document info or None if not found
        """
        # Get IDs by hpath
        try:
            result = await cls._request(
                "/filetree/getIDsByHPath",
                {"notebook": notebook, "path": path},
            )
            if result:
                return {"id": result[0]} if isinstance(result, list) else {"id": result}
        except Exception:
            pass
        return None

    @classmethod
    async def append_block(
        cls, parent_id: str, markdown: str
    ) -> dict[str, Any]:
        """Append a block as a child of the given parent.

        Args:
            parent_id: Parent block ID
            markdown: Markdown content to append
        """
        return await cls._request(
            "/block/appendBlock",
            {"parentID": parent_id, "data": markdown, "dataType": "markdown"},
        )

    @classmethod
    async def list_notebooks(cls) -> list[dict[str, Any]]:
        """List all notebooks."""
        result = await cls._request("/notebook/lsNotebooks")
        return result.get("notebooks", [])
