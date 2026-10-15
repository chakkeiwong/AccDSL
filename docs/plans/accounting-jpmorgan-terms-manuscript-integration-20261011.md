# Version 2.28 instrument-terms manuscript integration

11 October 2026. Bounded reader-facing repair of the 168-page Version 2.27
candidate using the closed JPMorgan instrument-terms source unit.

## Argument state and evidence contract

The Version 2.27 bank chapter distinguishes entity, guarantee and funding path,
but it does not yet tell the reader what the cited Series A description says
about priority, payment-not-collection or the explicit limit on the guarantee.
The repair places those clauses after the reported group boundary. The reader
should move from “a guarantee is a separate exposure” to “its stated scope and
priority still do not supply an outstanding balance or recognition entry.”

The target reader is a technical designer who must preserve source wording while
building a bank funding model. The bounded delta is one prose paragraph in
`chapters/15-banking.tex` plus the Version 2.28 title/date. Existing equations,
numerical examples, citations, source qualifications and the Version 2.27 tree
are protected. The source/provenance sidecar is
`data/accounting-master/jpmorgan-instrument-terms-20261011/terms.json`.

Promotion requires a nonempty TeX delta, a clean LuaLaTeX build, the
same 48 displayed equations and valid labels/references, the four existing
JPMorgan citations, preserved Version 2.27 PDF identity, and visual inspection
of changed/adjacent pages. The source paragraph must retain the “summary,”
“payment and not collection,” subsidiary-priority and amount/defense
qualifications. Vetoes are source drift, deleted qualifications/equations,
unresolved citations, build/box errors, or a claim that these clauses establish
outstanding debt, valuation or accounting recognition. Author review remains
`independent_reader_pending`.

## Skeptical audit and default review

The principal risk is turning a prospectus summary into an asserted live
liability or treating the 2023–2025 funding sentence as a 2022 fact. The prose
therefore attributes the terms to the complete 10-K descriptions, preserves
the year-specific source boundary in the sidecar, and states the missing
balance/recognition facts immediately. The smallest diagnostic is a source
phrase check against the 48-check terms result before compilation.

The Version 2.27 tree is the reviewed baseline; the new wording is a source
interpretation repair, not a new accounting default or runtime policy. No
network, GPU, installation, product-engine run or professional engagement is
needed.

## Resumption audit and corrected acceptance criterion

Addresses MC01/03/04/17/19/28/30/32–35, E01/E07 and C08. The 168-page
target above was inherited from Version 2.27, not a user limit or a measure of
source fidelity. Two added-paragraph builds produced 169 pages. A compacted
replacement reached 168 but dropped the original offered-and-sold wording and
blurred which registrations and securities the unconditional-guarantee wording
covered. That candidate is rejected. Page count is an explanatory layout
diagnostic; it is neither a promotion criterion nor a continuation veto.

Restore the original paragraph verbatim and add the qualified term explanation.
Preserve the issuer-nonpayment trigger and the insolvency/bankruptcy exception to
the defense clause. Require a clean 168–170-page build as a bounded layout
check, then inspect PDF indices 114–122 (the preceding page, full bank chapter,
and following chapter opening). Equation/citation/source preservation remains
mandatory regardless of page count. A longer document would trigger a layout
investigation, not deletion of evidence. The source result is a description of
terms, not a legal-enforceability, live-balance or accounting-recognition verdict.

Default audit: Version 2.27 is the protected comparator, provenance established
by its saved tree and PDF hash; original chapter text must be retained in full.
The same TeX environment and type size remain the build baseline. No stochastic
comparison, numeric threshold or accounting default is proposed. Primary pass:
faithful, readable source integration with no substantive loss. Source drift,
missing evidence, changed displays and broken rendering veto this candidate and
trigger repair; they do not by themselves veto further internal preparation.

Reader questions: how does the guarantee differ from ownership or accessible
cash; what triggers the parent's payment; what limits and defenses survive; why
do those terms still not determine a live balance or recognition entry? The
existing EAD/PD/LGD illustration must remain explicitly illustrative and
separate from these actual instrument descriptions.
