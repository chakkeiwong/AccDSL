# Complete JPMorgan 2021–2025 filing-event supplement

11 October 2026. E01/MC01/04/05/30/33–35; G5/G11/G13/G18. Extend the
closed 2018–2020 filing-event supplement to the twenty remaining annual and
first-three-quarter periods, without changing selected-byte historical admission.
Baseline: frozen corpus, current SEC parent retained in the preceding unit,
two already retained historical shards (041/042) and Version 2.26.

The parent recent filings identify 2025 Q3 and annual events; its 42 historical
shards covering 2021–2025 can contain the other eighteen. Forty shards (001–040)
are unacquired. Retrieve those, reusing 041/042 and the parent. This is a bounded
complete-period check; selecting shards by guessed filing deadlines could miss
late or amended events. Source files are metadata only, about 0.35 MiB each
based on prior observed shards. Budget: forty new requests, enforced 2 MiB
streamed body cap and 45 seconds each. No unchanged route retry; preserve any
failure. No documents, models, installs, new extraction or GPU.

Primary criterion: one identified original filing per declared target period,
with issuer/form/period correspondence to retained report covers; enumerate
retrieved amendments and duplicates. Keep later evidence and exact clocks in
their own fields. Hard vetoes: source identity mismatch, inconsistent duplicate
accessions, unexplained missing period, wrong report period, historical bytes
inferred solely from a filing date. Missing selected-byte comparison blocks
as-of admission, not source-event records. Explanatory diagnostics: filename,
shard date ranges and counts. No historical completeness, forecast readiness,
or exact earliest public timestamp follows. Artifact:
`data/accounting-master/jpmorgan-filing-events-20261011/`.

Skeptical/default audit: the preceding probe exposed mutable SEC shard ranges
and a curl cap that did not constrain streamed bodies. Reuse the corrected
streaming cap, verify actual returned rows and identify events by accession and
period rather than shard number. Preserve same-accession duplicates with source
paths; inconsistent metadata prevents promotion. Exact CIK may differ from an
accession prefix because a filing agent can submit it; bind issuer identity to
the parent CIK and retained cover, not an invented prefix equality. The target
set is twenty periods from the existing corpus, not a new sampled benchmark.

Verify 1730 inherited references and save controls before modifications. Record
source requests, wall times, target rows and uncertainty. Preserve all original
reports and the frozen 56/136 corpus assessment. Update live controls only at
unit closeout and continue feasible source work. No new manuscript text unless
a substantive generic omission is found.

Identity-audit repair: retained 2022–2025 annual PDFs are shareholder reports,
and each expressly excludes pages of its corresponding Form 10-K (2022:
1–42, 304; 2023: 1–44, 322; 2024: 1–48, 334; 2025: 1–42, 328). The original
cover-match assumption is wrong for these four artifacts. Record official
filing-event identity independently, and classify these selected PDFs as
partial-content counterparts with their exact exclusion notice. They cannot
close whole-filing coverage or inherit filing dates for their whole contents.
This finding repairs the association test and adds an explicit E01 coverage
gap. Other retained 10-Q/2021 10-K covers remain eligible for the narrower
issuer/form/period check. Do not mark official filing-event identification
failed merely because the selected counterpart is incomplete.
