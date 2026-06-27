from app.core.gemini_client import call_gemini_json
from app.prompts.follow_up_prompt import get_follow_up_prompt
from pydantic import BaseModel
from typing import List


class FollowUpOutput(BaseModel):
    follow_up_question: str
    targets: List[str]
    intent: str


def generate_follow_up(
    original_question: str,
    candidate_answer: str,
    missing_concepts: list[str],
    score: float
) -> FollowUpOutput:
    """
    Generates a targeted follow-up question based on candidate gaps.

    Args:
        original_question: The original interview question
        candidate_answer: What the candidate answered
        missing_concepts: Concepts they missed (from EvaluationOutput)
        score: Their score (affects follow-up difficulty)

    Returns:
        FollowUpOutput with follow_up_question, targets, intent
    """

    # If nothing was missed and score is high, generate extension question
    if not missing_concepts and score >= 7:
        missing_concepts = ["deeper understanding", "edge cases", "practical application"]

    prompt = get_follow_up_prompt(
        original_question=original_question,
        candidate_answer=candidate_answer,
        missing_concepts=missing_concepts,
        score=score
    )

    raw_json = call_gemini_json(prompt)
    return FollowUpOutput(**raw_json)