# LDS Dashboard — Plan 5: Client & CRM

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `pages/3_Client_CRM.py` — client health KPIs, a health matrix scatter plot, a client tier table with CSV download, a pipeline funnel, and a renewal calendar.

**Architecture:** Three new utility functions are added to `utils/metrics.py` first. The health matrix uses `client_df` directly. The renewal calendar uses `clients_expiring_soon()`. Pipeline and CRM data come from session state.

**Tech Stack:** Python 3.12, Streamlit ≥1.32.0, Plotly Express ≥5.18.0, pandas ≥2.0.0, pytest

---

## File Map

| File | Change |
|---|---|
| `utils/metrics.py` | Modify — add 3 functions |
| `tests/test_metrics.py` | Modify — add 4 tests (total ~64) |
| `pages/3_Client_CRM.py` | Create |

---

## Task 1: New metric functions + tests

**Files:**
- Modify: `utils/metrics.py`
- Modify: `tests/test_metrics.py`

- [ ] **Step 1: Append failing tests to tests/test_metrics.py**

```python
from datetime import date as date_type
from utils.metrics import avg_contract_value, clients_expiring_soon, revenue_at_risk


def test_avg_contract_value_basic():
    df = pd.DataFrame([
        {"client_id": "C1", "annual_revenue": 1_000_000, "status": "Active"},
        {"client_id": "C2", "annual_revenue": 3_000_000, "status": "Active"},
    ])
    assert avg_contract_value(df) == 2_000_000.0


def test_avg_contract_value_empty_returns_zero():
    df = pd.DataFrame(columns=["client_id", "annual_revenue", "status"])
    assert avg_contract_value(df) == 0.0


def test_clients_expiring_soon_filters_by_window():
    today = date_type(2026, 5, 12)
    df = pd.DataFrame([
        {"client_id": "C1", "client_name": "A", "tier": "Platinum", "contract_type": "Retainer",
         "annual_revenue": 500_000, "margin_pct": 0.35, "renewal_date": date_type(2026, 7, 1),
         "last_contact_date": date_type(2026, 5, 1), "engagement_score": 80, "status": "Active"},
        {"client_id": "C2", "client_name": "B", "tier": "Gold", "contract_type": "Retainer",
         "annual_revenue": 200_000, "margin_pct": 0.30, "renewal_date": date_type(2026, 12, 1),
         "last_contact_date": date_type(2026, 5, 1), "engagement_score": 65, "status": "Active"},
    ])
    result = clients_expiring_soon(df, days=90, today=today)
    # C1 renewal is Jul 1 = 50 days from May 12 — within 90 days
    # C2 renewal is Dec 1 = 203 days from May 12 — outside 90 days
    assert len(result) == 1
    assert result.iloc[0]["client_id"] == "C1"


def test_revenue_at_risk_sums_expiring_revenue():
    today = date_type(2026, 5, 12)
    df = pd.DataFrame([
        {"client_id": "C1", "client_name": "A", "tier": "Platinum", "contract_type": "Retainer",
         "annual_revenue": 500_000, "margin_pct": 0.35, "renewal_date": date_type(2026, 7, 1),
         "last_contact_date": date_type(2026, 5, 1), "engagement_score": 80, "status": "Active"},
        {"client_id": "C2", "client_name": "B", "tier": "Gold", "contract_type": "Retainer",
         "annual_revenue": 200_000, "margin_pct": 0.30, "renewal_date": date_type(2026, 12, 1),
         "last_contact_date": date_type(2026, 5, 1), "engagement_score": 65, "status": "Active"},
    ])
    result = revenue_at_risk(df, days=90, today=today)
    assert result == 500_000.0
```

