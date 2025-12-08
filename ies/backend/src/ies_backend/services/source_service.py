"""Service layer for importing source documents (web/arxiv/youtube/text)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import httpx

from ies_backend.schemas.entity import ExtractionResult, ExtractedEntity
from ies_backend.schemas.source_document import (
    SourceDocument,
    SourceImport,
    SourceImportResponse,
    SourceListResponse,
    SourceType,
)
from ies_backend.services.extraction_service import ExtractionService
from ies_backend.services.neo4j_client import Neo4jClient


class SourceService:
    """Import and render source documents."""

    @staticmethod
    async def import_source(request: SourceImport) -> SourceImportResponse:
        """Import a source, extract entities, and persist."""
        from ies_backend.extractors import WebExtractor, YouTubeExtractor, PDFExtractor

        raw_content = request.content
        uri = None
        title = request.title
        extracted_metadata: dict[str, str] = {}

        # Use smart extractors for URL-based sources
        if raw_content.startswith(("http://", "https://")):
            uri = raw_content

            if YouTubeExtractor.can_handle(raw_content):
                extractor = YouTubeExtractor()
                result = await extractor.extract(raw_content)
                raw_content = result.content
                title = title or result.title
                extracted_metadata = result.metadata
            elif PDFExtractor.can_handle(raw_content):
                extractor = PDFExtractor()
                result = await extractor.extract(raw_content)
                raw_content = result.content
                title = title or result.title
                extracted_metadata = result.metadata
            elif WebExtractor.can_handle(raw_content):
                extractor = WebExtractor()
                result = await extractor.extract(raw_content)
                raw_content = result.content
                title = title or result.title
                extracted_metadata = result.metadata
            else:
                # Fallback to raw fetch
                raw_content = await SourceService._fetch_text(raw_content)

        # Handle local PDF files
        elif PDFExtractor.can_handle(raw_content):
            extractor = PDFExtractor()
            result = await extractor.extract(raw_content)
            raw_content = result.content
            title = title or result.title
            extracted_metadata = result.metadata

        extraction: ExtractionResult | None = None
        if request.extract_entities:
            extraction = await SourceService._extract_entities(raw_content)

        document = await SourceService._persist_document(
            user_id=request.user_id,
            source_type=request.source_type,
            title=title,
            topic=request.topic,
            uri=uri,
            content=raw_content,
            extraction=extraction,
        )
        return SourceImportResponse(document=document, extraction=extraction)

    @staticmethod
    async def list_sources(user_id: str | None = None) -> SourceListResponse:
        """List stored sources."""
        query = """
        MATCH (s:SourceDocument)
        WHERE $user_id IS NULL OR s.user_id = $user_id
        RETURN s
        ORDER BY s.imported_at DESC
        """
        rows = await Neo4jClient.execute_query(query, {"user_id": user_id})
        docs: list[SourceDocument] = []
        for row in rows:
            node = row.get("s", {})
            docs.append(
                SourceDocument(
                    id=node.get("id"),
                    source_type=SourceType(node.get("source_type", "text")),
                    title=node.get("title"),
                    topic=node.get("topic"),
                    uri=node.get("uri"),
                    imported_at=SourceService._parse_dt(node.get("imported_at")),
                    entity_count=node.get("entity_count", 0),
                    content=node.get("content", ""),
                )
            )
        return SourceListResponse(sources=docs)

    @staticmethod
    async def get_source(source_id: str) -> SourceDocument | None:
        """Fetch a single source."""
        query = """
        MATCH (s:SourceDocument {id: $id})
        OPTIONAL MATCH (s)-[:MENTIONS]->(e:Entity)
        RETURN s, collect(e.name) AS entities
        """
        rows = await Neo4jClient.execute_query(query, {"id": source_id})
        if not rows:
            return None
        node = rows[0].get("s", {})
        return SourceDocument(
            id=node.get("id"),
            source_type=SourceType(node.get("source_type", "text")),
            title=node.get("title"),
            topic=node.get("topic"),
            uri=node.get("uri"),
            imported_at=SourceService._parse_dt(node.get("imported_at")),
            entity_count=node.get("entity_count", 0),
            content=node.get("content", ""),
            entities=rows[0].get("entities", []),
        )

    @staticmethod
    async def delete_source(source_id: str) -> bool:
        """Delete a source document."""
        query = """
        MATCH (s:SourceDocument {id: $id})
        DETACH DELETE s
        RETURN COUNT(s) AS deleted
        """
        rows = await Neo4jClient.execute_write(query, {"id": source_id})
        return bool(rows and rows[0].get("deleted", 0))

    @staticmethod
    async def get_extraction_result(source_id: str) -> ExtractionResult | None:
        """Fetch extraction result for a source document."""
        query = """
        MATCH (s:SourceDocument {id: $id})-[:MENTIONS]->(e:Entity)
        RETURN e
        """
        rows = await Neo4jClient.execute_query(query, {"id": source_id})
        if not rows:
            return None

        entities: list[ExtractedEntity] = []
        for row in rows:
            node = row.get("e", {})
            # Assuming ExtractedEntity fields are directly on the Node.
            # 'quotes' and 'connections' might need more complex retrieval if not stored directly.
            # For now, initialize as empty lists if not present.
            entities.append(
                ExtractedEntity(
                    name=node.get("name"),
                    kind=node.get("kind", "idea"),  # Default to 'idea' if not present
                    domain=node.get("domain", "meta"),  # Default to 'meta'
                    status=node.get("status", "seed"),  # Default to 'seed'
                    description=node.get("description", ""),
                    quotes=node.get("quotes", []),
                    connections=node.get("connections", []),
                )
            )
        return ExtractionResult(entities=entities)

    # ---- helpers ----

    @staticmethod
    async def _fetch_text(url: str) -> str:
        """Fetch text content from a URL."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=20)
            resp.raise_for_status()
            return resp.text

    @staticmethod
    async def _extract_entities(content: str) -> ExtractionResult:
        """Run extraction with fallback."""
        try:
            extractor = ExtractionService()
            return await extractor.extract_entities(content)
        except Exception:
            # Simple fallback
            entities: list[ExtractedEntity] = []
            for word in set(content.split())[:5]:
                entities.append(
                    ExtractedEntity(
                        name=word.strip(",. "),
                        kind="idea",
                        domain="meta",
                        status="seed",
                        description="",
                        quotes=[],
                        connections=[],
                    )
                )
            return ExtractionResult(entities=entities)

    @staticmethod
    async def _persist_document(
        user_id: str,
        source_type: SourceType,
        title: str | None,
        topic: str | None,
        uri: str | None,
        content: str,
        extraction: ExtractionResult | None,
    ) -> SourceDocument:
        """Persist source document and entity links."""
        doc_id = f"src_{uuid.uuid4().hex[:10]}"
        imported_at = datetime.now(timezone.utc).isoformat()
        entity_names = [e.name for e in extraction.entities] if extraction else []

        query = """
        MERGE (s:SourceDocument {id: $id})
        SET s.source_type = $source_type,
            s.title = $title,
            s.topic = $topic,
            s.uri = $uri,
            s.user_id = $user_id,
            s.imported_at = $imported_at,
            s.entity_count = $entity_count,
            s.content = $content
        """
        await Neo4jClient.execute_write(
            query,
            {
                "id": doc_id,
                "source_type": source_type.value,
                "title": title,
                "topic": topic,
                "uri": uri,
                "user_id": user_id,
                "imported_at": imported_at,
                "entity_count": len(entity_names),
                "content": content,
            },
        )

        if entity_names:
            rel_query = """
            UNWIND $entities AS name
            MERGE (e:Entity {user_id: $user_id, name: name})
            ON CREATE SET e.created_at = $now, e.status = 'seed'
            SET e.updated_at = $now
            WITH e
            MATCH (s:SourceDocument {id: $id})
            MERGE (s)-[:MENTIONS]->(e)
            """
            await Neo4jClient.execute_write(
                rel_query,
                {
                    "entities": entity_names,
                    "user_id": user_id,
                    "id": doc_id,
                    "now": imported_at,
                },
            )

        return SourceDocument(
            id=doc_id,
            source_type=source_type,
            title=title,
            topic=topic,
            uri=uri,
            imported_at=SourceService._parse_dt(imported_at),
            entity_count=len(entity_names),
            content=content,
        )

    @staticmethod
    def _parse_dt(raw: str | None):
        """Parse ISO timestamps with Z tolerance."""
        if raw is None:
            return datetime.now(timezone.utc)
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except Exception:
            return datetime.now(timezone.utc)
