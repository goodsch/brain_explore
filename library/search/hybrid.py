"""
Hybrid search combining vector similarity and knowledge graph traversal.

Search modes:
1. Vector only - pure semantic similarity
2. Graph only - entity/relationship traversal
3. Hybrid - vector search enhanced with graph context
"""

from dataclasses import dataclass
from typing import Optional

from library.ingest.embed import Embedder, VectorStore
from library.graph.neo4j_client import KnowledgeGraph


@dataclass
class SearchResult:
    """A search result with content and metadata."""
    content: str
    score: float
    source_file: str
    chapter: Optional[str]
    related_concepts: list[str]
    supporting_authors: list[str]


class HybridSearch:
    """Combines vector search with knowledge graph for enhanced retrieval."""

    def __init__(
        self,
        embedder: Optional[Embedder] = None,
        vector_store: Optional[VectorStore] = None,
        knowledge_graph: Optional[KnowledgeGraph] = None
    ):
        self.embedder = embedder or Embedder()
        self.vector_store = vector_store or VectorStore()
        self.knowledge_graph = knowledge_graph or KnowledgeGraph()

    def vector_search(self, query: str, limit: int = 10) -> list[dict]:
        """Pure vector similarity search."""
        query_embedding = self.embedder.embed_text(query)
        return self.vector_store.search(query_embedding, limit=limit)

    def graph_search(self, concept: str, depth: int = 2) -> dict:
        """Search knowledge graph for concept and related entities."""
        related = self.knowledge_graph.find_related_concepts(concept, depth)
        authors = self.knowledge_graph.find_authors_for_concept(concept)
        chunks = self.knowledge_graph.find_supporting_chunks(concept)

        return {
            "concept": concept,
            "related": related,
            "authors": authors,
            "supporting_chunks": chunks
        }

    def hybrid_search(
        self,
        query: str,
        concepts: list[str] = None,
        limit: int = 10
    ) -> list[SearchResult]:
        """
        Hybrid search:
        1. Vector search for semantic relevance
        2. Graph expansion for related concepts
        3. Re-rank based on graph connections
        """
        # Step 1: Vector search
        vector_results = self.vector_search(query, limit=limit * 2)

        # Step 2: If concepts provided, get graph context
        graph_context = {}
        if concepts:
            for concept in concepts:
                try:
                    graph_context[concept] = self.graph_search(concept)
                except Exception:
                    pass

        # Step 3: Enhance results with graph info
        enhanced_results = []
        for vr in vector_results:
            # Find related concepts from graph
            related_concepts = []
            supporting_authors = []

            # Check if result mentions any known concepts
            content_lower = vr["content"].lower()
            for concept, context in graph_context.items():
                if concept.lower() in content_lower:
                    related_concepts.append(concept)
                    # Add related concepts from graph
                    for node in context.get("related", {}).get("nodes", []):
                        if node.get("name"):
                            related_concepts.append(node["name"])
                    # Add authors
                    for author in context.get("authors", []):
                        if author.get("author"):
                            supporting_authors.append(author["author"])

            enhanced_results.append(SearchResult(
                content=vr["content"],
                score=vr["score"],
                source_file=vr["metadata"].get("source_file", ""),
                chapter=vr["metadata"].get("chapter"),
                related_concepts=list(set(related_concepts)),
                supporting_authors=list(set(supporting_authors))
            ))

        # Sort by score and return top results
        enhanced_results.sort(key=lambda x: x.score, reverse=True)
        return enhanced_results[:limit]

    def find_experts(self, concept: str) -> list[dict]:
        """Find authors who are experts on a concept."""
        return self.knowledge_graph.find_authors_for_concept(concept)

    def find_related(self, concept: str) -> list[str]:
        """Find concepts related to the given concept."""
        result = self.knowledge_graph.find_related_concepts(concept)
        return [n.get("name") for n in result.get("nodes", []) if n.get("name")]

    def explain_concept(self, concept: str) -> dict:
        """Get a full explanation of a concept from the knowledge base."""
        # Get graph context
        graph_info = self.graph_search(concept)

        # Get supporting text from vectors
        chunks = self.vector_search(concept, limit=5)

        return {
            "concept": concept,
            "related_concepts": [
                n.get("name") for n in graph_info.get("related", {}).get("nodes", [])
            ],
            "relationships": graph_info.get("related", {}).get("relationships", []),
            "key_authors": graph_info.get("authors", []),
            "supporting_passages": [
                {
                    "content": c["content"],
                    "source": c["metadata"].get("source_file"),
                    "chapter": c["metadata"].get("chapter")
                }
                for c in chunks
            ]
        }
