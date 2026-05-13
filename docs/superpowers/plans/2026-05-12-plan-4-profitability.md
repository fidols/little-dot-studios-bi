# LDS Dashboard — Plan 4: Profitability & Finance

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `pages/2_Profitability.py` — margin KPIs, revenue vs cost trend, margin by client tier and project type, and an interactive new business pricing tool.

**Architecture:** Five new utility functions are added to `utils/metrics.py` (and tested) before any UI work. The pricing tool uses only data from `utils/metrics.py` — no business logic in the page file. All charts use LDS brand colors.

**Tech Stack:** Python 3.12, Streamlit ≥1.32.0, Plotly Express ≥5.18.0, pandas ≥2.0.0, pytest

---

## File Map

| File | Change |
|---|---|
| `utils/metrics.py` | Modify — add 5 functions + 2 constants |
| `tests/test_metrics.py` | Modify — add 8 tests (total ~60) |
| `pages/2_Profitability.py` | Create |

---

## Task 1: New metric functions + tests

**Files:**
- Modify: `utils/metrics.py`
- Modify: `tests/test_metrics.py`

- [ ] **Step 1: Append failing tests to tests/test_metrics.py**

```python
from utils.metrics import (
    margin_delta_qoq,
    monthly_financials_trend,
    margin_by_tier,
    margin_by_project_type,
    pricing_estimate,
)


def _make_financials(months_revenue):
    """months_revenue: list of (month_str, office, stream, revenue, direct_cost, labor_cost)"""
    rows = []
    for m, office, stream, rev, dc, lc in months_revenue:
        rows.append({
            "month": m, "office": office, "revenue_stream": stream,
            "revenue": rev, "direct_cost": dc, "labor_cost": lc,
        })
    return pd.DataFrame(rows)


def test_margin_delta_qoq_positive_trend():
    # Q1 (Jan-Mar): margin 30%, Q2 (Apr-Jun): margin 40% → delta = +10%
    rows = []
    for m, rev, cost in [
        ("2026-01-01", 100, 70), ("2026-02-01", 100, 70), ("2026-03-01", 100, 70),
        ("2026-04-01", 100, 60), ("2026-05-01", 100, 60), ("2026-06-01", 100, 60),
    ]:
        rows.append({"month": m, "office": "UK", "revenue_stream": "Ad Revenue",
                     "revenue": rev, "direct_cost": cost / 2, "labor_cost": cost / 2})
    df = pd.DataFrame(rows)
    result = margin_delta_qoq(df)
    assert abs(result - 0.10) < 0.01


def test_margin_delta_qoq_insufficient_data_returns_zero():
    rows = [{"month": "2026-01-01", "office": "UK", "revenue_stream": "Ad Revenue",
              "revenue": 100, "direct_cost": 30, "labor_cost": 30}]
    df = pd.DataFrame(rows)
    assert margin_delta_qoq(df) == 0.0


def test_monthly_financials_trend_groups_correctly():
    df = _make_financials([
        ("2026-01-01", "UK", "Ad Revenue", 1000, 200, 300),
        ("2026-01-01", "US", "Ad Revenue", 500, 100, 150),  # same month, different office
        ("2026-02-01", "UK", "Ad Revenue", 800, 160, 240),
    ])
    result = monthly_financials_trend(df)
    jan = result[result["month"] == pd.Timestamp("2026-01-01")]
    assert jan["revenue"].values[0] == 1500
    assert len(result) == 2  # 2 distinct months


def test_margin_by_tier_correct():
    projects = pd.DataFrame([
        {"project_id": "P1", "client_id": "C1", "revenue": 100, "actual_cost": 60,
         "project_type": "Retainer", "office": "UK", "project_name": "P1",
         "department": "Production", "start_date": "2026-01-01", "end_date": "2026-03-31",
         "estimated_hours": 100, "actual_hours": 80, "budget": 70, "status": "Active"},
    ])
    clients = pd.DataFrame([
        {"client_id": "C1", "client_name": "Acme", "tier": "Platinum",
         "contract_type": "Retainer", "annual_revenue": 1_000_000, "margin_pct": 0.40,
         "renewal_date": "2027-01-01", "last_contact_date": "2026-05-01",
         "engagement_score": 85, "status": "Active"},
    ])
    result = margin_by_tier(projects, clients)
    plat = result[result["tier"] == "Platinum"]["avg_margin_pct"].values[0]
    assert abs(plat - 0.40) < 0.01


def test_margin_by_project_type_correct():
    projects = pd.DataFrame([
        {"project_id": "P1", "client_id": "C1", "revenue": 200, "actual_cost": 120,
         "project_type": "Retainer", "office": "UK", "project_name": "P1",
         "department": "Production", "start_date": "2026-01-01", "end_date": "2026-03-31",
         "estimated_hours": 100, "actual_hours": 80, "budget": 130, "status": "Active"},
        {"project_id": "P2", "client_id": "C1", "revenue": 100, "actual_cost": 80,
         "project_type": "Production", "office": "UK", "project_name": "P2",
         "department": "Production", "start_date": "2026-01-01", "end_date": "2026-03-31",
         "estimated_hours": 80, "actual_hours": 90, "budget": 90, "status": "Active"},
    ])
    result = margin_by_project_type(projects)
    retainer = result[result["project_type"] == "Retainer"]["avg_margin_pct"].values[0]
    production = result[result["project_type"] == "Production"]["avg_margin_pct"].values[0]
    assert abs(retainer - 0.40) < 0.01   # (200-120)/200
    assert abs(production - 0.20) < 0.01  # (100-80)/100


def test_pricing_estimate_returns_expected_keys():
    projects = pd.DataFrame(columns=[
        "project_id", "project_name", "client_id", "project_type", "office",
        "department", "start_date", "end_date", "estimated_hours", "actual_hours",
        "budget", "actual_cost", "revenue", "status",
    ])
    result = pricing_estimate("Retainer", weeks=4, team_size=3, seniority_mix="Balanced", project_df=projects)
    assert "floor_price" in result
    assert "recommended_price" in result
    assert "hours_breakdown" in result
    assert "comparable_count" in result


def test_pricing_estimate_floor_below_recommended():
    projects = pd.DataFrame(columns=[
        "project_id", "project_name", "client_id", "project_type", "office",
        "department", "start_date", "end_date", "estimated_hours", "actual_hours",
        "budget", "actual_cost", "revenue", "status",
    ])
    result = pricing_estimate("Production", weeks=8, team_size=4, seniority_mix="Senior-heavy", project_df=projects)
    assert result["floor_price"] < result["recommended_price"]
    assert result["total_hours"] > 0
```

