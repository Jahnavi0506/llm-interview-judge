import streamlit as st
from app.core.evaluator import evaluate_answer
from app.core.report_generator import generate_overall_report
from app.db.crud import (
    save_evaluation, get_session_results,
    save_report, get_report, complete_session
)
from app.utils.pdf_generator import generate_pdf_report
from app.db.crud import get_all_sessions

def score_color(score: float) -> str:
    if score >= 8:
        return "#22c55e"
    elif score >= 5:
        return "#f59e0b"
    else:
        return "#ef4444"


def recommendation_color(rec: str) -> str:
    colors = {
        "Strong Hire": "#22c55e",
        "Hire": "#84cc16",
        "Maybe": "#f59e0b",
        "No Hire": "#ef4444"
    }
    return colors.get(rec, "#94a3b8")


def show():
    st.title("📊 Evaluation")
    st.markdown("---")

    if "session_id" not in st.session_state or st.session_state.session_id is None:
        st.warning("Please start a session from the **Home** page first.")
        return

    # ── OVERALL REPORT (interview complete) ───────────────
    if st.session_state.get("interview_complete"):
        show_overall_report()
        return

    # ── SINGLE QUESTION EVALUATION ────────────────────────
    if not st.session_state.get("submitted_answer"):
        st.warning("Please submit an answer from the **Interview** page first.")
        return

    # Run evaluation if not done
    if st.session_state.get("evaluation") is None:
        with st.spinner("Evaluating your answer..."):
            try:
                evaluation = evaluate_answer(
                    question=st.session_state.question.question,
                    candidate_answer=st.session_state.submitted_answer,
                    key_concepts=st.session_state.question.key_concepts
                )

                # Calculate self assessment gap
                confidence = st.session_state.get("selected_confidence", "😐 Somewhat Sure")
                confidence_score = st.session_state.get("selected_confidence_score", 5.0)
                gap = round(evaluation.score - confidence_score, 1)

                save_evaluation(
                    st.session_state.question_id,
                    st.session_state.submitted_answer,
                    evaluation,
                    confidence=confidence,
                    confidence_score=confidence_score,
                    self_assessment_gap=gap
                )
                st.session_state.evaluation = evaluation
                st.session_state.self_assessment_gap = gap
                st.session_state.confidence_used = confidence
                st.session_state.confidence_score_used = confidence_score

                # Track score
                if st.session_state.session_scores is None:
                    st.session_state.session_scores = []
                st.session_state.session_scores.append(evaluation.score)

            except Exception as e:
                st.error(f"Evaluation failed: {str(e)}")
                return

    evaluation = st.session_state.evaluation
    current = st.session_state.current_question_num
    total = st.session_state.total_questions

    # ── Progress ───────────────────────────────────────────
    st.markdown(f"### Question {current} of {total} — Result")
    st.progress(current / total)
    st.markdown("---")

    # ── Score ──────────────────────────────────────────────
    color = score_color(evaluation.score)
    st.markdown(f"""
    <div style="text-align:center; padding:30px; background:#1e1e2e;
                border-radius:12px; margin-bottom:24px;">
        <div style="font-size:64px; font-weight:bold; color:{color};">
            {evaluation.score}/10
        </div>
        <div style="color:#94a3b8; font-size:16px; margin-top:8px;">
            {evaluation.interviewer_note}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Self Assessment Gap ────────────────────────────────
    confidence = st.session_state.get("confidence_used", "😐 Somewhat Sure")
    confidence_score = st.session_state.get("confidence_score_used", 5.0)
    gap = st.session_state.get("self_assessment_gap", 0)

    if gap < -2:
        gap_color = "#ef4444"
        gap_label = "⚠️ Overconfident"
        gap_msg = f"You rated yourself {confidence} but scored {evaluation.score}/10. You may have knowledge gaps you are unaware of."
    elif gap > 2:
        gap_color = "#3b82f6"
        gap_label = "💡 Underconfident"
        gap_msg = f"You rated yourself {confidence} but actually scored {evaluation.score}/10. Trust yourself more!"
    else:
        gap_color = "#22c55e"
        gap_label = "✅ Well Calibrated"
        gap_msg = "Your confidence matched your actual performance well."

    st.markdown(f"""
    <div style="background:#1e1e2e; padding:20px; border-radius:8px;
                border-left:4px solid {gap_color}; margin-bottom:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="color:#94a3b8; font-size:12px;">YOUR CONFIDENCE</div>
                <div style="color:#e2e8f0; font-size:16px; font-weight:bold;">{confidence}</div>
            </div>
            <div style="text-align:center;">
                <div style="color:{gap_color}; font-size:20px; font-weight:bold;">{gap_label}</div>
                <div style="color:#94a3b8; font-size:12px;">Gap: {gap:+.1f} points</div>
            </div>
            <div style="text-align:right;">
                <div style="color:#94a3b8; font-size:12px;">ACTUAL SCORE</div>
                <div style="color:{score_color(evaluation.score)}; font-size:16px; font-weight:bold;">{evaluation.score}/10</div>
            </div>
        </div>
        <div style="color:#94a3b8; font-size:13px; margin-top:12px;">{gap_msg}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Concept Coverage ───────────────────────────────────
    st.subheader("Concept Coverage")
    cols = st.columns(len(evaluation.concept_coverage))
    status_icons = {"covered": "🟢", "partial": "🟡", "missing": "🔴"}
    for col, (concept, status) in zip(cols, evaluation.concept_coverage.items()):
        with col:
            st.markdown(f"""
            <div style="text-align:center; padding:12px; background:#1e1e2e; border-radius:8px;">
                <div style="font-size:24px;">{status_icons.get(status, '⚪')}</div>
                <div style="font-size:12px; color:#e2e8f0; margin-top:4px;">{concept}</div>
                <div style="font-size:11px; color:#94a3b8;">{status}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Strengths and Weaknesses ───────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✅ Strengths")
        if evaluation.strengths:
            for s in evaluation.strengths:
                st.success(s)
        else:
            st.info("No notable strengths identified.")
    with col2:
        st.subheader("❌ Weaknesses")
        if evaluation.weaknesses:
            for w in evaluation.weaknesses:
                st.error(w)
        else:
            st.info("No weaknesses identified.")

    st.markdown("---")

    # ── Missing Concepts ───────────────────────────────────
    if evaluation.missing_concepts:
        st.subheader("🔍 Missing Concepts")
        cols = st.columns(min(len(evaluation.missing_concepts), 4))
        for i, concept in enumerate(evaluation.missing_concepts):
            with cols[i % 4]:
                st.markdown(f"""
                <div style="background:#1e1e2e; border:1px solid #ef4444;
                            padding:8px 12px; border-radius:6px;
                            color:#ef4444; text-align:center; margin-bottom:8px;">
                    {concept}
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Your Answer vs Improved Answer ────────────────────
    st.subheader("📝 Your Answer")
    st.markdown(f"""
    <div style="background:#1e1e2e; padding:16px; border-radius:8px;
                border-left:4px solid #94a3b8; color:#e2e8f0;">
        {st.session_state.submitted_answer}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.subheader("💡 Improved Answer")
    st.markdown(f"""
    <div style="background:#1e1e2e; padding:16px; border-radius:8px;
                border-left:4px solid #22c55e; color:#e2e8f0;">
        {evaluation.improved_answer}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Navigation ─────────────────────────────────────────
    if current < total:
        if st.button("➡️ Next Question", use_container_width=True, type="primary"):
            st.session_state.current_question_num += 1
            st.session_state.question = None
            st.session_state.question_id = None
            st.session_state.evaluation = None
            st.session_state.submitted_answer = None
            st.session_state.selected_confidence = None
            st.session_state.selected_confidence_score = None
            st.session_state.self_assessment_gap = None
            st.session_state.confidence_used = None
            st.session_state.confidence_score_used = None
            st.info("👈 Go to **Interview** for your next question.")
    else:
        if st.button("🏁 Finish Interview & See Report", use_container_width=True, type="primary"):
            st.session_state.interview_complete = True
            st.rerun()


def show_overall_report():
    """Shows the full interview report after all questions are done."""

    st.subheader("🏁 Interview Complete!")

    # Generate report if not already done
    existing_report = get_report(st.session_state.session_id)

    if existing_report is None:
        with st.spinner("Generating your overall interview report..."):
            try:
                results = get_session_results(st.session_state.session_id)
                # ── PDF Download ───────────────────────────────────────
                st.markdown("---")
                st.subheader("📄 Download Report")

                # Get session info for PDF
                all_sessions = get_all_sessions()
                session_info = next(
                (s for s in all_sessions if s["id"] == st.session_state.session_id),
                {"domain": st.session_state.domain,
                "difficulty": st.session_state.difficulty,
                "total_questions": st.session_state.total_questions,
                 "created_at": ""}
                )

                try:
                    pdf_bytes = generate_pdf_report(session_info, report, results)
                    st.download_button(
                    label="⬇️ Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"interview_report_session_{st.session_state.session_id}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                except Exception as e:
                    st.error(f"PDF generation failed: {str(e)}")
                report = generate_overall_report(results)
                save_report(st.session_state.session_id, report)
                complete_session(st.session_state.session_id)
                existing_report = report
            except Exception as e:
                st.error(f"Report generation failed: {str(e)}")
                return

    report = existing_report
    results = get_session_results(st.session_state.session_id)

    # ── Overall Score ──────────────────────────────────────
    rec_color = recommendation_color(report["recommendation"])
    st.markdown(f"""
    <div style="text-align:center; padding:40px; background:#1e1e2e;
                border-radius:12px; margin-bottom:24px;">
        <div style="font-size:72px; font-weight:bold; color:{score_color(report['avg_score'])};">
            {report['avg_score']}/10
        </div>
        <div style="font-size:24px; font-weight:bold; color:{rec_color}; margin-top:12px;">
            {report['recommendation']}
        </div>
        <div style="color:#94a3b8; font-size:15px; margin-top:12px; max-width:600px;
                    margin-left:auto; margin-right:auto;">
            {report['overall_feedback']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Strongest and Weakest ──────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background:#1e1e2e; padding:20px; border-radius:8px;
                    border-left:4px solid #22c55e; text-align:center;">
            <div style="color:#94a3b8; font-size:12px;">STRONGEST TOPIC</div>
            <div style="color:#22c55e; font-size:18px; font-weight:bold; margin-top:8px;">
                {report['strongest_topic']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background:#1e1e2e; padding:20px; border-radius:8px;
                    border-left:4px solid #ef4444; text-align:center;">
            <div style="color:#94a3b8; font-size:12px;">WEAKEST TOPIC</div>
            <div style="color:#ef4444; font-size:18px; font-weight:bold; margin-top:8px;">
                {report['weakest_topic']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Calibration Summary ────────────────────────────────
    st.markdown("---")
    st.subheader("🎯 Self-Assessment Calibration")

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

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Well Calibrated", f"{calibrated} questions")
    with col2:
        st.metric("⚠️ Overconfident", f"{overconfident} questions")
    with col3:
        st.metric("💡 Underconfident", f"{underconfident} questions")

    # ── Per Question Breakdown ─────────────────────────────
    st.markdown("---")
    st.subheader("📋 Question-by-Question Breakdown")

    for r in results:
        color = score_color(r["score"])
        with st.expander(
            f"Q{r['question_number']}: {r['question_text'][:80]}... — Score: {r['score']}/10"
        ):
            st.markdown(f"""
            <div style="background:#1e1e2e; padding:16px; border-radius:8px; margin-bottom:12px;">
                <span style="color:{color}; font-size:24px; font-weight:bold;">{r['score']}/10</span>
                <span style="color:#94a3b8; margin-left:16px;">{r['interviewer_note']}</span>
            </div>
            """, unsafe_allow_html=True)

            # Confidence gap per question
            if r.get("confidence") and r.get("self_assessment_gap") is not None:
                gap = r["self_assessment_gap"]
                if gap < -2:
                    glabel = "⚠️ Overconfident"
                    gcolor = "#ef4444"
                elif gap > 2:
                    glabel = "💡 Underconfident"
                    gcolor = "#3b82f6"
                else:
                    glabel = "✅ Well Calibrated"
                    gcolor = "#22c55e"
                st.markdown(f"""
                <div style="color:{gcolor}; font-size:13px; margin-bottom:12px;">
                    Confidence: {r['confidence']} → {glabel} (Gap: {gap:+.1f})
                </div>
                """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Strengths**")
                for s in r["strengths"]:
                    st.success(s)
            with col2:
                st.markdown("**❌ Missing Concepts**")
                for m in r["missing_concepts"]:
                    st.error(m)

            st.markdown("**💡 Improved Answer**")
            st.markdown(f"""
            <div style="background:#1e1e2e; padding:12px; border-radius:8px;
                        border-left:3px solid #22c55e; color:#e2e8f0;">
                {r['improved_answer']}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Start New Interview ────────────────────────────────
    if st.button("🔁 Start New Interview", use_container_width=True, type="primary"):
        for key in ["session_id", "domain", "difficulty", "topic",
                    "total_questions", "question", "question_id",
                    "evaluation", "submitted_answer", "current_question_num",
                    "session_scores", "interview_complete", "report",
                    "asked_questions", "selected_confidence",
                    "selected_confidence_score", "self_assessment_gap",
                    "confidence_used", "confidence_score_used"]:
            st.session_state[key] = None
        st.info("👈 Go to **Home** to start a new session.")