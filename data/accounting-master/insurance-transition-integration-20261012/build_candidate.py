"""Build separate 2.48 while preserving every 2.47 source file."""
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'docs/design/proposal/manuscript-vfa-20261012'
CAND = ROOT / 'docs/design/proposal/manuscript-transition-20261012'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n, v): (OUT / n).write_text(json.dumps(v, indent=2)+'\n')
def expected_text(rel):
    s = (BASE / rel).read_text()
    if rel == 'accounting-product-proposal.tex':
        assert s.count('Version 2.47 (proposal candidate)') == 1
        s = s.replace('Version 2.47 (proposal candidate)', 'Version 2.48 (proposal candidate)')
    elif rel == 'sections/insurance-methods.tex':
        anchor = '\\clearpage\n\\hypertarget{interfaces-exclusions-and-acceptance-cases}'
        assert s.count(anchor) == 1
        s = s.replace(anchor, (OUT / 'insurance-addition.tex').read_text()+'\n'+anchor, 1)
    return s

def main():
    assert not CAND.exists() and not (OUT / 'completion.json').exists()
    assert sha(BASE / 'accounting-product-proposal.pdf') == '7c7f76426717293127b4469a937eff9ddb50a543ff7fee5b4a87f309a97f40a5'
    source = ROOT / 'data/accounting-master/insurance-transition-source-20261012'
    closed = json.loads((source / 'completion.json').read_text())
    assert closed['source_checks'] == 43 and closed['failed'] == 0
    assert sha(source / 'run-manifest.json') == closed['manifest_sha256']
    rows = []
    for rel in ['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-current.md',
                'docs/plans/accounting-continuation-requirements-20261007.md','data/accounting-master/next-plan.md']:
        q = OUT / 'pointers-before' / rel;q.parent.mkdir(parents=True, exist_ok=True);shutil.copyfile(ROOT / rel, q)
        rows.append({'live': rel, 'snapshot': str(q.relative_to(ROOT)), 'sha256': sha(q)})
    save('baseline.json', {'git_commit': subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip(),
        'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'pointer_snapshots': rows,
        'pdf_sha256': sha(BASE / 'accounting-product-proposal.pdf')})
    files = sorted(p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'})
    hashes = {str(p.relative_to(BASE)): sha(p) for p in files}
    for rel in hashes:
        for parent in [OUT / 'baseline-source', CAND]: (parent / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(BASE / rel, OUT / 'baseline-source' / rel)
        (CAND / rel).write_text(expected_text(rel))
    save('candidate.json', {'source_hashes': hashes, 'baseline_pdf_sha256': sha(BASE / 'accounting-product-proposal.pdf'),
        'candidate': str(CAND.relative_to(ROOT)), 'delta': 'Add historical-source transition-method and information-limit explanation; preserve all prior text and bibliography.',
        'passage_hashes': {'insurance-addition.tex': sha(OUT / 'insurance-addition.tex')}, 'readiness': 'not_ready'})
    command = ['latexmk','-g','-lualatex','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
    overrides = {'TEXMFVAR':'/tmp/accdsl-texmfvar','TEXMFCACHE':'/tmp/accdsl-texmfvar','CUDA_VISIBLE_DEVICES':'-1'}
    env = os.environ.copy();env.update(overrides);start = time.monotonic()
    with (OUT / 'build-stdout.log').open('w') as log:
        r = subprocess.run(command, cwd=CAND, env=env, stdout=log, stderr=subprocess.STDOUT)
    record = {'command': command, 'cwd': str(CAND.relative_to(ROOT)), 'environment_overrides': overrides,
        'wall_seconds': time.monotonic()-start, 'exit_code': r.returncode}
    save('build-run.json', record);print(json.dumps(record));raise SystemExit(r.returncode)
if __name__ == '__main__': main()