- [ ] **Step 2: Run to confirm new tests fail**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && python -m pytest tests/test_metrics.py -v -k "contract or expiring or at_risk"
```

Expected: 4 FAILED with `ImportError`

- [ ] **Step 3: Append the 3 new functions to utils/metrics.py**

```python
def avg_contract_value(client_df: pd.DataFrame) -> float:
    """Mean annual_revenue across all clients."""
    if client_df.empty:
        return 0.0
    return float(client_df["annual_revenue"].mean())


def clients_expiring_soon(
    client_df: pd.DataFrame, days: int = 90, today=None
) -> pd.DataFrame:
    """
    Clients whose renewal_date falls within `days` days from today (inclusive).
    Returns the filtered subset of client_df (no extra columns).
    """
    from datetime import date as _date
    if today is None:
        today = _date(2026, 5, 12)
    df = client_df.copy()
    df["_renewal"] = pd.to_datetime(df["renewal_date"])
    today_ts = pd.Timestamp(today)
    cutoff = today_ts + pd.Timedelta(days=days)
    mask = (df["_renewal"] >= today_ts) & (df["_renewal"] <= cutoff)
    return df[mask].drop(columns=["_renewal"]).reset_index(drop=True)


def revenue_at_risk(
    client_df: pd.DataFrame, days: int = 90, today=None
) -> float:
    """Total annual_revenue of clients renewing within `days` days."""
    expiring = clients_expiring_soon(client_df, days=days, today=today)
    return float(expiring["annual_revenue"].sum())
```

- [ ] **Step 4: Run full test suite**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && python -m pytest tests/ -v
```

Expected: **64 PASSED** (60 existing + 4 new)

- [ ] **Step 5: Commit**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add utils/metrics.py tests/test_metrics.py
git commit -m "feat: add avg_contract_value, clients_expiring_soon, revenue_at_risk — 64 tests"
```

---

## Task 2: Page scaffold + KPI cards

**Files:**
- Create: `pages/3_Client_CRM.py`

- [ ] **Step 1: Create 3_Client_CRM.py**

```python
import streamlit as st
import plotly.express as px
from datetime import date

from utils.metrics import (
    pipeline_value,
    renewal_rate,
    avg_contract_value,
    clients_expiring_soon,
    revenue_at_risk,
)

TODAY = date(2026, 5, 12)

# ── Session state guard ───────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.warning("Please start from the Overview page to load data.")
    st.stop()

data = st.session_state["data"]
offices = st.session_state.get("selected_offices", ["UK", "US", "Germany", "ANZ"])

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
```

- [ ] **Step 2: Visually verify**

Run `streamlit run app.py`, navigate to "3 Client CRM". Expected: 4 KPI cards.

- [ ] **Step 3: Commit**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add pages/3_Client_CRM.py
git commit -m "feat: add Client CRM page scaffold and KPI cards"
```

---

## Task 3: Client health matrix + tier table

**Files:**
- Modify: `pages/3_Client_CRM.py`

- [ ] **Step 1: Append the health matrix scatter and tier table**

```python
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
eng_mid = 65

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
```

- [ ] **Step 2: Visually verify**

Expected: scatter plot with quadrant labels and colored dots by tier; sortable table with status filter and download button.

- [ ] **Step 3: Commit**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add pages/3_Client_CRM.py
git commit -m "feat: add client health matrix and tier table to CRM page"
```

---

## Task 4: Pipeline chart + renewal calendar

**Files:**
- Modify: `pages/3_Client_CRM.py`

- [ ] **Step 1: Append the pipeline and renewal sections**

```python
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
        risk_level = "high" if row["engagement_score"] < 50 else "medium" if row["engagement_score"] < 70 else "low"
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
```

- [ ] **Step 2: Visually verify**

Expected:
- Bar chart across all 5 pipeline stages with win rate caption
- Revenue at risk metric card
- Color-coded renewal cards (red = high risk, amber = medium, blue = low)

- [ ] **Step 3: Commit and push**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add pages/3_Client_CRM.py
git commit -m "feat: add pipeline chart and renewal calendar — Client CRM page complete"
git push origin main
```
