"""Tests for JourneyPatternService."""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, AsyncMock

from ies_backend.schemas.journey_patterns import (
    JourneyPatternRequest,
    JourneyPatternAnalysis,
    FrequentEntity,
    EntityCluster,
    ExplorationPath,
)
from ies_backend.schemas.journey_timeline import (
    JourneyTimelineEntry,
    JourneyTimelineResponse,
    TimelineGroup,
    TimelineEntryType,
    TimelineGrouping,
)
from ies_backend.services.journey_pattern_service import JourneyPatternService


class TestJourneyPatternService:
    """Tests for JourneyPatternService."""

    @pytest.fixture
    def sample_entries(self) -> list[JourneyTimelineEntry]:
        """Create sample journey entries for testing."""
        now = datetime.now(timezone.utc)
        return [
            JourneyTimelineEntry(
                id="e1",
                timestamp=now - timedelta(hours=1),
                entry_type=TimelineEntryType.ENTITY_VISIT,
                title="Visit Concept A",
                target_id="concept_a",
                target_name="Concept A",
                target_type="Concept",
                entity_links=["concept_a", "concept_b"],
                dwell_time_seconds=120,
            ),
            JourneyTimelineEntry(
                id="e2",
                timestamp=now - timedelta(hours=2),
                entry_type=TimelineEntryType.ENTITY_VISIT,
                title="Visit Concept B",
                target_id="concept_b",
                target_name="Concept B",
                target_type="Concept",
                entity_links=["concept_b", "concept_c"],
                dwell_time_seconds=180,
            ),
            JourneyTimelineEntry(
                id="e3",
                timestamp=now - timedelta(hours=3),
                entry_type=TimelineEntryType.ENTITY_VISIT,
                title="Visit Concept A again",
                target_id="concept_a",
                target_name="Concept A",
                target_type="Concept",
                entity_links=["concept_a"],
                dwell_time_seconds=90,
            ),
            JourneyTimelineEntry(
                id="e4",
                timestamp=now - timedelta(hours=4),
                entry_type=TimelineEntryType.ENTITY_VISIT,
                title="Visit Concept C",
                target_id="concept_c",
                target_name="Concept C",
                target_type="Concept",
                entity_links=["concept_c", "concept_a"],
                dwell_time_seconds=60,
            ),
        ]

    @pytest.fixture
    def mock_timeline_response(self, sample_entries) -> JourneyTimelineResponse:
        """Create a mock timeline response."""
        return JourneyTimelineResponse(
            groups=[
                TimelineGroup(
                    group_key="session_1",
                    group_label="Session 1",
                    start_time=datetime.now(timezone.utc) - timedelta(hours=4),
                    end_time=datetime.now(timezone.utc),
                    entry_count=len(sample_entries),
                    entries=sample_entries,
                )
            ],
            total_entries=len(sample_entries),
            total_groups=1,
        )

    async def test_analyze_patterns_empty(self):
        """Test analysis with no journey data."""
        empty_response = JourneyTimelineResponse(
            groups=[], total_entries=0, total_groups=0
        )

        with patch.object(
            JourneyPatternService,
            "_find_frequent_entities",
            return_value=[],
        ):
            with patch(
                "ies_backend.services.journey_pattern_service.JourneyTimelineService.build_timeline",
                new_callable=AsyncMock,
                return_value=empty_response,
            ):
                request = JourneyPatternRequest(user_id="test_user")
                result = await JourneyPatternService.analyze_patterns(request)

                assert result.user_id == "test_user"
                assert result.total_entries_analyzed == 0
                assert len(result.discovered_clusters) == 0
                assert len(result.recommendations) == 0

    async def test_analyze_patterns_with_data(self, mock_timeline_response):
        """Test analysis with journey data."""
        with patch(
            "ies_backend.services.journey_pattern_service.JourneyTimelineService.build_timeline",
            new_callable=AsyncMock,
            return_value=mock_timeline_response,
        ):
            request = JourneyPatternRequest(
                user_id="test_user",
                days_back=30,
                min_visits_for_frequent=2,
            )
            result = await JourneyPatternService.analyze_patterns(request)

            assert result.user_id == "test_user"
            assert result.total_entries_analyzed == 4
            assert result.unique_entities_visited > 0
            assert result.total_sessions == 1

    def test_find_frequent_entities(self, sample_entries):
        """Test frequent entity detection."""
        frequent = JourneyPatternService._find_frequent_entities(
            sample_entries, min_visits=2
        )

        # concept_a appears 3 times (2 as target, 2 in entity_links)
        assert len(frequent) > 0
        entity_ids = [e.entity_id for e in frequent]
        assert "concept_a" in entity_ids

    def test_find_frequent_entities_min_visits_filter(self, sample_entries):
        """Test that min_visits filter works."""
        frequent = JourneyPatternService._find_frequent_entities(
            sample_entries, min_visits=10
        )
        # No entity has 10+ visits
        assert len(frequent) == 0

    def test_extract_sessions(self, mock_timeline_response):
        """Test session extraction."""
        sessions = JourneyPatternService._extract_sessions(
            mock_timeline_response.groups
        )

        assert len(sessions) == 1
        assert len(sessions[0]) > 0

    def test_find_entity_clusters(self):
        """Test entity clustering."""
        # Create sessions with co-occurring entities
        sessions = [
            ["a", "b", "c"],
            ["a", "b", "d"],
            ["a", "b"],
            ["c", "d", "e"],
        ]

        clusters = JourneyPatternService._find_entity_clusters(sessions)

        # a and b should be clustered together (appear together 3 times)
        assert len(clusters) > 0
        # Find cluster containing both a and b
        ab_cluster = None
        for cluster in clusters:
            if "a" in cluster.entity_ids and "b" in cluster.entity_ids:
                ab_cluster = cluster
                break
        assert ab_cluster is not None

    def test_find_common_paths(self):
        """Test common path detection."""
        sessions = [
            ["a", "b", "c"],
            ["a", "b", "c"],
            ["a", "b", "d"],
            ["x", "y", "z"],
        ]

        paths = JourneyPatternService._find_common_paths(sessions, min_frequency=2)

        # a->b and a->b->c should be found
        path_sequences = [tuple(p.sequence) for p in paths]
        assert ("a", "b") in path_sequences
        assert ("a", "b", "c") in path_sequences

    def test_find_common_paths_min_frequency(self):
        """Test that min_frequency filter works."""
        sessions = [
            ["a", "b", "c"],
            ["x", "y", "z"],
        ]

        paths = JourneyPatternService._find_common_paths(sessions, min_frequency=2)

        # No path appears 2+ times
        assert len(paths) == 0

    def test_generate_recommendations(self):
        """Test recommendation generation."""
        frequent = [
            FrequentEntity(
                entity_id="entity_1",
                entity_name="Entity 1",
                visit_count=10,
                avg_dwell_seconds=120,
            ),
        ]
        clusters = [
            EntityCluster(
                cluster_id="cluster_1",
                entity_ids=["a", "b", "c"],
                entity_names=["A", "B", "C"],
                cohesion_score=0.8,
                visit_count=15,
            ),
        ]
        paths = [
            ExplorationPath(
                path_id="path_1",
                sequence=["x", "y", "z"],
                sequence_names=["X", "Y", "Z"],
                frequency=5,
            ),
        ]

        recommendations = JourneyPatternService._generate_recommendations(
            frequent, clusters, paths, max_recommendations=10
        )

        assert len(recommendations) > 0
        # Should have recommendations from clusters, paths, or frequent entities
        sources = [r.source_pattern for r in recommendations]
        assert any(s in ["cluster_member", "common_path", "high_engagement"] for s in sources)

    def test_generate_insights(self):
        """Test insight generation."""
        frequent = [
            FrequentEntity(
                entity_id="entity_1",
                entity_name="Test Entity",
                visit_count=10,
            ),
        ]
        clusters = [
            EntityCluster(
                cluster_id="cluster_1",
                entity_ids=["a", "b", "c"],
                entity_names=["A", "B", "C"],
                cohesion_score=0.8,
                visit_count=15,
            ),
        ]
        paths = [
            ExplorationPath(
                path_id="path_1",
                sequence=["x", "y"],
                sequence_names=["X", "Y"],
                frequency=5,
            ),
        ]

        insights = JourneyPatternService._generate_insights(
            frequent, clusters, paths, session_count=3
        )

        assert len(insights) > 0
        insight_types = [i.insight_type for i in insights]
        assert "exploration_habit" in insight_types


