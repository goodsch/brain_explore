"""
Neo4j knowledge graph client.

Schema:
- (:Researcher {name, description})
- (:Concept {name, description, aliases})
- (:Theory {name, description, aliases})
- (:Assessment {name, description, aliases})
- (:Book {title, author, path})
- (:Chunk {id, content})

Relationships:
- (Researcher)-[:CITES]->(Researcher)
- (Researcher)-[:DEVELOPS]->(Theory|Concept)
- (Chunk)-[:SUPPORTS]->(Concept|Theory)
- (Chunk)-[:CONTRADICTS]->(Concept|Theory)
- (Assessment)-[:OPERATIONALIZES]->(Concept)
- (Concept)-[:COMPONENT_OF]->(Theory|Concept)
- (Chunk)-[:FROM_BOOK]->(Book)
- (Chunk)-[:MENTIONS]->(Entity)
"""

from neo4j import GraphDatabase
from typing import Optional

from .entities import Entity, Relationship, ExtractionResult


class KnowledgeGraph:
    """Neo4j knowledge graph operations."""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "brainexplore"
    ):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._ensure_schema()

    def close(self):
        self.driver.close()

    def _ensure_schema(self):
        """Create indexes and constraints."""
        with self.driver.session() as session:
            # Create constraints for unique names
            constraints = [
                "CREATE CONSTRAINT researcher_name IF NOT EXISTS FOR (r:Researcher) REQUIRE r.name IS UNIQUE",
                "CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE",
                "CREATE CONSTRAINT theory_name IF NOT EXISTS FOR (t:Theory) REQUIRE t.name IS UNIQUE",
                "CREATE CONSTRAINT assessment_name IF NOT EXISTS FOR (a:Assessment) REQUIRE a.name IS UNIQUE",
                "CREATE CONSTRAINT book_path IF NOT EXISTS FOR (b:Book) REQUIRE b.path IS UNIQUE",
                "CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE",
            ]
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception:
                    pass  # Constraint may already exist

            # Create indexes for search
            indexes = [
                "CREATE INDEX researcher_name_idx IF NOT EXISTS FOR (r:Researcher) ON (r.name)",
                "CREATE INDEX concept_name_idx IF NOT EXISTS FOR (c:Concept) ON (c.name)",
                "CREATE INDEX theory_name_idx IF NOT EXISTS FOR (t:Theory) ON (t.name)",
            ]
            for index in indexes:
                try:
                    session.run(index)
                except Exception:
                    pass

    def add_book(self, title: str, author: Optional[str], path: str):
        """Add a book node."""
        with self.driver.session() as session:
            session.run("""
                MERGE (b:Book {path: $path})
                SET b.title = $title, b.author = $author
            """, title=title, author=author, path=path)

    def add_chunk(self, chunk_id: str, content: str, book_path: str):
        """Add a chunk and link to its book."""
        with self.driver.session() as session:
            session.run("""
                MERGE (c:Chunk {id: $chunk_id})
                SET c.content = $content
                WITH c
                MATCH (b:Book {path: $book_path})
                MERGE (c)-[:FROM_BOOK]->(b)
            """, chunk_id=chunk_id, content=content[:500], book_path=book_path)

    def add_entity(self, entity: Entity) -> str:
        """Add an entity node, return the node label used."""
        label = entity.type.capitalize()
        if label not in ["Researcher", "Concept", "Theory", "Assessment"]:
            label = "Concept"  # Default

        with self.driver.session() as session:
            session.run(f"""
                MERGE (e:{label} {{name: $name}})
                SET e.description = $description,
                    e.aliases = $aliases
            """,
                name=entity.name,
                description=entity.description,
                aliases=entity.aliases
            )
        return label

    def add_relationship(self, rel: Relationship):
        """Add a relationship between entities."""
        rel_type = rel.relation_type.upper()

        with self.driver.session() as session:
            # Try to find source and target nodes of any type
            session.run(f"""
                MATCH (source) WHERE source.name = $source_name
                MATCH (target) WHERE target.name = $target_name
                MERGE (source)-[r:{rel_type}]->(target)
                SET r.evidence = $evidence
            """,
                source_name=rel.source,
                target_name=rel.target,
                evidence=rel.evidence
            )

    def link_chunk_to_entity(self, chunk_id: str, entity_name: str):
        """Create MENTIONS relationship from chunk to entity."""
        with self.driver.session() as session:
            session.run("""
                MATCH (c:Chunk {id: $chunk_id})
                MATCH (e) WHERE e.name = $entity_name
                MERGE (c)-[:MENTIONS]->(e)
            """, chunk_id=chunk_id, entity_name=entity_name)

    def add_extraction_result(self, result: ExtractionResult, book_path: str):
        """Add all entities and relationships from an extraction result."""
        # Add chunk
        self.add_chunk(result.chunk_id, "", book_path)

        # Add entities
        for entity in result.entities:
            self.add_entity(entity)
            self.link_chunk_to_entity(result.chunk_id, entity.name)

        # Add relationships
        for rel in result.relationships:
            self.add_relationship(rel)

    def find_related_concepts(self, concept_name: str, depth: int = 2) -> list[dict]:
        """Find concepts related to a given concept."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Concept {name: $name})
                CALL apoc.path.subgraphAll(c, {
                    maxLevel: $depth,
                    relationshipFilter: "COMPONENT_OF|SUPPORTS|OPERATIONALIZES"
                })
                YIELD nodes, relationships
                RETURN nodes, relationships
            """, name=concept_name, depth=depth)

            record = result.single()
            if record:
                return {
                    "nodes": [dict(n) for n in record["nodes"]],
                    "relationships": [
                        {
                            "type": r.type,
                            "start": r.start_node["name"],
                            "end": r.end_node["name"]
                        }
                        for r in record["relationships"]
                    ]
                }
            return {"nodes": [], "relationships": []}

    def find_researchers_for_concept(self, concept_name: str) -> list[dict]:
        """Find researchers who have written about a concept."""
        with self.driver.session() as session:
            # Find researchers who develop the concept directly
            result = session.run("""
                MATCH (r:Researcher)-[:DEVELOPS]->(c:Concept {name: $name})
                RETURN DISTINCT r.name as researcher, r.description as description
                UNION
                MATCH (r:Researcher)-[:DEVELOPS]->()<-[:COMPONENT_OF]-(c:Concept {name: $name})
                RETURN DISTINCT r.name as researcher, r.description as description
            """, name=concept_name)
            return [dict(r) for r in result]

    def find_supporting_chunks(self, entity_name: str, limit: int = 10) -> list[dict]:
        """Find chunks that mention an entity."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Chunk)-[:MENTIONS]->(e {name: $name})
                MATCH (c)-[:FROM_BOOK]->(b:Book)
                RETURN c.id as chunk_id, c.content as content,
                       b.title as book_title, b.author as book_author
                LIMIT $limit
            """, name=entity_name, limit=limit)
            return [dict(r) for r in result]

    def get_stats(self) -> dict:
        """Get graph statistics."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(*) as count
                ORDER BY count DESC
            """)
            node_counts = {r["label"]: r["count"] for r in result}

            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(*) as count
                ORDER BY count DESC
            """)
            rel_counts = {r["type"]: r["count"] for r in result}

            return {
                "nodes": node_counts,
                "relationships": rel_counts
            }

    def clear_all(self):
        """Clear all data (use with caution!)."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
