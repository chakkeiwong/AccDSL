from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
B=R/'docs/design/proposal/manuscript-consolidated-v552-20261027'
O=R/'docs/design/proposal/manuscript-release-prep-v551r1-20261027'
N=R/'docs/design/proposal/manuscript-release-prep-v552r1-20261027';W=H/'v552r1'
assert (R/'docs/AccDSL-latest.tex').resolve().parent==B
W.mkdir(exist_ok=False);N.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=[]
for p in sorted(B.rglob('*')):
 if p.is_file() and p.suffix in {'.tex','.bib','.lark','.md','.json'}:
  q=N/p.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);inputs.append({'path':str(p.relative_to(B)),'sha256':sha(p)})
baseline={'source':str(B.relative_to(R)),'target':str(N.relative_to(R)),'inputs':inputs,'pdfs':{p.name:sha(p) for p in B.glob('*.pdf')},'current_controls':{name:sha(R/name) for name in ['MISSION_CONTROL.md','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']}}
(W/'baseline.json').write_text(json.dumps(baseline,indent=2)+chr(10))
for name in ['accounting-product-proposal','simulation-foundations']:
 p=N/(name+'.tex');s=p.read_text();assert 'Version 5.52' in s;p.write_text(s.replace('Version 5.52','Version 5.52-R1'))
for name in ['simulation/family-policies.tex','simulation/observation-binding.tex','chapters/10-validation.tex']:
 (N/name).write_text((O/name).read_text().replace('sim:release-temporal-frontier','sim:temporal-frontier'))
for name in ['companions','fixtures']:shutil.copytree(O/name,N/name)
for p in (O/'spec').iterdir():
 if p.is_file() and not (N/'spec'/p.name).exists():shutil.copy2(p,N/'spec'/p.name)
for name in ['README.md','reference-map.json','component-index.json']:shutil.copy2(O/name,N/name)
p=N/'README.md';s=p.read_text().replace('5.51-R1','5.52-R1').replace('successor to 5.51','successor to 5.52');start=s.index('This is a protected');end=s.index('Run from this directory');s=s[:start]+'''This is a protected successor to 5.52. It preserves the explained complementary
share conventions and ordered-term program, repairs three stale scope statements,
and includes exact historical normative references and two runnable components.
It remains not_ready. Full release acceptance and redistribution rights remain open.

'''+s[end:];p.write_text(s)
p=N/'spec/REFERENCE-ROOTS.md';s=p.read_text().replace('5.52 source package','5.52-R1 source package');s+='''

This preparation package additionally includes exact historical sibling fixtures
under fixtures/ and both runnable components under companions/. Their manifests
and source identities are listed in component-index.json and package-manifest.json.
The historical contract may therefore resolve ../fixtures/ locally. General
scripts/ and docs/ evidence references still require the original repository
layout; the manuscript evidence closure remains incomplete. No private original
path is needed to typeset the two volumes or run these two bounded companions.
''';p.write_text(s)
print(json.dumps({'target':str(N),'protected_sources':len(inputs),'modified_tex':5,'status':'prepared_not_promoted'}))
