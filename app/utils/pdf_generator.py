from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io

from app.config import PDF_FOOTER


# ── Color Palette ──────────────────────────────────────────
COLOR_PRIMARY   = colors.HexColor("#7c3aed")
COLOR_GREEN     = colors.HexColor("#22c55e")
COLOR_RED       = colors.HexColor("#ef4444")
COLOR_AMBER     = colors.HexColor("#f59e0b")
COLOR_BLUE      = colors.HexColor("#3b82f6")
COLOR_BG        = colors.HexColor("#1e1e2e")
COLOR_TEXT      = colors.HexColor("#1e293b")
COLOR_LIGHT     = colors.HexColor("#64748b")
COLOR_WHITE     = colors.white


def score_color(score: float):
    if score >= 8:
        return COLOR_GREEN
    elif score >= 5:
        return COLOR_AMBER
    return COLOR_RED


def recommendation_color(rec: str):
    mapping = {
        "Strong Hire": COLOR_GREEN,
        "Hire": COLOR_GREEN,
        "Maybe": COLOR_AMBER,
        "No Hire": COLOR_RED
    }
    return mapping.get(rec, COLOR_LIGHT)


def build_styles():
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "title",
            fontSize=24,
            fontName="Helvetica-Bold",
            textColor=COLOR_PRIMARY,
            alignment=TA_CENTER,
            spaceAfter=4
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontSize=11,
            fontName="Helvetica",
            textColor=COLOR_LIGHT,
            alignment=TA_CENTER,
            spaceAfter=16
        ),
        "section": ParagraphStyle(
            "section",
            fontSize=14,
            fontName="Helvetica-Bold",
            textColor=COLOR_PRIMARY,
            spaceBefore=14,
            spaceAfter=6
        ),
        "subsection": ParagraphStyle(
            "subsection",
            fontSize=11,
            fontName="Helvetica-Bold",
            textColor=COLOR_TEXT,
            spaceBefore=8,
            spaceAfter=4
        ),
        "body": ParagraphStyle(
            "body",
            fontSize=10,
            fontName="Helvetica",
            textColor=COLOR_TEXT,
            spaceAfter=4,
            leading=14
        ),
        "body_light": ParagraphStyle(
            "body_light",
            fontSize=9,
            fontName="Helvetica",
            textColor=COLOR_LIGHT,
            spaceAfter=4,
            leading=13
        ),
        "question": ParagraphStyle(
            "question",
            fontSize=11,
            fontName="Helvetica-Bold",
            textColor=COLOR_TEXT,
            spaceBefore=6,
            spaceAfter=4,
            leading=15
        ),
        "answer": ParagraphStyle(
            "answer",
            fontSize=10,
            fontName="Helvetica-Oblique",
            textColor=COLOR_LIGHT,
            spaceAfter=4,
            leading=13
        ),
        "improved": ParagraphStyle(
            "improved",
            fontSize=10,
            fontName="Helvetica",
            textColor=COLOR_TEXT,
            spaceAfter=4,
            leading=13
        ),
        "tag": ParagraphStyle(
            "tag",
            fontSize=9,
            fontName="Helvetica",
            textColor=COLOR_WHITE,
            alignment=TA_CENTER
        ),
    }
    return styles


