"""Question Engine schemas for state detection and approach selection."""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class UserState(str, Enum):
    """Detected user cognitive/emotional state during session."""

    FLOWING = "flowing"           # Engaged, productive, good energy
    STUCK = "stuck"               # Looping, not making progress
    OVERWHELMED = "overwhelmed"   # Too much, need grounding
    EXPLORING = "exploring"       # Curious, branching out
    PROCESSING = "processing"     # Need time to digest
    UNCERTAIN = "uncertain"       # Unclear on direction/purpose
    EMOTIONAL = "emotional"       # Strong feelings present
    TIRED = "tired"               # Low energy, need gentle approach


class InquiryApproach(str, Enum):
    """Question approach types from the resource library."""

    # MVP approaches (5 core)
    SOCRATIC = "socratic"                   # Clarifying assumptions, testing logic
    SOLUTION_FOCUSED = "solution_focused"   # Forward motion, small steps
    PHENOMENOLOGICAL = "phenomenological"   # Body-based, felt sense, focusing
    SYSTEMS = "systems"                     # Connections, patterns, emergence
    METACOGNITIVE = "metacognitive"         # Reflection on thinking process

    # Extended approaches (for future)
    CBT = "cbt"                             # Cognitive restructuring, testing beliefs
    NARRATIVE = "narrative"                 # Story, meaning-making, identity
    STRATEGIC = "strategic"                 # Planning, decisions, trade-offs
    SOMATIC = "somatic"                     # Grounding, regulation, body awareness
    DESIGN = "design"                       # Reframing, prototyping, iteration


class QuestionClass(str, Enum):
    """Nine question classes from the IES Question Engine expansion.

    Each class has a distinct cognitive function and maps to specific
    thinking modes in the AST (Assisted Structured Thinking) system.
    """

    # Structure surfacing
    SCHEMA_PROBE = "schema_probe"           # Surfaces hidden structure (lists, buckets, taxonomies)
    BOUNDARY = "boundary"                   # Clarifies edges/limits to avoid scope creep
    DIMENSIONAL = "dimensional"             # Introduces spectra/coordinates for precise positioning

    # Mechanism exploration
    CAUSAL = "causal"                       # Pushes for mechanisms, prerequisites, sequences
    COUNTERFACTUAL = "counterfactual"       # "What if" deviations to expose assumptions

    # Grounding and perspective
    ANCHOR = "anchor"                       # Grounds abstractions in concrete instances
    PERSPECTIVE_SHIFT = "perspective_shift" # Forces viewpoint changes (roles, time, system level)

    # Meta-level
    META_COGNITIVE = "meta_cognitive"       # Checks thinking patterns (confidence, stuckness, energy)
    REFLECTIVE_SYNTHESIS = "reflective_synthesis"  # Integration statements that tie threads together


# Question class descriptions for prompts
QUESTION_CLASS_DESCRIPTIONS: dict[QuestionClass, str] = {
    QuestionClass.SCHEMA_PROBE: """Schema-Probe questions surface hidden structure by asking for
lists, buckets, or taxonomies. Examples: 'What are the main categories here?',
'Can you break this into components?', 'What's the underlying structure?'""",

    QuestionClass.BOUNDARY: """Boundary questions clarify edges and limits to avoid vague scope creep.
Examples: 'What's NOT included in this?', 'Where does this end?',
'What distinguishes this from adjacent concepts?'""",

    QuestionClass.DIMENSIONAL: """Dimensional questions introduce spectra or coordinates to position
ideas precisely. Examples: 'On a spectrum from X to Y, where is this?',
'What dimensions matter here?', 'How would you rate this on multiple axes?'""",

    QuestionClass.CAUSAL: """Causal questions push for mechanisms, prerequisites, or sequences.
Examples: 'What causes this?', 'What has to happen first?',
'What's the chain of events?', 'How does A lead to B?'""",

    QuestionClass.COUNTERFACTUAL: """Counterfactual questions invite "what if" deviations to expose
assumptions. Examples: 'What if the opposite were true?',
'What would change if X didn't exist?', 'Imagine this failed - why?'""",

    QuestionClass.ANCHOR: """Anchor questions ground abstractions in concrete instances or lived
experiences. Examples: 'Can you give me a specific example?',
'When did you actually experience this?', 'What does this look like in practice?'""",

    QuestionClass.PERSPECTIVE_SHIFT: """Perspective-Shift questions force viewpoint changes across
roles, time horizons, or system levels. Examples: 'How would X see this?',
'What would this look like in 5 years?', 'Zoom out - what's the bigger picture?'""",

    QuestionClass.META_COGNITIVE: """Meta-Cognitive questions check thinking patterns directly.
Examples: 'How confident are you in this?', 'Where do you feel stuck?',
'What's your energy level right now?', 'What patterns do you notice in your thinking?'""",

    QuestionClass.REFLECTIVE_SYNTHESIS: """Reflective-Synthesis questions ask for integration
statements that tie threads together. Examples: 'What's the main insight here?',
'How do these pieces connect?', 'What's the essence of what we've discovered?'""",
}


