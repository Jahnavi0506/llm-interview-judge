import streamlit as st
from app.core.accuracy_evaluator import run_accuracy_evaluation, get_accuracy_label
from tests.ground_truth_dataset import get_dataset_summary, GROUND_TRUTH_DATASET


def show():
    st.title("🎯 Judge Accuracy Validation")
    st.markdown("---")

    st.markdown("""
    This page validates whether the **LLM judge's scores match expert human judgment**.
    
    Unlike the Consistency Tester (which checks if scores are *repeatable*), this 
    measures whether scores are *correct* by comparing against a hand-curated 
    ground truth dataset of 20 question-answer pairs with expert-assigned scores.
    """)

    st.markdown("---")

    # Dataset overview
    summary = get_dataset_summary()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Dataset Size", summary["total_items"])
    with col2:
        st.metric("Domains Covered", len(summary["domains"]))
    with col3:
        st.metric(
            "Score Range",
            f"{summary['score_range'][0]} - {summary['score_range'][1]}"
        )

    with st.expander("📋 View Ground Truth Dataset"):
        for item in GROUND_TRUTH_DATASET:
            st.markdown(f"**Q{item['id']} ({item['domain']}):** {item['question']}")
            st.caption(f"Answer: \"{item['candidate_answer'][:100]}...\"" 
                      if len(item['candidate_answer']) > 100 
                      else f"Answer: \"{item['candidate_answer']}\"")
            st.caption(f"Human Score: **{item['human_score']}/10** — {item['human_reasoning']}")
            st.markdown("---")

    st.markdown("---")

    # Run evaluation
    if st.button("🚀 Run Accuracy Validation (20 evaluations)", 
                 use_container_width=True, type="primary"):
        progress_bar = st.progress(0, text="Starting evaluation...")

        with st.spinner("Evaluating all 20 ground truth answers... this takes a few minutes."):
            try:
                result = run_accuracy_evaluation()
                st.session_state.accuracy_result = result
            except Exception as e:
                st.error(f"Accuracy evaluation failed: {str(e)}")
                return

        progress_bar.progress(100, text="Complete!")

    # Display results
    if st.session_state.get("accuracy_result"):
        result = st.session_state.accuracy_result

        st.markdown("---")
        st.subheader("📊 Accuracy Results")

        label, desc = get_accuracy_label(result["mean_absolute_error"])

        st.markdown(f"""
        <div style="text-align:center; padding:24px; background:#1e1e2e;
                    border-radius:12px; margin-bottom:20px;">
            <div style="font-size:28px; font-weight:bold; color:#e2e8f0;">
                {label}
            </div>
            <div style="color:#94a3b8; margin-top:8px;">
                {desc}
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Mean Absolute Error",
                f"{result['mean_absolute_error']}"
            )
        with col2:
            st.metric(
                "Agreement Rate",
                f"{result['agreement_rate']}%",
                f"within ±{result['tolerance']} pts"
            )
        with col3:
            corr = result.get("correlation")
            st.metric(
                "Correlation",
                f"{corr}" if corr is not None else "N/A"
            )
        with col4:
            st.metric(
                "Items Evaluated",
                f"{result['total_items']}"
            )

        st.markdown("---")

        # Scatter plot: human vs LLM scores
        st.subheader("📈 Human Score vs LLM Score")
        try:
            import plotly.graph_objects as go

            valid_results = [r for r in result["results"] if r.get("llm_score") is not None]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[r["human_score"] for r in valid_results],
                y=[r["llm_score"] for r in valid_results],
                mode="markers",
                marker=dict(
                    size=12,
                    color=[
                        "#22c55e" if r["within_tolerance"] else "#ef4444"
                        for r in valid_results
                    ],
                    opacity=0.8
                ),
                text=[
                    f"Q{r['id']} ({r['domain']})<br>"
                    f"Human: {r['human_score']}<br>"
                    f"LLM: {r['llm_score']}<br>"
                    f"Error: {r['error']:+.1f}"
                    for r in valid_results
                ],
                hovertemplate="%{text}<extra></extra>"
            ))
            fig.add_trace(go.Scatter(
                x=[0, 10], y=[0, 10],
                mode="lines",
                line=dict(color="#94a3b8", dash="dash", width=1),
                name="Perfect Agreement"
            ))
            fig.update_layout(
                xaxis=dict(title="Human Score", range=[-0.5, 10.5]),
                yaxis=dict(title="LLM Judge Score", range=[-0.5, 10.5]),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                height=400,
                showlegend=False,
                margin=dict(t=20)
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("🟢 Within tolerance (±1.5 pts) &nbsp; 🔴 Outside tolerance &nbsp; --- Perfect agreement line")
        except ImportError:
            st.warning("Install plotly to see the scatter chart: pip install plotly")

        st.markdown("---")

        # Per-item breakdown
        st.subheader("📋 Per-Item Breakdown")
        for r in result["results"]:
            if r.get("failed"):
                st.error(f"Q{r['id']} ({r['domain']}) — Evaluation failed: {r.get('error_message')}")
                continue

            status_icon = "✅" if r["within_tolerance"] else "⚠️"
            with st.expander(
                f"{status_icon} Q{r['id']} ({r['domain']}) — "
                f"Human: {r['human_score']} | LLM: {r['llm_score']} | "
                f"Error: {r['error']:+.1f}"
            ):
                st.markdown(f"**Question:** {r['question']}")
                st.markdown(f"**Answer:** {r['candidate_answer']}")
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**👤 Human Score: {r['human_score']}/10**")
                    st.caption(r["human_reasoning"])
                with col2:
                    st.markdown(f"**🤖 LLM Score: {r['llm_score']}/10**")
                    st.caption(r["llm_note"])

        st.markdown("---")
        st.subheader("💡 What This Means")
        st.markdown(f"""
        - Mean Absolute Error of **{result['mean_absolute_error']}** points means 
          the LLM judge's scores deviate from expert human scores by this much on average
        - **{result['agreement_rate']}%** of evaluations fell within ±{result['tolerance']} 
          points of the human score — considered acceptable agreement
        - A correlation of **{result.get('correlation', 'N/A')}** shows how well the 
          LLM's score *ranking* matches the human's ranking (1.0 = perfect, 0 = no relationship)
        - This validation demonstrates the judge isn't just consistent, but also 
          **accurate** relative to expert human evaluation
        """)