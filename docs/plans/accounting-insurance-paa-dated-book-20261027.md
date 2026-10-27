# Connect the existing PAA example to a dated company book

27 October 2026. C2/C3/C4; MC05/13/15/16/22/24–26/33–35. The original
MC22 acceptance review selects the complete short-duration gross/reinsurance
roll-forward in chapter 16. It does not require the newest recovery-change
extension as its only valid example. Preserve that extension's missing chronology
and group identities; this work supplies an explicitly synthetic calendar for
the existing, separate premium-allocation example.

Question: can the existing gross/held PAA example, with distinct group identities
and its three already-authored transferred-risk/non-performance variants, execute
through the unchanged company-book and report interfaces with complete expected
journals, intermediate states and report outputs? Candidate: a narrow conditional
adapter which compiles those supplied facts into DeclaredCompanyProgram/2.
Baselines: current chapter 16; docs/design/fixtures/sectors.json;
docs/design/review/accounting-dossier-checks.json; the retained December 2022
AASB 17 edition; unchanged CompanyBook/1, method-clock and CompanyBookReport/1.

Primary criterion: both named and renamed account charts yield every independently
authored dated journal, balance and group-preserving memory state, gross cash
origin and complete report. Base endpoint cash101, assets119, liabilities72,
profit27 and equity47 must match the original example. Separate transferred risk
3/2 raises the held claims asset and profit by1/2. Non-performance loss2 lowers
them by2. Neither changes issued liabilities, premium receipts or paid claims.
No allowance is mechanically set to a fraction of the gross risk adjustment.

Promotion vetoes: source drift, invented actual facts, lost issued/held identity,
wrong service fraction, netted gross cash or balances, unknown inputs silently
zeroed, changed unrelated accounts, final reports after failed events, native
interface failure or disagreement with independent complete expectations.
Failures trigger local contract/adapter/harness repair; no candidate failure by
itself invalidates the direction. Continuation vetoes: corrupt required evidence,
unresolvable native incompatibility or destructive concurrent conflict. Counts,
runtime and successful syntax checks are explanatory only.

Default/assumption audit: all amounts, zero financing/acquisition/investment
components, non-onerous coverage, short claims settlement, uniform service and
three ceded-risk cases come from the original example/dossier. They are supplied
conditional facts, not calibration or defaults. Both groups independently use
the one-year-or-less eligibility route under AASB17 53(b)/69(b); held recognition
uses62/62A, claims use59(b), transferred risk/non-performance use63/64 and revenue
allocation usesB126/B127. The retained edition supports these conditional rules,
not automatic current jurisdictional applicability.

Calendar assumption: coverage is 2024-01-01 to 2025-01-01 exclusive. The supplied
measurement boundary is 2024-07-02 00:00, exactly183 of366 elapsed days. Thus the
existing one-half uniform-service amount has an exact date basis; a convenient
June30 cutoff would not be the same fraction. Premium events are dated January1;
service, incurred-claims measurement and settlements are declared observations
at the July2 boundary with explicit command order. These dates are authored
synthetic inputs, not recovered issuer chronology. Group identifiers and owner
are explicit; equal group IDs or mismatched underlying-group links refuse.

The declared book period is the coverage year, with an interim report at July2.
It remains recorded-period-only with fiscal/notes completeness false. Cash flows
use an explicitly supplied operating-classification premise. No actual IAS7
admission is inferred from reconciliation. An unrelated equipment/equity balance
is used only as a complement-preservation control and is separately labelled.

Skeptical audit: directly wrapping the older recovery stages would invent missing
facts; this plan instead implements the already-selected PAA example with new
synthetic facts visibly supplied. Fixed dated commands must still enforce group,
date and stage continuity. A compiler which merely constructs a correct final
balance would miss duplicate/omitted events, so check every native transition and
use reordered/changed-date controls. Author expected journals, intermediate
states and reports before execution. Keep the original program and all accepted
writers unchanged. The plan passes for this bounded design/conformance repair.

Use exact rational arithmetic and Python3.11.15; no stochastic inference, GPU,
installation, forecasting, outreach or publication. Inspect the native entry
points and source paragraphs before implementation. Run one debugging smoke,
then six complete chart/case combinations and meaningful malformed-input and
native sequence controls with a120-second CPU limit per attempt. Preserve full
records, hashes, actual commands/environment and interpretation under
data/accounting-master/insurance-paa-dated-book-20261027/. After meaningful results
record a decision table and reset; keep human/domain acceptance pending while
continuing internal work. General actuarial calibration, full-year lifecycle,
new recovery-change admission and broad MC22 closure are not concluded.
