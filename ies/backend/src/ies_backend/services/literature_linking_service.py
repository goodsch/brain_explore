"""Literature linking service - connects entities to source material in Qdrant."""

import os
from dataclasses import dataclass
from datetime import datetime, timezone

from openai import OpenAI
from qdrant_client import QdrantClient

from ies_backend.schemas.entity import ExtractedEntity
from ies_backend.services.neo4j_client import Neo4jClient


@dataclass
class LiteratureMatch:
    """A match from the literature."""

    content: str
    score: float
    source_file: str
    chapter: str | None
    chunk_id: str


class LiteratureLinkingService:
    """Service for linking extracted entities to literature in Qdrant."""

    COLLECTION_NAME = "brain_explore_library"
    SCORE_THRESHOLD = 0.45  # Minimum similarity score to create a link
    MAX_LINKS_PER_ENTITY = 5  # Maximum literature links per entity

    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        embedding_model: str = "text-embedding-3-small",
    ):
        self.qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.openai = OpenAI()
        self.embedding_model = embedding_model

    def _embed_text(self, text: str) -> list[float]:
        """Generate embedding for text."""
        response = self.openai.embeddings.create(
            input=text,
            model=self.embedding_model,
        )
        return response.data[0].embedding

    def search_literature(self, query: str, limit: int = 10) -> list[LiteratureMatch]:
        """Search Qdrant for similar literature chunks."""
        try:
            query_embedding = self._embed_text(query)

            # Use query_points (newer Qdrant API)
            results = self.qdrant.query_points(
                collection_name=self.COLLECTION_NAME,
                query=query_embedding,
                limit=limit,
            )

            return [
                LiteratureMatch(
                    content=r.payload.get("content", ""),
                    score=r.score,
                    source_file=r.payload.get("source_file", "unknown"),
                    chapter=r.payload.get("chapter"),
                    chunk_id=r.payload.get("chunk_id", str(r.id)),
                )
                for r in results.points
            ]
        except Exception as e:
            # Log but don't fail - literature linking is enhancement, not critical
            print(f"Literature search failed: {e}")
            return []

    async def link_entity_to_literature(
        self, user_id: str, entity: ExtractedEntity
    ) -> list[str]:
        """Find and create links between entity and relevant literature.

        Args:
            user_id: User ID
            entity: The extracted entity to ground in literature

        Returns:
            List of chunk_ids that were linked
        """
        # Build search query from entity name and description
        search_query = f"{entity.name}: {entity.description}"

        # Search for relevant literature
        matches = self.search_literature(search_query, limit=self.MAX_LINKS_PER_ENTITY * 2)

        # Filter by score threshold
        good_matches = [m for m in matches if m.score >= self.SCORE_THRESHOLD]

        # Take top matches
        top_matches = good_matches[: self.MAX_LINKS_PER_ENTITY]

        linked_chunks = []

        for match in top_matches:
            # Create GROUNDED_IN relationship
            query = """
            MATCH (e:Entity {user_id: $user_id, name: $entity_name})
            MERGE (c:Chunk {chunk_id: $chunk_id})
            ON CREATE SET
                c.content = $content,
                c.source_file = $source_file,
                c.chapter = $chapter,
                c.created_at = $now
            MERGE (e)-[r:GROUNDED_IN]->(c)
            ON CREATE SET
                r.score = $score,
                r.created_at = $now
            ON MATCH SET
                r.score = CASE WHEN r.score < $score THEN $score ELSE r.score END
            """

            await Neo4jClient.execute_write(
                query,
                {
                    "user_id": user_id,
                    "entity_name": entity.name,
                    "chunk_id": match.chunk_id,
                    "content": match.content[:500],  # Truncate for storage
                    "source_file": match.source_file,
                    "chapter": match.chapter,
                    "score": match.score,
                    "now": datetime.now(timezone.utc).isoformat(),
                },
            )

            linked_chunks.append(match.chunk_id)

        return linked_chunks

    async def link_entities_to_literature(
        self, user_id: str, entities: list[ExtractedEntity]
    ) -> dict[str, list[str]]:
        """Link multiple entities to literature.

        Args:
            user_id: User ID
            entities: List of entities to ground

        Returns:
            Dict mapping entity names to list of linked chunk_ids
        """
        results = {}

        for entity in entities:
            linked = await self.link_entity_to_literature(user_id, entity)
            if linked:
                results[entity.name] = linked

        return results

    async def get_entity_literature(
        self, user_id: str, entity_name: str
    ) -> list[dict]:
        """Get literature linked to an entity.

        Returns list of chunks with their relationship metadata.
        """
        query = """
        MATCH (e:Entity {user_id: $user_id, name: $entity_name})-[r:GROUNDED_IN]->(c:Chunk)
        RETURN c.chunk_id as chunk_id,
               c.content as content,
               c.source_file as source_file,
               c.chapter as chapter,
               r.score as score
        ORDER BY r.score DESC
        """

        results = await Neo4jClient.execute_read(
            query,
            {"user_id": user_id, "entity_name": entity_name},
        )

        return [dict(r) for r in results]
