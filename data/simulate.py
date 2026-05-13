import numpy as np
import pandas as pd
from datetime import date, timedelta

SEED = 42

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


def generate_projects() -> pd.DataFrame:
    """Generate 180 projects calibrated to $257.7M annual revenue."""
    rng = np.random.default_rng(SEED + 2)
    clients = generate_clients()
    client_ids = clients["client_id"].tolist()

    type_counts = {ptype: c for ptype, c in zip(PROJECT_TYPES, [60, 70, 30, 20])}
    type_revenue_share = {ptype: s for ptype, s in zip(PROJECT_TYPES, [0.25, 0.25, 0.15, 0.10])}
    project_revenue_total = ANNUAL_REVENUE

    rows = []
    proj_id = 1
    for ptype in PROJECT_TYPES:
        count = type_counts[ptype]
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
        statuses = rng.choice(
            ["Active", "Completed", "On Hold"],
            size=count,
            p=[0.50, 0.40, 0.10],
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
                "budget": round(rev * rng.uniform(0.85, 1.15), 2),
                "actual_cost": round(cost, 2),
                "revenue": round(rev, 2),
                "status": statuses[i],
            })
            proj_id += 1

    return pd.DataFrame(rows)


def generate_pipeline() -> pd.DataFrame:
    """Generate 35 pipeline deals across stages."""
    rng = np.random.default_rng(SEED + 3)
    stage_counts = {stage: c for stage, c in zip(PIPELINE_STAGES, [12, 9, 6, 5, 3])}
    stage_prob = {
        "Prospecting": (0.05, 0.20),
        "Proposal": (0.20, 0.40),
        "Negotiation": (0.40, 0.70),
        "Closed Won": (1.0, 1.0),
        "Closed Lost": (0.0, 0.0),
    }
    rows = []
    deal_id = 1
    for stage in PIPELINE_STAGES:
        count = stage_counts[stage]
        p_min, p_max = stage_prob[stage]
        probs = rng.uniform(p_min, p_max, size=count)
        values = rng.uniform(50_000, 2_000_000, size=count)
        close_days = rng.integers(7, 180, size=count)
        client_names = [f"Prospect {deal_id + i}" for i in range(count)]
        closed_stages = {"Closed Won", "Closed Lost"}
        for i in range(count):
            if stage in closed_stages:
                close_date = TODAY - timedelta(days=int(rng.integers(30, 180)))
            else:
                close_date = TODAY + timedelta(days=int(close_days[i]))
            rows.append({
                "deal_id": f"DEAL{deal_id:03d}",
                "client_name": client_names[i],
                "stage": stage,
                "value": round(float(values[i]), 2),
                "probability": round(float(probs[i]), 4),
                "expected_close_date": close_date,
            })
            deal_id += 1
    return pd.DataFrame(rows)


def generate_timelogs() -> pd.DataFrame:
    """Generate daily time log entries for all employees over 12 months."""
    rng = np.random.default_rng(SEED + 4)
    employees = generate_employees()
    projects = generate_projects()
    project_ids = projects["project_id"].tolist()

    rows = []
    log_id = 1
    # Sample 15–45 logs per employee
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
