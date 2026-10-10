# Accounting master checkpoint

Updated 11 October 2026 (Asia/Hong_Kong). Authorised proposal preparation
continues. Full readiness is **not_ready**; implementation and the historical
background controller remain held.

## Current candidate and checked result

Current candidate: **168-page Version 2.27** at
`docs/design/proposal/manuscript-jpmorgan-guarantees-20261011/accounting-product-proposal.pdf`.
SHA256: `933091db38e0006a0124418150b3115b608780b777aee7dfc94ba270eb77a3f0`.

All eight JPMorgan Exhibit 21/22.2 bodies for 2022–2025 are read at author
level: 72 dated entity/jurisdiction rows, four guarantee descriptions and 96
exact source spans. All 147 checks pass; 2131 inherited references verify.
The eighteen-row rosters are explicitly partial and omit Financial Company
LLC, which Exhibit 22.2 identifies as the guaranteed issuer. Display nesting,
ownership, funding rights and guarantee scope remain distinct. Version 2.27
integrates these distinctions and the panel-coverage qualification without
changing the 48 displayed equations; readiness remains not_ready.

[Latest result](../../data/accounting-master/jpmorgan-subsidiary-guarantees-20261011/result.md),
[exhibit annotations](../../data/accounting-master/jpmorgan-subsidiary-guarantees-20261011/exhibits.json),
[author review](../../data/accounting-master/jpmorgan-subsidiary-guarantees-20261011/author-review.md),
[next frontier](../../data/accounting-master/jpmorgan-subsidiary-guarantees-20261011/next-source-frontier.md).

[Version 2.27 integration result](../../data/accounting-master/accounting-proposal-v227-integration-20261011/result.md),
[four-ledger review](../../data/accounting-master/accounting-proposal-v227-integration-20261011/four-ledger-review.md),
[candidate PDF](../design/proposal/manuscript-jpmorgan-guarantees-20261011/accounting-product-proposal.pdf).

## Exact next action

Continue the bounded source frontier after the completed Version 2.27
integration: inspect operative guarantee/registration terms, parent funding
facts, historical availability and full package semantics. Preserve the
candidate and its integration evidence, then feed any supported findings into
a separate later revision.

## Remaining program

[Current master program](accounting-master-current.md) preserves MC01–MC35 and
G1–G18. E01 complete filing semantics, E05 a genuine same-context accounting
conflict, E07 operative authority/broader methods, E08 deeper source support and
E14 dependency/model/interface evidence remain open. The forty prior exhibit
targets and 136 unverified publication dates remain; new JPMorgan dependencies
are recorded separately. The completed 290-equal-pair E05 search is not repeated.
Human, independent implementability and domain acceptance remain pending.

## Preservation and recovery

2131 inherited references verify after preserving the previous live controls.
Current controls and exhibit evidence are bound by
`data/accounting-master/jpmorgan-subsidiary-guarantees-20261011/run-manifest.json` and adjacent `completion.json`.

Frozen requirements, eighteen G rows, earlier manifests, source PDFs and
controller remain intact. Version 2.26 and its PDF remain preserved; Version
2.27 is bound by the integration run manifest, 86-check result and eight-page
render manifest.

Git HEAD `891a80316c3291d701b30723df687e517e11a06e`, branch `main`. CPU source
checks use the existing tfgpu Python with GPU devices intentionally hidden.
No commit/push, installation, model run, controller restart, outreach or
publication occurred. Never rerun closed generators into bound outputs.
Keep tool output bounded; advance across completed units.
