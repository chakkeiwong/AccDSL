# R03/R04 — reserve-risk horizons and risk adjustments

20 October 2026. P15/P17/P19; MC10–12/18/22/26/29/30/32–35; G6–G8.
Output: `data/accounting-master/r04-reserve-risk-20261020/`.

Question: what extra targets, information sets, valuation assumptions and risk
preferences are needed to turn the existing reserve-distribution design into
a specified risk-adjustment method? The exact comparator is candidate 3.44's
insurance-methods discussion and its existing reserving/bootstrap supplements.
The paper is England, Verrall and Wüthrich (2019), *On the Lifetime and One-Year
Views of Reserve Risk, with Application to IFRS 17 and Solvency II Risk Margins*,
DOI 10.1016/j.insmatheco.2018.12.002, retained institutional accepted manuscript
21270. Its hash is
`d195f617ffacdb72e6f5f445d54b829cb1f47ad6dc4d0fbe55cc67b06cc70268`.
Exact equality to the published article is unverified.

Prior-scope audit: the 14 October reserving-bootstrap inspection covered §2.2,
§3/3.2, equations 5–7, §4 Tables 1–4 and Appendix 1. It explicitly excluded
§§5–6 and Appendices 2–3. Bounded searches of later inspection/result/review
notes found no later completion of that scope. The 2023/2024 consistency inquiry
is a separate source and remains protected. Reuse these predecessor findings;
do not repeat bootstrap comparisons or adopt the accepted manuscript's dated
regulatory statements as current authority.

## Evidence contract and intent

Read §§5–7 and Appendices 2–3 completely, with the earlier mathematical
definitions, comparison tables and references needed to understand them.
Inspect actual rendered equations/figures when extraction is ambiguous.
Primary pass criterion: source-specific target definitions and derivations
that distinguish remaining payments, future reserve revisions, projected
capital and entity risk adjustment, including the conditions of any identity,
bound or approximation. Check source claims against the exact current prose.
If a consequential missing method is established, specify it in a separate
method note; integrate only through a separately audited manuscript unit.

The mechanism under review is the relation between future conditional
re-estimation and remaining cash flows, followed by a declared risk measure.
Expected failure: silently treating unconditional future variability as
conditional risk at a future information date, or treating a standard deviation
or illustrative capital profile as a calibrated accounting measurement.
Wrong edition, missing assumptions, incorrect algebra or unsupported law
veto the affected claim. A manuscript contradiction triggers repair; an
uninspected dependency becomes a named source task. Only corrupt inputs,
conflicting edits or a genuine permission/direction dependency veto continuation.
Counts, matching bytes, successful rendering and published example values are
explanatory/integrity diagnostics, never evidence of real-company calibration.

No source formula establishes a current regulatory rate, acceptable accounting
choice for a real entity, calibrated risk preference, empirical ranking,
bootstrap consistency or production implementation. No E3 question is selected.
Preserve those distinctions in `inspection.md`, the six additive literature
ledgers, result/review, run manifest and an R08 supplement.

## Defaults, assumptions and early diagnostics

| Choice and provenance | Role and justification | Failure mode | Earliest check |
|---|---|---|---|
| Retained accepted manuscript from record 21270 | Inspected source edition, not published-equivalence assumption | Import a changed formula or dated rule | Compare front matter/hash and retained metadata; retain version/date limits |
| Existing 3.44 reserve examples | Actual design baseline | Redo completed work or compare to a weaker invented baseline | Read exact current included sections and predecessor inspection |
| Paper's filtration, payment timing and loss sign | Mathematical hypotheses | Confuse cash-flow and re-estimation horizons | Reconstruct definitions before interpreting §§5–6/Appendix 3 |
| Paper's discount rates, confidence levels and cost of capital | Historical example choices only | Promote convenient percentages to policy | Identify every example choice and its scope |
| Exact finite arithmetic, if needed | Authored explanatory diagnostic only | Pass a toy check while implying general validity | Write the specific law and independent expected result before implementation |
| CPU standard-library checks and existing PDF tools | Documentary convenience | Execute acquired code or hide numerical uncertainty | No scientific packages/GPU; retain source and rendering hashes |

Pre-mortem: an elegant identity may hold for true conditional expectations but
fail for fitted plug-in reserves; a prudent variance bound may fail to bound
a quantile or imply a required risk adjustment. Source reading must expose
that distinction before a local calculation is admitted. If an exact example
is useful, write an additive derivation plan after the source reading and
before its calculation; do not invent stochastic experiments.

Skeptical pre-run audit passes for this source/method inquiry. The unresolved
sections are consequential to MC22, the current baseline is identified,
source/version limits and expected errors are explicit, and no proxy metric
or inherited risk preference can promote a default. Local source reading
continues despite the unrelated Tamer barrier and pending E3 direction.

## Execution and preservation

Use `CUDA_VISIBLE_DEVICES=-1
/home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B` and existing PDF tools.
Read retained text/PDF and metadata; no source acquisition is initially needed.
Correction and forward-search observations keep their actual 14 October date;
no new clearance or search is implied. An identified consequential source lead
requires a successor plan. No package installation or upstream code execution.

Prepare once, construct once after reading, check once, record once, then
no-flag read-only replay. Protect all predecessor records, original paper,
exact candidate and repository state; only four live controls advance.
Keep 3.44/396/`not_ready`, 53 obligations, six interactions, 46 operations and
zero whole-row closures. Controller/runtime, empirical campaigns, commits,
outreach, publication and fees remain held. Missing human acceptance does not
block provisional internal source and method preparation.
