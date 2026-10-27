# Bank profiles and compatible connections

This map selects retained contracts; it creates no new financial semantics.
All paths are relative to the AccDSL root. The original MC21 asks for bank
records, funding/credit/liquidity/capital interfaces, accounting-prudential
reconciliation and an appropriate worked case. Those obligations are tested
separately from the stronger, still-open whole-bank implementation requirement.

| Profile and authoritative files | Supported state and operations | Permitted connection | Boundary and missing work |
| --- | --- | --- | --- |
| BankComponents/1: extended-method-exchanges-20261015/bank/semantic-contract.md, attempt-03/record-schemas.json, attempt-03/portable-exchanges.json | Conditional historical AU USD book; funded loans, original credit memory, deposits, commitments, collateral, fees, funding requests/receipts and withdrawal shortfalls; authorize/propose/commit/report | Its own context, source/date, opening-state and receipt-chain records connect exact events to journals, closing states and annual/lifetime reports | No implicit current authority, tax, arbitrary dates/rates, POCI or cross-profile migration. Capacity/request is not a cash receipt; unpaid demand stays in deposits. |
| BankComponents/2: extended-method-exchanges-20261015/bank-v2/semantic-contract.md, attempt-02/record-schemas.json, attempt-02/portable-exchanges.json | Separate historical AU transfer/option and asset-classification book; retained exposure, associated liabilities, interest, impairment, OCI and disposal | Its own full receipt chain and financial reports; shared canonical transport conventions only | /1 is explicitly refused as a foreign profile. Combining /1 and /2 requires a typed state migration or composition that preserves both profiles' accounts, exposure, rights, credit memory and reporting classifications. |
| BankAssessment/1: extended-method-exchanges-20261015/bank-assessment/semantic-contract.md, attempt-03/record-schemas.json, attempt-03/portable-exchanges.json | Separate supplied US CECL book, loan/deposit/allowance/funding/runoff history; historical conditional capital assessment, economic loss query and policy description | Its own book is checked from opening balances and dated events before capital is derived; unknown eligibility/applicability/average-assets inputs retain partial results | AU /1 or /2 cannot supply this book merely through account-name mapping. CECL allowance is supplied, not estimated by the economic loss query. A policy description neither optimizes actions nor grants payout permission. |
| BankAssessmentExactTime/1: exact-bank-profile-adoption-20261026/semantic-contract.md, record-schemas.json, successor.py, adapted_methods.py and saved examples | Same US financial definitions, explicit exact information clocks and separately versioned request identity | Retained records with unchanged meaning may be shared; converted envelopes and changed evidence clocks require the recorded reference mapping and new receipts | No general migration; historical profile/receipts remain intact. Read-only query publication never changes accounting state. At most 18 fractional digits and a known UTC offset are required. |

The first three folders above are under data/accounting-master/. Their complete
schema locks bind each contract. The exact-time folder is under the same root.
The full source and normative dependency paths are in bank-manifest.json.

## Accounting and prudential consequences of the existing US example

The original book contains all dated events, opening balances, journals and
closing balances. Loan origination credits deposits before external settlement;
funding draw and deposit runoff change actual cash. Unpaid withdrawals remain
deposits. The supplied allowance changes profit and equity once. The restricted
capital calculation uses gross loans G, allowance A, goodwill W and book equity E:
B=G, T=min(A,G/80), X=A-T, RWA=G-X, CET1=Tier1=E-W, Tier2=T and total=E-W+T.
Leverage requires the separately supplied period average M and denominator M-W.
These are the retained conditional target, not a current regulatory opinion.

Missing M leaves leverage unresolved while other outputs survive. Unknown
stock findings affect capital without inventing exposure uncertainty. Nonpositive
denominators return undefined ratios. Economic loss calculations preserve joint
cells, supplied law alternatives and unresolved zero-mass conditioning; they
cannot substitute for CECL measurement. Successful or partial assessments
publish only queries and receipts; they cannot post regulatory deductions into
the accounting book. The existing worked case already supplies a within-profile
accounting-to-capital connection; the absent AU-to-US join is not needed to
reproduce that case and must not be invented to present it.

## Remaining integration

A fresh implementation needs one chosen supported accounting basis and a
versioned composite bank-state contract before combining accounting profiles.
The plan must identify structural losses under migration, retain credit and
legal memory, distinguish actual cash from requested funding, and preserve
unresolved cash-flow classification and tax. A same-basis prudential adapter
then needs applicable rule/perimeter/eligibility/average-assets inputs and
complete state/report/query expectations. Independent implementation and domain
acceptance remain necessary. The selected general company-book credit projection
is additional evidence, not permission to substitute its treatment for this US
example. Positive recovery, POCI and wider methods remain separately tracked.
