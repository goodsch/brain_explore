"""Graph service for Layer 3 exploration.

Provides knowledge graph operations using the existing Neo4j client.
This is a backend-specific implementation that doesn't depend on library/.
"""

from ies_backend.services.neo4j_client import Neo4jClient


class GraphService:
    """Service for knowledge graph exploration operations."""

    @staticmethod
    async def find_related_concepts(concept: str, depth: int = 2) -> dict:
        """Find concepts related to a given concept.

        Uses APOC path expansion to find related nodes up to specified depth.
        Falls back to simpler query if APOC not available.
        """
        # Try APOC-based query first (more powerful)
        apoc_query = """
        MATCH (c {name: $name})
        CALL apoc.path.subgraphAll(c, {
            maxLevel: $depth,
            relationshipFilter: "COMPONENT_OF|SUPPORTS|OPERATIONALIZES|DEVELOPS|RELATED_TO"
        })
        YIELD nodes, relationships
        RETURN nodes, relationships
        """

        try:
            results = await Neo4jClient.execute_query(
                apoc_query, {"name": concept, "depth": depth}
            )

            if results and len(results) > 0:
                record = results[0]
                return {
                    "nodes": [dict(n) for n in record.get("nodes", [])],
                    "relationships": [
                        {
                            "type": r.type if hasattr(r, "type") else r.get("type", "RELATED_TO"),
                            "start": r.start_node["name"] if hasattr(r, "start_node") else r.get("start", ""),
                            "end": r.end_node["name"] if hasattr(r, "end_node") else r.get("end", ""),
                        }
                        for r in record.get("relationships", [])
                    ],
                }
        except Exception:
            pass  # Fall through to simpler query

        # Fallback: simpler query without APOC
        simple_query = """
        MATCH (c {name: $name})-[r]-(related)
        RETURN DISTINCT related.name as name, labels(related) as labels, type(r) as rel_type,
               c.name as from_name
        LIMIT 50
        """

        try:
            results = await Neo4jClient.execute_query(simple_query, {"name": concept})

            nodes = []
            relationships = []
            seen_names = set()

            for r in results:
                name = r.get("name")
                if name and name not in seen_names:
                    seen_names.add(name)
                    nodes.append({
                        "name": name,
                        "labels": r.get("labels", []),
                    })
                    relationships.append({
                        "start": r.get("from_name", concept),
                        "type": r.get("rel_type", "RELATED_TO"),
                        "end": name,
                    })

            return {"nodes": nodes, "relationships": relationships}
        except Exception as e:
            return {"nodes": [], "relationships": [], "error": str(e)}

    @staticmethod
    async def find_supporting_chunks(entity_name: str, limit: int = 10) -> list[dict]:
        """Find chunks that mention an entity."""
        query = """
        MATCH (c:Chunk)-[:MENTIONS]->(e {name: $name})
        OPTIONAL MATCH (c)-[:FROM_BOOK]->(b:Book)
        RETURN c.id as chunk_id, c.content as content,
               b.title as book_title, b.author as book_author
        LIMIT $limit
        """

        try:
            results = await Neo4jClient.execute_query(
                query, {"name": entity_name, "limit": limit}
            )
            return [dict(r) for r in results]
        except Exception:
            return []

    @staticmethod
    async def get_stats() -> dict:
        """Get graph statistics."""
        node_query = """
        MATCH (n)
        RETURN labels(n)[0] as label, count(*) as count
        ORDER BY count DESC
        """

        rel_query = """
        MATCH ()-[r]->()
        RETURN type(r) as type, count(*) as count
        ORDER BY count DESC
        """

        try:
            node_results = await Neo4jClient.execute_query(node_query, {})
            rel_results = await Neo4jClient.execute_query(rel_query, {})

            node_counts = {r["label"]: r["count"] for r in node_results if r.get("label")}
            rel_counts = {r["type"]: r["count"] for r in rel_results if r.get("type")}

            return {
                "nodes": node_counts,
                "relationships": rel_counts,
            }
        except Exception as e:
            return {"nodes": {}, "relationships": {}, "error": str(e)}

    @staticmethod
    async def search_concepts(query: str, limit: int = 10) -> list[dict]:
        """Search for concepts by name (case-insensitive substring match)."""
        search_query = """
        MATCH (n)
        WHERE n.name IS NOT NULL AND toLower(n.name) CONTAINS toLower($query)
        RETURN DISTINCT n.name as name, labels(n) as labels
        ORDER BY size(n.name)
        LIMIT $limit
        """

        try:
            results = await Neo4jClient.execute_query(
                search_query, {"query": query, "limit": limit}
            )
            return [
                {
                    "name": r["name"],
                    "type": r["labels"][0] if r.get("labels") else "Unknown",
                    "labels": r.get("labels", []),
                }
                for r in results
            ]
        except Exception:
            return []

    @staticmethod
    async def get_most_connected(limit: int = 10) -> list[dict]:
        """Get the most connected concepts in the graph."""
        query = """
        MATCH (n)-[r]-()
        WHERE n.name IS NOT NULL
        WITH n, count(r) as connections
        ORDER BY connections DESC
        LIMIT $limit
        RETURN n.name as name, labels(n) as labels, connections
        """

        try:
            results = await Neo4jClient.execute_query(query, {"limit": limit})
            return [
                {
                    "name": r["name"],
                    "type": r["labels"][0] if r.get("labels") else "Unknown",
                    "connections": r["connections"],
                }
                for r in results
            ]
        except Exception:
            return []

    @staticmethod
    async def get_entities_by_book(
        book_hash: str,
        title: str | None = None,
        types: list[str] | None = None,
        limit: int = 500
    ) -> list[dict]:
        """Get all entities mentioned in a book.

        Args:
            book_hash: The book's file hash (used as identifier)
            title: Optional book title for fallback matching
            types: Optional list of entity types to filter by
            limit: Maximum entities to return

        Returns:
            List of entities with name, type, and mention_count
        """
        # Build type filter clause
        type_filter = ""
        if types:
            type_labels = " OR ".join([f"e:{t}" for t in types])
            type_filter = f"AND ({type_labels})"

        # Try to match by hash, path, or title
        # Books in Neo4j use 'path' and 'title' as identifiers, Readest uses file hash
        title_match = "OR toLower(b.title) CONTAINS toLower($title)" if title else ""
        query = f"""
        MATCH (b:Book)
        WHERE b.hash = $book_hash
           OR b.path CONTAINS $book_hash
           OR b.file_hash = $book_hash
           {title_match}
        WITH b
        MATCH (b)-[:MENTIONS]->(e)
        WHERE e.name IS NOT NULL {type_filter}
        WITH e, count(*) as mention_count
        RETURN DISTINCT e.name as name, labels(e)[0] as type, mention_count
        ORDER BY mention_count DESC
        LIMIT $limit
        """

        try:
            results = await Neo4jClient.execute_query(
                query, {"book_hash": book_hash, "title": title or "", "limit": limit}
            )
            return [
                {
                    "name": r["name"],
                    "type": r["type"] or "Concept",
                    "mention_count": r["mention_count"],
                }
                for r in results
            ]
        except Exception:
            return []

    @staticmethod
    async def get_entities_by_calibre_id(
        calibre_id: int,
        types: list[str] | None = None,
        limit: int = 500
    ) -> list[dict]:
        """Get all entities mentioned in a book by its Calibre ID.

        Args:
            calibre_id: The Calibre book ID (integer)
            types: Optional list of entity types to filter by
            limit: Maximum entities to return

        Returns:
            List of entities with name, type, and mention_count
        """
        # Build type filter clause
        type_filter = ""
        if types:
            type_labels = " OR ".join([f"e:{t}" for t in types])
            type_filter = f"AND ({type_labels})"

        query = f"""
        MATCH (b:Book)
        WHERE b.calibre_id = $calibre_id
        WITH b
        MATCH (b)-[:MENTIONS]->(e)
        WHERE e.name IS NOT NULL {type_filter}
        WITH e, count(*) as mention_count
        RETURN DISTINCT e.name as name, labels(e)[0] as type, mention_count
        ORDER BY mention_count DESC
        LIMIT $limit
        """

        try:
            results = await Neo4jClient.execute_query(
                query, {"calibre_id": calibre_id, "limit": limit}
            )
            return [
                {
                    "name": r["name"],
                    "type": r["type"] or "Concept",
                    "mention_count": r["mention_count"],
                }
                for r in results
            ]
        except Exception:
            return []

    @staticmethod
    async def get_all_book_entity_counts() -> dict[int, int]:
        """Get entity counts for all indexed books.

        Returns:
            Dict mapping calibre_id to entity count
        """
        query = """
        MATCH (b:Book)
        WHERE b.calibre_id IS NOT NULL
        WITH b
        OPTIONAL MATCH (b)-[:MENTIONS]->(e)
        WITH b.calibre_id as calibre_id, count(DISTINCT e) as entity_count
        WHERE entity_count > 0
        RETURN calibre_id, entity_count
        """

        try:
            results = await Neo4jClient.execute_query(query, {})
            return {r["calibre_id"]: r["entity_count"] for r in results}
        except Exception:
            return {}


    @staticmethod
    async def get_entity_details(name: str) -> dict | None:
        """Get detailed entity information for Flow Mode EntityFocus.

        Returns entity details, related concepts, and source book evidence.
        Works with any node type (Concept, Researcher, Theory, etc.).

        Args:
            name: Entity/concept name to look up

        Returns:
            Dict with name, type, description, related entities, and source books.
            Returns None if entity not found.
        """
        # Get entity node with properties
        entity_query = """
        MATCH (e {name: $name})
        RETURN e, labels(e) as labels
        LIMIT 1
        """

        try:
            entity_results = await Neo4jClient.execute_query(
                entity_query, {"name": name}
            )

            if not entity_results:
                return None

            entity = entity_results[0]["e"]
            labels = entity_results[0]["labels"]
            # Filter out generic labels, prefer specific type
            node_type = next(
                (l for l in labels if l not in ["Node", "Entity", "Base"]),
                labels[0] if labels else "Concept"
            )

            # Get related entities with relationship types
            related_query = """
            MATCH (e {name: $name})-[r]-(related)
            WHERE related.name IS NOT NULL
            RETURN DISTINCT related.name as name, labels(related) as labels,
                   type(r) as relationship
            LIMIT 20
            """
            related_results = await Neo4jClient.execute_query(
                related_query, {"name": name}
            )

            related = []
            for r in related_results:
                r_labels = r.get("labels", [])
                r_type = next(
                    (l for l in r_labels if l not in ["Node", "Entity", "Base"]),
                    r_labels[0] if r_labels else "Concept"
                )
                related.append({
                    "name": r["name"],
                    "type": r_type,
                    "relationship": r.get("relationship", "RELATED_TO"),
                })

            # Get source books with snippets
            sources_query = """
            MATCH (c:Chunk)-[:MENTIONS]->(e {name: $name})
            OPTIONAL MATCH (c)-[:FROM_BOOK]->(b:Book)
            RETURN b.title as title, b.author as author, c.content as snippet
            LIMIT 5
            """
            sources_results = await Neo4jClient.execute_query(
                sources_query, {"name": name}
            )

            source_books = []
            seen_books = set()
            for s in sources_results:
                title = s.get("title")
                if title and title not in seen_books:
                    seen_books.add(title)
                    source_books.append({
                        "title": title,
                        "author": s.get("author"),
                        "snippet": (s.get("snippet") or "")[:300],  # Truncate long snippets
                    })

            return {
                "name": entity.get("name", name),
                "type": node_type,
                "description": entity.get("description"),
                "related": related,
                "source_books": source_books,
            }

        except Exception as e:
            # Log but don't crash - return None for not found
            return None
