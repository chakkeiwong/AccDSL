"""Build a separate Version 2.43 from the protected 2.42 source inventory."""
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,o): (OUT/n).write_text(json.dumps(o,indent=2)+'\n')

BASE = ROOT / 'docs/design/proposal/manuscript-capital-recognition-20261012'
CAND = ROOT / 'docs/design/proposal/manuscript-reporting-inputs-20261012'
ANCHOR = "Debt amounts add a second distinction."

def main():
    assert not CAND.exists()
    assert sha(BASE / 'accounting-product-proposal.pdf') == '59c9761e5da879bbd93ebb15068eda1f436980b9340dda4b9a32a4b3f813cfce'
    files = sorted(p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex', '.bib', '.lark'})
    hashes = {str(p.relative_to(BASE)): sha(p) for p in files}
    for path in files:
        target = CAND / path.relative_to(BASE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    title = CAND / 'accounting-product-proposal.tex'
    text = title.read_text()
    assert text.count('Version 2.42 (proposal candidate)') == 1
    title.write_text(text.replace('Version 2.42 (proposal candidate)', 'Version 2.43 (proposal candidate)'))
    chapter = CAND / 'chapters/15-banking.tex'
    text = chapter.read_text()
    assert text.count(ANCHOR) == 1
    chapter.write_text(text.replace(ANCHOR, (OUT / 'insertion.tex').read_text() + '\n' + ANCHOR))
    bib = CAND / 'references.bib'
    bib.write_text(bib.read_text() + '\n' + (OUT / 'new-references.bib').read_text())
    save('candidate.json', {'source_hashes': hashes, 'baseline_pdf_sha256': sha(BASE / 'accounting-product-proposal.pdf'),
         'insertion_sha256': sha(OUT / 'insertion.tex'), 'new_references_sha256': sha(OUT / 'new-references.bib'),
         'candidate': str(CAND.relative_to(ROOT)), 'readiness': 'not_ready'})
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

if __name__ == '__main__':
    main()
