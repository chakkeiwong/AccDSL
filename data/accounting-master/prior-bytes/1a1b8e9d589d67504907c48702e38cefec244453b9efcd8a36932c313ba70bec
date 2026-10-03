# Financial-report source corpus: execution record

Date: 2 October 2026 (Asia/Hong_Kong).
Authority: U5, MC01, MC03, MC05, MC19–22, MC28, MC30 and MC33–35.
Plan: [reviewed corpus plan](accounting-benchmark-corpus.md).

## Acceptance checkpoint

**Source acquisition accepted: 192 of 192 target slots, with eight complete
consecutive years (2018–2025) for all nine selected issuers.** Panel v2 is now
active. The frozen v1 selection remains at 172 of 192 slots, with incomplete
Unilever/Allianz interim series. This is source-corpus acceptance only; the
wider accounting, language/runtime and forecasting mission remains open.

| Issuer | Source-panel region | Reported basis family checked | Reports | Required series, 2018–2025 |
| --- | --- | --- | ---: | --- |
| Apple | United States | US GAAP | 32 | Annual + Q1/Q2/Q3 |
| Caterpillar | United States | US GAAP | 32 | Annual + Q1/Q2/Q3 |
| JPMorgan Chase | United States | US GAAP | 32 | Annual + Q1/Q2/Q3 |
| Henkel | Germany / EU | IFRS-oriented | 16 | Annual + H1 |
| HSBC | UK / Hong Kong | IFRS-oriented | 16 | Annual + H1 |
| Munich Re | Germany / EU | IFRS-oriented | 16 | Annual + H1 |
| SAIC Motor | Mainland China | ASBE | 16 | Annual + H1 |
| Ping An | Mainland China / Hong Kong | ASBE version selected | 16 | Annual + H1 |
| Midea | Mainland China | ASBE | 16 | Annual + H1 |

The accepted originals comprise 168 PDFs and 24 HTML filings, totalling
733,721,433 bytes. The PDFs contain 32,678 physical pages. These are source
inventory counts, not numbers of annotated or correctly interpreted pages.
The ledger contains 738 acquisition/revalidation records and 244 retained
original versions; alternate versions and rejected candidates are not extra
target observations. The independent manifest checks 631 retained files and
reports no integrity issue, cross-slot duplicate or PDF-repair diagnostic.

| Decision | Primary criterion | Veto checks | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept the source layer of v2 | All nine issuers exceed the five-year minimum; all meet the eight-year target | Current source QA and independent integrity/grid checks pass | Package closure, detailed semantics and vintage completeness | Freeze sources and prepare task-specific annotations internally | Accounting correctness, model accuracy or product readiness |
| Preserve v1 as historical/supplemental evidence | Source-access repair allowed by the reviewed plan | Do not count parent-only/other-basis files in target slots | Other accessible sources may exist | Retain originals, failures and selection reasons | Original issuers are unavailable everywhere |
| Keep annotation/evaluation provisional | Task protocol and schema exist | No adjudicated labels, named-model exposure audit or scoring plan yet | Labels, information availability and sample design | Build source-grounded records and exact oracles before evaluation | Forecast validity, statistical representativeness or superiority |

## What the source-access repair established

The continuation began with 175 acquisition records and 12 reported verified
documents. Those were an access/QA baseline, not a multi-year benchmark. The
collector now retains document-specific links and source indexes, checkpoints
each attempt, preserves versions, revalidates every retained version and keeps
an earlier verified file when a later network attempt fails. A failed
revalidation revokes the verdict for those bytes. Old QA versions require
revalidation rather than being silently accepted under new rules.

Official HSBC, SAIC, Midea and Ping An archives supplied report links. SEC
submissions supplied filing identities and dates, while direct SEC document
requests returned 403. Issuer-hosted Apple and Caterpillar copies were matched
to SEC filing metadata. JPMorgan's public quarterly feed supplied full filings.
All source and failed-response records remain in the append-only ledger and
the cumulative index record.

Unilever and Allianz's archives remained inaccessible in the bounded probes.
The public annual mirror supplied seven Unilever annuals and five qualifying
Allianz annuals, but no complete interim series. Two further Allianz files were
German-GAAP parent-company accounts for 2020–2021; they remain rejected for
consolidated IFRS slots. These failures describe the attempted endpoints, not
unavailability everywhere.

The plan permits source-access replacements that preserve the sector/standard
cells. Henkel supplies the consumer-products/adhesives cell and Munich Re the
insurance/reinsurance cell. Both have official eight-year annual/H1 archives.
Nestlé was an unsuccessful backup probe and was not selected. The v1 panel,
its coverage snapshots, originals and failed attempts remain preserved. No
model result influenced issuer selection.

Henkel's 2018–2019 archive calls its H1 files Q2/HY reports; the retained PDFs
identify them as half-year reports. Munich Re's oldest archive uses generic
Download links, so resolution uses only the nearest single-link paragraph's
title, excluding neighbouring parent-company reports. Its 2021 H1 cover prints
the year as `2/2021`; the parser now recognises that specific cover before
encountering prior-year references. English 2020 reports were found at official
Munich Re URLs and retained with search-discovery provenance.

