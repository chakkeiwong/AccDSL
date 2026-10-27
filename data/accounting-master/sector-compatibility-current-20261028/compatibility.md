# Sector interfaces and supported connections — 28 October 2026

This annex adds five already delivered profiles to the18-profile current index.
It is a versioned navigation reference for selected5.55-R1, which remains
not_ready. Source contracts and implementation identities are locked by the
fresh verification record. Historical packets retain their original semantics.

## InsurancePAADatedBook/1

Authority: insurance-paa-dated-book-20261027/contract.md, bridge.py, authored.py
and authored-expectations.json under data/accounting-master/.
Call bridge.propose(body), with exactly profile, payload and payload_sha256.
The typed payload binds the finite case/chart/complement, entity/currency,
calendar, distinct issued/held group records, amounts, explicit findings,
cash policy, exact source edition and synthetic assumptions.

The wrapper compiles DeclaredCompanyProgram/2 and delegates financial effects
to its unchanged CompanyBook/1 transition methods. CompanyBookReport/1 owns
the complete interim report. Group identity, role, common owner, cohort,
held-to-issued link, dates and each event's prior balances/memory are retained.
The fixed coverage year is2024; July2 is the supplied183/366-day service boundary.
The report does not invent the second half-year or close the year.

proposed_conditional preserves compiled program, complete execution, groups,
calendar qualification and unresolved conditions. Missing findings return
unresolved; contradicted/out-of-domain assumptions return unsupported; malformed
or stale identities return invalid; native refusal retains the stopped trace.
All source/accounting/posting/group/chronology admission flags remain false.

Supported edge: PAA → declared company program → full interim report, on the
same explicit synthetic basis. A complete report does not make actual group
facts known. Carrying into a new year, generalizing amounts/service curves,
merging group populations or adding an undated recovery ledger needs a new
explicit contract, source premises and complete expected reports.

## BankComponents/1 and BankComponents/2

Authorities: extended-method-exchanges-20261015/bank and bank-v2, respectively,
under data/accounting-master/. Their semantic-contract.md files, exact
attempt-03/attempt-02 record schemas and full portable-exchanges.json packets
define typed records and operations. Auditor.dispatch(self,rqref,w) in each
verify_exchanges.py checks the corresponding documentary requests/worlds; it
is not a new production endpoint. Operations are accounting.authorize@1,
accounting.propose@1, accounting.commit@1 and report.build@1.

/1 binds the historical conditional AU lending/deposit/funding book; /2 binds
the separate AU transfer/option/classification book. Each owns its exact
context, source/date, opening state, rights/credit memory and receipt chain.
Requested funding is not received cash; unpaid withdrawals remain deposits.
The financial verifiers derive all book effects and reports from their own
opening/event records. Receipt publication and recovery are documentary
state operations, not evidence of physical durability. Native refusal codes
and unchanged-world requirements remain authoritative.

The two profiles share transport conventions, not a composite financial state.
/2 explicitly refuses a foreign /1 profile. A same-AU join still needs an
account/asset/rights/credit-memory migration, exclusive ownership of financial
effects, preserved tax and cash-classification unknowns, and complete
combined before/after statements. Equal labels alone cannot establish it.

## BankAssessment/1

Authority: extended-method-exchanges-20261015/bank-assessment/semantic-contract.md
and attempt-03 record schema/complete packet. Auditor.request(self,rq,sub,w)
and response(self,ex) in verify_exchanges.py check the exact request/submission,
state, evidence view, receipt and declared read effect. Operations are
bank.regulatory.assess@1, bank.loss.query@1 and bank.policy.describe@1.

The supplied US CECL book and historical prudential rule inputs form one
within-profile accounting-to-capital example. Explicit context/perimeter,
dated rule/applicability, stock eligibility, exposure, allowance/deduction and
period-average-assets records remain required. The allowance is supplied; an
economic-loss query does not estimate CECL. Missing average assets leaves
leverage unresolved while the other capital outputs survive. Capital deductions
are query quantities and do not post into the accounting book. A policy
description does not authorize distributions or optimize decisions.

Supported edge: this US book → its own conditional prudential assessment.
The existing AU books do not feed it by renaming accounts. A compatible new
adapter requires one declared accounting basis, measurement/eligibility
premises, exact perimeter/period and complete expected financial/query outputs.
The retained arithmetic is not a current regulatory opinion.

## BankAssessmentExactTime/1

Authority: exact-bank-profile-adoption-20261026/semantic-contract.md,
record-schemas.json, successor.py and adapted_methods.py. Its Auditor wraps
the pinned financial checker and enforces profile_contract(self),
request(self,rq,sub,w), response(self,exchange) and shape(self,record,digest=None).

This separately versioned request identity supports exact information clocks
with a known UTC offset and at most18 fractional digits. Unchanged financial
records may be shared only under the retained reference mapping. Changed
envelopes/clocks require new receipts; old receipts remain old records.
It is a time/identity successor, not a second financial implementation,
general migration or changed accounting treatment. Publication remains read-only.

## Evidence and remaining work

The fresh check binds all five authorities and selected companion identities.
It reproduces the seven complete PAA requests/results and21 controls, compares
all financial report fields to independent authored expectations, and rederives
all amounts/ratios in the five retained US capital cases using Fraction.
The earlier complete bank replay remains separate, hash-bound evidence; this
annex does not relabel it as a new run.

Next same-basis composition work must specify identity, account/memory ownership,
dates/views, permitted effects, partial/refusal propagation, report/carry
semantics and full positive/adverse outputs before implementation. General
bank/insurance/group composition, actual applicability, source completeness and
independent acceptance remain open.
