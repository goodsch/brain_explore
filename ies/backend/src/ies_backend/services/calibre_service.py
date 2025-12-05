"""Service for querying Calibre metadata.db."""

import sqlite3
from pathlib import Path

from ies_backend.schemas.calibre import Book


class CalibreService:
    """Query the Calibre library metadata database."""

    def __init__(self, library_path: Path):
        """Initialize with path to Calibre library folder."""
        self.library_path = library_path
        self.db_path = library_path / "metadata.db"

    def list_books(self, search: str | None = None, limit: int = 100) -> list[Book]:
        """List books from the Calibre library.

        Args:
            search: Optional search string to filter by title or author
            limit: Maximum number of books to return

        Returns:
            List of Book objects
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if search:
                query = """
                    SELECT id, title, author_sort, path
                    FROM books
                    WHERE title LIKE ? OR author_sort LIKE ?
                    ORDER BY title
                    LIMIT ?
                """
                search_pattern = f"%{search}%"
                cursor.execute(query, (search_pattern, search_pattern, limit))
            else:
                query = """
                    SELECT id, title, author_sort, path
                    FROM books
                    ORDER BY title
                    LIMIT ?
                """
                cursor.execute(query, (limit,))

            rows = cursor.fetchall()

        return [
            Book(calibre_id=row[0], title=row[1], author=row[2], path=row[3])
            for row in rows
        ]

    def get_book(self, calibre_id: int) -> Book | None:
        """Get a single book by its Calibre ID.

        Args:
            calibre_id: The Calibre book ID

        Returns:
            Book object or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, author_sort, path FROM books WHERE id = ?",
                (calibre_id,),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return Book(calibre_id=row[0], title=row[1], author=row[2], path=row[3])

    def get_cover_path(self, calibre_id: int) -> Path | None:
        """Get the path to a book's cover image.

        Args:
            calibre_id: The Calibre book ID

        Returns:
            Path to cover.jpg or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM books WHERE id = ?", (calibre_id,))
            row = cursor.fetchone()

        if row is None:
            return None

        cover_path = self.library_path / row[0] / "cover.jpg"
        if cover_path.exists():
            return cover_path
        return None

    def get_book_file_path(self, calibre_id: int) -> Path | None:
        """Get the path to a book's epub/pdf file.

        Args:
            calibre_id: The Calibre book ID

        Returns:
            Path to the book file or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM books WHERE id = ?", (calibre_id,))
            row = cursor.fetchone()

        if row is None:
            return None

        book_dir = self.library_path / row[0]
        if not book_dir.exists():
            return None

        # Look for epub first, then pdf
        for ext in [".epub", ".pdf"]:
            for file in book_dir.iterdir():
                if file.suffix.lower() == ext:
                    return file

        return None
