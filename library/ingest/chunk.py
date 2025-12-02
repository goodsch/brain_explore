"""
Semantic chunking for extracted documents.

Chunks text while preserving semantic boundaries (paragraphs, sections)
rather than arbitrary token limits.
"""

import re
from dataclasses import dataclass
from typing import Iterator

import tiktoken

from .extract import ExtractedDocument, Section


@dataclass
class Chunk:
    """A chunk of text ready for embedding."""
    id: str
    content: str
    token_count: int
    metadata: dict

    def __repr__(self):
        return f"Chunk({self.id}, {self.token_count} tokens)"


class SemanticChunker:
    """Chunks documents while respecting semantic boundaries."""

    def __init__(
        self,
        max_tokens: int = 512,
        overlap_tokens: int = 50,
        model: str = "cl100k_base"  # OpenAI's tokenizer
    ):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.tokenizer = tiktoken.get_encoding(model)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.tokenizer.encode(text))

    def split_into_paragraphs(self, text: str) -> list[str]:
        """Split text into paragraphs."""
        # Split on double newlines or multiple newlines
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]

    def chunk_section(self, section: Section, doc_id: str) -> Iterator[Chunk]:
        """Chunk a single section into semantic chunks."""
        paragraphs = self.split_into_paragraphs(section.content)

        current_chunk = []
        current_tokens = 0
        chunk_index = 0

        for para in paragraphs:
            para_tokens = self.count_tokens(para)

            # If single paragraph exceeds max, split it further
            if para_tokens > self.max_tokens:
                # First, yield current chunk if any
                if current_chunk:
                    yield self._make_chunk(
                        current_chunk, section, doc_id, chunk_index
                    )
                    chunk_index += 1
                    current_chunk = []
                    current_tokens = 0

                # Split large paragraph by sentences
                for sub_chunk in self._split_large_text(para):
                    yield self._make_chunk(
                        [sub_chunk], section, doc_id, chunk_index
                    )
                    chunk_index += 1
                continue

            # Check if adding this paragraph would exceed limit
            if current_tokens + para_tokens > self.max_tokens and current_chunk:
                # Yield current chunk
                yield self._make_chunk(
                    current_chunk, section, doc_id, chunk_index
                )
                chunk_index += 1

                # Start new chunk with overlap
                overlap_text = self._get_overlap(current_chunk)
                current_chunk = [overlap_text] if overlap_text else []
                current_tokens = self.count_tokens(overlap_text) if overlap_text else 0

            current_chunk.append(para)
            current_tokens += para_tokens

        # Yield final chunk
        if current_chunk:
            yield self._make_chunk(
                current_chunk, section, doc_id, chunk_index
            )

    def _split_large_text(self, text: str) -> Iterator[str]:
        """Split large text by sentences when paragraph is too big."""
        sentences = re.split(r'(?<=[.!?])\s+', text)

        current = []
        current_tokens = 0

        for sentence in sentences:
            sent_tokens = self.count_tokens(sentence)

            if current_tokens + sent_tokens > self.max_tokens and current:
                yield " ".join(current)
                current = []
                current_tokens = 0

            current.append(sentence)
            current_tokens += sent_tokens

        if current:
            yield " ".join(current)

    def _get_overlap(self, chunks: list[str]) -> str:
        """Get overlap text from end of chunks."""
        full_text = " ".join(chunks)
        tokens = self.tokenizer.encode(full_text)

        if len(tokens) <= self.overlap_tokens:
            return full_text

        overlap_tokens = tokens[-self.overlap_tokens:]
        return self.tokenizer.decode(overlap_tokens)

    def _make_chunk(
        self,
        paragraphs: list[str],
        section: Section,
        doc_id: str,
        index: int
    ) -> Chunk:
        """Create a Chunk object."""
        content = "\n\n".join(paragraphs)
        chunk_id = f"{doc_id}:{section.title}:{index}"

        return Chunk(
            id=chunk_id,
            content=content,
            token_count=self.count_tokens(content),
            metadata={
                "source_file": section.source_file,
                "chapter": section.chapter,
                "section_title": section.title,
                "page_start": section.page_start,
                "page_end": section.page_end,
                "chunk_index": index
            }
        )

    def chunk_document(self, doc: ExtractedDocument) -> Iterator[Chunk]:
        """Chunk an entire document."""
        # Create a doc ID from title
        doc_id = re.sub(r'[^\w\s-]', '', doc.title).strip().replace(' ', '_')[:50]

        for section in doc.sections:
            yield from self.chunk_section(section, doc_id)


def chunk_document(
    doc: ExtractedDocument,
    max_tokens: int = 512,
    overlap: int = 50
) -> list[Chunk]:
    """Convenience function to chunk a document."""
    chunker = SemanticChunker(max_tokens=max_tokens, overlap_tokens=overlap)
    return list(chunker.chunk_document(doc))
