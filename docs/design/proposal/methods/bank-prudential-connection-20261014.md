# One bank book and a separate prudential assessment

14 October2026. Proposed documentary extension of interfaces-contract-v1 I4.
This specifies a read-only RegulatoryAssessment; it does not add a runtime
endpoint or extend the implemented initial profile. MC02/05/13–17/19–21/24–28/30/32–35.

## Authority, context and inputs

The rule package is a historical 1 January2026 snapshot of12 CFR Part3 for
a synthetic ordinary US national bank. The bank has no subsidiaries, minority
interests, advanced-approaches or CategoryIII treatment, market-risk book,
community-bank leverage-ratio election, special supervisory adjustment, CECL
transition adjustment, AOCI, own-capital holdings, financial-institution capital
investments, deferred taxes, other intangibles, pension asset or securitization.
These are supplied restrictions on the example, not findings about a bank.
The conditional reporting window is1 January–31 March2026, assessed at its
end with the1 January rules deliberately frozen. This is a scenario-law
assumption, not verification of actual31 March reporting applicability.
All stock eligibility conditions in§3.20(b)(1)(i)–(xiii) are explicitly supplied
as satisfied. Unknown conditions must remain unknown in an actual case.

Amounts are authored USD millions. Settlement cash is a direct Federal
Reserve balance, not a generic commercial-bank deposit or cash in collection.
Loans are ordinary unsecured, non-PCD, performing corporate exposures at
amortized cost; no loan is90days past due, on nonaccrual, HVCRE, a derivative,
an equity exposure, a security, a QCCP exposure or credit-mitigated.
The allowances are supplied US-GAAP/CECL accounting measurements, not local
estimates or a transfer of the earlier AASB9 staging calculation. No method
for estimating those allowances is promoted. All the allowance qualifies as
AACL; no allocated transfer risk reserve or off-balance credit exposure exists.
Borrowing under the bank's own funding facility is a liability, not its
extension of credit to a customer. The facility's availability is supplied.

The retained FDIC FFIEC051 December2024 instruction files operationally
cross-check the cap ordering: PartI item42, printed RC-R-27–28 (physical39–40),
and PartII items26,28–31, printed RC-R-109–110 (physical89–90). The cap pages
carry March2024 revision footers, while the final denominator page carries
December2024. These older instructions do not replace the legal snapshot or
establish a complete amendment chain. The inspected ordering agrees with
§§3.2,3.20(d)(3),3.22(a)(1)/(g),3.31 and3.32 for this restricted case.

## Calculation and sequence

Let G be the gross ordinary loan balance, A the eligible allowance, W the
goodwill without an associated DTL, E accounting equity and B the allowance
cap base. Section3.2's carrying-value definition leaves G unreduced by A for
this exposure. Sections3.31 and3.32(a)(1)(i)(A)/(f)(1) give zero weight to the
Federal Reserve balance and100% to these corporate loans. Goodwill is deducted
under§3.22(a)(1) and excluded under§3.22(g). Thus B=G in this case.

The general cap base is not always the final standardized denominator or
every bank's undeducted exposure total. The instructions exclude§22(a)
deductions such as goodwill from the cap base but include specified§22(c)–(f)
deductions. None of those other deductions or market-risk amounts exists here.
Compute eligible Tier2 allowance T=min(A,B/80), excess allowance X=A−T and
standardized RWA D=B−X, in that order. Do not solve T=min(A,D/80); the cap base
precedes subtraction of excess allowance. PartI item42 and PartII items26,29,31
make the ordering explicit.

All book equity here consists of eligible paid-in common stock and retained
earnings. CET1=E−W; additional Tier1=0; Tier1=CET1; Tier2=T; total=CET1+T.
There is no second subtraction of A from CET1: the expense already reduced
retained earnings. Ratios under§3.10(b)(1)–(3) use D. The ordinary leverage
ratio instead uses Tier1/(M−W), where M is a separately supplied average total
consolidated assets amount satisfying§3.10(b)(4), with matching bank, period
and currency. A period-end balance is not M. No M means leverage unresolved,
while eligible risk-based quantities remain available with their dependencies.

