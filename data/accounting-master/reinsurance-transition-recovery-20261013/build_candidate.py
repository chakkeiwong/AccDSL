"""Create the separate Version 2.55 manuscript from a protected baseline."""
import datetime
import difflib
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
BASE = ROOT / 'docs/design/proposal/manuscript-transition-balances-20261013'
CAND = ROOT / 'docs/design/proposal/manuscript-reinsurance-recovery-20261013'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, data):
    (UNIT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

def expected_text(rel):
    text = (BASE / rel).read_text()
    if rel == 'accounting-product-proposal.tex':
        assert text.count('Version 2.54 (proposal candidate)') == 1
        return text.replace('Version 2.54 (proposal candidate)', 'Version 2.55 (proposal candidate)')
    if rel != 'sections/insurance-methods.tex':
        return text
    assert text.count('The next case shows both') == 1
    text = text.replace('The next case shows both', 'The later Munich Re case shows both')
    marker = r'\hypertarget{munich-re-transition-disclosure}'
    assert text.count(marker) == 1
    return text.replace(marker, (UNIT / 'reinsurance-addition.tex').read_text() + marker)

def main():
    assert not CAND.exists() and not (UNIT / 'completion.json').exists()
    evidence = json.loads((UNIT / 'source-calculation-checks.json').read_text())
    assert not evidence['failed']
    baseline = json.loads((UNIT / 'baseline.json').read_text())
    assert sha(BASE / 'accounting-product-proposal.pdf') == baseline['baseline_pdf_sha256']
    source_hashes = {str(p.relative_to(BASE)): sha(p) for p in sorted(BASE.rglob('*'))
                     if p.is_file() and p.suffix in {'.tex', '.bib', '.lark'}}
    changes = []
    for rel in source_hashes:
        original = (BASE / rel).read_text()
        current = expected_text(rel)
        p = CAND / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(current)
        if current != original:
            changes.append(rel)
            patch = ''.join(difflib.unified_diff(original.splitlines(True), current.splitlines(True), fromfile=str(BASE / rel), tofile=str(p)))
            (UNIT / (Path(rel).stem + '.diff')).write_text(patch)
    save('candidate.json', {'baseline': str(BASE.relative_to(ROOT)), 'candidate': str(CAND.relative_to(ROOT)),
                           'baseline_pdf_sha256': baseline['baseline_pdf_sha256'], 'source_hashes': source_hashes,
                           'changed_files': changes, 'readiness': 'not_ready', 'human_review': 'pending'})
    cmd = ['latexmk', '-g', '-lualatex', '-interaction=nonstopmode', '-halt-on-error', 'accounting-product-proposal.tex']
    overrides = {'TEXMFVAR': '/tmp/accdsl-texmfvar', 'TEXMFCACHE': '/tmp/accdsl-texmfvar', 'CUDA_VISIBLE_DEVICES': '-1'}
    env = os.environ.copy()
    env.update(overrides)
    started = time.monotonic()
    with (UNIT / 'build-stdout.log').open('w') as log:
        result = subprocess.run(cmd, cwd=CAND, env=env, stdout=log, stderr=subprocess.STDOUT)
    record = {'command': cmd, 'cwd': str(CAND.relative_to(ROOT)), 'environment_overrides': overrides,
              'exit_code': result.returncode, 'wall_seconds': time.monotonic() - started,
              'completed_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    save('build-run.json', record)
    print(json.dumps(record))
    raise SystemExit(result.returncode)

if __name__ == '__main__':
    main()
