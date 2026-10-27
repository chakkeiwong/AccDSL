# JPMorgan Series A instrument and guarantee terms

11 October 2026. Bounded E01/MC01/03/05/15/16/21/28/30/33–35 and
G4/G5/G7/G11/G13/G18 continuation from the Version 2.27 integration.

## Research intent ledger

- **Question:** What legal and payment terms are stated in the complete
  issuer-hosted 2022–2025 Form 10-K sections that Exhibit 22.2 identifies by
  issuer, Series A and registration statement?
- **Candidate mechanism:** the repeated Series A description, the issuer's
  direct/unsecured-obligation language, the parent guarantee paragraph and any
  stated limitations or events of default.
- **Expected failure mode:** the sections describe securities that may be
  issued or currently offered without identifying an outstanding population,
  carrying amount, valuation, redemption history or accounting recognition.
  A registration statement's effectiveness is a filing fact, not proof that a
  note was issued or remains outstanding.
- **Promotion criterion:** each 2022–2025 complete 10-K has source-identified
  passages for issuer, Series A/2016 Indenture, payment obligation, guarantee
  scope and any material condition; year-specific wording is preserved and
  every interpretation is tied to a source span.
- **Promotion veto:** a missing or mismatched complete 10-K, an unsupported
  legal conclusion, a comparison that ignores issuer/series/time, or a claim
  that the passages establish outstanding balances or accounting recognition.
- **Continuation veto:** retained PDF/text corruption or an unresolved page
  identity that prevents source-bound transcription.
- **Repair trigger:** if text order drops a clause or page, render the bounded
  source page and transcribe the exact layout before interpreting it.
- **Explanatory diagnostics:** line/page anchors, year-to-year wording, issue
  versus may-issue verbs, and the separation of instrument terms from balance
  and accounting facts.
- **Must not be concluded:** legal enforceability, complete indenture terms,
  ownership/control, outstanding principal, guarantee fair value, default
  probability, unrestricted subsidiary cash transfer or accounting treatment.

## Evidence contract and default audit

The comparator is the eight already-checked Exhibit 21/22.2 pages. The primary
pass/fail criterion is a complete, year-specific source map for the four
issuer-hosted 10-K sections; no numerical or legal ranking is sought. Missing
paragraphs, source identity mismatch and any unsupported strengthening of the
guarantee are veto diagnostics. Text location and repetition are explanatory
only. The result artifact will be a source-span ledger, a decision table and a
run manifest under
`data/accounting-master/jpmorgan-instrument-terms-20261011/`.

The local issuer-hosted 10-K candidates are used because the preceding source
unit bound their URLs, PDF identities and omitted-section coverage. That choice
is a source-layer baseline, not evidence of regulator-byte equality. Text
extraction is a navigation aid; any interpretation depends on the retained PDF
page and exact quote. The inherited assumption that the cited Series A passages
are the relevant operative description is a hypothesis to test, not a legal
default.

## Skeptical audit and pre-mortem

The plan could pass while misleading us if the prospectus describes a possible
issuance and the result silently turns it into a current liability. It could
also fail because the text extraction loses a two-column qualification rather
than because the source lacks the fact. The smallest discriminating check is a
bounded four-year search for the issuer, Series A, 2016 Indenture, direct
obligation and guarantee paragraphs, followed by PDF-page identity checks.

Use only retained local PDFs/texts; do not fetch new sources, retry failed SEC
routes, alter the Version 2.27 candidate, or run a product engine. Run the
bounded checks with the existing CPU environment and record the actual command,
commit, source hashes, page/line anchors, result and next action.
