import streamlit as st
from app.core.question_generator import generate_question
from app.db.crud import save_question


def show():
    st.title("📝 Interview")
    st.markdown("---")

    if "session_id" not in st.session_state or st.session_state.session_id is None:
        st.warning("Please start a session from the **Home** page first.")
        return

    if st.session_state.get("interview_complete"):
        st.success("✅ Interview complete! Go to **Evaluation** to see your full report.")
        return

    # If already submitted and evaluated, show next button
    if st.session_state.get("submitted_answer") and st.session_state.get("evaluation"):
        current = st.session_state.current_question_num
        total = st.session_state.total_questions

        st.info(f"✅ Q{current} submitted. Go to **Evaluation** to see your result.")

        if current < total:
            if st.button("➡️ Next Question", use_container_width=True, type="primary"):
                st.session_state.current_question_num += 1
                st.session_state.question = None
                st.session_state.question_id = None
                st.session_state.evaluation = None
                st.session_state.submitted_answer = None
                st.session_state.selected_confidence = None
                st.session_state.selected_confidence_score = None
                st.rerun()
        else:
            if st.button("🏁 Finish Interview", use_container_width=True, type="primary"):
                st.session_state.interview_complete = True
                st.rerun()
        return

    total = st.session_state.total_questions
    current = st.session_state.current_question_num

    # Progress
    st.markdown(f"### Question {current} of {total}")
    st.progress((current - 1) / total)
    st.markdown(
        f"**Domain:** {st.session_state.domain} &nbsp;|&nbsp; "
        f"**Difficulty:** {st.session_state.difficulty}"
    )
    st.markdown("---")

    # Generate question if needed
    if st.session_state.get("question") is None:
        with st.spinner(f"Generating question {current} of {total}..."):
            try:
                previous = st.session_state.get("asked_questions", [])

                question = generate_question(
                    domain=st.session_state.domain,
                    difficulty=st.session_state.difficulty,
                    topic=st.session_state.get("topic", ""),
                    previous_questions=previous
                )
                question_id = save_question(
                    st.session_state.session_id,
                    question,
                    question_number=current
                )

                # Track asked questions
                if not isinstance(st.session_state.get("asked_questions"), list):
                    st.session_state.asked_questions = []
                st.session_state.asked_questions.append(question.question)

                st.session_state.question = question
                st.session_state.question_id = question_id
                st.session_state.evaluation = None
                st.session_state.submitted_answer = None

            except Exception as e:
                st.error(f"Failed to generate question: {str(e)}")
                return

    question = st.session_state.question

    # ── Display Question ───────────────────────────────────
    st.subheader("Your Question")
    st.markdown(f"""
    <div style="
        background-color: #1e1e2e;
        border-left: 4px solid #7c3aed;
        padding: 20px;
        border-radius: 8px;
        font-size: 18px;
        color: #e2e8f0;
        margin-bottom: 20px;
    ">
        {question.question}
    </div>
    """, unsafe_allow_html=True)

    if question.topic_tags:
        tags = " &nbsp; ".join([f"`{tag}`" for tag in question.topic_tags])
        st.markdown(f"**Topics:** {tags}")

    st.markdown("---")

    # ── Answer Input ───────────────────────────────────────
    st.subheader("✍️ Your Answer")
    answer_input = st.text_area(
        "Type your answer here...",
        height=200,
        placeholder="Explain your understanding clearly. Include relevant concepts, examples, or formulas where appropriate.",
        key="answer_input"
    )

    st.markdown("---")

    # ── Self Assessment ────────────────────────────────────
    st.subheader("🎯 Self Assessment")
    st.markdown("How confident are you in your answer? *(Select before submitting)*")

    confidence_options = {
        "😰 Not Sure": 2.5,
        "😐 Somewhat Sure": 5.0,
        "😊 Confident": 7.5,
        "🚀 Very Confident": 10.0
    }

    confidence_label = st.radio(
        "Confidence Level",
        options=list(confidence_options.keys()),
        horizontal=True,
        key="confidence_radio"
    )

    st.markdown("---")

    # ── Buttons ────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⏭️ Skip Question", use_container_width=True):
            if current < total:
                st.session_state.current_question_num += 1
            else:
                st.session_state.interview_complete = True
            st.session_state.question = None
            st.session_state.question_id = None
            st.session_state.evaluation = None
            st.session_state.submitted_answer = None
            st.session_state.selected_confidence = None
            st.session_state.selected_confidence_score = None
            st.rerun()

    with col2:
        if st.button("✅ Submit Answer", use_container_width=True, type="primary"):
            if not answer_input.strip():
                st.warning("Please write an answer before submitting.")
            else:
                st.session_state.submitted_answer = answer_input
                st.session_state.selected_confidence = confidence_label
                st.session_state.selected_confidence_score = confidence_options[confidence_label]
                st.success("✅ Answer submitted! Go to **Evaluation** in the sidebar.")