# Little Dot Studios BI Dashboard — Design Spec

**Date:** 2026-05-12
**Role target:** Analyst, Business Intelligence — Commercial Planning, Little Dot Studios (LA)
**Purpose:** Portfolio project demonstrating BI Analyst capabilities aligned to the LDS JD

---

## Goal

Build a multi-page Streamlit dashboard simulating Little Dot Studios' internal Commercial Planning analytics. Simulated operational data is calibrated to real publicly available LDS figures. The final page uses real YouTube Data API data pre-fetched from LDS-owned channels. The dashboard is deployable to Streamlit Community Cloud.

---

## Architecture

### Data Layer
- `data/simulate.py` — seeded generator for all operational data (projects, time logs, clients, financials)
- `data/youtube/` — pre-fetched YouTube API data saved as CSV files (static, no live API calls at runtime)
- All simulated data calibrated to real anchors: $257.7M revenue, 419 employees, 800+ channels, 930M subscribers

### Utility Layer
- `utils/metrics.py` — shared KPI calculations used across pages
- `utils/youtube.py` — helpers for loading and processing pre-fetched YouTube data

### Page Layer
- `app.py` — Overview (landing page)
- `pages/1_Time_Tracking.py`
- `pages/2_Profitability.py`
- `pages/3_Client_CRM.py`
- `pages/4_Channel_Network.py`

