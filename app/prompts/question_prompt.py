def get_question_prompt(domain: str, difficulty: str, topic: str = "", previous_questions: list[str] = []) -> str:

    topic_line = f"- Topic Focus: {topic}" if topic else "- Topic Focus: Any relevant topic within the domain"

    # Build exclusion block if there are previous questions
    if previous_questions:
        exclusion = "## Already Asked Questions (DO NOT repeat or ask similar questions):\n"
        exclusion += "\n".join(f"  - {q}" for q in previous_questions)
    else:
        exclusion = ""

    return f"""
You are a senior technical interviewer at a top AI/ML company with 10+ years of experience.
Your job is to generate a single high-quality technical interview question.

## Interview Configuration:
- Domain: {domain}
- Difficulty: {difficulty}
{topic_line}

{exclusion}

## Rules for the question:
1. Must be open-ended — not a yes/no or multiple choice question
2. Must test conceptual understanding, not just memorization
3. Must be answerable in 3-6 sentences by a strong candidate
4. Should expose depth of knowledge when answered well
5. Must be DIFFERENT from any already asked questions listed above
6. Cover a DIFFERENT concept or topic than previously asked questions

## Difficulty Guidelines:
- Easy: Foundational concepts, definitions with explanation
- Medium: How things work internally, tradeoffs, comparisons
- Hard: Edge cases, system design aspects, deep internals

## Output Format:
Respond ONLY with a valid JSON object. No extra text before or after.
{{
    "question": "<the interview question>",
    "topic_tags": ["<tag1>", "<tag2>"],
    "key_concepts": ["<concept1>", "<concept2>", "<concept3>", "<concept4>"],
    "difficulty": "{difficulty}"
}}
"""