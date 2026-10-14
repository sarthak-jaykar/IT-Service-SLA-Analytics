"""
generate_data.py
Generates the simulated IT ticket dataset for the
IT Service Management & SLA Performance Analytics project.

Output (written to ../data relative to this script):
    fact_tickets.csv, dim_service.csv, dim_date.csv

All data is synthetic. Fixed seed = reproducible.
"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

SNAPSHOT = pd.Timestamp("2025-12-31 23:59:00")
START, END = pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")
N_INCIDENTS, N_REQUESTS = 1100, 400
OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------- Dimensions ----------------
services = [
    # id, name, group, team, incident_weight, request_weight
    ("S01", "Laptops & Desktops",          "End User Computing", "Service Desk",             20, 25),
    ("S02", "Printing",                    "End User Computing", "Service Desk",              8,  2),
    ("S03", "Email & Calendar",            "Collaboration",      "Service Desk",             12, 10),
    ("S04", "Collaboration Tools",         "Collaboration",      "Service Desk",             10, 10),
    ("S05", "VPN & Remote Access",         "Network",            "Infrastructure & Network",  9,  5),
    ("S06", "Wi-Fi & LAN",                 "Network",            "Infrastructure & Network",  8,  2),
    ("S07", "Telephony",                   "Network",            "Infrastructure & Network",  4,  2),
    ("S08", "ERP (Finance & Procurement)", "Business Applications", "Applications Support",   8,  8),
    ("S09", "HR Portal",                   "Business Applications", "Applications Support",   5,  8),
    ("S10", "CRM",                         "Business Applications", "Applications Support",   5,  5),
    ("S11", "Identity & Access",           "Security",           "Security & Access",         8, 20),
    ("S12", "Endpoint Security",           "Security",           "Security & Access",         3,  3),
]
dim_service = pd.DataFrame(services, columns=["service_id", "service_name", "service_group",
                                              "support_team", "w_inc", "w_req"])
team_of = dict(zip(dim_service.service_id, dim_service.support_team))

# allowed categories per service (weights)
cat_w = {
    "S01": {"Hardware": 55, "Software": 25, "Performance": 15, "Access & Permissions": 5},
    "S02": {"Hardware": 50, "Software": 20, "Network & Connectivity": 30},
    "S03": {"Software": 40, "Access & Permissions": 30, "Performance": 20, "Security": 10},
    "S04": {"Software": 45, "Access & Permissions": 25, "Performance": 20, "Network & Connectivity": 10},
    "S05": {"Network & Connectivity": 60, "Access & Permissions": 25, "Performance": 15},
    "S06": {"Network & Connectivity": 75, "Hardware": 15, "Performance": 10},
    "S07": {"Hardware": 25, "Software": 20, "Network & Connectivity": 45, "Performance": 10},
    "S08": {"Software": 35, "Access & Permissions": 30, "Performance": 30, "Security": 5},
    "S09": {"Software": 40, "Access & Permissions": 35, "Performance": 25},
    "S10": {"Software": 45, "Access & Permissions": 25, "Performance": 30},
    "S11": {"Access & Permissions": 80, "Security": 20},
    "S12": {"Security": 60, "Software": 25, "Performance": 15},
}
REQ_CATS = {"Hardware", "Software", "Access & Permissions"}  # requests limited to these

# ---------------- SLA policy (resolution target, calendar hours) ----------------
SLA = {("Incident", "P1 Critical"): 4, ("Incident", "P2 High"): 8,
       ("Incident", "P3 Medium"): 24, ("Incident", "P4 Low"): 72,
       ("Service Request", "P3 Medium"): 48, ("Service Request", "P4 Low"): 120}

# ---------------- Date table ----------------
all_dates = pd.date_range(START, END, freq="D")
dim_date = pd.DataFrame({"date": all_dates})
dim_date["month_start"] = dim_date["date"].dt.to_period("M").dt.to_timestamp()
dim_date["month_label"] = dim_date["date"].dt.strftime("%b")

month_w = dict(zip(range(1, 13), [0.90, 0.90, 1.05, 1.00, 1.00, 0.95, 0.90, 0.90, 1.05, 1.15, 1.10, 1.00]))
day_w = np.array([month_w[d.month] * (1.0 if d.weekday() < 5 else 0.2) for d in all_dates])
day_p = day_w / day_w.sum()
hour_w = np.array([0.2]*7 + [3, 6, 8, 8, 6, 5, 6, 8, 8, 6, 3] + [0.3]*6)  # 24 hours, peak 8-18
hour_p = hour_w / hour_w.sum()

def pick(options, weights, n):
    w = np.array(weights, dtype=float)
    return rng.choice(options, size=n, p=w / w.sum())

# ---------------- Ticket generation ----------------
def build(ticket_type, n):
    if ticket_type == "Incident":
        svc = pick(dim_service.service_id.values, dim_service.w_inc.values, n)
        pr = pick(["P1 Critical", "P2 High", "P3 Medium", "P4 Low"], [4.5, 15, 50, 30.5], n)
    else:
        svc = pick(dim_service.service_id.values, dim_service.w_req.values, n)
        pr = pick(["P3 Medium", "P4 Low"], [60, 40], n)
    cats = []
    for s in svc:
        opts = {k: v for k, v in cat_w[s].items() if ticket_type == "Incident" or k in REQ_CATS}
        cats.append(pick(list(opts.keys()), list(opts.values()), 1)[0])
    day = rng.choice(all_dates, size=n, p=day_p)
    hour = rng.choice(24, size=n, p=hour_p)
    minute = rng.integers(0, 60, size=n)
    created = pd.to_datetime(day) + pd.to_timedelta(hour, unit="h") + pd.to_timedelta(minute, unit="m")
    return pd.DataFrame({"ticket_type": ticket_type, "service_id": svc, "category": cats,
                         "priority": pr, "created_datetime": created})

df = pd.concat([build("Incident", N_INCIDENTS), build("Service Request", N_REQUESTS)], ignore_index=True)
df = df.sort_values("created_datetime").reset_index(drop=True)
n = len(df)

df["sla_target_hours"] = [SLA[(t, p)] for t, p in zip(df.ticket_type, df.priority)]

# Resolution time = target x ratio. ratio ~ lognormal around a median set by priority,
# nudged by team, category and a few services (builds in differences to analyse).
base_ratio = {("Incident", "P1 Critical"): 0.80, ("Incident", "P2 High"): 0.72,
              ("Incident", "P3 Medium"): 0.55, ("Incident", "P4 Low"): 0.45,
              ("Service Request", "P3 Medium"): 0.60, ("Service Request", "P4 Low"): 0.50}
team_f = {"Service Desk": 0.90, "Infrastructure & Network": 1.15,
          "Applications Support": 1.25, "Security & Access": 1.05}
cat_f = {"Hardware": 1.20, "Software": 1.00, "Network & Connectivity": 1.00,
         "Access & Permissions": 0.85, "Performance": 1.25, "Security": 1.05}
svc_f = {"S08": 1.15, "S07": 1.20}
SIGMA = 0.55

median = np.array([base_ratio[(t, p)] for t, p in zip(df.ticket_type, df.priority)])
median *= df.service_id.map(team_of).map(team_f).values
median *= df.category.map(cat_f).values
median *= df.service_id.map(svc_f).fillna(1.0).values
ratio = np.minimum(median * rng.lognormal(0, SIGMA, n), 6.0)
res_minutes = np.maximum(np.round(ratio * df.sla_target_hours.values * 60), 15)
df["resolved_datetime"] = df.created_datetime + pd.to_timedelta(res_minutes, unit="m")

# Unresolved tickets:
# (a) natural: would resolve after the snapshot
# (b) stuck: stays open; likelier for recent tickets, some services, lower priorities
stuck_svc = {"S08": 2.0, "S11": 1.8, "S07": 1.8, "S10": 1.5, "S09": 1.3}
stuck_pri = {"P1 Critical": 0.15, "P2 High": 0.6, "P3 Medium": 1.0, "P4 Low": 1.1}
doy = df.created_datetime.dt.dayofyear.values
p_stuck = 0.23 * np.exp((doy - 365) / 100.0)
p_stuck *= df.service_id.map(stuck_svc).fillna(1.0).values
p_stuck *= df.priority.map(stuck_pri).values
stuck = rng.random(n) < np.clip(p_stuck, 0, 0.5)
natural = (df.resolved_datetime > SNAPSHOT).values
open_mask = stuck | natural

df["status"] = "Resolved"
df.loc[open_mask, "status"] = rng.choice(["Open", "In Progress"], size=open_mask.sum(), p=[0.4, 0.6])
df.loc[open_mask, "resolved_datetime"] = pd.NaT

res_h = (df.resolved_datetime - df.created_datetime).dt.total_seconds() / 3600
df["resolution_hours"] = res_h.round(2)

age_h = (SNAPSHOT - df.created_datetime).dt.total_seconds() / 3600
df["backlog_age_days"] = np.where(open_mask, (age_h / 24).round(2), np.nan)

outcome = np.where(~open_mask,
                   np.where(res_h <= df.sla_target_hours, "Met", "Breached"),
                   np.where(age_h > df.sla_target_hours, "Open - Overdue", "Open - Within SLA"))
df["sla_outcome"] = outcome

# IDs (sequential in created order within each type)
df["ticket_id"] = ""
for t, prefix in [("Incident", "INC"), ("Service Request", "REQ")]:
    m = df.ticket_type == t
    df.loc[m, "ticket_id"] = [f"{prefix}-{i:04d}" for i in range(1, m.sum() + 1)]
df["created_date"] = df.created_datetime.dt.normalize()

cols = ["ticket_id", "ticket_type", "created_date", "created_datetime", "resolved_datetime",
        "service_id", "category", "priority", "status", "sla_target_hours",
        "resolution_hours", "sla_outcome", "backlog_age_days"]
fact = df[cols]

# ---------------- Save ----------------
fact.assign(created_date=fact.created_date.dt.strftime("%Y-%m-%d")) \
    .to_csv(OUT / "fact_tickets.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
dim_service[["service_id", "service_name", "service_group", "support_team"]] \
    .to_csv(OUT / "dim_service.csv", index=False)
dim_date.assign(date=dim_date.date.dt.strftime("%Y-%m-%d"),
                month_start=dim_date.month_start.dt.strftime("%Y-%m-%d")) \
    .to_csv(OUT / "dim_date.csv", index=False)

print(f"fact_tickets.csv : {len(fact)} rows, {fact.shape[1]} columns")
print(f"dim_service.csv  : {len(dim_service)} rows")
print(f"dim_date.csv     : {len(dim_date)} rows")
print(f"Files saved to   : {OUT}")