CNINFO search-discovered URLs for Midea's 2025 annual returned 404. The report
was instead acquired from Midea's own site and its ASBE preparation statement
checked. A later indexed CNINFO candidate remains unresolved; the acquired
report is not asserted to exhaust all amendments or publication vintages.

Ping An's original-client requests intermittently timed out in TLS handshakes.
The host-pause rule stopped the batch after two failures. A proposed interrupt
found the process had already exited normally; no running process was killed.
The ordinary curl option subsequently retrieved the same 2022 H1 and 2023
annual URLs, with unchanged content checks. It uses a 20-second connection
limit, 120-second total request limit and 130-second subprocess limit, with
one retry for document acquisition. No authentication, challenge solving or
denial bypass was used. Request failures remain in the ledger.

The 2019 annual succeeded on retry. The issuer endpoint for the 2019 interim
continued to time out. A first IRAsia mirror copy was the IFRS/IAS 34 version,
which correctly remained outside the ASBE slot. A separate overseas regulatory
announcement reproduced the A-share interim report; it passed QA and its
ASBE preparation note was separately inspected. Both versions are preserved.
The mirror is disclosed as a public mirror, not represented as an issuer host.

## Engineering checks and interpretation

QA version 6 checks issuer, report period/class, statements, notes and quoted
preparation basis. Negated English and Chinese preparation statements cannot
establish basis on their own. Henkel's affirmative preparation note and Ping
An's ASBE interim-preparation note were inspected when repairing this check.
The check identifies the report's stated family; detailed jurisdictional,
transition and policy annotations remain provisional.

The independent verifier recomputes the expected period grid and consecutive
years without importing the collector's coverage-selection code. It checks
original, text, index and discovery hashes; latest version verdicts; quoted
basis evidence in retained text; duplicate content across target slots; and
accepted PDF opening/ending pages. Its manifest supplies physical PDF page
anchors for basis quotes. Hash-named originals and text cannot be silently
reused if their contents were altered.

All 244 retained versions were revalidated under QA 6: 237 version-level checks
pass and seven remain excluded from their requested slots. The 20 regression
tests pass, including corruption, revoked verdicts, comparative-year mistakes,
hidden HTML metadata, negative basis statements, curl timeouts and denied
responses. The annotation JSON Schema validates structurally, and provisional
roles cover all nine selected issuer families. Cover and preparation-note
rendering checks are preserved in `data/financial-report-benchmark/qa-inspection/`.
The Henkel quote begins on one page and its preparation statement on the next;
the integrity manifest distinguishes quote range from the actual basis-match
page, rather than presenting the preceding page as the preparation note.

Reproduction from the repository root, after preserving any desired release
snapshot:

```text
python3 -m unittest scripts.test_financial_report_corpus -v
python3 scripts/acquire_financial_report_corpus.py --revalidate-retained --init-grid --report
python3 scripts/verify_financial_report_corpus.py
```

The default command revalidates the active panel. Supplemental Unilever and
Allianz versions were also checked in the recorded v1 run. Exact network
batches, source snapshots and all failed attempts are retained in the run
records and ledger; reproducing source acceptance needs no new download.

Execution uses the existing Python 3.11.15 interpreter at
`/home/chakwong/miniconda3/envs/tfgpu/bin/python3` and CPU text/PDF utilities.
No environment packages were installed. No accelerator framework, stochastic
computation, external model worker or paid service is used. Seeds are not
applicable. The existing Git marker is unusable, so no
repository was initialised and no commit is asserted. Run manifests under
`data/financial-report-benchmark/runs/` preserve actual arguments, timestamps,
environment, code/panel hashes and wall time. Later runs retain their exact
collector source as well. Final revalidation is the reproducible current-QA
baseline; earlier acquisition runs did not all retain executable source copies.

## Next benchmark layer

`benchmark-protocol-v1.json` defines source inventory, context extraction,
temporal/revision handling, shared-IR conformance, bounded reconstruction and
conditional journal/statement tasks. `annotation-record.schema.json` defines
literal source spans, exact/unknown values, context, alternative readings and
review evidence. Structural schema validity is not accounting validity.

Provisional roles keep whole issuer families together. Apple and Caterpillar
have substantive prior development exposure. All issuers have source-QA
exposure. The proposed heldout families are concentrated in finance/insurance;
they are stress cases, not a representative or sector-balanced test population.
No split has been promoted for a named model or task, and no model score or
adjudicated accounting label has been produced.

Remaining work includes report-wide semantic annotation, closure of incorporated
documents and HTML assets, revision/translation family links, exact publication
availability, accounting-policy/transition mapping and executable task oracles.
The wider compiler/runtime, accounting authority and forecast-validation work
remains open. Unknown publication dates bar historical as-of tests. These are
internal preparation tasks under MC35; no paid review, outreach or spending has
been authorised or undertaken.

Publication metadata currently identifies filing dates for 56 accepted reports;
136 have no verified publication date. Filing-date metadata also does not prove
that all earlier/later byte vintages have been captured. The positive result is
an eight-year usable source collection; the strongest alternative explanation
for apparent downstream performance would be template familiarity, leakage or
unreviewed labels. A wrong-period/basis report, failed integrity check or later
version contradiction would trigger targeted repair and revalidation. The
weakest remaining evidence concerns complete disclosure-package semantics and
historical availability, which are explicitly outside this source acceptance.
