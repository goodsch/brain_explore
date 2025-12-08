"""Graph service for Layer 3 exploration.

Provides knowledge graph operations using the existing Neo4j client.
This is a backend-specific implementation that doesn't depend on library/.
"""

import json
import logging

from ies_backend.config import settings
from ies_backend.services.neo4j_client import Neo4jClient

# Optional Anthropic for AI facet generation
try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)


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

    @staticmethod
    async def get_entity_facets(
        entity_name: str,
        generate_if_empty: bool = True,
        force_regenerate: bool = False,
    ) -> dict | None:
        """Get facets for an entity to enable categorical drilling in Flow Mode.

        Facets are thematic groupings of related concepts under an entity.
        They are stored as Facet nodes connected to the entity with HAS_FACET relationships,
        and individual concepts connect to facets with BELONGS_TO relationships.

        If no facets exist and generate_if_empty is True, AI will generate them.
        Generated facets are persisted to Neo4j for caching.

        Args:
            entity_name: Entity to get facets for
            generate_if_empty: If True, generate facets via AI when none exist
            force_regenerate: If True, delete existing facets and regenerate

        Returns:
            Dict with entity info and list of facets with their entities.
            Returns None if entity not found.
        """
        # First check if entity exists
        entity_query = """
        MATCH (e {name: $name})
        RETURN e, labels(e) as labels
        LIMIT 1
        """

        try:
            entity_results = await Neo4jClient.execute_query(
                entity_query, {"name": entity_name}
            )

            if not entity_results:
                return None

            entity = entity_results[0]["e"]
            labels = entity_results[0]["labels"]
            node_type = next(
                (l for l in labels if l not in ["Node", "Entity", "Base"]),
                labels[0] if labels else "Concept"
            )

            # If force regenerate, delete existing facets first
            if force_regenerate:
                delete_query = """
                MATCH (e {name: $name})-[:HAS_FACET]->(f:Facet)
                DETACH DELETE f
                """
                await Neo4jClient.execute_query(
                    delete_query, {"name": entity_name}
                )
                logger.info(f"Deleted existing facets for {entity_name}")

            # Get facets and their entities
            facets_query = """
            MATCH (e {name: $name})-[:HAS_FACET]->(f:Facet)
            OPTIONAL MATCH (concept)-[r:BELONGS_TO]->(f)
            WHERE concept.name IS NOT NULL
            WITH f, concept, r, labels(concept) as concept_labels
            ORDER BY f.order, concept.name
            RETURN f.name as facet_name,
                   f.description as facet_description,
                   f.order as facet_order,
                   collect({
                       name: concept.name,
                       type: concept_labels[0],
                       relationship: type(r)
                   }) as entities
            ORDER BY facet_order
            """

            facets_results = await Neo4jClient.execute_query(
                facets_query, {"name": entity_name}
            )

            facets = []
            for f in facets_results:
                # Filter out null entities (from OPTIONAL MATCH when facet has no entities yet)
                entities = [e for e in f.get("entities", []) if e.get("name")]

                facets.append({
                    "name": f["facet_name"],
                    "description": f.get("facet_description"),
                    "entity_count": len(entities),
                    "entities": entities,
                })

            # If no facets and generation is enabled, generate via AI
            if not facets and generate_if_empty:
                logger.info(f"No facets found for {entity_name}, generating via AI")
                facets = await GraphService.generate_facets_with_ai(
                    entity_name=entity_name,
                    entity_type=node_type,
                    persist=True,
                )

            return {
                "entity_name": entity.get("name", entity_name),
                "entity_type": node_type,
                "facets": facets,
                "generated": not facets_results and bool(facets),
            }

        except Exception as e:
            logger.error(f"Error getting facets for {entity_name}: {e}")
            return None

    @staticmethod
    async def create_facet(
        entity_name: str,
        facet_name: str,
        description: str | None = None,
        order: int = 0
    ) -> bool:
        """Create a facet for an entity.

        Args:
            entity_name: Entity to attach facet to
            facet_name: Name of the facet
            description: Optional description of what this facet covers
            order: Display order (lower = earlier)

        Returns:
            True if created successfully, False otherwise
        """
        query = """
        MATCH (e {name: $entity_name})
        MERGE (f:Facet {name: $facet_name, entity: $entity_name})
        ON CREATE SET f.description = $description, f.order = $order
        MERGE (e)-[:HAS_FACET]->(f)
        RETURN f
        """

        try:
            results = await Neo4jClient.execute_query(
                query,
                {
                    "entity_name": entity_name,
                    "facet_name": facet_name,
                    "description": description,
                    "order": order,
                }
            )
            return len(results) > 0
        except Exception:
            return False

    @staticmethod
    async def add_entity_to_facet(
        facet_name: str,
        entity_name: str,
        concept_name: str
    ) -> bool:
        """Add a concept to a facet.

        Args:
            facet_name: Facet to add to
            entity_name: Parent entity (for facet lookup)
            concept_name: Concept to add to the facet

        Returns:
            True if added successfully, False otherwise
        """
        query = """
        MATCH (f:Facet {name: $facet_name, entity: $entity_name})
        MATCH (c {name: $concept_name})
        MERGE (c)-[:BELONGS_TO]->(f)
        RETURN f, c
        """

        try:
            results = await Neo4jClient.execute_query(
                query,
                {
                    "facet_name": facet_name,
                    "entity_name": entity_name,
                    "concept_name": concept_name,
                }
            )
            return len(results) > 0
        except Exception:
            return False

    @staticmethod
    async def generate_facets_with_ai(
        entity_name: str,
        entity_type: str,
        persist: bool = True
    ) -> list[dict]:
        """Generate facets for an entity using AI.

        When an entity has no predefined facets, use Claude to generate
        thematic categories for exploration. Generated facets are persisted
        to Neo4j for caching.

        Args:
            entity_name: Name of the entity to generate facets for
            entity_type: Type of entity (Concept, Theory, etc.)
            persist: Whether to save generated facets to Neo4j

        Returns:
            List of facet dicts with name, description, and empty entities list
        """
        if not ANTHROPIC_AVAILABLE or not settings.anthropic_api_key:
            logger.warning("Anthropic not available for facet generation")
            return []

        # Prompt designed for structured output
        prompt = f"""You are helping organize knowledge about "{entity_name}" (type: {entity_type}).

Generate 4-7 thematic facets/categories that would help someone explore and understand this topic systematically. Each facet should represent a distinct aspect or dimension.

Return ONLY a JSON array with this structure:
[
  {{"name": "Facet Name", "description": "Brief description of what this facet covers"}},
  ...
]

Example for "ADHD":
[
  {{"name": "Diagnosis & Assessment", "description": "Criteria, testing, and identification processes"}},
  {{"name": "Neurobiology", "description": "Brain structures, neurotransmitters, and neural mechanisms"}},
  {{"name": "Executive Function", "description": "Working memory, attention, inhibition, planning"}},
  {{"name": "Time Perception", "description": "Time blindness, temporal processing, and urgency"}},
  {{"name": "Treatment", "description": "Medication, therapy, and management strategies"}},
  {{"name": "Lived Experience", "description": "Daily impact, coping, and personal perspectives"}}
]

Now generate facets for "{entity_name}":"""

        try:
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse JSON response
            response_text = response.content[0].text.strip()
            # Handle potential markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            facets_data = json.loads(response_text)

            # Persist to Neo4j if requested
            if persist:
                for i, facet in enumerate(facets_data):
                    await GraphService.create_facet(
                        entity_name=entity_name,
                        facet_name=facet["name"],
                        description=facet.get("description"),
                        order=i,
                    )
                logger.info(
                    f"Generated and persisted {len(facets_data)} facets for {entity_name}"
                )

            # Return in the format expected by get_entity_facets
            return [
                {
                    "name": f["name"],
                    "description": f.get("description"),
                    "entity_count": 0,
                    "entities": [],
                }
                for f in facets_data
            ]

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI facet response: {e}")
            return []
        except Exception as e:
            logger.error(f"AI facet generation failed: {e}")
            return []

    @staticmethod
    async def create_entity_from_exploration(
        name: str,
        entity_type: str = "Concept",
        parent_entity: str | None = None,
        facet_name: str | None = None,
        description: str | None = None,
    ) -> dict:
        """Create a new entity from facet/graph exploration.

        When a user clicks a facet to explore, and that facet doesn't exist
        as an entity yet, create it. Optionally link to parent and facet.

        Args:
            name: Name of the entity to create
            entity_type: Type label (Concept, Theory, Person, Method, etc.)
            parent_entity: Name of parent entity (for relationship)
            facet_name: Name of facet this came from (for BELONGS_TO)
            description: Optional initial description

        Returns:
            Dict with entity info and whether it was newly created
        """
        # Check if entity already exists
        check_query = """
        MATCH (e {name: $name})
        RETURN e, labels(e) as labels
        LIMIT 1
        """

        try:
            existing = await Neo4jClient.execute_query(
                check_query, {"name": name}
            )

            if existing:
                # Entity exists, just return it
                entity = existing[0]["e"]
                labels = existing[0]["labels"]
                node_type = next(
                    (l for l in labels if l not in ["Node", "Entity", "Base"]),
                    labels[0] if labels else entity_type
                )
                return {
                    "name": entity.get("name", name),
                    "entity_type": node_type,
                    "created": False,
                    "parent_entity": parent_entity,
                    "facet_name": facet_name,
                }

            # Create new entity
            create_query = f"""
            CREATE (e:{entity_type} {{name: $name, description: $description}})
            RETURN e
            """

            await Neo4jClient.execute_query(
                create_query,
                {"name": name, "description": description or ""}
            )
            logger.info(f"Created new {entity_type} entity: {name}")

            # If parent provided, create RELATED_TO relationship
            if parent_entity:
                rel_query = """
                MATCH (parent {name: $parent_name})
                MATCH (child {name: $child_name})
                MERGE (child)-[:RELATED_TO]->(parent)
                MERGE (parent)-[:HAS_COMPONENT]->(child)
                """
                await Neo4jClient.execute_query(
                    rel_query,
                    {"parent_name": parent_entity, "child_name": name}
                )
                logger.info(f"Linked {name} to parent {parent_entity}")

            # If facet provided, add to facet
            if facet_name and parent_entity:
                await GraphService.add_entity_to_facet(
                    facet_name=facet_name,
                    entity_name=parent_entity,
                    concept_name=name,
                )
                logger.info(f"Added {name} to facet {facet_name}")

            return {
                "name": name,
                "entity_type": entity_type,
                "created": True,
                "parent_entity": parent_entity,
                "facet_name": facet_name,
            }

        except Exception as e:
            logger.error(f"Failed to create entity {name}: {e}")
            raise

    @staticmethod
    async def get_entity_evidence(
        entity_name: str,
        limit: int = 20,
        include_book_mentions: bool = True,
    ) -> dict:
        """Get evidence passages for an entity from the knowledge graph.

        Retrieves evidence from two sources:
        1. Chunks: Extracted text passages with MENTIONS relationships (high confidence)
        2. Books: Book-level mentions, useful when chunks are sparse (lower confidence)

        Args:
            entity_name: Name of the entity to find evidence for
            limit: Maximum passages to return
            include_book_mentions: Include book-level mentions if chunks are sparse

        Returns:
            Dict with evidence list, total_count, and sources_searched
        """
        evidence = []
        sources_searched = set()

        # Query 1: Get direct chunk evidence (highest confidence)
        chunk_query = """
        MATCH (c:Chunk)-[:MENTIONS]->(e {name: $name})
        OPTIONAL MATCH (c)-[:FROM_BOOK]->(b:Book)
        RETURN c.chunk_id as id, c.content as text,
               c.chapter as chapter, c.source_file as source_file,
               b.title as book_title, b.author as book_author
        ORDER BY c.created_at DESC
        LIMIT $limit
        """

        try:
            chunk_results = await Neo4jClient.execute_query(
                chunk_query, {"name": entity_name, "limit": limit}
            )

            for record in chunk_results:
                source_title = record.get("book_title") or record.get("source_file") or "Unknown"
                sources_searched.add(source_title)

                location = {}
                if record.get("chapter"):
                    location["chapter"] = record["chapter"]

                evidence.append({
                    "id": record["id"] or f"chunk_{len(evidence)}",
                    "text": record["text"],
                    "source_title": source_title,
                    "source_author": record.get("book_author"),
                    "location": location if location else None,
                    "confidence": 1.0,  # Direct chunk mention = highest confidence
                    "source_type": "chunk",
                })

            logger.info(f"Found {len(evidence)} chunk evidence for {entity_name}")

        except Exception as e:
            logger.warning(f"Chunk evidence query failed for {entity_name}: {e}")

        # Query 2: Get book-level mentions (if chunks are sparse)
        if include_book_mentions and len(evidence) < limit:
            remaining = limit - len(evidence)

            book_query = """
            MATCH (b:Book)-[:MENTIONS]->(e {name: $name})
            WHERE NOT exists {
                MATCH (c:Chunk)-[:MENTIONS]->(e)
                WHERE (c)-[:FROM_BOOK]->(b)
            }
            RETURN b.title as title, b.author as author, b.description as description
            LIMIT $limit
            """

            try:
                book_results = await Neo4jClient.execute_query(
                    book_query, {"name": entity_name, "limit": remaining}
                )

                for record in book_results:
                    title = record.get("title", "Unknown")
                    sources_searched.add(title)

                    # Use book description as evidence snippet, or indicate it's a mention
                    text = record.get("description") or f"Mentioned in '{title}'"

                    evidence.append({
                        "id": f"book_{title.replace(' ', '_')[:30]}",
                        "text": text,
                        "source_title": title,
                        "source_author": record.get("author"),
                        "location": None,  # Book-level, no specific location
                        "confidence": 0.7,  # Lower confidence - book mention, not chunk
                        "source_type": "book",
                    })

                logger.info(f"Added {len(book_results)} book-level evidence for {entity_name}")

            except Exception as e:
                logger.warning(f"Book evidence query failed for {entity_name}: {e}")

        # Count total evidence available (not limited)
        count_query = """
        MATCH (c:Chunk)-[:MENTIONS]->(e {name: $name})
        RETURN count(c) as chunk_count
        """
        book_count_query = """
        MATCH (b:Book)-[:MENTIONS]->(e {name: $name})
        RETURN count(b) as book_count
        """

        total_count = len(evidence)
        try:
            chunk_count = await Neo4jClient.execute_query(count_query, {"name": entity_name})
            book_count = await Neo4jClient.execute_query(book_count_query, {"name": entity_name})
            total_count = (
                (chunk_count[0]["chunk_count"] if chunk_count else 0) +
                (book_count[0]["book_count"] if book_count else 0)
            )
        except Exception:
            pass

        return {
            "entity_name": entity_name,
            "evidence": sorted(evidence, key=lambda x: x["confidence"], reverse=True),
            "total_count": total_count,
            "sources_searched": len(sources_searched),
        }
