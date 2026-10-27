"""Freeze this direct-source unit and bind preserved/current controls."""
import hashlib
import json
import subprocess
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(name, obj):
    (OUT/name).write_text(json.dumps(obj, indent=2)+'\n')

def main():
    start = time.monotonic()
    assert not (OUT/'completion.json').exists(), 'Closed unit: use a separate verification output'
    checks = []
    def check(name, yes):
        checks.append({'check': name, 'passed': bool(yes)})
    source = json.loads((OUT/'source-checks.json').read_text())
    check('source checks pass', source['passed'] == 17 and source['failed'] == 0)
    for unit in ['easyocr-python-bidi-20261011','apple-constitutional-sources-20261011']:
        manifest = json.loads((OUT.parent/unit/'run-manifest.json').read_text())
        check(unit+' preserved', all(sha(ROOT/p) == h for p,h in manifest['artifact_hashes'].items()))
    ledger = json.loads((OUT/'source-ledger.json').read_text())
    for item in ledger['crates']:
        check(item['crate']+' witness hashes', all(sha(ROOT/w['path']) == w['sha256'] for w in item['witnesses']))
    reloc = json.loads((OUT/'baseline-controls.json').read_text())['pointer_relocations']
    check('four prior controls preserved', len(reloc) == 4 and all(sha(ROOT/x['preserved_path']) == x['sha256'] for x in reloc))
    controls = {x['historical_path']: sha(ROOT/x['historical_path']) for x in reloc}
    candidate = json.loads((OUT.parent/'accounting-proposal-v231-integration-20261011/completion.json').read_text())['candidate_pdf']
    check('Version 2.31 PDF unchanged', sha(ROOT/candidate['path']) == candidate['sha256'])
    for p in controls:
        body = (ROOT/p).read_text()
        check(p+' reconciled', '0.6.11' in body and 'Version 2.31' in body and 'not_ready' in body)
    for name in ['result.md','author-review.md','next-source-frontier.md']:
        check(name+' exists', (OUT/name).is_file())
    if any(not x['passed'] for x in checks):
        write('closeout-checks.json', {'checks':checks, 'failed':sum(not x['passed'] for x in checks)})
        raise SystemExit(1)
    receipts = [json.loads(p.read_text()) for p in sorted((OUT/'sources').glob('*.receipt.json'))]
    paths = [p for p in OUT.rglob('*') if p.is_file() and p.name not in {'run-manifest.json','completion.json','closeout-checks.json'}]
    paths += [ROOT/'docs/plans/accounting-bidi-direct-rust-terms-20261011.md']
    write('run-manifest.json', {
        'recorded_at':'2026-10-11', 'unit':'Exact direct Rust source terms for python-bidi 0.6.11',
        'git_commit':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
        'git_state':'Read-only .git; unrelated dirty work preserved; no Git write',
        'plan':'docs/plans/accounting-bidi-direct-rust-terms-20261011.md', 'result':str((OUT/'result.md').relative_to(ROOT)),
        'data_version':{'python_bidi_sdist':ledger['parent_sha256'],'direct_crates':[{k:x[k] for k in ['crate','version','sha256']} for x in ledger['crates']]},
        'commands':[x['command'] for x in receipts]+[['CUDA_VISIBLE_DEVICES=-1','python3',str((OUT/'audit_sources.py').relative_to(ROOT))],['CUDA_VISIBLE_DEVICES=-1','python3',str((OUT/'closeout.py').relative_to(ROOT))]],
        'environment':{'python':'3.11','cpu_gpu':'CPU-only documentary checks; GPU intentionally hidden','seeds':'N/A deterministic'},
        'wall_time':{'acquisition_seconds':sum(x['wall_seconds'] for x in receipts),'closeout_seconds':time.monotonic()-start,'author_reading':'Not timed'},
        'source_checks':17, 'candidate_pdf':candidate,'controls':controls,'pointer_relocations':reloc,
        'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in paths},'readiness':'not_ready','runtime_compatibility':'not_checked','distribution_clearance':'not_checked'})
    write('closeout-checks.json', {'checks':checks,'passed':len(checks),'failed':0,'manifest_sha256':sha(OUT/'run-manifest.json')})
    write('completion.json', {'status':'closed_bounded_direct_source_terms','source_checks':17,'closeout_checks':len(checks),'failed':0,'manifest_sha256':sha(OUT/'run-manifest.json'),'readiness':'not_ready'})
    print(json.dumps({'source_checks':17,'closeout_checks':len(checks),'failed':0}))

if __name__ == '__main__':
    main()
