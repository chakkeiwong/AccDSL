# Audit the sector measurement-to-book posting boundary

25 October2026. S1–S5; MC02/06–13/16/19–22/24–28/30/32–35.
Baseline: Version4.27 and existing sector/native records. This is an internal
design audit before any new sector implementation or numerical comparison.

## Question and skeptical audit

Which retained sector computation can be connected to the declared company book
without changing its accounting target, importing notional cash twice, choosing
an arbitrary point from an interval, or presenting a report as an executed
journal? Inspect the actual method, state, units, timing, provenance and results.
The recently linked bank/insurer assessment profiles explicitly have no accounting
effect. They are wrong baselines for a posting bridge. The older finite
SectorCompany/1 report does have component financial deltas, but stays report-only
and uses its own historical profile and explicit context/scale assumptions.

The plan passes because it first discriminates those boundaries rather than
writing a universal adapter. Current promising candidates are the dated credit
schedule and insurance service/finance origins used by SectorCompany/1. Neither
is selected as a default before inspection. Exact state/report outputs must
identify the smallest honest posting contract; inability to identify it triggers
a documented design repair rather than an invented balancing journal.

## Evidence and assumption contract

Compare retained native source definitions, locked inputs, requests and full
outputs with current declared-book and module interfaces. Primary criterion:
an explicit account/memory/time/unit mapping with independently reconstructible
journal movements and named refused cases. Vetoes: source-version mismatch,
unexplained balances, inconsistent time, interval-to-point collapse, lost gross
flows, repeated opening capital or policy admission inferred from arithmetic.
Counts, clean schema validation and report balance are explanatory only.

For every proposed transferred convention record provenance, justification,
failure mode and early diagnostic. Keep the historical authority qualification;
do not claim current standards compliance. Reuse unchanged checked methods where
possible. No external source is newly interpreted without inspecting its technical
text and preserving the exact source. An inaccessible source blocks its claim,
not independent ready work.

1. Read and hash the retained sector-composition, dated-credit and insurance
   contracts and selected outputs, plus current book/module interfaces.
2. Trace a full candidate from supplied opening state through economic event,
   measurement, journal and cash to closing state. List missing meanings.
3. Compare at least the two candidates; choose a bounded executable repair only
   when its target and exact comparator are clear. Record the rejected shortcuts.
4. Write and audit that repair plan, then continue implementation and conformance
   without waiting for generic professional review. Preserve pending domain/human
   acceptance and full mission obligations. If no candidate is ready, identify
   the exact missing source or semantic fact and continue other ready design work.

Artifacts: data/accounting-master/sector-posting-boundary-20261025/.
Use bounded local reads, python3 -B and compact output. No model/API workers,
installations, GPU runs, commits, outreach or forecasts. All53/6/46 obligations
remain; S1–S5 partial,S6 held,S7 deferred.
