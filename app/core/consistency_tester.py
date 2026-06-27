"""
Consistency Tester — evaluates the same answer multiple times
and measures score variance across runs.

Why this matters:
- LLMs are non-deterministic — same prompt can give different outputs
- In a production judge system, high variance = unreliable scores
- This test measures how consistent our evaluation prompt is
- Low variance (< 1.5 points) = reliable judge
"""

import statistics
from app.core.evaluator import evaluate_answer


def run_consistency_test(
    question: str,
    candidate_answer: str,
    key_concepts: list[str],
    runs: int = 3
) -> dict:
    """
    Runs the same evaluation N times and measures consistency.

    Args:
        question: The interview question
        candidate_answer: The answer to evaluate
        key_concepts: Expected concepts
        runs: Number of times to evaluate (default 3)

    Returns:
        dict with scores, mean, std_dev, variance_label, and all evaluations
    """
    scores = []
    evaluations = []

    for i in range(runs):
        evaluation = evaluate_answer(question, candidate_answer, key_concepts)
        scores.append(evaluation.score)
        evaluations.append(evaluation)

    mean_score = round(statistics.mean(scores), 2)
    std_dev = round(statistics.stdev(scores) if len(scores) > 1 else 0.0, 2)
    score_range = round(max(scores) - min(scores), 2)

    if std_dev <= 0.5:
        variance_label = "🟢 Highly Consistent"
        variance_desc = "Scores varied by less than 0.5 points — excellent judge reliability"
    elif std_dev <= 1.5:
        variance_label = "🟡 Moderately Consistent"
        variance_desc = "Scores varied by up to 1.5 points — acceptable for most use cases"
    else:
        variance_label = "🔴 High Variance"
        variance_desc = "Scores varied significantly — prompt may need refinement"

    return {
        "scores": scores,
        "mean_score": mean_score,
        "std_dev": std_dev,
        "score_range": score_range,
        "variance_label": variance_label,
        "variance_desc": variance_desc,
        "runs": runs,
        "evaluations": evaluations
    }