# LDS Dashboard — Plan 1: Foundation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold the project, generate all simulated data calibrated to real LDS figures, and implement shared KPI utility functions — all test-driven.

**Architecture:** A seeded NumPy generator in `data/simulate.py` produces six DataFrames (employees, clients, projects, time logs, pipeline, financials) calibrated to $257.7M revenue and 419 employees. Pure KPI functions in `utils/metrics.py` are consumed by all pages. No Streamlit code in this plan.

**Tech Stack:** Python 3.12, pandas, NumPy, pytest

---

## File Map

| File | Change |
|---|---|
| `requirements.txt` | Create |
| `.gitignore` | Create |
| `tests/__init__.py` | Create |
| `tests/conftest.py` | Create |
| `data/__init__.py` | Create |
| `data/simulate.py` | Create |
| `utils/__init__.py` | Create |
| `utils/metrics.py` | Create |
| `tests/test_simulate.py` | Create |
| `tests/test_metrics.py` | Create |

---

## Task 1: Project scaffold

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `tests/__init__.py`
- Create: `data/__init__.py`
- Create: `utils/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
streamlit>=1.32.0
pandas>=2.0.0
numpy>=1.26.0
plotly>=5.18.0
```

- [ ] **Step 2: Create .gitignore**

```
__pycache__/
*.pyc
.env
.venv/
venv/
*.egg-info/
.DS_Store
.streamlit/secrets.toml
```

- [ ] **Step 3: Create empty init files**

```bash
touch tests/__init__.py data/__init__.py utils/__init__.py
```

- [ ] **Step 4: Verify structure**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && find . -name "*.py" | sort
```

Expected output includes:
```
./data/__init__.py
./tests/__init__.py
./utils/__init__.py
```

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .gitignore tests/__init__.py data/__init__.py utils/__init__.py
git commit -m "chore: scaffold project structure"
```

---

## Task 2: Employee & client simulation (TDD)

**Files:**
- Create: `tests/test_simulate.py` (employee + client tests only)
- Create: `data/simulate.py` (employee + client generators only)

- [ ] **Step 1: Write failing tests**

Create `tests/test_simulate.py`:

```python
import pandas as pd
import pytest
from data.simulate import generate_employees, generate_clients


# --- Employees ---

def test_employees_columns():
    df = generate_employees()
    assert list(df.columns) == [
        "employee_id", "name", "department", "office", "role", "loaded_cost_rate"
    ]


def test_employees_total_headcount():
    df = generate_employees()
    assert len(df) == 419


def test_employees_office_distribution():
    df = generate_employees()
    counts = df["office"].value_counts()
    assert counts["UK"] == 220
    assert counts["US"] == 90
    assert counts["Germany"] == 65
    assert counts["ANZ"] == 44


def test_employees_no_nulls():
    df = generate_employees()
    assert df.isnull().sum().sum() == 0


def test_employees_loaded_cost_rate_positive():
    df = generate_employees()
    assert (df["loaded_cost_rate"] > 0).all()


# --- Clients ---

def test_clients_columns():
    df = generate_clients()
    assert list(df.columns) == [
        "client_id", "client_name", "tier", "contract_type",
        "annual_revenue", "margin_pct", "renewal_date",
        "last_contact_date", "engagement_score", "status"
    ]


def test_clients_tier_counts():
    df = generate_clients()
    counts = df["tier"].value_counts()
    assert counts["Platinum"] == 8
    assert counts["Gold"] == 15
    assert counts["Silver"] == 17


def test_clients_engagement_score_range():
    df = generate_clients()
    assert (df["engagement_score"] >= 0).all()
    assert (df["engagement_score"] <= 100).all()


def test_clients_no_nulls():
    df = generate_clients()
    assert df.isnull().sum().sum() == 0


def test_clients_status_valid():
    df = generate_clients()
    assert set(df["status"].unique()).issubset({"Active", "At Risk", "Churned"})
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && python -m pytest tests/test_simulate.py -v
```

Expected: 10 FAILED with `ModuleNotFoundError: No module named 'data.simulate'`

- [ ] **Step 3: Implement employee + client generators**

Create `data/simulate.py`:

