"""
Text extraction from PDF and EPUB files.
"""

import re
from pathlib import Path
from dataclasses import dataclass
from typing import Iterator

import fitz  # pymupdf
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


@dataclass
class Section:
    """A section of extracted text with metadata."""
    title: str
    content: str
    source_file: str
    chapter: str | None = None
    page_start: int | None = None
    page_end: int | None = None


@dataclass
class ExtractedDocument:
    """Full extracted document with sections."""
    title: str
    author: str | None
    source_path: str
    sections: list[Section]

    @property
    def full_text(self) -> str:
        return "\n\n".join(s.content for s in self.sections)


def extract_pdf(path: Path) -> ExtractedDocument:
    """Extract text from PDF with structure preservation."""
    doc = fitz.open(path)

    # Get metadata
    metadata = doc.metadata
    title = metadata.get("title") or path.stem
    author = metadata.get("author")

    sections = []
    current_section = None
    current_content = []
    current_page_start = 0

    for page_num, page in enumerate(doc):
        text = page.get_text("text")

        # Simple heuristic: detect chapter/section headers
        # (lines that are short, possibly numbered, followed by content)
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect potential headers (customize based on book structure)
            is_header = (
                len(line) < 100 and
                (line.isupper() or
                 re.match(r'^(Chapter|CHAPTER|Part|PART|\d+\.|\d+\s)', line) or
                 re.match(r'^[IVX]+\.?\s', line))  # Roman numerals
            )

            if is_header and current_content:
                # Save previous section
                sections.append(Section(
                    title=current_section or "Introduction",
                    content="\n".join(current_content),
                    source_file=str(path),
                    chapter=current_section,
                    page_start=current_page_start,
                    page_end=page_num
                ))
                current_content = []
                current_section = line
                current_page_start = page_num
            else:
                current_content.append(line)

    # Don't forget last section
    if current_content:
        sections.append(Section(
            title=current_section or "Content",
            content="\n".join(current_content),
            source_file=str(path),
            chapter=current_section,
            page_start=current_page_start,
            page_end=len(doc) - 1
        ))

    doc.close()

    return ExtractedDocument(
        title=title,
        author=author,
        source_path=str(path),
        sections=sections
    )


def extract_epub(path: Path) -> ExtractedDocument:
    """Extract text from EPUB with chapter structure."""
    try:
        book = epub.read_epub(str(path))
    except AttributeError:
        # Handle malformed NCX - read EPUB without parsing navigation
        import zipfile
        from io import BytesIO

        # Manually extract content without relying on NCX
        book = epub.EpubBook()
        with zipfile.ZipFile(str(path)) as zf:
            # Try to read metadata from content.opf
            opf_files = [f for f in zf.namelist() if f.endswith('.opf')]
            if opf_files:
                opf_content = zf.read(opf_files[0])
                soup = BeautifulSoup(opf_content, 'xml')

                # Extract title
                title_elem = soup.find('dc:title')
                if title_elem:
                    book.set_title(title_elem.get_text())

                # Extract author
                creator_elem = soup.find('dc:creator')
                if creator_elem:
                    book.add_author(creator_elem.get_text())

            # Read all HTML/XHTML content files
            for filename in zf.namelist():
                if filename.endswith(('.html', '.xhtml', '.htm')):
                    content = zf.read(filename)
                    # Decode if needed
                    if isinstance(content, bytes):
                        try:
                            content = content.decode('utf-8')
                        except UnicodeDecodeError:
                            try:
                                content = content.decode('latin-1')
                            except:
                                continue  # Skip if we can't decode
                    item = epub.EpubHtml(
                        title=filename,
                        file_name=filename,
                        content=content
                    )
                    book.add_item(item)

    # Get metadata
    title = book.get_metadata("DC", "title")
    title = title[0][0] if title else path.stem

    author = book.get_metadata("DC", "creator")
    author = author[0][0] if author else None

    sections = []

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # Parse HTML content
            soup = BeautifulSoup(item.get_content(), "html.parser")

            # Try to find chapter title
            chapter_title = None
            for tag in ["h1", "h2", "h3", "title"]:
                header = soup.find(tag)
                if header:
                    chapter_title = header.get_text().strip()
                    break

            # Get text content
            text = soup.get_text(separator="\n", strip=True)

            if text.strip():
                sections.append(Section(
                    title=chapter_title or item.get_name(),
                    content=text,
                    source_file=str(path),
                    chapter=chapter_title
                ))

    return ExtractedDocument(
        title=title,
        author=author,
        source_path=str(path),
        sections=sections
    )


def extract_document(path: Path) -> ExtractedDocument:
    """Extract document based on file type."""
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return extract_pdf(path)
    elif suffix == ".epub":
        return extract_epub(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def extract_all(directory: Path) -> Iterator[ExtractedDocument]:
    """Extract all documents from a directory."""
    for path in directory.iterdir():
        if path.suffix.lower() in [".pdf", ".epub"]:
            try:
                yield extract_document(path)
            except Exception as e:
                print(f"Error extracting {path}: {e}")
