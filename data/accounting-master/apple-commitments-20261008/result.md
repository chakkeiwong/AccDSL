# Apple leases, purchase commitments and funding result

8 October 2026. The bounded E01/C03/C08 unit is complete. Version 2.8 adds
the real-company commitments discussion and repairs the earlier implication
that short-term purchase amounts were wholly unquantified. It advances
MC01–05/07–12/14–16/28/30/32–35 and G1/G4/G5/G11/G13/G15/G16. The full
proposal remains **not_ready**; product implementation and the historical
controller remain held.

Candidate: `docs/design/proposal/manuscript-commitments-20261008/accounting-product-proposal.pdf`,
137 pages, SHA256
`c7d3a55d92d48529ef376b0207f87d45febe115710dce96f20c836ba632f26b4`.
Plan: `docs/plans/accounting-apple-commitments-20261008.md`.

## Source findings and computed quantities

Full retained annual Notes 8/12 and interim Note 9 have sixteen source units;
six dependency passages cover the lease policy and annual/interim management
discussion. Fifty monetary table cells and nine query examples carry their
scopes, dates, qualifications and missing facts. Source reading includes the
contingency and supply paragraphs after the purchase table. Complete character
coverage of those notes is not complete filing semantics or independent review.

The September lease maturity table reconciles 14,790 million of undiscounted
payments less 2,360 imputed interest to 12,430 recognised liabilities. All class,
date and component sums reconcile. ROU assets of 11,303, the current liability
of 1,632 and fiscal-2025 maturities of 1,991 are distinct measurements. The
additional 849 of uncommenced fixed payments gives a displayed-centre sum of
15,639, compatible under a nearest-0.1-billion assumption with management's
15.6 billion fixed-payment disclosure. This does not verify issuer rounding
policy or contract population identity, book the 849, or recover commencement
dates, cash dates and discount rates.

The note's 13.8 billion variable lease cost is historical expense, primarily
associated with output purchases. It is different from fixed future cash and
cannot simply be added to manufacturing commitments without an overlap map.
Fixed operating cost, fixed operating cash and noncash ROU additions remain
separate. Aggregate term/rate descriptions do not reconstruct contract curves,
renewal decisions or the `thereafter` payment profile.

The earlier A18 selected interpretation correctly records Note 12's remaining-
term-over-one-year condition. It cannot support a file-wide claim that all
shorter-horizon amounts are unknown. Annual MD&A reports manufacturing
obligations of 53.0 billion, with 52.9 payable within twelve months, and other
purchases of 12.0, with 4.1 within twelve months. Note 12's 11,226-million total
includes 3,206 in fiscal 2025: remaining contract term and payment date are
different filters. A 12.0-minus-11.226 short-contract residual is unsupported
without a source-backed population mapping. Historical A18 bytes are preserved;
the supplement records the more complete file-level interpretation.

At December the manufacturing aggregate is 39.8 billion, all due within twelve
months. The quantity computed by 53.0−39.8 is the change in reported amounts
at displayed centres. It is **not actual deliveries, purchases or cash spent**.
The conditional model defines a comparable population of undelivered fixed-
price orders extinguished on delivery, with no cancellations or price/FX changes.
New orders of 0 or 5 then require deliveries of 13.2 or 18.2 to preserve both
endpoints. Cash versus payable settlement yields four balanced subsystem
witnesses. Unsold inventory, no opening payables/prepayments/tax and no other
statement constraints are explicit assumptions. The disclosure does not
establish that reporting convention for every actual obligation.

The interim no-material-change statement supplies no exact new lease amount.
Management's negative contingency assessment is retained with its dated
reasonable-possibility/materiality/excess-over-accrual qualifications; it does
not identify zero litigation exposure. Supplier concentration, capacity,
technology and location statements constrain possible future scenarios without
supplying quantitative shocks, probabilities or control/revenue allocations.

