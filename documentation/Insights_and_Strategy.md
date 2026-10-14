# Insights & Strategy

> The data is **simulated**. Differences between teams, categories and services, and the likelihood of tickets staying open, were seeded in the generator (see Data Dictionary). These results demonstrate the analytical method and are not real-world evidence. The data shows **where** misses and backlog sit, not **why**, so no causal claims are made. Figures below reconcile to `documentation/eda/eda_summary.txt`.

## 1. Overall position (12 months, snapshot 31 Dec 2025)

| Measure | Value |
| --- | --- |
| Total tickets | 1,500 (1,100 incidents, 400 service requests) |
| Resolved / Open | 1,378 / 122 (8.1% open) |
| SLA Met / Breached | 1,127 / 251 |
| SLA Compliance % (resolved only) | 81.8% |
| Avg Resolution Hours | 29.2 |
| Overdue Open Tickets | 110 of 122 |
| Avg Backlog Age | 94.5 days (median 47.5) |

**Compliance including overdue tickets.** SLA Compliance % excludes open tickets. If the 110 overdue open tickets were counted as breaches, compliance would be 1,127 / (1,127 + 251 + 110) = about **75.7%**. Both views are useful: 81.8% describes resolved work, 75.7% describes total exposure.

Volume by month ranged from 99 (Aug) to 147 (Oct).

## 2. Q1: Which categories and priorities miss SLAs most often?

**By priority**

| Priority | Tickets | SLA Compliance % | Breached | Avg Resolution (h) |
| --- | --- | --- | --- | --- |
| P1 Critical | 45 | 62.2% | 17 | 4.3 |
| P2 High | 169 | 66.2% | 54 | 7.0 |
| P3 Medium | 787 | 81.4% | 136 | 23.0 |
| P4 Low | 499 | 90.0% | 44 | 50.0 |

**By category**

| Category | Tickets | SLA Compliance % | Breached |
| --- | --- | --- | --- |
| Performance | 149 | 71.7% | 39 |
| Hardware | 289 | 79.5% | 56 |
| Software | 417 | 81.0% | 72 |
| Access & Permissions | 414 | 84.9% | 56 |
| Network & Connectivity | 176 | 86.8% | 22 |
| Security | 55 | 88.2% | 6 |

**Category x priority (weakest cells with a meaningful base)**

| Cell | SLA Compliance % | Resolved tickets |
| --- | --- | --- |
| Performance, P2 | 56.0% | 25 |
| Software, P2 | 58.5% | 41 |
| Access & Permissions, P2 | 63.6% | 33 |
| Network & Connectivity, P2 | 71.4% | 21 |
| Hardware, P1 | 54.5% | 11 |
| Software, P1 | 50.0% | 10 |

Performance at P1 shows 0% but rests on 3 tickets, and Security at P1 has none, so P1 cells should be read with caution.

**Reading.** Compliance is lowest at the highest priorities, which also have the tightest targets (4h and 8h). In absolute terms, most breaches sit in P3 (136 of 251) because of its volume. Performance is the weakest category by rate and Software is the largest by breach count.

## 3. Q2: Where is the backlog accumulating?

| Service | Open | | Category | Open |
| --- | --- | --- | --- | --- |
| Identity & Access | 22 | | Access & Permissions | 44 |
| Laptops & Desktops | 19 | | Software | 38 |
| Email & Calendar | 17 | | Hardware | 16 |
| ERP (Finance & Procurement) | 17 | | Performance | 11 |
| Collaboration Tools | 12 | | Network & Connectivity | 9 |
| HR Portal, Telephony | 7 each | | Security | 4 |

- The top four services hold **75 of the 122** open tickets. Access & Permissions and Software hold **82 (67%)**.
- By priority, open tickets are P4 (57), P3 (56) and P2 (9). There are **no open P1 tickets**. 110 are overdue: P3 53, P4 48, P2 9.
- By team: Service Desk 52, Applications Support 27, Security & Access 26, Infrastructure & Network 17.
- By type: 85 incidents and 37 service requests.
- **Age:** 48 tickets are older than 90 days and 27 are older than 180 days. The 10 oldest are P3 or P4 and are 272 to 356 days old (for example REQ-0014, Identity & Access, 355.6 days; INC-0059, ERP, 343.4 days).

