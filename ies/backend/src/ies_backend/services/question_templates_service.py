"""Question Templates Service for the Intelligent Exploration System.

This service provides research-backed question templates from therapy and coaching literature,
organized by inquiry approach and adapted to user profile settings.
"""

from typing import Any

from ies_backend.schemas.question_engine import (
    InquiryApproach,
    QuestionBatch,
    QuestionTemplate,
    UserState,
)


class QuestionTemplatesService:
    """Service for managing and retrieving question templates."""

    def __init__(self) -> None:
        """Initialize the service with template library."""
        self._templates: list[QuestionTemplate] = self._build_template_library()

    def _build_template_library(self) -> list[QuestionTemplate]:
        """Build the complete template library from therapy/coaching literature."""
        return [
            # ============================================================
            # SOCRATIC INQUIRY
            # Source: Paul & Elder (2006) "The Thinker's Guide to The Art of Socratic Questioning"
            # ============================================================
            QuestionTemplate(
                approach=InquiryApproach.SOCRATIC,
                category="clarifying",
                template="What do you mean when you say '{concept}'?",
                when_to_use="When user uses an undefined or ambiguous term",
                source="Paul & Elder (2006) - The Art of Socratic Questioning",
                directness_variants={
                    "direct": "Define what you mean by '{concept}'.",
                    "balanced": "What do you mean when you say '{concept}'?",
                    "gentle": "I'm curious what '{concept}' means to you - could you say more?",
                },
                pace_considerations="Allow time for reflection; this question often reveals hidden complexity",
            ),
            QuestionTemplate(
                approach=InquiryApproach.SOCRATIC,
                category="clarifying",
                template="Can you give me an example of {concept}?",
                when_to_use="When abstract concept needs grounding in concrete experience",
                source="Paul & Elder (2006) - The Art of Socratic Questioning",
                directness_variants={
                    "direct": "Give me a specific example of {concept}.",
                    "balanced": "Can you give me an example of {concept}?",
                    "gentle": "What might be an example of {concept} in your experience?",
                },
                pace_considerations="Concrete examples slow down and deepen exploration",
            ),
            QuestionTemplate(
                approach=InquiryApproach.SOCRATIC,
                category="assumptions",
                template="What are you assuming when you say {statement}?",
                when_to_use="When user makes a claim that rests on hidden assumptions",
                source="Paul & Elder (2006) - The Art of Socratic Questioning",
                directness_variants={
                    "direct": "What assumption underlies {statement}?",
                    "balanced": "What are you assuming when you say {statement}?",
                    "gentle": "I notice {statement} - what might you be taking for granted there?",
                },
                pace_considerations="Uncovering assumptions can be destabilizing; proceed gently",
            ),
            QuestionTemplate(
                approach=InquiryApproach.SOCRATIC,
                category="reasoning",
                template="How does {concept_a} relate to {concept_b}?",
                when_to_use="When exploring relationships between ideas",
                source="Paul & Elder (2006) - The Art of Socratic Questioning",
                directness_variants={
                    "direct": "What's the connection between {concept_a} and {concept_b}?",
                    "balanced": "How does {concept_a} relate to {concept_b}?",
                    "gentle": "I'm wondering about the relationship between {concept_a} and {concept_b}...",
                },
                pace_considerations="Relationship questions invite systems thinking",
            ),
            QuestionTemplate(
                approach=InquiryApproach.SOCRATIC,
                category="implications",
                template="If {statement} is true, what else would have to be true?",
                when_to_use="When testing logical consistency and exploring consequences",
                source="Paul & Elder (2006) - The Art of Socratic Questioning",
                directness_variants={
                    "direct": "What follows logically from {statement}?",
                    "balanced": "If {statement} is true, what else would have to be true?",
                    "gentle": "What might follow from {statement}, I wonder?",
                },
                pace_considerations="Implication questions can reveal contradictions; allow processing time",
            ),
            QuestionTemplate(
                approach=InquiryApproach.SOCRATIC,
                category="evidence",
                template="What leads you to believe {claim}?",
                when_to_use="When user makes a claim that needs grounding in evidence",
                source="Paul & Elder (2006) - The Art of Socratic Questioning",
                directness_variants={
                    "direct": "What evidence supports {claim}?",
                    "balanced": "What leads you to believe {claim}?",
                    "gentle": "I'm curious what makes {claim} seem true to you?",
                },
                pace_considerations="Evidence questions ground abstract thinking",
            ),

            # ============================================================
            # SOLUTION-FOCUSED BRIEF THERAPY
            # Source: De Jong & Berg (2013) "Interviewing for Solutions"
            # ============================================================
            QuestionTemplate(
                approach=InquiryApproach.SOLUTION_FOCUSED,
                category="opening",
                template="What would be different if this problem was solved?",
                when_to_use="Early in session to orient toward desired outcome",
                source="De Jong & Berg (2013) - Interviewing for Solutions",
                directness_variants={
                    "direct": "Describe what life looks like when this is solved.",
                    "balanced": "What would be different if this problem was solved?",
                    "gentle": "Imagine this gets better - what might change?",
                },
                pace_considerations="Future-oriented questions create hope and direction",
            ),
            QuestionTemplate(
                approach=InquiryApproach.SOLUTION_FOCUSED,
                category="exceptions",
                template="When is this problem less severe or absent?",
                when_to_use="When user is stuck in problem-saturated narrative",
                source="De Jong & Berg (2013) - Interviewing for Solutions",
                directness_variants={
                    "direct": "When doesn't this happen?",
                    "balanced": "When is this problem less severe or absent?",
                    "gentle": "Are there times when things feel a little easier?",
                },
                pace_considerations="Exception questions reveal existing resources",
            ),
            QuestionTemplate(
                approach=InquiryApproach.SOLUTION_FOCUSED,
                category="scaling",
                template="On a scale of 1-10, where 10 is {goal} fully achieved and 1 is the opposite, where are you now?",
                when_to_use="To establish baseline and track progress",
                source="De Jong & Berg (2013) - Interviewing for Solutions",
                directness_variants={
                    "direct": "Rate where you are: 1-10, where 10 is {goal} achieved.",
                    "balanced": "On a scale of 1-10, where 10 is {goal} fully achieved, where are you?",
                    "gentle": "If you had to guess, where might you be on a 1-10 scale toward {goal}?",
                },
                pace_considerations="Scaling makes progress visible and concrete",
            ),
            QuestionTemplate(
                approach=InquiryApproach.SOLUTION_FOCUSED,
                category="scaling",
                template="What would one point higher on the scale look like?",
                when_to_use="After establishing current position on scale",
                source="De Jong & Berg (2013) - Interviewing for Solutions",
                directness_variants={
                    "direct": "Describe what one point higher looks like.",
                    "balanced": "What would one point higher on the scale look like?",
                    "gentle": "What might be a small sign you'd moved up just one point?",
                },
                pace_considerations="Small increment questions make change feel achievable",
            ),
            QuestionTemplate(
                approach=InquiryApproach.SOLUTION_FOCUSED,
                category="coping",
                template="How have you managed to keep things from getting worse?",
                when_to_use="When user feels helpless or defeated",
                source="De Jong & Berg (2013) - Interviewing for Solutions",
                directness_variants={
                    "direct": "What's keeping this from getting worse?",
                    "balanced": "How have you managed to keep things from getting worse?",
                    "gentle": "I'm noticing you're still here, still trying - what's helped you keep going?",
                },
                pace_considerations="Coping questions highlight resilience and agency",
            ),
            QuestionTemplate(
                approach=InquiryApproach.SOLUTION_FOCUSED,
                category="resources",
                template="What resources or strengths have you used in similar situations?",
                when_to_use="When user needs reminder of past competence",
                source="De Jong & Berg (2013) - Interviewing for Solutions",
                directness_variants={
                    "direct": "What strengths can you draw on here?",
                    "balanced": "What resources or strengths have you used in similar situations?",
                    "gentle": "What's helped you through difficult times before?",
                },
                pace_considerations="Resource questions activate existing capabilities",
            ),

            # ============================================================
            # PHENOMENOLOGICAL INQUIRY / FOCUSING
            # Source: Gendlin (1982) "Focusing" and Cornell (2013) "The Radical Acceptance of Everything"
            # ============================================================
            QuestionTemplate(
                approach=InquiryApproach.PHENOMENOLOGICAL,
                category="grounding",
                template="What do you notice in your body as you say that?",
                when_to_use="When user is abstract or disconnected from felt experience",
                source="Gendlin (1982) - Focusing",
                directness_variants={
                    "direct": "Check your body - what's there?",
                    "balanced": "What do you notice in your body as you say that?",
                    "gentle": "If you tune into your body for a moment, what's present?",
                },
                pace_considerations="Body questions require slowing down; allow 10-15 seconds",
            ),
            QuestionTemplate(
                approach=InquiryApproach.PHENOMENOLOGICAL,
                category="deepening",
                template="Can you stay with that feeling for a moment and see what it wants to say?",
                when_to_use="When felt sense has emerged but not yet articulated",
                source="Gendlin (1982) - Focusing",
                directness_variants={
                    "direct": "Stay with that feeling - what does it want to say?",
                    "balanced": "Can you stay with that feeling and see what it wants to say?",
                    "gentle": "If that feeling could speak, what might it say?",
                },
                pace_considerations="Staying with feelings is advanced; user needs capacity",
            ),
            QuestionTemplate(
                approach=InquiryApproach.PHENOMENOLOGICAL,
                category="naming",
                template="What word or image captures the quality of {sensation}?",
                when_to_use="When helping user articulate vague bodily sense",
                source="Gendlin (1982) - Focusing",
                directness_variants={
                    "direct": "What word fits {sensation}?",
                    "balanced": "What word or image captures the quality of {sensation}?",
                    "gentle": "Is there a word or image that might fit {sensation}?",
                },
                pace_considerations="Finding the right word creates 'felt shift' - be patient",
            ),
            QuestionTemplate(
                approach=InquiryApproach.PHENOMENOLOGICAL,
                category="welcoming",
                template="Can you say hello to {feeling} and let it know you're here with it?",
                when_to_use="When user is resisting or fighting an emotion",
                source="Cornell (2013) - The Radical Acceptance of Everything",
                directness_variants={
                    "direct": "Acknowledge {feeling} - say hello to it.",
                    "balanced": "Can you say hello to {feeling} and let it know you're here with it?",
                    "gentle": "What if you could just be with {feeling}, without changing it?",
                },
                pace_considerations="Radical acceptance approach - needs gentle, permissive framing",
            ),
            QuestionTemplate(
                approach=InquiryApproach.PHENOMENOLOGICAL,
                category="checking",
                template="Does {word} feel right for what you're experiencing, or is there something more accurate?",
                when_to_use="After user has named an experience - verify the fit",
                source="Gendlin (1982) - Focusing",
                directness_variants={
                    "direct": "Is {word} the right word?",
                    "balanced": "Does {word} feel right, or is there something more accurate?",
                    "gentle": "How does {word} sit with you - does it fit?",
                },
                pace_considerations="Checking creates precision and deeper contact with experience",
            ),
            QuestionTemplate(
                approach=InquiryApproach.PHENOMENOLOGICAL,
                category="sensation",
                template="Where in your body do you feel {emotion}?",
                when_to_use="When user names emotion but stays cognitive",
                source="Gendlin (1982) - Focusing",
                directness_variants={
                    "direct": "Where is {emotion} in your body?",
                    "balanced": "Where in your body do you feel {emotion}?",
                    "gentle": "If you scan your body, where might {emotion} be showing up?",
                },
                pace_considerations="Locating emotions in body creates embodied awareness",
            ),

            # ============================================================
            # SYSTEMS THINKING
            # Source: Meadows (2008) "Thinking in Systems" and Senge (1990) "The Fifth Discipline"
            # ============================================================
            QuestionTemplate(
                approach=InquiryApproach.SYSTEMS,
                category="connections",
                template="How does changing {element_a} affect {element_b}?",
                when_to_use="When exploring relationships in a system",
                source="Meadows (2008) - Thinking in Systems",
                directness_variants={
                    "direct": "What's the causal link between {element_a} and {element_b}?",
                    "balanced": "How does changing {element_a} affect {element_b}?",
                    "gentle": "I'm curious about the connection between {element_a} and {element_b}...",
                },
                pace_considerations="Causal questions invite complexity - allow thinking time",
            ),
            QuestionTemplate(
                approach=InquiryApproach.SYSTEMS,
                category="feedback",
                template="What happens when {action} creates {result}, and then {result} influences {action}?",
                when_to_use="When identifying feedback loops",
                source="Meadows (2008) - Thinking in Systems",
                directness_variants={
                    "direct": "Trace the feedback loop: {action} → {result} → ?",
                    "balanced": "What happens when {action} creates {result}, which then influences {action}?",
                    "gentle": "It sounds like {action} and {result} might be influencing each other - how does that cycle work?",
                },
                pace_considerations="Feedback loops are cognitively demanding - use visual aids if possible",
            ),
            QuestionTemplate(
                approach=InquiryApproach.SYSTEMS,
                category="emergence",
                template="What patterns emerge when {elements} interact over time?",
                when_to_use="When exploring emergent properties of a system",
                source="Meadows (2008) - Thinking in Systems",
                directness_variants={
                    "direct": "What patterns do you see emerging from {elements}?",
                    "balanced": "What patterns emerge when {elements} interact over time?",
                    "gentle": "As you step back and look at {elements} together, what do you notice?",
                },
                pace_considerations="Emergence requires zooming out - create spaciousness",
            ),
            QuestionTemplate(
                approach=InquiryApproach.SYSTEMS,
                category="leverage",
                template="Where could a small change in {system} create a large effect?",
                when_to_use="When looking for high-leverage interventions",
                source="Meadows (2008) - Thinking in Systems",
                directness_variants={
                    "direct": "What's the leverage point in {system}?",
                    "balanced": "Where could a small change create a large effect in {system}?",
                    "gentle": "What's something small that might shift {system} in a big way?",
                },
                pace_considerations="Leverage point questions focus energy efficiently",
            ),
            QuestionTemplate(
                approach=InquiryApproach.SYSTEMS,
                category="boundaries",
                template="What are you including in {system} and what are you leaving out?",
                when_to_use="When system boundaries need examination",
                source="Meadows (2008) - Thinking in Systems",
                directness_variants={
                    "direct": "Define the boundaries of {system}.",
                    "balanced": "What are you including in {system} and what are you leaving out?",
                    "gentle": "How are you thinking about what's inside vs. outside {system}?",
                },
                pace_considerations="Boundary questions reveal hidden assumptions",
            ),
            QuestionTemplate(
                approach=InquiryApproach.SYSTEMS,
                category="delays",
                template="What delays exist between {action} and {outcome}?",
                when_to_use="When timing and delays are relevant",
                source="Senge (1990) - The Fifth Discipline",
                directness_variants={
                    "direct": "How long between {action} and {outcome}?",
                    "balanced": "What delays exist between {action} and {outcome}?",
                    "gentle": "How much time passes between {action} and seeing {outcome}?",
                },
                pace_considerations="Delay awareness prevents premature conclusions",
            ),

            # ============================================================
            # METACOGNITIVE INQUIRY
            # Source: Flavell (1979) and Schraw & Moshman (1995) on Metacognition
            # ============================================================
            QuestionTemplate(
                approach=InquiryApproach.METACOGNITIVE,
                category="reflection",
                template="How are you approaching this problem?",
                when_to_use="When user needs to step back from content to examine process",
                source="Flavell (1979) - Metacognition and cognitive monitoring",
                directness_variants={
                    "direct": "Describe your problem-solving approach.",
                    "balanced": "How are you approaching this problem?",
                    "gentle": "I'm curious about your thinking process here - what's your approach?",
                },
                pace_considerations="Metacognitive questions create healthy distance",
            ),
            QuestionTemplate(
                approach=InquiryApproach.METACOGNITIVE,
                category="assumptions",
                template="What assumptions are you making about {situation}?",
                when_to_use="When hidden assumptions may be constraining thinking",
                source="Schraw & Moshman (1995) - Metacognitive theories",
                directness_variants={
                    "direct": "List your assumptions about {situation}.",
                    "balanced": "What assumptions are you making about {situation}?",
                    "gentle": "What might you be taking for granted about {situation}?",
                },
                pace_considerations="Surfacing assumptions can be destabilizing - proceed gently",
            ),
            QuestionTemplate(
                approach=InquiryApproach.METACOGNITIVE,
                category="perspective",
                template="What would you tell a friend who came to you with this situation?",
                when_to_use="When user needs distance from their own situation",
                source="Cognitive therapy tradition - self-distancing technique",
                directness_variants={
                    "direct": "Advise yourself as if you were someone else.",
                    "balanced": "What would you tell a friend facing this situation?",
                    "gentle": "If a good friend told you about this, what might you say to them?",
                },
                pace_considerations="Third-person perspective creates helpful objectivity",
            ),
            QuestionTemplate(
                approach=InquiryApproach.METACOGNITIVE,
                category="monitoring",
                template="How confident are you in {conclusion}?",
                when_to_use="When calibrating certainty and identifying knowledge gaps",
                source="Schraw & Moshman (1995) - Metacognitive theories",
                directness_variants={
                    "direct": "Rate your confidence in {conclusion}: 1-10.",
                    "balanced": "How confident are you in {conclusion}?",
                    "gentle": "How sure do you feel about {conclusion}?",
                },
                pace_considerations="Confidence calibration prevents overcommitment",
            ),
            QuestionTemplate(
                approach=InquiryApproach.METACOGNITIVE,
                category="strategy",
                template="Is this thinking strategy working, or do you need to try something different?",
                when_to_use="When user seems stuck in unproductive pattern",
                source="Flavell (1979) - Metacognition and cognitive monitoring",
                directness_variants={
                    "direct": "This approach isn't working - what else could you try?",
                    "balanced": "Is this strategy working, or should you try something different?",
                    "gentle": "How is this approach feeling - helpful, or time for something new?",
                },
                pace_considerations="Strategy evaluation prevents perseveration",
            ),
            QuestionTemplate(
                approach=InquiryApproach.METACOGNITIVE,
                category="learning",
                template="What are you learning about how you think through {domain}?",
                when_to_use="When highlighting patterns in user's thinking process",
                source="Schraw & Moshman (1995) - Metacognitive theories",
                directness_variants={
                    "direct": "What patterns do you notice in how you think about {domain}?",
                    "balanced": "What are you learning about how you think through {domain}?",
                    "gentle": "As you explore {domain}, what do you notice about your thinking?",
                },
                pace_considerations="Meta-learning questions build self-awareness over time",
            ),
        ]

    def get_templates_for_approach(
        self, approach: InquiryApproach, category: str | None = None
    ) -> list[QuestionTemplate]:
        """Get all templates for a specific approach, optionally filtered by category.

        Args:
            approach: The inquiry approach to filter by
            category: Optional category to further filter (e.g., "clarifying", "deepening")

        Returns:
            List of matching question templates
        """
        templates = [t for t in self._templates if t.approach == approach]

        if category:
            templates = [t for t in templates if t.category == category]

        return templates

    def get_template_by_criteria(
        self, approach: InquiryApproach, category: str, context: str
    ) -> QuestionTemplate | None:
        """Get a specific template matching approach, category, and context keywords.

        Args:
            approach: The inquiry approach
            category: The template category
            context: Context string to match against when_to_use

        Returns:
            Matching template or None
        """
        candidates = self.get_templates_for_approach(approach, category)

        # Simple keyword matching in when_to_use field
        context_lower = context.lower()
        for template in candidates:
            if any(
                keyword in context_lower
                for keyword in template.when_to_use.lower().split()
            ):
                return template

        # Return first matching category if no context match
        return candidates[0] if candidates else None

    def adapt_template(
        self,
        template: QuestionTemplate,
        directness: str = "balanced",
        placeholders: dict[str, Any] | None = None,
    ) -> str:
        """Adapt a template to profile settings and fill in placeholders.

        Args:
            template: The template to adapt
            directness: Profile directness setting (direct/balanced/gentle)
            placeholders: Dictionary of placeholder values to fill in template

        Returns:
            Adapted and filled question string
        """
        # Get directness variant or fall back to default template
        question = template.directness_variants.get(directness, template.template)

        # Fill in placeholders if provided
        if placeholders:
            try:
                question = question.format(**placeholders)
            except KeyError as e:
                # If placeholder is missing, return template with unfilled placeholders
                # This is acceptable - AI can fill them contextually
                pass

        return question

    def generate_question_batch(
        self,
        approach: InquiryApproach,
        state: UserState,
        context: str,
        directness: str = "balanced",
        abstraction: str = "mixed",
        count: int = 3,
    ) -> QuestionBatch:
        """Generate a batch of questions for a given state and approach.

        Args:
            approach: The inquiry approach to use
            state: The detected user state
            context: Current conversation context
            directness: Profile directness setting
            abstraction: Profile abstraction preference
            count: Number of questions to generate

        Returns:
            QuestionBatch with adapted questions
        """
        templates = self.get_templates_for_approach(approach)

        # Select diverse templates (different categories)
        selected_templates: list[QuestionTemplate] = []
        categories_used: set[str] = set()

        for template in templates:
            if template.category not in categories_used:
                selected_templates.append(template)
                categories_used.add(template.category)
                if len(selected_templates) >= count:
                    break

        # If we don't have enough unique categories, add more from any category
        if len(selected_templates) < count:
            for template in templates:
                if template not in selected_templates:
                    selected_templates.append(template)
                    if len(selected_templates) >= count:
                        break

        # Adapt templates to profile settings
        questions = [
            self.adapt_template(template, directness=directness)
            for template in selected_templates
        ]

        adaptations = [f"directness={directness}"]
        if abstraction != "mixed":
            adaptations.append(f"abstraction={abstraction}")

        return QuestionBatch(
            approach=approach,
            state=state,
            questions=questions,
            context=context,
            profile_adaptations_applied=adaptations,
        )

    def get_approach_description(self, approach: InquiryApproach) -> str:
        """Get a description of an inquiry approach.

        Args:
            approach: The inquiry approach

        Returns:
            Description string for system prompts
        """
        from ies_backend.schemas.question_engine import APPROACH_DESCRIPTIONS

        return APPROACH_DESCRIPTIONS.get(
            approach, "No description available for this approach."
        )

    def get_all_approaches(self) -> list[InquiryApproach]:
        """Get list of all inquiry approaches that have templates.

        Returns:
            List of InquiryApproach values with templates
        """
        approaches = {t.approach for t in self._templates}
        return sorted(approaches, key=lambda a: a.value)

    def get_categories_for_approach(self, approach: InquiryApproach) -> list[str]:
        """Get all categories available for an approach.

        Args:
            approach: The inquiry approach

        Returns:
            List of category names
        """
        categories = {
            t.category for t in self._templates if t.approach == approach
        }
        return sorted(categories)

    def get_template_count(self, approach: InquiryApproach | None = None) -> int:
        """Get count of templates, optionally filtered by approach.

        Args:
            approach: Optional approach to filter by

        Returns:
            Number of templates
        """
        if approach:
            return len([t for t in self._templates if t.approach == approach])
        return len(self._templates)


# Singleton instance
question_templates_service = QuestionTemplatesService()
