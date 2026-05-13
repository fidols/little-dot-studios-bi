import streamlit as st
import plotly.express as px

from data.simulate import generate_all
from utils.metrics import revenue_by_stream

st.set_page_config(
    page_title="Little Dot Studios — Commercial Planning",
    page_icon="\U0001f534",
    layout="wide",
)

# Load all simulated data once per session — all pages read from st.session_state["data"]
if "data" not in st.session_state:
    with st.spinner("Loading data..."):
        st.session_state["data"] = generate_all()

data = st.session_state["data"]

# Office filter default — all offices selected, persists across page navigation
if "selected_offices" not in st.session_state:
    st.session_state["selected_offices"] = ["UK", "US", "Germany", "ANZ"]

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("Little Dot Studios — Commercial Planning")
st.caption("Stakeholders: Commercial Planning · Finance · Executive Leadership")
