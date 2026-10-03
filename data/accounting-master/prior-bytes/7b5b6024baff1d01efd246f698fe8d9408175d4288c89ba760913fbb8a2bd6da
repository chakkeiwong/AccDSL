# Multi-year financial-report benchmark corpus

Authority: user instruction, 2 October 2026, to build quarterly or semi-annual
reports over preferably 5–10 years across regions, industries and standards,
before the remaining implementation work. MC01, MC03, MC05, MC19–22, MC28,
MC30, MC33–35; gaps G5, G7, G10–11 and G13. This priority supersedes the
previous immediate compiler-first sequence for the present work unit.

## Deliverable and selection

Build a retained, reproducible source corpus with period coverage, issuer and
accounting-basis metadata, provenance, content hashes, extracted text, source
validation and explicit missing-document records. Target 2018–2025 inclusive:
eight complete reporting years, covering pre-pandemic periods and major
accounting transitions. Acquire annual and full half-year statements with notes
for each issuer/year; acquire all three US 10-Qs alongside the 10-K. A trading
update or earnings presentation does not substitute for interim financial
statements. Annual is not labelled Q4. Fiscal periods are not assumed to equal
calendar quarters.

Initial v1 strata (preserved as historical selection): Apple, Caterpillar and JPMorgan Chase (US GAAP); Unilever,
HSBC and Allianz (IFRS-oriented reporting, exact basis checked per report);
SAIC Motor, Ping An and Midea (Mainland ASBE reports, exact basis checked).
These are purposive engineering cases, not a representative probability sample.
They cover technology, machinery, consumer goods, automotive/appliances,
banking and insurance across US, UK, continental Europe and Mainland China.
Issuer domicile, listing location, reporting jurisdiction and operating reach
are distinct fields. An H-share issuer's IFRS statements must not be labelled
ASBE merely because the issuer is Chinese. Bilingual versions are duplicates
within one report family, not independent observations.

Selection may be repaired if a full-report archive is unavailable, but retain
the rejected candidate/reason and preserve the intended sector/standard cell.
Do not shrink to annual-only or a single standard merely to report success.
Five complete consecutive years per selected issuer is the user-compatible
minimum if eight years are genuinely inaccessible; record exact coverage.

## Evidence contract and skeptical audit

Question: does a multi-year, diverse, locally usable source benchmark exist?
Baseline: Apple FY2024 + FY2025 Q1 and Caterpillar FY2024, with synthetic cases.
Pass criterion: actual retained full interim/annual reports spanning at least
five consecutive years for a diverse multi-standard issuer panel, an explicit
expected-versus-acquired coverage matrix, and reproducible integrity checks.
The target is eight years with at least nine issuers across three standard
families. Count bytes/years as acquisition evidence, not model correctness.

Vetoes for a report: unreadable/truncated file; error/login page posing as PDF;
wrong issuer, period, report class or accounting basis; no financial statements;
missing source attribution; duplicate content masquerading as another period.
Retry transient errors with bounded backoff, obey access restrictions and stop
repeating the same blocked endpoint. Prefer issuer/regulator sources; disclose
mirrors. Preserve downloaded originals and landing/index evidence.

| Skeptical concern | Resolution / early diagnostic |
| --- | --- |
| Existing tiny example corpus is treated as a benchmark | Inventory the actual retained reports before acquisition. |
| Region, sector and standard are conflated | Use multiple sectors per standard and distinguish domicile/listing/basis; report the panel's uneven coverage. |
| A successful download is a full statement | Inspect MIME/magic, parse pages/text, issuer/year and statement/note signals; inspect each archive's report classification. Quarantine ambiguous items. |
| “Q2 results” means a presentation or 6-K cover | Require the full interim report or attached complete statements and notes; keep release-only documents supplemental. |
| Later restatements leak into earlier forecast inputs | Store report vintage separately from covered dates; publication dates require evidence, otherwise mark unknown and bar as-of tests. |
| IFRS 17 or other transitions are silently harmonised | Retain original reported basis and comparative vintage; annotate transition candidates without inventing comparability. |
| Corpus counts become benchmark scores | No extraction, accounting, forecast or accuracy score is claimed. Gold annotation is a separate layer. |
| Heldout issuer families are split across years/languages | Assign all versions/years of an issuer together; current Apple material already has development exposure. Acquisition QA is not model evaluation. |
| Broad downloads cost time without usable result | Probe one annual/interim per source first, then cache and acquire bounded batches; maintain coverage after each batch. |
| Source access needs unsafe or expensive workarounds | No paid source, login bypass, new account or reviewer outreach. A blocked source does not block other cells. |

