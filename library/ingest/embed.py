"""
Embedding generation and vector store operations.
"""

import os
from dataclasses import dataclass
from typing import Iterator

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from .chunk import Chunk


@dataclass
class EmbeddedChunk:
    """A chunk with its embedding vector."""
    chunk: Chunk
    embedding: list[float]


class Embedder:
    """Generate embeddings using OpenAI."""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.client = OpenAI()
        self.model = model
        self.dimensions = 1536  # text-embedding-3-small default

    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding

    def embed_chunks(self, chunks: list[Chunk]) -> Iterator[EmbeddedChunk]:
        """Generate embeddings for multiple chunks."""
        # Batch for efficiency (OpenAI allows up to 2048 inputs)
        batch_size = 100

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [c.content for c in batch]

            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )

            for chunk, data in zip(batch, response.data):
                yield EmbeddedChunk(
                    chunk=chunk,
                    embedding=data.embedding
                )


class VectorStore:
    """Qdrant vector store operations."""

    COLLECTION_NAME = "brain_explore_library"

    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.COLLECTION_NAME for c in collections)

        if not exists:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=1536,  # OpenAI embedding dimension
                    distance=Distance.COSINE
                )
            )

    def add_chunks(self, embedded_chunks: list[EmbeddedChunk]):
        """Add embedded chunks to the vector store."""
        points = []

        for i, ec in enumerate(embedded_chunks):
            # Create unique ID from chunk ID
            point_id = hash(ec.chunk.id) % (2**63)  # Qdrant needs int IDs

            points.append(PointStruct(
                id=point_id,
                vector=ec.embedding,
                payload={
                    "chunk_id": ec.chunk.id,
                    "content": ec.chunk.content,
                    "token_count": ec.chunk.token_count,
                    **ec.chunk.metadata
                }
            ))

        # Upsert in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=batch
            )

    def search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        source_filter: str | None = None
    ) -> list[dict]:
        """Search for similar chunks."""
        filter_condition = None
        if source_filter:
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="source_file",
                        match=MatchValue(value=source_filter)
                    )
                ]
            )

        results = self.client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit,
            query_filter=filter_condition
        )

        return [
            {
                "score": r.score,
                "content": r.payload.get("content"),
                "metadata": {
                    k: v for k, v in r.payload.items()
                    if k not in ["content", "chunk_id"]
                }
            }
            for r in results
        ]

    def get_stats(self) -> dict:
        """Get collection statistics."""
        info = self.client.get_collection(self.COLLECTION_NAME)
        return {
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status
        }


def embed_and_store(chunks: list[Chunk], embedder: Embedder = None, store: VectorStore = None):
    """Convenience function to embed chunks and store them."""
    embedder = embedder or Embedder()
    store = store or VectorStore()

    embedded = list(embedder.embed_chunks(chunks))
    store.add_chunks(embedded)

    return len(embedded)
