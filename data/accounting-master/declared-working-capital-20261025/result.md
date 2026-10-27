# Trace-derived working-capital result

Four supported schedules reconcile verified program traces to actual report-period
opening and closing balances. Normal,two-chart,stopped-prefix,carry and next-period
cases provide140 exact checks.15 focused and36 operating/program regression methods
are required by verify.py;recorded status appears in checks.json and manifest.json.
Receivables0+50-35=15;inventory20+30-25=25;supplier payables0+30-20=10;
payroll payable0+10-8=2. Gross activity,typed inputs and event/result hashes remain.

Attempt01 exposed a classification bug: unsupported +1/-1 postings within one event
were hidden by a zero net journal. A smaller valid diagnostic confirmed it after
the first fixture exceeded the existing structure bound. The repair inspects gross
monetary postings,retains all bounds and rejects the unsupported movement. Both logs
and original implementation are preserved. This rejected the candidate,not the
method direction. A noncash unrelated method leaves an explicit cash-bridge residual;
no balancing plug is inserted. Second-period reports exclude prior movement history.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain repaired bounded schedules if recorded verification passes | Independent roll-forwards and exact verified trace lineage | Gross-offset,method identity,tamper,period and disclosure checks pass | Missing ageing,maturity,valuation,source population and full notes | Integrate,refresh,financing clocks | Complete notes,accounting admission,production or mission closure |

Strongest alternative explanation:financial engine and schedules share sign/premise
conventions. Independent expected values and unsupported-method counterexamples
address local errors;they do not establish broader disclosures. Counts are descriptive.
S1–S5 partial,S6 held,S7 deferred. No whole requirement closes.
