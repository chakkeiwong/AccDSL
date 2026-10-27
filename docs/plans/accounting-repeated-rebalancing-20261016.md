# Repeated hedge rebalancing with preserved cumulative measurement

16 October2026. R03/P17-05.05; MC02/04/05/08/11/13/16/17/19/24/25/28/30/32/33/34/35;
G2/G4/G7/G13/G15/G16/G18. Documentary exact method; no runtime/empirical work.

## Skeptical audit and question

The retained FinancingComponents/2 rebalancing example permits one prospective
measurement after a ratio change and then refuses further observations. Its
state has no cumulative anchor for arbitrary later observations. Extending
the same per-segment lower-of calculation would be wrong: previous cumulative
ineffectiveness can reverse, while a sum of segment minima suppresses that
reversal. This is a target mismatch, not a numerical-tolerance issue.

Use IFRS9.6.5.11(a)–(c), B6.5.7–21 in the retained EU2023/1803 source. Preserve
the unchanged hedging instrument and allow repeated increases to hedged-item
volume under B6.5.17. This finite method does not reduce either designated
volume or add hedging instruments; those require their own cumulative allocation
and partial-discontinuation methods. All broader original obligations survive.

Main question: can any finite sequence of admitted item-layer additions and
observations retain cumulative OCI/ineffectiveness and each layer's origin,
including reversals? Candidate: compute total hedged-item change from all layer
origins and apply the lower-of rule to cumulative derivative gain at each
observation, posting only changes in cumulative reserve/profit. A ratio change
requires a same-date old-designation measurement and revised documentation.

Baseline: preserved finite /2 example and the exact source rule. Discriminating
case: 100 units at80, observe90 with derivative gain1200, reserve1000 and
ineffectiveness200; add10 units at90, then observe95 with derivative1400 and
item loss1550. Correct reserve is1400 and cumulative ineffectiveness0. A reset
formula produces reserve1200 and incorrectly retains profit200. The journal
must record derivative+200, OCI+400 and profit−200. An equal same-sign per-step
comparison would miss this defect.

## Evidence contract and assumption audit

Primary criterion: independent expected cumulative/reserve/P&L values and dated
balanced journals agree over two additions and later gains/losses/reversals;
an independently summed incremental item path must equal the origin-based
valuation. The wrong-reset construction must fail the source criterion.
Vetoes: stale measurement, wrong layer price/date, changed objective disguised
as rebalancing, missing eligibility/valuation evidence, silent removal, bad
context, failed book/cumulative identity or predecessor mutation. Such a
failure triggers retained repair. Counts, PDF bounds and runtime are explanatory.

Continuation veto: contradictory/unavailable required source, corrupted fixed
inputs, or a necessary unauthorized runtime/empirical action. A wider method
gap or an unsupported actual finding blocks only that dependent claim.

| Material choice | Provenance/status | Why used; failure mode | Earliest check |
|---|---|---|---|
| Original100@80 and added10@90 | B6.5.17 illustration, not market facts | Makes new-origin rule observable; original date applied to added layer invents value | Source paragraph and hand sum1550 |
| Further20@95 and selected derivative prices | Authored diagnostic hypothesis | Exposes repeated reset/reversal; does not price a real derivative | Pre-authored expected cumulative amounts |
| Zero discount; same quantity/price units and common price risk | Explicit finite valuation convenience | Omitting discount/forward/credit effects can invalidate application | Required findings; other valuation models unsupported |
| Unchanged objective and eligible revised ratio/forecast | Supplied findings, not inferred from offset | Rebalancing cannot cure default or ordinary fluctuation | Missing finding unresolved; false criterion unsupported |
| Cumulative retained derivative, no settlement/release | Source-grounded finite profile | Partial discontinuation needs allocation; do not silently freeze prior reserve | Explicit operation refusal and immutable layer history |

Pre-mortem: all journals could balance while cumulative OCI is wrong; compare
the independently derived reserve, not only debits/credits. Giving a new layer
the old price can also balance; separately check origin-based and incremental
item valuations. A larger measured offset does not prove the ratio was
admissible; supplied eligibility remains an application boundary. No superiority,
actual compliance, derivative valuation, full financing coverage or runtime
conformance will be concluded.

The repaired plan passes the skeptical audit for add-only item rebalancing.
It refuses generalization to removed/instrument layers and uses a reversal case
that distinguishes the correct target from a tempting balanced wrong journal.

## Execution

Record exact source anchors and independently author six observation targets,
two additions and adverse inputs before code. Freeze inputs under
`data/accounting-master/repeated-rebalancing-20261016/`. Run exact rational CPU
checks with `CUDA_VISIBLE_DEVICES=-1`, at most three focused repair attempts
(a convenience local work bound). Preserve each attempt and result/manifest.
Integrate the source-bound derivation in a protected successor after it passes;
inspect actual rendered changes and retain all inherited content. Refresh the
next phase without treating pending review as a continuation veto.
