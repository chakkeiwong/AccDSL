# JPMorgan parent-only balances and funding

12 October 2026. E01/C03; MC01/02/03/05/08/15/16/28/30/32–35,
G4/G5/G7/G11/G13. This is foreground source preparation for the governing
proposal. Version 2.34 remains the protected manuscript candidate. Runtime
implementation, the controller, installations, paid review and outreach stay
held. No external acquisition is needed for this unit.

## Question and exact baseline

What do the reported parent-only statements establish about JPMorgan Chase &
Co.'s cash, subsidiary income and intercompany funding, and what would be
wrong with treating consolidated resources or parent accounting income as
cash available for parent debt service? The comparator is the current bank
chapter's source-supported qualitative parent/IHC funding discussion and the
reported statements themselves, not a numerical simulation or a forecast.

Use the retained complete 2025 Form 10-K at
data/accounting-master/jpmorgan-complete-filings-20261011/sources/jpmorgan-2025-10k.pdf,
SHA256 e16cdad03ca84732dbe21b2595c112e975d5a3f27bce9f394828160275bfe79c.
Read all of Note 33, Parent Company (printed 310–311 / PDF 312–313), including
all table headings and footnotes. The 2025 contents establishes this identity.
Reuse existing 2022–2025 Exhibit 21/22.2 and funding annotations; they are
completed evidence, not a task to repeat. Inspect the relevant 2025 Item 1A
funding paragraph as a dependency, with exact page/column identity.

## Evidence contract and research intent

The mechanism is legal-entity and cash-versus-accrual separation. Expected
failure modes are comparing different perimeters, treating subsidiary equity
income as cash, confusing a receivable with unrestricted cash, missing a
negative cash-flow amount, or ignoring transfer limits. The primary pass
criterion is a reconstructible source ledger with exact selected rows,
headings, units and qualifications, checked displayed-amount reconciliations,
and explicit unknown facts for any forward funding claim.

| Diagnostic | Role |
| --- | --- |
| PDF identity, exact page/quote hashes, table column alignment | Promotion veto; repair before relying on the affected assertion |
| Balance-sheet, income and cash-flow displayed-number bridges | Primary documentary check; a mismatch triggers row/rounding/footnote investigation, not an invented residual |
| Missing footnote, perimeter, restriction or date | Promotion veto and repair trigger |
| Corrupt baseline or unreadable required source | Continuation veto for dependent work; independent tasks remain eligible |
| Counts of rows, pages, hashes and checks | Explanatory only; no semantic-completeness score |
| Missing contract rights, unrounded amounts or future policy | Explicit output limitation; not a reason to abandon source preparation |

Do not conclude parent payment capacity at a future date, legal enforceability,
complete group representation, ASC compliance, historical-byte availability,
default probability or full proposal readiness. No stochastic ranking or
default change is under test.

## Defaults, assumptions and skeptical audit

The issuer-hosted 10-K is an already checked retained source, not independently
verified regulatory bytes. That provenance supports reported facts within its
edition, not earlier as-of access. PDF page numbers are navigation hypotheses
until the rendered note title and printed page are checked. US$ millions and
parent-only scope come from the tables; neither may be inferred from the
consolidated report title. Displayed values are used for exact documentary
arithmetic only, not claimed as unrounded economic amounts.

The plan passes the skeptical audit after rejecting two stale premises:
Exhibits 21/22.2 were already read and integrated in Version 2.27; Parent
Company is Note 33 in this edition, not an inherited Note 32/34 guess. The
main misleading-success risk is that a reconciled parent balance sheet is
mistaken for spendable liquidity. The earliest discriminating diagnostic is
reading the cash footnote and funding restriction beside the income/cash-flow
bridge. Source-preservation and arithmetic checks cannot promote accounting
or forecast validity. Stop this unit only at a source/correctness veto; preserve
missing actual facts as unknowns.

## Execution and artifacts

Create a separate unit at data/accounting-master/jpmorgan-parent-note-20261012/.
Preserve the four current control files before changing them. Use existing
PyMuPDF and pdftotext for two note pages and the bounded funding dependency;
render at normal resolution and retain text, image and PDF hashes. Run CPU-only
documentary checks with CUDA_VISIBLE_DEVICES=-1; no ML framework or GPU is used.
Record exact commands, Python/tool environment, elapsed seconds and git HEAD.

Write source-ledger.json, source-manifest.json, checks.json, author-review.md,
result.md and run-manifest.json, including a decision table and post-run
alternative explanation. If the source materially improves the bank argument,
write a separate integration plan and candidate; do not mutate Version 2.34.
Update the live controls with the completed boundary and actual next action.
