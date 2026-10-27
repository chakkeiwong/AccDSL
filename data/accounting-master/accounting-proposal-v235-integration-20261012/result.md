# Version 2.35: parent income and parent funding

12 October 2026. E01/P18; MC01/02/03/05/08/15/16/28/30/32–35 and
G4/G5/G7/G11/G13. The separate 174-page candidate adds a 2025 parent-only
income/cash example after the bank chapter's transfer restriction. **All 154
integration checks pass.** All inherited prose outside the bounded insertion
and title, 48 displays and 75 bibliography entries are preserved. A
layout-only break keeps the next instrument discussion together.

PDF: docs/design/proposal/manuscript-parent-cash-20261012/accounting-product-proposal.pdf
SHA256: 23d1d9da1b599bf5caee7aca7ce6559c0afa1d0ae077504800d97acd8652b7e7

The source unit passes 74 documentary/arithmetic and 60 closeout checks.
The new prose makes the 2025 cash-flow bridge explicit: 57,048 net income
less 71,163 subsidiary/affiliate net income yields a 14,115 parent-company
net loss in the cash-flow reconciliation; 50,000 cash dividends and 8,583
other operating adjustments yield 44,468 operating cash. Investing adds 34
and financing uses 44,512, so cash/deposits decline by 10 to 9,790. The
parent balance sheet splits that total into 39 cash/due and 9,751 deposits
with banking subsidiaries; footnote (b) says it includes 8.0 billion of
intercompany time deposits. The 669,449 equity-method investment in bank
and bank-holding subsidiaries is a different asset. These dated issuer
figures do not establish cash freely transferable in a future scenario.

The final LuaLaTeX/bibliography logs are clean. Twelve ordered render hashes
bind PDF 115–126; the new example and its qualification appear together on
116, followed by instrument terms on 117. The unchanged historical ASU
passage remains on 120. The source paragraph was checked at normal
resolution; the first cramped pagination was repaired with one break at a
substantive transition. The final build took 8.215 seconds, with no GPU or
runtime execution.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain Version 2.35 as current provisional candidate | Exact bounded insertion, 154 passing checks, preserved equations/bibliography, legible ordered pages | No remaining source, citation, build or layout failure observed | Independent-reader and domain acceptance | Continue actual debt and transfer fact preparation | Full proposal readiness |
| Separate parent accounting resources from funding | Note 33 and Item 1A exact retained source, 74 source checks | Free-transfer or future-payment-capacity inference unsupported | Debt dates, deposit terms, regulatory and management conditions | Carry these as missing inputs in the company model | Parent can meet every future obligation |
| Keep historical and current authority separate | Dated 2016 ASU paragraph inherited exactly | Current-Codification completeness veto remains active | Missing official amendment index and operative text | Seek a genuinely new official route while continuing independent work | Issuer compliance verified |

Post-run red team: 2025 cash dividends and positive operating cash could be
mistaken for an assurance of unrestricted future payments. The adjacent
Bank/IHC restrictions and dated balance sheet defeat that inference. The
strongest alternative to an apparent funding surplus is a restriction or
timing mismatch at the legal entity that owes the payment. Actual future
transfer and maturity facts could change a later capacity verdict. The
weakest evidence is author-only reading and unresolved future conditions,
not the retained 2025 displayed arithmetic.

Full readiness remains not_ready. Implementation and the old controller stay
held. No installation, model run, paid engagement, outreach, publication or
Git write occurred.