Decision: proceed with local tooling and bounded public-source acquisition.
No new package installation or model worker is necessary. Network commands use
the permission model and preserve failure evidence. The target is source-corpus
readiness, not a certified accounting gold standard or empirical forecast result.

## Execution and artifacts

1. Inventory current reports and archive entry points; inspect a small sample.
2. Save a versioned issuer panel and expected period grid under
   `data/financial-report-benchmark/`; retain raw archive indexes and originals.
3. Implement resumable acquisition/extraction with content hashes and explicit
   failure records. Do not overwrite original reports when a source changes.
4. Verify coverage, duplicates, parseability, full-statement/note evidence,
   accounting-basis anchors and period identity. Provide a browsable local index
   and machine-readable manifest; record uncertain metadata separately.
5. Define benchmark tasks, provisional family-level development/validation/test
   assignments and annotation schema. Prepare source-based cases internally;
   unreviewed annotations must remain provisional. Freeze actual as-of dates
   before any forecast test. No aggregate model score is produced in this pass.
6. Record commands, environment, source versions, wall time, results, limits and
   next annotation tasks. Update mission, requirements and checkpoint so future
   work starts from this corpus. Preserve prior evidence as historical records.

Run environment: existing Python 3, requests/BeautifulSoup, PyMuPDF/poppler and
ordinary CPU utilities. No GPU or stochastic computation; seeds N/A. Git is
unavailable; use content digests. Exact commands and final paths are recorded
in the result note. Successful compilation/download counts are explanatory
only; period and source completeness determine acquisition acceptance.

## Resumption audit and repair, 2 October 2026

The saved six-file baseline is retained. Code inspection found material flaws:
annual URL templates were applied to interim slots; an incidental prior-year
mention could pass period QA; generic issuer words could pass identity; an
IFRS mention did not necessarily describe the preparation basis; changed bytes
could be recorded against an unchanged original; failures could hide an earlier
successful acquisition; and results were only saved at batch completion.
These invalidate the old automated QA as a sufficient readiness criterion.

Repair before acceptance: class-specific and document-specific URL candidates,
strict issuer aliases, report-heading/filing-period checks, quoted basis anchors,
immutable versions of both originals and extracts, hash/duplicate verification,
per-attempt checkpointing, resumable acquisition, and complete revalidation.
Use issuer/regulator archive metadata to resolve ambiguous periods, retain that
metadata, and quarantine unresolved cases. A failed URL is evidence about that
URL only. A sandbox network failure is not an issuer-access verdict; rerun the
smallest request with the authorized trusted network context.

Acceptance is source-corpus readiness only: at least five consecutive complete
annual-plus-interim years per selected issuer with diverse regions, industries
and three evidenced accounting families. Aim for all eight years and all nine
issuers. A source index or a passing keyword check alone cannot meet acceptance.
Publication dates remain unknown unless sourced; this corpus alone cannot
support historical as-of forecasts. No model evaluation or paid review is run.

Audit decision: proceed after the above repairs and adversarial QA checks. The
comparator is retained source coverage, not algorithm performance. No stochastic
ranking, environment transfer, tuned default or GPU computation is involved.
Stop a source at a persistent denial; continue other sources and document the
unfilled cells. Do not silently replace standards or annualize interim data.

## Execution continuation audit

Baseline on resumption: 175 acquisition records and 12 reported verified
documents; zero complete five-year issuer sequences. This is a source
acquisition repair under the existing evidence contract, not a model benchmark.
Inspection found two remaining implementation defects: results were still
appended only at batch end, and ranking successful attempts above all failures
would conceal a later failed revalidation of those same retained bytes. Repair
both before extending coverage. Revalidate every retained version, including
previously rejected files, and let a new QA verdict supersede the verdict for
that version while preserving other valid versions and all network failures.

Resolve exact links from retained issuer indexes. The saved HSBC 100-item
archive contains the full 2018–2025 annual/interim sequence. Midea's corrected
Financial_Reports archive contains 2018–2024 annuals and 2018–2025 half-years;
the label “2022 H1 年度报告” must be treated as a half-year candidate and checked
against its actual cover. The substring 年度报告 also occurs in 半年度报告, so
classify half-year titles first. Do not infer 2025 annual availability.

Reviewed defaults: the inherited 2018–2025 window and nine issuers remain the
declared purposive panel; the five-year minimum comes from the user's request.
Archive labels nominate downloads; report contents, full statements/notes,
preparation basis and integrity determine source QA. Network failures veto
that endpoint only. Two consecutive access/network failures stop a host in a
batch; bounded probes then use another documented public source. This avoids
another 60-failure batch. Transient failure cannot erase intact verified bytes.

