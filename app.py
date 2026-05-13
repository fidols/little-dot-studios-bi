import streamlit as st
import plotly.express as px

from data.simulate import generate_all

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

st.divider()

# ── Office Filter ─────────────────────────────────────────────────────────────
st.subheader("Office Filter")
selected_offices = st.multiselect(
    "Select offices — this filter applies to all pages:",
    options=["UK", "US", "Germany", "ANZ"],
    default=st.session_state["selected_offices"],
)
st.session_state["selected_offices"] = selected_offices
offices = selected_offices if selected_offices else ["UK", "US", "Germany", "ANZ"]
if not selected_offices:
    st.info("No offices selected — showing all offices.")

st.divider()

# ── Revenue by Stream ─────────────────────────────────────────────────────────
st.subheader("Revenue by Stream")
st.caption(
    "Simulated FY2026 revenue breakdown calibrated to $257.7M total. "
    "Filtered by selected offices."
)

fin_df = data["financials_df"]
active_offices = offices if offices else ["UK", "US", "Germany", "ANZ"]
stream_df = (
    fin_df[fin_df["office"].isin(active_offices)]
    .groupby(["revenue_stream", "office"])
    .agg(revenue=("revenue", "sum"))
    .reset_index()
)

office_colors = {
    "UK": "#E31837",
    "US": "#3B82F6",
    "Germany": "#F59E0B",
    "ANZ": "#16A34A",
}

fig = px.bar(
    stream_df,
    x="revenue_stream",
    y="revenue",
    color="office",
    color_discrete_map=office_colors,
    barmode="group",
    labels={"revenue_stream": "Revenue Stream", "revenue": "Annual Revenue ($)", "office": "Office"},
)
fig.update_layout(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font_color="#1A1A1A",
    xaxis_title="Revenue Stream",
    yaxis_title="Annual Revenue ($)",
    margin=dict(t=40, b=40),
)
fig.update_xaxes(tickfont=dict(color="#1A1A1A"), title_font=dict(color="#1A1A1A"))
fig.update_yaxes(tickfont=dict(color="#1A1A1A"), title_font=dict(color="#1A1A1A"))
st.plotly_chart(fig, use_container_width=True)
