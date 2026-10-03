# Financial-report source benchmark

Source acquisition accepted on 2 October 2026: **192 of 192 target reports,
2018–2025, with eight complete years for each of nine issuers.** Open
[the local index](index.html) to browse originals, text and source-QA evidence.
The [result note](../../docs/plans/accounting-benchmark-corpus-results.md)
records the selection repair, checks and remaining work.

| Reported basis family | Issuers | Required reports per issuer | Total |
| --- | --- | --- | ---: |
| US GAAP | Apple, Caterpillar, JPMorgan Chase | 8 annual + 24 quarterly | 96 |
| IFRS-oriented | Henkel, HSBC, Munich Re | 8 annual + 8 half-year | 48 |
| ASBE | SAIC Motor, Ping An, Midea | 8 annual + 8 half-year | 48 |

The active selection is [target-panel-v2.json](target-panel-v2.json), now the
collector default. Henkel and Munich Re replace Unilever and Allianz because
the probed original archives did not yield complete interim series. The
[frozen v1 results](snapshots/v1-final-selection/coverage.json), candidate
acceptance evidence, all originals and failed attempts remain preserved.
The selected panel is purposive, not statistically representative.

There are 168 accepted PDFs and 24 HTML filings. Source acceptance checks
report identity, period/class, financial statements and notes, preparation-basis
anchors and byte integrity. It does not adjudicate accounting meanings or
certify extraction accuracy. Annual reports are not labelled Q4. HTML external
assets and incorporated disclosures are not yet closed as complete packages.

## Local verification

Run from the project root:

```text
python3 -m unittest scripts.test_financial_report_corpus -v
python3 scripts/acquire_financial_report_corpus.py --revalidate-retained --init-grid --report
python3 scripts/verify_financial_report_corpus.py
```

These commands need no network access. Revalidation appends new verdicts;
it does not rewrite originals. A failed verdict revokes that retained version,
while a later network failure cannot erase a different verified version. The
last command independently checks hashes, current version verdicts, evidence
quotes, PDF readability, cross-slot duplicates and consecutive coverage. It
does not import the collector's coverage logic.

The accepted run used QA 6 and passed 20 regression tests. Its independent
manifest checks 244 retained original versions and 631 retained files. Seven
versions remain excluded from their requested slots. Those include parent-only
Allianz accounts and a Ping An IFRS report sought for an ASBE slot; exclusion
does not mean the report itself is illegitimate.

## Bounded acquisition and source updates

Acquisition is resumable and skips already verified slots. Use exact resolved
links and bounded batches, for example:

```text
python3 scripts/acquire_financial_report_corpus.py --only ping_an-2019-interim_h1 --source-host doc.irasia.com --acquire --resolved-only --http-client curl --limit 1
```

Run one collector writer at a time. Curl uses ordinary public HTTP(S), a
20-second connect limit, 120-second total request limit, 130-second process
limit and at most one retry per document request. Two consecutive access or
network failures pause a host within a batch. HTTP denials are retained;
no login, challenge solving or access-control bypass is supported. A source
host filter selects a known alternative without spending attempts on an
already failing host. Retain failures and inspect each downloaded candidate;
an annual/interim results release is not a substitute for full statements.

`--index-url` and `--index-plan` preserve archive evidence.
`scripts/resolve_financial_report_sources.py` resolves local indexes and keeps
the exact URL/provenance records. Search discoveries have their own hashed
records. Revalidate and regenerate integrity evidence after changing sources,
panel membership or QA logic. Do not overwrite frozen snapshots.

## Files and limits

- `documents/`: immutable originals and hash-named extracted text.
- `landing/`, `source-access.json`: cumulative source-index evidence.
- `access-failures/`, `acquisition-results.jsonl`: failed responses and all
  acquisition/revalidation attempts, including rejected versions.
- `resolved-sources.json`: exact candidates and discovery provenance.
- `expected-grid-v2.json`, `coverage.json`, `coverage.csv`: the active 192-slot
  grid and selected current verdicts. The v1 grid remains a historical file.
- `source-evidence.json`, `integrity-manifest.json`: current QA details,
  independent checks, hashes and physical PDF anchors for basis quotes.
- `runs/`: actual commands, environments, timings and later collector-source
  snapshots. `release-manifest.json` pins the accepted release's control files.
- `benchmark-protocol-v1.json`, `annotation-record.schema.json`: provisional
  tasks, issuer-family roles and annotation format; no gold labels or scores.

Only 56 accepted reports currently have sourced filing-date metadata; 136
publication dates remain unverified. Even a known filing date does not by
itself establish every historical byte vintage. Historical as-of forecasting
must wait for the required availability evidence.

Next work is internal source-span/context annotation, package/reference closure,
revision and basis-transition mapping, exact task oracles and implementation.
Whole issuer families must stay together across years, languages and versions.
Proposed heldout roles require an exposure audit for the particular model/task;
no clean unseen-model split or accuracy claim is established. No paid data
service or professional review was used for this collection.