```python
import numpy as np
import pandas as pd
from datetime import date, timedelta

SEED = 42
RNG = np.random.default_rng(SEED)

OFFICES = ["UK", "US", "Germany", "ANZ"]
OFFICE_HEADCOUNT = {"UK": 220, "US": 90, "Germany": 65, "ANZ": 44}
DEPARTMENTS = ["Production", "Strategy", "Distribution", "Sales", "Operations"]
DEPT_WEIGHTS = [0.35, 0.20, 0.15, 0.15, 0.15]
ROLES = ["Junior", "Mid", "Senior", "Lead"]
ROLE_WEIGHTS = [0.30, 0.40, 0.20, 0.10]
LOADED_COST_RATES = {"Junior": 45, "Mid": 75, "Senior": 110, "Lead": 140}

CLIENT_TIERS = ["Platinum", "Gold", "Silver"]
TIER_COUNTS = {"Platinum": 8, "Gold": 15, "Silver": 17}
TIER_REVENUE_RANGE = {
    "Platinum": (3_000_000, 8_000_000),
    "Gold": (500_000, 3_000_000),
    "Silver": (50_000, 500_000),
}
CONTRACT_TYPES = ["Retainer", "Production", "Mixed"]
PIPELINE_STAGES = ["Prospecting", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
PROJECT_TYPES = ["Retainer", "Production", "Licensing", "Content ID"]

ANNUAL_REVENUE = 257_700_000
TODAY = date(2026, 5, 12)


def generate_employees() -> pd.DataFrame:
    """Generate 419 employees across 4 offices."""
    rng = np.random.default_rng(SEED)
    rows = []
    emp_id = 1
    for office, count in OFFICE_HEADCOUNT.items():
        depts = rng.choice(DEPARTMENTS, size=count, p=DEPT_WEIGHTS)
        roles = rng.choice(ROLES, size=count, p=ROLE_WEIGHTS)
        for i in range(count):
            rows.append({
                "employee_id": f"EMP{emp_id:04d}",
                "name": f"Employee {emp_id}",
                "department": depts[i],
                "office": office,
                "role": roles[i],
                "loaded_cost_rate": LOADED_COST_RATES[roles[i]],
            })
            emp_id += 1
    return pd.DataFrame(rows)


def generate_clients() -> pd.DataFrame:
    """Generate 40 clients across Platinum / Gold / Silver tiers."""
    rng = np.random.default_rng(SEED + 1)
    rows = []
    client_id = 1

    # Real-ish client names anchored to known LDS client types
    client_name_pools = {
        "Platinum": [
            "Warner Bros. Digital", "Disney Content Hub", "NBCUniversal Archive",
            "ZDF Studios International", "BBC Studios Digital", "Sony Pictures Network",
            "Formula 1 Media", "IOC Digital",
        ],
        "Gold": [
            "McLaren Racing", "Coca-Cola Brand", "Hugo Boss Content", "Vodafone Media",
            "Land Rover Digital", "Cineverse Entertainment", "Acast Podcasts",
            "History Hit Network", "Channel 4 Archive", "ITV Studios Digital",
            "America's Cup", "Sky Sports Digital", "BT Sport Content",
            "National Geographic EMEA", "Discovery Networks",
        ],
        "Silver": [
            f"Silver Client {i}" for i in range(1, 18)
        ],
    }

    for tier, count in TIER_COUNTS.items():
        rev_min, rev_max = TIER_REVENUE_RANGE[tier]
        names = client_name_pools[tier]
        revenues = rng.uniform(rev_min, rev_max, size=count)
        margins = rng.uniform(0.25, 0.55, size=count)
        engagements = rng.integers(30, 95, size=count)
        statuses = rng.choice(
            ["Active", "At Risk", "Churned"],
            size=count,
            p=[0.70, 0.20, 0.10],
        )
        contract_types = rng.choice(CONTRACT_TYPES, size=count)
        days_to_renewal = rng.integers(10, 400, size=count)
        days_since_contact = rng.integers(1, 60, size=count)

        for i in range(count):
            rows.append({
                "client_id": f"CLT{client_id:03d}",
                "client_name": names[i],
                "tier": tier,
                "contract_type": contract_types[i],
                "annual_revenue": round(float(revenues[i]), 2),
                "margin_pct": round(float(margins[i]), 4),
                "renewal_date": TODAY + timedelta(days=int(days_to_renewal[i])),
                "last_contact_date": TODAY - timedelta(days=int(days_since_contact[i])),
                "engagement_score": int(engagements[i]),
                "status": statuses[i],
            })
            client_id += 1

    return pd.DataFrame(rows)
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && python -m pytest tests/test_simulate.py -v -k "employee or client"
```

