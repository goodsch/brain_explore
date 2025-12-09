"""
Unit tests for relationship extraction (Pass 2).

Tests the RelationshipExtractor class with mocked OpenAI responses.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock

from library.graph.relationship_extractor import (
    RelationshipExtractor,
    ExtractedRelationship,
    RelationshipExtractionResult,
    deduplicate_relationships,
    validate_relationship,
)
from library.ingest.chunk import Chunk


# Mock OpenAI response data
MOCK_RESPONSE_VALID = {
    "relationships": [
        {
            "source": "Working Memory",
            "target": "Executive Function",
            "relation_type": "PART_OF",
            "evidence": "Working memory is a component of executive function.",
            "confidence": 0.95
        },
        {
            "source": "Executive Function Deficit",
            "target": "Self-Regulation Difficulty",
            "relation_type": "CAUSES",
            "evidence": "Deficits in executive function cause difficulties with self-regulation.",
            "confidence": 0.90
        },
        {
            "source": "ADHD",
            "target": "Neurotypical Development",
            "relation_type": "CONTRASTS_WITH",
            "evidence": "ADHD contrasts with neurotypical development patterns.",
            "confidence": 0.85
        }
    ]
}

MOCK_RESPONSE_LOW_CONFIDENCE = {
    "relationships": [
        {
            "source": "Concept A",
            "target": "Concept B",
            "relation_type": "CAUSES",
            "evidence": "Maybe A causes B.",
            "confidence": 0.3
        }
    ]
}

MOCK_RESPONSE_EMPTY = {
    "relationships": []
}

MOCK_RESPONSE_INVALID_TYPE = {
    "relationships": [
        {
            "source": "Entity A",
            "target": "Entity B",
            "relation_type": "INVALID_TYPE",
            "evidence": "Some evidence",
            "confidence": 0.8
        }
    ]
}

MOCK_RESPONSE_MISSING_FIELDS = {
    "relationships": [
        {
            "source": "Entity A",
            # Missing target
            "relation_type": "CAUSES",
            "evidence": "Some evidence",
            "confidence": 0.8
        }
    ]
}


@pytest.fixture
def sample_chunk():
    """Create a sample chunk for testing."""
    return Chunk(
        id="chunk_123",
        content="""
        Executive function includes several component processes: working memory,
        cognitive flexibility, and inhibitory control. Research by Barkley shows
        that deficits in these executive function components cause significant
        difficulties with self-regulation in individuals with ADHD. This contrasts
        with neurotypical development where executive functions develop uniformly.
        """,
        token_count=100,
        metadata={"test": True}
    )


@pytest.fixture
def sample_entities():
    """Sample entity names for testing."""
    return [
        "Working Memory",
        "Cognitive Flexibility",
        "Inhibitory Control",
        "Executive Function",
        "Executive Function Deficit",
        "Self-Regulation Difficulty",
        "ADHD",
        "Neurotypical Development"
    ]


class TestRelationshipExtractor:
    """Tests for RelationshipExtractor class."""

    @patch('library.graph.relationship_extractor.OpenAI')
    def test_extract_relationships_success(self, mock_openai_class, sample_chunk, sample_entities):
        """Test successful relationship extraction."""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(MOCK_RESPONSE_VALID)
        mock_client.chat.completions.create.return_value = mock_response

        # Create extractor after mocking OpenAI
        extractor = RelationshipExtractor(
            model="gpt-4o-mini",
            confidence_threshold=0.5
        )

        # Extract relationships
        result = extractor._extract_from_chunk(sample_chunk, sample_entities)

        # Assertions
        assert isinstance(result, RelationshipExtractionResult)
        assert result.chunk_id == "chunk_123"
        assert len(result.relationships) == 3
        assert result.entities_present == sample_entities

        # Check first relationship
        rel = result.relationships[0]
        assert rel.source == "Working Memory"
        assert rel.target == "Executive Function"
        assert rel.relation_type == "PART_OF"
        assert rel.confidence == 0.95
        assert "component" in rel.evidence.lower()
        assert rel.chunk_id == "chunk_123"

    @patch('library.graph.relationship_extractor.OpenAI')
    def test_extract_filters_low_confidence(self, mock_openai_class, sample_chunk, sample_entities):
        """Test that low confidence relationships are filtered out."""
        # Mock OpenAI response with low confidence
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(MOCK_RESPONSE_LOW_CONFIDENCE)
        mock_client.chat.completions.create.return_value = mock_response

        extractor = RelationshipExtractor()

        # Extract relationships
        result = extractor._extract_from_chunk(sample_chunk, sample_entities)

        # Should filter out relationship with confidence 0.3 (threshold is 0.5)
        assert len(result.relationships) == 0

    @patch('library.graph.relationship_extractor.OpenAI')
    def test_extract_handles_empty_response(self, mock_openai_class, sample_chunk, sample_entities):
        """Test handling of empty relationships array."""
        # Mock OpenAI response with no relationships
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(MOCK_RESPONSE_EMPTY)
        mock_client.chat.completions.create.return_value = mock_response

        extractor = RelationshipExtractor()

        # Extract relationships
        result = extractor._extract_from_chunk(sample_chunk, sample_entities)

        # Should return empty result
        assert len(result.relationships) == 0

    @patch('library.graph.relationship_extractor.OpenAI')
    def test_extract_handles_malformed_json(self, mock_openai_class, sample_chunk, sample_entities):
        """Test handling of malformed JSON response."""
        # Mock OpenAI response with invalid JSON
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is not valid JSON {invalid}"
        mock_client.chat.completions.create.return_value = mock_response

        extractor = RelationshipExtractor()

        # Extract relationships (should handle gracefully)
        result = extractor._extract_from_chunk(sample_chunk, sample_entities)

        # Should return empty result on parse error
        assert len(result.relationships) == 0

    @patch('library.graph.relationship_extractor.OpenAI')
    def test_extract_handles_markdown_code_blocks(self, mock_openai_class, sample_chunk, sample_entities):
        """Test handling of JSON wrapped in markdown code blocks."""
        # Mock OpenAI response with markdown wrapper
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Here's the result:\n```json\n" +
            json.dumps(MOCK_RESPONSE_VALID) +
            "\n```"
        )
        mock_client.chat.completions.create.return_value = mock_response

        extractor = RelationshipExtractor()

        # Extract relationships
        result = extractor._extract_from_chunk(sample_chunk, sample_entities)

        # Should successfully parse despite markdown wrapper
        assert len(result.relationships) == 3

    @patch('library.graph.relationship_extractor.OpenAI')
    def test_extract_filters_invalid_type(self, mock_openai_class, sample_chunk, sample_entities):
        """Test that relationships with invalid types are filtered."""
        # Mock OpenAI response with invalid relation type
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(MOCK_RESPONSE_INVALID_TYPE)
        mock_client.chat.completions.create.return_value = mock_response

        extractor = RelationshipExtractor()

        # Extract relationships
        result = extractor._extract_from_chunk(sample_chunk, sample_entities)

        # Should filter out invalid type
        assert len(result.relationships) == 0

    @patch('library.graph.relationship_extractor.OpenAI')
    def test_extract_filters_missing_fields(self, mock_openai_class, sample_chunk, sample_entities):
        """Test that relationships with missing fields are filtered."""
        # Mock OpenAI response with missing target
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(MOCK_RESPONSE_MISSING_FIELDS)
        mock_client.chat.completions.create.return_value = mock_response

        extractor = RelationshipExtractor()

        # Extract relationships
        result = extractor._extract_from_chunk(sample_chunk, sample_entities)

        # Should filter out relationship with missing target
        assert len(result.relationships) == 0

    @patch('library.graph.relationship_extractor.OpenAI')
    def test_extract_from_chunks_skips_low_entity_count(self, mock_openai_class):
        """Test that chunks with <2 entities are skipped."""
        # Create chunks with varying entity counts
        chunk1 = Chunk(id="chunk_1", content="Some text", token_count=10, metadata={})
        chunk2 = Chunk(id="chunk_2", content="More text", token_count=10, metadata={})
        chunk3 = Chunk(id="chunk_3", content="Even more text", token_count=10, metadata={})

        chunks_with_entities = [
            (chunk1, ["Entity A"]),  # Only 1 entity - should skip
            (chunk2, ["Entity B", "Entity C"]),  # 2 entities - should process
            (chunk3, ["Entity D", "Entity E", "Entity F"])  # 3 entities - should process
        ]

        # Mock OpenAI response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(MOCK_RESPONSE_EMPTY)
        mock_client.chat.completions.create.return_value = mock_response

        extractor = RelationshipExtractor()

        # Extract from chunks
        results = extractor.extract_relationships_from_chunks(chunks_with_entities)

        # Should only call OpenAI for chunk2 and chunk3 (skipped chunk1)
        assert mock_client.chat.completions.create.call_count == 2


class TestDeduplication:
    """Tests for relationship deduplication."""

    def test_deduplicate_removes_exact_duplicates(self):
        """Test that exact duplicates are removed."""
        rel1 = ExtractedRelationship(
            source="A",
            target="B",
            relation_type="CAUSES",
            evidence="Evidence 1",
            confidence=0.8,
            chunk_id="chunk_1"
        )
        rel2 = ExtractedRelationship(
            source="A",
            target="B",
            relation_type="CAUSES",
            evidence="Evidence 2",
            confidence=0.7,
            chunk_id="chunk_2"
        )

        deduplicated = deduplicate_relationships([rel1, rel2])

        # Should keep only one relationship
        assert len(deduplicated) == 1
        # Should keep the one with higher confidence
        assert deduplicated[0].confidence == 0.8
        # Should merge evidence
        assert "Evidence 1" in deduplicated[0].evidence
        assert "Evidence 2" in deduplicated[0].evidence

    def test_deduplicate_case_insensitive(self):
        """Test that deduplication is case-insensitive."""
        rel1 = ExtractedRelationship(
            source="Working Memory",
            target="Executive Function",
            relation_type="PART_OF",
            evidence="Evidence 1",
            confidence=0.9,
            chunk_id="chunk_1"
        )
        rel2 = ExtractedRelationship(
            source="working memory",
            target="executive function",
            relation_type="PART_OF",
            evidence="Evidence 2",
            confidence=0.8,
            chunk_id="chunk_2"
        )

        deduplicated = deduplicate_relationships([rel1, rel2])

        # Should deduplicate despite different case
        assert len(deduplicated) == 1

    def test_deduplicate_keeps_different_types_separate(self):
        """Test that same entities with different types are kept separate."""
        rel1 = ExtractedRelationship(
            source="A",
            target="B",
            relation_type="CAUSES",
            evidence="A causes B",
            confidence=0.8,
            chunk_id="chunk_1"
        )
        rel2 = ExtractedRelationship(
            source="A",
            target="B",
            relation_type="PART_OF",
            evidence="A is part of B",
            confidence=0.8,
            chunk_id="chunk_2"
        )

        deduplicated = deduplicate_relationships([rel1, rel2])

        # Should keep both (different types)
        assert len(deduplicated) == 2


class TestValidation:
    """Tests for relationship validation."""

    def test_validate_accepts_valid_relationship(self):
        """Test that valid relationships pass validation."""
        rel = ExtractedRelationship(
            source="Entity A",
            target="Entity B",
            relation_type="CAUSES",
            evidence="Entity A causes Entity B according to research.",
            confidence=0.8,
            chunk_id="chunk_1"
        )

        valid_entities = {"Entity A", "Entity B", "Entity C"}
        is_valid, reason = validate_relationship(rel, valid_entities)

        assert is_valid is True
        assert reason == "valid"

    def test_validate_rejects_low_confidence(self):
        """Test that low confidence relationships are rejected."""
        rel = ExtractedRelationship(
            source="Entity A",
            target="Entity B",
            relation_type="CAUSES",
            evidence="Some evidence",
            confidence=0.3,  # Below 0.5 threshold
            chunk_id="chunk_1"
        )

        valid_entities = {"Entity A", "Entity B"}
        is_valid, reason = validate_relationship(rel, valid_entities)

        assert is_valid is False
        assert "confidence too low" in reason

    def test_validate_rejects_self_loop(self):
        """Test that self-loops are rejected."""
        rel = ExtractedRelationship(
            source="Entity A",
            target="Entity A",  # Same as source
            relation_type="CAUSES",
            evidence="Some evidence",
            confidence=0.8,
            chunk_id="chunk_1"
        )

        valid_entities = {"Entity A"}
        is_valid, reason = validate_relationship(rel, valid_entities)

        assert is_valid is False
        assert "self-loop" in reason

    def test_validate_rejects_invalid_type(self):
        """Test that invalid relationship types are rejected."""
        rel = ExtractedRelationship(
            source="Entity A",
            target="Entity B",
            relation_type="INVALID_TYPE",
            evidence="Some evidence",
            confidence=0.8,
            chunk_id="chunk_1"
        )

        valid_entities = {"Entity A", "Entity B"}
        is_valid, reason = validate_relationship(rel, valid_entities)

        assert is_valid is False
        assert "invalid type" in reason

    def test_validate_rejects_unknown_source(self):
        """Test that relationships with unknown source are rejected."""
        rel = ExtractedRelationship(
            source="Unknown Entity",
            target="Entity B",
            relation_type="CAUSES",
            evidence="Some evidence",
            confidence=0.8,
            chunk_id="chunk_1"
        )

        valid_entities = {"Entity B"}  # Source not in set
        is_valid, reason = validate_relationship(rel, valid_entities)

        assert is_valid is False
        assert "source entity not found" in reason

    def test_validate_rejects_unknown_target(self):
        """Test that relationships with unknown target are rejected."""
        rel = ExtractedRelationship(
            source="Entity A",
            target="Unknown Entity",
            relation_type="CAUSES",
            evidence="Some evidence",
            confidence=0.8,
            chunk_id="chunk_1"
        )

        valid_entities = {"Entity A"}  # Target not in set
        is_valid, reason = validate_relationship(rel, valid_entities)

        assert is_valid is False
        assert "target entity not found" in reason

    def test_validate_rejects_insufficient_evidence(self):
        """Test that relationships with insufficient evidence are rejected."""
        rel = ExtractedRelationship(
            source="Entity A",
            target="Entity B",
            relation_type="CAUSES",
            evidence="Short",  # Less than 10 characters
            confidence=0.8,
            chunk_id="chunk_1"
        )

        valid_entities = {"Entity A", "Entity B"}
        is_valid, reason = validate_relationship(rel, valid_entities)

        assert is_valid is False
        assert "insufficient evidence" in reason

    def test_validate_case_insensitive_entity_check(self):
        """Test that entity validation is case-insensitive."""
        rel = ExtractedRelationship(
            source="Working Memory",
            target="Executive Function",
            relation_type="PART_OF",
            evidence="Working memory is part of executive function.",
            confidence=0.9,
            chunk_id="chunk_1"
        )

        # Entities in different case
        valid_entities = {"working memory", "executive function"}
        is_valid, reason = validate_relationship(rel, valid_entities)

        assert is_valid is True
        assert reason == "valid"
