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
