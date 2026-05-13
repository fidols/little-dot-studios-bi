import pandas as pd
import pytest
from data.simulate import (
    generate_employees,
    generate_clients,
    generate_projects,
    generate_pipeline,
    ANNUAL_REVENUE,
)


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
    df = generate_projects()
    total = df["revenue"].sum()
    assert 0.85 * ANNUAL_REVENUE <= total <= 1.15 * ANNUAL_REVENUE
    assert (df["revenue"] > 0).all()
    assert df["revenue"].max() < ANNUAL_REVENUE * 0.05


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
        {"Active", "Completed", "On Hold"}
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


def test_pipeline_count():
    df = generate_pipeline()
    assert len(df) == 35


def test_pipeline_no_nulls():
    df = generate_pipeline()
    assert df.isnull().sum().sum() == 0


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
