# JPMorgan 2016 Indenture summary: default and remedy distinctions

11 October 2026. Bounded E01/MC01/03/05/15/16/21/28/30/33–35 documentary
continuation after the closed Version 2.29 integration. The target reader is a
technical designer deciding which reported default and remedy conditions can
be represented as distinct conditional contract states. This source-only unit
does not edit the manuscript or claim legal enforceability.

## Research intent and evidence contract

- **Question:** What do the complete issuer-hosted 2022–2025 Form 10-K
  summaries separately say about issuer and guarantor insolvency, failure to
  pay, acceleration, holder thresholds, waiver and modification consent for
  securities under the 2016 Indenture?
- **Comparator:** the retained Version 2.29 callable-note source ledger, which
  binds principal and a few callable terms but has no systematic default or
  remedy reading. It is not the original Indenture.
- **Mechanism:** a default trigger, an acceleration option and a modification
  vote are different state transitions; they cannot be collapsed into a single
  `default` bit or treated as the same cash payment.
- **Primary pass:** four year-specific records with source PDF/text hashes,
  exact line and PDF-page spans, an ordered summary of each distinct condition,
  and an explicit account of changed versus repeated wording. Every promoted
  statement must be traceable to its own filing and source passage.
- **Promotion veto:** wrong issuer, indenture or date; missing or damaged body;
  text/PDF mismatch; omitted condition or exception; conflated issuer and
  guarantor; or any inference about operative completeness, ownership,
  recognition, enforceability or actual occurrence unsupported by the source.
- **Continuation veto:** a required filing's identity or summary pages cannot
  be verified, or a passage cannot be transcribed from retained source pages.
  A difference in wording alone is a review trigger, not a stop condition.
- **Repair trigger:** two-column or OCR order confuses a clause; render the
  exact page and compare before interpreting. Preserve unresolved wording
  rather than inventing an interpretation.
- **Explanatory diagnostics:** repeated words, page location, title labels and
  10-K year. These are not evidence of complete operative terms.
- **Must not conclude:** that the annual summary replaces the uninspected
  Indenture or supplements; that a default occurred; that any note was
  accelerated; legal enforceability; payment probability; liability carrying
  value; or a 2025 year-end balance.
- **Artifact:** source ledger, a compact result with decision/inference tables,
  author page review, run manifest and completion record under
  `data/accounting-master/jpmorgan-default-remedies-20261011/`.

## Skeptical and default audit

The wrong baseline would be Version 2.29's bank paragraph as if it quoted the
whole Indenture. That paragraph reports callable-note terms and explicitly
leaves the original contract uninspected. The 2022–2025 10-Ks are source-layer
comparators, not proof that the terms applied unchanged to every outstanding
series or that any trigger happened. A repeated summary can omit operative
exceptions. The smallest falsifier is a year-by-year exact-span comparison
against each PDF page, with separate issuer, guarantor, payment, acceleration
and modification fields. Promotion is to a **reported summary** ledger only.

The inherited choice of the four filings is justified by the closed source
unit's verified PDF/text identities; its failure mode is incomplete package
coverage, detected early by checking the summary heading, adjoining pages and
incorporation reference. The inherited 2016-Indenture link is a navigation
hypothesis; the official route returned HTTP 403 and no original text is
available. No threshold, timing or waiver clause is accepted merely because
one year's extracted text contains a matching phrase. The unit stops after the
four bounded summaries and does not retry the unchanged SEC route.

This audit passes for a source-only reading: the comparator, stop conditions,
qualification and source artifacts can answer the narrow question. It would
not pass as an operative legal or accounting policy evaluation.

## Execution

Use retained 10-K PDFs and their checked text only. Search headings and a few
lines at a time, bind exact spans and PDF-page witnesses, render only ambiguous
pages, then run deterministic source/identity/consistency checks. Record exact
commands and hashes in the result manifest. Preserve the Version 2.29 PDF and
all frozen controls. A later manuscript integration requires its own plan,
source-bound wording and rendered review.
