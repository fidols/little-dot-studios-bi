import streamlit as st
import plotly.express as px
from datetime import date

from utils.metrics import (
    utilization_rate,
    billable_hours_this_month,
    budget_variance_df,
    utilization_by_dept,
    monthly_utilization_trend,
)

TODAY = date(2026, 5, 12)

# ── Session state guard ───────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.warning("Please start from the Overview page to load data.")
    st.stop()

data = st.session_state["data"]
offices = st.session_state.get("selected_offices", ["UK", "US", "Germany", "ANZ"])

employee_df = data["employee_df"]
timelog_df = data["timelog_df"]
project_df = data["project_df"]
client_df = data["client_df"]

# Filter by selected offices
emp_filtered = employee_df[employee_df["office"].isin(offices)]
timelog_filtered = timelog_df[timelog_df["employee_id"].isin(emp_filtered["employee_id"])]
project_filtered = project_df[project_df["office"].isin(offices)]

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("Time Tracking & Utilization")
st.caption("Stakeholders: Operations · Department Heads · Finance")

st.divider()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
util = utilization_rate(timelog_filtered, emp_filtered)
billable_mtd = billable_hours_this_month(timelog_filtered, TODAY)
variance_df = budget_variance_df(project_filtered)
overrun_count = int((variance_df["status"] == "Over Budget").sum())

c1, c2, c3 = st.columns(3)
c1.metric("Overall Utilization Rate", f"{util:.1%}")
c2.metric("Billable Hours (May 2026)", f"{billable_mtd:,.0f}")
c3.metric(
    "Projects Over Budget",
    str(overrun_count),
    delta=f"-{overrun_count}" if overrun_count > 0 else "0",
    delta_color="inverse",
)

st.divider()

# ── Utilization by Department ─────────────────────────────────────────────────
st.subheader("Utilization by Department")
st.caption("Green = at or above 75% target. Amber = 55–74%. Red = below 55% industry average.")

dept_df = utilization_by_dept(timelog_filtered)
dept_df["color"] = dept_df["utilization_rate"].apply(
    lambda r: "#16A34A" if r >= 0.75 else "#F59E0B" if r >= 0.55 else "#E31837"
)

fig_dept = px.bar(
    dept_df,
    x="utilization_rate",
    y="department",
    orientation="h",
    color="color",
    color_discrete_map="identity",
    labels={"utilization_rate": "Utilization Rate", "department": "Department"},
)
fig_dept.add_vline(
    x=0.75, line_dash="dash", line_color="#1A1A1A",
    annotation_text="Target (75%)", annotation_position="top right",
)
fig_dept.add_vline(
    x=0.55, line_dash="dot", line_color="#6D6E71",
    annotation_text="Industry Avg (55%)", annotation_position="bottom right",
)
fig_dept.update_layout(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font_color="#1A1A1A",
    showlegend=False,
    xaxis_tickformat=".0%",
    xaxis_range=[0, 1.05],
)
st.plotly_chart(fig_dept, use_container_width=True)

st.divider()

# ── Monthly Utilization Trend ─────────────────────────────────────────────────
st.subheader("Monthly Utilization Trend")
st.caption("Last 12 months by office. F1 season (Mar–Nov) and high-event periods typically drive peaks.")

trend_df = monthly_utilization_trend(timelog_filtered, emp_filtered)

fig_trend = px.line(
    trend_df,
    x="month",
    y="utilization_rate",
    color="office",
    color_discrete_map={
        "UK": "#E31837",
        "US": "#1A1A1A",
        "Germany": "#6D6E71",
        "ANZ": "#94A3B8",
    },
    labels={"month": "Month", "utilization_rate": "Utilization Rate", "office": "Office"},
    markers=True,
)
fig_trend.update_layout(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font_color="#1A1A1A",
    yaxis_tickformat=".0%",
)
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# ── Budget vs Actuals ─────────────────────────────────────────────────────────
st.subheader("Budget vs Actuals")
st.caption("% Burned = actual hours / estimated hours. Color coding: green = on track, amber = at risk, red = over budget.")

display_df = variance_df.merge(
    client_df[["client_id", "client_name"]], on="client_id", how="left"
)
table_cols = [
    "project_name", "client_name", "project_type",
    "estimated_hours", "actual_hours", "pct_burned",
    "budget", "actual_cost", "status",
]
display_df = display_df[table_cols].rename(columns={
    "project_name": "Project",
    "client_name": "Client",
    "project_type": "Type",
    "estimated_hours": "Est. Hours",
    "actual_hours": "Actual Hours",
    "pct_burned": "% Burned",
    "budget": "Budget ($)",
    "actual_cost": "Actual Cost ($)",
    "status": "Status",
})

col_dept, col_type = st.columns(2)
dept_filter = col_dept.multiselect(
    "Filter by department:",
    options=sorted(project_filtered["department"].unique()),
    default=[],
)
type_filter = col_type.multiselect(
    "Filter by project type:",
    options=["Retainer", "Production", "Licensing", "Content ID"],
    default=[],
)

filtered_table = display_df.copy()
if dept_filter:
    filtered_table = filtered_table[filtered_table["Project"].isin(
        project_filtered[project_filtered["department"].isin(dept_filter)]["project_name"]
    )]
if type_filter:
    filtered_table = filtered_table[filtered_table["Type"].isin(type_filter)]


def _row_color(row):
    if row["Status"] == "Over Budget":
        return ["background-color: #fde8e8"] * len(row)
    elif row["Status"] == "At Risk":
        return ["background-color: #fef9c3"] * len(row)
    return [""] * len(row)


styled = (
    filtered_table.style
    .apply(_row_color, axis=1)
    .format({
        "% Burned": "{:.1%}",
        "Budget ($)": "${:,.0f}",
        "Actual Cost ($)": "${:,.0f}",
    })
)
st.dataframe(styled, use_container_width=True)

st.divider()

# ── Overrun Alert Panel ────────────────────────────────────────────────────────
overrun_df = variance_df[variance_df["status"] == "Over Budget"].merge(
    client_df[["client_id", "client_name"]], on="client_id", how="left"
)

if len(overrun_df) > 0:
    st.subheader(f"Overrun Alerts — {len(overrun_df)} Project(s) Over Budget")
    for _, row in overrun_df.iterrows():
        cost_impact = round(row["hours_over"] * 75)  # approximate using avg loaded cost rate
        st.warning(
            f"**{row['project_name']}** ({row['client_name']}) — "
            f"{int(row['hours_over'])} hours over estimate · "
            f"Est. cost impact: ${cost_impact:,.0f}"
        )
else:
    st.success("No projects currently over budget.")
