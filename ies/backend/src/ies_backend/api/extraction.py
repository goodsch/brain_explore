"""API endpoints for Extraction Engine."""

from fastapi import APIRouter, HTTPException

from ies_backend.schemas.extraction import (
    ExtractionProfile,
    ExtractionProfileCreate,
    ExtractionRunRequest,
    ExtractionRunResponse,
)
from ies_backend.services.extraction_engine import ExtractionEngine

router = APIRouter(prefix="/extraction", tags=["extraction"])


@router.post("/profiles", response_model=ExtractionProfile)
async def create_profile(request: ExtractionProfileCreate) -> ExtractionProfile:
    """Create or update an extraction profile for a context."""
    profile = ExtractionProfile(
        context_id=request.context_id,
        core_concepts=request.core_concepts,
        synonyms=request.synonyms,
        relation_types=request.relation_types,
        domain_filters=request.domain_filters,
    )
    return ExtractionEngine.save_profile(profile)


@router.get("/profiles/{context_id}", response_model=ExtractionProfile)
async def get_profile(context_id: str) -> ExtractionProfile:
    """Get extraction profile for a context."""
    profile = ExtractionEngine.get_profile(context_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/run", response_model=ExtractionRunResponse)
async def run_extraction(request: ExtractionRunRequest) -> ExtractionRunResponse:
    """Run context-aware extraction.

    Searches for relevant segments in sources, extracts entities and
    relationships using LLM, and logs the extraction as a journey entry.

    Pipeline:
    1. Load context and profile
    2. Build keywords from profile + question
    3. Search for segments containing keywords
    4. Extract entities/relationships via Claude
    5. Log journey entry
    6. Return results
    """
    return await ExtractionEngine.run_extraction(request)
