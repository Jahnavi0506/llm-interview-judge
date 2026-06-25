from app.core.gemini_client import call_gemini_json
from app.prompts.evaluation_prompt import get_evaluation_prompt
from app.schemas.evaluation import EvaluationOutput


def evaluate_answer(
    question: str,
    candidate_answer: str,
    key_concepts: list[str]
) -> EvaluationOutput:
    """
    Evaluates a candidate's answer using Gemini as a judge.

    Args:
        question: The interview question that was asked
        candidate_answer: What the candidate wrote
        key_concepts: Expected concepts (from QuestionOutput.key_concepts)

    Returns:
        EvaluationOutput — validated Pydantic object
    """

    # Step 1: Build the evaluation prompt
    prompt = get_evaluation_prompt(question, candidate_answer, key_concepts)

    # Step 2: Call Gemini and get JSON back
    raw_json = call_gemini_json(prompt)

    # Step 3: Validate through Pydantic schema
    evaluation = EvaluationOutput(**raw_json)

    return evaluation