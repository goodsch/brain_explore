"""Profile schemas - User cognitive profile for personalized exploration."""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class ProcessingStyle(str, Enum):
    """How user processes information."""

    DETAIL_FIRST = "detail_first"
    PATTERN_FIRST = "pattern_first"
    BALANCED = "balanced"


class DecisionStyle(str, Enum):
    """How user makes decisions."""

    DELIBERATIVE = "deliberative"
    INTUITIVE = "intuitive"
    MIXED = "mixed"


class PacePreference(str, Enum):
    """Conversation pace preference."""

    FAST = "fast"
    SLOW = "slow"
    ADAPTIVE = "adaptive"


class StructureNeed(str, Enum):
    """How much structure user needs."""

    RIGID = "rigid"
    FLEXIBLE = "flexible"
    MODERATE = "moderate"


# Profile dimension models


class ProcessingProfile(BaseModel):
    """Dimension 1: How user processes information."""

    style: ProcessingStyle = ProcessingStyle.BALANCED
    decision_style: DecisionStyle = DecisionStyle.MIXED
    habituation_speed: Annotated[
        int, Field(ge=1, le=10, description="How quickly 'new' becomes 'familiar' (1=slow, 10=fast)")
    ] = 5
    abstraction_preference: Annotated[
        int, Field(ge=1, le=10, description="Concrete (1) vs theoretical (10)")
    ] = 5


class AttentionProfile(BaseModel):
    """Dimension 2: Attention and energy patterns."""

    hyperfocus_triggers: list[str] = Field(
        default_factory=list, description="Topics/contexts that unlock flow state"
    )
    distraction_vulnerabilities: list[str] = Field(
        default_factory=list, description="What tends to derail focus"
    )
    current_capacity: Annotated[
        int, Field(ge=1, le=10, description="Current energy level (session check-in)")
    ] = 5
    recovery_patterns: list[str] = Field(
        default_factory=list, description="What restores energy"
    )
    optimal_session_length: Annotated[
        int, Field(ge=5, le=120, description="Ideal session length in minutes")
    ] = 30


class CommunicationProfile(BaseModel):
    """Dimension 3: Communication preferences."""

    verbal_fluency: Annotated[
        int, Field(ge=1, le=10, description="Ease of verbal expression (1=difficult, 10=effortless)")
    ] = 5
    scripts_preference: Annotated[
        int, Field(ge=1, le=10, description="Prefers scripts (1) vs spontaneity (10)")
    ] = 5
    directness_preference: Annotated[
        int, Field(ge=1, le=10, description="Gentle (1) vs blunt (10)")
    ] = 5
    pace: PacePreference = PacePreference.ADAPTIVE
    wait_time_needed: Annotated[
        int, Field(ge=1, le=10, description="Processing time needed before responding (1=none, 10=lots)")
    ] = 5


class ExecutiveProfile(BaseModel):
    """Dimension 4: Executive functioning patterns."""

    task_initiation: Annotated[
        int, Field(ge=1, le=10, description="Ease of starting tasks (1=very hard, 10=easy)")
    ] = 5
    transition_cost: Annotated[
        int, Field(ge=1, le=10, description="Difficulty switching tasks (1=easy, 10=very hard)")
    ] = 5
    time_perception: Annotated[
        int, Field(ge=1, le=10, description="Time blindness (1=accurate, 10=very blind)")
    ] = 5
    structure_need: StructureNeed = StructureNeed.MODERATE
    working_memory: Annotated[
        int, Field(ge=1, le=10, description="Working memory capacity (1=low, 10=high)")
    ] = 5


class SensoryProfile(BaseModel):
    """Dimension 5: Sensory and environmental context."""

    environment_preference: Annotated[
        int, Field(ge=1, le=10, description="Quiet (1) vs stimulating (10) environment")
    ] = 5
    overwhelm_signals: list[str] = Field(
        default_factory=list, description="Signs that indicate overwhelm"
    )
    regulation_tools: list[str] = Field(
        default_factory=list, description="What helps regulate state"
    )


class MaskingProfile(BaseModel):
    """Dimension 6: Masking awareness (optional/advanced)."""

    traits_feel_unsafe: list[str] = Field(
        default_factory=list, description="Traits that feel unsafe to show"
    )
    high_cost_contexts: list[str] = Field(
        default_factory=list, description="Contexts with high masking energy cost"
    )
    authentic_contexts: list[str] = Field(
        default_factory=list, description="Contexts where masking is minimal"
    )


# Main profile model


class UserProfile(BaseModel):
    """Complete user cognitive profile."""

    user_id: str
    display_name: str | None = None

    # Profile dimensions
    processing: ProcessingProfile = Field(default_factory=ProcessingProfile)
    attention: AttentionProfile = Field(default_factory=AttentionProfile)
    communication: CommunicationProfile = Field(default_factory=CommunicationProfile)
    executive: ExecutiveProfile = Field(default_factory=ExecutiveProfile)
    sensory: SensoryProfile = Field(default_factory=SensoryProfile)
    masking: MaskingProfile | None = None  # Optional, only if user wants to explore

    # Metadata
    onboarding_complete: bool = False
    sessions_completed: int = 0
    last_updated: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "chris",
                "display_name": "Chris",
                "processing": {
                    "style": "pattern_first",
                    "decision_style": "intuitive",
                    "habituation_speed": 8,
                    "abstraction_preference": 7,
                },
                "attention": {
                    "hyperfocus_triggers": ["complex systems", "novel ideas"],
                    "distraction_vulnerabilities": ["notifications", "tangential thoughts"],
                    "current_capacity": 7,
                    "recovery_patterns": ["walking", "music"],
                    "optimal_session_length": 45,
                },
                "communication": {
                    "verbal_fluency": 7,
                    "scripts_preference": 3,
                    "directness_preference": 8,
                    "pace": "fast",
                    "wait_time_needed": 3,
                },
                "executive": {
                    "task_initiation": 4,
                    "transition_cost": 7,
                    "time_perception": 8,
                    "structure_need": "moderate",
                    "working_memory": 6,
                },
                "sensory": {
                    "environment_preference": 6,
                    "overwhelm_signals": ["short responses", "irritability"],
                    "regulation_tools": ["movement", "music"],
                },
                "onboarding_complete": True,
                "sessions_completed": 12,
            }
        }
    }


class ProfileUpdate(BaseModel):
    """Partial profile update."""

    display_name: str | None = None
    processing: ProcessingProfile | None = None
    attention: AttentionProfile | None = None
    communication: CommunicationProfile | None = None
    executive: ExecutiveProfile | None = None
    sensory: SensoryProfile | None = None
    masking: MaskingProfile | None = None


class CapacityCheckIn(BaseModel):
    """Session capacity check-in."""

    current_capacity: Annotated[int, Field(ge=1, le=10)]
    notes: str | None = None


class ProfileObservation(BaseModel):
    """Observation from session to update profile."""

    session_id: str
    session_length_minutes: int
    topics_explored: list[str]
    energy_signals: list[str] = Field(
        default_factory=list, description="Observed energy changes during session"
    )
    approach_effectiveness: dict[str, int] = Field(
        default_factory=dict, description="Which questioning approaches worked well (1-10)"
    )
    suggested_updates: dict[str, str] = Field(
        default_factory=dict, description="AI-suggested profile updates based on session"
    )
