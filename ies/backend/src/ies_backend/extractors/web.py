"""Web article extraction using trafilatura."""

import re
from urllib.parse import urlparse

from .base import ExtractedContent


class WebExtractor:
    """Extract readable content from web pages."""

    URL_PATTERN = re.compile(r"^https?://")

    @staticmethod
    def can_handle(source: str) -> bool:
        """Check if source is a web URL (not YouTube/podcast)."""
        if not WebExtractor.URL_PATTERN.match(source):
            return False
        parsed = urlparse(source)
        host = parsed.netloc.lower()
        # Exclude YouTube and common podcast hosts
        excluded = {"youtube.com", "youtu.be", "www.youtube.com"}
        return host not in excluded

    async def extract(self, url: str) -> ExtractedContent:
        """Extract article content from URL."""
        import trafilatura

        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            raise ValueError(f"Failed to fetch URL: {url}")

        # Extract with metadata
        result = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            output_format="txt",
            with_metadata=True,
        )

        if not result:
            raise ValueError(f"Failed to extract content from: {url}")

        # trafilatura returns string when with_metadata=True and output_format=txt
        # Get metadata separately
        metadata_obj = trafilatura.extract_metadata(downloaded)

        title = None
        metadata: dict[str, str] = {"url": url}

        if metadata_obj:
            title = metadata_obj.title
            if metadata_obj.author:
                metadata["author"] = metadata_obj.author
            if metadata_obj.date:
                metadata["date"] = metadata_obj.date
            if metadata_obj.sitename:
                metadata["site"] = metadata_obj.sitename
            if metadata_obj.description:
                metadata["description"] = metadata_obj.description

        return ExtractedContent(
            title=title,
            content=result,
            metadata=metadata,
        )
