def get_evaluation_prompt(
    question: str,
    candidate_answer: str,
    key_concepts: list[str]
) -> str:
    concepts_formatted = "\n".join(f"  - {c}" for c in key_concepts)

    return f"""
You are an expert technical interviewer evaluating a candidate's answer during a job interview.
Be strict but fair. Your evaluation will directly affect hiring decisions.

## Question Asked:
{question}

## Candidate's Answer:
{candidate_answer}

## Key Concepts Expected in a Strong Answer:
{concepts_formatted}

## Scoring Rubric (0 to 10):
- 9-10 : Covers all key concepts accurately with clear explanation and good depth
- 7-8  : Covers most key concepts, minor gaps or slight imprecision
- 5-6  : Covers some key concepts but significant gaps or vague explanations
- 3-4  : Shows basic awareness but major misconceptions or critical concepts missing
- 1-2  : Largely incorrect, irrelevant, or shows fundamental misunderstanding
- 0    : No meaningful response or completely off-topic

## Concept Coverage Rules (VERY IMPORTANT):
- Mark as "covered" if the candidate clearly explains the concept even without using the exact word
- Mark as "partial" if the candidate mentions the concept but without sufficient explanation
- Mark as "missing" ONLY if the concept is truly absent from the answer
- Do NOT mark a concept as missing if the candidate demonstrated understanding of it
- Judge by understanding shown, not by exact keyword matching

## Your Instructions:
1. Read the candidate's answer carefully word by word
2. For each key concept, check if the understanding is demonstrated in the answer
3. Identify specific strengths (what they said correctly)
4. Identify specific weaknesses (what was wrong or imprecise)
5. List ONLY concepts that are truly absent — not partially mentioned ones
6. Write an improved answer a strong candidate would give
7. Write one short interviewer note summarizing overall performance

## Output Format:
Respond ONLY with a valid JSON object. No extra text before or after.
{{
    "score": <float between 0.0 and 10.0>,
    "strengths": ["<specific thing candidate got right>"],
    "weaknesses": ["<specific thing that was wrong or vague>"],
    "missing_concepts": ["<concept truly not mentioned or demonstrated>"],
    "concept_coverage": {{
        "<concept_from_key_concepts>": "covered" | "partial" | "missing"
    }},
    "improved_answer": "<a complete, well-structured answer a strong candidate would give>",
    "interviewer_note": "<one sentence summary of candidate performance>"
}}
"""