import sqlite3
import os

DB_PATH = os.path.join("data", "interview_judge.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            domain          TEXT NOT NULL,
            difficulty      TEXT NOT NULL,
            total_questions INTEGER DEFAULT 5,
            status          TEXT DEFAULT 'in_progress',
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS questions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      INTEGER REFERENCES sessions(id),
            question_text   TEXT NOT NULL,
            topic_tags      TEXT,
            key_concepts    TEXT,
            difficulty      TEXT,
            question_number INTEGER DEFAULT 1,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS evaluations (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id         INTEGER REFERENCES questions(id),
            candidate_answer    TEXT NOT NULL,
            score               REAL NOT NULL,
            confidence          TEXT,
            confidence_score    REAL,
            self_assessment_gap REAL,
            missing_concepts    TEXT,
            strengths           TEXT,
            weaknesses          TEXT,
            concept_coverage    TEXT,
            improved_answer     TEXT,
            interviewer_note    TEXT,
            evaluated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS interview_reports (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id          INTEGER REFERENCES sessions(id),
            avg_score           REAL,
            strongest_topic     TEXT,
            weakest_topic       TEXT,
            overall_feedback    TEXT,
            recommendation      TEXT,
            created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()