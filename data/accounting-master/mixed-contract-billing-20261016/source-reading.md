# Source and comparator reading

16 October2026. AASB15, compilation8,31December2022, registered F2023C00402.
Retained PDF/text: `docs/design/proposal/methods/sources/aasb15-compiled-dec2022.*`.
The title limits this edition to annual starts2023-01-01 inclusive through
2026-07-01 exclusive. This example uses Australian for-profit annual2024.
It makes no assertion about present law or IFRS/ASC/ASBE equivalence.

Inspected paragraphs9–10 (text304–328),18–21 (378–439),35–37 (561 onward),
39–45 (630–675),63 (821–826),73–78 (887–923),105–109 (1122–1158) and
B18–B19 (1541–1578). Paragraph21(c) applies the objectives of prospective
remaining distinct services and cumulative changes in the integrated promise.
The supplied allocations100/20 then140/30 and reliable cost progress are
example facts. Neither an invoice nor a contractual label proves allocation,
control transfer, contract eligibility, collectibility or faithful progress.

Paragraph63 concerns expected intervals between payment and transfer at
inception. All new events, including amended completion/payment expectations,
are within calendar2024; the timing finding and expedient election are explicit.
The old prepaid case ends in2025. Only its financial calculations are compared.
Paragraphs105–108 require an unconditional receivable separately from the net
contract balance and require AASB9 treatment of receivables/contract assets.
The finite join requires a supplied zero-impairment assessment at each event;
it does not compute that assessment or infer it from eventual collection.

Protected comparator: CorporateComponents/5 `additional_cases.py`,
mixed-amendment case, and `semantic-contract.md` mixed and CustomerCycle
paragraphs. The mixed example already supplies revenue55,61,71,170 and
cost42,42,46,112. CustomerCycle supplies identity-specific advances,
gross invoices, credited advances and settlements. Their composition is the
new contribution. Existing contracts and their scope remain unchanged.

Local derivation: gross unconditional bills G less applied advances K and
later collections C leave AR=G-K-C. Paid-or-unconditionally-due entitlement
T=G+A-K removes overlap between gross bills and earlier cash A. Comparing
earned R with T gives CA=max(R-T,0), CL=max(T-R,0). Therefore
cash+AR+CA-CL = capital+A+C-cost+G-K-C+R-G-A+K
= capital+R-cost. This identity verifies arithmetic, not the legal findings.
Each invoice, advance, credit and settlement retains its own contract identity.
Event journals are differences of the complete book; they cannot silently
recognize invoice revenue or credit an advance twice.