def generate_pdf_report(
    session_info: dict,
    report: dict,
    results: list[dict]
) -> bytes:
    """
    Generates a PDF interview report and returns it as bytes.
    """

    # Safely extract report fields with fallbacks
    avg_score = report.get("avg_score", 0) or 0
    recommendation = report.get("recommendation", "N/A") or "N/A"
    strongest_topic = report.get("strongest_topic", "N/A") or "N/A"
    weakest_topic = report.get("weakest_topic", "N/A") or "N/A"
    overall_feedback = report.get("overall_feedback", "") or ""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    S = build_styles()
    story = []

    # ── Header ─────────────────────────────────────────────
    story.append(Paragraph("LLM Interview Judge", S["title"]))
    story.append(Paragraph("Technical Interview Assessment Report", S["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY))
    story.append(Spacer(1, 10))

    # ── Session Info Table ─────────────────────────────────
    created = str(session_info.get("created_at", ""))[:19]
    domain = session_info.get("domain", "N/A")
    difficulty = session_info.get("difficulty", "N/A")
    total_questions = str(session_info.get("total_questions", len(results)))

    info_data = [
        ["Domain", domain, "Difficulty", difficulty],
        ["Questions", total_questions, "Date", created],
    ]
    info_table = Table(info_data, colWidths=[35*mm, 55*mm, 35*mm, 55*mm])
    info_table.setStyle(TableStyle([
        ("FONTNAME",    (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",    (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",   (0, 0), (-1, -1), COLOR_TEXT),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1),
         [colors.HexColor("#f1f5f9"), colors.HexColor("#f8fafc")]),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING",     (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    # ── Overall Score ──────────────────────────────────────
    story.append(Paragraph("Overall Performance", S["section"]))

    score_data = [
        ["Average Score", "Recommendation"],
        [f"{avg_score}/10", recommendation]
    ]
    score_table = Table(score_data, colWidths=[85*mm, 85*mm])
    score_table.setStyle(TableStyle([
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME",    (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0), 10),
        ("FONTSIZE",    (0, 1), (-1, 1), 20),
        ("TEXTCOLOR",   (0, 0), (-1, 0), COLOR_LIGHT),
        ("TEXTCOLOR",   (0, 1), (0, 1), score_color(avg_score)),
        ("TEXTCOLOR",   (1, 1), (1, 1), recommendation_color(recommendation)),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND",  (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ROWHEIGHTS",  (0, 0), (-1, -1), 28),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 8))

    # Strongest / Weakest
    sw_data = [
        ["Strongest Topic", "Weakest Topic"],
        [strongest_topic, weakest_topic]
    ]
    sw_table = Table(sw_data, colWidths=[85*mm, 85*mm])
    sw_table.setStyle(TableStyle([
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME",    (0, 1), (-1, 1), "Helvetica"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("TEXTCOLOR",   (0, 0), (-1, 0), COLOR_LIGHT),
        ("TEXTCOLOR",   (0, 1), (0, 1), COLOR_GREEN),
        ("TEXTCOLOR",   (1, 1), (1, 1), COLOR_RED),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND",  (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ROWHEIGHTS",  (0, 0), (-1, -1), 24),
    ]))
    story.append(sw_table)
    story.append(Spacer(1, 8))

    if overall_feedback:
        story.append(Paragraph(overall_feedback, S["body_light"]))

    # ── Calibration Summary ────────────────────────────────
    story.append(Paragraph("Self-Assessment Calibration", S["section"]))

    calibrated = sum(
        1 for r in results
        if r.get("self_assessment_gap") is not None
        and abs(r["self_assessment_gap"]) <= 2
    )
    overconfident = sum(
        1 for r in results
        if r.get("self_assessment_gap") is not None
        and r["self_assessment_gap"] < -2
    )
    underconfident = sum(
        1 for r in results
        if r.get("self_assessment_gap") is not None
        and r["self_assessment_gap"] > 2
    )

    cal_data = [
        ["✅ Well Calibrated", "⚠️ Overconfident", "💡 Underconfident"],
        [str(calibrated), str(overconfident), str(underconfident)]
    ]
    cal_table = Table(cal_data, colWidths=[56*mm, 56*mm, 56*mm])
    cal_table.setStyle(TableStyle([
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME",    (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0), 9),
        ("FONTSIZE",    (0, 1), (-1, 1), 16),
        ("TEXTCOLOR",   (0, 0), (-1, 0), COLOR_LIGHT),
        ("TEXTCOLOR",   (0, 1), (0, 1), COLOR_GREEN),
        ("TEXTCOLOR",   (1, 1), (1, 1), COLOR_RED),
        ("TEXTCOLOR",   (2, 1), (2, 1), COLOR_BLUE),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND",  (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ROWHEIGHTS",  (0, 0), (-1, -1), 26),
    ]))
    story.append(cal_table)
    story.append(Spacer(1, 12))

    # ── Per Question Breakdown ─────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY))
    story.append(Paragraph("Question-by-Question Breakdown", S["section"]))

    for r in results:
        story.append(Spacer(1, 6))

        q_num = r.get("question_number", "?")
        q_score = r.get("score", 0) or 0
        q_text = r.get("question_text", "") or ""
        interviewer_note = r.get("interviewer_note", "") or ""
        candidate_answer = r.get("candidate_answer", "") or ""
        improved_answer = r.get("improved_answer", "") or ""
        strengths = r.get("strengths", []) or []
        missing_concepts = r.get("missing_concepts", []) or []
        confidence = r.get("confidence", None)
        gap = r.get("self_assessment_gap", None)

        # Question header
        header_data = [[
            f"Q{q_num}",
            q_text,
            f"{q_score}/10"
        ]]
        header_table = Table(
            header_data,
            colWidths=[12*mm, 138*mm, 20*mm]
        )
        header_table.setStyle(TableStyle([
            ("FONTNAME",    (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 10),
            ("TEXTCOLOR",   (0, 0), (1, 0), COLOR_WHITE),
            ("TEXTCOLOR",   (2, 0), (2, 0), score_color(q_score)),
            ("BACKGROUND",  (0, 0), (1, 0), COLOR_BG),
            ("BACKGROUND",  (2, 0), (2, 0), COLOR_BG),
            ("ALIGN",       (0, 0), (0, 0), "CENTER"),
            ("ALIGN",       (2, 0), (2, 0), "CENTER"),
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING",     (0, 0), (-1, -1), 7),
        ]))
        story.append(header_table)

        # Confidence row
        if confidence and gap is not None:
            if gap < -2:
                cal_text = "⚠️ Overconfident"
            elif gap > 2:
                cal_text = "💡 Underconfident"
            else:
                cal_text = "✅ Well Calibrated"
            story.append(Paragraph(
                f"Confidence: {confidence}  |  {cal_text}  |  Gap: {gap:+.1f} pts",
                S["body_light"]
            ))

        if interviewer_note:
            story.append(Paragraph(
                f"Interviewer Note: {interviewer_note}",
                S["body_light"]
            ))
        story.append(Spacer(1, 4))

        # Strengths and Missing
        strengths_text = "\n".join(f"• {s}" for s in strengths)
        missing_text = "\n".join(f"• {m}" for m in missing_concepts)

        sm_data = [
            ["✅ Strengths", "🔍 Missing Concepts"],
            [
                Paragraph(strengths_text or "None", S["body"]),
                Paragraph(missing_text or "None", S["body"])
            ]
        ]
        sm_table = Table(sm_data, colWidths=[85*mm, 85*mm])
        sm_table.setStyle(TableStyle([
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, 0), 9),
            ("TEXTCOLOR",   (0, 0), (0, 0), COLOR_GREEN),
            ("TEXTCOLOR",   (1, 0), (1, 0), COLOR_RED),
            ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("VALIGN",      (0, 0), (-1, -1), "TOP"),
            ("PADDING",     (0, 0), (-1, -1), 6),
        ]))
        story.append(sm_table)
        story.append(Spacer(1, 4))

        if candidate_answer:
            story.append(Paragraph("Your Answer:", S["subsection"]))
            story.append(Paragraph(candidate_answer, S["answer"]))

        if improved_answer:
            story.append(Paragraph("Improved Answer:", S["subsection"]))
            story.append(Paragraph(improved_answer, S["improved"]))

        story.append(HRFlowable(
            width="100%", thickness=0.5,
            color=colors.HexColor("#e2e8f0")
        ))

    # ── Footer ─────────────────────────────────────────────
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        PDF_FOOTER,
        S["body_light"]
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()