"""API endpoints for thinking templates."""

from fastapi import APIRouter, HTTPException

from ies_backend.schemas.template import ThinkingTemplate
from ies_backend.services.template_service import TemplateService, TemplateServiceError

router = APIRouter()
template_service = TemplateService()


@router.get("/templates/{template_id}", response_model=ThinkingTemplate)
async def get_template(template_id: str) -> ThinkingTemplate:
    """
    Retrieve a thinking template by ID.

    Available templates:
    - learning-mechanism-map: Learning mode - understand how something works
    - articulating-clarify-intuition: Articulating mode - clarify vague intuitions
    """
    try:
        return template_service.load_template(template_id)
    except TemplateServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