Expected: **10 PASSED**

- [ ] **Step 5: Commit**

```bash
git add data/simulate.py tests/test_simulate.py
git commit -m "feat: add employee and client simulation with tests"
```

---

## Task 3: Project & pipeline simulation (TDD)

**Files:**
- Modify: `tests/test_simulate.py` (add project + pipeline tests)
- Modify: `data/simulate.py` (add project + pipeline generators)

- [ ] **Step 1: Append failing tests to test_simulate.py**

Add to `tests/test_simulate.py`:

```python
from data.simulate import generate_projects, generate_pipeline


# --- Projects ---

def test_projects_columns():
    df = generate_projects()
    expected = [
        "project_id", "project_name", "client_id", "project_type",
        "office", "department", "start_date", "end_date",
        "estimated_hours", "actual_hours", "budget", "actual_cost",
        "revenue", "status",
    ]
    assert list(df.columns) == expected


def test_projects_count():
    df = generate_projects()
    assert len(df) == 180


def test_projects_revenue_calibration():
    # Total project revenue should be within 15% of ANNUAL_REVENUE
    df = generate_projects()
    total = df["revenue"].sum()
    assert 0.85 * ANNUAL_REVENUE <= total <= 1.15 * ANNUAL_REVENUE


def test_projects_project_types_valid():
    df = generate_projects()
    assert set(df["project_type"].unique()).issubset(
        {"Retainer", "Production", "Licensing", "Content ID"}
    )


def test_projects_offices_valid():
    df = generate_projects()
    assert set(df["office"].unique()).issubset({"UK", "US", "Germany", "ANZ"})


def test_projects_status_valid():
    df = generate_projects()
    assert set(df["status"].unique()).issubset(
        {"On Track", "At Risk", "Over Budget", "Complete"}
    )


def test_projects_no_nulls():
    df = generate_projects()
    assert df.isnull().sum().sum() == 0


# --- Pipeline ---

def test_pipeline_columns():
    df = generate_pipeline()
    assert list(df.columns) == [
        "deal_id", "client_name", "stage", "value", "probability", "expected_close_date"
    ]


def test_pipeline_stages_valid():
    df = generate_pipeline()
    assert set(df["stage"].unique()).issubset(
        {"Prospecting", "Proposal", "Negotiation", "Closed Won", "Closed Lost"}
    )


def test_pipeline_probability_range():
    df = generate_pipeline()
    assert (df["probability"] >= 0).all()
    assert (df["probability"] <= 1).all()
```

Also add this import at the top of the existing test file (after existing imports):
```python
from data.simulate import ANNUAL_REVENUE
```

