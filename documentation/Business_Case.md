# Business Case

## 1. Context

**Meridian Services Ltd** is a fictional mid-sized company with a central IT support function. The function handles **incidents** (something is broken or degraded) and **service requests** (a standard request such as access or equipment) across 12 IT services. Four support teams own the services: Service Desk, Infrastructure & Network, Applications Support, and Security & Access.

IT management agrees resolution-time targets (SLAs) by ticket type and priority. Management reviews performance from ticket data but does not have a single view that shows SLA misses, resolution speed and unresolved work together.

> The organisation and all data are fictional and simulated.

## 2. Problem Statement

IT management cannot easily see:

- which categories and priorities miss their SLA targets most often,
- where unresolved tickets are accumulating and how old they are,
- which services take longest to resolve,
- how the support teams compare.

Without this view, improvement effort is spread across the whole service desk instead of being aimed at the areas with the largest gaps.

## 3. Objectives

1. Measure SLA compliance by priority, category, service and support team.
2. Make the unresolved backlog visible, including how much of it is already overdue.
3. Identify the slowest-resolving services.
4. Provide prioritised, evidence-based operational recommendations.

## 4. Business Questions

1. Which incident categories and priorities miss SLAs most often?
2. Where is the unresolved ticket backlog accumulating?
3. Which services have the longest resolution times?
4. What operational improvements should IT management prioritise?

## 5. Stakeholders and Use

| Stakeholder | Use of the report |
| --- | --- |
| Head of IT / IT Service Delivery Manager | Monthly performance review and prioritisation |
| Support team leads | See their own SLA compliance, resolution time and backlog |
| Service owners | Understand performance of the services they own |

## 6. Scope

**In scope**

- One year of incident and service-request data (1 Jan to 31 Dec 2025) with a snapshot at 31 Dec 2025, 23:59
- SLA compliance, resolution time, backlog, overdue tickets, recurring issue types (category) and team comparison
- A three-page Power BI report, Python validation and EDA, and documentation

**Out of scope**

- Requirements gathering, user stories, process maps and ITSM tool configuration (this is a performance-analytics project)
- Business-hours calendars, on-hold or pause clocks, response-time SLAs
- Individual agent performance, cost, customer satisfaction, reopen rates
- Forecasting, machine learning and anomaly detection
- Any change to an ITSM tool or process

## 7. Success Criteria

- The dataset passes all validation checks and its business rules are documented.
- All 9 report KPIs reconcile exactly to the independent pandas calculation.
- Each of the four business questions is answered by at least one dashboard visual.
- Recommendations are traceable to specific results and avoid unsupported causal claims.
- The project can be reproduced from the documented files and steps.

## 8. Constraints and Assumptions

- Synthetic data, one 12-month window, 1,500 tickets.
- SLA targets are calendar hours, set by ticket type and priority (see Data Dictionary).
- SLA Compliance % covers resolved tickets only. Overdue open tickets are reported separately.
- All targets in the recommendations are proposed management targets, not proven outcomes.
