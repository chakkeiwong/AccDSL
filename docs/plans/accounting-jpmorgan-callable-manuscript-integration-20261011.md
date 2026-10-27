# Version 2.29 callable-note manuscript integration

11 October 2026. Bounded E01/MC01/03/05/15/16/21/28/30/33–35 repair of the
Version 2.28 bank chapter. The target reader is a technical designer who must
distinguish a reported note population, contractual payment rules, and the
accounting measurement that a complete implementation would still need.

## Argument and evidence contract

The 169-page Version 2.28 PDF (SHA256
`23c4e9dd0df82a62cdfa4dcf76716f19cee7b8f47d3c50d588c66cc61791f6ab`)
is the protected comparator. Its bank chapter explains guarantees but says the
terms do not supply a *current* balance. The new evidence identifies a
particular callable-note population at three dated year-ends, so the reader
needs that observation next to the payment terms while the 2025 disclosure's
2024 as-of date remains explicit.

Primary pass: a separate source tree and PDF add only a source-faithful bank
discussion and Version 2.29 title; all Version 2.28 prose, 48 displayed
equations, 71 bibliography entries and four JPMorgan citations remain. The
source contract is the 70/0 `source-ledger.json` under
`data/accounting-master/jpmorgan-callable-indentures-20261011/`, including
four issuer-hosted Form 10-Ks, page witnesses and exact source hashes. The
retained official SEC metadata identifies the S-3 event, while the four PDF
Exhibit 4.4 hyperlinks identify the original indenture URL. Direct SEC
Archives retrieval returned 403, so the underlying indenture and prospectus
supplements are not inspected and cannot be quoted as original terms.

Veto a changed equation, deleted qualification, incorrect 2025 balance date,
unsupported carrying/fair value or recognition inference, title-only delta,
unresolved citation, bad build, or clipped/illegible changed page. Page count
is a layout diagnostic, not a promotion criterion. Build with the existing
LuaLaTeX environment and inspect changed/adjacent PDF pages in order.

## Skeptical and default audit

The wrong baseline would be Exhibit 22.2 alone: it did not state an outstanding
amount, whereas the complete 10-K callable description does. The reported
`$5,000,000` is aggregate principal at its stated dates, not an accounting
carrying amount, a fair-value measure, all Series A debt, or a 2025 year-end
observation. The 2016 Indenture may contain provisions absent from the annual
summary. The smallest check is to compare the four source pages and as-of
dates, then verify the exact body delta and rendered page. The inherited
Version 2.28 layout and TeX environment are baseline conveniences; no new
accounting or numerical default is promoted.

The audit passes for a bounded explanatory repair: the source unit preserves
the report year, as-of date, instrument identity and summary/operative-text
boundary, and the manuscript can say only what those sources establish.
Independent reader, domain, legal and human acceptance remain pending; none
blocks provisional drafting.
