"""Concept API endpoints for knowledge graph formalization."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException

from ..schemas.concept import (
    CreateConceptRequest,
    ConceptResponse,
    ConceptListResponse,
)
from ..services.concept_service import ConceptService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/concepts", tags=["concepts"])


@router.post("", response_model=ConceptResponse)
async def create_concept(request: CreateConceptRequest) -> ConceptResponse:
    """
    Create a new concept in the knowledge graph.

    This formalizes an insight from a thinking session into a persistent
    concept that becomes part of the domain knowledge graph.
    """
    try:
        return await ConceptService.create_concept(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating concept: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create concept: {e}")


@router.get("", response_model=ConceptListResponse)
async def list_concepts(
    search: Optional[str] = None,
    concept_type: Optional[str] = None,
    limit: int = 50
) -> ConceptListResponse:
    """
    List concepts from the knowledge graph.

    Optional filters:
    - search: Search by name or description
    - concept_type: Filter by type (concept, theory, framework, etc.)
    """
    try:
        return await ConceptService.list_concepts(
            search=search,
            concept_type=concept_type,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error listing concepts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list concepts: {e}")


@router.get("/{concept_name}", response_model=dict)
async def get_concept(concept_name: str) -> dict:
    """Get details of a specific concept by name."""
    try:
        result = await ConceptService.get_concept(concept_name)
        if not result:
            raise HTTPException(status_code=404, detail=f"Concept '{concept_name}' not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting concept: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get concept: {e}")
