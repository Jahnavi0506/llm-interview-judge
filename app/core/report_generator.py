from app.core.gemini_client import call_gemini_json


def generate_overall_report(results: list[dict]) -> dict:
    """
    Takes all question+evaluation results from a session
    and generates an overall interview performance report.
    """

    # Build summary for the prompt
    summary_lines = []
    for i, r in enumerate(results, 1):
        summary_lines.append(
            f"Q{i}: {r['question_text']}\n"
            f"Score: {r['score']}/10\n"
            f"Missing: {', '.join(r['missing_concepts']) if r['missing_concepts'] else 'None'}\n"
            f"Interviewer Note: {r['interviewer_note']}"
        )

    summary = "\n\n".join(summary_lines)
    avg_score = round(sum(r["score"] for r in results) / len(results), 1)

    prompt = f"""
You are a senior technical interviewer summarizing a candidate's overall interview performance.

## Interview Summary:
{summary}

## Average Score: {avg_score}/10

## Your Task:
Based on the performance across all questions, provide an overall assessment.

Respond ONLY with a valid JSON object:
{{
    "avg_score": {avg_score},
    "strongest_topic": "<topic or concept the candidate handled best>",
    "weakest_topic": "<topic or concept the candidate struggled with most>",
    "overall_feedback": "<3-4 sentences summarizing overall performance, patterns observed, and key areas to improve>",
    "recommendation": "Strong Hire" | "Hire" | "Maybe" | "No Hire"
}}
"""

    return call_gemini_json(prompt)