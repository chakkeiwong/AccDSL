# Accounting master checkpoint

Updated 16 October 2026 (Asia/Hong_Kong). Full readiness is **not_ready**.
Current proposal: **Version 3.18, 357 pages**.
PDF: `docs/design/proposal/docs/design/proposal/manuscript-compound-rollforward-20261016/accounting-product-proposal.pdf`
SHA256 `77ab65d6820b561c555423de828ec7819e8681f7e82280ebb0b9c1e571638bb4`.
Runtime, empirical campaigns, installation and the former controller remain held.

## Current result and next work

CompoundTaxRollforward/1 passes 200 schedule checks; CompanyTaxEPS/1 accepted
attempt-02 passes 242 company/projection checks plus four focused binding checks.
A separate principal100/coupon4 instrument has effective interest12, current tax
relief1 and deferred tax income2: after-tax cost9. It connects the initial equity
charge to maturity, complete P5 earnings/NCI/cash and dated read-only EPS.
The first wrapper's source/base call-chain finding was repaired and preserved.
Result: `data/accounting-master/compound-tax-rollforward-20261016/result.md`.

Version3.18 preserves all117 Version3.17 sources;356 document checks pass.
Eight affected/boundary pages received incremental visual inspection. All53
original MC/G obligations are retained in that unit's assessment successor.
The3.17 fixed packet remains unchanged; exact new3.18 inputs and predecessor
binding are in `data/accounting-master/compound-tax-rollforward-20261016/review-delta.json`.
Independent technical and human/domain acceptance remain pending.

**Next:** execute `docs/plans/accounting-repeated-rebalancing-20261016.md`.
The audit identified why adding per-reset minima can fail cumulative hedge
measurement. Extend repeated additions of hedged-item layers while preserving
origin prices and cumulative ineffectiveness. Removed/instrument layers,
early conversion, broader fiscal periods/rights and sector joins remain open.
Pending review is not a continuation veto.

## Continuity

Master: `docs/plans/accounting-master-current.md`.
Direct action: `data/accounting-master/next-plan.md`.
HEAD `03fea070f089821f4759e49a4466a3399b7fc078`, branch `main`.
Index empty; cached raw-diff SHA256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
No commit was made in these units; unrelated work/index are preserved.
Previous controls: `data/accounting-master/company-tax-assessment-20261016/controls-before/`.
Original requirements, catalog/controller/corpus records, frozen release hashes
and P5/P2/P3a2/OrderedEPS/R03–R08 evidence retain their limited scope.
No continuation veto fired. No publication, outreach or fees are authorized.
