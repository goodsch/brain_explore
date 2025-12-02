"""Session context service - aggregates context for session start (Phase 4)."""

from ies_backend.schemas.entity import (
    ActiveEntity,
    EntityKind,
    EntityStatus,
    RecentSession,
    SessionContext,
)
from ies_backend.services.entity_storage_service import EntityStorageService
from ies_backend.services.profile_service import ProfileService


class SessionContextService:
    """Service for loading session context at session start."""

    def __init__(self) -> None:
        self.profile_service = ProfileService()
        self.storage_service = EntityStorageService()

    async def get_context(self, user_id: str) -> SessionContext:
        """Get full session context for a user.

        Aggregates:
        - Profile summary + current capacity
        - Last 2-3 session summaries (medium detail)
        - Active developing/seed entities

        Args:
            user_id: User ID

        Returns:
            SessionContext with all data for session start
        """
        # Get profile and summary
        profile = await self.profile_service.get_profile(user_id)
        profile_summary_dict = await self.profile_service.get_profile_summary(user_id)

        # Format profile summary as string for prompts
        if profile_summary_dict:
            profile_summary = (
                f"{profile_summary_dict.get('processing_style', 'Unknown')} thinker. "
                f"Pace: {profile_summary_dict.get('pace_preference', 'moderate')}. "
                f"Structure need: {profile_summary_dict.get('structure_need', 'moderate')}."
            )
        else:
            profile_summary = "No profile configured. Consider running /onboard-profile."

        # Get current capacity from profile
        capacity = None
        if profile and profile.attention:
            capacity = profile.attention.current_capacity

        # Get recent sessions (last 3)
        recent_sessions_raw = await self.storage_service.get_recent_sessions(
            user_id, limit=3
        )
        recent_sessions = [
            RecentSession(
                date=s.get("date", ""),
                topic=s.get("topic", ""),
                entities=s.get("entity_names", []),
                hanging_question=s.get("hanging_question"),
            )
            for s in recent_sessions_raw
        ]

        # Get active entities (developing or seed status)
        active_entities_raw = await self.storage_service.get_active_entities(
            user_id, limit=10
        )
        active_entities = [
            ActiveEntity(
                name=e.get("name", ""),
                status=EntityStatus(e.get("status", "seed")),
                kind=EntityKind(e.get("kind", "idea")),
                last_updated=e.get("updated_at"),
            )
            for e in active_entities_raw
        ]

        return SessionContext(
            profile_summary=profile_summary,
            capacity=capacity,
            recent_sessions=recent_sessions,
            active_entities=active_entities,
        )


# Singleton instance
session_context_service = SessionContextService()
