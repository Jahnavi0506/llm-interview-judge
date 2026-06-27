"""
Unit tests for the question generator.
Run with: python -m pytest tests/ -v
"""

import pytest
from unittest.mock import patch, MagicMock
from app.schemas.question import QuestionOutput


# ── Mock Data ──────────────────────────────────────────────

MOCK_QUESTION_JSON = {
    "question": "What is self-attention in Transformers?",
    "topic_tags": ["attention", "transformers"],
    "key_concepts": ["Query", "Key", "Value", "Softmax"],
    "difficulty": "Medium"
}


# ── Tests ──────────────────────────────────────────────────

def test_question_output_schema_valid():
    """QuestionOutput accepts valid data."""
    q = QuestionOutput(**MOCK_QUESTION_JSON)
    assert q.question == "What is self-attention in Transformers?"
    assert len(q.key_concepts) == 4
    assert q.difficulty == "Medium"


def test_question_output_schema_missing_field():
    """QuestionOutput rejects data with missing required fields."""
    invalid = {
        "topic_tags": ["attention"],
        "key_concepts": ["Query"],
        "difficulty": "Medium"
        # missing 'question'
    }
    with pytest.raises(Exception):
        QuestionOutput(**invalid)


def test_question_output_empty_concepts():
    """QuestionOutput accepts empty key_concepts list."""
    data = MOCK_QUESTION_JSON.copy()
    data["key_concepts"] = []
    q = QuestionOutput(**data)
    assert q.key_concepts == []


@patch("app.core.question_generator.call_gemini_json")
def test_generate_question_returns_valid_output(mock_call):
    """generate_question returns QuestionOutput when API succeeds."""
    mock_call.return_value = MOCK_QUESTION_JSON

    from app.core.question_generator import generate_question
    result = generate_question(domain="LLMs", difficulty="Medium")

    assert isinstance(result, QuestionOutput)
    assert result.difficulty == "Medium"
    mock_call.assert_called_once()


@patch("app.core.question_generator.call_gemini_json")
def test_generate_question_excludes_previous(mock_call):
    """generate_question passes previous_questions to the prompt."""
    mock_call.return_value = MOCK_QUESTION_JSON

    from app.core.question_generator import generate_question
    from app.prompts.question_prompt import get_question_prompt

    previous = ["What is backpropagation?", "Explain gradient descent."]
    result = generate_question(
        domain="ML",
        difficulty="Easy",
        previous_questions=previous
    )

    # Check that the prompt was built with previous questions
    call_args = mock_call.call_args[0][0]
    assert "backpropagation" in call_args
    assert isinstance(result, QuestionOutput)


def test_difficulty_values():
    """QuestionOutput accepts all valid difficulty levels."""
    for diff in ["Easy", "Medium", "Hard"]:
        data = MOCK_QUESTION_JSON.copy()
        data["difficulty"] = diff
        q = QuestionOutput(**data)
        assert q.difficulty == diff