- [ ] **Step 2: Run tests to confirm new ones fail**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && python -m pytest tests/test_simulate.py -v -k "project or pipeline"
```

Expected: 10 FAILED with `ImportError`

- [ ] **Step 3: Add project + pipeline generators to data/simulate.py**

Append to `data/simulate.py`:

```python
def generate_projects() -> pd.DataFrame:
    """Generate 180 projects calibrated to $257.7M annual revenue."""
    rng = np.random.default_rng(SEED + 2)
    clients = generate_clients()
    client_ids = clients["client_id"].tolist()

    type_counts = {"Retainer": 60, "Production": 70, "Licensing": 30, "Content ID": 20}
    # Revenue weights by type (must sum to ANNUAL_REVENUE)
    type_revenue_share = {
        "Retainer": 0.25,
        "Production": 0.25,
        "Licensing": 0.15,
        "Content ID": 0.10,
    }
    # Remaining 25% comes from ad revenue (in financials_df, not projects)
    project_revenue_total = ANNUAL_REVENUE * 0.75

    rows = []
    proj_id = 1
    for ptype, count in type_counts.items():
        type_total = project_revenue_total * (type_revenue_share[ptype] / 0.75)
        revenues = rng.dirichlet(np.ones(count)) * type_total
        margins = rng.uniform(0.20, 0.50, size=count)
        estimated_hours_arr = rng.integers(50, 2000, size=count)
        overrun = rng.uniform(0.80, 1.30, size=count)
        actual_hours_arr = (estimated_hours_arr * overrun).astype(int)
        offices = rng.choice(
            OFFICES,
            size=count,
            p=[0.52, 0.22, 0.16, 0.10],
        )
        departments = rng.choice(DEPARTMENTS, size=count, p=DEPT_WEIGHTS)
        client_ids_arr = rng.choice(client_ids, size=count)
        days_ago_start = rng.integers(30, 365, size=count)
        duration_days = rng.integers(30, 180, size=count)
        pct_burned = actual_hours_arr / estimated_hours_arr
        statuses = np.where(
            pct_burned > 1.0, "Over Budget",
            np.where(pct_burned > 0.85, "At Risk",
            np.where(pct_burned > 0.50, "On Track", "Complete"))
        )

        for i in range(count):
            rev = float(revenues[i])
            margin = float(margins[i])
            cost = rev * (1 - margin)
            est_h = int(estimated_hours_arr[i])
            act_h = int(actual_hours_arr[i])
            start = TODAY - timedelta(days=int(days_ago_start[i]))
            end = start + timedelta(days=int(duration_days[i]))
            rows.append({
                "project_id": f"PRJ{proj_id:04d}",
                "project_name": f"{ptype} Project {proj_id}",
                "client_id": client_ids_arr[i],
                "project_type": ptype,
                "office": offices[i],
                "department": departments[i],
                "start_date": start,
                "end_date": end,
                "estimated_hours": est_h,
                "actual_hours": act_h,
                "budget": round(cost / (1 - margin) * 0.9, 2),
                "actual_cost": round(cost, 2),
                "revenue": round(rev, 2),
                "status": statuses[i],
            })
            proj_id += 1

    df = pd.DataFrame(rows)
    return df


def generate_pipeline() -> pd.DataFrame:
    """Generate 35 pipeline deals across stages."""
    rng = np.random.default_rng(SEED + 3)
    stage_counts = {
        "Prospecting": 12,
        "Proposal": 9,
        "Negotiation": 6,
        "Closed Won": 5,
        "Closed Lost": 3,
    }
    stage_prob = {
        "Prospecting": (0.05, 0.20),
        "Proposal": (0.20, 0.40),
        "Negotiation": (0.40, 0.70),
        "Closed Won": (1.0, 1.0),
        "Closed Lost": (0.0, 0.0),
    }
    rows = []
    deal_id = 1
    for stage, count in stage_counts.items():
        p_min, p_max = stage_prob[stage]
        probs = rng.uniform(p_min, p_max, size=count)
        values = rng.uniform(50_000, 2_000_000, size=count)
        close_days = rng.integers(7, 180, size=count)
        client_names = [f"Prospect {deal_id + i}" for i in range(count)]
        for i in range(count):
            rows.append({
                "deal_id": f"DEAL{deal_id:03d}",
                "client_name": client_names[i],
                "stage": stage,
                "value": round(float(values[i]), 2),
                "probability": round(float(probs[i]), 4),
                "expected_close_date": TODAY + timedelta(days=int(close_days[i])),
            })
            deal_id += 1
    return pd.DataFrame(rows)
```

- [ ] **Step 4: Run all simulate tests**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && python -m pytest tests/test_simulate.py -v
```

Expected: **20 PASSED**

- [ ] **Step 5: Commit**

```bash
git add data/simulate.py tests/test_simulate.py
git commit -m "feat: add project and pipeline simulation with tests"
```

---

## Task 4: Time log & financials simulation (TDD)

**Files:**
- Modify: `tests/test_simulate.py` (add timelog + financials tests)
- Modify: `data/simulate.py` (add timelog + financials generators)

