# Accounting master checkpoint

Updated 16 October 2026 (Asia/Hong_Kong). Full readiness is **not_ready**.
Current proposal: **Version 3.20, 360 pages**.
PDF: `docs/design/proposal/manuscript-hedge-inventory-20261016/accounting-product-proposal.pdf`
SHA256 `52ee0ba7013029fc3a725e937b32e9afdb407504d3836ed0a44600d6903eab73`.
Runtime, empirical campaigns, installation and the former controller remain held.

## Current result and next work

HedgeInventoryClose/1 passes170 checks: source-bound replay, full purchase,
settlement, direct inventory basis transfer and full sale for positive and
negative reserves. Pre-sale inventory/earnings detect an incorrect direct
reserve-to-profit release even when terminal profit agrees. This is a cumulative
pre-tax subledger; full-company tax/NCI integration remains open.
Result: `data/accounting-master/hedge-inventory-close-20261016/result.md`.

Version3.20 preserves119 baseline sources and passes362 document checks.
Physical pages1,8,196–200 were inspected,198–199 also at full resolution.
All53 original obligations and six interactions retain their acceptance states;
55 preservation checks pass. The3.19 delta passes162 integrity checks.
Exact3.20 delta: `data/accounting-master/hedge-inventory-close-20261016/review-delta.json`.
Independent technical/domain and human comprehension acceptance remain pending.

**Next:** execute `docs/plans/accounting-hedge-inventory-subsequent-20261016.md`.
Follow the adjusted basis through partial sales, NRV write-downs and capped
recoveries for a homogeneous single batch. Partial forecast purchases and
retained reserves require a separately supported allocation rule; removed or
changed instrument layers, tax/NCI and wider company joins remain open.

## Continuity

Master: `docs/plans/accounting-master-current.md`.
Direct action: `data/accounting-master/next-plan.md`.
HEAD `03fea070f089821f4759e49a4466a3399b7fc078`, branch `main`.
No commit was made in these units; unrelated work and index are preserved.
Previous controls: `data/accounting-master/hedge-inventory-close-20261016/controls-before/`.
Original requirements, frozen release hashes, catalog/controller/corpus records
and earlier P5/P2/P3a2/OrderedEPS/R03–R08 evidence retain their limited scope.
No continuation veto fired. No publication, outreach or fees are authorized.
