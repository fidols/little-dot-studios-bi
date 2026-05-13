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

st.divider()

# ── All3Media Pressure Banner ─────────────────────────────────────────────────
st.subheader("All3Media Group — Parent Company Pressure")
st.caption(
    "Little Dot Studios is a wholly-owned subsidiary of All3Media. "
    "FY2024 results signal that cost discipline is a business imperative."
)

a1, a2, a3 = st.columns(3)
a1.metric("All3Media Group Revenue", "£895.9M")
a2.metric("FY2024 YoY Change", "-10%", delta="-10%")
a3.metric("FY2024 Operating Result", "-£30.8M", delta="-£30.8M")

st.caption(
    "Source: All3Media FY2024 audited financials. First operating loss in recent history."
)

st.divider()

# ── LDS Network KPIs ─────────────────────────────────────────────────────────
st.subheader("LDS Network Scale")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue", "$257.7M")
k2.metric("Employees", "419")
k3.metric("Network Subscribers", "930M")
k4.metric("Monthly Views", "11.2B")
st.caption(
    "Sources: ZoomInfo (revenue) · LeadIQ March 2026 (employees) · "
    "LDS Whitepaper 2026 (subscribers, views)"
)
