# LDS Dashboard — Plan 2: Overview Page (app.py)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `app.py` — the landing page that loads all simulated data once, shows the All3Media parent company context, LDS network KPIs, a revenue chart, and an office selector that persists across all pages.

**Architecture:** `app.py` is the Streamlit entry point. It calls `generate_all()` once per session and stores the result in `st.session_state["data"]` so all other pages can read it without re-running the generator. The office multiselect writes to `st.session_state["selected_offices"]`. No new utility functions are needed — all logic is already covered by the 47 tests from Plan 1. Verification for this plan is visual via `streamlit run app.py`.

**Tech Stack:** Python 3.12, Streamlit ≥1.32.0, Plotly Express ≥5.18.0, pandas ≥2.0.0

---

## File Map

| File | Change |
|---|---|
| `app.py` | Create |

No test files — pure Streamlit UI with no new utility functions.

---

## Task 1: app.py scaffold

**Files:**
- Create: `app.py`

- [ ] **Step 1: Create app.py with page config, data loading, and title**

Create `/Users/mr.fidols/github/little-dot-studios-bi/app.py`:

```python
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
```

- [ ] **Step 2: Verify the file is importable**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && python -c "
import sys
sys.path.insert(0, '.')
# Just check the non-streamlit imports resolve
from data.simulate import generate_all
from utils.metrics import revenue_by_stream
print('imports OK')
"
```

Expected: `imports OK`

- [ ] **Step 3: Commit**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add app.py
git commit -m "feat: add app.py scaffold with session state data loading"
```

---

## Task 2: All3Media pressure banner

**Files:**
- Modify: `app.py`

The All3Media banner tells the story that drives the whole dashboard: LDS's parent company just posted its worst year on record. This context explains why operational analytics matter.

Delta formatting rule: `delta="-10%"` must have the sign **before** the value (and before any currency symbol) so Streamlit parses it as negative and renders a red down arrow. Writing `delta="£-30.8M"` (sign after £) will not render the arrow correctly — the sign must come first: `delta="-£30.8M"`.

- [ ] **Step 1: Append the All3Media banner to app.py**

```python
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
```

- [ ] **Step 2: Run the app and visually confirm**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && streamlit run app.py
```

Expected:
- Three metric cards side by side
- "FY2024 YoY Change" shows `-10%` with a red down arrow
- "FY2024 Operating Result" shows `-£30.8M` with a red down arrow
- Caption appears below the cards

- [ ] **Step 3: Commit**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add app.py
git commit -m "feat: add All3Media pressure banner to overview page"
```

---

## Task 3: LDS Network KPI cards

**Files:**
- Modify: `app.py`

These four cards are anchored to real published data — they are not simulated.

- [ ] **Step 1: Append the LDS Network KPIs section after the All3Media banner**

```python
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
```

- [ ] **Step 2: Run the app and visually confirm**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && streamlit run app.py
```

Expected: Four KPI cards in a row — `$257.7M`, `419`, `930M`, `11.2B` — with caption below.

- [ ] **Step 3: Commit**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add app.py
git commit -m "feat: add LDS network KPI cards to overview page"
```

---

## Task 4: Office selector + Revenue by Stream chart

**Files:**
- Modify: `app.py`

The office selector is placed **before** the chart so changing it immediately updates the revenue breakdown below. The selected offices are written to `st.session_state["selected_offices"]` — this value is what all other pages will read to apply their filters.

Chart conventions:
- LDS brand red: `#E31837`
- Background white: `#FFFFFF`
- Font: `#1A1A1A`
- `use_container_width=True` — makes the chart span the full page width

- [ ] **Step 1: Append the office selector and revenue chart to app.py**

```python
st.divider()

# ── Office Filter ─────────────────────────────────────────────────────────────
st.subheader("Office Filter")
selected_offices = st.multiselect(
    "Select offices — this filter applies to all pages:",
    options=["UK", "US", "Germany", "ANZ"],
    default=st.session_state["selected_offices"],
)
if selected_offices:
    st.session_state["selected_offices"] = selected_offices
offices = st.session_state["selected_offices"]

st.divider()

# ── Revenue by Stream ─────────────────────────────────────────────────────────
st.subheader("Revenue by Stream")
st.caption(
    "Simulated FY2026 revenue breakdown calibrated to $257.7M total. "
    "Filtered by selected offices."
)

fin_df = data["financials_df"]
stream_df = revenue_by_stream(fin_df, offices=offices if offices else None)

fig = px.bar(
    stream_df.sort_values("revenue", ascending=False),
    x="revenue_stream",
    y="revenue",
    color_discrete_sequence=["#E31837"],
    labels={"revenue_stream": "Revenue Stream", "revenue": "Annual Revenue ($)"},
)
fig.update_layout(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font_color="#1A1A1A",
    xaxis_title="Revenue Stream",
    yaxis_title="Annual Revenue ($)",
    margin=dict(t=40, b=40),
)
st.plotly_chart(fig, use_container_width=True)
```

- [ ] **Step 2: Run the app and visually confirm**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && streamlit run app.py
```

Expected:
- Office multiselect appears with all 4 offices checked by default
- Red bar chart appears with 5 streams (Ad Revenue, Agency Retainers, Content Licensing, Content ID, Production Fees)
- Ad Revenue should be the tallest bar (40% share)
- Deselecting `Germany` (16% of revenue) reduces all bar heights proportionally

- [ ] **Step 3: Commit and push**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi
git add app.py
git commit -m "feat: add office selector and revenue by stream chart — overview page complete"
git push origin main
```

---

## Final app.py — complete reference

After all 4 tasks, `app.py` should contain exactly this (for review):

```python
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

st.divider()

# ── Office Filter ─────────────────────────────────────────────────────────────
st.subheader("Office Filter")
selected_offices = st.multiselect(
    "Select offices — this filter applies to all pages:",
    options=["UK", "US", "Germany", "ANZ"],
    default=st.session_state["selected_offices"],
)
if selected_offices:
    st.session_state["selected_offices"] = selected_offices
offices = st.session_state["selected_offices"]

st.divider()

# ── Revenue by Stream ─────────────────────────────────────────────────────────
st.subheader("Revenue by Stream")
st.caption(
    "Simulated FY2026 revenue breakdown calibrated to $257.7M total. "
    "Filtered by selected offices."
)

fin_df = data["financials_df"]
stream_df = revenue_by_stream(fin_df, offices=offices if offices else None)

fig = px.bar(
    stream_df.sort_values("revenue", ascending=False),
    x="revenue_stream",
    y="revenue",
    color_discrete_sequence=["#E31837"],
    labels={"revenue_stream": "Revenue Stream", "revenue": "Annual Revenue ($)"},
)
fig.update_layout(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font_color="#1A1A1A",
    xaxis_title="Revenue Stream",
    yaxis_title="Annual Revenue ($)",
    margin=dict(t=40, b=40),
)
st.plotly_chart(fig, use_container_width=True)
```
