# Apple Item 1A coverage reconciliation

10 October 2026. E01/C03/C08; MC01–05/28/30/32–35 and G5/G11/G13/G18.
This is a source-coverage diagnostic. The manuscript remains the 161-page
Version 2.19, SHA256
`3303c933b57375818ab171eec1f2945f4d2f98f0771139db2fd515be5d292b9f`.
Full readiness remains `not_ready`; independent, human and domain acceptance
remain pending.

## Result and scope

The revised diagnostic has **65 passed checks and zero failed checks**. It
inventories all 28 annual Item 1A risk headings and both interim Item 1A
headings, retaining exact heading/body boundaries, offsets and hashes.
Annual categories, preambles and page furniture are separate from risk bodies.
The original annual PDF pages 8–20 were inspected for heading hierarchy and
navigation; this contact-sheet inspection is not continuous semantic reading.
Thirteen frozen prior source supplements supply 211 eligible source intervals.
Newly extracted inventory bodies do not count as prior source interpretation.

| Filing population | Complete prior body retention | Partial prior dependencies | No prior retained body reading | Total |
| --- | ---: | ---: | ---: | ---: |
| Annual FY2024 Item 1A | 5 | 3 | 20 | 28 |
| Interim FY2025 Q1 Item 1A | 2 | 0 | 0 | 2 |

Complete annual bodies are annual-05 (outsourcing), annual-18 (litigation),
annual-19 (general regulation), annual-21 (technology-industry scrutiny) and
annual-26 (receivables/prepayment credit). Partial dependencies are annual-02
(business interruptions/insurance), annual-15 (confidential information) and
annual-27 (tax). Both interim bodies were retained by the regulation and legal
units. The exact population and overlap provenance are in `risk-coverage.json`;
this table concerns inspected source scope, not accepted financial meaning.

Three evidence layers must remain distinct. A file may retain literal bytes
without establishing that every intervening paragraph was inspected. A bounded
body reading can support author interpretations within that source unit's
questions without independent acceptance. Independent accounting or semantic
acceptance requires additional evidence. None of these layers establishes
whole-report semantic coverage or a complete company forecast.

## Two source-locator defects

The first completed map incorrectly classified all annual bodies as retained.
Its interval arithmetic included these two historical locators:

| Historical locator | Original interval | Checked defect and disposition |
| --- | --- | --- |
| EPS `dependencies/4`, `annual.calendar` | 14600–161340 | Crosses Business through Note 1; wrong relative to a narrow calendar reading. Excluded from risk-reading coverage. |
| Revenue `dependencies/2`, `annual.segment` | 17584–225192 | Crosses Business through Note 13; wrong relative to a narrow segment reading. Excluded from risk-reading coverage. |

Their literal bytes, source supplements and frozen manifests are preserved.
`locator-scope-repairs.json` and `scope-repairs/` provide context-bound
replacement locators. Those repairs do not create new risk interpretations.
No prior source file was edited. The locator defect does not establish that
the earlier EPS or segment calculations are wrong; that conclusion would
require checking their actual mathematical dependencies.

Attempts 01/02/04 and the obsolete overbroad map in
`attempt-03-overbroad-map/` remain retained. The corrected coverage contract
excludes the exact two defective scopes rather than relaxing the population
or silently rewriting earlier evidence. No other literal/offset mismatch
was reported by this diagnostic.

## Decision and inference status

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | What is not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept this structural inventory within its declared source population | Exhaustive contiguous Item 1A partitions, exact body/heading checks and explicit prior provenance pass | Two overbroad scopes excluded and replaced; no remaining literal mismatch reported | Prior author interpretations retain their original scope and pending acceptance | Read annual-01, the first genuinely missing macroeconomic body, with its query-relevant dependencies | Whole-risk/report semantics, compliance, completeness of economic history or readiness |
| Keep E01 open | 20 annual bodies have no prior retained reading and three are partial | Missing interpretation is an open obligation, not a continuation veto | Exhibit recursion and other package narratives remain incomplete | Continue internal source preparation | Rejection of the wider mission or a reason to stop feasible internal work |

| Inference class | Status |
| --- | --- |
| Hard veto screen | Original overbroad mapping was invalid for reading coverage; corrected scopes and 65 checks support the revised inventory only. |
| Statistically supported ranking | N/A; deterministic documentary reconciliation, no stochastic method comparison. |
| Descriptive-only differences | 5/3/20 and 2/0/0 are source-population counts, not semantic scores. |
| Default-readiness | `not_ready`; no numerical, accounting or product default changes. |
| Next evidence needed | Complete scoped source readings, query consequences and later independent/human/domain acceptance. |

The result invalidated the original coverage diagnostic's interpretation of
two locators. It did not invalidate the filings, mission or current manuscript.
The repair is complete for this map, and no continuation veto remains.
The strongest alternative explanation for an apparently retained body is a
broad dependency interval without body-level inspection. Exact exclusions
address the discovered instances; fresh source review could reveal further
scope defects. This is the weakest part of author-level coverage evidence,
and the map must not be treated as a semantic acceptance certificate.

## Execution record

Actual diagnostic command:
`CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/apple-risk-coverage-20261010/reconcile.py`.
The retained `checks.json` reports 0.136509 seconds for the diagnostic stage;
this excludes later hierarchy rendering and human/model inspection. No exact
whole-stage wall time was recorded before resumption; do not invent one.
The resumed closeout command and measured time are recorded in the run manifest.
CPU only; GPU devices intentionally hidden; seeds N/A. Pinned annual PDF/text
and interim HTML/text, script, plan, repaired scopes, renders, result, frontier,
prior manifest and four current live-record hashes are bound by the closeout.
No network, worker, controller restart, installation, outreach, fee, publication,
commit or push occurred.