- [ ] **Step 2: Run to confirm new tests fail**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && python -m pytest tests/test_metrics.py -v -k "margin or financial or pricing"
```

Expected: 8 FAILED with `ImportError`

- [ ] **Step 3: Append the 5 new functions to utils/metrics.py**

```python
# Pricing tool constants
SENIORITY_MIXES = {
    "Junior-heavy": {"Junior": 0.50, "Mid": 0.35, "Senior": 0.10, "Lead": 0.05},
    "Balanced":     {"Junior": 0.25, "Mid": 0.40, "Senior": 0.25, "Lead": 0.10},
    "Senior-heavy": {"Junior": 0.10, "Mid": 0.25, "Senior": 0.45, "Lead": 0.20},
}
_LOADED_COST_RATES = {"Junior": 45, "Mid": 75, "Senior": 110, "Lead": 140}
_BILLABLE_HOURS_PER_PERSON_PER_WEEK = 30  # ~75% of 40h week
_TARGET_MARGIN = 0.30
_MIN_MARGIN = 0.20


def margin_delta_qoq(financials_df: pd.DataFrame, offices: list = None) -> float:
    """
    Gross margin delta: current quarter minus prior quarter.
    Positive = improving. Returns 0.0 if fewer than 6 months of data.
    Margin = (revenue - direct_cost - labor_cost) / revenue.
    """
    df = financials_df if offices is None else financials_df[financials_df["office"].isin(offices)]
    df = df.copy()
    df["_month"] = pd.to_datetime(df["month"])
    months = sorted(df["_month"].dt.to_period("M").unique())
    if len(months) < 6:
        return 0.0
    curr_months = months[-3:]
    prev_months = months[-6:-3]

    def _qmargin(month_list):
        mask = df["_month"].dt.to_period("M").isin(month_list)
        q = df[mask]
        rev = q["revenue"].sum()
        cost = q["direct_cost"].sum() + q["labor_cost"].sum()
        return (rev - cost) / rev if rev > 0 else 0.0

    return float(_qmargin(curr_months) - _qmargin(prev_months))


def monthly_financials_trend(
    financials_df: pd.DataFrame, offices: list = None
) -> pd.DataFrame:
    """
    Monthly totals for revenue, direct_cost, labor_cost.
    Returns DataFrame sorted by month with columns: month, revenue, direct_cost, labor_cost.
    """
    df = financials_df if offices is None else financials_df[financials_df["office"].isin(offices)]
    df = df.copy()
    df["month"] = pd.to_datetime(df["month"])
    return (
        df.groupby("month")
        .agg(
            revenue=("revenue", "sum"),
            direct_cost=("direct_cost", "sum"),
            labor_cost=("labor_cost", "sum"),
        )
        .reset_index()
        .sort_values("month")
    )


def margin_by_tier(project_df: pd.DataFrame, client_df: pd.DataFrame) -> pd.DataFrame:
    """
    Average project margin % by client tier (Platinum / Gold / Silver).
    Returns DataFrame with columns: tier, avg_margin_pct.
    """
    merged = project_df.merge(client_df[["client_id", "tier"]], on="client_id", how="left")
    merged["margin"] = (merged["revenue"] - merged["actual_cost"]) / merged["revenue"].replace(0, float("nan"))
    return (
        merged.groupby("tier")["margin"]
        .mean()
        .reset_index()
        .rename(columns={"margin": "avg_margin_pct"})
    )


