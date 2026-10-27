"""One-shot freeze and control refresh after the finite asset increment."""
from pathlib import Path
import hashlib
import json
import platform
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=HERE/'corporate-v3'
assert not (OUT/'run-manifest.json').exists(), 'Do not rerun closeout'
checks=json.loads((OUT/'checks.json').read_text())
assert checks['passed'] and checks['count']==3493 and checks['financial_steps']==80
index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
assert index==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
for pin in json.loads((OUT/'predecessor.json').read_text())['files']:
    assert hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256']
paths=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
    'docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md',
    'docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
tag='## Extended method exchanges in progress — 15 October 2026'
section='''R03-P1 maps all46 original operation rows and protects204 inputs. Frozen
CorporateComponents/1,/2,/3 pass their finite checks. The asset successor /3
specifies58 methods,80 financial transitions in33 paths,329 exchanges and16
annual reports; all3,493 documentary checks pass. Direct surplus transfers,
separate restoration OCI, corporate-test order and unposted NCI goodwill are explicit.
Result: data/accounting-master/extended-method-exchanges-20261015/corporate-v3/result.md.
P2 remains open for benefit/tax and contract-composition variants under
docs/plans/accounting-corporate-remaining-exchanges-20261015.md. Continue P3/P4
sector profiles and P5 assembly/integration; R04/R06 residuals, whole-candidate
R07 and all53/interactions R08 remain. Active PDF: Version3.13,340 pages.
Full readiness is not_ready; runtime and empirical execution remain held.'''
prepared={}
for path in paths:
    old=(ROOT/path).read_text(); assert old.count(tag)==1
    a,b=old.split(tag); current,rest=b.split('\n## ',1)
    assert '2,665' in current
    prepared[path]=a+tag+'\n\n'+section+'\n\n## '+rest
next_path=str((HERE/'next-units.md').relative_to(ROOT))
prepared[next_path]=(ROOT/next_path).read_text()+'''
## P2c asset increment delivered — 15 October 2026

CorporateComponents/3 passes3,493 checks across58 methods,80 transitions and329
exchanges. Class revaluation, corporate-asset ordering, partial/NCI goodwill,
depreciated reversal and revalued restoration now have typed complete exchanges.
Direct surplus transfers preserve current OCI; restoration OCI is separate.
The exact profile is frozen by corporate-v3/run-manifest.json. This is a finite
asset increment, not P2 closure. The plan is
docs/plans/accounting-corporate-remaining-exchanges-20261015.md.

Next: pension ceiling/refund/contribution availability and multi-employer
findings; uncertain/acquisition/investment/Pillar Two tax; separate-contract
composition, variable price, recovery costs and progress fallback. P3/P4 remain
ready. P5 must still reconcile complete coverage, migration and combined reports.
'''
backup=HERE/'controls-before-p2c-assets';backup.mkdir(exist_ok=False)
records=[]
for path,new in prepared.items():
    p=ROOT/path;b=p.read_bytes();(backup/p.name).write_bytes(b);p.write_text(new)
    records.append({'path':path,'before_sha256':hashlib.sha256(b).hexdigest(),
        'after_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(backup/'refresh.json').write_text(json.dumps(records,indent=2)+'\n')
outputs=[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    for p in sorted(OUT.iterdir()) if p.is_file()]
manifest={'date':'2026-10-15','git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'plan':'docs/plans/accounting-corporate-remaining-exchanges-20261015.md',
    'result':str((OUT/'result.md').relative_to(ROOT)),
    'commands':['python3 '+str((OUT/name).relative_to(ROOT)) for name in ['build_exchanges.py','verify_exchanges.py']],
    'environment':{'python':platform.python_version(),'jsonschema':checks['jsonschema_version']},
    'cpu_gpu_status':'CPU-only; no GPU/framework calls','data_version':'Retained EU/AASB sources and existing P17/R03 exact illustrative cases',
    'random_seeds':'N/A: exact deterministic arithmetic','wall_seconds':{'final_verification':checks['wall_seconds'],'author_total':'Not captured; no performance claim'},
    'checks':checks['count'],'outputs':outputs,'readiness':'not_ready','index_preserved':True,
    'next':'P2c benefit/tax and remaining customer successors; P3/P4 sectors; P5 integration'}
assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==index
(OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'frozen':'CorporateComponents/3','checks':checks['count'],'controls_refreshed':len(prepared),'index_preserved':True}))
