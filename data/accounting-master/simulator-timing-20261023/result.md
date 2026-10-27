# Annual reconciliation does not establish payment feasibility

23 October 2026. MC13–18/24/26/28. All 63 exact checks pass across six
Northstar combinations: the retained 7% and 9% stress rates, each with floating
shares 0, 1/2 and 1. This is a documentary design diagnostic, not execution of
the proposed AccDSL runtime.

The original proposed journal order reproduces every closing account, cash-flow
category, cash bridge, balance sheet, income, equity roll-forward and indirect
operating cash-flow reconciliation. Moving the 160 supplier payment ahead of
the 280 collections leaves the unconstrained closing accounting unchanged.
It nevertheless requires 85.4 more cash than the opening 74.6 available at
that payment. Under the stated no-facility/full-payment rule, the payment is
refused and no part of its journal is applied. Subsequent outcomes after that
failure have not been computed.

This counterexample explains why the successor profile needs dated claims and
funding decisions. It does not invalidate the original Northstar order or imply
that an actual company has no credit facility. When payment timing is unknown,
the two schedules remain alternatives; a feasible annual total does not select
the feasible order.

The successor documentary schedule schema has 15 complete input cases and
21 passing checks after the boundary repair. It rejects missing/duplicate events, cyclic dependencies,
contradictory dates, an event on the exclusive end date, unknown fields,
an unresolved projection reference and an invalid calendar date. Unknown
collection timing and unordered same-instant events return unresolved timing;
unknown facility access at a cash shortfall returns unresolved funding. An
explicit dependency resolves the simultaneous collection/payment case.
Reversing the input array preserves the result because dates and dependencies
determine execution. These bodies are a proposed annotation subprofile, not
the general claim, behaviour or whole-company text language.

Recovery review exposed an exact-boundary defect: comparing only calendar dates
accepted a one-hour shift of either fiscal boundary. Both invalid schedules
were reproduced before repair (`boundary-repair-before.json`). The checker now
requires the retained fiscal dates at midnight UTC; two additional controls
reject shifted start/end instants. Original 15 case bodies and the prior
19-check outputs are preserved. `facility_required` denotes a cash-only
shortfall needing additional funding; it does not assert that a facility exists
or can legally be drawn.

| Decision | Primary criterion | Veto diagnostic | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Accept the bounded timing counterexample | Original outputs reproduced; changed order produces stated shortfall | Balanced journals, exact retained outputs, refusal atomicity and preserved source bytes pass | Real invoice dates, facility access and post-default rules are outside this fixture | Specify dated obligation, schedule and funding-input records; add known/unknown/ambiguous cases | General simulator correctness or forecasting validity |
| Retain the existing Northstar case | No baseline output changed | Original source hashes preserved | Aggregate annual drivers do not identify per-claim schedules | Extend under a distinct successor profile | Original example is wrong, or current text parser supports the extension |

No stochastic comparison occurred, so there is no statistical ranking. The
63-check count is explanatory; the material evidence is the common closing
result together with the different settlement feasibility. The primary source
and exact command/environment/wall time are in `run-manifest.json`; detailed
cases are in `checks.json`. Safe replay is `verify.py`, which reads the original
package and writes only this directory's diagnostic outputs.

`schedule.schema.json`, `schedule-cases.json` and `schedule-checks.json` preserve
the additional specification and results. Safe replay is `verify_schedules.py`;
`schedule-manifest.json` records its environment and measured verification
duration. The one-time `prepare_schedules.py` preserves existing examples and
must not be rerun to overwrite them.

Red-team finding: payment order is stipulated, and a real committed facility
could remove the shortfall. Therefore the result supports explicit schedule
and funding inputs, not a prediction of default. Unknown timing or unknown
facility access must not be converted to known economic failure.
