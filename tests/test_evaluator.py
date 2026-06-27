"""
Unit tests for the evaluator.
Run with: python -m pytest tests/ -v
"""

import pytest
from unittest.mock import patch
from app.schemas.evaluation import EvaluationOutput


# ── Mock Data ──────────────────────────────────────────────

MOCK_EVALUATION_JSON = {
    "score": 7.5,
    "strengths": ["Good intuition about attention"],
    "weaknesses": ["Did not explain QKV computation"],
    "missing_concepts": ["Query", "Key", "Value"],
    "concept_coverage": {
        "Query": "missing",
        "Key": "missing",
        "Value": "missing",
        "Softmax": "partial"
    },
    "improved_answer": "Self-attention computes Query, Key, Value vectors...",
    "interviewer_note": "Candidate shows basic understanding but lacks depth."
}

SAMPLE_QUESTION = "Explain the self-attention mechanism in Transformers."
SAMPLE_ANSWER = "Self-attention helps the model focus on important words."
SAMPLE_CONCEPTS = ["Query", "Key", "Value", "Softmax"]


# ── Schema Tests ───────────────────────────────────────────

def test_evaluation_output_valid():
    """EvaluationOutput accepts valid data."""
    e = EvaluationOutput(**MOCK_EVALUATION_JSON)
    assert e.score == 7.5
    assert len(e.missing_concepts) == 3
    assert e.interviewer_note != ""


def test_evaluation_score_bounds():
    """EvaluationOutput rejects scores outside 0-10."""
    invalid = MOCK_EVALUATION_JSON.copy()
    invalid["score"] = 11.0
    with pytest.raises(Exception):
        EvaluationOutput(**invalid)


def test_evaluation_score_lower_bound():
    """EvaluationOutput rejects negative scores."""
    invalid = MOCK_EVALUATION_JSON.copy()
    invalid["score"] = -1.0
    with pytest.raises(Exception):
        EvaluationOutput(**invalid)


def test_evaluation_concept_coverage_values():
    """concept_coverage only allows covered/partial/missing."""
    invalid = MOCK_EVALUATION_JSON.copy()
    invalid["concept_coverage"] = {"Query": "unknown_status"}
    with pytest.raises(Exception):
        EvaluationOutput(**invalid)


def test_evaluation_empty_strengths():
    """EvaluationOutput accepts empty strengths list."""
    data = MOCK_EVALUATION_JSON.copy()
    data["strengths"] = []
    e = EvaluationOutput(**data)
    assert e.strengths == []


@patch("app.core.evaluator.call_gemini_json")
def test_evaluate_answer_returns_valid_output(mock_call):
    """evaluate_answer returns EvaluationOutput when API succeeds."""
    mock_call.return_value = MOCK_EVALUATION_JSON

    from app.core.evaluator import evaluate_answer
    result = evaluate_answer(
        question=SAMPLE_QUESTION,
        candidate_answer=SAMPLE_ANSWER,
        key_concepts=SAMPLE_CONCEPTS
    )

    assert isinstance(result, EvaluationOutput)
    assert 0 <= result.score <= 10
    mock_call.assert_called_once()


@patch("app.core.evaluator.call_gemini_json")
def test_evaluate_answer_weak_response(mock_call):
    """Weak answer gets a low score."""
    weak_eval = MOCK_EVALUATION_JSON.copy()
    weak_eval["score"] = 1.0
    weak_eval["missing_concepts"] = ["Query", "Key", "Value", "Softmax"]
    mock_call.return_value = weak_eval

    from app.core.evaluator import evaluate_answer
    result = evaluate_answer(
        question=SAMPLE_QUESTION,
        candidate_answer="I don't know.",
        key_concepts=SAMPLE_CONCEPTS
    )

    assert result.score <= 3.0
    assert len(result.missing_concepts) > 0


def test_difficulty_adjuster_increase():
    """High score should increase difficulty."""
    from app.core.difficulty_adjuster import get_next_difficulty
    next_diff, reason = get_next_difficulty("Easy", [9.0, 8.5])
    assert next_diff == "Medium"
    assert "increasing" in reason.lower()


def test_difficulty_adjuster_decrease():
    """Low score should decrease difficulty."""
    from app.core.difficulty_adjuster import get_next_difficulty
    next_diff, reason = get_next_difficulty("Hard", [2.0, 3.0])
    assert next_diff == "Medium"
    assert "decreasing" in reason.lower()


def test_difficulty_adjuster_maintain():
    """Average score should maintain difficulty."""
    from app.core.difficulty_adjuster import get_next_difficulty
    next_diff, reason = get_next_difficulty("Medium", [6.0, 5.5])
    assert next_diff == "Medium"
    assert "maintaining" in reason.lower()


def test_difficulty_adjuster_ceiling():
    """Already at Hard should not go higher."""
    from app.core.difficulty_adjuster import get_next_difficulty
    next_diff, reason = get_next_difficulty("Hard", [9.5, 10.0])
    assert next_diff == "Hard"


def test_difficulty_adjuster_floor():
    """Already at Easy should not go lower."""
    from app.core.difficulty_adjuster import get_next_difficulty
    next_diff, reason = get_next_difficulty("Easy", [1.0, 2.0])
    assert next_diff == "Easy"