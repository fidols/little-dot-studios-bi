# LDS Dashboard — Plan 3: Time Tracking & Utilization

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `pages/1_Time_Tracking.py` — department utilization rates, monthly utilization trends, a budget vs actuals table, and an overrun alert panel.

**Architecture:** Three new utility functions are added to `utils/metrics.py` and unit tested first. The page reads filtered data from `st.session_state`, applies office-based filtering, and renders four sections. `budget_variance_df()` from Plan 1 is reused as-is for the table.

**Tech Stack:** Python 3.12, Streamlit ≥1.32.0, Plotly Express ≥5.18.0, pandas ≥2.0.0, pytest

---

## File Map

| File | Change |
|---|---|
| `utils/metrics.py` | Modify — add 3 functions |
| `tests/test_metrics.py` | Modify — add 5 tests (total ~52) |
| `pages/1_Time_Tracking.py` | Create |

---

## Task 1: New metric functions + tests

**Files:**
- Modify: `utils/metrics.py`
- Modify: `tests/test_metrics.py`

- [ ] **Step 1: Append failing tests to tests/test_metrics.py**

Add at the bottom of `tests/test_metrics.py`:

```python
from datetime import date as date_type
from utils.metrics import billable_hours_this_month, utilization_by_dept, monthly_utilization_trend


def _tl(log_id, date_val, hours, billable, dept="Production", emp_id="EMP0001"):
    return {
        "log_id": log_id, "employee_id": emp_id, "project_id": "PRJ0001",
        "date": date_val, "hours": hours, "billable": billable, "department": dept,
    }


def test_billable_hours_this_month_counts_current_month_only():
    df = pd.DataFrame([
        _tl("L1", date_type(2026, 5, 1), 8.0, True),
        _tl("L2", date_type(2026, 4, 30), 8.0, True),  # prior month — must be excluded
    ])
    assert billable_hours_this_month(df, date_type(2026, 5, 12)) == 8.0


def test_billable_hours_this_month_excludes_non_billable():
    df = pd.DataFrame([
        _tl("L1", date_type(2026, 5, 3), 8.0, True),
        _tl("L2", date_type(2026, 5, 4), 4.0, False),
    ])
    assert billable_hours_this_month(df, date_type(2026, 5, 12)) == 8.0


def test_utilization_by_dept_basic():
    df = pd.DataFrame([
        _tl("L1", date_type(2026, 5, 1), 8.0, True, "Production"),
        _tl("L2", date_type(2026, 5, 2), 4.0, False, "Production"),  # 8/12 ≈ 66.7%
        _tl("L3", date_type(2026, 5, 1), 6.0, True, "Strategy", "EMP0002"),  # 100%
    ])
    result = utilization_by_dept(df)
    prod = result[result["department"] == "Production"]["utilization_rate"].values[0]
    strat = result[result["department"] == "Strategy"]["utilization_rate"].values[0]
    assert abs(prod - 8 / 12) < 0.01
    assert abs(strat - 1.0) < 0.01


def test_utilization_by_dept_empty_returns_empty():
    df = pd.DataFrame(columns=["log_id", "employee_id", "project_id", "date", "hours", "billable", "department"])
    assert len(utilization_by_dept(df)) == 0


def test_monthly_utilization_trend_joins_office():
    timelogs = pd.DataFrame([
        _tl("L1", date_type(2026, 1, 5), 8.0, True),
        _tl("L2", date_type(2026, 1, 6), 4.0, False),  # UK Jan: 8/12 ≈ 66.7%
    ])
    employees = pd.DataFrame([{
        "employee_id": "EMP0001", "name": "E1", "department": "Production",
        "office": "UK", "role": "Mid", "loaded_cost_rate": 75,
    }])
    result = monthly_utilization_trend(timelogs, employees)
    assert len(result) == 1
    assert result.iloc[0]["office"] == "UK"
    assert abs(result.iloc[0]["utilization_rate"] - 8 / 12) < 0.01
```

- [ ] **Step 2: Run to confirm new tests fail**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && python -m pytest tests/test_metrics.py -v -k "billable or utilization_by_dept or trend"
```

Expected: 5 FAILED with `ImportError: cannot import name 'billable_hours_this_month'`

- [ ] **Step 3: Append the 3 new functions to utils/metrics.py**

```python
def billable_hours_this_month(timelog_df: pd.DataFrame, today) -> float:
    """Total billable hours logged in the same calendar month as today."""
    if timelog_df.empty:
        return 0.0
    df = timelog_df.copy()
    df["_date"] = pd.to_datetime(df["date"])
    mask = (
        (df["_date"].dt.year == today.year)
        & (df["_date"].dt.month == today.month)
        & df["billable"]
    )
    return float(df.loc[mask, "hours"].sum())


