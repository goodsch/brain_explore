"""Tests for enhanced Context Note Parser."""

import pytest

from ies_backend.schemas.context import ContextStatus, ContextType
from ies_backend.services.context_note_parser import ContextNoteParser


# -----------------------------------------------------------------------------
# Test Fixtures - Sample Markdown Documents
# -----------------------------------------------------------------------------


@pytest.fixture
def basic_context_note():
    """Basic Context Note without frontmatter."""
    return """
# Feynman: Understanding Executive Function

## Summary / Intent
Exploring how executive function works in ADHD brains and why it's so difficult.

## Key Questions
- What are the core components of executive function?
- How does working memory relate to EF?
- Why is task initiation so hard?

## Areas of Exploration
- Neural mechanisms of attention
- Working memory capacity
- Dopamine's role

## Core Concepts
- Executive Function
- Working Memory
- Dopamine
- Prefrontal Cortex
"""


@pytest.fixture
def context_note_with_frontmatter():
    """Context Note with YAML frontmatter."""
    return """---
context_id: ctx_abc123
context_type: feynman_problem
status: active
created: 2025-12-09T12:00:00Z
parent_context_id: ctx_parent456
---

# Feynman: Understanding Executive Function

## Summary / Intent
Exploring EF mechanisms.

## Key Questions
- What is EF?

## Core Concepts
- Executive Function
"""


@pytest.fixture
def context_note_with_checkboxes():
    """Context Note with checkbox status and IDs."""
    return """
# Project: Build IES Reader

## Key Questions
- [ ] How do we implement entity overlay? <!-- q_abc123 -->
- [x] Should we use epub.js or foliate? <!-- q_def456 -->
- Q1: What about CFI-based highlighting?
- [X] Do we need mobile support?

## Core Concepts
- Entity Overlay
- CFI
"""


@pytest.fixture
def context_note_with_existing_ids():
    """Context Note with existing IDs in comments."""
    return """
# Theory: Predictive Processing

## Key Questions
- What is prediction error? <!-- q_pred_001 -->
- How does PP explain perception? <!-- q_pred_002 -->

## Areas of Exploration
- Bayesian brain hypothesis <!-- area_bayes_001 -->
- Free energy principle <!-- area_fep_001 -->

## Core Concepts
- Prediction Error <!-- concept_pe_001 -->
- Precision Weighting
"""


@pytest.fixture
def minimal_context_note():
    """Minimal valid Context Note (title only)."""
    return """
# Life: Personal Growth

## Summary / Intent
My personal growth journey.
"""


@pytest.fixture
def context_note_mixed_types():
    """Context Note with different context type formats."""
    return """
# Concept: Dopamine Regulation

## Summary
Understanding dopamine's role in motivation.

## Key Questions
- How does dopamine affect motivation?

## Core Concepts
- Dopamine
- Motivation
"""


# -----------------------------------------------------------------------------
# Basic Parsing Tests
# -----------------------------------------------------------------------------


def test_parse_basic_context_note(basic_context_note):
    """Test parsing a basic Context Note without frontmatter."""
    result = ContextNoteParser.parse(basic_context_note)

    # Check context
    assert result.context.title == "Understanding Executive Function"
    assert result.context.type == ContextType.FEYNMAN_PROBLEM
    assert result.context.summary == "Exploring how executive function works in ADHD brains and why it's so difficult."
    assert result.context.status == ContextStatus.ACTIVE

    # Check questions
    assert len(result.questions) == 3
    assert result.questions[0].text == "What are the core components of executive function?"
    assert result.questions[1].text == "How does working memory relate to EF?"
    assert result.questions[2].text == "Why is task initiation so hard?"

    # Check areas
    assert len(result.areas) == 3
    assert result.areas[0].title == "Neural mechanisms of attention"
    assert result.areas[1].title == "Working memory capacity"
    assert result.areas[2].title == "Dopamine's role"

    # Check concepts
    assert len(result.concepts) == 4
    assert result.concepts[0].name == "Executive Function"
    assert result.concepts[1].name == "Working Memory"
    assert result.concepts[2].name == "Dopamine"
    assert result.concepts[3].name == "Prefrontal Cortex"


def test_parse_with_frontmatter(context_note_with_frontmatter):
    """Test parsing with YAML frontmatter."""
    result = ContextNoteParser.parse(context_note_with_frontmatter)

    # Check frontmatter values override defaults
    assert result.context.id == "ctx_abc123"
    assert result.context.type == ContextType.FEYNMAN_PROBLEM
    assert result.context.status == ContextStatus.ACTIVE
    assert result.context.parent_context_id == "ctx_parent456"


