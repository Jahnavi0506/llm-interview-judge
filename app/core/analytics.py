"""
Analytics Engine — computes performance metrics across all sessions.
Powers the dashboard page.
"""

from app.db.database import get_connection
import json


def get_score_trend() -> list[dict]:
    """
    Returns average score per session ordered by date.
    Used for the score trend line chart.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            s.id as session_id,
            s.domain,
            s.difficulty,
            s.created_at,
            ROUND(AVG(e.score), 1) as avg_score,
            COUNT(e.id) as total_questions
        FROM sessions s
        JOIN questions q ON q.session_id = s.id
        JOIN evaluations e ON e.question_id = q.id
        GROUP BY s.id
        ORDER BY s.created_at ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_domain_performance() -> list[dict]:
    """
    Returns average score grouped by domain.
    Used for the domain bar chart.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            s.domain,
            ROUND(AVG(e.score), 1) as avg_score,
            COUNT(e.id) as total_questions,
            ROUND(MIN(e.score), 1) as min_score,
            ROUND(MAX(e.score), 1) as max_score
        FROM sessions s
        JOIN questions q ON q.session_id = s.id
        JOIN evaluations e ON e.question_id = q.id
        GROUP BY s.domain
        ORDER BY avg_score DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_missing_concepts_frequency() -> list[dict]:
    """
    Returns most frequently missed concepts across all sessions.
    Used for the concept gap heatmap.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT missing_concepts
        FROM evaluations
        WHERE missing_concepts IS NOT NULL
    """)
    rows = cursor.fetchall()
    conn.close()

    concept_count = {}
    for row in rows:
        try:
            concepts = json.loads(row["missing_concepts"])
            for concept in concepts:
                concept = concept.strip()
                if concept:
                    concept_count[concept] = concept_count.get(concept, 0) + 1
        except Exception:
            continue

    sorted_concepts = sorted(
        concept_count.items(),
        key=lambda x: x[1],
        reverse=True
    )
    return [
        {"concept": c, "frequency": f}
        for c, f in sorted_concepts[:15]  # top 15
    ]


def get_calibration_stats() -> dict:
    """
    Returns overall self-assessment calibration statistics.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            self_assessment_gap,
            confidence,
            confidence_score,
            score
        FROM evaluations
        WHERE self_assessment_gap IS NOT NULL
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {
            "total": 0,
            "well_calibrated": 0,
            "overconfident": 0,
            "underconfident": 0,
            "avg_gap": 0,
            "data": []
        }

    total = len(rows)
    well_calibrated = sum(
        1 for r in rows
        if abs(r["self_assessment_gap"]) <= 2
    )
    overconfident = sum(
        1 for r in rows
        if r["self_assessment_gap"] < -2
    )
    underconfident = sum(
        1 for r in rows
        if r["self_assessment_gap"] > 2
    )
    avg_gap = round(
        sum(r["self_assessment_gap"] for r in rows) / total, 2
    )

    return {
        "total": total,
        "well_calibrated": well_calibrated,
        "overconfident": overconfident,
        "underconfident": underconfident,
        "avg_gap": avg_gap,
        "data": [dict(r) for r in rows]
    }

def get_difficulty_performance() -> list[dict]:
    """
    Returns average score grouped by difficulty level.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            q.difficulty,
            ROUND(AVG(e.score), 1) as avg_score,
            COUNT(e.id) as total_questions
        FROM questions q
        JOIN evaluations e ON e.question_id = q.id
        GROUP BY q.difficulty
        ORDER BY
            CASE q.difficulty
                WHEN 'Easy' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Hard' THEN 3
            END
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_overall_stats() -> dict:
    """
    Returns high-level summary statistics.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM sessions")
    total_sessions = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM evaluations")
    total_evaluations = cursor.fetchone()["count"]

    cursor.execute("SELECT ROUND(AVG(score), 1) as avg FROM evaluations")
    overall_avg = cursor.fetchone()["avg"] or 0

    cursor.execute("SELECT ROUND(MAX(score), 1) as best FROM evaluations")
    best_score = cursor.fetchone()["best"] or 0

    cursor.execute("""
        SELECT s.domain, ROUND(AVG(e.score), 1) as avg
        FROM sessions s
        JOIN questions q ON q.session_id = s.id
        JOIN evaluations e ON e.question_id = q.id
        GROUP BY s.domain
        ORDER BY avg DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    best_domain = dict(row) if row else {"domain": "N/A", "avg": 0}

    cursor.execute("""
        SELECT s.domain, ROUND(AVG(e.score), 1) as avg
        FROM sessions s
        JOIN questions q ON q.session_id = s.id
        JOIN evaluations e ON e.question_id = q.id
        GROUP BY s.domain
        ORDER BY avg ASC
        LIMIT 1
    """)
    row = cursor.fetchone()
    weak_domain = dict(row) if row else {"domain": "N/A", "avg": 0}

    conn.close()

    return {
        "total_sessions": total_sessions,
        "total_evaluations": total_evaluations,
        "overall_avg": overall_avg,
        "best_score": best_score,
        "best_domain": best_domain,
        "weak_domain": weak_domain
    }