"""Tests for /books API endpoints."""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from unittest.mock import patch, MagicMock

from ies_backend.main import app
from ies_backend.schemas.calibre import Book


client = TestClient(app)


class TestListBooksEndpoint:
    """Tests for GET /books endpoint."""

    def test_list_books_returns_books(self):
        """GET /books should return list of books from Calibre."""
        mock_books = [
            Book(calibre_id=1, title="ADHD 2.0", author="Hallowell, Edward", path="/path"),
            Book(calibre_id=2, title="Driven to Distraction", author="Hallowell, Edward", path="/path2"),
        ]

        with patch("ies_backend.api.books.get_calibre_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.list_books.return_value = mock_books
            mock_get_service.return_value = mock_service

            response = client.get("/books")

            assert response.status_code == 200
            data = response.json()
            assert len(data["books"]) == 2
            assert data["books"][0]["calibre_id"] == 1
            assert data["books"][0]["title"] == "ADHD 2.0"

    def test_list_books_with_search_parameter(self):
        """GET /books?search=ADHD should filter books."""
        mock_books = [
            Book(calibre_id=1, title="ADHD 2.0", author="Hallowell, Edward", path="/path"),
        ]

        with patch("ies_backend.api.books.get_calibre_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.list_books.return_value = mock_books
            mock_get_service.return_value = mock_service

            response = client.get("/books?search=ADHD")

            assert response.status_code == 200
            mock_service.list_books.assert_called_once_with(search="ADHD", limit=100)


class TestGetBookEndpoint:
    """Tests for GET /books/{calibre_id} endpoint."""

    def test_get_book_returns_single_book(self):
        """GET /books/42 should return a single book."""
        mock_book = Book(
            calibre_id=42, title="Driven to Distraction", author="Hallowell, Edward", path="/path"
        )

        with patch("ies_backend.api.books.get_calibre_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_book.return_value = mock_book
            mock_get_service.return_value = mock_service

            response = client.get("/books/42")

            assert response.status_code == 200
            data = response.json()
            assert data["calibre_id"] == 42
            assert data["title"] == "Driven to Distraction"

    def test_get_book_returns_404_for_missing_book(self):
        """GET /books/99999 should return 404 when book not found."""
        with patch("ies_backend.api.books.get_calibre_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_book.return_value = None
            mock_get_service.return_value = mock_service

            response = client.get("/books/99999")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()


class TestGetBookCoverEndpoint:
    """Tests for GET /books/{calibre_id}/cover endpoint."""

    def test_get_cover_calls_service_with_calibre_id(self):
        """GET /books/42/cover should call service with correct ID."""
        with patch("ies_backend.api.books.get_calibre_service") as mock_get_service:
            mock_service = MagicMock()
            # Return None to trigger 404 (easier to test than mocking FileResponse)
            mock_service.get_cover_path.return_value = None
            mock_get_service.return_value = mock_service

            client.get("/books/42/cover")

            # Verify service was called with correct calibre_id
            mock_service.get_cover_path.assert_called_once_with(calibre_id=42)

    def test_get_cover_returns_404_when_no_cover(self):
        """GET /books/42/cover should return 404 when cover not found."""
        with patch("ies_backend.api.books.get_calibre_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_cover_path.return_value = None
            mock_get_service.return_value = mock_service

            response = client.get("/books/42/cover")

            assert response.status_code == 404