- [ ] **Step 1: Append failing tests**

Add to `tests/test_simulate.py`:

```python
from data.simulate import generate_timelogs, generate_financials


# --- Time logs ---

def test_timelogs_columns():
    df = generate_timelogs()
    assert list(df.columns) == [
        "log_id", "employee_id", "project_id", "date", "hours", "billable", "department"
    ]


def test_timelogs_hours_positive():
    df = generate_timelogs()
    assert (df["hours"] > 0).all()


def test_timelogs_hours_max_per_day():
    # No single log entry should exceed 12 hours
    df = generate_timelogs()
    assert (df["hours"] <= 12).all()


def test_timelogs_billable_is_bool():
    df = generate_timelogs()
    assert df["billable"].dtype == bool


def test_timelogs_no_nulls():
    df = generate_timelogs()
    assert df.isnull().sum().sum() == 0


# --- Financials ---

def test_financials_columns():
    df = generate_financials()
    assert list(df.columns) == [
        "month", "office", "revenue_stream", "revenue", "direct_cost", "labor_cost"
    ]


def test_financials_annual_revenue_calibration():
    df = generate_financials()
    total = df["revenue"].sum()
    assert 0.90 * ANNUAL_REVENUE <= total <= 1.10 * ANNUAL_REVENUE


def test_financials_revenue_streams_valid():
    df = generate_financials()
    valid = {"Ad Revenue", "Agency Retainers", "Content Licensing", "Content ID", "Production Fees"}
    assert set(df["revenue_stream"].unique()).issubset(valid)


def test_financials_no_negative_revenue():
    df = generate_financials()
    assert (df["revenue"] >= 0).all()


def test_financials_months_count():
    # Should have 12 months of data
    df = generate_financials()
    assert df["month"].nunique() == 12
```

- [ ] **Step 2: Run to confirm new tests fail**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && python -m pytest tests/test_simulate.py -v -k "timelog or financial"
```

Expected: 10 FAILED with `ImportError`

- [ ] **Step 3: Add timelog + financials generators to data/simulate.py**

Append to `data/simulate.py`:

```python
def generate_timelogs() -> pd.DataFrame:
    """Generate daily time log entries for all employees over 12 months."""
    rng = np.random.default_rng(SEED + 4)
    employees = generate_employees()
    projects = generate_projects()
    project_ids = projects["project_id"].tolist()

    rows = []
    log_id = 1
    # Sample 30 logs per employee (manageable size, realistic density)
    for _, emp in employees.iterrows():
        n_logs = int(rng.integers(15, 45))
        days_back = rng.integers(1, 365, size=n_logs)
        hours_arr = rng.uniform(1, 8, size=n_logs).round(1)
        billable_arr = rng.random(size=n_logs) < 0.72  # 72% billable rate
        proj_arr = rng.choice(project_ids, size=n_logs)
        for i in range(n_logs):
            rows.append({
                "log_id": f"LOG{log_id:07d}",
                "employee_id": emp["employee_id"],
                "project_id": proj_arr[i],
                "date": TODAY - timedelta(days=int(days_back[i])),
                "hours": float(hours_arr[i]),
                "billable": bool(billable_arr[i]),
                "department": emp["department"],
            })
            log_id += 1
    return pd.DataFrame(rows)


def generate_financials() -> pd.DataFrame:
    """Generate monthly revenue, direct cost, and labor cost by office and stream."""
    rng = np.random.default_rng(SEED + 5)
    revenue_streams = ["Ad Revenue", "Agency Retainers", "Content Licensing", "Content ID", "Production Fees"]
    stream_share = {
        "Ad Revenue": 0.40,
        "Agency Retainers": 0.25,
        "Content Licensing": 0.15,
        "Content ID": 0.10,
        "Production Fees": 0.10,
    }
    office_share = {"UK": 0.52, "US": 0.22, "Germany": 0.16, "ANZ": 0.10}

    rows = []
    months = pd.date_range(end=TODAY, periods=12, freq="MS")
    for month in months:
        for office, o_share in office_share.items():
            for stream, s_share in stream_share.items():
                base = ANNUAL_REVENUE / 12 * o_share * s_share
                noise = rng.uniform(0.85, 1.15)
                revenue = round(base * noise, 2)
                direct_cost = round(revenue * rng.uniform(0.20, 0.35), 2)
                labor_cost = round(revenue * rng.uniform(0.25, 0.40), 2)
                rows.append({
                    "month": month.date(),
                    "office": office,
                    "revenue_stream": stream,
                    "revenue": revenue,
                    "direct_cost": direct_cost,
                    "labor_cost": labor_cost,
                })
    return pd.DataFrame(rows)


