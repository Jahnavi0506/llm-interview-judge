import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.db.database import init_db

init_db()

st.set_page_config(
    page_title="LLM Interview Judge",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0f0f1a;
    }

    /* Main background */
    .stApp {
        background-color: #13131f;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: #1e1e2e;
        border: 1px solid #2d2d44;
        border-radius: 8px;
        padding: 16px;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }

    /* Success/Error/Info boxes */
    .stSuccess, .stError, .stInfo, .stWarning {
        border-radius: 8px;
    }

    /* Text area */
    textarea {
        border-radius: 8px !important;
        background-color: #1e1e2e !important;
        color: #e2e8f0 !important;
    }

    /* Expander */
    details {
        background: #1e1e2e;
        border-radius: 8px;
        border: 1px solid #2d2d44;
        margin-bottom: 8px;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Progress bar color */
    div[data-testid="stProgressBar"] > div {
        background-color: #7c3aed;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:20px 0;">
        <div style="font-size:48px;">🎯</div>
        <div style="color:#e2e8f0; font-size:20px; font-weight:bold;
                    margin-top:8px;">LLM Interview Judge</div>
        <div style="color:#64748b; font-size:12px; margin-top:4px;">
            AI-Powered Assessment
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["🏠 Home",
         "📝 Interview",
         "📊 Evaluation",
         "🕘 History",
         "📈 Dashboard",
         "🔬 Consistency Test",
         "🎯 Accuracy Validation"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Session status in sidebar
    if st.session_state.get("session_id"):
        current = st.session_state.get("current_question_num", 1)
        total = st.session_state.get("total_questions", 5)
        domain = st.session_state.get("domain", "")
        diff = st.session_state.get("current_difficulty",
               st.session_state.get("difficulty", ""))

        diff_colors = {"Easy": "#22c55e", "Medium": "#f59e0b", "Hard": "#ef4444"}
        diff_color = diff_colors.get(diff, "#94a3b8")

        st.markdown(f"""
        <div style="background:#1e1e2e; padding:12px; border-radius:8px;
                    border:1px solid #2d2d44;">
            <div style="color:#64748b; font-size:10px; margin-bottom:6px;">
                ACTIVE SESSION
            </div>
            <div style="color:#e2e8f0; font-size:13px; font-weight:bold;">
                {domain}
            </div>
            <div style="color:{diff_color}; font-size:12px; margin-top:2px;">
                {diff}
            </div>
            <div style="color:#64748b; font-size:11px; margin-top:6px;">
                Q{current} of {total}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#1e1e2e; padding:12px; border-radius:8px;
                    border:1px solid #2d2d44; text-align:center;">
            <div style="color:#64748b; font-size:12px;">No active session</div>
            <div style="color:#7c3aed; font-size:11px; margin-top:4px;">
                Start from Home →
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#64748b; font-size:10px;">
        Powered by Groq + Streamlit<br>
        LLM-as-a-Judge Architecture
    </div>
    """, unsafe_allow_html=True)

# ── Page Routing ───────────────────────────────────────────
if page == "🏠 Home":
    from app.pages.home import show
    show()

elif page == "📝 Interview":
    from app.pages.interview import show
    show()

elif page == "📊 Evaluation":
    from app.pages.evaluation import show
    show()

elif page == "🕘 History":
    from app.pages.history import show
    show()

elif page == "📈 Dashboard":
    from app.pages.dashboard import show
    show()

elif page == "🔬 Consistency Test":
    from app.pages.consistency_test import show
    show()
elif page == "🎯 Accuracy Validation":
    from app.pages.accuracy_test import show
    show()