"""Tests for the Question Feedback Service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ies_backend.schemas.question_engine import (
    FeedbackType,
    QuestionClass,
    QuestionFeedbackRequest,
)
from ies_backend.services.feedback_service import FeedbackService


@pytest.fixture
def feedback_service():
    """Create a FeedbackService instance."""
    return FeedbackService()


@pytest.fixture
def sample_feedback_request():
    """Create a sample feedback request."""
    return QuestionFeedbackRequest(
        user_id="test-user-123",
        question_text="What assumptions underlie your current approach?",
        question_class=QuestionClass.SCHEMA_PROBE,
        feedback_type=FeedbackType.HELPFUL,
        entity_id="concept-456",
        session_id="session-789",
        response_text="This helped me see my blind spots",
    )


@pytest.mark.asyncio
async def test_record_feedback_creates_response(feedback_service, sample_feedback_request):
    """Test that record_feedback returns a valid response."""
    # Mock the Neo4j driver
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.single = AsyncMock(return_value={"feedback_id": "fb-test123"})
    mock_session.run = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_driver = AsyncMock()
    mock_driver.session = MagicMock(return_value=mock_session)

    with patch.object(feedback_service, "_get_driver", return_value=mock_driver):
        response = await feedback_service.record_feedback(sample_feedback_request)

    assert response.recorded is True
    assert response.feedback_id.startswith("fb-")
    assert response.message is not None


@pytest.mark.asyncio
async def test_record_feedback_with_minimal_data(feedback_service):
    """Test feedback with only required fields."""
    minimal_request = QuestionFeedbackRequest(
        user_id="user-1",
        question_text="What do you mean by that?",
        feedback_type=FeedbackType.NOT_HELPFUL,
    )

    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.single = AsyncMock(return_value={"feedback_id": "fb-minimal"})
    mock_session.run = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_driver = AsyncMock()
    mock_driver.session = MagicMock(return_value=mock_session)

    with patch.object(feedback_service, "_get_driver", return_value=mock_driver):
        response = await feedback_service.record_feedback(minimal_request)

    assert response.recorded is True


@pytest.mark.asyncio
async def test_record_insight_feedback(feedback_service):
    """Test recording that a question led to an insight."""
    insight_request = QuestionFeedbackRequest(
        user_id="user-2",
        question_text="What if the opposite were true?",
        question_class=QuestionClass.COUNTERFACTUAL,
        feedback_type=FeedbackType.LED_TO_INSIGHT,
        response_text="I realized I was approaching this backwards!",
    )

    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.single = AsyncMock(return_value={"feedback_id": "fb-insight"})
    mock_session.run = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_driver = AsyncMock()
    mock_driver.session = MagicMock(return_value=mock_session)

    with patch.object(feedback_service, "_get_driver", return_value=mock_driver):
        response = await feedback_service.record_feedback(insight_request)

    assert response.recorded is True
    assert "fb-" in response.feedback_id


@pytest.mark.asyncio
async def test_get_feedback_stats(feedback_service):
    """Test getting aggregated feedback statistics."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.data = AsyncMock(return_value=[
        {"feedback_type": "helpful", "question_class": "schema_probe", "count": 10},
        {"feedback_type": "led_to_insight", "question_class": "schema_probe", "count": 3},
        {"feedback_type": "not_helpful", "question_class": "causal", "count": 2},
    ])
    mock_session.run = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_driver = AsyncMock()
    mock_driver.session = MagicMock(return_value=mock_session)

    with patch.object(feedback_service, "_get_driver", return_value=mock_driver):
        stats = await feedback_service.get_feedback_stats()

    assert stats["total"] == 15
    assert stats["by_type"]["helpful"] == 10
    assert stats["by_type"]["led_to_insight"] == 3
    assert "insight_rate" in stats


@pytest.mark.asyncio
async def test_get_effective_question_classes(feedback_service):
    """Test getting question classes with high insight rates."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.data = AsyncMock(return_value=[
        {"qc": "counterfactual", "total": 10, "insights": 4, "rate": 0.4},
        {"qc": "perspective_shift", "total": 8, "insights": 2, "rate": 0.25},
    ])
    mock_session.run = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_driver = AsyncMock()
    mock_driver.session = MagicMock(return_value=mock_session)

    with patch.object(feedback_service, "_get_driver", return_value=mock_driver):
        effective = await feedback_service.get_effective_question_classes(min_insight_rate=0.2)

    assert "counterfactual" in effective
    assert "perspective_shift" in effective


@pytest.mark.asyncio
async def test_get_user_effective_classes(feedback_service):
    """Test getting user-specific question class effectiveness."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    # User has strong preferences based on their feedback history
    mock_result.data = AsyncMock(return_value=[
        {"qc": "schema_probe", "total": 15, "helpful": 12, "insights": 5, "effectiveness": 0.8},
        {"qc": "counterfactual", "total": 10, "helpful": 7, "insights": 3, "effectiveness": 0.7},
        {"qc": "causal", "total": 8, "helpful": 2, "insights": 0, "effectiveness": 0.25},
    ])
    mock_session.run = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_driver = AsyncMock()
    mock_driver.session = MagicMock(return_value=mock_session)

    with patch.object(feedback_service, "_get_driver", return_value=mock_driver):
        weights = await feedback_service.get_user_effective_classes("test-user", min_sample=5)

    assert "schema_probe" in weights
    assert weights["schema_probe"] > weights["causal"]  # More effective = higher weight
    assert weights["counterfactual"] > weights["causal"]


@pytest.mark.asyncio
async def test_get_user_effective_classes_with_insufficient_data(feedback_service):
    """Test that Neo4j query filters out classes with insufficient samples."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    # The query filters WHERE total >= min_sample, so only qualifying classes are returned
    # This simulates what Neo4j would return after filtering
    mock_result.data = AsyncMock(return_value=[
        {"qc": "schema_probe", "total": 10, "helpful": 8, "insights": 2, "effectiveness": 0.8},
        # counterfactual would not be returned because total=3 < min_sample=5
    ])
    mock_session.run = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_driver = AsyncMock()
    mock_driver.session = MagicMock(return_value=mock_session)

    with patch.object(feedback_service, "_get_driver", return_value=mock_driver):
        weights = await feedback_service.get_user_effective_classes("test-user", min_sample=5)

    # Only schema_probe should be included (has 10 samples >= 5)
    assert "schema_probe" in weights
    assert len(weights) == 1  # Only one class returned