def generate_all() -> dict:
    """Generate all DataFrames. Call once and cache."""
    return {
        "employee_df": generate_employees(),
        "client_df": generate_clients(),
        "project_df": generate_projects(),
        "timelog_df": generate_timelogs(),
        "pipeline_df": generate_pipeline(),
        "financials_df": generate_financials(),
    }
```

- [ ] **Step 4: Run full test suite**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && python -m pytest tests/test_simulate.py -v
```

Expected: **30 PASSED**

- [ ] **Step 5: Commit**

```bash
git add data/simulate.py tests/test_simulate.py
git commit -m "feat: add timelog and financials simulation — 30 tests passing"
```

---

## Task 5: Metrics utilities (TDD)

**Files:**
- Create: `tests/test_metrics.py`
- Create: `utils/metrics.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_metrics.py`:

```python
import pandas as pd
import pytest
from datetime import date, timedelta
from utils.metrics import (
    utilization_rate,
    budget_variance_df,
    gross_margin_pct,
    avg_project_margin_pct,
    renewal_rate,
    pipeline_value,
    revenue_by_stream,
)


def _make_timelogs(billable_hours, total_hours):
    """Helper: one employee, one project, one day."""
    rows = []
    for i, (bh, th) in enumerate(zip(billable_hours, total_hours)):
        rows.append({
            "log_id": f"LOG{i:04d}",
            "employee_id": "EMP0001",
            "project_id": "PRJ0001",
            "date": date(2026, 1, i + 1),
            "hours": bh,
            "billable": True,
            "department": "Production",
        })
        if th > bh:
            rows.append({
                "log_id": f"LOG{i:04d}X",
                "employee_id": "EMP0001",
                "project_id": "PRJ0001",
                "date": date(2026, 1, i + 1),
                "hours": th - bh,
                "billable": False,
                "department": "Production",
            })
    return pd.DataFrame(rows)


def _make_employees(n=1, office="UK"):
    return pd.DataFrame([{
        "employee_id": f"EMP{i:04d}",
        "name": f"Employee {i}",
        "department": "Production",
        "office": office,
        "role": "Mid",
        "loaded_cost_rate": 75,
    } for i in range(1, n + 1)])


def _make_projects(revenues, costs, estimated_hours, actual_hours, statuses=None):
    rows = []
    for i, (r, c, eh, ah) in enumerate(zip(revenues, costs, estimated_hours, actual_hours)):
        rows.append({
            "project_id": f"PRJ{i:04d}",
            "project_name": f"Project {i}",
            "client_id": "CLT001",
            "project_type": "Retainer",
            "office": "UK",
            "department": "Production",
            "start_date": date(2026, 1, 1),
            "end_date": date(2026, 3, 31),
            "estimated_hours": eh,
            "actual_hours": ah,
            "budget": c * 1.1,
            "actual_cost": c,
            "revenue": r,
            "status": statuses[i] if statuses else "On Track",
        })
    return pd.DataFrame(rows)


# --- utilization_rate ---

def test_utilization_rate_basic():
    # 1 employee, 20 billable hours out of 40 available = 50%
    timelogs = _make_timelogs([8, 8, 4], [8, 8, 8])
    # billable = 8+8+4 = 20, total = 8+8+8 = 24
    employees = _make_employees(1)
    result = utilization_rate(timelogs, employees)
    assert abs(result - 20 / 24) < 0.01


def test_utilization_rate_all_billable():
    timelogs = _make_timelogs([8, 8], [8, 8])
    employees = _make_employees(1)
    result = utilization_rate(timelogs, employees)
    assert abs(result - 1.0) < 0.01


def test_utilization_rate_zero_logs():
    timelogs = pd.DataFrame(columns=[
        "log_id", "employee_id", "project_id", "date", "hours", "billable", "department"
    ])
    employees = _make_employees(1)
    result = utilization_rate(timelogs, employees)
    assert result == 0.0


# --- budget_variance_df ---

def test_budget_variance_on_track():
    df = _make_projects([100], [60], [100], [70])
    result = budget_variance_df(df)
    assert result.iloc[0]["pct_burned"] == pytest.approx(0.70)
    assert result.iloc[0]["status"] == "On Track"


def test_budget_variance_at_risk():
    df = _make_projects([100], [60], [100], [90])
    result = budget_variance_df(df)
    assert result.iloc[0]["status"] == "At Risk"


def test_budget_variance_over_budget():
    df = _make_projects([100], [60], [100], [110])
    result = budget_variance_df(df)
    assert result.iloc[0]["status"] == "Over Budget"
    assert result.iloc[0]["hours_over"] == 10


# --- gross_margin_pct ---

def test_gross_margin_pct_correct():
    # revenue=200, cost=120 → margin = 40%
    df = _make_projects([100, 100], [60, 60], [100, 100], [80, 80])
    result = gross_margin_pct(df)
    assert abs(result - 0.40) < 0.001


def test_gross_margin_pct_zero_revenue():
    df = _make_projects([0], [0], [100], [80])
    result = gross_margin_pct(df)
    assert result == 0.0


# --- avg_project_margin_pct ---

def test_avg_project_margin_pct_correct():
    # Project 1: (100-60)/100=40%, Project 2: (200-80)/200=60% → avg=50%
    df = _make_projects([100, 200], [60, 80], [100, 100], [80, 80])
    result = avg_project_margin_pct(df)
    assert abs(result - 0.50) < 0.001


# --- renewal_rate ---

def test_renewal_rate_correct():
    df = pd.DataFrame({
        "client_id": ["C1", "C2", "C3", "C4", "C5"],
        "status": ["Active", "Active", "Active", "Churned", "At Risk"],
    })
    result = renewal_rate(df)
    # Active + At Risk = 4, Churned = 1 → 4/5 = 80%
    assert abs(result - 0.80) < 0.01


def test_renewal_rate_all_active():
    df = pd.DataFrame({
        "client_id": ["C1", "C2"],
        "status": ["Active", "Active"],
    })
    assert renewal_rate(df) == 1.0


# --- pipeline_value ---

def test_pipeline_value_excludes_closed():
    df = pd.DataFrame({
        "deal_id": ["D1", "D2", "D3"],
        "stage": ["Prospecting", "Closed Won", "Closed Lost"],
        "value": [100_000, 200_000, 50_000],
        "probability": [0.10, 1.0, 0.0],
    })
    result = pipeline_value(df)
    # Only Prospecting is open: 100_000
    assert result == 100_000


def test_pipeline_value_all_open():
    df = pd.DataFrame({
        "deal_id": ["D1", "D2"],
        "stage": ["Proposal", "Negotiation"],
        "value": [100_000, 200_000],
        "probability": [0.30, 0.60],
    })
    result = pipeline_value(df)
    assert result == 300_000


# --- revenue_by_stream ---

def test_revenue_by_stream_sums_correctly():
    df = pd.DataFrame({
        "month": ["2026-01-01", "2026-01-01", "2026-02-01"],
        "office": ["UK", "US", "UK"],
        "revenue_stream": ["Ad Revenue", "Ad Revenue", "Agency Retainers"],
        "revenue": [1000, 500, 800],
        "direct_cost": [200, 100, 160],
        "labor_cost": [300, 150, 240],
    })
    result = revenue_by_stream(df)
    assert result.loc[result["revenue_stream"] == "Ad Revenue", "revenue"].values[0] == 1500
    assert result.loc[result["revenue_stream"] == "Agency Retainers", "revenue"].values[0] == 800


def test_revenue_by_stream_filters_by_office():
    df = pd.DataFrame({
        "month": ["2026-01-01", "2026-01-01"],
        "office": ["UK", "US"],
        "revenue_stream": ["Ad Revenue", "Ad Revenue"],
        "revenue": [1000, 500],
        "direct_cost": [200, 100],
        "labor_cost": [300, 150],
    })
    result = revenue_by_stream(df, offices=["UK"])
    assert result.loc[result["revenue_stream"] == "Ad Revenue", "revenue"].values[0] == 1000
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && python -m pytest tests/test_metrics.py -v
```