**Reading.** The backlog is mostly low-to-medium priority work that has aged past its target. It is concentrated in a few services and two ticket categories. Whether these tickets are still valid cannot be told from the data.

## 4. Q3: Which services resolve slowest?

| Service | Tickets | Avg Resolution (h) | SLA Compliance % |
| --- | --- | --- | --- |
| HR Portal | 82 | 40.0 | 70.7% |
| Telephony | 45 | 37.6 | 71.1% |
| ERP (Finance & Procurement) | 124 | 34.4 | 67.3% |
| Endpoint Security | 40 | 34.3 | 86.1% |
| CRM | 76 | 33.5 | 65.8% |
| Identity & Access | 163 | 32.1 | 84.4% |
| Laptops & Desktops | 343 | 29.9 | 84.9% |
| VPN & Remote Access | 110 | 28.5 | 83.7% |
| Collaboration Tools | 165 | 26.0 | 90.2% |
| Wi-Fi & LAN | 107 | 25.7 | 79.6% |
| Email & Calendar | 166 | 21.1 | 91.3% |
| Printing | 79 | 19.7 | 78.7% |

**Reading.** HR Portal, Telephony and ERP take longest on average. Hours and compliance do not rank services identically because average hours are not adjusted for priority mix: Endpoint Security is slow (34.3h) but compliant (86.1%), while CRM and ERP combine long resolution with the lowest compliance (65.8% and 67.3%). Read both together.

## 5. Support teams

| Team | Tickets | SLA Compliance % | Avg Resolution (h) | Breached | Open |
| --- | --- | --- | --- | --- | --- |
| Applications Support | 282 | 67.8% | 35.8 | 82 | 27 |
| Infrastructure & Network | 262 | 80.0% | 28.7 | 49 | 17 |
| Security & Access | 203 | 84.7% | 32.5 | 27 | 26 |
| Service Desk | 753 | 86.7% | 26.1 | 93 | 52 |

Applications Support has the lowest compliance and longest resolution time. The Service Desk has the highest compliance but, handling about half of all tickets, the most breaches (93) and the largest open backlog (52).

## 6. Q4: Recommendations

All targets are **proposed management targets**, not proven results.

| Priority | Area | Recommended action | Evidence | Proposed target |
| --- | --- | --- | --- | --- |
| P1 | Backlog | Triage the 110 overdue open tickets, starting with Identity & Access, Laptops & Desktops, Email & Calendar and ERP. Close or re-validate stale tickets | 110 of 122 overdue; 27 older than 180 days; top four services hold 75 | No open ticket older than 180 days at the monthly review |
| P1 | High-priority handling | Review the P1 and P2 breaches, starting with Performance, Software and Access & Permissions at P2 | P1 62.2%, P2 66.2% versus P3 81.4%, P4 90.0% | SLA compliance of 90% or more for P1 and P2 |
| P2 | Ticket types | Review how Access & Permissions and Software tickets are queued and tracked | 82 of 122 open tickets (67%) | No Access & Permissions or Software ticket open beyond its SLA target at the monthly review |
| P2 | Team workflow | Review Applications Support workflow and the slowest services (HR Portal, Telephony, ERP) | Lowest compliance (67.8%) and longest resolution (35.8h) | Applications Support compliance of 80% or more |
| P3 | Reporting | Report Overdue Open Tickets next to SLA Compliance % | 81.8% compliance versus 75.7% including overdue tickets | Both metrics in every monthly management pack |

Each action is a prioritisation or investigation step. Before changing staffing, tooling or process, management should establish **why** the affected tickets were slow, which this dataset cannot show.

## 7. What the data cannot tell us

- **Causes.** There are no fields for root cause, handoffs, waiting-on-customer time, agent workload or change activity.
- **Trend in backlog.** Only a single snapshot is held.
- **Business-hours effects.** Targets are calendar hours, so out-of-hours creation and weekends count fully.
- **P1 reliability.** With 45 P1 tickets, a handful of cases moves the P1 rate noticeably.
- **Real-world generalisation.** All patterns are seeded in simulated data.
