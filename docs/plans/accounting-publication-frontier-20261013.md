# Locate the next retained-report publication evidence

13 October 2026. P17; E01/C02–C03; MC01/03/05/28/30/33–35; G13.

Question: which of the remaining 120 selected reports with an unverified
publication-date status contain an explicit report-specific publication
statement? Comparator and identity baseline: the frozen 192-document
active rows from `coverage.json` and panel v2, joined to `source-evidence.json`,
excluding the sixteen completed Munich Re reports
and the 56 records carrying filing-date evidence. Search retained text for
publication/release/imprint terms in English and Chinese. Save all candidate
locations to disk, returning only counts and a small selection.

Search is an explanatory discovery diagnostic only. The pass criterion for a
new date record is an exact attributed statement read in its actual page
context, bound to the selected PDF hash, with competing date roles separated.
Wrong identity, illegible text, future-calendar language, an authorisation
date mistaken for publication, or an unrelated event vetoes that candidate.
No hit means unresolved in this search, not absence of publication evidence.

Choose the next coherent issuer group from the hits; inspect at most two
rendered pages per call. Save original evidence, quotes, labels and date
precision. Date-only assertions cannot supply an intraday cutoff, timezone,
or independent historical byte availability. Preserve original files and the
56/136 frozen assessment. New author exposure is recorded; no gold-label,
accounting-validity, forecast-performance or readiness promotion follows.

Skeptical/default audit: the Munich Re outcome motivates discovery but does not
establish a pattern in other issuers. Keyword coverage is incomplete by design;
the early diagnostic is contextual reading of candidate pages. The choice of
the next group is a convenience choice for source preparation, not a
representative sample or ranking. No network retry or runtime campaign is needed.
The audit passes for this bounded source question.

Pre-run population repair: `source-evidence.json` retains 224 records, including
32 reports from the superseded Allianz/Unilever panel. It is not itself the
192-report active panel. Join the 192 current coverage rows to their exact
source hashes and paths before selecting the 120 remaining unverified records.
This avoids silently introducing replaced issuers. The inspected coverage and
panel-v2 records agree on nine issuers, 192 reports and the 56/136 split.

Evidence root: `data/accounting-master/publication-frontier-20261013/`.
Run a local Python discovery script, preserve the queried patterns and selected
population, then record bounded page inspection and checks in a source-specific
result. Stop each invalid source claim; continue other valid candidates and
ready source work. Reassess further work after the discovery result.

Discovery follow-up: Henkel's credits pages contain an explicit “Date of
publication of this report” statement in all sixteen selected reports.
Five extracted labels split `publication` into `publica tion`; adjacent final
credits pages nominate those cases without altering raw text. Inspect all
sixteen credits pages, including their issuer, report-year and German-original
qualification. Keep a visibly inherited PR code separate from the stated date.
Search the rest of the declared 120-report population for report-specific
statements before concluding the local discovery phase; non-report event dates
remain excluded or unreviewed as appropriate. No expansion to replaced issuers.

A second, report-specific pass found a further explicit declaration in HSBC's
2025 annual report (PDF 248): 25 February 2026 is called its publication date.
Read that page and the matched 2023 hit (PDF 40, apparently BoE stress results)
before interpreting either. Compare the already retained 2025 issuer results
group only as corroborating event context, without promoting it to byte history.
Both inspections answer the existing publication question; no network is needed.
The broader `date of publication` phrase also nominates HSBC 2023 PDF 313 and
2024 PDF 325; multi-column extraction interrupts their report titles. Render
those pages and transcribe the actual column before adding a record. The 2018
occurrence describes board composition without stating a calendar date.
