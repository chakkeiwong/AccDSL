# Recover and inspect Tamer's partial-identification survey

13 October 2026. P17/E08; MC08–12/18/26/29–30/32–35; G1/G3/G6/G8/G15.
Proposal preparation only. The lease unit's Version 2.51 is the protected
manuscript baseline; source availability does not by itself change it.

Question: can a legitimate, previously untried repository route recover the
blocked Tamer survey, and what does its technical discussion actually support
about identified sets, assumptions and uncertainty in this proposal?

The old retrieval ledger records a 404 from the legacy Harvard bitstream
handle. The retained `docs/design/research/raw/tamer-landing.html` contains a
different PDF link with `rel="item"` and `type="application/pdf"`:
`https://dash.harvard.edu/bitstreams/7312037d-3acf-6bd4-e053-0100007fdf3b/download`.
It also exposes the repository API base and the publication identifier
`73120378-d55b-6bd4-e053-0100007fdf3b`. Start with the explicit PDF link.
Use API metadata/content only if the returned link or retained page supports
it. Do not repeat the legacy 404 route. Inspect existing attempts before any
further fallback. At most eight distinct HTTP resources, 60 seconds and 30 MB
per request; sandbox network failure gets the required trusted retry and does
not count as evidence against the source. Retain commands, headers, receipts,
errors and original response bytes. No access-control bypass or paid service.

Pass criterion: a retained full text with checked author/title/version identity,
technical inspection, exact claim anchors and explicit implications/limits for
the proposal. A successful HTTP status, PDF magic, title match or search hit
only nominates a source. Wrong content/version, missing required technical
sections or unresolved source conflict veto use of the corresponding claims.
If acquisition fails, close the finite source inquiry with the exact blocker
and continue another independent ready obligation. Do not reject identification
methods because a URL fails.

Skeptical audit passes for this bounded route: the prior result is source-blocked,
the new link comes from a retained institutional page, and the previous failed
route is explicitly excluded. The paper is a survey: its exposition may clarify
concepts, but cited original results need their own inspected primary support
before adoption. A population identified set, a sample confidence region and a
set of accounting-compatible histories are different targets. No automatic
probability measure or real-company inference follows from a feasible set.
No stochastic ranking or runtime experiment is proposed.

Defaults and failure checks: retain the exact fetched version rather than
silently treating it as the published article; check page count, front matter,
technical sections and bibliography. The eight-resource cap is a convenience
stop for this inquiry, not a literature-completeness standard. Existing citation
counts are dated metadata only. Check version/correction/retraction information
through available publisher/repository/index metadata; record unavailable
checks as such. Look for author code if an actual algorithm is adopted.

If acquired, preserve the paper under `docs/papers/Partial Identification in
Econometrics Tamer (2010).pdf` without replacing any original. Read methods,
theory, examples, inference, relevant appendices and references. Keep separate
source-support, claim-support, citation/venue metadata, backward/forward
screening and omissions records in the new unit, with precise scope. Integrate
only a material checked finding under a further bounded P18 plan; preserve
the distinction between acquisition, technical reading and human acceptance.

Artifacts: `data/accounting-master/tamer-source-recovery-20261013/`, including
plan/baseline, acquisition records, source inspection, result and run manifest.
Continue to maintain all five E obligations and the full MC/G register.
