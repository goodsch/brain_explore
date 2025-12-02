"""Entity storage service - persists entities to Neo4j graph."""

from datetime import datetime, timezone
from typing import Any

from ies_backend.schemas.entity import ExtractedEntity, ExtractionResult
from ies_backend.services.neo4j_client import Neo4jClient
from ies_backend.services.literature_linking_service import LiteratureLinkingService


class EntityStorageService:
    """Service for storing extracted entities in Neo4j."""

    def __init__(self, enable_literature_linking: bool = True):
        """Initialize entity storage service.

        Args:
            enable_literature_linking: Whether to link entities to literature.
                Set to False to skip Qdrant/OpenAI calls (e.g., in tests).
        """
        self.enable_literature_linking = enable_literature_linking
        self._literature_service: LiteratureLinkingService | None = None

    @property
    def literature_service(self) -> LiteratureLinkingService:
        """Lazy-load literature linking service."""
        if self._literature_service is None:
            self._literature_service = LiteratureLinkingService()
        return self._literature_service

    async def store_entities(
        self,
        user_id: str,
        session_id: str,
        extraction: ExtractionResult,
    ) -> dict[str, Any]:
        """Store extracted entities in Neo4j and link to literature.

        Args:
            user_id: User ID
            session_id: Session document ID
            extraction: Extraction result with entities

        Returns:
            Dict with created, updated, and literature_links
        """
        created = []
        updated = []

        for entity in extraction.entities:
            # Check if entity exists
            existing = await self._find_entity(user_id, entity.name)

            if existing:
                # Update existing entity
                await self._update_entity(user_id, entity, session_id)
                updated.append(entity.name)
            else:
                # Create new entity
                await self._create_entity(user_id, entity, session_id)
                created.append(entity.name)

        # Create connections between entities
        await self._create_connections(user_id, extraction.entities)

        # Link entities to literature (if enabled)
        literature_links: dict[str, list[str]] = {}
        if self.enable_literature_linking:
            try:
                literature_links = await self.literature_service.link_entities_to_literature(
                    user_id, extraction.entities
                )
            except Exception as e:
                # Log but don't fail - literature linking is enhancement
                print(f"Literature linking failed: {e}")

        return {
            "created": created,
            "updated": updated,
            "literature_links": literature_links,
        }

    async def _find_entity(
        self, user_id: str, entity_name: str
    ) -> dict[str, Any] | None:
        """Find an entity by name for a user."""
        query = """
        MATCH (e:Entity {user_id: $user_id, name: $name})
        RETURN e
        """
        results = await Neo4jClient.execute_query(
            query, {"user_id": user_id, "name": entity_name}
        )
        return results[0]["e"] if results else None

    async def _create_entity(
        self,
        user_id: str,
        entity: ExtractedEntity,
        session_id: str,
    ) -> None:
        """Create a new entity node."""
        query = """
        CREATE (e:Entity {
            user_id: $user_id,
            name: $name,
            kind: $kind,
            domain: $domain,
            status: $status,
            description: $description,
            quotes: $quotes,
            created_at: $created_at,
            updated_at: $updated_at,
            session_ids: [$session_id]
        })
        """
        now = datetime.now(timezone.utc).isoformat()
        await Neo4jClient.execute_write(
            query,
            {
                "user_id": user_id,
                "name": entity.name,
                "kind": entity.kind.value,
                "domain": entity.domain.value,
                "status": entity.status.value,
                "description": entity.description,
                "quotes": entity.quotes,
                "created_at": now,
                "updated_at": now,
                "session_id": session_id,
            },
        )

    async def _update_entity(
        self,
        user_id: str,
        entity: ExtractedEntity,
        session_id: str,
    ) -> None:
        """Update an existing entity node."""
        # Update entity, promoting status if appropriate
        # (seed → developing → solid, never demote)
        query = """
        MATCH (e:Entity {user_id: $user_id, name: $name})
        SET e.description = $description,
            e.updated_at = $updated_at,
            e.quotes = e.quotes + $new_quotes,
            e.session_ids = e.session_ids + [$session_id],
            e.status = CASE
                WHEN e.status = 'seed' AND $status IN ['developing', 'solid'] THEN $status
                WHEN e.status = 'developing' AND $status = 'solid' THEN $status
                ELSE e.status
            END
        """
        await Neo4jClient.execute_write(
            query,
            {
                "user_id": user_id,
                "name": entity.name,
                "description": entity.description,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "new_quotes": entity.quotes,
                "session_id": session_id,
                "status": entity.status.value,
            },
        )

    async def _create_connections(
        self, user_id: str, entities: list[ExtractedEntity]
    ) -> None:
        """Create connections between entities."""
        for entity in entities:
            for conn in entity.connections:
                # Create relationship if target exists
                query = """
                MATCH (from:Entity {user_id: $user_id, name: $from_name})
                MATCH (to:Entity {user_id: $user_id, name: $to_name})
                MERGE (from)-[r:RELATES_TO {type: $rel_type}]->(to)
                ON CREATE SET r.created_at = $now
                """
                await Neo4jClient.execute_write(
                    query,
                    {
                        "user_id": user_id,
                        "from_name": entity.name,
                        "to_name": conn.to,
                        "rel_type": conn.relationship.value,
                        "now": datetime.now(timezone.utc).isoformat(),
                    },
                )

    async def get_user_entities(
        self, user_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get all entities for a user."""
        query = """
        MATCH (e:Entity {user_id: $user_id})
        RETURN e
        ORDER BY e.updated_at DESC
        LIMIT $limit
        """
        results = await Neo4jClient.execute_query(
            query, {"user_id": user_id, "limit": limit}
        )
        return [r["e"] for r in results]

    async def get_entity_graph(
        self, user_id: str, entity_name: str, depth: int = 2
    ) -> dict[str, Any]:
        """Get an entity and its connected entities.

        Args:
            user_id: User ID
            entity_name: Name of central entity
            depth: How many hops to traverse

        Returns:
            Dict with entity and its connections
        """
        query = """
        MATCH path = (e:Entity {user_id: $user_id, name: $name})-[*0..{depth}]-(connected)
        WHERE connected:Entity
        WITH e, collect(DISTINCT connected) as connected_entities,
             collect(DISTINCT relationships(path)) as all_rels
        RETURN e, connected_entities, all_rels
        """.replace("{depth}", str(depth))

        results = await Neo4jClient.execute_query(
            query, {"user_id": user_id, "name": entity_name}
        )

        if not results:
            return {"entity": None, "connected": [], "relationships": []}

        return {
            "entity": results[0]["e"],
            "connected": results[0]["connected_entities"],
            "relationships": results[0]["all_rels"],
        }

    # Session metadata storage for context loading (Phase 4)

    async def store_session_metadata(
        self,
        user_id: str,
        session_id: str,
        topic: str,
        entity_names: list[str],
        hanging_question: str | None = None,
    ) -> None:
        """Store session metadata in Neo4j for context loading."""
        query = """
        CREATE (s:Session {
            user_id: $user_id,
            session_id: $session_id,
            topic: $topic,
            entity_names: $entity_names,
            hanging_question: $hanging_question,
            date: $date,
            created_at: $created_at
        })
        """
        now = datetime.now(timezone.utc)
        await Neo4jClient.execute_write(
            query,
            {
                "user_id": user_id,
                "session_id": session_id,
                "topic": topic,
                "entity_names": entity_names,
                "hanging_question": hanging_question,
                "date": now.strftime("%Y-%m-%d"),
                "created_at": now.isoformat(),
            },
        )

    async def get_recent_sessions(
        self, user_id: str, limit: int = 3
    ) -> list[dict[str, Any]]:
        """Get recent session metadata for context loading."""
        query = """
        MATCH (s:Session {user_id: $user_id})
        RETURN s
        ORDER BY s.created_at DESC
        LIMIT $limit
        """
        results = await Neo4jClient.execute_query(
            query, {"user_id": user_id, "limit": limit}
        )
        return [r["s"] for r in results]

    async def get_active_entities(
        self, user_id: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get entities with status 'developing' or 'seed' for context loading."""
        query = """
        MATCH (e:Entity {user_id: $user_id})
        WHERE e.status IN ['seed', 'developing']
        RETURN e
        ORDER BY e.updated_at DESC
        LIMIT $limit
        """
        results = await Neo4jClient.execute_query(
            query, {"user_id": user_id, "limit": limit}
        )
        return [r["e"] for r in results]
