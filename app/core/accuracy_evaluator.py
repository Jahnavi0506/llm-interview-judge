"""
Accuracy Evaluator — compares LLM judge scores against human ground truth.

This measures ACCURACY (is the score correct?) as opposed to
consistency_tester.py which measures CONSISTENCY (is the score repeatable?).

Together these two give a complete reliability picture of the judge:
- Consistency: same answer → same score across runs
- Accuracy: LLM score → matches expert human score
"""

from app.core.evaluator import evaluate_answer
from tests.ground_truth_dataset import GROUND_TRUTH_DATASET
import statistics


def run_accuracy_evaluation(dataset: list = None) -> dict:
    """
    Runs the LLM judge against the ground truth dataset and
    computes accuracy metrics.

    Returns:
        dict with per-item results, mean absolute error, correlation,
        and agreement rate within tolerance
    """
    if dataset is None:
        dataset = GROUND_TRUTH_DATASET

    results = []
    errors = []

    for item in dataset:
        try:
            llm_eval = evaluate_answer(
                question=item["question"],
                candidate_answer=item["candidate_answer"],
                key_concepts=item["key_concepts"]
            )

            llm_score = llm_eval.score
            human_score = item["human_score"]
            error = round(llm_score - human_score, 2)
            abs_error = abs(error)

            results.append({
                "id": item["id"],
                "domain": item["domain"],
                "question": item["question"],
                "candidate_answer": item["candidate_answer"],
                "human_score": human_score,
                "human_reasoning": item["human_reasoning"],
                "llm_score": llm_score,
                "llm_note": llm_eval.interviewer_note,
                "error": error,
                "abs_error": abs_error,
                "within_tolerance": abs_error <= 1.5
            })
            errors.append(abs_error)

        except Exception as e:
            results.append({
                "id": item["id"],
                "domain": item["domain"],
                "question": item["question"],
                "candidate_answer": item["candidate_answer"],
                "human_score": item["human_score"],
                "llm_score": None,
                "error": None,
                "abs_error": None,
                "within_tolerance": False,
                "failed": True,
                "error_message": str(e)
            })

    valid_errors = [e for e in errors if e is not None]

    mean_absolute_error = round(statistics.mean(valid_errors), 2) if valid_errors else None
    agreement_count = sum(1 for r in results if r.get("within_tolerance"))
    agreement_rate = round(agreement_count / len(results) * 100, 1) if results else 0

    # Correlation between human and LLM scores
    human_scores = [r["human_score"] for r in results if r.get("llm_score") is not None]
    llm_scores = [r["llm_score"] for r in results if r.get("llm_score") is not None]

    correlation = None
    if len(human_scores) >= 2:
        try:
            correlation = round(
                statistics.correlation(human_scores, llm_scores), 3
            )
        except Exception:
            correlation = None

    return {
        "results": results,
        "total_items": len(results),
        "mean_absolute_error": mean_absolute_error,
        "agreement_rate": agreement_rate,
        "agreement_count": agreement_count,
        "correlation": correlation,
        "tolerance": 1.5
    }


def get_accuracy_label(mae: float) -> tuple[str, str]:
    """Returns a label and description based on mean absolute error."""
    if mae is None:
        return "⚪ No Data", "Run the evaluation to see results"
    elif mae <= 1.0:
        return "🟢 Highly Accurate", "LLM judge closely matches expert human scoring"
    elif mae <= 2.0:
        return "🟡 Reasonably Accurate", "LLM judge is generally aligned with human scoring, minor deviations"
    else:
        return "🔴 Needs Improvement", "LLM judge deviates significantly from human scoring — prompt may need refinement"