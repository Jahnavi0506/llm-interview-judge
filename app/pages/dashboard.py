import streamlit as st
from app.core.analytics import (
    get_score_trend,
    get_domain_performance,
    get_missing_concepts_frequency,
    get_calibration_stats,
    get_difficulty_performance,
    get_overall_stats
)


def show():
    st.title("📈 Performance Dashboard")
    st.markdown("---")

    # Check if any data exists
    stats = get_overall_stats()

    if stats["total_sessions"] == 0:
        st.info(
            "No data yet. Complete at least one interview session "
            "to see your performance analytics."
        )
        return

    # ── Overall Stats ──────────────────────────────────────
    st.subheader("🏆 Overall Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Sessions", stats["total_sessions"])
    with col2:
        st.metric("Questions Answered", stats["total_evaluations"])
    with col3:
        st.metric("Overall Avg Score", f"{stats['overall_avg']}/10")
    with col4:
        st.metric("Best Score", f"{stats['best_score']}/10")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background:#1e1e2e; padding:16px; border-radius:8px;
                    border-left:4px solid #22c55e;">
            <div style="color:#94a3b8; font-size:11px;">STRONGEST DOMAIN</div>
            <div style="color:#22c55e; font-size:18px; font-weight:bold; margin-top:4px;">
                {stats['best_domain']['domain']}
            </div>
            <div style="color:#94a3b8; font-size:13px;">
                Avg: {stats['best_domain']['avg']}/10
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background:#1e1e2e; padding:16px; border-radius:8px;
                    border-left:4px solid #ef4444;">
            <div style="color:#94a3b8; font-size:11px;">WEAKEST DOMAIN</div>
            <div style="color:#ef4444; font-size:18px; font-weight:bold; margin-top:4px;">
                {stats['weak_domain']['domain']}
            </div>
            <div style="color:#94a3b8; font-size:13px;">
                Avg: {stats['weak_domain']['avg']}/10
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Score Trend ────────────────────────────────────────
    st.subheader("📈 Score Trend Across Sessions")
    trend = get_score_trend()

    if len(trend) >= 2:
        import plotly.graph_objects as go

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[f"Session {r['session_id']}\n{r['domain']}" for r in trend],
            y=[r["avg_score"] for r in trend],
            mode="lines+markers+text",
            text=[f"{r['avg_score']}" for r in trend],
            textposition="top center",
            line=dict(color="#7c3aed", width=2),
            marker=dict(
                size=10,
                color=[
                    "#22c55e" if r["avg_score"] >= 8
                    else "#f59e0b" if r["avg_score"] >= 5
                    else "#ef4444"
                    for r in trend
                ]
            ),
            fill="tozeroy",
            fillcolor="rgba(124,58,237,0.1)"
        ))
        fig.update_layout(
            yaxis=dict(range=[0, 10.5], title="Average Score"),
            xaxis=dict(title="Session"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            height=300,
            margin=dict(t=20, b=20)
        )
        fig.add_hline(
            y=7, line_dash="dash",
            line_color="#22c55e",
            annotation_text="Good (7+)",
            annotation_position="right"
        )
        fig.add_hline(
            y=5, line_dash="dash",
            line_color="#f59e0b",
            annotation_text="Average (5+)",
            annotation_position="right"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Simple display for single session
        for r in trend:
            color = "#22c55e" if r["avg_score"] >= 8 else \
                    "#f59e0b" if r["avg_score"] >= 5 else "#ef4444"
            st.markdown(f"""
            <div style="background:#1e1e2e; padding:12px; border-radius:8px;
                        border-left:4px solid {color}; margin-bottom:8px;">
                Session {r['session_id']} — {r['domain']} —
                <strong style="color:{color};">{r['avg_score']}/10</strong>
            </div>
            """, unsafe_allow_html=True)
        st.caption("Complete more sessions to see the trend chart.")

    st.markdown("---")

    # ── Domain Performance ─────────────────────────────────
    st.subheader("🎯 Performance by Domain")
    domain_data = get_domain_performance()

    if domain_data:
        import plotly.graph_objects as go

        fig = go.Figure(go.Bar(
            x=[d["domain"] for d in domain_data],
            y=[d["avg_score"] for d in domain_data],
            text=[f"{d['avg_score']}/10" for d in domain_data],
            textposition="outside",
            marker_color=[
                "#22c55e" if d["avg_score"] >= 8
                else "#f59e0b" if d["avg_score"] >= 5
                else "#ef4444"
                for d in domain_data
            ]
        ))
        fig.update_layout(
            yaxis=dict(range=[0, 11], title="Average Score"),
            xaxis=dict(title="Domain"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            height=300,
            margin=dict(t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Difficulty Performance ─────────────────────────────
    st.subheader("⚡ Performance by Difficulty")
    diff_data = get_difficulty_performance()

    if diff_data:
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
        diff_colors = {
            "Easy": "#22c55e",
            "Medium": "#f59e0b",
            "Hard": "#ef4444"
        }

        for i, d in enumerate(diff_data):
            color = diff_colors.get(d["difficulty"], "#94a3b8")
            with cols[i % 3]:
                st.markdown(f"""
                <div style="background:#1e1e2e; padding:20px; border-radius:8px;
                            border-top:4px solid {color}; text-align:center;">
                    <div style="color:{color}; font-size:14px; font-weight:bold;">
                        {d['difficulty']}
                    </div>
                    <div style="color:#e2e8f0; font-size:32px; font-weight:bold;
                                margin-top:8px;">
                        {d['avg_score']}/10
                    </div>
                    <div style="color:#94a3b8; font-size:12px; margin-top:4px;">
                        {d['total_questions']} questions
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Concept Gap Heatmap ────────────────────────────────
    st.subheader("🔥 Most Frequently Missed Concepts")
    concepts = get_missing_concepts_frequency()

    if concepts:
        max_freq = concepts[0]["frequency"]

        for c in concepts:
            intensity = c["frequency"] / max_freq
            red = int(239 * intensity)
            bar_width = int(intensity * 100)

            st.markdown(f"""
            <div style="display:flex; align-items:center;
                        margin-bottom:6px; gap:12px;">
                <div style="width:180px; color:#e2e8f0;
                            font-size:13px; flex-shrink:0;">
                    {c['concept']}
                </div>
                <div style="flex:1; background:#1e1e2e;
                            border-radius:4px; height:24px; position:relative;">
                    <div style="width:{bar_width}%; background:rgb({red},68,68);
                                height:100%; border-radius:4px;">
                    </div>
                </div>
                <div style="color:#94a3b8; font-size:12px;
                            width:30px; text-align:right; flex-shrink:0;">
                    {c['frequency']}x
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No missed concepts data yet.")

    st.markdown("---")

    # ── Calibration Chart ──────────────────────────────────
    st.subheader("🎯 Self-Assessment Calibration Overview")
    cal = get_calibration_stats()

    if cal["total"] > 0:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Evaluated", cal["total"])
        with col2:
            st.metric(
                "✅ Well Calibrated",
                cal["well_calibrated"],
                f"{round(cal['well_calibrated']/cal['total']*100)}%"
            )
        with col3:
            st.metric(
                "⚠️ Overconfident",
                cal["overconfident"],
                f"{round(cal['overconfident']/cal['total']*100)}%"
            )
        with col4:
            st.metric(
                "💡 Underconfident",
                cal["underconfident"],
                f"{round(cal['underconfident']/cal['total']*100)}%"
            )

        # Scatter plot — confidence vs actual
        # Filter only rows that have confidence_score data
        valid_data = [
            d for d in cal["data"]
            if d.get("confidence_score") is not None
            and d.get("score") is not None
            and d.get("self_assessment_gap") is not None
        ]

        if len(valid_data) >= 3:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[d["confidence_score"] for d in valid_data],
                y=[d["score"] for d in valid_data],
                mode="markers",
                marker=dict(
                    size=10,
                    color=[
                        "#22c55e" if abs(d["self_assessment_gap"]) <= 2
                        else "#ef4444" if d["self_assessment_gap"] < -2
                        else "#3b82f6"
                        for d in valid_data
                    ],
                    opacity=0.8
                ),
                text=[
                    f"Confidence: {d['confidence_score']}<br>"
                    f"Actual: {d['score']}<br>"
                    f"Gap: {d['self_assessment_gap']:+.1f}"
                    for d in valid_data
                ],
                hovertemplate="%{text}<extra></extra>"
            ))
            fig.add_trace(go.Scatter(
                x=[0, 10], y=[0, 10],
                mode="lines",
                line=dict(color="#94a3b8", dash="dash", width=1),
                name="Perfect Calibration"
            ))
            fig.update_layout(
                xaxis=dict(title="Confidence Score", range=[0, 11]),
                yaxis=dict(title="Actual Score", range=[0, 11]),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                height=350,
                showlegend=False,
                margin=dict(t=20)
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption(
                "🟢 Well Calibrated &nbsp; "
                "🔴 Overconfident &nbsp; "
                "🔵 Underconfident &nbsp; "
                "--- Perfect Calibration Line"
            )
        else:
            st.info("Answer at least 3 questions with confidence ratings to see the scatter plot.")
            
    # ── Log Viewer ─────────────────────────────────────────
    st.markdown("---")
    with st.expander("🪵 System Logs (last 50 lines)"):
        try:
            with open("logs/app.log", "r") as f:
                lines = f.readlines()
                last_50 = lines[-50:] if len(lines) > 50 else lines
                log_text = "".join(last_50)
            st.code(log_text, language="text")
        except FileNotFoundError:
            st.info("No logs yet. Logs appear after your first API call.")