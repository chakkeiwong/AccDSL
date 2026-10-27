"""Refresh mutable controls only, after frozen Version3.34 evidence."""
from pathlib import Path
ROOT=Path('/home/chakwong/python/AccDSL')
checkpoint='''# Accounting master checkpoint

Updated16 October2026. Current proposal: **Version3.34,382 pages; not_ready**.
PDF: docs/design/proposal/manuscript-insurance-service-finance-origins-20261016/accounting-product-proposal.pdf
SHA256 49447b425936bcb6f35a616f34dbb3a3aa028088b3324d59222393aad19b1ffc.
Runtime/controller, empirical campaigns and installations remain held.

## Current evidence and next work

InsuranceOrigins/1 passes477 checks:11 cases,88 adverse inputs and2 source
challenges. It preserves multiperiod loss/service/finance allocation, held
recovery origins, both frozen B135 switches and homogeneous paragraph91 OCI.
Evidence: data/accounting-master/insurance-service-finance-origins-20261016/.
Attempt01 encoding refusals and their exact-value repair remain preserved.

Version3.34 passes404 document checks with133 protected prior sources.
Physical pages1,8,285–291 inspected;288–289 at full resolution. Frozen delta:
187 files,197 integrity checks.55 assessment checks preserve all53 obligations
and six interactions. Independent technical/domain/human acceptance pending.

Next: docs/plans/accounting-insurance-retrospective-measurement-20261016.md.
Compute full/modified transition measurements from cash and assumption histories;
then refresh J1 sector/company composition. All46 original operation rows govern.

## Continuity

Master: docs/plans/accounting-master-current.md.
Direct action: data/accounting-master/next-plan.md.
HEAD03fea070f089821f4759e49a4466a3399b7fc078, branch main. No commit made.
Previous controls: data/accounting-master/insurance-service-finance-origins-20261016/controls-before/.
Preserve unrelated work/index and frozen evidence. No continuation veto fired.
No publication, outreach or fees are authorized.
'''
(ROOT/'docs/plans/accounting-master-checkpoint.md').write_text(checkpoint)
p=ROOT/'docs/plans/accounting-master-current.md';s=p.read_text()
s=s.replace('Version 3.33, 380 pages','Version 3.34, 382 pages').replace('The 3.33 review delta','The 3.34 review delta')
a=s.index('B1 dated schedules pass');b=s.index('C1 and finite C2',a)
s=s[:a]+'''InsuranceOrigins/1 passes477 checks:11 cases,88 adverse inputs and2 source
challenges. Version3.34 passes404 document checks with133 protected sources.
Pages1,8,285–291 inspected;288–289 at full resolution. Frozen delta:197 integrity
checks;55 assessment checks preserve all53 obligations and six interactions.
Evidence: data/accounting-master/insurance-service-finance-origins-20261016/.
'''+s[b:]
s=s.replace('Next: I1 insurance\nservice/finance origins, then I2 transition measurement.','I1 now has finite service/finance and frozen OCI methods; mixed-origin early\ntermination remains explicit. Next: I2 full/modified transition measurement,\nthen J1 sector/company composition.')
s=s.replace('accounting-insurance-service-finance-origins-20261016.md','accounting-insurance-retrospective-measurement-20261016.md').replace('then refresh I2','then refresh J1')
p.write_text(s)
(ROOT/'data/accounting-master/next-plan.md').write_text('''# Accounting proposal — direct next plan

16 October2026. Version3.34,382 pages; not_ready.
PDF/hash: docs/plans/accounting-master-checkpoint.md.
Completed: InsuranceOrigins/1,477 checks;404 manuscript checks;133 protected sources.

Execute docs/plans/accounting-insurance-retrospective-measurement-20261016.md
after the recorded audit. Preserve full versus modified information views,
known cash, acquisition allocations, C14D nil rules and C16A–C recovery origins.
Then refresh J1 sector/company composition. All46 original rows remain.

Runtime/controller, installations, empirical campaigns, publication, outreach
and paid review remain held. Independent/domain/human acceptance remains
pending without stopping internal preparation. No continuation veto fired.
''')
print('Updated three live controls to3.34 and I2')
