import streamlit as st
from app.db.crud import get_all_sessions, get_session_results, get_report
from app.utils.pdf_generator import generate_pdf_report


def score_badge(score):
    if score is None:
        return "⚪ N/A"
    elif score >= 8:
        return f"🟢 {score}/10"
    elif score >= 5:
        return f"🟡 {score}/10"
    else:
        return f"🔴 {score}/10"


def show():
    st.title("🕘 Session History")
    st.markdown("---")

    sessions = get_all_sessions()

    if not sessions:
        st.info("No sessions yet. Start an interview from the Home page!")
        return

    st.markdown(f"**Total Sessions:** {len(sessions)}")
    st.markdown("---")

    for session in sessions:
        status_icon = "✅" if session["status"] == "completed" else "🔄"

        with st.expander(
            f"{status_icon} Session #{session['id']} — "
            f"{session['domain']} | {session['difficulty']} | "
            f"Avg Score: {score_badge(session['avg_score'])} | "
            f"{str(session['created_at'])[:19]}"
        ):
            results = get_session_results(session["id"])
            report = get_report(session["id"])

            if not results:
                st.info("No completed evaluations in this session.")
                continue

            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Questions Answered", session["completed_questions"])
            with col2:
                st.metric("Average Score", f"{session['avg_score']}/10" if session['avg_score'] else "N/A")
            with col3:
                if report:
                    st.metric("Recommendation", report["recommendation"])

            st.markdown("---")

            # Per question summary
            for r in results:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Q{r['question_number']}: {r['question_text'][:100]}...**")
                    if r.get("confidence"):
                        st.caption(f"Confidence: {r['confidence']}")
                with col2:
                    st.metric("Score", f"{r['score']}/10")
                st.markdown(f"*{r['interviewer_note']}*")
                st.markdown("---")

            # PDF download for completed sessions
            if report:
                try:
                    pdf_bytes = generate_pdf_report(session, report, results)
                    st.download_button(
                        label=f"⬇️ Download PDF — Session #{session['id']}",
                        data=pdf_bytes,
                        file_name=f"interview_report_session_{session['id']}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"pdf_{session['id']}"
                    )
                except Exception as e:
                    st.error(f"PDF generation failed: {str(e)}")