def margin_by_project_type(project_df: pd.DataFrame) -> pd.DataFrame:
    """
    Average project margin % by project type (Retainer / Production / Licensing / Content ID).
    Returns DataFrame with columns: project_type, avg_margin_pct.
    """
    df = project_df.copy()
    df["margin"] = (df["revenue"] - df["actual_cost"]) / df["revenue"].replace(0, float("nan"))
    return (
        df.groupby("project_type")["margin"]
        .mean()
        .reset_index()
        .rename(columns={"margin": "avg_margin_pct"})
    )


def pricing_estimate(
    project_type: str,
    weeks: int,
    team_size: int,
    seniority_mix: str,
    project_df: pd.DataFrame,
) -> dict:
    """
    Estimate floor price, recommended price, and hours breakdown for a new project.

    Returns dict:
        floor_price: cost / (1 - 20% min margin)
        recommended_price: cost / (1 - 30% target margin)
        hours_breakdown: {role: hours}
        total_hours: int
        total_cost: int
        comparable_count: int — past projects with same type and similar hours
    """
    mix = SENIORITY_MIXES[seniority_mix]
    total_hours = weeks * team_size * _BILLABLE_HOURS_PER_PERSON_PER_WEEK
    hours_breakdown = {}
    total_cost = 0.0
    for role, share in mix.items():
        role_hours = round(total_hours * share)
        hours_breakdown[role] = role_hours
        total_cost += role_hours * _LOADED_COST_RATES[role]
    comparable = project_df[
        (project_df["project_type"] == project_type)
        & (project_df["actual_hours"].between(total_hours * 0.5, total_hours * 2.0))
    ]
    return {
        "floor_price": round(total_cost / (1 - _MIN_MARGIN)),
        "recommended_price": round(total_cost / (1 - _TARGET_MARGIN)),
        "hours_breakdown": hours_breakdown,
        "total_hours": total_hours,
        "total_cost": round(total_cost),
        "comparable_count": len(comparable),
    }
```

- [ ] **Step 4: Run full test suite**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && python -m pytest tests/ -v
```

Expected: **60 PASSED** (52 existing + 8 new)

- [ ] **Step 5: Commit**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add utils/metrics.py tests/test_metrics.py
git commit -m "feat: add margin, pricing, and financials trend functions — 60 tests"
```

---

## Task 2: Page scaffold + KPI cards

**Files:**
- Create: `pages/2_Profitability.py`

- [ ] **Step 1: Create 2_Profitability.py**

```python
import streamlit as st
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
```

- [ ] **Step 2: Visually verify**

Run `streamlit run app.py` and navigate to "2 Profitability". Expected: info banner + 4 KPI cards.

- [ ] **Step 3: Commit**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add pages/2_Profitability.py
git commit -m "feat: add Profitability page scaffold, banner, and KPI cards"
```

---

## Task 3: Revenue vs cost stacked area chart

**Files:**
- Modify: `pages/2_Profitability.py`

- [ ] **Step 1: Append the revenue vs cost section**

```python
st.divider()

# ── Revenue vs Cost Over Time ─────────────────────────────────────────────────
st.subheader("Revenue vs Cost Over Time")
st.caption("The gap between revenue and combined costs = gross margin. Narrowing gap = margin compression.")

trend_df = monthly_financials_trend(financials_filtered)
trend_df["total_cost"] = trend_df["direct_cost"] + trend_df["labor_cost"]

# Melt for stacked area
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
st.plotly_chart(fig_area, use_container_width=True)
```

- [ ] **Step 2: Visually verify**

Expected: stacked area chart with revenue (red) clearly above combined costs, showing the margin gap.

- [ ] **Step 3: Commit**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add pages/2_Profitability.py
git commit -m "feat: add revenue vs cost stacked area chart to Profitability"
```

---

## Task 4: Margin by tier + project type charts

**Files:**
- Modify: `pages/2_Profitability.py`

- [ ] **Step 1: Append the two margin charts**

```python
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
    st.plotly_chart(fig_type, use_container_width=True)
```

- [ ] **Step 2: Visually verify**

Expected: two side-by-side bar charts — tier chart (Platinum/Gold/Silver) and project type chart, both with 30% reference lines.

- [ ] **Step 3: Commit**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add pages/2_Profitability.py
git commit -m "feat: add margin by tier and project type charts to Profitability"
```

---

## Task 5: New business pricing tool

**Files:**
- Modify: `pages/2_Profitability.py`

- [ ] **Step 1: Append the pricing tool section**

```python
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
```

- [ ] **Step 2: Visually verify**

Run `streamlit run app.py` and go to Profitability. Expected:
- Four inputs: project type, weeks slider, team size slider, seniority mix
- Three output metrics (floor price, recommended price, hours)
- Info callout with comparable project count
- Expandable hours breakdown

- [ ] **Step 3: Commit and push**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add pages/2_Profitability.py
git commit -m "feat: add pricing tool — Profitability page complete"
git push origin main
```
