"""Quick Add prompt-to-create endpoint."""

from fastapi import APIRouter

from ies_backend.schemas.plan import BuildPlanRequest, BuildPlanResponse
from ies_backend.services.plan_builder_service import PlanBuilderService

router = APIRouter(tags=["quick-add"])


@router.post("/quick-add/prompt", response_model=BuildPlanResponse)
async def quick_add_prompt(request: BuildPlanRequest) -> BuildPlanResponse:
    """Create plan/checklist/spark from a short prompt."""
    return await PlanBuilderService.build(
        prompt=request.content,
        intents=request.intent,
        duration=request.duration,
        due=request.due,
        user_id=request.user_id,
        source_id=request.source_id,
    )
