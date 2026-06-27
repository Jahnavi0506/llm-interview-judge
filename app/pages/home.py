import streamlit as st
from app.db.crud import create_session

DOMAINS = ["Machine Learning", "Deep Learning", "NLP", "LLMs", "DSA"]
DIFFICULTIES = ["Easy", "Medium", "Hard"]


def show():
    st.title("🎯 LLM Interview Judge")
    st.markdown("### AI-powered technical interview assessment system")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Step 1**\n\nSelect domain, difficulty, and number of questions")
    with col2:
        st.info("**Step 2**\n\nAnswer each generated technical question")
    with col3:
        st.info("**Step 3**\n\nGet your full interview report with scores and feedback")

    st.markdown("---")
    st.subheader("Start a New Interview Session")

    col1, col2 = st.columns(2)
    with col1:
        domain = st.selectbox("Select Domain", DOMAINS)
    with col2:
        difficulty = st.selectbox("Select Difficulty", DIFFICULTIES)

    col3, col4 = st.columns(2)
    with col3:
        total_questions = st.selectbox("Number of Questions", [3, 5, 7, 10], index=1)
    with col4:
        topic = st.text_input(
            "Topic Focus (optional)",
            placeholder="e.g. Attention Mechanism, Binary Trees..."
        )

    st.markdown("")

    if st.button("🚀 Start Interview", use_container_width=True):
        # Create session in DB
        session_id = create_session(domain, difficulty, total_questions)

        # Reset full session state
        # Reset full session state
        for key in ["question", "question_id", "evaluation",
                    "submitted_answer", "current_question_num",
                    "session_scores", "interview_complete",
                    "report", "asked_questions",
                    "selected_confidence", "selected_confidence_score",
                    "self_assessment_gap", "confidence_used",
                    "confidence_score_used", "current_difficulty",
                    "difficulty_history", "follow_up",
                    "follow_up_evaluation"]:
            st.session_state[key] = None

        # Set new session values
        st.session_state.session_id = session_id
        st.session_state.domain = domain
        st.session_state.difficulty = difficulty
        st.session_state.current_difficulty = difficulty  # ← tracks adaptive difficulty
        st.session_state.difficulty_history = []          # ← tracks changes
        st.session_state.topic = topic
        st.session_state.total_questions = total_questions
        st.session_state.current_question_num = 1
        st.session_state.session_scores = []
        st.session_state.interview_complete = False
        st.session_state.asked_questions = []

        st.success(
            f"Session started! **{total_questions} questions** | "
            f"Domain: **{domain}** | Difficulty: **{difficulty}**"
        )
        st.info("👈 Go to **Interview** in the sidebar to begin.")

    # ── Prompt Registry ────────────────────────────────────
    st.markdown("---")
    with st.expander("🔧 Prompt Registry — Current Versions"):
        from app.core.prompt_registry import get_all_versions
        versions = get_all_versions()
        for name, info in versions.items():
            st.markdown(f"**{name}** — v{info['version']}")
            st.caption(info["description"])
            with st.expander(f"Changelog — {name}"):
                for log in info["changelog"]:
                    st.markdown(f"- {log}")
        st.markdown("")
        st.info("Prompt versions are automatically stored with every evaluation for traceability.")