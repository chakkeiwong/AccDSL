"""Freeze source inventory; live control update accompanies manuscript integration."""
import hashlib
import json
import subprocess
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2)+'\n')

def main():
    tick = time.monotonic()
    assert not (OUT/'completion.json').exists(), 'Preserve closed result; verify separately'
    source = json.loads((OUT/'source-checks.json').read_text())
    ledger = json.loads((OUT/'source-ledger.json').read_text())
    checks = []
    def check(name, value):
        checks.append({'check':name, 'passed':bool(value)})
    check('118 source checks pass', source['passed'] == 118 and source['failed'] == 0)
    check('thirteen exact packages', len(ledger['packages']) == 13)
    for r in ledger['packages']:
        check(r['name']+' source witnesses intact', sha(ROOT/r['archive']) == r['sha256'] and sha(ROOT/r['registry_metadata']) == r['metadata_sha256'] and all(sha(ROOT/w['path']) == w['sha256'] for w in r['witnesses']))
    for name in ['result.md','author-review.md','next-source-frontier.md']:
        check(name+' retained', (OUT/name).is_file())
    predecessors = []
    for unit in ['easyocr-python-bidi-20261011','bidi-direct-rust-terms-20261011']:
        p = OUT.parent/unit/'run-manifest.json'
        m = json.loads(p.read_text())
        check(unit+' bound artifacts preserved', all(sha(ROOT/f)==h for f,h in m['artifact_hashes'].items()))
        predecessors.append({'path':str(p.relative_to(ROOT)), 'sha256':sha(p)})
    if any(not x['passed'] for x in checks):
        write('closeout-checks.json', {'checks':checks,'failed':sum(not x['passed'] for x in checks)})
        raise SystemExit(1)
    receipts = [json.loads(p.read_text()) for p in sorted((OUT/'sources').glob('*.receipt.json'))]
    plan = ROOT/'docs/plans/accounting-bidi-remaining-rust-terms-20261011.md'
    paths = [p for p in OUT.rglob('*') if p.is_file() and p.name not in {'run-manifest.json','closeout-checks.json','completion.json'}] + [plan]
    write('run-manifest.json', {
        'recorded_at':'2026-10-11', 'unit':'Remaining thirteen external Rust source terms for candidate python-bidi 0.6.11',
        'git_commit':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
        'git_state':'Read-only .git; no commit attempt; unrelated work preserved',
        'plan':str(plan.relative_to(ROOT)), 'result':str((OUT/'result.md').relative_to(ROOT)),
        'data_version':{'parent_sdist_sha256':ledger['parent_sha256'],'packages':[{k:p[k] for k in ['name','version','sha256']} for p in ledger['packages']]},
        'commands':['python3 data/accounting-master/bidi-remaining-rust-terms-20261011/fetch_remaining.py','CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/bidi-remaining-rust-terms-20261011/audit_sources.py','CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/bidi-remaining-rust-terms-20261011/closeout.py'],
        'environment':{'python':'3.11','cpu_gpu':'CPU-only documentary checks; GPU intentionally hidden','random_seeds':'N/A deterministic'},
        'wall_time':{'acquisition_seconds':sum(r['wall_seconds'] for r in receipts),'closeout_seconds':time.monotonic()-tick,'author_reading':'Not timed'},
        'source_checks':118, 'predecessor_manifests':predecessors,
        'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in paths},
        'controls':'Reconciliation accompanies planned Version 2.32 integration; current candidate remains Version 2.31',
        'readiness':'not_ready','runtime_compatibility':'not_checked','distribution_clearance':'not_checked'})
    write('closeout-checks.json', {'checks':checks,'passed':len(checks),'failed':0,'manifest_sha256':sha(OUT/'run-manifest.json')})
    write('completion.json', {'status':'closed_bounded_source_inventory','source_checks':118,'closeout_checks':len(checks),'failed':0,'manifest_sha256':sha(OUT/'run-manifest.json'),'readiness':'not_ready'})
    print(json.dumps({'source_checks':118,'closeout_checks':len(checks),'failed':0}))

if __name__ == '__main__':
    main()
