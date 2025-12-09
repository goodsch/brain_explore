"""Hardcover API Service for book metadata enrichment.

Hardcover (hardcover.app) provides rich book metadata including:
- Descriptions and summaries
- Genre/subject tags (user-curated)
- Series information
- Author details
- Community statistics (read count, ratings)

Used in Pass 0 of ingestion pipeline to enrich Calibre books with
metadata before entity extraction.

API: GraphQL at https://api.hardcover.app/v1/graphql
Docs: https://docs.hardcover.app/api/getting-started/
Rate limit: 60 requests/minute
"""

import json
import logging
import os
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)

HARDCOVER_API_URL = "https://api.hardcover.app/v1/graphql"
HARDCOVER_API_TOKEN = os.getenv("HARDCOVER_API_TOKEN")


@dataclass
class HardcoverBook:
    """Book metadata from Hardcover."""

    hardcover_id: int
    title: str
    slug: str
    description: str | None = None
    pages: int | None = None
    release_year: int | None = None
    authors: list[str] | None = None
    genres: list[str] | None = None
    subjects: list[str] | None = None
    series_name: str | None = None
    series_position: int | None = None
    users_read_count: int = 0
    rating: float | None = None
    isbn_10: str | None = None
    isbn_13: str | None = None
    image_url: str | None = None


