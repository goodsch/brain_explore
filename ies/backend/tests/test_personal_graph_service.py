"""Tests for PersonalGraphService - Wave 5 test coverage."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
import pytest

from ies_backend.schemas.personal import (
    CreateSparkRequest,
    EnergyLevel,
    EntityStatus,
    PromoteSparkRequest,
    ResonanceSignal,
)
from ies_backend.services.personal_graph_service import PersonalGraphService


@pytest.fixture
def sample_create_spark_request():
    """Sample spark creation request."""
    return CreateSparkRequest(
        title="Connection between EF and shame",
        content="Reading Barkley - realized shame blocks executive function access",
        resonance_signal=ResonanceSignal.SURPRISED,
        energy_level=EnergyLevel.MEDIUM,
        source_id="concept_executive_function",
        concept_ids=["concept_shame", "concept_adhd"],
        siyuan_block_id="block_123",
    )


@pytest.fixture
def mock_spark_node():
    """Mock spark node returned from Neo4j."""
    return {
        "id": "spark_abc123def456",
        "title": "Test Spark",
        "content": "Test content for spark",
        "resonance_signal": "curious",
        "energy_level": "medium",
        "status": "captured",
        "source_id": None,
        "concept_ids": [],
        "siyuan_block_id": None,
        "visit_count": 0,
        "created_at": "2025-12-06T10:00:00",
        "updated_at": None,
    }


@pytest.fixture
def mock_insight_node():
    """Mock insight node returned from Neo4j."""
    return {
        "id": "insight_abc123def456",
        "title": "Test Insight",
        "core_statement": "A key realization about ADHD",
        "supporting_evidence": ["Evidence 1", "Evidence 2"],
        "status": "captured",
        "created_at": "2025-12-06T10:00:00",
    }


class TestPersonalGraphServiceCreateSpark:
    """Tests for spark creation."""

    @pytest.mark.asyncio
    async def test_create_spark_returns_spark_response(self, sample_create_spark_request, mock_spark_node):
        """Test that create_spark returns a valid SparkResponse."""
        with patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_write",
            new_callable=AsyncMock,
        ) as mock_write:
            mock_write.return_value = [{"s": mock_spark_node}]

            result = await PersonalGraphService.create_spark(sample_create_spark_request)

            assert result is not None
            assert result.id.startswith("spark_") or result.id == mock_spark_node["id"]
            assert result.status == EntityStatus.CAPTURED

    @pytest.mark.asyncio
    async def test_create_spark_stores_resonance_signal(self, sample_create_spark_request, mock_spark_node):
        """Test that create_spark preserves resonance signal."""
        mock_spark_node["resonance_signal"] = "surprised"

        with patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_write",
            new_callable=AsyncMock,
        ) as mock_write:
            mock_write.return_value = [{"s": mock_spark_node}]

            result = await PersonalGraphService.create_spark(sample_create_spark_request)

            # Verify params included resonance_signal
            call_params = mock_write.call_args[0][1]
            assert call_params["resonance_signal"] == "surprised"

    @pytest.mark.asyncio
    async def test_create_spark_raises_on_failure(self, sample_create_spark_request):
        """Test that create_spark raises ValueError on creation failure."""
        with patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_write",
            new_callable=AsyncMock,
            return_value=[],
        ):
            with pytest.raises(ValueError, match="Failed to create spark"):
                await PersonalGraphService.create_spark(sample_create_spark_request)


class TestPersonalGraphServiceGetSpark:
    """Tests for spark retrieval."""

    @pytest.mark.asyncio
    async def test_get_spark_returns_spark(self, mock_spark_node):
        """Test that get_spark returns spark when found."""
        with patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[{"s": mock_spark_node}],
        ):
            result = await PersonalGraphService.get_spark("spark_abc123def456")

            assert result is not None
            assert result.id == "spark_abc123def456"

    @pytest.mark.asyncio
    async def test_get_spark_returns_none_for_nonexistent(self):
        """Test that get_spark returns None for non-existent spark."""
        with patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await PersonalGraphService.get_spark("nonexistent")

            assert result is None


class TestPersonalGraphServiceVisitSpark:
    """Tests for spark visit tracking."""

    @pytest.mark.asyncio
    async def test_visit_spark_returns_true_for_existing(self):
        """Test that visit_spark returns True for existing spark."""
        with patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_write",
            new_callable=AsyncMock,
            return_value=[{"id": "spark_abc123def456"}],
        ):
            result = await PersonalGraphService.visit_spark("spark_abc123def456")

            assert result is True

    @pytest.mark.asyncio
    async def test_visit_spark_returns_false_for_nonexistent(self):
        """Test that visit_spark returns False for non-existent spark."""
        with patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_write",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await PersonalGraphService.visit_spark("nonexistent")

            assert result is False


class TestPersonalGraphServicePromoteToInsight:
    """Tests for spark promotion to insight."""

    @pytest.mark.asyncio
    async def test_promote_to_insight_creates_insight(self, mock_spark_node, mock_insight_node):
        """Test that promote_to_insight creates an insight from spark."""
        promote_request = PromoteSparkRequest(
            core_statement="A key realization about ADHD and shame",
            supporting_evidence=["Evidence from reading", "Personal experience"],
        )

        with patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query, patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_write",
            new_callable=AsyncMock,
        ) as mock_write:
            # First query gets the spark
            mock_query.return_value = [{"s": mock_spark_node}]
            # Write creates the insight
            mock_write.return_value = [{"i": mock_insight_node}]

            result = await PersonalGraphService.promote_to_insight(
                "spark_abc123def456", promote_request
            )

            assert result is not None
            assert mock_write.call_count >= 1

    @pytest.mark.asyncio
    async def test_promote_to_insight_raises_for_nonexistent_spark(self):
        """Test that promote_to_insight raises ValueError for non-existent spark."""
        promote_request = PromoteSparkRequest(
            core_statement="Test statement",
            supporting_evidence=[],
        )

        with patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[],
        ), patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_write",
            new_callable=AsyncMock,
        ):
            with pytest.raises(ValueError, match="Spark not found"):
                await PersonalGraphService.promote_to_insight(
                    "nonexistent", promote_request
                )


class TestPersonalGraphServiceFinders:
    """Tests for spark finder methods."""

    @pytest.mark.asyncio
    async def test_find_sparks_by_resonance_returns_matching(self, mock_spark_node):
        """Test that find_sparks_by_resonance returns matching sparks."""
        with patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[{"s": mock_spark_node}],
        ):
            result = await PersonalGraphService.find_sparks_by_resonance(
                ResonanceSignal.CURIOUS
            )

            assert result is not None
            assert len(result.sparks) == 1

    @pytest.mark.asyncio
    async def test_find_sparks_by_energy_returns_matching(self, mock_spark_node):
        """Test that find_sparks_by_energy returns matching sparks."""
        with patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[{"s": mock_spark_node}],
        ):
            result = await PersonalGraphService.find_sparks_by_energy(EnergyLevel.MEDIUM)

            assert result is not None
            assert len(result.sparks) == 1

    @pytest.mark.asyncio
    async def test_find_unvisited_sparks_returns_sparks(self, mock_spark_node):
        """Test that find_unvisited_sparks returns sparks with low visit count."""
        with patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[{"s": mock_spark_node}],
        ):
            result = await PersonalGraphService.find_unvisited_sparks()

            assert result is not None
            assert len(result.sparks) == 1

    @pytest.mark.asyncio
    async def test_finders_return_empty_for_no_matches(self):
        """Test that finder methods return empty list when no matches."""
        with patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await PersonalGraphService.find_sparks_by_resonance(
                ResonanceSignal.EXCITED
            )

            assert result.sparks == []


class TestPersonalGraphServiceStats:
    """Tests for statistics retrieval."""

    @pytest.mark.asyncio
    async def test_get_stats_returns_statistics(self):
        """Test that get_stats returns graph statistics."""
        mock_stats = {
            "total_sparks": 10,
            "total_insights": 3,
            "total_threads": 2,
            "total_favorite_problems": 1,
            "captured": 5,
            "exploring": 3,
            "anchored": 2,
        }

        with patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
        ) as mock_query:
            # First call: main stats, second call: resonance breakdown
            mock_query.side_effect = [
                [mock_stats],
                [{"signal": "curious", "count": 5}, {"signal": "excited", "count": 3}],
            ]

            result = await PersonalGraphService.get_stats()

            assert result.total_sparks == 10
            assert result.total_insights == 3
            assert result.sparks_by_status["captured"] == 5
            assert result.sparks_by_resonance.get("curious") == 5

    @pytest.mark.asyncio
    async def test_get_stats_returns_empty_for_no_data(self):
        """Test that get_stats returns zeros when no data exists."""
        with patch(
            "ies_backend.services.personal_graph_service.Neo4jClient.execute_query",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await PersonalGraphService.get_stats()

            assert result.total_sparks == 0
            assert result.total_insights == 0
            assert result.sparks_by_status == {}
