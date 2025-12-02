# Question Engine API Documentation

The Question Engine provides intelligent question generation based on user state detection and cognitive profiling.

## Endpoints

### 1. Detect State
`POST /question-engine/detect-state`

Analyzes recent conversation messages to detect user's cognitive/emotional state.

**Request:**
```json
{
  "recent_messages": [
    "I'm not sure where to go with this",
    "It feels like I'm going in circles"
  ],
  "user_id": "user123",
  "capacity": 6
}
```

**Response:**
```json
{
  "primary_state": "stuck",
  "confidence": 0.85,
  "secondary_states": [],
  "signals_observed": {
    "response_length": "medium",
    "certainty_language": 3,
    "energy_words": [],
    "frustration_indicators": ["going in circles"],
    "engagement_indicators": [],
    "repetition_detected": true,
    "abstraction_level": "mixed",
    "capacity_reported": 6
  },
  "reasoning": "Repetition with frustration indicates stuck state"
}
```

### 2. Select Approach
`POST /question-engine/select-approach`

Selects the best inquiry approach based on detected state and user profile.

**Request:**
```json
{
  "user_id": "user123",
  "recent_messages": [
    "I'm not sure where to go with this"
  ],
  "previous_approach": "socratic",
  "session_duration_minutes": 15
}
```

**Response:**
```json
{
  "selected_approach": "metacognitive",
  "confidence": 0.76,
  "reasoning": "Detected state: stuck (Repetition detected without progress). Using metacognitive inquiry to reflect on process",
  "pacing": "moderate",
  "directness": "balanced",
  "abstraction": "mixed",
  "structure": "moderate",
  "fallback_approaches": ["socratic"]
}
```

### 3. Get Templates
`GET /question-engine/templates/{approach}?category=clarifying`

Retrieves question templates for a specific approach.

**Example:**
`GET /question-engine/templates/socratic?category=clarifying`

**Response:**
```json
[
  {
    "approach": "socratic",
    "category": "clarifying",
    "template": "What do you mean by '{concept}'?",
    "when_to_use": "When user uses abstract or ambiguous term",
    "source": null,
    "directness_variants": {
      "gentle": "I'm curious what '{concept}' means to you?",
      "balanced": "What do you mean by '{concept}'?",
      "direct": "Define '{concept}' - what exactly does that mean?"
    },
    "pace_considerations": null
  }
]
```

### 4. Generate Questions
`POST /question-engine/generate-questions`

Orchestrates the full pipeline: state detection → approach selection → question generation.

**Request:**
```json
{
  "user_id": "user123",
  "recent_messages": [
    "I feel stuck on this problem"
  ],
  "context": "User exploring their relationship to perfectionism",
  "num_questions": 3
}
```

**Response:**
```json
{
  "approach": "metacognitive",
  "state": "stuck",
  "questions": [
    "How are you thinking about perfectionism?",
    "What assumptions are you making about perfectionism?",
    "If a friend came to you with this, what might you say?"
  ],
  "context": "User exploring their relationship to perfectionism",
  "profile_adaptations_applied": ["directness=gentle"]
}
```

### 5. List Approaches
`GET /question-engine/approaches`

Returns mapping of user states to recommended inquiry approaches.

**Response:**
```json
{
  "flowing": ["socratic", "systems"],
  "stuck": ["socratic", "metacognitive"],
  "overwhelmed": ["solution_focused", "phenomenological"],
  "exploring": ["systems", "socratic"],
  "processing": ["phenomenological", "metacognitive"],
  "uncertain": ["metacognitive", "solution_focused"],
  "emotional": ["phenomenological", "solution_focused"],
  "tired": ["solution_focused", "phenomenological"]
}
```

### 6. List Categories
`GET /question-engine/categories?approach=socratic`

Returns available question categories, optionally filtered by approach.

**Response:**
```json
["challenging", "clarifying", "deepening", "grounding"]
```

## User States

- **flowing**: Engaged, productive, good energy
- **stuck**: Looping, not making progress
- **overwhelmed**: Too much, need grounding
- **exploring**: Curious, branching out
- **processing**: Need time to digest
- **uncertain**: Unclear on direction/purpose
- **emotional**: Strong feelings present
- **tired**: Low energy, need gentle approach

## Inquiry Approaches

- **socratic**: Clarifying assumptions, testing logic
- **solution_focused**: Forward motion, small steps
- **phenomenological**: Body-based, felt sense, focusing
- **systems**: Connections, patterns, emergence
- **metacognitive**: Reflection on thinking process

## Profile Adaptations

The Question Engine adapts questions based on user profile:

- **Pacing**: fast | moderate | slow
- **Directness**: direct | balanced | gentle
- **Abstraction**: concrete | mixed | abstract
- **Structure**: tight | moderate | loose

## Integration Example

```python
from ies_backend.api.question_engine import (
    DetectStateRequest,
    GenerateQuestionsRequest,
)
import httpx

async def get_questions_for_user(user_id: str, messages: list[str], context: str):
    async with httpx.AsyncClient() as client:
        # Generate adapted questions
        response = await client.post(
            "http://localhost:8000/question-engine/generate-questions",
            json={
                "user_id": user_id,
                "recent_messages": messages,
                "context": context,
                "num_questions": 3,
            }
        )
        batch = response.json()
        return batch["questions"]
```

## Development Notes

- State detection uses pattern matching on message content (future: LLM enhancement)
- Templates are currently hardcoded (future: database-driven)
- Profile integration is automatic when user_id provided
- All endpoints handle missing profiles gracefully with defaults
