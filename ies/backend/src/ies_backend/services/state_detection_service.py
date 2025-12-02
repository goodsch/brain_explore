"""State detection service for analyzing user cognitive/emotional state during sessions."""

import re
from dataclasses import dataclass

from ..schemas.profile import UserProfile
from ..schemas.question_engine import (
    StateDetection,
    StateSignal,
    UserState,
)


@dataclass
class MessageAnalysis:
    """Analysis of a single message."""

    word_count: int
    avg_word_length: float
    question_count: int
    certainty_markers: list[str]
    uncertainty_markers: list[str]
    frustration_markers: list[str]
    energy_markers: list[str]
    emotional_markers: list[str]


# Marker word lists for signal detection
CERTAINTY_MARKERS = [
    "definitely", "certainly", "absolutely", "clearly", "obviously",
    "I know", "I'm sure", "without doubt", "for certain"
]

UNCERTAINTY_MARKERS = [
    "maybe", "perhaps", "I think", "I guess", "not sure", "might",
    "I don't know", "possibly", "could be", "wondering", "unclear"
]

FRUSTRATION_MARKERS = [
    "ugh", "argh", "frustrated", "annoying", "stuck", "can't",
    "doesn't make sense", "going in circles", "again", "still"
]

LOW_ENERGY_MARKERS = [
    "tired", "exhausted", "drained", "low energy", "sleepy",
    "brain fog", "can't focus", "overwhelmed", "too much"
]

HIGH_ENERGY_MARKERS = [
    "excited", "energized", "curious", "interesting", "ooh",
    "that's it", "yes", "exactly", "clicking", "flow"
]

EMOTIONAL_MARKERS = [
    "feel", "feeling", "felt", "scared", "anxious", "worried",
    "sad", "happy", "angry", "hurt", "afraid", "hopeful", "grief"
]


def analyze_message(text: str) -> MessageAnalysis:
    """Analyze a single message for state signals."""
    words = text.split()
    word_count = len(words)
    avg_word_length = sum(len(w) for w in words) / max(word_count, 1)

    text_lower = text.lower()

    return MessageAnalysis(
        word_count=word_count,
        avg_word_length=avg_word_length,
        question_count=text.count("?"),
        certainty_markers=[m for m in CERTAINTY_MARKERS if m in text_lower],
        uncertainty_markers=[m for m in UNCERTAINTY_MARKERS if m in text_lower],
        frustration_markers=[m for m in FRUSTRATION_MARKERS if m in text_lower],
        energy_markers=[m for m in HIGH_ENERGY_MARKERS if m in text_lower]
        + [m for m in LOW_ENERGY_MARKERS if m in text_lower],
        emotional_markers=[m for m in EMOTIONAL_MARKERS if m in text_lower],
    )


def detect_repetition(messages: list[str], threshold: float = 0.5) -> bool:
    """Detect if user is repeating similar content (indicating stuck state)."""
    if len(messages) < 3:
        return False

    # Simple approach: check word overlap between recent messages
    recent = messages[-3:]
    word_sets = [set(m.lower().split()) for m in recent]

    # Calculate Jaccard similarity between consecutive messages
    similarities = []
    for i in range(len(word_sets) - 1):
        if word_sets[i] and word_sets[i + 1]:
            intersection = len(word_sets[i] & word_sets[i + 1])
            union = len(word_sets[i] | word_sets[i + 1])
            similarities.append(intersection / union if union > 0 else 0)

    return any(s > threshold for s in similarities)


def classify_response_length(word_count: int) -> str:
    """Classify response length."""
    if word_count < 20:
        return "short"
    elif word_count < 80:
        return "medium"
    else:
        return "long"


def classify_abstraction(text: str) -> str:
    """Classify abstraction level of response."""
    text_lower = text.lower()

    # Concrete indicators: specific examples, numbers, actions
    concrete_patterns = [
        r"\d+",  # Numbers
        r"for example",
        r"specifically",
        r"yesterday|today|tomorrow",
        r"when I|I did|I said",
    ]

    # Abstract indicators: concepts, generalizations
    abstract_patterns = [
        r"in general",
        r"the concept of",
        r"theoretically",
        r"fundamentally",
        r"essentially",
        r"the nature of",
    ]

    concrete_count = sum(1 for p in concrete_patterns if re.search(p, text_lower))
    abstract_count = sum(1 for p in abstract_patterns if re.search(p, text_lower))

    if concrete_count > abstract_count + 1:
        return "concrete"
    elif abstract_count > concrete_count + 1:
        return "abstract"
    else:
        return "mixed"


