"""Concept service for knowledge graph formalization."""

import logging
import uuid
from datetime import datetime
from typing import Optional

from neo4j import GraphDatabase

from ..schemas.concept import (
    CreateConceptRequest,
    ConceptResponse,
    ConceptListResponse,
    ConceptType,
)
from .graph_service import GraphService

logger = logging.getLogger(__name__)


class ConceptService:
    """Service for creating and managing formalized concepts."""

    _driver = None

    @classmethod
    def _get_driver(cls):
        """Get or create Neo4j driver."""
        if cls._driver is None:
            import os
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "brainexplore")
            cls._driver = GraphDatabase.driver(uri, auth=(user, password))
        return cls._driver

    @classmethod
    async def create_concept(cls, request: CreateConceptRequest) -> ConceptResponse:
        """
        Create a new concept in the knowledge graph.

        This creates:
        1. A Concept node with the appropriate label
        2. Relationships to other concepts if specified
        """
        driver = cls._get_driver()

        # Determine the Neo4j label based on concept type
        label_map = {
            ConceptType.CONCEPT: "Concept",
            ConceptType.THEORY: "Theory",
            ConceptType.FRAMEWORK: "Framework",
            ConceptType.MECHANISM: "Concept",  # Use Concept label
            ConceptType.PATTERN: "Concept",
            ConceptType.DISTINCTION: "Concept",
        }
        label = label_map.get(request.concept_type, "Concept")

        concept_id = f"concept_{uuid.uuid4().hex[:12]}"
        created_at = datetime.utcnow().isoformat()

        with driver.session() as session:
            # Check if concept already exists
            existing = session.run(
                "MATCH (c) WHERE c.name = $name RETURN c.name LIMIT 1",
                name=request.name
            ).single()

            if existing:
                raise ValueError(f"Concept '{request.name}' already exists")

            # Create the concept node
            session.run(
                f"""
                CREATE (c:{label} {{
                    name: $name,
                    description: $description,
                    aliases: $aliases,
                    concept_type: $concept_type,
                    concept_id: $concept_id,
                    created_at: $created_at,
                    created_by: $user_id,
                    source_session_id: $source_session_id,
                    source_quotes: $source_quotes
                }})
                """,
                name=request.name,
                description=request.description,
                aliases=request.aliases,
                concept_type=request.concept_type.value,
                concept_id=concept_id,
                created_at=created_at,
                user_id=request.user_id,
                source_session_id=request.source_session_id,
                source_quotes=request.source_quotes,
            )

            # Create relationships
            relationships_created = 0
            for rel in request.relationships:
                # Try to create relationship if target exists
                result = session.run(
                    f"""
                    MATCH (source) WHERE source.name = $source_name
                    MATCH (target) WHERE target.name = $target_name
                    MERGE (source)-[r:{rel.relationship_type.value.upper()}]->(target)
                    SET r.evidence = $evidence, r.created_at = $created_at
                    RETURN r
                    """,
                    source_name=request.name,
                    target_name=rel.target_name,
                    evidence=rel.evidence,
                    created_at=created_at,
                ).single()

                if result:
                    relationships_created += 1

        logger.info(f"Created concept '{request.name}' with {relationships_created} relationships")

        return ConceptResponse(
            concept_id=concept_id,
            name=request.name,
            concept_type=request.concept_type,
            description=request.description,
            relationships_created=relationships_created,
            message=f"Concept '{request.name}' created successfully",
        )

    @classmethod
    async def list_concepts(
        cls,
        search: Optional[str] = None,
        concept_type: Optional[str] = None,
        limit: int = 50
    ) -> ConceptListResponse:
        """List concepts with optional filtering."""
        driver = cls._get_driver()

        query = """
            MATCH (c)
            WHERE (c:Concept OR c:Theory OR c:Framework)
        """
        params = {"limit": limit}

        if search:
            query += " AND (c.name CONTAINS $search OR c.description CONTAINS $search)"
            params["search"] = search

        if concept_type:
            query += " AND c.concept_type = $concept_type"
            params["concept_type"] = concept_type

        query += """
            RETURN c.name as name,
                   c.description as description,
                   c.concept_type as concept_type,
                   c.created_at as created_at,
                   labels(c)[0] as label
            ORDER BY c.created_at DESC
            LIMIT $limit
        """

        concepts = []
        with driver.session() as session:
            results = session.run(query, **params)
            for record in results:
                concepts.append({
                    "name": record["name"],
                    "description": record["description"],
                    "concept_type": record["concept_type"],
                    "created_at": record["created_at"],
                    "label": record["label"],
                })

        return ConceptListResponse(concepts=concepts, total=len(concepts))

    @classmethod
    async def get_concept(cls, concept_name: str) -> Optional[dict]:
        """Get detailed concept information."""
        driver = cls._get_driver()

        with driver.session() as session:
            result = session.run(
                """
                MATCH (c) WHERE c.name = $name
                OPTIONAL MATCH (c)-[r]->(related)
                RETURN c,
                       collect({
                           name: related.name,
                           type: type(r),
                           evidence: r.evidence
                       }) as relationships
                """,
                name=concept_name,
            ).single()

            if not result:
                return None

            node = result["c"]
            relationships = [r for r in result["relationships"] if r["name"]]

            return {
                "name": node.get("name"),
                "description": node.get("description"),
                "concept_type": node.get("concept_type"),
                "aliases": node.get("aliases", []),
                "created_at": node.get("created_at"),
                "created_by": node.get("created_by"),
                "source_session_id": node.get("source_session_id"),
                "source_quotes": node.get("source_quotes", []),
                "relationships": relationships,
            }
