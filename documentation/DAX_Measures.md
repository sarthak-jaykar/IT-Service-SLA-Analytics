# DAX Measures

The model has **9 measures** and **no calculated columns**. SLA targets, resolution hours, outcomes and backlog age are prepared in the source data (see Data Dictionary), so each measure is a simple count or average.

All measures are stored on `fact_tickets`.

## Volume

```DAX
Total Tickets = COUNTROWS ( fact_tickets )
```
Count of tickets in the current filter context.

```DAX
Resolved Tickets =
CALCULATE ( COUNTROWS ( fact_tickets ), fact_tickets[status] = "Resolved" )
```
Tickets with status Resolved.

## Backlog

```DAX
Open Backlog =
CALCULATE ( COUNTROWS ( fact_tickets ), fact_tickets[status] IN { "Open", "In Progress" } )
```
Unresolved tickets at the snapshot date.

```DAX
Overdue Open Tickets =
CALCULATE ( COUNTROWS ( fact_tickets ), fact_tickets[sla_outcome] = "Open - Overdue" )
```
Open tickets whose age already exceeds their SLA target. Shown separately from SLA Compliance %.

```DAX
Avg Backlog Age (days) = AVERAGE ( fact_tickets[backlog_age_days] )
```
`backlog_age_days` is blank for resolved tickets, so `AVERAGE` covers open tickets only.

## SLA performance

```DAX
SLA Met Tickets =
CALCULATE ( COUNTROWS ( fact_tickets ), fact_tickets[sla_outcome] = "Met" )
```

```DAX
SLA Breached Tickets =
CALCULATE ( COUNTROWS ( fact_tickets ), fact_tickets[sla_outcome] = "Breached" )
```
Resolved tickets that took longer than their target.

```DAX
SLA Compliance % =
DIVIDE ( [SLA Met Tickets], [SLA Met Tickets] + [SLA Breached Tickets] )
```
Resolved tickets only. Open tickets are in neither numerator nor denominator, so compliance is not inflated by tickets that have not closed. Overdue open tickets are reported by `Overdue Open Tickets`.

## Speed

```DAX
Avg Resolution Hours = AVERAGE ( fact_tickets[resolution_hours] )
```
`resolution_hours` is blank for open tickets, so `AVERAGE` covers resolved tickets only. The value is elapsed calendar hours and is not adjusted for priority mix.

## Formatting

| Measure | Format | Dashboard display |
| --- | --- | --- |
| Total Tickets, Resolved Tickets, Open Backlog, SLA Met Tickets, SLA Breached Tickets, Overdue Open Tickets | Whole number, thousands separator | As is |
| SLA Compliance % | Percentage | 1 decimal on cards, charts and tables |
| Avg Resolution Hours, Avg Backlog Age (days) | Decimal | 1 decimal |

## Model settings

- Relationships: `dim_service[service_id]` to `fact_tickets[service_id]` and `dim_date[date]` to `fact_tickets[created_date]`, both one-to-many with single-direction filtering.
- `dim_date[month_label]` is sorted by `dim_date[month_start]`.
- Key columns used only for relationships are hidden from report view.

## Reconciliation (no filters applied)

| Measure | Power BI | Python reference |
| --- | --- | --- |
| Total Tickets | 1,500 | 1,500 |
| Resolved Tickets | 1,378 | 1,378 |
| Open Backlog | 122 | 122 |
| SLA Met Tickets | 1,127 | 1,127 |
| SLA Breached Tickets | 251 | 251 |
| SLA Compliance % | 81.79% | 81.79% |
| Avg Resolution Hours | 29.18 | 29.18 |
| Overdue Open Tickets | 110 | 110 |
| Avg Backlog Age (days) | 94.54 | 94.54 |

Reference values are produced by `python/exploratory_analysis.py` and saved in `documentation/eda/eda_summary.txt`.
