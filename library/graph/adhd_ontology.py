"""
ADHD-Friendly Knowledge Graph Ontology

Research-backed schema designed to work WITH the ADHD brain:
- Interest-based nervous system (Rosier/Dodson)
- Capture what resonates, not what's "important" (Forte)
- Multiple entry points for navigation
- Non-judgmental status lifecycle (growth metaphor)
- Visible progress through breadcrumb trails

References:
- Russell Barkley: Executive function as self-regulation
- Tamara Rosier: Interest-based nervous system
- Gabor Maté: Implicit memory and emotional resonance
- Tiago Forte: Capture what resonates, 12 favorite problems
- Research synthesis in .interleaved-thinking/final-answer.md
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# =============================================================================
# Entity Types
# =============================================================================

class EntityType(str, Enum):
    """
    Entity types split into personal artifacts and domain knowledge.

    Personal artifacts are raw, unprocessed, captured in the moment.
    Domain knowledge is structured, validated, from external sources.
    """

    # Personal Artifacts (captured from thinking)
    SPARK = "spark"                    # Raw resonance, unprocessed insight
    INSIGHT = "insight"                # Processed spark with personal meaning
    THREAD = "thread"                  # Connected exploration path
    FAVORITE_PROBLEM = "favorite_problem"  # Feynman-style anchor question

    # Domain Knowledge (from books/research)
    CONCEPT = "concept"                # Abstract idea or principle
    FRAMEWORK = "framework"            # Structured way of thinking
    THEORY = "theory"                  # Explanatory model
    MECHANISM = "mechanism"            # How something works
    PHENOMENON = "phenomenon"          # Observable pattern
    PATTERN = "pattern"                # Recurring structure
    DISTINCTION = "distinction"        # Key difference that matters
    PERSON = "person"                  # Researcher, author, thinker
    BOOK = "book"                      # Source material
    ASSESSMENT = "assessment"          # Scale or measurement tool


# =============================================================================
# ADHD-Critical Metadata Enums
# =============================================================================

class ResonanceSignal(str, Enum):
    """
    WHY something resonated - the emotional hook for retrieval.

    ADHD brains retrieve via emotional resonance, not taxonomic importance.
    These signals become retrieval cues for future exploration.
    """
    CURIOUS = "curious"          # "I want to know more"
    EXCITED = "excited"          # "This could change everything"
    SURPRISED = "surprised"      # "I didn't expect that"
    MOVED = "moved"              # "This touched something deep"
    DISTURBED = "disturbed"      # "This challenges my assumptions"
    UNCLEAR = "unclear"          # "I don't understand but it matters"
    CONNECTED = "connected"      # "This links to something else"
    VALIDATED = "validated"      # "This confirms what I sensed"


class EnergyLevel(str, Enum):
    """
    Energy level appropriate for engaging with this entity.

    ADHD energy fluctuates. Some content requires high energy to engage.
    Matching content to energy state prevents abandonment.
    """
    LOW = "low"        # Can engage when depleted (simple, grounding)
    MEDIUM = "medium"  # Requires some activation (most content)
    HIGH = "high"      # Needs full engagement (complex, challenging)


class EntityStatus(str, Enum):
    """
    Non-judgmental growth lifecycle using gardening metaphor.

    Avoids shame-inducing terms like "unprocessed" or "incomplete".
    Growth happens naturally, not through forced completion.
    """
    CAPTURED = "captured"    # Seed planted - exists, not yet explored
    EXPLORING = "exploring"  # Growing - actively being developed
    ANCHORED = "anchored"    # Rooted - integrated into understanding


# =============================================================================
# Enhanced Entity Model
# =============================================================================

@dataclass
class ADHDEntity:
    """
    Entity designed for ADHD-friendly knowledge capture and retrieval.

    Key differences from standard entity:
    - Resonance signal captures WHY it mattered (emotional retrieval cue)
    - Capture context preserves the moment (implicit memory support)
    - Energy level enables mood-appropriate navigation
    - Favorite problems link to ongoing inquiry anchors
    - Exploration visits and last_visited support spaced retrieval
    """

    # Core identity
    id: str                              # Unique identifier
    type: EntityType                     # What kind of entity
    title: str                           # Display name
    content: str                         # Full content/description

    # ADHD-critical metadata
    resonance_signal: Optional[ResonanceSignal] = None  # Why it resonated
    capture_context: Optional[str] = None    # Where/when captured (e.g., "Reading Scattered Minds, ch.26")
    energy_level_appropriate: EnergyLevel = EnergyLevel.MEDIUM

    # Status lifecycle
    status: EntityStatus = EntityStatus.CAPTURED

    # Navigation support
    favorite_problems: list[str] = field(default_factory=list)  # IDs of related favorite problems
    tags: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)

    # Engagement tracking (for spaced retrieval)
    exploration_visits: int = 0
    last_visited: Optional[datetime] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    # Source linking
    source_id: Optional[str] = None      # Book/chapter ID if from reading
    source_location: Optional[str] = None  # Page, paragraph, highlight

    def visit(self) -> None:
        """Record an exploration visit."""
        self.exploration_visits += 1
        self.last_visited = datetime.now()
        self.updated_at = datetime.now()

    def promote_to_exploring(self) -> None:
        """Transition from captured to exploring."""
        if self.status == EntityStatus.CAPTURED:
            self.status = EntityStatus.EXPLORING
            self.updated_at = datetime.now()

    def anchor(self) -> None:
        """Mark as fully integrated."""
        self.status = EntityStatus.ANCHORED
        self.updated_at = datetime.now()


# =============================================================================
# Relationship Types
# =============================================================================

class RelationshipType(str, Enum):
    """
    Relationship types organized by category.

    Includes new ADHD-critical types for tracking:
    - How discoveries happen (sparked_by, led_to_discovery)
    - Energy flow (energy_toward, energy_away)
    - Problem-solution links (addresses_problem)
    """

    # ADHD-Critical: Discovery Flow
    SPARKED_BY = "sparked_by"              # "This spark came from reading X"
    LED_TO_DISCOVERY = "led_to_discovery"  # "Exploring X led me to discover Y"
    ADDRESSES_PROBLEM = "addresses_problem"  # "This insight addresses favorite problem X"
    ENERGY_TOWARD = "energy_toward"        # "Thinking about X gives me energy for Y"
    ENERGY_AWAY = "energy_away"            # "X drains energy needed for Y"

    # Resonance Mapping
    RESONATES_WITH = "resonates_with"      # Emotional/intuitive connection
    ANALOGOUS_TO = "analogous_to"          # Similar pattern in different domain
    METAPHOR_FOR = "metaphor_for"          # One thing illuminates another
    REFRAMES = "reframes"                  # Changes perspective on

    # Structural (existing from ontology doc)
    COMPONENT_OF = "component_of"          # Part-whole relationship
    INSTANCE_OF = "instance_of"            # Example of category
    RELATED_TO = "related_to"              # General association
    SUBCATEGORY_OF = "subcategory_of"      # Taxonomic hierarchy

    # Causal (existing)
    CAUSES = "causes"                      # X causes Y
    ENABLES = "enables"                    # X makes Y possible
    PREVENTS = "prevents"                  # X blocks Y
    MODULATES = "modulates"                # X affects intensity of Y

    # Epistemic (existing)
    SUPPORTS = "supports"                  # Evidence supports theory
    CONTRADICTS = "contradicts"            # Evidence against
    DEVELOPS = "develops"                  # Author develops theory
    CITES = "cites"                        # Reference relationship
    OPERATIONALIZES = "operationalizes"    # Makes measurable

    # Evaluative
    CONTRASTS_WITH = "contrasts_with"      # Key difference
    COMPLEMENTS = "complements"            # Works together with
    DEPENDS_ON = "depends_on"              # Prerequisite relationship


# =============================================================================
# Enhanced Relationship Model
# =============================================================================

@dataclass
class ADHDRelationship:
    """
    Relationship with ADHD-friendly metadata.

    Captures not just that two things are connected, but:
    - How the connection was discovered
    - Why it matters (resonance context)
    - Strength of the connection
    """

    # Core relationship
    id: str                              # Unique identifier
    source_id: str                       # Source entity ID
    target_id: str                       # Target entity ID
    relation_type: RelationshipType      # Type of relationship

    # Context
    evidence: Optional[str] = None       # Quote or explanation
    discovery_context: Optional[str] = None  # How/when this connection was found

    # Strength and confidence
    strength: float = 0.5                # 0.0-1.0 connection strength
    confidence: float = 0.5              # 0.0-1.0 how sure we are

    # Bidirectional flag
    bidirectional: bool = False          # True if relationship goes both ways

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def is_discovery_flow(self) -> bool:
        """Check if this is an ADHD discovery flow relationship."""
        return self.relation_type in {
            RelationshipType.SPARKED_BY,
            RelationshipType.LED_TO_DISCOVERY,
            RelationshipType.ADDRESSES_PROBLEM,
            RelationshipType.ENERGY_TOWARD,
            RelationshipType.ENERGY_AWAY,
        }


# =============================================================================
# Favorite Problem (Feynman's 12 Problems)
# =============================================================================

@dataclass
class FavoriteProblem:
    """
    A persistent inquiry anchor (Feynman's "12 Favorite Problems").

    These are questions you carry with you always, testing new
    information against them. They serve as navigation anchors
    in the knowledge graph.

    Example: "How do I stay present when anxiety pulls me away?"
    """

    id: str
    question: str                        # The problem framed as a question
    why_matters: str                     # Personal significance

    # Discovery tracking
    discoveries: list[str] = field(default_factory=list)  # Entity IDs that address this
    last_discovery: Optional[datetime] = None

    # Status
    active: bool = True                  # Still an active inquiry

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    def add_discovery(self, entity_id: str) -> None:
        """Record that an entity addresses this problem."""
        if entity_id not in self.discoveries:
            self.discoveries.append(entity_id)
            self.last_discovery = datetime.now()
            self.updated_at = datetime.now()


# =============================================================================
# Thread (Exploration Journey)
# =============================================================================

@dataclass
class Thread:
    """
    A connected exploration path through the knowledge graph.

    Threads capture the journey of discovery, not just the destination.
    They become visible progress markers and can be resumed later.
    """

    id: str
    title: str                           # Descriptive name
    description: Optional[str] = None    # What this thread explores

    # The path
    breadcrumbs: list[str] = field(default_factory=list)  # Ordered entity IDs

    # Status
    status: EntityStatus = EntityStatus.EXPLORING

    # Context
    starting_context: Optional[str] = None  # What prompted this exploration
    current_question: Optional[str] = None  # What we're currently exploring

    # Related
    favorite_problems: list[str] = field(default_factory=list)  # Problem IDs this addresses

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_extended: Optional[datetime] = None

    def add_breadcrumb(self, entity_id: str) -> None:
        """Add an entity to the exploration path."""
        self.breadcrumbs.append(entity_id)
        self.last_extended = datetime.now()

    @property
    def length(self) -> int:
        """Number of stops in this journey."""
        return len(self.breadcrumbs)
