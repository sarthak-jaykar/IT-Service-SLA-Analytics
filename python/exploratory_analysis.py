"""
exploratory_analysis.py
Brief EDA on the validated IT ticket data, plus the reference KPI values
used to reconcile the Power BI report.

Reads : ../data/*.csv
Writes: ../documentation/eda/eda_summary.txt  (copy of the console output)
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA, DOCS = ROOT / "data", ROOT / "documentation" / "eda"
DOCS.mkdir(parents=True, exist_ok=True)

class Tee:
    def __init__(self, path): self.f = open(path, "w", encoding="utf-8")
    def write(self, s): sys.__stdout__.write(s); self.f.write(s)
    def flush(self): sys.__stdout__.flush(); self.f.flush()
sys.stdout = Tee(DOCS / "eda_summary.txt")

f = pd.read_csv(DATA / "fact_tickets.csv", parse_dates=["created_date", "created_datetime", "resolved_datetime"])
svc = pd.read_csv(DATA / "dim_service.csv")

res = f.status == "Resolved"
opn = ~res
met, br = (f.sla_outcome == "Met").sum(), (f.sla_outcome == "Breached").sum()
compliance = met / (met + br)

print("\n" + "=" * 70)
print("PART 1: REFERENCE KPIs (reconcile Power BI against these)")
print("=" * 70)
print(f"Total Tickets         : {len(f)}")
print(f"Resolved Tickets      : {res.sum()}")
print(f"Open Backlog          : {opn.sum()}")
print(f"SLA Met Tickets       : {met}")
print(f"SLA Breached Tickets  : {br}")
print(f"SLA Compliance %      : {compliance:.2%}")
print(f"Avg Resolution Hours  : {f.loc[res, 'resolution_hours'].mean():.2f}")
print(f"Overdue Open Tickets  : {(f.sla_outcome == 'Open - Overdue').sum()}")
print(f"Avg Backlog Age (days): {f.loc[opn, 'backlog_age_days'].mean():.2f}")

# ------------------------------------------------------------------
print("\n" + "=" * 70)
print("PART 2: BRIEF EDA")
print("=" * 70)
d = f.merge(svc, on="service_id")
d["met"] = d.sla_outcome == "Met"
d["breached"] = d.sla_outcome == "Breached"
d["is_open"] = d.status != "Resolved"
d["overdue"] = d.sla_outcome == "Open - Overdue"

def summary(by):
    g = d.groupby(by).agg(tickets=("ticket_id", "size"), met=("met", "sum"), breached=("breached", "sum"),
                          avg_res_hrs=("resolution_hours", "mean"), open_backlog=("is_open", "sum"),
                          overdue_open=("overdue", "sum"))
    g["compliance_%"] = (g.met / (g.met + g.breached) * 100).round(1)
    g["avg_res_hrs"] = g.avg_res_hrs.round(1)
    return g[["tickets", "compliance_%", "avg_res_hrs", "open_backlog", "overdue_open"]]

pd.set_option("display.width", 140)
print("\n-- Mix --")
print(d.ticket_type.value_counts().to_string())
print("\n-- Tickets by month --")
print(d.groupby(d.created_date.dt.strftime("%Y-%m")).size().to_string())
print("\n-- By priority (Q1) --")
print(summary("priority").to_string())
print("\n-- By category (Q1) --")
print(summary("category").sort_values("compliance_%").to_string())
print("\n-- SLA compliance %: category x priority (Q1; incidents + requests) --")
pv = d.groupby(["category", "priority"])[["met", "breached"]].sum()
print((pv.met / (pv.met + pv.breached) * 100).round(1).unstack().to_string())
print("\n-- By service, sorted by avg resolution hours (Q3) --")
print(summary("service_name").sort_values("avg_res_hrs", ascending=False).to_string())
print("\n-- By support team --")
print(summary("support_team").to_string())
print("\n-- Backlog by service (Q2) --")
print(summary("service_name").sort_values("open_backlog", ascending=False)[["open_backlog", "overdue_open"]].to_string())
print("\n-- Backlog by category (Q2) --")
print(summary("category").sort_values("open_backlog", ascending=False)[["open_backlog", "overdue_open"]].to_string())
print("\n-- 10 oldest open tickets --")
print(d[d.is_open].nlargest(10, "backlog_age_days")[["ticket_id", "service_name", "priority", "status", "backlog_age_days"]].to_string(index=False))

print(f"\n(Output also saved to {DOCS / 'eda_summary.txt'})")
_t = sys.stdout
sys.stdout = sys.__stdout__
_t.f.close()
