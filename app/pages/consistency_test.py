import streamlit as st
from app.core.consistency_tester import run_consistency_test
from app.core.question_generator import generate_question


def show():
    st.title("🔬 Consistency Tester")
    st.markdown("---")
    st.markdown("""
    This tool evaluates the **same answer multiple times** to measure how 
    consistent the LLM judge is. Low variance = reliable evaluator.
    
    This demonstrates understanding of **LLM reliability** — a key concern 
    in production GenAI systems.
    """)
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        domain = st.selectbox(
            "Domain",
            ["Machine Learning", "Deep Learning", "NLP", "LLMs", "DSA"],
            key="ct_domain"
        )
    with col2:
        runs = st.selectbox("Number of Runs", [3, 5], key="ct_runs")

    # Option to use custom question or generate one
    mode = st.radio(
        "Question Mode",
        ["Generate a question automatically", "Enter question manually"],
        horizontal=True
    )

    if mode == "Enter question manually":
        question_text = st.text_input(
            "Question",
            placeholder="e.g. What is self-attention in Transformers?"
        )
        key_concepts_input = st.text_input(
            "Key Concepts (comma separated)",
            placeholder="e.g. Query, Key, Value, Softmax, Attention Weights"
        )
        key_concepts = [k.strip() for k in key_concepts_input.split(",") if k.strip()]
    else:
        question_text = None
        key_concepts = []

    candidate_answer = st.text_area(
        "Candidate Answer to Test",
        height=150,
        placeholder="Enter the answer you want to test for consistency...",
        key="ct_answer"
    )

    st.markdown("---")

    if st.button("🔬 Run Consistency Test", use_container_width=True, type="primary"):
        if not candidate_answer.strip():
            st.warning("Please enter a candidate answer.")
            return

        # Generate question if needed
        if mode == "Generate a question automatically":
            with st.spinner("Generating question..."):
                try:
                    q = generate_question(domain=domain, difficulty="Medium")
                    question_text = q.question
                    key_concepts = q.key_concepts
                    st.info(f"**Generated Question:** {question_text}")
                except Exception as e:
                    st.error(f"Question generation failed: {str(e)}")
                    return

        if not question_text or not key_concepts:
            st.warning("Please provide a question and key concepts.")
            return

        with st.spinner(f"Running {runs} evaluations... this will take a moment."):
            try:
                result = run_consistency_test(
                    question=question_text,
                    candidate_answer=candidate_answer,
                    key_concepts=key_concepts,
                    runs=runs
                )
            except Exception as e:
                st.error(f"Consistency test failed: {str(e)}")
                return

        # ── Results ────────────────────────────────────────
        st.markdown("---")
        st.subheader("📊 Consistency Results")

        # Variance label
        st.markdown(f"""
        <div style="text-align:center; padding:20px; background:#1e1e2e;
                    border-radius:12px; margin-bottom:20px;">
            <div style="font-size:28px; font-weight:bold; color:#e2e8f0;">
                {result['variance_label']}
            </div>
            <div style="color:#94a3b8; margin-top:8px;">
                {result['variance_desc']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Mean Score", f"{result['mean_score']}/10")
        with col2:
            st.metric("Std Deviation", f"±{result['std_dev']}")
        with col3:
            st.metric("Score Range", f"{result['score_range']} pts")
        with col4:
            st.metric("Runs", result["runs"])

        st.markdown("---")

        # Per-run scores
        st.subheader("Per-Run Breakdown")
        for i, (score, evaluation) in enumerate(
            zip(result["scores"], result["evaluations"]), 1
        ):
            color = "#22c55e" if score >= 8 else "#f59e0b" if score >= 5 else "#ef4444"
            with st.expander(f"Run {i} — Score: {score}/10"):
                st.markdown(f"""
                <div style="background:#1e1e2e; padding:12px; border-radius:8px;
                            margin-bottom:12px;">
                    <span style="color:{color}; font-size:28px; font-weight:bold;">
                        {score}/10
                    </span>
                    <span style="color:#94a3b8; margin-left:12px;">
                        {evaluation.interviewer_note}
                    </span>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**✅ Strengths**")
                    for s in evaluation.strengths:
                        st.success(s)
                with col2:
                    st.markdown("**🔍 Missing**")
                    for m in evaluation.missing_concepts:
                        st.error(m)

        st.markdown("---")

        # What this means
        st.subheader("💡 What This Means")
        st.markdown(f"""
        - Scores across {runs} runs: **{result['scores']}**
        - Standard deviation of **{result['std_dev']}** means scores vary 
          by ±{result['std_dev']} points on average
        - A well-designed evaluation prompt should have std dev **< 1.0**
        - This result shows our judge is **{result['variance_label'].split(' ', 1)[1]}**
        """)