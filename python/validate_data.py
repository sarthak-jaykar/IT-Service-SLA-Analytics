"""
validate_data.py
Runs data-quality and business-rule checks on the simulated IT ticket data.

Reads : ../data/*.csv
Writes: ../documentation/validation_report.txt  (copy of the console output)
Exit code is 1 if any check fails.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA, DOCS = ROOT / "data", ROOT / "documentation"
DOCS.mkdir(exist_ok=True)

class Tee:
    def __init__(self, path): self.f = open(path, "w", encoding="utf-8")
    def write(self, s): sys.__stdout__.write(s); self.f.write(s)
    def flush(self): sys.__stdout__.flush(); self.f.flush()
sys.stdout = Tee(DOCS / "validation_report.txt")

SNAPSHOT = pd.Timestamp("2025-12-31 23:59:00")
SLA = {("Incident", "P1 Critical"): 4, ("Incident", "P2 High"): 8,
       ("Incident", "P3 Medium"): 24, ("Incident", "P4 Low"): 72,
       ("Service Request", "P3 Medium"): 48, ("Service Request", "P4 Low"): 120}

f = pd.read_csv(DATA / "fact_tickets.csv", parse_dates=["created_date", "created_datetime", "resolved_datetime"])
svc = pd.read_csv(DATA / "dim_service.csv")
dte = pd.read_csv(DATA / "dim_date.csv", parse_dates=["date", "month_start"])

results = []
def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail else ""))

res = f.status == "Resolved"
opn = ~res

print("=" * 70)
print("PART 1: VALIDATION")
print("=" * 70)

# 1. Structure & keys
check("Row counts", len(f) == 1500 and len(svc) == 12 and len(dte) == 365,
      f"fact={len(f)}, service={len(svc)}, date={len(dte)}")
check("fact_tickets has 13 columns", f.shape[1] == 13)
check("ticket_id is unique", f.ticket_id.is_unique)
check("No duplicate rows (ignoring ticket_id)", not f.drop(columns="ticket_id").duplicated().any())
required = ["ticket_id", "ticket_type", "created_date", "created_datetime", "service_id",
            "category", "priority", "status", "sla_target_hours", "sla_outcome"]
check("No nulls in required fields", f[required].notna().all().all())
check("Every service_id exists in dim_service", f.service_id.isin(svc.service_id).all())
check("Every created_date exists in dim_date", f.created_date.isin(dte.date).all())
check("dim_service / dim_date keys unique", svc.service_id.is_unique and dte.date.is_unique)

# 2. Dates
check("created_datetime within 2025", f.created_datetime.between("2025-01-01", "2025-12-31 23:59:59").all())
check("created_date matches created_datetime", (f.created_datetime.dt.normalize() == f.created_date).all())
check("resolved_datetime >= created_datetime", (f.loc[res, "resolved_datetime"] >= f.loc[res, "created_datetime"]).all())
check("resolved_datetime <= snapshot", (f.loc[res, "resolved_datetime"] <= SNAPSHOT).all())

# 3. Status consistency
check("Resolved: has resolved_datetime & resolution_hours, no backlog_age_days",
      f.loc[res, ["resolved_datetime", "resolution_hours"]].notna().all().all() and f.loc[res, "backlog_age_days"].isna().all())
check("Open/In Progress: has backlog_age_days, no resolved_datetime/resolution_hours",
      f.loc[opn, "backlog_age_days"].notna().all() and f.loc[opn, ["resolved_datetime", "resolution_hours"]].isna().all().all())

# 4. Calculations
diff_h = (f.loc[res, "resolved_datetime"] - f.loc[res, "created_datetime"]).dt.total_seconds() / 3600
check("resolution_hours matches timestamp difference (tol 0.1h)", ((diff_h - f.loc[res, "resolution_hours"]).abs() <= 0.1).all())
age_h = (SNAPSHOT - f.loc[opn, "created_datetime"]).dt.total_seconds() / 3600
check("backlog_age_days matches snapshot - created (tol 0.01d)", ((age_h / 24 - f.loc[opn, "backlog_age_days"]).abs() <= 0.01).all())
expected_target = [SLA.get((t, p)) for t, p in zip(f.ticket_type, f.priority)]
check("sla_target_hours matches policy for every type/priority", (pd.Series(expected_target) == f.sla_target_hours).all())
check("Service Requests are only P3/P4", f.loc[f.ticket_type == "Service Request", "priority"].isin(["P3 Medium", "P4 Low"]).all())

exp = pd.Series("", index=f.index)
exp[res] = np.where(diff_h <= f.loc[res, "sla_target_hours"], "Met", "Breached")
exp[opn] = np.where(age_h > f.loc[opn, "sla_target_hours"], "Open - Overdue", "Open - Within SLA")
mism = (exp != f.sla_outcome).sum()
check("sla_outcome agrees with SLA rules", mism == 0, f"mismatches={mism}")

# 5. Allowed values
check("ticket_type values", set(f.ticket_type) <= {"Incident", "Service Request"})
check("priority values", set(f.priority) <= {"P1 Critical", "P2 High", "P3 Medium", "P4 Low"})
check("status values", set(f.status) <= {"Resolved", "Open", "In Progress"})
check("category values", set(f.category) <= {"Hardware", "Software", "Network & Connectivity",
                                              "Access & Permissions", "Performance", "Security"})
check("sla_outcome values", set(f.sla_outcome) <= {"Met", "Breached", "Open - Overdue", "Open - Within SLA"})

# 6. Plausibility ranges
met, br = (f.sla_outcome == "Met").sum(), (f.sla_outcome == "Breached").sum()
compliance = met / (met + br)
inc = f[f.ticket_type == "Incident"]
check("Total tickets 1,400-1,600", 1400 <= len(f) <= 1600, str(len(f)))
check("Overall SLA compliance 70-90%", 0.70 <= compliance <= 0.90, f"{compliance:.1%}")
check("Backlog 6-12% of tickets", 0.06 <= opn.mean() <= 0.12, f"{opn.mean():.1%}")
check("P1 is 3-6% of incidents", 0.03 <= (inc.priority == "P1 Critical").mean() <= 0.06, f"{(inc.priority == 'P1 Critical').mean():.1%}")

passed = sum(results)
print(f"\nVALIDATION RESULT: {passed}/{len(results)} checks passed")

_t = sys.stdout
sys.stdout = sys.__stdout__
_t.f.close()
sys.exit(0 if passed == len(results) else 1)
