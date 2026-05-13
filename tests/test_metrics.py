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
