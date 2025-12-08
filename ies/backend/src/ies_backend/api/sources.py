"""API endpoints for source document imports."""

from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from ies_backend.schemas.source_document import (
    SourceDocument,
    SourceImport,
    SourceImportResponse,
    SourceListResponse,
)
from ies_backend.services.rendering_service import RenderingService
from ies_backend.services.source_service import SourceService

router = APIRouter(tags=["sources"])


@router.post("/sources/import", response_model=SourceImportResponse)
async def import_source(request: SourceImport) -> SourceImportResponse:
    """Import a source (web/arxiv/youtube/text/file)."""
    return await SourceService.import_source(request)


@router.get("/sources", response_model=SourceListResponse)
async def list_sources(user_id: str | None = None) -> SourceListResponse:
    """List imported sources."""
    return await SourceService.list_sources(user_id=user_id)


@router.get("/sources/{source_id}", response_model=SourceDocument)
async def get_source(source_id: str) -> SourceDocument:
    """Get a single source document."""
    doc = await SourceService.get_source(source_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Source not found")
    return doc


@router.delete("/sources/{source_id}")
async def delete_source(source_id: str) -> dict[str, str]:
    """Delete a source document."""
    deleted = await SourceService.delete_source(source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"message": "Source deleted"}


@router.get("/sources/{source_id}/read", response_class=HTMLResponse)
async def read_source(source_id: str, theme: Optional[str] = "dark") -> HTMLResponse:
    """Render source as reader view."""
    doc = await SourceService.get_source(source_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Source not found")
    return RenderingService.render_source_reader(doc, theme=theme)


@router.get("/sources/{source_id}/epub")
async def epub_source(source_id: str):
    """Download source as EPUB."""
    doc = await SourceService.get_source(source_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Source not found")
    
    extraction_result = await SourceService.get_extraction_result(source_id)

    return RenderingService.render_source_epub(doc, extraction_result=extraction_result)
