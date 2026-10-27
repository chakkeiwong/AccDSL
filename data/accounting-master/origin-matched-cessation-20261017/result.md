# Origin-matched cessation: deterministic result

17 October 2026. MC02/05/16/17/24/26/29/30/32–35; G2/G3/G7/G8/G10.
Original operation: P17-05.05, Benchmark/hedges. Readiness remains `not_ready`.
Plan: `docs/plans/accounting-origin-matched-cessation-20261017.md`.

## Decision and computed target

The finite candidate passes its declared deterministic criteria. A documented
exact match from each designation origin identifies a stopped portion's own
effective-gain history while preserving the continuing relationship's cumulative
lower-of measurement. This is a local deduction under the supplied assumptions,
not an express general IFRS allocation rule or evidence of unique attribution.

The claimed target is the reserve, profit, gross cash and inventory history of
one named partial cessation in an exactly matched multi-origin purchase hedge.
The reference computes that finite target with exact rational arithmetic and
compares it with 21 independently authored complete histories frozen before the
reference was written. At each measurement, all active continuing origins have
the same weak gain sign and no historical ineffectiveness. Original designation
dates and prices survive cessation. All actual instruments remain owned.

The relationship totals satisfy H=-D before cessation. Its signed lower-of
therefore equals D; independently identified effective origin gains reconcile
to that amount. After stopping quantity z from origin k at price S_d, the frozen
gross gain is F_0=z(S_d-f_k), continuing reserve is
R_c=sum_j q'_j(S-f_j), and the stopped instrument's later gain is U=z(S-S_d).
For signed releases L, remaining stopped reserve F=F_0-L and profit P=U+L.
Thus the actual derivatives obey D=R_c+F+P. These equalities are derived in
`source-reading.md` and checked throughout the admitted histories. Independent
per-origin lower-of amounts do not replace the relationship calculation.

## Discriminating outcomes

Two origins each have quantity10, with original prices8 and9. At price11 their
gains are30 and20. Stopping5 from the first carries15; stopping5 from the second
carries10. Scaling total reserve50 by5/20 gives12.5 and is wrong for both named
histories. This rejects the aggregate-fraction candidate, not further research
on heterogeneous hedges.

At terminal price12, actual instruments settle for70 in every row below.
Opening cash/capital is300. Amounts are exact, in the example's currency units.
Continuing and attached reserve columns describe balances before basis transfer.

| Stopped history | Continuing reserve | Attached reserve | Profit | Supplier cash paid | Inventory | Final cash |
|---|---:|---:|---:|---:|---:|---:|---:|
| First origin; canceled |50|50|20|180|130|190|
| Second origin; canceled |55|55|15|180|125|190|
| First origin; still expected |50|65|5|240|175|130|
| Second origin; still expected |55|65|5|240|175|130|

The negative-reserve history stops the first origin at7, freezing a loss5.
Releasing an unrecoverable loss2 leaves loss3 attached. At terminal price6,
continuing reserve is-40, inventory is163, cash130 and profit-7. Cancellation
after that partial loss release releases only the remaining3: total signed
release is-5, never-7. A later price reversal does not reinstate the released2.
The final report separately records gross frozen gain, signed releases to
profit and basis transfer; its final live stopped reserve is zero.

## Checks, artifact and limits

The existing `attempt-01/checks.json` records **1,846 checks, zero failures**,
including80 adverse requests and18 changed/missing-source challenges. Checks
cover chronological balanced journals, every supplied balance snapshot, named
origin retention, actual asset/liability marks, relationship lower-of agreement,
retained/canceled purchases, partial/full loss release, both price-sign reversals,
zero frozen gain, scaling, three origins, a homogeneous comparator and the exact
supplier-funding boundary. Refusals return no partial report or journals.
The addendum's negative-inventory-basis refusal was fixed before the first run;
it conservatively excludes an unestablished extension rather than declaring a
general rule against negative basis.

The exact command, commit, input/code hashes, interpreter, wall time and output
locations are preserved in `attempt-01/manifest.json`. The actual interpreter
is `/home/chakwong/miniconda3/envs/tfgpu/bin/python3`; despite the manifest's
loose label “system Python”, this run used only Python's standard library in
that existing environment. `CUDA_VISIBLE_DEVICES=-1` intentionally hid GPUs.
No training, stochastic simulation, installation or product execution occurred.
The completed attempt is preserved and has not been rerun.

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | What is not concluded |
|---|---|---|---|---|---|
| Admit this finite documentary method | Exact authored histories and direct cash/equity/basis identities agree | No supported mathematical, journal, funding, source-integrity or atomic-refusal failure in admitted cases | Actual qualification and complete origin matching must be supplied | Integrate into a protected successor and inspect affected pages | General heterogeneous allocation, actual eligibility or production readiness |
| Reject nominal-fraction allocation here |15 and10 differ from12.5 for the named histories | Identity counterexample is decisive for that proposed formula | Other fully documented histories may require different analysis | Retain origin identity and original measurement terms | Rejection of the research direction |
| Keep broader cases open | No primary evidence for unmatched histories | Scope refusals prevent silent widening | Shared ineffectiveness, opposed gains, acquired nonzero origins and repeated stops | Follow a specific source or derivation lead; continue independent ready work | That an omitted case is impossible or compliant |

This is deterministic evidence; statistical ranking and stochastic uncertainty
intervals are not applicable. Check counts and page counts are explanatory only.
Source scope is the inspected historical EU2023/1803 IFRS9 text, especially
6.5.11–12 and B6.5.16–28. B6.6.14 is presentation guidance and supplies no
stopped-reserve attribution formula. Current-law, tax, market valuation, general
group/layer allocation and full-company conclusions are unsupported here.

## Red-team interpretation and continuation

The strongest alternative explanation is that perfect matching makes the
arithmetic easy while avoiding the hard shared-ineffectiveness problem. That
limitation is correct and explicit: the evidence closes this named exact-match
transition only. Supplied marks and eligibility are not independently established
company facts. A source contradiction, a failure of the direct identity under
the stated domain, or evidence that matching was invented retrospectively would
overturn admission. The weakest evidence is the accounting applicability of
supplied hypothetical qualification findings, not the checked rational sums.

No harness, source artifact, mathematical assumption or required diagnostic
failed within the declared domain. No continuation veto fired. Integrate the
finite derivation, preserve all predecessor arguments and obligations, then
reassess the residual queue and continue substantive internal preparation.
