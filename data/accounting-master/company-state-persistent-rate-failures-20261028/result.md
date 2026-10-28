# Persistent loan type and dated rate shocks

28 October2026. C04; MC08/09/10/11/14/18/26/28/33. Attempt01 passes216 checks
over13 exact solver cases,9 native programs and18 schedule/negative cases.
SIM-F011 and SIM-F018 receive individual supplemental evidence; their original
statuses and the broader financing requirements remain unchanged.

## The two-year path is the target

For the original100 loan, a fixed5% type pays(5,5) and a floating7% type
pays(7,7). An explicit persistent binary variable in the unchanged rational
solver retains exactly these paths. Independently redrawing the type adds
(5,7) and(7,5), which are wrong relative to the no-amendment target. Total
interest has bounds10 and14, but total12 is infeasible in the original family;
an interval hull would lose that distinction. Closing cash from20 is10 or6.
The zero-cell-budget result remains Unknown with its formula and unvisited
remainder, rather than being reported as infeasible.

Both original types execute through two annual coupon payments and an actual
native annual carry, for two account-name owners. Independent expectations
check all balances and memory, full journal accounts, cash flows, both annual
income/balance-sheet/equity/cash bridges, and the closing archive. The coupon
and type persist. Only the annual execution-stage field resets. Each result
also passes complete native replay with undeclared native posting disabled.

The first-year loss transfers to the retained-earnings account on carry, with
the debit sign implied by this book convention. The next opening has cash15
or13, inventory100, debt100, capital20 and retained loss5 or7. Year two
reduces cash to10 or6, recognizes only that year's expense5 or7, and reports
equity10 or6. Complementary memory remains identical.

Changing type, or both type and coupon, through an incorrectly authored carry
is refused at the next coupon by explicit contract guards. Dropping the type's
carry policy, repeating a coupon or skipping the year-end carry also refuses.
Every refusal preserves its complete successful prefix. Generic carry permits
authored reset policies; these contract-specific guards supply the persistence
requirement. This is not a general proof that arbitrary authored methods
preserve all latent contract characteristics.

## Reset timing is a separate, explicit calculation

The bounded schedule uses fixed5% or floating reference3% plus spread2%,
principal100 and actual-days/365 simple interest in2027. Floating resets are
1 January and1 July; a shock effective on the reset date is included. An
independent day-by-day sum checks the interval calculation.

A two-point reference-rate increase before the first reset gives full-year
interest7. After1 January but no later than1 July, it gives5 + 2(184/365),
because the two intervals contain181 and184 days. After1 July it gives5
for this contract year. A fixed coupon remains5. A reset only at maturity
does not affect earlier interest. The manuscript's idealized half-year
increment1 remains correct for a supplied year fraction1/2; it is not silently
substituted for this actual dated interval. Zero shock, zero delta and doubled
principal controls also agree with independent arithmetic.

Applying the same identified shock twice refuses. Shocking the spread,
unsupported day count, floating-point inputs, unordered resets or resets
after the supported maturity boundary also refuse. Applying the two-point
increase twice instead of once gives9 rather than7; applying it to the fixed
coupon gives7 rather than5. These are wrong relative to the specified targets.

Two different IDs can still encode the same economic shock: the negative
control then computes9. The input identifier is a syntactic uniqueness check,
not evidence of independent source meaning. The caller must justify shock
identity and target before admission. No general shock-lineage or floating
contract adapter is implemented. The native two-year programs use supplied
constant coupon amounts; the schedule is separately authored diagnostic code.

## Decisions and limits

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain SIM-F011 evidence | Exact two-path family and two native annual books agree | Mixed paths infeasible; bad carry/coupon guards refuse | General source and contract admission | Preserve type and operation-specific guards | General latent-state construction |
| Retain SIM-F018 evidence | Exact dated interval and independent daily sums agree | Invalid targets/IDs/conventions refuse | Alias identity and real reset calendars | Carry explicit reset and shock identity requirements into software review | Native floating-rate schedule support |
| Reject yearly redraw | Adds mixed paths and total12 | Changes original target | No amendment was supplied | Retain negative fixture | All contract changes impossible |
| Continue connected program | No continuation veto | Protected code and original populations unchanged | S09 comparative reuse and source boundaries | Reconcile retained software evidence next | DSL or release complete |

| Inference status | Assessment |
| --- | --- |
| Hard veto screen | Mixed paths, invalid state changes and wrong schedule inputs are distinguished from supported results |
| Statistically supported ranking | None; exact deterministic checks |
| Descriptive-only differences | Counts and wall time |
| Default readiness | No actual loan, day-count, probability or numerical default promoted |
| Next evidence needed | Source/contract/reset admission, semantic shock lineage, wider calendar and method comparisons |

Strongest alternative explanation: explicit fixtures may supply information
the real source never identifies. These tests establish conditional execution
and joint-path preservation, not source reconstruction. Missing amendment,
business-day or legal terms would require a new definition. The weakest
evidence is admission of real contracts and shock identities. That limits
promotion while leaving source/software comparison ready to continue.

Full formulas, solver outputs, native inputs/results, schedule inputs/results,
independent state expectations, original rows and source hashes are retained
in attempt-01. The exact environment, command, commit, CPU-only status and
wall time are recorded in run-manifest.json. No forecast experiment is run.

Post-refresh verification:24 existing native carry/program tests pass. A fresh
final-verification.json validates the40-task graph and all1,179 protected and
referenced hashes, including both452-file and545-file release packages.
Thirty-two run-source hashes also match. The supplemental review now covers
25 original rows;176 remain outside this continuation. All original statuses
and task criteria persist; S09 is the next connected work unit.
