# Pre-implementation audit — 24 October 2026

MC05/11/13/16/24/26/28/35; G2/G4; S2–S5. The research/engineering question is
whether selected events can continue after the first following-period assessment
without losing liability provenance or changing tax expense through payment.
The baseline is the complete frozen first-assessment result and its actual
carried opening. Aggregate-only payment is insufficient once two vintages exist.

The plan passes after making two details explicit: settlement conservation must
link all vintage amounts to actual dated cash flows, and new native events leave
current tax assessed only through its prior endpoint. They cannot imply a fresh
assessment. Pure apply must retain the entire predecessor, trace and findings.
No prior source or profile will be modified.

| Choice | Provenance and justification | Failure mode | Early diagnostic | Status |
| --- | --- | --- | --- | --- |
| Explicit positive allocations | Active plan; avoids guessing settlement order | Correct total but wrong liability settled | Equal-total different-vintage cases | Reviewed scoped design |
| Partial assessment inside a full financial year | Existing interval contract | No valid time left for ordinary events | June 30 assessment, July 1 event; year-end rejection | Fixture assumption |
| Existing native adapters and 26 accounts | Frozen continuation | Tax footprint or state projection | Account-set, unchanged tax and statement ties | Baseline reuse |
| Operating cash classification | Existing hypothetical payment model | Mistaken statutory generalization | Exact old/new flow linkage; no legal claim | Scoped inherited convention |
| Rational arithmetic and explicit authority | Existing caller contract | Rounding, unknown selection treated as true | Fractional splits and unknown/false authorization | Reviewed engineering default |

Primary criterion: independent exact payment arithmetic, per-vintage and aggregate
conservation, state/schema and journal integrity, actual-opening statement ties,
ordered successful prefixes, complete apply and protected bytes. Invalid hashes,
broken invariants, missing required evidence or a wrong oracle veto recording
and trigger repair. A rejected payment stops that operation and preserves prior
successful work; it does not veto the research direction. Counts and runtime are
explanatory only. No stochastic ranking, legal correctness, annual readiness,
forecast claim or whole-company completeness follows. Evidence is retained here
with request/result cases, checks, test observation and replayable manifest.