class TestJourneyPatternSchemas:
    """Tests for journey pattern schemas."""

    def test_journey_pattern_request_defaults(self):
        """Test default values in request."""
        request = JourneyPatternRequest(user_id="test")
        assert request.days_back == 30
        assert request.min_visits_for_frequent == 3
        assert request.max_recommendations == 10

    def test_journey_pattern_analysis_model(self):
        """Test analysis response model."""
        analysis = JourneyPatternAnalysis(
            user_id="test",
            analysis_period_start=datetime.now(timezone.utc) - timedelta(days=30),
            analysis_period_end=datetime.now(timezone.utc),
            total_entries_analyzed=100,
        )
        assert analysis.user_id == "test"
        assert len(analysis.discovered_clusters) == 0
        assert analysis.exploration_breadth_score == 0.0

    def test_entity_cluster_validation(self):
        """Test cohesion score validation."""
        cluster = EntityCluster(
            cluster_id="test",
            entity_ids=["a", "b"],
            entity_names=["A", "B"],
            cohesion_score=0.5,
            visit_count=10,
        )
        assert 0.0 <= cluster.cohesion_score <= 1.0

    def test_frequent_entity_model(self):
        """Test frequent entity model."""
        entity = FrequentEntity(
            entity_id="test",
            entity_name="Test",
            visit_count=5,
            total_dwell_seconds=300,
            avg_dwell_seconds=60,
        )
        assert entity.visit_count == 5
        assert entity.avg_dwell_seconds == 60
