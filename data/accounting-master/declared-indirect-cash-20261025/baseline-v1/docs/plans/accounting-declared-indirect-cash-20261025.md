# Explicit indirect operating-cash explanation for declared books

25 October 2026. S2–S5; MC02/06/08/10–13/16/19–22/24–28/30/32–35.
Question: can a verified declared-company period explain operating cash from
profit and explicitly classified journal movements without inserting a residual
or confusing reconciliation with accounting-policy validity?

## Evidence contract and skeptical audit

Baseline: CompanyBookReport/1 exposes direct cash and explicitly leaves the
indirect bridge unresolved. DeclaredWorkingCapital/1 supplies a four-account
diagnostic only. RecordedSharedBookStatements/1 has a fixed native bridge.
Retain those contracts unchanged. Use the verified DeclaredCompanyProgram/2
trace and its selected report/carry, including exact method definitions,
gross posting diagnostics and period-opening lineage.

An explicit bridge policy assigns each non-cash balance-sheet account used by
each supported method hash to a named adjustment category. Income/expense
postings contribute to profit. Categories distinguish operating working-capital
movements, noncash profit adjustments, nonoperating movements and owner
movements. Classification is a supplied premise with provenance, not inferred
from account names, cash equality or a residual. Reject missing/duplicate/extra
method bindings and missing gross-posting account classifications, including
offsetting postings whose net movement is zero. Identity/hash checking is
necessary but does not prove economic or accounting correctness.

With debit-positive journal entries j, the event profit is minus the sum of
income/expense entries. Let W and N be minus the sums of the explicitly
classified working-capital and noncash-adjustment entries. Let X be the sum
of nonoperating and owner balance-sheet entries. Balanced journals imply
cash_change = profit + W + N - X. Require the separate event reconciliation
X + investing_cash + financing_cash = 0. Then profit + W + N equals operating
cash. Preserve the per-account and gross-posting contributions; do not add
X plus nonoperating cash to the bridge as a balancing plug. A failed equality
refuses the selected classification, not the original recorded report.

The policy may legitimately assign a liability such as accrued interest to
working capital under an explicitly operating interest-cash convention. That
choice is supplied for the constructed case; it is not an accounting default.
Noncash asset purchases financed by debt need both excluded movements, whose
sum can be zero. Acquisition/FX/mixed-method decompositions that need more than
one category within one account/method remain unsupported in this first exact
contract. This limitation must remain visible rather than forcing a split.

Audit outcome: proceed with the finite deterministic contract. The main risk
is algebraic tautology being sold as semantic proof. Separate the nonoperating
reconciliation, expose classifications and keep admission/completeness flags
false. A deliberately wrong category, an omitted zero-net gross movement and
a rehashed altered result must each fail the relevant check. A syntactically
valid alternate policy that remains algebraically consistent is conditional
evidence only; no unique accounting interpretation is inferred.

## Validation and continuation

Pass: independent expected profit/adjustment/operating-cash arithmetic for both
charts, a financing-plus-operating case, a noncash asset/debt case and selected
prefix/carry periods; exact retained trace lineage; read-only replay. Vetoes:
unverified result, missing event/method/posting, incorrect period opening,
unbalanced exclusion check, source-lock change or semantic overclaim. Counts
and compilation are explanatory diagnostics. No stochastic ranking or GPU use.

Implement scripts/declared_indirect_cash_v1.py and focused tests. Preserve
evidence, schema/policy requests, results, negative cases and a run manifest in
data/accounting-master/declared-indirect-cash-20261025/. After checks, integrate
the algebra and limitation into a manuscript successor and refresh controls.
Broader reporting, actual populations, group/sector methods, source research
and independent/domain/human review remain; E3 stays deferred.
