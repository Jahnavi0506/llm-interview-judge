import streamlit as st
from app.core.question_generator import generate_question
from app.core.difficulty_adjuster import get_next_difficulty
from app.db.crud import save_question


DIFFICULTY_COLORS = {
    "Easy": "#22c55e",
    "Medium": "#f59e0b",
    "Hard": "#ef4444"
}


def show():
    st.title("📝 Interview")
    st.markdown("---")

    if "session_id" not in st.session_state or st.session_state.session_id is None:
        st.warning("Please start a session from the **Home** page first.")
        return

    if st.session_state.get("interview_complete"):
        st.success("✅ Interview complete! Go to **Evaluation** to see your full report.")
        return

    # If already submitted, show next button
    if st.session_state.get("submitted_answer") and st.session_state.get("evaluation"):
        current = st.session_state.current_question_num
        total = st.session_state.total_questions

        st.info(f"✅ Q{current} submitted. Go to **Evaluation** to see your result.")

        if current < total:
            if st.button("➡️ Next Question", use_container_width=True, type="primary"):
                # Adjust difficulty before next question
                scores = st.session_state.get("session_scores") or []
                current_diff = st.session_state.get(
                    "current_difficulty",
                    st.session_state.difficulty
                )
                next_diff, reason = get_next_difficulty(current_diff, scores)

                # Store adjustment
                st.session_state.current_difficulty = next_diff
                if st.session_state.difficulty_history is None:
                    st.session_state.difficulty_history = []
                st.session_state.difficulty_history.append({
                    "question": current + 1,
                    "difficulty": next_diff,
                    "reason": reason
                })

                st.session_state.current_question_num += 1
                st.session_state.question = None
                st.session_state.question_id = None
                st.session_state.evaluation = None
                st.session_state.submitted_answer = None
                st.session_state.selected_confidence = None
                st.session_state.selected_confidence_score = None
                st.session_state.follow_up = None
                st.session_state.follow_up_evaluation = None
                st.rerun()
        else:
            if st.button("🏁 Finish Interview", use_container_width=True, type="primary"):
                st.session_state.interview_complete = True
                st.rerun()
        return

    total = st.session_state.total_questions
    current = st.session_state.current_question_num
    current_diff = st.session_state.get(
        "current_difficulty",
        st.session_state.difficulty
    )
    diff_color = DIFFICULTY_COLORS.get(current_diff, "#94a3b8")

    # Progress
    st.markdown(f"### Question {current} of {total}")
    st.progress((current - 1) / total)

    # Domain + adaptive difficulty display
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.markdown(f"**Domain:** {st.session_state.domain}")
    with col2:
        st.markdown(f"""
        <div style="text-align:center; background:{diff_color}22;
                    border:1px solid {diff_color}; border-radius:6px;
                    padding:4px 8px; color:{diff_color}; font-weight:bold;">
            {current_diff}
        </div>
        """, unsafe_allow_html=True)
    with col3:
        # Show difficulty adjustment reason if available
        history = st.session_state.get("difficulty_history") or []
        if history:
            last = history[-1]
            if last["question"] == current:
                st.caption(f"⚡ {last['reason']}")

    st.markdown("---")

    # Generate question
    if st.session_state.get("question") is None:
        with st.spinner(f"Generating {current_diff} question {current} of {total}..."):
            try:
                previous = st.session_state.get("asked_questions") or []

                question = generate_question(
                    domain=st.session_state.domain,
                    difficulty=current_diff,        # ← uses adaptive difficulty
                    topic=st.session_state.get("topic", ""),
                    previous_questions=previous
                )
                question_id = save_question(
                    st.session_state.session_id,
                    question,
                    question_number=current
                )

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

    # Display question
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

    # Answer input
    st.subheader("✍️ Your Answer")
    answer_input = st.text_area(
        "Type your answer here...",
        height=200,
        placeholder="Explain your understanding clearly...",
        key="answer_input"
    )

    st.markdown("---")

    # Self assessment
    st.subheader("🎯 Self Assessment")
    st.markdown("How confident are you in your answer?")

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
                st.session_state.selected_confidence_score = (
                    confidence_options[confidence_label]
                )
                st.success("✅ Answer submitted! Go to **Evaluation** in the sidebar.")