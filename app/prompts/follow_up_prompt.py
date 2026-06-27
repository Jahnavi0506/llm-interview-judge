def get_follow_up_prompt(
    original_question: str,
    candidate_answer: str,
    missing_concepts: list[str],
    score: float
) -> str:
    """
    Builds a prompt to generate a targeted follow-up question
    based on what the candidate missed.
    """

    missing_formatted = "\n".join(f"  - {c}" for c in missing_concepts)

    return f"""
You are a senior technical interviewer conducting a live interview.
The candidate just answered a question but missed some key concepts.
Your job is to ask ONE targeted follow-up question to probe their understanding further.

## Original Question:
{original_question}

## Candidate's Answer:
{candidate_answer}

## Score Received: {score}/10

## Concepts the Candidate Missed:
{missing_formatted}

## Rules for the Follow-up Question:
1. Must directly probe one or more of the missing concepts
2. Must reference what the candidate said to feel natural and conversational
3. Must be a single focused question — not multiple questions
4. Should feel like a real interviewer naturally probing deeper
5. If score >= 7, make it a deeper/harder extension question
6. If score < 7, make it a clarifying question about what was missed

## Output Format:
Respond ONLY with a valid JSON object. No extra text before or after.
{{
    "follow_up_question": "<the follow-up question>",
    "targets": ["<concept it targets>"],
    "intent": "<why this follow-up was chosen>"
}}
"""
