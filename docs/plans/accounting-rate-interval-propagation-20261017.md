# B1 — propagate the certified original rate through financial state

17 October 2026. MC02/04/05/11/13/16/17/21/24–26/30/32–35;
G2/G3/G7/G10/G18. Baseline: Version 3.37 and the frozen
dated-credit-schedules-20261016 reference. Evidence:
`data/accounting-master/rate-interval-propagation-20261017/`.
Only documentary reference calculations and manuscript work are authorized.

## Skeptical audit and research intent

The named B1 residual is substantive: its existing root solver can enclose an
EIR, but the financial profiles admit only exact rational initial PV equality.
Rounding an irrational root into that profile would change the measurement
target. Requiring an exact rational root would reject ordinary cash schedules.
Repair that boundary while preserving the original accounting domain.

Question: can one certified original-rate interval enclose all dated gross,
allowance, net, interest, catch-up, impairment and cash results, including early
write-offs, without treating independent interval endpoints as a joint history?
The target remains the unique rate r* making initial expected-cash PV equal
the net acquisition amount. For POCI these are original expected credit cash
flows; performing credit keeps the separate zero-loss finding. The comparator
is the unchanged exact-rate reference and independent analytic identities.

Promotion criterion: certified root endpoint signs and width; every stage
encloses independently derived targets; monetary widths meet a declared
budget; dated cash, fee, write-off and statement origins reconcile. This
promotes only the finite documentary method, not a runtime or default.
Veto missing source identities, ambiguous calendars, invalid cash schedules,
uncertified roots, future information, absent no-recovery findings, a target
outside its interval, or excessive width. A failed candidate triggers repair.
A wrong source/target or unverifiable oracle stops the dependent comparison.
Counts, speed and interval overlap alone are explanatory, never sufficient
evidence of correctness. No credit-prediction or statistical ranking claim.

## Mathematical contract and assumption audit

Retain supplied ACT/365F annual compounding and positive, strictly future
initial receipts, with r > -1. PV is continuous and strictly decreasing, so
certified opposite endpoint signs imply exactly one root. The original-rate
interval R is computational uncertainty about that one rate; it is not a
distribution or a family of different contractual rates.

For d >= 0, (1+r)^(d/365) increases in r. Bound it with the lower-rate
factor's lower endpoint and upper-rate factor's upper endpoint. The inherited
integer-power inequalities certify each factor. Ordinary interval addition,
subtraction, multiplication and reciprocal preserve containment. Induct over
the unchanged financial recurrences from exact initial carrying and zero
allowance. Direct original-rate PV and compounded cash/write-off origins are
separate reconciliation expressions. All intervals share r*; marginal bounds
must never be combined into a synthetic endpoint journal or posted as amounts.

The initial PV interval need only contain the exact acquisition amount because
the root certificate establishes equality at r*. No rounded point rate and no
nonzero initial PV tolerance is admitted. Root/rounding error is propagated,
not discarded by forced balance. Terminal zero state is admitted only after
the same supported contractual/financial derecognition conditions as before.

| Choice and provenance | Justification | Failure mode / early diagnostic | Status |
|---|---|---|---|
| Existing ACT/365F convention | Keeps the predecessor target unchanged | Leap-day drift; actual-day regression | Supplied model convention |
| Positive initial receipts | Unique monotone EIR | Multiple roots with mixed signs; reject before solve | Restricted supported domain |
| One immutable rate interval | Preserves original EIR and chronology | Refitting at credit revision; explicit certificate/source trace | Required numerical semantics |
| Rational interval arithmetic | Auditable enclosure without floating-point claims | Dependency inflation; measured widths and tighter-root regression | Engineering choice |
| Scale 18, root width 1e-12, monetary width 1e-7 for examples | Small deterministic examples with integer-power checks | Insufficient precision; refuse and record repair | Convenience test budgets, not universal defaults |
| Decimal oracle at 80 digits plus quadratic identities | Independently computes authored targets | Decimal approximation mistaken for proof; bracket square-root by exact integer inequalities | Independent diagnostic plus analytic support |
| Inherited performing/POCI scope | Isolates numerical gap | Silent domain expansion; preserve predecessor refusals | Protected baseline |

Pre-mortem: two inconsistent endpoint books could each appear balanced.
Retain one root identity across every origin; test analytic joint identities
and disclose conservative marginal intervals. An omitted integral fee can fit
a different rate perfectly; compare against the supplied net initial cash.
Wide intervals can hide mistakes; enforce the monetary-width cap and challenge
the result with an independently wrong cash/interest/allowance expectation.

## Independent cases before implementation

Primary initial expected receipts are 50 and 60 after one and two years,
carrying 100 including integral costs. Let x=1+r*. Then
100x^2-50x-60=0 and x=(5+sqrt(265))/20. For POCI use contractual 60 and 75.
After 181 days let f=x^(181/365). Revise expected receipts to 40 and 48:
net=80f and loss=20f. Write off a supported proportional fifth of gross and
allowance, leaving gross=net=80f. At year one collect 40: gross=48/x.
Improve remaining expectation to 60: net=60/x and allowance=-12/x. Just
before terminal collection gross=48, allowance=-12, net=60. Final cash 300
and profit 0 must agree without changing the original root.

Comparators: unchanged schedule, credit revision without write-off, full early
write-off, performing prepayment to 105 at year one, negative irrational rate
(receipts 40/50, x=(2+sqrt(54))/10), zero rate, irregular actual-day dates and
all nine predecessor exact-rate cases. Full write-off profit is -100; ordinary
unchanged profit is 10; performing prepayment profit is 5. Fee omission must
produce a different root, not a silently altered target. Too-wide intervals,
invalid brackets, sign-changing cash, missing findings and stale protected
inputs must refuse without partial publication.

## Execution and completion

First preserve source/calculator hashes and authored analytic expectations.
Implement a successor reference and use the predecessor as an unchanged
regression comparator. Run standard-library CPU checks with
`python3 data/accounting-master/rate-interval-propagation-20261017/verify.py`;
no framework or GPU call, installation, benchmark or production posting.
Save numbered attempts, command/environment/commit/time, decisions and widths.
Then integrate a protected Version 3.38 successor, check all predecessor text,
build and inspect changed pages, and update all 53 obligations/six interactions.
Refresh the next named residual. Full numerical/calendar/general-bank support,
independent/domain and human acceptance remain separate obligations.

Insurance I1 dependency disposition: IFRS 17.91(a)/(b) distinguishes original
88(b)/89(b) OCI origins; B135–136 also requires a frozen former-policy runoff.
The retained text does not explicitly settle termination during that runoff.
Treat the interaction as unresolved until an inspected source or derivation
supports a precedence rule. Do not invent an accounting choice to finish a row.
This local dependency does not block B1's numerical repair.

The first diagnostic rejected the authored recovery 60 because the original
terminal contract 72 left only 57.6 after a fifth was written off. Repair the
synthetic terminal contract to 75, leaving 60; retain all expected-cash, rate
and financial targets. The failed inputs and result remain in attempt-01.
