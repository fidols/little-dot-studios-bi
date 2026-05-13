import streamlit as st
import pandas as pd
import plotly.express as px

from data.simulate import TODAY
from utils.metrics import (
    pipeline_value,
    renewal_rate,
    avg_contract_value,
    clients_expiring_soon,
    revenue_at_risk,
)

_ENGAGEMENT_HIGH_RISK_THRESHOLD = 50   # below this = high risk
_ENGAGEMENT_MED_RISK_THRESHOLD = 70    # below this = medium risk
_ENGAGEMENT_QUADRANT_MID = 65          # scatter plot horizontal divider

# ── Session state guard ───────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.warning("Please start from the Overview page to load data.")
    st.stop()

data = st.session_state["data"]
client_df = data["client_df"]
pipeline_df = data["pipeline_df"]
project_df = data["project_df"]

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("Client & CRM")
st.caption("Stakeholders: Commercial Team · Sales · Finance")

st.divider()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
active_clients = int((client_df["status"] == "Active").sum())
pipe_val = pipeline_value(pipeline_df)
renew_rate = renewal_rate(client_df)
acv = avg_contract_value(client_df)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Active Clients", str(active_clients))
k2.metric("Open Pipeline Value", f"${pipe_val / 1_000_000:.1f}M")
k3.metric("Renewal Rate", f"{renew_rate:.1%}")
k4.metric("Avg Contract Value", f"${acv / 1_000:,.0f}K")

st.divider()

# ── Client Health Matrix ───────────────────────────────────────────────────────
st.subheader("Client Health Matrix")
st.caption(
    "Stars (top-right): high revenue + high engagement. "
    "At Risk (bottom-right): high revenue, low engagement. "
    "Growth (top-left): low revenue, high engagement. "
    "Deprioritize (bottom-left): low revenue, low engagement."
)

tier_colors = {"Platinum": "#E31837", "Gold": "#F59E0B", "Silver": "#6D6E71"}

fig_scatter = px.scatter(
    client_df,
    x="annual_revenue",
    y="engagement_score",
    color="tier",
    color_discrete_map=tier_colors,
    size="annual_revenue",
    size_max=30,
    hover_data={"client_name": True, "annual_revenue": True,
                "engagement_score": True, "renewal_date": True},
    labels={"annual_revenue": "Annual Revenue ($)", "engagement_score": "Engagement Score (0–100)"},
)

# Quadrant lines at median values
rev_mid = client_df["annual_revenue"].median()
eng_mid = _ENGAGEMENT_QUADRANT_MID

fig_scatter.add_vline(x=rev_mid, line_dash="dot", line_color="#6D6E71")
fig_scatter.add_hline(y=eng_mid, line_dash="dot", line_color="#6D6E71")

# Quadrant labels
fig_scatter.add_annotation(x=rev_mid * 2, y=90, text="Stars", showarrow=False,
                            font=dict(color="#16A34A", size=12))
fig_scatter.add_annotation(x=rev_mid * 2, y=40, text="At Risk", showarrow=False,
                            font=dict(color="#E31837", size=12))
fig_scatter.add_annotation(x=rev_mid * 0.3, y=90, text="Growth", showarrow=False,
                            font=dict(color="#1A1A1A", size=12))
fig_scatter.add_annotation(x=rev_mid * 0.3, y=40, text="Deprioritize", showarrow=False,
                            font=dict(color="#6D6E71", size=12))

fig_scatter.update_layout(
    plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font_color="#1A1A1A",
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# ── Client Tier Table ──────────────────────────────────────────────────────────
st.subheader("Client Directory")

table_df = client_df[[
    "client_name", "tier", "contract_type", "annual_revenue",
    "margin_pct", "renewal_date", "last_contact_date", "status",
]].rename(columns={
    "client_name": "Client",
    "tier": "Tier",
    "contract_type": "Contract Type",
    "annual_revenue": "Revenue ($)",
    "margin_pct": "Margin %",
    "renewal_date": "Renewal Date",
    "last_contact_date": "Last Contact",
    "status": "Status",
})

status_filter = st.multiselect(
    "Filter by status:", options=["Active", "At Risk", "Churned"], default=["Active", "At Risk"]
)
if status_filter:
    table_df = table_df[table_df["Status"].isin(status_filter)]


def _status_color(row):
    if row["Status"] == "Churned":
        return ["background-color: #fde8e8"] * len(row)
    elif row["Status"] == "At Risk":
        return ["background-color: #fef9c3"] * len(row)
    return ["background-color: #d4edda"] * len(row)


styled = (
    table_df.style
    .apply(_status_color, axis=1)
    .format({"Revenue ($)": "${:,.0f}", "Margin %": "{:.1%}"})
)
st.dataframe(styled, use_container_width=True)

csv_data = table_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name="lds_clients.csv",
    mime="text/csv",
)

st.divider()

# ── Pipeline by Stage ──────────────────────────────────────────────────────────
st.subheader("Pipeline by Stage")

stage_order = ["Prospecting", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
pipeline_summary = (
    pipeline_df.groupby("stage")["value"]
    .sum()
    .reset_index()
    .rename(columns={"value": "total_value"})
)
pipeline_summary["stage"] = pd.Categorical(
    pipeline_summary["stage"], categories=stage_order, ordered=True
)
pipeline_summary = pipeline_summary.sort_values("stage")

open_stages = {"Prospecting", "Proposal", "Negotiation"}
total_open = pipeline_df[pipeline_df["stage"].isin(open_stages)]["value"].sum()
closed_won = pipeline_df[pipeline_df["stage"] == "Closed Won"]["value"].sum()
total_closed = closed_won + pipeline_df[pipeline_df["stage"] == "Closed Lost"]["value"].sum()
win_rate = (closed_won / total_closed * 100) if total_closed > 0 else 0.0

st.caption(f"Open pipeline: **${total_open / 1_000_000:.1f}M** · Win rate on closed deals: **{win_rate:.0f}%**")

fig_pipe = px.bar(
    pipeline_summary,
    x="stage",
    y="total_value",
    color_discrete_sequence=["#E31837"],
    labels={"stage": "Stage", "total_value": "Total Value ($)"},
)
fig_pipe.update_layout(
    plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font_color="#1A1A1A",
)
st.plotly_chart(fig_pipe, use_container_width=True)

st.divider()

# ── Renewal Calendar ──────────────────────────────────────────────────────────
st.subheader("Contracts Expiring in Next 90 Days")

expiring = clients_expiring_soon(client_df, days=90, today=TODAY)
rar = revenue_at_risk(client_df, days=90, today=TODAY)

st.metric("Revenue at Risk (90-day window)", f"${rar / 1_000_000:.2f}M")

if len(expiring) == 0:
    st.success("No contracts expiring in the next 90 days.")
else:
    for _, row in expiring.sort_values("renewal_date").iterrows():
        risk_level = "high" if row["engagement_score"] < _ENGAGEMENT_HIGH_RISK_THRESHOLD else "medium" if row["engagement_score"] < _ENGAGEMENT_MED_RISK_THRESHOLD else "low"
        revenue_m = row["annual_revenue"] / 1_000_000
        msg = (
            f"**{row['client_name']}** ({row['tier']}) — "
            f"Renews {row['renewal_date']} · "
            f"Revenue: ${revenue_m:.2f}M · "
            f"Engagement: {row['engagement_score']}/100 · "
            f"Risk: **{risk_level}**"
        )
        if risk_level == "high":
            st.error(msg)
        elif risk_level == "medium":
            st.warning(msg)
        else:
            st.info(msg)
