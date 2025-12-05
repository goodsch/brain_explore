"""Service coordinating session processing pipeline."""

from __future__ import annotations

from typing import Any

from ies_backend.schemas.entity import (
    SessionProcessRequest,
    SessionProcessResponse,
)
from ies_backend.services.entity_storage_service import EntityStorageService
from ies_backend.services.extraction_service import ExtractionService
from ies_backend.services.session_document_service import SessionDocumentService
from ies_backend.services.template_service import TemplateService, TemplateServiceError


class SessionService:
    """Orchestrates session extraction, storage, and template mapping."""

    def __init__(
        self,
        extraction_service: ExtractionService | None = None,
        document_service: SessionDocumentService | None = None,
        storage_service: EntityStorageService | None = None,
        template_service: TemplateService | None = None,
    ) -> None:
        self.extraction_service = extraction_service or ExtractionService()
        self.document_service = document_service or SessionDocumentService()
        self.storage_service = storage_service or EntityStorageService()
        self.template_service = template_service or TemplateService()

    async def process_session(self, request: SessionProcessRequest) -> SessionProcessResponse:
        """Process a completed session transcript."""

        extraction = await self.extraction_service.extract_entities(request.transcript)

        session_doc_id = await self._create_session_document(request, extraction)
        entity_result = await self._store_entities(request, extraction, session_doc_id)
        await self._store_session_metadata(request, extraction, session_doc_id, entity_result)

        template_entities = await self._execute_template_mapping(
            request,
            session_doc_id,
        )

        return SessionProcessResponse(
            session_doc_id=session_doc_id,
            entities_created=entity_result.get("created", []),
            entities_updated=entity_result.get("updated", []),
            literature_links=entity_result.get("literature_links", {}),
            template_entities=template_entities,
            summary=extraction.session_summary,
        )

    async def _create_session_document(
        self,
        request: SessionProcessRequest,
        extraction: Any,
    ) -> str | None:
        try:
            return await self.document_service.create_session_document(
                user_id=request.user_id,
                extraction=extraction,
                session_title=request.session_title,
                session_date=request.session_date,
            )
        except Exception as exc:  # pragma: no cover - external dependency failure
            return f"siyuan_unavailable: {exc}"

    async def _store_entities(
        self,
        request: SessionProcessRequest,
        extraction: Any,
        session_doc_id: str | None,
    ) -> dict[str, Any]:
        session_ref = session_doc_id or "no_session_doc"
        try:
            return await self.storage_service.store_entities(
                user_id=request.user_id,
                session_id=session_ref,
                extraction=extraction,
            )
        except Exception:  # pragma: no cover - Neo4j outages shouldn't fail pipeline
            return {"created": [], "updated": [], "literature_links": {}}

    async def _store_session_metadata(
        self,
        request: SessionProcessRequest,
        extraction: Any,
        session_doc_id: str | None,
        entity_result: dict[str, Any],
    ) -> None:
        try:
            topic = request.session_title or (
                extraction.session_summary.threads_explored[0]
                if extraction.session_summary.threads_explored
                else "Exploration session"
            )
            hanging_question = (
                extraction.session_summary.open_questions[0]
                if extraction.session_summary.open_questions
                else None
            )
            await self.storage_service.store_session_metadata(
                user_id=request.user_id,
                session_id=session_doc_id or "no_session_doc",
                topic=topic,
                entity_names=(entity_result.get("created", []) + entity_result.get("updated", [])),
                hanging_question=hanging_question,
            )
        except Exception:  # pragma: no cover - metadata is non-critical
            return

    async def _execute_template_mapping(
        self,
        request: SessionProcessRequest,
        session_doc_id: str | None,
    ) -> list[str]:
        if not request.template_id or not request.section_responses:
            return []

        payload = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "session_doc_id": session_doc_id or "no_session_doc",
            "session_title": request.session_title,
            "section_responses": request.section_responses,
            "journey_id": request.journey_id,
            "transcript": request.transcript,
            "template_id": request.template_id,
        }

        try:
            template = self.template_service.load_template(request.template_id)
            return await self.template_service.execute_graph_mapping(template, payload)
        except TemplateServiceError as exc:  # pragma: no cover - logged for observability
            print(f"Template execution failed: {exc}")
        except FileNotFoundError:
            print(f"Template '{request.template_id}' not found")
        except Exception as exc:  # pragma: no cover
            print(f"Unexpected template execution error: {exc}")
        return []
