# P5 manuscript integration result

16 October 2026. Version 3.14 has 349 pages. The accepted PDF is
`docs/design/proposal/manuscript-company-composition-20261016/accounting-product-proposal.pdf`,
SHA256 `2d9d1c2bf2eeaa17ea5eb4b1ba5e8c0c95dd33104b4e6a3bcbd7f1211980d94e`.

The new company narrative derives the common opening, return and tax settlement,
internal inventory profit, non-controlling interest purchase, annual profit,
equity and gross cash flow. It distinguishes legal entries from consolidation
adjustments and migration from instantiation. The corporate section explains
the subsequent return, impairment, lease, contract-cost and tax-origin methods.
The reference section states the closed exchange and two migration subsets.
The corresponding finite financial evidence remains P5 attempt 03 and P2
CorporateResiduals/1 attempt 01; compilation does not add accounting evidence.

All 109 predecessor sources are retained. Four files change only the title/date
or insert the three new sections; every inherited equation, citation and
paragraph remains. The first integration accidentally reused an existing
section filename. The preservation check caught it, the failed candidate was
retained, and the inherited section was restored before the successful build.
The preparation script now uses the distinct filename as well.

Rendered review inspected physical pages 1, 17–22, 157–161 and 320–323 at 1.25
scale: all added content, title and adjacent boundaries. The first visual pass
found cramped sale labels on page 20. That compiled candidate is retained in
`manuscript-attempt-02/`; wider arrows and raised labels repaired the diagram.
The final page 20 was reinspected. The other 15 rendered images are byte-identical
between render attempts 01 and 02. There is no clipped table, equation or heading
on the inspected pages, and the final log has no overfull, undefined or duplicate
label warning. This is a 16-page visual review, not a claim that all 349 pages
have been read or that a human reader has accepted the narrative.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain Version 3.14 as current provisional candidate | Integrated derivations agree with the checked case; baseline content preserved | Filename collision and diagram defect repaired; clean final build | Whole-candidate consistency and human understanding | Reconcile current R04/R06 evidence, review R07 and reassess all 53 obligations | Mission readiness or human acceptance |
| Continue remaining method work | P5 demonstrates the named corporate/financing/group subset | No preservation or accounting failure in the accepted packet | Bank/insurance composition and other named methods remain incomplete | Maintain original-row residuals and repair ready methods | Closure of every original corporate or sector promise |

Existing LuaLaTeX and PyMuPDF were used; no installation, runtime/controller,
empirical campaign, external review or publication occurred. The build required
the trusted font-cache context already used by this project. Missing human
feedback remains an acceptance condition and does not stop provisional work.
