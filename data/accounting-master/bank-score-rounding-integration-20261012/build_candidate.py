"""Create and build a separate 2.44; freeze its 2.43 comparator."""
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
BASE = ROOT / 'docs/design/proposal/manuscript-reporting-inputs-20261012'
CAND = ROOT / 'docs/design/proposal/manuscript-score-rounding-20261012'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n, o): (OUT / n).write_text(json.dumps(o, indent=2) + '\n')

def expected_text(relative):
    text = (BASE / relative).read_text()
    if relative == 'accounting-product-proposal.tex':
        text = text.replace('Version 2.43 (proposal candidate)', 'Version 2.44 (proposal candidate)')
    elif relative == 'chapters/15-banking.tex':
        old = (OUT / 'old-passage.tex').read_text()
        assert text.count(old) == 1
        text = text.replace(old, (OUT / 'new-passage.tex').read_text())
    elif relative == 'references.bib':
        text += '\n' + (OUT / 'new-references.bib').read_text()
    return text

def main():
    assert not CAND.exists() and not (OUT / 'completion.json').exists()
    assert sha(BASE / 'accounting-product-proposal.pdf') == '47516cce310d21b716e5226fd159a173985f58da0528909706b6c182842fd068'
    controls = ['docs/plans/accounting-master-checkpoint.md', 'docs/plans/accounting-master-current.md',
                'docs/plans/accounting-continuation-requirements-20261007.md', 'data/accounting-master/next-plan.md']
    rows = []
    for rel in controls:
        dest = OUT / 'pointers-before' / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, dest)
        rows.append({'live': rel, 'snapshot': str(dest.relative_to(ROOT)), 'sha256': sha(dest)})
    save('baseline.json', {'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
         'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'pointer_snapshots': rows,
         'pdf_sha256': sha(BASE / 'accounting-product-proposal.pdf')})
    frozen = OUT / 'baseline-source'
    files = sorted(p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex', '.bib', '.lark'})
    hashes = {str(p.relative_to(BASE)): sha(p) for p in files}
    for relative in hashes:
        for parent in [frozen, CAND]:
            (parent / relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(BASE / relative, frozen / relative)
        (CAND / relative).write_text(expected_text(relative))
    save('candidate.json', {'source_hashes': hashes, 'baseline_pdf_sha256': sha(BASE / 'accounting-product-proposal.pdf'),
         'candidate': str(CAND.relative_to(ROOT)), 'delta': 'Replace unresolved score-rounding sentence with attributed explanation and proposed-policy boundary; two references added.',
         'passage_hashes': {n: sha(OUT / n) for n in ['old-passage.tex', 'new-passage.tex', 'new-references.bib']}, 'readiness': 'not_ready'})
    command = ['latexmk', '-g', '-lualatex', '-interaction=nonstopmode', '-halt-on-error', 'accounting-product-proposal.tex']
    env = os.environ.copy()
    overrides = {'TEXMFVAR': '/tmp/accdsl-texmfvar', 'TEXMFCACHE': '/tmp/accdsl-texmfvar', 'CUDA_VISIBLE_DEVICES': '-1'}
    env.update(overrides)
    start = time.monotonic()
    with (OUT / 'build-stdout.log').open('w') as log:
        result = subprocess.run(command, cwd=CAND, env=env, stdout=log, stderr=subprocess.STDOUT)
    record = {'command': command, 'cwd': str(CAND.relative_to(ROOT)), 'environment_overrides': overrides,
              'wall_seconds': time.monotonic() - start, 'exit_code': result.returncode}
    save('build-run.json', record)
    print(json.dumps(record))
    raise SystemExit(result.returncode)

if __name__ == '__main__': main()
