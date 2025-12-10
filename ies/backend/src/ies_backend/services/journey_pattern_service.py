"""Journey Pattern Analysis Service.

Analyzes exploration patterns from journey data to provide:
- Entity clustering (co-occurrence analysis)
- Frequent entity detection
- Common exploration paths
- Personalized recommendations
- Natural language insights
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from itertools import combinations
import hashlib

from ..schemas.journey_patterns import (
    EntityCluster,
    EntityRecommendation,
    ExplorationPath,
    FrequentEntity,
    JourneyInsight,
    JourneyPatternAnalysis,
    JourneyPatternRequest,
)
from ..schemas.journey_timeline import (
    JourneyTimelineEntry,
    JourneyTimelineRequest,
    TimelineGrouping,
)
from .journey_timeline_service import JourneyTimelineService


class JourneyPatternService:
    """Service for analyzing journey patterns and generating recommendations."""

    @classmethod
    async def analyze_patterns(
        cls, request: JourneyPatternRequest
    ) -> JourneyPatternAnalysis:
        """Analyze journey patterns for a user.

        Args:
            request: Pattern analysis request with user_id and parameters

        Returns:
            Complete pattern analysis with clusters, paths, and recommendations
        """
        # Calculate time window
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=request.days_back)

        # Fetch journey data
        timeline_request = JourneyTimelineRequest(
            user_id=request.user_id,
            context_id=request.context_id,
            limit=10000,
            grouping=TimelineGrouping.BY_SESSION,
        )
        timeline = await JourneyTimelineService.build_timeline(timeline_request)

        # Flatten entries within time window
        all_entries = [
            entry
            for group in timeline.groups
            for entry in group.entries
            if entry.timestamp >= start_time
        ]

        if not all_entries:
            return JourneyPatternAnalysis(
                user_id=request.user_id,
                context_id=request.context_id,
                analysis_period_start=start_time,
                analysis_period_end=end_time,
                total_entries_analyzed=0,
            )

        # Run pattern analysis
        frequent_entities = cls._find_frequent_entities(
            all_entries, request.min_visits_for_frequent
        )
        sessions = cls._extract_sessions(timeline.groups)
        clusters = cls._find_entity_clusters(sessions)
        paths = cls._find_common_paths(sessions, request.min_path_frequency)

        # Generate recommendations
        recommendations = cls._generate_recommendations(
            frequent_entities, clusters, paths, request.max_recommendations
        )

        # Generate insights
        insights = cls._generate_insights(
            frequent_entities, clusters, paths, len(sessions)
        )

        # Calculate summary metrics
        unique_entities = set()
        for entry in all_entries:
            unique_entities.update(entry.entity_links)
            if entry.target_id:
                unique_entities.add(entry.target_id)

        total_dwell = sum(e.dwell_time_seconds or 0 for e in all_entries)
        avg_session_duration = (
            (total_dwell / len(sessions) / 60) if sessions else 0.0
        )

        # Breadth: unique entities / total visits
        total_entity_visits = sum(len(e.entity_links) for e in all_entries)
        breadth = (
            len(unique_entities) / total_entity_visits
            if total_entity_visits > 0
            else 0.0
        )

        # Depth: average visits per unique entity
        depth_raw = (
            total_entity_visits / len(unique_entities)
            if unique_entities
            else 0.0
        )
        depth = min(depth_raw / 10.0, 1.0)  # Normalize to 0-1

        return JourneyPatternAnalysis(
            user_id=request.user_id,
            context_id=request.context_id,
            analysis_period_start=start_time,
            analysis_period_end=end_time,
            total_entries_analyzed=len(all_entries),
            discovered_clusters=clusters[:10],  # Top 10 clusters
            frequent_entities=frequent_entities[:20],  # Top 20 frequent
            common_paths=paths[:10],  # Top 10 paths
            recommendations=recommendations,
            insights=insights,
            unique_entities_visited=len(unique_entities),
            total_sessions=len(sessions),
            avg_session_duration_minutes=avg_session_duration,
            exploration_breadth_score=min(breadth, 1.0),
            exploration_depth_score=depth,
        )

    @classmethod
    def _find_frequent_entities(
        cls, entries: list[JourneyTimelineEntry], min_visits: int
    ) -> list[FrequentEntity]:
        """Find entities that are frequently visited."""
        entity_data: dict[str, dict] = defaultdict(
            lambda: {
                "name": "",
                "type": None,
                "visits": 0,
                "dwell": 0.0,
                "last_visited": None,
            }
        )

        for entry in entries:
            # Count target entities
            if entry.target_id:
                data = entity_data[entry.target_id]
                data["name"] = entry.target_name or entry.target_id
                data["type"] = entry.target_type
                data["visits"] += 1
                data["dwell"] += entry.dwell_time_seconds or 0
                if data["last_visited"] is None or entry.timestamp > data["last_visited"]:
                    data["last_visited"] = entry.timestamp

            # Count linked entities
            for entity_id in entry.entity_links:
                data = entity_data[entity_id]
                data["visits"] += 1
                data["dwell"] += (entry.dwell_time_seconds or 0) / max(
                    len(entry.entity_links), 1
                )
                if data["last_visited"] is None or entry.timestamp > data["last_visited"]:
                    data["last_visited"] = entry.timestamp

        # Filter and sort
        frequent = []
        for entity_id, data in entity_data.items():
            if data["visits"] >= min_visits:
                frequent.append(
                    FrequentEntity(
                        entity_id=entity_id,
                        entity_name=data["name"] or entity_id,
                        entity_type=data["type"],
                        visit_count=data["visits"],
                        total_dwell_seconds=data["dwell"],
                        avg_dwell_seconds=(
                            data["dwell"] / data["visits"] if data["visits"] > 0 else 0
                        ),
                        last_visited=data["last_visited"],
                    )
                )

        return sorted(frequent, key=lambda x: x.visit_count, reverse=True)

    @classmethod
    def _extract_sessions(cls, groups) -> list[list[str]]:
        """Extract entity sequences from session groups."""
        sessions = []
        for group in groups:
            session_entities = []
            for entry in group.entries:
                if entry.target_id:
                    session_entities.append(entry.target_id)
                session_entities.extend(entry.entity_links)
            if session_entities:
                sessions.append(session_entities)
        return sessions

    @classmethod
    def _find_entity_clusters(
        cls, sessions: list[list[str]]
    ) -> list[EntityCluster]:
        """Find clusters of entities that are frequently explored together."""
        # Build co-occurrence matrix
        cooccurrence: dict[tuple[str, str], int] = defaultdict(int)
        entity_counts: dict[str, int] = defaultdict(int)

        for session in sessions:
            unique_in_session = list(set(session))
            for entity in unique_in_session:
                entity_counts[entity] += 1
            for e1, e2 in combinations(sorted(unique_in_session), 2):
                cooccurrence[(e1, e2)] += 1

        # Find clusters using simple threshold-based grouping
        clusters: list[EntityCluster] = []
        visited = set()

        # Sort entities by frequency
        sorted_entities = sorted(
            entity_counts.keys(), key=lambda x: entity_counts[x], reverse=True
        )

        for seed in sorted_entities:
            if seed in visited:
                continue

            cluster_entities = [seed]
            visited.add(seed)

            # Find strongly co-occurring entities
            for other in sorted_entities:
                if other in visited:
                    continue
                pair = tuple(sorted([seed, other]))
                co_count = cooccurrence.get(pair, 0)
                min_count = min(entity_counts[seed], entity_counts[other])
                if min_count > 0 and co_count / min_count >= 0.3:  # 30% threshold
                    cluster_entities.append(other)
                    visited.add(other)

            if len(cluster_entities) >= 2:
                # Calculate cohesion score
                total_pairs = len(cluster_entities) * (len(cluster_entities) - 1) / 2
                co_sum = sum(
                    cooccurrence.get(tuple(sorted([e1, e2])), 0)
                    for e1, e2 in combinations(cluster_entities, 2)
                )
                max_possible = sum(
                    min(entity_counts[e1], entity_counts[e2])
                    for e1, e2 in combinations(cluster_entities, 2)
                )
                cohesion = co_sum / max_possible if max_possible > 0 else 0.0

                cluster_id = hashlib.md5(
                    ",".join(sorted(cluster_entities)).encode()
                ).hexdigest()[:8]

                clusters.append(
                    EntityCluster(
                        cluster_id=f"cluster_{cluster_id}",
                        entity_ids=cluster_entities,
                        entity_names=cluster_entities,  # Names same as IDs for now
                        cohesion_score=min(cohesion, 1.0),
                        visit_count=sum(entity_counts[e] for e in cluster_entities),
                    )
                )

        return sorted(clusters, key=lambda x: x.visit_count, reverse=True)

    @classmethod
    def _find_common_paths(
        cls, sessions: list[list[str]], min_frequency: int
    ) -> list[ExplorationPath]:
        """Find common exploration paths (sequences of 2-4 entities)."""
        path_counts: dict[tuple, int] = defaultdict(int)
        path_durations: dict[tuple, list[float]] = defaultdict(list)

        for session in sessions:
            # Extract subsequences of length 2-4
            for length in range(2, min(5, len(session) + 1)):
                for i in range(len(session) - length + 1):
                    path = tuple(session[i : i + length])
                    path_counts[path] += 1

        # Filter by frequency
        paths = []
        for path, count in path_counts.items():
            if count >= min_frequency:
                path_id = hashlib.md5("->".join(path).encode()).hexdigest()[:8]
                paths.append(
                    ExplorationPath(
                        path_id=f"path_{path_id}",
                        sequence=list(path),
                        sequence_names=list(path),  # Names same as IDs for now
                        frequency=count,
                        avg_duration_seconds=0.0,  # Would need timestamp data
                    )
                )

        return sorted(paths, key=lambda x: x.frequency, reverse=True)

    @classmethod
    def _generate_recommendations(
        cls,
        frequent: list[FrequentEntity],
        clusters: list[EntityCluster],
        paths: list[ExplorationPath],
        max_recommendations: int,
    ) -> list[EntityRecommendation]:
        """Generate entity recommendations based on patterns."""
        recommendations = []
        seen_entities = set()

        # From clusters: recommend less-visited entities in active clusters
        for cluster in clusters[:5]:
            if len(cluster.entity_ids) > 2:
                # Find the least visited in cluster
                for entity_id in cluster.entity_ids:
                    if entity_id not in seen_entities:
                        recommendations.append(
                            EntityRecommendation(
                                entity_id=entity_id,
                                entity_name=entity_id,
                                reason=f"Part of your '{cluster.cluster_id}' exploration cluster",
                                confidence=cluster.cohesion_score * 0.8,
                                source_pattern="cluster_member",
                            )
                        )
                        seen_entities.add(entity_id)
                        break

        # From paths: recommend next steps from common paths
        for path in paths[:5]:
            if len(path.sequence) >= 2:
                last_entity = path.sequence[-1]
                if last_entity not in seen_entities:
                    recommendations.append(
                        EntityRecommendation(
                            entity_id=last_entity,
                            entity_name=last_entity,
                            reason=f"Common exploration path leads here ({path.frequency}x)",
                            confidence=min(path.frequency / 10.0, 0.9),
                            source_pattern="common_path",
                        )
                    )
                    seen_entities.add(last_entity)

        # From frequent: recommend revisiting high-dwell entities
        for entity in frequent[:5]:
            if entity.entity_id not in seen_entities and entity.avg_dwell_seconds > 60:
                recommendations.append(
                    EntityRecommendation(
                        entity_id=entity.entity_id,
                        entity_name=entity.entity_name,
                        entity_type=entity.entity_type,
                        reason=f"You've spent significant time here ({entity.avg_dwell_seconds:.0f}s avg)",
                        confidence=0.7,
                        source_pattern="high_engagement",
                    )
                )
                seen_entities.add(entity.entity_id)

        return sorted(
            recommendations[:max_recommendations],
            key=lambda x: x.confidence,
            reverse=True,
        )

    @classmethod
    def _generate_insights(
        cls,
        frequent: list[FrequentEntity],
        clusters: list[EntityCluster],
        paths: list[ExplorationPath],
        session_count: int,
    ) -> list[JourneyInsight]:
        """Generate natural language insights from patterns."""
        insights = []

        # Exploration habit insights
        if frequent:
            top = frequent[0]
            insights.append(
                JourneyInsight(
                    insight_type="exploration_habit",
                    message=f"You frequently explore '{top.entity_name}' ({top.visit_count} visits)",
                    supporting_data={"entity_id": top.entity_id, "visits": top.visit_count},
                )
            )

        # Cluster insights
        if clusters:
            top_cluster = clusters[0]
            if len(top_cluster.entity_ids) >= 3:
                insights.append(
                    JourneyInsight(
                        insight_type="emerging_interest",
                        message=f"You're building a knowledge cluster around {len(top_cluster.entity_ids)} related concepts",
                        supporting_data={
                            "cluster_size": len(top_cluster.entity_ids),
                            "cohesion": top_cluster.cohesion_score,
                        },
                    )
                )

        # Path insights
        if paths:
            top_path = paths[0]
            if top_path.frequency >= 3:
                path_str = " → ".join(top_path.sequence_names[:3])
                insights.append(
                    JourneyInsight(
                        insight_type="exploration_habit",
                        message=f"Common exploration pattern: {path_str}",
                        supporting_data={
                            "path": top_path.sequence,
                            "frequency": top_path.frequency,
                        },
                    )
                )

        # Session insights
        if session_count > 0:
            insights.append(
                JourneyInsight(
                    insight_type="exploration_habit",
                    message=f"You've had {session_count} exploration sessions in this period",
                    supporting_data={"sessions": session_count},
                )
            )

        return insights
