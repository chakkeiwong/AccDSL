"""One-shot freeze and control refresh after the benefit/tax increment."""
from pathlib import Path
import hashlib
import json
import platform
import subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=HERE/'corporate-v4'
assert not (OUT/'run-manifest.json').exists(),'Do not rerun closeout'
checks=json.loads((OUT/'checks.json').read_text())
assert checks['passed'] and checks['count']==4809 and checks['financial_steps']==106
index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
assert index==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
for pin in json.loads((OUT/'predecessor.json').read_text())['files']:
    assert hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256']
paths=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
    'docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md',
    'docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
tag='## Extended method exchanges in progress — 15 October 2026'
section='''R03-P1 maps all46 operation rows and protects204 inputs. Frozen corporate
successors /1–/4 retain their checked increments. CorporateComponents/4 specifies
75 methods,106 transitions in51 paths,448 exchanges and18 annual reports;
all4,809 documentary checks pass. Benefit availability/classification and tax
origins/current-deferred/Pillar Two disclosures now have finite typed paths.
Result: data/accounting-master/extended-method-exchanges-20261015/corporate-v4/result.md.
P2 remains open for customer composition and exact residuals; full annual and
company joins remain P5 work. Continue P3/P4 sector profiles and P5 integration,
then R04/R06 residuals, R07 and all53/interactions R08. Active PDF: Version3.13,
340 pages. Full readiness is not_ready; runtime and empirical execution remain held.'''
prepared={}
for path in paths:
    old=(ROOT/path).read_text();assert old.count(tag)==1
    a,b=old.split(tag);current,rest=b.split('\n## ',1);assert '3,493' in current
    prepared[path]=a+tag+'\n\n'+section+'\n\n## '+rest
next_path=str((HERE/'next-units.md').relative_to(ROOT))
prepared[next_path]=(ROOT/next_path).read_text()+'''
## P2c benefit/tax increment delivered — 15 October 2026

CorporateComponents/4 passes4,809 checks across75 methods,106 transitions and448
exchanges. Benefit ceiling/availability, multi-employer deficit, uncertain tax,
acquisition/investment origins, revalued tax and Pillar Two boundaries have finite
typed paths. Full annual/company joins, further acquisition-DTA/mixed-origin and
benefit-allocation interactions remain P5 obligations. Preserve /1–/4 exactly.

Next: separate-contract addition, variable consideration, nonzero return-recovery
costs and unmeasurable-progress fallback, then reconcile P2 against every original
promise. Continue P3/P4 and P5; no source boundary or finite refusal closes a
missing original method. R04/R06/R07/R08 remain required.
'''
backup=HERE/'controls-before-p2c-benefit-tax';backup.mkdir(exist_ok=False);records=[]
for path,new in prepared.items():
    p=ROOT/path;b=p.read_bytes();(backup/p.name).write_bytes(b);p.write_text(new)
    records.append({'path':path,'before_sha256':hashlib.sha256(b).hexdigest(),'after_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(backup/'refresh.json').write_text(json.dumps(records,indent=2)+'\n')
manifest={'date':'2026-10-15','git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'plan':'data/accounting-master/extended-method-exchanges-20261015/benefit-tax-plan.md',
    'result':str((OUT/'result.md').relative_to(ROOT)),
    'commands':['python3 '+str((OUT/name).relative_to(ROOT)) for name in ['build_exchanges.py','verify_exchanges.py']],
    'environment':{'python':platform.python_version(),'jsonschema':checks['jsonschema_version']},
    'cpu_gpu_status':'CPU-only; no GPU/framework calls','data_version':'Retained EU/AASB sources; R03-E/F/G/L exact cases and targeted recognition-condition variants',
    'random_seeds':'N/A: exact deterministic arithmetic','wall_seconds':{'final_verification':checks['wall_seconds'],'author_total':'Not captured; no performance claim'},
    'checks':checks['count'],'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in sorted(OUT.iterdir()) if p.is_file()],
    'readiness':'not_ready','index_preserved':True,'next':'Remaining customer composition; P3/P4 sectors; P5 integration'}
assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==index
(OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'frozen':'CorporateComponents/4','checks':checks['count'],'controls_refreshed':len(prepared),'index_preserved':True}))
