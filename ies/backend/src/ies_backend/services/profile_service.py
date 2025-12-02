"""Profile service - business logic for profile management."""

import json
from datetime import datetime, timezone
from typing import Any

from ies_backend.schemas.profile import (
    AttentionProfile,
    CapacityCheckIn,
    CommunicationProfile,
    ExecutiveProfile,
    MaskingProfile,
    ProcessingProfile,
    ProfileObservation,
    ProfileUpdate,
    SensoryProfile,
    UserProfile,
)
from ies_backend.services.neo4j_client import Neo4jClient


class ProfileService:
    """Service for managing user profiles with Neo4j persistence."""

    async def get_profile(self, user_id: str) -> UserProfile | None:
        """Get profile by user ID from Neo4j."""
        query = """
        MATCH (p:UserProfile {user_id: $user_id})
        RETURN p
        """
        results = await Neo4jClient.execute_query(query, {"user_id": user_id})
        if not results:
            return None

        node = results[0]["p"]
        return self._node_to_profile(node)

    async def create_profile(
        self, user_id: str, display_name: str | None = None
    ) -> UserProfile:
        """Create a new profile with defaults in Neo4j."""
        profile = UserProfile(
            user_id=user_id,
            display_name=display_name,
            last_updated=datetime.now(timezone.utc).isoformat(),
        )

        query = """
        CREATE (p:UserProfile {
            user_id: $user_id,
            display_name: $display_name,
            processing: $processing,
            attention: $attention,
            communication: $communication,
            executive: $executive,
            sensory: $sensory,
            masking: $masking,
            onboarding_complete: $onboarding_complete,
            sessions_completed: $sessions_completed,
            last_updated: $last_updated
        })
        RETURN p
        """

        await Neo4jClient.execute_write(
            query,
            {
                "user_id": profile.user_id,
                "display_name": profile.display_name,
                "processing": json.dumps(profile.processing.model_dump()),
                "attention": json.dumps(profile.attention.model_dump()),
                "communication": json.dumps(profile.communication.model_dump()),
                "executive": json.dumps(profile.executive.model_dump()),
                "sensory": json.dumps(profile.sensory.model_dump()),
                "masking": json.dumps(profile.masking.model_dump()) if profile.masking else None,
                "onboarding_complete": profile.onboarding_complete,
                "sessions_completed": profile.sessions_completed,
                "last_updated": profile.last_updated,
            },
        )

        return profile

    async def update_profile(
        self, user_id: str, update: ProfileUpdate
    ) -> UserProfile | None:
        """Update profile dimensions in Neo4j."""
        profile = await self.get_profile(user_id)
        if not profile:
            return None

        # Apply updates - use the Pydantic models directly, not dicts
        if update.display_name is not None:
            profile.display_name = update.display_name
        if update.processing is not None:
            profile.processing = update.processing
        if update.attention is not None:
            profile.attention = update.attention
        if update.communication is not None:
            profile.communication = update.communication
        if update.executive is not None:
            profile.executive = update.executive
        if update.sensory is not None:
            profile.sensory = update.sensory
        if update.masking is not None:
            profile.masking = update.masking

        profile.last_updated = datetime.now(timezone.utc).isoformat()

        # Save to Neo4j
        query = """
        MATCH (p:UserProfile {user_id: $user_id})
        SET p.display_name = $display_name,
            p.processing = $processing,
            p.attention = $attention,
            p.communication = $communication,
            p.executive = $executive,
            p.sensory = $sensory,
            p.masking = $masking,
            p.onboarding_complete = $onboarding_complete,
            p.sessions_completed = $sessions_completed,
            p.last_updated = $last_updated
        RETURN p
        """

        await Neo4jClient.execute_write(
            query,
            {
                "user_id": profile.user_id,
                "display_name": profile.display_name,
                "processing": json.dumps(profile.processing.model_dump()),
                "attention": json.dumps(profile.attention.model_dump()),
                "communication": json.dumps(profile.communication.model_dump()),
                "executive": json.dumps(profile.executive.model_dump()),
                "sensory": json.dumps(profile.sensory.model_dump()),
                "masking": json.dumps(profile.masking.model_dump()) if profile.masking else None,
                "onboarding_complete": profile.onboarding_complete,
                "sessions_completed": profile.sessions_completed,
                "last_updated": profile.last_updated,
            },
        )

        return profile

    async def record_capacity(
        self, user_id: str, check_in: CapacityCheckIn
    ) -> UserProfile | None:
        """Record capacity check-in."""
        profile = await self.get_profile(user_id)
        if not profile:
            return None

        profile.attention.current_capacity = check_in.current_capacity
        profile.last_updated = datetime.now(timezone.utc).isoformat()

        query = """
        MATCH (p:UserProfile {user_id: $user_id})
        SET p.attention = $attention,
            p.last_updated = $last_updated
        RETURN p
        """

        await Neo4jClient.execute_write(
            query,
            {
                "user_id": user_id,
                "attention": json.dumps(profile.attention.model_dump()),
                "last_updated": profile.last_updated,
            },
        )

        return profile

    async def apply_observation(
        self, user_id: str, observation: ProfileObservation
    ) -> UserProfile | None:
        """Apply session observations to update profile.

        This is where the system learns about the user over time.
        """
        profile = await self.get_profile(user_id)
        if not profile:
            return None

        # Increment session count
        profile.sessions_completed += 1

        # Update hyperfocus triggers if new topics engaged deeply
        for topic in observation.topics_explored:
            if topic not in profile.attention.hyperfocus_triggers:
                # TODO: Only add if session showed deep engagement
                pass

        # Track approach effectiveness for future question selection
        # TODO: Store this in a separate analytics structure

        profile.last_updated = datetime.now(timezone.utc).isoformat()

        query = """
        MATCH (p:UserProfile {user_id: $user_id})
        SET p.sessions_completed = $sessions_completed,
            p.attention = $attention,
            p.last_updated = $last_updated
        RETURN p
        """

        await Neo4jClient.execute_write(
            query,
            {
                "user_id": user_id,
                "sessions_completed": profile.sessions_completed,
                "attention": json.dumps(profile.attention.model_dump()),
                "last_updated": profile.last_updated,
            },
        )

        return profile

    async def get_profile_summary(self, user_id: str) -> dict | None:
        """Get condensed profile summary for session context.

        Returns a prompt-friendly summary of key profile dimensions.
        """
        profile = await self.get_profile(user_id)
        if not profile:
            return None

        return {
            "user_id": profile.user_id,
            "display_name": profile.display_name,
            "current_capacity": profile.attention.current_capacity,
            "optimal_session_length": profile.attention.optimal_session_length,
            "processing_style": profile.processing.style.value,
            "pace_preference": profile.communication.pace.value,
            "directness": profile.communication.directness_preference,
            "structure_need": profile.executive.structure_need.value,
            "hyperfocus_triggers": profile.attention.hyperfocus_triggers[:5],
            "overwhelm_signals": profile.sensory.overwhelm_signals[:3],
            "sessions_completed": profile.sessions_completed,
            "onboarding_complete": profile.onboarding_complete,
        }

    def _node_to_profile(self, node: dict[str, Any]) -> UserProfile:
        """Convert Neo4j node to UserProfile model."""
        processing_data = json.loads(node.get("processing", "{}"))
        attention_data = json.loads(node.get("attention", "{}"))
        communication_data = json.loads(node.get("communication", "{}"))
        executive_data = json.loads(node.get("executive", "{}"))
        sensory_data = json.loads(node.get("sensory", "{}"))
        masking_data = node.get("masking")

        return UserProfile(
            user_id=node["user_id"],
            display_name=node.get("display_name"),
            processing=ProcessingProfile(**processing_data) if processing_data else ProcessingProfile(),
            attention=AttentionProfile(**attention_data) if attention_data else AttentionProfile(),
            communication=CommunicationProfile(**communication_data) if communication_data else CommunicationProfile(),
            executive=ExecutiveProfile(**executive_data) if executive_data else ExecutiveProfile(),
            sensory=SensoryProfile(**sensory_data) if sensory_data else SensoryProfile(),
            masking=MaskingProfile(**json.loads(masking_data)) if masking_data else None,
            onboarding_complete=node.get("onboarding_complete", False),
            sessions_completed=node.get("sessions_completed", 0),
            last_updated=node.get("last_updated"),
        )
