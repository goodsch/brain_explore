#!/usr/bin/env python3
"""
Match existing Neo4j Book nodes to Calibre books and add calibre_id property.

This is a one-time migration script to enable entity lookup by calibre_id.
"""

import sqlite3
from difflib import SequenceMatcher
from typing import Optional
import requests


# Configuration
CALIBRE_DB = "/home/chris/Documents/calibre/metadata.db"
NEO4J_URL = "http://localhost:7474/db/neo4j/query/v2"
NEO4J_AUTH = ("neo4j", "brainexplore")
MATCH_THRESHOLD = 0.7  # Minimum similarity for auto-match


def get_calibre_books() -> list[dict]:
    """Get all books from Calibre database."""
    conn = sqlite3.connect(CALIBRE_DB)
    cursor = conn.execute(
        "SELECT id, title, author_sort FROM books ORDER BY title"
    )
    books = [
        {"id": row[0], "title": row[1], "author": row[2]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return books


def get_neo4j_books() -> list[dict]:
    """Get all Book nodes from Neo4j."""
    response = requests.post(
        NEO4J_URL,
        auth=NEO4J_AUTH,
        json={"statement": "MATCH (b:Book) RETURN b.title, b.author, b.path, elementId(b) as id"},
    )
    data = response.json()["data"]
    return [
        {
            "title": row[0],
            "author": row[1],
            "path": row[2],
            "element_id": row[3],
        }
        for row in data["values"]
    ]


def normalize_title(title: str) -> str:
    """Normalize title for comparison."""
    if not title:
        return ""
    # Remove common subtitle patterns and punctuation
    title = title.lower()
    for sep in [":", "-", "—", "–"]:
        if sep in title:
            title = title.split(sep)[0]
    return title.strip()


def similarity(s1: str, s2: str) -> float:
    """Calculate string similarity (0-1)."""
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()


def find_best_match(neo4j_book: dict, calibre_books: list[dict]) -> Optional[dict]:
    """Find the best matching Calibre book for a Neo4j book."""
    neo4j_title = normalize_title(neo4j_book.get("title", ""))
    if not neo4j_title:
        return None

    best_match = None
    best_score = 0

    for calibre_book in calibre_books:
        calibre_title = normalize_title(calibre_book["title"])
        score = similarity(neo4j_title, calibre_title)

        # Boost score if authors match
        neo4j_author = (neo4j_book.get("author") or "").lower()
        calibre_author = (calibre_book.get("author") or "").lower()
        if neo4j_author and calibre_author:
            # Check if any author name appears in both
            neo4j_parts = set(neo4j_author.replace(",", " ").split())
            calibre_parts = set(calibre_author.replace(",", " ").split())
            if neo4j_parts & calibre_parts:  # Intersection
                score += 0.1

        if score > best_score:
            best_score = score
            best_match = {**calibre_book, "score": score}

    if best_match and best_match["score"] >= MATCH_THRESHOLD:
        return best_match
    return None


def update_neo4j_book(element_id: str, calibre_id: int) -> bool:
    """Update a Neo4j Book node with calibre_id."""
    response = requests.post(
        NEO4J_URL,
        auth=NEO4J_AUTH,
        json={
            "statement": f"MATCH (b:Book) WHERE elementId(b) = $id SET b.calibre_id = $calibre_id RETURN b.title",
            "parameters": {"id": element_id, "calibre_id": calibre_id}
        },
    )
    return response.status_code == 200


def main():
    print("Loading Calibre books...")
    calibre_books = get_calibre_books()
    print(f"Found {len(calibre_books)} books in Calibre")

    print("\nLoading Neo4j books...")
    neo4j_books = get_neo4j_books()
    print(f"Found {len(neo4j_books)} books in Neo4j")

    # Track matches
    matched = []
    unmatched = []

    print("\nMatching books...")
    for neo4j_book in neo4j_books:
        match = find_best_match(neo4j_book, calibre_books)
        if match:
            matched.append((neo4j_book, match))
        else:
            unmatched.append(neo4j_book)

    # Show matches for review
    print(f"\n=== MATCHED ({len(matched)}) ===")
    for neo4j_book, calibre_match in matched:
        print(f"\nNeo4j:   {neo4j_book['title'][:60]}")
        print(f"Calibre: {calibre_match['title'][:60]}")
        print(f"Score:   {calibre_match['score']:.2f}, calibre_id: {calibre_match['id']}")

    print(f"\n=== UNMATCHED ({len(unmatched)}) ===")
    for book in unmatched:
        print(f"  - {book['title'][:70]}")

    # Prompt for confirmation
    print(f"\n{len(matched)} books will be updated with calibre_id.")
    confirm = input("Proceed? (y/n): ").strip().lower()

    if confirm == "y":
        print("\nUpdating Neo4j...")
        success = 0
        for neo4j_book, calibre_match in matched:
            if update_neo4j_book(neo4j_book["element_id"], calibre_match["id"]):
                success += 1
                print(f"  Updated: {neo4j_book['title'][:50]}")
            else:
                print(f"  FAILED:  {neo4j_book['title'][:50]}")
        print(f"\nDone! Updated {success}/{len(matched)} books.")
    else:
        print("Aborted.")


if __name__ == "__main__":
    main()