def utilization_by_dept(timelog_df: pd.DataFrame) -> pd.DataFrame:
    """
    Utilization rate (billable / total hours) per department.
    Returns DataFrame with columns: department, utilization_rate.
    Sorted descending by utilization_rate.
    """
    if timelog_df.empty:
        return pd.DataFrame(columns=["department", "utilization_rate"])
    result = []
    for dept, group in timelog_df.groupby("department"):
        total = group["hours"].sum()
        if total == 0:
            continue
        billable = group.loc[group["billable"], "hours"].sum()
        result.append({"department": dept, "utilization_rate": float(billable / total)})
    return (
        pd.DataFrame(result)
        .sort_values("utilization_rate", ascending=False)
        .reset_index(drop=True)
    )


def monthly_utilization_trend(
    timelog_df: pd.DataFrame,
    employee_df: pd.DataFrame,
    months: int = 12,
) -> pd.DataFrame:
    """
    Monthly utilization rate by office for the last `months` months.
    Joins timelog with employee_df to get office per employee.
    Returns DataFrame with columns: month (datetime), office, utilization_rate.
    """
    if timelog_df.empty:
        return pd.DataFrame(columns=["month", "office", "utilization_rate"])
    df = timelog_df.merge(
        employee_df[["employee_id", "office"]], on="employee_id", how="left"
    )
    df["_date"] = pd.to_datetime(df["date"])
    df["month"] = df["_date"].dt.to_period("M").dt.to_timestamp()
    result = []
    for (month, office), group in df.groupby(["month", "office"]):
        total = group["hours"].sum()
        if total == 0:
            continue
        billable = group.loc[group["billable"], "hours"].sum()
        result.append({
            "month": month,
            "office": str(office),
            "utilization_rate": float(billable / total),
        })
    return pd.DataFrame(result).sort_values(["month", "office"]).reset_index(drop=True)
```

- [ ] **Step 4: Run full test suite**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && python -m pytest tests/ -v
```

Expected: **52 PASSED** (47 existing + 5 new)

- [ ] **Step 5: Commit**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add utils/metrics.py tests/test_metrics.py
git commit -m "feat: add billable_hours_this_month, utilization_by_dept, monthly_utilization_trend — 52 tests"
```

---

## Task 2: Page scaffold + KPI cards

**Files:**
- Create: `pages/1_Time_Tracking.py`

- [ ] **Step 1: Create the pages/ directory and 1_Time_Tracking.py**

```bash
mkdir -p /Users/mr.fidols/github/little-dot-studios-bi/pages
```

Create `pages/1_Time_Tracking.py`:

```python
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
```

- [ ] **Step 2: Visually verify**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && streamlit run app.py
```

Navigate to "1 Time Tracking" in the sidebar. Expected: three KPI cards with realistic values.

- [ ] **Step 3: Commit**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add pages/1_Time_Tracking.py
git commit -m "feat: add Time Tracking page scaffold and KPI cards"
```

---

## Task 3: Utilization by department chart

**Files:**
- Modify: `pages/1_Time_Tracking.py`

- [ ] **Step 1: Append the department utilization section**

```python
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
```

- [ ] **Step 2: Visually verify**

Run `streamlit run app.py` and go to Time Tracking. Expected: horizontal bar chart with color-coded bars and two reference lines.

- [ ] **Step 3: Commit**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add pages/1_Time_Tracking.py
git commit -m "feat: add utilization by department chart to Time Tracking"
```

---

## Task 4: Monthly utilization trend

**Files:**
- Modify: `pages/1_Time_Tracking.py`

- [ ] **Step 1: Append the monthly trend section**

```python
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
```

- [ ] **Step 2: Visually verify**

Expected: multi-line chart with one line per selected office, showing utilization over the last 12 months.

- [ ] **Step 3: Commit**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add pages/1_Time_Tracking.py
git commit -m "feat: add monthly utilization trend to Time Tracking"
```

---

## Task 5: Budget vs actuals table + overrun alerts

**Files:**
- Modify: `pages/1_Time_Tracking.py`

- [ ] **Step 1: Append the budget table and overrun alert panel**

```python
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
    options=sorted(project_df["department"].unique()),
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
        project_df[project_df["department"].isin(dept_filter)]["project_name"]
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
```

- [ ] **Step 2: Visually verify**

Run `streamlit run app.py` and go to Time Tracking. Expected:
- Color-coded table with department/type filters
- Warning cards for each over-budget project showing name, client, hours over, cost impact

- [ ] **Step 3: Commit and push**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add pages/1_Time_Tracking.py
git commit -m "feat: add budget table and overrun alert panel — Time Tracking page complete"
git push origin main
```
