"""Question Engine API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ies_backend.schemas.question_engine import (
    ApproachSelection,
    InquiryApproach,
    QuestionBatch,
    QuestionTemplate,
    StateDetection,
    UserState,
)
from ies_backend.services.approach_selection_service import ApproachSelectionService
from ies_backend.services.profile_service import ProfileService
from ies_backend.services.question_templates_service import QuestionTemplatesService
from ies_backend.services.state_detection_service import StateDetectionService

router = APIRouter()

# Initialize services
state_detection_service = StateDetectionService()
approach_selection_service = ApproachSelectionService()
question_templates_service = QuestionTemplatesService()
profile_service = ProfileService()


# Request/Response models
class DetectStateRequest(BaseModel):
    """Request for state detection."""

    recent_messages: list[str] = Field(
        ..., description="Last 3-5 user messages from conversation"
    )
    user_id: str | None = Field(None, description="User ID to load profile context")
    capacity: int | None = Field(
        None, ge=1, le=10, description="Optional explicit capacity check-in (1-10)"
    )


class SelectApproachRequest(BaseModel):
    """Request for approach selection."""

    user_id: str | None = Field(None, description="User ID to load profile")
    recent_messages: list[str] = Field(
        ..., description="Recent conversation messages for state detection"
    )
    previous_approach: InquiryApproach | None = Field(
        None, description="Previously used approach to avoid repetition"
    )
    session_duration_minutes: int = Field(
        0, ge=0, description="How long the session has been running"
    )


class GenerateQuestionsRequest(BaseModel):
    """Request for question generation."""

    user_id: str | None = Field(None, description="User ID for profile adaptation")
    recent_messages: list[str] = Field(
        ..., description="Recent conversation for state detection"
    )
    context: str = Field(..., description="Current topic/context for question generation")
    num_questions: int = Field(3, ge=1, le=10, description="Number of questions to generate")


@router.post("/detect-state", response_model=StateDetection)
async def detect_state(request: DetectStateRequest) -> StateDetection:
    """
    Detect user's current cognitive/emotional state from recent messages.

    Analyzes conversation patterns, language markers, and explicit signals
    to determine if user is flowing, stuck, overwhelmed, etc.

    Args:
        request: State detection request with messages and optional context

    Returns:
        StateDetection with primary state, confidence, and observed signals
    """
    try:
        # Load profile if user_id provided
        profile = None
        if request.user_id:
            profile = await profile_service.get_profile(request.user_id)

        # Detect state
        state = state_detection_service.detect_state(
            recent_messages=request.recent_messages,
            profile=profile,
            explicit_capacity=request.capacity,
        )

        return state

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"State detection failed: {str(e)}",
        )


@router.post("/select-approach", response_model=ApproachSelection)
async def select_approach(request: SelectApproachRequest) -> ApproachSelection:
    """
    Select best inquiry approach based on detected state and user profile.

    First detects user state, then selects appropriate questioning approach
    (Socratic, Solution-Focused, Phenomenological, etc.) with profile-based
    adaptations for pacing, directness, abstraction, and structure.

    Args:
        request: Approach selection request with messages and context

    Returns:
        ApproachSelection with chosen approach and adaptation parameters
    """
    try:
        # Load profile if user_id provided
        profile = None
        if request.user_id:
            profile = await profile_service.get_profile(request.user_id)

        # First detect state
        state = state_detection_service.detect_state(
            recent_messages=request.recent_messages,
            profile=profile,
        )

        # Select approach based on state and profile
        selection = approach_selection_service.select_approach(
            state=state,
            profile=profile,
            previous_approach=request.previous_approach,
            session_duration_minutes=request.session_duration_minutes,
        )

        return selection

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Approach selection failed: {str(e)}",
        )


@router.get("/templates/{approach}", response_model=list[QuestionTemplate])
async def get_templates(
    approach: InquiryApproach,
    category: str | None = Query(None, description="Filter by category (e.g., 'clarifying', 'deepening')"),
) -> list[QuestionTemplate]:
    """
    Get question templates for a specific inquiry approach.

    Returns template library with different question patterns, directness
    variants, and usage guidance for the specified approach.

    Args:
        approach: The inquiry approach (socratic, solution_focused, etc.)
        category: Optional category filter (clarifying, deepening, challenging, grounding)

    Returns:
        List of question templates for the approach
    """
    try:
        templates = question_templates_service.get_templates_for_approach(
            approach=approach,
            category=category,
        )

        if not templates:
            raise HTTPException(
                status_code=404,
                detail=f"No templates found for approach='{approach}' and category='{category}'",
            )

        return templates

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve templates: {str(e)}",
        )


@router.post("/generate-questions", response_model=QuestionBatch)
async def generate_questions(request: GenerateQuestionsRequest) -> QuestionBatch:
    """
    Generate profile-adapted questions for current conversation context.

    Combines state detection, approach selection, and template adaptation
    to produce questions tailored to user's current state and cognitive profile.

    This endpoint orchestrates the full Question Engine pipeline:
    1. Detect current user state
    2. Select appropriate inquiry approach
    3. Retrieve matching question templates
    4. Adapt questions based on profile (directness, pacing, etc.)

    Args:
        request: Question generation request with context and parameters

    Returns:
        QuestionBatch with generated questions and metadata
    """
    try:
        # Load profile if user_id provided
        profile = None
        if request.user_id:
            profile = await profile_service.get_profile(request.user_id)

        # Detect state
        state = state_detection_service.detect_state(
            recent_messages=request.recent_messages,
            profile=profile,
        )

        # Select approach
        selection = approach_selection_service.select_approach(
            state=state,
            profile=profile,
        )

        # Get templates for selected approach
        templates = question_templates_service.get_templates_for_approach(
            approach=selection.selected_approach
        )

        if not templates:
            raise HTTPException(
                status_code=404,
                detail=f"No templates found for approach '{selection.selected_approach}'",
            )

        # Generate adapted questions
        questions = []
        adaptations_applied = []

        # Use different categories to get variety
        categories = question_templates_service.get_categories_for_approach(selection.selected_approach)
        templates_by_category = {cat: [] for cat in categories}
        for template in templates:
            templates_by_category[template.category].append(template)

        # Select templates from different categories
        selected_templates = []
        for category in categories:
            if templates_by_category[category]:
                selected_templates.append(templates_by_category[category][0])
            if len(selected_templates) >= request.num_questions:
                break

        # If we don't have enough variety, add more from any category
        while len(selected_templates) < request.num_questions and len(selected_templates) < len(templates):
            for template in templates:
                if template not in selected_templates:
                    selected_templates.append(template)
                    if len(selected_templates) >= request.num_questions:
                        break

        # Adapt each template
        for template in selected_templates[:request.num_questions]:
            # Adapt to directness level
            adapted = question_templates_service.adapt_template(
                template=template,
                directness=selection.directness,
            )
            questions.append(adapted)

            # Track what adaptations were applied
            if selection.directness != "balanced":
                adaptations_applied.append(f"directness={selection.directness}")
            if selection.pacing != "moderate":
                adaptations_applied.append(f"pacing={selection.pacing}")
            if selection.abstraction != "mixed":
                adaptations_applied.append(f"abstraction={selection.abstraction}")

        # Remove duplicates from adaptations
        adaptations_applied = list(set(adaptations_applied))

        return QuestionBatch(
            approach=selection.selected_approach,
            state=state.primary_state,
            questions=questions,
            context=request.context,
            profile_adaptations_applied=adaptations_applied,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Question generation failed: {str(e)}",
        )


@router.get("/approaches")
async def list_approaches() -> dict[str, list[str]]:
    """
    List all available inquiry approaches and their recommended states.

    Returns a mapping of user states to recommended inquiry approaches,
    helping understand the Question Engine's decision logic.

    Returns:
        Dictionary mapping states to approach lists
    """
    from ies_backend.schemas.question_engine import STATE_TO_APPROACHES

    return {
        state.value: [approach.value for approach in approaches]
        for state, approaches in STATE_TO_APPROACHES.items()
    }


@router.get("/categories")
async def list_categories(
    approach: InquiryApproach | None = Query(None, description="Filter by approach"),
) -> list[str]:
    """
    List all available question categories.

    Args:
        approach: Optional filter by approach

    Returns:
        List of category names
    """
    try:
        categories = question_templates_service.get_categories_for_approach(approach=approach)
        return categories
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list categories: {str(e)}",
        )