Opening cash30, loans100, goodwill2, allowance0.8, deposits110, common stock20
and retained earnings1.2 balance: net assets131.2=liabilities110+equity21.2.
Originate20 by crediting the borrower deposit; transfer15 externally; receive
earned interest6 in settlement cash; credit deposit interest2; increase the
supplied allowance to2.4 through expense1.6. The final pre-runoff book has
interest income6, deposit-interest expense2 and credit-loss expense1.6; a
separate closing journal transfers their net profit2.4 to retained earnings.
No regulatory adjustment is included in that journal. The resulting book has
cash21, loans120, goodwill2, allowance2.4, deposits117 and equity23.6.
CET1=21.6, cap1.5, excess0.9, standardized RWA119.1 and total capital23.1.
Opening A0.8 was below cap1.25; final A2.4 is above cap1.5.

Settle a25 deposit runoff by drawing4 under the supplied10 facility limit.
Closing cash0, deposits92 and borrowing4 balance against net assets119.6
and equity23.6. Capital and RWA do not change because the cash has zero
weight and no new income/expense is supplied. If40 is demanded instead, draw10
and pay31; deposits still include9 unpaid within balance86. That obligation
is flagged as unpaid/default, not removed or replaced by a capital plug.
These are alternative histories, not events to be combined.

For a separate complete averaging-input example, supply M145 for this bank's
declared reporting window: denominator143 and leverage21.6/143. It is an
authored input requiring separate average-assets evidence, not computed from
the event path. The closing-assets substitution would give a different answer
and is rejected as an average-input mismatch. No minimum-ratio or payout
permission verdict is emitted by these finite cases.

## Proposed records and observable failures

RegulatoryAssessmentRequest contains assessment_id, bank_id, book_id,
perimeter_id, accounting_state_ref, information_view, assessment_date,
reporting_window, currency/unit/scale, rule_snapshot_refs, applicability_ref,
capital_eligibility_ref, exposure_classification_refs, allowance_admission_ref,
deduction_ref, optional average_assets_ref and method_version. The referenced
accounting state retains signed accounts and the exact event/measurement
history. Applicability/eligibility records have true/false/unknown values with
provenance; missing is never coerced to false or zero.

RegulatoryAssessment carries input identities, source/dependency fingerprints,
book equity, deductions, CET1/Tier1/Tier2/total, gross exposure, cap base, cap,
admitted/excess allowance, standardized RWA, separately named ratio numerators
and denominators, per-output status, unresolved inputs and diagnostics.
Finite values use exact reduced rationals. Undefined ratios have no value
and a nonpositive-denominator diagnostic. Zero remains a valid amount.
This assessment produces no accounting entry or changed book head.

Unknown stock eligibility makes dependent capital amounts/ratios unresolved;
known exposure subtotals remain diagnostic and are not a completed assessment.
A book/perimeter or date/rule mismatch rejects input. Unsupported PCD,
nonaccrual, collateral or capital-instrument treatment requires a different
admitted method; it is not silently assigned the example's100% weight.
Absent M leaves only leverage unresolved. A closing-asset amount labelled as
an average is rejected rather than guessed. Numerically balanced adverse
proposals using net loans, missing excess subtraction, goodwill in RWA, a
circular cap or double allowance deduction fail reconciliation.

A changed accounting measurement, capital instrument, tax link, exposure
classification, reporting window, average or rule snapshot invalidates only
the outputs depending on it and requires a new assessment. Historical results
remain bound to their original references. Reassessment does not rewrite
old journals or retroactively authorize a distribution. Generic API envelopes,
storage identity/replay and accounting commit contracts remain unchanged.

The exact examples specify a restricted connected calculation. They do not
establish actual-bank GAAP or capital compliance, a calibrated credit model,
complete current law, supervisory permission, liquidity adequacy, dividend
capacity, stress performance or a runtime prudential engine.