Expected: 17 FAILED with `ModuleNotFoundError: No module named 'utils.metrics'`

- [ ] **Step 3: Implement utils/metrics.py**

Create `utils/metrics.py`:

```python
import pandas as pd


def utilization_rate(timelog_df: pd.DataFrame, employee_df: pd.DataFrame) -> float:
    """Billable hours / total hours logged. Returns 0.0 if no logs."""
    if timelog_df.empty:
        return 0.0
    total = timelog_df["hours"].sum()
    if total == 0:
        return 0.0
    billable = timelog_df.loc[timelog_df["billable"], "hours"].sum()
    return float(billable / total)


def budget_variance_df(project_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns project_df with added columns:
        pct_burned: actual_hours / estimated_hours
        hours_over: max(0, actual_hours - estimated_hours)
        status: On Track / At Risk / Over Budget
    """
    df = project_df.copy()
    df["pct_burned"] = df["actual_hours"] / df["estimated_hours"]
    df["hours_over"] = (df["actual_hours"] - df["estimated_hours"]).clip(lower=0)
    df["status"] = df["pct_burned"].apply(
        lambda p: "Over Budget" if p > 1.0 else "At Risk" if p > 0.85 else "On Track"
    )
    return df


def gross_margin_pct(project_df: pd.DataFrame, offices: list = None) -> float:
    """(sum revenue - sum actual_cost) / sum revenue. Returns 0.0 if revenue is 0."""
    df = project_df if offices is None else project_df[project_df["office"].isin(offices)]
    total_revenue = df["revenue"].sum()
    if total_revenue == 0:
        return 0.0
    total_cost = df["actual_cost"].sum()
    return float((total_revenue - total_cost) / total_revenue)


def avg_project_margin_pct(project_df: pd.DataFrame, offices: list = None) -> float:
    """Mean of per-project (revenue - actual_cost) / revenue."""
    df = project_df if offices is None else project_df[project_df["office"].isin(offices)]
    margins = (df["revenue"] - df["actual_cost"]) / df["revenue"].replace(0, float("nan"))
    return float(margins.mean())


def renewal_rate(client_df: pd.DataFrame) -> float:
    """Non-churned clients / total clients."""
    total = len(client_df)
    if total == 0:
        return 0.0
    churned = (client_df["status"] == "Churned").sum()
    return float((total - churned) / total)


def pipeline_value(pipeline_df: pd.DataFrame) -> float:
    """Total value of open deals (excludes Closed Won and Closed Lost)."""
    open_stages = {"Prospecting", "Proposal", "Negotiation"}
    open_deals = pipeline_df[pipeline_df["stage"].isin(open_stages)]
    return float(open_deals["value"].sum())


def revenue_by_stream(
    financials_df: pd.DataFrame, offices: list = None
) -> pd.DataFrame:
    """Group financials by revenue_stream, optionally filtered by office."""
    df = financials_df if offices is None else financials_df[financials_df["office"].isin(offices)]
    return (
        df.groupby("revenue_stream")
        .agg(revenue=("revenue", "sum"), direct_cost=("direct_cost", "sum"), labor_cost=("labor_cost", "sum"))
        .reset_index()
    )
```

- [ ] **Step 4: Run full test suite**

```bash
cd /Users/mr.fidols/github/little-dot-studios-bi && python -m pytest tests/ -v
```

Expected: **47 PASSED** (30 simulate + 17 metrics)

- [ ] **Step 5: Commit**

```bash
git add utils/metrics.py tests/test_metrics.py
git commit -m "feat: add metrics utilities with 17 tests — 47 total passing"
```

- [ ] **Step 6: Push**

```bash
git push origin main
```

Expected: `main -> main` confirmed.
