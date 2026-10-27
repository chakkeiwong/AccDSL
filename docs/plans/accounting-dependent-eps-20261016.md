# F1 successor — consequential earnings and contingent exercise

16 October2026. MC02/04/05/11/16/17/19/24–28/30/32–35;
G2/G4/G7/G12/G13/G17/G18. Documentary methods and exact reference calculations
only. Evidence: `data/accounting-master/dependent-eps-20261016/`.
Baseline: Version3.29 and the preserved OrderedEPS/1/CappedParticipationEPS/1
contracts. Runtime/controller, installations and empirical campaigns remain held.

## Skeptical audit and research intent

The question is how to preserve consequential earnings and source-required
exercise dependencies without passing nonadditive inputs to an additive EPS
selector. IAS33.35 explicitly names employee profit-sharing consequences.
IAS33.57 requires a separate contingency test and forbids assumed conversion of
contingently issuable potential instruments unless similar noncontingent
outstanding instruments are also assumed exercised/converted.

Two distinct methods are necessary. The first calculates the complete earnings
of every requested hypothetical conversion world, with nonlinear remuneration.
It does not claim a general nonadditive diluted-EPS selection rule. The second
implements paragraph57 for a single pair of zero-earnings-effect options, whose
eligibility and treasury-share quantities are separately established. Similarity
is an explicit supplied assessment, never inferred from labels or strike prices.

A raw subset minimum is not automatically a permissible diluted EPS. Applying
such a minimizer to arbitrary dependency graphs would be an unsupported change
of target. The plan therefore refuses a final dilution selection in the
nonadditive profile and uses the actual paragraph57 dependency for the option
profile. This is a deliberate source boundary, not closure of arbitrary
contractual dependence. Missing similarity/terms blocks that application; the
remaining F2 and sector methods remain ready.

## Evidence contract and independent targets

Consequence model: supplied pretax profit P before a nondiscretionary bonus,
bonus q*max(P−H,0), and complete proportional tax t on the resulting amount.
Assumed debt conversions add their saved pretax interest I to P. These are
synthetic remuneration/tax terms, not an IAS19 recognition or fiscal-law claim.
Positive profits use an explicit no-other-tax-effects finding; loss cases use
t=0 so no tax asset is silently recognized. Ordinary rights are nonparticipating,
continuing and total earnings coincide, and all series cover the whole period.

At P90,H100,q1/2,t1/5,n100, basic bonus0/tax18/earnings72/EPS18/25.
Two debts A and B each save20 interest and add20 shares. Each single world has
bonus5/tax21/earnings84/shares120/EPS7/10. Together: bonus15/tax23/earnings92,
shares140/EPS23/35. Summing the standalone earnings effects would wrongly give
96 and EPS24/35. Preserve the difference4 and both individual marginal effects
12 then8. Also check q=0 (additive limit), P100 (threshold), P80 (two-conversion
kink), zero/loss with no tax, and unequal savings/shares (B40/40): B alone92/140,
both100/160. These are conditional world EPS values, not asserted final diluted
EPS under an unproved ordering theorem.

Contingent option model: report-year profit100 and ordinary count100. A similar
outstanding option has20 instruments, strike6, average market10, hence8 free
shares. A contingent option has20 instruments, strike5, average market10,
hence10 free shares. An admitted similarity finding is required despite the
different strike; the method does not decide that issue. The contingent
agreement began at the reporting-period start, its contingency period ends
later, and a supplied nonfinancial store condition is tested under52/56/57 at
report end. Observed5/required5 qualifies, but future opening forecasts do not.
Basic EPS1, outstanding-option EPS25/27, both EPS50/59. If the condition fails,
return25/27. If the similar option is out of the money (strike12), its exercise
is not assumed; paragraph57 then excludes the contingent option even though
its isolated EPS would be10/11. This case remains conditional on the admitted
similarity finding, not an assertion that unlike terms are always similar.
Loss and zero profit exclude dilution. Equal strike/price gives no free shares.

Primary pass criteria: independent complete world amounts, exact bonus/tax/share
conservation, demonstrated nonadditivity, correct contingency and similarity
dependency, unchanged inputs and explicit absence of a nonadditive final
selection. Invalid rights, missing complete tax/remuneration effects,
lookahead, false/unknown similarity, changed sources and partial refusal output
veto affected results. Check/build counts are explanatory. No actual issuer,
operative-law, arbitrary graph optimizer or production-engine claim follows.

## Default and assumption audit

| Choice and provenance | Justification | Failure mode and early check | Status |
|---|---|---|---|
| Threshold bonus, synthetic contract | Makes IAS33.35's consequential effect visible | Single-world addbacks hide joint expense; derive all four worlds first | Hypothesis/example |
| Flat tax, supplied complete tax effects | Isolates the EPS consequence | Pretax addback or implicit loss DTA; tax reconciliation and zero-tax loss cases | Conditional input |
| Equal continuing/total, no participation | Separates this question from3.29 | Wrong control numerator; refuse false finding | Explicit finite scope |
| Similarity, supplied assessment | Applies paragraph57 without inventing a similarity test | Same label wrongly treated as authority; unknown/false finding refuses | Unproved actual fact |
| Nonfinancial period-end count | Directly supported by52/56 | Forecast count leaks future information; date and failed-condition cases | Source-grounded finite condition |
| Exact fractions, existing CPU Python | No root or stochastic uncertainty required | Encoding/domain errors; strict input checks | Engineering choice |

The pre-mortem is a numerically correct but legally inadmissible subset minimum,
or a missing profit-sharing/tax consequence. World-only output and the explicit
paragraph57 gate address these before drafting. The inspected source audit
passes for these two methods. General nonadditive ordering and arbitrary linked
conversion remain source/derivation obligations, not new default behavior.

## Execution and continuation

Freeze primary source bytes, hand-authored expectations and this plan before
implementation. Use numbered attempts with manifests, exact adverse cases and
source challenges. Command:
`CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/dependent-eps-20261016/verify.py`.
Write contracts/results with a decision table, then integrate Version3.30 with
129 protected3.29 sources. Teach the expense interaction first, then why a
period-end contingency and a similar-option decision both matter. Build and
inspect the new pages. Human voice/independent acceptance remain pending.

Refresh F1's exact residual disposition and the F2 instrument-only/heterogeneous
hedge plan before continuing F2. Do not expand this finite unit into arbitrary
contract simulations or stop unrelated internal work on a source-dependent EPS
selection claim. No continuation veto has fired.
