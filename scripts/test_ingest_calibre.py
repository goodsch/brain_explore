import json
from unittest.mock import MagicMock

from scripts.ingest_calibre import PatternTypeClassifier


def test_pattern_classifier_parses_llm_response():
    """PatternTypeClassifier should return parsed classification data."""
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps({
        "pattern_type": "design",
        "confidence": 0.87,
        "rationale": "Pattern language for built environments"
    })
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    classifier = PatternTypeClassifier(client=mock_client, model="gpt-4o-mini")
    result = classifier.classify(
        title="A Pattern Language",
        author="Christopher Alexander",
        metadata="Architecture pattern library",
        text_sample="Timeless way of building using structural patterns."
    )

    assert result is not None
    assert result.pattern_type == "design"
    assert result.confidence == 0.87