class StateDetectionService:
    """Service for detecting user state from conversation context."""

    def detect_state(
        self,
        recent_messages: list[str],
        profile: UserProfile | None = None,
        explicit_capacity: int | None = None,
    ) -> StateDetection:
        """
        Detect user state from recent conversation messages.

        Args:
            recent_messages: Last 3-5 user messages
            profile: User's cognitive profile for context
            explicit_capacity: If user reported capacity (1-10)

        Returns:
            StateDetection with primary state, confidence, and signals
        """
        if not recent_messages:
            return StateDetection(
                primary_state=UserState.EXPLORING,
                confidence=0.3,
                reasoning="No messages to analyze, defaulting to exploring",
            )

        # Analyze most recent message primarily
        latest = recent_messages[-1]
        analysis = analyze_message(latest)

        # Build signal object
        signals = StateSignal(
            response_length=classify_response_length(analysis.word_count),
            certainty_language=self._score_certainty(analysis),
            energy_words=analysis.energy_markers,
            frustration_indicators=analysis.frustration_markers,
            engagement_indicators=analysis.certainty_markers,
            repetition_detected=detect_repetition(recent_messages),
            abstraction_level=classify_abstraction(latest),
            capacity_reported=explicit_capacity,
        )

        # Determine primary state based on signals
        state, confidence, reasoning = self._classify_state(signals, analysis)

        # Check for explicit capacity override
        if explicit_capacity is not None:
            if explicit_capacity <= 3:
                state = UserState.TIRED
                confidence = 0.9
                reasoning = f"User reported low capacity ({explicit_capacity}/10)"
            elif explicit_capacity <= 5:
                # Low-moderate capacity - be gentler
                if state not in [UserState.TIRED, UserState.OVERWHELMED]:
                    confidence *= 0.8  # Reduce confidence in other states

        return StateDetection(
            primary_state=state,
            confidence=confidence,
            signals_observed=signals,
            reasoning=reasoning,
        )

    def _score_certainty(self, analysis: MessageAnalysis) -> int:
        """Score certainty level 1-10 based on language markers."""
        certainty_count = len(analysis.certainty_markers)
        uncertainty_count = len(analysis.uncertainty_markers)

        # Base score of 5
        score = 5 + (certainty_count * 1.5) - (uncertainty_count * 1.5)
        return max(1, min(10, int(score)))

    def _classify_state(
        self,
        signals: StateSignal,
        analysis: MessageAnalysis,
    ) -> tuple[UserState, float, str]:
        """Classify state based on accumulated signals."""
        # Priority-ordered checks

        # Check for overwhelmed (highest priority - safety)
        if any("overwhelm" in w or "too much" in w for w in signals.energy_words):
            return (
                UserState.OVERWHELMED,
                0.85,
                "Explicit overwhelm language detected",
            )

        # Check for tired
        if any(w in LOW_ENERGY_MARKERS for w in signals.energy_words):
            return (
                UserState.TIRED,
                0.8,
                f"Low energy markers detected: {signals.energy_words}",
            )

        # Check for stuck (repetition + frustration)
        if signals.repetition_detected:
            if signals.frustration_indicators:
                return (
                    UserState.STUCK,
                    0.85,
                    "Repetition with frustration indicates stuck state",
                )
            return (
                UserState.STUCK,
                0.7,
                "Repetition detected without progress",
            )

        # Check for emotional
        if analysis.emotional_markers:
            return (
                UserState.EMOTIONAL,
                0.75,
                f"Emotional language present: {analysis.emotional_markers}",
            )

        # Check for uncertainty
        if (signals.certainty_language or 5) < 4 and analysis.question_count > 1:
            return (
                UserState.UNCERTAIN,
                0.7,
                "Multiple questions with uncertainty language",
            )

        # Check for processing (short responses, asking for time)
        if signals.response_length == "short" and analysis.question_count == 0:
            return (
                UserState.PROCESSING,
                0.6,
                "Short responses suggest processing/reflecting",
            )

        # Check for flowing (high engagement signals)
        if any(w in HIGH_ENERGY_MARKERS for w in signals.energy_words):
            return (
                UserState.FLOWING,
                0.8,
                f"High engagement markers: {signals.energy_words}",
            )

        if signals.response_length == "long" and (signals.certainty_language or 5) >= 6:
            return (
                UserState.FLOWING,
                0.7,
                "Detailed, confident responses suggest flow",
            )

        # Default to exploring
        return (
            UserState.EXPLORING,
            0.5,
            "No strong signals - defaulting to exploratory state",
        )


# Singleton instance
state_detection_service = StateDetectionService()