Audit passes with these repairs. Use one sequential network collector at a
time, retain index hashes and exact links, then revalidate and check duplicate
hashes across periods before reporting readiness. Readiness does not establish
semantic annotation, historical as-of availability, accounting correctness or
forecast accuracy. Record the result and commands in
`docs/plans/accounting-benchmark-corpus-results.md` and a machine-readable run
manifest beside the corpus. No paid source, expert engagement, model worker,
GPU, stochastic ranking or Git operation is required.

## Bounded source-selection repair audit

After acquisition reached 157 accepted target slots, the Unilever and Allianz
HTML archives still returned HTTP 403, including a bounded Allianz static-PDF
probe. Search responses supplied no usable report series; challenges were not
solved or bypassed. The annual mirror supplied Allianz SE parent-only German
GAAP files for 2020–2021; source QA correctly excluded them from the intended
consolidated IFRS slots. This does not show the companies' reports are
unavailable elsewhere.

Exercise the plan's existing selection-repair option by probing Henkel
(consumer products/adhesives, Germany) and Munich Re (insurance, Germany).
Nestlé's official archive returned 403 in the initial backup probe and was
not selected. Henkel's corrected official archive is accessible. Retain
the original v1 panel, all downloaded files, failed attempts and a frozen v1
coverage matrix. A candidate v2 preserves nine companies, three standard
families, consumer and insurance cells, the eight-year target and five-year
minimum. Candidate accounting bases must still be evidenced from each report.
Do not activate v2 unless retained archive links and report probes show that
the replacements can supply the required sequences. No model results or
accuracy scores influence this source-access repair, so it does not select
for performance. Full annotation and as-of evidence remain separate.

Ping An's 2019 PDF timeouts trigger a bounded newer-period probe and, if
needed, an ordinary alternative HTTP client against the same public links;
they do not establish archive unavailability. No denial or challenge is to be
bypassed. Midea already meets the seven-year sequence; resolving its 2025
annual remains a target-completion task rather than a minimum-readiness veto.

### Continuation checkpoint audit

The inherited twelve regression checks pass. Resolve Munich Re's two 2018
links from the nearest single-link paragraph or text element only; borrowing a
title from an entire year section could accept parent-only accounts. Probe
one annual/H1 pair per replacement, inspect the contents and basis statements,
then extend to the exact retained archive links. All report/parser changes
require revalidation of retained versions before acceptance. Try Ping An's
newer years without allowing the two 2019 timeouts to suppress them. The
baseline, five-year acceptance criterion, version retention, host stop rule and
non-claims above remain unchanged. This audit passes: the commands can resolve
source coverage, and no source-access or parser convenience is an accounting
or model-performance promotion criterion. Freeze v1 results before activating
any revised panel; nine passing issuer sequences are required.

Ping An continuation: some newer files succeed but the 2022 H1 request has a
TLS-handshake timeout. Add an explicit ordinary curl client option (same public
URLs and user-agent, no login/cookie/challenge handling), with 20-second connect,
120-second total request and 130-second process limits, at most one retry for
document acquisition. Compare against the existing urllib failure on the same
file, and apply unchanged content QA. A curl success establishes byte access
only; it cannot override HTTP denial or a content-QA failure. Preserve the
in-flight collector source and all subsequent run-source snapshots. This
bounded access repair passes the skeptical audit; stop repeated endpoint
denials and preserve the host-pause rule.

## Accepted source checkpoint

Execution completed at the source-acquisition layer on 2 October 2026. Active
panel v2 has 192/192 target reports, with eight complete years for every issuer.
Henkel and Munich Re supply the two replacement cells. The v1 selection and its
172/192 coverage result remain frozen, with all versions and failures retained.
All 244 original versions were revalidated under QA 6. The independent byte,
provenance, period-grid and PDF checks pass, as do 20 regression tests. The
final Ping An ASBE interim came from a separately identified A-share report
attachment; an IFRS mirror copy remains excluded from that ASBE slot.

The [result note](accounting-benchmark-corpus-results.md) and corpus
`release-manifest.json` preserve final acceptance, exact execution records and
remaining obligations. Task definitions, a provisional annotation schema and
issuer-family roles are prepared; accounting labels and model scores are not.
The next work is internal annotation/oracle preparation and the planned
compiler/runtime work. Unknown publication dates, incorporated packages,
revisions, standards transitions and semantic closure retain separate tasks.
