# ACTUS editions do not yet define one admissible adapter

23 October 2026. S1/S2; MC17/23/25/29–31. Plan:
docs/plans/accounting-actus-core-review-20261023.md. This continues the retained
specification and service review. No downloaded code was installed or executed.

The inspected service requests core 1.1.0, but this investigation did not
establish that dependency's resolved bytes or source. The official core
repository endpoint and the exact Maven Central POM URL returned 404. The
official distributions tree contains a license only, and its releases endpoint
returned an empty array. These observations concern those routes, not global
availability. Public repository search found a Java mirror describing itself
as a duplicate of the ACTUS core. Its inspected POM identifies 1.0-beta, not
1.1.0. It is useful source evidence for that mirror; it cannot stand in for the
service's dependency. Other language implementations were discovery leads only.

## Exact sources and inspected portions

All raw responses and decoded files are retained under
docs/design/research/software/actus-core-review-20261023/. Tree identities are
Git trees, not commit identifiers. Each decoded Git blob is independently
checked against its advertised SHA1 and retained with a SHA256.

| Source | Identity and inspected scope |
|---|---|
| Official dictionary | Tree 356f7663f26091105cc4fef4ae3496942dcf0ebf; event file complete; terms lines 1–16, 306–403, 1132–1184; versions lines 1–85 |
| Public Java mirror, simplexityware/actus-core | Tree 6d8cfd9a39ab7c1cdf91c9142992f9427af116b2; POM, PrincipalAtMaturity, ContractEvent, EventSequence, DayCountCalculator, ActualThreeSixtyFiveFixed, TimeAdjuster, BusinessDayAdjuster, Following, ContractRoleConvention, and IED/IP/MD payoff and state-transition functions read completely |
| Retained technical specification | PAM functions, lines 878–945, rechecked for initial exchange and maturity; earlier reading remains recorded separately |
| Local comparator | FundedYearInputsDraft/1 example and its input-driven executor; explicit Jan 4 11:00 draw, Jan 6 09:00 interest and Jan 6 10:00 principal repayment |

The mirror retains ACTUS copyright headers, but provenance correspondence to
the service release remains unproved. Its other functions, schedule factory,
attribute defaults and tests were not comprehensively inspected. No claim
about the current official core follows from this historical mirror.

## Findings that change adapter design

**Day count is materially different for the actual local example.**
DayCountCalculator.java:82–83 first applies TimeAdjuster.toFullHours.
TimeAdjuster.java:29–30 drops seconds/nanoseconds and rounds minutes at 30.
ActualThreeSixtyFiveFixed.java:19–26 counts complete LocalDateTime days, then
divides by 365. For Jan 4 at 11:00 through Jan 6 at 09:00 the rounded endpoints
are 46 hours apart: one complete day, whereas the local ACT365_calendar rule
uses two calendar dates. With principal 85.4 and rate 5%, the respective exact
formula values are 427/36500 and 427/18250. This is a source-level deduction,
not execution of the Java library; floating-point results have not been tested.

The earlier two-day algebraic substitution is conditional on supplying y=2/365.
It is not correspondence for these unmodified timestamps. An adapter must
declare accrual-date conventions independently of payment instants and retain
both. It may not strip times from all events just to make this example agree.
The actual service core remains unverified.

**Event sequence is an edition-dependent rule, not a universal rank.**
The dictionary event file labels itself version 1.4 dated 2023-12-08. Its FP
sequence is 2 and IP is 8; the mirror's EventSequence.java:51–65 uses IP offset
40 and FP offset 60. Their same-instant order is opposite. Both place IP before
MD, which is insufficient to establish general ordering equivalence. The
dictionary also has noncanonical sequence strings and duplicate sequence 22;
no generic strict total-order importer is justified from it.

ContractEvent.java:61 and 177–179 adds the type offset to epoch seconds. This
is different from lexicographic ordering by actual instant and then event type.
An MD at 09:00 has offset 150; an IP at 09:01 has offset 40. The later IP sorts
50 seconds before the earlier MD. Such a mirror ordering is wrong relative to
AccDSL's exact-instant chronology. Keep chronological instants and same-instant
precedence separate. Reject conflicting cross-contract prerequisites.

**Maturity formulas differ outside the zero-accrual special case.**
The retained technical specification's MD payoff includes scaled principal,
scaled accrued interest and accrued fees. Mirror POF_MD_PAM.java:23–25 includes
only scaled principal, while STF_MD_PAM.java:23–25 clears all three balances.
For unit factors and state principal -85.4, accrued interest -1, fees 0, the
specification expression is -86.4 and the mirror expression is -85.4. This
counterexample rejects unrestricted formula equivalence between these inspected
sources. It is not a finding about uninspected core 1.1.0.

The IED/IP formulas and borrower sign agree algebraically under the previously
stated unit-factor, zero-fee, zero-premium assumptions, once the year fraction
is supplied explicitly. Initialization still needs separate scrutiny:
PrincipalAtMaturity's absent-accrued-interest branch takes the last earlier
interest-schedule element without checking an empty list. Fee initialization
contains an unfinished branch. Specify opening accruals and unsupported cases;
do not allow undocumented defaults to supply an economic history.

**Business-day meaning is clearer; executable dictionary admission is not.**
Terms lines 306–403 explicitly shift to business days, and Following.java:42–47
advances until the calendar accepts the day. These support the intended
business-day reading where the retained specification says non-working day.
The dictionary distinguishes shifting before accrual calculation from shifting
after calculation and excludes specified noncyclical dates from its general
shift rule. Mirror BusinessDayAdjuster has distinct event and calculation time
methods. Do not apply one blanket shift to all dates.

The exact terms blob is not valid JSON: its description at line 15 uses curly
quotation marks as JSON delimiters. The exact versions blob also fails parsing
at line 55; it has additional visible syntax defects. Preserve those bytes as
source evidence and reject direct machine import. A separately reviewed repair
could define a derived edition, but no such repair or adoption is made here.
The event file parses. The terms additionally repeat SCMP for two distinct
business-day options; the mirror distinguishes CSMP and SCMP. Therefore even
syntactic repair alone would not establish an unambiguous adapter.

## Decision and remaining work

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Limit |
|---|---|---|---|---|---|
| Retain ACTUS as a candidate component | Boundary rules now have inspected anchors | Edition, ordering, accrual and maturity mismatches veto substitution | Actual core 1.1.0 bytes/source and dictionary relation remain unknown | Require one matched spec/dictionary/core bundle and explicit time adapter before conformance execution | No dependency adoption or runtime-equivalence claim |
| Continue company semantics now | Contract component is separable from posting/reporting design | No global continuation veto | Wider whole-company input and operation closure remains partial | Replace imported operating journals with explicit operation inputs in the existing company case | No empirical forecast or whole-phase completion |

The strongest alternative explanation is edition drift: newer official code
may repair the mirror differences. A pinned matched release plus inspected
functions and controlled conformance would overturn the component hold. The
weakest evidence is resolved dependency identity. These findings reject a
proposed substitution, not the ACTUS research direction.
