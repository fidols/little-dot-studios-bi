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
    df["pct_burned"] = df["actual_hours"] / df["estimated_hours"].replace(0, float("nan"))
    df["hours_over"] = (df["actual_hours"] - df["estimated_hours"]).clip(lower=0).fillna(0)
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
    if df["revenue"].sum() == 0:
        return 0.0
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
    # Employees not in employee_df get NaN office and are excluded from groupby results.
    # In practice all employee_ids come from generate_employees() so this is not a data loss risk.
    df = timelog_df.merge(
        employee_df[["employee_id", "office"]], on="employee_id", how="left"
    )
    df["_date"] = pd.to_datetime(df["date"])
    df["month"] = df["_date"].dt.to_period("M").dt.to_timestamp()
    cutoff = df["_date"].max() - pd.DateOffset(months=months)
    df = df[df["_date"] >= cutoff]
    if df.empty:
        return pd.DataFrame(columns=["month", "office", "utilization_rate"])
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