class HardcoverService:
    """Service for interacting with Hardcover GraphQL API."""

    def __init__(self, api_token: str | None = None):
        """Initialize with API token.

        Args:
            api_token: Hardcover Bearer token. Falls back to HARDCOVER_API_TOKEN env var.
        """
        self.api_token = api_token or HARDCOVER_API_TOKEN
        if not self.api_token:
            logger.warning("No Hardcover API token provided. Set HARDCOVER_API_TOKEN env var.")

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with auth."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}",
        }

    async def _execute_query(self, query: str, variables: dict | None = None) -> dict[str, Any]:
        """Execute a GraphQL query against Hardcover API.

        Args:
            query: GraphQL query string
            variables: Optional query variables

        Returns:
            Response data dict

        Raises:
            httpx.HTTPError: On request failure
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                HARDCOVER_API_URL,
                headers=self._get_headers(),
                json=payload,
            )
            response.raise_for_status()
            result = response.json()

            if "errors" in result:
                logger.error(f"GraphQL errors: {result['errors']}")
                raise ValueError(f"GraphQL error: {result['errors'][0].get('message', 'Unknown error')}")

            return result.get("data", {})

    async def search_books(
        self,
        query: str,
        limit: int = 10,
        sort: str = "users_read_count:desc",
    ) -> list[dict]:
        """Search for books by title/author.

        Args:
            query: Search query (title, author, ISBN)
            limit: Max results (default 10)
            sort: Sort order (default by popularity)

        Returns:
            List of search result dicts with book data
        """
        gql_query = """
        query SearchBooks($query: String!, $limit: Int!, $sort: String!) {
            search(
                query: $query,
                query_type: "books",
                per_page: $limit,
                page: 1,
                sort: $sort
            ) {
                results
            }
        }
        """

        try:
            data = await self._execute_query(
                gql_query,
                {"query": query, "limit": limit, "sort": sort},
            )
            results_data = data.get("search", {}).get("results", {})

            # Parse JSON string if needed (Hardcover returns stringified JSON)
            if isinstance(results_data, str):
                results_data = json.loads(results_data)

            # Extract documents from hits array
            if isinstance(results_data, dict):
                hits = results_data.get("hits", [])
                return [hit.get("document", hit) for hit in hits]

            return results_data if isinstance(results_data, list) else []

        except Exception as e:
            logger.error(f"Book search failed for '{query}': {e}")
            return []

    async def get_book_by_id(self, book_id: int) -> HardcoverBook | None:
        """Get detailed book metadata by Hardcover ID.

        Args:
            book_id: Hardcover book ID

        Returns:
            HardcoverBook with full metadata, or None if not found
        """
        gql_query = """
        query GetBook($id: Int!) {
            books_by_pk(id: $id) {
                id
                title
                slug
                description
                pages
                release_year
                cached_contributors
                cached_tags
                users_read_count
                rating
                image {
                    url
                }
                editions {
                    isbn_10
                    isbn_13
                }
                book_series {
                    position
                    series {
                        name
                    }
                }
            }
        }
        """

        try:
            data = await self._execute_query(gql_query, {"id": book_id})
            book_data = data.get("books_by_pk")

            if not book_data:
                return None

            return self._parse_book(book_data)

        except Exception as e:
            logger.error(f"Failed to get book {book_id}: {e}")
            return None

    async def search_and_match(
        self,
        title: str,
        author: str | None = None,
    ) -> HardcoverBook | None:
        """Search for a book and return the best match.

        Args:
            title: Book title to search
            author: Optional author name for better matching

        Returns:
            Best matching HardcoverBook or None
        """
        # Build search query
        search_query = title
        if author:
            # Clean author name (remove initials like "B. F.")
            clean_author = author.split(",")[0].strip()  # Take first author
            search_query = f"{title} {clean_author}"

        results = await self.search_books(search_query, limit=5)

        if not results:
            # Try title-only search as fallback
            if author:
                results = await self.search_books(title, limit=5)

        if not results:
            return None

        # Find best match by title similarity
        best_match = None
        best_score = 0.0

        title_lower = title.lower()
        for result in results:
            result_title = (result.get("title") or "").lower()

            # Simple similarity score
            score = self._title_similarity(title_lower, result_title)

            # Boost if author matches
            if author:
                result_authors = result.get("author_names", [])
                if isinstance(result_authors, str):
                    result_authors = [result_authors]
                author_lower = author.lower()
                for ra in result_authors:
                    if author_lower in ra.lower() or ra.lower() in author_lower:
                        score += 0.3
                        break

            if score > best_score:
                best_score = score
                best_match = result

        if best_match and best_score >= 0.5:
            # Parse the search result into HardcoverBook
            return self._parse_search_result(best_match)

        return None

    def _title_similarity(self, a: str, b: str) -> float:
        """Calculate simple title similarity score (0-1)."""
        # Normalize
        a = a.lower().strip()
        b = b.lower().strip()

        if a == b:
            return 1.0

        # Check if one contains the other
        if a in b or b in a:
            return 0.8

        # Word overlap
        words_a = set(a.split())
        words_b = set(b.split())

        if not words_a or not words_b:
            return 0.0

        intersection = words_a & words_b
        union = words_a | words_b

        return len(intersection) / len(union)

    def _parse_book(self, data: dict) -> HardcoverBook:
        """Parse full book data from books_by_pk query."""
        # Extract authors from cached_contributors
        authors = []
        contributors = data.get("cached_contributors") or {}
        if isinstance(contributors, str):
            try:
                contributors = json.loads(contributors)
            except json.JSONDecodeError:
                contributors = {}

        for contrib in contributors.get("author", []):
            if isinstance(contrib, dict):
                authors.append(contrib.get("name", ""))
            elif isinstance(contrib, str):
                authors.append(contrib)

        # Extract genres/tags
        tags_data = data.get("cached_tags") or {}
        if isinstance(tags_data, str):
            try:
                tags_data = json.loads(tags_data)
            except json.JSONDecodeError:
                tags_data = {}

        genres = []
        subjects = []
        for tag in tags_data.get("Genre", []):
            genres.append(tag.get("tag", "") if isinstance(tag, dict) else str(tag))
        for tag in tags_data.get("Subject", []):
            subjects.append(tag.get("tag", "") if isinstance(tag, dict) else str(tag))

        # Extract series info
        series_name = None
        series_position = None
        book_series = data.get("book_series", [])
        if book_series:
            first_series = book_series[0]
            series_name = first_series.get("series", {}).get("name")
            series_position = first_series.get("position")

        # Extract ISBN from editions
        isbn_10 = None
        isbn_13 = None
        editions = data.get("editions", [])
        for ed in editions:
            if ed.get("isbn_13") and not isbn_13:
                isbn_13 = ed["isbn_13"]
            if ed.get("isbn_10") and not isbn_10:
                isbn_10 = ed["isbn_10"]

        # Image URL
        image_url = None
        image = data.get("image")
        if image:
            image_url = image.get("url")

        return HardcoverBook(
            hardcover_id=data["id"],
            title=data.get("title", ""),
            slug=data.get("slug", ""),
            description=data.get("description"),
            pages=data.get("pages"),
            release_year=data.get("release_year"),
            authors=authors if authors else None,
            genres=genres if genres else None,
            subjects=subjects if subjects else None,
            series_name=series_name,
            series_position=series_position,
            users_read_count=data.get("users_read_count", 0),
            rating=data.get("rating"),
            isbn_10=isbn_10,
            isbn_13=isbn_13,
            image_url=image_url,
        )

    def _parse_search_result(self, data: dict) -> HardcoverBook:
        """Parse book data from search result."""
        # Search results have different structure than full book query

        # Authors from search
        authors = data.get("author_names", [])
        if isinstance(authors, str):
            authors = [authors]

        # Tags from search (may be combined)
        genres = []
        tags = data.get("cached_tags") or data.get("tags") or []
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except json.JSONDecodeError:
                tags = []

        if isinstance(tags, dict):
            for tag_list in tags.values():
                if isinstance(tag_list, list):
                    for t in tag_list:
                        tag_name = t.get("tag", "") if isinstance(t, dict) else str(t)
                        if tag_name:
                            genres.append(tag_name)

        # Series from search
        series_names = data.get("series_names", [])
        series_name = series_names[0] if series_names else None

        return HardcoverBook(
            hardcover_id=data.get("id", 0),
            title=data.get("title", ""),
            slug=data.get("slug", ""),
            description=data.get("description"),
            pages=data.get("pages"),
            release_year=data.get("release_year"),
            authors=authors if authors else None,
            genres=genres if genres else None,
            subjects=None,  # Not in search results
            series_name=series_name,
            series_position=None,  # Not in search results
            users_read_count=data.get("users_read_count", 0),
            rating=data.get("rating"),
            isbn_10=None,
            isbn_13=None,
            image_url=data.get("image_url"),
        )


# Convenience function for direct use
async def enrich_book_metadata(title: str, author: str | None = None) -> HardcoverBook | None:
    """Search Hardcover and return enriched metadata for a book.

    Args:
        title: Book title
        author: Optional author name

    Returns:
        HardcoverBook with metadata or None if not found
    """
    service = HardcoverService()
    return await service.search_and_match(title, author)