# Mapping question classes to thinking modes
CLASS_TO_MODES: dict[QuestionClass, list[str]] = {
    QuestionClass.SCHEMA_PROBE: ["discovery", "learning"],
    QuestionClass.BOUNDARY: ["discovery", "articulating"],
    QuestionClass.DIMENSIONAL: ["discovery", "planning"],
    QuestionClass.CAUSAL: ["dialogue", "learning"],
    QuestionClass.COUNTERFACTUAL: ["dialogue", "ideating"],
    QuestionClass.ANCHOR: ["dialogue", "reflecting"],
    QuestionClass.PERSPECTIVE_SHIFT: ["flow", "ideating"],
    QuestionClass.META_COGNITIVE: ["ast", "reflecting"],
    QuestionClass.REFLECTIVE_SYNTHESIS: ["ast", "articulating"],
}


# Mapping inquiry approaches to question classes (which classes they typically generate)
APPROACH_TO_CLASSES: dict[InquiryApproach, list[QuestionClass]] = {
    InquiryApproach.SOCRATIC: [QuestionClass.SCHEMA_PROBE, QuestionClass.BOUNDARY, QuestionClass.CAUSAL],
    InquiryApproach.SOLUTION_FOCUSED: [QuestionClass.ANCHOR, QuestionClass.DIMENSIONAL],
    InquiryApproach.PHENOMENOLOGICAL: [QuestionClass.ANCHOR, QuestionClass.META_COGNITIVE],
    InquiryApproach.SYSTEMS: [QuestionClass.CAUSAL, QuestionClass.PERSPECTIVE_SHIFT, QuestionClass.DIMENSIONAL],
    InquiryApproach.METACOGNITIVE: [QuestionClass.META_COGNITIVE, QuestionClass.REFLECTIVE_SYNTHESIS],
}


class StateSignal(BaseModel):
    """Signals used to detect user state."""

    # Response patterns
    response_length: Annotated[str, Field(description="short | medium | long")] | None = None
    response_speed: Annotated[str, Field(description="quick | normal | delayed")] | None = None
    certainty_language: Annotated[int, Field(ge=1, le=10, description="1=uncertain, 10=confident")] | None = None

    # Energy indicators
    energy_words: list[str] = Field(default_factory=list, description="Words indicating energy level")
    frustration_indicators: list[str] = Field(default_factory=list)
    engagement_indicators: list[str] = Field(default_factory=list)

    # Content patterns
    repetition_detected: bool = False  # Saying similar things
    tangent_frequency: Annotated[str, Field(description="low | medium | high")] | None = None
    abstraction_level: Annotated[str, Field(description="concrete | mixed | abstract")] | None = None

    # Explicit signals
    explicit_state: str | None = None  # User said "I'm tired" etc.
    capacity_reported: Annotated[int, Field(ge=1, le=10)] | None = None


class StateDetection(BaseModel):
    """Result of state detection analysis."""

    primary_state: UserState
    confidence: Annotated[float, Field(ge=0, le=1)]
    secondary_states: list[UserState] = Field(default_factory=list)
    signals_observed: StateSignal = Field(default_factory=StateSignal)
    reasoning: str | None = None  # Why this state was detected


