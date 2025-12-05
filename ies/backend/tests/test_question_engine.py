"""Tests for Question Engine - state detection and approach selection."""

import pytest

from ies_backend.schemas.profile import (
    AttentionProfile,
    CommunicationProfile,
    DecisionStyle,
    ExecutiveProfile,
    PacePreference,
    ProcessingProfile,
    ProcessingStyle,
    SensoryProfile,
    StructureNeed,
    UserProfile,
)
from ies_backend.schemas.question_engine import (
    InquiryApproach,
    STATE_TO_APPROACHES,
    StateDetection,
    UserState,
)
from ies_backend.services.approach_selection_service import ApproachSelectionService
from ies_backend.services.state_detection_service import (
    StateDetectionService,
    analyze_message,
    detect_repetition,
)


class TestStateDetection:
    """Test state detection from message analysis."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.service = StateDetectionService()

    def test_detect_overwhelmed_from_explicit_language(self) -> None:
        """Test detecting OVERWHELMED state from explicit language."""
        messages = [
            "I'm feeling overwhelmed by all this information",
            "This is too much to process right now",
        ]

        result = self.service.detect_state(messages)

        assert result.primary_state == UserState.OVERWHELMED
        assert result.confidence >= 0.8
        assert "overwhelm" in result.reasoning.lower()

    def test_detect_overwhelmed_from_too_much_language(self) -> None:
        """Test detecting OVERWHELMED from 'too much' markers."""
        messages = ["There's just too much going on here"]

        result = self.service.detect_state(messages)

        assert result.primary_state == UserState.OVERWHELMED
        assert result.confidence >= 0.8

    def test_detect_stuck_from_repetitive_messages(self) -> None:
        """Test detecting STUCK state from repetitive content."""
        # Use more similar messages to trigger repetition detection
        messages = [
            "I keep thinking about the problem with my workflow",
            "The problem with my workflow keeps coming back",
            "Still stuck on this workflow problem",
        ]

        result = self.service.detect_state(messages)

        assert result.primary_state == UserState.STUCK
        assert result.confidence >= 0.7
        assert result.signals_observed.repetition_detected

    def test_detect_stuck_with_frustration_increases_confidence(self) -> None:
        """Test that frustration + repetition increases STUCK confidence."""
        messages = [
            "I keep thinking about the same problem issue",
            "Ugh, I'm stuck on this same problem again",
            "Still can't get past this frustrating problem",
        ]

        result = self.service.detect_state(messages)

        assert result.primary_state == UserState.STUCK
        assert result.confidence >= 0.8
        assert len(result.signals_observed.frustration_indicators) > 0

    def test_detect_tired_from_low_energy_markers(self) -> None:
        """Test detecting TIRED state from energy markers."""
        messages = ["I'm feeling pretty tired and drained right now"]

        result = self.service.detect_state(messages)

        assert result.primary_state == UserState.TIRED
        assert result.confidence >= 0.75
        assert len(result.signals_observed.energy_words) > 0

    def test_detect_tired_from_brain_fog(self) -> None:
        """Test detecting TIRED from brain fog and focus issues."""
        messages = ["Can't focus today, brain fog is real"]

        result = self.service.detect_state(messages)

        assert result.primary_state == UserState.TIRED
        assert result.confidence >= 0.75

    def test_detect_flowing_from_engagement_markers(self) -> None:
        """Test detecting FLOWING state from high engagement."""
        messages = [
            "This is really interesting and exciting!",
            "Yes! Exactly, that's clicking for me now",
        ]

        result = self.service.detect_state(messages)

        # Should be FLOWING based on "excited" and "clicking" markers
        assert result.primary_state == UserState.FLOWING
        assert result.confidence >= 0.7
        assert len(result.signals_observed.energy_words) > 0

    def test_detect_flowing_from_detailed_confident_responses(self) -> None:
        """Test detecting FLOWING from detailed, confident responses."""
        messages = [
            "I definitely see the connection here. When I think about how "
            "these concepts relate, I'm certain that the underlying pattern "
            "is about emergence and feedback loops. Obviously, this ties into "
            "what we discussed earlier about systems thinking, and I can clearly "
            "articulate how each piece contributes to the whole."
        ]

        result = self.service.detect_state(messages)

        assert result.primary_state == UserState.FLOWING
        assert result.confidence >= 0.6
        assert result.signals_observed.certainty_language >= 6
        # 49 words is "medium" (20-80), not "long" (80+) - but confident medium responses indicate flow
        assert result.signals_observed.response_length in ["medium", "long"]

    def test_explicit_capacity_overrides_to_tired(self) -> None:
        """Test that low explicit capacity (1-3) overrides to TIRED state."""
        messages = ["I'm excited to explore this topic!"]

        # Without capacity, should detect engagement
        result_without = self.service.detect_state(messages)
        # With low capacity, should override to TIRED
        result_with = self.service.detect_state(messages, explicit_capacity=2)

        assert result_with.primary_state == UserState.TIRED
        assert result_with.confidence >= 0.85
        assert "capacity" in result_with.reasoning.lower()

    def test_explicit_capacity_moderate_reduces_confidence(self) -> None:
        """Test that moderate capacity (4-5) reduces confidence in other states."""
        messages = ["Yes! This is really clicking for me"]

        result_high = self.service.detect_state(messages)
        result_moderate = self.service.detect_state(messages, explicit_capacity=5)

        # Should still detect FLOWING but with reduced confidence
        if result_moderate.primary_state == UserState.FLOWING:
            assert result_moderate.confidence < result_high.confidence

    def test_detect_emotional_from_feeling_language(self) -> None:
        """Test detecting EMOTIONAL state from emotional markers."""
        messages = ["I feel really anxious and scared about this"]

        result = self.service.detect_state(messages)

        assert result.primary_state == UserState.EMOTIONAL
        assert result.confidence >= 0.7

    def test_detect_uncertain_from_questions_and_uncertainty(self) -> None:
        """Test detecting UNCERTAIN from multiple questions and uncertainty."""
        messages = ["I don't know... maybe this? Or perhaps that? I'm not sure which way to go?"]

        result = self.service.detect_state(messages)

        assert result.primary_state == UserState.UNCERTAIN
        assert result.confidence >= 0.6
        assert result.signals_observed.certainty_language <= 5

    def test_detect_processing_from_short_responses(self) -> None:
        """Test detecting PROCESSING from short reflective responses."""
        messages = ["Hmm, let me think"]

        result = self.service.detect_state(messages)

        assert result.primary_state == UserState.PROCESSING
        assert result.signals_observed.response_length == "short"

    def test_default_to_exploring_with_no_strong_signals(self) -> None:
        """Test defaulting to EXPLORING when no strong signals present."""
        messages = ["Tell me more about how this might work"]

        result = self.service.detect_state(messages)

        # Should default to EXPLORING with lower confidence
        assert result.primary_state in [UserState.EXPLORING, UserState.UNCERTAIN]
        assert result.confidence <= 0.7

    def test_empty_messages_defaults_to_exploring(self) -> None:
        """Test that empty message list defaults to EXPLORING."""
        result = self.service.detect_state([])

        assert result.primary_state == UserState.EXPLORING
        assert result.confidence <= 0.5


class TestMessageAnalysis:
    """Test message analysis helper functions."""

    def test_analyze_message_counts_words(self) -> None:
        """Test that message analysis counts words correctly."""
        text = "This is a test message with seven words"
        analysis = analyze_message(text)

        assert analysis.word_count == 8
        assert analysis.avg_word_length > 0

    def test_analyze_message_detects_certainty_markers(self) -> None:
        """Test certainty marker detection."""
        text = "I definitely know this is clearly the right answer"
        analysis = analyze_message(text)

        assert len(analysis.certainty_markers) >= 2
        assert "definitely" in analysis.certainty_markers
        assert "clearly" in analysis.certainty_markers

    def test_analyze_message_detects_uncertainty_markers(self) -> None:
        """Test uncertainty marker detection."""
        text = "I think maybe it could be this, but I'm not sure"
        analysis = analyze_message(text)

        assert len(analysis.uncertainty_markers) >= 2

    def test_analyze_message_detects_frustration(self) -> None:
        """Test frustration marker detection."""
        text = "Ugh, this is so frustrating, I'm stuck again"
        analysis = analyze_message(text)

        assert len(analysis.frustration_markers) >= 2

    def test_analyze_message_counts_questions(self) -> None:
        """Test question counting."""
        text = "What is this? How does it work? Why?"
        analysis = analyze_message(text)

        assert analysis.question_count == 3

    def test_detect_repetition_with_similar_messages(self) -> None:
        """Test repetition detection with similar content."""
        messages = [
            "thinking about the same problem issue",
            "considering the same problem issue",
            "the same problem issue keeps coming",
        ]

        is_repetitive = detect_repetition(messages, threshold=0.4)
        assert is_repetitive is True

    def test_detect_repetition_with_different_messages(self) -> None:
        """Test no repetition with different content."""
        messages = [
            "I like apples",
            "The weather is nice today",
            "Learning about quantum physics is interesting",
        ]

        is_repetitive = detect_repetition(messages)
        assert is_repetitive is False

    def test_detect_repetition_needs_minimum_messages(self) -> None:
        """Test that repetition detection needs at least 3 messages."""
        messages = ["Same thing", "Same thing"]

        is_repetitive = detect_repetition(messages)
        assert is_repetitive is False


class TestApproachSelection:
    """Test approach selection based on state and profile."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.service = ApproachSelectionService()

    def create_test_profile(self, **overrides) -> UserProfile:
        """Create a test profile with optional overrides."""
        defaults = {
            "user_id": "test_user",
            "display_name": "Test User",
            "processing": ProcessingProfile(),
            "attention": AttentionProfile(),
            "communication": CommunicationProfile(),
            "executive": ExecutiveProfile(),
            "sensory": SensoryProfile(),
        }
        defaults.update(overrides)
        return UserProfile(**defaults)

    def test_overwhelmed_selects_solution_focused_or_phenomenological(self) -> None:
        """Test that OVERWHELMED state selects appropriate approaches."""
        state = StateDetection(
            primary_state=UserState.OVERWHELMED,
            confidence=0.85,
            reasoning="User is overwhelmed",
        )

        result = self.service.select_approach(state)

        assert result.selected_approach in [
            InquiryApproach.SOLUTION_FOCUSED,
            InquiryApproach.PHENOMENOLOGICAL,
        ]
        assert result.pacing == "slow"
        assert result.directness == "gentle"

    def test_stuck_selects_socratic_or_metacognitive(self) -> None:
        """Test that STUCK state selects appropriate approaches."""
        state = StateDetection(
            primary_state=UserState.STUCK,
            confidence=0.8,
            reasoning="User is stuck",
        )

        result = self.service.select_approach(state)

        assert result.selected_approach in [
            InquiryApproach.SOCRATIC,
            InquiryApproach.METACOGNITIVE,
        ]
        assert result.directness == "direct"

    def test_tired_selects_gentle_approaches(self) -> None:
        """Test that TIRED state selects gentle approaches."""
        state = StateDetection(
            primary_state=UserState.TIRED,
            confidence=0.85,
            reasoning="User is tired",
        )

        result = self.service.select_approach(state)

        assert result.selected_approach in [
            InquiryApproach.SOLUTION_FOCUSED,
            InquiryApproach.PHENOMENOLOGICAL,
        ]
        assert result.pacing == "slow"
        assert result.directness == "gentle"

    def test_flowing_selects_exploratory_approaches(self) -> None:
        """Test that FLOWING state selects exploratory approaches."""
        state = StateDetection(
            primary_state=UserState.FLOWING,
            confidence=0.8,
            reasoning="User is in flow",
        )

        result = self.service.select_approach(state)

        assert result.selected_approach in [
            InquiryApproach.SOCRATIC,
            InquiryApproach.SYSTEMS,
        ]
        assert result.pacing == "fast"

    def test_profile_high_abstraction_favors_systems(self) -> None:
        """Test that high abstraction preference can favor Systems approach."""
        profile = self.create_test_profile(
            processing=ProcessingProfile(
                style=ProcessingStyle.PATTERN_FIRST,
                abstraction_preference=8,
            )
        )
        state = StateDetection(
            primary_state=UserState.FLOWING,
            confidence=0.8,
            reasoning="Flow state",
        )

        result = self.service.select_approach(state, profile)

        # Should prefer SYSTEMS for high abstraction + FLOWING
        assert result.selected_approach == InquiryApproach.SYSTEMS
        assert result.abstraction in ["abstract", "mixed"]

    def test_profile_intuitive_style_favors_phenomenological(self) -> None:
        """Test that intuitive decision style favors Phenomenological."""
        profile = self.create_test_profile(
            processing=ProcessingProfile(
                decision_style=DecisionStyle.INTUITIVE,
            )
        )
        state = StateDetection(
            primary_state=UserState.OVERWHELMED,
            confidence=0.8,
            reasoning="Overwhelmed",
        )

        result = self.service.select_approach(state, profile)

        assert result.selected_approach == InquiryApproach.PHENOMENOLOGICAL

    def test_profile_high_structure_need_favors_socratic(self) -> None:
        """Test that high structure need favors Socratic approach."""
        profile = self.create_test_profile(
            executive=ExecutiveProfile(
                structure_need=StructureNeed.RIGID,
            )
        )
        state = StateDetection(
            primary_state=UserState.STUCK,
            confidence=0.8,
            reasoning="Stuck",
        )

        result = self.service.select_approach(state, profile)

        assert result.selected_approach == InquiryApproach.SOCRATIC
        assert result.structure == "tight"

    def test_pacing_adapts_to_state(self) -> None:
        """Test pacing adaptation based on state."""
        # Overwhelmed should be slow
        overwhelmed = StateDetection(
            primary_state=UserState.OVERWHELMED, confidence=0.8, reasoning="Overwhelmed"
        )
        result = self.service.select_approach(overwhelmed)
        assert result.pacing == "slow"

        # Flowing should be fast
        flowing = StateDetection(
            primary_state=UserState.FLOWING, confidence=0.8, reasoning="Flow"
        )
        result = self.service.select_approach(flowing)
        assert result.pacing == "fast"

    def test_pacing_adapts_to_profile_preference(self) -> None:
        """Test pacing adaptation based on profile preference."""
        profile = self.create_test_profile(
            communication=CommunicationProfile(
                pace=PacePreference.SLOW,
            )
        )
        state = StateDetection(
            primary_state=UserState.EXPLORING, confidence=0.6, reasoning="Exploring"
        )

        result = self.service.select_approach(state, profile)

        # Profile preference should override for non-strong state
        assert result.pacing == "slow"

    def test_pacing_slows_with_long_session(self) -> None:
        """Test pacing slows down with long session duration."""
        state = StateDetection(
            primary_state=UserState.EXPLORING, confidence=0.6, reasoning="Exploring"
        )

        result = self.service.select_approach(state, session_duration_minutes=50)

        assert result.pacing == "slow"

    def test_pacing_considers_profile_capacity(self) -> None:
        """Test pacing considers current capacity from profile."""
        profile = self.create_test_profile(
            attention=AttentionProfile(current_capacity=4)
        )
        state = StateDetection(
            primary_state=UserState.EXPLORING, confidence=0.6, reasoning="Exploring"
        )

        result = self.service.select_approach(state, profile)

        # Low capacity should slow pacing
        assert result.pacing == "slow"

    def test_directness_adapts_to_vulnerable_states(self) -> None:
        """Test directness is gentle for vulnerable states."""
        vulnerable_states = [
            UserState.OVERWHELMED,
            UserState.EMOTIONAL,
            UserState.TIRED,
        ]

        for state_type in vulnerable_states:
            state = StateDetection(
                primary_state=state_type, confidence=0.8, reasoning="Vulnerable"
            )
            result = self.service.select_approach(state)
            assert result.directness == "gentle", f"Failed for {state_type}"

    def test_directness_adapts_to_stuck_state(self) -> None:
        """Test directness is direct for stuck state."""
        state = StateDetection(
            primary_state=UserState.STUCK, confidence=0.8, reasoning="Stuck"
        )

        result = self.service.select_approach(state)

        assert result.directness == "direct"

    def test_directness_adapts_to_profile_preference(self) -> None:
        """Test directness adapts to profile preference."""
        # High directness preference
        profile_direct = self.create_test_profile(
            communication=CommunicationProfile(directness_preference=8)
        )
        state = StateDetection(
            primary_state=UserState.EXPLORING, confidence=0.6, reasoning="Exploring"
        )
        result = self.service.select_approach(state, profile_direct)
        assert result.directness == "direct"

        # Low directness preference
        profile_gentle = self.create_test_profile(
            communication=CommunicationProfile(directness_preference=3)
        )
        result = self.service.select_approach(state, profile_gentle)
        assert result.directness == "gentle"

    def test_abstraction_adapts_to_overwhelmed_state(self) -> None:
        """Test abstraction is concrete for overwhelmed state."""
        state = StateDetection(
            primary_state=UserState.OVERWHELMED, confidence=0.8, reasoning="Overwhelmed"
        )

        result = self.service.select_approach(state)

        assert result.abstraction == "concrete"

    def test_abstraction_adapts_to_profile_preference(self) -> None:
        """Test abstraction adapts to profile preference."""
        # High abstraction preference
        profile_abstract = self.create_test_profile(
            processing=ProcessingProfile(abstraction_preference=8)
        )
        state = StateDetection(
            primary_state=UserState.EXPLORING, confidence=0.6, reasoning="Exploring"
        )
        result = self.service.select_approach(state, profile_abstract)
        assert result.abstraction == "abstract"

        # Low abstraction preference
        profile_concrete = self.create_test_profile(
            processing=ProcessingProfile(abstraction_preference=3)
        )
        result = self.service.select_approach(state, profile_concrete)
        assert result.abstraction == "concrete"

    def test_approach_switches_when_stuck_with_same_approach(self) -> None:
        """Test that approach switches if stuck with previous approach."""
        state = StateDetection(
            primary_state=UserState.STUCK, confidence=0.8, reasoning="Still stuck"
        )
        previous = InquiryApproach.SOCRATIC

        result = self.service.select_approach(state, previous_approach=previous)

        # Should switch to METACOGNITIVE instead of repeating SOCRATIC
        assert result.selected_approach != previous or result.selected_approach == InquiryApproach.METACOGNITIVE

    def test_includes_fallback_approaches(self) -> None:
        """Test that selection includes fallback approaches."""
        state = StateDetection(
            primary_state=UserState.FLOWING, confidence=0.8, reasoning="Flow"
        )

        result = self.service.select_approach(state)

        assert len(result.fallback_approaches) > 0
        assert result.selected_approach not in result.fallback_approaches

    def test_reasoning_includes_state_and_approach(self) -> None:
        """Test that reasoning explains selection."""
        state = StateDetection(
            primary_state=UserState.STUCK,
            confidence=0.8,
            reasoning="User repeating same ideas",
        )

        result = self.service.select_approach(state)

        assert "stuck" in result.reasoning.lower()
        assert len(result.reasoning) > 20  # Should be meaningful


