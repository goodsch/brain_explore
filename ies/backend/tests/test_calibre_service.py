"""Tests for CalibreService - queries Calibre metadata.db."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from ies_backend.services.calibre_service import CalibreService
from ies_backend.schemas.calibre import Book


class TestCalibreServiceListBooks:
    """Tests for listing books from Calibre."""

    def test_list_books_returns_books_from_metadata_db(self):
        """List books should return Book objects from Calibre metadata.db."""
        # Arrange: Mock sqlite connection to return test data
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, "Taking Charge of Adult ADHD", "Barkley, Russell A.", "/path/to/book.epub"),
            (2, "Driven to Distraction", "Hallowell, Edward M.", "/path/to/book2.epub"),
        ]
        mock_cursor.description = [("id",), ("title",), ("author_sort",), ("path",)]

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=False)

        with patch("sqlite3.connect", return_value=mock_connection):
            service = CalibreService(library_path=Path("/calibre-library"))

            # Act
            books = service.list_books()

            # Assert
            assert len(books) == 2
            assert isinstance(books[0], Book)
            assert books[0].calibre_id == 1
            assert books[0].title == "Taking Charge of Adult ADHD"
            assert books[0].author == "Barkley, Russell A."

    def test_list_books_with_search_filters_by_title_or_author(self):
        """Search parameter should filter books by title or author."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, "Taking Charge of Adult ADHD", "Barkley, Russell A.", "/path/to/book.epub"),
        ]
        mock_cursor.description = [("id",), ("title",), ("author_sort",), ("path",)]

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=False)

        with patch("sqlite3.connect", return_value=mock_connection):
            service = CalibreService(library_path=Path("/calibre-library"))

            # Act
            books = service.list_books(search="ADHD")

            # Assert: Verify search was passed to query
            call_args = mock_cursor.execute.call_args
            assert "LIKE" in call_args[0][0]  # SQL should contain LIKE for search


class TestCalibreServiceGetBook:
    """Tests for getting a single book by ID."""

    def test_get_book_returns_book_by_calibre_id(self):
        """Get book should return a single Book by calibre_id."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (
            42, "Driven to Distraction", "Hallowell, Edward M.", "/path/to/book.epub"
        )

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=False)

        with patch("sqlite3.connect", return_value=mock_connection):
            service = CalibreService(library_path=Path("/calibre-library"))

            # Act
            book = service.get_book(calibre_id=42)

            # Assert
            assert book is not None
            assert book.calibre_id == 42
            assert book.title == "Driven to Distraction"

    def test_get_book_returns_none_for_missing_id(self):
        """Get book should return None when book not found."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=False)

        with patch("sqlite3.connect", return_value=mock_connection):
            service = CalibreService(library_path=Path("/calibre-library"))

            # Act
            book = service.get_book(calibre_id=99999)

            # Assert
            assert book is None


class TestCalibreServiceGetCover:
    """Tests for getting book cover image."""

    def test_get_cover_returns_cover_path(self):
        """Get cover should return path to cover.jpg in book folder."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("Author Name/Book Title (42)",)

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=False)

        with patch("sqlite3.connect", return_value=mock_connection):
            with patch("pathlib.Path.exists", return_value=True):
                service = CalibreService(library_path=Path("/calibre-library"))

                # Act
                cover_path = service.get_cover_path(calibre_id=42)

                # Assert
                assert cover_path is not None
                assert "cover.jpg" in str(cover_path)

    def test_get_cover_returns_none_when_no_cover(self):
        """Get cover should return None when cover.jpg doesn't exist."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("Author Name/Book Title (42)",)

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=False)

        with patch("sqlite3.connect", return_value=mock_connection):
            with patch("pathlib.Path.exists", return_value=False):
                service = CalibreService(library_path=Path("/calibre-library"))

                # Act
                cover_path = service.get_cover_path(calibre_id=42)

                # Assert
                assert cover_path is None