class ApproachSelection(BaseModel):
    """Result of approach selection based on state and profile."""

    selected_approach: InquiryApproach
    confidence: Annotated[float, Field(ge=0, le=1)]
    reasoning: str

    # Profile adaptations
    pacing: Annotated[str, Field(description="fast | moderate | slow")]
    directness: Annotated[str, Field(description="direct | balanced | gentle")]
    abstraction: Annotated[str, Field(description="concrete | mixed | abstract")]
    structure: Annotated[str, Field(description="tight | moderate | loose")]

    # Alternatives if this doesn't land
    fallback_approaches: list[InquiryApproach] = Field(default_factory=list)


class QuestionTemplate(BaseModel):
    """A question template for a specific approach."""

    approach: InquiryApproach
    category: str  # e.g., "clarifying", "deepening", "challenging", "grounding"
    template: str  # The question pattern with {placeholders}
    when_to_use: str  # Description of appropriate context
    source: str | None = None  # Book/resource this came from

    # Profile adaptations
    directness_variants: dict[str, str] = Field(
        default_factory=dict,
        description="Alternative phrasings by directness level"
    )
    pace_considerations: str | None = None


class ClassifiedQuestion(BaseModel):
    """A question with its class tag for Mode Transition Engine tracking."""

    question: str
    question_class: QuestionClass
    approach: InquiryApproach


class QuestionBatch(BaseModel):
    """A batch of generated questions for a given state/approach."""

    approach: InquiryApproach
    state: UserState
    questions: list[str]
    context: str  # What triggered this generation
    profile_adaptations_applied: list[str] = Field(default_factory=list)

    # New: classified questions with class tags
    classified_questions: list[ClassifiedQuestion] = Field(default_factory=list)


# Selection rules mapping
STATE_TO_APPROACHES: dict[UserState, list[InquiryApproach]] = {
    UserState.FLOWING: [InquiryApproach.SOCRATIC, InquiryApproach.SYSTEMS],
    UserState.STUCK: [InquiryApproach.SOCRATIC, InquiryApproach.METACOGNITIVE],
    UserState.OVERWHELMED: [InquiryApproach.SOLUTION_FOCUSED, InquiryApproach.PHENOMENOLOGICAL],
    UserState.EXPLORING: [InquiryApproach.SYSTEMS, InquiryApproach.SOCRATIC],
    UserState.PROCESSING: [InquiryApproach.PHENOMENOLOGICAL, InquiryApproach.METACOGNITIVE],
    UserState.UNCERTAIN: [InquiryApproach.METACOGNITIVE, InquiryApproach.SOLUTION_FOCUSED],
    UserState.EMOTIONAL: [InquiryApproach.PHENOMENOLOGICAL, InquiryApproach.SOLUTION_FOCUSED],
    UserState.TIRED: [InquiryApproach.SOLUTION_FOCUSED, InquiryApproach.PHENOMENOLOGICAL],
}


# Approach descriptions for system prompts
APPROACH_DESCRIPTIONS: dict[InquiryApproach, str] = {
    InquiryApproach.SOCRATIC: """Socratic inquiry uses clarifying questions to surface assumptions,
test logical consistency, and deepen understanding. Ask 'what do you mean by...',
'what would have to be true for...', 'how does X relate to Y'.""",

    InquiryApproach.SOLUTION_FOCUSED: """Solution-focused approach emphasizes forward motion
and small, concrete steps. Ask about exceptions (when things worked), scaling questions
(1-10 where are you?), and 'what's one small thing that would make a difference'.""",

    InquiryApproach.PHENOMENOLOGICAL: """Phenomenological/Focusing approach attends to
felt sense and body-based knowing. Ask 'what do you notice in your body when you say that?',
'can you stay with that feeling?', 'what word or image fits that sensation?'.""",

    InquiryApproach.SYSTEMS: """Systems thinking looks at connections, patterns, and emergence.
Ask about relationships between parts, feedback loops, unintended consequences,
and how changes in one area affect others.""",

    InquiryApproach.METACOGNITIVE: """Metacognitive inquiry reflects on the thinking process itself.
Ask 'how are you approaching this problem?', 'what assumptions are you making?',
'what would you tell someone else in this situation?'.""",
}
