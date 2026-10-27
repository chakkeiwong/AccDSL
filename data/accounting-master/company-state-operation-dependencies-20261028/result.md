# Native operations expose distinct output and feasibility dependencies

28 October 2026. Unified T01/T03/C04; MC08/09/10/11/13/18/19/20/28/33.
Plan: docs/plans/company-state-operation-dependencies-20261028.md.

The new adapter derives exact sparse affine expressions directly from the
existing TypedAffineHistory/1 contract. It traces account and memory values
from their openings through every declared event, then records dependencies
for requested snapshots, reported measurements, balance and state constraints.
It does not introduce an independent catalogue of assumed operations.

The final attempt04 passes264 checks:42 queries across all three independently
retained full histories,11 event prefixes, complete constraint coverage and
adverse controls. Hand-derived cash, held-claims and component-memory formulas
agree with the adapter. The complete native replay agrees with each retained
history before its snapshot values are used as comparators.

The distinction between outputs and feasibility is substantive. A query that
subtracts cash from itself has no remaining scalar output dependency. The
original cash inputs still enter intermediate cash constraints and remain in
the returned domain population. Likewise, balanced postings cancel event
amounts from the aggregate balance equation without removing those events or
their account effects. Every original domain, obligation and scope exclusion
is retained. No variable is removed and no executable reduction is returned.

This establishes an exact dependency inspection within the supplied affine
history. It is a first executable part of operation-driven state construction,
not a proof that these operations cover a real company. Nonlinear behavior,
contract-population discovery, collections, industry/basis composition and
generic operating preconditions remain outside the profile. The adapter keeps
operational_preconditions_checked=false. Measurement-only definitions cannot
be treated as complete histories.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain native dependency inspection | Exact formulas match all42 queries over three full native histories |264 checks pass | Generality outside the additive typed profile | Extend explicit operation/population contracts while preserving native rules | General company-state constructor |
| Keep feasibility dependencies separate | Every state constraint and balance condition retained at all11 prefixes | Cancellation controls preserve all variables | Nonlinear guards and economic preconditions not supplied | Derive those dependencies from their own native profiles | Permission to remove events or compress state |
| Continue actual-source construction | Reported debt measurements remain separate from unknown issuer history | Observation-only input refused as a history | Legal instruments, openings, access and accounting memory | Resolve supported source-to-operation links or retain obligations | Actual company simulation or release readiness |

Attempts01/02 stopped on harness/fixture mistakes: attachment witness
namespacing and the native obligation record structure. Both code/failures are
retained. Attempt03 passed but described three witnesses as two in its manifest;
attempt04 adds an exact population check and corrects the metadata. These were
engineering repairs, not evidence against company-state construction.

The final manifest binds the exact native modules, source history, plan,
command, commit, Python, CPU-only execution, elapsed time and output paths.
No stochastic comparison or default-policy change occurred. Post-run review:
symbolic equality answers which supplied scalars affect an output; it does not
establish economic sufficiency, source truth or completeness of the declared
operation population. Those distinctions remain in the executable result.