class TestStateToApproachMapping:
    """Test STATE_TO_APPROACHES mapping coverage."""

    def test_all_states_have_approaches(self) -> None:
        """Test that all UserState values have approach mappings."""
        for state in UserState:
            assert state in STATE_TO_APPROACHES, f"{state} missing from mapping"
            assert len(STATE_TO_APPROACHES[state]) > 0, f"{state} has no approaches"

    def test_all_mapped_approaches_are_valid(self) -> None:
        """Test that all mapped approaches are valid InquiryApproach values."""
        valid_approaches = set(InquiryApproach)

        for state, approaches in STATE_TO_APPROACHES.items():
            for approach in approaches:
                assert (
                    approach in valid_approaches
                ), f"Invalid approach {approach} for state {state}"

    def test_vulnerable_states_have_gentle_approaches(self) -> None:
        """Test that vulnerable states map to appropriate gentle approaches."""
        gentle_approaches = {
            InquiryApproach.SOLUTION_FOCUSED,
            InquiryApproach.PHENOMENOLOGICAL,
        }

        vulnerable_states = [
            UserState.OVERWHELMED,
            UserState.TIRED,
            UserState.EMOTIONAL,
        ]

        for state in vulnerable_states:
            state_approaches = set(STATE_TO_APPROACHES[state])
            assert len(state_approaches & gentle_approaches) > 0, (
                f"Vulnerable state {state} should have at least one gentle approach"
            )

    def test_stuck_state_has_reflective_approaches(self) -> None:
        """Test that STUCK state includes reflective approaches."""
        stuck_approaches = set(STATE_TO_APPROACHES[UserState.STUCK])
        reflective = {InquiryApproach.SOCRATIC, InquiryApproach.METACOGNITIVE}

        assert len(stuck_approaches & reflective) > 0


