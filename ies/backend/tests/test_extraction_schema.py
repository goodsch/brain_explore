"""Tests for extraction profile schemas."""

import pytest
from pydantic import ValidationError

from ies_backend.schemas.extraction import (
    ExtractionProfile,
    ExtractionProfileCreate,
    ExtractionResult,
    ExtractionRunRequest,
    ExtractionRunResponse,
    QuestionExtractionProfile,
)


class TestQuestionExtractionProfile:
    """Tests for QuestionExtractionProfile schema."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        profile = QuestionExtractionProfile()

        assert profile.focus_concepts == []
        assert profile.relation_types == []
        assert profile.depth == 1

    def test_with_values(self):
        """Test creating profile with explicit values."""
        profile = QuestionExtractionProfile(
            focus_concepts=["executive function", "working memory"],
            relation_types=["causes", "enables"],
            depth=2,
        )

        assert profile.focus_concepts == ["executive function", "working memory"]
        assert profile.relation_types == ["causes", "enables"]
        assert profile.depth == 2

    def test_depth_validation(self):
        """Test that depth must be between 1 and 3."""
        # Valid depths
        QuestionExtractionProfile(depth=1)
        QuestionExtractionProfile(depth=2)
        QuestionExtractionProfile(depth=3)

        # Invalid depths
        with pytest.raises(ValidationError):
            QuestionExtractionProfile(depth=0)

        with pytest.raises(ValidationError):
            QuestionExtractionProfile(depth=4)

    def test_serialization(self):
        """Test JSON serialization."""
        profile = QuestionExtractionProfile(
            focus_concepts=["concept1"],
            relation_types=["supports"],
            depth=2,
        )

        data = profile.model_dump()
        assert data == {
            "focus_concepts": ["concept1"],
            "relation_types": ["supports"],
            "depth": 2,
        }


class TestExtractionProfile:
    """Tests for ExtractionProfile schema."""

    def test_minimal_profile(self):
        """Test creating profile with only required fields."""
        profile = ExtractionProfile(context_id="ctx_123")

        assert profile.context_id == "ctx_123"
        assert profile.core_concepts == []
        assert profile.synonyms == {}
        assert profile.relation_types == []
        assert profile.domain_filters == []
        assert profile.question_overrides is None

    def test_full_profile(self):
        """Test creating profile with all fields."""
        question_profile = QuestionExtractionProfile(
            focus_concepts=["memory"],
            relation_types=["causes"],
            depth=2,
        )

        profile = ExtractionProfile(
            context_id="ctx_123",
            core_concepts=["executive function", "ADHD"],
            synonyms={
                "executive function": ["EF", "cognitive control"],
                "ADHD": ["attention deficit", "ADD"],
            },
            relation_types=["supports", "contradicts", "enables"],
            domain_filters=["neuroscience", "psychology"],
            question_overrides={"q_456": question_profile},
        )

        assert profile.context_id == "ctx_123"
        assert len(profile.core_concepts) == 2
        assert "executive function" in profile.core_concepts
        assert profile.synonyms["ADHD"] == ["attention deficit", "ADD"]
        assert "supports" in profile.relation_types
        assert "psychology" in profile.domain_filters
        assert profile.question_overrides["q_456"].depth == 2

    def test_serialization(self):
        """Test JSON serialization."""
        profile = ExtractionProfile(
            context_id="ctx_123",
            core_concepts=["concept1", "concept2"],
            synonyms={"concept1": ["alt1"]},
            relation_types=["supports"],
            domain_filters=["domain1"],
        )

        data = profile.model_dump()
        assert data["context_id"] == "ctx_123"
        assert data["core_concepts"] == ["concept1", "concept2"]
        assert data["synonyms"] == {"concept1": ["alt1"]}
        assert data["relation_types"] == ["supports"]
        assert data["domain_filters"] == ["domain1"]

    def test_deserialization(self):
        """Test creating profile from dict."""
        data = {
            "context_id": "ctx_123",
            "core_concepts": ["concept1"],
            "synonyms": {"concept1": ["alt1"]},
            "relation_types": ["supports"],
            "domain_filters": ["domain1"],
            "question_overrides": {
                "q_456": {
                    "focus_concepts": ["focus1"],
                    "relation_types": ["causes"],
                    "depth": 2,
                }
            },
        }

        profile = ExtractionProfile(**data)
        assert profile.context_id == "ctx_123"
        assert profile.core_concepts == ["concept1"]
        assert profile.question_overrides["q_456"].depth == 2


class TestExtractionResult:
    """Tests for ExtractionResult schema."""

    def test_minimal_result(self):
        """Test creating result with only required fields."""
        result = ExtractionResult(context_id="ctx_123")

        assert result.context_id == "ctx_123"
        assert result.concepts_found == []
        assert result.relations_found == []
        assert result.subquestions_generated == []
        assert result.sources_processed == 0
        assert result.segments_analyzed == 0

    def test_full_result(self):
        """Test creating result with all fields."""
        result = ExtractionResult(
            context_id="ctx_123",
            concepts_found=["concept1", "concept2"],
            relations_found=[
                {"source": "concept1", "target": "concept2", "type": "supports"},
            ],
            subquestions_generated=["What about X?", "How does Y work?"],
            sources_processed=5,
            segments_analyzed=42,
        )

        assert result.context_id == "ctx_123"
        assert len(result.concepts_found) == 2
        assert len(result.relations_found) == 1
        assert result.relations_found[0]["type"] == "supports"
        assert len(result.subquestions_generated) == 2
        assert result.sources_processed == 5
        assert result.segments_analyzed == 42

    def test_negative_counts_invalid(self):
        """Test that negative counts are not allowed."""
        with pytest.raises(ValidationError):
            ExtractionResult(
                context_id="ctx_123",
                sources_processed=-1,
            )

        with pytest.raises(ValidationError):
            ExtractionResult(
                context_id="ctx_123",
                segments_analyzed=-5,
            )

    def test_serialization(self):
        """Test JSON serialization."""
        result = ExtractionResult(
            context_id="ctx_123",
            concepts_found=["concept1"],
            relations_found=[{"source": "a", "target": "b", "type": "supports"}],
            sources_processed=3,
        )

        data = result.model_dump()
        assert data["context_id"] == "ctx_123"
        assert data["concepts_found"] == ["concept1"]
        assert len(data["relations_found"]) == 1
        assert data["sources_processed"] == 3
        assert data["segments_analyzed"] == 0  # default


class TestExtractionProfileCreate:
    """Tests for ExtractionProfileCreate request schema."""

    def test_minimal_create(self):
        """Test creating profile create request with only required fields."""
        create = ExtractionProfileCreate(context_id="ctx_123")

        assert create.context_id == "ctx_123"
        assert create.core_concepts == []
        assert create.synonyms == {}
        assert create.relation_types == []
        assert create.domain_filters == []

    def test_full_create(self):
        """Test creating profile create request with all fields."""
        create = ExtractionProfileCreate(
            context_id="ctx_123",
            core_concepts=["concept1"],
            synonyms={"concept1": ["alt1"]},
            relation_types=["supports"],
            domain_filters=["domain1"],
        )

        assert create.context_id == "ctx_123"
        assert create.core_concepts == ["concept1"]
        assert create.synonyms == {"concept1": ["alt1"]}
        assert create.relation_types == ["supports"]
        assert create.domain_filters == ["domain1"]


class TestExtractionRunRequest:
    """Tests for ExtractionRunRequest schema."""

    def test_minimal_request(self):
        """Test creating extraction run request with only required fields."""
        request = ExtractionRunRequest(context_id="ctx_123")

        assert request.context_id == "ctx_123"
        assert request.question_id is None
        assert request.source_ids is None
        assert request.max_segments is None

    def test_full_request(self):
        """Test creating extraction run request with all fields."""
        request = ExtractionRunRequest(
            context_id="ctx_123",
            question_id="q_456",
            source_ids=["book_1", "book_2"],
            max_segments=100,
        )

        assert request.context_id == "ctx_123"
        assert request.question_id == "q_456"
        assert request.source_ids == ["book_1", "book_2"]
        assert request.max_segments == 100

    def test_max_segments_validation(self):
        """Test that max_segments must be positive."""
        # Valid
        ExtractionRunRequest(context_id="ctx_123", max_segments=1)
        ExtractionRunRequest(context_id="ctx_123", max_segments=1000)

        # Invalid
        with pytest.raises(ValidationError):
            ExtractionRunRequest(context_id="ctx_123", max_segments=0)

        with pytest.raises(ValidationError):
            ExtractionRunRequest(context_id="ctx_123", max_segments=-10)


class TestExtractionRunResponse:
    """Tests for ExtractionRunResponse schema."""

    def test_minimal_response(self):
        """Test creating extraction run response."""
        result = ExtractionResult(context_id="ctx_123")
        response = ExtractionRunResponse(result=result)

        assert response.result.context_id == "ctx_123"
        assert response.journey_entry_id is None

    def test_full_response(self):
        """Test creating extraction run response with all fields."""
        result = ExtractionResult(
            context_id="ctx_123",
            concepts_found=["concept1"],
            sources_processed=5,
        )
        response = ExtractionRunResponse(
            result=result,
            journey_entry_id="journey_789",
        )

        assert response.result.context_id == "ctx_123"
        assert response.result.concepts_found == ["concept1"]
        assert response.journey_entry_id == "journey_789"

    def test_serialization(self):
        """Test JSON serialization."""
        result = ExtractionResult(context_id="ctx_123")
        response = ExtractionRunResponse(
            result=result,
            journey_entry_id="journey_789",
        )

        data = response.model_dump()
        assert data["result"]["context_id"] == "ctx_123"
        assert data["journey_entry_id"] == "journey_789"


class TestSchemaIntegration:
    """Integration tests for schema interactions."""

    def test_extraction_workflow(self):
        """Test typical extraction workflow using schemas."""
        # 1. Create extraction profile
        profile_create = ExtractionProfileCreate(
            context_id="ctx_123",
            core_concepts=["executive function"],
            relation_types=["causes", "enables"],
        )

        # 2. Create full profile (simulating backend processing)
        profile = ExtractionProfile(
            context_id=profile_create.context_id,
            core_concepts=profile_create.core_concepts,
            relation_types=profile_create.relation_types,
        )

        # 3. Run extraction request
        run_request = ExtractionRunRequest(
            context_id="ctx_123",
            question_id="q_456",
            max_segments=50,
        )

        # 4. Create extraction result
        result = ExtractionResult(
            context_id=run_request.context_id,
            concepts_found=["executive function", "working memory"],
            relations_found=[
                {
                    "source": "executive function",
                    "target": "working memory",
                    "type": "enables",
                }
            ],
            subquestions_generated=["How does EF enable working memory?"],
            sources_processed=3,
            segments_analyzed=42,
        )

        # 5. Create response
        response = ExtractionRunResponse(
            result=result,
            journey_entry_id="journey_789",
        )

        # Verify complete workflow
        assert profile.context_id == run_request.context_id
        assert response.result.context_id == profile.context_id
        assert len(response.result.concepts_found) == 2
        assert response.journey_entry_id == "journey_789"

    def test_question_override_workflow(self):
        """Test extraction with question-specific overrides."""
        # Create question-specific profile
        question_profile = QuestionExtractionProfile(
            focus_concepts=["dopamine", "norepinephrine"],
            relation_types=["regulates", "influences"],
            depth=2,
        )

        # Create main profile with override
        profile = ExtractionProfile(
            context_id="ctx_123",
            core_concepts=["ADHD", "neurotransmitters"],
            relation_types=["causes"],
            question_overrides={"q_456": question_profile},
        )

        # Verify override is accessible
        assert "q_456" in profile.question_overrides
        override = profile.question_overrides["q_456"]
        assert "dopamine" in override.focus_concepts
        assert override.depth == 2

        # Run extraction for specific question
        run_request = ExtractionRunRequest(
            context_id="ctx_123",
            question_id="q_456",
        )

        # Verify question ID matches override key
        assert run_request.question_id == "q_456"
        assert run_request.question_id in profile.question_overrides
