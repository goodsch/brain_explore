"""Approach selection service for choosing questioning strategy based on state and profile."""

from ..schemas.profile import (
    PacePreference,
    StructureNeed,
    UserProfile,
)
from ..schemas.question_engine import (
    ApproachSelection,
    InquiryApproach,
    STATE_TO_APPROACHES,
    StateDetection,
    UserState,
)


class ApproachSelectionService:
    """Service for selecting inquiry approach based on user state and profile."""

    def select_approach(
        self,
        state: StateDetection,
        profile: UserProfile | None = None,
        previous_approach: InquiryApproach | None = None,
        session_duration_minutes: int = 0,
    ) -> ApproachSelection:
        """
        Select the best inquiry approach given detected state and user profile.

        Args:
            state: Detected user state
            profile: User's cognitive profile
            previous_approach: What approach was used most recently
            session_duration_minutes: How long the session has been going

        Returns:
            ApproachSelection with chosen approach and adaptations
        """
        # Get candidate approaches for this state
        candidates = STATE_TO_APPROACHES.get(
            state.primary_state,
            [InquiryApproach.SOCRATIC],
        )

        # Select primary approach
        selected = self._select_from_candidates(
            candidates,
            profile,
            previous_approach,
            state,
        )

        # Determine profile-based adaptations
        pacing = self._determine_pacing(profile, state, session_duration_minutes)
        directness = self._determine_directness(profile, state)
        abstraction = self._determine_abstraction(profile, state)
        structure = self._determine_structure(profile, state)

        # Build reasoning
        reasoning = self._build_reasoning(
            state, selected, profile, pacing, directness
        )

        # Determine fallback approaches
        fallbacks = [c for c in candidates if c != selected]
        if not fallbacks:
            # Add default fallback
            fallbacks = [InquiryApproach.SOCRATIC]

        return ApproachSelection(
            selected_approach=selected,
            confidence=state.confidence * 0.9,  # Slightly reduce for selection uncertainty
            reasoning=reasoning,
            pacing=pacing,
            directness=directness,
            abstraction=abstraction,
            structure=structure,
            fallback_approaches=fallbacks[:2],
        )

    def _select_from_candidates(
        self,
        candidates: list[InquiryApproach],
        profile: UserProfile | None,
        previous_approach: InquiryApproach | None,
        state: StateDetection,
    ) -> InquiryApproach:
        """Select best approach from candidates based on context."""
        if not candidates:
            return InquiryApproach.SOCRATIC

        # Avoid repeating the same approach too much (unless it's working)
        if previous_approach and previous_approach in candidates:
            if state.primary_state in [UserState.STUCK, UserState.TIRED]:
                # Switch if not working
                candidates = [c for c in candidates if c != previous_approach]
                if not candidates:
                    candidates = [InquiryApproach.SOLUTION_FOCUSED]

        # Profile-based preference
        if profile:
            # High abstraction preference → favor Systems, Metacognitive
            if profile.processing.abstraction_preference and profile.processing.abstraction_preference >= 7:
                for approach in [InquiryApproach.SYSTEMS, InquiryApproach.METACOGNITIVE]:
                    if approach in candidates:
                        return approach

            # Intuitive style → favor Phenomenological
            if profile.processing.decision_style and profile.processing.decision_style.value == "intuitive":
                if InquiryApproach.PHENOMENOLOGICAL in candidates:
                    return InquiryApproach.PHENOMENOLOGICAL

            # High structure need → favor Socratic (clear, logical)
            if profile.executive.structure_need == StructureNeed.RIGID:
                if InquiryApproach.SOCRATIC in candidates:
                    return InquiryApproach.SOCRATIC

        # Default: first candidate
        return candidates[0]

    def _determine_pacing(
        self,
        profile: UserProfile | None,
        state: StateDetection,
        session_minutes: int,
    ) -> str:
        """Determine conversation pacing."""
        # State-based adjustments
        if state.primary_state in [UserState.OVERWHELMED, UserState.TIRED]:
            return "slow"
        if state.primary_state == UserState.PROCESSING:
            return "slow"
        if state.primary_state == UserState.FLOWING:
            return "fast"

        # Session duration fatigue
        if session_minutes > 45:
            return "slow"

        # Profile-based
        if profile:
            if profile.communication.pace == PacePreference.SLOW:
                return "slow"
            if profile.communication.pace == PacePreference.FAST:
                return "fast"
            # Check capacity
            if profile.attention.current_capacity and profile.attention.current_capacity <= 5:
                return "slow"

        return "moderate"

    def _determine_directness(
        self,
        profile: UserProfile | None,
        state: StateDetection,
    ) -> str:
        """Determine how direct to be in questioning."""
        # State-based: gentler when vulnerable
        if state.primary_state in [UserState.OVERWHELMED, UserState.EMOTIONAL]:
            return "gentle"
        if state.primary_state == UserState.TIRED:
            return "gentle"

        # State-based: more direct when stuck
        if state.primary_state == UserState.STUCK:
            return "direct"

        # Profile-based
        if profile:
            pref = profile.communication.directness_preference
            if pref is not None:
                if pref >= 7:
                    return "direct"
                elif pref <= 4:
                    return "gentle"

        return "balanced"

    def _determine_abstraction(
        self,
        profile: UserProfile | None,
        state: StateDetection,
    ) -> str:
        """Determine abstraction level for questions."""
        # State-based: concrete when overwhelmed or tired
        if state.primary_state in [UserState.OVERWHELMED, UserState.TIRED]:
            return "concrete"

        # Profile-based
        if profile:
            pref = profile.processing.abstraction_preference
            if pref is not None:
                if pref >= 7:
                    return "abstract"
                elif pref <= 4:
                    return "concrete"

        # Signal-based
        if state.signals_observed.abstraction_level:
            return state.signals_observed.abstraction_level

        return "mixed"

    def _determine_structure(
        self,
        profile: UserProfile | None,
        state: StateDetection,
    ) -> str:
        """Determine structure level (tight vs loose exploration)."""
        # State-based
        if state.primary_state == UserState.OVERWHELMED:
            return "tight"  # Clear boundaries help
        if state.primary_state == UserState.EXPLORING:
            return "loose"  # Let them wander
        if state.primary_state == UserState.UNCERTAIN:
            return "moderate"  # Some structure helps

        # Profile-based
        if profile:
            need = profile.executive.structure_need
            if need == StructureNeed.RIGID:
                return "tight"
            elif need == StructureNeed.FLEXIBLE:
                return "loose"

        return "moderate"

    def _build_reasoning(
        self,
        state: StateDetection,
        approach: InquiryApproach,
        profile: UserProfile | None,
        pacing: str,
        directness: str,
    ) -> str:
        """Build human-readable reasoning for the selection."""
        parts = []

        # State reasoning
        parts.append(f"Detected state: {state.primary_state.value}")
        if state.reasoning:
            parts.append(f"({state.reasoning})")

        # Approach reasoning
        approach_reasons = {
            InquiryApproach.SOCRATIC: "Using Socratic inquiry to clarify thinking",
            InquiryApproach.SOLUTION_FOCUSED: "Using solution-focused approach to build forward momentum",
            InquiryApproach.PHENOMENOLOGICAL: "Using phenomenological approach to access felt sense",
            InquiryApproach.SYSTEMS: "Using systems thinking to see connections",
            InquiryApproach.METACOGNITIVE: "Using metacognitive inquiry to reflect on process",
        }
        parts.append(approach_reasons.get(approach, f"Selected {approach.value} approach"))

        # Adaptation reasoning
        if pacing != "moderate":
            parts.append(f"Pacing: {pacing}")
        if directness != "balanced":
            parts.append(f"Directness: {directness}")

        return ". ".join(parts)


# Singleton instance
approach_selection_service = ApproachSelectionService()