### Conventions
- Session state: data loaded once in `app.py`, shared across all pages
- Charts: Plotly Express, `width="stretch"` (not `use_container_width=True`)
- Color palette: LDS brand — black (#1A1A1A), red (#E31837), gray (#6D6E71)
- All pages have a stakeholder caption below the title
- Tests: pytest, TDD workflow, pure logic in utils/

---

## Data Model

### Simulated Entities

**Projects** (`project_df`)
- `project_id`, `project_name`, `client_id`, `project_type` (Retainer / Production / Licensing / Content ID), `office` (UK / US / Germany / ANZ), `department`, `start_date`, `end_date`, `estimated_hours`, `actual_hours`, `budget`, `actual_cost`, `revenue`, `status`

**Time Logs** (`timelog_df`)
- `log_id`, `employee_id`, `project_id`, `date`, `hours`, `billable` (bool), `department`

**Employees** (`employee_df`)
- `employee_id`, `name`, `department`, `office`, `role`, `loaded_cost_rate`

**Clients** (`client_df`)
- `client_id`, `client_name`, `tier` (Platinum / Gold / Silver), `contract_type`, `annual_revenue`, `margin_pct`, `renewal_date`, `last_contact_date`, `engagement_score`, `status`

**Pipeline** (`pipeline_df`)
- `deal_id`, `client_name`, `stage`, `value`, `probability`, `expected_close_date`

**Financials** (`financials_df`)
- Monthly revenue, cost, and margin by office and revenue stream

### Real Data (YouTube)
Pre-fetched from YouTube Data API v3:
- `data/youtube/channels.csv` — channel_id, channel_name, subscribers, total_views, video_count, category
- `data/youtube/videos.csv` — video_id, channel_id, title, published_at, views, likes, duration_seconds
- `data/youtube/growth.csv` — channel_id, month, subscriber_count, monthly_views

### Calibration Anchors
| Metric | Real Value | Source |
|---|---|---|
| LDS annual revenue | $257.7M | ZoomInfo |
| Employees | 419 | LeadIQ (March 2026) |
| Network subscribers | 930M | LDS Whitepaper 2026 |
| Monthly views | 11.2B | LDS Whitepaper 2026 |
| Channels managed | 800+ | LDS Whitepaper 2026 |
| Content ID earnings (3yr) | $100M+ | littledotstudios.com |
| All3Media revenue | £895.9M | All3Media FY2024 filing |
| All3Media YoY change | -10% | Variety / Deadline |
| All3Media operating result | -£30.8M loss | Broadcast Now |

---

## Pages

### app.py — Overview

**Stakeholders:** Commercial Planning · Finance · Executive Leadership
**Story:** Little Dot Studios operates at extraordinary scale — but their parent company just posted its worst year on record. This dashboard exists because operational excellence is no longer optional.

**Layout:**

1. **Title + caption**

2. **All3Media pressure banner** (full width)
   - Metric cards: All3Media Group Revenue (£895.9M), YoY Change (-10%, red arrow), Operating Result (-£30.8M loss, red)
   - Caption: *"Source: All3Media FY2024 audited financials. First operating loss in recent history."*
   - Same delta sign treatment as Skechers: sign before £ symbol so Streamlit arrow renders correctly

3. **LDS Network KPIs** (4 columns)
   - Total Revenue: $257.7M
   - Employees: 419
   - Network Subscribers: 930M
   - Monthly Views: 11.2B
   - Anchored to real sources, captioned

4. **Revenue by Stream** (bar chart)
   - Simulated breakdown: Ad Revenue, Agency Retainers, Content Licensing, Content ID, Production Fees
   - Calibrated to sum to $257.7M

5. **Office selector** (multiselect)
   - UK / US / Germany / ANZ
   - Stored in session state, filters all subsequent pages
   - Default: All offices selected

---

### pages/1_Time_Tracking.py — Time Tracking & Utilization

**Stakeholders:** Operations · Department Heads · Finance
**Story:** Are we getting the most out of our people, and are our projects coming in on budget?

**Layout:**

1. **3 KPI cards**
   - Overall utilization rate (billable hours / available hours)
   - Total billable hours this month
   - Budget variance across active projects (actual hours vs. estimated)

2. **Utilization by department** (horizontal bar chart)
   - Departments: Production, Strategy, Distribution, Sales, Operations
   - Reference line at 75% (target) and 55% (industry average)
   - Color: green if ≥75%, amber if 55–74%, red if <55%

3. **Monthly utilization trend** (line chart)
   - Last 12 months, by office (filtered by selector)
   - Annotate peaks (F1 season Mar–Nov, Olympic years)

4. **Budget vs. actuals table**
   - Columns: Project, Client, Type, Est. Hours, Actual Hours, % Burned, Budget, Actual Cost, Status flag
   - Status: On Track (green) / At Risk (amber) / Over Budget (red)
   - Sortable, filterable by department and project type

5. **Overrun alert panel**
   - Projects currently Over Budget surfaced as `st.warning` cards
   - Shows project name, client, hours over, estimated cost impact

---

### pages/2_Profitability.py — Profitability & Finance

**Stakeholders:** Finance · Commercial Leadership · CEO
**Story:** Which clients and project types are making us money — and is the business getting more or less profitable?

**Layout:**

1. **All3Media callback banner** (slim)
   - *"All3Media FY2024 operating loss: -£30.8M. LDS profitability targets are set against this backdrop."*

2. **4 KPI cards**
   - Total revenue (selected office/period)
   - Gross margin %
   - Average project margin %
   - Margin delta vs. prior quarter (with arrow)

3. **Revenue vs. cost over time** (stacked area chart)
   - Monthly: revenue, direct costs, labor costs
   - The gap = margin — visually shows compression or expansion

4. **Margin by client tier** (horizontal bar chart)
   - Platinum / Gold / Silver tiers
   - Immediately shows which tier is most profitable

5. **Project type profitability** (bar chart)
   - Retainer vs. Production vs. Licensing vs. Content ID
   - Shows gross margin % per type with reference line at 30% (healthy threshold)

6. **New business pricing tool**
   - Inputs: project type (selectbox), estimated weeks (slider), team size (slider), seniority mix (selectbox)
   - Output: floor price (cost + minimum margin), recommended price (target margin), estimated hours breakdown
   - Based on historical actuals from simulated data
   - `st.info` callout: *"Based on {N} comparable past projects"*

---

### pages/3_Client_CRM.py — Client & CRM

**Stakeholders:** Commercial Team · Sales · Finance
**Story:** Which clients are growing, which are at risk, and where is the next dollar of revenue coming from?

**Layout:**

1. **4 KPI cards**
   - Total active clients
   - Pipeline value ($)
   - Renewal rate %
   - Average contract value

2. **Client health matrix** (scatter plot)
   - X-axis: Annual revenue ($)
   - Y-axis: Engagement score (0–100)
   - Quadrant labels: Stars (top right), At Risk (bottom right), Growth (top left), Deprioritize (bottom left)
   - Each dot = one client, sized by contract value, colored by tier
   - Hover shows: client name, revenue, engagement score, renewal date

3. **Client tier table**
   - Columns: Client, Tier, Contract Type, Revenue, Margin %, Renewal Date, Last Contact, Status
   - Color-coded status: Active (green) / At Risk (amber) / Churned (red)
   - Sortable, filterable
   - CSV download

4. **Pipeline by stage** (funnel/bar chart)
   - Stages: Prospecting → Proposal → Negotiation → Closed Won / Closed Lost
   - Total $ value per stage
   - Win rate shown as caption

5. **Renewal calendar**
   - Contracts expiring in next 90 days
   - Flagged by risk level (based on engagement score)
   - Revenue at risk total shown as metric card

---

### pages/4_Channel_Network.py — Channel Network

**Stakeholders:** Commercial Team · Content Strategy · Ad Sales
**Story:** Across LDS's owned channel network, where is growth happening and what content format is driving performance?

**Data source:** Pre-fetched YouTube API data from LDS-owned channels (real data)

**Layout:**

1. **3 KPI cards** (real data)
   - Total subscribers across fetched channels
   - Total monthly views
   - Average views per video

2. **Top channels leaderboard** (table)
   - Real channel names, real subscriber and view counts
   - Ranked by subscribers
   - Columns: Channel, Category, Subscribers, Monthly Views, Videos, Avg Views/Video

3. **Subscriber growth trend** (line chart)
   - Top 5 channels over time
   - Real historical data from API

4. **Video length vs. performance** (bar chart)
   - Bins: <10 min, 10–30 min, 30–45 min, 45–60 min, 60+ min
   - Average views per bin
   - Annotation: *"LDS research: 45–60 min videos drive ~40% of network revenue"*
   - Shows the whitepaper finding validated (or challenged) by real channel data

5. **Content category breakdown** (donut chart)
   - Views by category across all channels

6. **Underperforming channels panel**
   - Channels with: declining subscribers MoM, below-average views/video, or low upload frequency
   - Surfaced as `st.warning` cards with specific metric callout

---

## Tech Stack
- Python 3.12
- Streamlit ≥1.32.0
- pandas ≥2.0.0
- NumPy ≥1.26.0
- Plotly Express ≥5.18.0
- google-api-python-client (for YouTube data pre-fetch script only)
- pytest (dev dependency)

## Testing
- Pure logic in `utils/` — all functions unit tested
- TDD: failing tests written before implementation
- Target: 25+ tests covering metrics, data simulation, pricing tool logic

## Deployment
- Streamlit Community Cloud
- `requirements.txt` with `>=` version pins
- YouTube data committed as static CSVs — no API key needed at runtime