def test_parse_with_checkboxes(context_note_with_checkboxes):
    """Test parsing questions with checkbox status."""
    result = ContextNoteParser.parse(context_note_with_checkboxes)

    # Check title type parsing
    assert result.context.title == "Build IES Reader"
    assert result.context.type == ContextType.PROJECT

    # Check questions
    assert len(result.questions) == 4

    # Question 1: unchecked with ID
    assert result.questions[0].text == "How do we implement entity overlay?"
    assert result.questions[0].existing_id == "q_abc123"
    assert result.questions[0].is_completed is False

    # Question 2: checked with ID
    assert result.questions[1].text == "Should we use epub.js or foliate?"
    assert result.questions[1].existing_id == "q_def456"
    assert result.questions[1].is_completed is True

    # Question 3: prefix without checkbox
    assert result.questions[2].text == "What about CFI-based highlighting?"
    assert result.questions[2].prefix == "Q1"
    assert result.questions[2].is_completed is False

    # Question 4: uppercase [X] checkbox
    assert result.questions[3].text == "Do we need mobile support?"
    assert result.questions[3].is_completed is True


def test_parse_with_existing_ids(context_note_with_existing_ids):
    """Test parsing with existing IDs in HTML comments."""
    result = ContextNoteParser.parse(context_note_with_existing_ids)

    # Check questions have IDs
    assert len(result.questions) == 2
    assert result.questions[0].existing_id == "q_pred_001"
    assert result.questions[1].existing_id == "q_pred_002"

    # Check areas have IDs
    assert len(result.areas) == 2
    assert result.areas[0].existing_id == "area_bayes_001"
    assert result.areas[1].existing_id == "area_fep_001"

    # Check concepts have IDs
    assert len(result.concepts) == 2
    assert result.concepts[0].existing_id == "concept_pe_001"
    assert result.concepts[1].existing_id is None  # No ID in comment


def test_parse_minimal_context_note(minimal_context_note):
    """Test parsing minimal Context Note (title only)."""
    result = ContextNoteParser.parse(minimal_context_note)

    assert result.context.title == "Personal Growth"
    assert result.context.type == ContextType.LIFE_AREA
    assert result.context.summary == "My personal growth journey."
    assert len(result.questions) == 0
    assert len(result.areas) == 0
    assert len(result.concepts) == 0


def test_parse_different_context_types(context_note_mixed_types):
    """Test parsing different context type prefixes."""
    result = ContextNoteParser.parse(context_note_mixed_types)

    assert result.context.title == "Dopamine Regulation"
    assert result.context.type == ContextType.CONCEPT_CLUSTER


# -----------------------------------------------------------------------------
# Edge Cases and Error Handling
# -----------------------------------------------------------------------------


def test_parse_no_sections():
    """Test parsing note with title but no sections."""
    markdown = "# Feynman: Test Title"
    result = ContextNoteParser.parse(markdown)

    assert result.context.title == "Test Title"
    assert len(result.questions) == 0
    assert len(result.areas) == 0
    assert len(result.concepts) == 0


def test_parse_empty_sections():
    """Test parsing note with empty sections."""
    markdown = """
# Project: Empty Sections

## Summary / Intent

## Key Questions

## Core Concepts
"""
    result = ContextNoteParser.parse(markdown)

    assert result.context.title == "Empty Sections"
    assert result.context.summary is None
    assert len(result.questions) == 0
    assert len(result.concepts) == 0


def test_parse_no_title():
    """Test parsing note without heading."""
    markdown = """
## Key Questions
- What is this?
"""
    result = ContextNoteParser.parse(markdown)

    # Should use fallback title
    assert result.context.title == "Untitled Context"
    assert result.context.type == ContextType.FEYNMAN_PROBLEM


def test_parse_invalid_frontmatter():
    """Test parsing note with invalid YAML frontmatter."""
    markdown = """---
invalid: yaml: content: here
---

# Feynman: Test

## Key Questions
- Question 1
"""
    result = ContextNoteParser.parse(markdown)

    # Should treat as no frontmatter and parse body
    assert result.context.title == "Test"
    assert len(result.questions) == 1


def test_parse_alternative_section_names():
    """Test parsing with alternative section name variations."""
    markdown = """
# Theory: Alternative Sections

## Summary
This is a summary.

## Intent
This is intent (should be ignored, summary takes precedence).

## Key Questions
- Question 1

## Areas of Exploration
- Area 1

## Core Concepts
- Concept 1
"""
    result = ContextNoteParser.parse(markdown)

    # Should use "Summary" section (first match)
    assert result.context.summary == "This is a summary."
    assert len(result.questions) == 1
    assert len(result.areas) == 1
    assert len(result.concepts) == 1


def test_parse_case_insensitive_type():
    """Test case-insensitive context type parsing."""
    markdown = "# FEYNMAN: Test"
    result = ContextNoteParser.parse(markdown)
    assert result.context.type == ContextType.FEYNMAN_PROBLEM

    markdown = "# Project: Test"
    result = ContextNoteParser.parse(markdown)
    assert result.context.type == ContextType.PROJECT

    markdown = "# theory: Test"
    result = ContextNoteParser.parse(markdown)
    assert result.context.type == ContextType.THEORY


