from pathlib import Path
ROOT=Path('/home/chakwong/python/AccDSL')
p=ROOT/'docs/plans/accounting-master-checkpoint.md';s=p.read_text()
s=s.replace('Version3.34,382 pages','Version3.35,384 pages').replace('manuscript-insurance-service-finance-origins','manuscript-insurance-retrospective-measurement').replace('49447b425936bcb6f35a616f34dbb3a3aa028088b3324d59222393aad19b1ffc','43e86e2408915c8c3c015bb4197b2d020dbba8be8ad3d0517338d8aadfd3f3fe')
a=s.index('InsuranceOrigins/1');b=s.index('## Continuity',a)
s=s[:a]+'''InsuranceRetrospective/1 passes436 checks:10 cases,87 adverse inputs and2 source
challenges. Full/modified measurements preserve cash, acquisition, loss recovery
and opening-equity origins. Evidence:
data/accounting-master/insurance-retrospective-measurement-20261016/.

Version3.35 passes407 document checks with134 protected prior sources.
Pages1,8,311–316 inspected;313–314 at full resolution. Frozen delta:174 files,
183 integrity checks.55 assessment checks preserve all53 obligations and six
interactions. Independent technical/domain/human acceptance remains pending.

Next: docs/plans/accounting-sector-company-composition-20261016.md.
Join bank/insurer/guarantee, tax, FX and ownership through shared legal books.
All46 original operation rows govern; general transition methods remain open.

'''+s[b:]
s=s.replace('data/accounting-master/insurance-service-finance-origins-20261016/controls-before/','data/accounting-master/insurance-retrospective-measurement-20261016/controls-before/');p.write_text(s)
p=ROOT/'docs/plans/accounting-master-current.md';s=p.read_text().replace('Version 3.34, 382 pages','Version 3.35, 384 pages').replace('The 3.34 review delta','The 3.35 review delta')
a=s.index('InsuranceOrigins/1');b=s.index('C1 and finite C2',a)
s=s[:a]+'''InsuranceRetrospective/1 passes436 checks:10 cases,87 adverse inputs and2 source
challenges. Version3.35 passes407 document checks with134 protected sources.
Pages1,8,311–316 inspected;313–314 at full resolution. Frozen delta:183 integrity
checks;55 assessment checks preserve all53 obligations and six interactions.
Evidence:data/accounting-master/insurance-retrospective-measurement-20261016/.
'''+s[b:]
s=s.replace('Next: I2 full/modified transition measurement,\nthen J1 sector/company composition.','I2 now supplies finite full/modified measurements and acquisition/recovery origins;\ngeneral discount, VFA and OCI methods remain. Next:J1 sector/company composition.')
s=s.replace('accounting-insurance-retrospective-measurement-20261016.md','accounting-sector-company-composition-20261016.md').replace('then refresh J1','then refresh source/protocol/reuse units');p.write_text(s)
p=ROOT/'data/accounting-master/next-plan.md';p.write_text('''# Accounting proposal — direct next plan

16 October2026. Version3.35,384 pages; not_ready. PDF/hash in master checkpoint.
Completed:I2 finite full/modified transition,436 checks;407 document checks.
Evidence:data/accounting-master/insurance-retrospective-measurement-20261016/.

Execute docs/plans/accounting-sector-company-composition-20261016.md after its
recorded audit. Bind shared legal bank/insurer/guarantee books, tax, matched
internal cash, FX and changing ownership. Preserve all46 operation obligations.
Then refresh source/protocol/reuse work and whole-candidate assessment.

Runtime/controller, installations and empirical work remain held; no outreach,
publication or fees. Independent/domain/human acceptance pending; no global
continuation veto. Internal preparation continues.
''')
print('Updated live controls to3.35 and J1')
