import json
import sqlite3
from app.db.database import get_connection
from app.schemas.question import QuestionOutput
from app.schemas.evaluation import EvaluationOutput


# ── Sessions ──────────────────────────────────────────────

def create_session(domain: str, difficulty: str, total_questions: int = 5) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (domain, difficulty, total_questions) VALUES (?, ?, ?)",
        (domain, difficulty, total_questions)
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def complete_session(session_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE sessions SET status = 'completed' WHERE id = ?",
        (session_id,)
    )
    conn.commit()
    conn.close()


def get_all_sessions() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            s.id,
            s.domain,
            s.difficulty,
            s.total_questions,
            s.status,
            s.created_at,
            COUNT(e.id) as completed_questions,
            ROUND(AVG(e.score), 1) as avg_score
        FROM sessions s
        LEFT JOIN questions q ON q.session_id = s.id
        LEFT JOIN evaluations e ON e.question_id = q.id
        GROUP BY s.id
        ORDER BY s.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ── Questions ─────────────────────────────────────────────

def save_question(session_id: int, question: QuestionOutput, question_number: int = 1) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO questions
           (session_id, question_text, topic_tags, key_concepts, difficulty, question_number)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            session_id,
            question.question,
            json.dumps(question.topic_tags),
            json.dumps(question.key_concepts),
            question.difficulty,
            question_number
        )
    )
    question_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return question_id


# ── Evaluations ───────────────────────────────────────────

def save_evaluation(
    question_id: int,
    candidate_answer: str,
    evaluation: EvaluationOutput,
    confidence: str = None,
    confidence_score: float = None,
    self_assessment_gap: float = None
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO evaluations
           (question_id, candidate_answer, score, confidence, confidence_score,
            self_assessment_gap, missing_concepts, strengths, weaknesses,
            concept_coverage, improved_answer, interviewer_note)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            question_id,
            candidate_answer,
            evaluation.score,
            confidence,
            confidence_score,
            self_assessment_gap,
            json.dumps(evaluation.missing_concepts),
            json.dumps(evaluation.strengths),
            json.dumps(evaluation.weaknesses),
            json.dumps(evaluation.concept_coverage),
            evaluation.improved_answer,
            evaluation.interviewer_note
        )
    )
    evaluation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return evaluation_id


def get_session_results(session_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            q.question_text,
            q.key_concepts,
            q.difficulty,
            q.question_number,
            e.candidate_answer,
            e.score,
            e.confidence,
            e.confidence_score,
            e.self_assessment_gap,
            e.strengths,
            e.weaknesses,
            e.missing_concepts,
            e.concept_coverage,
            e.improved_answer,
            e.interviewer_note,
            e.evaluated_at
        FROM questions q
        JOIN evaluations e ON e.question_id = q.id
        WHERE q.session_id = ?
        ORDER BY q.question_number ASC
    """, (session_id,))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        r = dict(row)
        r["key_concepts"] = json.loads(r["key_concepts"])
        r["strengths"] = json.loads(r["strengths"])
        r["weaknesses"] = json.loads(r["weaknesses"])
        r["missing_concepts"] = json.loads(r["missing_concepts"])
        r["concept_coverage"] = json.loads(r["concept_coverage"])
        results.append(r)

    return results


# ── Interview Reports ─────────────────────────────────────

def save_report(session_id: int, report: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO interview_reports
           (session_id, avg_score, strongest_topic, weakest_topic,
            overall_feedback, recommendation)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            session_id,
            report["avg_score"],
            report["strongest_topic"],
            report["weakest_topic"],
            report["overall_feedback"],
            report["recommendation"]
        )
    )
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return report_id


def get_report(session_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM interview_reports WHERE session_id = ?",
        (session_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None