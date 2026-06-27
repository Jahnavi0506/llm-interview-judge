from app.core.gemini_client import call_gemini_json
from app.prompts.question_prompt import get_question_prompt
from app.schemas.question import QuestionOutput
from app.utils.logger import get_logger

logger = get_logger(__name__)


def generate_question(
    domain: str,
    difficulty: str,
    topic: str = "",
    previous_questions: list[str] = []
) -> QuestionOutput:
    logger.info(f"Generating question | domain={domain} | difficulty={difficulty}")

    prompt = get_question_prompt(domain, difficulty, topic, previous_questions)
    raw_json = call_gemini_json(prompt)
    question = QuestionOutput(**raw_json)

    logger.info(f"Question generated | topic_tags={question.topic_tags}")
    return question