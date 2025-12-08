"""Base types for content extraction."""

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class ExtractedContent:
    """Result of content extraction."""

    title: str | None
    content: str
    metadata: dict[str, str] = field(default_factory=dict)


class ContentExtractor(Protocol):
    """Protocol for content extractors."""

    async def extract(self, source: str) -> ExtractedContent:
        """Extract content from source (URL, file path, or raw input)."""
        ...

    @staticmethod
    def can_handle(source: str) -> bool:
        """Check if this extractor can handle the given source."""
        ...