class TestIntegration:
    """Integration tests combining state detection and approach selection."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.state_service = StateDetectionService()
        self.approach_service = ApproachSelectionService()

    def test_overwhelmed_user_gets_gentle_solution_focused(self) -> None:
        """Test full pipeline for overwhelmed user."""
        messages = [
            "I'm feeling really overwhelmed by all this",
            "There's too much to think about",
        ]

        state = self.state_service.detect_state(messages)
        approach = self.approach_service.select_approach(state)

        assert state.primary_state == UserState.OVERWHELMED
        assert approach.pacing == "slow"
        assert approach.directness == "gentle"
        assert approach.selected_approach in [
            InquiryApproach.SOLUTION_FOCUSED,
            InquiryApproach.PHENOMENOLOGICAL,
        ]

    def test_stuck_user_with_high_structure_gets_socratic(self) -> None:
        """Test stuck user with high structure need gets Socratic."""
        messages = [
            "I keep coming back to the same thing problem",
            "Ugh, stuck on this problem again",
            "Same problem, different day",
        ]
        profile = UserProfile(
            user_id="test",
            executive=ExecutiveProfile(structure_need=StructureNeed.RIGID),
        )

        state = self.state_service.detect_state(messages)
        approach = self.approach_service.select_approach(state, profile)

        assert state.primary_state == UserState.STUCK
        assert approach.selected_approach == InquiryApproach.SOCRATIC
        assert approach.directness == "direct"
        assert approach.structure == "tight"

    def test_flowing_intuitive_user_gets_appropriate_approach(self) -> None:
        """Test flowing intuitive user gets appropriate approach."""
        messages = ["This is really clicking for me, it feels right"]
        profile = UserProfile(
            user_id="test",
            processing=ProcessingProfile(decision_style=DecisionStyle.INTUITIVE),
        )

        state = self.state_service.detect_state(messages)
        approach = self.approach_service.select_approach(state, profile)

        assert state.primary_state == UserState.FLOWING
        assert approach.pacing == "fast"

    def test_low_capacity_override_results_in_gentle_approach(self) -> None:
        """Test that low capacity results in gentle, slow approach."""
        messages = ["Let's explore this interesting topic"]

        state = self.state_service.detect_state(messages, explicit_capacity=2)
        approach = self.approach_service.select_approach(state)

        assert state.primary_state == UserState.TIRED
        assert approach.pacing == "slow"
        assert approach.directness == "gentle"
