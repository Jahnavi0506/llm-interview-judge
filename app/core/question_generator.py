from app.core.gemini_client import call_gemini_json
from app.prompts.question_prompt import get_question_prompt
from app.schemas.question import QuestionOutput


def generate_question(
    domain: str,
    difficulty: str,
    topic: str = "",
    previous_questions: list[str] = []
) -> QuestionOutput:
    """
    Generates a technical interview question using Groq.
    Passes previously asked questions to avoid repetition.
    """
    prompt = get_question_prompt(domain, difficulty, topic, previous_questions)
    raw_json = call_gemini_json(prompt)
    return QuestionOutput(**raw_json)