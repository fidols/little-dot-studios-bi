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
