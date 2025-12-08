"""PDF text extraction using pypdf."""

import io
import re
from pathlib import Path

import httpx

from .base import ExtractedContent


class PDFExtractor:
    """Extract text content from PDF files."""

    @staticmethod
    def can_handle(source: str) -> bool:
        """Check if source is a PDF file or URL ending in .pdf."""
        source_lower = source.lower()
        if source_lower.endswith(".pdf"):
            return True
        if source_lower.startswith(("http://", "https://")) and ".pdf" in source_lower:
            return True
        # Check if it's a file path to PDF
        if Path(source).suffix.lower() == ".pdf":
            return True
        return False

    async def extract(self, source: str) -> ExtractedContent:
        """Extract text from PDF file or URL."""
        from pypdf import PdfReader

        if source.startswith(("http://", "https://")):
            pdf_bytes = await self._fetch_pdf(source)
            reader = PdfReader(io.BytesIO(pdf_bytes))
            metadata = {"url": source}
        else:
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"PDF file not found: {source}")
            reader = PdfReader(path)
            metadata = {"file": str(path.name)}

        # Extract metadata
        title = None
        if reader.metadata:
            title = reader.metadata.title
            if reader.metadata.author:
                metadata["author"] = reader.metadata.author
            if reader.metadata.subject:
                metadata["subject"] = reader.metadata.subject
            if reader.metadata.creator:
                metadata["creator"] = reader.metadata.creator

        metadata["pages"] = str(len(reader.pages))

        # Extract text from all pages
        text_parts = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"--- Page {i + 1} ---\n{page_text}")

        if not text_parts:
            raise ValueError(f"No text content found in PDF: {source}")

        content = "\n\n".join(text_parts)
        content = self._clean_text(content)

        return ExtractedContent(
            title=title,
            content=content,
            metadata=metadata,
        )

    @staticmethod
    async def _fetch_pdf(url: str) -> bytes:
        """Fetch PDF from URL."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=60, follow_redirects=True)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "pdf" not in content_type.lower() and not url.lower().endswith(".pdf"):
                raise ValueError(f"URL does not appear to be a PDF: {url}")
            return response.content

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean extracted PDF text."""
        # Remove excessive whitespace
        text = re.sub(r"[ \t]+", " ", text)
        # Normalize line breaks
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove page break artifacts
        text = re.sub(r"--- Page \d+ ---\s*\n\s*\n", "--- Page break ---\n\n", text)
        return text.strip()
