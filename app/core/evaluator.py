from app.core.gemini_client import call_gemini_json
from app.prompts.evaluation_prompt import get_evaluation_prompt
from app.schemas.evaluation import EvaluationOutput
from app.utils.logger import get_logger

logger = get_logger(__name__)


def evaluate_answer(
    question: str,
    candidate_answer: str,
    key_concepts: list[str]
) -> EvaluationOutput:
    logger.info(
        f"Evaluating answer | "
        f"answer_length={len(candidate_answer)} | "
        f"concepts={key_concepts}"
    )

    prompt = get_evaluation_prompt(question, candidate_answer, key_concepts)
    raw_json = call_gemini_json(prompt)
    evaluation = EvaluationOutput(**raw_json)

    logger.info(
        f"Evaluation complete | "
        f"score={evaluation.score} | "
        f"missing={evaluation.missing_concepts}"
    )
    return evaluation