## Decision and evidence status

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | What is not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept bounded source preparation | All declared note/passage units disposed; fifty monetary cells and nine queries; 110 source/arithmetic checks pass | Source partition failure repaired; no remaining detected source/date/scale or arithmetic defect | Contract populations, commencement, output/price, delivery and settlement facts remain unknown | Continue retained inventory/PP&E and cash-flow interpretation | Full package semantics, actual funding projection or accounting compliance |
| Retain conditional delivery/settlement examples | Four witnesses balance under explicitly stated subsystem assumptions | Model conventions and omitted facts are visible; no inferred probabilities | Apple reporting conventions or other statements may exclude these histories | Require actual delivery/contract data before narrowing real history families | Actual Apple purchases/cash or exhaustive admissible histories |
| Integrate Version 2.8 provisionally | 31 candidate/preservation checks; clean build; thirteen rendered pages inspected | Exact-string checker failure repaired by whitespace normalisation; manuscript already contained the qualifications | Independent reader, human and domain acceptance pending | Continue internal source work and manuscript repair | Whole-proposal readiness or an implemented engine |

Issuer assertions are source evidence. Deterministic table/journal checks,
hashes and build records are engineering evidence. The bounded interpretations
and conditional derivations are author evidence; full operative ASC support
and independent semantic acceptance remain separate obligations. There is no
stochastic comparison, uncertainty-based ranking or default-policy promotion.

## Validation, review and preservation

The evidence checker initially matched `Contingencies` inside the title. Two
coverage checks failed; the exact subsection marker repairs them. The first
checker, report and outputs remain in `first-evidence-attempt/`. The candidate
checker initially failed a phrase spanning a source newline; its first script,
report and delta are in `first-candidate-attempt/`. Whitespace normalisation
repairs that diagnostic without changing the manuscript. Current results:
**110 source/arithmetic checks and 31 candidate/preservation checks pass**.

Only the title version, appended real-company section and history-opening
bridge change from Version 2.7. All 38 prior displays and 66 bibliography
entries survive; one new labelled identity brings the display count to 39.
One build produced a 137-page PDF with clean LuaLaTeX/BibTeX logs. Navigation/
layout inspection covered pages 1–7 and 18–23; pages 19–22 were read continuously
at full size. The author review records source limits, diagnostic dispositions
and pending acceptance. The unchanged bibliography has no new full visual audit.

Original annual pages 28, 37, 45, 48 and 49 and one derived interim print page
were inspected. The interim view is not an original browser screenshot. No
network request, installation, GPU work, outreach or paid engagement occurred.

The baseline protects 114 files and resolves 112 prior-manifest references
through saved pointer copies. Historical verification retains 1,266 protected
files, 518 upstream references and six controller hashes, including P19's
existing path relocations. Original sources, prior candidates and closed units
are unchanged. No Git mutation or closed-unit generator rerun occurred.
The run manifest records commands, environment, source versions, the full
elapsed interval and artifact hashes; completion binds its exact hash.

## Post-run red-team and next work

The strongest alternative explanation is that reported manufacturing obligations
are reduced on a different event, or contain populations incompatible with the
illustrative order/delivery model. That would invalidate applying the model to
actual Apple transactions; the result explicitly does not apply it that way.
A complete issuer roll-forward and contract/settlement evidence could identify
deliveries and cash and make this aggregate illustration unnecessary. The
weakest evidence remains author semantic interpretation and unknown actual
contracts. Arithmetic cannot remove those limitations.

No continuation veto fired. The evidence supports continuing E01/C03 with the
retained inventory and property, plant and equipment disclosures, starting from
A09 (annual Note 5) and I06 (interim Note 5), their policies, statement and
cash-flow dependencies. Distinguish purchases, production/consumption,
depreciation, noncash acquisitions and payment. Plan and audit that population
before work; do not silently treat a stock change as a flow.

All five wider E01/E05/E07/E08/E14 workstreams remain open, including forty
exhibit targets, the genuine same-context conflict, operative applicability,
four blocked papers and broader interface/dependency/model/terms support.
The 136 unverified publication dates are unchanged. All MC01–MC35/G1–G18
acceptance wording is retained, with no whole-mission closure from this example.
