# Carrying debt and promised repayment remain distinct

28 October2026. C04/T03; MC08/09/12/13/19/24/28/33. Attempt01 passes109
exact checks across21 solver cases and6 native report cases. Original SIM-F026
receives supplemental evidence; its inherited status remains unchanged.

Within the explicitly supplied finite domain, carrying amount100 is compatible
with face100/discount0 and face110/discount10. The unchanged rational solver
retains exactly those joint pairs. Separately supplied discount10 selects110;
discount0 selects100. Book95 conflicts with this declared domain, which does
not establish that book95 is impossible for an actual company. Zero solver
budget yields Unknown and preserves the formula and unexplored remainder.

Under the supplied one-payment, no-default gross return21/20, promise110 has
current value2200/21. That differs from both carrying amount100 and promised110.
Using book100 as the promise instead yields2000/21: the pricing arithmetic is
correct for the substituted contract, but its answer is wrong for promise110
by200/21. Changing the return to110/100 to force value back to book100 would
change the supplied pricing law rather than repair the reconstruction.

For two account maps, the native reporting engine preserves the complete
opening book and complementary memory for each supplied promise. Both histories
report assets120, liabilities100, equity20 and profit0, with cash20 and no cash
movement. Contract memory retains face100 or110 even though the reported
amounts coincide. Reports alone cannot select the promise. A deliberately
substituted face100 still balances and reports; the independent promised-amount
criterion rejects it when the target history stipulates110.

These are native reports, not native pricing, amortization or repayment
execution. The finite bridge and pricing calculation are separately authored
diagnostics. The bridge assumes carrying=face-discount with no fees, accrued
interest, currency changes or other measurement adjustments. Its two candidates
are hypotheses, not an exhaustive real-company reconstruction.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain scoped SIM-F026 evidence | Exact joint family, values and complete native report states agree | Declared-domain conflict and budget Unknown remain distinct | Real source-to-instrument and measurement bridge | Inspect supported issuer disclosures and preserve unresolved contractual mappings | Whole-company debt reconstruction |
| Reject carrying-as-promise shortcut | It changes110 to100 and value by200/21 | Independent contract criterion rejects despite balanced reporting | Actual promise evidence | Require explicit contract evidence and adjustment components | Book values never equal contractual principal |
| Continue program | No continuation veto | Protected identities require fresh verification | Remaining source/construction/review work | Continue T03 and remaining original cases | Release ready or forecasting authorized |

| Inference status | Assessment |
| --- | --- |
| Hard veto screen | Wrong reconstructed promise, inconsistent finite bridge and exhausted budget receive distinct outcomes |
| Statistically supported ranking | None; deterministic exact checks |
| Descriptive-only differences | Check counts and elapsed time |
| Default readiness | No measurement, discount rate, domain or source assumption promoted |
| Next evidence needed | Sourced instrument terms and measurement adjustments, plus lifecycle execution where required |

Post-run red team: the strongest alternative explanation is omitted measurement
terms or instruments outside the two-point domain. The smallest discriminating
next step is to inspect an actual issuer debt disclosure and identify which
principal, carrying and adjustment quantities are separately supported. A
source mapping that remains unresolved limits actual-company promotion; it
does not invalidate the conditional counterexample or stop independent work.

Attempt01 preserves full solver formulas/results, native inputs/reports,
independent enumeration, the original row and manuscript anchor, and command,
commit, Python/Z3 environment, source hashes and timing. CPU-only exact
arithmetic uses no random seeds; no actual-company admission is asserted.

Post-refresh checks:9 program tests pass and all1,179 protected/referenced
hashes match, including997 frozen release files.29 run-source hashes matched
before refresh. Supplemental coverage is28 original rows;173 outside this pass.
The existing Apple Note9 source and measurement work already distinguishes
principal97,341 from carrying96,662. Do not repeat that completed aggregate
mapping as new progress: the next source task is a supported instrument/exhibit
connection and explicit residual population, timing and adjustment gaps.
