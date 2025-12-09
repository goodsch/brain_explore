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

    @classmethod
    async def get_doc_by_id(cls, doc_id: str) -> dict[str, Any] | None:
        """Get document info by ID."""
        try:
            data = await cls._request(
                "block/getBlockInfo",
                {"id": doc_id},
            )
            return data if isinstance(data, dict) else None
        except Exception:
            return None

    @classmethod
    async def search_docs(cls, query: str, notebook_id: str | None = None) -> list[dict]:
        """Search documents by keyword."""
        try:
            params = {"k": query}
            if notebook_id:
                params["box"] = notebook_id
            data = await cls._request("search/searchBlock", params)
            return data.get("blocks", []) if isinstance(data, dict) else []
        except Exception:
            return []

    @classmethod
    async def create_book_note(
        cls,
        calibre_id: str,
        title: str,
        author: str,
        notebook_id: str | None = None,
    ) -> str | None:
        """Create a Book Note document in SiYuan.

        Uses the Book Template structure with proper frontmatter.

        Args:
            calibre_id: Calibre book ID
            title: Book title
            author: Book author
            notebook_id: Target notebook ID (auto-detects if None)

        Returns:
            Document ID or None if creation fails
        """
        try:
            # Find or use provided notebook
            if not notebook_id:
                notebooks = await cls.list_notebooks()
                open_notebooks = [nb for nb in notebooks if not nb.get("closed", True)]

                notebook = None
                for name in ["IES", "Personal", "Intelligent Exploration"]:
                    for nb in open_notebooks:
                        if name.lower() in nb.get("name", "").lower():
                            notebook = nb
                            break
                    if notebook:
                        break

                if not notebook and open_notebooks:
                    notebook = open_notebooks[0]

                if not notebook:
                    logger.warning("No SiYuan notebook found for book note creation")
                    return None

                notebook_id = notebook["id"]

            # Clean title for path (remove special characters)
            clean_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
            clean_title = clean_title[:50]  # Limit length
            path = f"/Sources/Books/{clean_title}"

            # Check if book note already exists
            existing_id = await cls.get_doc_id_by_path(notebook_id, path)
            if existing_id:
                logger.info(f"Book note already exists for {title}: {existing_id}")
                return existing_id

            # Create Book Note with template structure
            markdown = f"""---
be_type: book
be_id: calibre_{calibre_id}
status: reading
calibre_id: {calibre_id}
title: {title}
author: {author}
---

# {title}

**Author:** {author}
**Calibre ID:** {calibre_id}

## Overview

*Summary and key themes will appear here as you read.*

## Key Concepts

*Extracted concepts from highlights.*

## Highlights

*Reading highlights from IES Reader.*

## Questions

*Questions that emerged while reading.*

## Connections

*Links to other concepts and sources.*

## Notes

*Your reflections and observations.*
"""
            doc_id = await cls.create_doc(notebook_id, path, markdown)
            logger.info(f"Created book note for {title}: {doc_id}")
            return doc_id

        except Exception as e:
            logger.warning(f"Failed to create book note: {e}")
            return None

    @classmethod
    async def append_highlight_to_book_note(
        cls,
        doc_id: str,
        highlight_text: str,
        note: str | None = None,
        chapter: str | None = None,
        cfi: str | None = None,
    ) -> str | None:
        """Append a highlight to a book note's Highlights section.

        Args:
            doc_id: Book note document ID
            highlight_text: The highlighted text
            note: User's note about the highlight
            chapter: Chapter name
            cfi: EPUB CFI location for jump-back

        Returns:
            Block ID of the created highlight or None
        """
        try:
            # Build highlight block with frontmatter
            location = chapter or ""
            if cfi:
                location = f"{location} (CFI: `{cfi}`)" if location else f"CFI: `{cfi}`"

            note_line = f"\n\n**Note:** {note}" if note else ""

            markdown = f"""---
custom-block-type: highlight
custom-source-cfi: {cfi or ''}
---

> "{highlight_text}"

*{location}*{note_line}

---
"""
            block_id = await cls.append_block(doc_id, markdown)
            return block_id

        except Exception as e:
            logger.warning(f"Failed to append highlight: {e}")
            return None

    @classmethod
    async def find_book_note_by_calibre_id(cls, calibre_id: str) -> str | None:
        """Find existing book note by calibre ID.

        Args:
            calibre_id: Calibre book ID

        Returns:
            Document ID or None if not found
        """
        try:
            # Search for documents containing the calibre_id
            results = await cls.search_docs(f"calibre_{calibre_id}")
            for block in results:
                # Check if it's a document root and contains our frontmatter
                content = block.get("content", "")
                if f"calibre_id: {calibre_id}" in content:
                    return block.get("rootID") or block.get("id")
            return None
        except Exception:
            return None
