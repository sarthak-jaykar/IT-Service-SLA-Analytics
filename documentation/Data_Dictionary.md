# Data Dictionary

All data is **fictional and synthetic**, produced by `python/generate_data.py` with a fixed random seed (42). Snapshot date: **31 Dec 2025, 23:59**.

## Model

```
dim_service ───► fact_tickets ◄─── dim_date
```

| Relationship | Cardinality | Filter direction |
| --- | --- | --- |
| `dim_service[service_id]` → `fact_tickets[service_id]` | One to many | Single |
| `dim_date[date]` → `fact_tickets[created_date]` | One to many | Single |

## fact_tickets (1,500 rows)

| Column | Type | Description |
| --- | --- | --- |
| `ticket_id` | Text | Unique key. `INC-0001` for incidents, `REQ-0001` for service requests |
| `ticket_type` | Text | Incident or Service Request |
| `created_date` | Date | Date part of `created_datetime`; used for the date relationship |
| `created_datetime` | Date/Time | Ticket creation timestamp |
| `resolved_datetime` | Date/Time | Resolution timestamp. Blank if unresolved at the snapshot |
| `service_id` | Text | Foreign key to `dim_service` |
| `category` | Text | Hardware, Software, Network & Connectivity, Access & Permissions, Performance, Security |
| `priority` | Text | P1 Critical, P2 High, P3 Medium, P4 Low |
| `status` | Text | Resolved, Open or In Progress |
| `sla_target_hours` | Whole number | Resolution target from the SLA policy (policy, not outcome) |
| `resolution_hours` | Decimal | Elapsed calendar hours from creation to resolution. Resolved tickets only |
| `sla_outcome` | Text | Met, Breached, Open - Within SLA, or Open - Overdue (actual outcome) |
| `backlog_age_days` | Decimal | Days from creation to the snapshot. Open and In Progress tickets only |

## dim_service (12 rows)

| Column | Description |
| --- | --- |
| `service_id` | Key, S01 to S12 |
| `service_name` | IT service |
| `service_group` | End User Computing, Collaboration, Network, Business Applications, Security |
| `support_team` | Owning team |

| Support team | Services |
| --- | --- |
| Service Desk | Laptops & Desktops, Printing, Email & Calendar, Collaboration Tools |
| Infrastructure & Network | VPN & Remote Access, Wi-Fi & LAN, Telephony |
| Applications Support | ERP (Finance & Procurement), HR Portal, CRM |
| Security & Access | Identity & Access, Endpoint Security |

## dim_date (365 rows)

| Column | Description |
| --- | --- |
| `date` | Calendar date, 1 Jan to 31 Dec 2025 (relationship key) |
| `month_start` | First day of the month. Used as the sort-by column for `month_label` |
| `month_label` | Short month name (Jan to Dec) |

## SLA policy

Resolution targets in **calendar hours** (24x7, no pause clock).

| Ticket type | P1 Critical | P2 High | P3 Medium | P4 Low |
| --- | --- | --- | --- | --- |
| Incident | 4 | 8 | 24 | 72 |
| Service Request | n/a | n/a | 48 | 120 |

Service requests are generated only at P3 and P4.

## Derived-field rules

| Field | Rule |
| --- | --- |
| `resolution_hours` | (`resolved_datetime` - `created_datetime`) in hours, rounded to 2 decimals |
| `backlog_age_days` | (snapshot - `created_datetime`) in days, rounded to 2 decimals |
| `sla_outcome` (resolved) | Met if `resolution_hours` <= `sla_target_hours`, otherwise Breached |
| `sla_outcome` (open) | Open - Overdue if age in hours > `sla_target_hours`, otherwise Open - Within SLA |

## Generator rules (disclosed)

The generator builds in realistic differences so the analysis has patterns to find. Because they are seeded, results illustrate the method and are not real-world evidence.

- **Volume:** weighted by service (Laptops & Desktops highest), mild monthly seasonality (higher in Oct and Nov), weekdays weighted above weekends, creation times concentrated in working hours.
- **Priority mix (incidents):** P1 4.5%, P2 15%, P3 50%, P4 30.5%. Service requests: P3 60%, P4 40%.
- **Categories:** each service draws only from plausible categories. Service requests use Hardware, Software and Access & Permissions only.
- **Resolution time:** target multiplied by a log-normal ratio (sigma 0.55). The median ratio is set by priority (P1 0.80, P2 0.72, P3 0.55, P4 0.45 for incidents; 0.60 and 0.50 for requests) and scaled by support team (Service Desk 0.90, Infrastructure & Network 1.15, Applications Support 1.25, Security & Access 1.05), category (Hardware 1.20, Software 1.00, Network 1.00, Access 0.85, Performance 1.25, Security 1.05), and service (ERP 1.15, Telephony 1.20). Minimum 15 minutes, maximum 6x target.
- **Unresolved tickets:** a ticket is unresolved if its simulated resolution falls after the snapshot, or if it is randomly marked "stuck". Stuck probability rises for recently created tickets, is higher for ERP, Identity & Access, Telephony, CRM and HR Portal, and lower for P1 (x0.15) and P2 (x0.6). Open tickets are split 40% Open and 60% In Progress.

## Validation

`python/validate_data.py` runs 28 checks and writes `documentation/validation_report.txt`: row counts, key uniqueness, duplicates, nulls, referential integrity, date logic, status consistency, recalculation of `resolution_hours`, `backlog_age_days`, `sla_target_hours` and `sla_outcome`, allowed values, and plausibility ranges (total tickets, overall compliance, backlog share, P1 share).
