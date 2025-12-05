#!/usr/bin/env python
"""Check ingestion status and show what's been processed."""

import sqlite3
from pathlib import Path
from neo4j import GraphDatabase
import os
from rich.console import Console
from rich.table import Table

console = Console()

# Database paths
calibre_db = Path("./calibre/library/metadata.db")
neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
neo4j_password = os.environ.get("NEO4J_PASSWORD", "brainexplore")

def get_calibre_books():
    """Get all books from Calibre."""
    with sqlite3.connect(calibre_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author_sort FROM books ORDER BY id")
        return cursor.fetchall()

def get_neo4j_status():
    """Get processing status from Neo4j."""
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    with driver.session() as session:
        result = session.run("""
            MATCH (b:Book)
            OPTIONAL MATCH (b)-[:MENTIONS]->(e)
            RETURN b.calibre_id as id, b.processing_status as status, count(distinct e) as entity_count
            ORDER BY b.calibre_id
        """)
        status_map = {r["id"]: (r["status"], r["entity_count"]) for r in result}
    driver.close()
    return status_map

def main():
    calibre_books = get_calibre_books()
    neo4j_status = get_neo4j_status()
    
    table = Table(title="Book Ingestion Status")
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Title", style="white", width=50)
    table.add_column("Status", style="yellow", width=20)
    table.add_column("Entities", style="green", width=10)
    
    for book_id, title, author in calibre_books:
        status, entity_count = neo4j_status.get(book_id, ("not started", 0))
        if len(title) > 47:
            title = title[:47] + "..."
        
        # Color code status
        if status == "entities_extracted":
            status_style = "[green]✓ extracted[/]"
        elif status == "pending":
            status_style = "[yellow]⏳ pending[/]"
        elif status == "error":
            status_style = "[red]✗ error[/]"
        else:
            status_style = "[gray]- not started[/]"
            
        table.add_row(
            str(book_id),
            title,
            status_style,
            str(entity_count) if entity_count > 0 else "-"
        )
    
    console.print(table)
    
    # Summary
    total = len(calibre_books)
    extracted = sum(1 for _, (s, _) in neo4j_status.items() if s == "entities_extracted")
    pending = sum(1 for _, (s, _) in neo4j_status.items() if s == "pending")
    
    console.print(f"\n[bold]Summary:[/] {extracted}/{total} books processed, {pending} pending")
    
    # Check if daemon is running
    import psutil
    daemon_running = any("auto_ingest_daemon" in " ".join(p.cmdline()) for p in psutil.process_iter(['cmdline']))
    if daemon_running:
        console.print("[green]✓ Auto-ingest daemon is running[/]")
    else:
        console.print("[yellow]⚠ Auto-ingest daemon is not running[/]")

if __name__ == "__main__":
    main()
