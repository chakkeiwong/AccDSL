# Named annual inventory scenario families

25 October 2026. S2–S5; MC11/13/15/23/24/26/28/32/35.

## Question, baseline and evidence contract
Can named unweighted alternatives execute exact AnnualInventoryProgram/1
requests while retaining all whole-period statements, failures, budgets and
unreached periods? Baselines: direct optional annual execution and the frozen
AnnualScenarioFamily/1 semantics for old operations. Primary pass criterion:
complete member requests/results and joint report vectors match their direct
counterparts. Require exact old-family behavior apart from explicit profile,
implementation and request metadata. Root validation, nonmutation, state/report
replay, IDs, horizon and budget checks veto promotion. Counts and timings are
explanatory only. Do not infer probabilities, exhaustive coverage, actual-history
membership, real accounting admission or forecast accuracy.

## Skeptical audit and implementation choice
The old family binds both its author and evaluator at module scope. Its author
only accepts AnnualProgramAuthoring/1; the new author produces a different runtime
request. Mutating globals or using the old evaluator for new requests is invalid.
Use an explicit AnnualInventoryFamily/1 with the frozen structure copied locally,
new authoring validation, and new runtime for both common-root and member runs.
Reuse invariant helpers directly from the frozen author for dates/digests/closed
records. Preserve the old family unchanged. Replayed equality includes every
financial field and diagnostic; profiles/hashes must be excluded only by an
explicit documented comparator. No recursive arbitrary metadata stripping.

## Assumptions and defaults
Common root and consecutive horizon are explicit caller declarations. Member
and period limits (64 each) are inherited bounded-reference constraints, not
scalability claims; budget counts members, not root validation. Zero budget still
validates root. Preserve structurally valid unknown/false findings for semantic
refusal. Distinct names with equal outputs remain distinct; unvisited members
retain assumptions and request identity with null results. No implicit weights.

## Execution and stop conditions
First check a two-member partial/full-sale family against direct requests. Then
check tax reassessment and residual-stock carry across periods; unknown findings,
unsupported methods, oversale, budgets/empty families, invalid root/horizon/IDs,
Unicode names, input preservation and tampered results/reports. Run old-family
and authoring regressions. Record source locks, cases, tests, manifest, replay and
result only after repair of any failure. Preserve first failures. A corrupted
root or unresolved substantive design decision stops dependent work; an ordinary
candidate failure triggers repair. No external engagement or forecasting.

After conformance, integrate both checked interfaces additively in Version 3.98,
refresh the complete 53/6/46 coverage and select the next substantive simulator
gap. S1–S5 remain partial; S6 held; S7 deferred until their own evidence exists.
