import streamlit as st
import pandas as pd
import plotly.express as px

from utils.metrics import (
    gross_margin_pct,
    avg_project_margin_pct,
    margin_delta_qoq,
    monthly_financials_trend,
    margin_by_tier,
    margin_by_project_type,
    pricing_estimate,
    SENIORITY_MIXES,
)

# ── Session state guard ───────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.warning("Please start from the Overview page to load data.")
    st.stop()

data = st.session_state["data"]
offices = st.session_state.get("selected_offices", ["UK", "US", "Germany", "ANZ"])

project_df = data["project_df"]
client_df = data["client_df"]
financials_df = data["financials_df"]

project_filtered = project_df[project_df["office"].isin(offices)]
financials_filtered = financials_df[financials_df["office"].isin(offices)]

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("Profitability & Finance")
st.caption("Stakeholders: Finance · Commercial Leadership · CEO")

# ── All3Media Callback Banner ─────────────────────────────────────────────────
st.info(
    "All3Media FY2024 operating loss: **-£30.8M**. "
    "LDS profitability targets are set against this backdrop."
)

st.divider()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
gm = gross_margin_pct(project_filtered)
avg_pm = avg_project_margin_pct(project_filtered)
margin_delta = margin_delta_qoq(financials_filtered)
total_rev = project_filtered["revenue"].sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue", f"${total_rev / 1_000_000:.1f}M")
k2.metric("Gross Margin %", f"{gm:.1%}")
k3.metric("Avg Project Margin %", f"{avg_pm:.1%}")
k4.metric(
    "Margin Delta (QoQ)",
    f"{margin_delta:+.1%}",
    delta=f"{margin_delta:+.1%}",
    delta_color="normal",
)

st.divider()

# ── Revenue vs Cost Over Time ─────────────────────────────────────────────────
st.subheader("Revenue vs Cost Over Time")
st.caption("The gap between revenue and combined costs = gross margin. Narrowing gap = margin compression.")

trend_df = monthly_financials_trend(financials_filtered)

melted = trend_df.melt(
    id_vars="month",
    value_vars=["revenue", "direct_cost", "labor_cost"],
    var_name="category",
    value_name="amount",
)
melted["category"] = melted["category"].map({
    "revenue": "Revenue",
    "direct_cost": "Direct Cost",
    "labor_cost": "Labor Cost",
})

fig_area = px.area(
    melted,
    x="month",
    y="amount",
    color="category",
    color_discrete_map={
        "Revenue": "#E31837",
        "Direct Cost": "#6D6E71",
        "Labor Cost": "#94A3B8",
    },
    labels={"month": "Month", "amount": "Amount ($)", "category": "Category"},
)
fig_area.update_layout(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font_color="#1A1A1A",
)
fig_area.update_xaxes(tickfont=dict(color="#1A1A1A"), title_font=dict(color="#1A1A1A"))
fig_area.update_yaxes(tickfont=dict(color="#1A1A1A"), title_font=dict(color="#1A1A1A"))
st.plotly_chart(fig_area, use_container_width=True)

st.divider()

col_left, col_right = st.columns(2)

# ── Margin by Client Tier ─────────────────────────────────────────────────────
with col_left:
    st.subheader("Margin by Client Tier")
    tier_df = margin_by_tier(project_filtered, client_df)
    tier_order = ["Platinum", "Gold", "Silver"]
    tier_df["tier"] = pd.Categorical(tier_df["tier"], categories=tier_order, ordered=True)
    tier_df = tier_df.sort_values("tier")

    fig_tier = px.bar(
        tier_df,
        x="tier",
        y="avg_margin_pct",
        color_discrete_sequence=["#E31837"],
        labels={"tier": "Client Tier", "avg_margin_pct": "Avg Margin %"},
    )
    fig_tier.add_hline(y=0.30, line_dash="dash", line_color="#1A1A1A",
                       annotation_text="Target (30%)")
    fig_tier.update_layout(
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font_color="#1A1A1A",
        yaxis_tickformat=".0%",
    )
    fig_tier.update_xaxes(tickfont=dict(color="#1A1A1A"), title_font=dict(color="#1A1A1A"))
    fig_tier.update_yaxes(tickfont=dict(color="#1A1A1A"), title_font=dict(color="#1A1A1A"))
    st.plotly_chart(fig_tier, use_container_width=True)

# ── Project Type Profitability ─────────────────────────────────────────────────
with col_right:
    st.subheader("Margin by Project Type")
    type_df = margin_by_project_type(project_filtered)

    fig_type = px.bar(
        type_df.sort_values("avg_margin_pct", ascending=False),
        x="project_type",
        y="avg_margin_pct",
        color_discrete_sequence=["#1A1A1A"],
        labels={"project_type": "Project Type", "avg_margin_pct": "Avg Margin %"},
    )
    fig_type.add_hline(y=0.30, line_dash="dash", line_color="#E31837",
                       annotation_text="Healthy (30%)")
    fig_type.update_layout(
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font_color="#1A1A1A",
        yaxis_tickformat=".0%",
    )
    fig_type.update_xaxes(tickfont=dict(color="#1A1A1A"), title_font=dict(color="#1A1A1A"))
    fig_type.update_yaxes(tickfont=dict(color="#1A1A1A"), title_font=dict(color="#1A1A1A"))
    st.plotly_chart(fig_type, use_container_width=True)

st.divider()

# ── New Business Pricing Tool ─────────────────────────────────────────────────
st.subheader("New Business Pricing Tool")
st.caption("Estimates floor and recommended price for a new project based on historical actuals.")

p_col1, p_col2, p_col3, p_col4 = st.columns(4)

with p_col1:
    p_type = st.selectbox(
        "Project Type",
        options=["Retainer", "Production", "Licensing", "Content ID"],
    )
with p_col2:
    p_weeks = st.slider("Estimated Weeks", min_value=1, max_value=52, value=8)
with p_col3:
    p_team = st.slider("Team Size", min_value=1, max_value=20, value=4)
with p_col4:
    p_seniority = st.selectbox(
        "Seniority Mix",
        options=list(SENIORITY_MIXES.keys()),
        index=1,  # default: Balanced
    )

estimate = pricing_estimate(
    project_type=p_type,
    weeks=p_weeks,
    team_size=p_team,
    seniority_mix=p_seniority,
    project_df=project_df,
)

r1, r2, r3 = st.columns(3)
r1.metric("Floor Price (20% min margin)", f"${estimate['floor_price']:,.0f}")
r2.metric("Recommended Price (30% target)", f"${estimate['recommended_price']:,.0f}")
r3.metric("Estimated Hours", f"{estimate['total_hours']:,}")

st.info(
    f"Based on **{estimate['comparable_count']}** comparable past {p_type} projects "
    f"with similar scope."
)

with st.expander("Hours breakdown by seniority"):
    for role, hours in estimate["hours_breakdown"].items():
        st.write(f"**{role}:** {hours:,} hours")
    st.write(f"**Total cost base:** ${estimate['total_cost']:,.0f}")
