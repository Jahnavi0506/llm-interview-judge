"""
Adaptive Difficulty Engine

Adjusts question difficulty based on recent performance.
Mirrors how a real interviewer naturally adjusts their questions.
"""

DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]


def get_next_difficulty(
    current_difficulty: str,
    recent_scores: list[float]
) -> tuple[str, str]:
    """
    Determines next question difficulty based on recent scores.

    Args:
        current_difficulty: Current difficulty level
        recent_scores: List of scores from recent questions

    Returns:
        Tuple of (next_difficulty, reason)
    """

    if not recent_scores:
        return current_difficulty, "Starting difficulty maintained"

    # Use last 1-2 scores to decide
    last_score = recent_scores[-1]
    avg_recent = sum(recent_scores[-2:]) / len(recent_scores[-2:])

    current_idx = DIFFICULTY_LEVELS.index(current_difficulty)

    # Strong performance → increase difficulty
    if last_score >= 8.0 and avg_recent >= 7.5:
        next_idx = min(current_idx + 1, len(DIFFICULTY_LEVELS) - 1)
        if next_idx == current_idx:
            reason = "Already at maximum difficulty — maintaining Hard"
        else:
            reason = f"Score {last_score}/10 — increasing difficulty"
        return DIFFICULTY_LEVELS[next_idx], reason

    # Weak performance → decrease difficulty
    elif last_score <= 4.0 and avg_recent <= 4.5:
        next_idx = max(current_idx - 1, 0)
        if next_idx == current_idx:
            reason = "Already at minimum difficulty — maintaining Easy"
        else:
            reason = f"Score {last_score}/10 — decreasing difficulty"
        return DIFFICULTY_LEVELS[next_idx], reason

    # Average performance → maintain difficulty
    else:
        reason = f"Score {last_score}/10 — maintaining {current_difficulty}"
        return current_difficulty, reason


def get_difficulty_trend(scores: list[float], difficulties: list[str]) -> list[dict]:
    """
    Returns a history of difficulty adjustments across the session.
    Used for the overall report and analytics.
    """
    trend = []
    for i, (score, difficulty) in enumerate(zip(scores, difficulties), 1):
        trend.append({
            "question": i,
            "score": score,
            "difficulty": difficulty,
            "color": "#22c55e" if score >= 8 else "#f59e0b" if score >= 5 else "#ef4444"
        })
    return trend