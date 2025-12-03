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
