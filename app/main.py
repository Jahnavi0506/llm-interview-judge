import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.db.database import init_db

# rest of the file stays exactly the same...

# Initialize database on every startup
init_db()

# Page configuration
st.set_page_config(
    page_title="LLM Interview Judge",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("🎯 LLM Interview Judge")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "📝 Interview", "📊 Evaluation", "🕘 History"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Built with Groq + Streamlit + SQLite")

# Route to correct page
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