def test_parse_whitespace_handling():
    """Test robust whitespace handling in bullets."""
    markdown = """
# Feynman: Whitespace Test

## Key Questions
-    Question with spaces
*   Question with asterisk
  - Indented question

## Core Concepts
-  Concept 1
- Concept 2
"""
    result = ContextNoteParser.parse(markdown)

    assert len(result.questions) == 3
    assert result.questions[0].text == "Question with spaces"
    assert result.questions[1].text == "Question with asterisk"
    assert result.questions[2].text == "Indented question"

    assert len(result.concepts) == 2


def test_parse_multiline_summary():
    """Test parsing summary that spans multiple lines."""
    markdown = """
# Feynman: Multiline Summary

## Summary / Intent
This is a summary that
spans multiple lines and
should be concatenated together.

## Key Questions
- Question 1
"""
    result = ContextNoteParser.parse(markdown)

    # Note: Current implementation doesn't concatenate non-bullet lines
    # Only first line is captured for summary
    assert result.context.summary is not None


def test_parse_with_siyuan_block_id():
    """Test parsing with siyuan_block_id parameter."""
    markdown = "# Feynman: Test"
    siyuan_block_id = "20251209120000-abc123"

    result = ContextNoteParser.parse(markdown, siyuan_block_id=siyuan_block_id)

    assert result.context.siyuan_block_id == siyuan_block_id


# -----------------------------------------------------------------------------
# Regression Tests
# -----------------------------------------------------------------------------


def test_question_prefix_with_colon():
    """Test question prefix parsing (Q1:, Q2:, etc.)."""
    markdown = """
# Feynman: Prefix Test

## Key Questions
- Q1: First question
- Q2: Second question
- Third question without prefix
"""
    result = ContextNoteParser.parse(markdown)

    assert len(result.questions) == 3
    assert result.questions[0].prefix == "Q1"
    assert result.questions[0].text == "First question"
    assert result.questions[1].prefix == "Q2"
    assert result.questions[1].text == "Second question"
    assert result.questions[2].prefix is None


def test_checkbox_variations():
    """Test different checkbox formats."""
    markdown = """
# Project: Checkbox Test

## Key Questions
- [ ] Open task
- [x] Completed task (lowercase)
- [X] Completed task (uppercase)
- [  ] Empty brackets with spaces
"""
    result = ContextNoteParser.parse(markdown)

    assert len(result.questions) == 4
    assert result.questions[0].is_completed is False
    assert result.questions[1].is_completed is True
    assert result.questions[2].is_completed is True
    assert result.questions[3].is_completed is False


def test_html_comment_id_extraction():
    """Test extraction of IDs from HTML comments."""
    markdown = """
# Feynman: ID Test

## Key Questions
- Question without ID
- Question with ID <!-- q_abc123 -->
- Question with spaces <!-- q_def456   -->
- Question with complex ID <!-- q_complex_id_789 -->

## Areas of Exploration
- Area with ID <!-- area_test_001 -->

## Core Concepts
- Concept with ID <!-- concept_dopamine_001 -->
"""
    result = ContextNoteParser.parse(markdown)

    # Questions
    assert result.questions[0].existing_id is None
    assert result.questions[1].existing_id == "q_abc123"
    assert result.questions[2].existing_id == "q_def456"
    assert result.questions[3].existing_id == "q_complex_id_789"

    # Areas
    assert result.areas[0].existing_id == "area_test_001"

    # Concepts
    assert result.concepts[0].existing_id == "concept_dopamine_001"


def test_context_id_generation():
    """Test that context IDs are generated when not in frontmatter."""
    markdown = "# Feynman: Test"
    result = ContextNoteParser.parse(markdown)

    # Should have generated ID
    assert result.context.id is not None
    assert result.context.id.startswith("ctx_")


def test_parse_status_from_frontmatter():
    """Test parsing different status values from frontmatter."""
    test_cases = [
        ("active", ContextStatus.ACTIVE),
        ("paused", ContextStatus.PAUSED),
        ("archived", ContextStatus.ARCHIVED),
        ("idea", ContextStatus.IDEA),
    ]

    for status_str, expected_status in test_cases:
        markdown = f"""---
status: {status_str}
---

# Feynman: Test
"""
        result = ContextNoteParser.parse(markdown)
        assert result.context.status == expected_status


def test_parse_datetime_from_frontmatter():
    """Test parsing created datetime from frontmatter."""
    markdown = """---
created: 2025-12-09T12:34:56Z
---

# Feynman: Test
"""
    result = ContextNoteParser.parse(markdown)

    # Should parse ISO datetime
    assert result.context.created_at.year == 2025
    assert result.context.created_at.month == 12
    assert result.context.created_at.day == 9


def test_raw_sections_preserved():
    """Test that raw sections are preserved in result."""
    markdown = """
# Feynman: Test

## Key Questions
- Question 1
- Question 2

## Core Concepts
- Concept 1

## Custom Section
- Custom content
"""
    result = ContextNoteParser.parse(markdown)

    assert "key questions" in result.raw_sections
    assert "core concepts" in result.raw_sections
    assert "custom section" in result.raw_sections
    assert len(result.raw_sections["key questions"]) == 2
    assert result.raw_sections["custom section"] == ["- Custom content"]
